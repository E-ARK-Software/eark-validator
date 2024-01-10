# -*- coding: utf-8 -*-

from enum import Enum

class ChecksumAlg(Enum):
    """
    allowed enum values
    """
    MD5 = 'MD5'
    SHA1 = 'SHA1'
    SHA256 = 'SHA256'
    SHA512 = 'SHA512'
