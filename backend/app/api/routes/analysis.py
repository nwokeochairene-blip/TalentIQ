from fastapi import APIRouter, HTTPException

from app.schemas.analysis import (
    CandidateJobAnalysisRequest,
    CandidateJobAnalysisResponse,
)
from app.services.analysis_service import analyze_candidate_job

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Candidate-Job Analysis"],
)


@router.post(
    "/candidate-job",
    response_model=CandidateJobAnalysisResponse,
)
def candidate_job_analysis(
    request: CandidateJobAnalysisRequest,
) -> CandidateJobAnalysisResponse:
    try:
        return analyze_candidate_job(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Candidate-job analysis failed.",
        ) from exc
