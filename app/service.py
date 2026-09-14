"""The question-to-evidence workflow shared by the API and tests."""
import re
import time
from app.retrieval import SearchIndex, tokenize
from app.provider import ProviderError


def validate_claims(result: dict, sources: list[dict]) -> list[dict]:
    """Reject fabricated source IDs. This does not prove semantic correctness."""
    if not isinstance(result, dict) or not isinstance(result.get("answerable"), bool):
        raise ProviderError("The AI service returned an invalid answer format.")
    if not result.get("answerable"):
        return []
    allowed = {s["id"] for s in sources}
    claims = result.get("claims", [])
    if not isinstance(claims, list) or not claims or len(claims) > 4:
        raise ProviderError("The answer could not be linked reliably to its sources.")
    for claim in claims:
        if not isinstance(claim, dict):
            raise ProviderError("Invalid answer format")
        ids = claim.get("source_ids")
        if (not isinstance(claim.get("text"), str) or not claim["text"].strip() or len(claim["text"]) > 3000
            or not isinstance(ids, list) or not ids or any(not isinstance(i, str) or i not in allowed for i in ids)):
            raise ProviderError("The answer could not be linked reliably to its sources.")
    return claims


class AnswerService:
    """Real lexical demo; optional semantic retrieval and generated answers."""
    def __init__(self, index: SearchIndex, settings, provider=None):
        self.index, self.settings, self.provider = index, settings, provider

    async def ask(self, question: str, category="All", method="bm25") -> dict:
        started = time.perf_counter()
        live = self.settings.mode == "live"
        vector = None
        if method != "bm25":
            if not live or self.index.vectors is None:
                raise ValueError("Semantic search is available after enabling live mode and building embeddings.")
            vector = (await self.provider.embed([question], self.settings.embedding_model))[0]
        sources = self.index.search(question, category, method, vector)
        if live and sources:
            claims = validate_claims(await self.provider.answer(question, sources, self.settings.answer_model), sources)
            status = "answered" if claims else "insufficient_evidence"
        else:
            # An excerpt is never presented as a generated answer or confident refusal.
            terms = set(tokenize(question))
            ranked = []
            for source in sources:
                sentences = re.split(r"(?<=[.!?])\s+", source["text"])
                sentence = max(sentences, key=lambda s: len(terms & set(tokenize(s))))
                overlap = len(terms & set(tokenize(sentence)))
                if overlap >= min(2, max(len(terms), 1)):
                    ranked.append({"text": sentence, "source_ids": [source["id"]]})
            claims = ranked[:3]
            status = "excerpts" if claims else "insufficient_evidence"
        return {"mode": self.settings.mode, "status": status, "claims": claims, "sources": sources,
            "method": method, "elapsed_ms": round((time.perf_counter() - started) * 1000),
            "notice": "Exact passages from the library. Demo mode does not generate AI answers." if not live else "AI synthesis. Check the supporting passages; citations do not guarantee correctness."}
