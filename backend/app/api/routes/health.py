from fastapi import APIRouter

from app.core.config import settings
from app.schemas.suitability import HealthResponse


router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get(
    "",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        model=settings.model_name,
        feature_count=settings.model_feature_count,
    )
