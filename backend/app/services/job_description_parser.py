import re
from typing import List, Optional

from backend.app.schemas.job_description import JobDescriptionProfile


class JobDescriptionParser:
    """Deterministic and conservative job-description parser."""

    SECTION_ALIASES = {
        "required_skills": {
            "required skills",
            "required qualifications",
            "technical requirements",
        },
        "preferred_skills": {
            "preferred skills",
            "preferred qualifications",
            "nice to have",
            "nice-to-have",
        },
        "responsibilities": {
            "responsibilities",
            "key responsibilities",
            "duties",
            "what you will do",
            "what you'll do",
        },
    }

    def parse(self, text: str) -> JobDescriptionProfile:
        if not text or not text.strip():
            raise ValueError("Job description text cannot be empty.")

        normalized_text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [line.strip() for line in normalized_text.split("\n") if line.strip()]

        sections = self._extract_sections(lines)

        return JobDescriptionProfile(
            job_title=self._extract_job_title(lines),
            required_skills=self._extract_list(
                sections.get("required_skills", [])
            ),
            preferred_skills=self._extract_list(
                sections.get("preferred_skills", [])
            ),
            required_experience_years=self._extract_experience_years(
                normalized_text
            ),
            responsibilities=self._extract_list(
                sections.get("responsibilities", [])
            ),
            location=self._extract_location(normalized_text),
        )

    def _extract_job_title(self, lines: List[str]) -> Optional[str]:
        for line in lines[:5]:
            lowered = line.lower()

            if lowered.startswith("job title:"):
                return line.split(":", 1)[1].strip()

            if lowered.startswith("position:"):
                return line.split(":", 1)[1].strip()

        return lines[0] if lines else None

    def _extract_location(self, text: str) -> Optional[str]:
        match = re.search(
            r"(?:location|work location)\s*:\s*(.+)",
            text,
            flags=re.IGNORECASE,
        )
        return match.group(1).strip() if match else None

    def _extract_experience_years(self, text: str) -> Optional[float]:
        patterns = [
            r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+of\s+experience",
            r"minimum\s+of\s+(\d+(?:\.\d+)?)\s*years?",
            r"at\s+least\s+(\d+(?:\.\d+)?)\s*years?",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return float(match.group(1))

        return None

    def _extract_sections(self, lines: List[str]) -> dict:
        sections = {}
        current_section = None

        aliases = {
            alias: section_name
            for section_name, alias_group in self.SECTION_ALIASES.items()
            for alias in alias_group
        }

        for line in lines:
            cleaned = line.rstrip(":").strip().lower()

            if cleaned in aliases:
                current_section = aliases[cleaned]
                sections.setdefault(current_section, [])
                continue

            # Generic headings terminate the current section.
            if current_section and self._looks_like_heading(line):
                current_section = None

            if current_section:
                sections[current_section].append(line)

        return sections

    def _looks_like_heading(self, line: str) -> bool:
        cleaned = line.strip().rstrip(":")
        return (
            len(cleaned) <= 60
            and bool(cleaned)
            and not cleaned.startswith(("-", "•", "*"))
            and not any(separator in cleaned for separator in [",", ";", "|"])
            and cleaned == cleaned.title()
        )

    def _extract_list(self, lines: List[str]) -> List[str]:
        items = []

        for line in lines:
            parts = re.split(r"[,;|]", line)

            for part in parts:
                item = part.strip(" -–—:.,;|")
                if item:
                    items.append(item)

        return list(dict.fromkeys(items))


def parse_job_description(text: str) -> JobDescriptionProfile:
    return JobDescriptionParser().parse(text)
