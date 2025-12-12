#!/usr/bin/env bash
IF=eth0
echo "[CLEANUP] Removing any existing qdisc rules..."
sudo tc qdisc del dev $IF root 2>/dev/null
echo "[CLEANUP] Done."
