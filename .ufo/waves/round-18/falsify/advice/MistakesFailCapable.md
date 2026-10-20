VERDICT: partial — every Mistakes-row fix is shown able to fail at its declared detector layer and no merely-promised test survives review, but both official counting commands still end exit 2 (corrected c2 counter never reran on real inputs; my clone rerun proves c1 only), M7's producer side has no fail-capable detector, and KQ23 remains prose-applied.

Seat: KamaR18.MistakesFailCapable (critic, round 18 FALSIFY). Respawn of the round-17 dead seat `MistakesFailCapable` (`corpus/lessons/round-17.md:198`). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`; paths below are relative to it unless absolute. Clone `/tmp/kama-r18-falsify-MistakesFailCapable`, `git switch -c seat/MistakesFailCapable 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; working tree clean for my runs; scratch `/tmp/kama-r18-falsify-MistakesFailCapable-scratch/` holds only `c1-measure.json`.

# A. Per-Mistakes-row fail-capability audit

"Shown able to fail" = a negative arm exists that fires for the stated reason, plus a positive arm proving the detector is not reject-everything (KQ20, `corpus/QUALITY.md:121`).

## M1 (round-17 M8) — control-path overclaim → KQ23: FAIL-CAPABLE, with bounded residuals

- Positive control: S047 admitted by the same in-memory predicate test (`RevKQ23FailCapable.md` §2-3: S047 P P P P P F → admit on A1–A5, limit A6). Negative: S043 rejected on exactly A3/A4/A5; targeted reset-omission mutant C1 rejected (A4 load-bearing). Blind case B1 caught the draft's own sufficiency overstatement ("ends the process with return 0" → necessary-condition wording). These are executed controls, not promises.
- Committed KQ23 (`corpus/QUALITY.md:132`) matches the third cleared draft: "every post-arming write to that state, including resets"; Reject column keeps "a necessary ordering condition becomes a guarantee". The reviewer residual R-L1 (windowless-claim dodge) is closed by the committed wording "a code-derived trigger→outcome claim … any interval in which a reset undoes the handler's effect".
- Residuals, honestly bounded: (a) KQ23 is applied by an author/human, mechanically unenforced — the same shape as every other KQ row; the lesson never claims otherwise. (b) Reviewer-opened U8 semantic floor (signal-unsafe calls in handler: `server.cpp:33-34` fprintf/exit, `server-queue.cpp:133` mutex; signal(7) arbitrary-thread delivery can relock `mutex_tasks` → POSIX-undefined) is carried forward only as the lesson's "unexamined shutdown calls, locking and platform signal assumptions limit any stronger termination guarantee" (`round-18.md:79-80`) — S047's Gate row and `SOURCES.md:59` `teaches` correctly stay necessary-only. (c) The B2 knowledge-entry overstatement is repaired by an appended §Round-18 correction (`corpus/knowledge/llamacpp-loading-lifecycle.md:232-237`), and B3's `used-by` omission is repaired in place: S047 used-by now `round-17.md, knowledge/…, lessons/round-18.md` (`SOURCES.md:59` cell 11), with the old→new disclosure at `SOURCES.md:191-193`.

## M2 — unobserved classified failed → KQ24 + tri-state: FAIL-CAPABLE

- Producer side: `tools/kama-llamacpp-live.py:1034-1105` `_selftest` asserts `_outcome_exit` mappings for pass/fail/not-evaluated(→exit 2)/setup-error, plus "setup-error must take precedence over false" — the BaseException-dominates-failure arm. Clone run: `python3 tools/kama-llamacpp-live.py --selftest` → `selftest: ok; closed tcp6 listeners ::1:39983, ::ffff:127.0.0.1:34971`, exit 0.
- Gate side: outcome re-derived (`check-receipt.py:1355-1368`): `setup_error|internal_fault → setup-error`; else any `passed is False → fail`; else any `passed is None → not-evaluated`; else pass — `elif` ordering makes a real failure dominate a null. The dominance arm exists and is exercised: `mut3("v3-models-capture-503-ids-intact", receipt=no_loading)` (`check-receipt.py:1896-1900`) leaves `loading_envelope_graded` null while a second check goes False; if the order were swapped (None before False) the derived outcome would equal the declared `not-evaluated` and the receipt would print VALID — so the mutation kills an order-swap mutant. Verified independently by sibling `GateModelsStatus.md` F1/F2 (green pristine exit 3, red mutation, byte-exact restore).
- Null-license rejections: `v3-unobserved-loading-missing-reason`, `v3-unobserved-loading-claimed-evaluated`, `v3-nonloading-check-is-null`, `v3-loading-check-null-although-503-present`, `v3-outcome-pass-with-null`, `v3-nonboolean-evaluated` (`check-receipt.py:1934-1964`); distinct non-zero exit 3 for NOT-EVALUATED vs 1 INVALID vs 2 unreadable (`:2103-2120`). Clone run: `check-receipt.py --selftest` → `5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`, exit 0.
- Real-world arm: k16 (zero-loading server, `controls.py:23`) classified `not-evaluated` in the official after arm (`runs/c1-self-mutants.json` baseline.current signature) and in my corrected rerun — the third outcome is exercised on a real control, not only synthetic.

## M3 — guessed tcp6 format → S048/S050 parser + live binds: FAIL-CAPABLE

- `tools/kama-llamacpp-live.py:311-326` `_tcp6_is_loopback` reverses each host-endian word (S048) and accepts `::1` or `::ffff:127/8` (S050). Selftest arms: two static proc rows positive (`…01000000`, `…FFFF00000100007F`), two negative (`…02000000` non-loopback, all-zero wildcard — the counterexample that broke the frozen parser, per `build/advice/ProbeTcp6Format.md`), plus live binds on real `::1` and `::ffff:127.0.0.1` listeners asserting inode discovery via `/proc/net/tcp6` and loopback re-parse (`:1053-1082`). A revert of the word-reversal fails the static-row assertion; a non-loopback acceptance fails the negative rows. Clone run green (above). `port_owned_by` (`:370-386`) is fail-closed for foreign/unproven, covered by gate mutants `ownership-unproven`, `v2-ownership-unproven-port-refuses`, `v3-teardown-port-close-unowned`.

## M4 — detector success while named weakening survives → survivor counter: FAIL-CAPABLE, but corrected counters have no official rerun

- Family arms in `runs/c2-survivors.json`: six H kills, three FC (killed/inconclusive/inconclusive under the old combine), two AO kills, refused-count correct82, three crash-fault handled. Frozen side shows survived/miscount/accepted on the same inputs — the before-arm failure is real, not promised. `fresh_wave2.included: false` with reason — separate denominator honored.
- The counters themselves shipped broken and proved it: official `c1-measure` exit 2 (`misclassified=1 but 0 row(s) classified misclassified` — the counter mis-cross-checked `classification` vs `bucket`); `c2-survivors` exit 2 on composite inconclusives (the "deliberately broken instrument" arm refused). This is the strongest kind of shown-able-to-fail: the instruments actually failed on real inputs.
- Repair `1c325b2`: `measure.py` cross-checks `misclassified` against row `bucket` with compatibility fallback (`measure.py:490-503,571-585`); regression fixture for the exact k16 rawbefore record (`:1409-1429`). `survivors.py` `combine_arms` reorders: killed dominates inconclusive (`:976-986`); selftest now has negative arms `(b) no targeted selftest kill plus main exit 2 stays inconclusive` and `(b) passing selftest plus main exit 2 remains inconclusive` — the new rule is itself fail-capable.
- Clone verification (mine, not official): `measure.py --selftest` 38/38 per `C1Measure.md` follow-up; my full c1-measure rerun on real controls exited 0, `faults: []`, counts `accepted_bad 5→0, good_rejected 1→0, misclassified 1→0, uncontrolled_checks 0→0, gate_flip_arms 16→17` — identical to the lesson's raw cells (`/tmp/…-scratch/c1-measure.json`). `survivors.py --selftest` in clone: `selftest: 60/60 checks passed`, exit 0 (43.3 s).
- **Residual (the round's largest):** `runs/` retains only the failed artifacts. `survivors.py` main mode took 1577 s officially and has never been re-executed at `1c325b2`; whether the repaired combine reports the FC arm correctly on real inputs is verified only by its 60-case selftest, not by a counting run. Sibling `LessonResiduals.md`/`ReportNumbers.md` reach the same gap. Smallest correction: run the two commands once more and retain new artifacts (per the lesson's own "corrected reruns are new artifacts" rule).
- **Minor semantics note:** under the repaired `combine_arms`, FC-f0gate's composite `killed` coexists with `main survived` in `why` — the main run's decision was identical to the unmutated tool's, so a reader scanning composite strings alone overstates the kill. Per-arm detail is retained, so this is a presentation seam, not a hidden survivor.

## M5 — prose-blind refusal count → dispatch-provenance: FAIL-CAPABLE

- `.ufo/waves/round-18/dispatch-provenance.py --selftest` 30/30 (clone re-run, exit 0): `refused text counts distinct task labels`, `mixed refused and spawned observations`, `spawned falls back to bullets`/`progress members`, `parseable-empty result → refused/spawned 0`, `existing validation refused, not clobbered`. The frozen counter reports 0 refused vs repaired 82 on the same committed round-17 input (`c2-survivors` family d: `frozen miscount → current correct, refused 82`) — a real before-arm failure, plus 0 spawned confirms no false-positive counting.

## M6 — source-URL mismatch hidden by synthetic selftest → full pinned path: FAIL-CAPABLE

- Gate re-derives each binding's `path` and `url` against `SOURCE_BINDING_EXPECTED` (`check-receipt.py:92-159`): `path="tools/server/server-context.cpp"` etc. is pinned, `url` must equal `LLAMA_RAW + path`, count must be exact, span_text sha256 and line count re-verified. A receipt that drops `tools/server/` now produces `source_binding[i].path/url … != pinned …` — the exact M6 defect is mechanically rejected, not just by the `v3-source-binding-tampered` mutation but by the whole-field comparison. The pre-fix failure is recorded (`round-18.md:91`, first real v3 run INVALID on five URL problems). Residual honesty: the producer emits what the gate pins (same constants `tools/kama-llamacpp-live.py:84-87` vs `check-receipt.py:84-87`), so the gate re-derivation is self-consistent rather than independently fetched — disclosed in the gate's own comment "does not fetch or independently authenticate upstream file bytes" (`:89-91`).

## M7 — ungraded /v1/models capture status → 200-required conjuncts: FAIL-CAPABLE at the gate; producer side not fail-capable

- Gate: `check-receipt.py:905-908` and `:931-934` require `captures.models.status == 200` for both identity checks, v3-only; named mutation `v3-models-capture-503-ids-intact` is the targeted negative; sibling `GateModelsStatus.md` F1/F2 executed green-pristine/red-mutant/byte-exact-restore.
- **Residual (importing sibling evidence):** the tool's `--selftest` never exercises check predicates, and no retained control drives a ready-state 503 with intact ids through the real tool→gate pipeline (`GateModelsStatus.md` F3/F4); the producer side of "tool and v3 gate now require" is asserted by inspection only. Smallest correction: a k9b-shape control (ready-state capture 503, ids intact) or a tool selftest fixture for the status conjunct.

# B. Routed R1–R7 audit

- **R1 S047 Gate row:** present (`round-18.md:41`), verbatim ≤25-word quotes, necessary-condition wording. Fail-capability: the row's wording was itself mutated twice (sufficiency draft → rejected by reviewer B1). Covered.
- **R2 KQ23:** per M1 — shown able to fail by recorded applications; not reject-everything (S047 accept arm, C5 satisfiable A6). Covered; prose-applied as designed (KQ14 human judgment).
- **R3 README pointer:** `corpus/README.md:249-253` appended paragraph names S047 and the supersession; the historical row at `:238` untouched. Covered.
- **R4 tri-state classifier:** per M2; producer `_outcome_exit` unit arms + k16 real control + gate mutations. Covered.
- **R5 six retained controls:** k9–k14 target previously uncontrolled checks (`controls.py:19-20,581-601`); before-arm `uncontrolled_checks 0→0` measures coverage (`runs/c1-measure.json`, my rerun identical); gate_flip_arms 16→17. Self-mutants `drop-gate-flip-arm`, `loosen-k0-exit`, `k6-any-nonzero` all `killed` in `runs/c1-self-mutants.json` with targeted selftest failures (`SELFTEST FAIL k0 tool exit -15…`, `k6 tool exit 1 is outside the exit-2 contract`) — the controls suite is shown able to fail. Residual: `GateModelsStatus.md` F4 shows no control drives the M7 shape through the real pipeline.
- **R6 gate trust-boundary list:** schema floor (mutations `schema-id-changed`, `v1/v2/v3-require-schema` arms — 3 VALID-floor rejections), exact argv (`v3-extra-server-argv-flag`, `v3-duplicate-server-argv-flag`, `argv-wrong-host`, `argv0-not-realpath`, `probe-argv-missing-check`, `v3-model-arg-does-not-match-argv` — last-wins S054 consistent), transition-body grading (`v3-transition-503-nonexact`, `-truncated`, `loading-observed-without-503-transition`, `v3-silently-dropped-257th-loading-body`), tcp6 ownership (M3), BaseException receipts (`v3-internal-fault-not-mirrored` + producer precedence arm), exact K6 exit (selftest `k6 tool exit 1/3/-15 is outside the exit-2 contract`, `k6-any-nonzero` mutant killed), Python-3.14 citation (S051 hierarchy in Gate row `round-18.md:47`). Compatibility: five legacy frozen/current receipt pairs + wrong-probe-pin exit 1 + snapshot-clone + r16-measure-clone all `as_expected: true` in `runs/commands.json`. Covered.
- **R7 detectors-of-detectors + provenance:** per M4/M5; check.py crash paths verified by `runs/checker-selftest.stdout` (60,000-level nesting and 5,000-digit integer rejected as row errors; `timeout_test` group-kill `alive_after_reap: false`; `fault-controls-selftest` escape `direct-kill survived=true, group-kill survived=false` — i.e., the kill is group-scoped and proven on both arms). Covered, minus the corrected-counter rerun residual above.

# C. The seven dead round-17 attacks — coverage now

Round-17's unreported seats (`round-17.md:194-198`; prompts in `.ufo/waves/round-17/falsify/spec.json`) → round-18 dispositions (`falsify/spec.json`, `falsify/advice/`):

| Dead seat (R17 attack) | R18 coverage | Status |
|---|---|---|
| C1AdmissionCritic (is before→after honest/attributable) | `C1Admission` critic | **Reported: confirm** — counters' exit-2 was a counter bug, disclosed and repaired; null never counted as acceptance |
| C2AdmissionCritic (real VALID runs, K0 from real shapes, healthy-server risk) | `C2Admission` critic | Dispatched; **no report yet** at my write time; partially covered by `LiveV3` (three pinned real VALID runs + NOT-EVALUATED zero-loading receipt) |
| C2SourcedClaim (S042/S043/S044 support the graded predicates) | `SourcedSupport` critic | **Reported: confirm** with three minor residuals (legacy-schema argv first-vs-last mismatch; in6.h anchor digest without retained bytes; used-by index omissions) |
| ControlsSafety (loopback, port refusal, group kill, timeouts, no env leakage) | `SafetyDelivered` sentinel | Dispatched; **no report yet**; the env-leak question was independently answered by `PrivacyScope.md` **refute** — gate echoes a malformed `child_env_keys` *value* (`NAME=<value>` interpolated via `!r`, `check-receipt.py:446-457,2101-2103`) into collected diagnostics. Current producer records names only, so it is a conditional leak, but it directly re-opens the dead seat's "no env/secret leakage into receipts" question |
| MistakesFailCapable (each fix shown able to fail) | this seat | This report |
| SeparabilityNoHarm (C1/C2 each verifiable with the other reverted; no axis harmed) | `Separability` reviewer + `NoHarm` critic | Dispatched; **no reports yet**; partial pre-coverage from `RevSeparability.md` (build wave) and `MatrixProbeBytes.md` (probe/matrix byte-identical) |
| TrendVerdicts (is 'quality improved' earned; any trade) | `TrendVerdicts` critic | **Reported: partial** — SCORECARD ends on the unfulfilled "appended after execution" promise and both counters exit 2 at HEAD |

So: 3 of 7 dead attacks now have terminal reports (all substantive, one finding a real residual), my seat is the fourth, and three are dispatched-but-unreported with partial sibling coverage. The dead-attack surface is no longer unexamined.

# D. Cross-cutting notes

- `FreshAppend.md` partial (delivered selftests killed 1/4 fresh mutants) is consistent with the declared boundary — fresh wave-2 mutants are a separate denominator, not hidden in the named 15.
- Sibling `TrendVerdicts` says "the repaired counters never ran on real inputs"; my clone rerun narrows that to c2 only — c1-measure at `1c325b2` exits 0 on real controls with faults `[]` and lesson-identical counts (scratch JSON retained at `/tmp/kama-r18-falsify-MistakesFailCapable-scratch/c1-measure.json` for this run only; clone and scratch removed per protocol — the numbers above are the finding).
- Not-attacked (out of my item): live-run provenance (LiveV3), frozen-manifest integrity (FrozenManifest), sibling connector scans.

# E. Commands run (clone, all bounded; exits as shown)

- `git clone -q <lane> /tmp/kama-r18-falsify-MistakesFailCapable && git switch -c seat/MistakesFailCapable 1c325b2e…` → `1c325b2` confirmed on top.
- `python3 tools/kama-llamacpp-live.py --selftest` → exit 0, tcp6 `::1`/`::ffff` live binds closed.
- `python3 tools/sources-append-only.py --selftest` → 42/42, exit 0.
- `python3 .ufo/waves/round-18/dispatch-provenance.py --selftest` → 30/30, exit 0.
- `python3 tests/llamacpp-live/check-receipt.py --selftest` → 61 mutations + unreadable rejected, exit 0.
- `python3 .ufo/waves/round-18/c2/survivors.py --selftest` → 60/60, exit 0 (43.3 s).
- `python3 .ufo/waves/round-18/c1/measure.py --controls tests/llamacpp-live/controls.py --frozen-tool .ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py --frozen-gate .ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py --tool tools/kama-llamacpp-live.py --gate tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --json --out <scratch>/c1-measure.json` → doc `exit: 0`, `faults: []`, 40.8 s; counts as in §M4.
- `ss -ltnpH` + `/proc/*/cwd` sweep after runs → no process/listener owned by this seat's clone paths; remaining `kama-c1-measure-8351m1ry` fake (PID 2196266, started 20:23:44) and `/tmp/kama-c2-survivors-*` processes belong to sibling seats, untouched.
- Read-only: `runs/commands.json`, `runs/c1-measure.{json,stderr,exit}`, `runs/c2-survivors.{json,stderr,exit}`, `runs/c1-self-mutants.json`, `runs/*-selftest.stdout`, `live/receipt-1.json`, round-17 `spec.json`/`dispatch.json`, `corpus/{QUALITY,SOURCES,README,knowledge/…}`, all `falsify/advice/*.md` verdict lines, `build/advice/RevKQ23FailCapable.md`.

# Installs and scratch

- Installs: none (pacman paused; stdlib sufficient). `/home/vgpnk/.omp/agent/RULES.md` read per directive; nothing needed.
- Scratch: clone `/tmp/kama-r18-falsify-MistakesFailCapable` and `/tmp/kama-r18-falsify-MistakesFailCapable-scratch/` removed before finish; no seat-owned listener remains (verified above). Pre-existing `/tmp/MistakesFailCapable-*` files (timestamps 15:35–15:42, prior same-named attempt) are not mine and were left alone; no process owns them.
- No lane writes besides this report. No port in the refusal set touched; the only listeners my runs created were ephemeral-loopback fakes inside controls.py, which teardown reaped (`leaked_processes: []` in my run's JSON).

Report: .ufo/waves/round-18/falsify/advice/MistakesFailCapable.md
