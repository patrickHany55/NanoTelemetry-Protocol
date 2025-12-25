NanoTelemetry Protocol v1.0 — Phase 2 and 3
UDP Telemetry System with Batching, Reordering, Loss & Delay Testing

This repository implements Phase 2 and 3 of the NanoTelemetry Protocol (NTP-v1), a lightweight UDP-based telemetry system designed for embedded devices.
Phase 2 introduces:

Batching (up to 49 readings per packet under 200 bytes)

Reordering buffer (120 ms)

Duplicate and gap detection

Heartbeat support

Three automated network test scenarios:

Baseline (no impairment)

100 ms ± 10 ms delay & jitter

5% packet loss
Repository Structure
NanoTelemetry-Protocol/
│
├── CSE361 Project Description_updated.pdf
│
└── NanoTelemetry Protocol v1.0 (NTP-v1)/
    ├── Mini-RFC/                     # Protocol specification
    ├── Project-proposal/
    ├── README.md                     # ← YOU ARE HERE
    ├── Output/
    │   └── NanoTelemetry_log_v1.csv  # Example logged data
    │
    └── Code/
        ├── client.py                 # Telemetry client
        ├── server.py                 # Telemetry server (reorder buffer, CSV logs)
        │
        ├── run_baseline.sh           # Test 1 – no network impairment
        ├── run_loss5.sh              # Test 2 – 5% packet loss
        ├── run_delay_jitter.sh       # Test 3 – 100ms delay ±10ms
        └── clear_netem.sh            # Reset network interface shaping rules
        Protocol Summary
Header Format (HEADER_FMT = !BBBBII)
Field	Size	Description
Version	1B	Protocol version (1)
Msg Type	1B	1=DATA, 2=HEARTBEAT
Flags	1B	0x01 = BATCH_MODE
Device ID	1B	0–255
Sequence	4B	Monotonic packet counter
Timestamp	4B	Unix timestamp (seconds)
Payload

Single mode: a single float32

Batch mode: count (1 byte) + N×float32

200-byte maximum payload rule
1 + N*4 ≤ 200  →  N ≤ 49


The client automatically clamps batch size.
How to Run (Linux)
1. Install Dependencies
sudo apt update
sudo apt install -y iproute2 tcpdump

2. Navigate to the Code Directory
cd NanoTelemetry-Protocol
cd "NanoTelemetry Protocol v1.0 (NTP-v1)"
cd Code

3. Make the test scripts executable
chmod +x run_baseline.sh
chmod +x run_loss5.sh
chmod +x run_delay_jitter.sh
chmod +x clear_netem.sh

4. Run the Tests
Test 1 — Baseline (no delay, no loss)
./run_baseline.sh

Test 2 — 5% Packet Loss
./run_loss5.sh

Test 3 — 100 ms Delay ± 10 ms Jitter
./run_delay_jitter.sh

Clear netem rules
./clear_netem.sh

Output Files

Each run produces:

File	Description
NanoTelemetry_log_v1.csv	Per-packet log (seq, device, gap/dup flags, arrival time)
NanoTelemetry_log_v1_expanded.csv	Unpacked batch values
capture_*.pcap	Raw packet capture (can be opened in Wireshark)

All output files are placed inside:

NanoTelemetry Protocol v1.0 (NTP-v1)/Output/

Components Overview
client.py

Sends telemetry packets at a configurable interval

Supports single or batch mode

Ensures payload ≤ 200 bytes

Sends a heartbeat on shutdown

Environment-configurable:

SERVER_IP
SERVER_PORT
DEVICE_ID
DURATION
INTERVAL
BATCH_SIZE

server.py

Listens for UDP telemetry packets

Verifies payload size

Maintains a reorder buffer (120ms)

Detects:

duplicate packets

missing sequence numbers (gaps)

Logs:

Packet metadata → NanoTelemetry_log_v1.csv

Unpacked readings → NanoTelemetry_log_v1_expanded.csv

Shell Scripts
Script	Function
run_baseline.sh	Runs server + client + packet capture
run_loss5.sh	Adds 5% loss then executes test
run_delay_jitter.sh	Adds delay/jitter then executes test
clear_netem.sh	Removes all network shaping rules
Requirements

Python 3.8+

Linux system with:

iproute2 (for tc)

tcpdump

A network interface supporting netem (e.g., eth0, ens33, etc.)

Mini-RFC

Protocol specification available in:

Mini-RFC/

Validation

The system has been validated with:

baseline network

controlled delay/jitter

random packet loss

Wireshark packet captures

CSV telemetry logs
# Video Demo Link:
https://drive.google.com/file/d/185dnR8Uth5A4JEioryVVhCVWyb702QNS/view?usp=sharing
