from pydantic import BaseModel, Field


class ExperienceItem(BaseModel):
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class EducationItem(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None


class CertificationItem(BaseModel):
    name: str
    issuer: str | None = None
    date: str | None = None


class ProjectItem(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None

    summary: str | None = None

    skills: list[str] = Field(default_factory=list)

    experience: list[ExperienceItem] = Field(
        default_factory=list
    )

    education: list[EducationItem] = Field(
        default_factory=list
    )

    certifications: list[CertificationItem] = Field(
        default_factory=list
    )

    projects: list[ProjectItem] = Field(
        default_factory=list
    )
