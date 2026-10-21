# Kama shokunin — round 20 report

## Work performed

**Declared claims and author verdicts.** C1 targets calibration (7→7): the finite named error-classification population is repaired from six frozen misclassifications to zero on the current instrument; it is not a universal error census. C2 targets operability (8→8): a first-working offline GGUF declared-identity reader compares selected metadata with a captured receipt; it does not authenticate loaded weights or execution. Both claims are supported at those bounded scopes; scores are held and independent admission remains the closure's decision.

- Reused the committed R20 implementation/frozen population and original measurement at `0957ce619789d13d894ef21bc863486bcb35b56c`; wave 1's 72 seats and the complete original evidence remain under `.ufo/waves/round-20/build/` and `runs/0957ce61/`. Rechecked the material claims and repaired the carried scope/citation notes rather than counting the nonconformant KnowGguf draft as evidence (`LOG.md:1204-1227`, `SCORECARD.md:865-930`).
- Ran the validated falsify wave without splitting or padding: attempt 1 was cap-refused before spawning; after at least 180 seconds the exact saved 86-seat payload was retried and spawned all 86. All 73 returned reports and all 13 dead-seat failures are accounted in `.ufo/waves/round-20/falsify/{dispatch-attempts.json,completion-summary.json,seat-failures.json,verdict-count.json}`.
- Integrated falsify findings: S063's `used-by` changed from `—` to the two actual citing paths; S065 adds the Python 3.14.8 `sys.exit(None)` exception (“None is equivalent to passing zero”) without rewriting S061; the S051 current range was corrected append-only after S065 shifted it; the C1 real-invalid cell's measured source was hash-bound to its clean commit; and the GGUF fixture generator/manifest defaults were corrected to match the parser. Details are in `corpus/lessons/round-20.md` and `LOG.md:1239-1252`.
- Reconciled the R19 non-author verifier: the routed tool-registration rows are present in `SKILL.md:652-656` at `0957ce619789d13bb5779606078fa1498114d2c7`; C1 counts, the mislabeled R19 falsify attribution, append-only R18 corrections, retrospective assignments, and clean-commit census/selftest receipts are recorded in `LOG.md:1176-1195` and `SCORECARD.md:853-863`.
- Retained two fail-closed measurement attempts and fixed their stale pins rather than crediting them: `runs/c7311039/` found the changed manifest SHA still pinned in `measure-reference.json`; `runs/04de7a87/` found the changed reference SHA still pinned in `c2/measure.py`. The corrected clean-tree run is `runs/9add96e4/`.

## Landed changes

- `c7311039bcbd76c38b0648d33197864331f34364` — 73 falsify reports, wave accounting, S063/S065/S051 corrections, GGUF manifest metadata correction, and the integrated lesson/scorecard/log entries.
- `04de7a8720139e57cf4960013229b8fd23d497f5` — updated `c2/measure-reference.json`'s `expected_json_sha256` and retained the first fail-closed run.
- `9add96e462e62dc5141cd02730b7a699268b3513` — synchronized `c2/measure.py`'s `REFERENCE_SHA256` and retained the second fail-closed run.
- `3ec5ea6882994ff2e950a76b4e951b8973505f5e` — committed the final corrected 21-command run and its appended measurement/census record.
- `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d` — logged the R19 verifier's routed instrument-registration closure. **Final pushed lane HEAD:** `7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d` (lane state: local=remote, clean).

## Before → after measurements

| Claim | Before → after | Counting command and evidence | Measured commit |
|---|---|---|---|
| C1 — finite named error regressions, calibration 7→7 | 15 pinned cells; frozen misclassified **6**, current **0**; frozen-witness mismatch 0, red-vector mismatch 0, unrun 0. | `python3 tools/error-verdict-census.py --arm frozen --json` and `--arm current --json`; paired results: `.ufo/waves/round-20/runs/9add96e4/error-pair.stdout:1-10`. | `9add96e462e62dc5141cd02730b7a699268b3513` |
| C2 — offline GGUF declared identity / captured receipt, operability 8→8 plus one capability | Instrument absent at frozen base → working bounded reader; **23/23** declared fixture predicates, mismatches 0, snapshot tampering 0, unavailable 0; real-file oracle and receipt evidence pass, receipt status `engine-agreement`. | `python3 .ufo/waves/round-20/c2/measure.py --json`; `.ufo/waves/round-20/runs/9add96e4/gguf-measure.stdout` (`summary`); local reader `tools/gguf-identity.py`. | `9add96e462e62dc5141cd02730b7a699268b3513` |

The clean-tree official runner recorded **21/21 declared exits**, harness exit 0, in `.ufo/waves/round-20/runs/9add96e4/commands.json`. C2 remains limited to selected identity keys/types, arrays, header facts, size and digest; the `v3-all-scalars` fixture's 12 `test.*` values are not individually compared (`c2/measure.py:459-484`). The receipt is self-reported, not execution authentication.

## Sources & frontier

The official census command was `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama`; validation used the same command with `validate`. Both exited 0 in `runs/9add96e4/commands.json`.

| Census | Rows | Tier A / C | Mined / queued / rejected | Missing |
|---|---:|---:|---:|---:|
| Round-start committed baseline | 57 | 54 / 3 | 46 / 5 / 6 | 0 |
| Final post-S065 tree | 65 | 62 / 3 | 52 / 6 / 7 | 0 |

Eight new tier-A rows were added: S058, S059, S060, S061, S062, S063, S064 and S065; six are mined, one queued (S061), one rejected (S063). S065 is a correction row for the `sys.exit(None)` special case; it does not turn S061's queued remainder into an admitted universal claim. The only existing-row edit is S063 `used-by`: `—` → `corpus/knowledge/error-is-not-a-verdict.md, corpus/lessons/round-20.md`; S063 remains rejected. No existing frontier status advanced: S061 remains queued, S063 remains rejected, and S065 is newly mined. The six validation W04 duplicate-URL warnings are S031/S043/S056/S060/S064/S065; validation still exits 0. The S065 search note records the opened Python 3.14.8 paragraph, quote, one candidate screened/included and stop condition in `corpus/SOURCES.md`.

## Trend verdicts

- **Expansion — improved.** R20 adds the first-working `gguf-declared-identity-replay` capability (`SCORECARD.md:909-918`); the credit is the new demonstrated capability, not source-row growth.
- **Quality — improved.** C1's bounded 15-cell misclassification count falls 6→0; C2's declared fixture predicates and oracle/receipt checks pass after the fail-closed reference pins were synchronized. The scalar-value limit above bounds this verdict.
- **Discernment — unchanged for R20.** No independent R20 admit/reject sample was run. The R19 outside verifier's two admits/one reject agreed and credited R19 discernment as improved; it disagreed with the R19 author expansion verdict because a source row alone was not new repertoire. R20's new capability surface resolves that expansion distinction without retroactively rewriting R19 (`corpus/lessons/round-19-verifier-spotcheck.md:160-172`; `corpus/lessons/round-20.md` §Trend verdicts).

## SHONEN

- [~] Decision tables, error patterns, checklist and cited sources — `SKILL.md` §§Decision table, Error signatures, Checklist; no non-author promotion verifier.
- [~] End-to-end domain task — `LOG.md` §round 20 and `.ufo/waves/round-20/runs/9add96e4/gguf-receipt.stdout`; author evidence only.
- [~] Instructions executable without oral context — `SKILL.md` §Checklist and `corpus/knowledge/snapshot-history.md`; independent execution review remains open.
- [~] No cross-domain bleed — `PROVINCE.md` §Write boundary and `corpus/knowledge/cross-lane-scope.md`; no host/service/config ownership was taken.

## Wave accounting and evidence disposition

- **Build wave:** 72 spawned; 70 completed, 2 dead (`CellDesign`, `SrcGateStandard`), no replacements. Roles scout16/reviewer13/executor12/critic6/mutation-tester2/revenger2/sentinel2/connector6/scribe12/simplifier1; L1 held the frozen planner seat. First whole-wave call was refused (`Background job limit reached (100)`), same payload then spawned72. Seventy-one advice files counted 41 confirm/27 partial/2 refute/1 nonconformant; `KnowGguf` is not reused as a conformant claim, and `SrcGateStandard`'s partial artifact is not counted as completion. Evidence: `.ufo/waves/round-20/build/completion-summary.json`, `seat-failures.json`, `verdict-count.json`.
- **Falsify wave:** 86 spawned; 73 advice files, 13 original seats dead, zero replacements. Roles reviewer60/mutation-tester17/scout6/critic2/connector1. Top-level advice count 66 confirm/7 partial/0 refute/0 nonconformant. The dead seats were `C1ErrorCensus`, `C2GgufMeasure`, `CitationR18C1CheckpointExit`, `R18C2EvidenceScope`, `CellCitationValidToken`, `CitationGateLive1`, `FixtureVersion99`, `CitationR18C2Preofficial`, `FixtureBadMagicNearMiss`, `CitationR18FalsifySpec`, `CellCitationMissingToken`, `CitationR18Assignments`, `FixtureV3Minimal`; the first four exhausted Codex `turn_rate_limit_exceeded` retries, the other nine reported `429 Rate limit reached (type=1302)`, all after five retries. Exact per-seat text: `.ufo/waves/round-20/falsify/seat-failures.json`.
- Across both waves: **158 spawned**, 15 original seats dead, zero replacements. The failed first wave-2 call spawned zero; its identical retry followed the ≥180-second wait. The slot was released after all wave seats settled. No ordinary ≤8 residual-review task call was used.
- All 17 mutation-tester reports were retained: 15 targeted mutants killed, two diagnostic-only survivors. Removing the signal-specific branch still yields `error`; removing timeout-to-error conversion also yields `error` through traceback fallback but loses structured timeout reason. These do not refute the declared class boundary; reason precision remains unclaimed. Seven top-level partial reports remain visible in `verdict-count.json`; integrated corrections and remaining limits are recorded in `corpus/lessons/round-20.md`.
- The 17 required-citation rows verify, comprising 4 existing plus 13 reconstructed revision/path instances—not all citations. The pins for `r18-dispatch-95` and `r18-validation-supplement` are artifact-byte-valid but their lesson tokens are retrospective (added after the pinned artifact revision); no contemporaneous-document claim is made. The R18 C2 preofficial/official comparison is scoped to 15 item outcomes, summary counts, frozen witnesses and 42 run-status tuples; full `results` and tool hashes differ, and no full 42-run survivor measurement was rerun.

## Open limits, L0 and hygiene

- R19's additional frontiers `TreeCap`, `TreeDeterminism`, `GridDefaults`, `SentinalSecrets`, and the other-engine/serving leaves remain outside C1/C2 and unclaimed; the active planned row still names broader receipt-header minimization, symlinked soname identity and K05/other-engine serving evidence.
- The existing L0 remains open: `kama | round-17` asks whether to keep or remove `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22,240,468 bytes; observed digest prefix/suffix `753bfa73…e226`) with the install/PATH/model cache. No archive, PATH, model cache, service, or host setting was changed.
- Tool installs/updates: none. No persistent model server, large model download, pacman transaction, or host mutation occurred.
- **Stale-lane:** no other Kama mission is open; round 21 was not started. The pre-report fleet-root status also showed unrelated Kagi/Tabi/watchdog changes and an untracked `.ufo/waves/round-20/final/AuditCase07.md` about `souji-seat-audit` (plus empty `w1/`); none was a Kama artifact, so it was left untouched.
