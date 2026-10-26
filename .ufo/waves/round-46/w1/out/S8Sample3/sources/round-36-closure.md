# kama round 36 — verifier spot-check

author: hyaku closure (non-author integrator, @m_flash)
date: 2026-10-25
round: 36
reviewer role: non-author; this session did not author the round, its lesson, its tools or its
report, and wrote only this file.
base: e5a8ececf3d60fd53b36bb74299693a29e8f74b6
claim-measurement commit: 2e8beda5b2a2dcc62d6782838ee6e47cda04df55
lane tip reviewed: 6a4afdfe48b0b54239d127761d21a5cf21b5b0ea
report: .ufo/reports/round-36/kama.md (fleet repo)

## 1. Step-1 conformance

Verified:

- **Report identity and ancestry.** `git log --format='%an %H' -- .ufo/reports/round-36/kama.md`
  prints `kama-shokunin 428a0560daa851bd16913dd2eb98db61d2f76b2a` (report and L0) and
  `kama-shokunin 2969810803281779373de6e82309e7173a6e605c` (erratum). Both are ancestors of
  fleet master `04411e88`; the report path is clean in the worktree. Not a marker report: it
  carries Work performed, Landed changes, Before → after measurements, Sources & frontier,
  Trend verdicts and a `## SHONEN` heading with four box lines — one per box of the lane's
  `SHONEN.md` (`grep -cE '^- \[' SHONEN.md` = 4, report box lines = 4).
- **Prompt contract.** `.ufo/prompts/kama-round-36.md` carries the template contract sections
  (`Required sections, in order`, `Marker rule`) and the hyaku §6 addendum verbatim.
- **Cited lane commits exist and are ancestors of the branch tip.** For
  `9014843cb7de8fbe87a97954c13832b67d55f046` (freeze), `2e8beda5…` (claim work) and
  `6a4afdfe…` (SCORECARD/LOG/w3), `git merge-base --is-ancestor <hash> master` exits 0 for
  all three (tested against the branch ref, not `@{u}`; git HEAD is detached on the parked
  chain, as the report states).
- **Pushed and no uncommitted round work.** `jj-lane.sh state` prints
  `branch=master local=6a4afdfe… remote=6a4afdfe… ahead=0 behind=0 head=detached tracked=11
  untracked=87`. The 87/98 porcelain entries are an artefact of the parked jj working copy:
  every one of the nine round-36 paths compares byte-identical between the worktree and the
  tip (`git hash-object <p>` = `git rev-parse <tip>:<p>` for the lesson, the knowledge entry,
  SOURCES.md, README.md, QUALITY.md, SCORECARD.md, LOG.md and both round-36 tools). No
  tracked file differs from the tip.

Conformance defects (status-neutral, routed in §5):

- **D1 — cited receipt not committed.** `.ufo/waves/round-36/census-end.out` is cited as the
  round-end census evidence at `report:147` and `report:232`, but it is not tracked at the tip
  (`git cat-file -e <tip>:.ufo/waves/round-36/census-end.out` fails; it is one of the
  untracked files). `census-start.out` is tracked. The census claim itself re-verified — see
  §2 — so this is an unreachable-pointer defect under the evidence standard, not a false claim.
- **D2 — three staged-id cross-references in the lesson's Gate do not resolve.** See §3.
- **D3 — two dead wave-3 seats are missing from the report.** See §4.

## 2. Claims re-checked

Both claims were re-derived by plain measurement over committed bytes that this session ran
itself; the lane's counters were **not** executed. The lane's committed receipts were read for
consistency only (`.ufo/waves/round-36/{controls,c1,c2}/*`, all tracked at the tip).

### C1 — calibration 7 → 7 (four r35 routed statements corrected by append)

`git show <rev>:corpus/lessons/round-36.md` at base `e5a8ecec…` fails (file absent) — 0 of the
four statements corrected. At tip, `grep -nE 'R35-(S211|WORDS|MIRROR|KEEP)'` returns four
rows at lines 21, 23, 25 and 27, one per routed statement, each naming its own id:

- R35-S211 — the r35 lesson's "unreachable" reason is wrong; the row stays unappended.
- R35-WORDS — the S327 quote is 20 words, not the 18 the r35 lesson records.
- R35-MIRROR — the r35 validate tree is a mixed mirror, not a symlink tree.
- R35-KEEP — seven r35 leftovers classified, none swept.

Re-derived facts:

- **Append-only.** `git rev-parse <base>:corpus/lessons/round-35.md` and `…<tip>:…` both return
  `428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412` — the r35 lesson blob is unchanged. The r35 fleet
  report has exactly one fleet commit (`19b66dd4 round-35: kama report`), no round-36 edit, and
  is clean in the fleet worktree.
- **No false correction restated.** The Corrections section contains 0 occurrences of the
  token `429` (`git show <tip>:corpus/lessons/round-36.md | sed -n '/## Corrections/,/## Gate/p'
  | grep -c 429` → `0`).
- **Word count.** The r35 lesson records "18 words" for the S327 sentence, whose own text is
  *"When the limit is reached, new requests are rejected with HTTP 503 so the client can retry
  on another instance."* — this session counts 20 whitespace-delimited words. The correction's
  20 is right and the quote is inside the 25-word bound.
- **Leftover evidence untouched.** `<tip>:.ufo/waves/round-35/w1/out/ExecDisposition.md` is
  `9307c5d61c1942857a17cb259b4313460b37d0da`, the committed thinking dump, as R35-KEEP requires.

Verdict: **claim verified by re-measurement** (4 → 0 uncorrected, 0 false corrections, both
r35 blobs unchanged).

### C2 — coverage 9 → 9 (coverage map names the published-route entry)

- `git show <base>:corpus/README.md | grep -c sglang-native-route-deprecation` → `0`; at the tip
  → `1`, at `README.md:550` inside the `## Coverage map — round 36 addition` block.
- The entry exists at the tip (`corpus/knowledge/sglang-native-route-deprecation.md`, 2831
  bytes) and cites `S328` at line 3 and `S329` at line 4.
- `git show <base>:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S(328|329)[[:space:]]*\|'` → `0`;
  at the tip → 2 rows (`S328` line 214, `S329` line 215). Both ids are therefore present at the
  tip and absent at base, as the predicate requires.

Verdict: **claim verified by re-measurement**.

### Frontier, census and instrument repair (supporting checks)

- SOURCES rows: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → **201 at base, 203 at
  tip**, matching the report. Tier A 194 / B 6 / C 3; statuses mined 184, queued 8, rejected 11
  — all four counts reproduce.
- Census: this session ran
  `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` and got exit
  **0**, last line `kama ok …corpus/SOURCES.md`, with **93** `W04` lines, the pre-existing
  duplicate-url warnings the report names.
- Instrument repair: `git diff 2e8beda5… 6a4afdfe… -- tools/round36-coverage-audit.py` is a
  25-line diff confined to the `--selftest` arms (both arms now `load(..., BASE)`); `score()`,
  `PREDICATE`, `HEADING`, `ENTRY`, `BASE` and the measurement print are untouched, so the
  measurement line is unchanged by the repair.
- Freeze: `.ufo/waves/round-36/preregistration.json` is committed at `9014843c` with both
  predicates, both counting commands, both do-nothing controls and `frozen_before_scoring:
  true`; it matches the SCORECARD and report wording.

## 3. Discernment spot-check (LEARNING.md)

Sources were re-opened by this session on 2026-10-25 (`curl` for URLs, file reads for the
staged package under `/home/vgpnk/Projects/shokuknow/merge/kama/`).

| item | decision | re-opened source | agree / disagree | reason |
|---|---|---|---|---|
| S328 — SGLang native API at v0.5.22 | admit | `raw.githubusercontent.com/…/v0.5.22/docs/docs/basic_usage/native_api.mdx` → HTTP 200, 17359 bytes; line 6 carries the quoted sentence; route list line 9 is ``- `/get_model_info` `` | **agree** | the 15-word quote is byte-exact at the cited anchor and inside the 25-word bound; the page never names `/model_info` (`grep -c` = 0) |
| S329 — `http_server.py` at v0.5.22 | admit | `raw.githubusercontent.com/…/v0.5.22/python/sglang/srt/entrypoints/http_server.py` → HTTP 200, 110718 bytes; 786 `@app.get("/get_model_info")`, 790–791 the two literals, 796 `@app.get("/model_info")` | **agree** | the 16-word quote is the exact concatenation of the two adjacent string literals at 790–791; a byte-grep for the joined sentence returns 0, so the anchor — not a naive grep — is what locates it. Worth stating because a later recheck script must not use the joined-form grep as its test |
| quarantine S202 — Docker Compose services | present, not appended | `docs.docker.com/reference/compose-file/services/` → HTTP 200; `service_healthy`, `expected to be`, `before starting` all occur | **agree** | the span is on the page; the register's cell differs in quote style, which explains the linter miss |
| quarantine S210 — unsloth SGLang guide | absent | `unsloth.ai/docs/jp/…/sglang-guide` → HTTP 200; `Page Not Found` occurs **0** times; `sglang.launch_server` 12 times | **agree** | the page is reachable and the quoted cell is a status fragment, not a page sentence |
| staged `hosted-health-route-configuration.md` | reject — out of province | staged file `/…/merge/kama/knowledge/corpus/knowledge/hosted-health-route-configuration.md`: cites Google Cloud S351/S354/S355; `serving_container_health_route` at line 15 | **agree** | it is a remote-platform deployment field; remote endpoint health is kake's province |
| staged rows "S359, S360, S372" — "the same `http_server.py` URL" | reject — one URL, one row | staged `SOURCES.append.md`: `S359` = vLLM health API docs (line 36), `S360` = sglang tags API (line 37), `S372` = the lane's own evidence artifact (line 49); the `http_server.py` rows are **S364, S365, S377, S396** | **disagree on the ids** | the decision is right — several staged rows do cite that URL — but none of the three ids the lesson names does. D2 |
| staged `endpoint-health-probe-conventions.md` — "cites S331-S334" | reject — byte-copy | `amendments/corpus/knowledge/endpoint-health-probe-conventions.md` cites **S332, S336, S337, S338, S339** | **disagree on the ids** | the decision stands (those rows were not opened this round), but only S332 falls inside the stated range; the range repeats the r35 lesson's wording without re-deriving it. D2 |
| staged ids cited in the two admit paragraphs ("S366" for the docs page, "S359, S360, S372 and S391" for the code page) | cross-reference only | `SOURCES.append.md:43` `S366` = AWS SageMaker; `:68` `S391` = Azure ML BYOC; the `native_api.mdx` staged row is **S371** (`:48`) | **disagree** | five misattributed ids in one Gate section; the same defect class the round mined (`number-drift`, `false-grounded-reason`) was repeated in fresh prose. D2 |

Discernment reading: this sample agrees with **every decision** — 2 admits, 4 rejects, 2
quarantine verdicts — and with the three-way separation of `present` / `absent` /
`quote-not-located` that the register's single `payload-absent` class cannot express. It
disagrees with the **id evidence** used in three of the reject reasons and both admit
paragraphs. Judgment improved; citation discipline did not.

## 4. Axis verdicts

`git diff <base> <tip> -- SCORECARD.md` is a pure addition (`git diff --numstat` → `70 0`):
no existing score line is touched, so no axis can have been harmed. LOG.md `64 0`,
QUALITY.md `6 0`, README.md `16 0`, SOURCES.md `2 0`; `PROVINCE.md` and `SKILL.md` are
unchanged at the repo root (the only `PROVINCE.md` in the diff is the copy inside the
round-36 scratch mirror).

| axis | verdict | basis |
|---|---|---|
| calibration | **unchanged** | C1 measured 7 → 7; the four routed statements are corrected by append and both pinned blobs are unchanged. The score is held by the lane's own declaration and no counter-evidence exists |
| coverage | **unchanged** | C2 measured 9 → 9; one new coverage-map pointer, one new entry, two new registry rows |
| operability | **unchanged** | no claim, no SCORECARD movement, no touched surface |
| freshness | **unchanged** | two rows opened 2026-10-24 with recheck 90d; no stale row refreshed |
| depth | **unchanged** | no claim; entry and rows add ground rather than depth on an existing surface |
| adjacency | **unchanged** | no claim; the sibling-overlap question was re-read, not moved |

Neither claim is exploratory, so no `unprovable-but-better` / `unprovable` ruling is required.

## 5. Trend verdicts

- **expansion — improved.** One knowledge entry on ground the base did not hold
  (`corpus/knowledge/sglang-native-route-deprecation.md`), two registry rows (201 → 203) and
  one coverage-map pointer. The base README has 0 mentions of the entry name; the tip has 1.
  Bounded as the report says: a documentation-and-source reading of one tag, not a live sample.
- **quality — improved.** Four routed r35 statements now carry append-only corrections that
  this session re-derived from committed bytes, and both pinned r35 blobs are unchanged. The
  validate-before-append gate caught a real defect (E12 on both new rows before they entered
  the registry), and the C2 selftest fixture repair is confined to the selftest arms with the
  measurement bytes unchanged. Counter-evidence: the Gate's staged-id cross-references are
  wrong (§3, D2) — new prose with unverified pointers, routed below.
- **discernment — improved.** The lane separated three quarantine verdicts the register
  conflates, and both sampled rows reproduce; both admits locate at their anchors; all four
  sampled rejects stand on their stated reasons. Withheld: the staged-id citations (D2).

## 6. Routed defects for the lane's next round

1. **D1 — commit the round-end census receipt, or re-point the report.** `census-end.out`
   (12426 bytes, on disk, untracked) is cited twice as committed evidence. Either land it under
   `.ufo/waves/round-36/` or append a correction naming the tracked substitute. A cited pointer
   must resolve at closure.
2. **D2 — re-derive staged ids before citing them (appended correction, never a rewrite of
   `round-36.md`).** In the round-36 Gate: `S366` → `S371` (the `native_api.mdx` staged row);
   "`S359`, `S360`, `S372` and `S391`" → `S364`, `S365`, `S377`, `S396` (the `http_server.py`
   staged rows); "`cites S331-S334`" → `cites S332, S336, S337, S338, S339`. Every decision
   stands; only the id evidence is wrong. The criterion that should have caught it: an id range
   copied from a previous lesson is a claim, and the evidence standard makes it resolvable or
   absent.
3. **D3 — account for the two wave-3 seats that died on a rate limit.** `w3/out/seat-exit-codes.json`
   has 32 seats: 24 `rc=0`, 6 `rc=143` (the six the report names) and **2 `rc=1`** with
   `provider.rate_limit: 429` — `ScribeLog` and `RevQ206` (`RevQ206` had already fetched the
   S206 page and shipped a 4247-byte report). The report's wave table accounts for 30 of 32.
   Name them, with their last error text, in the lane's next report.
4. **D4 — carry, not new.** The lane working copy is still parked on the five foreign-identity
   commits and re-anchoring it stays an operator item (L0 open). This verifier did not touch
   the lane's jj state beyond the one commit that carries this file.

## 7. Admission

Both claims verify by independent re-measurement; no axis is harmed; the four routed r35
statements are corrected without rewriting the r35 lesson or report. **Admitted**, with D1–D3
routed to the lane's next round. SHONEN boxes remain `[~]` (four boxes, each with a resolvable
pointer except the census receipt D1 names); none is `[x]`, so promotion stays operator-owned
and this verifier wrote no `[x]`.
