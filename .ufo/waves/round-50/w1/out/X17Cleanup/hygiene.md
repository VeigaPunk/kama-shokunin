# X17Cleanup — round-50 w1 end-of-wave hygiene

Snapshot window: 2026-10-26 21:52:00 → 21:59:40 −03:00 (wave still live: ~11–30 seat
processes, all three counters in flight). Every number below is timestamped; the wave
churns fast (out/ moved 81 M → 456 M → 83 M inside 5 s), so treat this as a reading,
not a state. `hygiene-recheck.sh` next to this file re-measures all of it read-only —
run it with `--final` after the last seat lands.

Scope note: no counter was run by this seat, no clone was made, no lane file was edited,
no process was started, and nothing was deleted outside this seat's own scratch.

---

## 1. `pgrep -af llama-server`

```
$ pgrep -af llama-server        # 21:52:12
2087662 /usr/bin/python3 -I .../J1NoEnv/.../tools/kama-llamacpp-live.py --server .../llama-server ...
rc=0
```

At 21:52 and 21:56 the only matches were **python tools with `llama-server` in argv**;
no `llama-server` binary existed yet. By 21:56:30 real servers were up (seats mid-run):

```
$ pgrep -x llama-server         # exe name only — the correct emptiness check
2592273
2752383
$ ps -eo pid,ppid,comm,args | grep '[l]lama'
2592273 2590137 llama-server .../X11ModelSwap/work1/server/llama-b11909/llama-server ...
```

**Nothing in that list was started by this seat** (this seat started no server and no
process at all; its only writes are the three files in `out/X17Cleanup/`).

Calibration defect in the literal check as specified: `pgrep -af llama-server` matches
`kama-llamacpp-live.py --server .../llama-server` (argv contains the name) and so cannot
distinguish "a server is running" from "a python tool is running". Use
`pgrep -x llama-server` (matches the executable name only). Verified: at 21:52
`pgrep -x llama-server` → rc=1 (empty) while `pgrep -af` → rc=0 with one python pid.

Additionally, `ps -eo comm= | sort | uniq -c | grep -i llama` → rc=1 at 21:52, i.e. no
binary at all at that instant.

At 21:58 the recheck (section 1) found 5 wave servers, each with a live, non-orphan
parent (`ppid` = the seat's live tool), i.e. normal in-flight work:

```
wave llama-server pid=2990076 ppid=2987107 age=51s cwd=.../J2NoPdeathsig/tree
wave llama-server pid=3127949 ppid=3124696 age=39s cwd=.../Sen3Teardown/lane
wave llama-server pid=3133900 ppid=3130587 age=39s cwd=.../Sen3Teardown/lane
```

## 2. `/fast/scratch/hyaku/kama-r50` — top 10 by size

```
$ du -sh /fast/scratch/hyaku/kama-r50/* | sort -rh | head -10     # 21:57:58
3.2G  /fast/scratch/hyaku/kama-r50/J6Ablation
2.7G  /fast/scratch/hyaku/kama-r50/Rev1Base
1.7G  /fast/scratch/hyaku/kama-r50/Sen1Env
1.2G  /fast/scratch/hyaku/kama-r50/X3Gate2
1.1G  /fast/scratch/hyaku/kama-r50/X6Sao2
968M  /fast/scratch/hyaku/kama-r50/X1Observe2
792M  /fast/scratch/hyaku/kama-r50/J2NoPdeathsig
718M  /fast/scratch/hyaku/kama-r50/L1
717M  /fast/scratch/hyaku/kama-r50/Sen2Proc
591M  /fast/scratch/hyaku/kama-r50/X8WitnessPort
$ du -sh /fast/scratch/hyaku/kama-r50                              # 25G at 21:57:58
```

Growth across the window (same lane, live seats): 12 G @21:54 → 20 G @21:56 → 25 G
@21:57 → 22 G @21:58 → 17 G @22:02 → **12 G @22:04** as seats finished and removed their
clones/work dirs. Each C1 replay pulls ~75 MB from github.com plus ~1 MB from
huggingface.co, and most seats keep a lane clone (~700 MB); 60+ seats put the wave in
the 25–60 GB band. `/fast` headroom never dropped below 575 G (`df -h /fast`: 804 G
total, 596 G avail at 21:56; 606 G at 22:04). Disk is not a risk for this wave.

Host load at 21:56: `17.34 11.26 11.98`, mem 12 Gi/30 Gi used, swap 7.2 Gi used.

## 3. `git -C /home/vgpnk/Projects/shokunin status --porcelain`

Four readings, all clean **of anything this seat wrote**:

| 21:52:12 | `?? .ufo/reports/round-52/mori.md` |
| 21:56:30 | ` M .ufo/l0-questions.md` |
| 21:57:42 | *(empty — clean)* |
| 21:58:05 | ` M .scratch/goal-20261026-hyaku-run9.md` |

Nothing there is mine and nothing names this lane. Note for the L1: the fleet root
porcelain **is not stable during an active wave** — fleet tooling rewrites
`.ufo/l0-questions.md`, `.scratch/goal-*.md` and `.ufo/reports/round-52/mori.md`
between readings. A single clean reading is not proof of cleanliness; re-read
immediately before integrating.

Also checked, in case a seat wrote a gitignored stray at the fleet root:
`git status --porcelain --ignored=matching | grep -E '^(\?\?|!!) [^/]+/?$'` lists only
the lane directories (`kama-shokunin/`, `mori-shokunin/`, …), i.e. by design. Root-level
non-directory files are the 14 fleet files (ROADMAP.md, AXES.md, …, MANIFEST.json); the
newest are `MANIFEST.json` 21:24 and `.gitignore` 11:54 — both timestamped before this
wave's seats and unmodified per porcelain. **No stray file from this wave sits at the
fleet root.**

## 4. Stray files written by this seat at the fleet root

**None.** This seat wrote exactly three files, all under its own out dir:

```
.ufo/waves/round-50/w1/out/X17Cleanup.md                    (report)
.ufo/waves/round-50/w1/out/X17Cleanup/hygiene.md            (this file)
.ufo/waves/round-50/w1/out/X17Cleanup/hygiene-recheck.sh    (read-only re-check)
.ufo/waves/round-50/w1/out/X17Cleanup/recheck-snapshot.out  (its output)
.ufo/waves/round-50/w1/out/X17Cleanup/proposed-gitignore.diff
```

Scratch `/fast/scratch/hyaku/kama-r50/X17Cleanup` removed at the end of the wave.

---

# Findings

## F1 (high, operability) — `w1/out` is unignored, and a run can drop 74 MiB of binaries into it

`kama-shokunin/.gitignore:1-3` ignores only `.ufo/interactive-sessions/`, `.ufo/state/`,
`__pycache__/`. Seat work dirs under `w1/out` are **not** ignored:

```
$ git -C kama-shokunin check-ignore -v .ufo/waves/round-50/w1/out/Sen1Env/runs/V0-baseline/work/download/llama-b11909-bin-ubuntu-x64.tar.gz
rc=1                        # NOT ignored
$ find .ufo/waves/round-50/w1/out -type f -size +1M -printf '%s\n' | awk '{s+=$1;n++} END{printf "files=%d MiB=%.1f\n",n,s/1048576}'
files=22 MiB=74.0           # 21:59:34 (peak)
```

The 22 files at that instant were the 75 MB llama.cpp release tarball, `stories260K.gguf`
(twice) and the `llama-b11909/*.so` set that a run had downloaded into its `work/`.
Transiently worse: at **21:59:29** `du -sh out` = **585 M / 26,799 files**
(`Sen1Env/homescratch`, a full HOME copy built and removed by its run inside a minute).
By **22:01:59** Sen1Env had cleaned up after itself: out = **8.4 M / 607 files**, largest
files `T4Lesson/evidence/sweep-build-tip-tree.out` 1.38 MB and
`R3Provenance/stories260K.gguf` 1.19 MB — so the exposure is a **race window during the
wave, not a permanent payload**. The window is real: `git add -A` at 21:59 would have
committed 585 MB, and the 1.19 MB unignored gguf is still there now.

Command that shows it: `git -C kama-shokunin status --porcelain --untracked-files=all -- .ufo/waves/round-50/w1/out | wc -l` → 313 at 21:58 (all untracked, none ignored).

Proposed fix (full diff in `out/X17Cleanup/proposed-gitignore.diff`, patterns validated
with `git -c core.excludesFile=… check-ignore -v`, which matched the tarball, both ggufs
and `libllama.so.0.7.0`):

```
+.ufo/waves/round-50/w1/out/**/work/
+.ufo/waves/round-50/w1/out/**/*.gguf
+.ufo/waves/round-50/w1/out/**/*.tar.gz
+.ufo/waves/round-50/w1/out/**/llama-b11909/
```

Alternative (L1's call): commit `w1/out` selectively (`*.md`, `*.json`, `*.txt`, `*.out`,
`*.diff`) and never `-A`.

## F2 (high, calibration) — the literal `pgrep -af llama-server` check is not a check

See §1. `pgrep -af llama-server` matches `kama-llamacpp-live.py --server …/llama-server`
and any process carrying `--alias kama-r48-live`. Same class of false positive appeared in
my own first draft of the recheck: the pattern `kama-r4[0-9]` matched every round-50
replay because the live tool is invoked with `--alias kama-r48-live`. Correct forms, both
now in `hygiene-recheck.sh`:

```
pgrep -x llama-server                    # binary only
pgrep -f "$HYAKU/kama-r4[0-9]/"          # earlier-round SCRATCH PATH (trailing slash)
```

## F3 (medium, real leftover inherited by this wave) — round-49 stub servers still hold ports

```
$ ps -o pid,ppid,etimes,args -p 2553430,2608023
2553430  ppid=1494  age=4803s  /usr/bin/python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-k_sicwpn/work-w1/stub.py -m …/m.gguf …/tree/tools/round49-replay-witness-audit.py
2608023  ppid=1494  age=4764s  /usr/bin/python3 /fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-tj8m881o/work-w1/stub.py …
$ readlink /proc/2553430/cwd
/fast/scratch/hyaku/kama-r49/M1Ctr/r49c1-k_sicwpn/tree (deleted)
$ ss -ltnp | grep -E '43591|43151'
127.0.0.1:43591  users:(("python3",pid=2553430,fd=3))
127.0.0.1:43151  users:(("python3",pid=2608023,fd=3))
$ curl -s -m2 -o /dev/null -w '%{http_code}' http://127.0.0.1:43591/health
501
```

Both are **reparented to `systemd --user` (pid 1494)**, their scratch trees are already
deleted, and they still answer HTTP 501 after ~80 min. This is exactly the round-49 R2
failure shape ("a killed counter left … server up") surviving into round 50 — round-49's
counter, not round-50's C1. Two consequences:

1. This seat does not kill other seats' processes; the L1 must decide to `kill 2553430
   2608023` (they can only be reaped by hand — their parent is init-side and their cwd is
   gone).
2. **Any hygiene check that looks only for `ppid==1` misses them.** On a systemd-user
   session an orphan reparents to `systemd --user`, not to pid 1. That exact bug was in
   my first draft (it reported "no orphan" while these two were alive); the shipped
   `hygiene-recheck.sh:64-92` treats `ppid==1 OR parent comm == systemd` as orphan.

## F4 (withdrawn on verification) — the wave-root `X1Assimilation` dir is dispatch-assigned

At 21:54–21:58 `.ufo/waves/round-50/X1Assimilation` was an empty dir at the wave root while
`w1/out/X1Assimilation` held 3 files, and I flagged it as a seat writing in the wrong place.
It is not:

```
$ grep -oE '\.ufo/waves/round-50/[A-Z][A-Za-z0-9]+/' .ufo/waves/round-50/w1/dispatch.json | sort | uniq -c
      2 .ufo/waves/round-50/X1Assimilation/
$ find .ufo/waves/round-50/X1Assimilation -maxdepth 1 -type f | wc -l
7          # 22:00: collision-report.md, guard-proof.md, quarantine-verdicts.md, ids…
```

`w1/dispatch.json` assigns that exact directory to the seat, which then populated it. My
recheck originally mislabelled it (wave-root empty dir → WARN) and then (once populated)
as a lane change outside the wave scaffolding → FAIL; both were my check's fault, not the
seat's. `hygiene-recheck.sh:215-231` now treats `X1Assimilation` as sanctioned and reports
only wave-root dirs the dispatch does not name. **No action for the L1.**

## F5 (low, stray) — `mktemp -d` without `-p $S` at the shared scratch root

Observed at the root of `/fast/scratch/hyaku` (not under any seat dir), 21:55:47–21:56:

```
drwx------ /fast/scratch/hyaku/run-receipt-h00alous        (a git repo: .git/, .ufo/)
drwx------ /fast/scratch/hyaku/run-receipt-home-hv59cndy   (.config/)
drwx------ /fast/scratch/hyaku/run-receipt-jew2ws70        (lane checkout: .git/, .ufo/, .gitignore)
drwx------ /fast/scratch/hyaku/run-receipt-home-mz6pmbp7   (.config/)
```

They are transient (all four were gone by 21:58), consistent with a driver doing
`mktemp -d` against `TMPDIR=/fast/scratch/hyaku` instead of its seat dir. Pre-existing
non-directory strays at the same root, older than this wave and not mine:
`_d.txt` (16:25), `base-census.sh` (04:14), `line137.txt` (15:20), `unblob-tree.json`
(18:51). Not deleted.

## F6 (low/medium, deviation) — several lane clones per seat

Constraint: "One live clone at most (`git clone --shared`)". Counted by
`.git` dirs whose `objects/info/alternates` points at the lane (so fixture repos, which
have no alternates, are excluded):

```
J6Ablation   6 lane-derived repos
J1NoEnv      2   (the second has origin=/fast/scratch/hyaku/kama-r50/J1NoEnv/lane —
                  a clone of its own clone, so it is not even --shared against the lane)
L1           2
X15NoHarm2   2
36 lane-derived repos total across the wave scratch
```

J6Ablation's six are plausibly one per ablation scenario, but the J1NoEnv
clone-of-a-clone is a real extra copy of ~700 MB and is worth a word in the capsule.
No action from this seat.

## F7 (low, evidence hygiene) — seven Sen1Env receipts cite `/tmp`

```
$ grep -rl --exclude=hygiene-recheck.sh '/tmp/' .ufo/waves/round-50/w1/out   # 22:01
Sen1Env/runs/V4-path-python/V4-path-python.json
Sen1Env/runs/V4-path-python/mark-pathpython.txt
Sen1Env/runs/V3-home-pth/V3-home-pth.json
Sen1Env/runs/V3-home-pth/mark-home.txt
Sen1Env/runs/V13-path-curl/V13-path-curl.json
Sen1Env/runs/V13-path-curl/mark-curl.txt
Sen1Env/summary.json
$ grep -n -o '/tmp/[A-Za-z0-9._/-]*' …/V4-path-python.json | head -2
206:/tmp/kama-probe.qgPeOO/m40409.body
206:/tmp/kama-probe.V4L7ir/m40409.body
```

Three arms (V3 home-path, V4 python-path, V13 curl-path) plus `summary.json` record probe
paths under `/tmp/kama-probe.*`. Per the operator directive `/tmp` paths are never
evidence (a reaper deletes idle entries), so those three arms' probe locations cannot be
re-checked after the wave. `X13Threshold.md` also mentions `/tmp` in prose; this report and
`hygiene.md` cite it deliberately as the finding. Everything else in out is `/tmp`-free.

The recheck separates the two cases: a `/tmp` citation in a receipt is a WARN
("never evidence"); in `.md` prose it is reported but treated as a quoted finding.

## F8 (informational) — the lane tip is three commits past the build

```
$ git -C kama-shokunin merge-base --is-ancestor 97c864bead3ee4a2f629574e77263d33834ec98a HEAD; echo $?
0
$ git log --oneline 26ecba64..HEAD
3b79eadd round-50: build regression battery receipts (measure.sh + *-build.out)
3d42897b round-50: build-fix - S498 row markdown tick parity so sources-append-only row parser accepts it
6f3bd322 round-50: wave spec kama-r50-w1 (66 seats), dispatch, validate exit 0, build receipts
97c864be round-50: build - replay isolation + parent-death teardown, live model-mapping record, append-only-audit v5 …
601c8889 round-50: freeze - C1 replay-bind and C2 append-audit-v5 counters, preregistration, base controls, start census, source captures
```

The task framing says the build landed at 97c864b — true, but integration tip is
3b79eadd and there is a **post-build fix commit 3d42897b** (S498 row markdown tick
parity) touching sources, so any source-row claim should name the tip it was measured at.
Lane porcelain never showed a change outside `.ufo/waves/round-50/` — at 21:57:42,
21:58:05 and 22:02 (`PASS` each time), i.e. no seat edited a lane file in place.

## Clean items

- No credential marker (names only, value-bearing patterns) in any of the 607 out files:
  `server.token = <value>`, `ghp_…`, `sk-ant-…`, `ANTHROPIC_API_KEY=<value>`,
  `BEGIN … PRIVATE KEY` → none (22:02). The markers are self-tested so the PASS is not
  vacuous: 6/6 real leak shapes match (`server.token = "…"`, `server.token: …`,
  `server.token='…'`, `ghp_…`, `ANTHROPIC_API_KEY=…`, `-----BEGIN RSA PRIVATE KEY-----`)
  and 4/4 prose shapes are rejected.
- Largest file in out at 22:02 is a 1.38 MB text tree (`T4Lesson/evidence/sweep-build-tip-tree.out`),
  then the 1.19 MB `R3Provenance/stories260K.gguf` (see F1 for why that one should be ignored).
- No orphaned round-50 process older than 300 s (F3's two are round-49).
- No wave process running with `TMPDIR` outside `/fast/scratch/hyaku/kama-r50/*`
  (11/11 checked at 21:57 had a per-seat `TMPDIR`; one transient child, pid 2681419,
  showed `TMPDIR` unset at 21:56:02 and had exited before it could be named).
- `pgrep -x llama-server` from this seat's own working set: none started.

---

## Re-check (for the L1, after the last seat lands)

```
kama-shokunin/.ufo/waves/round-50/w1/out/X17Cleanup/hygiene-recheck.sh --final
```

Ten checks, read-only, exit 1 on any FAIL: wave llama-servers (`pgrep -x`), orphans
(ppid 1 *or* systemd-reparented, age-gated at 300 s so a live teardown experiment's fresh
orphan is not a leftover), earlier-round kama leftovers (scratch-path match), loopback
listeners held by kama pids, fleet porcelain, lane porcelain (containment: no change
outside `.ufo/waves/round-50/`), scratch-root strays, sizes/headroom, out-dir evidence
hygiene (`/tmp` in receipts vs prose, value-bearing credential markers), and wave-root
dirs the dispatch does not name.

Run at 22:03:40 — `RESULT met=True fails=0`, exit 0; WARNs at that instant: 2 round-49
stubs (F3), 2 loopback listeners (same two), 3 scratch-root files (F5), 1 >1 MiB file in
out (F1), 7 `/tmp`-citing receipts (F7). `recheck-snapshot.out` is the verbatim latest run.

Four defects were found *in the check itself* while writing it, all fixed and documented
above because they are the same traps the L1's own gate will hit: `pgrep -af llama-server`
matches argv (F2); `ppid==1`-only orphan detection misses systemd reparenting (F3);
`--alias kama-r48-live` makes a bare `kama-r4[0-9]` pattern match every round-50 process;
and a wave-root dir named by the dispatch is not a stray (F4).
