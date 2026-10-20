# Round 17 — graded fields backed by failing detectors; fail-capable live checks

Steered round 17, 2026-10-20 (hyaku phase 2, jj-colocated lane). Starting
revision `cff9e62f05aa7cfb9059444f62eb787100719713`; initial `git status
--porcelain` was empty; no `lane-dead-no-report kama round=17` line in
`.ufo/watchdog.log`, so nothing was inherited. Assignment: operability +
calibration (`../shokunin.conf:52`); calibration 7 is the lowest assigned axis
(operability 8); no stagnation waiver (a capability entered at round 16).
Pre-round copies of every file this round changes are frozen byte-for-byte in
`.ufo/waves/round-17/frozen/` (`manifest.json`, captured with `git show
cff9e62:<path>`).

## Declared claims

- **C1 calibration — the verdict-matrix gate claimed gradings no detector could
  fail.** `SKILL.md:533` said `tests/probe-verdicts/check.py` "grades verdict,
  reason, exit and drift" and maps harness errors to exit 2. Round 16's
  mutation seat showed all five grading-weakening mutants survive the only
  detector (the 55/17 vs 72/0 pair), and a sixth (ignore-verdict) survives it
  too (`build/advice/ReviewCheckPyClaims.md` F1). `served_model` and the route
  were recorded but never graded, and a valid-JSON stdout whose first row is not
  an object raised an uncaught `AttributeError` (traceback, exit 1, matrix
  aborted) — the exit-2 promise was false. The lane's statement about its own
  instrument did not match what the instrument could show. Repair: check.py
  grades `served_model` (derived from each row's own literal `/v1/models` body
  with the probe's `served_ids()` precedence) and the `GET /v1/models` route,
  and records malformed or non-UTF-8 probe output per row; a fault-control suite
  (`tests/probe-verdicts/fault-controls.py`, F0 identity control plus F1–F8 one
  corruption each) is the detector; `mutants.py --grid` reports both gates under
  both detectors. The nine matrix files and the probe stay byte-identical.
- **C2 operability — fail-capable live lifecycle checks (sourced).** Receipt v1
  checks could not fail on the misbehaviour they named
  (`.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md`): a degraded
  `/health` body passed; `teardown_exited` passed on any returncode, including a
  self-exit or a SIGKILL; `teardown_port_closed` was vacuous; the loading envelope
  was recorded and graded by nothing; a teardown exception escaped without a
  receipt. Repair: receipt `kama-llamacpp-live/v2` with `health_ready` on the
  exact body (S042), `teardown_graceful` on harness SIGTERM to a live child with
  returncode 0 and no SIGKILL (S043, S044), ownership-gated `teardown_port_closed`,
  `loading_envelope_graded` over every stored 503 body, and a receipt on internal
  faults; the gate re-derives every v2 check and still validates v1 receipts;
  `tests/llamacpp-live/controls.py` counts accepted-bad fake-server controls.

**Separation criterion** (written down because the claims share a principle,
`build/advice/CriticAxisSeparability.md` F6): C1 changes the lane's own
measuring instrument and corrects a false self-description (calibration); C2
changes which server and harness behaviours the capability rejects
(operability). C1 never touches the live tool, its gate or the probe; C2 never
touches check.py or the matrix; `tools/kama-probe.sh` is byte-identical
(`36b64978…`) at start and end, so each claim verifies with the other reverted.
C2 adds no capability row: `live-llamacpp-lifecycle` (round 16) is hardened,
not new.

## Gate

All sources opened 2026-10-20. Quotes are verbatim and at most 25 words.

| Candidate | Decision | Source, location, quote |
|---|---|---|
| The `/health` 200 body is exactly `{"status":"ok"}` (compare parsed JSON) | admit (S042) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp line 5297 `res->ok({{"status", "ok"}});`; line 5289 "error and loading states are handled by middleware" |
| Grade the README bytes `{"status": "ok" }` | reject | README:489 spacing differs from the compact wire body (15 bytes, observed by `ProbeHealthBody.md` and S046); a byte compare would fail a correct server |
| A first SIGTERM after handler install ends in `return 0` | admit, scoped (S043) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp line 575 "this call blocks the main thread until queue_tasks.terminate() is called"; line 590 `return 0;` |
| A second signal exits 1 | admit (S043) | server.cpp lines 33-34 "Received second interrupt, terminating immediately." then `exit(1);` |
| "Graceful exit 0 is documented" | reject | the README documents no exit status (S035 lines 479-490); the claim is code-derived (`CriticSourcedClaim.md`) |
| Returncode 0 alone proves the harness signal caused the exit | reject | any SIGTERM sender ends the same way; the receipt binds the harness by a fresh poll before `killpg`, `sigterm_sent` on delivery and child ownership |
| Negative returncode = death by signal N | admit (S044) | https://docs.python.org/3.14/library/subprocess.html#subprocess.Popen.returncode "A negative value -N indicates that the child was terminated by signal N (POSIX only)." |
| Cite the `/3/` Python docs page | reject | `/3/` now serves 3.15.0; the host runs 3.14.8 (`ScoutPythonReturncode.md`) |
| A killed mutant is one a test caught | admit, vocabulary only (S045) | https://pitest.org/quickstart/basic_concepts/ §Running the tests "Killed means a test caught the mutation successfully." |
| Jia & Harman TSE survey as the definition row | reject | publisher page paywalled; the quotes came from a technical report, and a survey would be `paper` tier B, not A (`ReviewCorpusContractRules.md` F4) |
| Live v2 receipts as own-work row | admit (S046) | receipt-1 check `teardown_graceful` observed `{"alive_at_teardown_start": true, "returncode": 0, "sigkill_sent": false, "sigterm_sent": true}` |
| A green v2 receipt proves registered-consumer health | reject | ports 40089, 43091, 38545 are lane-owned; `registry/history/latest.tsv` still lists all three consumers `DEAD`; 8080/34113 untouched |
| A newer llama.cpp build changed these surfaces | reject (checked) | b11756/b11757 change only CUDA files and `server-chat.cpp`; `server-http.cpp`, `server-context.cpp`, `server.cpp` byte-identical (`ScoutLlamaNewerReleases.md`) |

Row changes: new S042–S046. No `status`, `recheck` or `used-by` cell of an
existing row changed, and no immutable cell of any row changed
(`tools/sources-append-only.py`, §Measurements). The v2 receipts' in-file
`source_binding` entries with `row: null` are the spans S042
(`server-context.cpp` 5288-5299) and S043 (`server.cpp` signal path); the rows
did not exist when the tool was written.

## Mistakes

| ID | Class | Evidence pointer | Captured-by | Fix / failure obligation |
|---|---|---|---|---|
| M1 (mined) | append-only registry violation: S041 `anchor` and `teaches` rewritten in place after the row's first commit | `corpus/SOURCES.md:53`, `git diff b8e485c ccc4bb3` (anchor `13:49:38…, port 32845` → `14:06:27…, port 37527, tool sha256 b8c5e8d4…`; teaches gained the loading-envelope sentence); disclosed only in prose (`round-16.md:147-149`); the full pairwise sweep finds no second violation (`build/advice/ReviewSourcesHistoryRule2.md`) | none mechanical: contract rule 2 (`CORPUS.md` §SOURCES Rules 2) existed, the census checks shape only, and a base-to-tip diff shows an added-then-edited row as one addition; caught by the non-author spot-check (routed defect 3) | `tools/sources-append-only.py` + KQ22. Shown able to fail: `--from b8e485c --to ccc4bb3` → exit 1 naming S041 `anchor` and `teaches`; `--from ccc4bb3 --to master` → exit 0 |
| M2 | gate-overclaim class: a gate documents gradings no input can make fail | seven instances rounds 11-16 (`build/advice/RevengerPlannerWalk.md`); this round's two (C1, C2); every one was admitted with fail-capability routed as debt | none — fail-capability was never an admission condition | KQ20 and KQ21; shown able to fail by the frozen arms: frozen check.py accepts 3/8 faults, frozen tool+gate accept 6/8 bad controls |
| M3 | summary miscount: round-16 falsify `verdict_first_lines` 36/41/2 | a keyword scan of the first line containing `VERDICT` anywhere, with refute-word priority (`build/advice/RevengerSummaryProducer.md`); strict first-line count is 34/40/0 + 5 nonconformant; the outside check's 36/43/0 is itself a relaxed count | the non-author spot-check (routed defect 2) | `.ufo/waves/round-17/count-verdicts.py`; shown able to fail on round-16 falsify (5 nonconformant listed); used for this round's summaries |
| M4 | provenance counter blind to async results: `spawned: 0` for 79 spawned seats | `.ufo/waves/round-16/falsify/provenance-ledger.json`; `dispatch-provenance.py:162-181` counted only literal keys and `status` values, while all 79 rows were `pending` (`build/advice/ScoutR16DispatchProvenanceBug.md`) | the non-author spot-check (routed defect 1) | `.ufo/waves/round-17/dispatch-provenance.py`; shown able to fail: the round-16 tool records 0, the round-17 tool records 79 on the same `spawn-result.json` (`.ufo/waves/round-17/provenance-0to79-demo.txt`). Residual: a refused attempt still records `refused: 0` for 82 per-task refusals (`build/provenance-ledger.json`) — open |
| M5 | L1 wave-context premises not re-checked | the build context said `registry/history/.lock` was not ignored (it is, `registry/history/.gitignore:3`, since round 2) and expected "36/43/0 + 5" (impossible: 84 > 79) | seats `ReviewSpotcheckDefectMap`, `RevengerSummaryProducer`, `ScoutJjLaneHygiene`, `ConnectMado` | before a routed premise enters a wave context, run its check (`git check-ignore -v`, a recount) and paste the output; this round's `.gitignore` adds only `.ufo/state/` (and `__pycache__/`) |
| M6 | seat write misroots and bound slips | `ScoutPythonReturncode`, `ScoutReceiptSchemaConsumers` and `RevengerS041Edit` first wrote reports at the fleet root and moved them (their disclosures); `ConnectKumitate` ran one recursive grep without the exclusion and printed three `interactive-sessions` lines (unused); `ConnectKake` read kake `corpus/knowledge/` beyond its bound | context clauses (absolute paths; exclusion flags) as detectors through disclosure only | L1 misroot sweep before the report found no remaining fleet-root file; M7 of round 16 recurred once despite exact exclusions — still no mechanical guard |
| M7 | L1 measurement invocation error | first `controls.py` runs with relative or shell-variable paths exited 2 (`tool not found`); discarded and rerun with absolute paths | the tool's own refusal | SKILL.md row says absolute paths |

## Routed defects from `round-16-verifier-spotcheck.md`

1. Wave provenance — every round-17 wave has a `validation.json` with a policy
   block (path, sha256, version `v2`, band) and one canonicalization
   (`ensure_ascii=False`, sorted keys, tight separators); the spawned-count bug
   is fixed (M4). The round-16 build digest `cdf02ba7…` reproduces only with
   `ensure_ascii=True`; it stays as recorded, declared here.
2. Falsify summary accuracy — corrected here: round-16 falsify strict first-line
   counts are **34 confirm / 40 partial / 0 refute / 5 nonconformant**
   (`ConnectSiblingCollision`, `ExecNoPythonFallback`, `ReviewLesson`,
   `ScribeNumbersLedger`, `ScribeReportWaves`); the recorded 36/41/2 came from a
   relaxed keyword scan (M3). Round-17 wave contexts require the `VERDICT:`
   first line, and `count-verdicts.py` reports nonconformant seats.
3. Append-only SOURCES — M1, KQ22 and the guard. S041 is left as committed; its
   old values are recorded in M1, and later receipts take new rows (S046).
4. Wording precision — appended corrections at the ends of `corpus/README.md`,
   `corpus/knowledge/endpoint-identity.md`,
   `corpus/knowledge/runtime-health-surface-matrix.md`, `SKILL.md` and
   `corpus/knowledge/llamacpp-loading-lifecycle.md` (OPTIONS excluded; type and
   code at server-http.cpp:319-320 beside message at 318). S036's cell is not
   edited; the existing end-of-file note in `SOURCES.md` already excludes OPTIONS.
   Not changed: `tools/kama-probe.sh:422-423` (comment) — editing the probe would
   move the probe digest both claims and round 16 pin; deferred, named here.
5. Install disclosure — report §Tool installs names
   `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 bytes, sha256
   `753bfa73…e226`, equal to the upstream asset) and states that no
   `/usr/bin/llama-server` exists (`ls` fails), so the PATH link shadows nothing.
   Install untouched; an L0 follow-up names the archive.
6. Carried debt — the five surviving check.py mutants, `served_model`, route
   match, malformed output, weak live checks and the teardown-fault escape are
   C1/C2. Still open: M3 of round 16 (harness `shutdown()` design — the backstops
   remain the 30 s and 600 s timeouts), M6 (no mechanical guard stops a seat
   running a measurement), matrix `why` line numbers, the one duplicate
   equivalence class and the frozen manifest's prior-exposure field (all need
   matrix bytes, which the round-16 digest pins).

## Routed jj-migration risks (`.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md`, `JjTrialKama.md`)

- R1, round-13 live gate false failure while the worktree is ahead of the
  measured revision — fixed in `.ufo/waves/round-13/measure.py`: divergence with
  every other check clean is now exit 4 `worktree_not_at_measured_revision`
  (could-not-evaluate); content failures stay exit 1. Selftest 13/13 (three new
  sandbox cases). Frozen copy `.ufo/waves/round-17/frozen/round-13_measure.py`.
- `.ufo/state/` not ignored — `.gitignore` now lists it (and `__pycache__/`,
  after seats' `py_compile` runs left `.pyc` files). `registry/history/.lock`
  was already ignored (M5).
- Lane VCS instructions — `AGENTS.md` VCS rule (helper only, cite `landed`/
  `pushed`, exit 3 recovery, detached-HEAD read rules, round-13 ordering).
- R2 unborn HEAD — not applicable: the lane has history.
- R3 silent empty jj commits — fleet-owned helper (it tracks paths and refuses
  empty diffs); the lane runs no hand jj commits.
- Round-16 `measure.py:116` parity (`--no-replace-objects`, GIT_* scrub) — not
  changed: it is the round-16 counting command, the hazard is latent (no replace
  refs, no GIT_* set, `ReviewR16MeasureParity.md`), and leaving it byte-intact
  keeps round 16 re-runnable as committed; this round ran it only in a `/tmp`
  clone.
- Old verifier lessons quoting `@{u}..HEAD` (rounds 11-15) — not edited (frozen
  history); the replacement forms are in `AGENTS.md`.

## Measurements (L1)

Commands run by L1 after wave 1 returned; outputs under `.ufo/waves/round-17/runs/`.

- C1 gate under a fixed detector: `python3 tests/probe-verdicts/fault-controls.py
  --check <check.py> --json` — frozen check.py (`b853576e…`): 5 detected, **3
  accepted** (F5 served_model, F6 route skip, F8 malformed), exit 1; current
  check.py: 8 detected, **0 accepted**, exit 0.
- C1 mutant grid: `python3 .ufo/waves/round-17/c1/mutants.py --grid --out
  .ufo/waves/round-17/runs/mutants-grid.json` — frozen/pair killed 1 of 8
  applicable (only reject-all), frozen/full 7 of 8 (M8 survives: the frozen gate
  crashes on that input either way), current/pair 1 of 10, current/full **10 of
  10**. The pair detector cannot kill any field-deleting mutant on either gate;
  the gate's own gain is the fixed-detector accepted count (3 → 0).
- C2: `python3 tests/llamacpp-live/controls.py --tool ABS --gate ABS --json` —
  frozen tool+gate: **6 accepted-bad** (K1, K2, K4, K5, K6 escape without a
  receipt, K8) plus 1 inconclusive (K3), K0 accepted; current: **0 accepted-bad**,
  0 inconclusive, each bad control failing its targeted check, gate-flip arm 0
  accepted.
- C2 real runs: three `tools/kama-llamacpp-live.py` runs on b11755, each exit 0,
  11/11 checks, gate `VALID` with model, server, probe and tool pins
  (`.ufo/waves/round-17/live/gate.txt`).
- No-harm: probe sha256 unchanged (`36b64978…`); matrix set digest unchanged
  (`bf9068d8…`, 9 files, 72 rows); `check.py --selftest` 72/72 + 5/5; round-16
  `measure.py` in a `/tmp` clone with the new check.py: PASS (55/17 → 72/0,
  exit 0); `test-snapshot.sh` 30/0 there; both round-16 v1 receipts `VALID` with
  all four pins and the frozen-probe receipt still exits 1 against the current
  probe pin; gate `--selftest` 26 v1 + 13 v2 mutations rejected; round-13
  selftest 13/13.

Discernment: no non-author admit/reject sample exists for this round yet; every
seat is lane-dispatched (LEARNING.md). Outside review remains pending.
