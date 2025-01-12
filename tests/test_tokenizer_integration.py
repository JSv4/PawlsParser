"""Test suite to verify that the two PDF tokenizers (Tesseract and PdfPlumber) are
effectively initialized and used within the extract_tokens_from_pdf function.
We use a sample PDF (doc.pdf) and compare the extracted tokens to previously
stored fixtures.
"""

import json
from pathlib import Path

import pytest

from pdftokenizer import extract_tokens_from_pdf
from pdftokenizer.types import PawlsPagePythonType

FIXTURE_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def sample_pdf_bytes() -> bytes:
    """Loads the sample PDF as bytes from tests/fixtures/doc.pdf.

    Returns:
        PDF file content in bytes.
    """
    pdf_path = FIXTURE_DIR / "doc.pdf"
    with open(pdf_path, "rb") as f:
        return f.read()


@pytest.fixture(scope="session")
def expected_pdfplumber_tokens() -> list[PawlsPagePythonType]:
    """Loads the pre-generated PDFPlumber-extracted tokens from
    tests/fixtures/tokens_pdfplumber.json (stored as a fixture).

    Returns:
        The token data structure as a list of PawlsPagePythonType objects (deserialized).
    """
    json_path = FIXTURE_DIR / "tokens_pdfplumber.json"
    if not json_path.exists():
        pytest.skip("Missing fixture file tokens_pdfplumber.json. Please generate it.")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    return data


@pytest.fixture(scope="session")
def expected_tesseract_tokens() -> list[PawlsPagePythonType]:
    """Loads the pre-generated Tesseract-extracted tokens from
    tests/fixtures/tokens_tesseract.json (stored as a fixture).

    Returns:
        The token data structure as a list of PawlsPagePythonType objects (deserialized).
    """
    json_path = FIXTURE_DIR / "tokens_tesseract.json"
    if not json_path.exists():
        pytest.skip("Missing fixture file tokens_tesseract.json. Please generate it.")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_pdfplumber_extraction(sample_pdf_bytes: bytes, expected_pdfplumber_tokens: list[PawlsPagePythonType]) -> None:
    """Test that extract_tokens_from_pdf uses the PdfPlumberExtractor when force_ocr is False
    and that we get the expected token output.

    Args:
        sample_pdf_bytes: The byte content of our sample PDF fixture.
        expected_pdfplumber_tokens: The list of expected token data from the pdfplumber flow.
    """
    # Extract tokens with PdfPlumber by ensuring force_ocr=False
    tokens = extract_tokens_from_pdf(sample_pdf_bytes, force_ocr=False)
    assert isinstance(tokens, list), "Extracted tokens should be a list."
    assert tokens, "PdfPlumber extraction returned an empty list of tokens."

    # Because these data structures can have floating-point bounding boxes,
    # we might want to do more flexible comparisons, but here we do a direct check.
    # You may want to write a custom comparison for bounding box coords if minor float differences occur.
    assert len(tokens) == len(
        expected_pdfplumber_tokens
    ), f"Expected {len(expected_pdfplumber_tokens)} page(s) of tokens, got {len(tokens)}."


def test_tesseract_extraction(sample_pdf_bytes: bytes, expected_tesseract_tokens: list[PawlsPagePythonType]) -> None:
    """Test that extract_tokens_from_pdf uses the TesseractExtractor when force_ocr is True
    and that we get the expected token output.

    Args:
        sample_pdf_bytes: The byte content of our sample PDF fixture.
        expected_tesseract_tokens: The list of expected token data from the tesseract flow.
    """
    # Extract tokens with Tesseract by ensuring force_ocr=True
    tokens = extract_tokens_from_pdf(sample_pdf_bytes, force_ocr=True)
    assert isinstance(tokens, list), "Extracted tokens should be a list."
    assert tokens, "Tesseract extraction returned an empty list of tokens."

    # Compare the length of the pages:
    assert len(tokens) == len(
        expected_tesseract_tokens
    ), f"Expected {len(expected_tesseract_tokens)} page(s) of tokens, got {len(tokens)}."
