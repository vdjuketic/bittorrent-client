import logging as log
import argparse
from typing import Any

from util.bencode import decode_bencode
from models.torrentmeta import TorrentMeta
from peer.request_util import get_peers_from_tracker
from util.file_util import write_to_file
from peer.peer_control import Downloader


def handle_command(command: str) -> Any:
    parser = argparse.ArgumentParser()
    parser.add_argument("command")

    if command == "info":
        parser.add_argument("filename")

        p = parser.parse_args()
        handle_info_command(p.filename)

    elif command == "peers":
        parser.add_argument("filename")

        p = parser.parse_args()
        handle_peers_command(p.filename)

    elif command == "download":
        parser.add_argument("--output", "-o")
        parser.add_argument("torrent_file")

        p = parser.parse_args()
        handle_download_command(p.output, p.torrent_file)

    else:
        raise NotImplementedError(f"Unknown command {command}")


def handle_info_command(torrent_file):
    try:
        with open(torrent_file, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))
            print(torrent_meta)

    except FileNotFoundError:
        log.error("File %s not found !", torrent_file)
        raise FileNotFoundError()


def handle_peers_command(torrent_file):
    try:
        with open(torrent_file, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))
            get_peers_from_tracker(torrent_meta)

    except FileNotFoundError:
        log.error("File %s not found !", torrent_file)
        raise FileNotFoundError()


def handle_download_command(output_path, torrent_file):
    try:
        with open(torrent_file, "rb") as file:
            torrent_meta = TorrentMeta(decode_bencode(file.read()))

            downloader = Downloader(torrent_meta)
            content = downloader.download()

            write_to_file(content, output_path)
            print(f"Downloaded {torrent_file} downloaded to {output_path}.")

    except FileNotFoundError:
        log.error(f"File {torrent_file} not found !")
        raise FileNotFoundError()
