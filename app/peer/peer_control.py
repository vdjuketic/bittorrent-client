from pebble import ProcessPool
from concurrent.futures import TimeoutError 

from app.peer.request_util import get_peers_from_tracker
from app.peer.peer_client import PeerClient, PeerClientStatus
from app.models.piece import Piece, PieceStatus

MAX_WORKERS = 5

pieces = []

#TODO bind job to peer instead of piece
class PieceJob:
    def __init__(self, piece):
        self.piece = piece
    
    def process_piece(self, piece, peers):
        for peer, status in peers:
            if status == False:
                status == True
                print(f"adding piece {piece.piece_num} to peer {peer.host}")
                peer.download_piece(piece)
                break

    def task_done(self, future):
        try:
            print("task done")
            piece_num = future.result()
            for piece in pieces:
                if piece.piece_num == piece_num:
                    piece.status = PieceStatus.COMPLETED
                    downloaded += 1

        except Exception as error:
            print("Function raised %s" % error)
            print(error.traceback)  # traceback of the function

class Downloader:
    jobs = []
    peers = []

    downloaded = 0

    def __init__ (self, torrent_meta):
        self.torrent_meta = torrent_meta
        

    def download(self):
        peer_urls = get_peers_from_tracker(self.torrent_meta)

        for peer_url in peer_urls:
            self.peers.append((PeerClient(peer_url), False))

        for piece_num in range(len(self.torrent_meta.piece_hashes)):
            piece = Piece(piece_num, self.torrent_meta)
            pieces.append(piece)
            self.jobs.append(piece)
        
        with ProcessPool(max_workers=5, max_tasks=10) as pool:
            for piece in pieces:
                p = PieceJob(piece)
                future = pool.schedule(p.process_piece, args=[piece, self.peers])
                future.add_done_callback(p.task_done)
            
        print("bleh")
        print(pieces)
                        
        #content = b""
        #for piece in self.pieces:
        #    content += piece.result
        #return content
        