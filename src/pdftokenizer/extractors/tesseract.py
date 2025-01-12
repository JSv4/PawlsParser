import logging
from io import BufferedReader, BytesIO
from pathlib import Path

import pdf2image
import pytesseract

from ..types import PawlsPagePythonType, PawlsTokenPythonType
from ..utils import get_poppler_path
from .base import PdfTokenExtractor

logger = logging.getLogger(__name__)


class TesseractExtractor(PdfTokenExtractor):
    """Extract via tesseract."""

    def extract(self, pdf_file: str | Path | BufferedReader | BytesIO) -> list[PawlsPagePythonType]:
        """Extract tokens from a PDF file using Tesseract OCR.

        Args:
            pdf_file: PDF file input, can be:
                     - string file path
                     - Path object
                     - BufferedReader (file object)
                     - BytesIO object

        Returns:
            List[PawlsPagePythonType]: List of pages with extracted tokens
        """
        pawls_pages = []

        # Handle different input types
        if isinstance(pdf_file, str | Path):
            with open(pdf_file, "rb") as f:
                pdf_bytes = f.read()
        elif isinstance(pdf_file, BufferedReader | BytesIO):
            pdf_bytes = pdf_file.read()
            pdf_file.seek(0)  # Reset file pointer
        else:
            raise ValueError("Unsupported pdf_file type")

        # Get Poppler path for Windows
        poppler_path = get_poppler_path()

        # Convert PDF to images
        images = pdf2image.convert_from_bytes(
            pdf_bytes,
            poppler_path=str(poppler_path) if poppler_path else None,  # type: ignore
            use_pdftocairo=True,
            fmt="png",
        )

        for page_num, page_image in enumerate(images, start=1):
            logger.info(f"Processing page number {page_num}")
            width, height = page_image.size

            custom_config = r"--oem 3 --psm 3"
            word_data = pytesseract.image_to_data(
                page_image,
                output_type=pytesseract.Output.DICT,
                config=custom_config,
            )

            tokens: list[PawlsTokenPythonType] = []
            n_boxes = len(word_data["text"])

            for i in range(n_boxes):
                word_text = word_data["text"][i]
                conf = int(word_data["conf"][i])

                if conf > 0 and word_text.strip():
                    token: PawlsTokenPythonType = {
                        "x": float(word_data["left"][i]),
                        "y": float(word_data["top"][i]),
                        "width": float(word_data["width"][i]),
                        "height": float(word_data["height"][i]),
                        "text": word_text,
                    }
                    tokens.append(token)

            pawls_page: PawlsPagePythonType = {
                "page": {
                    "width": width,
                    "height": height,
                    "index": page_num,
                },
                "tokens": tokens,
            }
            pawls_pages.append(pawls_page)

        return pawls_pages
