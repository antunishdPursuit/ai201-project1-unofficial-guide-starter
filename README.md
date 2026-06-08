# The Unofficial Guide — Project 1

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

The history of K-pop idol groups across generations such as group formation, member lineups and positions, debut eras, agencies, fandoms, lineup changes (departures, disbandments, reunions), and how group concepts shifted over time. The documents span first-generation groups (H.O.T., S.E.S.), second generation (BIGBANG, Girls' Generation, SHINee, 2NE1), third generation (EXO, BTS, BLACKPINK), and fourth generation (aespa).

This knowledge is valuable but hard to find through official channels because agencies present only the current view of a group. Official pages just focus on the active roster and upcoming releases. That historical and cross-group context lives in fan-maintained profile sites, forums, and community wikis, where it's accurate but scattered across many separate pages.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

All ten documents are member-profile pages from the fan-maintained site **kprofiles.com**, saved locally as Markdown in `documents/`. Together they span all four idol generations, both boy and girl groups, and the three major agencies (SM, YG, BigHit/HYBE).

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | H.O.T. Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/h-o-t-members-profile/ — `documents/H.O.T. Members Profile.md` |
| 2 | S.E.S Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/s-e-s-members-profile/ — `documents/S.E.S Members Profile.md` |
| 3 | BIGBANG Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/big-bang-members-profile — `documents/BIGBANG Members Profile.md` |
| 4 | Girls' Generation / SNSD Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/girls-generation-snsd-members-profile — `documents/Girls' Generation SNSD Members Profile.md` |
| 5 | SHINee Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/shinee-members-profile — `documents/SHINee Members Profile.md` |
| 6 | 2NE1 Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/2ne1-members-profile/ — `documents/2NE1 Members Profile.md` |
| 7 | EXO Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/exo-members-profile — `documents/EXO Members Profile.md` |
| 8 | BTS Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/bts-bangtan-boys-members-profile/ — `documents/BTS Members Profile.md` |
| 9 | BLACKPINK Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/black-pink-members-profile/ — `documents/BLACKPINK Members Profile.md` |
| 10 | aespa Members Profile | Fan profile (kprofiles.com) | https://kprofiles.com/aespa-members-profile/ — `documents/aespa Members Profile.md` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** One chunk per member and one group-header chunk per document. Any member whose chunk would exceed **500 tokens** (a safety margin under bge-small's 512-token limit) is packed into sequential sub-chunks on line boundaries, each re-prefixed with a `<Group> — <Member>` context header. Final token distribution: **min 33, median 396, max 500.**

**Why this fits the documents:** Every profile follows the same template — a group header followed by a repeating block per member — and a member's block is a self-contained semantic unit. Splitting on member boundaries means a question like "Who is aespa's maknae?" maps cleanly to a single chunk instead of being diluted across a fixed-size cut or split mid-member.

**Overlap:** None because splits happen on natural member/line boundaries and every (sub-)chunk repeats the `<Group> — <Member>` header.

**Preprocessing before chunking:** Removed the site-header block, image-caption lines, "Show more … fun facts" links, and empty "Official Logo:" placeholders.

**Final chunk count:** **88 chunks** — 58 members (across 78 member-chunks, since 19 oversized members were split) + 10 group-header chunks.

---

## Sample Chunks

<!-- At least 5 labeled sample chunks, each with its source document name. -->

Each chunk is prefixed with a `<Group> — <Member>` line so it stays self-contained. Excerpts shown; token counts from the bge-small tokenizer.

**1. Group-header chunk — source: `2NE1 Members Profile.md`** (294 tokens)
```
2NE1 — Group Info
# 2NE1 Members Profile
Source URL: https://kprofiles.com/2ne1-members-profile/
2NE1 (투애니원) is a 4-member South Korean girl group under YG Entertainment, consisting of CL,
Dara, Park Bom, and Minzy. They debuted on May 17, 2009 ... Minzy left the band in April 2016.
On November 25, 2016, YG announced that 2NE1 disbanded. ...
2NE1 Official Fandom Name: BlackJacks   |   Official Colors: Hot Pink   |   SNS: @2ne1xxi ...
```

**2. Member chunk (whole) — source: `2NE1 Members Profile.md`** (405 tokens)
```
2NE1 — Minzy
Minzy
Stage name: Minzy (민지)  Birth name: Gong Minji (공민지)
Position: Main Dancer, Lead Vocalist, Lead Rapper, Maknae  ...
Minzy Facts:
– She's the granddaughter of famous traditional dancer Gong Ok-jin.
– YGE announced Minzy is leaving the group on April 5, 2016 ...
– In October 2020 Minzy launched her own agency, MZ Entertainment. ...
```

**3. Member chunk (split, part 1/2) — source: `aespa Members Profile.md`** (490 tokens)
```
aespa — NingNing
NingNing
Stage Name: NingNing (닝닝)  ...  Position(s): Main Vocalist, Maknae  Nationality: Chinese
Ningning Facts:
– She was born in Harbin, China.  – Her hobby is cooking.  ...
```

**4. Member chunk (split, part 1/3) — source: `BTS Members Profile.md`** (496 tokens)
```
BTS — Jung Kook
Jung Kook
Stage Name: Jung Kook / Jungkook (정국)  Position(s): Main Vocalist, Lead Dancer, ..., Maknae
Jung Kook Facts:
– He was born in Busan, South Korea.  – Before joining the group he was a handball player. ...
```

**5. Member chunk (split, part 2/3) — source: `BTS Members Profile.md`** (396 tokens)
```
BTS — Jung Kook
Note 2: The listed heights are taken from BTS's official site ... Jungkook confirmed his height
is 177 cm ("Stationhead Radio" Oct 1, 2023). ...
For reference on MBTI types: E = Extroverted, I = Introverted ...
```
*(This last chunk shows a known limitation: trailing document-level Notes attach to the last member of a document — see Failure Case Analysis.)*

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice. -->

**Model used:** `BAAI/bge-small-en-v1.5` via `sentence-transformers`, running locally. Vectors are normalized and stored in a persistent **ChromaDB** collection configured with `hnsw:space = cosine`. I chose bge-small over the common default `all-MiniLM-L6-v2` specifically because MiniLM truncates at **256 tokens** whereas bge-small's 512-token window fits a full member chunk and matches or beats MiniLM on retrieval benchmarks while still running free and offline.

**Production tradeoff reflection:** If cost weren't a constraint, the biggest factor for this domain is **multilingual support**. The sources mix Korean, Japanese, and Chinese names and stage names (e.g. "Yu Ji-min" / "유지민" / "Karina"), and an English-only model can miss a query phrased with a different script or romanization. A multilingual model (e.g. `bge-m3` or `multilingual-e5-large`) or a high-accuracy API model (OpenAI `text-embedding-3-large`, Voyage) would improve cross-script recall and offers longer context to embed an entire group as one chunk instead of per-member. 

---

## Grounded Generation

<!-- Explain how your system enforces grounding. -->

Generation uses **Groq's `llama-3.3-70b-versatile`** at `temperature=0` (`generate.py`). Grounding is enforced two ways:

**System prompt grounding instruction:** The model is given the retrieved chunks as labeled context and a system prompt with hard rules:
```
Answer the user's question using ONLY the information in the provided context documents.
1. Do not use any outside or prior knowledge, even if you are confident.
2. If the context does not contain the answer, reply exactly:
   "I don't have enough information on that."
3. Do not guess or fill gaps. Only state facts present in the context.
4. Be concise and factual.
```
Each retrieved chunk is wrapped as `[Document N — <Group> / <Member> (source: <file>)]` so the model can see provenance, and the user question is appended after the context block. Asked an out-of-scope question and the system returns the exact refusal string rather than hallucinating.

**How source attribution is surfaced in the response:** Attribution is **programmatic, not model-dependent**. After generation, `ask()` collects the unique source filenames of the retrieved chunks and returns them as a `sources` list so it never relies on the model remembering to cite. When the model returns the "not enough information" refusal, the source list is suppressed so we don't attribute a non-answer.

---

## Retrieval Test Results

<!-- At least 3 queries with top returned chunks; for at least 2, why the chunks are relevant. -->

Top results from ChromaDB (cosine distance; lower = closer). bge-small + top-k=5.

**Query A — "What does aespa's name come from?"**
| rank | chunk | distance |
|---|---|---|
| 1 | aespa — Group Info | **0.234** |
| 2 | aespa — Giselle | 0.379 |
| 3 | aespa — Karina | 0.397 |

*Why relevant:* The group-header chunk contains the exact explanation ("æ" from "Avatar X Experience" + "aspect") and ranks first by a wide margin; the other hits are aespa member chunks, i.e. correct group, adjacent context.

**Query B — "When did 2NE1 disband and which member left before that?"**
| rank | chunk | distance |
|---|---|---|
| 1 | 2NE1 — Group Info | **0.238** |
| 2 | BIGBANG — Group Info | 0.401 |
| 3 | H.O.T. — Group Info | 0.401 |

*Why relevant:* The 2NE1 group header contains both facts (Minzy left April 2016; disbanded Nov 25 2016) and ranks first. Ranks 2–3 are other groups' headers — semantically near because they also describe debut/disbandment timelines, but clearly farther in distance.

**Query C — "Which girl groups are under YG Entertainment?"**
| rank | chunk | distance |
|---|---|---|
| 1 | 2NE1 — Group Info | 0.371 |
| 2 | BLACKPINK — Group Info | 0.380 |
| 3 | Girls' Generation SNSD — Group Info | 0.399 |
| 4 | S.E.S — Group Info | 0.407 |

The two correct YG groups rank 1–2, but SM groups (SNSD, S.E.S) appear at 3–4 — see Failure Case Analysis.

---

## Example Responses

<!-- At least 2 responses with source attribution visible, plus one out-of-scope refusal. -->

**Example 1 — "What individual agencies did the BLACKPINK members set up?"**
> Jennie — ODD ATELIER; Lisa — LLOUD; Jisoo — BLISSOO; Rosé — signed with THEBLACKLABEL.
>
> **Retrieved from:** • BLACKPINK Members Profile.md

**Example 2 — "When did 2NE1 disband and which member left the group before that?"**
> 2NE1 disbanded on November 25, 2016. Before that, Minzy left the band in April 2016.
>
> **Retrieved from:** • 2NE1 Members Profile.md • BIGBANG Members Profile.md • H.O.T. Members Profile.md • EXO Members Profile.md

**Example 3 (out-of-scope) — "Who is the leader of TWICE?"** *(TWICE is not in the corpus)*
> I don't have enough information on that.
>
> *(no sources listed)*

---

## Query Interface

<!-- Describe the input and output fields, and a sample interaction transcript. -->

A **Gradio** web app (`python app.py` → http://localhost:7860):
- **Input:** a "Your question" text box (Enter or the **Ask** button submits). A left sidebar lists clickable example questions.
- **Output:** an **Answer** box (the grounded response) and a **Retrieved from** box (the source documents). The page has a centered title and a TWICE background image.

**Sample transcript:**
```
Your question:  Who is the maknae of aespa and what is her nationality?

Answer:         The maknae of aespa is NingNing, and her nationality is Chinese.

Retrieved from: • aespa Members Profile.md
                • BLACKPINK Members Profile.md
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Who is the maknae of aespa and what is her nationality? | NingNing; Chinese | "The maknae of aespa is NingNing, and her nationality is Chinese." | Partially relevant | Accurate |
| 2 | When did S.E.S disband? | December 2002 | "S.E.S officially disbanded in December 2002." | Relevant | Accurate |
| 3 | When did 2NE1 disband and which member left before that? | Minzy left Apr 2016; disbanded Nov 25 2016 | "2NE1 disbanded on November 25, 2016. Before that, Minzy left the band in April 2016." | Relevant | Accurate |
| 4 | What individual agencies did the BLACKPINK members set up? | Jennie→ODD ATELIER, Lisa→LLOUD, Jisoo→BLISSOO, Rosé→THEBLACKLABEL | "According to the context documents, the individual agencies set up by the BLACKPINK members are: 1. Jennie - ODD ATELIER 2. Lisa - LLOUD 3. Jisoo - BLISSOO 4. Rosé - (signed with THEBLACKLABEL, but did not set up her own agency)" | Relevant  | Accurate |
| 5 | Which girl groups are under YG Entertainment? | 2NE1 and BLACKPINK | "According to the provided context documents, the girl groups under YG Entertainment are: 1. 2NE1 2. BLACKPINK" | Partially relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected. -->

**Question that failed (retrieval, not final answer):** "Which girl groups are under YG Entertainment?" (Q5)

**What the system returned:** The final answer was correct (2NE1, BLACKPINK), but the **retrieval** step returned a mixed set: the two YG group-header chunks ranked 1–2, but two **SM** groups — Girls' Generation (0.399) and S.E.S (0.407) — ranked 3–4, only ~0.03 behind the correct ones.

**Root cause (tied to a specific pipeline stage):** This is an **embedding/retrieval** limitation. Every group-header chunk is dominated by shared topic vocabulary ("South Korean girl group", "Entertainment"), and the agency name *YG* vs *SM* is a tiny part of a ~300-token embedding. Dense cosine similarity captures overall topical closeness, so all "girl group + agency" headers cluster together and the agency distinction barely moves the distance. 

**What I would change to fix it:** Add an `agency` field to chunk metadata (parsed from "under YG Entertainment" in the group description) and apply a ChromaDB `where={"agency": "YG Entertainment"}` filter when the query names an agency thereby turning a fuzzy semantic match into an exact metadata filter. A lighter-weight alternative is enriching the chunk header with the discriminating attribute (e.g. `aespa — Group Info (SM Entertainment girl group)`) so the agency carries more embedding weight. In this case the grounded generation step already compensated and produced the right answer, but retrieval precision is the correct place to fix it.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation. Personalize before submitting. -->

**One way the spec helped you during implementation:** Deciding the chunking strategy, embedding model, and top-k in `planning.md` *before* writing code made the implementation targeted instead of exploratory. Because the plan already specified "one chunk per member" and `bge-small-en-v1.5`, the chunker and the embedding setup could be written directly from those choices, and the planning note about MiniLM's 256-token limit is exactly what flagged the truncation risk that drove the final chunking design.

**One way your implementation diverged from the spec, and why:** The plan called for whole per-member chunks of ~300–450 tokens with ~50-token overlap. In practice, measuring real token counts with the bge tokenizer showed 16 of 58 members exceeded the 512-token limit, which would have silently truncated their facts at embed time. So the implementation diverged to **token-aware packing with no overlap**: members under the cap stay whole, oversized members are split into header-repeating sub-chunks. The "one chunk per member" ideal was kept for the majority and only relaxed where the model's context window forced it.

---

## AI Usage

<!-- Describe at least 2 specific instances. Personalize before submitting. -->

**Instance 1 — Implementing the chunker**

- *What I gave the AI:* My Chunking Strategy section from `planning.md` plus a full sample document so it could see the real kprofiles structure .
- *What it produced:* A `chunk_text()` that detected member boundaries using the `Stage Name:` field.
- *What I changed or overrode:* That approach missed irregular members with no `Stage Name:` line and falsely flagged the group-description paragraph as a member. I directed it to switch to a structural rule (a short, colon-free name line following a section break, confirmed by a nearby profile field) with a length guard, and added token-aware packing so no chunk exceeds bge-small's 512-token limit.

**Instance 2 — Embedding-model choice and the truncation discovery**

- *What I gave the AI:* My Retrieval Approach section and a question about whether my chunk sizes fit the embedding model.
- *What it produced:* An analysis showing `all-MiniLM-L6-v2` truncates at 256 tokens, then exact per-chunk token counts using the real bge tokenizer (16 chunks over 512, max ~1001).
- *What I changed or overrode:* The measured data changed my decision from "keep whole members and accept truncation" to token-aware packing, and confirmed the switch to `bge-small-en-v1.5` (512-token window).