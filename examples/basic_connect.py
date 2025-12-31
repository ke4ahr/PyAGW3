#!/usr/bin/env python3
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Basic connection example for PyAGW3.

Connects to a local AGWPE-compatible server (e.g., Dire Wolf, UZ7HO SoundModem),
registers the callsign, enables monitoring, and prints received monitored frames.
"""

from pyagw3 import AGWPEClient
import time
import logging

# Optional: enable debug logging
logging.basicConfig(level=logging.INFO)

def on_monitored(frame):
    """Callback for monitored frames (unproto UI frames)."""
    from_call = frame.call_from.decode('ascii', errors='ignore').strip()
    to_call = frame.call_to.decode('ascii', errors='ignore').strip()
    data = frame.data
    print(f"[{from_call} > {to_call}] {data!r}")

def main():
    # Replace with your actual callsign
    MYCALL = "N0CALL"

    client = AGWPEClient(
        host="127.0.0.1",
        port=8000,
        callsign=MYCALL
    )

    # Set callback for monitored frames
    client.on_frame = on_monitored

    print(f"Connecting to AGWPE server as {MYCALL}...")
    if not client.connect():
        print("Failed to connect.")
        return

    print("Connected. Monitoring for 60 seconds (Ctrl+C to stop)...")
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping...")

    client.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()
