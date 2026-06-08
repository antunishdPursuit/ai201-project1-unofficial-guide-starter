# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

The history of K-pop idol groups across generations — focusing on group formation, member lineups, debut eras, agencies, fandoms, lineup changes (additions, departures, disbandments, reunions), and how group concepts and styles evolved from the first generation (H.O.T., S.E.S.) through the fourth (aespa).

This knowledge is valuable but hard to find through official channels because agencies and the groups themselves rarely publish a consolidated, factual history. Official sites are promotional and current-roster focused — they don't document former members, disbandment circumstances, contract disputes, or how a group fit into the broader generational timeline. That context is scattered across fan-maintained profile sites (e.g., kprofiles.com), forums, and community wikis, where it's accurate but fragmented across many pages and never indexed in one place. A retrieval system over these sources lets a user ask cross-cutting questions ("which second-generation girl groups broke from the cute concept?") that no single official page answers.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | H.O.T. Members Profile | First-generation boy group; SM Entertainment's early idol model, fandom identity, member positions, debut/disbandment timeline. | https://kprofiles.com/h-o-t-members-profile/ — `documents/H.O.T. Members Profile.md` |
| 2 | S.E.S Members Profile | First-generation girl group; early SM girl-group structure, member roles, disbandment, anniversary reunion context. | https://kprofiles.com/s-e-s-members-profile/ — `documents/S.E.S Members Profile.md` |
| 3 | BIGBANG Members Profile | Second-generation boy group; YG Entertainment, self-producing idol image, member departures, global influence. | https://kprofiles.com/big-bang-members-profile — `documents/BIGBANG Members Profile.md` |
| 4 | Girls' Generation / SNSD Members Profile | Second-generation girl group; large-member formations, fandom culture, member transitions, SM's girl-group legacy. | https://kprofiles.com/girls-generation-snsd-members-profile — `documents/Girls' Generation SNSD Members Profile.md` |
| 5 | SHINee Members Profile | Second-generation performance-focused group; vocal/dance roles, long-term group activity, solo career expansion. | https://kprofiles.com/shinee-members-profile — `documents/SHINee Members Profile.md` |
| 6 | 2NE1 Members Profile | Second-generation girl group with an edgier image; YG's hip-hop/pop branding, disbandment and reunion history. | https://kprofiles.com/2ne1-members-profile/ — `documents/2NE1 Members Profile.md` |
| 7 | EXO Members Profile | Early third-generation group; Korean/Chinese market strategy, large group structure, subunits, member departures. | https://kprofiles.com/exo-members-profile — `documents/EXO Members Profile.md` |
| 8 | BTS Members Profile | Third-generation global expansion; member roles, fandom identity, BigHit/HYBE era, international popularity. | https://kprofiles.com/bts-bangtan-boys-members-profile/ — `documents/BTS Members Profile.md` |
| 9 | BLACKPINK Members Profile | Third-generation girl group; global marketing, individual branding, YG's international strategy, solo careers. | https://kprofiles.com/black-pink-members-profile/ — `documents/BLACKPINK Members Profile.md` |
| 10 | aespa Members Profile | Fourth-generation group; virtual/avatar concepts, global label partnerships, newer SM branding and digital-world concepts. | https://kprofiles.com/aespa-members-profile/ — `documents/aespa Members Profile.md` |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
about 300 to 450 tokens so that it fits one members profile
**Overlap:**
about 50 tokens 
**Reasoning:**
a chunk would contain enough info about each members profile and would not cut into another member's profile
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
`BAAI/bge-small-en-v1.5` via sentence-transformers, running locally. It's 384-dim with a 512-token context, which fits a full ~300–450 token member chunk without truncation (unlike all-MiniLM-L6-v2, which cuts off at 256 tokens and would drop the tail of each member's facts). BGE also recommends prepending `"Represent this sentence for searching relevant passages: "` to the query (not the documents), so we do that for retrieval. Generation is handled separately by Groq.

**Top-k:**
5 chunks per query. Since each chunk is one member's profile, top-5 covers a full small group (e.g., all of aespa or BLACKPINK) or the most relevant members from a larger group like SNSD, giving the generator enough context to answer comparison questions without flooding it with off-topic members.

**Production tradeoff reflection:**
If cost weren't a constraint, the main tradeoffs I'd weigh are context length, multilingual support, and domain accuracy. A larger API-hosted model (e.g., OpenAI text-embedding-3-large or Voyage) would give higher retrieval accuracy and longer context, letting me embed an entire group's document as one chunk instead of per-member. Multilingual support matters a lot here: K-pop sources mix Korean, Japanese, and Chinese names and stage names, so a multilingual model (e.g., bge-m3 or multilingual-e5) would better match queries that use a romanized vs. Hangul name. The cost of going API-hosted is added latency and a network dependency per query, plus sending data off-machine; the local bge-small model is fast, free, and private, which is why it's the right default for this project even though it's not the most accurate option available.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | Who is the maknae (youngest member) of aespa, and what is her nationality? | NingNing — she is the maknae and main vocalist, and her nationality is Chinese (born in Harbin, China). |
| 2 | What does aespa's name (æ) come from? | "æ" is derived from "Avatar X Experience" combined with "aspect" — the theme of experiencing a new world by meeting your avatar "æ". |
| 3 | When did 2NE1 originally disband, and which member left the group before that? | Minzy left in April 2016; YG announced 2NE1's disbandment on November 25, 2016. (They later re-signed in July 2024 and disbanded again after their contracts ended in 2025.) |
| 4 | After renewing with YG in December 2023, which individual agency did each BLACKPINK member set up or sign with? | Lisa — LLOUD; Jennie — ODD ATELIER; Jisoo — BLISSOO; Rosé — signed with THEBLACKLABEL. |
| 5 | Which girl groups in this collection are under YG Entertainment? | 2NE1 and BLACKPINK are both under YG Entertainment. (Tests cross-document retrieval across two separate profiles.) |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. The queries would return incorrect questions because the generation was off

2. The chunks would mix member's profiles together and the retriecel process would be wrong.
---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
[1] Document Ingestion      ->  read .md files from documents/        (Python file I/O)
[2] Chunking                ->  split per member (+ group header)     (custom chunk_text())
[3] Embedding + Vector Store->  encode chunks, store vectors          (bge-small-en-v1.5 / sentence-transformers + Chroma)
[4] Retrieval               ->  embed query, top-k=5 cosine search    (Chroma)
[5] Generation              ->  answer from retrieved chunks          (Groq chat model)
```

User query ──▶ [4] Retrieval ──(top-5 chunks)──▶ [5] Generation ──▶ grounded answer

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
- *Tool:* Claude (in Claude Code).
- *Input:* My Documents table and Chunking Strategy section, plus one sample profile so it sees how a kprofiles template looks like
- *Expected output:* A loader that reads every `.md` in `documents/`, and a `chunk_text()` that splits each file into one chunk per member plus one group-header chunk, prepending a `Group — Member` context header to each chunk.
- *Verification:* Print the chunk count and spot-check a few chunks — confirm no chunk mixes two members and each carries its group/member header.

**Milestone 4 — Embedding and retrieval:**
- *Tool:* Claude (in Claude Code).
- *Input:* My Retrieval Approach section and the chunk objects from Milestone 3.
- *Expected output:* Code that embeds all chunks with sentence-transformers, stores them in Chroma, and a `retrieve(query)` 
- *Verification:* Run my 5 Evaluation Plan questions and inspect the retrieved chunks. Check that the expected member/group profile appears

**Milestone 5 — Generation and interface:**
- *Tool:* Claude for the code; Groq chat model at runtime for generation.
- *Input:* My Architecture diagram and a grounding requirement which is that the model must answer only from retrieved chunks and cite which group/member the answer came from.
- *Expected output:* A web interface that builds a prompt from the top-5 chunks + a system instruction enforcing grounding, calls the Groq API, and returns the answer
- *Verification:* Re-run the 5 eval questions end-to-end and compare answers to my expected answers; confirm the model refuses / says "not in the documents" when I ask something not covered.
