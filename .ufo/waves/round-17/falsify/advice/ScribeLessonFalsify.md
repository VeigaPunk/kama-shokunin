VERDICT: n/a — drafted the `## Falsify wave — dispositions` skeleton for the 80 seats in falsify/spec.json; no claim was tested and every disposition cell is blank for L1.

# Scope

Attacked: nothing. Task: enumerate the falsify seats from `.ufo/waves/round-17/falsify/spec.json` into a lesson skeleton with an empty disposition column. Lane commit at draft time: `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (`git rev-parse HEAD`). Lane status: `?? .ufo/waves/round-17/falsify/` (the wave's own untracked directory; nothing else dirty).

# Evidence for the counts

- `.ufo/waves/round-17/falsify/spec.json`: 80 items, 407 lines, 0 duplicate names, sha256 `96062a47f8b2958ce54e91cb065b65c279b4316dd516259817e9ca59d800cad9`. Item `name` lines are cited below as `spec.json:N`.
- Role mix of those 80 items (python over `items[].role`): reviewer 34, scout 8, critic 7, executor 6, connector 6, scribe 6, revenger 5, mutation-tester 4, sentinel 2, simplifier 2.
- `.ufo/waves/round-17/falsify/assignments.json`: 80 keys, equal to the spec names (set equality checked).
- `.ufo/waves/round-17/falsify/validation.json`: `counts.dispatch` spawn 80, resume 0, total 80; `tasks` 80; `exit` 0; policy band `waveMinLanes` 64 / `waveMaxLanes` 100.
- `.ufo/waves/round-17/falsify/advice/`: contains only `swarm-registry.json` at draft time. No seat report exists yet, so no disposition can be recorded from evidence.
- Precedent: `corpus/lessons/round-16.md:108` heads its section `## Falsify wave — dispositions (79 seats, 2026-10-20)`. Round-16 advice holds 80 entries (`.ufo/waves/round-16/falsify/advice/`), consistent with 79 seat files plus a registry [INFERENCE].
- Insert point: `corpus/lessons/round-17.md` has no dispositions section and ends at line 183 (`seat is lane-dispatched (LEARNING.md). Outside review remains pending.`, lines 182-183).

# Counting decisions for L1

- Fourteen of the 80 seats are not attack seats by their own prompts: six connectors (`spec.json:317`, `:322`, `:327`, `:332`, `:337`, `:342`), six scribes (`:367`-`:392`), two simplifiers (`:397`, `:402`). Their prompts compare sibling repos, draft report text, or propose deletions. [INFERENCE] L1 should count them in a separate group, not as falsify dispositions. Round-16's header does not split roles (`round-16.md:108`).
- Per-seat report path: the spec has no per-item report field. `spec.json:3` gives `reportDir` = `.ufo/waves/round-17/falsify/advice`. Round-16 files are named `<SeatName>.md`. Expected path per seat: `.ufo/waves/round-17/falsify/advice/<Name>.md` [INFERENCE].
- Disposition cells are intentionally blank. Marker: [L1 fills after falsify].

# Commands run (all from the lane, read-only, except the /tmp scratch)

| Command | Exit |
|---|---|
| `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD` | 0 |
| `git -C ... status --porcelain` | 0 |
| `ls -la .ufo/waves/round-17/falsify/ .ufo/waves/round-17/` (via bash) | 0 |
| `grep -rn --exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj -i "dispositions" corpus/lessons/` | 0 |
| `wc -l corpus/lessons/round-17.md`; `sed -n '183p'` | 0 |
| `sha256sum .ufo/waves/round-17/falsify/spec.json` | 0 |
| python3 JSON reads of spec.json, assignments.json, validation.json, role counts | 0 |
| `grep -n '^ *"name": "'` on spec.json; python name-to-line map written to `/tmp/ScribeLessonFalsify-scratch/seats.txt` | 0 |
| `ls .ufo/waves/round-16/falsify/advice`, `ls .ufo/waves/round-17/falsify/advice`, `sed -n '183p' corpus/lessons/round-17.md` | 0 |

The tool results did not print exit codes; "0" means the call returned output with no error.

No tool was installed or updated. No llama-server or port was touched. No `jj` or git write was run.

# Draft section (for corpus/lessons/round-17.md, insert after line 183)

## Falsify wave — dispositions (80 seats, 2026-10-20)

Source of seats: `.ufo/waves/round-17/falsify/spec.json` (items in order). Each row's attack summary is taken from that item's prompt. The Disposition column is blank until L1 integrates the seat reports. [L1 fills after falsify]

Fourteen rows (connectors, scribes, simplifiers) are not falsify attacks by their prompts; see Counting decisions above.

| # | Seat | Role | spec.json | Attacks (per prompt) | Disposition |
|---|---|---|---|---|---|
| 0 | RerunFaultFrozen | reviewer | :7 | Re-run fault-controls.py on frozen check.py; expect 5 detected / 3 accepted (F5, F6, F8). | |
| 1 | RerunFaultCurrent | reviewer | :12 | Re-run fault-controls.py on current check.py; expect 8 detected / 0 accepted; F0 identity; targeted conjuncts. | |
| 2 | RerunMutantGrid | reviewer | :17 | Re-run c1/mutants.py --grid in a clone; compare every cell with runs/mutants-grid.json. | |
| 3 | MutC1Preregistered | mutation-tester | :22 | Seat-written mutants H1-H4 of check.py (case-insensitive reason, strip, method-blind route, verdict-keyed served_model). | |
| 4 | MutC1Preregistered2 | mutation-tester | :27 | Seat-written mutants H5-H8 (normalised ids, stub-branch pass, rows[-1], two-row output). | |
| 5 | MutFaultControlsSelf | mutation-tester | :32 | Weaken the C1 detector (conjunct, exit rule, shared cache, F0 skip); does any output change? | |
| 6 | MutControlsSelf | mutation-tester | :37 | Weaken the C2 detector controls.py (exit-only rejection, attribution, gate-flip arm, K0 accepting -15). | |
| 7 | ServedModelOracle | critic | :42 | Circularity of the served_model expectation derived from the stub body; 401/503/name-only scratch rows. | |
| 8 | RouteMatchEdge | reviewer | :47 | Route conjunct: HEAD, query string, trailing-slash variants of /v1/models. | |
| 9 | MalformedNonUtf8 | reviewer | :52 | Malformed probe output (non-UTF-8, null row, string row, int verdict, 2 MB, trailing JSON) must be a per-row failure. | |
| 10 | TimeoutPath | reviewer | :57 | Hanging probe recorded as failure; no orphan processes; F7 duration. | |
| 11 | MatrixBytes | reviewer | :62 | Nine probe-verdicts JSON byte-identical to cff9e62; matrix digest bf9068d8; probe 36b64978. | |
| 12 | R16MeasureClone | reviewer | :67 | Round-16 measure.py in a clone; PASS 55/17 to 72/0 against runs/noharm-r16-measure-clone.txt. | |
| 13 | SnapshotClone | reviewer | :72 | test-snapshot.sh 30/0 and check.py --selftest 72/72 + 5/5. | |
| 14 | CheckPySelftestScope | reviewer | :77 | Selftest writes only under TemporaryDirectory; original malformed cases; SKILL.md "5 rejected" wording. | |
| 15 | C1AdmissionCritic | critic | :82 | Admission of C1 as a calibration claim; gate vs detector attribution of the before/after numbers. | |
| 16 | C1NumbersLedger | reviewer | :87 | Every C1 number in lesson, SCORECARD, LOG, SKILL against runs/*.json. | |
| 17 | ServedIdsMirror | scout | :92 | check.py served_ids_of() vs kama-probe.sh served_ids(), line by line. | |
| 18 | RerunControlsFrozen | reviewer | :97 | controls.py on frozen tool+gate; expect 6 accepted-bad, K3 inconclusive, K0 accepted. | |
| 19 | RerunControlsCurrent | reviewer | :102 | controls.py on current tool+gate twice; 0 accepted-bad; stability; leftover processes. | |
| 20 | LiveRerun | executor | :107 | Three live runs on b11755 with four pins; checks, loading counts, teardown fields. | |
| 21 | LiveUnderLoad | executor | :112 | Ten live runs under host load; any false failure of teardown_graceful or loading_envelope_graded. | |
| 22 | LiveFastLoad | executor | :117 | Twenty live runs; total_503_responses min/median/max; any run seeing zero. | |
| 23 | GateForgeries | executor | :122 | Forged v2 receipts (degraded health, rc -9/-15, sigterm_sent false, api-key in argv, others) against the round-commit gate. | |
| 24 | GateV1Compat | reviewer | :127 | v1 path of check-receipt.py vs frozen; round-16 receipts; gate selftest 26 v1 + 13 v2. | |
| 25 | TeardownCode | reviewer | :132 | teardown_graceful: fresh poll before killpg, sigterm_sent on delivery, ProcessLookupError, listening precondition. | |
| 26 | InternalFaultPath | reviewer | :137 | Every exception path in main(): receipt, group kill, handler restore, log removal, exit 2; BaseException escapes. | |
| 27 | LoopbackOwnership | reviewer | :142 | _listen_inodes / port_owned_by: false failures on ::1, 0.0.0.0, /proc/net/tcp6; refusal of foreign listeners. | |
| 28 | SourceBindingCheck | reviewer | :147 | Recompute source_binding span sha256 from pinned sources; line ranges; row:null entries mapped to S042/S043. | |
| 29 | DocStringsSources | reviewer | :152 | documented_by URL+line vs pinned copies; model_unchanged labelled as input integrity; KQ21. | |
| 30 | ControlsAttribution | reviewer | :157 | Literal expected-failed sets, substring attribution, gate-flip arm isolation, K3 determinism. | |
| 31 | ControlsSafety | sentinel | :162 | Read-only safety audit: loopback binds, registered-port refusal, pidfile guard, argv/env leakage, write scope. | |
| 32 | C2AdmissionCritic | critic | :167 | Admission of C2 as operability without a new row; 6 to 0 sufficiency; K0 realism; false-failure risk. | |
| 33 | C2SourcedClaim | critic | :172 | Do S042/S043/S044 support exactly the graded predicates; row-scope and teaches overclaims. | |
| 34 | ReopenS042 | scout | :177 | Re-open SOURCES row S042 cell by cell; lesson Gate quote verbatim. | |
| 35 | ReopenS043 | scout | :182 | Re-open S043 (server.cpp signal path) cell by cell; quote check. | |
| 36 | ReopenS044 | scout | :187 | Re-open S044 (Popen.returncode) cell by cell; page version; quote check. | |
| 37 | ReopenS045 | scout | :192 | Re-open S045 (pitest) cell by cell; killed/survived quote check. | |
| 38 | ReopenS046 | scout | :197 | Re-open S046 (own-work receipts) cell by cell; anchor and teaches numbers. | |
| 39 | CensusRerun | reviewer | :202 | sources-census.sh validate and manual census vs SCORECARD "41 to 46 (A 38 to 43, mined 31 to 36)". | |
| 40 | AppendOnlyPairwise | reviewer | :207 | sources-append-only.py over each consecutive commit pair cff9e62..54a2926; S041 pair exits 1. | |
| 41 | MutAppendOnlyGuard | executor | :212 | Mutants of sources-append-only.py (teaches change allowed, removed rows ignored, 8-column compare, blank-line parse). | |
| 42 | KQRowsReview | reviewer | :217 | QUALITY.md KQ20-KQ22: column shape, grounding, testable admit/reject, consistency with the tools. | |
| 43 | R13GateSandbox | executor | :222 | round-13 measure.py selftest 13/13; uncommitted QUALITY.md append gives exit 4 or 1. | |
| 44 | CountVerdictsRerun | reviewer | :227 | count-verdicts.py on round-16 falsify (34/40/0 + 5) and round-17 build (34/32/1/15/0). | |
| 45 | ProvenanceRerun | reviewer | :232 | 0-to-79 provenance demo; validation.json policy block; taskCall_sha256 recompute; refused:0 residual. | |
| 46 | GitignoreAgents | reviewer | :237 | .gitignore entries via check-ignore; AGENTS.md VCS statements; jj-lane.sh output and exit 3. | |
| 47 | MisrootSweep | scout | :242 | Read-only fleet-root and in-lane untracked/ignored file sweep for round-17 files. | |
| 48 | AppendOnlyDocs | revenger | :247 | Every deleted doc line between cff9e62 and the round commit; justification. | |
| 49 | MistakesTable | reviewer | :252 | Lesson ## Mistakes M1-M7: evidence pointers, captured-by, fail-capable claims; re-run M1 pair and M4 demo. | |
| 50 | RoutedDefects | reviewer | :257 | Lesson routed defects and jj risks vs round-16 spotcheck 1-6 and the jj-w1 reports; false reasons. | |
| 51 | OptionsCorrections | reviewer | :262 | Appended OPTIONS corrections (five files) vs server-http.cpp 300-360; line refs; residual "non-frontend" grep. | |
| 52 | KnowledgeAppendix | reviewer | :267 | llamacpp-loading-lifecycle.md §Round 17: each factual sentence vs S042/S043/S044/S046 and receipts. | |
| 53 | ScorecardRound17 | reviewer | :272 | SCORECARD §Round 17 numbers, deltas, capability statement, trend verdicts. | |
| 54 | SkillRound17Rows | reviewer | :277 | SKILL.md §Round-17 table: command spellings, exit maps, self-test counts, pins. | |
| 55 | ShonenProvince | reviewer | :282 | SHONEN.md box 2 pointer and PROVINCE.md note: numbers, paths, no [x], PATH statement. | |
| 56 | LogEntry | reviewer | :287 | LOG.md §round 17 bullets vs build completion, validation, attempts, verdict counts, git show --stat. | |
| 57 | ReportReadiness | scout | :292 | Report contract (kama-round-17.md §4, §6) vs lane evidence paths; flag missing evidence. | |
| 58 | SeparabilityNoHarm | critic | :297 | C1/C2 separability with the other reverted; probe digest; round-16 gates and round-13 exit table. | |
| 59 | TrendVerdicts | critic | :302 | SCORECARD trend verdicts (expansion, quality, discernment) vs LEARNING.md; any trade. | |
| 60 | MistakesFailCapable | critic | :307 | "Shown able to fail" claims for M1-M4 (run failing side); M5-M7 wording. | |
| 61 | SentinelWaveDiscipline | sentinel | :312 | Commit file list vs lesson; out-of-scope seat writes; committed __pycache__; round-16 run-*.json rewrites. | |
| 62 | ConnectTameshi | connector | :317 | Read-only compare of tameshi conventions with KQ20; what to hand off. | |
| 63 | ConnectKumitate | connector | :322 | Read-only compare of wave-provenance conventions with kumitate; what to hand off. | |
| 64 | ConnectSouji | connector | :327 | Overlap of KQ22 / sources-append-only.py with souji gates; what to hand off. | |
| 65 | ConnectKagi | connector | :332 | Receipt v2 argv/env handling vs kagi ownership; what to hand off. | |
| 66 | ConnectTsukuroi | connector | :337 | Operator-owned llama.cpp install footprint disclosure: accuracy and ownership. | |
| 67 | ConnectKaidoku | connector | :342 | source_binding span-hash conventions vs kaidoku; what to hand off. | |
| 68 | RevengerToolGrowth | revenger | :347 | Reconstruct growth of kama-llamacpp-live.py (1078 to about 1423 lines); silent v1 changes. | |
| 69 | RevengerCheckPyDiff | revenger | :352 | Every behavioural change in check.py vs cff9e62; loosened gradings; changes not in SKILL §Round-17. | |
| 70 | RevengerGateDiff | revenger | :357 | check-receipt.py diff: v1 logic identical; shared-helper effects on v1 outcomes. | |
| 71 | RevengerR13Diff | revenger | :362 | round-13 measure.py exit-4 change; committed round-13 evidence still true; SKILL:430 superseded. | |
| 72 | ScribeReportWork | scribe | :367 | Draft report sections "Work performed" and "Landed changes" (not an attack). | |
| 73 | ScribeReportMeasurements | scribe | :372 | Draft "Before → after measurements" and no-harm list (not an attack). | |
| 74 | ScribeReportSources | scribe | :377 | Draft "Sources & frontier" (not an attack). | |
| 75 | ScribeReportTrends | scribe | :382 | Draft "Trend verdicts" and SHONEN lines (not an attack). | |
| 76 | ScribeReportExtras | scribe | :387 | Draft stale-lane, installs, wave table, planner mapping, open L0 questions (not an attack). | |
| 77 | ScribeLessonFalsify | scribe | :392 | Draft this skeleton (not an attack). | |
| 78 | SimplifyC1Tools | simplifier | :397 | YAGNI review of fault-controls.py and c1/mutants.py; deletions with line ranges (not an attack). | |
| 79 | SimplifyC2Tools | simplifier | :402 | YAGNI review of the C2 tool, check-receipt.py, controls.py growth; deletions (not an attack). | |

[L1 fills after falsify]

# Limitations

- No seat has written a report yet (`advice/` holds only `swarm-registry.json`), so every disposition is unknown, not "confirmed" or "refuted".
- The per-seat `.md` path is an inference from the reportDir and round-16 naming, not a field in the spec.
- Attack summaries paraphrase each prompt's first sentence and acceptance clause; the prompts themselves are authoritative.

# Installs

None.

# Scratch

`/tmp/ScribeLessonFalsify-scratch/` (seat list). Removed before finish.
