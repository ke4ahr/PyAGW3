#!/usr/bin/env python3
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Unproto beacon example for PyAGW3.

Sends periodic unproto (UI) frames – useful for beacons, APRS position reports,
or general unconnected packet transmission.
"""

from pyagw3 import AGWPEClient
import time
import logging

# Optional: enable info logging
logging.basicConfig(level=logging.INFO)

def main():
    # Replace with your actual callsign
    MYCALL = "N0CALL"
    # Destination – common choices: "BEACON", "APRS", "CQ", "ID"
    DEST = "BEACON"
    # Port number on the AGWPE server (0 is usually the first radio port)
    PORT = 0

    client = AGWPEClient(
        host="127.0.0.1",
        port=8000,
        callsign=MYCALL
    )

    print(f"Connecting to AGWPE server as {MYCALL}...")
    if not client.connect():
        print("Failed to connect.")
        return

    print(f"Connected. Sending unproto beacons every 60 seconds to {DEST} (Ctrl+C to stop)...")

    try:
        while True:
            beacon_text = f"{MYCALL}>APRS:PyAGW3 unproto beacon test at {time.strftime('%H:%M:%S')}"
            client.send_ui(
                port=PORT,
                dest=DEST,
                src=MYCALL,
                pid=0xF0,  # No Layer 3 protocol (common for beacons)
                info=beacon_text.encode('ascii')
            )
            print(f"[{time.strftime('%H:%M:%S')}] Beacon sent: {beacon_text}")
            time.sleep(60)  # Beacon interval – adjust as needed
    except KeyboardInterrupt:
        print("\nStopping beacon...")

    client.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()
