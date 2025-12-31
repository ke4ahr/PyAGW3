#!/usr/bin/env python3
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Raw monitoring example for PyAGW3.

Enables raw AX.25 frame monitoring ('k' frame type) on a specified port.
This receives complete raw frames as transmitted on air (including headers),
useful for deep packet analysis or custom decoding.
"""

from pyagw3 import AGWPEClient
import time
import logging

# Optional: enable debug logging to see all frame traffic
logging.basicConfig(level=logging.INFO)

def on_raw_frame(frame):
    """Callback for raw monitored frames ('K' type)."""
    from_call = frame.call_from.decode('ascii', errors='ignore').strip()
    to_call = frame.call_to.decode('ascii', errors='ignore').strip()
    raw_data = frame.data.hex(' ')  # Display as hex for visibility
    print(f"[Raw] Port {frame.port} | {from_call} > {to_call} | {raw_data}")

def main():
    # Replace with your actual callsign
    MYCALL = "N0CALL"
    # Radio port to monitor (0 is usually the first port)
    PORT = 0

    client = AGWPEClient(
        host="127.0.0.1",
        port=8000,
        callsign=MYCALL
    )

    # Use the general on_frame callback for raw frames ('K')
    client.on_frame = on_raw_frame

    print(f"Connecting to AGWPE server as {MYCALL}...")
    if not client.connect():
        print("Failed to connect.")
        return

    print(f"Connected. Enabling raw monitoring on port {PORT}...")
    # Send 'k' to enable raw frames (some servers use 'K' or separate command)
    # Many servers enable raw with monitoring 'M' + raw preference; here we assume 'K' works
    client._send_frame(data_kind=b'k', port=PORT)  # Direct raw enable if supported

    print("Monitoring raw frames for 60 seconds (Ctrl+C to stop)...")
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping...")

    client.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()
