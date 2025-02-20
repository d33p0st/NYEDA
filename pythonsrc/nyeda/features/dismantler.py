
from nyeda.bin.sharedobject import validation, bundle
from nyeda.types.archive import ArchByte, ArchByteInt
from nyeda.types.abc import Feature

class dismantler(Feature):
    def dismantle(self, content) -> ArchByte[ArchByteInt]:
        if validation.Validation().validate_meta(content):
            setattr(self, '__dismantlefailure__', False)
            return ArchByte(bundle.Dismantle(content).get())
        else:
            setattr(self, '__dismantlefailure__', True)
            return None
    
    def dismantle2(self, content, ext) -> bool:
        if validation.Validation().validate_meta(content):
            setattr(self, '__dismantlefailure__', False)
            return bundle.Dismantle(content).export(ext)
        else:
            setattr(self, '__dismantlefailure__', True)
            return False