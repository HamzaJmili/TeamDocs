# Run it locally

## Requirements

- Python 3.12 or newer. Development validation used Python 3.12.
- Git, if you want to clone or publish the repository.
- An internet connection to install packages.
- No API key for demo mode.

The tested package versions are pinned in `requirements-lock.txt`. Runtime and development requirements use it as a constraints file.

## Windows PowerShell

Open a terminal inside the repository:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m scripts.ingest
.\.venv\Scripts\python.exe -m sphinx -W -b html docs docs/_build/html
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Using the virtual environment's Python directly avoids PowerShell activation-policy changes.

## macOS and Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env
python -m scripts.ingest
python -m sphinx -W -b html docs docs/_build/html
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. The guide is at `/guide/`, and interactive API documentation is at `/api/docs`.

## Enable live AI with Gemini

1. Copy `.env.gemini.example` to `.env`. If `.env` already exists, edit its settings instead of overwriting it.
2. Replace `replace_with_your_key` with your Google AI Studio key inside `.env` only.
3. Open a terminal in the project folder and run:

```powershell
.\.venv\Scripts\python.exe -m scripts.ingest --embeddings
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`. The template enables live mode and selects `gemini-embedding-001` for retrieval and `gemini-3.6-flash` for answers. Indexing must succeed before starting live mode.

The key stays on the server. Never paste it into JavaScript, GitHub, or the chat. `.env` is ignored by Git. Google account/model access and quotas vary; check [Google AI Studio](https://aistudio.google.com/) and [provider pricing](https://ai.google.dev/gemini-api/docs/pricing). A free quota is not unlimited usage. Use only the included public fictional documents.

If indexing reports a provider failure, check the key, model access and quota in AI Studio. Wait for quota renewal if exhausted; do not repeatedly rerun indexing. Restart the server after editing `.env`. If you switch embedding models or providers, rebuild the index.

## OpenAI alternative

Use `.env.example`, set `AI_PROVIDER=openai`, `OPENAI_API_KEY`, `EMBEDDING_MODEL=text-embedding-3-small` and `ANSWER_MODEL=gpt-4.1-mini`. Run ingestion with `--embeddings`, then enable `APP_MODE=live` and restart. Calls use your OpenAI API billing account.

Indexing skips API calls when the corpus fingerprint, provider and model match. Live startup rejects missing keys and mismatched indexes.

## Add documents

Place text-based `.pdf` or `.md` files directly in `data/documents/`. Markdown should have a `# Title`, a `Category: Name` line, and `## Section` headings. PDF documents are placed in the Reference collection.

Run ingestion again. For live mode, rebuild with `--embeddings`. Review metadata, source passages and retrieval results after every corpus change. The current parser expects well-formed Markdown and text PDFs; scanned PDFs need an OCR workflow that is not included.

Everything in this collection is publicly downloadable through the application. Do not put private documents here.

## Useful commands

```bash
python -m pytest -q
python -m scripts.evaluate --split dev
python -m scripts.evaluate --split test --output evaluation/test-results.json
python -m sphinx -W --keep-going -b html docs docs/_build/html
```

