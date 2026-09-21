# Limitations and responsible operation

## Scope

This is a public, single-user-style portfolio demo. There are no accounts, private uploads, document permissions, connectors or background ingestion workers. All included source files are public and fictional. A category filter is not authorization.

## Search and answers

- English-only tokenization; no stemming or language detection.
- Short, clean sample documents; PDF reading order and complex tables may need a better parser.
- No OCR, document version precedence, reranking or conversational memory.
- Word-based chunking is simple and not an optimized tokenizer-based strategy.
- Demo excerpts can be relevant without fully answering the question.
- Live citations are checked for valid IDs, not proven entailment.
- Prompt injection defenses are limited to instruction separation and a tool-free generation path; adversarial model behavior has not been certified.
- The provider API path requires valid credentials and access. Automated fake-provider tests do not establish live service availability or model answer quality.

## Runtime

There is no persistent user-data storage. Feedback and limits are bounded and in memory. One worker is the supported deployment shape. A public live demo can still incur API charges despite the basic limits, especially across restarts. Configure provider-side controls and monitor use.

## Security boundaries

Keys remain on the server. Original-file downloads use indexed filenames, not arbitrary user paths. The frontend escapes untrusted values. Inputs and streamed bodies have size limits. Provider errors are replaced with safe messages.

These controls are useful engineering practices, not a security certification. Before a private-company rollout, add identity, per-document authorization before retrieval, durable auditing, proper data lifecycle handling, vetted ingestion, proxy-aware shared rate limiting and a reviewed provider-data policy.

## Known follow-up work

The most valuable next steps are an independently written benchmark, real live-model evaluation, a document-version policy, and a deployment smoke check on Render. Add complexity only in response to observed failures.


## Temporary provider failures

Gemini HTTP 502, 503 and 504 responses are retried once after one second. Credentials, unavailable models and quota errors are not retried. Persistent errors produce distinct user messages and log only the HTTP status. This bounded retry does not guarantee provider availability and can increase request latency.
