"""BM25, cosine similarity and reciprocal-rank fusion in plain Python."""
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
import numpy as np

STOP = set("a an the is are was were be been to of for from in on at by with and or as it this that these those i me my we our you your how what which who when where do does can could should would please about have has get need want".split())


def tokenize(text: str) -> list[str]:
    """Lowercase word tokens; deliberately no hidden synonym expansion."""
    return [word for word in re.findall(r"[a-z0-9]+", text.lower()) if word not in STOP]


def corpus_hash(chunks: list[dict]) -> str:
    """Bind a semantic index to the precise chunks and their order."""
    return hashlib.sha256(json.dumps(chunks, sort_keys=True).encode()).hexdigest()


class SearchIndex:
    """Read-only small-corpus index, with optional precomputed embeddings."""

    def __init__(self, directory: Path):
        self.chunks = json.loads((directory / "chunks.json").read_text(encoding="utf-8"))
        self.documents = json.loads((directory / "documents.json").read_text(encoding="utf-8"))
        self.tokens = [tokenize(c["title"] + " " + c["section"] + " " + c["text"]) for c in self.chunks]
        self.counts = [Counter(tokens) for tokens in self.tokens]
        self.avg_length = sum(map(len, self.tokens)) / max(len(self.tokens), 1)
        self.df = Counter(t for tokens in self.tokens for t in set(tokens))
        self.vectors = None
        self.embedding_model = None
        self.embedding_provider = "openai"
        if (directory / "embeddings.npz").exists():
            meta = json.loads((directory / "embedding_meta.json").read_text())
            if meta["corpus_hash"] != corpus_hash(self.chunks):
                raise ValueError("Stale embeddings: run python -m scripts.ingest --embeddings")
            with np.load(directory / "embeddings.npz", allow_pickle=False) as archive:
                self.vectors = archive["vectors"].astype(np.float32)
            if len(self.vectors) != len(self.chunks) or not np.isfinite(self.vectors).all():
                raise ValueError("Invalid embedding index")
            self.embedding_model = meta["model"]
            self.embedding_provider = meta.get("provider", "openai")

    def bm25_scores(self, question: str) -> list[float]:
        """BM25 with k1=1.5 and b=0.75; scores are not confidence values."""
        scores = []
        for counts, tokens in zip(self.counts, self.tokens):
            value = 0.0
            for term in set(tokenize(question)):
                frequency = counts[term]
                idf = math.log(1 + (len(self.chunks) - self.df[term] + .5) / (self.df[term] + .5))
                denom = frequency + 1.5 * (1 - .75 + .75 * len(tokens) / max(self.avg_length, 1))
                value += idf * frequency * 2.5 / denom
            scores.append(value)
        return scores

    def search(self, question: str, category: str = "All", method: str = "bm25", vector=None, top_k: int = 5) -> list[dict]:
        """Rank within a category. Hybrid combines ranks, not incompatible scores."""
        candidates = [i for i, c in enumerate(self.chunks) if category == "All" or c["category"] == category]
        lexical = self.bm25_scores(question)
        lexical_order = sorted((i for i in candidates if lexical[i] > 0), key=lambda i: (-lexical[i], i))
        if method == "bm25":
            order, scores = lexical_order, lexical
        else:
            if self.vectors is None or vector is None:
                raise ValueError("Semantic retrieval requires a matching embedding index and question vector")
            v = np.asarray(vector, dtype=np.float32)
            if v.shape != (self.vectors.shape[1],) or not np.isfinite(v).all():
                raise ValueError("Question embedding dimension mismatch")
            similarities = self.vectors @ v / (np.maximum(np.linalg.norm(self.vectors, axis=1), 1e-9) * max(np.linalg.norm(v), 1e-9))
            semantic_order = sorted(candidates, key=lambda i: (-float(similarities[i]), i))
            if method == "semantic":
                order, scores = semantic_order, similarities
            elif method == "hybrid":
                fused = Counter()
                for ranking in (lexical_order, semantic_order):
                    for rank, i in enumerate(ranking):
                        fused[i] += 1 / (60 + rank + 1)
                scores = fused
                order = sorted(candidates, key=lambda i: (-fused[i], i))
            else:
                raise ValueError("Unknown retrieval method")
        return [{**self.chunks[i], "score": round(float(scores[i]), 5)} for i in order[:top_k]]

