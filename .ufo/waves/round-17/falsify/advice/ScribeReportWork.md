VERDICT: n/a — drafting seat; attacks no claim; cross-checks the report's numbers against stored round-17 artifacts only (no lane tool or gate rerun).

Scope: round 17, lane commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (short `54a2926`, lane HEAD). Start `cff9e62`. Sources: `corpus/lessons/round-17.md`, `LOG.md` §round 17 (lines 992-1025), `SCORECARD.md` §Round 17 (lines 645-708), raw outputs under `.ufo/waves/round-17/runs/` and `.ufo/waves/round-17/live/`.

## Work performed

Two declared claims, one axis each. Both are bounded repairs of the lane's own instruments; neither is a capability row.

### C1 — calibration (declared; calibration 7 → 7, delta 0)

- **Claim.** `SKILL.md:533` said `tests/probe-verdicts/check.py` "grades verdict, reason, exit and drift". No detector could fail those gradings (round-16 mutants 5/5 survived), `served_model` and the `GET /v1/models` route were recorded but not graded, and a valid-JSON non-object probe row ended in an uncaught `AttributeError` (exit 1, not the documented exit 2). Source: `corpus/lessons/round-17.md:15-25`; `SCORECARD.md:654-657`.
- **Repair.** `tests/probe-verdicts/check.py` grades `served_model` (`expected_served_model`, line 339, derived from each row's own `/v1/models` body) and the route (`models_route`, lines 329-331; route use at 365), and records malformed or non-UTF-8 probe output per row. Detector: `tests/probe-verdicts/fault-controls.py` (header lines 20-38: F0 identity control, F1-F8 one corruption each). Mutant grid: `.ufo/waves/round-17/c1/mutants.py --grid`.
- **Stored measurements** (not rerun):
  - Fixed detector, frozen check.py (sha `b853576e…`): `detected 5, accepted 3` (F5 served_model, F6 route skip, F8 malformed), exit 1. Source: `.ufo/waves/round-17/runs/fault-controls-frozen.json`, `…frozen.exit`.
  - Fixed detector, current check.py (sha `ddc3f3cc…`): `detected 8, accepted 0`, exit 0. Source: `.ufo/waves/round-17/runs/fault-controls-current.json`.
  - Mutant grid totals, `.ufo/waves/round-17/runs/mutants-grid.json` (`cells[].totals`): pair/frozen killed 1 of 8 applicable (M9 reject-all only); full/frozen 7 of 8 (M8 `malformed-output-passes` survives); pair/current 1 of 10; full/current 10 of 10.
- **Limit (stated by the lane, confirmed by the grid).** The round-16 pair detector cannot kill any field-deleting mutant on either gate. Under pair/current, M6 `ignore-served_model` and M7 `ignore-route-match` survive; the gain is the fixed-detector accepted count (3 → 0), not the pair detector's kill count. `SCORECARD.md:663-665` says the same.

### C2 — operability (declared; operability 8 → 8, delta 0)

- **Claim.** Receipt v1 checks could not fail on the misbehaviour they named: a degraded `/health` body passed; `teardown_exited` passed on any returncode; `teardown_port_closed` was vacuous; the loading envelope was recorded but graded by nothing; a teardown exception escaped without a receipt. Source: `corpus/lessons/round-17.md:31-42`; `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md` (cited there).
- **Repair.** `tools/kama-llamacpp-live.py` emits `kama-llamacpp-live/v2` (`SCHEMA`, line 50): exact `/health` body, `teardown_graceful` on harness SIGTERM to a live child (`TERM_GRACE = 10.0`, line 73; SIGKILL only after grace), ownership-gated port closure, `loading_envelope_graded` over every stored 503 body, a receipt on internal fault. Gate: `tests/llamacpp-live/check-receipt.py` v1+v2. Controls: `tests/llamacpp-live/controls.py`. Source sentences: sources S042-S044 in `corpus/SOURCES.md` lines 54-56.
- **Stored measurements** (not rerun):
  - Frozen tool+gate: `accepted_bad 6`, `inconclusive 1`, `gate_flip_bad 0`, exit 1. Source: `.ufo/waves/round-17/runs/controls-frozen.json`, `…frozen.exit`.
  - Current tool+gate: `accepted_bad 0`, `inconclusive 0`, `gate_flip_bad 0`, exit 0; each bad control fails its targeted check (k1: `failed_checks: ["health_ready"]`, `gate_exit 1`). Source: `.ufo/waves/round-17/runs/controls-current.json`.
  - Real b11755 runs: `.ufo/waves/round-17/live/receipt-1.json`, `receipt-2.json`, `receipt-3.json` each `schema: kama-llamacpp-live/v2`, 11 checks all `True` (receipt-1: `health_ready`, `teardown_graceful`, `teardown_port_closed`, `loading_envelope_graded`, plus 7 others), `setup_error: null`, `internal_fault: null`, `port_listener_ownership: "child"`. Gate: `.ufo/waves/round-17/live/gate.txt` — `VALID` ×3 with probe `36b64978…`, tool `0efd1723…`.
- **Evidence gap (see Findings F2).** `live/run-N.stdout` and `run-N.stderr` are 0 bytes and no tool exit file exists. The lesson's "each exit 0" (`corpus/lessons/round-17.md:171`) rests on the gate's own exit (`gate.txt`) and the receipt's null error fields, not on a stored tool exit.

### Process and frontier work landed with the claims

- **Sources.** `corpus/SOURCES.md` rows 41 → 46 (new S042-S046; S041 untouched). Counted: tiers A 43 / C 3; status mined 36 / queued 5 / rejected 5. Append-only guard: `tools/sources-append-only.py` (433 lines, new). Validation output in `.ufo/waves/round-17/sources-before-validate.txt`: one W04 warning (S031 duplicate URL, pre-existing), `validate exit=0`.
- **Quality rules.** KQ20-KQ22 at `corpus/QUALITY.md:114-122`.
- **Mined mistakes.** M1-M7 at `corpus/lessons/round-17.md:83-91`; M1 (S041 edited in place) is the one with the new mechanical guard.
- **Build wave.** 82 seats dispatched and completed, 0 failed (`.ufo/waves/round-17/build/completion-summary.json`); first-line verdicts `confirm 34 / partial 32 / refute 1 / n/a 15 / nonconformant 0` (`.ufo/waves/round-17/build/verdict-counts.json`). Matches `LOG.md:1008`.
- **No-harm** (stored outputs): probe `36b64978…` unchanged (`sha256sum tools/kama-probe.sh`); `git diff --stat cff9e62 54a2926 -- tests/probe-verdicts/*.json tools/kama-probe.sh` empty (matrix bytes and probe unchanged); `runs/noharm-test-snapshot.txt` `RESULT pass=30 fail=0` exit 0; `runs/noharm-r16-measure-clone.txt` `result: PASS`, `measure exit=0`; `runs/v1-receipts-current-gate.txt` round-16 v1 receipts `VALID`; `runs/selftest-tests_probe-verdicts_check.py_--selftest.txt` `tests=72 passes=72` and `5/5 malformed tests rejected`; `runs/selftest-check-receipt.txt` `39 mutations + unreadable case all rejected`.
- **Discernment.** No non-author admit/reject sample exists for round 17 (`corpus/lessons/round-17.md:182-183`). [L1 fills after falsify]

## Landed changes

Each row is a path in commit `54a2926` (`git show --stat 54a2926`), tied to the `LOG.md` §round 17 "Landed" bullet (lines 1011-1019) unless marked.

| Change | Path (lane commit `54a2926`) | Diff size (commit stat) | LOG.md §round 17 tie |
|---|---|---|---|
| C1 graded `served_model`, route, malformed output | `tests/probe-verdicts/check.py` | 198 +/- | 1011-1012 |
| C1 fault-control detector F0, F1-F8 | `tests/probe-verdicts/fault-controls.py` | +815 | 1012 |
| C1 mutant grid (M0-M9) | `.ufo/waves/round-17/c1/mutants.py` | +1341 | 1013 |
| C2 receipt v2 tool | `tools/kama-llamacpp-live.py` | 609 +/- | 1013 |
| C2 gate v1+v2 | `tests/llamacpp-live/check-receipt.py` | 292 +/- | 1014 |
| C2 fake-server controls K0-K8 | `tests/llamacpp-live/controls.py` | +700 | 1014 |
| SOURCES append-only guard | `tools/sources-append-only.py` | +433 | 1015-1016 |
| Round-13 gate exit 4 (`worktree_not_at_measured_revision`) | `.ufo/waves/round-13/measure.py` | 166 +/- | 1015 |
| Strict first-line verdict counter | `.ufo/waves/round-17/count-verdicts.py` | +288 | 1016 |
| Provenance counter v2 | `.ufo/waves/round-17/dispatch-provenance.py` | +969 | 1016 |
| SOURCES S042-S046 | `corpus/SOURCES.md` | +20 | 1016 |
| KQ20-KQ22 | `corpus/QUALITY.md` | +14 | 1016-1017 |
| Appended corrections (OPTIONS wording, graded-check supersession) | `corpus/README.md` (+17), `corpus/knowledge/endpoint-identity.md` (+2), `corpus/knowledge/runtime-health-surface-matrix.md` (+2), `corpus/knowledge/llamacpp-loading-lifecycle.md` (+63), `SKILL.md` (+32/-) | as stated | 1017 |
| Lesson record | `corpus/lessons/round-17.md` | +183 | (this round's lesson, not a LOG bullet) |
| Lane VCS hygiene | `.gitignore` (+2: `.ufo/state/`, `__pycache__/`), `AGENTS.md` (+1, VCS rule) | 2 / 1 | 1018-1019 |
| Install disclosure | `PROVINCE.md` (+13, "Round-17 note") | 13 +/- | **not in LOG.md §round 17** (Finding F4) |
| Pointer edit | `SHONEN.md` (+2/-1, author-assertion line) | 2 +/- | **not in LOG.md §round 17** (Finding F4) |
| Round record | `LOG.md` (+35), `SCORECARD.md` (+65) | 35 / 65 | the entry itself |
| Frozen pre-round copies | `.ufo/waves/round-17/frozen/` (manifest + 5 files) | +37 manifest; 5 copies | 1011 ("frozen") — cited by `corpus/lessons/round-17.md:9-11` |
| Live receipts and gate output | `.ufo/waves/round-17/live/` (`receipt-1..3.json`, `gate.txt`) | 597 lines each | 1022-1023 |
| Measurement outputs | `.ufo/waves/round-17/runs/` | — | 1020-1024 |

Installs: none in this seat. Lane commit includes no tool installation record beyond `PROVINCE.md`'s note on the operator-owned llama.cpp archive (`~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`, sha256 `753bfa73…e226`).

## Findings (advice to L1; path:line + evidence)

- **F1 — verified, no defect.** Both declared headline counts reproduce from stored artifacts: fixed-detector accepted faults 3 → 0 (`runs/fault-controls-{frozen,current}.json`); controls accepted-bad 6 → 0 (`runs/controls-{frozen,current}.json`); mutant grid 1/8, 7/8, 1/10, 10/10 (`runs/mutants-grid.json` `cells[].totals`); receipts 11/11 `VALID` (`live/gate.txt`). Source counts: SOURCES 46 rows; build verdicts 34/32/1/15/0.
- **F2 — evidence gap, C2.** `corpus/lessons/round-17.md:171` "each exit 0" and `SCORECARD.md` §Round 17 `kama-llamacpp-live.py ×3` have no stored tool exit (`live/run-1..3.stdout/stderr` are 0 bytes; no `.exit` file under `live/`, unlike `runs/`). Gate exit 0 is recorded (`live/gate.txt`). [INFERENCE] tool exit 0 follows from the receipt's null error fields, not from observation. Fix: store the tool exit beside the receipts.
- **F3 — dangling pointer.** `SCORECARD.md:674-675` says the measured tree is "hash in `LOG.md` §round 17". `LOG.md:992-1025` contains no commit hash (`grep -n 54a29 LOG.md` empty; the entry records start `cff9e62` only). The measured revision is recoverable only from git (`54a2926`). Fix: record the hash in LOG.md or correct SCORECARD.md's pointer.
- **F4 — LOG omissions.** `PROVINCE.md` (+13, install-disclosure note, routed defect 5 in `corpus/lessons/round-17.md:116-120`) and `SHONEN.md` (+2/-1 author-assertion line) changed in `54a2926` but are not in `LOG.md:1011-1019`. The install note is also not in LOG's install list.
- **F5 — stale v1 self-test count, not superseded.** `SKILL.md:533` (v1 row) says `--selftest: … 4 malformed tests rejected`; `runs/selftest-tests_probe-verdicts_check.py_--selftest.txt` reports `5/5 malformed tests rejected`. The appended §Round-17 correction block (`SKILL.md:555-566`) lists five superseded statements (verdict/reason/exit/drift grading; exit-2 scope; "0 all 10 checks pass"; gate "10 check ids"; round-13 row exit 4) and does not list the self-test count. [INFERENCE] an unlisted drift in the same row; L1 to decide whether it needs an appended line.
- **F6 — unverified lesson sentence.** `corpus/lessons/round-17.md:162-163` says the full-detector frozen survivor M8 "crashes on that input either way". The grid records M8 as `survived` (`runs/mutants-grid.json`, full/frozen); the crash claim was not checked in this seat. [L1 fills after falsify]
- **F7 — no mechanical guard for M6/M7 recurrence.** Kept as stated by the lesson (`corpus/lessons/round-17.md:90-91`); not a new finding.

## Limitations

- Read-only over the lane (`git show`, `grep`, `sha256sum`, `git diff --stat`, JSON reads). No lane tool, gate, or count was rerun; every number is from a stored artifact cited by path.
- Commands and exit codes in this seat: `ls`, `git log`, `git show --stat 54a2926` (0), `git -C … rev-parse HEAD` (0), `grep -n` over LOG/SCORECARD/SKILL/SOURCES/corpus (0 or 1 for no match), `python3` read-only JSON and row-count probes (0), `sha256sum tools/kama-probe.sh` (0), `git diff --stat cff9e62 54a2926 -- tests/probe-verdicts/*.json tools/kama-probe.sh` (0, empty).
- One unintended write: a placeholder file was created at the fleet root `/home/vgpnk/Projects/shokunin/kama-lane-placeholder` during this seat's tooling, and was removed (`rm -f`, verified absent). No other fleet-root or sibling-lane write. Recorded for the L1 misroot sweep (LOG M6).
- Scratch: none created in `/tmp`; nothing to remove.
- Installs: none.
- Not checked: no outside non-author spot-check exists (`corpus/lessons/round-17.md:182-183`); no independent verification of the falsify seats' results. [L1 fills after falsify]
