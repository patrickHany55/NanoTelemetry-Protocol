import socket
import struct
import time
import csv
import os

# Header format: version(1), msg_type(1), flags(1), device_id(1), seq(4), timestamp(4)
HEADER_FMT = '!BBBBII'
HEADER_LEN = struct.calcsize(HEADER_FMT)

MSG_TYPE_DATA = 1
MSG_TYPE_HEARTBEAT = 2

def main():
    HOST = "0.0.0.0"
    PORT = 12000
    CSV_FILE = "NanoTelemetry_log_v1.csv"

    # create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    # prepare CSV
    header_needed = not os.path.exists(CSV_FILE)
    csv_file = open(CSV_FILE, "a", newline="")
    writer = csv.writer(csv_file)
    if header_needed:
        writer.writerow(["device_id", "seq", "timestamp", "arrival_time", "duplicate_flag", "gap_flag"])
        csv_file.flush()

    last_seq = {} 

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            arrival = time.time()

            if len(data) < HEADER_LEN:
                print("[SERVER] Ignored too-small packet")
                continue

            version, msg_type, flags, device_id, seq, timestamp = struct.unpack(HEADER_FMT, data[:HEADER_LEN])

            duplicate_flag = 0
            gap_flag = 0
            if device_id in last_seq:
                prev = last_seq[device_id]
                if seq <= prev:
                    duplicate_flag = 1
                elif seq > prev + 1:
                    gap_flag = 1
            last_seq[device_id] = seq

            writer.writerow([device_id, seq, timestamp, f"{arrival:.6f}", duplicate_flag, gap_flag])
            csv_file.flush()
    except KeyboardInterrupt:
        print("\n[SERVER] Interrupted by user. Closing socket and exiting...")
    finally:
        sock.close()
        csv_file.close()
        print("[SERVER] Socket closed. CSV saved.")

if __name__ == "__main__":
    main()
