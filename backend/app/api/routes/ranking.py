from fastapi import APIRouter, HTTPException

from app.schemas.ranking import (
    RankingRequest,
    RankingResponse,
    RankingResult,
)
from app.services.inference_service import (
    rank_candidates_for_job,
)


router = APIRouter(
    prefix="/api/v1/ranking",
    tags=["Recruiter Ranking"],
)


@router.post(
    "/candidates",
    response_model=RankingResponse,
)
def rank_candidates(
    request: RankingRequest,
) -> RankingResponse:
    """
    Rank multiple candidates against a job description
    using TalentIQ Hybrid V2.
    """

    try:
        candidates = [
            {
                "candidate_id": candidate.candidate_id,
                "resume_text": candidate.resume_text,
            }
            for candidate in request.candidates
        ]

        ranked_df = rank_candidates_for_job(
            job_description=request.job_description,
            candidates=candidates,
        )

        results = []

        for _, row in ranked_df.iterrows():
            results.append(
                RankingResult(
                    rank=int(row["rank"]),
                    candidate_id=str(
                        row["candidate_id"]
                    ),
                    predicted_class=str(
                        row["predicted_class"]
                    ),
                    good_fit_probability=float(
                        row["prob_good_fit"]
                    ),
                    potential_fit_probability=float(
                        row["prob_potential_fit"]
                    ),
                    no_fit_probability=float(
                        row["prob_no_fit"]
                    ),
                    expected_relevance=float(
                        row["expected_relevance"]
                    ),
                    cosine_similarity=float(
                        row["semantic_cosine_similarity"]
                    ),
                    embedding_euclidean_distance=float(
                        row["semantic_euclidean_distance"]
                    ),
                )
            )

        return RankingResponse(
            candidate_count=len(candidates),
            ranking_strategy=(
                "2*P(Good Fit) + P(Potential Fit)"
            ),
            results=results,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Candidate ranking failed.",
        ) from exc
