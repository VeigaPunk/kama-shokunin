VERDICT: S496/S497/S498 ground exactly the surfaces their claims name (model_mapping, teardown mechanism, fence rule); the counter's biggest ungrounded kernel surfaces are /proc/<pid>/stat (tree descent, liveness, starttime reuse guard — in all three legs) and the stat()-side file-identity join plus open(2) O_NOFOLLOW — propose proc_pid_stat(5) and inode(7) next round; note the seat spec's guess proc_net_tcp(5) does NOT exist on man7.org (404).

# N5Sources2 — source-row cross-map for round-50 instruments

Axes (godspeed): operability (C1) is the axis served; the move — two source rows closing the largest ungrounded kernel surfaces — improves sourced-claim depth and harms no axis (calibration's C2 needs no new row; see §3).

Method: read both frozen counters' docstrings (the contract) and bodies, the lane tools they exercise, and every SOURCES.md registry row; fetched the candidate man7 pages live to confirm existence and coverage. Lane read-only; no counter or tool run (doc-level task); no installs.

## 1. What the new rows ground

| row | URL (as in corpus/SOURCES.md) | grounds |
|---|---|---|
| S496 proc_pid_maps(5) | man7.org/linux/man-pages/man5/proc_pid_maps.5.html | C1 `mapped`: `/proc/<pid>/maps` dev/major:minor, inode, pathname of a file-backed mapping; inode 0 = no file (counter lines 309-340; tool kama-llamacpp-live.py:678-727 `model_mapping`); C1 `newrow` requires this URL in a new SOURCES row (counter:529-539) |
| S497 PR_SET_PDEATHSIG(2const) | man7.org/linux/man-pages/man2/PR_SET_PDEATHSIG.2const.html | C1 `teardown` mechanism: replay `set_own_pdeathsig` (kama-live-replay.py:100-109, called :587), live-tool child `_child_pdeathsig` preexec (:314-318), live tool `_preexec_pdeathsig` for server (kama-llamacpp-live.py:661-671) |
| S498 CommonMark 0.31.2 §4.5 | spec.commonmark.org/0.31.2/#fenced-code-blocks | C2 `fence` scenario + lane leg's fence-aware `sections()`/`fence_open`/`fence_close` (counter:304-340): ≤3-space indent, ≥3 backticks/tildes, same-char longer/equal closing fence, unclosed runs to EOF |

## 2. C1 check-by-check grounding map (tools/round50-replay-bind-audit.py)

| check | mechanism | row(s) |
|---|---|---|
| exe | sha256(`/proc/<pid>/exe`) == frozen server digest | S495 proc_pid_exe(5); digest pinned via S488 (b11909 asset) |
| listen | `/proc/net/tcp{,6}` rows, `st=="0A"`, loopback addr, inode ∩ `socket:[i]` links of `/proc/<pid>/fd` (counter:198-231) | PARTIAL: S049 kernel proc_net_tcp.rst (tcp6_seq_show named; scope **excludes state codes**); S048 tcp_ipv6.c (tcp6 address printing only). No row grounds the `0A` LISTEN code, the inode column, or the `socket:[` fd-link name |
| nonce | POST /tokenize `with_pieces` + /detokenize round-trip vs counter's own GGUF vocab decode (counter:149-194, 360-372) | S494 (server README b11909 endpoint shapes); S492/S493 (pinned model URL identity); S058 gguf.md format (vocab decode — partial, tokenizer-key scope) |
| tree | ppid chain via `/proc/<pid>/stat` fields (3) state, (4) ppid, (22) starttime (counter:234-306) | **NO ROW** |
| env | `/proc/<pid>/environ` NUL-separated keys (counter:271-276); `-I` ignores PYTHONPATH; sitecustomize import = canary (counter:376-393) | **NO ROW** for environ format or python `-I` |
| mapped | maps row → `os.stat(pathname)` dev/inode equal → sha256 == model (counter:309-340) | S496 grounds the maps side; **the stat(2) dev+inode identity join has NO ROW**; tool's O_NOFOLLOW reopen (kama-llamacpp-live.py:704) has NO ROW |
| post-release | `p.wait()` exit 0; `pid_alive` false; `port_refuses` (counter:251-260, 458-478) | S044/S064 (returncode semantics); connect(2) ECONNREFUSED ungrounded (minor) |
| teardown | snapshot descendants via /proc scan; SIGKILL invoker; all gone|zombie|reused in 30 s; port refuses (counter:279-294, 497-526) | S497 grounds pdeathsig firing; **state/ppid/starttime fields NO ROW** (same proc_pid_stat gap); SIGKILL/PPID-1 reparenting semantics ungrounded (minor: S497 covers reparenting) |
| newrow | diff of `git show <rev>:corpus/SOURCES.md` rows vs BASE, MAPS_URL match (counter:529-539) | S032 git-show; self-verifying |

## 3. C2 check-by-check grounding map (tools/round50-append-audit-v5-check.py)

| check | mechanism | row(s) |
|---|---|---|
| fence | CommonMark fence open/close grammar | S498 |
| key(l) | drop one trailing `\r` per line (counter:343-344) | definitional (v5 contract), no external row — consistent with `sourced` wording scoping to the fence rule |
| birth/origin | `git rev-list --parents` parent lists; `cat-file --batch-check`/`blob` bodies (counter:417-435) | blob reads S032/S033/S071/S083 grounded; **`--parents` column grammar NO ROW** |
| deleted == numstat | `git diff --numstat` deletion count per event (counter:472-475) | S491 |
| deleted_with_pos | parse unified hunk headers `@@ -a,b +c,d @@` at -U0 (counter:365-385) | PARTIAL: S491 anchors diff-format §other diff formats but its scope excludes the grammar |
| v4 binder | token/negation regexes on contract rows (counter:122-145, 401-416) | own-work definitional (routed V2Ctr limit — accepted) |

## 4. Proposed rows (2) for next round — proposed text in out/N5Sources2/proposed-rows.md

**P1 — Linux proc_pid_stat(5)** — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
Why: the single largest ungrounded kernel surface. It documents fields (3) `state`, (4) `ppid`, (22) `starttime` — the exact triple `stat_fields` reads (counter:234-239) — plus the PTRACE_MODE_READ_VISIBILITY caveat on field validity. Grounds `tree` (ppid chain), `env`'s parent lookup, `descendants`, `teardown`'s liveness/`Z` test and pid-reuse-by-starttime guard — touches all three legs. Verified: page 200, fields confirmed quoted above. Anchor: §DESCRIPTION field list (3),(4),(22), man-pages 6.19.

**P2 — Linux inode(7)** — https://man7.org/linux/man-pages/man7/inode.7.html
Why: grounds the C1 `mapped` join's load-bearing claim that (dev, inode) identifies a file — the counter's `os.stat(path)` dev/inode equality test (:333) and the tool's `fstat` of the O_NOFOLLOW fd (kama-llamacpp-live.py:709-713). Page: "Each file in a filesystem has a unique inode number… unique only within a filesystem" — i.e. dev+inode together identify. Without it, S496 says what maps prints but not that the join proves same-file. Verified: page 200. Anchor: §DESCRIPTION `st_dev`/`st_ino` paragraphs.

## 5. Notable runner-up gaps (not proposed — at most two rows)

- `listen` is the largest *remaining* ungrounded check: **the guessed page proc_net_tcp(5) does not exist on man7.org (404; verified 2026-10-26)** — tcp/tcp6 material lives in proc_pid_net(5) (served at man5/proc_net.5.html), which names tcp's `st` column but not the 0A code, the tcp inode column, tcp6, or `/proc/<pid>/fd` socket links; full grounding would want kernel `tcp4_seq_show` (net/ipv4/tcp_ipv4.c, precedent S048) + proc_pid_fd(5). Two rows' worth — flag to L1 if a third is admissible.
- open(2) `O_NOFOLLOW` — grounds the tool-side symlink guard (kama-llamacpp-live.py:704); weaker than P2 because the counter check it serves is already S496-anchored.
- `/proc/<pid>/environ` (proc_pid_environ(5), exists, 200) + Python `-I`/`sitecustomize` docs — grounds `env` canary semantics.
- `git rev-list --parents` output grammar; `connect(2)` ECONNREFUSED; SIGKILL uncatchability (signal(7)) — minor.

## 6. Observations, not defects

- Counter `mapped` stat()-then-open() is TOCTOU-exposed but fails closed (a swap changes dev/inode → problem appended) — noted, not reported; the tool's O_NOFOLLOW+fstat is the strict version.
- `stat_fields` parses via `rsplit(')',1)` — correct only because comm is the last field containing `)`; proc_pid_stat(5)'s documented field order would ground this.

## Evidence commands

- `grep -nE 'S49[0-9]|S50[0-9]' corpus/SOURCES.md` → S496 line 249, S497 line 250, S498 line 251 (anchors `.ufo/waves/round-50/c{1,2}/*.txt`, all present on disk).
- `curl -sI https://man7.org/linux/man-pages/man5/proc_net_tcp.5.html` → **404**; man5/proc_net.5 → 200 (proc_pid_net(5), no tcp6); man5/proc_pid_stat.5 → 200; man5/proc_pid_fd.5 → 200; man5/proc_pid_environ.5 → 200; man7/inode.7 → 200; man2/open.2 → 200.
- Counter cites: round50-replay-bind-audit.py:198-340 (proc observation), :343-373 (observe), :497-539 (teardown/newrow); round50-append-audit-v5-check.py:304-385 (fence/key/diff parse), :388-496 (lane leg).

Files written:
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/N5Sources2.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/N5Sources2/proposed-rows.md
