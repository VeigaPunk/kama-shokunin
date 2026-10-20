VERDICT: confirm — the no-harm claim for snapshot history holds: `test-snapshot.sh` is 30/30 on the current probe and goes red (27/30, exit 1) on the frozen pre-round probe, with all three failures inside the `MODEL_LOADING` baseline family.

# Attack

Target: C1 claim in `corpus/lessons/round-16.md:95` — "C1 no-harm: `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0` (was 24; the new cases assert a `MODEL_LOADING` baseline row is kept and an unknown verdict is still dropped)."

Question: is that 30/0 a genuine capability detector, or a tautology that would also pass on the pre-round probe? Method: restore the frozen probe (manifest-attested) under an otherwise identical copy of `tools/` and re-run.

## R0 — baseline, lane tools, unmodified

```
$ bash tools/test-snapshot.sh            # cwd = lane root
...
PASS symlinked history dir refused
RESULT pass=30 fail=0
EXIT=0
```

30 asserts, all pass, including the three `MODEL_LOADING` ones:
`MODEL_LOADING baseline row accepted and diffed`, `... never audited as malformed`, `... never warns`.

## R1 — frozen-probe swap

```
$ mkdir -p /tmp/kama-r16-RerunSnapshotHarness
$ cp -a <lane>/tools /tmp/kama-r16-RerunSnapshotHarness/tools
$ cp <lane>/.ufo/waves/round-16/frozen/kama-probe-before.sh \
     /tmp/kama-r16-RerunSnapshotHarness/tools/kama-probe.sh
```

Digest identity confirmed both before and after the copy:

```
93ee4302...97a2cd64  .../frozen/kama-probe-before.sh
93ee4302...97a2cd64  /tmp/kama-r16-RerunSnapshotHarness/tools/kama-probe.sh
6edd3c4c...5972fa50  <lane>/tools/kama-probe.sh        (current, different)
```

`frozen/manifest.json` names sha256 `93ee4302…cd64`, source commit `20e392e`, source blob `447e29b3…` — matches the frozen file, so the control artifact is the attested pre-round probe.

Structural delta (diff frozen→current), the mechanism under test:
- `895c939`: `diff_baseline` verdict whitelist gains `* MODEL_LOADING *`. The frozen file contains **zero** occurrences of `MODEL_LOADING` (`grep -n 'MODEL_LOADING' frozen/kama-probe-before.sh` → only the whitelist line matched via the alternation; no literal hit).
- `412a420,448`: new `body_is_llamacpp_loading` classifier (absent in frozen).
- `466a503,509`: new `MODEL_LOADING`/`llamacpp-loading` classification branch (absent in frozen).
- `704,705c748,749` + `680c723` + `689a733`: `listeners` summary gains `model_loading` (outside snapshot, listed for completeness).

## R2 — frozen probe through the copied harness

```
$ bash /tmp/kama-r16-RerunSnapshotHarness/tools/test-snapshot.sh
...
PASS grown-vocabulary baseline keeps drift exit 2
FAIL MODEL_LOADING baseline row accepted and diffed (pattern fixture-a row-absent \(was verdict=MODEL_LOADING absent)
FAIL MODEL_LOADING baseline row dropped as malformed
FAIL MODEL_LOADING baseline row warned as malformed
PASS unknown verdict still warns
PASS unknown verdict still audited and dropped
...
RESULT pass=27 fail=3
EXIT=1
```

Exactly three failures, all in the `MODEL_LOADING` baseline family; the other 27 assertions pass identically. Note the second and third are the *negative* guards (the harness flags the row being dropped/warned as malformed), so they fail precisely because the frozen probe takes the malformed path. The unknown-verdict control (`MODEL_LOADED`) still passes on the frozen probe, proving the drop is specific to the widened vocabulary and not a general fixture breakage.

## R3 — control that the copy itself is not the cause

```
$ KAMA_PROBE=<lane>/tools/kama-probe.sh bash /tmp/kama-r16-RerunSnapshotHarness/tools/test-snapshot.sh
RESULT pass=30 fail=0
EXIT=0
```

Same copied harness, current probe → 30/0. So R2's red is attributable to the frozen probe alone, not to the copy, cwd, or temp-dir handling. `bash -n` on both copied scripts → exit 0; the frozen probe sources no auxiliary files (`grep '^[[:space:]]*(source|\.)[[:space:]]'` → no match), so relocation cannot have broken it.

## R4 — direct behavioral reproduction (no harness), seeded `latest.tsv`

Registry: one row `fixture-a` → dead port 34199, `expected_model_id=fixture-model`.
Seeded baseline (`latest.tsv`), same seed fed to both probes:

```
fixture-a	MODEL_LOADING	llamacpp-loading	-	34199	yes
fixture-z	MODEL_LOADED	bogus	-	34199	no
```

Frozen probe, exit 2:

```
[kama-probe] latest.tsv: dropping malformed baseline row for id='fixture-a'
[kama-probe] latest.tsv: dropping malformed baseline row for id='fixture-z'
[kama-probe] latest.tsv has no usable baseline rows — rebaselining
snapshot=20261020T135412Z prev=- rows=1 model_ok=0 drift=1 transitions=0 exit=2
DELTA.md:
- 2026-10-20T13:54:12Z baseline-note malformed-row-dropped id='fixture-a'
- 2026-10-20T13:54:12Z baseline-note malformed-row-dropped id='fixture-z'
- 2026-10-20T13:54:12Z baseline recorded (1 rows); transitions begin with the next snapshot
```

Current probe, exit 2, same seed:

```
[kama-probe] latest.tsv: dropping malformed baseline row for id='fixture-z'
[kama-probe] latest.tsv had malformed rows (dropped); this snapshot rebaselines them
snapshot=20261020T135412Z prev=- rows=1 model_ok=0 drift=1 transitions=2 exit=2
DELTA.md:
- 2026-10-20T13:54:12Z baseline-note malformed-row-dropped id='fixture-z'
- 2026-10-20T13:54:12Z fixture-a verdict MODEL_LOADING -> DEAD
- 2026-10-20T13:54:12Z fixture-a reason llamacpp-loading -> connection-refused
```

This isolates the behavioral difference the test encodes: on the frozen probe a `MODEL_LOADING` baseline row is destroyed and the real `MODEL_LOADING → DEAD` transition is lost (`transitions=0`); on the current probe both transitions are recorded (`transitions=2`). The near-miss `MODEL_LOADED` is dropped in both.

## Findings

1. **No actionable defect in the current probe's snapshot path.** The frozen probe's behavior is the documented rollback limit in `corpus/knowledge/snapshot-history.md:113-114` ("an older probe copy reading a history written by the new probe would drop `MODEL_LOADING` rows as malformed (rollback limit)"). My R2/R4 measurements reproduce that sentence exactly. The claim is honest and matches observation.
2. **The three new asserts are sensitive, not tautological.** A test that merely re-read 30/0 on the old probe would have been worthless; it does not — R2 flips exactly those three, and R3 rules out harness drift.
3. **Degradation is loud, not silent.** On the frozen probe the loss is warned on stderr and audited in `DELTA.md` as `baseline-note malformed-row-dropped`, so no reader of the ledger is silently misled about row identity. The residual hazard is `transitions=0` masking a lost transition, which is exactly what the warning and audit line announce.
4. **Coverage gap [INFERENCE from code reading, not exercised]:** `tools/test-snapshot.sh` seeds `MODEL_LOADING` in `latest.tsv`; its only loopback fixture serves `200 /v1/models` + `200 /health` and never a 503 loading envelope. Therefore the snapshot suite covers the **baseline-diff whitelist** half of the change, not the live `classify` branch. Live classification is covered elsewhere (`tests/probe-verdicts/check.py`, and C2's live receipt), so this is a scoping note, not a hole in the no-harm claim; the knowledge correction's wording ("The six new assertions check that a seeded `latest.tsv` row ... is accepted by `diff_baseline`") states the scope correctly.
5. **Durability risk:** nothing under `tools/` or `tests/` invokes `test-snapshot.sh`; `grep -rn test-snapshot tools tests registry SKILL.md` finds only documentation references (`corpus/knowledge/snapshot-history.md`, `corpus/lessons/*`, `SKILL.md:298,303,306,314`). The no-harm guarantee is therefore enforced only on manual invocation. This matches the lane's documented invocation-contract stance (no scheduler installed), so it is a residual risk to state, not a regression introduced this round.
6. **Tracked history untouched.** The harness uses `mktemp -d` and `rm -rf`s it on exit; `ls -d /tmp/kama-snapshot-test.*` after both runs → no leftover fixture dirs. R4 wrote only under my `/tmp` scratch.

## Limitations

- This seat did not start, bind, or probe 8080/34113, and did not start `llama-server`; `pgrep -x llama-server` → empty, `ss -ltn` on both ports → clear, after all work.
- Live `MODEL_LOADING` classification (503 envelope) was not re-exercised here; that is C1/C2's scope and R4 deliberately used a dead port.
- The 3rd negative assert's label ("warned as malformed") is the failure label, not a separate behavior; the underlying condition is the stderr warning quoted in R4.
- Procedural disclosure: a broad `grep -rn "test-snapshot" .` (lane root, before I bounded it) returned matches from `.ufo/interactive-sessions/`. I did not open those files and ran no further search under that directory; the banned-path access was incidental grep context only.

## Installs

None. No package, tool, or binary was installed or upgraded. All commands used the lane's existing `bash`, `curl`, `flock`, `python3`, `ss`, `sha256sum`, `diff`.

## Re-run recipe

```
bash <lane>/tools/test-snapshot.sh                                   # expect RESULT pass=30 fail=0, exit 0
cp -a <lane>/tools /tmp/x/tools && cp <lane>/.ufo/waves/round-16/frozen/kama-probe-before.sh /tmp/x/tools/kama-probe.sh
bash /tmp/x/tools/test-snapshot.sh                                   # expect RESULT pass=27 fail=3, exit 1
```
