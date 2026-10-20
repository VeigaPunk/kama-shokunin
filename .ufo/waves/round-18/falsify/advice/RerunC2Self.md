VERDICT: confirm — the assigned b/c/d named-survivor families are detected on pushed commit `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; the two main-arm exit-2 results are own-faults, while their separately targeted selftests provide the actual kills.

## Axes and scope

Axes tested: detector-self calibration; full diagnostic versus main-decision-tuple classification; append-only parser self-detection; refusal-count provenance; experiment containment. This is only the requested `b,c,d` subset (six named items), not the complete 15-item a–e universe or a general immunity claim.

I cloned the lane to `/tmp/kama-r18-falsify-RerunC2Self` and verified `HEAD` was `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. Experiment source was the committed `.ufo/waves/round-18/c2/survivors.py`, SHA-256 `87cad1cad4565be01ce06e7f92c578c2f449c951894a880166040c3f118dc3ac`; no custom experiment source or code edits were made.

Ran `python3 .ufo/waves/round-18/c2/survivors.py --help` first. Help identified `--family`, `--jobs`, `--out` (exclusive creation), and default current tool paths in the clone. Then ran exactly:

```text
python3 .ufo/waves/round-18/c2/survivors.py --family b,c,d --jobs 1 --out /tmp/kama-r18-falsify-RerunC2Self/rerun-bcd.json
```

Observed stdout:

```text
kama-c2-survivors/v1 families=b,c,d jobs=1 seconds=483.2
[b] fault-controls self-mutants (frozen -> current tool)
  FC-target      frozen survived         current killed           selftest killed (targeted selftest assertion failed: target-conjunct attribution); main inconclusive
  FC-f6cache     frozen survived         current killed           selftest killed (targeted selftest assertion failed: F6: replay run shares one cache); main inconclu
  FC-f0gate      frozen survived         current killed           selftest killed (targeted selftest assertion failed: F0 gate: a reject-everything); main survived (m
[c] sources-append-only self-mutants (frozen -> current tool)
  AO-opened      frozen survived         current killed           targeted selftest assertion failed: only `opened` changes
  AO-blank       frozen survived         current killed           targeted selftest assertion failed: edit after a blank line
[d] dispatch-provenance refused count on round-17 evidence
  refused-count  frozen miscount         current correct          refused 82
named items not killed/handled/correct: before 6 -> after 0 (of 6 named)
exit 0
```

The summary truncates long `why` values; the JSON has complete retained fields. The command returned successfully; the separate process stderr stream was not separately labeled in the tool response. Per-child stdout/stderr tails are in the JSON. Result JSON SHA-256: `3ba00535c7cd166e530b546ec14fdfdf89357d60bc80489d1a2c9631dea8b9d5`; JSON records `/usr/bin/python3` 3.14.8, `own_faults: []`, exit `0`, and no frozen witness mismatches (`rerun-bcd.json:1-24,1096-1176`).

## Findings

1. **FC-target and FC-f6cache: targeted selftest, not main decision, kills.** The rerun reports both current mutants `killed` and frozen copies `survived` (`rerun-bcd.json:324-325,450-465,471-473,592-606`). For each current mutant, the `--selftest` exits 1 and names its intended assertion: `target-conjunct attribution` or `F6: replay run shares one cache`. The main invocation separately exits 2 with empty stdout and no decision tuple. Its complete stderr diagnostics are:
   - target: `fault-controls: own fault: F1: fault declares no target conjunct; a row failure cannot be attributed to it`
   - cache: `fault-controls: own fault: F6: a cached replay must target exactly one row (per-row cache), got 4`

   The stored `unparsed: JSONDecodeError: Expecting value...` is the wrapper's explanation for attempting to parse empty main stdout; it is not the cause of the classification. In code, `fc_view()` records a missing decision and parse diagnostic (`.ufo/waves/round-18/c2/survivors.py:861-879`); `main_arm()` explicitly maps exit 2 to inconclusive, not killed (`:956-973`). The independent `selftest_arm()` requires the named failing assertion (`:928-953`), and `combine_arms()` keeps a targeted kill despite another inconclusive arm (`:976-985`). Thus the aggregate `killed` is justified by the targeted red selftest, not by treating an own-fault or a JSON parse failure as rejection.

2. **FC-f0gate: decision tuple is unchanged; named selftest supplies the kill.** The unmutated current baseline main tuple is `(exit=0, f0_detected=true, detected=17, accepted=0, F1–F17=true)` (`rerun-bcd.json:130-158`). The mutant's main invocation is also exit 0 with the same tuple and no accepted IDs (`:739-776`); its main arm correctly survives. The selftest exits 1 and says `F0 gate: a reject-everything check.py was not refused before any fault counted`, with the bad synthetic outcome `code=0, accepted=0` (`:740-744`). The aggregate kill is therefore selftest-only. This is the strongest illustration that full diagnostics and the compact decision tuple answer different questions.

3. **Append-only opened/blank-line mutants: exact named failures, not mere nonzero exits.** Both frozen mutants pass (14/14); the current unmutated baseline passes 42/42 (`rerun-bcd.json:936-949,959-973,1010-1024`). Current AO-opened exits 1 and is classified against `only `opened` changes` (`:975-997`). Its full retained diagnostics also show other cases failing because the weakened comparison set omits `opened`; e.g. the comparator reports that `['source', 'kind', 'tier', 'scope', 'anchor', 'teaches']` is not the contract's immutable set containing `opened` (`:989-996`). Current AO-blank exits 1 and specifically fails `edit after a blank line`; diagnostics show a later row being refused as outside the parsed registry (`:1026-1047`). These are targeted selftest detections; the multiple affected assertions are consistent with each mutation and are not being counted as extra named mutants.

4. **Refused-count provenance: 0 → 82 on the same pinned input.** Frozen provenance reports `refused=0` / `miscount`; current reports `refused=82` / `correct`, with `spawned=0` (`rerun-bcd.json:1058-1092`). The 9,427-byte refused-result input matches SHA-256 and pinned SHA-256 `7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c`; attempts.json independently records 82 (`:1186-1198` and `:1061-1065`). Current output's result digest is the same as the input digest. No task was spawned.

The fresh matrix has nine files and its set digest matches the pinned `bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32`; frozen inputs match the committed SHA256SUMS (`rerun-bcd.json:1177-1289`). Across the six requested items, counts are before 6 / after 0, with five `killed`, one `correct`, zero inconclusive, and all frozen witnesses matching (`:1096-1176`).

## Comparison with retained official run

The official all-family run remains intact and is not overwritten. Its command is retained in `runs/commands.json` as `python3 .../c2/survivors.py --json --out .../runs/c2-survivors.json`, with exit 2 (expected 0), stdout SHA-256 `bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829`, and stderr SHA-256 `9da3990cc432a14257f7e85d4f0cb30b709b9ee6e433967897e7315be30a21ec`. Its result JSON records tool SHA-256 `2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d`, counts 15 before → 2 after, and the two b-family current results FC-target and FC-f6cache as inconclusive (`runs/c2-survivors.exit:1`, `runs/c2-survivors.stderr:9-12`, `runs/c2-survivors.json:3332-3365,4711-4728`). The fresh b/c/d run at the pushed commit uses a different survivor-script digest and returns 0; it resolves those two composite outcomes within this selected family set. This does not retroactively change the earlier official evidence and does not measure families a/e.

## Containment, limits, installs, blockers

The run's bind guard recorded 474 binds across 466 distinct ephemeral ports (49204–60993), no protected-port hits, and `ss -ltnpH` ownership check `owned: []`; teardown reports no marked stragglers and scratch removed (`rerun-bcd.json:1291-1312,1894-1899`). A separate post-run host `ss -ltnpH` showed other loopback listeners; I did not attribute or touch those. The harness's PID/port ownership result is the evidence that none belonged to this run. No 8080/34113 listener, service, or global state was intentionally used or changed.

No tools were installed or updated. No blocker. Limits: only named families b/c/d were rerun; this supports the bounded named-survivor claim, not all C2 families, unseen-mutant immunity, live-service health, or outside/non-author admission. The only main-arm evidence for FC-target and FC-f6cache remains own-fault exit 2; their kills depend on the named selftest controls, which is explicitly recorded rather than hidden.
