"""Aggregate numbers for the dashboard (all computed from the database)."""
from datetime import datetime, timedelta, timezone

from database.db import get_connection
from services.classification_service import classifier
from services.document_service import list_documents
from utils.config import NEEDS_REVIEW_LABEL, settings


def get_stats() -> dict:
    with get_connection() as conn:
        total, review, avg_conf = conn.execute(
            "SELECT COUNT(*), COALESCE(SUM(needs_review), 0), AVG(confidence) FROM documents"
        ).fetchone()
        dist_rows = conn.execute(
            "SELECT category, COUNT(*) AS n FROM documents WHERE needs_review = 0 "
            "GROUP BY category ORDER BY n DESC"
        ).fetchall()
        since = (datetime.now(timezone.utc) - timedelta(days=6)).date().isoformat()
        day_rows = conn.execute(
            "SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS n FROM documents "
            "WHERE substr(created_at, 1, 10) >= ? GROUP BY day",
            (since,),
        ).fetchall()

    distribution = [{"category": r["category"], "count": r["n"]} for r in dist_rows]
    if review:
        distribution.append({"category": NEEDS_REVIEW_LABEL, "count": review})

    per_day = {r["day"]: r["n"] for r in day_rows}
    today = datetime.now(timezone.utc).date()
    daily = []
    for i in range(6, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        daily.append({"date": d, "count": per_day.get(d, 0)})

    return {
        "total_documents": total,
        "auto_classified": total - review,
        "needs_review": review,
        "average_confidence": round(avg_conf, 4) if avg_conf is not None else None,
        "category_distribution": distribution,
        "daily_activity": daily,
        "recent_activity": list_documents(page=1, page_size=6)["items"],
    }


def get_model_info() -> dict:
    return {
        "ready": classifier.is_ready,
        "labels": classifier.labels,
        "confidence_threshold": settings.confidence_threshold,
        "metrics": classifier.metrics or None,
    }
