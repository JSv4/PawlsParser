import logging
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
import os

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

    # Define AppData location for Poppler
    poppler_dir = Path.home() / 'AppData/Roaming/PDFTokenizer/poppler'
    poppler_path = poppler_dir / "Library" / "bin"
    
    if poppler_path.exists():
        return str(poppler_path)

    return setup_poppler_windows()


def setup_poppler_windows() -> str:
    """
    Downloads and sets up Poppler for Windows in a temporary directory.
    
    Returns:
        str: Path to the Poppler binaries directory
    
    Raises:
        RuntimeError: If setup fails
    """
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, "poppler.zip")
    extract_dir = os.path.join(temp_dir, "extract")
    
    try:
        # Download Poppler
        logger.info("Downloading Poppler for Windows...")
        download_url = "https://github.com/oschwartz10612/poppler-windows/releases/download/v24.08.0-0/Release-24.08.0-0.zip"
        urllib.request.urlretrieve(download_url, zip_path)
        
        # Extract ZIP
        logger.info(f"Extracting ZIP file from {zip_path}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
            
        # Find the bin directory
        poppler_version_dir = next(d for d in os.listdir(extract_dir) if d.startswith('poppler-'))
        bin_dir = os.path.join(extract_dir, poppler_version_dir, 'Library', 'bin')
        
        if not os.path.exists(bin_dir):
            raise RuntimeError(f"Poppler binaries not found in temporary location: {bin_dir}")
            
        # Verify key executables exist
        required_exes = ['pdftotext.exe', 'pdftoppm.exe']
        for exe in required_exes:
            if not os.path.exists(os.path.join(bin_dir, exe)):
                raise RuntimeError(f"Required Poppler executable not found: {exe}")
                
        return bin_dir
        
    except Exception as e:
        # Clean up temp dir on failure
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(f"Failed to setup Poppler: {str(e)}")
