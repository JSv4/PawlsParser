import logging
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from pypdf import PdfReader

logger = logging.getLogger(__name__)


def check_if_pdf_needs_ocr(file_object, threshold: int = 10) -> bool:
    """Check if a PDF file needs OCR by attempting to extract text and comparing against a threshold.

    Args:
        file_object: A file-like object containing the PDF
        threshold: Minimum number of characters to consider the PDF as having readable text

    Returns:
        bool: True if the PDF needs OCR, False otherwise
    """
    pdf_reader = PdfReader(file_object)
    total_text = ""

    for page in pdf_reader.pages:
        total_text += page.extract_text()

    # Reset file pointer to the beginning for subsequent use
    file_object.seek(0)

    # If the total extracted text is less than the threshold, it likely needs OCR
    return len(total_text.strip()) < threshold


def get_poppler_path() -> str | None:
    """Get the path to the Poppler binaries. On Windows, it will be downloaded if not present.

    Returns:
        Optional[str]: Path to Poppler binaries or None if not on Windows
    """
    if sys.platform != "win32":
        return None

    poppler_path = Path(__file__).parent / "poppler-windows" / "Library" / "bin"
    if poppler_path.exists():
        return str(poppler_path)

    return setup_poppler_windows()


def setup_poppler_windows() -> str:
    """Download and setup Poppler for Windows.

    Returns:
        str: Path to the Poppler binaries

    Raises:
        RuntimeError: If download or extraction fails
    """
    try:
        # Using the direct download URL for the zip file
        poppler_url = (
            "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
        )

        # Create a temporary directory for download and extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)
            zip_path = temp_dir_path / "poppler.zip"
            extract_dir = temp_dir_path / "poppler"

            # Create headers to mimic a browser request
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            }

            # Download Poppler with proper headers
            logger.info("Downloading Poppler for Windows...")
            req = urllib.request.Request(poppler_url, headers=headers)

            with (
                urllib.request.urlopen(req) as response,
                open(zip_path, "wb") as out_file,
            ):
                out_file.write(response.read())

            # Extract the ZIP file to temp directory
            logger.info(f"Extracting Poppler to temporary directory: {extract_dir}")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            # Find the bin directory in the extracted contents
            temp_bin_path = extract_dir / "Library" / "bin"
            if not temp_bin_path.exists():
                raise RuntimeError(f"Poppler binaries not found in temporary location: {temp_bin_path}")

            # Move to final location
            final_dir = Path(__file__).parent / "poppler-windows"
            if final_dir.exists():
                shutil.rmtree(final_dir)

            logger.info(f"Moving Poppler to final location: {final_dir}")
            shutil.copytree(extract_dir, final_dir)

            final_bin_path = final_dir / "Library" / "bin"
            if not final_bin_path.exists():
                raise RuntimeError(f"Poppler binaries not found in final location: {final_bin_path}")

            return str(final_bin_path)

    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise RuntimeError(f"Failed to download Poppler: {e!s}") from e
    except zipfile.BadZipFile as e:
        raise RuntimeError("Downloaded file is not a valid ZIP file") from e
    except Exception as e:
        raise RuntimeError(f"Failed to setup Poppler: {e!s}") from e
