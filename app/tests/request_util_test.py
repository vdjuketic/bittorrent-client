import pytest
from app.util.request_util import decode_address


def test_decode_address_single_peer():
    peers = [178, 62, 82, 89, 201, 14]
    result = list(decode_address(peers))
    assert result == [("178.62.82.89", 51470)]


def test_decode_address_multiple_peers():
    peers = [178, 62, 82, 89, 201, 14, 165, 232, 33, 77, 201, 11]
    result = list(decode_address(peers))
    assert result == [("178.62.82.89", 51470), ("165.232.33.77", 51467)]


def test_decode_address_empty_input():
    peers = []
    result = list(decode_address(peers))
    assert result == []


def test_decode_address_invalid_input_length():
    peers = [178, 62, 82, 89, 14]  # Incomplete peer data
    with pytest.raises(IndexError):
        list(decode_address(peers))


def test_decode_address_invalid_ip_range():
    peers = [300, 62, 82, 89, 201, 14]  # Invalid IP range
    with pytest.raises(ValueError):
        list(decode_address(peers))
