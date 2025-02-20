
from typing import TypeGuard, TypedDict, Any
from nyeda.types.abc import Feature

class base64tools(Feature):
    """[`base64tools`] Feature.
    
    This feature provides tools to work with the base64 library within
    NYEDA's Context.
    """
    @staticmethod
    def is_urlsafe_b64encoded(data: Any) -> TypeGuard[bytes]:
        """Returns `True` if given data is urlsafe_b64encoded else `False`.
        Also acts as type guard similar to `isinstance` method.
        
        #### Meaning
        
        If this method is used to check some data contained in a variable,
        if the method returns `True`, the static type check will show
        `bytes` for the variable.
        """
    
    @staticmethod
    def encode(content: bytes) -> bytes:
        """Returns url-safe base64 encoded value."""
    
    @staticmethod
    def decode(content: bytes) -> bytes:
        """Returns url-safe base64 decoded value if the content is
        encoded in the same format else raises partially secret error."""

class Cryptogram(TypedDict):
    """Frozen ciphertext and metadata container."""
    ctext: bytes
    salt: bytes
    intervention: bool

    @staticmethod
    def validate(other: Any) -> TypeGuard['Cryptogram']:
        """Validates any given data to check if it is a valid Cryptogram."""

class encrypter(Feature):
    """[`encrypter`] Feature.
    
    This feature provides an `encrypt` method to encrypt any python object.

    The `encrypt` method returns a `Cryptogram` which is a frozen ciphertext
    and metadata container.
    """
    def encrypt(
            self,
            content: Any,
            password: bytes,
            salt: bytes,
    ) -> Cryptogram:
        """Encrypts any given python object and returns a `Cryptogram`.

        The password and salt must be url-safe base64 encoded bytes for this
        method to accept it.
        
        Features:
        - Large memory requirements to compute the hash.
        - Prevents effective use of specialized hardware (ASICs,
        GPUs) for password cracking.
        - Makes parallel attacks much more expensive.
        - Because the memory usage cannot be reduced significantly
        without dramatically increasing computation time and no
        known shortcuts to speed up computation, the ecrypted
        content becomes resistant to time-memory tradeoff attacks
        that affect other key derivation functions.
        - Prevents Rainbow Table attacks due to involvement of salt.
        - Makes hardware acceleration difficult as it uses a
        memory-hard mixing function (BlockMix) which requires random
        access to all memory allocated.
        - Prevents BruteForce Attacks.
        - Based on PBKDF2 and Salsa20/8 core.
        - Freezes the ciphertext to avoid tampering of data.
        """

class decrypter(Feature):
    """[`decrypter`] Feature.
    
    This feature provides the `decrypt` method to decrypt a `Cryptogram`
    object.
    """
    def decrypt(self, cryptogram: Cryptogram, password: bytes) -> Any:
        """Decrypts a cryptogram and returns the decrypted original object.
        
        The password must be url-safe base64 encoded bytes for this method
        to accept it.
        """
    def __decryptionfailsafe__(self, file: str, overwrites: int) -> None: ...