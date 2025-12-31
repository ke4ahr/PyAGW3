import pytest
import struct

def test_parse_outstanding_frames(agwpe_client):
    payload = struct.pack('<I', 42)
    frame = struct.pack('<4I10s10sI4s', 0, ord('y'), b'', b'', 4, b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    received = []
    agwpe_client.on_outstanding = lambda port, count: received.append((port, count))
    agwpe_client._receive_once()
    
    assert received == [(0, 42)]

def test_parse_heard_list(agwpe_client):
    payload = b"CALL1     \x01\x00\x00\x00" + b"CALL2     \x02\x00\x00\x00" + b"\x00" * (20*14 - 28)
    frame = struct.pack('<4I10s10sI4s', 0, ord('H'), b'', b'', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    heard = []
    agwpe_client.on_heard_stations = lambda port, lst: heard.append(lst)
    agwpe_client._receive_once()
    
    assert len(heard[0]) == 2
    assert heard[0][0]["callsign"] == "CALL1"

def test_parse_extended_version(agwpe_client):
    payload = b"AGWPE v1.2.3"
    frame = struct.pack('<4I10s10sI4s', 0, ord('v'), b'', b'', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    version = [None]
    agwpe_client.on_extended_version = lambda v: version.__setitem__(0, v)
    agwpe_client._receive_once()
    
    assert version[0] == "AGWPE v1.2.3"

def test_parse_memory_usage(agwpe_client):
    payload = struct.pack('<II', 1048576, 524288)  # 1MB free, 512KB used
    frame = struct.pack('<4I10s10sI4s', 0, ord('m'), b'', b'', 8, b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    mem_info = [None]
    agwpe_client.on_memory_usage = lambda m: mem_info.__setitem__(0, m)
    agwpe_client._receive_once()
    
    assert mem_info[0] == {"free_kb": 1024, "used_kb": 512}

def test_parse_connected_data(agwpe_client):
    payload = b"Connected data payload"
    frame = struct.pack('<4I10s10sI4s', 0, ord('d'), b'FROM      ', b'TO        ', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    received = []
    agwpe_client.on_connected_data = lambda port, call, data: received.append((port, call, data))
    agwpe_client._receive_once()
    
    assert received == [(0, "FROM", payload)]

def test_parse_monitored_frame(agwpe_client):
    payload = b"Monitored UI data"
    frame = struct.pack('<4I10s10sI4s', 0, ord('D'), b'FROM      ', b'TO        ', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    frames = []
    agwpe_client.on_frame = lambda f: frames.append(f)
    agwpe_client._receive_once()
    
    assert len(frames) == 1
    assert frames[0].data_kind == b'D'
    assert frames[0].data == payload

def test_parse_raw_frame(agwpe_client):
    raw_payload = b'\x00\x01\x02\x03\x04'
    frame = struct.pack('<4I10s10sI4s', 0, ord('K'), b'RAWFROM   ', b'RAWTO     ', len(raw_payload), b'') + raw_payload
    agwpe_client.sock.recv.return_value = frame
    
    frames = []
    agwpe_client.on_frame = lambda f: frames.append(f)
    agwpe_client._receive_once()
    
    assert len(frames) == 1
    assert frames[0].data_kind == b'K'
    assert frames[0].data == raw_payload

def test_partial_frame_buffering(agwpe_client):
    # Simulate split receive: header + partial payload, then rest
    header = struct.pack('<4I10s10sI', 0, ord('D'), b'FROM      ', b'TO        ', 10)
    partial_payload = b'part1'
    full_payload = b'partial_data'
    
    agwpe_client.sock.recv.side_effect = [
        header + partial_payload,  # First recv: incomplete
        full_payload[len(partial_payload):]  # Second: completes it
    ]
    
    frames = []
    agwpe_client.on_frame = lambda f: frames.append(f)
    
    agwpe_client._receive_once()  # First call gets partial, buffers
    agwpe_client._receive_once()  # Second completes and dispatches
    
    assert len(frames) == 1
    assert frames[0].data == full_payload
