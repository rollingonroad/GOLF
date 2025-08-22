# GOLF
stuff for GOLF simulator
# 记得关掉所有网卡上的防火墙
# 安装有线、无线网卡驱动
* 有线网卡地址：172.16.0.2/255.255.255.0


# 安装tplink无线网卡驱动

# 禁用windows自动更新

# 设置自动登录
* 将密码改为空

# 设置hotkey
* 安装autohotkey v2  
* golf.ahk  
```
#Requires AutoHotkey v2.0

SC16A:: Send("#{d}")
SC15D:: Send("!{Enter}")
```
* 将golf.ahk放入startup目录里面


# 设置udp服务
* 关闭专有网络上的windows defender防火墙
* C:\shutdown_listener\listener.py
```
import socket
import os

UDP_IP = "0.0.0.0"
UDP_PORT = 4000

print(f"Listening for UDP packets on port {UDP_PORT}...")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024)
    if b"shutdown" in data:
        print("Shutdown command received, shutting down...")
        os.system("shutdown /s /t 0")
```
* 测试代码：
```
>>> import socket
>>> sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
>>> sock.sendto(b'shutdowntangguo', ("192.168.1.154", 4000))
```
* NSSM
** nssm.cc
** 复制nssm.exe 到C:\windows\
** 安装python要安装到C:\program Files\python下面，另外参数的目录要写对
<img width="645" height="347" alt="image" src="https://github.com/user-attachments/assets/11291da9-cb0c-46cb-9e96-44665a3480fa" />


# 安装golf软件，并设置自动启动
https://skytrakgolf.com/pages/downloads
登录信息：
flyonsnow@hotmail.com
S******166

# 设置自动启动
Win+R shell:strtup

# 设置鼠标大小和颜色

设置-轻松使用-鼠标指针

# Linux
 3  sudo apt install tcpdump
    8  python3 -m venv ~/wol
    9  source wol/bin/activate
   10  pip install wakeonlan
72  pip install evdev
   73  python3 -m evdev.evtest
   96  sudo vi /etc/systemd/system/wakeonir.service
   97  sudo touch /var/log/wake_on_ir.log
   98  sudo chown david:david /var/log/wake_on_ir.log
   99  sudo systemctl daemon-reexec
  100  sudo systemctl daemon-reload
  101  sudo systemctl enable wakeonir.service
  102  sudo systemctl start wakeonir.service
  103  sudo systemctl status wakeonir.service

