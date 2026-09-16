from pydantic import BaseModel, Field
from typing import List, Optional


class JobDescriptionProfile(BaseModel):
    job_title: Optional[str] = None
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    required_experience_years: Optional[float] = None
    responsibilities: List[str] = Field(default_factory=list)
    location: Optional[str] = None
