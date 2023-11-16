import logging as log


def encode_bencode(data):
    log.info(f"encoding : {data}")

    if isinstance(data, int):
        return f"i{data}e".encode()
    elif isinstance(data, str):
        return f"{len(data)}:{data}".encode()
    elif isinstance(data, bytes):
        return f"{len(data)}:".encode() + data
    elif isinstance(data, list):
        res = "l".encode()
        for i in data:
            res += encode_bencode(i)
        res += "e".encode()
        return res
    elif isinstance(data, dict):
        res = "d".encode()
        for key, val in data.items():
            res += encode_bencode(key) + encode_bencode(val)
        res += "e".encode()
        return res
    else:
        raise TypeError("Encoding type not supported")


def decode_bencode(bencoded_value):
    return decode_bencode_with_end_delimeter(bencoded_value)[0]


def decode_bencode_with_end_delimeter(bencoded_value):
    if chr(bencoded_value[0]).isdigit():
        return decode_string(bencoded_value)

    elif chr(bencoded_value[0]) == "i":
        return decode_int(bencoded_value)

    elif chr(bencoded_value[0]) == "l":
        return decode_list(bencoded_value)

    elif chr(bencoded_value[0]) == "d":
        return decode_dictionary(bencoded_value)

    else:
        raise NotImplementedError(
            "Only strings, digits and lists are supported at the moment"
        )


def decode_string(bencoded_string):
    log.debug(f"decoding string: {bencoded_string}")

    colon_index = bencoded_string.find(b":")
    if colon_index == -1:
        raise ValueError("Invalid encoded value")

    length = int(bencoded_string[:colon_index])
    decoded_string = bencoded_string[colon_index + 1 : colon_index + 1 + length]

    end_delimeter = colon_index + 1 + length

    return decoded_string, end_delimeter


def decode_int(bencoded_int):
    log.debug(f"decoding int: {bencoded_int}")

    end_delimeter = bencoded_int.find(b"e")
    bencoded_int = bencoded_int[1:end_delimeter]

    decoded_int = int(bencoded_int.replace(b"~", b"-"))

    return decoded_int, end_delimeter + 1


def decode_list(bencoded_list):
    log.debug(f"decoding list: {bencoded_list}")

    decoded_list = []
    current_char = 1

    while chr(bencoded_list[current_char]) != "e":
        decoded_part, chars_read = decode_bencode_with_end_delimeter(
            bencoded_list[current_char:]
        )
        decoded_list.append(decoded_part)
        current_char += chars_read

    return decoded_list, current_char + 1


def decode_dictionary(bencoded_dictionary):
    log.debug(f"decoding dictionary: {bencoded_dictionary}")

    decoded_dictionary = {}
    current_char = 1

    while chr(bencoded_dictionary[current_char]) != "e":
        decoded_key, key_chars_read = decode_bencode_with_end_delimeter(
            bencoded_dictionary[current_char:]
        )
        current_char += key_chars_read

        decoded_value, value_chars_read = decode_bencode_with_end_delimeter(
            bencoded_dictionary[current_char:]
        )
        current_char += value_chars_read

        decoded_dictionary[decoded_key.decode("utf-8")] = decoded_value

    return decoded_dictionary, current_char + 1
