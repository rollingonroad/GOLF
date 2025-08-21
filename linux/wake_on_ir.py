import subprocess
import socket
import serial
import time
from evdev import InputDevice, list_devices, ecodes
from wakeonlan import send_magic_packet
from datetime import datetime
import serial.tools.list_ports

# ---------- 配置项 ----------
TARGET_MAC = '48:21:0B:71:2C:32'
TARGET_IP = '172.16.0.255'
WINDOWS_IP = '172.16.0.2'
UDP_PORT = 4000
LOG_FILE = '/var/log/wake_on_ir.log'
BAUDRATE = 9600
TIMEOUT = 1
CMD_ON  = b'\x7E\x30\x30\x30\x30\x20\x31\x0D'
CMD_OFF = b'\x7E\x30\x30\x30\x30\x20\x30\x0D'

# ---------- 日志 ----------
def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{datetime.now()}] {msg}\n")

# ---------- 设备查找函数 ----------
from evdev import InputDevice, list_devices
import serial.tools.list_ports

def find_input_device(name_keyword, verbose=True):
    """
    使用 evdev 查找包含指定关键词的输入设备路径。
    如果未找到，打印所有候选设备，辅助调试。
    """
    candidates = []
    for path in list_devices():
        try:
            dev = InputDevice(path)
            candidates.append((path, dev.name))
            if name_keyword.lower() in dev.name.lower():
                if verbose:
                    log(f"[OK] 找到输入设备: {dev.name} @ {path}")
                return path
        except Exception as e:
            if verbose:
                log(f"[跳过] {path}: 无法读取 ({e})")

    if verbose:
        log(f"[!] 未找到包含 '{name_keyword}' 的输入设备，候选如下：")
        for path, name in candidates:
            log(f" - {path}: {name}")
        log("请检查关键词拼写，或尝试使用更常见或唯一的关键字。")

    return None

def find_serial_device(description_keyword, verbose=True):
    ports = serial.tools.list_ports.comports()
    candidates = []

    for port in ports:
        vid = f"{port.vid:04X}" if port.vid else '-'
        pid = f"{port.pid:04X}" if port.pid else '-'
        sn = port.serial_number or '-'
        desc = port.description or '-'
        man = port.manufacturer or '-'
        prod = port.product or '-'

        info_str = f"{port.device} | {desc} | {man} | {prod} | VID:{vid} PID:{pid} SN:{sn}"
        candidates.append(info_str)

        if description_keyword.lower() in info_str.lower():
            if verbose:
                log(f"[OK] 找到串口设备: {info_str}")
            return port.device

    if verbose:
        log(f"[!] 未找到匹配串口设备: '{description_keyword}'")
        log("候选串口设备如下：")
        for line in candidates:
            log(f" - {line}")

    return None

# ---------- 网络 & 控制 ----------
def is_windows_running():
    try:
        result = subprocess.run(['ping', '-c', '5', '-i', '0.2', WINDOWS_IP], capture_output=True, text=True)
        count = sum(1 for line in result.stdout.splitlines() if 'bytes from' in line or '来自' in line)
        return count >= 3
    except Exception as e:
        log(f"ping 失败：{e}")
        return False

def send_shutdown_packet():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b'shutdowntangguo', (WINDOWS_IP, UDP_PORT))
        log("已发送关机数据包到 Windows")
    except Exception as e:
        log(f"发送关机包失败：{e}")

def send_wake_packet():
    try:
        send_magic_packet(TARGET_MAC, ip_address=TARGET_IP)
        log("发送 Magic Packet 唤醒 Windows")
    except Exception as e:
        log(f"唤醒失败：{e}")

def send_serial(cmd, port):
    try:
        with serial.Serial(port, BAUDRATE, timeout=TIMEOUT) as ser:
            ser.write(cmd)
            time.sleep(0.1)
            resp = ser.read(16)
            log(f"Sent: {cmd.hex()} Response: {resp.hex()}")
    except Exception as e:
        log(f"串口错误（{port}）：{e}")

def buzzer(duration, port):
    try:
        with serial.Serial(port) as ser:
            ser.dtr = True
            time.sleep(duration)
            ser.dtr = False
        log(f"蜂鸣器响了 {duration}s")
    except Exception as e:
        log(f"蜂鸣器错误（{port}）：{e}")

# ---------- 主函数 ----------
def main():
    DEVICE_PATH = find_input_device("flirc") or "/dev/input/event5"
    PROJECTOR_PORT = find_serial_device("067B") or "/dev/ttyUSB0"
    BUZZER_PORT = find_serial_device("1A86") or "/dev/ttyUSB2"

    if not DEVICE_PATH:
        log("找不到输入设备，退出程序")
        return

    try:
        dev = InputDevice(DEVICE_PATH)
        log(f"启动监听设备: {dev.path} ({dev.name})")

        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY and event.value == 1:
                log(f"收到按键：code={event.code}")
                if event.code == 99:  # 替换为你的关机键
                    log("收到 SC99，检查 Windows 是否在线")
                    buzzer(0.5, BUZZER_PORT)
                    if is_windows_running():
                        log("Windows 正在运行，发送关机指令")
                        send_shutdown_packet()
                        time.sleep(10)
                        send_serial(CMD_OFF, PROJECTOR_PORT)
                    else:
                        log("Windows 未运行，尝试唤醒")
                        send_wake_packet()
                        send_serial(CMD_ON, PROJECTOR_PORT)

    except Exception as e:
        log(f"主循环异常退出：{e}")

# ---------- 入口 ----------
if __name__ == '__main__':
    main()
