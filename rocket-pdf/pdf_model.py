from typing import Union
from fitz import Document
from dataclasses import dataclass


@dataclass
class PDF:
    source: Union[str, Document]
    is_doc: int

    def __init__(self, source: Union[str, Document]):
        self.source = source
        self.is_doc = isinstance(source, Document)
