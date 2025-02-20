
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.types.abc import Feature
from nyeda.exceptions import NYEDAException, NYEDASEG
from nyeda.features.interface import popup, icons
from nyeda.features.encdec import decrypter, base64tools, Cryptogram
from typing import Any, Iterable
import pickle

class preproc(decrypter, popup, Feature):
    def preproc(self, content: Any) -> ArchByte[ArchByteInt]:
        # return the content itself if it is in iterable
        # format
        if not isinstance(content, bytes) and isinstance(content, Iterable) \
            and all(isinstance(element, int) for \
                     element in content):
            return content

        # The default encrypted content will be encoded serialized cryptogram.
        # Therefore it will be url-safe base64 encoded bytes
        # Proceed further only if the content is url-safe base64 encoded
        # bytes
        if not isinstance(content, bytes) or not base64tools.is_urlsafe_b64encoded(content):
            return NYEDASEG(NYEDAException, 'content is invalid! (via. preproc)')
        
        # At this point the content will be url-safe base64 encoded bytes
        # There will be two things that can happen
        # 1. The decoded content cannot be unpickled
        # 2. The decoded content successfully unpickles
        try:
            content = pickle.loads(base64tools.decode(content))
        except Exception:
            return NYEDASEG(NYEDAException, 'content cannot be de-serialized! (via. preproc)')

        # Validate the content to be a valid Cryptogram
        if not Cryptogram.validate(content):
            return NYEDASEG(NYEDAException, 'content has invalid signature! (via. preproc)')
        
        # Once completely validated that that the content is a valid
        # Cryptogram, ask for a password from the user.
        # Before decrypting, get the __thisfile__ and __overwrites__
        # from the child class and set the decryption failsafe.
        self.__decryptionfailsafe__(getattr(self, '__thisfile__'), getattr(self, '__overwrites__'))
        __passkey__ = self.getpasscode(
            title='preproc -> decrypt',
            icon=icons.passcode,
            geometry=(270, 80),
            resizable=False,
            withdraw=True,
            show='*'
        )

        while __passkey__ == b'':
            # handle topmost attribute of master here (as a gui betterment)
            self.__master__.attributes('-topmost', False)
            # show an error message
            from tkinter.messagebox import showerror
            showerror('Empty passkey!', 'Passkey cannot be empty!')
            __passkey__ = self.getpasscode(
                title='preproc -> decrypt',
                icon=icons.passcode,
                geometry=(270, 80),
                resizable=False,
                withdraw=True,
                show='*'
            )
            self.__master__.attributes('-topmost', True)
        
        return self.decrypt(content, __passkey__)
