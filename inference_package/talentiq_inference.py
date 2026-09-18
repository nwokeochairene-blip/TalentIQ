"""
TalentIQ Hybrid V2 — Production Inference Module

This module provides production inference for candidate-job
suitability prediction and candidate ranking.

Model:
    TalentIQ Hybrid V2

Task:
    Candidate-job suitability

Important:
    This model predicts suitability, NOT hiring probability.

Ranking:
    Expected Relevance =
        2 * P(Good Fit) + P(Potential Fit)

The module loads trained artifacts from a configurable model root.
"""

import os
import re
import joblib
import numpy as np
import pandas as pd

from scipy.sparse import hstack, csr_matrix
from sentence_transformers import SentenceTransformer


# ======================================================================
# Configuration
# ======================================================================

DEFAULT_MODEL_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

STRUCTURED_FEATURE_NAMES = [
    "resume_word_count",
    "jd_word_count",
    "resume_char_count",
    "jd_char_count",
    "resume_unique_token_count",
    "jd_unique_token_count",
    "resume_unique_ratio",
    "jd_unique_ratio",
    "length_ratio",
    "resume_log_words",
    "jd_log_words",
    "token_overlap_count",
    "jaccard_similarity",
    "resume_coverage",
    "jd_coverage",
    "bigram_overlap_count",
    "bigram_jaccard",
]

VALID_CLASSES = {
    "Good Fit",
    "Potential Fit",
    "No Fit",
}

EXPECTED_FEATURE_COUNT = 100019

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)


# ======================================================================
# Text normalization
# ======================================================================

def normalize_for_features(text):
    """
    Conservative text normalization used by the production pipeline.
    """

    text = str(text)

    text = text.replace(
        "\r\n",
        "\n"
    ).replace(
        "\r",
        "\n"
    )

    text = text.replace(
        "\xa0",
        " "
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n\s*\n+",
        "\n\n",
        text
    )

    return text.strip()


def tokenize(text):
    """
    Whitespace tokenization used by the structured feature pipeline.
    """

    return text.lower().split()


def make_bigrams(tokens):
    """
    Create a set of adjacent token bigrams.
    """

    if len(tokens) < 2:
        return set()

    return set(
        zip(
            tokens[:-1],
            tokens[1:]
        )
    )


# ======================================================================
# Structured features
# ======================================================================

def extract_structured_features(
    resume_text,
    jd_text
):
    """
    Generate the exact 17 structured features used by Hybrid V2.

    Returns
    -------
    pandas.DataFrame
        One-row DataFrame with the exact feature names used when
        fitting the StandardScaler.
    """

    resume = normalize_for_features(
        resume_text
    )

    jd = normalize_for_features(
        jd_text
    )

    resume_tokens = tokenize(
        resume
    )

    jd_tokens = tokenize(
        jd
    )

    resume_set = set(
        resume_tokens
    )

    jd_set = set(
        jd_tokens
    )

    resume_bigrams = make_bigrams(
        resume_tokens
    )

    jd_bigrams = make_bigrams(
        jd_tokens
    )

    resume_word_count = len(
        resume_tokens
    )

    jd_word_count = len(
        jd_tokens
    )

    resume_char_count = len(
        resume
    )

    jd_char_count = len(
        jd
    )

    resume_unique_token_count = len(
        resume_set
    )

    jd_unique_token_count = len(
        jd_set
    )

    resume_unique_ratio = (
        resume_unique_token_count
        / resume_word_count
        if resume_word_count
        else 0.0
    )

    jd_unique_ratio = (
        jd_unique_token_count
        / jd_word_count
        if jd_word_count
        else 0.0
    )

    length_ratio = (
        resume_word_count
        / jd_word_count
        if jd_word_count
        else 0.0
    )

    resume_log_words = np.log1p(
        resume_word_count
    )

    jd_log_words = np.log1p(
        jd_word_count
    )

    token_overlap = (
        resume_set & jd_set
    )

    token_overlap_count = len(
        token_overlap
    )

    token_union = (
        resume_set | jd_set
    )

    jaccard_similarity = (
        len(token_overlap)
        / len(token_union)
        if token_union
        else 0.0
    )

    resume_coverage = (
        len(token_overlap)
        / len(resume_set)
        if resume_set
        else 0.0
    )

    jd_coverage = (
        len(token_overlap)
        / len(jd_set)
        if jd_set
        else 0.0
    )

    bigram_overlap = (
        resume_bigrams & jd_bigrams
    )

    bigram_overlap_count = len(
        bigram_overlap
    )

    bigram_union = (
        resume_bigrams | jd_bigrams
    )

    bigram_jaccard = (
        len(bigram_overlap)
        / len(bigram_union)
        if bigram_union
        else 0.0
    )

    values = [[
        resume_word_count,
        jd_word_count,
        resume_char_count,
        jd_char_count,
        resume_unique_token_count,
        jd_unique_token_count,
        resume_unique_ratio,
        jd_unique_ratio,
        length_ratio,
        resume_log_words,
        jd_log_words,
        token_overlap_count,
        jaccard_similarity,
        resume_coverage,
        jd_coverage,
        bigram_overlap_count,
        bigram_jaccard,
    ]]

    return pd.DataFrame(
        values,
        columns=STRUCTURED_FEATURE_NAMES
    )


# ======================================================================
# Production model wrapper
# ======================================================================

class TalentIQInference:
    """
    Production wrapper for TalentIQ Hybrid V2.
    """

    def __init__(
        self,
        model_root=None,
        embedding_device=None
    ):

        if model_root is None:
            model_root = DEFAULT_MODEL_ROOT

        self.model_root = os.path.abspath(
            model_root
        )

        self.model_dir = os.path.join(
            self.model_root,
            "models"
        )

        self.embedding_dir = os.path.join(
            self.model_root,
            "embeddings"
        )

        # --------------------------------------------------------------
        # Model artifacts
        # --------------------------------------------------------------

        classifier_path = os.path.join(
            self.model_dir,
            "hybrid_v2_tfidf_structured_semantic_logreg.joblib"
        )

        tfidf_path = os.path.join(
            self.model_dir,
            "tfidf_vectorizer_baseline.joblib"
        )

        structured_scaler_path = os.path.join(
            self.model_dir,
            "hybrid_structured_scaler.joblib"
        )

        semantic_scaler_path = os.path.join(
            self.model_dir,
            "hybrid_v2_semantic_scaler.joblib"
        )

        required_paths = {
            "classifier": classifier_path,
            "tfidf_vectorizer": tfidf_path,
            "structured_scaler": structured_scaler_path,
            "semantic_scaler": semantic_scaler_path,
        }

        for name, path in required_paths.items():

            if not os.path.exists(path):
                raise FileNotFoundError(
                    f"Missing {name} artifact: {path}"
                )

        # --------------------------------------------------------------
        # Load artifacts
        # --------------------------------------------------------------

        self.classifier = joblib.load(
            classifier_path
        )

        self.tfidf_vectorizer = joblib.load(
            tfidf_path
        )

        self.structured_scaler = joblib.load(
            structured_scaler_path
        )

        self.semantic_scaler = joblib.load(
            semantic_scaler_path
        )

        # --------------------------------------------------------------
        # Verify classifier
        # --------------------------------------------------------------

        if self.classifier.n_features_in_ != (
            EXPECTED_FEATURE_COUNT
        ):
            raise ValueError(
                "Unexpected classifier feature count: "
                f"{self.classifier.n_features_in_}"
            )

        expected_classes = np.array([
            "Good Fit",
            "No Fit",
            "Potential Fit"
        ])

        if not np.array_equal(
            self.classifier.classes_,
            expected_classes
        ):
            raise ValueError(
                "Classifier class ordering does not match "
                "the locked production configuration."
            )

        # --------------------------------------------------------------
        # Embedding model
        # --------------------------------------------------------------

        if embedding_device is None:

            try:
                import torch

                embedding_device = (
                    "cuda"
                    if torch.cuda.is_available()
                    else "cpu"
                )

            except Exception:
                embedding_device = "cpu"

        self.embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME,
            device=embedding_device
        )

        embedding_dimension = (
            self.embedding_model
            .get_embedding_dimension()
        )

        if embedding_dimension != 384:
            raise ValueError(
                "Unexpected embedding dimension: "
                f"{embedding_dimension}"
            )

    # ==================================================================
    # Single-pair prediction
    # ==================================================================

    def predict(
        self,
        resume_text,
        job_description
    ):

        if not isinstance(
            resume_text,
            str
        ) or not resume_text.strip():

            raise ValueError(
                "resume_text must be a non-empty string."
            )

        if not isinstance(
            job_description,
            str
        ) or not job_description.strip():

            raise ValueError(
                "job_description must be a non-empty string."
            )

        resume_clean = normalize_for_features(
            resume_text
        )

        jd_clean = normalize_for_features(
            job_description
        )

        # --------------------------------------------------------------
        # TF-IDF
        # --------------------------------------------------------------

        pair_text = (
            "RESUME "
            + resume_clean
            + " JOB_DESCRIPTION "
            + jd_clean
        )

        tfidf_features = (
            self.tfidf_vectorizer.transform(
                [pair_text]
            )
        )

        # --------------------------------------------------------------
        # Structured
        # --------------------------------------------------------------

        structured_raw = (
            extract_structured_features(
                resume_clean,
                jd_clean
            )
        )

        structured_scaled = (
            self.structured_scaler.transform(
                structured_raw
            )
        )

        structured_sparse = csr_matrix(
            structured_scaled
        )

        # --------------------------------------------------------------
        # Semantic
        # --------------------------------------------------------------

        embeddings = (
            self.embedding_model.encode(
                [
                    resume_clean,
                    jd_clean
                ],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False
            ).astype(np.float32)
        )

        resume_embedding = embeddings[0]
        jd_embedding = embeddings[1]

        cosine_similarity = float(
            np.dot(
                resume_embedding,
                jd_embedding
            )
        )

        euclidean_distance = float(
            np.linalg.norm(
                resume_embedding
                - jd_embedding
            )
        )

        # Semantic scaler was fitted without feature names,
        # so provide the exact NumPy array representation used
        # during model development.
        semantic_raw = np.array(
            [[
                cosine_similarity,
                euclidean_distance
            ]],
            dtype=np.float64
        )

        semantic_scaled = (
            self.semantic_scaler.transform(
                semantic_raw
            )
        )

        semantic_sparse = csr_matrix(
            semantic_scaled
        )

        # --------------------------------------------------------------
        # Hybrid feature vector
        # --------------------------------------------------------------

        hybrid_features = hstack(
            [
                tfidf_features,
                structured_sparse,
                semantic_sparse
            ],
            format="csr"
        )

        if hybrid_features.shape[1] != (
            EXPECTED_FEATURE_COUNT
        ):
            raise ValueError(
                "Unexpected hybrid feature count: "
                f"{hybrid_features.shape[1]}"
            )

        # --------------------------------------------------------------
        # Prediction
        # --------------------------------------------------------------

        probabilities = (
            self.classifier
            .predict_proba(
                hybrid_features
            )[0]
        )

        probability_map = {
            class_name: float(probability)
            for class_name, probability in zip(
                self.classifier.classes_,
                probabilities
            )
        }

        predicted_index = int(
            np.argmax(probabilities)
        )

        predicted_class = (
            self.classifier
            .classes_[predicted_index]
        )

        expected_relevance = (
            2.0 * probability_map["Good Fit"]
            + probability_map["Potential Fit"]
        )

        # --------------------------------------------------------------
        # Integrity
        # --------------------------------------------------------------

        if not np.isfinite(
            probabilities
        ).all():

            raise ValueError(
                "Non-finite prediction probabilities."
            )

        if abs(
            probabilities.sum() - 1.0
        ) >= 1e-10:

            raise ValueError(
                "Prediction probabilities do not sum to 1."
            )

        return {
            "predicted_class":
                predicted_class,

            "probabilities":
                probability_map,

            "expected_relevance":
                float(expected_relevance),

            "semantic_features": {
                "cosine_similarity":
                    cosine_similarity,

                "embedding_euclidean_distance":
                    euclidean_distance
            },

            "structured_features":
                {
                    name: float(value)
                    for name, value in zip(
                        STRUCTURED_FEATURE_NAMES,
                        structured_raw.iloc[0].values
                    )
                },

            "feature_count":
                int(hybrid_features.shape[1])
        }

    # ==================================================================
    # Batch ranking
    # ==================================================================

    def rank_candidates(
        self,
        job_description,
        candidates
    ):

        if not isinstance(
            candidates,
            list
        ) or len(candidates) == 0:

            raise ValueError(
                "candidates must be a non-empty list."
            )

        results = []

        for candidate in candidates:

            if not isinstance(
                candidate,
                dict
            ):

                raise ValueError(
                    "Each candidate must be a dictionary."
                )

            if "candidate_id" not in candidate:
                raise ValueError(
                    "Candidate missing candidate_id."
                )

            if "resume" not in candidate:
                raise ValueError(
                    "Candidate missing resume."
                )

            prediction = self.predict(
                resume_text=candidate["resume"],
                job_description=job_description
            )

            probabilities = (
                prediction["probabilities"]
            )

            results.append({
                "candidate_id":
                    candidate["candidate_id"],

                "predicted_class":
                    prediction["predicted_class"],

                "prob_good_fit":
                    probabilities["Good Fit"],

                "prob_potential_fit":
                    probabilities["Potential Fit"],

                "prob_no_fit":
                    probabilities["No Fit"],

                "expected_relevance":
                    prediction["expected_relevance"],

                "semantic_cosine_similarity":
                    prediction[
                        "semantic_features"
                    ]["cosine_similarity"],

                "semantic_euclidean_distance":
                    prediction[
                        "semantic_features"
                    ]["embedding_euclidean_distance"],
            })

        ranking_df = pd.DataFrame(
            results
        )

        ranking_df = ranking_df.sort_values(
            by=[
                "expected_relevance",
                "prob_good_fit",
                "prob_potential_fit"
            ],
            ascending=False
        ).reset_index(
            drop=True
        )

        ranking_df.insert(
            0,
            "rank",
            np.arange(
                1,
                len(ranking_df) + 1
            )
        )

        return ranking_df


__all__ = [
    "TalentIQInference",
    "extract_structured_features",
    "normalize_for_features",
]
