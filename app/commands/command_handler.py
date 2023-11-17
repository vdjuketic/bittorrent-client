import sys
import json
import struct
import hashlib
import logging as log

from typing import Any
from app.util.bencode import decode_bencode
from app.models.torrentmeta import TorrentMeta
from app.util.request_util import get_peers_from_tracker
from app.util.socketutil import send_handshake


def handle_command(command: str) -> Any:
    if command == "decode":
        handle_decode_command(sys.argv[2].encode())

    elif command == "info":
        handle_info_command(sys.argv[2].encode())

    elif command == "peers":
        handle_peers_command(sys.argv[2].encode())

    elif command == "handshake":
        handle_handshake_command(sys.argv[2].encode(), sys.argv[3].encode())

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
            get_peers_from_tracker(torrent_meta)

    except FileNotFoundError:
        log.error("File %s not found !", filename)


def handle_handshake_command(filename, url):
    try:
        with open(filename, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))
            request = generate_handshake_message(
                torrent_meta.info_hash, b"00112233445566778899"
            )

            host, port = tuple(url.decode("utf-8").split(":"))

            send_handshake(host, port, request)

    except FileNotFoundError:
        log.error("File %s not found !", filename)


def generate_handshake_message(info_hash, peer_id):
    length = struct.pack(">B", 19)
    protocol = b"BitTorrent protocol"
    reserved = b"\x00" * 8
    info_hash = hashlib.sha1(info_hash).digest()
    peer_id = peer_id

    return length + protocol + reserved + info_hash + peer_id
