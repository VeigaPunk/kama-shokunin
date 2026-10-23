````RESULTS
1. Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD`
   Exit code: 0
   Verbatim tail: `bda324bbc5c1d7db93553adb13c5f380492c3c93`

2. Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --short -- .ufo/waves/round-31/w1/out/swarm-registry.json .ufo/waves/round-31/w2 .ufo/waves/round-31/controls`
   Exit code: 0
   Verbatim tail:
   ```
   ?? .ufo/waves/round-31/w2/out/
   ?? .ufo/waves/round-31/w2/validate.err
   ?? .ufo/waves/round-31/w2/validate.json
   ```

3. Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/w1/out/swarm-registry.json .ufo/waves/round-31/w2 .ufo/waves/round-31/controls`
   Exit code: 0
   Verbatim output tail (complete output):
   ```
   .ufo/waves/round-31/controls/CtlAllRows/receipt.txt
   .ufo/waves/round-31/controls/CtlBaseTree/receipt.txt
   .ufo/waves/round-31/controls/CtlDoNothing/c2.json
   .ufo/waves/round-31/controls/CtlDoNothing/receipt.txt
   .ufo/waves/round-31/controls/CtlEditInPlace/c2.json
   .ufo/waves/round-31/controls/CtlEditInPlace/receipt.txt
   .ufo/waves/round-31/controls/CtlNoId/c2.out
   .ufo/waves/round-31/controls/CtlNoId/receipt.txt
   .ufo/waves/round-31/controls/CtlNoLive/c1.json
   .ufo/waves/round-31/controls/CtlNoLive/receipt.txt
   .ufo/waves/round-31/controls/CtlNoLive/report.txt
   .ufo/waves/round-31/controls/CtlSchemaProjection/c1.json
   .ufo/waves/round-31/controls/CtlSchemaProjection/receipt.txt
   .ufo/waves/round-31/controls/CtlSchemaProjection/report.md
   .ufo/waves/round-31/controls/CtlTamper/c1-tampered.json
   .ufo/waves/round-31/controls/CtlTamper/c2-frozen.json
   .ufo/waves/round-31/controls/CtlTamper/c2-tampered.json
   .ufo/waves/round-31/controls/CtlTamper/receipt.txt
   .ufo/waves/round-31/controls/CtlTypeGuess/c1.json
   .ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt
   .ufo/waves/round-31/controls/CtlWrongCell/c1.out
   .ufo/waves/round-31/controls/CtlWrongCell/receipt.txt
   .ufo/waves/round-31/controls/CtlWrongObserved/c2-freeze-list.json
   .ufo/waves/round-31/controls/CtlWrongObserved/c2.json
   .ufo/waves/round-31/controls/CtlWrongObserved/receipt.txt
   .ufo/waves/round-31/controls/RefRepair/receipt.txt
   .ufo/waves/round-31/w1/out/swarm-registry.json
   ```

4. Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only HEAD -- .ufo/waves/round-31/w2`
   Exit code: 0
   Verbatim tail:
   ```
   .ufo/waves/round-31/w2/census-validate-start.out
   .ufo/waves/round-31/w2/plan.json
   .ufo/waves/round-31/w2/spec.json
   .ufo/waves/round-31/w2/taskCall.json
   ```

5. Command (verbatim):
   ```
   set -e
   out=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ScribeWaveRecord
   mkdir -p "$out"
   for arm in CtlWrongCell CtlNoLive CtlSchemaProjection CtlTypeGuess CtlTamper RefRepair CtlBaseTree CtlEditInPlace CtlNoId CtlWrongObserved CtlAllRows CtlDoNothing; do
     cp "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/controls/$arm/receipt.txt" "$out/$arm.receipt.txt"
   done
   cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w1/out/swarm-registry.json "$out/w1-swarm-registry.json"
   cp /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/plan.json "$out/w2-plan.json"
   printf 'saved 12 control receipts, wave-one registry, and wave-two plan\n'
   ```
   Exit code: 0
   Verbatim tail: `saved 12 control receipts, wave-one registry, and wave-two plan`
````
FINDING: Committed artifacts account for 100 control/roster/plan entries, but do not prove 100 executions; the frozen planned total is 108 of 128, with an eight-seat Wave-1 roster gap and Wave-2 status pending.
LIMITS: Seat registries/plans do not prove that a seat ran or succeeded. Neither W1 nor W2 records a dead-seat status or last-error field; local W2 outputs are untracked and are not used as committed execution evidence.

## Seat ledger

| wave | seats | role mix | dead seats (names + last error text) | evidence path |
|---|---:|---|---|---|
| Control call, attempt 1 | 12 receipt-backed control arms | 2 shortcut controls (`CtlTypeGuess`, `CtlSchemaProjection`); 3 C1 controls (`CtlNoLive`, `CtlWrongCell`, `CtlTamper`); 7 C2 controls (`CtlDoNothing`, `CtlAllRows`, `CtlWrongObserved`, `CtlNoId`, `CtlEditInPlace`, `CtlBaseTree`, `RefRepair`) | No dead-seat ledger. Receipts record arm commands/results, not worker death or last-error status. | `.ufo/waves/round-31/controls/*/receipt.txt` (all 12 receipt paths appear in commit `382d11b2`) |
| Wave 1, attempt 1 | 44 registered `spawn` entries; preregistered shape says 52 (8 not represented) | executor 27; scribe 8; reviewer 2; critic 2; connector 1; revenger 1; scout 1; sentinel 1; mutation-tester 1 | Unknown; registry has only `kind`, `agentId`, `role`, `item`; `agentId` and `item` are null, with no status/last-error field. No dead names or error text can be derived. | `.ufo/waves/round-31/w1/out/swarm-registry.json` (committed at `382d11b2`) |
| Wave 2, attempt 2 | 44 planned `spawn` assignments (`spawn: 44`, `resume: 0`, `total: 44`); standalone post-dispatch registry pending | reviewer 13; critic 10; executor 5; mutation-tester 5; scribe 4; connector 2; scout 2; sentinel 2; simplifier 1 | Unknown; embedded plan registry has null `agentId`/`item` and no status/last-error field. No dead names or error text are evidenced. | `.ufo/waves/round-31/w2/plan.json`, `.ufo/waves/round-31/w2/taskCall.json`; standalone `.ufo/waves/round-31/w2/out/swarm-registry.json` absent from the committed tree. `w2/out/` is untracked. |

### Wave-2 status still pending

The committed plan names all 44 assignments, but the standalone registry and post-dispatch status record have not landed. The pending status roster is: `SrcReopen1`, `SrcReopen2`, `SrcReopen3`, `SrcReopen4`, `SrcReopen5`, `SrcReopen6`, `ReRunC1`, `ReRunC2`, `ReRunHold`, `RevLiveRepeat`, `RevSourcesCells`, `RevReportSkeleton`, `RevAdmissionEvidence`, `RevRowA`, `RevRowB`, `RevRowC`, `RevRowD`, `RevRowE`, `CriticNoop`, `CriticKeyCollapse`, `CriticK31Ten`, `CriticClaimAdmission`, `CriticC3Control`, `ConnSibling`, `ConnInstrumentDup`, `ScoutProvince`, `ScoutFrontier`, `SentinelScope`, `SentinelBind`, `SimplifyAdditions`, `ScribeReportData`, `ScribeLessonMistake`, `ScribeTrend`, `ScribeWaveRecord`, `ExecC3Row`, `ExecC3Control`, `ExecCensusRows`, `ExecGateRegistry`, `ExecHoldRepro`, `MutC1Dup`, `MutC1Pin`, `MutC1Live`, `MutC2Append`, `MutC2Key`. This means registry/status is pending; it does not assert that no seat work has occurred. The current `w2/out/` contains local evidence but, as the captured status shows, is untracked and therefore excluded from the committed count.

### Round total against the 128 cap

The frozen planned shape is 12 controls + 52 Wave-1 seats + 44 Wave-2 seats = **108 planned / 128 cap**, or 20 planned seats below the cap. The committed evidence provides 12 control receipts, 44 Wave-1 registry entries, and 44 Wave-2 plan assignments: **100 control/roster/plan entries**, not 100 execution-confirmed seats. The eight-seat difference between the frozen Wave-1 count and its committed registry is unexplained (the registry does not name those seats). Wave-2 has no committed standalone post-dispatch registry; its current output directory is untracked. Therefore 108 is the declared plan, 100 is the committed entry count, and the realized cross-attempt execution total is not established. Within the named seat-ledger artifacts inspected, only the control arms have per-seat receipts documenting commands; the Wave-1 registry and Wave-2 plan do not establish execution.

### Saved raw evidence

Copied into this directory without editing source contents:

- `CtlWrongCell.receipt.txt`
- `CtlNoLive.receipt.txt`
- `CtlSchemaProjection.receipt.txt`
- `CtlTypeGuess.receipt.txt`
- `CtlTamper.receipt.txt`
- `RefRepair.receipt.txt`
- `CtlBaseTree.receipt.txt`
- `CtlEditInPlace.receipt.txt`
- `CtlNoId.receipt.txt`
- `CtlWrongObserved.receipt.txt`
- `CtlAllRows.receipt.txt`
- `CtlDoNothing.receipt.txt`
- `w1-swarm-registry.json`
- `w2-plan.json`
