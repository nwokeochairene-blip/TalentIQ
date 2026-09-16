from app.schemas.analysis import (
    CandidateJobAnalysisResponse,
)
from app.services.resume_service import parse_resume_text
from app.services.job_description_parser import parse_job_description
from app.services.inference_service import predict_candidate_job_fit


def analyze_candidate_job(
    resume_text: str,
    job_description: str,
) -> CandidateJobAnalysisResponse:
    """
    Perform end-to-end candidate-job analysis.

    Workflow:
    1. Parse the resume.
    2. Parse the job description.
    3. Run the verified Hybrid V2 suitability model.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")

    if not job_description or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    candidate_profile = parse_resume_text(resume_text)
    job_profile = parse_job_description(job_description)

    raw_result = predict_candidate_job_fit(
        resume_text=resume_text,
        job_description=job_description,
    )

    probabilities = raw_result["probabilities"]
    semantic = raw_result["semantic_features"]

    suitability = {
        "predicted_class": raw_result["predicted_class"],
        "probabilities": {
            "good_fit": probabilities["Good Fit"],
            "no_fit": probabilities["No Fit"],
            "potential_fit": probabilities["Potential Fit"],
        },
        "expected_relevance": raw_result["expected_relevance"],
        "semantic_features": {
            "cosine_similarity": semantic["cosine_similarity"],
            "embedding_euclidean_distance": semantic[
                "embedding_euclidean_distance"
            ],
        },
        "feature_count": raw_result["feature_count"],
    }

    return CandidateJobAnalysisResponse(
        candidate_profile=candidate_profile,
        job_profile=job_profile,
        suitability=suitability,
    )
