"""
TalentIQ deterministic resume parser.

Purpose:
    Convert extracted resume text into a structured ResumeProfile.

Design principles:
    - Conservative extraction
    - No hallucinated fields
    - No demographic inference
    - Preserve source text where possible
    - Semantic enrichment can be added later
"""

import re

from app.schemas.resume import (
    CertificationItem,
    EducationItem,
    ExperienceItem,
    ProjectItem,
    ResumeProfile,
)


SECTION_ALIASES = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "objective",
        "career objective",
    },
    "skills": {
        "skills",
        "technical skills",
        "core skills",
        "key skills",
        "technologies",
        "technical expertise",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
    },
    "education": {
        "education",
        "academic background",
        "academic qualifications",
    },
    "certifications": {
        "certifications",
        "certificates",
        "professional certifications",
    },
    "projects": {
        "projects",
        "key projects",
        "selected projects",
    },
}


EMAIL_PATTERN = re.compile(
    r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}\\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\\d)(?:\\+?\\d[\\d\\s().-]{7,}\\d)(?!\\d)"
)

DATE_PATTERN = re.compile(
    r"\\b(?:"
    r"Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
    r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?"
    r")?\\s*\\d{4}\\b"
    r"|\\b\\d{4}\\s*[-–—]\\s*(?:Present|Current|\\d{4})\\b",
    re.IGNORECASE,
)


def clean_lines(text: str) -> list[str]:
    """
    Prepare resume text for section detection.

    Handles both:
    - normally line-separated extracted text
    - flattened extraction where the entire document becomes one line

    This parser-specific reconstruction does not modify the
    production ML normalization pipeline.
    """

    if not isinstance(text, str):
        raise ValueError("Resume text must be a string.")

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")

    raw_lines = [
        " ".join(line.split()).strip()
        for line in text.split("\n")
        if line.strip()
    ]

    if len(raw_lines) == 1:
        flattened = raw_lines[0]

        headings = sorted(
            {
                heading
                for aliases in SECTION_ALIASES.values()
                for heading in aliases
            },
            key=len,
            reverse=True,
        )

        # Find all headings in the ORIGINAL flattened text.
        matches = []

        for heading in headings:
            pattern = re.compile(
                rf"(?<!\w){re.escape(heading)}(?!\w)",
                re.IGNORECASE,
            )

            for match in pattern.finditer(flattened):
                matches.append(
                    (
                        match.start(),
                        match.end(),
                        match.group(0),
                    )
                )

        # Remove nested/overlapping matches.
        matches.sort(key=lambda item: (item[0], -(item[1] - item[0])))

        selected = []

        for match in matches:
            start_pos, end_pos, heading_text = match

            if any(
                start_pos < existing_end
                and end_pos > existing_start
                for existing_start, existing_end, _
                in selected
            ):
                continue

            selected.append(match)

        selected.sort(key=lambda item: item[0])

        # Reconstruct lines using the selected heading positions.
        reconstructed = []

        cursor = 0

        for start_pos, end_pos, heading_text in selected:
            before = flattened[cursor:start_pos].strip()

            if before:
                reconstructed.append(before)

            reconstructed.append(
                heading_text.strip()
            )

            cursor = end_pos

        remaining = flattened[cursor:].strip()

        if remaining:
            reconstructed.append(remaining)

        raw_lines = [
            " ".join(line.split()).strip()
            for line in reconstructed
            if line.strip()
        ]

    return raw_lines


def detect_sections(lines: list[str]) -> dict[str, list[str]]:
    """Split resume lines into recognized sections."""

    sections: dict[str, list[str]] = {}
    current_section = "header"

    sections[current_section] = []

    alias_lookup = {}

    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            alias_lookup[alias.lower()] = section

    for line in lines:
        normalized = line.lower().strip(" :|-")

        if normalized in alias_lookup:
            current_section = alias_lookup[normalized]
            sections.setdefault(current_section, [])
            continue

        sections.setdefault(current_section, [])
        sections[current_section].append(line)

    return sections


def extract_name(header_lines: list[str]) -> str | None:
    """Conservatively identify a likely name from the header."""

    for line in header_lines[:5]:
        if (
            "@" in line
            or PHONE_PATTERN.search(line)
            or any(char.isdigit() for char in line)
        ):
            continue

        words = line.split()

        if 2 <= len(words) <= 4:
            if all(
                re.match(r"^[A-Za-z][A-Za-z'’-]*$", word)
                for word in words
            ):
                return line

    return None


def extract_email(text: str) -> str | None:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    match = PHONE_PATTERN.search(text)
    return match.group(0).strip() if match else None


def parse_skills(lines: list[str]) -> list[str]:
    """
    Extract skills conservatively.

    Handles comma/semicolon/bullet-separated skill lists.
    """

    skills = []

    for line in lines:
        parts = re.split(r"[,;|•·]", line)

        for part in parts:
            skill = part.strip(" -–—:.,;|")

            if not skill:
                continue

            if len(skill) > 80:
                continue

            if len(skill.split()) > 8:
                continue

            skills.append(skill)

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(skills))


def parse_experience(lines: list[str]) -> list[ExperienceItem]:
    """Create conservative experience entries."""

    if not lines:
        return []

    entries = []
    current_lines = []

    for line in lines:
        if DATE_PATTERN.search(line) and current_lines:
            entries.append(
                _experience_from_lines(current_lines)
            )
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        entries.append(
            _experience_from_lines(current_lines)
        )

    return [
        entry for entry in entries
        if entry.job_title
        or entry.company
        or entry.description
    ]


def _experience_from_lines(
    lines: list[str],
) -> ExperienceItem:

    if not lines:
        return ExperienceItem()

    first = lines[0]

    dates = DATE_PATTERN.findall(first)

    start_date = None
    end_date = None

    if dates:
        date_text = dates[0]

        if " - " in date_text:
            start_date, end_date = [
                part.strip()
                for part in date_text.split("-", 1)
            ]

    description_lines = lines[1:]

    return ExperienceItem(
        job_title=first,
        start_date=start_date,
        end_date=end_date,
        description="\n".join(description_lines).strip() or None,
    )


def parse_education(lines: list[str]) -> list[EducationItem]:
    """Create conservative education entries."""

    if not lines:
        return []

    entries = []

    for line in lines:
        entries.append(
            EducationItem(
                institution=line,
            )
        )

    return entries


def parse_certifications(
    lines: list[str],
) -> list[CertificationItem]:
    """Extract certification names without inventing issuers."""

    return [
        CertificationItem(name=line)
        for line in lines
        if line.strip()
    ]


def parse_projects(
    lines: list[str],
) -> list[ProjectItem]:
    """Extract project names/descriptions conservatively."""

    projects = []

    for line in lines:
        if ":" in line:
            name, description = line.split(":", 1)

            projects.append(
                ProjectItem(
                    name=name.strip(),
                    description=description.strip() or None,
                )
            )
        else:
            projects.append(
                ProjectItem(
                    name=line.strip()
                )
            )

    return projects


def parse_resume(text: str) -> ResumeProfile:
    """
    Parse extracted resume text into ResumeProfile.
    """

    lines = clean_lines(text)

    if not lines:
        raise ValueError("Resume text cannot be empty.")

    sections = detect_sections(lines)

    summary = None

    if sections.get("summary"):
        summary = "\n".join(
            sections["summary"]
        ).strip() or None

    return ResumeProfile(
        name=extract_name(
            sections.get("header", [])
        ),
        email=extract_email(text),
        phone=extract_phone(text),
        summary=summary,
        skills=parse_skills(
            sections.get("skills", [])
        ),
        experience=parse_experience(
            sections.get("experience", [])
        ),
        education=parse_education(
            sections.get("education", [])
        ),
        certifications=parse_certifications(
            sections.get("certifications", [])
        ),
        projects=parse_projects(
            sections.get("projects", [])
        ),
    )
