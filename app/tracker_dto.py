import json
from dataclasses import dataclass
from . torrentmeta import TorrentMeta

@dataclass
class TrackerDTO():
    info_hash: str
    peer_id: str
    port: int
    uploaded: int
    downloaded: int 
    left: int
    compact: int

    def __init__(self, meta: TorrentMeta):
        self.info_hash = meta.info_hash
        self.peer_id = "00112233445566778899"
        self.port = 6881
        self.uploaded = 0
        self.downloaded = 0
        self.left = meta.file_length
        self.compact = 1

    def to_json(self):
        return {"info_hash": self.info_hash,
            "peer_id": self.peer_id,
            "port": self.port,
            "uploaded": self.uploaded,
            "downloaded": self.downloaded,
            "left": self.left,
            "compact": self.compact
        }