from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.services.job_description_parser import parse_job_description
from backend.app.schemas.job_description import JobDescriptionProfile


router = APIRouter(
    prefix="/api/v1/job-descriptions",
    tags=["Job Descriptions"],
)


class JobDescriptionRequest(BaseModel):
    text: str


@router.post("/parse", response_model=JobDescriptionProfile)
def parse_job_description_endpoint(
    request: JobDescriptionRequest,
) -> JobDescriptionProfile:
    try:
        return parse_job_description(request.text)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
