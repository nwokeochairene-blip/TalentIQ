from app.schemas.resume import ResumeProfile
from app.services.resume_parser import parse_resume


def parse_resume_text(resume_text: str) -> ResumeProfile:
    """
    Parse already-extracted resume text into a structured profile.

    The parser is deterministic and conservative:
    it extracts only information supported by the document.
    """

    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    return parse_resume(resume_text)
