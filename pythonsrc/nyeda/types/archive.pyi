# type: ignore

from typing import Iterator, Iterable, NewType, Generic, TypeVar
from typing import overload

ArchByteInt = NewType('ArchByteInt', int)

T = TypeVar('T', bound=ArchByteInt)

class ArchByte(Generic[T]):
    """ArchByte DataType.
    
    This data-type resembles raw bytes of bundled archive data. The data is
    stored in a sequence of bytes
    """
    def __init__(self, items: Iterable[T]) -> None: ...
    def __iter__(self) -> Iterator[T]: ...