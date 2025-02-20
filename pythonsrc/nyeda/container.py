
from nyeda.features.interface.segmenter import segmenter
from nyeda.types import ArchByte, ArchByteInt
from typing import Union
from pathlib import Path

import sys
import os

DATA: Union[ArchByte[ArchByteInt], bytes]

class container:
    @staticmethod
    def __file__() -> Path:
        file = Path(os.path.abspath(sys.executable))

        if sys.platform == 'darwin':
            return file.parent.parent.parent
        else:
            return file

if __name__ == '__main__': _ = segmenter(DATA, container.__file__(), 5)