"""Feature scoring for Senior AI Engineer candidate ranking."""

from collections import Counter

from config import (
    ADJACENT_TECH_TITLE_TERMS,
    AI_TITLE_TERMS,
    CONSULTING_COMPANIES,
    CURRENT_DATE,
    CV_SPEECH_ROBOTICS_TERMS,
    EMBEDDING_TERMS,
    EVALUATION_TERMS,
    NON_TECH_TITLE_TERMS,
    PREFERRED_CITIES,
    PRODUCT_INDUSTRIES,
    PRODUCTION_TERMS,
    PROFICIENCY_WEIGHTS,
    RECENT_LLM_ONLY_TERMS,
    RETRIEVAL_TERMS,
    SKILL_WEIGHTS,
    STEM_FIELDS,
    TIER1_INDIAN_CITIES,
    VECTOR_DB_TERMS,
)
from parser import all_candidate_text, career_text, education_text, profile_text
from utils import any_term, as_float, as_int, capped_hits_score, clamp, hit_terms, norm_text, recency_days


def score_candidate(candidate):
    texts = build_text_features(candidate)
    skill_score, skill_details = skill_match_score(candidate, texts)
    experience_score = experience_fit_score(candidate)
    production_score, production_details = production_experience_score(candidate, texts)
    retrieval_score, retrieval_details = retrieval_ranking_score(texts)
    behavior_score, behavior_details = behavioral_signal_score(candidate)
    location_score = location_fit_score(candidate)
    education_score, education_details = education_fit_score(candidate)
    penalties, penalty_details = penalty_score(
        candidate,
        texts,
        skill_details,
        production_details,
        retrieval_details,
        behavior_details,
    )

    final_score = (
        skill_score
        + experience_score
        + production_score
        + retrieval_score
        + behavior_score
        + location_score
        + education_score
        - penalties
    )

    breakdown = {
        "skill_score": skill_score,
        "experience_score": experience_score,
        "production_score": production_score,
        "retrieval_score": retrieval_score,
        "behavior_score": behavior_score,
        "location_score": location_score,
        "education_score": education_score,
        "penalties": penalties,
        "final_score": final_score,
        "skills": skill_details,
        "production": production_details,
        "retrieval": retrieval_details,
        "behavior": behavior_details,
        "education": education_details,
        "penalty_details": penalty_details,
        "texts": texts,
    }
    return final_score, breakdown


def build_text_features(candidate):
    profile = norm_text(profile_text(candidate))
    career = norm_text(career_text(candidate))
    education = norm_text(education_text(candidate))
    all_text = norm_text(all_candidate_text(candidate))
    profile_obj = candidate.get("profile", {})
    title = norm_text(profile_obj.get("current_title", ""))
    return {
        "profile": profile,
        "career": career,
        "education": education,
        "all": all_text,
        "title": title,
    }


def skill_match_score(candidate, texts):
    score = 0.0
    exact_hits = []
    vector_hits = set()
    retrieval_hits = set()
    eval_hits = set()
    embedding_hits = set()
    skill_counter = Counter()

    for skill in candidate.get("skills", []):
        name = norm_text(skill.get("name", ""))
        if not name:
            continue
        prof = PROFICIENCY_WEIGHTS.get(norm_text(skill.get("proficiency", "")), 0.65)
        endorsements = as_int(skill.get("endorsements", 0))
        duration_months = as_int(skill.get("duration_months", 0))
        confidence = prof
        confidence += min(0.22, endorsements / 220.0)
        confidence += min(0.18, duration_months / 240.0)

        for term, weight in SKILL_WEIGHTS.items():
            if term in name:
                contribution = weight * confidence
                score += contribution
                exact_hits.append((canonical_skill_name(term), contribution))
                skill_counter[canonical_skill_name(term)] += 1

        if any_term(name, VECTOR_DB_TERMS):
            vector_hits.add(name)
        if any_term(name, RETRIEVAL_TERMS):
            retrieval_hits.add(name)
        if any_term(name, EVALUATION_TERMS):
            eval_hits.add(name)
        if any_term(name, EMBEDDING_TERMS):
            embedding_hits.add(name)

    text_score = 0.0
    text_hits = []
    for terms, cap, weight in (
        (VECTOR_DB_TERMS, 4.0, 1.6),
        (RETRIEVAL_TERMS, 4.0, 1.4),
        (EMBEDDING_TERMS, 3.0, 1.2),
        (EVALUATION_TERMS, 3.0, 1.2),
    ):
        part, hits = capped_hits_score(texts["all"], terms, weight=weight, cap=cap)
        text_score += part
        text_hits.extend(hits[:4])

    bundle_bonus = 0.0
    has_python = "python" in texts["all"]
    has_retrieval = any_term(texts["all"], RETRIEVAL_TERMS)
    has_vector = any_term(texts["all"], VECTOR_DB_TERMS)
    has_eval = any_term(texts["all"], EVALUATION_TERMS)
    has_embedding = any_term(texts["all"], EMBEDDING_TERMS)
    if has_python:
        bundle_bonus += 2.0
    if has_retrieval and has_embedding:
        bundle_bonus += 2.5
    if has_retrieval and has_vector:
        bundle_bonus += 2.5
    if has_eval and has_retrieval:
        bundle_bonus += 2.0
    if any_term(texts["title"], AI_TITLE_TERMS):
        bundle_bonus += 2.0
    elif any_term(texts["title"], ADJACENT_TECH_TITLE_TERMS):
        bundle_bonus += 1.0

    total = min(36.0, score + text_score + bundle_bonus)
    details = {
        "exact_hits": exact_hits,
        "text_hits": text_hits,
        "top_skills": top_skill_names(exact_hits),
        "has_python": has_python,
        "has_retrieval": has_retrieval,
        "has_vector": has_vector,
        "has_eval": has_eval,
        "has_embedding": has_embedding,
        "skill_counter": skill_counter,
    }
    return total, details


def experience_fit_score(candidate):
    years = as_float(candidate.get("profile", {}).get("years_of_experience", 0.0))
    if 5.0 <= years <= 9.0:
        return 12.0
    if 4.0 <= years < 5.0:
        return 9.0 + (years - 4.0) * 2.0
    if 9.0 < years <= 10.5:
        return 10.0 - (years - 9.0) * 1.2
    if 3.0 <= years < 4.0:
        return 6.5 + (years - 3.0) * 1.5
    if 10.5 < years <= 12.5:
        return 7.0 - (years - 10.5) * 1.0
    if 2.0 <= years < 3.0:
        return 4.0
    if 12.5 < years <= 15.0:
        return 3.5
    return 1.0


def production_experience_score(candidate, texts):
    career = texts["career"]
    profile = texts["profile"]
    score, hits = capped_hits_score(career, PRODUCTION_TERMS, weight=1.2, cap=11.0)
    profile_score, profile_hits = capped_hits_score(profile, PRODUCTION_TERMS, weight=0.45, cap=3.0)
    score += profile_score

    title_bonus = 0.0
    if any_term(texts["title"], AI_TITLE_TERMS):
        title_bonus += 2.0
    elif any_term(texts["title"], ADJACENT_TECH_TITLE_TERMS):
        title_bonus += 1.2

    product_months = 0
    consulting_months = 0
    for job in candidate.get("career_history", []):
        months = as_int(job.get("duration_months", 0))
        company = norm_text(job.get("company", ""))
        industry = norm_text(job.get("industry", ""))
        if any_term(industry, PRODUCT_INDUSTRIES):
            product_months += months
        if any_term(company, CONSULTING_COMPANIES) or "it services" in industry:
            consulting_months += months

    product_bonus = min(3.0, product_months / 36.0)
    consulting_drag = 0.0
    if consulting_months and product_months == 0:
        consulting_drag = 1.2
    total = clamp(score + title_bonus + product_bonus - consulting_drag, 0.0, 17.0)
    return total, {
        "hits": hits + profile_hits,
        "product_months": product_months,
        "consulting_months": consulting_months,
    }


def retrieval_ranking_score(texts):
    career = texts["career"]
    all_text = texts["all"]
    retrieval_score, retrieval_hits = capped_hits_score(career, RETRIEVAL_TERMS, weight=2.1, cap=9.0)
    vector_score, vector_hits = capped_hits_score(career, VECTOR_DB_TERMS, weight=2.1, cap=6.5)
    embedding_score, embedding_hits = capped_hits_score(career, EMBEDDING_TERMS, weight=1.8, cap=4.0)
    eval_score, eval_hits = capped_hits_score(career, EVALUATION_TERMS, weight=1.7, cap=4.0)

    if retrieval_score == 0.0:
        retrieval_score, retrieval_hits = capped_hits_score(all_text, RETRIEVAL_TERMS, weight=0.8, cap=3.0)
    if vector_score == 0.0:
        vector_score, vector_hits = capped_hits_score(all_text, VECTOR_DB_TERMS, weight=0.8, cap=2.5)
    if embedding_score == 0.0:
        embedding_score, embedding_hits = capped_hits_score(all_text, EMBEDDING_TERMS, weight=0.7, cap=2.0)
    if eval_score == 0.0:
        eval_score, eval_hits = capped_hits_score(all_text, EVALUATION_TERMS, weight=0.7, cap=2.0)

    systems_bonus = 0.0
    if retrieval_score > 0 and vector_score > 0:
        systems_bonus += 2.0
    if retrieval_score > 0 and eval_score > 0:
        systems_bonus += 1.5
    if retrieval_score > 0 and "real users" in career:
        systems_bonus += 1.0
    if retrieval_score > 0 and any_term(career, ("latency", "refresh", "regression", "drift")):
        systems_bonus += 1.0

    total = clamp(
        retrieval_score + vector_score + embedding_score + eval_score + systems_bonus,
        0.0,
        23.0,
    )
    return total, {
        "retrieval_hits": retrieval_hits,
        "vector_hits": vector_hits,
        "embedding_hits": embedding_hits,
        "eval_hits": eval_hits,
    }


def behavioral_signal_score(candidate):
    signals = candidate.get("redrob_signals", {})
    completeness = as_float(signals.get("profile_completeness_score", 0.0))
    response_rate = as_float(signals.get("recruiter_response_rate", 0.0))
    response_hours = as_float(signals.get("avg_response_time_hours", 999.0))
    github = as_float(signals.get("github_activity_score", -1.0))
    saved = as_int(signals.get("saved_by_recruiters_30d", 0))
    interview = as_float(signals.get("interview_completion_rate", 0.0))
    search_appearances = as_int(signals.get("search_appearance_30d", 0))
    notice_days = as_int(signals.get("notice_period_days", 180))
    last_active_days = recency_days(signals.get("last_active_date"), CURRENT_DATE)

    score = 0.0
    score += min(1.5, completeness / 70.0)
    score += min(2.2, response_rate * 2.6)
    if response_hours <= 24:
        score += 1.2
    elif response_hours <= 72:
        score += 0.8
    elif response_hours <= 120:
        score += 0.35
    score += min(1.3, interview * 1.4)
    if github >= 0:
        score += min(1.6, github / 55.0)
    score += min(1.0, saved / 8.0)
    score += min(0.7, search_appearances / 220.0)
    if signals.get("open_to_work_flag"):
        score += 1.0
    if signals.get("verified_email"):
        score += 0.35
    if signals.get("verified_phone"):
        score += 0.35
    if signals.get("linkedin_connected"):
        score += 0.25
    if last_active_days <= 30:
        score += 1.0
    elif last_active_days <= 90:
        score += 0.6
    elif last_active_days <= 180:
        score += 0.2
    if notice_days <= 30:
        score += 0.7
    elif notice_days <= 60:
        score += 0.3

    return min(13.0, score), {
        "completeness": completeness,
        "response_rate": response_rate,
        "response_hours": response_hours,
        "github": github,
        "saved": saved,
        "interview": interview,
        "notice_days": notice_days,
        "last_active_days": last_active_days,
        "open_to_work": bool(signals.get("open_to_work_flag")),
    }


def location_fit_score(candidate):
    profile = candidate.get("profile", {})
    location = norm_text(profile.get("location", ""))
    country = norm_text(profile.get("country", ""))
    signals = candidate.get("redrob_signals", {})
    relocate = bool(signals.get("willing_to_relocate"))
    if any_term(location, PREFERRED_CITIES):
        return 4.0
    if any_term(location, TIER1_INDIAN_CITIES):
        return 3.3
    if country == "india" and relocate:
        return 3.0
    if country == "india":
        return 2.3
    if relocate:
        return 1.2
    return 0.3


def education_fit_score(candidate):
    score = 0.0
    best = {}
    for edu in candidate.get("education", []):
        field = norm_text(edu.get("field_of_study", ""))
        degree = norm_text(edu.get("degree", ""))
        tier = norm_text(edu.get("tier", "unknown"))
        local = 0.0
        if any_term(field, STEM_FIELDS):
            local += 1.7
        if "ph.d" in degree or "phd" in degree:
            local += 1.1
        elif "m." in degree or "master" in degree or "mtech" in degree:
            local += 0.8
        else:
            local += 0.4
        if tier == "tier_1":
            local += 1.6
        elif tier == "tier_2":
            local += 1.0
        elif tier == "tier_3":
            local += 0.4
        if local > score:
            score = local
            best = {"field": field, "degree": degree, "tier": tier}
    return min(5.0, score), best


def penalty_score(candidate, texts, skill_details, production_details, retrieval_details, behavior_details):
    penalties = 0.0
    reasons = []
    profile = candidate.get("profile", {})
    title = texts["title"]
    career = texts["career"]
    all_text = texts["all"]
    years = as_float(profile.get("years_of_experience", 0.0))

    retrieval_evidence = (
        len(retrieval_details.get("retrieval_hits", []))
        + len(retrieval_details.get("vector_hits", []))
        + len(retrieval_details.get("embedding_hits", []))
        + len(retrieval_details.get("eval_hits", []))
    )
    exact_skill_count = len(skill_details.get("exact_hits", []))

    if any_term(title, NON_TECH_TITLE_TERMS) and retrieval_evidence < 2:
        penalties += 9.0
        reasons.append("non-technical current title with weak retrieval evidence")
    elif any_term(title, NON_TECH_TITLE_TERMS):
        penalties += 3.0
        reasons.append("non-technical current title")

    if exact_skill_count >= 8 and retrieval_evidence < 2 and not any_term(career, AI_TITLE_TERMS):
        penalties += 8.0
        reasons.append("keyword-heavy skills without matching work history")

    companies = [norm_text(job.get("company", "")) for job in candidate.get("career_history", [])]
    product_months = production_details.get("product_months", 0)
    if companies and all(any_term(company, CONSULTING_COMPANIES) for company in companies) and product_months == 0:
        penalties += 7.0
        reasons.append("consulting-only career")

    if "research" in all_text and production_details.get("hits") == [] and retrieval_evidence < 2:
        penalties += 5.0
        reasons.append("research signal without production deployment")

    cv_hits = hit_terms(all_text, CV_SPEECH_ROBOTICS_TERMS)
    if len(cv_hits) >= 2 and retrieval_evidence < 2:
        penalties += 5.0
        reasons.append("CV/speech/robotics leaning without enough NLP/IR evidence")

    if any_term(all_text, RECENT_LLM_ONLY_TERMS) and retrieval_evidence < 2 and production_details.get("hits") == []:
        penalties += 5.0
        reasons.append("recent LLM-tool usage only")

    github = behavior_details.get("github", -1)
    if github < 0 and not skill_details.get("has_python") and retrieval_evidence < 2:
        penalties += 3.0
        reasons.append("no coding activity signal")

    notice_days = behavior_details.get("notice_days", 180)
    if notice_days > 90:
        penalties += min(4.0, (notice_days - 90) / 20.0)
        reasons.append("notice period over 90 days")
    elif notice_days > 60:
        penalties += 1.0
        reasons.append("notice period above preferred band")

    if behavior_details.get("response_hours", 999) > 120:
        penalties += 2.0
        reasons.append("slow recruiter response time")
    if behavior_details.get("last_active_days", 9999) > 180:
        penalties += 2.5
        reasons.append("inactive profile")
    if behavior_details.get("response_rate", 0.0) < 0.15:
        penalties += 1.5
        reasons.append("low recruiter response rate")

    months = sum(as_int(job.get("duration_months", 0)) for job in candidate.get("career_history", []))
    if years >= 5 and months / 12.0 < years - 3.0:
        penalties += 3.0
        reasons.append("experience timeline mismatch")
    if years < 2 and exact_skill_count >= 8:
        penalties += 3.0
        reasons.append("senior-skill claim with very low experience")

    if "marketing manager" in texts["profile"] and any_term(title, AI_TITLE_TERMS) and retrieval_evidence < 2:
        penalties += 4.0
        reasons.append("summary-title mismatch")

    return min(38.0, penalties), reasons


def canonical_skill_name(term):
    aliases = {
        "llms": "LLMs",
        "llm": "LLMs",
        "embedding": "Embeddings",
        "embeddings": "Embeddings",
        "sentence transformers": "Sentence Transformers",
        "fine tuning": "Fine-tuning",
        "fine-tuning": "Fine-tuning",
        "a/b testing": "A/B Testing",
        "ab testing": "A/B Testing",
        "map": "MAP",
        "mrr": "MRR",
        "ndcg": "NDCG",
        "nlp": "NLP",
        "rag": "RAG",
        "peft": "PEFT",
        "lora": "LoRA",
        "qlora": "QLoRA",
        "faiss": "FAISS",
        "opensearch": "OpenSearch",
        "elasticsearch": "Elasticsearch",
        "qdrant": "Qdrant",
        "milvus": "Milvus",
        "pinecone": "Pinecone",
        "weaviate": "Weaviate",
        "learning to rank": "Learning-to-rank",
        "information retrieval": "Information Retrieval",
    }
    if term in aliases:
        return aliases[term]
    return " ".join(piece.capitalize() for piece in term.split())


def top_skill_names(exact_hits, limit=5):
    seen = []
    for name, _ in sorted(exact_hits, key=lambda item: item[1], reverse=True):
        if name not in seen:
            seen.append(name)
        if len(seen) >= limit:
            break
    return seen
