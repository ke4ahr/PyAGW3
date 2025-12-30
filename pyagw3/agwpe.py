# pyagw3/agwpe.py

# PyAGW3/agwpe.py
# GNU Lesser General Public License v3.0 or later
# Copyright (C) 2025-2026 Kris Kirby, KE4AHR
# SPDX-License-Identifier: LGPL-3.0-or-later
#
# AGWPE TCP/IP API client/server/serial interface
# Full implementation with unproto, connected mode, raw, outstanding frames
# TCP keepalive, login ('T'), parameters ('P'), extended version ('v'), memory usage ('m')
# Exponential backoff retry on connect

import socket
import struct
import threading
import time
import logging
import random
from typing import Optional, Callable, Dict, List

logger = logging.getLogger('AGWPE')

AGWPE_DEFAULT_PORT = 8000

class AGWPEFrame:
    """AGWPE frame structure."""
    def __init__(self):
        self.port: int = 0
        self.data_kind: bytes = b''
        self.call_from: bytes = b''
        self.call_to: bytes = b''
        self.data_len: int = 0
        self.data: bytes = b''

class AGWPEClient:
    """
    Full AGWPE TCP/IP API client.
    Supports unproto, connected mode, raw frames, outstanding queries, login, parameters, extended version, memory usage.
    """
    def __init__(self, host: str = "127.0.0.1", port: int = AGWPE_DEFAULT_PORT, callsign: str = "NOCALL"):
        self.host = host
        self.port = port
        self.callsign = callsign.ljust(10)[:10].upper().encode()
        self.sock: Optional[socket.socket] = None
        self.connected = False
        self.on_frame: Optional[Callable[[AGWPEFrame], None]] = None
        self.on_connected_data: Optional[Callable[[int, str, bytes], None]] = None
        self.on_outstanding: Optional[Callable[[int, int], None]] = None
        self.on_heard_stations: Optional[Callable[[int, List[Dict]], None]] = None
        self.on_extended_version: Optional[Callable[[str], None]] = None
        self.on_memory_usage: Optional[Callable[[Dict[str, int]], None]] = None
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.RLock()
        self._buffer = b''

    def connect(self, max_retries: int = 10, base_delay: float = 1.0) -> bool:
        """Connect with exponential backoff retry logic."""
        attempt = 0
        while attempt <= max_retries:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # Enable TCP keepalive
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                
                # Platform-specific tuning
                if hasattr(socket, 'TCP_KEEPIDLE'):
                    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                if hasattr(socket, 'TCP_KEEPINTVL'):
                    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                if hasattr(socket, 'TCP_KEEPCNT'):
                    self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
                
                self.sock.connect((self.host, self.port))
                
                # Register callsign
                self._send_frame(data_kind=b'R', call_from=self.callsign)
                
                self.connected = True
                self.thread = threading.Thread(target=self._receive_loop, daemon=True)
                self.thread.start()
                
                logger.info(f"[AGWPE] Connected to {self.host}:{self.port} as {self.callsign.decode()} (attempt {attempt + 1})")
                return True
                
            except Exception as e:
                if self.sock:
                    self.sock.close()
                    self.sock = None
                
                attempt += 1
                if attempt > max_retries:
                    logger.error(f"[AGWPE] Connection failed after {max_retries} retries: {e}")
                    return False
                
                # Exponential backoff with jitter
                delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, base_delay)
                logger.warning(f"[AGWPE] Connection attempt {attempt} failed: {e}. Retrying in {delay:.2f}s...")
                time.sleep(delay)

    def _send_frame(self, data_kind: bytes, port: int = 0, call_from: bytes = b'', call_to: bytes = b'', data: bytes = b''):
        """Send raw AGWPE frame."""
        if not self.connected or not self.sock:
            return
        
        with self.lock:
            try:
                # Header (36 bytes)
                header = bytearray(36)
                header[0:1] = data_kind
                struct.pack_into('<I', header, 4, port)
                header[8:18] = call_from.ljust(10, b' ')[:10]
                header[18:28] = call_to.ljust(10, b' ')[:10]
                struct.pack_into('<I', header, 28, len(data))
                
                self.sock.sendall(header + data)
                
                logger.debug(f"[AGWPE] Sent {data_kind.decode()} frame on port {port}")
                
            except Exception as e:
                logger.error(f"[AGWPE] Send failed: {e}")
                self.connected = False

    def send_ui(self, port: int, dest: str, src: str, pid: int, info: bytes = b''):
        """Send unproto UI frame (most common for PACSAT)."""
        self._send_frame(
            data_kind=b'D',
            port=port,
            call_from=src.upper().ljust(10)[:10].encode(),
            call_to=dest.upper().ljust(10)[:10].encode(),
            data=bytes([pid]) + info
        )

    def send_raw_unproto(self, port: int, dest: str, src: str, data: bytes):
        """Send raw unproto frame ('K')."""
        self._send_frame(
            data_kind=b'K',
            port=port,
            call_from=src.upper().ljust(10)[:10].encode(),
            call_to=dest.upper().ljust(10)[:10].encode(),
            data=data
        )

    def send_monitor(self, port: int):
        """Request monitored frames on port ('M')."""
        self._send_frame(data_kind=b'M', port=port)

    def request_outstanding(self, port: int = 0):
        """Request outstanding frames report ('Y')."""
        self._send_frame(data_kind=b'Y', port=port)

    def send_connect(self, port: int, dest: str):
        """Send connect request ('C')."""
        self._send_frame(
            data_kind=b'C',
            port=port,
            call_from=self.callsign,
            call_to=dest.upper().ljust(10)[:10].encode()
        )

    def send_disconnect(self, port: int, dest: str):
        """Send disconnect request ('D')."""
        self._send_frame(
            data_kind=b'D',
            port=port,
            call_from=self.callsign,
            call_to=dest.upper().ljust(10)[:10].encode()
        )

    def send_connected_data(self, port: int, dest: str, data: bytes):
        """Send connected data ('d')."""
        self._send_frame(
            data_kind=b'd',
            port=port,
            call_from=self.callsign,
            call_to=dest.upper().ljust(10)[:10].encode(),
            data=data
        )

    def request_heard_stations(self, port: int = 0):
        """Request heard stations list ('H')."""
        self._send_frame(data_kind=b'H', port=port)

    def send_login(self, username: str, password: str):
        """Send login frame ('T')."""
        payload = f"{username}\0{password}\0".encode('ascii')
        self._send_frame(data_kind=b'T', data=payload)

    def set_parameter(self, port: int, param_id: int, value: int):
        """Set parameter ('P')."""
        payload = struct.pack('<BI', param_id, value)
        self._send_frame(data_kind=b'P', port=port, data=payload)

    def request_extended_version(self):
        """Request extended version ('v')."""
        self._send_frame(data_kind=b'v')

    def request_memory_usage(self):
        """Request memory usage ('m')."""
        self._send_frame(data_kind=b'm')

    def _receive_loop(self):
        """Receive and parse AGWPE frames."""
        buffer = b''
        while self.connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    logger.warning("[AGWPE] Connection closed by server")
                    self.connected = False
                    break
                
                buffer += data
                
                while len(buffer) >= 36:
                    header = buffer[:36]
                    data_kind = header[0:1]
                    port = struct.unpack('<I', header[4:8])[0]
                    call_from = header[8:18].decode('ascii', errors='ignore').strip()
                    call_to = header[18:28].decode('ascii', errors='ignore').strip()
                    data_len = struct.unpack('<I', header[28:32])[0]
                    
                    if len(buffer) < 36 + data_len:
                        break
                    
                    payload = buffer[36:36 + data_len]
                    buffer = buffer[36 + data_len:]
                    
                    frame = AGWPEFrame()
                    frame.port = port
                    frame.data_kind = data_kind
                    frame.call_from = call_from.encode()
                    frame.call_to = call_to.encode()
                    frame.data_len = data_len
                    frame.data = payload
                    
                    # Dispatch
                    if data_kind in [b'D', b'K']:
                        if self.on_frame:
                            self.on_frame(frame)
                    elif data_kind == b'd':
                        if self.on_connected_data:
                            self.on_connected_data(port, call_from, payload)
                    elif data_kind == b'Y':
                        if payload and len(payload) >= 4:
                            count = struct.unpack('<I', payload[:4])[0]
                            if self.on_outstanding:
                                self.on_outstanding(port, count)
                    elif data_kind == b'H':
                        heard_list = []
                        for i in range(20):
                            if len(payload) >= (i+1)*14:
                                call = payload[i*14:i*14+10].decode('ascii', errors='ignore').strip()
                                timestamp = struct.unpack('<I', payload[i*14+10:i*14+14])[0]
                                if call:
                                    heard_list.append({"callsign": call, "last_heard": timestamp})
                        if self.on_heard_stations:
                            self.on_heard_stations(port, heard_list)
                    elif data_kind == b'v':
                        if payload:
                            version_str = payload.decode('ascii', errors='ignore').strip()
                        else:
                            version_str = "Unknown"
                        if self.on_extended_version:
                            self.on_extended_version(version_str)
                    elif data_kind == b'm':
                        if len(payload) >= 8:
                            free_mem = struct.unpack('<I', payload[0:4])[0]
                            used_mem = struct.unpack('<I', payload[4:8])[0]
                            mem_info = {"free_kb": free_mem // 1024, "used_kb": used_mem // 1024}
                        else:
                            mem_info = {"free_kb": 0, "used_kb": 0}
                        if self.on_memory_usage:
                            self.on_memory_usage(mem_info)
                    elif data_kind in [b'C', b'c', b'D']:
                        if self.on_frame:
                            self.on_frame(frame)
                    
                    logger.debug(f"[AGWPE] Received {data_kind.decode()} frame from {call_from} to {call_to}")
                    
            except Exception as e:
                logger.error(f"[AGWPE] Receive error: {e}")
                self.connected = False
                break

    def close(self):
        """Close connection."""
        self.connected = False
        if self.sock:
            self.sock.close()
        logger.info("[AGWPE] Disconnected")

# DOC: Full AGWPE TCP client with unproto, connected mode, raw frames, outstanding queries
# DOC: Supports all implemented frame types from current project
# DOC: Single application only - multiple app support requires further research
