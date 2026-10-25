# ReviewSGLangClaims — claim-vs-source check for S333 / S334 / S335

Seat: `L1Kama37.IndependentTarsier` (round 37, w1). Read-only review. The only file written is this
report. No corpus, registry, knowledge, jj or git state was touched; no campaign tool ran.

## 0. Method and what "supports" means here

- Sources checked against **saved bytes from this wave's authorized reopens**, not against prose:
  - `.ufo/waves/round-37/w1/out/FetchS333/page.html` — 296606 B, sha256 `0cf0de212514080ce4ce9cf6c1261c8399e00bfe61e54dc3d230a7752073825f`, HTTP 200 (receipt `FetchS333.md`)
  - `.ufo/waves/round-37/w1/out/FetchS334/sglang-session-radix-cache.html` — 277182 B, sha256 `69d21ab9a22a1ffdb114cf9a4ef7e53b539ce6d8670b0eeef659b03ecd828258`, HTTP 200 (`FetchS334.md`)
  - `.ufo/waves/round-37/w1/out/FetchS335/scratch/html-2312.07104v1.html` — 214951 B, sha256 `ea21c80c9991952494fe999449d5eef3f91fa36bb75b1af2ae42db12a3b494df`, HTTP 200; companion `/abs/2312.07104v1` — 43414 B, sha256 `5d2d5eb082bb73d89f1f751b8ee012388c064494e1a04a98bcd3d182f32fdc0b` (`FetchS335.md`)
  - `.ufo/waves/round-37/w1/out/FetchS346/06-reasoning-engine.md` — 36737 B, 587 lines, sha256 `2ed9f7acd96730f97e0bf0066c991f8bb683f40c5bc65f3f1d4ea3f42995ed8c` (`FetchS346.md`)
- Staged rows under review: `/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md` lines 10–12 (S333/S334/S335) and line 23 (S346), mirrored byte-identically in `.ufo/waves/round-37/w1/out/L1Kama37.MinimumPartridge/mirror-SOURCES.md:218-221` and `rows7.txt`.
- Staged entry under review: `corpus/knowledge/kv-cache-reclamation-models.md` in the read-only package (its frontmatter `source:` lines are the entry's own anchor claims).
- `lsp` device is **not mounted** in this seat (`xd://lsp` → "No such tool"; mounted list has no `lsp`), and the artifacts are Markdown/HTML corpus, so no language server would answer them. Caller/definition checks were therefore done as byte-exact substring verification plus heading/`id` enumeration on the saved bytes. Recorded as a method limit, not as semantic proof.
- Presence counts below are case-insensitive `re.findall` counts over the whole saved file, so rendered copy **and** the embedded RSC payload both count (the doubling on the two doc pages is that duplication, not two statements).
- Runtime/identity checks from the standing role (canonical runtime, same-identity rerouting, `resume_continuity_v1`) do not apply: this unit has no serving process, no resume path and no mutation surface.

## 1. The claim set and its required carrier

Each claim is quoted as the entry writes it. "Row quote" = the quoted cell of that S-row; "page bytes" = the saved reopen.

| # | Claim (entry wording) | Must be carried by | Row quote carries it? | Page bytes carry it? | Verdict |
|---|---|---|---|---|---|
| C1 | "The KV cache is a radix tree." | S333 or S335 (both say so) | S333 quote: **no**; S335 quote: **no** | yes, both (`S335` §5.1: "we utilize a radix tree to manage a mapping"; `S333` is a page about that radix cache) | **SUPPORTED** |
| C2 | "Only *evictable leaves* are candidates — present, unlocked, and not shadowed by a child still holding KV" | **S333 only** (S334 has 0 hits for `evictable`; S335 says only "recursively evicts leaf nodes") | **no** — S333's quote cell is the score sentence; the leaf rule is only in `teaches` | **yes, byte-exact** at `page.html:448`: "Eviction only ever considers **evictable leaves**: nodes whose KV is present, unlocked (no in-flight request holds them), and not shadowed by a child that still holds KV. The root is never evictable." | **SUPPORTED by bytes, not by the row quote** |
| C3 | "'the policy scores each candidate and the lowest score is evicted first'" | **S333 only** (`lowest score`: 0 hits in S334, S335, S346) | **yes, byte-exact** (12 words) | **yes**, `page.html:449`, rendered with `lowest score is evicted first` in `<strong>` | **SUPPORTED** |
| C4 | "with LRU as the tie-break" | **S333 only** | **no** — the quote cell stops at the score sentence | **yes**, `page.html:452` under `#available-policies` (`page.html:451`): "Select one with `--radix-eviction-policy`. All of them fall back to least-recently-used order within a tie." | **SUPPORTED by bytes, not by the row quote**; see L1 for the compressed default |
| C5 | "in continuous batching a node used by the running batch cannot be evicted, so 'a node is evictable if its reference counter is zero'" | **S335 only** — `reference counter` is **0×** in the S333 page (296606 B) and 0× in S334; 2× in the paper HTML; 0× in the paper abs page | **yes, byte-exact** (10 words) | **yes**: `html-2312.07104v1.html` byte 80972, inside `<p id="S5.SS1.p2.1">` (opens 80509) under `5.1 RadixAttention`; preceded verbatim by "In the continuous batching setting, we cannot evict nodes that are being used by the currently running batch. Therefore, each node maintains a reference counter indicating how many running requests are using it." | **SUPPORTED**, with the anchor defect M1 |
| C6 | "Session references are soft protection, not memory pins … Referenced KV can still be evicted when reclaiming unreferenced KV is insufficient" | **S334 only** (`soft protection` 0× in S333/S335/S346) | **partly** — the cell quotes only the first sentence; the eviction sentence is in `teaches` | **yes, the full 20-word pair is byte-exact** at `sglang-session-radix-cache.html:447` | **SUPPORTED by bytes; row quote is short by one sentence** |
| C7 | "The `session_id` labels cache references only; it neither appends nor reconstructs conversation context, so every request must still carry its full intended prompt." | **S334 only** (`session_id` 0× in S333/S335/S346) | **no** (only in `teaches`) | **yes, byte-exact**: "The ID labels cache references only; it does not append or reconstruct conversation context, so each request must still contain the intended prompt." — under the H2 `Pass and close the session` | **SUPPORTED by bytes; not in the row quote** |

No claim in C1–C7 is false against the reopened bytes. The entry's paraphrases preserve the sources'
modality: all three are documents/papers describing intended behaviour, and the entry's own
"What this entry does not establish" says no host observation was made, which matches (nothing in the
wave ran a server).

## 2. Findings, by severity

### H1 — S333's cited section does not exist on the page (entry frontmatter and row anchor)

The entry's `source: S333` line and the S333 row's anchor cell both say **`§Eviction candidates`**.
The served page has exactly four content H2s, by `id`:

```
how-eviction-picks-a-victim · available-policies · tuning-a-policy · which-policy-to-pick
```

`Eviction candidates` occurs **0 times in 296606 bytes**; the quoted score sentence sits under
`#how-eviction-picks-a-victim` (`page.html:447-449`). This is the KQ45 failure shape — the quote sits
at a location other than the one its anchor names — and KQ6's "names … the documented revision and
section". It does not make C2/C3 false; it makes the pointer wrong, so a reader who greps the anchor
cannot find the quote.

Fix: anchor → `§How eviction picks a victim` (score sentence) with the leaf sentence added to the
quote cell, or `§How eviction picks a victim; §Available policies` if the tie-break is also cited.

### H2 — S334's cited section does not exist either

The entry and the S334 row both say **`§Session references`**. The page has three content H2s only
(`enable-the-cache · pass-and-close-the-session · eviction-behavior`); `Session references` occurs
only as words of the quoted sentence itself (2×, rendered + payload), never as a heading. The
20-word soft-protection pair is the **untitled lead paragraph directly under the `<h1>`, before
`#enable-the-cache`** (`:447`), which the page's own TOC does not list. The `session_id` sentence
(C7) is under `#pass-and-close-the-session`.

Fix: anchor → "lead paragraph under `#page-title`, before `#enable-the-cache`" for C6, and
`§Pass and close the session` for C7 — not a section name that cannot be reached.

### M1 — S335's anchor claims the abs page carries the quote; it does not

The row anchor reads `§RadixAttention — "A node is evictable if its reference counter is zero.";
arXiv:2312.07104 (abs page) and arXiv:2312.07104v1 (HTML full text)`. Measured on this wave's two
reopens: the **abs page has 0 occurrences** of `reference counter` (43414 B, abstract only); the
sentence exists only in the **v1 HTML full text** at byte 80972. Also, the row's `source` URL
`https://arxiv.org/abs/2312.07104` (version-less, i.e. the *latest* version) was **not** fetched —
only `…/abs/2312.07104v1` was — so nothing in this wave says what v2's abs page or full text carry.

Fix: restrict the anchor to "arXiv:2312.07104v1 (HTML full text), §5.1 RadixAttention,
`<p id="S5.SS1.p2.1">`", or add the v2 reopen.

### M2 — the two docs rows assert commit pins that this wave did not verify and the served bytes do not contain

S333 pins `radix_eviction_policy.mdx @ 77091cea68d0701d6cc71edfb45f2815c4f8d791 (2026-09-29)`,
S334 pins `session_radix_cache.mdx @ d34f7b2326a10cb5f3ba8ec95efb31c761237750 (2026-09-22)`.
Neither 40-hex id nor either date occurs in the corresponding saved page (`0` occurrences each).
Both pages instead carry the same build stamp `"lastModified":"2026-10-24T12:16:03.909Z"` and
`"originalFileLocation":"docs/advanced_features/…mdx"`, plus the identical 40-hex
`a7eeabc39cfb37d74ea3d82eac674d0e1851b1cb` (a Mintlify deployment id present on both pages, not a
source commit).

So the pins rest on an earlier round's file read, not on anything re-opened here. Two consequences:
(a) per KQ45, a pin the check cannot reach must record its access route and be marked
unverifiable-by-fetch — currently it is asserted flatly; (b) the served page is the only byte identity
this wave holds, and H1/H2 show its section names differ from the row labels, which is exactly the
drift a commit pin is supposed to settle. I did **not** fetch the raw `.mdx` at those commits: those
URLs are in the row's anchor, not in my item's authorized URL set.

Fix: either reopen `https://raw.githubusercontent.com/sgl-project/sglang/<commit>/docs/docs/advanced_features/<file>.mdx`
and record that route in the anchor cell, or replace the commit pin with the served-byte sha256 and
mark the section labels as served-page labels.

### M3 — S335's recheck command cannot fail

`grep -c '2312.07104'` on `https://arxiv.org/abs/2312.07104` is satisfied by every arXiv abstract page
containing its own identifier; it says nothing about the quoted sentence, and it passed against the
**v1** abs page (0 hits for the quote) as readily as it would against v2. Every sibling row's recheck
greps its own quoted phrase (S333: `lowest score is evicted first`; S334: `soft protection, not memory
pins`). Fix: `grep -c 'reference counter is zero'` over `https://arxiv.org/html/2312.07104v1`.

### M4 — the entry's recheck line points at a file that does not exist in the lane

Entry frontmatter: `recheck: 90d — re-run the row recheck commands for S330, S333, S334, S335 and
S346 in SOURCES-PROPOSED.md (ran 2026-10-23)`. `find . -name SOURCES-PROPOSED.md` in
`/home/vgpnk/Projects/shokunin/kama-shokunin` returns **nothing**; the five rows live only in the
read-only package (`SOURCES.append.md`) and the L1's mirror. A reader cannot execute the stated
recheck. Fix: name the real target (`corpus/SOURCES.md` after the append) or drop the reference.

### L1 — "LRU as the tie-break" compresses away that LRU is the default policy

`page.html` §Available policies labels `lru` as **`(default)`** and then says all selectable policies
"fall back to least-recently-used order within a tie". The entry keeps only the tie-break half, which
is true, but a reader can take away that a score-based policy is primary and LRU only resolves
equality. For an operator question ("what does this box do out of the box") the missing default is
the decision-relevant half. No false claim; recommend one clause: "`lru` is the default policy, and
every policy falls back to LRU within a tie".

### L2 — two source sentences the entry drops

- S333: "The root is never evictable." (same paragraph as the leaf rule). Not needed for the model,
  but it is the page's own completeness condition.
- S333: "A policy only scores. It does not decide how much to free, and it cannot pin KV in memory — a
  node protected by the policy is still evicted if reclaiming everything else is not enough." This is
  the strongest docs-side support for the entry's "not a memory pin" section, and it is closer to the
  entry's thesis than S334's session-specific sentence. S334 carries the claim independently, so
  nothing is unsupported; the omission costs the argument, not its validity.

## 3. Claims resting only on the community source S346

**None of C1–C7 rests on S346** — each of the six behaviour claims has an A-tier carrier among
S333/S334/S335, and the row-level words for them (`evictable`, `lowest score`, `soft protection`,
`reference counter`, `session_id`) do not occur in S346 at all (counts: 0 each).

Two things in the entry do rest on S346 alone, and both are written as S346's content rather than as
upstream fact:

1. **Implementation paths and class names** — `mem_cache/radix_cache.py` → `RadixCache`,
   `managers/schedule_policy.py` → `SchedulePolicy`. Only S346 (tier B) names them; S333/S334/S335
   name no files, and `FetchS346.md` records "its file-path and class claims are assertions *about*
   SGLang, verified here only as text present in this document" and "Any lane use as a path/class
   claim needs a primary reopen of the SGLang tree" — which this wave did not do.
2. **"vLLM's flat hash-chain prefix cache"** — S346 line 319 (`hash 链式(扁平)` vs
   `RadixCache 基数树(层级共享)`). Within *this* entry's citation set nothing else carries the vLLM
   side: S330 is a scheduling/batching page and says nothing about prefix-cache structure, and S347
   (hash-keyed block pool) is cited in the sibling entry, not here.

The entry's grammar does scope both to the source ("it names the concrete implementation files … and
contrasts …"), and it hedges in "the Chinese file map may drift from the upstream source at any
release", so this is a scope note rather than an overclaim. It becomes an overclaim the moment the
paths or the "flat hash-chain" phrasing is restated outside that sentence; if the lane wants either
as a fact, it needs the SGLang tree at a pinned revision (and S347 for the vLLM side).

The `LPM` wording is S346's; S335 §5.2 says the same thing under the name **`LMP`** ("LMP, or longest
matching prefix, is the default policy"). The entry does not assert LPM as behaviour, so there is no
conflict — but a future sentence that mixes the two spellings should name which source it follows.

## 4. Contract-relevant state (frozen C2 dependency, read-only observation)

- `corpus/SOURCES.md` **at the working tip**: 462 lines, highest S-row `S329`; it contains **no row**
  for S330, S333, S334, S335, S346, S347 or S363 (`grep '^| S3[2-6][0-9] '` → only S324/S327/S328/S329).
- At base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`: the same 462-line file with the same S324/S327/
  S328/S329 rows and **no S330+**, so none of the cited ids collides with a base row — the coverage
  predicate's "absent at base" holds for the ids themselves.
- Therefore every S-id the three candidate knowledge files cite (`kv-cache-reclamation-models.md`:
  S330/S333/S334/S335/S346; `prefix-cache-reuse-models.md`: S347; `…-amendment-2026-10-23.md`: S363)
  is currently a **draft in the mirror, not a row in SOURCES.md**. C2's "present in corpus/SOURCES.md
  at the tip" is unsatisfied until the L1 lands those rows in the same tip as the knowledge files.

## 5. Residual risk and verification gaps

- **Wrong anchors propagate.** H1/H2 sit in the entry frontmatter as well as the row cells, so a
  copy-forward of the entry repeats them. They are label defects, not content defects: C2–C7 all
  survive on the page bytes.
- **Served page vs pinned revision is unresolved.** H1/H2/M2 are only reconcilable by opening the
  `.mdx` at `77091ce` / `d34f7b23`; I did not, because those URLs are outside this seat's authorized
  URL set. Until that fetch exists, "the section was named differently at the pinned commit" is an
  open possibility and must not be asserted as fact either way.
- **Paper version surface partially covered.** Only v1 (`/abs/…v1`, `/html/…v1`) was reopened. The
  version-less `source` URL in the S335 row resolves to the latest version; v2's text was not read,
  and the row's scope ("historical, revision-free by arXiv id") is only true for the sentence if v2
  still carries it.
- **S346 commit date unverified.** The entry writes `(2026-06-16)` beside commit `35b83cee`; the
  wave's fetch read the file bytes at that commit, not the commit object, so the date is not
  corroborated here.
- **No semantic tooling.** No LSP server was mounted, so "does this sentence appear in the cited
  section" is established by heading enumeration plus byte-exact substring counts on the saved
  bytes, and by no other means.
- **Not done by design:** no campaign tool, no counting command (`round37-statement-audit.py`,
  `round37-coverage-audit.py`), no corpus/row/lesson edit, no fleet-repo write, no commit.

## 6. One-line disposition

The six SGLang claims are source-supported (C2/C4/C6/C7 by page bytes only, C3 and C5 by the row
quotes too); the defects are pointer-level — two invented section names, one abs-page attribution,
two unverified commit pins, one vacuous recheck, one dangling `SOURCES-PROPOSED.md` reference — plus
two S346-only items that the entry already scopes to S346.
