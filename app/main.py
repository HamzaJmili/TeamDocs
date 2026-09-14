"""FastAPI routes and a single-service deployment entry point."""
import json
import time
from collections import OrderedDict, deque
from datetime import datetime, timezone
from uuid import uuid4
from typing import Literal
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from app.config import ROOT, Settings
from app.provider import make_provider, ProviderError
from app.retrieval import SearchIndex
from app.service import AnswerService


class Question(BaseModel):
    question: str = Field(min_length=3, max_length=600)
    category: str = Field(default="All", max_length=40)
    method: Literal["bm25", "semantic", "hybrid"] = "bm25"


class Feedback(BaseModel):
    answer_id: str = Field(max_length=40)
    helpful: bool


class Limiter:
    """Bounded, single-process limits. Reverse-proxy headers are not trusted."""
    def __init__(self, per_minute: int, daily: int):
        self.per_minute, self.daily = per_minute, daily
        self.clients = OrderedDict()
        self.day, self.calls = datetime.now(timezone.utc).date(), 0

    def check(self, client: str, live: bool):
        now = time.monotonic()
        today = datetime.now(timezone.utc).date()
        if today != self.day:
            self.day, self.calls = today, 0
        window = self.clients.setdefault(client, deque())
        self.clients.move_to_end(client)
        while window and now - window[0] >= 60:
            window.popleft()
        if len(window) >= self.per_minute:
            raise HTTPException(429, "Please wait a minute before asking another question.", headers={"Retry-After": "60"})
        if live and self.calls >= self.daily:
            raise HTTPException(429, "Today's live demo allowance has been reached. Try the library instead.")
        window.append(now)
        while len(self.clients) > 2000:
            self.clients.popitem(last=False)
        if live:
            self.calls += 1


def create_app(settings=None, index=None, provider=None):
    """Application factory lets tests inject a fake provider without network calls."""
    settings = settings or Settings()
    index = index or SearchIndex(ROOT / "data/index")
    if settings.mode not in {"demo", "live"}:
        raise ValueError("APP_MODE must be demo or live")
    if settings.mode == "live" and not settings.provider_key:
        raise ValueError("Live mode requires GEMINI_API_KEY or OPENAI_API_KEY for the selected AI_PROVIDER")
    if settings.mode == "live" and index.vectors is None:
        raise ValueError("Live mode requires an embedding index; run ingestion with --embeddings")
    if settings.mode == "live" and (index.embedding_model != settings.embedding_model or index.embedding_provider != settings.provider):
        raise ValueError("Embedding model differs from the saved index")
    service = AnswerService(index, settings, provider or make_provider(settings))
    limiter = Limiter(settings.rate_limit, settings.daily_limit)
    answers = OrderedDict()
    application = FastAPI(title="TeamDocs API", version="1.0.0", docs_url="/api/docs", redoc_url=None)

    @application.middleware("http")
    async def headers_and_body_limit(request, call_next):
        # Bound streamed request bodies as well as Content-Length.
        if request.method == "POST":
            body = bytearray()
            async for block in request.stream():
                body.extend(block)
                if len(body) > 8192:
                    return JSONResponse({"detail": "Request is too large."}, status_code=413)
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'" if not request.url.path.startswith(("/guide", "/api/docs")) else "frame-ancestors 'none'"
        return response

    @application.get("/health")
    def health():
        return {"status": "ok", "mode": settings.mode, "documents": len(index.documents), "chunks": len(index.chunks)}

    @application.get("/api/config")
    def config():
        return {"mode": settings.mode, "documents": len(index.documents), "chunks": len(index.chunks),
            "categories": sorted({d["category"] for d in index.documents}),
            "methods": ["bm25", "semantic", "hybrid"] if settings.mode == "live" else ["bm25"]}

    @application.get("/api/documents")
    def documents():
        return index.documents

    @application.get("/api/documents/{document_id}")
    def document(document_id: str):
        doc = next((d for d in index.documents if d["id"] == document_id), None)
        if not doc:
            raise HTTPException(404, "Document not found")
        return {**doc, "passages": [c for c in index.chunks if c["document_id"] == document_id]}

    @application.get("/api/documents/{document_id}/original")
    def original(document_id: str):
        doc = next((d for d in index.documents if d["id"] == document_id), None)
        if not doc:
            raise HTTPException(404, "Document not found")
        path = (ROOT / "data/documents" / doc["filename"]).resolve()
        if not path.is_relative_to((ROOT / "data/documents").resolve()):
            raise HTTPException(404, "Document not found")
        return FileResponse(path, filename=path.name)

    @application.post("/api/ask")
    async def ask(payload: Question, request: Request):
        question = payload.question.strip()
        if len(question) < 3:
            raise HTTPException(422, "Please enter a question with at least three characters.")
        categories = {d["category"] for d in index.documents} | {"All"}
        if payload.category not in categories:
            raise HTTPException(422, "Unknown collection")
        limiter.check(request.client.host if request.client else "unknown", settings.mode == "live")
        try:
            result = await service.ask(question, payload.category, payload.method)
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc
        except ProviderError as exc:
            raise HTTPException(503, str(exc)) from exc
        answer_id = str(uuid4())
        answers[answer_id] = None
        if len(answers) > 1000:
            answers.popitem(last=False)
        return {"answer_id": answer_id, **result}

    @application.post("/api/feedback")
    def feedback(payload: Feedback):
        if payload.answer_id not in answers:
            raise HTTPException(404, "This answer has expired. Run the question again to leave feedback.")
        answers[payload.answer_id] = payload.helpful
        return {"saved": True, "storage": "Temporary server memory; cleared on restart."}

    @application.get("/api/evaluation")
    def evaluation():
        path = ROOT / "evaluation/results.json"
        return json.loads(path.read_text()) if path.exists() else {"status": "not_run"}

    @application.get("/")
    def home():
        return FileResponse(ROOT / "app/static/index.html")

    application.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")
    if (ROOT / "docs/_build/html").exists():
        application.mount("/guide", StaticFiles(directory=ROOT / "docs/_build/html", html=True), name="guide")
    else:
        @application.get("/guide/")
        def guide_missing():
            return JSONResponse({"detail": "Build the guide with: python -m sphinx -b html docs docs/_build/html"}, status_code=503)
    return application


app = create_app()
