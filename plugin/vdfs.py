from pathlib import Path
from typing import Union

import vdf


class VDF(dict):
    """
    Represents a VDF file used by Steam.
    """

    def __init__(self, file: Union[str, Path]) -> None:
        self.file = Path(file)
        self._data = self._load()
        super(VDF, self).__init__(self._data)

    def _load(self):
        with open(self.file, 'r', encoding='utf-8', errors='ignore') as f:
            return vdf.load(f)
