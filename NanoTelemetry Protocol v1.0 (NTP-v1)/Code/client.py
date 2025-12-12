#!/usr/bin/env python3
"""
Phase 2 - Client with batching + 200-byte payload limit.
Environment variables:
- SERVER_IP (default 127.0.0.1)
- SERVER_PORT (default 12000)
- DEVICE_ID (default 1)
- INTERVAL (default 1.0)
- DURATION (default 60)
- BATCH_SIZE (default 1)
"""


import os
import socket
import struct
import time
import random

# Protocol constants: header format, message types, version
HEADER_FMT = '!BBBBII'
HEADER_LEN = struct.calcsize(HEADER_FMT)
MSG_TYPE_DATA = 1
MSG_TYPE_HEARTBEAT = 2
VERSION = 1


def pack_header(version, msg_type, flags, device_id, seq, timestamp):
    return struct.pack(HEADER_FMT, version, msg_type, flags, device_id, seq, timestamp)


def pack_batch_payload(values):
    count = len(values)
    payload = struct.pack('!B', count)
    for v in values:
        payload += struct.pack('!f', float(v))
    return payload


def pack_single_payload(value):
    return struct.pack('!f', float(value))


def main():
    # ========== Load Configuration ==========
    SERVER_IP = os.getenv('SERVER_IP', '127.0.0.1')
    SERVER_PORT = int(os.getenv('SERVER_PORT', '12000'))
    DEVICE_ID = int(os.getenv('DEVICE_ID', '1')) & 0xFF
    INTERVAL = float(os.getenv('INTERVAL', '1.0'))
    DURATION = int(os.getenv('DURATION', '60'))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', '1'))

    # ========== Enforce 200-byte Payload Limit ==========
    MAX_BATCH = 49  # 1 + 4*N <= 200
    if BATCH_SIZE > MAX_BATCH:
        print(f"[CLIENT] WARNING: BATCH_SIZE={BATCH_SIZE} too large, clamping to {MAX_BATCH}")
        BATCH_SIZE = MAX_BATCH

    # ========== Initialize Socket ==========
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    seq = 1
    end_time = time.time() + DURATION

    print(f"[CLIENT {DEVICE_ID}] Sending to {SERVER_IP}:{SERVER_PORT}, "
          f"interval={INTERVAL}s, duration={DURATION}s, batch={BATCH_SIZE}")

    try:
        while time.time() < end_time:
            timestamp = int(time.time())
            flags = 0

            if BATCH_SIZE > 1:
                # Batch Mode
                flags |= 0x01
                base = 25.0 + (DEVICE_ID % 10)
                values = [base + random.uniform(-0.5, 0.5) for _ in range(BATCH_SIZE)]
                header = pack_header(VERSION, MSG_TYPE_DATA, flags, DEVICE_ID, seq, timestamp)
                payload = pack_batch_payload(values)
                sock.sendto(header + payload, (SERVER_IP, SERVER_PORT))
                print(f"[CLIENT {DEVICE_ID}] Sent DATA seq={seq} batch={BATCH_SIZE}")

            else:
                # Single Mode
                value = 25.0 + random.uniform(-0.5, 0.5)
                header = pack_header(VERSION, MSG_TYPE_DATA, flags, DEVICE_ID, seq, timestamp)
                payload = pack_single_payload(value)
                sock.sendto(header + payload, (SERVER_IP, SERVER_PORT))
                print(f"[CLIENT {DEVICE_ID}] Sent DATA seq={seq} value={value:.2f}")

            seq = (seq + 1) & 0xFFFFFFFF
            time.sleep(INTERVAL)

        # ========== Graceful Shutdown ==========
        timestamp = int(time.time())
        header = pack_header(VERSION, MSG_TYPE_HEARTBEAT, 0, DEVICE_ID, seq, timestamp)
        sock.sendto(header, (SERVER_IP, SERVER_PORT))
        print(f"[CLIENT {DEVICE_ID}] Sent HEARTBEAT seq={seq}")

    except KeyboardInterrupt:
        print("\n[CLIENT] Interrupted by user.")

    finally:
        sock.close()
        print("[CLIENT] Socket closed. Exiting.")


if __name__ == '__main__':
    main()
