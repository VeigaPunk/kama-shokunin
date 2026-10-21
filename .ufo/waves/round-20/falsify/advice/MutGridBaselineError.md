VERDICT: confirm - pristine/restored ERROR baselines earn zero rejections; the single-line guard-bypass mutant is killed by the bounded output detector.

## Mutant and expected detector
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py:137-140,150-159,175-179.
Only scratch source change at line 140: `for member in (members if baseline == "VALID" else []):` -> `for member in members:`.
Scratch root: /tmp/kama-r20-MutGridBaselineError; no lane/registry/committed-evidence edits.
Synthetic receipt: server.install_tree contains libllama.so with digest `b` repeated 64 times; install_tree_sha256 is `c` repeated 64 times.
Synthetic gate: when receipt basename is baseline.json and PROBE_BASELINE_MODE=error, exit 42 silently; with mode=valid, print `VALID synthetic baseline` and exit 0. Every mutant prints `INVALID synthetic mutant: 1 problem(s)` and exits 1.
Detector requires ERROR case grid exit 2, baseline=ERROR, members=0, rejected=0, errors=0, rows=[]; positive control requires grid exit 0, baseline=VALID, one rejected row, rejected=1, errors=0.
Each child grid invocation has subprocess timeout=10 seconds; each detector command has tool timeout=30 seconds. All generated grid temporary directories were confined by TMPDIR to the private scratch root.

## Exact commands
The same command was run on pristine, mutated and restored bytes: `python3 /tmp/kama-r20-MutGridBaselineError/probe.py`.
Positive-control child command, printed by that detector on all three runs:
`env TMPDIR=/tmp/kama-r20-MutGridBaselineError PROBE_BASELINE_MODE=valid PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /tmp/kama-r20-MutGridBaselineError/install-tree-grid.py --gate /tmp/kama-r20-MutGridBaselineError/gate.py --receipt /tmp/kama-r20-MutGridBaselineError/receipt.json --model-sha 0000000000000000000000000000000000000000000000000000000000000000 --server-sha 0000000000000000000000000000000000000000000000000000000000000000 --impl-sha 0000000000000000000000000000000000000000000000000000000000000000 --probe-sha 0000000000000000000000000000000000000000000000000000000000000000 --tool-sha 0000000000000000000000000000000000000000000000000000000000000000 --members libllama.so --json`
ERROR-baseline child command, printed by that detector on all three runs:
`env TMPDIR=/tmp/kama-r20-MutGridBaselineError PROBE_BASELINE_MODE=error PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 /tmp/kama-r20-MutGridBaselineError/install-tree-grid.py --gate /tmp/kama-r20-MutGridBaselineError/gate.py --receipt /tmp/kama-r20-MutGridBaselineError/receipt.json --model-sha 0000000000000000000000000000000000000000000000000000000000000000 --server-sha 0000000000000000000000000000000000000000000000000000000000000000 --impl-sha 0000000000000000000000000000000000000000000000000000000000000000 --probe-sha 0000000000000000000000000000000000000000000000000000000000000000 --tool-sha 0000000000000000000000000000000000000000000000000000000000000000 --members libllama.so --json`

## Observed outputs and verdict
Pristine: positive-control assertion=PASS; error-baseline assertion=PASS; detector=PASS; detector exit 0.
Mutated: positive-control assertion=PASS; error-baseline assertion=FAIL; detector=FAIL; detector exit 1.
Restored: positive-control assertion=PASS; error-baseline assertion=PASS; detector=PASS; detector exit 0.
Positive-control grid exit 0 and stderr empty on all three runs. Its stdout, compacted without removing fields:
`{"baseline":"VALID","errors":0,"gate":"/tmp/kama-r20-MutGridBaselineError/gate.py","members":1,"receipt":"/tmp/kama-r20-MutGridBaselineError/receipt.json","rejected":1,"rows":[{"gate_exit":1,"member":"libllama.so","status":"rejected","stderr":"","stdout":"INVALID synthetic mutant: 1 problem(s)"}],"schema":"kama-install-tree-grid/v1","tree_pin":false}`
Pristine and restored ERROR-case grid exit 2; stdout, compacted without removing fields:
`{"baseline":"ERROR","errors":0,"gate":"/tmp/kama-r20-MutGridBaselineError/gate.py","members":0,"receipt":"/tmp/kama-r20-MutGridBaselineError/receipt.json","rejected":0,"rows":[],"schema":"kama-install-tree-grid/v1","tree_pin":false}`
Mutated ERROR-case grid exit 2; stdout, compacted without removing fields:
`{"baseline":"ERROR","errors":0,"gate":"/tmp/kama-r20-MutGridBaselineError/gate.py","members":1,"receipt":"/tmp/kama-r20-MutGridBaselineError/receipt.json","rejected":1,"rows":[{"gate_exit":1,"member":"libllama.so","status":"rejected","stderr":"","stdout":"INVALID synthetic mutant: 1 problem(s)"}],"schema":"kama-install-tree-grid/v1","tree_pin":false}`
All three ERROR-case stderr values: `install-tree-grid: baseline gate error: no verdict line for exit 42\n`.
Mutation verdict: KILLED, not inconclusive: pristine detector passed, bypass produced an observable spurious rejection count, restored detector passed. The mutant's exit 2 alone would not detect that misleading count.

## Hashes, restoration and cleanup
SHA-256 original lane source, pristine scratch, restored scratch, and final lane source: `d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5`.
SHA-256 mutated scratch: `0c515a07dac4c1cdfad4efc72b17e96dc68dd7332a69dc00ca322bfa8688716f`.
SHA-256 unchanged detector: `0850ae41b7b58d8d56a89b893526ed1f3daf9eb00b7e480dafdaa84cc17a75b5`.
SHA-256 unchanged synthetic gate: `4e87b08054ab4fb35f3d14ff2df44d1f44a96e7350f225669d9b8d1ca19e4814`.
SHA-256 unchanged receipt: `41bae33000b5869177ec29bcaa6e8872e314a75eda540855bf97ad66aac740f2`.
Restoration comparison: `cmp /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py /tmp/kama-r20-MutGridBaselineError/install-tree-grid.py` exited 0.
Cleanup: `rm -r -- /tmp/kama-r20-MutGridBaselineError && test ! -e /tmp/kama-r20-MutGridBaselineError` exited 0; emitted `restored_cmp_exit=0 scratch_removed=yes` in the chained command.
Scope: one synthetic unknown-exit ERROR baseline and one member; no stock --selftest/census run, no exhaustive error claim, no model/runtime load. No tools installed or updated.
