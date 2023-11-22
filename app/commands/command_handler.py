import json
import logging as log
import argparse

from typing import Any
from app.util.bencode import decode_bencode
from app.models.torrentmeta import TorrentMeta
from app.peer.request_util import get_peers_from_tracker
from app.peer.peer_client import PeerClient


def handle_command(command: str) -> Any:
    parser = argparse.ArgumentParser()
    if command == "decode":
        parser.add_argument("bencoded_value")

        p = parser.parse_args()
        handle_decode_command(p.bencoded_value)

    elif command == "info":
        parser.add_argument("filename")

        p = parser.parse_args()
        handle_info_command(p.filename)

    elif command == "peers":
        parser.add_argument("filename")

        p = parser.parse_args()
        handle_peers_command(p.filename)

    elif command == "handshake":
        parser.add_argument("filename")
        parser.add_argument("url")

        p = parser.parse_args()
        handle_handshake_command(p.filename, p.url)

    elif command == "download_piece":
        parser = argparse.ArgumentParser()
        parser.add_argument("--output", "-o")
        parser.add_argument("command")
        parser.add_argument("filename")
        parser.add_argument("piece_index")

        p = parser.parse_args()
        handle_download_piece_command(p.output, p.filename, p.piece_index)

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

            host, port = tuple(url.split(":"))

            client = PeerClient(host, port)
            client.connect()
            client.perform_handshake(torrent_meta.info_hash)

    except FileNotFoundError:
        log.error("File %s not found !", filename)


def handle_download_piece_command(location, filename, piece_index):
    try:
        try:
            with open(filename, "rb") as file:
                torrent_meta = TorrentMeta(decode_bencode(file.read()))
                peers = get_peers_from_tracker(torrent_meta)

                # for peer in peers:
                client = PeerClient(peers[0])
                client.connect()
                client.download_piece(
                    torrent_meta.info_hash,
                    torrent_meta.file_length,
                    torrent_meta.piece_length,
                    torrent_meta.piece_hashes,
                    int(piece_index),
                    location,
                )

        except FileNotFoundError:
            log.error("File %s not found !", filename)

    except FileNotFoundError:
        log.error("File %s not found !", filename)
