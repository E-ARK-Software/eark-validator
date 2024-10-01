# -*- coding: utf-8 -*-
from pathlib import Path

from eark_validator.const import NO_PATH, NOT_FILE
from eark_validator.model import Checksum, ChecksumAlg

class Checksummer:
    def __init__(self, algorithm: ChecksumAlg | str):
        if isinstance(algorithm, ChecksumAlg):
            self._algorithm: ChecksumAlg = algorithm
        else:
            self._algorithm: ChecksumAlg = ChecksumAlg.from_string(algorithm)

    @property
    def algorithm(self) -> ChecksumAlg:
        """Return the checksum algorithm used by this checksummer."""
        return self._algorithm

    def hash_file(self, path: Path) -> 'Checksum':
        """Calculate the checksum of a file.

        Args:
            path (Path): A path to a file to checksum.

        Raises:
            FileNotFoundError: If the path parameter is found.
            ValueError: If the path parameter resolves to a directory.

        Returns:
            Checksum: A Checksum object containing the Hexadecimal digest of the file.
        """
        if not path.exists():
            raise FileNotFoundError(NO_PATH.format(path))
        if not path.is_file():
            raise ValueError(NOT_FILE.format(path))
        implemenation: ChecksumAlg = ChecksumAlg.get_implementation(self._algorithm)
        with open(path, 'rb') as file:
            for chunk in iter(lambda: file.read(4096), b''):
                implemenation.update(chunk)
        return Checksum.model_validate({
                'algorithm': self._algorithm,
                'value': implemenation.hexdigest()
                }, strict=True
            )

    @classmethod
    def from_file(cls, path: Path, algorithm: 'ChecksumAlg') -> 'Checksum':
        """Create a Checksum from an etree element."""
        # Get the child flocat element and grab the href attribute.
        return Checksummer(algorithm).hash_file(path)
