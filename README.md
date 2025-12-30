# PyAGW3

A modern Python 3 implementation of the AGWPE TCP/IP API client for amateur packet radio applications.

## Features
- Full support for unproto, connected mode, and raw frames
- Callsign registration, monitoring, heard stations, outstanding frames
- Extended version and memory usage queries
- Exponential backoff reconnect with TCP keepalive
- Thread-safe with comprehensive error handling
- Callback-based event handling

## Installation

    pip install .

Or for development:

    pip install -e .

## Basic Usage

    from pyagw3 import AGWPEClient

    client = AGWPEClient(host="127.0.0.1", port=8000, callsign="YOURCALL")

    def on_monitored(frame):
        print(f"Monitored [{frame.call_from.decode().strip()}->{frame.call_to.decode().strip()}]: {frame.data}")

    client.on_frame = on_monitored
    client.connect()
    print("Connected. Monitoring...")
    # Run as needed
    client.close()

See the `examples/` directory for more complete scripts:
- `basic_connect.py`
- `unproto_beacon.py`
- `connected_mode.py`
- `query_server.py`
- `raw_monitoring.py`

## Documentation
Full API reference and usage guide available in the `docs/` directory. Build with Sphinx:

    cd docs
    sphinx-build -b html . _build/html

## Testing
Run the comprehensive test suite with pytest:

    pip install pytest
    pytest tests/

## Author
Kris Kirby, KE4AHR

## License
GNU Lesser General Public License v3.0 or later (LGPL-3.0-or-later)

See the LICENSE file for full text.
Copyright (C) 2025-2026 Kris Kirby, KE4AHR
