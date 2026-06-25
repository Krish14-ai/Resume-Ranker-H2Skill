"""Input parsing for Redrob candidate files."""

import gzip
import json
from pathlib import Path


def iter_candidates(path):
    """Yield candidates from .jsonl or .jsonl.gz without loading all records."""
    candidate_path = Path(path)
    opener = gzip.open if candidate_path.suffix == ".gz" else open
    with opener(candidate_path, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def profile_text(candidate):
    profile = candidate.get("profile", {})
    fields = (
        profile.get("headline", ""),
        profile.get("summary", ""),
        profile.get("current_title", ""),
        profile.get("current_company", ""),
        profile.get("current_industry", ""),
        profile.get("location", ""),
        profile.get("country", ""),
    )
    return " ".join(str(value) for value in fields if value)


def career_text(candidate):
    parts = []
    for job in candidate.get("career_history", []):
        parts.extend(
            [
                job.get("company", ""),
                job.get("title", ""),
                job.get("industry", ""),
                job.get("description", ""),
            ]
        )
    return " ".join(str(value) for value in parts if value)


def education_text(candidate):
    parts = []
    for edu in candidate.get("education", []):
        parts.extend(
            [
                edu.get("institution", ""),
                edu.get("degree", ""),
                edu.get("field_of_study", ""),
                edu.get("tier", ""),
            ]
        )
    return " ".join(str(value) for value in parts if value)


def skill_names(candidate):
    return [str(skill.get("name", "")) for skill in candidate.get("skills", [])]


def all_candidate_text(candidate):
    return " ".join(
        [
            profile_text(candidate),
            career_text(candidate),
            education_text(candidate),
            " ".join(skill_names(candidate)),
        ]
    )
