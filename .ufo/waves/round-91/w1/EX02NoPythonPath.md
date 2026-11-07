# EX02NoPythonPath — kama round 91, wave 1 (C1 on the python-free path)

Seat: leaf executor, lane `kama-shokunin` read-only. Revisions measured: base `c06838c5b94576971ea33ac465bf2c935e9037f9`
(probe sha256 `b71c309a…`, the do-nothing control), measured M `3decfa36b0eba7e5197c034dd1547146bca1568a` (probe sha256
`0aa43573…`). Lane HEAD during the wave `3f317ecd…`; lane tree untouched by this seat. Scratch
`/fast/scratch/hyaku/kama-r91/EX02NoPythonPath` (removed after copy).

## Scope

C1's held-out "python-free path": run the frozen counter `tools/round91-answer-time.py` with `python3` absent from the
PATH the probe inherits — a scratch dir of symlinks to every executable except `python*` (3946 links; `command -v python3`
exit 1) — and compare B vs M on the same path, focused on T1 (200 000 ids then `good`), T4 (3.9 MB id then `good`),
P2 (`/models/sub/good.gguf`), P4 (non-ASCII id), P5 (`q"b\s` id). Plus wall time of `tools/test-snapshot.sh` and
`tests/probe-verdicts/check.py` at B vs M, and a persisted latency-budget line for r90 routed R4 (prose only).

Host: X1, 32 cores. Load was high and moving throughout: `uptime` showed load1 23–41 while this seat was doing nothing
but timing (other lanes); every timing receipt below carries the `uptime`/`load1` reading taken at the same moment.
No tool installs; nothing mutated outside scratch and this out dir.

## Commands and outputs (true exit codes)

1. `PATH=$S/pbin TMPDIR=$S/tmp /usr/bin/python3 <lane>/tools/round91-answer-time.py --repo <lane> --rev <M> --work $S/work-m`
   → exit **1**; `ANSWER_TIME cells=12 mismatches=2 positive_mismatches=2 probe=rev probe_sha256=0aa43573… rev=3decfa36…`
   (`m-nopy.out`). Cells: T1 0.49 s MODEL_OK matched, T2 0.45 s, T3 0.21 s, T4 1.00 s matched, T5 1.14 s matched,
   P1/P2/P3/P6/P7 ok, **P4 0.02 s MODEL_MISMATCH**, **P5 0.02 s MODEL_MISMATCH**.
2. same with `--rev c06838c5…` → exit **1**; `cells=12 mismatches=7 positive_mismatches=2 probe=rev
   probe_sha256=b71c309a… rev=c06838c5…` (`b-nopy.out`). T1/T2/T4/T5 **killed at 120.10 s**, T3 101.99 s (cell fails on
   the 20 s budget), P4/P5 the same two mismatches as M.
3. `/usr/bin/python3 … --rev 3decfa36…` with python3 present → exit **0**; `cells=12 mismatches=0 positive_mismatches=0
   probe=rev probe_sha256=0aa43573…` (`m-py.out`, load1 27.7–28.9). Reproduces `measured/c1.out` under 30× the load of
   that receipt (max cell 2.11 s vs 2.05 s).
4. `probe_matrix.py` (stub bodies u1 raw-UTF-8 / u2 `\uXXXX`-escaped / u3 quoted id) × {B, M} × {python3, python-free}
   → 12 rows, `probe-matrix.out`: u1 `MODEL_OK matched` on all four combos; u2 and u3 `MODEL_MISMATCH served-id-mismatch`
   on the python-free rows of **both** revs and `MODEL_OK matched` on both python3 rows.
5. `PATH=$S/pbin /usr/bin/python3 tests/probe-verdicts/check.py --probe {b,m}.sh` (probe python-free, harness has python3)
   → exit **1** both; `tests=77 passes=55 failures=22` both; the two outputs are byte-identical (`cmp` clean), so the
   python-free failure *set* does not move between B and M.
6. `bash tools/test-snapshot.sh` under the python-free PATH → exit **1**, `FAIL missing dependency: python3`.
7. Paired suite timing, 5 runs/rev for the snapshot suite, 3 runs/rev for the verdict matrix (`snapshot-timing.out`,
   `timing.out`): `test-snapshot.sh` B median 1949 ms, M median 2109 ms (ratio 1.08, load1 36.4–40.8);
   `check.py` B median 45.30 s (45.53/45.30/42.86), M median 43.03 s (45.97/43.03/43.01), ratio 0.95 (load 23–34).
   All runs `pass=30 fail=0` / `tests=77 passes=77 failures=0`, exit 0.
8. Per-cell probe latency, 5 runs, first discarded (`budget-M.out`, `budget-B-P1.out`, load1 28–29): 200 000-id answer
   M median 1335 ms python3 / **698 ms python-free** (base: killed at 120 s in both modes); single id M 114 ms / 41 ms,
   B 138 ms / 43 ms.
9. `git -C <lane> show 9a41912a…|3decfa36…:tools/round91-answer-time.py | sha256sum` → `5d0fe009…` at the freeze commit,
   at M and in the working tree (counter unchanged, C1 K3 not triggered); probe bytes at M equal the working tree.

## Findings

**F1 — M holds on the python-free path; no harm pair exists.** Verdict pairs (base → M): T1 *killed@120 s → MODEL_OK
matched 0.49 s*; T4 *killed → MODEL_OK matched 1.00 s*; P2 *MODEL_OK 0.03 s → MODEL_OK 0.03 s*; P4 *MODEL_MISMATCH →
MODEL_MISMATCH*; P5 *MODEL_MISMATCH → MODEL_MISMATCH*. Base-right/M-wrong: none. The one-line counter summary moves
7 mismatches → 2, both remaining mismatches present at base too. Evidence: `m-nopy.out`, `b-nopy.out`. **NOTE.**

**F2 — DEFECT (pre-existing, identical at B and M): the python-free id matcher cannot decode `\uXXXX` escapes or a
quoted id, so it false-reds two of the counter's own positive cells.** On the python-free path `served_ids()` falls back
to `grep -aoE '"id"…"[^"]*"'` (`tools/kama-probe.sh:427-436`) which returns the JSON *text*, not the decoded string:
P4's body is `"modele-\u00e8-\u65e5\u672c-\u00fc"` (the counter serialises with `ensure_ascii`) and P5's id is
`"q\"b\\\\s"`. A real server emitting raw UTF-8 is fine — u1 grades `MODEL_OK matched` on all four combos
(`probe-matrix.out`) — so this is not a model-server false red in the common case, but it *is* a false red for any id
containing `"` or `\`, which JSON can only carry escaped. Consequence for the claim: the frozen C1 predicate
(`positive_mismatches=0`) is reachable only with `python3` on the probe's PATH; on a python-free PATH the counter prints
`positive_mismatches=2` and exits 1 **at M as well as at base**. Not M's doing (`served_ids` is unchanged between B and
M), not graded harm by §C1 held-out rule, but the counter cannot distinguish "python-free path" from "harm" and a runner
on such a host would read a false RED. **DEFECT.**

**F3 — DEFECT (pre-existing, identical at B and M): the python-free probe answers `MODEL_OK matched` for a router entry
whose model file fails to load.** `check.py` row `RouterUnloaded.router-unloaded-failed` prints
`verdict=MODEL_OK reason=matched exit=0 (expected MODEL_UNLOADED/router-unloaded-failed/2)` when the probe runs without
python3 (`verdicts-nopy-*.out:74`); 22 of 77 rows fail python-free, all documented degradations, and the set is
byte-identical at B and M. Operationally: a python-free host gets a false green on a broken router model, which is the
one direction this lane treats as worst. Base-equal, so not a round-91 regression. **DEFECT.**

**F4 — NOTE: neither harm suite can see the python-free path.** `tests/probe-verdicts/check.py` is python and
`tools/test-snapshot.sh` exits 1 with `FAIL missing dependency: python3` (`tools/test-snapshot.sh:8-11`), so K2's
77/77 + 30/0 is a python3-present statement; the M probe's python-free code path (the awk `AWK_NORM` pass when `grep`
feeds it, the `paste -sd,` join) is graded by no registered suite. Evidence: command 6, command 5. **NOTE.**

**F5 — NOTE: no measurable suite regression between B and M, but both suites are start-up dominated.**
`check.py` M/B = 0.95 (M faster), `test-snapshot.sh` M/B = 1.08 with a ±30 % run-to-run spread at load1 36–41
(1785–2658 ms); the snapshot suite's 30 probe spawns, not the probe's own work, dominate. Evidence:
`snapshot-timing.out`, `timing.out`. This is the r89 D3 "1.8× with no persisted budget" gap, quantified: a future
slowdown of the probe body would be invisible in either suite's total.

**F6 — NOTE (improvement, not a regression): M is also faster than B on the *python3* plain cell** (114 ms vs 138 ms
median, 5 runs each, load1 28–29) and ~2× faster python-free than python3 on the 200 000-id answer (698 ms vs 1335 ms),
because the single awk pass replaces the JSON parse for the match decision. Evidence: `budget-M.out`, `budget-B-P1.out`.

**F7 — NOTE: the frozen counter bytes are unchanged** (sha256 `5d0fe009…` at F, M and the working tree), so the C1
predicate I quote is the one frozen in the claims commit (C1 K3 not triggered). Evidence: command 9.

## Deliverables (all under `.ufo/waves/round-91/w1/out/EX02NoPythonPath/`)

- `m-nopy.out` / `b-nopy.out` — full 12-cell counter at M and base with python3 hidden.
- `m-py.out` — 12-cell counter at M with python3 present (exit 0), load noted.
- `probe-matrix.out` + `probe_matrix.py` + `stub.py` — raw-UTF-8 vs escaped vs quoted id bodies × {B, M} × {py, nopy}.
- `verdicts-nopy-b.out`, `verdicts-nopy-m.out`, `fail-b.txt`, `fail-m.txt` — 77-row matrix with the probe python-free.
- `budget-M.out`, `budget-B-P1.out` — per-cell probe latency, 5 runs, load1 recorded.
- `snapshot-timing.out`, `timing.out` — paired suite wall times at B vs M.
- `latency-budget-proposal.md` — the persisted line, its command, bound arithmetic and load/relative rules.
- `repro.sh` — exact commands (python-free PATH construction included).

VERDICT: holds — on the python-free path M turns the two killed large-answer cells into MODEL_OK in ≤1.14 s with no base-right/M-wrong pair, and the two remaining positive mismatches (escaped-unicode, quoted id) are byte-identical at base; they are a pre-existing fallback limitation the proposed budget line now covers explicitly.
