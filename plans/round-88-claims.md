# Round 88 — frozen claims

Base revision `9b4c7af16fdd4bba9e4815f4615f4b003f340747` (master, pushed; `jj-lane.sh state` at round start:
`local=9b4c7af1 remote=9b4c7af1 ahead=0 behind=0 tracked=0 untracked=0`). Freeze commit: the commit that adds
this file, `tools/round88-router-cells.py`, `tools/fetch-pinned-model.py` and `.ufo/waves/round-88/controls/`
(its hash is the helper's `landed` line, recorded in the report). Freeze date 2026-11-06.

**Fresh-start round** (run-15 amendment 46, "Fresh start authorized … kama r88"). The last three rejected
closures were read before declaring anything: `corpus/lessons/round-85-verifier-spotcheck.md`,
`round-86-verifier-spotcheck.md`, `round-87-verifier-spotcheck.md` (all `rejected-honest-stop`; r83 was
`rejected-harmed`). The common root of r83–r87: every calibration claim rode a lane-authored selector over
the lane's own prose (rendered cells, disposition oracles), each round's selector was falsified by the next
round's probes, and the frozen predicate could never be met without rewriting the instrument. This round does
not continue that line: the round-87 successor selector (R1 of the r87 spot-check) is **dropped**, not
re-frozen; its routed defects are recorded as carried debt in the round lesson.

Assigned axes: operability 8, calibration 7 (`shokunin.conf`). Calibration is the lowest assigned axis (tied
7 with depth and adjacency); C2 works it. Two claims, distinct axes, causally separable:
C1 touches `tools/kama-probe.sh` only (plus its new counter); C2 touches `SCORECARD.md` only. Neither needs
the other to verify. No exploratory claim.

## Do-nothing controls (executed and committed before this freeze)

| Control | Command | Receipt | Result |
|---|---|---|---|
| C1 router cells, no work | `python3 tools/round88-router-cells.py --repo . --rev 9b4c7af1… --work $S` | `controls/c1-base.out` | see receipt; must be mismatches ≥ 1, exit 1 |
| C1 forgery F1 always-unloaded | same, `--probe-file controls/f1-always-unloaded.sh` | `controls/c1-f1.out` | must be mismatches ≥ 1 |
| C1 forgery F2 any-loaded oracle | same, `--probe-file controls/f2-any-loaded.sh` | `controls/c1-f2.out` | must be mismatches ≥ 1 |
| C1 harm baseline | `python3 tests/probe-verdicts/check.py`; `bash tools/test-snapshot.sh` | `controls/harm-base-*.out` | pass/fail counts recorded |
| C2 self-description, no work | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip 9b4c7af1…` | `controls/c2-base.out` | `mismatches=4 met=False` |
| C2 newest closure, no work | `python3 tools/round69-newest-closure-counter.py --repo . --rev 9b4c7af1… --since-round 63` | `controls/c2-newest-base.out` | `STALE_CALIBRATION`, exit 1 |
| C2 cheapest partial (pointer only) | scratch clone, only the closure pointer re-pointed to round-87, then the reconciler | `controls/c2-pointer-only.out` | must be mismatches ≥ 1 |

## C1 — operability: llama.cpp router-mode readiness verdicts in `tools/kama-probe.sh`

Motivating evidence (this round, before any change): the base probe prints `MODEL_OK reason=matched` for
`stories260K` on a lane-owned pinned `llama-server` b11755 started in router mode (`--models-dir`,
`--no-models-autoload`) while a real `POST /v1/chat/completions` for that model answers
`HTTP 400 {"error":{"code":400,"message":"model is not loaded",…}}`; the same false green holds read-only on
the operator's live router at 127.0.0.1:1234 (`LFM3-1.7B`, `status.value=unloaded`). Receipts:
`controls/pilot-*.out`. Source: llama.cpp `tools/server/README.md` "Using multiple models" router section,
`status` object values `unloaded`/`loading`/`loaded`/`sleeping`/`downloading`/`incomplete`, `failed: true`
(SOURCES row S581, opened this round).

Frozen verdict rule (the claim's predicate is the counter below; this is its specification):
- When the `GET /v1/models` entry (or entries) whose id matches the expected id under the probe's existing
  `normalize_id` rule carries an object `status` with a string `value`: `loaded` → `MODEL_OK`
  (reason `matched`, unchanged); `loading` or `downloading` → `MODEL_LOADING` (reason `router-<value>`); any
  other value (`unloaded`, `sleeping`, `incomplete`, an unknown string) → new verdict `MODEL_UNLOADED`
  (reason `router-<value>`, `-failed` appended when `failed` is true). A matching entry with no `status`
  object keeps today's verdict (single-model servers unchanged). If several entries match, any `loaded` or
  status-less match wins, else any loading/downloading, else `MODEL_UNLOADED`.
- Wildcard expectation (`*`, `-`, empty): if no entry carries a `status` object, unchanged (`MODEL_OK`);
  otherwise the same precedence over all entries.
- `MODEL_UNLOADED` is drift (`check`/`snapshot` exit 2), a model surface for `listeners` registration, and a
  vocabulary member for baseline parsing.

Counter (frozen at this commit; its bytes at the measured revision must equal its bytes here):
`python3 tools/round88-router-cells.py --repo . --rev <R> --work <scratch>` extracts
`git show <R>:tools/kama-probe.sh` into the scratch dir and runs those bytes (never the worktree), over 17
cells: 14 canned stub cells (C01–C14, expectations in the counter's `CANNED` table) and 3 live cells
(L01–L03) on a pinned `llama-server` b11755 router child (binary sha256 `b6a31a8e…`, model
`stories260K.gguf` sha256 `270cba1b…`, `--no-models-autoload`, free loopback port, child torn down). A live
cell's expected verdict is not authored: it is derived from an independent oracle executed right after the
probe — a real `POST /v1/chat/completions` for the model: HTTP 200 → `MODEL_OK`, HTTP 400 with
`model is not loaded` → `MODEL_UNLOADED`, anything else → could-not-evaluate (exit 2). It prints one
`ROUTER_CELL <id> expected=<V> observed=<V> reason=<r> ok=<0|1>` per cell and the summary
`ROUTER_CELLS cells=17 mismatches=<n> canned=14 live=3 probe=<rev|override> probe_sha256=<hex>`; exit 0 iff
mismatches=0, 1 if mismatches>0, 2 could-not-evaluate.

**Predicate C1 (one sentence, same in counter and receipt):** at measured revision M,
`ROUTER_CELLS cells=17 mismatches=0 canned=14 live=3 probe=rev` is printed with exit 0, the counter at M is
byte-identical to the freeze commit, and the do-nothing receipt at base printed mismatches ≥ 1.

**Harm conjunct:** `python3 tests/probe-verdicts/check.py` and `bash tools/test-snapshot.sh` print the same
pass/fail counts at M as in `controls/harm-base-*.out`.

**Kill rule:** any mismatch at M, a counter byte change after freeze, a could-not-evaluate at M, or a harm
conjunct regression → C1 not verified (honest stop; no post-hoc counter edit).

## C2 — calibration: SCORECARD self-description vs repo state, counted by the round-42 reconciler

Before (measured at base): `round42-selfdesc-reconcile.py` prints `mismatches=4 met=False`
(`retired` states 6 axes but the live table carries 7 rows; `saturation` vector lists `calibration 7` twice;
`caps` head table names `gate-round86-instruments` but the newest canonical list (round 86) does not;
`closure_ptr` names round-85 while the newest committed closure is round-87). Root: the live `## Axes`
table carries **two** `| calibration |` rows (round-86 and round-85 text), and the round-87 capability was
never added to a canonical list. `round69-newest-closure-counter.py` prints `STALE_CALIBRATION`.

Work: move the round-85 calibration row byte-identical out of the live table into a history subsection;
re-point the single live calibration row to `corpus/lessons/round-87-verifier-spotcheck.md` (verdict
`rejected-honest-stop`); add a canonical capabilities list as of round 88; re-anchor any hash the edits
change. Instruments are not edited.

**Predicate C2 (one sentence):** at measured revision M, `python3 tools/round42-selfdesc-reconcile.py --repo .
--tip M` prints `mismatches=0 met=True` and `python3 tools/round69-newest-closure-counter.py --repo . --rev M
--since-round 63` exits 0, with `tools/round42-selfdesc-reconcile.py`, `tools/round41-scorecard-reconcile.py`
and `tools/round69-newest-closure-counter.py` byte-identical between base and M, and the moved round-85 row
present verbatim at M.

**Kill rule:** mismatches ≥ 1 or a non-zero newest-closure exit at M, any instrument byte change, or the
moved row absent verbatim → C2 not verified. No axis score cell moves in this claim (calibration stays 7).

## Frontier step

- `corpus/SOURCES.md`: S581 (llama.cpp server README, router mode) opened this round; at least one
  source-level reject recorded in the lesson `## Gate` (r87 R7).
- Mistake mined into `corpus/lessons/round-88.md` `## Mistakes` (the self-referential calibration selector
  loop r83–r87, and the reaped pinned fixture model that silently turned `round78-live-reconcile` 4/4 → 0/4).
- Sourced claim: C1 (S581); knowledge entry `corpus/knowledge/router-mode-readiness.md` cites S581.
