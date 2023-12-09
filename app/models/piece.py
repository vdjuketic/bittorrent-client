from enum import Enum

from models.torrentmeta import TorrentMeta


class PieceStatus(Enum):
    NOT_STARTED = 1
    STARTED = 2
    FAILED = 3
    COMPLETED = 4


class Piece:
    piece_num: int
    status: PieceStatus
    info_hash: str
    piece_hash: str
    length: int
    result: str = ""

    def __init__(self, piece_num: int, torrent_meta: TorrentMeta):
        self.piece_num = piece_num
        self.status = PieceStatus.NOT_STARTED
        self.info_hash = torrent_meta.info_hash
        self.piece_hash = torrent_meta.piece_hashes[piece_num]
        self.length = self.calculate_piece_length(torrent_meta)

    def calculate_piece_length(self, torrent_meta):
        num_pieces = len(torrent_meta.piece_hashes)
        if num_pieces - 1 != self.piece_num:
            return torrent_meta.piece_length
        else:
            return torrent_meta.file_length % torrent_meta.piece_length

    def __str__(self):
        return f"Piece num: {self.piece_num}, status: {self.status}"
