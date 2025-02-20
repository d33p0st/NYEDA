
from customtkinter import CTk, CTkToplevel, CTkFrame
from tkinterdnd2.TkinterDnD import Tk
from tkinter import Event, ttk
from PIL.ImageTk import PhotoImage
from typing import Tuple, Union, List, Callable
from pathlib import Path

from nyeda.types.abc import Feature

class IconNamespace:
    """Icon Namespace contains all images in bytes"""
    topsecret: bytes
    folder: bytes
    passcode: bytes
    segment: bytes
    file: bytes

icons: IconNamespace

class mastertools(Feature):
    """[`mastertools`] Feature.
    
    This feature provides helper methods to safely create or
    destroy gui windows and prepare them in accordance to
    NYEDA requirements.
    """
    HEIGHT: int
    WIDTH: int

    __master__: Union[CTk, Tk]
    __toplevel__: CTkToplevel

    __mastericon__: PhotoImage
    __toplevelicon__: PhotoImage

    @staticmethod
    def generate_master(*args, **kwargs) -> CTk:
        """Generates a root gui window with given params."""
    
    @staticmethod
    def generate_dnd_master(*args, **kwargs) -> Tk:
        """Generates a root gui window with given parameters
        which supports drag and drop on the window."""
    
    @staticmethod
    def generate_toplevel(*args, **kwargs) -> CTkToplevel:
        """Generates a popup gui window with given params."""
    
    @staticmethod
    def centralgeometry(width: int, height: int) -> str:
        """Returns a geometry string for central window
        placement for the currently active screen based on
        given width and height."""
    
    def __quitmaster__(self, event: Union[Event, None] = None, /) -> None:
        """Master window delete protocol."""
    
    def __toplevelexitprotocol__(self, event: Union[Event, None] = None, /) -> None:
        """Toplevel window delete protocol."""
    
    def __toplevelmainloop__(self, event: Union[Event, None] = None, /) -> None:
        """Runs the Toplevel window mainloop. This is totally safe
        and can be run before the Master mainloop."""
    
    def __mastersetup__(
            self,
            title: str,
            icon: bytes,
            geometry: Tuple[int, int],
            resizable: bool,
    ) -> None:
        """Sets up the Master based on given parameters. Note 
        that the icon must be url-safe base64 encoded bytes.
        """
    
    def __toplevelsetup__(
            self,
            title: str,
            icon: bytes,
            geometry: Tuple[int, int],
            resizable: bool,
    ) -> None:
        """Sets up the Toplevel based on given parameters. Note
        that the icon must be url-safe base64 encoded bytes."""


class popup(Feature):
    """[`popup`] Feature.
    
    This feature provides a passcode retrieval popup creation
    toolkit.
    """
    def getpasscode(
            self,
            title: str,
            icon: bytes,
            geometry: Tuple[int, int],
            resizable: bool,
            withdraw: bool = False,
            show: str = "#",
            standalone: bool = False
    ) -> bytes:
        """Safely generates a popup window (either over
        pre-existing Master window or standalone) for passcode
        retrieval.
        
        Note that the icon must be url-safe base64 encoded bytes.
        The withdraw parameter must be set to `True` if the
        Master window should withdraw and only the Toplevel is
        needed alone."""

class FilesystemTree(ttk.Treeview):
    """[`Filesystem Tree`] View.
    
    This is a derived form of `tkinter.ttk.Treeview` which contains
    extra tools to handle file system representation.
    """
    __filetype__: PhotoImage
    __foldertype__: PhotoImage
    __archivetype__: PhotoImage
    def __init__(self, *args, **kwargs) -> None:
        """Createa Filesystem Tree."""

class DropFrame(CTkFrame):
    """[`Drop Frame`].
    
    This is a derived form of `customtkinter.CTkFrame` which
    contains extra tools to handle drag and drop.
    """
    __filesystem__: List[Path] = []
    def __init__(self, master, *args, **kwargs) -> None:
        """Create a Drop Frame."""
    
    def __dndenter__(self, event: Union[Event, None] = None, /) -> None:
        """Drag and drop enter event."""
    
    def __dndexit__(self, event: Union[Event, None] = None, /) -> None:
        """Drag and drop exit event."""
    
    def __ondrop__(self, event: Union[Event, None] = None, /) -> None:
        """Drag and drop event handler."""
    
    def set_drophandle(self, func: Callable[[Path], None]) -> None:
        """ondrop handler setter."""