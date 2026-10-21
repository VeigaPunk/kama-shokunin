VERDICT: confirm - KILLED: the pinned unknown-exit cell detects undeclared child exit 42 being classified as accepted; pristine/restored detectors exit 0 and the mutant detector exits 1.

Axes: behavioral detection, positive-control integrity, private isolation and exact restoration.
Scope: one mutation in /tmp/kama-r20-MutGridUnknownExit/install-tree-grid.py; no lane source, committed evidence or registry edits.
Source: /home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/install-tree-grid.py:69-93.
Mutation: insert immediately after original line 90, before the ERROR fallback:
```python
    elif code > 3:
        verdict, reason = "VALID", None
```
This accepts an undeclared positive child exit without a VALID output witness; it does not special-case 42.
Expected detector: /home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-cells.json:6 requires grid-unknown-exit => error; :8 requires the genuine INVALID control => rejected.
Fixture: /home/vgpnk/Projects/shokunin/kama-shokunin/registry/error-injection-fixtures/grid-gate.py:10-12 supplies VALID baseline, :19-20 exits 42 silently, :23-25 emits INVALID and exits 1.
Scoped driver: unchanged copies of /home/vgpnk/Projects/shokunin/kama-shokunin/tools/error-verdict-census.py load_registry (:116-138), run_grid (:220-240), and classify_grid (:164-179); compares the two selected cells with expected_current_class, matching the census comparison at :343-346.
The full 15-cell CLI, grid selftest, Git/citation/survivor probes and model runtimes were NOT run.

Exact detector command, repeated unchanged on pristine, mutated and restored grid bytes:
`timeout 75s env TMPDIR=/tmp/kama-r20-MutGridUnknownExit PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r20-MutGridUnknownExit/probe.py`
Working directory: /home/vgpnk/Projects/shokunin/kama-shokunin. Each run_grid subprocess has the existing 30-second bound; all completed.

Observed output (every cell baseline=VALID, members=1; child exit is distinct from grid/detector exit):
| Bytes | Cell | Child exit | Row | Rejected/errors | Grid exit | Detector exit |
|---|---|---:|---|---|---:|---:|
| pristine | unknown-exit | 42 | error | 0/1 | 2 | 0 |
| pristine | genuine INVALID control | 1 | rejected | 1/0 | 0 | 0 |
| mutated | unknown-exit | 42 | accepted | 0/0 | 1 | 1 |
| mutated | genuine INVALID control | 1 | rejected | 1/0 | 0 | 1 |
| restored | unknown-exit | 42 | error | 0/1 | 2 | 0 |
| restored | genuine INVALID control | 1 | rejected | 1/0 | 0 | 0 |
Pristine/restored unknown rows: stdout="", stderr="", error="no verdict line for exit 42"; grid stderr="install-tree-grid: 1 member gate run(s) gave no verdict\n".
Mutated unknown row: stdout="", stderr="", status="accepted"; grid stderr="". This was a real semantic mismatch, not a detector crash.
Positive control, all three phases: row stdout="INVALID synthetic mutant: 1 problem(s)", row stderr=""; grid stderr="".
Driver summaries: cells=2, current_misclassified=0/1/0 respectively, unrun=[] throughout; detector stderr empty throughout.

SHA-256 evidence (sha256sum exit 0; unchanged driver/fixtures/census/manifest across the probe):
- Original, pristine backup, restored scratch and before/after lane grid: d9689c0718a6001f808c00c7b5318327e0757713033e9df04994687a422650c5
- Mutated grid: 481d0817c5d92d2d40b741b11a5f0fccd417c1d7f3d3a86b8b116d6b4045be20
- Census helper, scratch and lane: f83f8a7029d95bb698cf4da6d1154c617a7559aa54668b947417b34b51200bc7
- Manifest, scratch and lane: ff3b7da9c060a7f12a7ca081c79db06899a4f5c9418d26ffe4a88bc6c607f469
- Gate fixture, scratch and lane: 0e65e584fe9d7bda52af233c7fd189555d4314b1b7ae6267b12cbf1e2d3bbb5f
- Scoped driver, before/after: 22fd376d2dabd7a8c2dc2cc50bb812564f6508f13030197956315fd946492bf3
Restoration ran in finally after the mutant detector: `cp /tmp/kama-r20-MutGridUnknownExit/install-tree-grid.pristine.py /tmp/kama-r20-MutGridUnknownExit/install-tree-grid.py` => exit 0.
`cmp -s /tmp/kama-r20-MutGridUnknownExit/install-tree-grid.pristine.py /tmp/kama-r20-MutGridUnknownExit/install-tree-grid.py` => exit 0, no output; restored detector then observed the original behavior as shown above (cmp was recorded after that run).
Cleanup: `rm -rf -- /tmp/kama-r20-MutGridUnknownExit` => exit 0, no output.
Absence: `test ! -e /tmp/kama-r20-MutGridUnknownExit` => exit 0, no output.
No installs/updates, lane edits, delegated probes or other runtime invocation. Finding is limited to this named regression cell, not an exhaustive error census.

Report: .ufo/waves/round-20/falsify/advice/MutGridUnknownExit.md
