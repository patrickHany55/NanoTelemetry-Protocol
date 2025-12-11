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

    # ========== State Tracking ==========
    last_seq = {}
    reorder_buffer = []

    # ========== Main Receive Loop ==========
    try:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except KeyboardInterrupt:
                break

            arrival = now()

            # ========== Parse Header ==========
            if len(data) < HEADER_LEN:
                print("[SERVER] Dropped too-small packet")
                continue

            version, msg_type, flags, device_id, seq, timestamp = struct.unpack(
                HEADER_FMT, data[:HEADER_LEN]
            )

            payload = data[HEADER_LEN:]

            # ========== Validate Payload Size ==========
            if len(payload) > PAYLOAD_LIMIT:
                print(f"[SERVER] Dropped packet: payload {len(payload)} > {PAYLOAD_LIMIT}")
                continue

            # ========== Duplicate & Gap Detection ==========
            dup = 0
            gap = 0
            if device_id in last_seq:
                prev = last_seq[device_id]
                if seq <= prev:
                    dup = 1
                elif seq > prev + 1:
                    gap = 1

            if device_id not in last_seq or seq > last_seq[device_id]:
                last_seq[device_id] = seq

            # ========== Add to Reorder Buffer ==========
            reorder_buffer.append({
                "device_id": device_id,
                "seq": seq,
                "timestamp": timestamp,
                "arrival_time": arrival,
                "duplicate_flag": dup,
                "gap_flag": gap,
                "msg_type": msg_type,
                "flags": flags,
                "payload": payload
            })

            # ========== Process Ready Packets ==========
            cutoff = now() - REORDER_WINDOW
            ready = [p for p in reorder_buffer if p["arrival_time"] <= cutoff]
            reorder_buffer = [p for p in reorder_buffer if p["arrival_time"] > cutoff]

            ready.sort(key=lambda p: p["timestamp"])

            # ========== Log Packets to CSV ==========
            for pkt in ready:
                p_writer.writerow([
                    pkt["device_id"], pkt["seq"], pkt["timestamp"],
                    f"{pkt['arrival_time']:.6f}", pkt["duplicate_flag"], pkt["gap_flag"]
                ])

                # ========== Unpack Batch Data ==========
                if pkt["msg_type"] == MSG_TYPE_DATA:
                    if pkt["flags"] & 0x01:
                        if len(pkt["payload"]) >= 1:
                            count = pkt["payload"][0]
                            offset = 1
                            for i in range(count):
                                if offset + 4 <= len(pkt["payload"]):
                                    val = struct.unpack_from('!f', pkt["payload"], offset)[0]
                                    offset += 4
                                    e_writer.writerow([
                                        pkt["device_id"], pkt["seq"], i, f"{val:.6f}",
                                        pkt["timestamp"], f"{pkt['arrival_time']:.6f}",
                                        pkt["duplicate_flag"], pkt["gap_flag"]
                                    ])
                    else:
                        if len(pkt["payload"]) >= 4:
                            val = struct.unpack('!f', pkt["payload"][:4])[0]
                            e_writer.writerow([
                                pkt["device_id"], pkt["seq"], 0, f"{val:.6f}",
                                pkt["timestamp"], f"{pkt['arrival_time']:.6f}",
                                pkt["duplicate_flag"], pkt["gap_flag"]
                            ])

                p_fp.flush()
                e_fp.flush()

    except KeyboardInterrupt:
        print("[SERVER] Shutting down gracefully...")


if __name__ == '__main__':
    main()