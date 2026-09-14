# Delivery validation

The project was validated locally on Windows with Python 3.12. This records what was actually checked; it is not a production certification.

| Check | Result |
| --- | --- |
| Automated backend and integration tests | 48 passed |
| Dependency consistency | `pip check` passed |
| Frontend JavaScript syntax | Node syntax check passed |
| Sphinx HTML documentation | Build passed with warnings treated as errors |
| Desktop interface | Visually inspected in a browser |
| Mobile interface | Inspected at 390px width; no horizontal content overflow observed |
| Question → source citation → original passage | Verified through the browser |
| Feedback | Verified temporary save confirmation |
| Library filtering | Verified on the mobile layout |
| Quality Lab and Sphinx guide | Loaded and inspected in the browser |
| Architecture illustration | Visually inspected |

Two upstream test-client deprecation warnings were emitted; they did not fail the test suite. No warnings were emitted by the strict Sphinx build.

## Retrieval reports

The checked-in development report covers 30 questions, including 24 answerable ones. BM25 found at least one expected passage in the top five for all 24. The designated test report covers 20 questions, including 16 answerable ones, and also found expected evidence for all 16. This is a small, clean, author-written fictional corpus. These results measure retrieval, not answer correctness or real-world performance. Per-question details are in `evaluation/results.json` and `evaluation/test-results.json`.

## Not yet verified externally

- Real embedding and answer API calls using the owner's credentials.
- Human evaluation of live AI answers, citation support and abstention.
- A GitHub-hosted CI run after the repository is pushed.
- A Render deployment and public deployment smoke test.
- The optional Docker image build on a Docker host.

The live integration is implemented and tested with deterministic fake providers. Demo mode is usable without external credentials. Follow `docs/deployment.md` for the remaining external steps.

Gemini adapter tests cover document/query task types, vector order and validation, structured answers and incomplete-response rejection. No real Gemini key was used; live connectivity remains to be checked after local configuration.

Live Gemini verification: 20 documents / 60 passages indexed successfully with gemini-embedding-001. Google rejected gemini-2.5-flash for this new account; gemini-3.6-flash succeeded. A real hybrid-search request returned HTTP 200 with an answered status, two cited claims and five retrieved sources. Homepage and health checks passed. This smoke test does not measure overall answer accuracy.

English/French interface verification: automated headless Edge checks passed for navigation, source reader labels, quality results, saved preference after reload, switching back to English, unchanged source/answer text, and a 390px mobile viewport without horizontal overflow. Dynamic answer rendering used a simulated API response; no model calls were made for this UI check. Desktop/mobile screenshots were inspected.
