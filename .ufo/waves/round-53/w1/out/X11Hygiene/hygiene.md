# X11Hygiene — round 53 end-of-wave hygiene (lane kama)

Verdict: **hygiene is clean for the five required surfaces with two pre-existing leaks and one lane artifact defect** — no llama-server left running at the final sweep, fleet tree clean, my scratch removed, no process of mine holding another's `/proc/<pid>/mem`; the frozen C2 counter and the replay selftest both reproduce at the build tip.

All timestamps are host local (`-03:00`), taken 2026-10-27 03:12–03:20. Scratch used and removed: `/fast/scratch/hyaku/kama-r53/X11Hygiene`. Nothing in the lane, the fleet, `measured/` or any tool was modified; no tracer was used; no package was installed (none was needed).

## 0. Re-runs before the hygiene sweep (calibration / operability)

### C2 — frozen cited-path counter at the build tip

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # toplevel verified == $S/lane
git -C $S/lane status --porcelain                                       # empty; HEAD bc8e6e7f, build c22602bd is an ancestor
python3 tools/round53-cited-path-check.py --repo $S/lane \
        --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch $S/c2b
```

exit 0; wall 1.1–1.4 s per run; output (identical in all runs):

```
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```

- Determinism: two runs at the same rev produced byte-identical output (`c2-rerun.out`, `c2-rerun2.out`).
- Reproduction at pinned fleet revisions (`--fleet-rev`), because the fleet HEAD moves every few minutes:
  - `--fleet-rev 0c3f44be6c7ec6503f4e672a193d911424a88c5e` → byte-identical to the **committed** receipt `git show bc8e6e7f:.ufo/waves/round-53/measured/c2-build.out` (`diff -u` exit 0).
  - `--fleet-rev ee9f7341bd98de0fcd85f6c01f689301589b27e9` → byte-identical to the **L1 worktree** receipt `.ufo/waves/round-53/measured/c2-build.out` once its `$ python3 …` header and `exit=0` trailer are stripped (`diff -u` exit 0).
  - unpinned `HEAD` (= `d2a6c59a` at 03:14:43) → same counts, met=True.
  So the lane's C2 receipt is exactly reproducible, and the verdict is invariant across three fleet trees: `cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0`.
- Scratch hygiene: `--scratch $S/c2b` was created by the counter and left empty (`ls -A` → no entries).
- Operability note: the counter's default `--fleet-rev HEAD` is a moving target during an active wave — `git reflog` shows five exports in twelve minutes (`0c3f44be` 03:06:09, `ee9f7341` 03:12:25, `d2a6c59a` 03:12:42, `71256a5d` 03:17:17, `33540c6e` 03:18:03). The receipt prints `fleet=<rev>` on its first line, which is what makes the run reproducible; keep pinning it.

### Replay selftest

The build commit `c22602bd` and the lane HEAD `bc8e6e7f` hold identical `tools/kama-live-replay.py` and `tools/kama-llamacpp-live.py` (`git diff --stat` empty), so the selftest run in the clone measures the same code as at the build.

```
mkdir -p $S/selftest
python3 tools/kama-live-replay.py --selftest --scratch $S/selftest
```

exit 0, `KLR_SELFTEST pass=43 fail=0`, no stderr, and the selftest leaves `$S/selftest` empty (it removes every `klr-st-*` directory). This matches the L1's untracked receipt `.ufo/waves/round-53/measured/klr-selftest-build.out` (`pass=43 fail=0`). The selftest never launches the archive binary (file:// fixtures plus a fake live tool), so it starts no `llama-server`; `pgrep -af llama-server` after the run confirmed that.

Minor defect found by the first attempt: `--selftest` with a `--scratch` directory that does not exist aborts with a traceback instead of creating it.

- file:line at the measured build: `tools/kama-live-replay.py:548` (blob of `c22602bd`; `_selftest` starts at 544): `d = tempfile.mkdtemp(prefix="klr-st-", dir=root)`
- command: `python3 tools/kama-live-replay.py --selftest --scratch $S/selftest` with `$S/selftest` absent →
  `FileNotFoundError: [Errno 2] No such file or directory: '.../selftest/klr-st-mtbk_igh'`, traceback, exit 1.
- proposed fix (verified, one line): `os.makedirs(root, exist_ok=True)` at the top of `_selftest`, before `cases = []`.
  Diff: `X11Hygiene/replay-selftest-scratch-fix.diff`. Applied to a copy of the `c22602bd` blob, `--selftest --scratch <nonexistent>` then exits 0 with `KLR_SELFTEST pass=43 fail=0` (`X11Hygiene/patched-selftest-nonexistent-scratch.out`).
- Note: line numbers refer to the committed blob; the lane worktree copy of the file is currently modified by the L1 (`M tools/kama-live-replay.py`), so its line numbers have shifted.

## 1. `pgrep -af llama-server`

Final sweep 03:19:50: **no match**, `pgrep -af llama-server` exit 1; cross-user check `sudo -n pgrep -af llama-server` matched only the `pgrep` itself; `sudo -n ss -ltnp | grep -i llama` → no llama listener at all, and at no point did I observe a llama listener outside `127.0.0.1` (count of non-loopback llama listeners: 0).

Mid-wave snapshot 03:18:15 (recorded for completeness, both were live seats, not leaks):

```
2826889  tools/kama-llamacpp-live.py (driver, K2Design seat)
2827397  .../K2Design/hold/work/server/llama-b11909/llama-server -m ...stories260K.gguf --host 127.0.0.1 --port 35203
2926594  tools/kama-llamacpp-live.py (driver, Sen2Scratch seat)
2927204  .../Sen2Scratch/.../llama-server ... --host 127.0.0.1 --port 46259
```

Both were gone 95 s later (servers and drivers), i.e. the seats' own teardown worked.

Leak that `pgrep -af llama-server` cannot see (round 49 leftovers, not mine, not killed — stopping services is outside this seat):

```
2553430  1494  06:43:00  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-k_sicwpn/work-w1/stub.py ...  (LISTEN 127.0.0.1:43591)
2608023  1494  06:42:21  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-tj8m881o/work-w1/stub.py ...  (LISTEN 127.0.0.1:43151)
```

Both are orphans (ppid 1494 = `systemd --user`), their scratch trees are gone (`/proc/<pid>/cwd` → `.../r49c1-*/tree (deleted)`). Teardown for the lane owner: `kill 2553430 2608023`. They bind loopback only.

## 2. `du` of `/fast/scratch/hyaku/kama-r53`

Final sweep 03:19:50 — total **15 G over 42 entries**, `/fast` 29 % used (574 G free):

```
3.1G kama-r53/Sen4Fixture    784M kama-r53/Sim1          654M kama-r53/L1
634M kama-r53/Sen2Scratch    599M kama-r53/J6HostMemfd   547M kama-r53/J5Preload
546M kama-r53/J7Late         491M kama-r53/K2Design      469M kama-r53/X3Teardown
469M kama-r53/K1Cheat
```

Trend during the wave: 13 G at 03:15:04 (top: Sen2Scratch 1.2 G, L1 977 M, X6Battery 612 M, X4Fresh 469 M, J6HostMemfd 468 M, J2SwapUnchecked 447 M, X2Rerun 414 M, J3ForgedReceipt 413 M, X5Selftest 393 M, J12Hide 393 M) → 20 G / 52 entries at 03:18:15 → 15 G / 42 entries at 03:19:50. Seats are removing their scratch as they finish; a 392 M `git clone --shared` checkout plus counter downloads per seat is the dominant cost. Earlier round accumulates too: `kama-r51` 5.6 G; `kama-r49` directories are gone from disk but their two processes still hold deleted cwds (see §1).

My own scratch: removed with `rm -rf /fast/scratch/hyaku/kama-r53/X11Hygiene`, verified absent at 03:19:50. It held one 392 M shared clone and ~5 kB of receipts (copies kept in the out dir).

## 3. `git -C /home/vgpnk/Projects/shokunin status --porcelain`

Empty, `count=0`, at 03:18:15 and again at 03:19:50 (also empty with `--untracked-files=all`). **No file a kama seat wrote is outstanding at the fleet root**, so there is nothing to name and nothing to delete. Fleet HEAD at the final sweep: `33540c6e 2026-10-27 03:18:03 -0300 round-46: kengaku report`.

The fleet HEAD moved five times during the wave, all `export from jj` (reflog): `0c3f44be` 03:06:09 → `ee9f7341` 03:12:25 → `d2a6c59a` 03:12:42 (`round-53: kama L0 question correction`) → `71256a5d` 03:17:17 → `33540c6e` 03:18:03. `git merge-base --is-ancestor d2a6c59a HEAD` → yes, so these are forward exports, not a rewind. Consequence for §0: pin `--fleet-rev` when reproducing.

## 4. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain`

36 entries at 03:19:50 (29 at 03:15). Lane HEAD unchanged: `bc8e6e7f 2026-10-27 03:11:49 round-53: wave kama-r53-w1 spec (66 seats, v2) and build receipts`.

**(a) The two build receipts were rewritten in place after the commit — defect to record.** HEAD committed `measured/{c1,c2}-build.out` at 03:11:49; their worktree mtimes are 03:12:26.96 and 03:12:29.05, i.e. re-runs overwrote the committed artifacts 37 s and 40 s later.

- `git -C … show bc8e6e7f:.ufo/waves/round-53/measured/c1-build.out` vs the file on disk: bind pids `2313814/2320072/2327888` → `2530913/2533254/2534535`; ports `35283/33003/39493` → `40803/44241/46589`; mapping inodes `1286953431/279466795/1489267792` → `2026804480/1081905417/550154254`; sealed memfd sizes `201925/204918/198961` → `184936/181765/190304`; nonces and witness strings changed; a `$ python3 …` header line and an `exit=0` trailer were added.
- c2-build.out: committed `fleet=0c3f44be…` → worktree `fleet=ee9f7341…`, plus the same header/trailer.
- Verdict lines are unchanged in both files (`bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`; `fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True`), and my independent reruns reproduce both readings exactly (§0). So no claim moved, but after an in-place rewrite the committed file is no longer the artifact of record for the run it describes. Proposed handling (lane owner, not applied): commit the re-run as the receipt of record (or add its `$ python3 …` line and re-commit), and treat `measured/*.out` as append-only-once for the wave.

**(b) L1 integration in flight** — `M SKILL.md`, `M corpus/QUALITY.md`, `M registry/hexrun-ledger.tsv`, `M tools/kama-live-replay.py`, `M tools/kama-llamacpp-live.py`. The last two are the files C1 measures: from this point a counter run with `--repo .` would measure uncommitted code, so a C1 rerun must name a clone/commit at the measured tip (I did: `git clone --shared`, tip `c22602bd`).

**(c) Untracked but expected in the wave directory** — 24 `measured/*-build.out` receipts plus `measured/measure.sh` (the L1 harness, not yet committed), `.ufo/waves/round-53/hexrun-evidence/`, `.ufo/waves/round-53/integration/`, `w1.ready`, `w1.ready.dispatched`, `w1/out/` (seat artifacts, mine included). No seat wrote outside `.ufo/waves/round-53/`; no leaf wrote into `measured/` — the listing shows only the L1's own files there.

## 5. Processes holding another process's `/proc/<pid>/mem`

Exactly one holder on the host at both 03:18:15 and 03:19:50:

```
holder=3283560 target=3684122 target=dead
cmd=/usr/bin/python -u /tmp/omp-python-runner-1000/runner-2y055qoyfok9i.py   (fd 9 -> /proc/3684122/mem, started 02:54:16, ppid 875345)
```

`/proc/3684122` no longer exists, so the open `/proc/<pid>/mem` fd keeps the dead process's `mm` pinned until the fd is closed; it is released when that runner's session ends. It is **not mine**: my eval kernel is pid 2738839 (checked with `os.getpid()` inside `eval`), and `pgrep -af X11Hygiene` exits 1. Neither of my runs opens another process's memory: the C2 counter does no `/proc` reads, and the replay selftest starts no server. A seat that needs memory readings should use the counter's own short-lived processes rather than an eval kernel, so the fd does not outlive the target.

## 6. My own seat state

- Scratch removed, verified absent; nothing of mine is at the fleet root, in the fleet repo, in the lane, or in `measured/`.
- No jj mutation: only `jj --ignore-working-copy -R <lane> root|log|status` (which never snapshots). Observed, not acted on: the lane's recorded working copy `f58c051e` reports deletions of `kama-shokunin/.ufo/waves/round-36/assimilation/…` paths that the git worktree does not show as deleted — a stale recorded state, not round-53 content, flagged for the lane owner.
- No packages installed or upgraded; no `pacman` transaction attempted; no counter, preregistration or control edited; no tracer wrapped around any counter.

## Evidence files (this directory)

- `final-sweep.txt` — the authoritative late sweep (03:19:50) with all five hygiene items verbatim.
- `c2-rerun.out`, `c2-rerun2.out`, `c2-rerun.err` — unpinned-HEAD reruns (determinism).
- `c2-at-0c3f44be6c7ec6503f4e672a193d911424a88c5e.out`, `c2-at-ee9f7341bd98de0fcd85f6c01f689301589b27e9.out`, `lane-head-c2-build.out` — pinned-fleet reproduction and the committed receipt it matches byte-for-byte.
- `selftest.out`, `selftest.err` — `KLR_SELFTEST pass=43 fail=0`.
- `replay-selftest-scratch-fix.diff`, `patched-selftest-nonexistent-scratch.out` — proposed one-line fix and its verification.
