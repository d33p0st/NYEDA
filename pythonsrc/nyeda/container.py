
import ctypes
import sys
import os

# If the given platform is windows, (as the app wont be windowed (due to some packaging error in current packager)), close the
# terminal if present.
if sys.platform == 'win32':
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

from nyeda.features.interface.segmenter import segmenter
from nyeda.types import ArchByte, ArchByteInt
from typing import Union
from pathlib import Path

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