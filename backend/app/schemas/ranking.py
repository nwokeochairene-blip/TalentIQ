from typing import List

from pydantic import BaseModel, Field


class RankingCandidate(BaseModel):
    candidate_id: str = Field(
        ...,
        min_length=1,
        description="Unique candidate identifier."
    )

    resume_text: str = Field(
        ...,
        min_length=1,
        description="Candidate resume text."
    )


class RankingRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=1,
        description="Job description used for ranking."
    )

    candidates: List[RankingCandidate] = Field(
        ...,
        min_length=1,
        description="Candidates to rank."
    )


class RankingResult(BaseModel):
    rank: int
    candidate_id: str
    predicted_class: str
    good_fit_probability: float
    potential_fit_probability: float
    no_fit_probability: float
    expected_relevance: float
    cosine_similarity: float
    embedding_euclidean_distance: float


class RankingResponse(BaseModel):
    candidate_count: int
    ranking_strategy: str
    results: List[RankingResult]
