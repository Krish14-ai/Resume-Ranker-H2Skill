# Redrob Senior AI Engineer Candidate Ranker

## Overview

This project ranks 100,000 Redrob candidates for the Senior AI Engineer role and writes the top 100 to `submission.csv`.

The solution is a deterministic, CPU-only feature ranker. It avoids external APIs, GPUs, local LLMs, and heavyweight embeddings so it can run under the hackathon constraints while remaining explainable in an interview.

## Idea Evaluation

The tempting approach is to count AI keywords in the `skills` list. That is risky because the job description explicitly warns about keyword-stuffed trap candidates. The ranker therefore treats skills as only one signal and gives stronger weight to career-history evidence of production retrieval, ranking, vector search, evaluation, and product-company experience.

The design favors:

- Evidence in career descriptions over unsupported skills.
- Retrieval/ranking and vector database co-occurrence over generic LLM usage.
- Production deployment terms over pure research.
- Behavioral availability signals so high-fit but inactive candidates are down-weighted.
- Honeypot penalties for inconsistent titles, consulting-only careers, weak work-history evidence, and impossible-looking profiles.

## Features

- Streams `candidates.jsonl` or `candidates.jsonl.gz`.
- Includes a Streamlit demo app over `sample_candidates.json`.
- Scores each candidate with modular components:
  - Skill match score
  - Experience score
  - Production experience score
  - Retrieval/ranking experience score
  - Behavioral signal score
  - Location score
  - Education score
  - Penalty score
- Keeps only the top 100 candidates in memory.
- Produces grounded 1-2 sentence reasoning per candidate.
- Outputs validator-compatible CSV with deterministic tie-breaking.

## Tech Stack

- Python standard runtime
- `gzip`
- `json`
- `collections`
- `pathlib`
- Streamlit, pandas, and Plotly for the demo UI

No network access, hosted models, GPU inference, or external APIs are used during ranking.

## Folder Structure

```text
.
├── ranker.py              # Entrypoint: stream, rank, and write CSV
├── app.py                 # Streamlit demo over sample candidates
├── scorer.py              # Weighted scoring and penalties
├── parser.py              # JSONL/GZ parsing and text extraction
├── reasoning.py           # Candidate explanation generation
├── config.py              # Weights, term dictionaries, constants
├── utils.py               # Small reusable helpers
├── validate_submission.py # Challenge-provided validator
├── candidates.jsonl       # Candidate pool
├── sample_candidates.json # Lightweight demo candidate set
└── submission.csv         # Generated output
```

## Setup

Use Python 3.10+.

No package installation is required.

If the dataset is compressed, keep `candidates.jsonl.gz` in this folder. If it is already uncompressed, keep `candidates.jsonl` in this folder.

For the Streamlit demo, install:

```bash
pip install streamlit pandas plotly
```

## Usage

Run:

```bash
python ranker.py
```

Run the demo app:

```bash
streamlit run app.py
```

Validate:

```bash
python validate_submission.py submission.csv
```

The generated CSV has exactly:

```text
candidate_id,rank,score,reasoning
```

with 100 ranked candidates.

## Architecture

Data flow:

1. `ranker.py` resolves the candidate file and streams records with `parser.iter_candidates`.
2. `scorer.score_candidate` builds normalized profile, career, education, and skill text.
3. The scorer computes component scores and penalties using explicit term dictionaries from `config.py`.
4. `ranker.py` keeps the current top 100 candidates and sorts them by score descending, then `candidate_id` ascending for deterministic ties.
5. `reasoning.py` creates short explanations from the same facts used by the ranker.
6. `ranker.py` writes `submission.csv`.

## Scoring Strategy

Final score:

```text
final_score =
  skill_score
  + experience_score
  + production_score
  + retrieval_score
  + behavior_score
  + location_score
  + education_score
  - penalties
```

The most important signals are retrieval/ranking experience, production ML/search systems, strong Python, vector databases, and evaluation frameworks such as NDCG, MRR, MAP, and A/B testing.

## Review And Improvement

Known limitations:

- It is a rule-based model, so it cannot infer every semantic match.
- It depends on term dictionaries; unusual phrasing may be missed.
- It does not train a learning-to-rank model because no labeled training set is provided.
- It approximates date recency with a simple deterministic day number.

Future improvements:

- Add a small offline-labeled validation set from manual review.
- Tune weights against NDCG@10 and NDCG@50.
- Add a lexical BM25-style scorer over career text.
- Add calibrated feature logging for top and rejected candidates.
- Train a lightweight learning-to-rank model if labels become available.

## Learning Guidance

To defend and improve this solution, study:

- Search ranking metrics: NDCG, MRR, MAP, precision@k.
- Candidate retrieval pipelines: lexical retrieval, dense retrieval, hybrid search, re-ranking.
- Feature engineering for ranking systems.
- Counterfactual evaluation and online A/B testing.
- Production ML reliability: drift, monitoring, index refresh, and latency budgets.
