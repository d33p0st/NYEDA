
from typing import Iterator, Generic, TypeVar, NewType
from base64 import urlsafe_b64encode
from collections.abc import Sequence
import pickle

ArchByteInt = NewType('ArchByteInt', int)

T = TypeVar('T', bound=ArchByteInt)

class ArchByte(Sequence, Generic[T]):
    def __init__(self, items: T = None) -> None:
        if items is None:
            self.__bytes__ = bytearray()
        else:
            self.__bytes__ = bytearray(items)
    
    def __len__(self) -> int:
        return len(self.__bytes__)
    
    def __getitem__(self, index, /):
        if isinstance(index, slice):
            return [x for x in self.__bytes__[index]]
        return self.__bytes__[index]
    
    def __setitem__(self, index, value, /) -> None:
        return None
    
    def __delitem__(self, index, /) -> None:
        return None
    
    def __iter__(self) -> Iterator[int]:
        return iter(self.__bytes__)
    
    def __repr__(self) -> str:
        return urlsafe_b64encode(pickle.dumps(self.__bytes__)).decode()
    
    def __str__(self) -> str:
        return str([x for x in self.__bytes__])
    
    def __buffer__(self) -> memoryview:
        return memoryview(self.__bytes__)