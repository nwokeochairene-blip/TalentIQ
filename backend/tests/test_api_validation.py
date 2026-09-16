from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)

FIXTURES_DIR = Path(__file__).parent / "test_documents"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_candidate_job_analysis():
    response = client.post(
        "/api/v1/analysis/candidate-job",
        json={
            "resume_text": """
            Jane Doe
            Full Stack Software Developer

            Professional Summary
            Full Stack Developer with 5 years of experience building web applications.

            Technical Skills
            Python, FastAPI, PostgreSQL, React, TypeScript, Docker, Git.

            Experience
            Software Developer — Tech Solutions
            Developed REST APIs and production web applications using Python and FastAPI.
            """,
            "job_description": """
            Job Title: Backend Developer
            Location: Remote

            Required Skills:
            Python, FastAPI, PostgreSQL

            Preferred Skills:
            Docker, Cloud Deployment, Git

            Requirements:
            At least 2 years of experience

            Responsibilities:
            - Build APIs
            - Maintain databases
            - Troubleshoot backend issues
            """,
        },
    )

    assert response.status_code == 200

    result = response.json()

    assert "candidate_profile" in result
    assert "job_profile" in result
    assert "suitability" in result
    assert result["suitability"]["feature_count"] == 100019


def test_pdf_document_extraction():
    pdf_path = FIXTURES_DIR / "sample_resume.pdf"

    with pdf_path.open("rb") as file:
        response = client.post(
            "/api/v1/documents/extract",
            files={
                "file": (
                    "sample_resume.pdf",
                    file,
                    "application/pdf",
                )
            },
        )

    assert response.status_code == 200
    assert response.json()["file_type"] == "pdf"
    assert response.json()["extracted_text"].strip()


def test_docx_document_extraction():
    docx_path = FIXTURES_DIR / "sample_resume.docx"

    with docx_path.open("rb") as file:
        response = client.post(
            "/api/v1/documents/extract",
            files={
                "file": (
                    "sample_resume.docx",
                    file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    assert response.status_code == 200
    assert response.json()["file_type"] == "docx"
    assert response.json()["extracted_text"].strip()


def test_unsupported_file_type():
    response = client.post(
        "/api/v1/documents/extract",
        files={
            "file": (
                "malicious.exe",
                BytesIO(b"Unsupported file content"),
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_empty_document():
    response = client.post(
        "/api/v1/documents/extract",
        files={
            "file": (
                "empty.pdf",
                BytesIO(b""),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."


def test_empty_resume_text():
    response = client.post(
        "/api/v1/resumes/parse",
        params={"resume_text": ""},
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Resume text cannot be empty."


def test_empty_job_description():
    response = client.post(
        "/api/v1/job-descriptions/parse",
        json={"text": ""},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Job description text cannot be empty."


def test_malformed_analysis_request():
    response = client.post(
        "/api/v1/analysis/candidate-job",
        json={"resume_text": "Jane Doe — Python Developer"},
    )

    assert response.status_code == 422
