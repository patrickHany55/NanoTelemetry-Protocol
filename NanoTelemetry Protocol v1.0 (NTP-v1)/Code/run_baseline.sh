#!/usr/bin/env bash
# Phase 2 - Baseline Test (no network impairment)

PORT=12000
CSV1=NanoTelemetry_log_v1.csv
CSV2=NanoTelemetry_log_v1_expanded.csv
PCAP=capture_baseline.pcap
DURATION=30

echo "[BASELINE] Clearing old files..."
rm -f "$CSV1" "$CSV2" "$PCAP"

echo "[BASELINE] Starting server..."
python3 server.py &
SERVER_PID=$!
sleep 1

echo "[BASELINE] Starting client..."
DURATION=$DURATION BATCH_SIZE=3 INTERVAL=0.1 python3 client.py &
CLIENT_PID=$!

echo "[BASELINE] Starting packet capture..."
sudo timeout $((DURATION+5)) tcpdump -i any udp port $PORT -w "$PCAP" 
>/dev/null 2>&1 &

echo "[BASELINE] Running for $DURATION seconds..."
sleep $((DURATION+2))

echo "[BASELINE] Stopping server and client..."
kill $CLIENT_PID 2>/dev/null
kill $SERVER_PID 2>/dev/null

echo "[BASELINE] Done. Output files:"
echo " → $CSV1"
echo " → $CSV2"
echo " → $PCAP"

