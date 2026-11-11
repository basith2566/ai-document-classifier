"""Extract plain text from PDF, DOCX and TXT files."""
import io
import zipfile

from utils.files import get_extension

MAX_PDF_PAGES = 200


class ExtractionError(Exception):
    """A file could not be read. The message is safe to show to users."""


def extract_text(filename: str, content: bytes) -> str:
    ext = get_extension(filename)
    if ext == ".pdf":
        return _from_pdf(content)
    if ext == ".docx":
        return _from_docx(content)
    if ext == ".txt":
        return _from_txt(content)
    raise ExtractionError(f"Unsupported file type '{ext or 'unknown'}'. Upload a PDF, DOCX or TXT file.")


def _from_pdf(content: bytes) -> str:
    if not content.lstrip().startswith(b"%PDF"):
        raise ExtractionError("This file is not a valid PDF.")
    try:
        import pymupdf as fitz  # newer PyMuPDF name
    except ImportError:
        import fitz  # older name of the same library
    try:
        doc = fitz.open(stream=content, filetype="pdf")
    except Exception:
        raise ExtractionError("The PDF is corrupted and could not be opened.")
    try:
        if doc.needs_pass:
            raise ExtractionError("The PDF is password-protected. Remove the password and upload it again.")
        pages = [page.get_text("text") for page in doc if page.number < MAX_PDF_PAGES]
    except ExtractionError:
        raise
    except Exception:
        raise ExtractionError("Text could not be extracted from this PDF.")
    finally:
        doc.close()
    return "\n".join(pages)


def _from_docx(content: bytes) -> str:
    if not zipfile.is_zipfile(io.BytesIO(content)):
        raise ExtractionError("This file is not a valid DOCX document.")
    try:
        from docx import Document

        document = Document(io.BytesIO(content))
        parts = [p.text for p in document.paragraphs]
        for table in document.tables:
            for row in table.rows:
                parts.append("  ".join(cell.text for cell in row.cells))
        return "\n".join(parts)
    except Exception:
        raise ExtractionError("The DOCX file is corrupted or could not be read.")


def _from_txt(content: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp1252", "latin-1"):
        try:
            text = content.decode(encoding)
            if "\x00" in text:  # binary data decoded as text
                continue
            return text
        except UnicodeError:
            continue
    raise ExtractionError("The text file uses an unsupported encoding.")
