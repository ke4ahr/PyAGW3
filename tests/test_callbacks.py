import pytest

def test_on_frame_callback(agwpe_client):
    payload = b"monitored data"
    frame = struct.pack('<4I10s10sI4s', 0, ord('D'), b'FROM      ', b'TO        ', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    called = []
    agwpe_client.on_frame = lambda frame: called.append(frame.data.decode('ascii', errors='ignore'))
    agwpe_client._receive_once()
    
    assert called == ["monitored data"]

def test_on_connected_data_callback(agwpe_client):
    payload = b"connected payload"
    frame = struct.pack('<4I10s10sI4s', 0, ord('d'), b'FROM      ', b'TO        ', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    received = []
    agwpe_client.on_connected_data = lambda port, call, data: received.append((port, call, data.decode('ascii', errors='ignore')))
    agwpe_client._receive_once()
    
    assert received == [(0, "FROM", "connected payload")]

def test_on_outstanding_callback(agwpe_client):
    payload = struct.pack('<I', 123)
    frame = struct.pack('<4I10s10sI4s', 1, ord('y'), b'', b'', 4, b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    outstanding = []
    agwpe_client.on_outstanding = lambda port, count: outstanding.append((port, count))
    agwpe_client._receive_once()
    
    assert outstanding == [(1, 123)]

def test_on_heard_stations_callback(agwpe_client):
    payload = b"CALL1     \x01\x00\x00\x00" + b"CALL2     \x02\x00\x00\x00" + b"\x00" * (20*14 - 28)
    frame = struct.pack('<4I10s10sI4s', 0, ord('H'), b'', b'', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    heard = []
    agwpe_client.on_heard_stations = lambda port, lst: heard.append((port, [h["callsign"] for h in lst]))
    agwpe_client._receive_once()
    
    assert heard == [(0, ["CALL1", "CALL2"])]

def test_on_extended_version_callback(agwpe_client):
    payload = b"Test Version 1.0"
    frame = struct.pack('<4I10s10sI4s', 0, ord('v'), b'', b'', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    version = []
    agwpe_client.on_extended_version = lambda v: version.append(v)
    agwpe_client._receive_once()
    
    assert version == ["Test Version 1.0"]

def test_on_memory_usage_callback(agwpe_client):
    payload = struct.pack('<II', 2048*1024, 1024*1024)  # 2048 KB free, 1024 KB used
    frame = struct.pack('<4I10s10sI4s', 0, ord('m'), b'', b'', 8, b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    mem = []
    agwpe_client.on_memory_usage = lambda m: mem.append(m)
    agwpe_client._receive_once()
    
    assert mem == [{"free_kb": 2048, "used_kb": 1024}]
