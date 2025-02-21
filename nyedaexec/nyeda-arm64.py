"""NYEDA arm64 executable"""

__version__: str = '1.0'

from nyeda.exceptions import NYEDAException, NYEDASEG
from nyeda.features.encdec import base64tools, encrypter
from nyeda.features.bundler import bundler
from nyeda.types.archive import ArchByte

from argpi import PathWays, Definition

from colorama import init as col_i, deinit as col_di, Fore as col

from pathlib import Path

import subprocess
import tempfile
import pickle
import shutil
import sys
import pwd
import os

CONFIGURATION = Path('~/Library/Application Support/NYEDA').expanduser().resolve()

class _Main(bundler, encrypter, base64tools):
    def __init__(
            self,
            source: Path,
            destination: Path,
            *,
            encrypt: bool = False,
            passkey: bytes = base64tools.encode(b'password!'),
            salt: bytes = base64tools.encode(os.urandom(16)),
    ) -> None:
        # Generalize the source and destination
        __source__ = source.expanduser().resolve()
        __destination__ = self.normalizer(destination.expanduser().resolve())

        # Check the existence of the source
        if not __source__.exists(): return NYEDASEG(NYEDAException, f'{__source__} does not exist.')

        # Bundle the source into archbyte
        __bundled__ = self.bundle(__source__)

        # Encrypt the bundle if instructed.
        if encrypt is True:
            # Check the passkey and salt
            if not self.is_urlsafe_b64encoded(passkey): return NYEDASEG(NYEDAException, 'passkey must be url-safe base64 encoded bytes.')
            if not self.is_urlsafe_b64encoded(salt): return NYEDASEG(NYEDAException, 'salt must be url-safe base64 encoded bytes.')

            # encrypt the bundled archive
            __bundled__ = self.encrypt(__bundled__, passkey, salt)

            # dump the cryptogram into bytes
            __bundled__ = pickle.dumps(__bundled__)

            # encode the dumped cryptogram into base64
            __bundled__ = self.encode(__bundled__)
        
        # decide the data adder
        if isinstance(__bundled__, ArchByte):
            __adder__ = f'DATA: Union[ArchByte[ArchByteInt], bytes] = ArchByte({[x for x in __bundled__]})'
        else:
            __adder__ = f'DATA: Union[ArchByte[ArchByteInt], bytes] = {__bundled__}'
        
        # Prepare the transformative content
        with open(Path(CONFIGURATION, '.new.py'), 'r') as ref:
            __newpy__ = ref.read().replace(
                'DATA: Union[ArchByte[ArchByteInt], bytes]',
                __adder__
            )
        
        # Use a temporary directory to do the deeds
        with tempfile.TemporaryDirectory(prefix='NYEDA-', delete=False) as __workdir__:
            # Move into the workdir
            os.chdir(__workdir__)

            # Create the transformative content generator
            with open(Path(__workdir__, __destination__.name + '.py'), 'w') as ref:
                ref.write(__newpy__)
            
            # Make the build script for pyinstaller
            __buildcmd__ = [
                'sudo',
                str(Path(CONFIGURATION, '.env.python', 'bin', 'python')),
                '-m',
                'PyInstaller',
                '--onefile',
                '--clean',
                '--noconfirm',
                '--noconsole',
                '--name',
                __destination__.name,
                '--icon',
                str(Path(CONFIGURATION, '.ico')),
                '--distpath',
                str(Path(__workdir__, 'dist')),
                '--workpath',
                str(Path(__workdir__, 'build')),
                '--specpath',
                str(Path(__workdir__)),
                str(Path(__workdir__, __destination__.name + '.py'))
            ]

            # Try to run the command as a subprocess.
            try: subprocess.check_call(__buildcmd__)
            except subprocess.CalledProcessError as e: return NYEDASEG(NYEDAException, 'Build Error:', str(e))

            # copy the .app from __workdir__/dist/__destination__.name.app
            os.system(f'sudo cp -r \"{Path(__workdir__, 'dist', __destination__.name + '.app')}\" \"{Path(__destination__.parent)}\"')

            # Apply permissions to the resultant file
            # As this script must be run with sudo priviledges
            # The `SUDO_USER` env var must be present
            __user__ = os.environ.get('SUDO_USER', os.popen('whoami').read().replace('\n', ''))
            self.arecp(Path(__destination__.parent, __destination__.name + '.app'), pwd.getpwnam(__user__))

            self._app = Path(__destination__.parent, __destination__.name + '.app')
            self.__workdir__ = __workdir__
        
        os.system(f'sudo rm -rf {self.__workdir__}')
    
    @property
    def transformed(self) -> Path:
        return self._app

    def arecp(self, path: Path, user: pwd.struct_passwd) -> None:
        uid_gid = f"{user.pw_uid}:{user.pw_gid}"

        # change ownership of the directory itself (.app)
        os.system(f"sudo chown {uid_gid} '{path}'")

        # Change ownership of the directory contents
        for root, _, files in os.walk(str(path)):
            os.system(f"sudo chown {uid_gid} '{root}'")

            for file in files:
                os.system(f"sudo chown {uid_gid} '{Path(root, file)}'")

    
    def normalizer(self, path: Path) -> Path:
        # Create all intermediate directories if necessary
        # but not the last part of the path.
        path.parent.mkdir(parents=True, exist_ok=True)

        # set a count:
        count = 1
        # set an extension (.app) as it is macos
        extension = '.app'

        # store the path as original path
        original = Path(path)

        # While the path (dest/name.app) or (dest/name) exists
        while Path(path.parent, path.name + extension).exists() or path.exists():
            # set path to (dest/name_count.app)
            path = Path(original.parent, original.name + f'_{count}')
            count += 1 # update the count
        
        # return the resultant path
        return path

# Script configurations (Arguments)
class ScriptCFG:
    source: Path
    destination: Path = Path(Path.cwd(), 'archive')
    encrypt: bool = False
    passkey: bytes = base64tools.encode(b'password!')
    
    parser: PathWays

    def __init__(self) -> None:
        args = [{}, {}, {}]
        args[0] = {'name': 'Bundle Source', 'value': 'create-from', 'short': '-src'}
        args[1] = {'name': 'Destination', 'value': 'move', 'short': '-dest'}
        args[2] = {'name': 'Encryption', 'value': 'set-encryption-with', 'short': '-e'}
        self.parser = PathWays(Definition(args))
        self.parser.register('create-from', self.src, 'EXEC', what_value_expected='Single', ignore_if_not_present=True)
        self.parser.register('move', self.dest, 'EXEC', what_value_expected='Single', ignore_if_not_present=True)
        self.parser.register('set-encryption-with', self.enc, 'EXEC', what_value_expected='Single', ignore_if_not_present=True)
        self.parser.orchestrate

        if self.parser.if_exec('create-from') is False:
            return self.helptext()
    
    def src(self, _: str) -> None:
        self.source = Path(_)
    
    def dest(self, _: str) -> None:
        self.destination = Path(_)
    
    def enc(self, p: str) -> None:
        self.encrypt = True
        self.passkey = base64tools.encode(p.encode())
    
    def helptext(self) -> None:
        col_i()
        print(col.BLUE + "Not Your Every-Day Archive (NYEDA)" + col.RESET, f'v{__version__}')
        print('\nHelp\n')
        print('1. Set source directory:                            create-from | -src <dir>')
        print('2. Set destination (default: current-dir/archive):  move | -dest <dir>/<name>')
        print('3. Encrypt the contents before embedding:           set-encryption-with | -e <pass>')
        col_di()
        sys.exit(0)
    
    def getsuper(self) -> None:
        if os.geteuid() != 0: return NYEDASEG(NYEDAException, 'Use super user priviledges to run this command!')

# Actual script logic
if __name__ == '__main__':
    # set configuration for the script
    cfg = ScriptCFG()

    # If helptext is not triggered by lack of arguments, move further
    if cfg.encrypt:
        _ = _Main(cfg.source, cfg.destination, encrypt=True, passkey=cfg.passkey)
    else:
        _ = _Main(cfg.source, cfg.destination)
    
    col_i()
    print(col.BLUE + 'Built:' + col.RESET, _.transformed)
    col_di()