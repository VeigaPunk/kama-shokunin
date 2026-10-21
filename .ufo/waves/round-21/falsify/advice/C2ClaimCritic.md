VERDICT: partial - 8->8 holds only for the flat b11755 install; 0/13->13/13 is detection-by-construction; fail-closed refusal hits shipped OpenVINO layouts; "unreadable" misses read errors.

# C2ClaimCritic: C2 as an operability claim (round 21, FALSIFY)

Attacked: "C2 operability 8->8; fails closed on unreadable/partial trees" (corpus/lessons/round-21.md:20-26, :83-92). Code: producer a6617149 (sha256 e4cc6d88...), gate 6b876437...; both equal the grid's `current_sources_sha256`, so the measured code is the code I ran (scratch clone at a6617149).

## Q1 Is 0/13 -> 13/13 an operability move? No: integrity coverage, by construction.
- Frozen 0/13 is definitional: `install_tree` skips every non-regular entry (producer:194-195, body unchanged by the 7a6bc911..a6617149 diff). A producer that never reads links cannot move on link edits.
- Current 13/13 is definitional: `changed` = identity != real identity, and the identity hashes the link map (grid:224 sets expect_change for every non-null cell).
- Nothing is launched or graded. Without a pin the gate's chain check passes 7/13 link cells (5 soname retargets, 1 dev-link retarget, 1 added link) and rejects 6 (dangling, absolute, dotdot, delete, loop, `./name`, which stays inside the directory).
- Frozen "regular 3/3" counts regular-unreadable as detected: frozen silently drops the file and its digest moves. The grid has 19 cells; "13" is the link class only.
- Executed: `grid --arm current --json` exit 0 (pass; link 13/13, subdir 1/1, regular 3/3, type 1/1, null 0/1); `--arm frozen --json` exit 1 (fail, 14 wrong); `--selftest` exit 0 (13 cases). Outputs in out/C2ClaimCritic/outputs/.

## Q2 Does fail-closed refusal reduce operability? Yes, for one class.
`composition-probe.py` (exit 0) replays producer main() lines 1375-1379 against frozen 1268->1341:

| synthetic install | current snapshot | frozen snapshot |
|---|---|---|
| control | OK | OK |
| LICENSE mode 000 | REFUSE `LICENSE:unreadable` | OK; digest moved (member dropped) |
| docs/ subdir, benign | REFUSE `docs:not-regular-or-symlink` | OK; digest unchanged |
| glibc-hwcaps/ shadow | REFUSE | OK; digest unchanged (refusal correct: loader-shadow class, LinksLoaderProof S5) |
| EIO on readable member (injected) | OK, 3 of 4 members | OK, same silent drop |

Refusal raises before Popen (1377-1379 < 1454) and maps to setup-error exit 2 (1561). Frozen has no refusal between snapshot and Popen, so these layouts launched under frozen and refuse now.

## Q3 Real llama.cpp layouts, b11755 (36 assets; zips read by Range request, 3 requests each)

| asset | evidence | subdir in server dir | C2 |
|---|---|---|---|
| ubuntu-x64 (this lane's install) | EXACT: local sha256 753bfa73... = GitHub digest; `tar -tvzf` exit 0: 1 dir, 51 regular (50x0755, 1x0644), 10 relative links | no | OK; real tree 51/10, no problems |
| Windows zips: CPU, CUDA, ROCm, SYCL, Vulkan, OpenCL, cudart | EXACT: central directories | no | flat |
| win-openvino-2026.4.1-x64.zip | EXACT: `openvino-licensing/` + 12 regular license/EULA files | YES | would refuse |
| ubuntu-openvino-2026.4.1-x64.tar.gz, 121.8 MB | INFERENCE: release.yml:742 `cp -r docs/licensing $dest/openvino-licensing`, :745 `tar -C $dest .` | YES | would refuse [INFERENCE] |
| ubuntu cuda/vulkan/sycl/rocm/arm64 tar.gz | INFERENCE: `tar -C ./build/bin .` (:236, 315, 426, 1489, 1609) | probably no | OK [INFERENCE] |
| snapdragon/android tar.gz | INFERENCE: `cmake --install` (:584, 637) | unknown | libs in lib/ sit outside the pinned dir [INFERENCE] |
| xcframework.zip | EXACT: framework bundle, 27 dirs | not an install dir | n/a |

Mode checks are uid-dependent: root reads mode-000 files, so the same tree could snapshot differently by runner [INFERENCE; not run, no sudo used].

## Q4 Honest wording (replaces "fails closed on unreadable/partial trees")
> C2, integrity coverage (operability 8 -> 8 on the measured install only). Records every symlink directly in the llama-server directory (`install_links`, `install_links_sha256`) and refuses before launch on a non-regular non-symlink entry, a control-character name, a mode-denied member, or an lstat/readlink failure. Real b11755 install: snapshot OK. Synthetic grid: the link class moves the digest 13/13 (frozen 0/13: no link field); the gate's chain check without a pin rejects 6 of 13. Reported trade, not netted out: a subdirectory in the server directory (upstream OpenVINO) or a mode-denied member, which the frozen producer launched, now refuses. Not covered: read-time I/O errors on a readable member (install_tree still skips them, producer:196-199).

Score: 8 -> 8 holds only with that trade named (precedent SCORECARD.md:724-730). By the lane's own test "existing command paths still run" (SCORECARD.md:87), the OpenVINO class is a regression until fixed. L1 decides.

## Q5 Corrections, smallest first
1. `install_tree`: drop the read-time `except OSError: continue` (producer:198-199) so read errors fail closed (TreeFailClosed). Changes only read-error runs.
2. Subdirectories: refuse only `glibc-hwcaps/` and RUNPATH-listed dirs; digest other subtrees under a separate key so flat-tree digests stay byte-identical [INFERENCE, untested].
3. Grid: add a read-error cell, a benign-subdir cell with an expected verdict, and an upstream-shaped OpenVINO fixture; rename "13 cells" to "link class 13 of 19".
4. Gate: `./name` stays inside the directory but the "/" rule rejects it (grid message: "leaves the pinned directory"). A false rejection, not a loophole; normalise it or reword the message (optional).

## Limits and tooling
- Not run: llama-server, live harness, model fetch, root execution. Only zip central directories (3-10 KB per asset) were fetched; no tar.gz beyond the local one.
- Real tree: `find ~/.local/opt/llama-b11755 -newermt 2026-10-21 | wc -l` = 0, exit 0.
- Installs: none; used pre-installed gh 2.102.0 (read-only API), git, python3, curl, jq, tar, sha256sum.
- Out: .ufo/waves/round-21/falsify/out/C2ClaimCritic/ (composition-probe.py, zip-layouts.py, outputs/). Scratch /tmp/kama-r21-C2ClaimCritic removed.
