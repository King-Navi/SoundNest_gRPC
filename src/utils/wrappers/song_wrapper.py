from dataclasses import dataclass
from models.mysql.models import Song

@dataclass
class SongWithFile:
    song: Song
    file_content: bytes
