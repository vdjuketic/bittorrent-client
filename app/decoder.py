def decode_bencode(bencoded_value):
    return decode_bencode_with_end_delimeter(bencoded_value)[0]

def decode_bencode_with_end_delimeter(bencoded_value):
    #print("decoding: ", bencoded_value)
    if chr(bencoded_value[0]).isdigit():
        return decode_string(bencoded_value)
    
    elif chr(bencoded_value[0]) == "i":
        return decode_int(bencoded_value)

    elif chr(bencoded_value[0]) == "l":
        return decode_list(bencoded_value)
    
    elif chr(bencoded_value[0]) == "d":
        return decode_dictionary(bencoded_value)
        
    else:
        raise NotImplementedError("Only strings, digits and lists are supported at the moment")

def decode_string(bencoded_string):
    #print("decoding string: ", bencoded_string)
    colon_index = bencoded_string.find(b":")
    if colon_index == -1:
        raise ValueError("Invalid encoded value")
    
    length = int(bencoded_string[:colon_index])
    decoded_string = bencoded_string[colon_index+1:colon_index + 1 + length]

    end_delimeter = colon_index + 1 + length

    return decoded_string, end_delimeter

def decode_int(bencoded_int):
    #print("decoding int: ", bencoded_int)
    end_delimeter = bencoded_int.find(b"e")
    bencoded_int = bencoded_int[1:end_delimeter]

    decoded_int = int(bencoded_int.replace(b"~", b"-"))
    
    return decoded_int, end_delimeter + 1

def decode_list(bencoded_list):
    #print("decoding list: ", bencoded_list)
    decoded_list = []
    current_char = 1

    while chr(bencoded_list[current_char]) != "e":
        decoded_part, chars_read = decode_bencode_with_end_delimeter(bencoded_list[current_char:])
        decoded_list.append(decoded_part)
        current_char += chars_read

    #print("decoding list: ", bencoded_list)
    return decoded_list, current_char + 1

def decode_dictionary(bencoded_dictionary):
    decoded_dictionary = {}
    current_char = 1

    while chr(bencoded_dictionary[current_char]) != "e":
        decoded_key, key_chars_read = decode_bencode_with_end_delimeter(bencoded_dictionary[current_char:])
        current_char += key_chars_read

        decoded_value, value_chars_read = decode_bencode_with_end_delimeter(bencoded_dictionary[current_char:])
        current_char += value_chars_read

        decoded_dictionary[decoded_key.decode("utf-8")] = decoded_value

    return decoded_dictionary, current_char + 1