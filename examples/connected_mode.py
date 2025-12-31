#!/usr/bin/env python3
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later

"""
Connected mode example for PyAGW3.

Demonstrates establishing an AX.25 connected session:
- Send connect request
- Send data when connected
- Receive connected data via callback
- Disconnect gracefully
"""

from pyagw3 import AGWPEClient
import time
import logging

# Optional: enable info/debug logging
logging.basicConfig(level=logging.INFO)

def on_connected_data(port: int, from_call: str, data: bytes):
    """Callback for received connected-mode data."""
    print(f"[Connected] From {from_call} on port {port}: {data!r}")

def main():
    # Replace with your actual callsign
    MYCALL = "N0CALL"
    # Target station callsign for connection
    TARGET = "TARGET-1"
    # Radio port on the AGWPE server
    PORT = 0

    client = AGWPEClient(
        host="127.0.0.1",
        port=8000,
        callsign=MYCALL
    )

    # Set callback for connected data
    client.on_connected_data = on_connected_data

    print(f"Connecting to AGWPE server as {MYCALL}...")
    if not client.connect():
        print("Failed to connect.")
        return

    print(f"Sending connect request to {TARGET} on port {PORT}...")
    client.send_connect(port=PORT, dest=TARGET)

    print("Waiting 30 seconds for activity (send/receive)...")
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    # Send some connected data (if connected)
    message = b"Hello from PyAGW3 connected mode!"
    print(f"Sending connected data to {TARGET}: {message!r}")
    client.send_connected_data(port=PORT, dest=TARGET, data=message)

    time.sleep(5)  # Allow delivery

    print(f"Sending disconnect request to {TARGET}...")
    client.send_disconnect(port=PORT, dest=TARGET)

    time.sleep(2)

    client.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()
