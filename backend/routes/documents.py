import logging

logger = logging.getLogger(__name__)
from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from ml.classifier import ModelNotReadyError
from models.schemas import DocumentDetail, DocumentList, UploadItemResult, UploadResponse
from services import document_service
from services.classification_service import classifier
from services.document_service import DocumentError
from utils.config import settings

router = APIRouter(prefix="/documents", tags=["documents"])


# A normal `def` endpoint runs in a worker thread, so slow PDF parsing and
# model inference never block other requests.
@router.post("/upload", response_model=UploadResponse)
def upload_documents(files: list[UploadFile] = File(...)):
    """Upload one or more files. Each file succeeds or fails independently."""
    if not classifier.is_ready:
        raise HTTPException(503, "The classification model is not available. Train it with `python -m ml.train`.")
    if not files:
        raise HTTPException(400, "No files were uploaded.")
    if len(files) > settings.max_files_per_request:
        raise HTTPException(400, f"Upload at most {settings.max_files_per_request} files at a time.")

    results = []
    for upload in files:
        name = upload.filename or "unnamed"
        try:
            # Read one byte over the limit so oversized files are detected cheaply.
            content = upload.file.read(settings.max_upload_bytes + 1)
            document = document_service.process_upload(name, content)
            results.append(UploadItemResult(filename=name, success=True, document=document))
        except DocumentError as exc:
            results.append(UploadItemResult(filename=name, success=False, error=str(exc)))
        except ModelNotReadyError as exc:
            raise HTTPException(503, str(exc))
        except Exception:
            logger.exception("Failed to process uploaded file: %s", name)
            results.append(
                UploadItemResult(
                    filename=name,
                    success=False,
                    error="Unexpected error while processing this file."
                )
            )
            results.append(UploadItemResult(filename=name, success=False, error="Unexpected error while processing this file."))
    return UploadResponse(results=results)


@router.get("", response_model=DocumentList)
def list_documents(
    search: str = "",
    category: str = "",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    return document_service.list_documents(search, category, page, page_size)


@router.get("/{doc_id}", response_model=DocumentDetail)
def get_document(doc_id: int):
    document = document_service.get_document(doc_id)
    if not document:
        raise HTTPException(404, "Document not found.")
    return document


@router.delete("/{doc_id}", status_code=204)
def delete_document(doc_id: int):
    if not document_service.delete_document(doc_id):
        raise HTTPException(404, "Document not found.")
