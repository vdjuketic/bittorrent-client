import pytest
from decoder import decode_bencode

def test_decode_string():
    assert decode_bencode(b"5:hello") == b"hello"
    assert decode_bencode(b"10:hello12345") == b"hello12345"

def test_decode_integer():
    assert decode_bencode(b"i123e") == 123
    assert decode_bencode(b"i-123e") == -123

def test_decode_empty_list():
    assert decode_bencode(b"le") == []

def test_decode_list_with_one_element():
    assert decode_bencode(b"li123ee") == [123]

def test_decode_list_with_strings():
    assert decode_bencode(b"l5:hello5:worlde") == [b"hello", b"world"]

def test_decode_list_with_integers():
    assert decode_bencode(b"li123ei456ee") == [123, 456]

def test_decode_list_with_mixed_types():
    assert decode_bencode(b"l5:helloi123ee") == [b"hello", 123]

def test_decode_nested_lists():
    assert decode_bencode(b"l5:helloi123el3:abci456eee") == [
        b"hello",
        123,
        [b"abc", 456],
    ]

def test_decode_dictionary():
    assert decode_bencode(b"d3:foo3:bar5:helloi52ee") == {
        "foo": b"bar",
        "hello": 52
    }

def test_decode_raise_exception_when_input_is_not_valid():
    with pytest.raises(NotImplementedError):
        decode_bencode(b"e")