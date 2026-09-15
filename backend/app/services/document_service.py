"""
TalentIQ document processing service.

Supports text extraction from:
- PDF
- DOCX

The service is intentionally independent of FastAPI so it can
be reused by API routes, background jobs, and future pipelines.
"""

from pathlib import Path


SUPPORTED_EXTENSIONS = {".pdf", ".docx"}


class DocumentProcessingError(Exception):
    """Raised when a document cannot be processed."""
    pass


def extract_text_from_pdf(file_path: str | Path) -> str:
    """
    Extract text from a PDF document.
    """

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DocumentProcessingError(
            "pypdf is not installed."
        ) from exc

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"File not found: {path}"
        )

    try:
        reader = PdfReader(str(path))
        pages = []

        for page in reader.pages:
            text = page.extract_text() or ""
            pages.append(text)

        return "\n".join(pages).strip()

    except Exception as exc:
        raise DocumentProcessingError(
            f"Unable to extract text from PDF: {path.name}"
        ) from exc


def extract_text_from_docx(file_path: str | Path) -> str:
    """
    Extract text from a DOCX document.
    """

    try:
        from docx import Document
    except ImportError as exc:
        raise DocumentProcessingError(
            "python-docx is not installed."
        ) from exc

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"File not found: {path}"
        )

    try:
        document = Document(str(path))

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs).strip()

    except Exception as exc:
        raise DocumentProcessingError(
            f"Unable to extract text from DOCX: {path.name}"
        ) from exc


def extract_text(file_path: str | Path) -> str:
    """
    Extract text from a supported document based on its extension.
    """

    path = Path(file_path)

    if not path.exists():
        raise DocumentProcessingError(
            f"File not found: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        text = extract_text_from_pdf(path)

    elif extension == ".docx":
        text = extract_text_from_docx(path)

    else:
        raise DocumentProcessingError(
            f"Unsupported file type: {extension}. "
            f"Supported types: {sorted(SUPPORTED_EXTENSIONS)}"
        )

    if not text.strip():
        raise DocumentProcessingError(
            "No text could be extracted from the document."
        )

    return text


def normalize_extracted_text(text: str) -> str:
    """
    Conservative normalization for extracted document text.

    This does not perform semantic cleaning or resume parsing.
    """

    if not isinstance(text, str):
        raise ValueError("text must be a string.")

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")

    lines = [
        " ".join(line.split())
        for line in text.split("\n")
    ]

    lines = [
        line for line in lines
        if line
    ]

    return "\n".join(lines).strip()
