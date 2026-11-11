"""Pydantic models that describe the API responses (they also power /docs)."""
from pydantic import BaseModel


class ClassProbability(BaseModel):
    category: str
    probability: float


class DocumentSummary(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    category: str
    display_category: str
    confidence: float
    needs_review: bool
    review_reason: str | None = None
    word_count: int
    created_at: str
    text_preview: str


class DocumentDetail(DocumentSummary):
    probabilities: list[ClassProbability]
    extracted_text: str


class UploadItemResult(BaseModel):
    filename: str
    success: bool
    document: DocumentDetail | None = None
    error: str | None = None


class UploadResponse(BaseModel):
    results: list[UploadItemResult]


class DocumentList(BaseModel):
    items: list[DocumentSummary]
    total: int
    page: int
    page_size: int


class CategoryCount(BaseModel):
    category: str
    count: int


class DailyCount(BaseModel):
    date: str
    count: int


class StatsResponse(BaseModel):
    total_documents: int
    auto_classified: int
    needs_review: int
    average_confidence: float | None
    category_distribution: list[CategoryCount]
    daily_activity: list[DailyCount]
    recent_activity: list[DocumentSummary]


class ModelInfo(BaseModel):
    ready: bool
    labels: list[str]
    confidence_threshold: float
    metrics: dict | None = None
