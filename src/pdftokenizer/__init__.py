# SPDX-FileCopyrightText: 2025-present JSv4 <scrudato@umich.edu>
#
# SPDX-License-Identifier: MIT

import io
import logging
import sys

from .extractors import PdfPlumberExtractor, TesseractExtractor
from .types import PawlsPagePythonType
from .utils import check_if_pdf_needs_ocr, get_poppler_path

logger = logging.getLogger(__name__)


def extract_tokens_from_pdf(pdf_bytes: bytes, force_ocr: bool = False) -> list[PawlsPagePythonType]:
    """Extract tokens from a PDF file using the appropriate method based on whether OCR is needed.

    Args:
        pdf_bytes: bytes or a file-like object containing PDF data
        force_ocr: If True, use OCR regardless of whether it seems necessary

    Returns:
        List of PAWLS pages with tokens
    """
    # On Windows, ensure Poppler is available
    if sys.platform == "win32":
        logger.info("Windows environment detected, checking Poppler setup...")
        poppler_path = get_poppler_path()
        logger.info(f"Using Poppler from: {poppler_path}")

    bytes_io = io.BytesIO(pdf_bytes)

    needs_ocr = check_if_pdf_needs_ocr(bytes_io)
    logger.info(f"PDF needs OCR: {needs_ocr}")

    extractor = TesseractExtractor() if (needs_ocr or force_ocr) else PdfPlumberExtractor()
    logger.info(f"Using {extractor.__class__.__name__} to extract text and tokens")

    return extractor.extract(bytes_io)
