VERDICT: confirm - no ownership overlap; shared `/tmp` needs exact-path cleanup only

Placement: per the binding out-only deliverable boundary, this note is under `build/out/ConnectTsukuroi/`, not the requested `build/advice/` path. No lane source was edited.

## Evidence
- Pin: `tsukuroi-shokunin` HEAD `2fd1e6768f187be8c5e837af6286c3736953fcff`. `git rev-parse HEAD` returned that hash (exit 0); `git diff --quiet HEAD -- PROVINCE.md tools/tsukuroi-census.sh .ufo/waves/round-18/build/ConnSibling.md .ufo/waves/round-12/Security.md corpus/knowledge/census-closeout-receipt-r10.md` returned 0 (`tracked_diff_exit=0`).
- `PROVINCE.md:25-28` at that revision: “Refuses: endpoint/model serving health (→ kama)” and “Never installs, upgrades, or removes packages”. `PROVINCE.md:46` routes a wrong local endpoint/served-model identity to kama, while tsukuroi retains kernel/driver/device/user-unit state and says kama must obtain its own endpoint evidence. No llama.cpp serving ownership transfers to tsukuroi.
- `tools/tsukuroi-census.sh:594-613` runs `pacman -Qkk` on the bounded package sample; `nonroot_artifacts` is counted from that output’s checksum/permission warnings. [INFERENCE] This is not a general `$HOME` file inventory and does not make the kama GGUF cache part of tsukuroi’s owned package plane.
- Historical corroboration only: `.ufo/waves/round-18/build/ConnSibling.md:13` records kama’s llama-server under `~/.local/opt`, outside `-Qm`. It is not a fresh install/process observation. Repo-wide `gguf` search returned “No matches found” (search tool exposes no process exit; no shell rc claimed).
- Current cleanup pattern: `tools/tsukuroi-census.sh:1713-1716` uses a unique `mktemp` prefix and an EXIT/INT/TERM trap that restores permissions within its own `$work` tree before removing that exact tree. The round-10 receipt, `corpus/knowledge/census-closeout-receipt-r10.md:123-128,175-177`, records changing `/tmp` dirs as unattributable `[unk]` and recommends a lane-tagged prefix.
- Executed `/tmp` snapshot: `find /tmp -mindepth 1 -maxdepth 1 -type d -name 'kama-r20-*' -print | wc -l` → 38, `find_exit=0`; same command with `tsukuroi-r19-*` → 16, `find_exit=0`. These are directories found, not proof of stale residue or ownership. None were removed.

## Axes, move, risks
- Axes: C2 operability boundary is the direct concern; C1 calibration is not directly measured or changed by this scan. [INFERENCE] The handoff below avoids treating a package-plane counter as evidence about an offline model-file parser.
- Bounded handoff: keep C2’s read-only GGUF parse, lane-cache input, and official `gguf` oracle under kama. Per the C2 bounds, use the permitted `uv run --with gguf` route if needed; do not use pacman or launch llama-server. Clean only the exact per-seat `/tmp/kama-r20-<YourName>` directory created by that seat—never sweep the shared `kama-r20-*` prefix.
- Contradiction: generic tool-channel guidance puts pacman first, but C2’s bounds pause pacman host-wide and tsukuroi’s Province refuses package installs. The C2-specific UV allowance is the compatible path; no tool was installed or updated in this scan.
- Risks: the r18 llama path is historical; `/tmp` counts are time-sensitive and cannot identify active owners. A prefix-wide cleanup could remove sibling work, so no such cleanup is proposed.

## Verification / actions
- Read-only source review and searches only; no endpoint calls, package operations, installs/updates, source edits, or tests. No scratch tree was created by this seat, so no seat-owned `/tmp` cleanup was needed.