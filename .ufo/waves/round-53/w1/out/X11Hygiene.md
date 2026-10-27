# X11Hygiene — round 53 end-of-wave hygiene (lane kama, w1)

**Verdict: PASS on the required surfaces — C2 at the build tip reproduces byte-for-byte (`met=True`) at two pinned fleet revs, the replay selftest is 43/43, no llama-server survives the wave, the fleet tree is clean, my scratch is removed and no process of mine holds another's `/proc/<pid>/mem`; two pre-existing leaks (round-49 stub servers, one peer eval-kernel mem fd) and one in-place rewrite of the L1's build receipts are recorded below.**

Full detail and raw captures: `.ufo/waves/round-53/w1/out/X11Hygiene/` (`hygiene.md`, `final-sweep.txt`). Nothing in the lane, the fleet, `measured/` or any tool was modified; no tracer used; no package installed (none needed).

## 1. Frozen C2 counter re-run at the build tip c22602bd (calibration)

```
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane   # toplevel == $S/lane, status clean
python3 tools/round53-cited-path-check.py --repo $S/lane --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch $S/c2b
```
exit 0, 1.1–1.4 s:
```
fixture=1 lane=1 scenarios=8/8 cited=682 unresolved=14 disclosed=14 undisclosed=0 bad=0 stale=0 dropped=0 met=True
```
- Deterministic: two runs byte-identical (`c2-rerun.out`, `c2-rerun2.out`).
- Reproduced at the exact fleet revisions, because fleet HEAD moved five times during the wave (`git reflog`: `0c3f44be` 03:06:09, `ee9f7341` 03:12:25, `d2a6c59a` 03:12:42, `71256a5d` 03:17:17, `33540c6e` 03:18:03 — all `export from jj`; `d2a6c59a` is an ancestor of HEAD, verified with `merge-base --is-ancestor`):
  - `--fleet-rev 0c3f44be…` → `diff -u` against `git show bc8e6e7f:.ufo/waves/round-53/measured/c2-build.out` **exit 0** (the committed receipt, byte for byte).
  - `--fleet-rev ee9f7341…` → `diff -u` against the L1's worktree `measured/c2-build.out` (header/trailer stripped) **exit 0**.
  - unpinned `HEAD` (= `d2a6c59a`) → same counts, `met=True`.
- Operability: the counter creates and empties its own scratch (`ls -A $S/c2b` → none). Its default `--fleet-rev HEAD` is not reproducible during a wave; the receipt's first line prints `fleet=<rev>`, so pin it.

## 2. Replay selftest (operability)

Build `c22602bd` and lane HEAD `bc8e6e7f` carry identical `tools/kama-live-replay.py` / `kama-llamacpp-live.py` (`git diff --stat` empty), so the clone measures the build code.

```
mkdir -p $S/selftest && python3 tools/kama-live-replay.py --selftest --scratch $S/selftest
```
exit 0 → `KLR_SELFTEST pass=43 fail=0`, empty stderr, no residue (`ls -A $S/selftest` → 0 entries). Matches the L1's `measured/klr-selftest-build.out`. It starts no server (file:// fixtures + fake live tool); `pgrep -af llama-server` afterwards confirmed.

**Defect (P3, verified fix):** `--selftest --scratch <nonexistent>` dies with a traceback instead of creating the directory.
- Location: `tools/kama-live-replay.py:548` in blob `c22602bd` (`_selftest` at 544): `d = tempfile.mkdtemp(prefix="klr-st-", dir=root)`.
- Command: first attempt with `$S/selftest` absent → `FileNotFoundError: [Errno 2] No such file or directory: '.../selftest/klr-st-mtbk_igh'`, exit 1.
- Fix: `os.makedirs(root, exist_ok=True)` at the top of `_selftest`. Diff: `X11Hygiene/replay-selftest-scratch-fix.diff`; applied to a copy of the build blob, the same command exits 0 with `pass=43 fail=0` (`X11Hygiene/patched-selftest-nonexistent-scratch.out`). Line numbers are from the committed blob — the lane worktree copy is currently `M`, so they have shifted there.

## 3. `pgrep -af llama-server` (final sweep 03:19:50)

No match: `pgrep -af llama-server` exit 1; `sudo -n pgrep -af llama-server` matched only the `pgrep` itself; `sudo -n ss -ltnp | grep -i llama` → no llama listener; **0** llama listeners off `127.0.0.1` at any observation. Mid-wave (03:18:15) two live seats held servers — `2827397` (`K2Design`, `127.0.0.1:35203`) and `2927204` (`Sen2Scratch`, `127.0.0.1:46259`) with their drivers — and both had torn down by 03:19:50, so seat teardown works.

Leak `pgrep llama-server` cannot see (not mine, not killed — stopping services is outside this seat): two orphaned round-49 stub servers, ppid 1494 (`systemd --user`), scratch trees deleted (`/proc/<pid>/cwd` → `(deleted)`):
```
2553430  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-k_sicwpn/work-w1/stub.py ...  LISTEN 127.0.0.1:43591  (6h43m)
2608023  python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-tj8m881o/work-w1/stub.py ...  LISTEN 127.0.0.1:43151  (6h42m)
```
Teardown for the lane owner: `kill 2553430 2608023`.

## 4. `du` of /fast/scratch/hyaku/kama-r53 (final sweep)

Total **15 G over 42 entries**, `/fast` 29 % used (574 G free); top 10: `Sen4Fixture 3.1G, Sim1 784M, L1 654M, Sen2Scratch 634M, J6HostMemfd 599M, J5Preload 547M, J7Late 546M, K2Design 491M, X3Teardown 469M, K1Cheat 469M`. Trend: 13 G at 03:15:04 → 20 G / 52 entries at 03:18:15 → 15 G / 42 at 03:19:50 (seats cleaning up as they finish; ~392 M shared clone + counter downloads per seat). Prior round: `kama-r51` 5.6 G. My scratch (`X11Hygiene`, one 392 M clone + ~5 kB receipts) removed with `rm -rf`, absent at 03:19:50; receipts copied out first.

## 5. `git -C /home/vgpnk/Projects/shokunin status --porcelain`

Empty, `count=0` at 03:18:15 and 03:19:50 (also empty with `--untracked-files=all`) → **no file a kama seat wrote is outstanding at the fleet root**; nothing to name or delete. Fleet HEAD `33540c6e 2026-10-27 03:18:03 round-46: kengaku report`.

## 6. `git -C …/kama-shokunin status --porcelain` (36 entries at 03:19:50; lane HEAD unchanged `bc8e6e7f`)

- **Build receipts rewritten in place after the commit (record):** HEAD committed `measured/{c1,c2}-build.out` at 03:11:49; worktree mtimes 03:12:26.96 / 03:12:29.05. `git show bc8e6e7f:…c1-build.out` has bind pids `2313814/2320072/2327888`, ports `35283/33003/39493`, inodes `1286953431/279466795/1489267792`; the file on disk has `2530913/2533254/2534535`, `40803/44241/46589`, `2026804480/1081905417/550154254`, new nonces, plus a `$ python3 …` header and `exit=0` trailer; c2 went `fleet=0c3f44be…` → `fleet=ee9f7341…` plus header/trailer. Verdict lines are identical in both versions (`met=True` both legs) and my independent reruns reproduce both readings exactly (§1), so no claim moved — but the committed file is no longer the artifact of record for its own run. Suggested: commit the re-run as the receipt of record, and treat `measured/*.out` as write-once for the wave.
- **L1 integration in flight:** `M SKILL.md`, `M corpus/QUALITY.md`, `M registry/hexrun-ledger.tsv`, `M tools/kama-live-replay.py`, `M tools/kama-llamacpp-live.py`. The last two are what C1 measures — a rerun must name a clone/commit at the measured tip, not `--repo .`.
- **Untracked, expected:** 24 `measured/*-build.out` + `measured/measure.sh`, `hexrun-evidence/`, `integration/`, `w1.ready{,.dispatched}`, `w1/out/`. No seat wrote outside `.ufo/waves/round-53/`; no leaf wrote in `measured/`.

## 7. Holders of another process's `/proc/<pid>/mem`

One holder, unchanged at both sweeps:
```
holder=3283560 target=3684122 target=dead  fd 9 -> /proc/3684122/mem
cmd=/usr/bin/python -u /tmp/omp-python-runner-1000/runner-2y055qoyfok9i.py   (started 02:54:16, ppid 875345)
```
The target is gone, so that fd pins a dead process's `mm` until the holder exits. **Not mine:** my eval kernel is pid 2738839 (`eval` → `os.getpid()`), and `pgrep -af X11Hygiene` exits 1. Neither of my runs opens another process's memory — C2 does no `/proc` reads and the selftest starts no server. Guidance: read memory through the counter's own short-lived processes, not an eval kernel, so fds cannot outlive their target.

## 8. Scope / non-actions

No jj mutation (only `jj --ignore-working-copy root|log|status`, which never snapshots). Observed, flagged, not acted on: the lane's recorded working copy `f58c051e` reports deletions of `kama-shokunin/.ufo/waves/round-36/assimilation/…` that the git worktree does not show — stale recorded state, not round-53 content. No counter/preregistration/control edit, no tracer, no pacman, no subagents, nothing written at the fleet root, nothing in `measured/`.

## Files written

```
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/hygiene.md
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/final-sweep.txt
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/c2-rerun.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/c2-rerun.err
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/c2-rerun2.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/c2-at-0c3f44be6c7ec6503f4e672a193d911424a88c5e.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/c2-at-ee9f7341bd98de0fcd85f6c01f689301589b27e9.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/lane-head-c2-build.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/selftest.out
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/selftest.err
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/replay-selftest-scratch-fix.diff
/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X11Hygiene/patched-selftest-nonexistent-scratch.out
```
