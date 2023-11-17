import hashlib
from dataclasses import dataclass
from typing import List

from . bencode import encode_bencode


@dataclass
class TorrentMeta:
    tracker_url: str
    file_length: int
    info_hash: str
    piece_length: int
    piece_hashes: List[str]

    def __init__(self, data):
        self.tracker_url = data["announce"].decode()
        self.file_length = data["info"]["length"]
        self.info_hash = hashlib.sha1(encode_bencode(data["info"])).digest()
        self.piece_length = data["info"]["piece length"]

        pieces_string = data["info"]["pieces"]
        hashes = [pieces_string[i : i + 20] for i in range(0, len(pieces_string), 20)]
        hex_hashes = [hash.hex() for hash in hashes]
        self.piece_hashes = hex_hashes

    def __repr__(self):
        hashes = ""
        for i in self.piece_hashes:
            hashes += f"{i}\n"

        res = f"""Tracker URL: {self.tracker_url}
        Length: {self.file_length}
        Info Hash: {self.info_hash}
        Piece Length: {self.piece_length}
        Piece Hashes: 
        {hashes}"""

        return res
