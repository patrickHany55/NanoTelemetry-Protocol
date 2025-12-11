#!/usr/bin/env bash
# Phase 2 - 5% Loss Test

PORT=12000
IF=eth0     # change this if VM uses a different interface (e.g., ens33)
CSV1=NanoTelemetry_log_v1.csv
CSV2=NanoTelemetry_log_v1_expanded.csv
PCAP=capture_loss5.pcap
DURATION=30

echo "[LOSS5] Clearing old files..."
rm -f "$CSV1" "$CSV2" "$PCAP"

echo "[LOSS5] Applying 5% loss..."
sudo tc qdisc add dev $IF root netem loss 5%

echo "[LOSS5] Starting server..."
python3 server.py &
SERVER_PID=$!
sleep 1

echo "[LOSS5] Starting client..."
DURATION=$DURATION BATCH_SIZE=3 INTERVAL=0.1 python3 client.py &
CLIENT_PID=$!

echo "[LOSS5] Starting packet capture..."
sudo timeout $((DURATION+5)) tcpdump -i any udp port $PORT -w "$PCAP" >/dev/null 2>&1 &

echo "[LOSS5] Running for $DURATION seconds..."
sleep $((DURATION+2))

echo "[LOSS5] Cleanup..."
kill $CLIENT_PID 2>/dev/null
kill $SERVER_PID 2>/dev/null

echo "[LOSS5] Removing netem rule..."
sudo tc qdisc del dev $IF root

echo "[LOSS5] Done. Outputs:"
echo " → $CSV1"
echo " → $CSV2"
echo " → $PCAP"
