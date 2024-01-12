# -*- coding: utf-8 -*-
from enum import Enum, unique
from pathlib import Path
from typing import List

from pydantic import BaseModel

from eark_validator.model.checksum import Checksum

class ManifestEntry(BaseModel):
    path : Path | str
    size : int = 0
    checksums : List[Checksum] = []

class ManifestSummary(BaseModel):
    file_count: int = 0
    total_size: int = 0

@unique
class SourceType(str, Enum):
    """Enum covering information package validation statuses."""
    UNKNOWN = 'UNKNOWN'
    # Information level, possibly not best practise
    METS = 'METS'
    # Non-fatal issue that should be corrected
    PACKAGE = 'PACKAGE'

class Manifest(BaseModel):
    source: SourceType = SourceType.UNKNOWN
    summary: ManifestSummary | None
    entries: List[ManifestEntry] = []
