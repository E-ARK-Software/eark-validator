# -*- coding: utf-8 -*-

from pydantic import BaseModel

from eark_validator.model.checksum_alg import ChecksumAlg

class Checksum(BaseModel):
    algorithm: ChecksumAlg | None
    value: str | None
