import pytest
from app.util.bencode import encode_bencode


def test_encode_string():
    assert encode_bencode("hello") == b"5:hello"
    assert encode_bencode("hello12345") == b"10:hello12345"


def test_encode_integer():
    assert encode_bencode(123) == b"i123e"
    assert encode_bencode(-123) == b"i-123e"


def test_encode_empty_list():
    assert encode_bencode([]) == b"le"


def test_encode_list_with_one_element():
    assert encode_bencode([123]) == b"li123ee"


def test_encode_list_with_strings():
    assert encode_bencode(["hello", "world"]) == b"l5:hello5:worlde"


def test_encode_list_with_integers():
    assert encode_bencode([123, 456]) == b"li123ei456ee"


def test_encode_list_with_mixed_types():
    assert encode_bencode(["hello", 123]) == b"l5:helloi123ee"


def test_encode_nested_lists():
    assert (
        encode_bencode(
            [
                "hello",
                123,
                ["abc", 456],
            ]
        )
        == b"l5:helloi123el3:abci456eee"
    )


def test_encode_dictionary():
    data = {"foo": "bar", "hello": 52}
    assert encode_bencode(data) == b"d3:foo3:bar5:helloi52ee"


def test_encode_nested_dictionary():
    data = {
        "inner_dict": {"key1": "value1", "key2": 42, "list_key": ["item1", "item2", 3]}
    }
    assert (
        encode_bencode(data)
        == b"d10:inner_dictd4:key16:value14:key2i42e8:list_keyl5:item15:item2i3eeee"
    )


def test_encode_raise_exception_when_input_is_not_valid():
    with pytest.raises(TypeError):
        encode_bencode(None)
