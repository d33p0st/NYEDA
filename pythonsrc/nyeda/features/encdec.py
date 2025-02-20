from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet, InvalidToken
from cryptography.exceptions import InvalidSignature
from nyeda.exceptions import NYEDASEG, NYEDAException
from typing import Any, TypeGuard, TypedDict
from nyeda.bin.sharedobject import secure_delete
from nyeda.types.abc import Feature
from pathlib import Path
import pickle
import re

class base64tools(Feature):
    @staticmethod
    def is_urlsafe_b64encoded(data: bytes) -> TypeGuard[bytes]:
        if not isinstance(data, bytes):
            return False
        
        # all characters must be in b64
        if not re.fullmatch(b"[A-Za-z0-9_-]+={0,2}", data):
            return False
            
        # must be multiple of 4
        if len(data) % 4 != 0:
            return False
            
        # try decoding
        try:
            urlsafe_b64decode(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def encode(content: bytes) -> bytes:
        return urlsafe_b64encode(content)
    
    @staticmethod
    def decode(content: bytes) -> bytes:
        if base64tools.is_urlsafe_b64encoded(content):
            return urlsafe_b64decode(content)
        return NYEDASEG(NYEDAException, 'content given is not url-safe base64 encoded to begin with! (via. decode)')

class Cryptogram(TypedDict):
    ctext: bytes
    salt: bytes
    intervention: bool

    @staticmethod
    def validate(other: Any) -> TypeGuard['Cryptogram']:
        if not isinstance(other, dict) or not len(other) == 3:
            return False
        if not isinstance(other.get('ctext', None), bytes):
            return False
        if not isinstance(other.get('salt', None), bytes):
            return False
        if not isinstance(other.get('intervention', None), bool):
            return False
        # additional base64 encoded check (internally only urlsafe)
        # base64 encoded bytes are sent in ctext and salt
        if not base64tools.is_urlsafe_b64encoded(other.get('ctext')) \
            or not base64tools.is_urlsafe_b64encoded(other.get('salt')):
            return False
        return True
    
    def __setattr__(self, key, value, /):
        raise TypeError(f"{self.__class__.__name__} is immutable and cannot be modified")

class encrypter(Feature):
    
    ENCRYPT_PARAM_ERROR_MESSAGE = "'encrypt' method takes {} as url-safe base64 encoded format."
    KEY_LENGTH = 32
    MEMORY_COST = 2**16
    BLOCKSIZE = 8
    PARALLEL = 1
    BACKEND = default_backend()

    def encrypt(self, content: Any, password: bytes, salt: bytes) -> Cryptogram:
        # only accept password and salt if it is url-safe base64 encoded.
        if not base64tools.is_urlsafe_b64encoded(password):
            return NYEDASEG(NYEDAException, self.ENCRYPT_PARAM_ERROR_MESSAGE.format('password'))
        if not base64tools.is_urlsafe_b64encoded(salt):
            return NYEDASEG(NYEDAException, self.ENCRYPT_PARAM_ERROR_MESSAGE.format('salt'))
        
        # check encryption runtime pickling.
        # if the content is not bytes, __preprocessing__ is True.
        __preprocessing__ = False
        if not isinstance(content, bytes):
            content = pickle.dumps(content)
            __preprocessing__ = True
        
        # for code cleanup use a try-finally block
        try:
            # create a key derivation function (Scrypt)
            __kdf__ = Scrypt(
                urlsafe_b64decode(salt),
                self.KEY_LENGTH,
                self.MEMORY_COST,
                self.BLOCKSIZE,
                self.PARALLEL,
                self.BACKEND
            )
            
            # create the Fernet object with a key derived using
            # the Scrypt kdf
            __fernet__ = Fernet(
                urlsafe_b64encode(
                    __kdf__.derive(
                        urlsafe_b64decode(password)
                    )
                ),
                self.BACKEND
            )

            # create a cryptogram object
            __encrypted__ = Cryptogram(
                ctext=urlsafe_b64encode(__fernet__.encrypt(content)),
                salt=salt,
                intervention=__preprocessing__
            )

            # return the final result
            return __encrypted__
        finally:
            # cleanup all variables
            del __preprocessing__
            del __fernet__
            del __kdf__
            del __encrypted__

class decrypter(Feature):

    KEY_LENGTH = 32
    MEMORY_COST = 2**16
    BLOCKSIZE = 8
    PARALLEL = 1
    BACKEND = default_backend()
    DECRYPT_PARAM_ERROR_MESSAGE = "'decrypt' method takes {} as url-safe base64 encoded format."
    FILE: Path = Path('')
    OVERWRITES: int = 5

    class decrypErr(Exception):
        DECRYPT_ERROR_MESSAGE = "Invalid Signature/Token! Decryption Failure."
    
    def __decryptionfailsafe__(self, file: str, overwrites: int) -> None:
        if Path(file).exists():
            self.FILE = Path(file)
        self.OVERWRITES = overwrites
    
    def decrypt(self, cryptogram: Cryptogram, password: bytes) -> Any:
        # validate cryptogram to be authentic
        if not Cryptogram.validate(cryptogram):
            return NYEDASEG(self.decrypErr, self.decrypErr.DECRYPT_ERROR_MESSAGE)
        # also accept password in urlsafe-base64 encoded format only.
        if not base64tools.is_urlsafe_b64encoded(password):
            return NYEDASEG(NYEDAException, self.DECRYPT_PARAM_ERROR_MESSAGE.format('password'))
        
        # use a try-finally block to clear variables after use
        try:
            # create a key derivation function (Scrypt)
            __kdf__ = Scrypt(
                urlsafe_b64decode(cryptogram['salt']),
                self.KEY_LENGTH,
                self.MEMORY_COST,
                self.BLOCKSIZE,
                self.PARALLEL,
                self.BACKEND
            )

            # create the Fernet object with the key derived
            # from the __kdf__
            __fernet__ = Fernet(
                urlsafe_b64encode(
                    __kdf__.derive(
                        urlsafe_b64decode(password)
                    )
                ),
                self.BACKEND
            )

            ## try to decrypt the ctext
            try:
                if cryptogram['intervention'] is True:
                    return pickle.loads(__fernet__.decrypt(urlsafe_b64decode(cryptogram['ctext'])))
                else:
                    return __fernet__.decrypt(urlsafe_b64decode(cryptogram['ctext']))
            except (InvalidToken, InvalidSignature):
                if self.FILE == Path(''):
                    return NYEDASEG(self.decrypErr, self.decrypErr.DECRYPT_ERROR_MESSAGE)
                else:
                    secure_delete.SecureDelete(str(self.FILE), self.OVERWRITES)
                    return NYEDASEG(self.decrypErr, f'{self.FILE} has been deleted as a security measure.')
            finally:
                __kdf__ = None
                __fernet__ = None
        finally:
            del __kdf__
            del __fernet__