"""Reproducible retrieval benchmark. No claims about answer correctness."""
import argparse
import asyncio
import json
from datetime import datetime, timezone
from app.config import ROOT, Settings
from app.retrieval import SearchIndex, corpus_hash
from app.provider import make_provider


async def evaluate(split="dev", method="bm25", output=None):
    index = SearchIndex(ROOT / "data/index")
    settings = Settings()
    questions = json.loads((ROOT / "evaluation/questions.json").read_text())
    questions = [q for q in questions if split == "all" or q["split"] == split]
    provider = make_provider(settings)
    if method != "bm25" and (not settings.provider_key or index.vectors is None or index.embedding_model != settings.embedding_model or index.embedding_provider != settings.provider):
        raise ValueError("Semantic evaluation requires a key and a matching embedding index")
    cases = []
    for q in questions:
        vector = (await provider.embed([q["question"]], settings.embedding_model))[0] if method != "bm25" else None
        sources = index.search(q["question"], method=method, vector=vector)
        retrieved = [s["id"] for s in sources]
        expected = set(q["expected_ids"])
        ranks = [retrieved.index(i) + 1 for i in expected if i in retrieved]
        cases.append({**q, "retrieved_ids": retrieved, "hit": bool(ranks),
            "all_evidence_found": bool(expected) and expected.issubset(retrieved),
            "recall": len(set(retrieved) & expected) / len(expected) if expected else None,
            "reciprocal_rank": 1/min(ranks) if ranks else 0})
    answerable = [c for c in cases if c["expected_ids"]]
    result = {"generated_at": datetime.now(timezone.utc).isoformat(), "method": method, "split": split,
        "total_questions": len(cases), "answerable_questions": len(answerable), "unanswerable_questions": len(cases)-len(answerable),
        "corpus_hash": corpus_hash(index.chunks), "metrics": {
            "hit_at_5": sum(c["hit"] for c in answerable)/max(len(answerable),1),
            "recall_at_5": sum(c["recall"] for c in answerable)/max(len(answerable),1),
            "mrr_at_5": sum(c["reciprocal_rank"] for c in answerable)/max(len(answerable),1),
            "all_evidence_at_5": sum(c["all_evidence_found"] for c in answerable)/max(len(answerable),1)},
        "disclosure": "Synthetic corpus and author-written questions. This is a small engineering check, not an independent benchmark. Test questions are designated holdouts but visible in the repository. No LLM answer quality has been measured in this report.",
        "cases": cases}
    destination = output or ROOT / "evaluation/results.json"
    destination.write_text(json.dumps(result,indent=2))
    print(json.dumps({k:v for k,v in result.items() if k != 'cases'},indent=2))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split",choices=["dev","test","all"],default="dev")
    parser.add_argument("--method",choices=["bm25","semantic","hybrid"],default="bm25")
    parser.add_argument("--output",type=str)
    args=parser.parse_args()
    from pathlib import Path
    asyncio.run(evaluate(args.split,args.method,Path(args.output) if args.output else None))


if __name__ == "__main__":
    main()
