"""Document loading for The Unofficial Guide (Milestone 3).

The kprofiles boilerplate (site headers, image captions, "Show more" links,
logos) has already been removed from the files in documents/ by hand, so this
module just loads them. The only normalization left is collapsing runs of
blank lines so they don't create empty chunks later.

Run directly to inspect what gets loaded:
    python ingest.py
"""

import re
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"


def load_documents(docs_dir: Path = DOCS_DIR) -> list[dict]:
    """Load every .md profile in docs_dir.

    Returns a list of {"source": <filename>, "text": <text>} dicts.
    The group source file (kpop-source-documents.md) lives outside docs_dir,
    so it is not picked up here.
    """
    docs = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"  # tidy blank lines
        docs.append({"source": path.name, "text": text})
    return docs


if __name__ == "__main__":
    # The documents contain Hangul/Japanese/Chinese text; force UTF-8 output so
    # printing works on Windows consoles that default to cp1252.
    sys.stdout.reconfigure(encoding="utf-8")

    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {DOCS_DIR}\n")
    for d in docs:
        print(f"  {d['source']:<45} {len(d['text']):>6} chars")
