"""Grounded generation for The Unofficial Guide (Milestone 5).

Retrieves the top-k chunks (retrieval.py), passes them to Groq's
llama-3.3-70b-versatile as the ONLY allowed source of truth, and returns an
answer plus the source documents it drew from.

Grounding is enforced two ways:
  1. A system prompt that forbids using outside knowledge and requires the
     model to say it doesn't have enough information when the context is silent.
  2. Source attribution is appended programmatically from chunk metadata, so it
     never depends on the model remembering to cite.

    python generate.py        # runs the 5 evaluation questions + an out-of-scope one
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq

from retrieval import EVAL_QUERIES, TOP_K, retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
NOT_ENOUGH = "I don't have enough information on that."

SYSTEM_PROMPT = (
    "You are a K-pop knowledge assistant. Answer the user's question using ONLY "
    "the information in the provided context documents. Follow these rules:\n"
    "1. Do not use any outside or prior knowledge, even if you are confident.\n"
    f'2. If the context does not contain the answer, reply exactly: "{NOT_ENOUGH}"\n'
    "3. Do not guess or fill gaps. Only state facts present in the context.\n"
    "4. Be concise and factual."
)

_client = None


def _groq() -> Groq:
    global _client
    if _client is None:
        _client = Groq(api_key=os.environ["GROQ_API_KEY"])
    return _client


def _format_context(chunks: list[dict]) -> str:
    """Render retrieved chunks into a labeled context block for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, 1):
        md = c["metadata"]
        who = md["member"] or "Group Info"
        blocks.append(f"[Document {i} — {md['group']} / {who} (source: {md['source']})]\n{c['text']}")
    return "\n\n".join(blocks)


def _source_list(chunks: list[dict]) -> list[str]:
    """Unique source documents behind the retrieved chunks, in retrieval order."""
    seen, sources = set(), []
    for c in chunks:
        src = c["metadata"]["source"]
        if src not in seen:
            seen.add(src)
            sources.append(src)
    return sources


def ask(question: str, k: int = TOP_K) -> dict:
    """Answer a question grounded in retrieved chunks.

    Returns {"answer", "sources", "chunks"}. "sources" is empty when the model
    reports it lacks the information, so we don't cite documents for a non-answer.
    """
    chunks = retrieve(question, k=k)
    context = _format_context(chunks)
    user_msg = f"Context documents:\n\n{context}\n\nQuestion: {question}"

    resp = _groq().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0,
    )
    answer = resp.choices[0].message.content.strip()

    sources = [] if answer.strip() == NOT_ENOUGH else _source_list(chunks)
    return {"answer": answer, "sources": sources, "chunks": chunks}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    questions = EVAL_QUERIES + ["Who is the leader of TWICE?"]  # last = out-of-scope
    for q in questions:
        result = ask(q)
        print("=" * 70)
        print("Q:", q)
        print("-" * 70)
        print(result["answer"])
        if result["sources"]:
            print("\nSources:")
            for s in result["sources"]:
                print(f"  • {s}")
        print()
