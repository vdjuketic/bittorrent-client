import sys
import json
import logging as log
from typing import Any

from . decoder import decode_bencode

def handle_command(command: str, *args: str) -> Any:
    if command == "decode":
        handleDecodeCommand()

    elif command == "info":
        handleInfoCommand()

    else:
        raise NotImplementedError(f"Unknown command {command}")
    
def handleDecodeCommand():
    bencoded_value = sys.argv[2].encode()

    def bytes_to_str(data):
        if isinstance(data, bytes):
            return data.decode()

        raise TypeError(f"Type not serializable: {type(data)}")

    print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))

def handleInfoCommand():
    try:
        filename = sys.argv[2].encode()
        with open(filename, 'rb') as file:
            decoded_data = decode_bencode(file.read())

            tracker_url = decoded_data['announce'].decode()
            file_length = decoded_data['info']['length']

            print(f"Tracker URL: {tracker_url}")
            print(f"Length: {file_length}")

    except FileNotFoundError:
        log.error(f"File {sys.argv[2]} not found !")