from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import csv
import json

from src.pennantiq.retrieval import Retriever


def reciprocal_rank(ids, relevant):
    for position, doc_id in enumerate(ids, 1):
        if doc_id.startswith(relevant + ":"):
            return 1 / position
    return 0.0


def hit_at(ids, relevant, k):
    return any(doc_id.startswith(relevant + ":") for doc_id in ids[:k])


items = [
    json.loads(line)
    for line in Path("evaluation/datasets/retrieval_ground_truth.jsonl")
    .read_text(encoding="utf-8")
    .splitlines()
    if line.strip()
]
retriever = Retriever()
rows = []
for method in ["keyword", "vector", "hybrid", "hybrid_rerank"]:
    hit1, hit3, hit5, reciprocal = [], [], [], []
    for item in items:
        results = getattr(retriever, method)(item["query"], k=5)
        ids = [document.doc_id for _, document in results]
        hit1.append(hit_at(ids, item["relevant"], 1))
        hit3.append(hit_at(ids, item["relevant"], 3))
        hit5.append(hit_at(ids, item["relevant"], 5))
        reciprocal.append(reciprocal_rank(ids, item["relevant"]))
    rows.append(
        {
            "method": method,
            "hit_rate@1": sum(hit1) / len(hit1),
            "hit_rate@3": sum(hit3) / len(hit3),
            "hit_rate@5": sum(hit5) / len(hit5),
            "mrr@5": sum(reciprocal) / len(reciprocal),
        }
    )

# Select the evaluated winner by MRR@5, then Hit@1, then Hit@3.
best = max(rows, key=lambda r: (r["mrr@5"], r["hit_rate@1"], r["hit_rate@3"]))
output = Path("evaluation/results")
output.mkdir(parents=True, exist_ok=True)
with (output / "retrieval_results.csv").open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=rows[0])
    writer.writeheader()
    writer.writerows(rows)
(output / "best_retrieval_method.json").write_text(
    json.dumps({"evaluation_cases": len(items), "selected": best, "all_methods": rows}, indent=2),
    encoding="utf-8",
)
print(json.dumps({"evaluation_cases": len(items), "selected": best, "all_methods": rows}, indent=2))
