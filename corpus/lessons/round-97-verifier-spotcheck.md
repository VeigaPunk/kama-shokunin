# Round 97 — non-author verifier spot-check (integrator, @m_zfl)

author: hyaku closure (non-author integrator, @m_zfl)
Lane `kama`, round 97. Base `40763bd2ca1e3f99881247eaa9f5e3ef3b596653`; measured commit `be59035141d3dcc3075de67b431eaa995e0aded4`; lane tip / closure commit `ac014090e99b3ef90d71e657b9173ee1a15e8e80`. Report: `.ufo/reports/round-97/kama.md` (fleet repo).

## Step-1 conformance

| Check | Result |
|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-97/kama.md` → `kama-shokunin` (two commits: report + erratum) — pass |
| `SHONEN` heading, one line per box | Yes, 4 lines (all `[~]` with evidence pointers, no named non-author verifier) — pass |
| Cited commits exist and are ancestors of `master` | `9e605d41`, `e057166e`, `be590351`, `ac014090`, base all exist; `merge-base --is-ancestor <h> master` YES for all — pass |
| Lane no uncommitted round work, pushed | `jj-lane.sh state` → `ahead=0 behind=0 tracked=0 untracked=0`; `ls-remote origin refs/heads/master` = `ac014090` — pass |
| Prompt template contract | Fleet `.ufo/prompts/kama-round-97.md` carries §§1–5 contract, §§2b/3/4/5 items, hyaku addendum §6, scratch §7, prefile §8 — pass |
| Marker vs real report | Real report: work, 4 landed changes with LOG ties, 3 before→after measurements, frontier, trends, SHONEN — **status `ok`, not marker/failed** |
| Prefile ledger (Amendment 59) | `prefile-falsification.py --lane kama --round 97` → `PREFILE-FALSIFICATION: pass claims=3 rows=24 attack_seats=8 findings=0`, **exit 0**; ledger covers every claim (C1×8, C2×8, C3×8 = 24 rows); every `falsifies-wording` row names `plans/round-97-amendment-2.md` as the narrowing — pass |

Conformance defects: none that bar admission. Historical census warnings (W04 duplicate-URL, W01 tier-C mined) persist across rounds; `sources-census validate` still exits 0 (counted as standing warnings, not new defects). `claims.json` frozen at freeze shows `checks=14` / `checks=8`; amendment 2 added the extra graded surfaces (now 18/10) with counters re-frozen — explained in the report, not a defect.

## Per-claim re-check

**C1 — calibration (re-measured).** Command: `python3 tools/round97-self-assessment-audit.py --repo . --rev be590351` → `SELF_ASSESS97 checks=18 mismatches=0 met=True rev=be590351… skill_sha256=863eb35d…`, exit 0. Matches report. Committed base control `c1-base.out` → `checks=18 mismatches=10 met=False rev=40763bd2`, exit 1. Also spot-verified live cells: `sha256sum SKILL.md` = `863eb35d…`, `wc -l` = 2473, `grep -c '^## '` = 59 — matching the SCORECARD depth row. **Verdict: verifies → improved.**

**C2 — operability (evidence-verified; sibling gate not executed).** Committed `measured/c2.out` tail: `ROUTER_BUDGET97 cells=17 mismatches=0 positive_mismatches=0 … slow_files=72 runs=2 … rev=be590351… w03_seconds=80.1 load1_nat=102.09`, exit 0. Legacy control `c2-legacy-mutants.out`: each of flat6/undercharge/maxmeta/nopreamble `cells=13 cells_ok=13 survived=1`. New-mutant control `c2-new-mutants.out`: all four `caught=1` with `expect_cell` red (flat6→W15-700k-nd4, undercharge→W14-900k-nd1, maxmeta→W16-maxmeta, nopreamble→W17-833333-nd1). Re-ran nothing executable against the probe (per Gate standard). **Verdict: verifies (evidence) → improved.**

**C3 — depth (re-measured).** Command: `python3 tools/round97-depth-boundary-audit.py --repo . --rev be590351` → `DEPTH_BOUNDARY97 rows=6 checks=10 mismatches=0 met=True rev=be590351…`, exit 0. Matches report. Base control `c3-base.out` → `rows=0 mismatches=1 met=False`, exit 1. SKILL.md §Round 97 correction present (line 2443) with `5 + nd` arithmetic at lines 2431/2446. **Verdict: verifies → improved.**

**Axis harm check.** `git diff 40763bd2 ac014090 -- SCORECARD.md`: operability 8→8, freshness 8→8, depth 7→7, coverage 9→9, calibration 7→7, adjacency 7→7. No score moves, no harmed axis. Capability `probe-forgery-grading` added with demonstrated evidence pointer. Gate selftests: C1/C3 are revision-graded counters (no `--selftest` flag); C2's mutant controls serve as the allowable-failure demonstration — committed receipts show both red (base/exit 1) and green (measured/exit 0) states. No gate regression found.

### Per-axis verdicts

| Axis | Verdict |
|---|---|
| calibration | improved (C1 verified) |
| operability | improved (C2 evidence-verified) |
| depth | improved (C3 verified) |
| coverage | unchanged |
| freshness | unchanged |
| adjacency | unchanged |

## Discernment spot-check (LEARNING.md)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S620 GGUF spec `57e2c2ca` | admit (A, spec, mined) | `https://raw.githubusercontent.com/ggml-org/ggml/57e2c2ca…/docs/gguf.md` — sha256 `1dead27b…` (43 175 B) | agree | Quote "uint64_t dimensions[n_dimensions];" found at line 313 verbatim; "Currently at most 4" line 310; five-field tensor-info grounds `5 + nd` cost |
| S621 `ggml.h` b12177 | admit (A, code, mined) | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/ggml/include/ggml.h` — sha256 `590e00a5…` (119 369 B) | agree | "nb[0] = ggml_type_size(type)" found at line 697 verbatim; `ne[GGML_MAX_DIMS]` line 695; correction of S618's constant-6 is grounded |
| S619 `gguf-py/README.md` | reject (C lead) | `https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/gguf-py/README.md` — sha256 `f759ed01…` | agree | Opens "This is a Python package for writing binary files in the [GGUF](…)" at lines 3–4; documents the writer, not the parsed header layout — grounds no step cost |
| `llama.cpp/docs/gguf.md` @ b12177 | reject (absent) | Same URL — HTTP 404 "Not Found" | agree | Path absent at pinned tag; spec's live location is the ggml repo (S620) |

Row-count cross-checks: `grep -cE '^\|[[:space:]]*S[0-9]{3,}'` → 361 at HEAD, 358 at base (`git show 40763bd2:corpus/SOURCES.md`). `sources-census validate` → `kama ok` exit 0 (with standing W04 duplicate-URL and W01 tier-C warnings that pre-date this round).

## Trend verdicts

- **expansion: unchanged** — S620/S621 deepen the already-governed header-cost surface; no new admitted `knowledge/` entry and no new governed surface. No coverage regression.
- **quality: improved** — C2 replaces a cell set that passed all four forgeries; C1 replaces a self-assessment that could stay green on a flat-6 parser; C3 adds the boundary decision with a KV/rank class caveat. Each carries a red-before control.
- **discernment: improved** — the wave falsified the freeze-time filings pre-filing (RV01 §2.1 count blocker, RV01/CR02 literal-presence checks, CR01 hardcoded formula/class width, CR02 unenforced six-row claim); amendment 2 answered each with a re-frozen instrument and the 24-row ledger's falsifies-wording rows all narrow to it.

**Trends: expansion unchanged, quality improved, discernment improved.**

## Routed defects for the next round

None blocking. Carried disclosures from the round report stand for round 98: `round75-instruments` red (bad_rows=19, L0 r87/r89); `round78-instruments` red from the host's non-lane Ollama listener on 127.0.0.1:8080; slow `/props` verdict still deciding (r94 SC02 F4); pass-level wall-clock wrapper (SC01); unobservable ctime memo shape; C1 checks 13–14 grade receipt needles rather than every header number (RV01 §2.10).

**Note for the operator:** all four SHONEN boxes remain `[~]` (author-asserted, no non-author verifier). If promotion is ever to be claimed, each box needs a named non-author `<id>` reviewer — promotion stays operator-owned; no boxes were checked here.
