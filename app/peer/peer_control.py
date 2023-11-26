from concurrent.futures import ThreadPoolExecutor

from app.peer.request_util import get_peers_from_tracker
from app.peer.peer_client import PeerClient, PeerClientStatus
from app.models.piece import Piece, PieceStatus

MAX_WORKERS = 5


class Downloader:
    free_peers = []
    pieces = []

    downloaded = 0
    total = 0

    def __init__(self, torrent_meta):
        self.torrent_meta = torrent_meta
        self.executor = ThreadPoolExecutor(MAX_WORKERS)

    def process_piece(self, piece):
        while True:
            if len(self.free_peers) > 0:
                peer = self.free_peers.pop()

                try:
                    print(f"starting download of {piece.piece_num} on peer {peer.host}")
                    peer.download_piece(piece)
                    print(f"job for {piece.piece_num} passed")
                    piece.status = PieceStatus.COMPLETED
                    self.downloaded += 1
                    self.free_peers.append(peer)
                    print(f"freed peer {peer.host}")
                except AttributeError:
                    print(f"removed peer {peer.host}")
                except Exception as e:
                    print(f"job for {piece.piece_num} failed")
                    self.executor.submit(self.process_piece, piece)
                    self.free_peers.append(peer)
                    print(f"freed peer {peer.host}")
                break

    def download(self):
        peer_urls = get_peers_from_tracker(self.torrent_meta)

        for peer_url in peer_urls:
            self.free_peers.append(PeerClient(peer_url))

        for piece_num in range(len(self.torrent_meta.piece_hashes)):
            piece = Piece(piece_num, self.torrent_meta)
            self.pieces.append(piece)
            self.total += 1

            self.executor.submit(self.process_piece, piece)
            print(f"added job for {piece.piece_num}")

        while True:
            if self.total == self.downloaded:
                self.executor.shutdown(wait=False)
                break

        print("all jobs finished")

        content = b""
        for piece in self.pieces:
            content += piece.result
        return content
