PORT=12000
CSV="NanoTelemetry_log_v1.csv"

echo "Cleaning old CSV..."
rm -f "$CSV"

echo "Starting server..."
python3 server.py &
SERVER_PID=$!
sleep 1

echo "Starting one client..."
python3 client.py &
CLIENT_PID=$!

echo "Running for 30 seconds..."
sleep 30

echo "Stopping server and client..."
kill $SERVER_PID 2>/dev/null
kill $CLIENT_PID 2>/dev/null
sleep 1

echo "Done. Check $CSV for logged packets."
