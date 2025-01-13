# PdfTokenizer

[![PyPI - Version](https://img.shields.io/pypi/v/pdftokenizer.svg)](https://pypi.org/project/pdftokenizer)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pdftokenizer.svg)](https://pypi.org/project/pdftokenizer)

A Python library for extracting text from PDFs with automatic OCR detection.

## Features

- 🔍 **Smart OCR Detection**: Automatically determines if OCR is needed by analyzing text extractability
- 🔄 **Dual Extraction Methods**: Uses PdfPlumber for native PDFs and Tesseract for scanned documents
- 🪟 **Windows Support**: Automatic Poppler download and setup for Windows users

## Installation

```console
pip install pdftokenizer
```

## Quick Start

```python
from pdftokenizer import extract_tokens_from_pdf

# Read your PDF file
with open("document.pdf", "rb") as f:
    pdf_bytes = f.read()

# Extract tokens - OCR will be used automatically if needed
pages = extract_tokens_from_pdf(pdf_bytes)

# Force OCR if desired
pages_ocr = extract_tokens_from_pdf(pdf_bytes, force_ocr=True)
```

## How It Works

The library automatically determines whether to use OCR based on text extractability:

1. Attempts to extract text from the PDF using PyPDF
2. If the extracted text contains fewer than 10 characters (configurable threshold), the PDF is considered to need OCR
3. Based on this detection:
   - Text-based PDFs: Processed using PdfPlumber for efficient extraction
   - Scanned/Image PDFs: Processed using Tesseract OCR

## Requirements

### Poppler
PDF processing backend:
- **Windows**: Automatically downloaded and configured
- **Linux**: `apt-get install poppler-utils`
- **macOS**: `brew install poppler`

### Tesseract
Required for OCR functionality:
- **Windows**: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
- **Linux**: `apt-get install tesseract-ocr`
- **macOS**: `brew install tesseract`

## License

`pdftokenizer` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
