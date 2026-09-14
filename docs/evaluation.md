# Evaluation: evidence before claims

## What is included

`evaluation/questions.json` contains 50 author-written questions: 40 answerable and 10 intentionally unsupported. Two answerable questions need evidence from two documents. There are 30 development cases and 20 designated test cases. The split is deterministic and visible in the repository; it is not an independent, externally held-out benchmark.

The checked-in dashboard report is generated from the development split. Its timestamp, corpus fingerprint, expected passage IDs and retrieved IDs are included. No LLM answer quality is measured by that report.

## Retrieval metrics

- **Hit@5:** fraction of answerable questions with at least one expected passage in the top five.
- **Recall@5:** fraction of expected passages found, averaged over answerable questions.
- **MRR@5:** average reciprocal rank of the first expected passage; zero when missing.
- **All-evidence@5:** fraction with every expected passage present. This matters for multi-document questions.

Unanswerable cases are listed but excluded from retrieval-quality denominators. A related retrieved passage is neither a correct answer nor a refusal.

```bash
python -m scripts.evaluate --split dev --method bm25
python -m scripts.evaluate --split test --method bm25 --output evaluation/test-results.json
```

For semantic or hybrid evaluation, first configure a key and build embeddings. These commands make paid query-embedding calls:

```bash
python -m scripts.evaluate --split dev --method semantic --output evaluation/semantic-dev.json
python -m scripts.evaluate --split dev --method hybrid --output evaluation/hybrid-dev.json
```

Keep corpus, questions and split constant when comparing methods. Do not tune on the test split and then describe it as unseen. The defaults were selected for clarity, not optimized against test outcomes.

## Human answer review

Use `evaluation/human-review.csv`. Run live answers, then record:

1. Whether all requested facts are answered correctly: 0 = wrong, 1 = partial, 2 = correct.
2. Whether every claim is supported by its cited passage: yes/no.
3. Whether the system correctly abstains when information is missing.
4. Whether it wrongly abstains on an answerable question.
5. Observed latency, model name, and failure notes.

A structured response and valid source ID do not establish support. Review claims against the passage itself. Do not replace this review with a vague “AI accuracy” number.

## Adversarial and boundary cases

- Ask for the CEO's salary, health insurer or a real API key: the corpus does not provide them.
- Ask for the actual security emergency number: the document explicitly withholds it.
- Put instruction-like text in a test document and verify it is treated as evidence, not commands.
- Search in the wrong category and inspect the fallback.
- Test similar policy names, expired permissions and multi-document questions.
- Simulate provider timeouts and invalid citation IDs.

The automated prompt test checks the instruction/data separation and response plumbing with a fake provider. It does **not** prove that a real model resists prompt injection. Real-model adversarial testing remains required before such a claim.

## Extend the benchmark honestly

The tiny synthetic corpus is relatively clean and easy. Add longer documents, contradictory versions, harder paraphrases and questions written by another person. Record actual metrics and failure examples. Synthetic results must not be presented as performance on real company documents.

