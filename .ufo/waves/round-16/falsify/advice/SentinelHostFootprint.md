VERDICT: confirm — round-16 host footprint (no live llama-server, no 8080/34113 listener, no llama-named config/unit, install + cache trees owner-only-writable and digest-identical to the receipt). Two low-severity notes follow: the assigned `-newer` anchor cannot see the round, and stale build-wave scratch is still in /tmp.

Axes: process residue, socket residue, config/unit residue, install-tree integrity/permissions, PATH exposure, scratch hygiene.

## Evidence (read-only; every command run as vgpnk, 2026-10-20 ~10:54 -0300)

| # | Command | Exit | Output excerpt |
|---|---|---|---|
| 1 | `pgrep -x llama-server` | 1 | (empty) |
| 2 | `pgrep -af 'llama\|kama-llamacpp'` | 1 | (empty). Nothing is running under any llama-like name, including the tool's wrapper. |
| 3 | `ss -Hltnp 'sport = :8080 or sport = :34113'` | 0 | (empty). The host had 17 TCP listeners in total (`ss -Hltn \| wc -l`). |
| 4 | Scan of `/proc/net/tcp{,6}` for LISTEN (`0A`) on 8080/34113 | 0 | (empty), which agrees with #3 |
| 5 | `find ~/.config ~/.omp/agent ~/.config/systemd -maxdepth 3 -newer …/frozen/manifest.json -name '*llama*'` (as assigned, names only) | 0 | (empty) |
| 6 | The same `find` without `-newer` | 0 | (empty) |
| 7 | `find ~/.config/systemd ~/.local/share/systemd /etc/systemd -maxdepth 4 -iname '*llama*'` | 0 | (empty) |
| 8 | `systemctl --user list-units --all --no-legend '*llama*'` | 0 | (empty) |
| 9 | `readlink -f ~/.local/bin/llama-server` | 0 | `/home/vgpnk/.local/opt/llama-b11755/llama-server`. Link is `lrwxrwxrwx vgpnk vgpnk`, created Oct 20 10:17. |
| 10 | `which -a llama-server`; `pacman -Qq \| grep -i llama` | 0; 1 | Only `~/.local/bin/llama-server`. No pacman package and no other llama-server binary on PATH is shadowed. |
| 11 | `find ~/.local/opt/llama-b11755` for non-vgpnk owner/group, o+w, g+w, setuid/setgid | 0 | 0 / 0 / none / 0 / none. Modes: 50×755 files + dir 755, 1×644. There are 10 symlinks and all are intra-tree `lib*.so` → `lib*.so.N[.x.y]`; `find -L -type l` reports none broken. |
| 12 | `readelf -d …/llama-server`; `ldd` | 0 | `RUNPATH [$ORIGIN]`. All `libllama*`, `libggml*`, `libmtmd*` resolve inside `~/.local/opt/llama-b11755`, with no "not found". |
| 13 | `sha256sum llama-server libllama-server-impl.so` | 0 | `b6a31a8e97615a2a…cd804` and `e404b91a81c9ab65…b59ed`. Both match `corpus/knowledge/llamacpp-loading-lifecycle.md:92-93`. |
| 14 | Recomputed the `install_tree` digest with the tool's own algorithm (`tools/kama-llamacpp-live.py:146-170`) | 0 | `51 6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c`. This equals `receipt.json` `server.install_tree_sha256`, the impl sha and the member count 51, so the tree has not been mutated since the receipt. |
| 15 | `sha256sum ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` | 0 | `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, size 22240468. Equals S038 (`corpus/SOURCES.md:50`) and `LOG.md:941`. |
| 16 | `find ~/.cache/kama-shokunin -printf '%m %u:%g …'`; `sha256sum models/stories260K.gguf` | 0 | `755 vgpnk:vgpnk .`, `755 ./models`, `644 … 1185376 ./models/stories260K.gguf`. The digest `270cba1b…d256d` equals S039 and the receipt. |
| 17 | `find /tmp -maxdepth 1 -name 'kama-llamacpp-live-*'`; `find <lane> -name '.kama-live-*'` | 0; 0 | Both empty. The tool's mkstemp log (`:800`) and atomic-publish temp (`:671`) left no residue. |
| 18 | `cat /tmp/kama-ls.pid` → `ps -p 18574` | 1 | pid 18574 is dead. The stale pidfile is harmless. |

## Findings

1. **Info — the assigned `-newer` anchor is blind to round 16.** `stat` shows `frozen/manifest.json` and every `live/*` receipt with mtime `2026-10-20 10:50:49.1456… -0300`. The install link and model are from 10:17. The live run (receipt port 32845, S041 at 13:49:38Z = 10:49:38 local) also finished before the anchor. So command #5 could not have caught a config written during install or run. [INFERENCE] The 10:50:49 mtimes come from a checkout or commit rewrite, not from content creation. Remediation for future rounds: anchor on a pre-round timestamp (`-newermt '<round start>'`) or drop `-newer`. Command #6 already does this here and is also empty, so the conclusion stands.

2. **Low — persistent PATH exposure is disclosed and sanctioned, but it outlives the round.** `~/.local/bin/llama-server` stays on PATH after teardown. It is disclosed at `LOG.md:942-943` ("linked `~/.local/bin/llama-server`; reason C2"). It is consistent with PROVINCE.md:45 (the hard write boundary is `~/.config`, `~/.omp`, systemd units; `~/.local/bin` is not listed) and with the operator tooling directive. Exploit path: none is found in this audit. The binary is owner-only-writable (#11), RUNPATH is `$ORIGIN` with no foreign library resolution (#12), and no unit or config references it (#5-#8). Note that LOG.md:91 frames kama as charter-bound not to rewrite `~/.local/bin`. Read literally, that line is about the operator-owned *pins*, not new installs. Smallest remediation: none required. Optionally record the link removal command (`rm ~/.local/bin/llama-server`) in the capability row's teardown or uninstall note.

3. **Low — build-wave scratch hygiene.** `/tmp` still holds stale round-16 scratch that does not use the per-seat `/tmp/kama-r16-<Name>/` convention. Examples:
   - `/tmp/kama-ls.{log,pid}` and `/tmp/kama-smoke.sh` (10:18)
   - `/tmp/kama_stub503.{py,port}` and `/tmp/kama_curl.err` (10:29)
   - `/tmp/kama-fam-*.txt` (9 files, 10:40-10:41)
   - `/tmp/kama-live-dev1.json` (10:38) and `/tmp/kama-d2.json` (10:53)
   - upstream source copies: `/tmp/llama-srv-704366d76/`, `/tmp/lcpp-sleep/llama.cpp-704366d76`, `/tmp/kama-*server*.cpp`

   All are mode 644/755 and owned by vgpnk. No secrets were inspected (names only). Impact: clutter, plus a stale pidfile that a future `kill $(cat /tmp/kama-ls.pid)` could aim at a recycled pid. Smallest remediation: L1 removes them at closeout. This seat did not delete files it does not own.

4. **Info — the 22 MB release tarball remains in `~/.local/opt/`.** The file is `llama-b11755-bin-ubuntu-x64.tar.gz` and its digest matches S038 (#15). It is benign and useful as provenance. Keeping or removing it is an L1 call.

## Limitations

- `ss -p` ran without root, so the owners of other users' sockets are not visible. This does not matter here because nothing was listening on 8080/34113 (#3, #4).
- UDP was not checked.
- This is a point-in-time sample at about 10:54 -0300. Sibling seats such as RerunLiveNegatives may start and stop servers later.
- No config bodies, session stores or environment variables were read.

## Installs

None.

Scratch `/tmp/kama-r16-SentinelHostFootprint/` was created empty and has been removed.
