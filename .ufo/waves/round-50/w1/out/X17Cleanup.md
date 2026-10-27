# X17Cleanup — round-50 w1 end-of-wave hygiene

**Verdict: nothing of mine is left behind (no process, no clone, no fleet-root file, scratch removed), and the wave is clean on containment and evidence — but two things need the L1's hand: `w1/out` is unignored and a run can drop 74 MiB of binaries into it (race window, measured), and two round-49 stub servers still hold loopback ports after 80 min. The literal `pgrep -af llama-server` check cannot measure what it claims, and `ppid==1`-only orphan detection misses the round-49 leftovers entirely.**

Snapshot window 21:52:00 → 22:02:03 −03:00, wave live throughout (all three counters in flight, ~11–30 seats). Every number is timestamped; the wave churns (scratch 12 G→25 G→17 G; out 108 K→585 M→8.4 M), so `hygiene-recheck.sh` is the deliverable that re-measures, not the numbers.

## Required items

**(1) `pgrep -af llama-server`** — 21:52:12 returned exactly one match, a *python tool* whose argv contains the string (`2087662 …/J1NoEnv/.../kama-llamacpp-live.py --server …/llama-server …`, rc=0). `pgrep -x llama-server` at the same instant: rc=1; `ps -eo comm= | grep -i llama`: rc=1 — no binary was running. By 21:56:30 real servers existed (`pgrep -x llama-server` → `2592273`, `2752383`), each with a live non-orphan parent (`ps -o pid,ppid,comm,args`: `2592273 2590137 llama-server …/X11ModelSwap/work1/server/llama-b11909/llama-server`). **None was started by this seat — it started no process at all.** Final reading 22:04:00: `pgrep -af llama-server` → rc=1, `pgrep -x llama-server` → rc=1, and 0 orphaned round-50 processes (ppid 1 or systemd-reparented).

**(2) `/fast/scratch/hyaku/kama-r50` top 10** (21:57:58, total 25 G): `J6Ablation 3.2G`, `Rev1Base 2.7G`, `Sen1Env 1.7G`, `X3Gate2 1.2G`, `X6Sao2 1.1G`, `X1Observe2 968M`, `J2NoPdeathsig 792M`, `L1 718M`, `Sen2Proc 717M`, `X8WitnessPort 591M`. Growth 12 G→20 G→25 G→22 G→17 G→**12 G at 22:04** (seats self-clean). `/fast` headroom never below 575 G (804 G fs; 596 G avail 21:56, 606 G at 22:04).

**(3) `git -C /home/vgpnk/Projects/shokunin status --porcelain`** — four readings: `?? .ufo/reports/round-52/mori.md` (21:52), ` M .ufo/l0-questions.md` (21:56), *empty* (21:57:42), ` M .scratch/goal-20261026-hyaku-run9.md` (21:58). **Nothing named is mine or this lane's.** The fleet porcelain is time-varying during a live wave — re-read immediately before integrating; one clean reading is not proof.

**(4) Strays I wrote at the fleet root: none.** This seat wrote only the five files listed at the end. Nothing else needs sweeping for this seat; the only lane-side oddity I found (`X1Assimilation` at the wave root) is dispatch-assigned, see F4.

## Defects (file:line, command, fix)

### F1 high — `w1/out` unignored; 74 MiB of binaries inside the lane repo's untracked tree
`kama-shokunin/.gitignore:1-3` ignores only `.ufo/interactive-sessions/`, `.ufo/state/`, `__pycache__/`.
- `git -C kama-shokunin check-ignore -v .ufo/waves/round-50/w1/out/Sen1Env/runs/V0-baseline/work/download/llama-b11909-bin-ubuntu-x64.tar.gz` → **rc=1, not ignored**.
- Peak `find … -size +1M | awk` → `files=22 MiB=74.0` (21:59:34): the 75 MB release tarball, `stories260K.gguf` ×2, `llama-b11909/*.so`.
- Transient: `du -sh out` = **585 M / 26,799 files** at 21:59:29 (`Sen1Env/homescratch`, a full HOME copy, gone in a minute).
- Self-cleaned by 22:01:59 → out 8.4 M / 607 files; residual unignored binaries: `R3Provenance/stories260K.gguf` 1.19 MB (plus a 1.38 MB text tree that is fine to commit).
- `git status --porcelain -uall -- .ufo/waves/round-50/w1/out | wc -l` → 313 at 21:58, all untracked, none ignored.

So: a race window, not a permanent payload — `git add -A` at 21:59 would have committed 585 MB. Fix (validated diff at `out/X17Cleanup/proposed-gitignore.diff`; patterns confirmed with `git -c core.excludesFile=… check-ignore -v` against the tarball, both ggufs and `libllama.so.0.7.0`):
```
+.ufo/waves/round-50/w1/out/**/work/
+.ufo/waves/round-50/w1/out/**/*.gguf
+.ufo/waves/round-50/w1/out/**/*.tar.gz
+.ufo/waves/round-50/w1/out/**/llama-b11909/
```
Or commit `w1/out` selectively (`*.md|json|txt|out|diff`), never `-A`.

### F2 high (calibration) — `pgrep -af llama-server` cannot fail correctly
It matches `kama-llamacpp-live.py --server …/llama-server` and anything carrying `--alias kama-r48-live`. Correct forms (both in the script): `pgrep -x llama-server`; earlier-round leftovers by **scratch path** — `pgrep -f "$HYAKU/kama-r4[0-9]/"` (trailing slash: the alias has none). My first draft used the bare pattern and reported five round-50 seats as round-48 leftovers.

### F3 medium — round-49 stub servers alive on a deleted cwd
```
2553430 ppid=1494 age=4803s  /usr/bin/python3 …/kama-r49/M1Ctr/r49c1-k_sicwpn/work-w1/stub.py -m …/m.gguf …
2608023 ppid=1494 age=4764s  /usr/bin/python3 …/kama-r49/M1Ctr/r49c1-tj8m881o/work-w1/stub.py …
cwd → /fast/scratch/hyaku/kama-r49/M1Ctr/.../tree (deleted)
127.0.0.1:43591 users:(("python3",pid=2553430)); 127.0.0.1:43151 users:(("python3",pid=2608023))
curl -m2 http://127.0.0.1:43591/health → 501
```
Reparented to `systemd --user` (pid 1494), not pid 1 — **so `ppid==1`-only orphan checks pass while these two hold ports**. Round-49's counter left them (the R2 shape); round 50 inherited them. Not mine to kill: L1 decision (`kill 2553430 2608023`). Round-50's own orphans at 21:58 were all `fresh` (<300 s, teardown seats J2NoPdeathsig/Sen3Teardown/X9Descend, expected during a kill experiment) — the script age-gates at 300 s.

### F4 withdrawn — the wave-root `X1Assimilation` dir is dispatch-assigned
`grep -oE '\.ufo/waves/round-50/[A-Z][A-Za-z0-9]+/' .ufo/waves/round-50/w1/dispatch.json | sort | uniq -c` → `2 .ufo/waves/round-50/X1Assimilation/`. The seat populated it (7 files at 22:00: `collision-report.md`, `guard-proof.md`, `quarantine-verdicts.md`, …). I flagged it twice (empty dir at 21:54; populated dir at 22:00) — both were my check's fault, not the seat's. No action.

### F5 low — `mktemp -d` without `-p $S` at the shared scratch root
21:55:47–21:56 at `/fast/scratch/hyaku/`: `run-receipt-h00alous` (a git repo), `run-receipt-home-hv59cndy`, `run-receipt-jew2ws70` (lane checkout with `.git`/`.ufo`), `run-receipt-home-mz6pmbp7` — all transient (gone by 21:58), i.e. a driver using `TMPDIR=/fast/scratch/hyaku` rather than its seat dir. Pre-existing, older, not mine: `_d.txt` 16:25, `base-census.sh` 04:14, `line137.txt` 15:20, `unblob-tree.json` 18:51.

### F6 low/medium — more than one live lane clone per seat
Lane-derived repos (counted by `objects/info/alternates`, so fixture repos are excluded): `J6Ablation 6`, `J1NoEnv 2`, `L1 2`, `X15NoHarm2 2`; 36 total. `J1NoEnv`'s second has `origin=/fast/scratch/hyaku/kama-r50/J1NoEnv/lane` — a clone of its own clone (~700 MB, not `--shared` against the lane).

### F7 low — seven Sen1Env receipts cite `/tmp`
`grep -rl '/tmp/' w1/out` (22:01) → `Sen1Env/{runs/V3-home-pth, runs/V4-path-python, runs/V13-path-curl}` (`*.json` + `mark-*.txt`) and `summary.json`; e.g. `V4-path-python.json:206` → `/tmp/kama-probe.qgPeOO/m40409.body`. `/tmp` is never evidence, so those three arms' probe paths are unverifiable after the wave. (`X13Threshold.md` mentions `/tmp` in prose; my two docs quote this finding deliberately.)

### F8 informational — lane tip is 3 commits past the build
`git merge-base --is-ancestor 97c864b HEAD` → 0 (true ancestor); `26ecba64..HEAD` is 5 commits: `3b79eadd` receipts, **`3d42897b` S498 row markdown tick parity fix**, `6f3bd322` spec/dispatch, `97c864be` build, `601c8889` freeze. Source-row claims should name the measured tip. Lane porcelain never showed a change outside `.ufo/waves/round-50/` (21:57:42, 21:58:05, 22:02 — `PASS` each time): no seat edited a lane file in place.

## Clean
No value-bearing credential marker in any of the 607 out files (`server.token = <value>`, `ghp_…`, `sk-ant-…`, `ANTHROPIC_API_KEY=<value>`, `BEGIN … PRIVATE KEY`); the marker patterns are self-tested (6/6 real leak shapes match, 4/4 prose shapes rejected) so the PASS is not vacuous. No wave process with `TMPDIR` outside its seat dir (11/11 at 21:57; transient child 2681419 showed `TMPDIR` unset at 21:56:02 and exited before it could be named). Host at 21:56: load `17.34 11.26 11.98`, 12 Gi/30 Gi mem, 7.2 Gi swap.

## Retained evidence
`out/X17Cleanup/recheck-snapshot.out` — verbatim latest run, **22:03:40, exit 0, `RESULT met=True fails=0`**; WARNs at that instant: 2 round-49 stubs, 2 listeners (same two), 3 scratch-root files, 1 >1 MiB file in out, 7 `/tmp`-citing receipts. Re-run after the last seat lands:
`kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/hygiene-recheck.sh --final` (read-only, exit 1 on FAIL).
Four bugs were found in the check itself while writing it (argv-matching `pgrep`, `ppid==1`-only orphans, the `kama-r48-live` alias, and a dangling `!` that inverted the wave-root find) — fixed, and documented in `hygiene.md` because the L1's own gate will hit the same traps.

No counter was run, no clone made, no lane file edited, no process started, no pacman. Scratch `/fast/scratch/hyaku/kama-r50/X17Cleanup` removed.

## Files written (absolute)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/hygiene.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/hygiene-recheck.sh
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/recheck-snapshot.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/proposed-gitignore.diff
