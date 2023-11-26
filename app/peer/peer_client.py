import socket
import binascii
import struct
import hashlib
import logging as log
from enum import Enum

from app.models.piece import Piece


class PeerClientStatus(Enum):
    DISCONNECTED = 1
    CONNECTED = 2
    WORKING = 3


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
        self.status = PeerClientStatus.DISCONNECTED
        self.hex_peer_id = ""

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, int(self.port)))
        self.status = PeerClientStatus.CONNECTED
        self.socket.settimeout(None)

    def disconnect(self):
        self.socket.close()
        self.status = PeerClientStatus.DISCONNECTED

    def download_piece(self, piece: Piece):
        self.status = PeerClientStatus.WORKING
        print(f"starting download of piece {piece.piece_num}")
        downloaded_piece = b""

        try:
            self.perform_handshake(piece.info_hash)

            _, message_id, message = self.receive_message()
            assert message_id == self.BITFIELD

            self.send_message(self.INTERESTED, b"")

            _, message_id, message = self.receive_message()
            assert message_id == self.UNCHOKE

            piece_offset = 0
            while piece_offset < piece.length:
                block_size = min(self.BLOCK_SIZE, piece.length - piece_offset)

                payload = (
                    piece.piece_num.to_bytes(4, "big")
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

            if downloaded_piece_hash != piece.piece_hash:
                log.error(f"Integrity check failed for piece {piece.piece_num}")
                raise Exception(f"Integrity check failed for piece: {piece.piece_num}")

            print(f"Downloaded piece: {piece.piece_num} successfully")
            piece.result = downloaded_piece
        except AssertionError or TimeoutError as e:
            downloaded_piece = b""
            print(f"Error with download_piece protocol")
            raise e
        except AttributeError as e:
            downloaded_piece = b""
            print(e.args)
            raise e
        finally:
            self.disconnect()

    def perform_handshake(self, info_hash):
        self.connect()
        request = self.generate_handshake_message(info_hash, b"00112233445566778899")
        self.socket.sendall(request)

        response = self.socket.recv(1024)
        peer_id = response[-20:]
        self.hex_peer_id = binascii.hexlify(peer_id).decode()

        if self.hex_peer_id == "":
            raise AttributeError(f"Invalid peer ID for {self.host}")

        print(f"Peer ID: {self.hex_peer_id}")

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
        self.socket.settimeout(10)
        length = int.from_bytes(self.socket.recv(4), "big")
        self.socket.settimeout(None)

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
