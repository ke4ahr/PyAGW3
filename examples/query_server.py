#!/usr/bin/env python3
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later
"""
Query server example for PyAGW3.

Demonstrates querying various server information:
- Outstanding frames ('y')
- Heard stations list ('H')
- Extended version string ('v')
- Memory usage ('m')
"""

from pyagw3 import AGWPEClient
import time
import logging

# Optional: enable info logging
logging.basicConfig(level=logging.INFO)

def main():
    # Replace with your actual callsign
    MYCALL = "N0CALL"
    # Radio port to query (0 is usually the first port)
    PORT = 0

    client = AGWPEClient(
        host="127.0.0.1",
        port=8000,
        callsign=MYCALL
    )

    # Set up callbacks for query responses
    def on_outstanding(port: int, count: int):
        print(f"Port {port}: {count} outstanding frames waiting for TX")

    def on_heard_stations(port: int, heard_list):
        print(f"Port {port} heard stations ({len(heard_list)}):")
        for entry in heard_list:
            call = entry["callsign"]
            last = entry["last_heard"]
            print(f"  {call} - last heard {last} seconds ago")

    def on_extended_version(version: str):
        print(f"Server extended version: {version}")

    def on_memory_usage(mem_info):
        print(f"Server memory: {mem_info['free_kb']} KB free, {mem_info['used_kb']} KB used")

    client.on_outstanding = on_outstanding
    client.on_heard_stations = on_heard_stations
    client.on_extended_version = on_extended_version
    client.on_memory_usage = on_memory_usage

    print(f"Connecting to AGWPE server as {MYCALL}...")
    if not client.connect():
        print("Failed to connect.")
        return

    print("Connected. Sending queries...")

    client.request_outstanding(port=PORT)
    client.request_heard_stations(port=PORT)
    client.request_extended_version()
    client.request_memory_usage()

    print("Waiting 10 seconds for responses...")
    time.sleep(10)

    client.close()
    print("Disconnected.")

if __name__ == "__main__":
    main()
