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