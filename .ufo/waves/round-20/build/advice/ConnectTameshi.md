VERDICT: partial - tameshi's written method gives the right witness/timeout boundary, but its generic runner contradicts it.

# ConnectTameshi — kama C1 sibling-overlap scan

## Axes
- **Calibration (assigned lowest axis, 7):** the proposed move reduces false kill/survivor classifications; no scalar change is claimed.
- **Operability:** no proposed product/runtime changes; neutral.

## Evidence
Tameshi owns reusable fixture craft, but explicitly refuses endpoint health and editing sibling gates: `tameshi-shokunin/PROVINCE.md:14-20`. The overlap is a classification method, not a transfer of kama's product or gate ownership.

The governing method in `tameshi-shokunin/SKILL.md@6acaf4dd` is specific: green requires exit 0 plus PASS and the full count (`:189-194`); a kill requires red **and** full-count enumeration (`:191-194`); even a token-only failure can be a kill, so adjudicate exit and token/verdict, “never exit alone” (`:200-204`); timeout, crash before summary, and missing count are inconclusive, not kills, excluded from `killed/(killed+survived)` (`:208-212`). `corpus/QUALITY.md:77-85` separately requires every nonzero exit, including usage, to be classified.

**Contradiction; do not smooth over it:** tameshi's generic runner says any nonzero suite exit is red except 124/126/127 (`tools/mutate-and-run.sh:53-60`); implementation maps other nonzero exits to KILLED (`:537-542`). This disagrees with the SKILL rule for crashes before summary. Its recorded specific mutation cases also disclose exit-status-only grading (`corpus/knowledge/mutation-case-kumitate-round-gate.md:30-31`); therefore the runner is not a clean implementation of the written method. This scan follows the written method as the comparison contract, and reports the runner gap as risk.

Kama's frozen `tests/llamacpp-live/install-tree-grid.py@37bd4c5` claims exit 1 = INVALID/rejected and 2/3 = error, then classifies by gate return code alone (`:106-113`); its top-level exit 1 means a mutant survived (`:17-18, 128-129`). The frozen round-18 `survivors.py` selftest arm checks a named failure label, but does not require a completed mutant selftest count before returning killed (`:945-955`). These are direct analogues of tameshi's exit/token/full-count boundary.

## Executed evidence
Commands below ran in this task; no live server or endpoint was contacted.

1. From `kama-shokunin/.ufo/waves/round-20/build/out/ConnectTameshi/`: `python3 xlane-cells.py --out xlane-cells.receipt.json; echo "exit=$?"` → exit 0. Observed output:
   - `grid-invalid-verdict`: reject (expected verdict); `grid-uncaught-exception` and `grid-silent-exit-1`: reject (should be could-not-evaluate).
   - `grid-sigkill`, `grid-sigterm`, `grid-undeclared-exit-4`: accepted (should be could-not-evaluate); `grid-not-evaluated-3`: row error, aggregate grid exit 1 (survivor code).
   - tameshi runner: true kill → KILLED; uncaught exception, SIGTERM and SIGKILL → KILLED; timeout 124 and unavailable 127 → INCONCLUSIVE.
   - survivors arm: complete targeted failure → killed; targeted early abort with no summary → killed; signal → inconclusive.
   Receipt: `build/out/ConnectTameshi/xlane-cells.receipt.json` (pins exact frozen bytes and records `scratch_removed: true`).
2. Frozen-byte check command: `cd /home/vgpnk/Projects/shokunin/kama-shokunin && for p in tests/llamacpp-live/install-tree-grid.py .ufo/waves/round-18/c2/survivors.py tools/citation-provenance.py tests/llamacpp-live/check-receipt.py; do a=$(git show 37bd4c5bd456a2f8a54d3312c28495c321715856:$p | sha256sum | cut -c1-16); b=$(sha256sum < $p | cut -c1-16); echo "$p frozen=$a worktree=$b"; done; echo "exit=$?"; git rev-parse refs/heads/master; echo "exit=$?"` → exit 0. All four frozen/worktree prefixes matched; master was `37bd4c5bd456a2f8a54d3312c28495c321715856`.
3. Tameshi pin command: `git -C /home/vgpnk/Projects/shokunin/tameshi-shokunin rev-parse HEAD refs/heads/master` → exit 0; both were `6acaf4dd2f2a8c9de4312e89a05c0f5155c9f055`.

## One bounded move
For C1's error-injection census, record and adjudicate each cell as a **tool-specific verdict tuple**: declared exit class + emitted verdict token/finding + completion witness (full selftest count or terminal verdict line). Only a complete, attributable witness is a verdict; timeout, crash/signal, no token, incomplete count, and undeclared status are could-not-evaluate, never kill or survive. Keep such cells visible but outside `killed/(killed+survived)`; ensure an instrument's aggregate exit cannot fold an error row into “survived.” Freeze the error, signal, unexpected-code, and early-abort cells above alongside a positive true-verdict control.

This is a method alignment, not a universal exit-code table: kama tools already use different mappings, and tameshi's own generic runner has the contradiction stated above. Preserve raw exit/stdout/stderr and the per-tool map rather than equating exit 1 fleet-wide.

## Risks and verification
- **Risk/contradiction:** copying `mutate-and-run.sh`'s actual exit-only implementation would reintroduce crash-as-kill; use tameshi's documented witness rule and retain this disagreement explicitly.
- **Risk:** checking only per-row grid status misses its aggregation collision (an error row yields grid exit 1); census both row disposition and aggregate result.
- The probe covered fake offline cells only; `grid-hang` (the gate's hard-coded 300-second timeout) was not run. No behavior about that cell is claimed.
- After integration, verification should run the committed census against the frozen/current instrument bytes and assert exact raw tuple, row class, aggregate class, and denominator for each cell; retain the current positive control and run no live endpoint. This is a proposed verification, not run here.

Installs/updates: none.