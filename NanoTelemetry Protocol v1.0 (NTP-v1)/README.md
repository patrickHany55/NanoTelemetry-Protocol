# NanoTelemetry Protocol v1.0 (NTP-v1)
## Phase 1 Prototype

### Requirements
- Python 3.x  
- Runs on macOS, Linux, or Windows

### Files
- server.py  → UDP collector (logs CSV)
- client.py  → IoT sensor (sends DATA/HEARTBEAT)
- run_baseline.sh  → automates baseline test

### How to Run
1. Make script executable:
   chmod +x run_baseline.sh
2. Run baseline:
   ./run_baseline.sh
3. After run:
   - Check NanoTelemetry_log_v1.csv  
   - Confirm rows similar to:  
     `device_id,seq,timestamp,arrival_time,duplicate_flag,gap_flag`

### Notes
- Port number = 12000  
- Both sockets close automatically at end.  
- Tested on macOS.
