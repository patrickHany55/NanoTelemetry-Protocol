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
