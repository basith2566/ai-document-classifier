"""Upload processing and database operations for documents."""
import json
from datetime import datetime, timezone

from database.db import get_connection
from services.classification_service import classify_text
from services.extraction_service import ExtractionError, extract_text
from utils.config import NEEDS_REVIEW_LABEL, settings
from utils.files import ALLOWED_EXTENSIONS, count_words, get_extension, safe_name


class DocumentError(Exception):
    """A document was rejected. The message is safe to show to users."""


def process_upload(filename: str, content: bytes) -> dict:
    """Validate -> extract -> classify -> store. Returns the stored document."""
    filename = safe_name(filename)
    ext = get_extension(filename)

    if ext not in ALLOWED_EXTENSIONS:
        raise DocumentError(f"Unsupported file type '{ext or 'unknown'}'. Upload a PDF, DOCX or TXT file.")
    if len(content) == 0:
        raise DocumentError("The file is empty.")
    if len(content) > settings.max_upload_bytes:
        raise DocumentError(f"The file is larger than the {settings.max_upload_mb} MB limit.")

    try:
        text = extract_text(filename, content)
    except ExtractionError as exc:
        raise DocumentError(str(exc))

    text = text.replace("\x00", "").strip()
    if not text:
        raise DocumentError("No readable text found. Scanned or image-only documents are not supported.")

    result = classify_text(text)
    words = count_words(text)
    stored_text = text[: settings.max_stored_chars]
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with get_connection() as conn:
        cursor = conn.execute(
            """INSERT INTO documents
               (filename, file_type, file_size, category, confidence, needs_review,
                review_reason, probabilities, extracted_text, word_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                filename, ext.lstrip("."), len(content), result.category, result.confidence,
                int(result.needs_review), result.review_reason, json.dumps(result.probabilities),
                stored_text, words, now,
            ),
        )
        doc_id = cursor.lastrowid
    return get_document(doc_id)


def _row_to_dict(row, include_text: bool) -> dict:
    needs_review = bool(row["needs_review"])
    data = {
        "id": row["id"],
        "filename": row["filename"],
        "file_type": row["file_type"],
        "file_size": row["file_size"],
        "category": row["category"],
        "display_category": NEEDS_REVIEW_LABEL if needs_review else row["category"],
        "confidence": row["confidence"],
        "needs_review": needs_review,
        "review_reason": row["review_reason"],
        "word_count": row["word_count"],
        "created_at": row["created_at"],
        "text_preview": row["extracted_text"][:200],
    }
    if include_text:
        data["probabilities"] = json.loads(row["probabilities"])
        data["extracted_text"] = row["extracted_text"]
    return data


def get_document(doc_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM documents WHERE id = ?", (doc_id,)).fetchone()
    return _row_to_dict(row, include_text=True) if row else None


def delete_document(doc_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return cursor.rowcount > 0


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def list_documents(search: str = "", category: str = "", page: int = 1, page_size: int = 20) -> dict:
    where, params = [], []
    if search.strip():
        like = f"%{_escape_like(search.strip())}%"
        where.append("(filename LIKE ? ESCAPE '\\' OR category LIKE ? ESCAPE '\\' OR extracted_text LIKE ? ESCAPE '\\')")
        params += [like, like, like]
    if category == NEEDS_REVIEW_LABEL:
        where.append("needs_review = 1")
    elif category:
        where.append("category = ? AND needs_review = 0")
        params.append(category)
    clause = f"WHERE {' AND '.join(where)}" if where else ""

    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM documents {clause}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM documents {clause} ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            [*params, page_size, (page - 1) * page_size],
        ).fetchall()
    return {
        "items": [_row_to_dict(r, include_text=False) for r in rows],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
