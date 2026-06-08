"""Embedding + retrieval for The Unofficial Guide (Milestone 4).

Embeds the chunks from chunk.py with BAAI/bge-small-en-v1.5 (local, via
sentence-transformers), stores them in a persistent ChromaDB collection with
metadata, and exposes retrieve() for top-k semantic search.

Per planning.md:
  - embedding model : BAAI/bge-small-en-v1.5  (384-dim, cosine)
  - top-k           : 5
  - BGE query prefix: queries (not documents) are prefixed with the
    "Represent this sentence..." instruction for better short-query matching.

Build the index, then run the evaluation queries:
    python retrieval.py
"""

import sys
from pathlib import Path

import chromadb

from chunk import chunk_all

MODEL_NAME = "BAAI/bge-small-en-v1.5"
PERSIST_DIR = str(Path(__file__).parent / "chroma_db")
COLLECTION = "kpop_profiles"
TOP_K = 5
# bge-small recommends prefixing the *query* (not the documents) for retrieval.
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "

_embedder = None


def get_embedder():
    """Load and cache the sentence-transformers model."""
    global _embedder
    if _embedder is None:
        from sentence_transformers import SentenceTransformer

        _embedder = SentenceTransformer(MODEL_NAME)
    return _embedder


def _embed(texts: list[str]):
    """Encode texts to normalized vectors (cosine similarity ready)."""
    model = get_embedder()
    return model.encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()


def build_index(persist_dir: str = PERSIST_DIR) -> int:
    """(Re)build the Chroma collection from all chunks. Returns chunk count."""
    client = chromadb.PersistentClient(path=persist_dir)
    # Start fresh so re-runs reflect any chunk changes.
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    collection = client.create_collection(
        COLLECTION, metadata={"hnsw:space": "cosine"}
    )

    chunks = chunk_all()
    ids = [f"{c['metadata']['source']}#{c['metadata']['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    embeddings = _embed(documents)

    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    return len(chunks)


def get_collection(persist_dir: str = PERSIST_DIR):
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_collection(COLLECTION)


def retrieve(query: str, k: int = TOP_K, persist_dir: str = PERSIST_DIR) -> list[dict]:
    """Return the top-k chunks for a query as
    [{"text", "metadata", "distance"}], lowest cosine distance first.
    """
    collection = get_collection(persist_dir)
    q_emb = _embed([QUERY_PREFIX + query])
    res = collection.query(
        query_embeddings=q_emb,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    return [
        {"text": doc, "metadata": md, "distance": dist}
        for doc, md, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0])
    ]


# The 5 evaluation questions from planning.md.
EVAL_QUERIES = [
    "Who is the maknae of aespa and what is her nationality?",
    "What does aespa's name come from?",
    "When did 2NE1 disband and which member left the group before that?",
    "What individual agencies did the BLACKPINK members set up?",
    "Which girl groups are under YG Entertainment?",
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    print(f"Building index ({MODEL_NAME}) ...")
    n = build_index()
    print(f"Indexed {n} chunks into '{COLLECTION}'.\n")

    for q in EVAL_QUERIES:
        print("=" * 70)
        print("QUERY:", q)
        print("=" * 70)
        for r in retrieve(q):
            md = r["metadata"]
            who = md["member"] or "Group Info"
            part = f" [part {md['part'] + 1}/{md['n_parts']}]" if md["n_parts"] > 1 else ""
            snippet = " ".join(r["text"].split("\n")[1:])[:150]
            print(f"  dist={r['distance']:.3f}  {md['group']} — {who}{part}")
            print(f"           {snippet}...")
        print()
