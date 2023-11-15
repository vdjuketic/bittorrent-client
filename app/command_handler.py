import sys
import json
import hashlib
import logging as log

from typing import Any
from . bencode import encode_bencode, decode_bencode

def handle_command(command: str) -> Any:
    if command == "decode":
        handleDecodeCommand(sys.argv[2].encode())

    elif command == "info":
        handleInfoCommand(sys.argv[2].encode())

    else:
        raise NotImplementedError(f"Unknown command {command}")
    
def handleDecodeCommand(bencoded_value):
    def bytes_to_str(data):
        if isinstance(data, bytes):
            return data.decode()

        raise TypeError(f"Type not serializable: {type(data)}")

    print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))

def handleInfoCommand(filename):
    try:
        with open(filename, 'rb') as file:
            decoded_data = decode_bencode(file.read())

            tracker_url = decoded_data['announce'].decode()
            file_length = decoded_data['info']['length']
            info_hash = hashlib.sha1(encode_bencode(decoded_data["info"])).hexdigest()

            print(f"Tracker URL: {tracker_url}")
            print(f"Length: {file_length}")
            print(f"Info Hash: {info_hash}")

    except FileNotFoundError:
        log.error(f"File {filename} not found !")