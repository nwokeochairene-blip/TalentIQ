from pydantic import BaseModel, Field

from app.schemas.resume import ResumeProfile
from app.schemas.job_description import JobDescriptionProfile
from app.schemas.suitability import SuitabilityResponse


class CandidateJobAnalysisRequest(BaseModel):
    resume_text: str = Field(
        ...,
        min_length=1,
        description="Candidate resume text.",
    )

    job_description: str = Field(
        ...,
        min_length=1,
        description="Job description text.",
    )


class CandidateJobAnalysisResponse(BaseModel):
    candidate_profile: ResumeProfile
    job_profile: JobDescriptionProfile
    suitability: SuitabilityResponse
