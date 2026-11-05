# SC01SourcesRecon — round-86 w1, seat report

Seat: SC01SourcesRecon (scout, `@m_mim`). Read-only reconnaissance.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`
Measured revision: `7a21aaa167a0c1df81e7fca9d95364433ec36997` ("round-86: exclude container fences and
backtick info strings, with a control and a mutant for each"), worktree clean except `SCORECARD.md` (modified
by another seat). Access date for every live fetch below: **2026-11-04**.

---

## Part 1 — CommonMark 0.31.2, the three rules C1's selector depends on

### 1.1 The page, fetched once and retained

```
$ curl -sS -D headers-2026-11-04.txt -o commonmark-0.31.2.html https://spec.commonmark.org/0.31.2/
HTTP/2 200
server: GitHub.com
content-type: text/html; charset=utf-8
last-modified: Sun, 01 Jun 2025 18:05:05 GMT
etag: "683c9651-7da8a"
```

- bytes: `514698`
- sha256: `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`
- Version line read from the page: `CommonMark Spec / Version 0.31.2 (2024-01-28)`
- The same sha256 is already recorded in the lane at
  `corpus/knowledge/fenced-quotation-scope.md` ("the page was re-fetched live in round 76 (2026-11-04,
  sha256 `c85f56cc…`, bytes `.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`)"), and the retained
  round-76 copy hashes identically:
  `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d  .ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`.
  So the round-86 re-open is a byte-identical re-read of a page the lane already holds, not a new upstream state.

Receipt: `receipts/commonmark-0.31.2.html`, `receipts/headers-2026-11-04.txt`.

### 1.2 The three located sentences (each quoted from the fetched bytes, each ≤ 25 words)

Every quote below was extracted from the fetched HTML, whitespace-normalised, and counted for occurrences
(`norm.count(q) == 1` for each — no duplicate occurrence anywhere on the page). Section anchors were read off the
`id=` attributes of the section headings in the same fetch.

| Rule | § anchor | Located quote (verbatim from the fetched page) | words | occ. |
|---|---|---|---|---|
| ATX heading indentation | `https://spec.commonmark.org/0.31.2/#atx-headings` (§4.2) | "The opening # character may be preceded by up to three spaces of indentation." | 14 | 1 |
| Indented code blocks | `https://spec.commonmark.org/0.31.2/#indented-code-blocks` (§4.4) | "An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation." | 18 | 1 |
| Fenced code blocks | `https://spec.commonmark.org/0.31.2/#fenced-code-blocks` (§4.5) | "A fenced code block begins with a code fence, preceded by up to three spaces of indentation." | 17 | 1 |

Two more §4.5 sentences the selector also needs (same fetch, same uniqueness check):

- "If the info string comes after a backtick fence, it may not contain any backtick characters." (16 words, occ. 1)
- "(Tildes and backticks cannot be mixed.)" (6 words, occ. 1)
- "a closing code fence of the same type as the code block began with (backticks or tildes), and with at least as
  many backticks or tildes as the opening fence" (31 words — exceeds the 25-word budget; the ≤25-word fragment
  "until a closing code fence of the same type as the code block began with (backticks or tildes)" is occ. 1)
- "If the end of the containing block (or document) is reached and no closing code fence has been found" (19 words, occ. 1)
- "Code fences (opening and closing) cannot contain internal spaces or tabs:" (11 words, occ. 1)

For the comment-shadow arm the governing rule is in §4.6, not §4.5: "Start condition: line begins with the string
<!--. End condition:  line contains the string -->." (15 words, occ. 1), anchor
`https://spec.commonmark.org/0.31.2/#html-blocks`.

### 1.3 Is one row per section right? — Yes, and the census proves it

The census's duplicate rule keys on **URL + scope**, not on URL alone. `scripts/sources-census.sh` normalises the
URL by stripping the fragment (`url_of()`: `sub(/#[^ ]*$/,"",u)`), so all four CommonMark rows collapse to the
same normalised URL `spec.commonmark.org/0.31.2`. Consequently:

- **Different scope cells → `W04`, exit still 0.** The lane already holds two rows on that URL with different
  scopes (S498 §4.5, S576 §4.2) and validates clean.
- **Identical scope cell → `E04`, exit 1.** I proved this by inserting a synthetic row copying S498's scope
  verbatim: `file E04 S901 duplicate url spec.commonmark.org/0.31.2 within scope what opens and closes a fenced
  code block: …` — exit 1. Inserting the same row with a *different* scope yielded only `W04` and exit 1-from-
  other-causes, no E04.

So one row per section is exactly right, and each new section row must carry its **own scope text**. §4.2, §4.4,
§4.5 are three different sections with three different scope texts (S576 / S579 / S578) — correct.

### 1.4 Is a duplicate-URL warning expected? — Yes, and it is already disclosed

Because the fragment is stripped, every CommonMark row after the first produces
`W04 <id> duplicate url spec.commonmark.org/0.31.2 across scopes`. Measured on the lane at the measured revision:

```
$ bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama --today 2026-11-04
kama W04 S576 duplicate url spec.commonmark.org/0.31.2 across scopes
kama W04 S578 duplicate url spec.commonmark.org/0.31.2 across scopes
kama W04 S579 duplicate url spec.commonmark.org/0.31.2 across scopes
kama ok /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
exit=0
```

W04 is a warning: it does not change exit status (the lane is `ok`, exit 0). Counts: 113 W04 at base
`3ff23da3` (one CommonMark warning), **115 W04 at the measured revision** (three CommonMark warnings — S576, S578,
S579 — plus one for S498's shared URL scope). The lane's own `corpus/lessons/round-86.md` already discloses this:
"The census reports `W04 duplicate url spec.commonmark.org/0.31.2 across scopes` because it compares URLs without
anchors — disclosed, not suppressed." **The observed behaviour matches the disclosed behaviour exactly.** No E04
appears, so the three rows coexist legally.

Receipt: `receipts/final-lane-validate.out` (115 W04, exit 0), `receipts/base-validate.out` (base).

### 1.5 Selector fidelity against the spec's own fence examples (checked, no gap found)

I checked the committed selector against the fence rules the spec states, by replaying the spec's own examples
through `rendered()` in `tools/round86-rendered-cells.py` at the measured revision. **I found no divergence, and
one advisory I first wrote was wrong — corrected here rather than left in.**

The instrument matches the spec on all fourteen cases I replayed:

| spec example | input | spec verdict | instrument agrees |
|---|---|---|---|
| 121 | ` `` ` (two ticks) | not a fence | yes |
| 122 | close with `~~~` (wrong char) | not a closer | yes |
| 124 | closer shorter than opener | not a closer | yes |
| 127 | unclosed fence | runs to EOF | yes |
| 130 | empty code block | is a fence | yes |
| 131 / 133 | fence indented 1 / 3 spaces | is a fence | yes |
| 134 | fence indented 4 spaces | is code, not a fence | yes |
| 138 | `` ``` ``` `` (internal space) | not a fence | yes |
| 139 | closer `~~~ ~~` after opener `~~~~~~` | not a closer → runs to EOF | yes |
| 142 | `` ```python `` | is a fence | yes |
| 145 | `` ``` aa ``` `` (backtick in info) | not a fence | yes |
| 146 | ``~~~ aa ``` ~~~`` (tilde info with backticks) | is a fence | yes |
| 147 | closer with an info string | not a closer | yes |

**The advisory I first drafted was my own misreading of the spec and is withdrawn.** I had written that the
instrument wrongly treats `~~~ ~~` as a fence opener. That is wrong twice over: Example 139's `~~~ ~~` is a
**closing** fence, not an opener, and as an *opener* `~~~ ~~` is legal — the fence is `~~~` and the info string is
`~~`, and "Info strings for tilde code blocks can contain backticks and tildes" (§4.5, occ. 1). The instrument's
behaviour on that input is correct. The two sentences that actually govern the two cases I had in mind are, in the
fetched bytes, "Code fences (opening and closing) cannot contain internal spaces or tabs:" (§4.5, occ. 1) and
"If the info string comes after a backtick fence, it may not contain any backtick characters." (§4.5, occ. 1) — and
the instrument implements both (Examples 138 and 145 replay as "not a fence"). The lane's HEAD commit `7a21aaa1`
("exclude container fences and backtick info strings, with a control and a mutant for each") is what closed the
backtick-info case; at the round-86 freeze commit `c07e1f90` it was not yet closed. **No advisory remains from
this seat on the fence rules.**

---

## Part 2 — `/home/vgpnk/Projects/shokuknow/merge/kama/` (read-only)

Package shape, measured: `SOURCES.append.md` holds **142 rows** (ids S330–S471) in the lane's 11-column schema;
`MERGE-REPORT.md` lists **65** proposed knowledge entries (59 new-file + 3 amendment + 3 folded-into-canonical);
`knowledge/corpus/knowledge/` holds **56** files, `amendments/corpus/knowledge/` holds **3**.

### 2.1 Which staged entry's ground fits C1, C2 or C3?

- **C2 (mutation → owning arm, summary cardinality): nothing fits.** A keyword sweep of every staged knowledge
  file and amendment for `mutant|mutation|owning arm|cardinality|EXPECTED_ARMS|selftest|pass=|fail=|summary line`
  returns **0** hits across `knowledge/` and `amendments/`. The package is entirely serving-stack material
  (vLLM/SGLang/llama.cpp health routes, served identity, KV/prefix cache, upstream reachability). No staged entry
  speaks to mutation ownership or summary/ARMS cardinality.

- **C1 (Markdown rendered identity): one candidate, but it is a different subject.** The staged
  `knowledge/corpus/knowledge/spot-check-protocol.md` carries, in its round-12 superseded passage, the lane's own
  rule: "The issue's state is read from the page's **rendered** badge, not from its embedded JSON payload … The
  script's second assertion therefore looks for the words a reader would read, and the lane's quoting rule follows:
  **quote the rendered layer**." That is the same *epistemic shape* as C1 (the value a reader sees, not a value
  buried in a shadow region) but its subject is an HTML issue page's state badge vs its embedded JSON payload —
  not a Markdown authority cell vs a fenced/comment shadow. It does not name fences, comments, indentation or
  column 0. Admitting it as C1's ground would be a category error: it is *rendered-layer reading of an HTML page*,
  and C1 is *rendered-cell identity inside a Markdown tree*.

- **C3 (source-origin corroboration): one candidate that fits on substance.**
  `knowledge/corpus/knowledge/llama-cpp-reachability-correction-amendment-2026-10-24-r7.md` (cited row **S397**)
  states the standing rule C3 is about: "**Before recording that a pin is dead, the pin must be read back out of
  the registry it is claimed to describe**", and its measurement — the registry's pin resolves on raw, blob and the
  commits API, while a one-character-mistyped sha 404s and 422s — is exactly the "a hash-consistent extract whose
  bytes differ from upstream is `mismatch`, never `verified`" distinction in the direction C3 turns. But note the
  base file `corpus/knowledge/llama-cpp-reachability-correction.md` is **absent** from both the lane and the
  package, so this amendment has no base to amend; it cannot be admitted as a standalone knowledge entry without
  also admitting the base.

**Admission: one entry, with its exact path and cited source ids — the C3 candidate.**

- exact path in the package: `/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus/knowledge/llama-cpp-reachability-correction-amendment-2026-10-24-r7.md`
- target path it would take: `corpus/knowledge/llama-cpp-reachability-correction-amendment-2026-10-24-r7.md`
- cited source ids it carries: **S397** (its own `source:` line; its `recheck:` and `coverage-map:` lines
  reference the round-7 correction artifact `lanes/kama/round7/evidence/llama-cpp-pin-spelling-correction.md`)
- it is listed in `MERGE-REPORT.md` as `corpus/knowledge/llama-cpp-reachability-correction-amendment-2026-10-24-r7.md | new-file | round7`
- grounds C3's leg (pin-origin corroboration), not C1 and not C2.

### 2.2 Blocking facts the L1 must know before adopting anything from this package

These are measured, not inferred, and they are the reason I recommend **at most one** entry and even that one
only conditionally.

**(a) The staged rows do not parse under the lane's own census.** 90 of the 142 staged rows have a field count
≠ 13 (an unescaped `|` inside the `recheck` cell — the cells carry shell pipelines like
`` 90d — re-run `curl … | grep -c …` ``). 52 of the 142 rows are field-correct but every one of them puts
**prose in the `recheck` cell** ("90d — re-run `curl …` (ran 2026-10-23)"), whereas the lane's census requires
`recheck` to be an ISO date, `^[0-9]+d$`, or a symbolic cadence (`^[A-Za-z][A-Za-z0-9 _-]*$`) — the lane's own rows
use bare `90d` / `360d` / `on-release`. Measured on a scratch tree (lane files symlinked, staged rows inserted at
the `## Paths` boundary):

```
E01 (malformed row, NF≠13) : 90    <- all from staged rows
E09 (invalid recheck)       : 52    <- all from staged rows
E11 (used-by path missing)   : 138   <- 87 artifacts of the NF≠13 rows, 51 genuine
```

**(b) Nine staged ids collide with ids the lane already uses.** The staged range is S330–S471; the lane already
holds S330, S333, S334, S335, S346, S347, S352, S353, S363. The staged versions of those ids are *near-duplicates
of the lane's own rows* (same URL, same scope cell, slightly reworded `teaches`). Repairing the field counts
surfaces `E03 duplicate id` for exactly those nine. The lane's own S352/S353 rows are already mined and cited by
`corpus/knowledge/sglang-docs-version-pinning.md`; the staged copies are older (`verified-at: 2026-10-23`) than
the lane's (`2026-10-25`). Six of the 65 target paths in the report are likewise "new file" in the report but
**already exist in the lane** with a *newer* verified-at — adopting them verbatim would regress the lane's copies:
`kv-cache-reclamation-models.md`, `prefix-cache-reuse-models.md`, `sglang-docs-version-pinning.md`,
`sglang-docs-version-pinning-amendment-2026-10-23.md`, `prefix-cache-reuse-models-amendment-2026-10-23.md`,
`served-identity-crosswalk-amendment-2026-10-24-r16.md` (lane 2026-10-25 vs staged 2026-10-23/24). The report
does not list these as conflicts; only `corpus/knowledge/spot-check-protocol.md` is listed.

**(c) The three README amendments have no staged file.** `corpus/README-amendment-2026-10-24-r12.md`, `-r13.md`,
`-r14.md` are listed in the report's table but exist nowhere in the package tree — they are the only three
remaining genuine `E11` findings after the staged knowledge files are installed. Adopting the package's
`used-by` pointers for S437/S445/S457 would dangle.

**(d) 36 staged rows cite `lanes/kama/…` own-work artifacts that do not exist in the lane repo.** The lane tracks
zero files under `lanes/` (`git ls-files | grep -c '^lanes/'` → 0). Those rows' `source:` cells name paths that
cannot be re-opened in this repository.

**(e) `corpus/knowledge/llama-cpp-reachability-correction.md` (the base the C3 candidate amends) is absent from
both the lane and the package** — only its six amendments (r6, r7, r8, r9, r10, r11) are staged.

### 2.3 Verdict for the L1

- **Assimilation: none is required by this round's claims.** The package's own ground covers serving-stack
  reachability and identity; C1's ground (Markdown fences/comments/indentation, column-0) is already carried by
  the lane's S576/S578/S579 rows plus `corpus/knowledge/fenced-quotation-scope.md`; C2's ground (mutation
  ownership, summary cardinality) has **no** counterpart anywhere in the package.
- If one entry is admitted, it is the **C3 candidate only**:
  `corpus/knowledge/llama-cpp-reachability-correction-amendment-2026-10-24-r7.md`, cited source id **S397** — and
  only together with its missing base file `corpus/knowledge/llama-cpp-reachability-correction.md`, which must
  then also be admitted (it is in the package only as the r6/r7–r11 amendment family; the base itself is absent).
- Nothing from this package should be appended to `corpus/SOURCES.md` as-is: 90 rows are malformed, 52 have an
  illegal `recheck` value, 9 duplicate ids already exist in the lane, 6 target paths would regress newer lane
  files, and 3 have no staged file.

---

## Commands actually run (read-only), with true exit codes

| Command | exit |
|---|---|
| `curl -sS -L -o commonmark-0.31.2.html https://spec.commonmark.org/0.31.2/` | 0 (HTTP 200) |
| `curl -sS -D headers-2026-11-04.txt -o /dev/null https://spec.commonmark.org/0.31.2/` | 0 (HTTP 200) |
| `bash scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama --today 2026-11-04` | **0** (115 W04, 1 W01) |
| `bash scripts/sources-census.sh validate --file <base 3ff23da3 SOURCES.md> --today 2026-11-04` | 1 (E11 ×664, path artifact of `--file` mode) |
| `bash scripts/sources-census.sh validate --file <scratch simtree baseline> --today 2026-11-04` | **0** (115 W04) |
| `bash scripts/sources-census.sh validate --file <scratch simtree + staged rows> --today 2026-11-04` | **1** (E01 ×90, E09 ×52, E11 ×138) |
| `bash scripts/sources-census.sh validate --file <scratch simtree + staged rows + staged knowledge files> --today 2026-11-04` | **1** (E01 ×90, E09 ×52, E11 ×90) |
| `git -C … show/ls-files/log/status/rev-parse` (read-only) | 0 |

All census runs used `--today 2026-11-04`. Scratch tree: `/fast/scratch/hyaku/kama-r86/SC01SourcesRecon/` (a
symlink farm over the lane's own files plus copies of `corpus/knowledge`, `corpus/lessons`, `corpus/anchors`);
**no lane file was modified**, no git mutation was run anywhere, and the scratch tree is removed on exit.

## Remaining unknowns

1. Whether the C3 candidate's missing base file exists in some other package (it is not in this one) — I could not
   locate it, so I cannot say whether the base is recoverable.
2. The package's `used-by` pointers for S437/S445/S457 name three README amendments that exist in no tree I can
   read; whether the operator holds them elsewhere is unknown to me.
3. The nine staged rows whose ids already exist in the lane (S330, S333, S334, S335, S346, S347, S352, S353,
   S363) are *near*-duplicates of the lane's own rows, not identical copies — the lane's `teaches` cells are
   reworded and slightly longer. Whether the operator intends the staged wording to supersede the lane's (which
   would need a `supersedes S###` marker to satisfy E04) or intends the lane's wording to stand is an authoring
   decision I cannot make from the sources.

No selector-fidelity unknown remains from this seat: §1.5 records fourteen spec examples replayed against the
committed instrument with no divergence.
