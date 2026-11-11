from fastapi import APIRouter

from models.schemas import ModelInfo, StatsResponse
from services import stats_service

router = APIRouter(tags=["statistics"])


@router.get("/stats", response_model=StatsResponse)
def stats():
    return stats_service.get_stats()


@router.get("/model", response_model=ModelInfo)
def model_info():
    return stats_service.get_model_info()
