import logging
from io import BufferedReader, BytesIO
from pathlib import Path

import pdfplumber

from ..types import PawlsPagePythonType, PawlsTokenPythonType
from .base import PdfTokenExtractor

logger = logging.getLogger(__name__)


class PdfPlumberExtractor(PdfTokenExtractor):
    """Class for PDF Extract vs Pdf Plumber."""

    def extract(self, pdf_file: str | Path | BufferedReader | BytesIO) -> list[PawlsPagePythonType]:
        """Extract tokens from a PDF file using pdfplumber."""
        pawls_pages = []

        with pdfplumber.open(pdf_file) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                logger.info(f"Processing page number {page_num}")

                tokens: list[PawlsTokenPythonType] = []
                words = page.extract_words()

                for word in words:
                    x0 = float(word["x0"])
                    y0 = float(word["top"])
                    x1 = float(word["x1"])
                    y1 = float(word["bottom"])

                    token: PawlsTokenPythonType = {
                        "x": x0,
                        "y": y0,
                        "width": x1 - x0,
                        "height": y1 - y0,
                        "text": word["text"],
                    }
                    tokens.append(token)

                pawls_page: PawlsPagePythonType = {
                    "page": {
                        "width": page.width,
                        "height": page.height,
                        "index": page_num,
                    },
                    "tokens": tokens,
                }
                pawls_pages.append(pawls_page)

        return pawls_pages
