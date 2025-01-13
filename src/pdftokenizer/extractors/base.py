from abc import ABC, abstractmethod
from io import BufferedReader, BytesIO

from pathlib import Path

from ..types import PawlsPagePythonType


class PdfTokenExtractor(ABC):
    """Base class for PDF token extractors."""

    @abstractmethod
    def extract(self, pdf_file: str | Path | BufferedReader | BytesIO) -> list[PawlsPagePythonType]:
        """Extract tokens from PDF file."""
        pass
