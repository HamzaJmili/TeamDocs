# GitHub and Render deployment

## Prepare your repository

Run the tests, ingestion check and documentation build before publishing. Confirm that `.env`, API keys and private documents are absent from staged files. The repository contains original fictional documents that are intended to be public.

Create an empty repository named `teamdocs` in your own GitHub account. From this project folder, run:

```bash
git init -b main
git add .
git commit -m "Build TeamDocs document search and project handbook"
```

Then copy the exact remote URL from GitHub and add it with `git remote add origin YOUR_REPOSITORY_URL`, followed by `git push -u origin main`. Replace the placeholder with your actual URL. If the directory is already a repository, inspect `git status` and `git remote -v` before changing anything.

The GitHub Actions workflow installs the pinned requirements, checks deterministic ingestion, runs tests, evaluates the development questions and builds Sphinx with warnings treated as errors. It uploads the guide and evaluation report as workflow artifacts. The workflow has been prepared locally; its GitHub-hosted run must be verified after pushing.

## Deploy live Gemini mode with Render

1. In Render, choose **New → Blueprint** and connect your repository.
2. Render reads `render.yaml` and creates one Python web service.
3. Enter your Gemini key when Render requests `GEMINI_API_KEY`. It is a secret field (`sync: false`), never a value in the repository. The Blueprint uses live mode.
4. Wait for the build and open the assigned URL.

The blueprint uses:

```text
Build:
pip install -r requirements-dev.txt && python -m scripts.ingest --embeddings && python -m sphinx -W --keep-going -b html docs docs/_build/html

Start:
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1

Health check:
/health
```

You can also create a web service manually using those same settings. Use Python 3.12.10, as specified in the repository. The guide is served at `/guide/` after its build completes.

## Configuration options

The checked-in Blueprint already includes live Gemini settings. To change them:

1. Add `GEMINI_API_KEY` through Render's environment settings. Never add the key to YAML or Git.
2. Change `APP_MODE` to `live` in `render.yaml` so future Blueprint syncs preserve it.
3. Set `AI_PROVIDER=gemini`, `EMBEDDING_MODEL=gemini-embedding-001` and `ANSWER_MODEL=gemini-3.6-flash`. For OpenAI instead, use `AI_PROVIDER=openai`, `OPENAI_API_KEY`, and the models from `.env.example`.
4. Change the blueprint's build command to include `python -m scripts.ingest --embeddings` instead of plain ingestion.
5. Keep the Sphinx build at the end, push the configuration change, sync the Blueprint, and redeploy. Never commit the API key.

The embedding index is generated during the build and included in that deployment's filesystem. API credentials must be available during the build. This avoids runtime uploads or disk persistence. A fresh build can incur embedding charges again; the local fingerprint cache is not a guarantee across clean Render builds.

Check the build logs for a successful embedding step. Live startup intentionally refuses to run with missing or mismatched embeddings.

## Hosting and budget limitations

Render free web services can sleep after 15 minutes without incoming traffic. Their runtime filesystem changes are ephemeral. The committed documents and build-generated files remain part of the deployment; temporary answers, rate-limit counters and feedback reset when the process restarts. See [Render free services](https://render.com/docs/free).

`LIVE_REQUESTS_PER_DAY=100` caps live question attempts per process per UTC calendar day. `RATE_LIMIT_PER_MINUTE=12` limits requests per observed client address. These are basic demo controls, not billing guarantees: they reset on restart, do not coordinate replicas, and depend on proxy configuration. They do not cap offline embedding jobs. Also configure the provider's available spending/rate controls and monitor usage.

Keep one worker. A production deployment needs trusted proxy configuration, shared limits, proper authentication and authorization before private documents are introduced.

## Verify the public deployment

- `/health` reports the expected mode and document count.
- A staging-access question produces traceable sources.
- A citation opens the correct section and its original file downloads.
- The document-library filters work on a narrow screen.
- `/guide/` and the interview guide load.
- An unsupported question does not produce an invented fact in live mode.
- A provider failure produces a friendly error, never a secret-bearing traceback.
- Reload after inactivity and check that the library is still available.

## Docker alternative

```bash
docker build -t teamdocs .
docker run --rm -p 8000:8000 teamdocs
```

The included image runs as a non-root user and defaults to demo mode. Its build recipe has no live key. For live mode, prepare an appropriate embedding artifact in your build pipeline and provide credentials only at the stages that need them. Do not put a key in an image layer.

## Official references

- [FastAPI on Render](https://render.com/docs/deploy-fastapi)
- [Render web services](https://render.com/docs/web-services)
- [Render free-service behavior](https://render.com/docs/free)
- [Sphinx quickstart](https://www.sphinx-doc.org/en/master/usage/quickstart.html)
- [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs)
- [OpenAI embeddings reference](https://developers.openai.com/api/reference/resources/embeddings/methods/create)

- [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key)
- [Gemini embeddings](https://ai.google.dev/api/embeddings)
