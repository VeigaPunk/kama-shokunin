# LowestAxis — round 22 C1: axis binding, lowest-axis obligation, saturation/window, why 7 → 7

Seat: KamaR22.LowestAxis (connector, read-only). Base observed: lane `HEAD` = `master` =
`10271460cc575fc2280aa831e442726385fc2319`. No builds/tests/runs executed; trace claims below
are static reads, marked `[INFERENCE]` where not executed. Owned path: this file only.
Installs: none.

## 1. Axis binding — verified, with one mislabel to correct

- `../shokunin.conf:52`: `kama|kama-shokunin|operability + calibration`.
- `SCORECARD.md` §Round 21 (line ~998): "Assigned axes operability 8 + calibration 7;
  calibration is the lowest non-retired assigned axis, below saturation 8".
- So the C1 claim works **calibration 7** (lowest); **operability is 8**, not 7. The goal
  string "lowest axis7 (operability8)" reads as calibration=7 / operability=8.
- **Contradiction in peer output:** `advice/CritRace.md:42,112` and `advice/SourceReject.md:1`
  label the claim "axis 7 operability (assigned lowest)". That conflicts with SCORECARD and
  shokunin.conf. L1 SHOULD normalize to "C1 calibration 7 → 7; operability 8 unchanged (no
  harm)" in the lesson/SCORECARD row; a C1 row saying "operability 7" would be a record defect
  of the kind round-19/20 errata had to retract.
- Unassigned owned axes also sit at 7 (depth 7, adjacency 7; freshness 8, coverage 9 per
  SCORECARD §Round 21). The lowest-axis rule is scoped to *assigned* axes
  (`../templates/round-prompt.md:15-17`), so they do not compete with calibration.

## 2. Lowest-axis obligation and stagnation nudge — binds, nudge inactive

- Saturation line 8/10 on every owned axis; window N = 4 rounds without a capability row
  (`SCORECARD.md:130-132`).
- Nudge condition (`../AXES.md:66-73`): *every* owned axis ≥ saturation **and** window expired.
  It fails on the first clause three times over: calibration 7, depth 7, adjacency 7.
- Window state: last capability row entered round 20 (`gguf-declared-identity-replay`);
  round 21 added none ("window 1 of 4"). A C1 calibration repair is not a capability row,
  so round 22 ends at **2 of 4** if nothing else enters. Irrelevant to the waiver anyway:
  calibration < 8 means the lowest-axis obligation binds regardless of window.
- Continuity: SCORECARD §Round 21 Planned names exactly this item — "an unreadable-member
  fail-closed rule for `install_tree` consumers outside the live producer". C1 is planned
  frontier, not invented scope.

## 3. Why the claim honestly stays calibration 7 → 7

1. **Precedent.** Every calibration claim rounds 12–21 landed 7 → 7; the one 7 → 8
   (round 19) was retracted by erratum (`SCORECARD.md:846-851`). Round 5's standing reason
   still applies: "correction of overclaims is not proof of externally calibrated judgment".
   No outside non-author spot-check of round 21 exists in the lane
   (`corpus/lessons/` has `round-21.md`, no `round-21-verifier-spotcheck.md`; SCORECARD §21
   Planned still lists it).
2. **The marginal delta is narrow — the frozen producer already refuses most cells.**
   `[INFERENCE, static trace of 10271460 tools/kama-llamacpp-live.py:178-262, 1413-1419]`
   The live producer calls `install_links(server_real, tree)`, whose cross-check
   (`not-hashed` when a regular readable member is absent from `tree`, `unreadable` via
   `os.access`, `<name>:<strerror>` on its own lstat failure, `listdir:<strerror>`) turns
   nearly every injected install_tree fault into `SetupError('install-tree-unpinnable:…')`
   *before* this round:

   | Fault (frozen) | `install_tree` API result | Frozen producer composition |
   |---|---|---|
   | listdir error (both scans) | `({}, None)` — incomplete, non-comparable | refused `listdir:…` |
   | listdir error (install_tree scan only) | `({}, None)` | refused: every regular member `not-hashed` |
   | lstat error, entry still present | comparable partial digest | refused (`<name>:<strerror>` or `not-hashed`) |
   | sha256_file Permission/OSError, library | comparable partial digest | refused `not-hashed` / `unreadable` |
   | sha256_file error, **server** | comparable partial digest | pre-empted: `sha256_file(server_real)` at line 1413 raises raw OSError → internal-fault path, never reaches install_tree |
   | member **vanishes** between scans (lstat/open FileNotFoundError, absent at install_links listdir) | comparable partial digest | **escapes** — no problem, partial identity written to receipt |
   | regular member **replaced by a directory** between lstat and open (IsADirectoryError; directory at install_links scan) | comparable partial digest | **escapes** — recorded only in `install_unpinned`, not refused |

   So the honest red-before is: (a) at the **API boundary** every lstat/read cell returns a
   comparable partial digest and listdir returns an incomplete null; (b) at the **producer
   boundary** only the two race-shaped cells escape. A C1 text saying "before, the producer
   emitted partial identities on permission errors" would overclaim.
3. **Mock-injected faults are not host observations** (no real-permission dependency by
   contract), no live run, and the CritRace residual windows (lstat→open swap, hash→exec)
   stay open. Refusal-on-raised-error is a calibration property of the instrument, not
   integrity/authentication.
4. Operability stays 8 → 8: no new serving capability; the refusal token path already exists.

## 4. Proposed move (one, bounded): two-boundary counting + two race cells

Affected axes: calibration (honesty of the before-state count) improves; operability
unharmed (no producer behavior beyond ApiFix's change).

- Matrix (`tests/llamacpp-live/install-io-grid.py`) SHOULD report each cell at **two
  boundaries**: `api` (install_tree raises `SetupError` vs returns) and `producer`
  (install_tree + `install_links(server, tree)` → refused vs identity emitted). Expected
  frozen outcomes: `api` violated on every fault cell; `producer` violated only on the two
  race cells. Current arm: refused at both boundaries on every fault cell; positive control
  digest byte-identical at both arms.
- Add the two deterministic race cells via `mock` `side_effect` that mutates the temp tree
  then raises: (i) `os.lstat`/`open` side_effect unlinks the member then raises
  `FileNotFoundError`; (ii) `open` side_effect replaces the member with a directory then
  raises `IsADirectoryError`. These are the only cells where the frozen *producer* leaks a
  partial identity, so they are the cells that make "after all consumers must refuse"
  red-before at the consumer level, not just the API level.
- Count **refused**, not **changed**. Mistake-mining note: round-21
  `install-links-grid.py` frozen arm scores `regular-unreadable` as `changed` (a smaller,
  well-formed digest) and credits it in "regular 3/3"; with no tree pin the gate accepts such
  a receipt (it only requires the server basename in `install_tree`,
  `tests/llamacpp-live/check-receipt.py:386-406`). "Changed" is detection-by-partial-identity
  and must not be reused as the refusal metric.
- Server-member read cells SHOULD be asserted at the `api` boundary only, or the
  producer-boundary expectation must name the line-1413 internal-fault precedence; demanding
  the `install-tree-unpinnable` token there yields a false red after the fix.
- Token grammar: `tests/llamacpp-live/unpinnable-e2e.py` requires
  `setup.startswith("install-tree-unpinnable:")` (colon). A bare
  `SetupError('install-tree-unpinnable')` from install_tree (SimplifyAPI's recommendation)
  fails that prefix if CallerRepair adds install_tree-fault e2e cells. Either raise
  `install-tree-unpinnable:<op>:<name>:<strerror>` (same grammar as the existing producer
  token) or have CallerRepair match the bare token explicitly. ApiFix/CallerRepair decide;
  the conflict must not be left implicit.

## 5. Risks

- Race cells via side_effect couple the grid to call order inside install_tree (lstat before
  open); ApiFix restructuring (e.g. `os.scandir`, single handler) can silently bypass the
  injection point. Matrix SHOULD assert each injected fault actually fired (call counter > 0)
  or report the cell as could-not-evaluate (exit 2), never as pass.
- `install-links-grid.py` `FROZEN_REV` is `7a6bc911`; install_tree is AST-identical there and
  at `10271460` (body hash `c9b5e78e178264c6` both, docstring excluded) so legacy frozen
  outcomes are unaffected, but the new Matrix MUST pin `10271460` per round contract.

## 6. Verification L1 should run after integration

- `python3 tests/llamacpp-live/install-io-grid.py --arm frozen --json` (expect exit 1;
  `api` violated on all fault cells, `producer` violated on exactly the 2 race cells),
  `--arm current --json` (exit 0), `--arm both --json` (exit 1), `--selftest` (exit 0).
- `python3 tools/kama-llamacpp-live.py --selftest` (exit 0; positive digest unchanged).
- `python3 tests/llamacpp-live/install-links-grid.py --arm current --json` (exit 0;
  `regular-unreadable` now refused via install_tree token; real tree gate-clean;
  `install_tree_sha256` unchanged vs frozen).
- `python3 tests/llamacpp-live/unpinnable-e2e.py …` with the round-21 recipe arguments
  (exit 0; prefix check consistent with the chosen token).
- `rg -n "operability 7|axis ?7 operability" corpus SCORECARD.md .ufo/waves/round-22` before
  commit: zero hits in admitted C1 text.
