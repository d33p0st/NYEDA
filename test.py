
from nyeda.features.bundler import bundler
from nyeda.features.preproc import preproc
from nyeda.nyeda import Nyeda
from nyeda.features.dismantler import dismantler
from nyeda.bin.sharedobject import validation
from nyeda.features.encdec import encrypter, base64tools
from nyeda.features.interface.segmenter import segmenter
from pathlib import Path
import pickle

b = bundler().bundle(Path('/Users/d33pster/txts'))
print('preproc', preproc().preproc(b) == b)

_ = Nyeda(Path('/Users/d33pster/txts'), Path('~/Desktop/txts'))
_.bundl()