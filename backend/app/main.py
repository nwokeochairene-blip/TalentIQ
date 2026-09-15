from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.suitability import router as suitability_router
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered candidate-job suitability and "
        "recruitment intelligence API."
    ),
)


# ------------------------------------------------------------
# API routes
# ------------------------------------------------------------

app.include_router(
    health_router,
)

app.include_router(
    suitability_router,
)


# ------------------------------------------------------------
# Root
# ------------------------------------------------------------

@app.get("/")
def root():
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
    }
