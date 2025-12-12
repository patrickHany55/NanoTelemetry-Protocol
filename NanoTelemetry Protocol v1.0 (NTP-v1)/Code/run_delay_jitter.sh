#!/usr/bin/env bash
# Delay 100ms ±10ms Test

PORT=12000
IF=eth0
CSV1=NanoTelemetry_log_v1.csv
CSV2=NanoTelemetry_log_v1_expanded.csv
PCAP=capture_delay_jitter.pcap
DURATION=30

echo "[DELAY] Clearing old files..."
rm -f "$CSV1" "$CSV2" "$PCAP"

echo "[DELAY] Applying delay 100ms jitter 10ms..."
sudo tc qdisc add dev $IF root netem delay 100ms 10ms

echo "[DELAY] Starting server..."
python3 server.py &
SERVER_PID=$!
sleep 1

echo "[DELAY] Starting client..."
DURATION=$DURATION BATCH_SIZE=3 INTERVAL=0.1 python3 client.py &
CLIENT_PID=$!

echo "[DELAY] Starting packet capture..."
sudo timeout $((DURATION+5)) tcpdump -i any udp port $PORT -w "$PCAP" >/dev/null 2>&1 &

echo "[DELAY] Running for $DURATION seconds..."
sleep $((DURATION+2))

echo "[DELAY] Cleanup..."
kill $CLIENT_PID 2>/dev/null
kill $SERVER_PID 2>/dev/null

echo "[DELAY] Removing netem rule..."
sudo tc qdisc del dev $IF root

echo "[DELAY] Done. Outputs:"
echo " → $CSV1"
echo " → $CSV2"
echo " → $PCAP"
