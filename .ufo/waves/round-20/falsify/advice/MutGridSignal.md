VERDICT: confirm - removing the explicit signal guard still leaves SIGKILL classified as error, never accepted/rejected; the mutant survived.

## Scope and mutant
- Advisory mutation probe only; axes: verdict-class safety, detector sensitivity, scratch isolation, exact restoration.
- Copied current lane bytes into `/tmp/kama-r20-MutGridSignal`; no Git/JJ operations, production edits, registry/evidence writes, installs, services or model loads.
- Target: `tests/llamacpp-live/install-tree-grid.py:85-86`; deleted only these two scratch lines:
```python
    elif code < 0:
        verdict, reason = "ERROR", f"killed by signal {-code}"
```
- Fixture: `registry/error-injection-fixtures/grid-gate.py:10-18` emits VALID baseline then kills its own mutant child with SIGKILL. Its accept/invalid arms are at lines 23-31.
- Pinned contract: `registry/error-injection-cells.json:4` expects grid-signal=error; frozen witness `.ufo/waves/round-20/runs/0957ce61/error-pair.stdout:35-43` records the same current class.

## Expected detector and exact commands
- One unchanged scratch detector reused copied census `child`, `env_for`, `doc`, and `classify_grid` (`tools/error-verdict-census.py:68-91,156-181`). Each child was bounded to 30 seconds; its TMPDIR/HOME were the private scratch directory.
- Signal assertion: baseline=VALID, one member, grid exit=2, class/status=error, gate_exit=-9, rejected=0, errors=1, and status neither accepted nor rejected. Controls require the genuine accepted/rejected classes and matching exits below.
- Receipt bytes: `{"server":{"install_tree":{"libllama.so.0.7.0":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}}}` followed by newline; same minimal receipt/argv as census `run_grid` at lines 228-239.
- Detector invocations, each observed exit 0 and `CHECK signal PASS`, `CHECK accept PASS`, `CHECK invalid PASS`, `DETECTOR PASS`:
```sh
python3 -B /tmp/kama-r20-MutGridSignal/detect.py pristine
python3 -B /tmp/kama-r20-MutGridSignal/detect.py mutated
python3 -B /tmp/kama-r20-MutGridSignal/detect.py restored
```
- Exact signal child command (all three phases; same command for positive controls except `CENSUS_GATE_MODE=accept` / `CENSUS_GATE_MODE=invalid`):
```sh
CENSUS_GATE_MODE=signal /usr/bin/python3 /tmp/kama-r20-MutGridSignal/install-tree-grid.py --gate /tmp/kama-r20-MutGridSignal/grid-gate.py --receipt /tmp/kama-r20-MutGridSignal/receipt.json --model-sha model --server-sha server --impl-sha impl --probe-sha probe --tool-sha tool --members libllama.so.0.7.0 --json
```

## Observed output and positive controls
Selected JSON fields, not a full-document-equality assertion; every run had baseline=VALID and members=1.
| Phase | Mode | Grid exit | Census class / row status | gate_exit | rejected / errors | Row output or error |
|---|---|---:|---|---:|---|---|
| pristine | signal | 2 | error | -9 | 0 / 1 | error=`killed by signal 9`; stdout/stderr empty |
| mutated | signal | 2 | error | -9 | 0 / 1 | error=`no verdict line for exit -9`; stdout/stderr empty |
| restored | signal | 2 | error | -9 | 0 / 1 | error=`killed by signal 9`; stdout/stderr empty |
| pristine | accept | 1 | accepted | 0 | 0 / 0 | stdout=`VALID synthetic mutant`; stderr empty |
| mutated | accept | 1 | accepted | 0 | 0 / 0 | stdout=`VALID synthetic mutant`; stderr empty |
| restored | accept | 1 | accepted | 0 | 0 / 0 | stdout=`VALID synthetic mutant`; stderr empty |
| pristine | invalid | 0 | rejected | 1 | 1 / 0 | stdout=`INVALID synthetic mutant: 1 problem(s)`; stderr empty |
| mutated | invalid | 0 | rejected | 1 | 1 / 0 | stdout=`INVALID synthetic mutant: 1 problem(s)`; stderr empty |
| restored | invalid | 0 | rejected | 1 | 1 / 0 | stdout=`INVALID synthetic mutant: 1 problem(s)`; stderr empty |
- Grid stderr for each signal run was exactly `install-tree-grid: 1 member gate run(s) gave no verdict\n`; control grid stderr was empty.
- Mutation verdict: **SURVIVED**, not killed/inconclusive. The fallback ERROR at source lines 91-92 still catches negative exits; only exits 0/1 plus matching stdout can become VALID/INVALID (lines 87-90), then accepted/rejected (lines 152-153). No signal death received verdict credit.
- Sensitivity finding: the class/exit detector does not enforce the signal-specific diagnostic; it missed that diagnostic loss. This is not evidence of an unsafe class survivor and does not change the contract. No full census or exhaustive signal claim was attempted.

## Hashes, restoration and cleanup
- SHA256 grid before = restored = lane after: `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`.
- SHA256 mutated grid: `ff1b4889245062e665b9332f06c650db6edb97e080a9a3d9f0a56e6cac69d4ba`.
- SHA256 unchanged detector in all three phases: `b443c629fb21c054a3a97e785bad05d91fbde84cdbe2bf9e85e0abe97a018af4`.
- Fixture SHA256 before/after: `0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f`; copied census and lane census after: `f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7`.
- Restored the exact deleted lines before the restored run. Both `cmp /tmp/kama-r20-MutGridSignal/install-tree-grid.pristine /tmp/kama-r20-MutGridSignal/install-tree-grid.py` and `cmp /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py /tmp/kama-r20-MutGridSignal/install-tree-grid.py` exited 0; SHA256 equality above confirmed exact bytes.
- Cleanup command: `rm -r -- /tmp/kama-r20-MutGridSignal && test ! -e /tmp/kama-r20-MutGridSignal && printf 'scratch_removed=/tmp/kama-r20-MutGridSignal\ncleanup_exit=0\n'`; exit 0, output `scratch_removed=/tmp/kama-r20-MutGridSignal` and `cleanup_exit=0`.
Report: .ufo/waves/round-20/falsify/advice/MutGridSignal.md
