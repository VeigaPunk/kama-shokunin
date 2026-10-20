# SentinelInstallChain — audit of L1's llama.cpp b11755 + stories260K install (read-only)

Seat: sentinel, advisory only. Axes named: **provenance integrity**, **channel compliance**, **loader/privilege safety**, **PATH hygiene**. All checks below are read-only (readelf, ldd/ld.so --list, stat/find, sha256sum, tarfile hash compare, pacman -Si/-Ss/-Fl queries, GitHub/HF public APIs). No installs, no pacman transactions, no writes except this file.

## Verdict summary

| # | Severity | Finding |
|---|----------|---------|
| F1 | none (pass) | Asset bytes == GitHub API digest; extracted tree == tarball, byte- and mode-exact |
| F2 | none (pass) | Model bytes == Hugging Face LFS oid for `tinyllamas/stories260K.gguf` |
| F3 | low (disclosure) | Channel order: pacman tier *has* a candidate (`extra/llama-cpp 0.6.0-1`); skipping it is justified by the host-wide pacman pause and the commit pin, but the report must say so |
| F4 | none (pass) | RUNPATH `$ORIGIN` on every dynamic ELF; all llama/ggml libs resolve inside the install dir, also via the `~/.local/bin` symlink; no DT_RPATH, no execstack |
| F5 | none (pass) | No setuid/setgid, no file capabilities, nothing world-/group-writable; all owned vgpnk:vgpnk (uid 1000); archive's runner uid 1001 not preserved → non-root extraction |
| F6 | none (pass) / low (latent) | Symlink shadows nothing today; would silently shadow a future `/usr/bin/llama-server` from `extra/llama-cpp` |
| F7 | info | Tarball residue left in `~/.local/opt`; release is `prerelease: true`, `immutable: false` |

No defect blocks C2. One disclosure (F3) and one latent-shadow note (F6) belong in the receipt/PROVINCE note.

## F1 — Release asset provenance (pass)

- API: https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755 — asset `"name": "llama-b11755-bin-ubuntu-x64.tar.gz"`, `"size": 22240468`, `"digest": "sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226"`, uploader `github-actions[bot]`, `"target_commitish": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`.
- Local: `sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` → `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`; `stat` size `22240468`. A second copy observed at `/tmp/r16src/llama-b11755-ubuntu-x64.tar.gz` had the same hash; it was gone on a later call (cleaned up, I assume [INFERENCE]).
- Tree integrity: Python `tarfile` compared every member with disk. Result: `51 files; mismatches [] ; extra on disk [] ; missing []`. Symlink targets also match. So nothing was added, dropped, or edited after extraction.
- Archive safety: `tar -tzf` → `no absolute/.. members`; all members start with `llama-b11755/`.

## F2 — Model provenance (pass)

- HF API https://huggingface.co/api/models/ggml-org/models-moved/tree/main/tinyllamas: `"path": "tinyllamas/stories260K.gguf"`, `"size": 1185376`, `"lfs": {"oid": "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`.
- Local `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` → `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`, size 1185376, mode `-rw-r--r-- vgpnk vgpnk`, dirs 755 vgpnk:vgpnk.
- Watch for confusables: the same tree also holds `stories260K-be.gguf` at the **same size** 1185376 but with a different oid (`276d6f9d…fc1c`). A size-only check would accept the wrong file. The sha256 pin is what rules it out. Keep it in `kama-llamacpp-live.py`.

## F3 — Channel order vs RULES.md (low; disclosure needed)

- Rule: `/home/vgpnk/.omp/agent/RULES.md:7-8` — "Channel order: `sudo pacman -S --needed --noconfirm <pkg>` → `uv tool install <pkg>` → official release binary into `~/.local/bin`".
- The pacman tier is not empty. `pacman -Si llama-cpp` → `Repository : extra`, `Version : 0.6.0-1`, `URL : https://github.com/ggml-org/llama.cpp`, `Depends On : ggml glibc libgcc libstdc++ openssl`; `pacman -Ss` also lists `extra/ggml 0.26.0-1`. The argument "no pacman package exists" would therefore be **false**. Do not make it.
- Why skipping pacman was still compliant:
  1. The orchestrator ruling in this wave's contract pauses all pacman transactions host-wide ("install only via `uv tool`/`npx`/an official binary in ~/.local/bin"). That ruling overrides tier 1.
  2. C1/C2 cite source lines pinned to b11755 / 704366d76. The Arch package is versioned `0.6.0` and links the separate system `ggml 0.26.0`, while the bundle ships `libggml.so.0.27.0`. Nothing local ties it to commit 704366d76 [INFERENCE], so it could not serve as the pinned binary.
- uv tier: there is no official `uv tool` distribution of llama.cpp's `llama-server`. `llama-cpp-python` is a third-party binding with its own server [INFERENCE; not checked online], so it would not exercise `tools/server/server-http.cpp`.
- Tier 3 form: the tree went into `~/.local/opt/llama-b11755` with only a symlink in `~/.local/bin`, not a binary copied into `~/.local/bin`. This is the right call: the binary needs its sibling libraries through `$ORIGIN` (F4). It also matches the host's existing convention (`~/.local/opt` already holds `ghidra_12.1.4_PUBLIC`, `jadx-headless-mcp`).
- No pacman use by L1: `/var/log/pacman.log` has 3160 lines. The last transaction is `:3152` "[2026-10-20T09:39:21-0300] [PACMAN] Running 'pacman -Rns --noconfirm gst-plugin-gtk hyprwayland-scanner webp-pixbuf-loader'", about 38 min before the 10:17 install. No log line mentions llama or ggml. Those earlier removals are someone else's yay/pacman activity and outside this seat.
- Remediation (smallest): the install record must state tool=llama.cpp llama-server, version=b11755 (704366d76), channel=official GitHub release binary (tier 3), reason=C2. It must also say tier 1 (`extra/llama-cpp 0.6.0-1`) exists but was skipped because of (a) the host-wide pacman pause and (b) the commit pin, and that tier 2 has no official equivalent. Same entry for the model: channel = official HF repo `ggml-org/models-moved`, sha256-pinned.

## F4 — RPATH / library resolution (pass)

- `readelf -d ~/.local/opt/llama-b11755/llama-server`: "(RUNPATH) Library runpath: [$ORIGIN]", plus `BIND_NOW` and "Flags: NOW PIE". NEEDED: `libllama-server-impl.so`, `libstdc++.so.6`, `libgcc_s.so.1`, `libc.so.6`.
- Across all 50 ELFs: 49 have `[$ORIGIN]`. No file has DT_RPATH (which, unlike RUNPATH, would take precedence over `LD_LIBRARY_PATH`). The one exception, `llama-connect`, is "static-pie linked" with no NEEDED entries, so it needs no runpath.
- Resolution through the PATH symlink (`ld.so --list ~/.local/bin/llama-server`): every non-system library resolves under `/home/vgpnk/.local/opt/llama-b11755/`, e.g. "libllama-server-impl.so => /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so". So `$ORIGIN` follows the real path, not `~/.local/bin`. Missing libraries: none. System libraries come from `/usr/lib` (libssl.so.3, libcrypto.so.3, libgomp.so.1, libz, brotli, zstd).
- Hijack surface: `LD_LIBRARY_PATH` and `LD_PRELOAD` are unset in this session (checked by presence only, values not dumped). `/etc/ld.so.preload` does not exist. `ldconfig -p` has "no system libllama/libggml in ld.so.cache". So no system `ggml 0.26.0` can be mixed with the bundled 0.27.0 today.
- Residual risk: anyone who can write to `~/.local/opt/llama-b11755` can plant libraries that `$ORIGIN` will load. That is the same trust boundary as `~/.local/bin` itself (both uid 1000, 755), so it adds no new exposure [INFERENCE].
- `readelf -lW llama-server`: `GNU_STACK … RW` (stack not executable), `GNU_RELRO` present. No file in the tree has an RWE stack.
- The CPU backend `libggml-cpu-*.so` variants are not NEEDED entries; ggml dlopens them at runtime from the executable's directory [INFERENCE; ScoutHostRuntimeFacts owns that question].

## F5 — Privilege bits & ownership (pass)

- `find … \( -perm -4000 -o -perm -2000 \)`: no matching regular file. The `-perm -o+w` hits were only the 10 internal soname symlinks (symlinks always show 0777 and ignore it). All 10 point to relative in-tree targets, e.g. `libllama.so.0 -> libllama.so.0.7.0`.
- `getcap -r ~/.local/opt/llama-b11755` → no output (no file capabilities).
- `find … ! -user vgpnk` → no output. `stat`: `vgpnk:vgpnk 755` for `~/.local/opt`, `~/.local/opt/llama-b11755`, `~/.local/bin`. Files are `-rwxr-xr-x` / `LICENSE -rw-r--r--`.
- The archive records owner `(1001, 1001, 'runner')`, but disk is owned by uid 1000. tar was therefore run without root (non-root tar cannot keep a foreign owner). No `sudo` was used on this chain.

## F6 — PATH shadowing (pass today; latent)

- `type -a llama-server` → only `/home/vgpnk/.local/bin/llama-server`. `/usr/bin`, `/usr/local/bin`, `/bin`, `/opt` have no `llama-server`. `pacman -Qo` says "No package owns /home/vgpnk/.local/bin/llama-server", and `pacman -Qs llama|ggml` finds nothing installed. The symlink shadows nothing.
- Dirs that come before `~/.local/bin` (PATH positions 1-3: an fnm multishell dir, `~/.local/share/fnm`, `~/.opencode/bin`) contain no `llama-server`. The symlink is not shadowed either.
- Latent: `~/.local/bin` is PATH position 4 and `/usr/bin` is position 13. If `extra/llama-cpp` is installed after the pause lifts, a bare `llama-server` would still run b11755. [INFERENCE: `pacman -Fl llama-cpp` returned nothing, so the files DB is unsynced and I could not confirm the package ships `/usr/bin/llama-server`.] C2 should call the absolute pinned path `~/.local/opt/llama-b11755/llama-server` (or check `--version` / sha before launch) instead of using the PATH name.
- Mtime check: in `~/.local/bin`, only `llama-server` (10:17:53) and `swarm` (09:10:43, not from this chain) changed today. No other llama binary was linked.

## F7 — Hygiene / info

- The release tarball is still at `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` (22 MB, 10:17:48). It does no harm and makes re-verification easy. Whether to remove it is L1's choice; if kept, record it as a lane-owned artifact.
- The API reports `"prerelease": true` and `"immutable": false`. Tags and assets on a mutable release can be replaced later. The asset sha256 above is the durable identity; a SOURCES row should cite the digest, not just the tag URL [INFERENCE].
- Release `"published_at": "2026-10-20T11:18:44Z"`. The asset was uploaded at `2026-10-20T11:21:10Z`, about 4 h before this audit.

## Limitations

- No signature or attestation check: llama.cpp releases ship no detached signatures, and I did not check GitHub artifact attestations.
- `ldd`/`ld.so --list` runs the dynamic loader on the binary. That is acceptable for an official binary but is not pure static analysis.
- I did not run `--version` or any launch (that belongs to HostRuntimeFacts / L1).

## Installs

None by this seat.
