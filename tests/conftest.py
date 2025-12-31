import pytest
from unittest.mock import Mock, patch
import socket

@pytest.fixture
def mock_socket():
    sock = Mock(spec=socket.socket)
    sock.connect.return_value = None
    sock.close.return_value = None
    sock.sendall.return_value = None
    sock.recv.side_effect = lambda size: b''  # Default: no data
    return sock

@pytest.fixture
def agwpe_client(mock_socket):
    from pyagw3.agwpe import AGWPEClient
    client = AGWPEClient(host="127.0.0.1", callsign="TEST")
    with patch.object(client, 'sock', mock_socket):
        client.connected = True
        yield client
        client.close()
