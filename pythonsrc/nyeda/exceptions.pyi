
class NYEDAException(Exception):
    """Generic NYEDA Exception class."""

class NYEDASEG:
    """NYEDA secretive error generator.
    
    Usage:
    ```python
    def func():
        return NYEDASEG(TypeError, 'This is a secretive TypeError')
    ```
    """
    def __init__(self, exception: BaseException, *args: str) -> None:
        """Generate a NYEDA secret error from given exception with args."""