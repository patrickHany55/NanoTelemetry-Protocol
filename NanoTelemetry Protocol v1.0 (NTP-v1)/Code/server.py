import socket
import struct
import time
import csv
import os

# Protocol header format and constants
HEADER_FMT = '!BBBBII'
HEADER_LEN = struct.calcsize(HEADER_FMT)

MSG_TYPE_DATA = 1
MSG_TYPE_HEARTBEAT = 2

# Reorder buffer window: packets within this time window can be reordered
REORDER_WINDOW_MS = 120
REORDER_WINDOW = REORDER_WINDOW_MS / 1000.0

# Maximum payload size enforcement
PAYLOAD_LIMIT = 200

def now():
    """Get current timestamp."""
    return time.time()

def main():
    HOST = "0.0.0.0"
    PORT = 12000

    # CSV output files for logging
    PACKET_CSV = "NanoTelemetry_log_v1.csv"
    EXPANDED_CSV = "NanoTelemetry_log_v1_expanded.csv"

    # ========== Initialize UDP Socket ==========
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    print(f"[SERVER] Listening on {HOST}:{PORT}")

    # ========== Initialize CSV Writers ==========
    # Packet-level CSV: logs each received packet
    packet_new = not os.path.exists(PACKET_CSV)
    p_fp = open(PACKET_CSV, "a", newline="")
    p_writer = csv.writer(p_fp)
    if packet_new:
        p_writer.writerow(["device_id","seq","timestamp","arrival_time","duplicate_flag","gap_flag"])

    # Expanded CSV: unpacks batch packets into individual readings
    expanded_new = not os.path.exists(EXPANDED_CSV)
    e_fp = open(EXPANDED_CSV, "a", newline="")
    e_writer = csv.writer(e_fp)
    if expanded_new:
        e_writer.writerow(["device_id","seq","reading_index","reading_value","timestamp","arrival_time","duplicate_flag","gap_flag"])

if __name__ == '__main__':
    main()