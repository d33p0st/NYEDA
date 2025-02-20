
from nyeda.types.abc import Feature
from typing import TypeVar, Dict, List

M = TypeVar('METADATA')

class dirtools(Feature):
    """[`dirtools`] Feature.
    
    This feature provides a tool for generating directory map from
    a metadata generator.
    """
    def generate_dirmap(self, metadata: M) -> Dict[str, List[str]]:
        """Creates a directory mapping from a given archive metadata factory."""