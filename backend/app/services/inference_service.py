from functools import lru_cache
from pathlib import Path
import sys


# ------------------------------------------------------------
# Locate the verified production inference module
# ------------------------------------------------------------

PROJECT_ROOT = Path(
    "/content/drive/MyDrive/TalentIQ"
)

INFERENCE_DIR = (
    PROJECT_ROOT
    / "artifacts"
    / "inference_package"
)

if not INFERENCE_DIR.exists():
    raise RuntimeError(
        f"TalentIQ inference package not found: {INFERENCE_DIR}"
    )

if str(INFERENCE_DIR) not in sys.path:
    sys.path.insert(0, str(INFERENCE_DIR))


from talentiq_inference import TalentIQInference


# ------------------------------------------------------------
# Singleton inference engine
# ------------------------------------------------------------

@lru_cache(maxsize=1)
def get_inference_engine() -> TalentIQInference:
    """
    Load the verified TalentIQ Hybrid V2 inference engine once.

    The cached engine prevents model artifacts from being
    reloaded for every API request.
    """
    return TalentIQInference()


# ------------------------------------------------------------
# Single candidate-job prediction
# ------------------------------------------------------------

def predict_candidate_job_fit(
    resume_text: str,
    job_description: str,
) -> dict:
    """
    Predict candidate-job suitability using the locked
    TalentIQ Hybrid V2 production inference engine.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError(
            "resume_text cannot be empty."
        )

    if not job_description or not job_description.strip():
        raise ValueError(
            "job_description cannot be empty."
        )

    engine = get_inference_engine()

    return engine.predict(
        resume_text=resume_text,
        job_description=job_description,
    )


# ------------------------------------------------------------
# Candidate ranking
# ------------------------------------------------------------

def rank_candidates_for_job(
    job_description: str,
    candidates: list[dict],
):
    """
    Rank candidates for a job using the locked TalentIQ
    expected-relevance ranking strategy.
    """

    if not job_description or not job_description.strip():
        raise ValueError(
            "job_description cannot be empty."
        )

    if not candidates:
        raise ValueError(
            "candidates cannot be empty."
        )

    engine = get_inference_engine()

    return engine.rank_candidates(
        job_description=job_description,
        candidates=candidates,
    )
