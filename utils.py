"""Small reusable helpers for parsing, scoring, and CSV writing."""

from pathlib import Path


def as_float(value, default=0.0):
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value, default=0):
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def clamp(value, low, high):
    if value < low:
        return low
    if value > high:
        return high
    return value


def norm_text(value):
    if value is None:
        return ""
    return str(value).lower()


def any_term(text, terms):
    for term in terms:
        if term in text:
            return True
    return False


def hit_terms(text, terms):
    hits = []
    for term in terms:
        if term in text:
            hits.append(term)
    return hits


def capped_hits_score(text, terms, weight=1.0, cap=10.0):
    score = 0.0
    hits = []
    for term in terms:
        if term in text:
            hits.append(term)
            score += weight
            if score >= cap:
                return cap, hits
    return min(score, cap), hits


def date_to_days(date_string):
    """Approximate sortable day number for YYYY-MM-DD strings.

    Exact leap-day handling is unnecessary for recency bands, but this keeps
    behavior deterministic without importing datetime.
    """
    if not date_string or len(str(date_string)) < 10:
        return 0
    try:
        year = int(str(date_string)[0:4])
        month = int(str(date_string)[5:7])
        day = int(str(date_string)[8:10])
    except ValueError:
        return 0
    return year * 365 + month * 31 + day


def recency_days(date_string, current_date):
    current = date_to_days(current_date)
    value = date_to_days(date_string)
    if not current or not value:
        return 9999
    return max(0, current - value)


def csv_escape(value):
    text = "" if value is None else str(value)
    text = text.replace("\r", " ").replace("\n", " ")
    if '"' in text:
        text = text.replace('"', '""')
    if "," in text or '"' in text:
        text = '"' + text + '"'
    return text


def resolve_candidate_file(base_dir):
    from config import INPUT_CANDIDATE_FILES

    root = Path(base_dir)
    for file_name in INPUT_CANDIDATE_FILES:
        path = root / file_name
        if path.exists():
            return path
    raise FileNotFoundError("Expected candidates.jsonl or candidates.jsonl.gz")


def candidate_id_rank_value(candidate_id):
    digits = "".join(ch for ch in str(candidate_id) if ch.isdigit())
    return int(digits) if digits else 0
