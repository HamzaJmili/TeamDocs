"""Turn Markdown/text PDFs into a reproducible, page-aware search collection."""
import argparse
import asyncio
import json
import re
from pathlib import Path
from app.config import ROOT, Settings
from app.retrieval import corpus_hash


def split_words(text: str, size: int = 180, overlap: int = 30):
    """Word windows stay inside their source section/page."""
    if size <= overlap or overlap < 0:
        raise ValueError("Chunk size must exceed non-negative overlap")
    words = text.split()
    for start in range(0, len(words), size - overlap):
        yield " ".join(words[start:start + size])
        if start + size >= len(words):
            break


def parse_document(path: Path):
    """Return title, category and (section, page, text) tuples."""
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader
        reader = PdfReader(path)
        sections = [(f"Page {i + 1}", i + 1, p.extract_text() or "") for i, p in enumerate(reader.pages)]
        if not any(text.strip() for _, _, text in sections):
            raise ValueError(f"{path.name}: no text found. OCR is outside this release.")
        return path.stem.replace("-", " ").title(), "Reference", sections
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^# (.+)$", text, re.M)
    title = title_match.group(1) if title_match else path.stem
    category_match = re.search(r"^Category: (.+)$", text, re.M)
    category = category_match.group(1) if category_match else "Reference"
    parts = re.split(r"^## (.+)$", text, flags=re.M)
    sections = [(parts[i].strip(), None, parts[i + 1].strip()) for i in range(1, len(parts), 2)]
    if not sections:
        body = re.sub(r"^# .+$|^Category: .+$", "", text, flags=re.M).strip()
        sections = [("Overview", None, body)]
    return title, category, sections


def ingest(source: Path, destination: Path):
    """Create stable chunk IDs, safe source mappings and a corpus fingerprint."""
    documents, chunks = [], []
    for path in sorted(source.iterdir()):
        if path.suffix.lower() not in {".md", ".pdf"}:
            continue
        title, category, sections = parse_document(path)
        document_id = re.sub(r"[^a-z0-9-]", "-", path.stem.lower())
        if any(d["id"] == document_id for d in documents):
            raise ValueError(f"Duplicate document identifier: {document_id}")
        count = 0
        for section_number, (section, page, body) in enumerate(sections, 1):
            for part, passage in enumerate(split_words(body), 1):
                if not passage.strip():
                    continue
                count += 1
                chunks.append({"id": f"{document_id}-s{section_number}-{part}", "document_id": document_id,
                    "title": title, "category": category, "section": section, "page": page, "text": passage})
        documents.append({"id": document_id, "title": title, "category": category, "filename": path.name,
            "format": path.suffix[1:].upper(), "chunks": count,
            "description": sections[0][2].split(". ")[0] + "." if sections else ""})
    if not chunks:
        raise ValueError("No readable documents found")
    destination.mkdir(parents=True, exist_ok=True)
    for name, value in (("documents", documents), ("chunks", chunks)):
        (destination / f"{name}.json").write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")
    return chunks


async def build_embeddings(chunks, destination, settings):
    """Explicitly invoked provider indexing. Rebuild only when inputs change."""
    import numpy as np
    from app.provider import make_provider
    if not settings.provider_key:
        raise ValueError("Set the API key for your AI_PROVIDER before building embeddings")
    fingerprint = corpus_hash(chunks)
    metadata_path = destination / "embedding_meta.json"
    metadata = {"provider": settings.provider, "model": settings.embedding_model, "corpus_hash": fingerprint}
    if metadata_path.exists() and (destination / "embeddings.npz").exists():
        if json.loads(metadata_path.read_text()) == metadata:
            print("Embedding index already matches the corpus; no API calls made.")
            return
    provider = make_provider(settings)
    vectors = []
    for start in range(0, len(chunks), 64):
        texts = [c["title"] + "\n" + c["section"] + "\n" + c["text"] for c in chunks[start:start + 64]]
        batch = await provider.embed_documents(texts, settings.embedding_model)
        if len(batch) != len(texts):
            raise ValueError("Embedding count mismatch")
        vectors.extend(batch)
    np.savez_compressed(destination / "embeddings.npz", vectors=np.asarray(vectors, dtype=np.float32))
    metadata_path.write_text(json.dumps(metadata, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embeddings", action="store_true", help="Calls the configured embedding API; uses provider quota; charges depend on your plan")
    args = parser.parse_args()
    directory = ROOT / "data/index"
    chunks = ingest(ROOT / "data/documents", directory)
    if args.embeddings:
        asyncio.run(build_embeddings(chunks, directory, Settings()))
    print(f"Indexed {len(chunks)} passages. Public demo documents only.")


if __name__ == "__main__":
    main()

