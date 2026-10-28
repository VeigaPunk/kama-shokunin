# W01LessonDraft — round-62 lesson skeleton (advisory draft for the L1)

Seat: W01LessonDraft (scribe leaf, axis calibration). Lane `kama-shokunin`, tip
`65d7cad0fce90e34de37527cde22e97b63b118bf`, base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`.
I did **not** edit `corpus/lessons/round-62.md` or any other lane source. This file is the draft
plus the evidence behind each row; the L1 integrates it.

## What was done

- Read the freeze, both do-nothing controls, census start, `measured/c1-before-fix.txt`, the
  canonical capability list, `registry/capability-claims-r62.tsv`, and every settled w1 seat
  report/out file (A01, A02, A04, A05, A06, A07, E04, M01, M02, M03, M05, M06, M10, R01–R04,
  S05 empty at read time).
- Re-fetched the pinned llama.cpp server README raw URL at `704366d76…` into scratch and hashed
  it: `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`, equal to the digest
  S526 records. README line 1314 = `### POST /v1/completions: OpenAI-compatible Completions API`
  (exact wording uses backticks), line 1316 = the quoted sentence, line 1320 = the OpenAI
  reference deferral, next heading at 1345.
- Inspected working-tree state with read-only git: `M corpus/SOURCES.md`, `M tools/round62-c1-counter.py`,
  untracked `corpus/knowledge/completion-request-plane.md`, `corpus/lessons/round-62.md`,
  `?? kama-shokunin/` (empty `.ufo` stray dir), wave dirs.
- Ran no counter, no lane tool, no live server. No tool installed or updated (nothing was needed).

## Calibration findings that the draft had to absorb

1. **S526 is a working-tree candidate, not a committed row.** `git show master:corpus/SOURCES.md`
   and the base both lack it; `git status` shows `M corpus/SOURCES.md`. Its two `used-by` targets
   are untracked. It must be committed with them or the next census re-raises the W01 used-by class.
2. **The C1 repairs are not at the tip.** `git show master:tools/round62-c1-counter.py` hashes
   `275610b5…`; the worktree copy hashes `a3498308…` and differs by three lines (two `(cj or {})`
   guards and `'hold'` → `'hold_released'`). A02 and A04 loaded master bytes and crashed at
   `grade()` line 130; M01/M05 likewise could not replay; A01/M03's successful `met=True` runs used
   the modified worktree. So any `met=True` cited by the round is reproducible only after that hunk
   is committed and the counter re-run.
3. **The sensitivity leg is vacuous in effect for the round's actual patterns**, though A05's exact
   counterexamples refute the blanket "any non-empty pattern" phrasing. With
   `MUT='__kama_mut__'`, no frozen pattern is a substring of MUT, so `P` is absent from
   `out.replace(P, MUT)` whether or not it appeared; the conjunct is true for every row. The C2
   docstring's "replacing the decisive output substring flips the result" is not what the code does.
4. **Gate row precision:** the S526 anchor says lines 1314–1336; the section actually runs
   1314–1344 and the deferral is line 1320. The `teaches` cell is prose, not a ≤25-word quote; the
   quote lives in the anchor cell, which matches the S525 style, so I did not treat that as a defect —
   only the line range is imprecise.

---

# DRAFT BEGINS (full text for `corpus/lessons/round-62.md`)

# Round 62 lesson — kama (2026-10-28, attempt 2)

Claims: C1 operability — lane-owned live `/v1/completions` request plane
(`tools/kama-completion-live.py`, receipt schema `kama-completion-live/v1`); C2 calibration — the
12-capability self-assessment bound to live re-execution of each capability's own check
(`registry/capability-claims-r62.tsv`). Freeze `.ufo/waves/round-62/controls/freeze.txt`; base
`a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3` (round-61 closure tip).

## Gate

| Source / candidate | Accessed | Located quote (≤25 words) | Verdict |
|---|---|---|---|
| S526 — llama.cpp server README @ `704366d76` (b11755), `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md` | 2026-10-28 | "Given an input `prompt`, it returns the predicted completion." (README line 1316; heading line 1314) | **recommend admit** — tier A pinned-build docs; raw fetch sha256 `714c067b…` equals the row's recorded digest; the route is new scope (S035/S112 hold `/health`/`/props`, S010/S524 are Ollama). Caveat: the same paragraph says no strong OpenAI-spec claims are made, so the row's "OpenAI-compatible" wording is the heading's, not a conformance claim; response fields are observed from the receipt, never documented here. The row is staged **uncommitted** (`M corpus/SOURCES.md`) and must land with its two `used-by` targets (`corpus/knowledge/completion-request-plane.md`, `corpus/lessons/round-62.md`) or the census W01 used-by class returns |
| `considerthese/2026-10-26.md`, suggestion 3 | 2026-10-28 | "Keep a running count of counters that a shortcut can satisfy" (line 33) | **adopt in part — running tally deferred** — the round supplies the proposal's per-round inputs (attack wave; the counter-bypass findings below) but adds no tally file; C2's eight control families are one round's controls, not a trend. Flip: add one append-only row per counter round (shortcut controls that met, mutants that survived, falsify wave ran/absent) and claim adoption only once a second round's row exists |
| `merge/kama/` staged package (read-only at `/home/vgpnk/Projects/shokuknow/merge/kama/`) | 2026-10-28 | r61 spot-check: "all 7 kama slice ids (S200/S202/S206/S210/S211/S224/S230) match `payload-absent` byte-exact" | **defer** — no staged entry appended; reason: payload absent, so there is no cited source to hand-check; the r61 non-author spot-check agreed with the deferral. Flip: re-open when the staged payload lands and a hand-check locates each cited quote, then admit or reject per row |
| Round-62 outside spot-check | pending | none | **pending** — no non-author closure exists; this lane's seats do not count. No gate admission is claimed until a fresh non-author file re-opens at least one admit and one reject |

SOURCES census at start: `.ufo/waves/round-62/census/start.out`, exit 0, 265 rows
(`git show master:corpus/SOURCES.md | grep -c '^| S'` = 265), with the existing duplicate-URL W04
and used-by W01 warning classes. S526 is not among the 265 at the tip; it is a working-tree row.
The pinned README was re-fetched this round and hashed to `714c067b…`; its completions section runs
lines 1314–1344, with the OpenAI-reference deferral at 1320.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| `attribution` — attempt 1 stopped on a generic wrap-up notice before freeze or report | `.ufo/watchdog.log:1824` — `2026-10-28T08:59:38-03:00 lane-dead-no-report kama round=62; retry same round (hyaku-inline attempt=1: KamaR62 stopped on a wrap-up notice before freeze: drafts only (tools/round62-c1/c2 counters uncommitted), no wave, no report)` | the failure event itself; no report or marker landed | attempt 2 re-verified the inherited drafts (tool smoke `REQUEST_OK`, predicate/code audit, base receipts still red) and ran freeze → wave → report; the stop is named in `SCORECARD.md` §Round 62 |
| `counter-crash` — the C1 counter died on a malformed receipt instead of grading it rejected: the tamper control replaces the completion body without updating `body_sha256`, `cap()` correctly returns `None`, and `grade()` dereferenced it | `.ufo/waves/round-62/measured/c1-before-fix.txt` — `AttributeError: 'NoneType' object has no attribute 'get'` at `tools/round62-c1-counter.py:130` (`u = cj.get('usage')`); independently reproduced against master bytes by A02 (whole-counter run, exit 1) and A04 (empty receipt, non-dict `captures`, integer body and list `checks.listener_owned` all crash). Master copy sha256 `275610b5…` still has it | none — found pre-data | guard `usage`/`timings` with `(cj or {})`, keep the frozen predicate text unchanged; the guard exists **only in the uncommitted worktree** (`sha256 a3498308…`) at draft time, so the landing commit must be named before any `met=True` is cited |
| `reference-drift` — the counter tested `checks['hold']` while the tool emits `checks['hold_released']`; the round's own live receipt therefore scored `met=False` with `inconsistent=['unexpected-checks']` even though every graded check passed | M05/M06 reports: the committed receipt at `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json` carries the extra `hold_released` key and fails the tip grader; A01/M03's passing runs are the worktree counter | M05C1AttackThe, M06C1AttackThe | gate on the emitted key; same uncommitted hunk as the crash guard; land both together |
| `frozen-instrument-drift` — the instrument that reaches `met=True` is not the instrument at the tip | `git diff -- tools/round62-c1-counter.py`: 3 changed lines; master sha `275610b5…` vs worktree `a3498308…`; A02/A04/M01/M05 load master bytes and crash or cannot replay, A04 states it refused the "modified" working-tree copy | A04C1SchemaFuzz, A02C1HoldTamper | commit the guard hunk in the same commit that carries the measurement and re-run the C1 counter afterwards; the round report must not cite a `met=True` that no committed instrument reproduces |
| `selftest-scratch-root` — `kama-live-replay.py --selftest --scratch <nonexistent>` raised `FileNotFoundError`: `tempfile.mkdtemp(dir=root)` ran before `root` existed | base `tools/kama-live-replay.py:582` has no `os.makedirs`; master diff is `+1 -0` adding `os.makedirs(root, exist_ok=True)`. Post-fix receipt `.ufo/waves/round-62/w1/out/E04SelftestsB/klr-selftest.txt` = `KLR_SELFTEST pass=48 fail=0` | E04SelftestsB | fixed in master; the C2 bound row `live-receipt-replay` depends on it |
| `vacuous-sensitivity` (confirmed in effect; earlier phrasing too strong) — the C2 sensitivity leg cannot fail for any real row, and it does not measure a verdict flip | `tools/round62-c2-counter.py:269-271`: `mut = out.replace(tpl['pattern'], MUT)`; `sensitive = not (tpl['pattern'] in mut and rc == 0 and not dead)`. With `MUT='__kama_mut__'`, no frozen pattern is a substring of MUT, so the pattern is absent after replacement whether or not it appeared ⇒ the conjunct is always true. A05's counterexamples (`P='a',O='a'` → False; `P='ab',O='aab'` → True) refute the blanket "any non-empty pattern" form, not the operative vacuity. R02 finding 3 concurs that it is textual, not re-execution | A05C2Sensitivity (`.ufo/waves/round-62/w1/out/A05C2Sensitivity/sensitivity-probe.txt`), R02C2Gap | **open** — use a dynamic marker guaranteed not to contain the pattern and assert the recomputed predicate flips; do not claim semantic sensitivity from this conjunct, and closure must not treat C2 as verified on it alone |

Additional counter limits confirmed by the wave, **open at this draft** (recorded here so the report
does not overstate `met=True`):

| class | evidence | fix |
|---|---|---|
| C1 receipt-byte blindness to teardown | M05: a receipt with child died mid-hold but `child_pre_dead=false` and `returncode=0`/`-15` scores `met=True`; M06: SIGKILL evidence absent, forged as `returncode=0`, is accepted; M03: wrong `hold.nonce` and wrong capture timestamp are accepted | bind teardown/signal claims to event evidence, not the receipt's own booleans |
| C1 witness binding is self-asserted | R01 finding 4: `sent_prompt`/`nonce_prompt` are set from the local variable, not from observed request bytes; response text only has to be a string | retain the sent request bytes and require the nonce in the response text |
| C1 response surface partly ungraded | R01 findings 1, 2, 3, 5, 6: headers and `body_truncated` ungraded, timings accept bool/negative values, `listener_owned` self-validating, fingerprint only shape-checked | grade the captured envelope, truncation flag, header contract and timing bounds; no control targets them today |
| C2 canonical-section authority | A06: a fenced ` ```md ` block with a later `round 999` heading and the 12 exact rows makes `canonical_rows()==(999, 12)`; later empty heading fails closed | track Markdown fences in `canonical_rows()`; treat an empty later heading as malformed |
| C2 bound-run injection | A07: `run_bound()` interpolates `%T` into `bash -c` unquoted; a crafted `--work` path ending `; echo '<frozen pattern>'; true #` returns `(True, pattern, True, False)` without executing the check | execute an argv vector with `shell=False`, or `shlex.quote` every substituted value |
| C2 environment not hermetic | R02 finding 5: only `TMPDIR` is overridden and `PYTHONPATH` removed; the rest of the caller environment is inherited, so "scrubbed environment" is overstated | use an explicit allowlist environment |

## Sources opened

- `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md`
  — fetched 2026-10-28, sha256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`;
  §POST `/v1/completions` lines 1314–1344, quote at 1316, deferral at 1320. Grounds S526.
- `considerthese/2026-10-26.md` — opened 2026-10-28; suggestion 3 at line 33 quotes above.
- `/home/vgpnk/Projects/shokuknow/merge/kama/` — read-only recon only; not modified; no adoption
  this round (deferral + flip above).
- Local evidence read: `.ufo/waves/round-62/controls/freeze.txt`, `c1-base.txt`, `c2-base.txt`,
  `census/start.out`, `measured/c1-before-fix.txt`, `registry/capability-claims-r62.tsv`,
  `SCORECARD.md` §Round 62 canonical list (lines 3272–3293),
  `.ufo/waves/round-62/w1/out/E04SelftestsB/*.txt`,
  `.ufo/waves/round-62/w1/out/A05C2Sensitivity/sensitivity-probe.txt`,
  `.ufo/waves/round-62/w1/{A01,A02,A04,A05,A06,A07,M01,M02,M03,M05,M06,M10,R01,R02,R03,R04}.md`.

## Status / integration notes

- Wave `w1` is one policy-v2 wave, 64 seats per `w1-spec.json` (18 mutation-tester, 16 executor,
  8 critic, 6 scout, 6 scribe, 5 reviewer, 4 connector, 1 sentinel). Results were not settled at
  draft time; no WAVE-DONE receipt exists yet, so no wave verdict is recorded here.
- C1: the spec-time measurement is `met=True` (`live_ok=1/1`, 16/16 controls, `errors=0`) at tip
  `65d7cad`; `SCORECARD.md` still says PENDING. Because of the instrument drift above, the report
  must name the commit that lands the counter guards before treating that measurement as the tip's.
- C2: measurement is running; `SCORECARD.md` says PENDING. Do not write a `met` line until the
  counter's own output is captured, and keep the sensitivity conjunct out of the credit if it is
  still vacuous.
- Working-tree items the integrator must resolve, not silently commit: `M corpus/SOURCES.md`
  (S526), `M tools/round62-c1-counter.py` (guards + `hold_released`), untracked
  `corpus/knowledge/completion-request-plane.md`, `corpus/lessons/round-62.md`, the stray
  `kama-shokunin/` directory (empty `.ufo`), and the wave `w1.ready*`/`measured/`/`w1/` trees.
- Nothing in this draft claims a correction is in the tip until it is committed; where status is
  uncertain the row says so.

# DRAFT ENDS

## Touched surfaces

- New: `.ufo/waves/round-62/w1/W01LessonDraft.md` (this file) and
  `.ufo/waves/round-62/w1/out/W01LessonDraft/` (duplicate + fetch receipt).
- Read-only: lane files listed above, read-only git on the lane, one HTTPS fetch into my scratch.
- Not touched: `corpus/lessons/round-62.md`, any tool, registry, SCORECARD, PROVINCE, the fleet
  repo, sibling lanes, lane jj/state, `shokuknow/merge/kama/`.

## Artifact paths

- `.ufo/waves/round-62/w1/out/W01LessonDraft/W01LessonDraft.md` — duplicate full result.
- `.ufo/waves/round-62/w1/out/W01LessonDraft/s526-fetch.txt` — URL, fetch date, sha256, line anchors.

Tally: gate_rows=4 (admit_candidate=1 adopt_partial=1 defer=1 pending=1) mistakes=6 open_counter_limits=6 sources=3 installs=0
