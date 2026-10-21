# CritMistake — C1 attack: KQ29 criterion vs `install_tree` implementation gap

Seat: KamaR22.CritMistake (critic, read-only). Base master = frozen = `10271460cc575fc2280aa831e442726385fc2319` (lane HEAD = master, observed with `git rev-parse`). Only this file was written. No verification, builds, tests or runs were done. No tools were installed.

## Axes
- **A1 provenance**: is the red-before real at the level being claimed?
- **A2 operability (axis7, the claimed axis)**: the refusal reason must stay specific.
- **A3 identity preservation**: the success map and digest stay byte-identical, and symlinks and nonregular entries are still skipped.
- **A4 authority**: one owner per readability or completeness decision. Matrix counts must not double-count.

## Finding F1 (A1, false-provenance risk): at frozen master the producer path already fails closed. Only the bare helper is red.
Evidence, `tools/kama-llamacpp-live.py` at 10271460:
- Lines 178–202: `install_tree` returns `(tree, None)` when listdir fails, and `continue`s when lstat or member-hash fails. So the helper's contract really does produce a comparable partial digest. KQ29's "skipped unreadable member" (`corpus/QUALITY.md:152`) is violated **inside the helper**.
- Lines 1414–1419: the producer calls `install_links(server_real, tree)` with the map. Lines 256–261 then flag a regular member missing from `tree` as `<name>:not-hashed`, `os.access` false as `<name>:unreadable`, an lstat OSError as `<name>:<strerror>`, and a listdir OSError as `listdir:<strerror>`. Any problem raises `install-tree-unpinnable:<problems>`.
- Each fault class, traced through the frozen producer (mock injected only into `install_tree`'s calls, so `install_links` sees the healthy directory):
  - listdir fails: `tree={}`. Every regular member gets `not-hashed`, so the producer **refuses**.
  - lstat fails: the member is regular in `install_links` and absent from `tree`, so `not-hashed`, and the producer **refuses**.
  - `sha256_file` fails: the member gets `not-hashed`, and the producer **refuses**.
  - The same fault in both scans gives `listdir:`, `<name>:<strerror>` or `<name>:unreadable`, and the producer **refuses**.
- `corpus/lessons/round-21.md:134-137` already records exactly this: the producer refuses "unreadable members and regular members `install_tree` failed to hash".

So the honest red-before is limited to two things:
1. The bare `install_tree` return value.
2. Consumers that use it without `install_links(…, tree)`:
   - the producer selftest. Lines 1135–1136 call `install_links(server)` with **no tree**, which disables the `not-hashed` arm.
   - `install-links-grid.py:177-180`, the `with_links=False` (frozen) arm.
   - any external digest comparison.

There is a concrete harm counterexample for the bare helper. Take install A = {llama-server, libX.so} where libX.so is unreadable, and install B = {llama-server}. A yields `install_tree_sha256` equal to B's. `check-receipt.py:409-422` recomputes the digest over the map and checks `--expect-install-tree-sha256`. That self-consistent partial pair passes, because the gate cannot see the omission.

## Finding F2 (A2, regression on the claimed axis): a bare `SetupError('install-tree-unpinnable')` reduces producer diagnostics
`install_tree` runs before `install_links` (line 1414 runs before 1415). A colon-less, detail-free raise therefore pre-empts the frozen message for every fault class in F1:
- Frozen message: `install-tree-unpinnable:libX.so:not-hashed`, `install-tree-unpinnable:libX.so:Permission denied` or `install-tree-unpinnable:listdir:Permission denied`.
- New message: the bare token.

This is a net operability loss on axis7 at the very consumer C1 says it protects. It also creates a second shape for one token. `unpinnable-e2e.py:91-92` requires the `install-tree-unpinnable:` prefix with the colon. Other producer codes already carry detail after a colon: `server-not-executable:{path}` (line 1399), `install-tree-unpinnable:…` (line 1418). `SetupError.code` is a plain string (lines 154–159), so no subtype is needed.

## Finding F3 (A4): matrix double-counting and vacuous cells
- Injecting the fault only into `install_tree` is the only way to separate "helper refused" from "`install_links` refused". If the fault reaches both scans (real chmod, or a mock on global `os.lstat`), a refusal is attributable to `install_links`, and a frozen producer cell scores green.
- Lines 1193–1197 and the grid cell `regular-unreadable` (`install-links-grid.py:169-170`) depend on chmod. They are vacuous under root, because `os.access(…, R_OK)` is True for root. Do not count them as C1 evidence.
- After C1, `install_links`' `not-hashed` arm is reachable only by a caller-supplied partial map or by membership changing between the two scans. Keep it (SimplifyAPI agrees), but its docstring (lines 224–225, "regular members it failed to hash") goes stale. The `install_tree` docstring (lines 179–181) must state that it raises.

## Falsifiable rejection conditions (for the judge)
- **R1 (helper):** Inject an `OSError` subclass only into `install_tree`'s own listdir call, lstat call, or `sha256_file` open or read, in a temporary tree. If the current `install_tree` returns **any** tuple (non-empty map, empty map, digest or `None`) instead of raising `SetupError` whose `.code` starts with `install-tree-unpinnable`, reject C1.
- **R2 (provenance):** The C1 report or matrix may claim a frozen **producer-level** red-before for the F1 cells. That claim needs a frozen producer receipt with `setup_error` null (launch proceeded) for that fault. Absent that witness, reject the red-before as false provenance. The admissible red-before is the bare helper tuple plus the tree-less consumers named in F1.
- **R3 (axis7 non-regression):** For each fault cell, compare the current producer's `setup_error` with the frozen one. If the current string drops the member basename (or `listdir`) or the errno text that the frozen string carried, axis7 is harmed. Reject, or at least do not admit the score move.
- **R4 (identity):** If the success controls change `tree` or `install_tree_sha256` byte-for-byte, or stop returning, reject. The controls are: pristine regular members, intentional symlinks (soname chain), the non-hwcaps subdirectory `openvino-licensing/`, and an empty or regular-only directory.
- **R5 (attribution):** A fault cell counted as "refused" whose fault also reaches `install_links`' scan (global mock, or real chmod as root or non-root) cannot count toward the C1 red-to-green delta.

## Minimum remedy (contract, not code)
1. **Keep the detail.** `install_tree` raises `SetupError` in the existing colon form, carrying the same detail `install_links` emits:
   - `install-tree-unpinnable:listdir:<strerror>`
   - `install-tree-unpinnable:<name>:<strerror>` for lstat and read failures

   Do not add a subtype, a third return field or an error collector. The `not S_ISREG` skip stays unchanged.
2. **Rescope the C1 claim text.** It hardens the helper contract and its tree-less consumers. The producer receipt path was already fail-closed via `install_links(server_real, tree)` at 10271460. Do not claim a producer red-before without the R2 witness.
3. **Inject into `install_tree` only.** The matrix (Matrix seat) injects only into `install_tree`'s calls, for example by patching the module's `sha256_file` and an `os.lstat` / `os.listdir` keyed to the call site. It reports the helper outcome and the producer `setup_error` string separately (R3), with the R4 controls pinned.
4. **Update the docstrings:** `install_tree` raises on incomplete enumeration, and `install_links`' `not-hashed` covers caller partial maps and changes between the two scans. That is the cutover clean-up; no other code changes.

## Coordination
- ApiFix: the remedy above (F2) affects their raise strings.
- CallerRepair: `unpinnable-e2e.py:92` colon predicate, and the grid `identity()` frozen arm.
- Matrix: F3, R5.

Owned/written path: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/CritMistake.md`.

Report: .ufo/waves/round-22/build/advice/CritMistake.md
