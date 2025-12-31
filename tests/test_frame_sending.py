import struct
import pytest

def test_send_register_callsign(agwpe_client, mock_socket):
    agwpe_client._send_frame(data_kind=b'R', call_from=b'TEST     ')
    expected_header = struct.pack('<4I10s10sI4s', 0, ord('R'), b'', b'', 0, b'')
    expected = expected_header[:28] + b'TEST     ' + expected_header[38:]
    mock_socket.sendall.assert_called_once_with(expected)

def test_send_ui_unproto(agwpe_client, mock_socket):
    agwpe_client.send_ui(port=0, dest="DEST", src="SOURCE", pid=0xF0, info=b"hello")
    header = bytearray(36)
    header[0:1] = b'D'
    struct.pack_into('<I', header, 4, 0)
    header[8:18] = b'SOURCE    '
    header[18:28] = b'DEST      '
    struct.pack_into('<I', header, 28, 6)  # pid + data length
    expected = header + b'\xf0hello'
    mock_socket.sendall.assert_called_with(expected)

def test_send_raw_unproto(agwpe_client, mock_socket):
    raw_data = b'\x00\x01\x02'
    agwpe_client.send_raw_unproto(port=0, dest="DEST", src="SOURCE", data=raw_data)
    header = bytearray(36)
    header[0:1] = b'K'
    struct.pack_into('<I', header, 4, 0)
    header[8:18] = b'SOURCE    '
    header[18:28] = b'DEST      '
    struct.pack_into('<I', header, 28, len(raw_data))
    expected = header + raw_data
    mock_socket.sendall.assert_called_with(expected)

def test_request_outstanding(agwpe_client, mock_socket):
    agwpe_client.request_outstanding(port=1)
    header = bytearray(36)
    header[0:1] = b'Y'
    struct.pack_into('<I', header, 4, 1)
    struct.pack_into('<I', header, 28, 0)
    mock_socket.sendall.assert_called_with(header)

def test_request_heard_stations(agwpe_client, mock_socket):
    agwpe_client.request_heard_stations(port=0)
    header = bytearray(36)
    header[0:1] = b'H'
    struct.pack_into('<I', header, 4, 0)
    struct.pack_into('<I', header, 28, 0)
    mock_socket.sendall.assert_called_with(header)

def test_request_extended_version(agwpe_client, mock_socket):
    agwpe_client.request_extended_version()
    header = bytearray(36)
    header[0:1] = b'v'
    struct.pack_into('<I', header, 28, 0)
    mock_socket.sendall.assert_called_with(header)

def test_request_memory_usage(agwpe_client, mock_socket):
    agwpe_client.request_memory_usage()
    header = bytearray(36)
    header[0:1] = b'm'
    struct.pack_into('<I', header, 28, 0)
    mock_socket.sendall.assert_called_with(header)
