VERDICT: confirm - the marker-removal mutant is killed by the existing selftest; exit-1 tracebacks are never credited as rejection.

Scope: one advisory scratch-only mutation; no integration, registry, production or committed-evidence edits.
Axes: verdict soundness; mutation sensitivity; byte-exact restoration.
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py:82-93,188-300 (current bytes, not a Git reconstruction).
Mutant: line 87 only, `elif code == 1 and out.startswith("INVALID "):` -> `elif code == 1:`; exit 1 and the earlier traceback guard remain.
Expected detector: the unchanged `--selftest` must fail on the marker-removal mutant, not count its silent exit-1 gate as a genuine rejection.
Environment for every invocation: TMPDIR=/tmp/kama-r20-MutGridMarker; PYTHONDONTWRITEBYTECODE=1; cwd=/tmp/kama-r20-MutGridMarker.
Each subprocess had timeout 90s (outer capture bound 95s); identical checks and expected results ran on pristine, mutated and restored bytes.

Exact selftest command: `timeout 90s python3 /tmp/kama-r20-MutGridMarker/install-tree-grid.py --selftest`
Observed selftest exit sequence (pristine / mutated / restored): 0 / 1 / 0.
Pristine and restored stdout (stderr empty):
`selftest: genuine verdicts, absent/bad input, crash, silent exit 1, signal, unknown exit, post-INVALID tracebacks, stderr-only INVALID and timeout passed`
Mutated stdout empty; stderr verbatim:
```text
SELFTEST FAIL silent exit 1: exit=0 baseline='VALID' row='rejected' rejected=1 errors=0
SELFTEST FAIL stderr-only INVALID: exit=0 baseline='VALID' row='rejected' rejected=1 errors=0
```

Fixture: copied check-receipt.py; receipt.json is JSON of its runpy `_selftest_receipt()`; member libllama.so; tree pin 24f0b0a81302abd039376b09dccdc2082a5ec5e1e3e08138f41c57d554e43bf1.
The private traceback-gate.py contained exactly:
```python
import json, sys
receipt = json.load(open(sys.argv[1], encoding='utf-8'))
if receipt['server']['install_tree_sha256'] == '24f0b0a81302abd039376b09dccdc2082a5ec5e1e3e08138f41c57d554e43bf1':
    print('VALID synthetic baseline')
    raise SystemExit(0)
raise RuntimeError('injected gate crash')
```
silent-gate.py used the same first five lines, followed by `raise SystemExit(1)` instead of RuntimeError.
Exact injected traceback command: `timeout 90s python3 /tmp/kama-r20-MutGridMarker/install-tree-grid.py --gate /tmp/kama-r20-MutGridMarker/traceback-gate.py --receipt /tmp/kama-r20-MutGridMarker/receipt.json --model-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --server-sha bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb --impl-sha dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd --probe-sha cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc --tool-sha 9999999999999999999999999999999999999999999999999999999999999999 --tree-sha 24f0b0a81302abd039376b09dccdc2082a5ec5e1e3e08138f41c57d554e43bf1 --members libllama.so --json`
Traceback output in ALL phases: grid exit=2; baseline="VALID"; members=1; rejected=0; errors=1; row gate_exit=1, status="error", stdout="", error="traceback in gate output (exit 1)".
Captured row stderr: `Traceback (most recent call last):` then traceback-gate.py line 6, `raise RuntimeError('injected gate crash')`, `RuntimeError: injected gate crash`.
Grid stderr in ALL phases: `install-tree-grid: 1 member gate run(s) gave no verdict`.
Exact positive-control command: `timeout 90s python3 /tmp/kama-r20-MutGridMarker/install-tree-grid.py --gate /tmp/kama-r20-MutGridMarker/check-receipt.py --receipt /tmp/kama-r20-MutGridMarker/receipt.json --model-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --server-sha bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb --impl-sha dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd --probe-sha cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc --tool-sha 9999999999999999999999999999999999999999999999999999999999999999 --tree-sha 24f0b0a81302abd039376b09dccdc2082a5ec5e1e3e08138f41c57d554e43bf1 --members libllama.so --json`
Positive control in ALL phases: grid exit=0; baseline="VALID"; members=1; rejected=1; errors=0; row gate_exit=1, status="rejected", stdout starts `INVALID `, stderr="".
Its genuine gate finding named server.install_tree_sha256 3f45a44ff7c48fa1462d7905cfdee3f8c155ccaa109f46fd87402b3bf4bd9846 versus the pinned tree; grid stderr empty.
Exact marker-sensitive control command: `timeout 90s python3 /tmp/kama-r20-MutGridMarker/install-tree-grid.py --gate /tmp/kama-r20-MutGridMarker/silent-gate.py --receipt /tmp/kama-r20-MutGridMarker/receipt.json --model-sha aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa --server-sha bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb --impl-sha dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd --probe-sha cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc --tool-sha 9999999999999999999999999999999999999999999999999999999999999999 --tree-sha 24f0b0a81302abd039376b09dccdc2082a5ec5e1e3e08138f41c57d554e43bf1 --members libllama.so --json`
Silent exit-1 output pristine/restored: grid exit=2, baseline="VALID", rejected=0, errors=1, row gate_exit=1/status="error", error="no verdict line for exit 1".
Silent exit-1 output mutated: grid exit=0, baseline="VALID", rejected=1, errors=0, row gate_exit=1/status="rejected", stdout="", stderr="" (the defect, NOT a valid detector pass).
Combined in-memory detector required selftest exit 0 plus those three CLI expectations; observed detector result sequence 0 / 1 / 0.
Attribution: KILLED by silent-exit-1 and stderr-only-INVALID selftest cases (source:267-285); traceback-only probe is non-discriminating/SURVIVED because source:82-84 still overrides exit 1.

SHA-256 pristine scratch and original lane before: d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5
SHA-256 mutated scratch: 81cfc4a3782726a9cb21f63573986e6cd29110e4f65099b6abbe14a735ff01c3
SHA-256 restored scratch and original lane after: d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5
Copied check-receipt.py SHA-256: a0dc1d07220ff804e375d5947ed8119a3ae697da5dbd0cc83006b2abe39043a6.
Restoration: finally-block shutil.copyfile from private pristine backup; observed restored_bytes_equal=True before repeating the unchanged detector.
Cleanup: shutil.rmtree(/tmp/kama-r20-MutGridMarker), observed scratch_removed=True before filing this report. No installs or other runtimes.
Limit: this single mutant and bounded regression set do not establish an exhaustive error census or alter C1/C2 scope.
Report: .ufo/waves/round-20/falsify/advice/MutGridMarker.md
