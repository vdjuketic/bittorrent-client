import sys
import json
import logging as log

from typing import Any
from bencode import decode_bencode
from torrentmeta import TorrentMeta


def handle_command(command: str) -> Any:
    if command == "decode":
        handle_decode_command(sys.argv[2].encode())

    elif command == "info":
        handle_info_command(sys.argv[2].encode())

    else:
        raise NotImplementedError(f"Unknown command {command}")


def handle_decode_command(bencoded_value):
    def bytes_to_str(data):
        if isinstance(data, bytes):
            return data.decode()

        raise TypeError(f"Type not serializable: {type(data)}")

    print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))


def handle_info_command(filename):
    try:
        with open(filename, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))
            print(torrent_meta)

    except FileNotFoundError:
        log.error("File %s not found !", filename)
