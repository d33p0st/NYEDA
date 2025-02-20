
import colorama
import sys

class NYEDAException(Exception):
    pass

class NYEDASEG:
    def __init__(self, exception: BaseException, *args: str) -> None:
        colorama.init()
        print(
            ("" if sys.platform == 'win32' else colorama.Fore.BLUE) \
            + exception.__qualname__ \
            + ("" if sys.platform == 'win32' else colorama.Fore.RESET) \
            + ':',
            *args,
        )
        colorama.deinit()
        sys.exit(1)