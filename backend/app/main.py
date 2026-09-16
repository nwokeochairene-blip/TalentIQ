from app.api.routes.job_descriptions import router as job_descriptions_router
from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.ranking import router as ranking_router
from app.api.routes.suitability import router as suitability_router
from app.api.routes.documents import router as documents_router
from app.api.routes.resumes import router as resumes_router
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

app.include_router(
    ranking_router,
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

app.include_router(documents_router)

app.include_router(resumes_router)

app.include_router(job_descriptions_router)
