import pytest
import socket

def test_receive_connection_closed(agwpe_client, mock_socket):
    mock_socket.recv.return_value = b''  # Empty recv indicates EOF
    agwpe_client._receive_once()
    assert not agwpe_client.connected

def test_receive_error_disconnects(agwpe_client, mock_socket):
    mock_socket.recv.side_effect = ConnectionResetError
    agwpe_client._receive_once()
    assert not agwpe_client.connected

def test_send_when_disconnected(agwpe_client, mock_socket):
    agwpe_client.connected = False
    agwpe_client._send_frame(data_kind=b'D', data=b'test')
    mock_socket.sendall.assert_not_called()

def test_partial_header_buffering(agwpe_client, mock_socket):
    # Send first 20 bytes of header, then rest
    partial_header = struct.pack('<4I', 0, ord('D'), 0, 0)[:20]
    full_header = struct.pack('<4I10s10sI4s', 0, ord('D'), b'FROM      ', b'TO        ', 10, b'')
    payload = b'1234567890'
    
    agwpe_client.sock.recv.side_effect = [partial_header, full_header[20:] + payload]
    
    frames = []
    agwpe_client.on_frame = lambda f: frames.append(f)
    
    agwpe_client._receive_once()  # Buffers partial header
    agwpe_client._receive_once()  # Completes and processes
    
    assert len(frames) == 1
    assert frames[0].data == payload

def test_multiple_frames_in_buffer(agwpe_client, mock_socket):
    payload1 = b"first frame"
    frame1 = struct.pack('<4I10s10sI4s', 0, ord('D'), b'FROM1     ', b'TO1       ', len(payload1), b'') + payload1
    
    payload2 = b"second frame"
    frame2 = struct.pack('<4I10s10sI4s', 0, ord('D'), b'FROM2     ', b'TO2       ', len(payload2), b'') + payload2
    
    agwpe_client.sock.recv.return_value = frame1 + frame2
    
    frames = []
    agwpe_client.on_frame = lambda f: frames.append(f.data.decode('ascii', errors='ignore'))
    agwpe_client._receive_once()
    
    assert frames == ["first frame", "second frame"]

def test_invalid_data_kind_ignored(agwpe_client, mock_socket):
    payload = b"invalid"
    frame = struct.pack('<4I10s10sI4s', 0, ord('Z'), b'', b'', len(payload), b'') + payload
    agwpe_client.sock.recv.return_value = frame
    
    called = {
        'frame': False,
        'connected': False,
        'outstanding': False,
        'heard': False,
        'version': False,
        'memory': False
    }
    
    agwpe_client.on_frame = lambda f: called.__setitem__('frame', True)
    agwpe_client.on_connected_data = lambda *args: called.__setitem__('connected', True)
    agwpe_client.on_outstanding = lambda *args: called.__setitem__('outstanding', True)
    agwpe_client.on_heard_stations = lambda *args: called.__setitem__('heard', True)
    agwpe_client.on_extended_version = lambda *args: called.__setitem__('version', True)
    agwpe_client.on_memory_usage = lambda *args: called.__setitem__('memory', True)
    
    agwpe_client._receive_once()
    
    assert all(not v for v in called.values())  # No callback should fire
