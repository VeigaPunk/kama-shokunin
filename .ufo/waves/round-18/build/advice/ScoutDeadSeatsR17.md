VERDICT: partial — ControlsSafety is covered and the r17 sourced claim was closed outside; four attacks are only partly covered and TrendVerdicts has no owner in the executed wave.

# Recon — round-17's seven dead falsify seats vs the round-18 plan

## 0. Plan state — two plans exist, only one is running

- Round 17 lost the seats to provider limits: "Terminal: 71 completed; 9 failed on provider rate limits" … "seven left none: `C1AdmissionCritic`, … — dead seats, not respawned" (`corpus/lessons/round-17.md:193-199`).
- The outside check states the debt: "Seven falsify seats died and were not respawned" … "Their attacks remain undone; this closure covered only separability (by file set) and the sourced claim (by re-open)" (`corpus/lessons/round-17-verifier-spotcheck.md:255-258`).
- The seven names appear in the round-17 lesson only at `:193-199`; they are absent from the "Kept as debt" list (`round-17.md:250-291`), which names defects, not seats. R7 is the only durable pointer, so a plan that does not read R7 can miss them.
- Round 18's first call was refused — `"refused": 95`, `"error": "Background job limit reached (100)"` (`.ufo/waves/round-18/build/attempts.json`) — then refit: `"refit 95->75 after job-cap refusal; dispatch-95.json/validation-95.json kept"` (`.ufo/waves/round-18/build/validation.json`, field `note`). The **executed** plan is the 75-item `.ufo/waves/round-18/build/spec.json`; the 20 extra seats in `.ufo/waves/round-18/build/dispatch-95.json` are **not running**.
- Four cut seats bear directly on this recon: `RevLowestAxis` (the only seat told to "state what score move, if any, each claim may honestly claim"), `CritTrendPreview` (the only trend critic: "Flag any planned verdict that would be self-attested only"), `RevExitTables`, `ScribeScorecardRound18`. Their prompts are already written in `dispatch-95.json`; restoring them in wave 2 costs no design work.
- In the executed 75 only two items name the seven seats: this recon item and `RevSpotcheckMap` (`spec.json:262`, "flag every sub-item left uncovered (e.g. … the seven dead seats)"). A map is not an attack; it must not be counted as coverage.

Method: read the seven prompts in `.ufo/waves/round-17/falsify/spec.json`, the round-17 lesson and outside spotcheck, the executed `spec.json` (75) and the refused `dispatch-95.json` (95), `SCORECARD.md`, `LEARNING.md`, `AXES.md`. No detector was run, no clone made, no port bound.

## 1. The seven attacks, one line each

| # | Seat (r17 spec) | Attack | Executed r18 owner | Coverage |
|---|---|---|---|---|
| 1 | `C1AdmissionCritic` (`spec.json:82`, prompt `:84`) | Is C1's before→after honest and attributable to the gate rather than the detector; calibration, operability, or neither? | `CritC1HiddenPass:277`, `CritC1NoHarm:282`, `CritCountingCommands:302` | partial |
| 2 | `C2AdmissionCritic` (`:167`, `:169`) | Is accepted-bad 6→0 + 3 VALID sufficient; is the good fake built from real b11755 shapes; can a v2 predicate false-fail a healthy server? | `CritC2AxisFit:287`, `CritC1NoHarm:282`, `RevV2Compat:222`, `CritC2Cherry:292` | partial |
| 3 | `C2SourcedClaim` (`:172`, `:174`) | Do S042/S043/S044 support exactly the predicates graded; any overclaim in scope/teaches? | old rows closed by the outside spotcheck; new rows only `CritSourcedClaim:297` | covered (r17) / partial (r18 rows) |
| 4 | `ControlsSafety` (`:162`, `:164`) | Safety audit of controls.py + live tool: binds, ports, killpg guard, timeouts, temp, env/secret leakage | `SentinelControlsSafety:92`, `SentinelLiveToolInvariants:97` | covered (design/frozen); delivered bytes residual |
| 5 | `MistakesFailCapable` (`:307`, `:309`) | Round-17 M1-M7 "shown able to fail": run M1-M4's failing side; is M5-M7 fail-capable? | M1 `C2AppendOnly:42`; M2 only `MutBaselineControls:82`; M4 refused residual `C2Provenance:47` | partial |
| 6 | `SeparabilityNoHarm` (`:297`, `:299`) | C1/C2 each verifiable with the other reverted; probe unchanged; any axis harmed incl. round-13 gate exit table? | `RevSeparability:257`, `CritC1NoHarm:282`, `RevV2Compat:222` | partial |
| 7 | `TrendVerdicts` (`:302`, `:304`) | Are SCORECARD §Round-17's three trend verdicts earned under LEARNING.md; any trade? | none (the only trend critic, `CritTrendPreview`, was cut) | uncovered (executed) |

## 2. Per-seat findings

### 2.1 C1AdmissionCritic — partial

Attack: "Is the before->after … honest and attributable to the gate rather than the detector?" (`spec.json:84`).

Covered:
- The round-17 trio and the cff9e62 claim were re-derived outside: `spotcheck:64-108` re-measured frozen/current accepted (3/0) and the mutant grid (1/8→1/10, 7/8→10/10), and `:74` quotes `git show cff9e62:SKILL.md | sed -n 533p`. The historical half is closed; do not re-litigate it.
- Round 18's new C1 is attacked for weakening (`CritC1HiddenPass:277`, "is reclassifying zero-observation from exit 1 to exit 2 … a weakening"), for harm (`CritC1NoHarm:282`, "list every way C1 could harm an axis"), and for counting provenance (`CritCountingCommands:302`, "Could the 'before' side be rigged by running the current detector on the frozen subject?").

Not covered:
- No executed seat rules C1's new axis/score. That was `RevLowestAxis` ("state what score move, if any, each claim may honestly claim", `dispatch-95.json`), cut in the refit; `CritC2AxisFit:287` covers C2 only.
- `measure.py` swaps tool+gate as one unit against a single controls path (`C1Measure`, `spec.json:22`: "against frozen tool+gate and against current tool+gate"), so no item separates the tool's contribution from the gate's. The r17 detector confound is removed by design (same detector both sides), but no seat says so explicitly.

### 2.2 C2AdmissionCritic — partial

Attack: "Is 'accepted-bad 6 -> 0' plus three real VALID runs a sufficient before->after? Is the K0 good fake built from the real b11755 shapes? Does any v2 predicate risk failing a healthy real server?" (`spec.json:169`).

Covered:
- Axis: `CritC2AxisFit:287` ("Is C2 … calibration or operability?"); the intended second look, `RevLowestAxis`, was cut.
- False-failure risk: `CritC1NoHarm:282` names "new false failures"; the C1 contract's zero-loading and AF_INET6 good-server controls are acceptance arms; `RevV2Compat:222` re-runs the frozen gate on committed receipts ("The new gate must reproduce them").
- Count universe: `CritC2Cherry:292` demands "equivalent-mutant declarations, a stated universe".

Not covered:
- Good-fake fidelity to real b11755 shapes. No executed item compares the fake's `/health`, `/v1/models`, `/props`, `/metrics` bodies to the real server's; `ScoutLlamaBindVsLoad`, `ScoutLlamaArgParse`, `ScoutLlamaMetricsProps` read the sources, not the fake's responses.
- No healthy **real** server is exercised with the v3 tool+gate: `C1LiveTool`'s acceptance is `--selftest`, and `C1Measure` uses fakes only. The v3 path would ship live-unexercised.

### 2.3 C2SourcedClaim — covered for r17, partial for the new rows

Attack: do S042/S043/S044 "support exactly the predicates graded"; any overclaim in row scope or teaches cells (`spec.json:174`).

Covered:
- The r17 instance is closed outside: "Sourced: S042, S044 and S047 were re-opened by this closure (§3), and all three agree" (`spotcheck:141`); S044's quote is verbatim 14 words (`:176`); S043 disagreed and was superseded by S047 (`:177`, row "**disagree with the build-time admit; agree with the S047 correction**").
- New rows are screened for behaviour-determining vs decorative (`CritSourcedClaim:297`), and the S043 failure mode is made a criterion (`ScribeQualityKQ23:342`; applied by `RevKQ23FailCapable:272`).

Not covered:
- No seat tests the new S048-S053 rows' `teaches`/scope cells against the opened pages — the exact S043 failure mode, applied to the new bytes. `CritSourcedClaim` rules admissibility; it does not re-read each cell.

### 2.4 ControlsSafety — covered (design/frozen), delivered bytes residual

Attack: "Safety audit of tests/llamacpp-live/controls.py and tools/kama-llamacpp-live.py at the round commit" covering loopback binds, registered-port refusal, pidfile + /proc cmdline guard killpg, K6 wrapper, ≥180 s timeouts, temp cleanup, no env/secret leakage (`spec.json:164`).

Covered:
- `SentinelControlsSafety:92` is explicitly the resurrection — "the round-17 ControlsSafety seat died" — and lists the must-keep properties incl. the AF_INET6 `::ffff:127.0.0.1` control, the registered-port ban, process-group teardown, temp removal, no env leakage, and an in-process KeyboardInterrupt that "cannot kill the harness or leave children".
- `SentinelLiveToolInvariants:97` enumerates the frozen tool's invariants with file:line and flags what v3 could weaken (e.g. BaseException handling swallowing Ctrl-C before teardown).

Residual: both run against the frozen copies in wave 1; neither audits the **delivered** controls.py/tool. The must-keep list is delegated to L1 ("checks L1 can verify in the delivered code").

### 2.5 MistakesFailCapable — partial

Attack: "For M1-M4, run (in a /tmp clone) the failing side and confirm it fails for the stated reason, not incidentally. For M5-M7, is a fix claimed that is not fail-capable?" (`spec.json:309`).

Covered:
- M1: `C2AppendOnly:42` re-runs the exact demonstration — "(`--from b8e485c --to ccc4bb3`, see corpus/lessons/round-17.md M1) still flags S041".
- M2 (partial): the frozen tool+gate arm (6/8 accepted) is re-exercised by `MutBaselineControls:82`; the frozen check.py arm (3/8 faults) is not re-derived by any executed item.
- M4 (partial): the refused residual is covered — `C2Provenance:47` must "record `refused: 82`" and show frozen 0 → new 82, and `RevengerRefusedZero:372` reconstructs the count; the original 0→79 spawned demo is not re-run.

Not covered:
- M3 (count-verdicts demo) has no item; no one runs `.ufo/waves/round-17/count-verdicts.py` on the round-16 falsify results.
- M5-M7 have no ruling. Their cells already disclaim a mechanical guard ("context clauses … through disclosure only", "still no mechanical guard", "SKILL.md row says absolute paths"), so the honest wording is probably "no fix claimed" — but nobody says it.
- No item requires the round-18 lesson's own M rows to be fail-capable; `RevKQ23FailCapable:272` covers KQ23 only. The class recurs every round.

### 2.6 SeparabilityNoHarm — partial

Attack: "C1 and C2 each verifiable with the other reverted? Probe unchanged? Did any axis get harmed (freshness, depth, coverage, adjacency, the round-16 gates, the round-13 gate exit table)?" (`spec.json:299`).

Covered:
- Separability: `RevSeparability:257` ("can either claim's counting command change if only the other lands?") and the spotcheck's r17 file-set re-measure (`spotcheck:56-61`).
- C1 no-harm: `CritC1NoHarm:282`; receipt back-compat: `RevV2Compat:222`.

Not covered:
- C2 no-harm. The new check.py/fault-controls could flip verdicts on honest probe output; the only accept-clean baseline is fault-controls' own F0 positive control (`.ufo/waves/round-18/frozen/tests_probe-verdicts_fault-controls.py:20`, "F0 is the positive control"), which is the detector checking itself, not an independent harm arm.
- Probe byte-diff for r18: no item; the spotcheck did it for r17 only (`spotcheck:60-61`, "the probe is byte-identical").
- The round-13 gate exit table: no executed item. The cut `RevExitTables` would collect the six tools'/probe's docstring-vs-exit tables, not `.ufo/waves/round-13/measure.py`'s exit-4 case (`round-17.md:131-135`).
- Round-16 gates beyond the v1 receipts (e.g. the round-16 measure) have no r18 re-run.

### 2.7 TrendVerdicts — uncovered (executed plan)

Attack: "Attack the author trend verdicts in SCORECARD.md §Round 17 (expansion unchanged, quality improved, discernment unchanged) against … LEARNING.md. Is 'quality improved' earned … Is anything a trade?" (`spec.json:304`).

Findings:
- No executed item mentions LEARNING.md; the only trend seat, `CritTrendPreview` ("Flag any planned verdict that would be self-attested only"), was cut in the refit. `ScribeScorecardRound18` was cut too.
- Live residue: `SCORECARD.md:702` still says "discernment unchanged (no non-author sample yet)", while the outside spotcheck rules "**discernment: improved** (this closure's outside judgment; the lane wrote `unchanged`" (`spotcheck:217`), under LEARNING.md's own clause "a disagreement becomes a lesson that adds a grounded `QUALITY.md` criterion" (`LEARNING.md:35`). Round 18 plans exactly that criterion as KQ23 (`ScribeQualityKQ23:342`), so the r17 cell is now stale and no item corrects it.
- "Quality improved" was agreed with the superseded entry named (S047 supersedes S043; round-16 v1 limits superseded; `spotcheck:209-219`), and "expansion unchanged" was agreed (`spotcheck:207`). Those two are answered; the attack's remaining teeth are the stale discernment cell and self-attestation of round-18's own verdicts.

## 3. Proposed wave-2 items (ranked)

Restore first (zero design cost; prompts already in `.ufo/waves/round-18/build/dispatch-95.json`): `RevLowestAxis` (axis + honest score for both claims), `CritTrendPreview` (round-18 trend verdicts), `RevExitTables` (exit-table consistency), `ScribeScorecardRound18` (scorecard draft). They close the axis and forward-trend holes W1/W4 below would otherwise duplicate.

**W1 — `CritTrendVerdictsR17` (critic, read-only).** Price the r17 verdicts against `LEARNING.md:31-35`, `SCORECARD.md:698-702` and `spotcheck:207-221`; one row per trend with the criterion line and agree/disagree; rule whether r17 discernment is `improved` now that the outside sample exists and KQ23 is the mined criterion; give the one appended line for `SCORECARD.md:702` (never rewrite it); then hold round-18's three verdicts to the same test before the Gate closes and flag any self-attested-only. Acceptance: 3-row table, one append line, VERDICT, no lane edits. Combine with restored `CritTrendPreview` if both run.

**W2 — `CritMistakesFailCapable` (critic, /tmp clone allowed).** (a) M1: run `tools/sources-append-only.py --from b8e485c --to ccc4bb3` at the r18 tip on frozen and delivered copies, paste exits. (b) M3: run `.ufo/waves/round-17/count-verdicts.py` on the round-16 falsify results, paste the nonconformant lines. (c) M2/M4: cite the `MutBaseline*` and `C2Provenance` evidence, do not re-run. (d) Rule M5-M7: state that their cells claim no mechanical fix, so fail-capability is not claimed, and give the exact wording. (e) Pre-register the admission rule for r18's M rows: named command + pasted exit, or an explicit "no mechanical guard". Acceptance: M1-M7 table (claim, command, exit, agree/disagree) + rule text.

**W3 — `CritC2NoHarm` (reviewer, /tmp clone).** (a) `git diff --quiet <round-start>..<tip> -- tools/kama-probe.sh` and the nine `tests/probe-verdicts/*.json`; paste the empty diffs. (b) Run frozen vs current check.py on unmutated matrix/probe outputs and show identical verdicts (the 72/72 selftest is not a harm test). (c) Re-run the round-13 gate exit-4 sandbox with `.ufo/waves/round-17/frozen/round-13_measure.py` (command as in `round-17.md:131-135`); cite `RevV2Compat` for the round-16/17 receipts instead of duplicating. (d) One line per axis freshness/depth/coverage/adjacency with its cheapest falsifier. Acceptance: command/exit per line, verdict.

**W4 — `CritC1Attribution` (critic, /tmp clone).** Run the 2×2 {frozen,current} tool × {frozen,current} gate with the one delivered controls.py; paste accepted_bad/good_rejected/misclassified/uncontrolled per cell; rule whether the pair-level delta is sufficient for an operability claim and whether the one-controls design removes the r17 detector confound; state the honest claim wording and the score move C1 may claim (fold in restored `RevLowestAxis` if available). Acceptance: 4-cell table, commands/exits, VERDICT.

**W5 — `LiveV3AndGoodFake` (executor; one real server at a time, loopback, torn down).** Run the delivered tool+gate once against real b11755 + `stories260K.gguf` (ports not in `registry/endpoint-consumers.tsv`; never 8080/34113); expect a v3 receipt; tool exit 0 / gate VALID if a loading 503 was observed, otherwise the legitimate not-evaluated pair (tool 2, gate 3) — record which. Capture `/health`, `/v1/models`, `/props`, `/metrics` bytes and diff them against the delivered good fake's responses; report any predicate that would false-fail the real server. Teardown evidence with `ss -ltnp`. Acceptance: receipt path, gate exit, byte-diff table, teardown proof. This is the only arm that exercises v3 against the real server and answers C2AdmissionCritic's fidelity question.

**W6 — `CritNewRowsSupport` (critic, read-only; may fold into `CritSourcedClaim`).** Re-open every S048+ row's URL/path at the pinned bytes and test each `teaches`/scope cell for the S043 overclaim ("a code-derived behavioural claim admitted past what its lines prove"); the kernel tcp6 format row is the highest risk. Name the append-only correction if one is needed; do not edit. Acceptance: per-row agree/disagree with a located ≤25-word quote.

**W7 — `SentinelControlsDelivered` (sentinel, optional).** Apply the `SentinelControlsSafety` must-keep list to `build/out/C1Controls/*` and `build/out/C1LiveTool/*` before integration: bind hosts, registered-port parser, temp removal, env allowlist, receipt path, KeyboardInterrupt containment, and that the `--api-key` forged-receipt control never launches a real server; run `controls.py --selftest` in a /tmp clone with the delivered tool+gate. Acceptance: property → file:line → pass/fail.

## 4. What the plan already does right

- ControlsSafety was resurrected twice and with sharper scope than round 17 (frozen invariants + must-keep list).
- The r17 sourced claim was genuinely closed outside (`spotcheck:141`, `:175-177`), and round 18 turns the S043 failure into a criterion (KQ23) instead of netting it out.
- Separability of the r18 claims has a dedicated reviewer, and C1's weakening/harm have two critics.
- `RevSpotcheckMap:262` will independently list the uncovered R7 sub-items; use it as a cross-check on this report, not as the attack.

## 5. Limitations

- Coverage is judged from the prompt text of the executed 75 and the refused 95; no item was observed running.
- `dispatch-95.json` seats were refused, so "intended coverage" in §0 is not coverage; if L1 re-dispatches any of them, re-check this table.
- No detector, gate, control or server was run for this item; the F0 and round-13 references are read, not executed.
- The 20 cut seats include several unrelated to this recon (`ScoutPySignal`, `ScoutAutomakeExitCodes`, `ScoutLlamaApiKeyPublic`, `ScoutPortsSafety`, `Connect*`, `SimplifyC1Plan`); they are left to `RevSpotcheckMap`/L1.
- Installs: none. Scratch: none (no /tmp clone used). Ports bound: none.
