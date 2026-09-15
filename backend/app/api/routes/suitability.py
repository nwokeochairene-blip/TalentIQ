from fastapi import APIRouter, HTTPException

from app.schemas.suitability import (
    SuitabilityRequest,
    SuitabilityResponse,
)
from app.services.inference_service import (
    predict_candidate_job_fit,
)


router = APIRouter(
    prefix="/api/v1/suitability",
    tags=["Suitability"],
)


@router.post(
    "/predict",
    response_model=SuitabilityResponse,
)
def predict_suitability(
    request: SuitabilityRequest,
) -> SuitabilityResponse:
    """
    Predict candidate-job suitability using TalentIQ Hybrid V2.
    """

    try:
        result = predict_candidate_job_fit(
            resume_text=request.resume_text,
            job_description=request.job_description,
        )

        probabilities = result["probabilities"]
        semantic = result["semantic_features"]

        return SuitabilityResponse(
            predicted_class=result["predicted_class"],
            probabilities={
                "good_fit": probabilities["Good Fit"],
                "no_fit": probabilities["No Fit"],
                "potential_fit": probabilities["Potential Fit"],
            },
            expected_relevance=result["expected_relevance"],
            semantic_features={
                "cosine_similarity": semantic[
                    "cosine_similarity"
                ],
                "embedding_euclidean_distance": semantic[
                    "embedding_euclidean_distance"
                ],
            },
            feature_count=result["feature_count"],
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Suitability inference failed.",
        ) from exc
