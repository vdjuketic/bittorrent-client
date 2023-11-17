import socket
import binascii


def send_handshake(host, port, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((str(host), int(port)))
    s.send(request)

    response = s.recv(1024)
    peer_id = response[-20:]

    # Convert to hexadecimal representation
    hex_peer_id = binascii.hexlify(peer_id).decode()
    print(f"Peer ID: {hex_peer_id}")
