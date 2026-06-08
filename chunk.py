"""Chunking for The Unofficial Guide (Milestone 3).

Strategy (see planning.md): one chunk per member, plus one group-header chunk
per document. Each chunk is prefixed with a "<Group> — <Member>" context line
and carries metadata for the vector store.

Member boundaries are detected structurally rather than by a single field,
because the older profiles are irregular (2NE1's Minzy and three H.O.T. members
have no "Stage Name:" line). A line starts a new member when it is a plain
name line (no colon, not a fact bullet) that follows a blank line or a
"... Profile(s):" section header and is soon followed by a profile field.

Most members fit in a single chunk, but 16 exceed bge-small's 512-token limit
(Jung Kook is ~1001). Those are packed into sequential sub-chunks under the cap
(each repeating the "<Group> — <Member>" header) so no content is silently
truncated at embed time. Token counts use the real bge-small tokenizer.

Run directly to inspect chunk counts and samples:
    python chunk.py
"""

import re
import sys

from ingest import load_documents

# Profile field labels that confirm a candidate line really begins a member.
_FIELD = re.compile(
    r"^(Stage Name|Birth Name|Real Name|English Name|Korean Name|Chinese Name|"
    r"Position|Birthday|Zodiac|Height|Nationality)\b.*:",
)
# bge-small's max sequence length; pack a little under it for tokenizer-vs-model
# rounding safety.
MAX_TOKENS = 500

_tokenizer = None


def bge_token_count(text: str) -> int:
    """Exact bge-small token count (including the CLS/SEP special tokens that
    count toward the 512 limit). The tokenizer is loaded once and cached.
    """
    global _tokenizer
    if _tokenizer is None:
        from transformers import AutoTokenizer

        _tokenizer = AutoTokenizer.from_pretrained("BAAI/bge-small-en-v1.5")
    return len(_tokenizer(text, add_special_tokens=True)["input_ids"])


def _group_name(source: str) -> str:
    """Derive a display group name from the filename."""
    stem = source.rsplit(".", 1)[0]
    stem = re.sub(r"\s*Members? Profile.*$", "", stem)
    return stem.strip()


def _is_section_break(prev: str) -> bool:
    """True if the previous line ends a section: blank, or a label-only line
    ending in a colon (e.g. "aespa Member Profiles:", "Former Members:",
    "Member for Eternity:"). Field lines like "Position: Leader" end with a
    value, not a colon, so they are not treated as breaks.
    """
    return prev == "" or prev.endswith(":")


def _find_member_starts(lines: list[str]) -> list[int]:
    starts = []
    for i, line in enumerate(lines):
        s = line.strip()
        # Member name headers are short, have no colon, and are not fact
        # bullets. The length guard rejects the long group-description
        # paragraph, which would otherwise match (a real field follows it).
        if not s or ":" in s or s[0] in "–-•" or len(s) > 40:
            continue
        prev = lines[i - 1].strip() if i > 0 else ""
        if not _is_section_break(prev):
            continue
        window = [l.strip() for l in lines[i + 1 : i + 13] if l.strip()]
        if any(_FIELD.match(w) for w in window):
            starts.append(i)
    return starts


def _pack_lines(header: str, body_lines: list[str], count_tokens, max_tokens: int) -> list[str]:
    """Greedily pack body lines into sub-chunk bodies that each stay under
    max_tokens once the header is prepended. Splits happen on line boundaries,
    so a fact bullet or field is never cut mid-line.
    """
    parts: list[str] = []
    cur: list[str] = []

    def fits(extra_lines: list[str]) -> bool:
        candidate = header + "\n" + "\n".join(extra_lines)
        return count_tokens(candidate) <= max_tokens

    for line in body_lines:
        if cur and not fits(cur + [line]):
            parts.append("\n".join(cur))
            cur = [line]
        else:
            cur.append(line)
    if cur:
        parts.append("\n".join(cur))
    return parts


def chunk_document(doc: dict, count_tokens=bge_token_count, max_tokens: int = MAX_TOKENS) -> list[dict]:
    """Split one {"source", "text"} doc into group-header + per-member chunks.

    A member whose chunk would exceed max_tokens is packed into multiple
    sub-chunks (see _pack_lines). Pass count_tokens=None to disable packing
    (keep every member whole) — handy for quick boundary inspection.
    """
    source = doc["source"]
    group = _group_name(source)
    lines = doc["text"].split("\n")
    starts = _find_member_starts(lines)

    spans = []  # (member_name_or_None, start, end)
    first = starts[0] if starts else len(lines)
    spans.append((None, 0, first))  # group header
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        spans.append((lines[start].strip(), start, end))

    chunks = []
    chunk_index = 0
    for member, start, end in spans:
        body = "\n".join(lines[start:end]).strip()
        if not body:
            continue
        if member is None:
            header, chunk_type, member_name = f"{group} — Group Info", "group_header", ""
        else:
            header, chunk_type, member_name = f"{group} — {member}", "member", member

        full = f"{header}\n{body}"
        if count_tokens is None or count_tokens(full) <= max_tokens:
            bodies = [body]
        else:
            bodies = _pack_lines(header, body.split("\n"), count_tokens, max_tokens)

        n_parts = len(bodies)
        for part, part_body in enumerate(bodies):
            chunks.append(
                {
                    "text": f"{header}\n{part_body}",
                    "metadata": {
                        "source": source,
                        "group": group,
                        "member": member_name,
                        "chunk_type": chunk_type,
                        "chunk_index": chunk_index,
                        "part": part,
                        "n_parts": n_parts,
                    },
                }
            )
            chunk_index += 1
    return chunks


def chunk_all(docs: list[dict] | None = None, count_tokens=bge_token_count) -> list[dict]:
    docs = docs if docs is not None else load_documents()
    out = []
    for doc in docs:
        out.extend(chunk_document(doc, count_tokens=count_tokens))
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    chunks = chunk_all()
    counts = [bge_token_count(c["text"]) for c in chunks]

    n_members = len({(c["metadata"]["group"], c["metadata"]["member"])
                     for c in chunks if c["metadata"]["chunk_type"] == "member"})
    n_group = sum(1 for c in chunks if c["metadata"]["chunk_type"] == "group_header")
    n_split = sum(1 for c in chunks if c["metadata"]["part"] == 0 and c["metadata"]["n_parts"] > 1)

    print(f"Total chunks: {len(chunks)}   ({n_members} members across "
          f"{len(chunks) - n_group} member-chunks + {n_group} group headers)")
    print(f"Members split into sub-chunks: {n_split}")
    print(f"Token counts: min={min(counts)}  median={sorted(counts)[len(counts)//2]}  "
          f"max={max(counts)}   over {MAX_TOKENS}: {sum(t > MAX_TOKENS for t in counts)}\n")

    # Show which members were split.
    print("Split members:")
    for c in chunks:
        if c["metadata"]["part"] == 0 and c["metadata"]["n_parts"] > 1:
            print(f"  {c['metadata']['group']} — {c['metadata']['member']}: "
                  f"{c['metadata']['n_parts']} parts")

    # Milestone 3 checkpoint: print 5 representative chunks to read.
    samples = [
        next(c for c in chunks if c["metadata"]["chunk_type"] == "group_header"),
        next(c for c in chunks if c["metadata"]["member"] == "Minzy"),
        next(c for c in chunks if c["metadata"]["member"] == "NingNing"),
        next(c for c in chunks if c["metadata"]["member"] == "Jung Kook" and c["metadata"]["part"] == 0),
        next(c for c in chunks if c["metadata"]["member"] == "Jung Kook" and c["metadata"]["part"] == 1),
    ]
    for c in samples:
        md = c["metadata"]
        print("\n" + "=" * 70)
        print(f"[{md['chunk_type']}] {md['group']} — {md['member'] or 'Group Info'} "
              f"(part {md['part'] + 1}/{md['n_parts']}, {bge_token_count(c['text'])} tokens)")
        print("=" * 70)
        print(c["text"])
