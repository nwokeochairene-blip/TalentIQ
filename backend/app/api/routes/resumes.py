from fastapi import APIRouter, HTTPException

from app.schemas.resume import ResumeProfile
from app.services.resume_service import parse_resume_text


router = APIRouter(
    prefix="/api/v1/resumes",
    tags=["Resumes"],
)


@router.post(
    "/parse",
    response_model=ResumeProfile,
)
def parse_resume_endpoint(resume_text: str):
    """
    Parse resume text into a structured candidate profile.
    """

    try:
        return parse_resume_text(resume_text)

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Resume parsing failed.",
        ) from exc
