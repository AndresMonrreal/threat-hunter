from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class FileEvidence:
    path: str
    sha256: str
    md5: str
    sha1: str
    file_type: str
    mime_type: str
    size_bytes: int
    modified_at: datetime
    analyzed_at: datetime
    entropy: float
    strings_sample: list[str] = field(default_factory=list)
    elf_info: dict | None = None

