# X12StabilityC2Final — C2 stability at measured tip

Axes: calibration; repeatability/operability under host churn.

Scored unmodified clone at `23b3fdb1a925129a9961cf551f6d40bf251602cb`; four sequential fresh-work runs followed by two simultaneous fresh-work runs. All six returned rc=0 / `met=True`; no `met=False` to classify. Each had `idle_ok=1`, context-capacity `tip=host-busy(21.0–21.4s)`, and `controls_rejected=120/120`, `errors=0`. Thus all six accepted the declared host-busy outcome, not the idle outcome. Other 11 row tip outcomes were true.

## Outputs / timings

Exact stdout (full field lines) and stderr for every run are preserved in `out/X12StabilityC2Final/seqN.out/.err` and `conN.out/.err`. Results:

| Run | rc | wall ms | stdout status | context-capacity | stderr |
|---|---:|---:|---|---|---|
| seq1 | 0 | 23329 | met=True; covered 12/12; mismatches 0; pinned 13/13; deps_pinned 2/2; regress_flipped 12/12; printers_rejected 12/12; idle_ok 1; work_reuse_refused 1; closure_ptr 1; recon_mismatches 0; tally_disclosed 8/8; tally_selftest 1; sens_selftest 4/4; controls_rejected 120/120; errors 0; families canon 4/4 closure 5/5 flip 11/11 gate 16/16 idle 21/21 pattern 5/5 pins 5/5 printer 2/2 reconciler 11/11 registry 17/17 regress 11/11 selftest 1/1 tally 8/8 work 3/3 | host-busy (21.0s) | 24 lines; all decoy checks `(True, 'not-flipped')`, row diagnostics, no error |
| seq2 | 0 | 23278 | same field values/family counts; met=True | host-busy (21.0s) | 24 lines; same diagnostics, no error |
| seq3 | 0 | 23429 | same field values/family counts; met=True | host-busy (21.1s) | 24 lines; same diagnostics, no error |
| seq4 | 0 | 23284 | same field values/family counts; met=True | host-busy (21.1s) | 24 lines; same diagnostics, no error |
| con1 | 0 | 23673 | same field values/family counts; met=True | host-busy (21.4s) | 24 lines; same diagnostics, no error |
| con2 | 0 | 23672 | same field values/family counts; met=True | host-busy (21.4s) | 24 lines; same diagnostics, no error |

Every run's detailed `tally[...]`, `recon[...]`, decoy and per-row lines are in the archived full stdout. The context-capacity row was specifically `tip=host-busy`; this reflects concurrent foreign llama-server processes reported by the instrument and is the declared alternate outcome. `idle_ok=1` means the counter's idle-outcome control passed, not that the host was idle.

## Process and storage observations

Initial `pgrep -af llama-server` (before trial batch) showed an unrelated llama-server PID 3262613 (`kama-r61-closure`, port 37323) and foreign evaluator/control processes including MT27EvaluatorPlants and RV08C1CounterAmended servers. Those were already present before this seat started and were not touched. The initial tool response truncated long process lines; it is not a complete archival process listing.

Post-run `pgrep -af llama-server` returned only PID 3262613 (the unrelated r61 closure server); full captured output is `out/X12StabilityC2Final/pgrep-after.txt`. No server from these six runs remained. Work-directory sizes after runs: each of seq1–4 and con1–2 was 598 MiB (`du -sh`); filesystem reported 804G total, 450–454G available across observations.

## Evidence and cleanup

Raw per-run stdout, stderr, concurrent timing metadata, and post-run process snapshot are archived in `out/X12StabilityC2Final/`. No code, tests, or docs beyond this assigned report were edited; no tools installed. The scratch root was retained only until these receipts were copied; it is removed before handoff.

Counter summary: 6/6 met=True, 0 met=False; sequential 23.278–23.429 s; concurrent 23.672–23.673 s; idle_ok=1 in all; context-capacity host-busy in all; no observed owned-process leaks.