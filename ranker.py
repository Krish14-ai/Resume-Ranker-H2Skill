"""Entrypoint for the Redrob Senior AI Engineer ranking solution.

Run:
    python ranker.py

The script streams candidates, scores each profile, keeps the top 100, and
writes a validator-compatible CSV: candidate_id,rank,score,reasoning.
"""

from pathlib import Path

from config import DEFAULT_OUTPUT, TOP_K
from parser import iter_candidates
from reasoning import make_reasoning
from scorer import score_candidate
from utils import csv_escape, resolve_candidate_file


def rank_candidates(candidate_path, top_k=TOP_K):
    top = []
    worst_index = -1
    worst_key = None

    for candidate in iter_candidates(candidate_path):
        candidate_id = candidate.get("candidate_id", "")
        score, breakdown = score_candidate(candidate)
        entry = {
            "candidate_id": candidate_id,
            "score": score,
            "candidate": candidate,
            "breakdown": breakdown,
        }

        if len(top) < top_k:
            top.append(entry)
            worst_index, worst_key = find_worst(top)
            continue

        candidate_key = (score, reverse_id_for_worst(candidate_id))
        if candidate_key > worst_key:
            top[worst_index] = entry
            worst_index, worst_key = find_worst(top)

    for entry in top:
        entry["score_out"] = round(entry["score"], 6)
    top.sort(key=lambda item: (-item["score_out"], item["candidate_id"]))
    return top


def reverse_id_for_worst(candidate_id):
    """Higher is better for tie comparison; lexically smaller ID should win."""
    digits = "".join(ch for ch in str(candidate_id) if ch.isdigit())
    number = int(digits) if digits else 0
    return -number


def find_worst(entries):
    worst_index = 0
    worst_key = (entries[0]["score"], reverse_id_for_worst(entries[0]["candidate_id"]))
    for index, entry in enumerate(entries[1:], start=1):
        key = (entry["score"], reverse_id_for_worst(entry["candidate_id"]))
        if key < worst_key:
            worst_index = index
            worst_key = key
    return worst_index, worst_key


def write_submission(entries, output_path):
    lines = ["candidate_id,rank,score,reasoning"]
    for rank, entry in enumerate(entries, start=1):
        reasoning = make_reasoning(entry["candidate"], entry["breakdown"])
        row = [
            entry["candidate_id"],
            str(rank),
            "%.6f" % entry["score_out"],
            reasoning,
        ]
        lines.append(",".join(csv_escape(value) for value in row))
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    base_dir = Path(__file__).resolve().parent
    candidate_path = resolve_candidate_file(base_dir)
    output_path = base_dir / DEFAULT_OUTPUT
    ranked = rank_candidates(candidate_path, TOP_K)
    write_submission(ranked, output_path)
    print("Wrote %s with %d ranked candidates." % (output_path.name, len(ranked)))


if __name__ == "__main__":
    main()
