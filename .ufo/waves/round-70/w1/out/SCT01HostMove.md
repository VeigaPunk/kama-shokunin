# SCT01HostMove — host claims the Linux move contradicts (round 70, kama)

Seat: advisory leaf, reconnaissance only. No tracked file was edited, created or deleted; no claim
verdict proposed. All line numbers are at the lane tip **0e14facd0c619f45a6461821d2bd80ddac9855b1**
(round-70 freeze commit; parent 6035e952). Cited files were confirmed byte-identical to HEAD with
`git hash-object` vs `git rev-parse HEAD:<path>` (SKILL.md, both census/audit tools) and line numbers
re-derived from `git show HEAD:PROVINCE.md` / `HEAD:SKILL.md`.

Observed host (every claim below is graded against this):

```
$ uname -a
Linux plazir27 7.2.11-arch1-1 #1 SMP PREEMPT_DYNAMIC Fri, 16 Oct 2026 00:28:58 +0000 x86_64 GNU/Linux
$ python3 -V            → Python 3.14.8          $ python3 -c "import sys" → rc 0 (/usr/bin/python3)
$ git --version         → git version 2.56.0      $ command -v ss flock jj → /usr/bin/ss /usr/bin/flock /home/vgpnk/.local/bin/jj
```

## Claims vs. current truth

| # | Location @ tip | Claim (abridged) | Re-derivation command | Observed | Verdict |
|---|---|---|---|---|---|
| 1 | `PROVINCE.md:193-194` | host is Windows 10.0.26200, Git Bash/MinGW64, git 2.55.0.windows.3, CPython 3.13.15; `python3` is the Microsoft Store alias stub, exit 49 | `uname -a; python3 -V; git --version; python3 -c "import sys"; echo $?` | Linux 7.2.11-arch1-1; Python 3.14.8; git 2.56.0; rc 0 | **FALSE** |
| 2 | `PROVINCE.md:199-201` | `~/.local/bin/omp` absent; no `LLAMA_CPP_BASE_URL` in env; `~/.omp/` holds only `agent/settings.json` (`shellPath`) | `ls -l ~/.local/bin/omp; echo ${LLAMA_CPP_BASE_URL-unset}; ls ~/.omp; find ~/.omp -name settings.json` | omp present (276,785,328-byte ELF, 2026-11-01); env var still unset; `~/.omp` holds APPEND_SYSTEM.md, agent/, browser-relay/, cache/, logs/, autoqa.db, install-id — **no settings.json** | binary/env/**dir-shape FALSE**, env-var TRUE |
| 3 | `PROVINCE.md:202-205` | `~/.local/opt/llama-b11755` and `~/.local/bin/llama-server` absent | `ls -l ~/.local/bin/llama-server; ~/.local/bin/llama-server --version` | symlink → `llama-b11755/llama-server`; `version: 0.7.0-dev (build 11755, commit 704366d76)` built for Linux x86_64 | **FALSE** |
| 4 | `PROVINCE.md:206-207` | `~/.cache/kama-shokunin/` absent | `ls -l ~/.cache/kama-shokunin/models/stories260K.gguf; sha256sum …` | present, 1,185,376 B, sha256 `270cba1b…bd256d` = pinned digest | **FALSE** |
| 5 | `PROVINCE.md:208-209` | `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` absent | `[ -e … ]` | present | **FALSE** |
| 6 | `PROVINCE.md:210-212` | `qwen-coder.service` absent; "no systemd on this host" | `ls ~/.config/systemd/user/qwen-coder.service; command -v systemctl; systemctl --user is-system-running` | unit file absent (TRUE); `/usr/bin/systemctl` present, user manager `degraded`, `~/.config/systemd/user/` exists | unit **TRUE**, "no systemd" **FALSE** |
| 7 | `PROVINCE.md:213-216` | `~/.config/opencode/opencode.json` absent; `opencode.jsonc` holds only `$schema` | `cat ~/.config/opencode/opencode.json; ls ~/.config/opencode` | `opencode.json` present, 4 lines `{$schema, autoupdate:false}`; no `opencode.jsonc`; dir also holds service.json, cli.json, tui.json, a `.tui-migration.bak` | **FALSE** |
| 8 | `PROVINCE.md:217-218` | `~/.config/opencode/agents/` absent | `[ -d ~/.config/opencode/agents ]` | absent | **TRUE** |
| 9 | `PROVINCE.md:219-222` | `UFO_SRC` unset and no ufo-fsd checkout located → the two `$UFO_SRC` rows cannot be evaluated | `echo ${UFO_SRC-unset}; ls -d ~/Projects/ufo-fsd-alpha` | unset (TRUE); `~/Projects/ufo-fsd-alpha` **exists** (the registry's own first fallback) and both pinned files resolve: the-tick.machine.json:16 `127.0.0.1:34113/v1/chat/completions`, local-helper.mjs:8 `DEFAULT_URL 127.0.0.1:34113` | env TRUE, "cannot be evaluated" **FALSE** |
| 10 | `PROVINCE.md:233-236` | `~/.local/opt/ollama-v0.40.11` absent | `~/.local/opt/ollama-v0.40.11/bin/ollama --version` | present; `client version is 0.40.11` | **FALSE** |
| 11 | `PROVINCE.md:237-240` | `~/.cache/kama-shokunin/models/stories260K.gguf` absent | as #4 | present, pinned digest | **FALSE** |
| 12 | `PROVINCE.md:241-248` | `python3` is the Store app-execution alias stub, not a usable interpreter; `python3 -c "import sys"` exits 49 | `python3 -c "import sys"; echo $?; command -v python3` | `/usr/bin/python3`, rc 0 | **FALSE** |
| 13 | `PROVINCE.md:250-260` | no listener on 8080/34113/11434; probes refused (curl 7); `ollama`/`llama-server` absent from PATH; "the probe gate itself refuses fail-closed (`ss` absent, `flock` absent)" | `ss -ltn; curl --noproxy '*' …; bash tools/kama-probe.sh listeners` | **no listener** on 8080/34113/11434 and all five probes `http=000 curl_exit=7` (**TRUE**); `ollama` →/usr/bin/ollama, `llama-server` →~/.local/bin (**FALSE**); `ss`/`flock` present and `listeners` runs, exit 0, 34 rows (**FALSE**) | ports **TRUE**, binaries/gate **FALSE** |
| 14 | `PROVINCE.md:266-270` | a tracked path (`.ufo/waves/round-52/w1/out/` with `\|`) "cannot be checked out under NTFS", so clone-based instruments refuse fail-closed | `git ls-tree -r --name-only HEAD \| grep -c '\|'`; `ls .ufo/waves/round-52/w1/out/`; `python3 tools/round42-selfdesc-reconcile.py --selftest --work <scratch>` | one such tracked path exists and **is checked out byte-exact**; the reconciler selftest cloned and ran: `SELFDESC_SELFTEST … pass=4 fail=1`, exit 1 — it did not refuse | premise **FALSE**; the pinned refusal is unreachable |
| 15 | `SKILL.md:574` | `~/.local/bin/llama-server` precedes `/usr/bin` on this host's PATH for every user | `echo $PATH \| tr : '\n'`; `type -a llama-server` | `~/.local/bin` is on PATH ahead of `/usr/bin`; only `~/.local/bin/llama-server` resolves (`/usr/bin/llama-server` does not exist) | **TRUE** |
| 16 | `SKILL.md:1681-1684` | "the new Windows host"; "on this host `python3` is the Microsoft Store alias stub" | as #1/#12 | Linux; `/usr/bin/python3` 3.14.8 | **FALSE** |
| 17 | `SKILL.md:1690` | census "pinned refusal markers name the missing Linux dependencies (`ss`, `flock`) and the NTFS-invalid tracked path" | `grep -nE '\bss\b\|flock' tools/round65-host-census.py` | **0 hits**; the only refusal pairs in `MEMBERS` are `"missing dependency"`, `"invalid path"`, `"cannot resolve master"` | **FALSE** (ss/flock); NTFS marker exists at `tools/round65-host-census.py:62` but is unreachable |
| 18 | `SKILL.md:1701` | `git status` / `git diff` "both are unreliable on this host" | `git status --porcelain -uno; git diff --stat` | both ran normally (status showed the concurrent sibling edits below) | **FALSE** on this host (informational parenthetical) |
| 19 | `PROVINCE.md:11` (Owns table) | `~/.config/opencode/opencode.json` "is now 5 lines holding `$schema`/`theme`/`autoupdate` only" | `wc -l …; cat …` | 4 lines, `$schema` + `autoupdate`, no `theme` | **FALSE** |

## Instrument-level consequence (measured, not proposed)

- `python3 tools/round65-province-host-audit.py` → `PROVINCE_HOST_AUDIT surfaces=13 present=10 absent=3 stale=0`, **exit 0**. The audit is green while **10 of its 13** `absent-on-this-host` notes are false: it grades markers for surfaces that are *absent*, and a now-present surface needs no marker, so a stale absence note is invisible to it. Only `qwen-coder-unit`, `janitor-md`, `ufo-src` are still absent (and all three carry markers).
- `python3 tools/round65-host-census.py` (base receipt `.ufo/waves/round-70/measured/before/census-at-base.out`, committed in the freeze commit) → `HOST_CENSUS pass=21 fail=1 refused=0 total=22 tierA_fail=1`, exit 1. `refused=0` independently confirms no pinned refusal fires on this Linux host; the one tier-A failure is the reconciler arm, which now fails rather than refusing (my direct run: `pass=4 fail=1`, exit 1, ~23 s).
- The NTFS refusal marker `"invalid path"` cannot match: `grep -c "invalid path" tools/round42-selfdesc-reconcile.py` → `0`.

## Undecidable read-only

- Whether the Windows host still exists / whether the former-host footprints there were removed (operator-owned; no remote access attempted).
- Whether `~/.local/bin/omp`'s `LLAMA_CPP_BASE_URL` fallback is the *effective* endpoint (env unset; registry records `file_match=inherited`; the binary does contain the literals `LLAMA_CPP_BASE_URL` and `127.0.0.1:8080`).
- Why `~/.local/opt/ollama-v0.40.11` and `/usr/bin/ollama` (0.40.7) both exist; which one is intended is not stated in the lane (no daemon listening on 11434).

## Notes / caveats

- A **live serving runtime** was observed on an unregistered port: `1234 | loopback | llama-server(pid=1505) | MODEL_OK | LFM3-1.7B,…`. It does not touch the registered consumer ports, but it does contradict any reading of "no serving runtime on this host".
- During this seat's run another writer modified `PROVINCE.md` (1 line, line 17) and `SCORECARD.md` (12 lines) in the worktree; I did not write them. All findings above are graded against HEAD bytes, whose cited line numbers I re-derived from `git show HEAD:`.
- No tools installed or upgraded (none needed). Scratch `/fast/scratch/hyaku/kama-r70/SCT01HostMove/` deleted before yielding.
