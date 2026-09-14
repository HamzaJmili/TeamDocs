# Design decisions and tradeoffs

| Decision | Reason | Tradeoff |
| --- | --- | --- |
| One FastAPI service | Simple local and Render deployment; one request flow to understand | A large UI or high traffic could justify separate services |
| Plain HTML/CSS/JavaScript | Accessible, small, easy to inspect; no frontend build pipeline | Complex shared UI state would be easier with a component framework |
| Fixed public corpus | Reproducible demo, no upload storage or authentication needed | Not a private company knowledge platform |
| Explicit BM25 implementation | A useful baseline you can explain line by line | Simple tokenizer has no stemming or multilingual normalization |
| NumPy vector search | Exact, understandable retrieval for a small corpus | Search cost grows with passages and embedding dimensions |
| Hosted models | No GPU or local model memory requirements on Render | API costs, network dependency and external data processing |
| Structured claims with source IDs | Citation references can be validated before display | Schema validity is not factual correctness |
| Visible excerpt demo mode | Runs immediately without credentials | Does not demonstrate real semantic search or generated answers |
| No automatic live fallback | Configuration or provider errors remain visible | Users must explicitly retry if the provider is unavailable |
| In-memory feedback | Small, bounded implementation without a database | Feedback disappears on restart |

## What would justify the next layer of complexity?

- Add a vector database when measured memory use, update frequency or search latency demands it.
- Add a shared limiter and durable feedback store before multiple replicas.
- Add identity and per-document authorization **before** accepting private documents.
- Add OCR when the product actually needs scanned documents and evaluation data exists.
- Add a reranker only after measured retrieval failures justify latency and cost.

## A decision journal to continue

For each improvement, record: **problem → options → experiment → decision → limitation**.

Example: “The keyword baseline missed paraphrases on an expanded test set. I compared semantic and hybrid retrieval using the same frozen questions. I selected the method with better evidence recall under an acceptable latency budget.” Only write that in the past tense after actually running it.

