"""Human-readable, grounded reasoning for top-ranked candidates."""

from utils import as_float


def make_reasoning(candidate, breakdown):
    profile = candidate.get("profile", {})
    years = as_float(profile.get("years_of_experience", 0.0))
    title = profile.get("current_title", "candidate")
    skills = breakdown.get("skills", {}).get("top_skills", [])
    if not skills:
        skills = fallback_skills(candidate)
    skill_text = ", ".join(skills[:4]) if skills else "relevant ML/search skills"

    strengths = []
    if breakdown.get("retrieval_score", 0.0) >= 12.0:
        strengths.append("strong retrieval/ranking evidence")
    elif breakdown.get("retrieval_score", 0.0) >= 6.0:
        strengths.append("some retrieval/search evidence")
    if breakdown.get("production_score", 0.0) >= 10.0:
        strengths.append("production systems background")
    behavior = breakdown.get("behavior", {})
    if is_behavior_relevant(behavior, breakdown.get("behavior_score", 0.0)):
        strengths.append(
            "behavioral fit with response rate %.2f, GitHub activity %.1f, and %d recruiter saves"
            % (
                behavior.get("response_rate", 0.0),
                behavior.get("github", -1.0),
                behavior.get("saved", 0),
            )
        )

    profile_style = int(str(candidate.get("candidate_id", "0"))[-1]) % 3
    if profile_style == 0:
        first = (
            "%.1f years in %s roles; strongest matching skills are %s"
            % (years, title, skill_text)
        )
    elif profile_style == 1:
        first = (
            "%s with %.1f years of experience and concrete evidence around %s"
            % (title, years, skill_text)
        )
    else:
        first = (
            "%.1f years of experience as %s, with profile and career evidence for %s"
            % (years, title, skill_text)
        )
    if strengths:
        first += ", plus " + strengths[0]
    first += "."

    concerns = []
    notice_days = behavior.get("notice_days", 0)
    if notice_days > 90:
        concerns.append("notice period is %d days" % notice_days)
    if behavior.get("response_hours", 0.0) > 120:
        concerns.append("recruiter response time is slow")
    if breakdown.get("penalty_details"):
        concerns.append(breakdown["penalty_details"][0])
    if breakdown.get("retrieval_score", 0.0) < 8.0:
        concerns.append("retrieval/ranking evidence is not as deep as the ideal profile")

    if concerns:
        second = "Concern: " + concerns[0] + "."
        return first + " " + second
    if len(strengths) > 1:
        return first + " Also shows " + strengths[1] + "."
    return first


def is_behavior_relevant(behavior, behavior_score):
    if behavior_score >= 8.0:
        return True
    if behavior.get("response_rate", 0.0) >= 0.65:
        return True
    if behavior.get("github", -1.0) >= 55:
        return True
    if behavior.get("saved", 0) >= 8:
        return True
    if behavior.get("open_to_work") and behavior.get("last_active_days", 9999) <= 90:
        return True
    return False


def fallback_skills(candidate):
    names = []
    for skill in candidate.get("skills", []):
        name = str(skill.get("name", "")).strip()
        if not name:
            continue
        low = name.lower()
        if any(term in low for term in ("python", "retrieval", "ranking", "rag", "llm", "nlp", "faiss", "milvus", "qdrant", "pinecone", "weaviate", "elasticsearch")):
            names.append(name)
        if len(names) >= 4:
            break
    return names
