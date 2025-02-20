
from typing import Type, Dict, List
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:    
    class bundle:
        """bundle [`module`].

        Contains the `Bundle` and `Dismantle` classes for bundling a source
        and dismantling it for system iterpretation respectively.
        """
        class _5160603462204636848:
            """Bundler [`class`].
            
            ... bundles any source directory into raw archive bytes. The best
            possible compression is used to make sure the archive is of
            minimal size.
            """
            def __init__(self) -> None:
                """Initialize the bundler for bundling any source directory
                of the current system."""
            def create(self, source: str, version: int, /) -> List[int]:
                """Create a bundle from given source and specified engine
                version."""

        class _4385504876945014275:
            """Dismantle [`class`].
            
            ... dismantles any bundled archive into metadata-data divided
            form which can be globally used across the `sharedobject`
            module contents.
            """
            def __init__(self, data: List[int], /) -> None:
                """Dismantle the archive data into separate system
                interpretable form."""
            def export(self, output: str, /) -> bool:
                """Re-combine necessary parts and export the archive into
                its original source form."""
            def get(self) -> List[int]:
                """Returns system interpretable part of the archive data."""
            def get_meta(self) -> str:
                """Returns the archive metadata hash string."""

        class _8947704719820868688:
            """Structure [`class`].
            
            ... provides a structure extraction mechanism to generate a partial
            metadata from any given archive data.
            """
            @staticmethod
            def get(data: List[int]) -> Dict[str, bytes]:
                """Returns a partial metadata based on the archive data given."""
        Structure: Type[_8947704719820868688]
        Dismantle: Type[_4385504876945014275]
        Bundle: Type[_5160603462204636848]
    
    class validation:
        """validation ['Module']
        
        Contains the `Validation` class for validating any bundled archive's
        metadata against current system.
        """
        class _3256342104921716572:
            """Validation [`class`].
            
            ... validates any given bundled (made using `bundle.Bundler`)
            archive's metadata against the current system.
            """
            def __init__(self) -> None: ...
            @staticmethod
            def validate_meta(data: List[int], /) -> bool:
                """Validates the given archive data against the current
                system."""
            @staticmethod
            def validate_meta_hash(version: int, hash: str, /) -> bool:
                """Validates the archive metadata hash against the current
                system."""
        Validation: Type[_3256342104921716572]
    
    class secure_delete:
        """secure_delete [`Module`].
        
        Contains the `SecureDelete` class for securely wiping contents from
        the system in accordance to DoD 5220.22-M secure delete standard.
        """
        class _6494856343047591817:
            """Secure Delete ['class'].
            
            ... securely deletes any file or folder (recursively) using
            `DoD 5220.22-M` secure delete standard.
            """
            def __init__(self, path: str, overwrites: int, /) -> None:
                """securely deletes any file or folder (recursively) using
                `DoD 5220.22-M` secure delete standard."""
        SecureDelete: Type[_6494856343047591817]
    
    if sys.platform == 'darwin':
        class macos:
            """macos [`Module`].
            
            Contains the `MacosSRCD` class for single shot detection of
            screenrecord/capture apps in macos.
            """
            class _5335542801870967125:
                """Macos Screen Record/Capture Detection [`class`].
                
                ... detects in a single shot if any supported screencapture
                app is running in this instant.
                """
                def __init__(self) -> None: """Initialize the detector."""
                def detect(self) -> bool: """Detect screencapture in this instant."""
                def kill(self) -> None:
                    """Kill if any screencapture app is found in this instant."""
            MacosSRCD: Type[_5335542801870967125]
    elif sys.platform == 'win32':
        class windows:
            """windows [`Module`].
            
            Contains the `WindowsSRCD` class for single shot detection of
            screenrecord/capture apps in windows
            """
            class _3859921643423807587:
                """Windows Screen Record/Capture Detection [`class`].
                
                ... detects in a single shot if any suported screencapture
                app is running in this instant.
                """
                def __init__(self) -> None: """Initialize the detector."""
                def detect(self) -> bool: """Detect screencapture in this instant."""
                def kill(self) -> None:
                    """Kill if any screencapture app is found in this instant."""
            WindowsSRCD: Type[_3859921643423807587]
else:
    secure_delete: object
    validation: object
    bundle: object
    if sys.platform == 'darwin':
        macos: object
    elif sys.platform == 'win32':
        windows: object

__all__ = ['bundle']