# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field

from eark_validator.model.checksum_alg import ChecksumAlg

class Checksum(BaseModel):
    algorithm: ChecksumAlg = ChecksumAlg.SHA1
    value: str = Field(default='', to_upper=True)
