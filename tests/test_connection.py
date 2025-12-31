import pytest
import time
from unittest.mock import patch, call

def test_connect_success(agwpe_client, mock_socket):
    agwpe_client.connect(max_retries=1)
    mock_socket.connect.assert_called_once()
    mock_socket.setsockopt.assert_called()  # Keepalive checks

def test_connect_exponential_backoff():
    from pyagw3.agwpe import AGWPEClient
    client = AGWPEClient()
    with patch('socket.socket') as mock_sock_class, \
         patch('time.sleep') as mock_sleep:
        mock_sock = mock_sock_class.return_value
        mock_sock.connect.side_effect = [ConnectionRefusedError, None]
        client.connect(max_retries=2, base_delay=0.1)
        mock_sleep.assert_called_with(0.2)  # 2x base delay

def test_close(agwpe_client, mock_socket):
    agwpe_client.close()
    assert not agwpe_client.connected
    mock_socket.close.assert_called_once()
