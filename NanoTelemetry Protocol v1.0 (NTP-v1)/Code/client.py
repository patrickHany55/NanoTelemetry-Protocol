import socket
import struct
import time
import random

# Configuration (edit values if needed)
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12000
DEVICE_ID = 1
INTERVAL = 1.0      # seconds between packets
DURATION = 20       # total run time in seconds

# Header format
HEADER_FMT = '!BBBBII'
HEADER_LEN = struct.calcsize(HEADER_FMT)

MSG_TYPE_DATA = 1
MSG_TYPE_HEARTBEAT = 2
VERSION = 1

def send_packet(sock, msg_type, seq, value=0.0):
    timestamp = int(time.time())
    flags = 0
    header = struct.pack(HEADER_FMT, VERSION, msg_type, flags, DEVICE_ID, seq, timestamp)

    if msg_type == MSG_TYPE_DATA:
        payload = struct.pack('!f', float(value))
    else:
        payload = b''

    sock.sendto(header + payload, (SERVER_IP, SERVER_PORT))

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 1
    print(f"[CLIENT {DEVICE_ID}] Sending to {SERVER_IP}:{SERVER_PORT} every {INTERVAL}s for {DURATION}s...")

    start_time = time.time()
    while time.time() - start_time < DURATION:
        reading = 25.0 + random.uniform(-0.5, 0.5)
        send_packet(sock, MSG_TYPE_DATA, seq, reading)
        print(f"[CLIENT {DEVICE_ID}] Sent DATA seq={seq}, value={reading:.2f}")
        seq += 1
        time.sleep(INTERVAL)

    # send final heartbeat
    send_packet(sock, MSG_TYPE_HEARTBEAT, seq)
    print(f"[CLIENT {DEVICE_ID}] Sent final HEARTBEAT seq={seq}")

    sock.close()
    print("[CLIENT] Socket closed. Done.")

if __name__ == "__main__":
    main()
