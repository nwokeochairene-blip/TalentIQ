from typing import Dict

from pydantic import BaseModel, Field


class SuitabilityRequest(BaseModel):
    resume_text: str = Field(
        ...,
        min_length=1,
        description="Candidate resume text."
    )

    job_description: str = Field(
        ...,
        min_length=1,
        description="Job description text."
    )


class SuitabilityProbabilities(BaseModel):
    good_fit: float
    no_fit: float
    potential_fit: float


class SemanticFeatures(BaseModel):
    cosine_similarity: float
    embedding_euclidean_distance: float


class SuitabilityResponse(BaseModel):
    predicted_class: str
    probabilities: SuitabilityProbabilities
    expected_relevance: float
    semantic_features: SemanticFeatures
    feature_count: int


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    model: str
    feature_count: int
