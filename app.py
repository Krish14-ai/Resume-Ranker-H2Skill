"""Streamlit demo for the Redrob AI Candidate Ranker."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from reasoning import make_reasoning
from scorer import score_candidate


APP_DIR = Path(__file__).resolve().parent
SAMPLE_PATH = APP_DIR / "sample_candidates.json"


def load_candidates(path: Path = SAMPLE_PATH) -> list[dict[str, Any]]:
    """Load the lightweight sample dataset used by the demo app."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("sample_candidates.json must contain a list of candidates.")
    return data


def format_percent(value: Any) -> str:
    try:
        return f"{float(value) * 100:.0f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_score(value: Any) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def rank_sample_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Score every sample candidate with the existing scorer pipeline."""
    progress = st.progress(0, text="Ranking candidates...")
    ranked: list[dict[str, Any]] = []
    total = max(len(candidates), 1)

    for index, candidate in enumerate(candidates, start=1):
        score, breakdown = score_candidate(candidate)
        ranked.append(
            {
                "candidate_id": candidate.get("candidate_id", ""),
                "candidate": candidate,
                "score": float(score),
                "breakdown": breakdown,
                "reasoning": make_reasoning(candidate, breakdown),
            }
        )
        progress.progress(index / total, text=f"Ranking candidates... {index}/{total}")

    ranked.sort(key=lambda item: (-item["score"], item["candidate_id"]))
    progress.empty()
    return ranked


def build_results_frame(ranked: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for rank, item in enumerate(ranked, start=1):
        profile = item["candidate"].get("profile", {})
        rows.append(
            {
                "Rank": rank,
                "Candidate ID": item["candidate_id"],
                "Current Title": profile.get("current_title", "N/A"),
                "Experience": profile.get("years_of_experience", "N/A"),
                "Final Score": format_score(item["score"]),
            }
        )
    return pd.DataFrame(rows)


def render_sidebar(candidate_count: int) -> None:
    st.sidebar.title("Redrob AI Candidate Ranker")
    st.sidebar.write(
        "A lightweight demo for ranking Senior AI Engineer candidates using "
        "skills, work history, behavioral signals, and production evidence."
    )
    st.sidebar.metric("Candidates Loaded", candidate_count)
    st.sidebar.divider()
    st.sidebar.caption("Author: Krish")
    st.sidebar.caption("Hackathon demo application")


def render_header() -> None:
    st.title("Intelligent Candidate Discovery & Ranking System")
    st.write(
        "This system ranks candidates for a Senior AI Engineer role based on "
        "skills, experience, behavioral signals, and production experience."
    )


def render_summary_metrics(ranked: list[dict[str, Any]]) -> None:
    if not ranked:
        return
    scores = [item["score"] for item in ranked]
    top = ranked[0]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Ranked Candidates", len(ranked))
    col2.metric("Top Score", f"{max(scores):.2f}")
    col3.metric("Average Score", f"{sum(scores) / len(scores):.2f}")
    col4.metric("Best Match", top["candidate_id"])


def render_results_table(ranked: list[dict[str, Any]]) -> pd.DataFrame:
    st.subheader("Candidate Ranking")
    limit = st.selectbox("Display", [10, 25, 50], index=0)
    results = build_results_frame(ranked)
    st.dataframe(results.head(limit), use_container_width=True, hide_index=True)
    return results


def render_skill_tags(skills: list[dict[str, Any]]) -> None:
    names = [str(skill.get("name", "")).strip() for skill in skills if skill.get("name")]
    if not names:
        st.write("N/A")
        return

    tags = " ".join(
        (
            "<span style='display:inline-block;margin:0 6px 6px 0;"
            "padding:5px 10px;border-radius:999px;background:#eef2ff;"
            "color:#1e293b;font-size:0.86rem;'>"
            f"{html.escape(name)}</span>"
        )
        for name in names
    )
    st.markdown(tags, unsafe_allow_html=True)


def render_candidate_details(ranked: list[dict[str, Any]]) -> None:
    st.subheader("Candidate Details")
    labels = [
        f"#{rank} | {item['candidate_id']} | "
        f"{item['candidate'].get('profile', {}).get('current_title', 'N/A')}"
        for rank, item in enumerate(ranked, start=1)
    ]
    selected = st.selectbox("Select a candidate", labels)
    selected_index = labels.index(selected)
    item = ranked[selected_index]
    candidate = item["candidate"]
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    st.markdown("### Profile Information")
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Score", f"{item['score']:.2f}")
    col2.metric("Experience", f"{profile.get('years_of_experience', 'N/A')} yrs")
    col3.metric("Rank", selected_index + 1)

    info = {
        "Current Title": profile.get("current_title", "N/A"),
        "Current Company": profile.get("current_company", "N/A"),
        "Location": profile.get("location", "N/A"),
        "Industry": profile.get("current_industry", "N/A"),
    }
    st.table(pd.DataFrame(info.items(), columns=["Field", "Value"]))

    st.markdown("### Skills")
    render_skill_tags(candidate.get("skills", []))

    st.markdown("### Behavioral Signals")
    b1, b2, b3, b4, b5 = st.columns(5)
    b1.metric("Response Rate", format_percent(signals.get("recruiter_response_rate")))
    b2.metric("GitHub Activity", signals.get("github_activity_score", "N/A"))
    b3.metric("Notice Period", f"{signals.get('notice_period_days', 'N/A')} days")
    b4.metric("Interview Rate", format_percent(signals.get("interview_completion_rate")))
    b5.metric("Open to Work", "Yes" if signals.get("open_to_work_flag") else "No")

    st.markdown("### Generated Reasoning")
    st.info(item["reasoning"])


def render_visualizations(ranked: list[dict[str, Any]]) -> None:
    st.subheader("Visualizations")
    chart_df = build_results_frame(ranked)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(
            chart_df,
            x="Final Score",
            nbins=16,
            title="Distribution of Candidate Scores",
            color_discrete_sequence=["#2563eb"],
        )
        fig.update_layout(bargap=0.08, yaxis_title="Candidates")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_10 = chart_df.head(10)
        fig = px.bar(
            top_10.sort_values("Final Score"),
            x="Final Score",
            y="Candidate ID",
            orientation="h",
            title="Top 10 Candidate Scores",
            color="Final Score",
            color_continuous_scale="Teal",
        )
        fig.update_layout(yaxis_title=None, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)


def main() -> None:
    st.set_page_config(
        page_title="Redrob AI Candidate Ranker",
        layout="wide",
    )

    candidates = load_candidates()
    render_sidebar(len(candidates))
    render_header()

    if "ranked_candidates" not in st.session_state:
        st.session_state.ranked_candidates = []

    if st.button("Run Ranking", type="primary", use_container_width=False):
        st.session_state.ranked_candidates = rank_sample_candidates(candidates)
        st.success("Ranking completed successfully.")

    ranked = st.session_state.ranked_candidates
    if ranked:
        render_summary_metrics(ranked)
        render_results_table(ranked)
        render_candidate_details(ranked)
        render_visualizations(ranked)
    else:
        st.info("Click Run Ranking to score and rank the sample candidates.")


if __name__ == "__main__":
    main()
