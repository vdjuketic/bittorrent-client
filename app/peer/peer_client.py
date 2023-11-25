import socket
import binascii
import struct
import hashlib
import logging as log

from app.models.torrentmeta import TorrentMeta

class PeerClient:
    UNCHOKE = 1
    INTERESTED = 2
    BITFIELD = 5
    REQUEST = 6
    PIECE = 7

    BLOCK_SIZE = 16 * 1024

    def __init__(self, url):
        self.host, self.port = url
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, int(self.port)))

    def download(self, torrent_meta):
        content = b""
        for index in range(0, len(torrent_meta.piece_hashes)):
            content += self.download_piece(torrent_meta, index)
        return content

    def download_piece(self, torrent_meta, piece_index):
        self.perform_handshake(torrent_meta.info_hash)
        piece_length = self.calculate_piece_length(torrent_meta, piece_index)

        _, message_id, message = self.receive_message()
        assert message_id == self.BITFIELD

        self.send_message(self.INTERESTED, b"")

        _, message_id, message = self.receive_message()
        assert message_id == self.UNCHOKE

        piece_offset = 0
        downloaded_piece = b""
        while piece_offset < piece_length:
            block_size = min(self.BLOCK_SIZE, piece_length - piece_offset)

            payload = (
                piece_index.to_bytes(4, "big")
                + piece_offset.to_bytes(4, "big")
                + block_size.to_bytes(4, "big")
            )

            self.send_message(self.REQUEST, payload)

            _, message_id, message = self.receive_message()
            assert message_id == self.PIECE

            block_piece = int.from_bytes(message[:4], "big")
            block_begin = int.from_bytes(message[4:8], "big")
            message = message[8:]

            downloaded_piece += message
            piece_offset += block_size

        downloaded_piece_hash = hashlib.sha1(downloaded_piece).hexdigest()

        if downloaded_piece_hash != torrent_meta.piece_hashes[piece_index]:
            log.error(f"Integrity check failed for piece {piece_index}")
        else:
            print(f"Downloaded piece: {piece_index} successfully")
            return downloaded_piece
        
        socket.close()

    def perform_handshake(self, info_hash):
        self.connect()
        request = self.generate_handshake_message(info_hash, b"00112233445566778899")
        self.socket.send(request)

        response = self.socket.recv(1024)
        peer_id = response[-20:]
        hex_peer_id = binascii.hexlify(peer_id).decode()
        print(f"Peer ID: {hex_peer_id}")

    def generate_handshake_message(self, info_hash, peer_id):
        length = struct.pack(">B", 19)
        protocol = b"BitTorrent protocol"
        reserved = b"\x00" * 8
        info_hash = hashlib.sha1(info_hash).digest()

        return length + protocol + reserved + info_hash + peer_id

    def send_message(self, message_id, payload):
        log.info(f"Sending message id {message_id}")
        message_id = message_id
        prefix = struct.pack(">I", len(payload) + 1)
        self.socket.sendall(prefix + struct.pack("B", message_id) + payload)

    def get_block_from_piece_message(self, message):
        return message[8:]

    def receive_message(self) -> tuple[int, int, bytes]:
        length = int.from_bytes(self.socket.recv(4), "big")

        if not length:
            return (0, -1, b"")

        message = self.socket.recv(length)
        received = len(message)

        msg_id = int.from_bytes(message[:1], "big")

        while received < length:
            message += self.socket.recv(length - received)
            received = len(message)

        log.info(f"Received message of type: {msg_id}")
        return (length, msg_id, message[1:])
    
    def calculate_piece_length(self, torrent_meta, piece_num):
        num_pieces = len(torrent_meta.piece_hashes)
        if num_pieces - 1 != piece_num:
            return torrent_meta.piece_length
        else:
            return torrent_meta.file_length % torrent_meta.piece_length
