import requests

from app.models.torrentmeta import TorrentMeta
from app.models.tracker_dto import TrackerDTO
from app.util.bencode import decode_bencode

def get_peers_from_tracker(torrent_meta: TorrentMeta, ):
    tracker_dto = TrackerDTO(torrent_meta)
    response = requests.get(url = torrent_meta.tracker_url, params = tracker_dto.to_json())

    peers = decode_peers(response.content)
    for ip, port in peers:
        print(f"{ip}:{port}")

def decode_peers(data):
    decoded_value = decode_bencode(data)
    return decode_address(decoded_value["peers"])

def decode_address(peers):
    length = 6

    for i in range(0, len(peers), length):
        ip_components = peers[i : i + 4]
        ip = ".".join(str(b) for b in ip_components)

        if any(component > 255 for component in ip_components):
            raise ValueError("Invalid IP range")

        port = peers[i + 4] << 8 | peers[i + 5]
        yield ip, port