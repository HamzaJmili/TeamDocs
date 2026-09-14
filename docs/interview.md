# Understand it. Then explain it.

## A 30-second explanation

“TeamDocs helps someone find answers in company documentation. It first finds relevant passages, then optionally uses an AI model to write a short answer linked to those sources. I focused on making the evidence easy to inspect, measuring retrieval separately from answer quality, and keeping the deployment small enough to understand.”

Adapt that introduction after you have worked through the code. The repository was built with AI assistance; be ready to explain what you inspected, tested and changed yourself. Do not claim to have independently authored or mastered parts you have not studied.

## A three-minute demo

1. Explain the new-employee problem: scattered information and repeated questions.
2. Ask how to request staging access.
3. Open the citation and show the exact passage.
4. Show a document filter and explain that search only sees that collection.
5. Explain whether the app is in excerpt demo mode or live AI mode.
6. Open Quality Lab and distinguish retrieval results from answer accuracy.
7. End with one limitation and the next experiment you would run.

## Read the code in this order

| Step | File | Check your understanding |
| --- | --- | --- |
| 1 | `data/documents/staging-access.md` | What answer can this source actually support? |
| 2 | `scripts/ingest.py` | How does text become a source-linked passage? |
| 3 | `app/retrieval.py` | Why does one passage rank above another? |
| 4 | `app/service.py` | What changes between demo and live mode? |
| 5 | `app/provider.py` | What is sent to the model? What happens on failure? |
| 6 | `app/main.py` | How are inputs, sources and limits handled? |
| 7 | `app/static/app.js` | How does a citation open its source? |
| 8 | `scripts/evaluate.py` | What exactly is counted as success? |

## Interview questions, with honest answers

**Why RAG instead of training a model?**

The knowledge changes in documents, so retrieving current evidence is a natural fit. Training a model would be costly and would not automatically provide traceable sources. RAG can still retrieve the wrong passage or generate an unsupported answer.

**What is an embedding?**

A numeric representation of text. Texts with similar meanings can have nearby representations. We use cosine similarity to rank passages relative to the question. It is not a percentage probability that an answer is correct.

**Why do you still have keyword search?**

It is a useful, inexpensive baseline, especially for exact terminology. Semantic retrieval may help with paraphrases. Hybrid retrieval combines their ranks. The project implements the comparison; live superiority must be measured rather than assumed.

**Why no vector database?**

The sample has only 60 passages. A small matrix fits in memory and allows exact search. A database becomes useful when measured scale, update requirements or access controls justify it.

**How do you reduce hallucinations?**

Supply retrieved evidence, request structured claims, instruct the model to abstain when unsupported, validate citation IDs, and expose the sources. These controls reduce some errors; they do not guarantee factual correctness. Human evaluation checks actual support.

**What survives a server restart?**

The bundled documents and prepared index can be loaded again. Temporary feedback, answer IDs and rate-limit counters are lost. The current application has no durable user database.

**Is it enterprise-ready?**

It is an enterprise-inspired portfolio prototype. A real internal deployment needs document-level permissions, trusted ingestion, durable operations, stronger abuse controls, privacy review, and testing on representative documents.

## Exercises that make the project yours

1. Add a new fictional policy and predict which question should retrieve it. Rebuild and verify.
2. Explain one BM25 score calculation on paper.
3. Create a long document that needs overlapping chunks. Inspect the boundaries.
4. Write five questions that fail the current retriever, without changing existing benchmark answers.
5. Compare keyword and semantic retrieval on those questions after enabling live mode.
6. Add one meaningful test, such as conflicting policy versions.
7. Make a small UI improvement and describe why it helps the reader.

## Résumé wording after verification

Use capabilities you have actually run and can defend. For example:

“Developed a document-search application with FastAPI, source-linked retrieval, a responsive interface and automated evaluation; prepared a reproducible Render deployment.”

Add embeddings, hybrid search or AI synthesis only after running those paths yourself. Add numbers only with a named dataset and measured result. A prepared deployment is not a deployed service until it is live.

