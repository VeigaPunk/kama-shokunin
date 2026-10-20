VERDICT: n/a — read-only host facts for the install disclosure (routed defect 5); no claim graded, nothing modified.

# Install footprint — llama.cpp b11755 (read-only scout)

All commands were read-only (`ls`, `stat`, `du`, `sha256sum`, `readlink`, `command -v`,
`readelf`, `objdump`, `ldd`, `tar -t`, `pacman -Qo/-Qs` queries, `gh api GET`). Nothing was
installed, moved, deleted or started; no port was bound. No installs to record.

## 1. Where `llama-server` resolves — one path only

```
$ command -v -a llama-server
/home/vgpnk/.local/bin/llama-server
$ type -a llama-server
llama-server is /home/vgpnk/.local/bin/llama-server
```

- `ls -l /usr/bin/llama-server` → `ls: cannot access '/usr/bin/llama-server': No such file or
  directory`. Same for `/usr/local/bin/llama-server`.
- `pacman -Qo /home/vgpnk/.local/bin/llama-server` → `error: No package owns
  /home/vgpnk/.local/bin/llama-server`; `pacman -Qs llama` prints nothing.
- Link: `lrwxrwxrwx 1 vgpnk vgpnk 48 Oct 20 10:17 /home/vgpnk/.local/bin/llama-server ->
  /home/vgpnk/.local/opt/llama-b11755/llama-server`; `readlink -f` →
  `/home/vgpnk/.local/opt/llama-b11755/llama-server`.

Consequence for the disclosure: the PATH entry shadows nothing (matches
`corpus/lessons/round-16-verifier-spotcheck.md:122` "no `/usr/bin/llama-server` exists"), and
only `llama-server` is linked — the release's other binaries (`llama-cli`, `llama-bench`,
`llama-tts`, …) are not on PATH.

## 2. `~/.local/opt/` contents and sizes

| entry | size (`du -sh`) | notes |
|---|---|---|
| `ghidra_12.1.4_PUBLIC/` | 876M | unrelated |
| `go-1.24.6/`, `go-1.25.0/`, `go-1.27.3/` | 280M, 236M, 276M | unrelated |
| `llama-b11755/` | **54M** (`du -sb` = 56,288,736 B) | extracted tree, 61 entries |
| `jadx-headless-mcp/` | 41M | unrelated |
| `llama-b11755-bin-ubuntu-x64.tar.gz` | **22M** (22,240,468 B) | retained release archive |

llama.cpp share of the host: 56,288,736 + 22,240,468 = **78,529,204 B ≈ 74.9 MiB**, of which
the tarball is extractable copy (redundant now that the tree is verified). Not deleted; removal
is the operator's call (round-16 L0 question (b)).

## 3. Tarball digest — matches upstream exactly

```
$ sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226  …tar.gz
```

Independent upstream check this round (`gh api repos/ggml-org/llama.cpp/releases/tags/b11755`,
read-only GET; the unauthenticated REST call and the HTML page both still 403):
`llama-b11755-bin-ubuntu-x64.tar.gz 22240468
sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226 uploaded`,
`.prerelease` `true`, `.published_at` `2026-10-20T11:18:44Z`, tag `b11755`.

Release page https://github.com/ggml-org/llama.cpp/releases/tag/b11755 links
"Ubuntu x64 (CPU)" to `…/releases/download/b11755/llama-b11755-bin-ubuntu-x64.tar.gz` and states
"Pre-release"; commit `704366d` per the same page. This agrees with `corpus/SOURCES.md:50`
(S038: "asset `lla…" size 22240468, digest `sha256:753bfa73…`).

Archive shape: 62 `tar -t` members (1 directory + 61 files), names after stripping
`llama-b11755/` are **set-identical to the installed directory** (61 entries; diff empty), so
nothing extra was added to the install tree.

## 4. Why the doc says "51 files" while the archive has 61 entries — reconciled, no drift

- Installed dir: 61 entries = **51 regular files + 10 symlinks** (`libggml*.so*`,
  `libllama*.so*`, `libmtmd.so*` version links).
- `tools/kama-llamacpp-live.py:146-149` — "for every regular file in dirname(server_real) …
  Symlinks are skipped as members (they are not regular files)." So the receipt's
  `install_tree` holds exactly the 51 regular files; `corpus/knowledge/llamacpp-loading-lifecycle.md:107`
  "install tree of 51 files hashed" is accurate under that rule.
- Re-derived today: per-file map and combined digest recompute to
  `install_tree_sha256` `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`,
  byte-equal to `.ufo/waves/round-16/live/receipt.json` → installed tree unchanged since the
  round-16 run. `sha256sum` of the launcher is
  `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, matching the receipt and
  the "server `b6a31a8e…0cd804`" line at `corpus/lessons/round-16-verifier-spotcheck.md:103`.
  [INFERENCE] "51 files" is true but invites a 61-vs-51 miscount in review; "51 regular files +
  10 symlinks" is the safe wording.

## 5. Build identity and runtime linkage

```
$ ~/.local/bin/llama-server --version
version: 0.7.0-dev (build 11755, commit 704366d76)
built with GNU 11.4.0 for Linux x86_64
```

`file` → "ELF 64-bit LSB pie executable, x86-64 … dynamically linked". `readelf -d` →
`RUNPATH … [$ORIGIN]` and `NEEDED libllama-server-impl.so`, `libstdc++.so.6`, `libgcc_s.so.1`,
`libc.so.6`; `ldd` resolves every llama/ggml object inside the install dir. Highest required
symbol version `GLIBC_2.34` vs host `ldd (GNU libc) 2.44`. [INFERENCE] the Ubuntu build is
self-contained apart from system libc/libstdc++/libgcc, so it runs unmodified on this Arch host;
the observed `--version` output is the direct evidence.

## 6. Retention chronology (stat, no writes)

- tarball `mtime=ctime=2026-10-20 10:17:48 -0300`
- install dir `ctime=2026-10-20 10:17:53 -0300`; member mtimes `08:10` (archive metadata preserved)
- `~/.local/bin/llama-server` symlink `mtime=10:17:53.109`

[INFERENCE] ordering: archive written 10:17:48 → extracted 10:17:53 → link created. No download
marker, `.part` file, checksum sidecar or install log exists beside the tarball, so the fetch
channel is inferable only from the asset name/digest equality, not from a local record.

## 7. Disclosure deficiencies this closes (defect 5)

`corpus/lessons/round-16-verifier-spotcheck.md:123` — "The retained release tarball in
`~/.local/opt/` is not named in the report or the L0 question." Facts to name verbatim in the
round-17 disclosure: path `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`, 22,240,468 B,
sha256 `753bfa73…a6e226`, upstream asset of the same digest on Pre-release tag b11755 (mutable →
cite the digest, not the tag); tree `~/.local/opt/llama-b11755/` 56,288,736 B; PATH link
`~/.local/bin/llama-server`; channel = official release binary (directive third channel), not
pacman, not a piped script; reason = C2 needs a real b11755 runtime and the host had none.

## Limitations

- `gh api` is an authenticated read; unauthenticated `api.github.com` and the release HTML
  assets block returned 403/"Sorry, something went wrong", so the upstream digest rests on the
  authenticated GET plus S038's earlier record — both agree, and both agree with the local hash.
- No check of who downloaded the archive or with which URL/command (no local record exists).
- No attempt to verify the extracted files against the tar (would require writing); instead the
  receipt's tree digest was recomputed in place and matched.
- [INFERENCE] judgments are marked; everything else is literal tool output above.

## Installs

None. `sha256sum`/`du`/`readelf`/`gh` were already present; no package transaction run
(pacman usage was query-only: `-Qo`, `-Qs`).
