VERDICT: partial - removing timeout-to-error handling loses the structured timeout row, but the mutant survives the pinned error-class detector.

## Mutant and expected detector
- Only the private scratch grid was mutated: deleted the `except subprocess.TimeoutExpired` branch and its two-line ERROR return, originally lines 76–78 of /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py. No second mutation was attempted.
- /home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-cells.json:5 pins `grid-timeout` to current class `error`; :8 supplies the genuine-rejection positive control, `grid-real-invalid-verdict` -> `rejected`.
- The unchanged detector used /home/vgpnk/Projects/shokunin/kama-shokunin/tools/error-verdict-census.py:220–240 (`run_grid`), :75–91 (30-second bounded child), and :164–181 (`classify_grid`). No Git operation or full census was invoked.
- Only the two named cells ran, on pristine, mutated, then exactly restored bytes. Detector PASS/exit 0 required both named classes to match and both children to run; structured JSON presence was recorded, not added to the pinned class contract.
- /home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-fixtures/sitecustomize.py:13–16 intercepts only the non-baseline grid-gate call and immediately raises TimeoutExpired. The fixture bytes matched the runner's pinned digest. No sleeping gate or long hang was used; “300 seconds” below is the injected exception's timeout argument, not elapsed time.

## Exact commands and observed output
Same top-level command for all three phases (each exited 0):
```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r20-MutGridTimeout python3 /tmp/kama-r20-MutGridTimeout/probe.py
```
The unchanged scratch probe imported the copied census, verified manifest/fixture hashes, called `run_grid` for the two named cells, and logged the existing bounded child's command/exit/stdout/stderr. All temporary directories were under the private scratch root.
Actual mutated timeout child command (exit 2, RAN=True; run_grid supplied CENSUS_GATE_MODE=timeout and PYTHONPATH pointing at its private work directory):
```sh
/usr/bin/python3 /tmp/kama-r20-MutGridTimeout/error-verdict-grid-z15ljib7/tests/llamacpp-live/install-tree-grid.py --gate /tmp/kama-r20-MutGridTimeout/error-verdict-grid-z15ljib7/grid-gate.py --receipt /tmp/kama-r20-MutGridTimeout/error-verdict-grid-z15ljib7/receipt.json --model-sha model --server-sha server --impl-sha impl --probe-sha probe --tool-sha tool --members libllama.so.0.7.0 --json
```
| Bytes | Timeout child exit | Observed pinned class | Structured timeout error | Positive-control child exit/class | Detector |
|---|---:|---|---|---|---|
| Pristine | 2 | error | True | 0 / rejected | PASS / 0 |
| Mutated | 2 | error | False | 0 / rejected | PASS / 0 |
| Restored | 2 | error | True | 0 / rejected | PASS / 0 |
Pristine/restored timeout stdout excerpts: `"baseline": "VALID"`, `"members": 1`, `"rejected": 0`, `"errors": 1`, row `"gate_exit": null`, `"status": "error"`, `"error": "timeout after 300s"`.
Pristine/restored timeout stderr exactly: `install-tree-grid: 1 member gate run(s) gave no verdict\n`.
Mutated timeout stdout exactly: empty. Stderr contained `install-tree-grid: internal error: Command`, `timed out after 300 seconds`, `Traceback (most recent call last):`, and `subprocess.TimeoutExpired:`; its traceback located the immediate fixture raise at private sitecustomize.py:16.
All three positive controls produced baseline VALID, rejected=1, errors=0, row status=rejected, gate_exit=1, stdout=`INVALID synthetic mutant: 1 problem(s)`, empty stderr; the grid child exited 0. These are excerpts/field observations, not assertions of full-document equality.
All three timeout logs ended `CLASS=error EXPECTED=error MATCH=True`; all three control logs ended `CLASS=rejected EXPECTED=rejected MATCH=True`; all three detectors printed `DETECTOR=PASS`.

## Mutation verdict and scope
SURVIVED, not killed or inconclusive: the pristine detector passed, and the same detector also passed on mutated and restored bytes.
The requested loss of the pinned current class was NOT observed. The removed conversion did lose the structured member error, but /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py:303–309 catches the exception, prints a traceback and exits 2; /home/vgpnk/Projects/shokunin/kama-shokunin/tools/error-verdict-census.py:180–181 classifies a non-JSON traceback as `error`.
This is a timeout-handler mutation coverage finding, not authority to broaden the finite class contract or claim a false accepted/rejected verdict. It does not adjudicate C1 as a whole.

## Hashes, restoration and cleanup
SHA-256 of grid before = restored = untouched lane after:
`d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`
SHA-256 of mutated grid:
`1b74ee4e82ff9424dcf0d803ca973307613a81bbf4c0cf8ff6c4159113393e62`
Detector script SHA-256 (same script in every phase): `4f1f2dd40e57cdd8b111d1783361e2c6dcaf3a1a4e94d6a9c427d6d05050d3ae`.
Census SHA-256, copied before and lane after: `f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7`.
Manifest SHA-256, copied before and lane after: `ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469`.
Gate fixture SHA-256, copied before and lane after: `0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f`.
Immediate-timeout fixture SHA-256, copied before and lane after: `6a467c6306862d740416a34b22178d3aae3f72812a43de0387df91bbd5e06ab1`.
Exact-byte restoration: `cmp --silent /tmp/kama-r20-MutGridTimeout/install-tree-grid.pristine.py /tmp/kama-r20-MutGridTimeout/install-tree-grid.py` exited 0 before the restored run; restored SHA-256 matched the pristine backup and lane source.
Cleanup: `rm -r -- /tmp/kama-r20-MutGridTimeout && test ! -e /tmp/kama-r20-MutGridTimeout` exited 0. Scratch and detector were removed. No lane/registry/evidence edits, installations, services, model loads, or other-runtime dispatches occurred; only this report was written in the lane.
