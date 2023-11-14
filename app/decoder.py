def decode_bencode(bencoded_value):
    return decode_bencode_with_end_delimeter(bencoded_value)[0]

def decode_bencode_with_end_delimeter(bencoded_value):
    while len(bencoded_value) > 0:
        if chr(bencoded_value[0]).isdigit():
            return decode_string(bencoded_value)
        
        elif chr(bencoded_value[0]) == "i":
            return decode_int(bencoded_value)

        elif chr(bencoded_value[0]) == "l":
            return decode_list(bencoded_value)
            
        else:
            raise NotImplementedError("Only strings, digits and lists are supported at the moment")

def decode_string(bencoded_string):
    colon_index = bencoded_string.find(b":")
    if colon_index == -1:
        raise ValueError("Invalid encoded value")
    
    length = int(bencoded_string[:colon_index])
    decoded_string = bencoded_string[colon_index+1:colon_index + 1 + length]

    end_delimeter = colon_index + 1 + length

    return decoded_string, end_delimeter

def decode_int(bencoded_int):
    end_delimeter = bencoded_int.find(b"e")
    bencoded_int = bencoded_int[1:end_delimeter]

    decoded_int = int(bencoded_int.replace(b"~", b"-"))
    
    return decoded_int, end_delimeter + 1

def decode_list(bencoded_list):
    decoded_list = []
    list_end_delimeter = 0

    bencoded_list = bencoded_list[1:]
    while chr(bencoded_list[0]) != "e":
        decoded_part, end_delimeter = decode_bencode_with_end_delimeter(bencoded_list)
        decoded_list.append(decoded_part)
        list_end_delimeter += end_delimeter

        bencoded_list = bencoded_list[end_delimeter:]

    return decoded_list, list_end_delimeter


