"""Utility script to generate and save token fixtures for both the pdfplumber and tesseract flows.

Usage:
    1) Place doc.pdf at tests/fixtures/doc.pdf.
    2) Run this script to create/update tokens_pdfplumber.json and tokens_tesseract.json.
"""

import json
import logging
import sys
from pathlib import Path

from pdftokenizer import extract_tokens_from_pdf
from pdftokenizer.utils import get_poppler_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_fixtures() -> None:
    """Generates token extraction fixtures for pdfplumber and tesseract, saving them as JSON
    in the tests/fixtures directory.
    """
    try:
        # Check for Windows and setup Poppler if needed
        if sys.platform == "win32":
            logger.info("Windows environment detected, checking Poppler setup...")
            try:
                poppler_path = get_poppler_path()
                logger.info(f"Using Poppler from: {poppler_path}")
            except RuntimeError as e:
                logger.error(f"Failed to setup Poppler: {e}")
                logger.error("Please ensure you have a working internet connection and try again")
                return

        fixture_dir = Path(__file__).parent / "fixtures"
        pdf_path = fixture_dir / "doc.pdf"

        if not pdf_path.exists():
            logger.error(f"Test PDF file not found at {pdf_path}")
            logger.error("Please place a test PDF file at tests/fixtures/doc.pdf")
            return

        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # Generate pdfplumber fixture
        logger.info("Generating PDFPlumber fixture...")
        plumber_tokens = extract_tokens_from_pdf(pdf_bytes, force_ocr=False)
        plumber_json_path = fixture_dir / "tokens_pdfplumber.json"
        with open(plumber_json_path, "w", encoding="utf-8") as f:
            json.dump(plumber_tokens, f, indent=2, ensure_ascii=False)
        logger.info(f"PDFPlumber fixture saved to {plumber_json_path}")

        # Generate tesseract fixture
        logger.info("Generating Tesseract fixture...")
        tess_tokens = extract_tokens_from_pdf(pdf_bytes, force_ocr=True)
        tess_json_path = fixture_dir / "tokens_tesseract.json"
        with open(tess_json_path, "w", encoding="utf-8") as f:
            json.dump(tess_tokens, f, indent=2, ensure_ascii=False)
        logger.info(f"Tesseract fixture saved to {tess_json_path}")

    except Exception as e:
        logger.error(f"An error occurred while generating fixtures: {e!s}")
        raise


if __name__ == "__main__":
    generate_fixtures()
