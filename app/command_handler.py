import sys
import json
import requests
import logging as log

from typing import Any
from . bencode import decode_bencode
from . torrentmeta import TorrentMeta
from . tracker_dto import TrackerDTO


def handle_command(command: str) -> Any:
    if command == "decode":
        handle_decode_command(sys.argv[2].encode())

    elif command == "info":
        handle_info_command(sys.argv[2].encode())

    elif command == "peers":
        handle_peers_command(sys.argv[2].encode())

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

def handle_peers_command(filename):
    try:
        with open(filename, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))
            tracker_dto = TrackerDTO(torrent_meta)

            response = requests.get(
                url = torrent_meta.tracker_url, params = tracker_dto.to_json())

            peers = decode_peers(response.content)
            for ip, port in peers:
                print(f"{ip}:{port}")

    except FileNotFoundError:
        log.error("File %s not found !", filename)

def decode_peers(data):
    decoded_value = decode_bencode(data)
    return decode_address(decoded_value["peers"])

def decode_address(peers):
    length = 6
    for i in range(0, len(peers), length):
        ip = ".".join(str(b) for b in peers[i : i + 4])
        port = peers[i + 4] << 8 | peers[i + 5]
        yield ip, port
