# -*- coding: utf-8 -*-

from enum import Enum
import hashlib

class ChecksumAlg(Enum):
    """
    allowed enum values
    """
    MD5 = 'MD5'
    SHA1 = 'SHA-1'
    SHA256 = 'SHA-256'
    SHA384 = 'SHA-384'
    SHA512 = 'SHA-512'

    @classmethod
    def from_string(cls, value: str) -> 'ChecksumAlg':
        search_value = value.upper() if hasattr(value, 'upper') else value
        for algorithm in ChecksumAlg:
            if (algorithm.value == search_value) or (algorithm.name == search_value) or (algorithm == value):
                return algorithm
        return None

    @classmethod
    def get_implementation(cls, algorithm: 'ChecksumAlg' = MD5):
        if isinstance(algorithm, str):
            algorithm = cls.from_string(algorithm)
        if algorithm == ChecksumAlg.SHA1:
            return hashlib.sha1()
        if algorithm == ChecksumAlg.SHA256:
            return hashlib.sha256()
        if algorithm == ChecksumAlg.SHA384:
            return hashlib.sha384()
        if algorithm == ChecksumAlg.SHA512:
            return hashlib.sha512()
        if algorithm == ChecksumAlg.MD5:
            return hashlib.md5()
        raise ValueError('Algorithm {} not supported.'.format(algorithm))
