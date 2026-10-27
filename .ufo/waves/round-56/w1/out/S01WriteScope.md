# S01WriteScope — write-scope and lane-state audit, round 56 w1

Seat: `S01WriteScope` (sentinel, operability). Milestone: round-56 falsification.
Audit window: 2026-10-27 13:05:40–13:10:30 -0300 (16:05:40–16:10:30Z), seats live throughout.
Lane (read-only): `/home/vgpnk/Projects/shokunin/kama-shokunin`; `git rev-parse --show-toplevel` → `/home/vgpnk/Projects/shokunin/kama-shokunin` (exit 0).
Frozen tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (`master`); working copy `@` = `0f65f84856f3` (`kmokrynx`, no description). Wave dispatch at 13:04:53 (`w1/dispatch.json`, mtime 13:04:53.947).

## Verdict

- **No seat wrote or modified lane content outside its own `.ufo/waves/round-56/w1/out/<Seat>/` or `out/<Seat>.md`** in the audit window.
- **Two seat-attributable side effects did land outside `out/`**, both metadata-only:
  1. `.git/index` rewritten at **13:07:58** by seat `git status`/`git diff` run inside the lane tree (~30 such calls; F1).
  2. One jj operation appended to lane `.jj` state — `snapshot working copy`, args `jj diff --summary`, op `f13c8cf251eb`, triggered by `X06Census` at 13:07:12 (F2).
- **All frozen surfaces are intact**: every file named by the preregistration plus all six receipts is byte-identical to the freeze commit; the wave manifest taken at 13:07:36 and again at 13:09:51 differs only in the orchestrator-owned `w1.ready.partial`.

## Method

1. Lane state: `jj status`, `jj diff --stat`, `jj --ignore-working-copy diff --summary`, `jj --ignore-working-copy file list`, `jj op log`, `git ls-tree -r 9244137892bf`.
2. Frozen-byte check: `sha256sum` of the four `tools/round56-*` files, `corpus/SOURCES.md`, `.ufo/waves/round-56/preregistration.json`, `controls/base-c1.out`, `controls/base-c2.out`, each compared with `git cat-file -p efc6b3ec:./<path> | sha256sum`.
3. Manifests of all non-`out/` wave files at three instants (13:07:36, 13:08:44, 13:09:51); copies in `out/S01WriteScope/manifest-{before,after,final}.sha256`.
4. Time-ordered sweep of the whole lane, `find . -path ./.jj -prune -o -path ./.git -prune -o -newermt '2026-10-27 13:04:53'`, repeated at the close of the window.
5. Escape checks: `find .ufo/waves/round-56 -type l` (empty — no symlink write-through), `find . -maxdepth 1 -newermt …` for stray lane-root files, `lsof +D` for live handles (none), `/fast/scratch/hyaku/kama-r56/` inventory, `/tmp` diff, `~/.local/bin` mtimes.
6. Attribution: parsed the 64 seat transcripts at `~/.omp/agent/sessions/-Projects-shokunin/2026-10-27T07-52-07-309Z_01a17c58-598d-7507-a58f-62bb501eed98/<Seat>.jsonl`, extracting every `write`/`edit` target and every `bash` command that mentions the lane; 135 unique lane-touching git/jj invocations are listed with timestamps in `out/S01WriteScope/seat-lane-vcs-calls.tsv`.

## Findings

### F1 — MEDIUM — seats rewrite lane `.git/index` (bound: "never mutate lane jj state/index")

`stat -c '%y %n' .git/index` → `2026-10-27 13:07:58.235234940 -0300 .git/index` (3989168 bytes), i.e. the index was rewritten 3 min into the wave. The lane-cwd git reads that can do this, with transcript timestamps (UTC), are a set of about thirty calls including:

- `S03SecretScan` 16:06:15 `git status --porcelain`; 16:06:21 `git status --porcelain --untracked-files=all -- . ':!.ufo/waves/round-56…'`
- `X03CleanEnv` 16:06:36 `git rev-parse --show-toplevel; git rev-parse HEAD; git status --porcelain…`
- `V01RouteDefects` 16:06:44 `git status --porcelain | wc -l`; 16:07:48 `git status --porcelain | grep -vE 'round-55/w1/out'`; 16:07:56 `git diff -- SCORECARD.md`
- `V04LateOutputs` 16:06:54, 16:07:22, 16:07:48, 16:08:17 (`git status --porcelain=v1 …`, `git diff --cached`)
- `K06NoHarm` 16:07:04 `git status --short`
- `X06Census` 16:07:12 `git status --porcelain corpus/SOURCES.md`; 16:08:14 `git status --porcelain .ufo/waves/round-56/`
- `V03ScorecardDrift` 16:07:14, 16:08:09, 16:08:17, 16:09:52
- `X02ReplayC2` 16:07:22 `git status --porcelain`
- `S03SecretScan` 16:08:14 `git status --porcelain --untracked-files=all -- .ufo/waves/round-56/w1/out/S03SecretScan …`
- `S04Policy` 16:06:46, 16:08:49, 16:09:06; `W02ReportSkeleton` 16:09:04, 16:09:55; `W03TrendReview` 16:09:39; `W04LogScorecard` 16:09:49, 16:09:55; `X05ControlSeparation` 16:09:35, 16:09:46

Exploit path: `git status`/`git diff` refresh the index stat cache; nothing more happened because no seat ran `git add|commit|reset|checkout|apply|stash`. A single `git add`/`git commit` in-lane by any of these seats would stage wave outputs into the lane, which the bounds forbid. Impact observed: index bytes (mtime/size) only; no tracked content, no `refs`, `master` still `efc6b3ec`.

Smallest remediation: one wave-policy line — lane VCS reads only via `jj --ignore-working-copy` or a scratch clone (`git clone --local` into `/fast/scratch/hyaku/kama-r56/<Seat>/`); no `git` invocation with the lane as cwd.

### F2 — MEDIUM — `X06Census` appended a lane jj operation

`jj op log` entry: `f13c8cf251eb … snapshot working copy`, `args: jj diff --summary`, executed 13:07:12 from `cd /home/vgpnk/Projects/shokunin/kama-shokunin && git status --porcelain corpus/SOURCES.md; echo "--- jj file list diff ---"; jj diff --summary 2>/dev/null | head -20; …` (`X06Census.jsonl`, 16:07:12.465Z). This is a lane jj state mutation, forbidden by the seat bounds.

Impact bounded: jj's auto-track does not adopt these files (verified `jj --ignore-working-copy diff --summary` returns no `A` entries and `jj --ignore-working-copy file list 'corpus/lessons/round-56.md'` → "No matching entries"), so the working-copy commit's tracked set is unchanged; the op is a snapshot record plus a new working-copy commit id (`221337955009` → …). No bookmark moved: `jj log -r master` = `efc6b3ec`.

Disclosure: this auditor also caused snapshot ops before switching to `--ignore-working-copy` (`jj status`, `jj diff --stat` at 13:06:13–13:06:23); after that point every read used `--ignore-working-copy`.

Smallest remediation: replace `jj diff --summary` with `jj --ignore-working-copy diff --summary` in seat prompts, and forbid `jj`/`git` in lane cwd entirely.

### F3 — LOW — `out/S03SecretScan` file/directory collision (self-resolved)

At 13:06:21 the path `.ufo/waves/round-56/w1/out/S03SecretScan` existed as a **0-byte regular file**, mode `-rw-------`: `ls -la …/out/` printed `-rw------- 1 vgpnk vgpnk 0 Oct 27 13:06 S03SecretScan`. By 13:06:40 the same path was a directory with mtime 13:06:21.0097218530 (`find … -printf '%y %s %TH:%TM:%TS %p'`). The seat's deliverables now sit correctly: `out/S03SecretScan/` (3 files: gitleaks JSON reports) and `out/S03SecretScan.md` (10532 B, 13:08:11).

Impact: transient; while the file occupied the name the seat could not create its evidence directory. Cause: an unescaped `>` redirect to a bare `out/<Seat>` path. Smallest remediation: `install -d` the seat dir first and treat the bare `out/<Seat>` path as forbidden; only `out/<Seat>/` and `out/<Seat>.md` exist.

### F4 — LOW — seat writes to `/tmp` (bound: "Never use /tmp for evidence")

`X03CleanEnv` (16:09:03–16:09:08Z): `/tmp/x` was created as a **directory** (`rm -f /tmp/x` → `rm: cannot remove '/tmp/x': Is a directory`), and `/tmp/x.out`, `/tmp/gs.out`, `/tmp/gc.out` exist with mtime 13:09 (221/884/549 B). Its own transcript records the defect: "Section A rev-parse lines are broken by my stray `/tmp/x` redirect (… the omp shell wrapper likely created a directory?)".

Also `S02Scratch`'s TMPDIR-unset probes created `/tmp/r53c1-3bikq1pb` and `/tmp/r53c1-uaepock3` (0700); both were gone at audit close (`ls -d /tmp/r53c1*` → none), so the counter cleans up.

Impact: host-global residue, no lane effect. Smallest remediation: probe under `$TMPDIR` (seat scratch) and export `TMPDIR` for every child process.

### F5 — MEDIUM (claim integrity) — two C1 counter files carry no frozen digest

`preregistration.json` freezes `counter_sha256` for `tools/round56-replay-code-audit.py` = `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` and `C2.counter_sha256` for `tools/round56-prereg-check.py` = `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`. But C1's stated counter is `tools/round56-env-leg-test.py + tools/round56-replay-code-audit.py`, and C1's kill condition depends on `tools/round56-env-leg-battery.py`'s expected-detected assertion. Neither of the latter two has a digest in the preregistration:

- `tools/round56-env-leg-test.py` = `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` (1279 B)
- `tools/round56-env-leg-battery.py` = `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` (2418 B)

Exploit path: changing the battery's `expected` field for the round56 counter (or the harness's child setup) changes C1's outcome while every frozen digest still matches; C2's checker reads the battery roster, so a coordinated roster+preregistration edit is the only tripwire, and the checker itself is frozen against that. No drift occurred: both files are byte-identical to `efc6b3ec`.

Smallest remediation: add both digests to `preregistration.json` (and quote them in the round-56 report) before scoring; the predicate already names the files, so this only makes the existing claim checkable.

### F6 — LOW (operability, substrate) — counter scratch silently falls back to `/tmp`

`S02Scratch` strace evidence (receipts `out/S02Scratch/mkdir2.trace.txt`, `mkdir3.trace.txt`): with `TMPDIR` unset, running `python3 tools/round56-replay-code-audit.py --repo /nonexistent-repo --tip HEAD` from the lane produced

```
1897616 mkdir("/tmp", 0777)             = -1 EEXIST (File exists)
1897616 mkdir("/tmp/r53c1-uaepock3", 0700) = 0
1897620 +++ exited with 128 +++
```

and at 13:07:18 `mkdir("/tmp/r53c1-3bikq1pb", 0700) = 0`. The preregistration's limits and the seat spec both say "set TMPDIR explicitly", but the tool neither requires nor reports it: a seat that forgets gets `/tmp` with 0700 and no warning. Smallest remediation: the counter exits non-zero when `TMPDIR` is unset or resolves outside an allowlisted root.

### F7 — INFO — L1 wrote lane production files mid-wave (not a seat violation)

Post-dispatch writes outside `out/`, complete list from the sweep:

| mtime | path | actor / evidence |
|---|---|---|
| 13:04:53 | `.ufo/waves/round-56/w1/` + `w1/dispatch.json` | orchestrator (`build_spec.py` emission) |
| 13:04:57 | `.ufo/waves/round-56/w1.ready` | orchestrator |
| 13:06:06 | `corpus/lessons/` (dir mtime) | L1 |
| 13:06:24 | `corpus/lessons/round-56.md` (4816 B, untracked) | L1 — `KamaR56.jsonl`: `write(/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/lessons/round-56.md) ⇒ ok`, then two `edit` calls on the same file |
| 13:07:27 | `SCORECARD.md` (367428 B) | L1 — `KamaR56.jsonl` edits at `SCORECARD.md#4A47` (line 16) and `#1F74` (line 6); `jj diff --stat -- SCORECARD.md` → `1 file changed, 3 insertions(+), 3 deletions(-)`; worktree sha256 `1bddff00…` vs freeze blob `50c594f5…` |
| 13:07:40, 13:08:08, 13:09:51 | `.ufo/waves/round-56/w1.ready.partial` | orchestrator liveness roster |
| 13:10:32 | `.ufo/waves/round-56/w1.ready.dispatched` | orchestrator |

Neither `corpus/lessons/round-56.md` nor the `SCORECARD.md` state is in the freeze commit: `git ls-tree -r 9244137892bf --name-only | grep -E 'lessons/round-56|SCORECARD'` returns nothing for either, and `jj --ignore-working-copy file list 'corpus/lessons/round-56.md'` → "No matching entries".

Operability consequence (not a bounds breach by a seat): seats auditing these surfaces read a moving target. `R12SCORECARD` (13:06–13:08), `V03ScorecardDrift` (13:07:14, 13:08:09, 13:09:52), `W03TrendReview`/`W04LogScorecard` (13:09:39–13:10:15) all diffed `SCORECARD.md` during or after the L1 edit, and `K07SourceScope`, `V02StaleLesson`, `S03SecretScan`, `X07Anchors`, `W01LessonReview` read `corpus/lessons/round-56.md` at points 13:07–13:10 while the L1 was still editing it. Any two of those reports may print different lesson/scorecard bytes. Smallest remediation: L1 states the `git hash-object`/sha256 of the SCORECARD and lesson bytes the wave is to cite, or defers those edits until after the wave closes.

### F8 — INFO — shared namespace at `out/` root, no per-seat isolation

`out/` root holds the orchestrator's `swarm-registry.json` (52626 B, mtime 13:04:39, unchanged through the window) next to 64 seats' `out/<Seat>/` and `out/<Seat>.md`. Directory mode is 755 and files 644 (same UID), so nothing prevents a seat with a wrong path from writing a sibling's evidence or the registry. No cross-seat write was observed: every written path in the window resolved inside the writing seat's own root, and `find .ufo/waves/round-56 -type l` is empty (no symlink write-through). Smallest remediation: `chmod 700` each seat dir in the dispatcher, or move `swarm-registry.json` out of the seat write root.

## Certifications (each checked, all negative for seat writes)

1. **Frozen bytes vs freeze commit `efc6b3ec`** — identical for all six, plus both committed receipts:

   | file | sha256 |
   |---|---|
   | `tools/round56-replay-code-audit.py` | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` |
   | `tools/round56-prereg-check.py` | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` |
   | `tools/round56-env-leg-test.py` | `ec7a2519f6d4b2e1bd08a7ead042a53c7b60e2f58af8e4db008dfd661acf82ac` |
   | `tools/round56-env-leg-battery.py` | `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` |
   | `corpus/SOURCES.md` | worktree = `efc6b3ec` blob (`jj diff --stat -- corpus/SOURCES.md` → `0 files changed`) |
   | `.ufo/waves/round-56/preregistration.json` | `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68` (= manifest, stable across window) |
   | `controls/base-c1.out` | `48a6f7457a8d015ed52c0a1f9877fa8548d393b8f87f442f7d4c08687eabacec` |
   | `controls/base-c2.out` | `13d5516a3b391ef1175b975c0ffa5fa3adc235c1ddc8565252f62bb0ecb9d9fc` |

   Command: `for f in <files>; do wt=$(sha256sum "$f"|cut -d' ' -f1); hd=$(git cat-file -p "efc6b3ec:./$f"|sha256sum|cut -d' ' -f1); [ "$wt" = "$hd" ] && echo "OK $f" || echo "DRIFT $f"; done` → eight `OK` lines, exit 0.

2. **Wave manifest stability** — `manifest-before.sha256` (13:07:36) vs `manifest-final.sha256` (13:09:51) differ on exactly one line: `w1.ready.partial` (orchestrator liveness). `controls/`, `measured/`, `census/`, `sources/`, `preregistration.json`, `w1/{spec,dispatch,validate}.out` unchanged. Receipt hashes: `measured/base-c1.out` `ece98c2f…`, `measured/build-c1.out` `1aea0d27…`, `measured/build-c2.out` `01d95f52…`, `measured/m-drop-ldaudit.out` `93813bd7…`.

3. **No symlinks under the wave tree** — `find .ufo/waves/round-56 -type l -printf '%p -> %l\n'` → empty; no write-through escape from `out/`.

4. **No post-dispatch writes to frozen receipt dirs** — `find .ufo/waves/round-56 -path '…/w1/out' -prune -o -newermt '2026-10-27 13:04:53' -print` returns only the orchestrator files and the two L1 production files (F7).

5. **No kama-seat writes in the fleet root or sibling lanes** — `find /home/vgpnk/Projects/shokunin -maxdepth 3 -newermt '2026-10-27 12:55'` outside the lane yields only `kotoba-shokunin/`, `kumitate-shokunin/`, `mado-shokunin/`, `revenger-shokunin/`, `tabi-shokunin/` files (those lanes' own agents) and host artefacts `.ufo/state/disk-guard.log`, `.ufo/state/inline-dispatcher.log`, `.ufo/watchdog.log`, `.ufo/reports/round-53/`, `.ufo/prompts/closure/`. `/home/vgpnk/Projects/shokuknow` → no file newer than 12:55.

6. **No PATH-dir or package-manager activity** — `find ~/.local/bin -maxdepth 1 -newermt '2026-10-27 12:00'` → empty; no `pacman` invocation in any of the 64 seat transcripts (matches the host-wide pause).

7. **No seat-written bytecode in the lane** — `tools/__pycache__/round56-replay-code-audit.cpython-314.pyc` is the only round-56 cache and carries mtime 13:03:27 (L1's pre-dispatch run). Seats that imported the counter did so in scratch or with `PYTHONDONTWRITEBYTECODE=1` (`X05ControlSeparation` sets it explicitly). Residual risk: an import without that flag writes `tools/__pycache__/` — outside the seat's out dir.

8. **Scratch hygiene** — `/fast/scratch/hyaku/kama-r56/` contains per-seat directories only; `S02Scratch`, `X02ReplayC2`, `X07Anchors` removed their scratch before yielding (`rm -rf …/S02Scratch` at 13:09:09, `rm -rf …/X02ReplayC2` at 13:07:22, `rm -rf …/X07Anchors` at 13:08:02). No `scratch`/`tmp`/`work`/`proof` directory exists anywhere under the lane.

9. **No destructive VCS verbs by seats** — across all 64 transcripts the only git verbs are `rev-parse`, `log`, `status`, `diff`, `show`, `ls-files`, `ls-tree`, `hash-object`, `cat-file`, `for-each-ref`, `grep`, `clone --local/--no-hardlinks` into scratch, and `git init`/`add`/`commit` inside scratch fixtures; no `git add|commit|reset|checkout|apply|stash|clean` with the lane as `-C`/cwd, and no `jj` verb other than reads plus the one snapshot in F2.

## Remediation, smallest first

1. Wave policy line: lane VCS inspection via `jj --ignore-working-copy` or a scratch clone; no `git`/`jj` with the lane as cwd (kills F1, F2).
2. Add `tools/round56-env-leg-test.py` and `tools/round56-env-leg-battery.py` digests to `preregistration.json` (F5).
3. Dispatcher/prompt: `install -d out/<Seat>` before any write, never redirect onto `out/<Seat>` (F3); `chmod 700` seat dirs (F8).
4. Counter guard: refuse to run when `TMPDIR` is unset or outside the allowlisted scratch root (F6); audit-side, forbid `/tmp` in seat probes (F4).
5. L1 pins the sha256 of the SCORECARD and lesson bytes the wave cites (F7).

## Limits

- Point-in-time audit with live seats; the window closes at 13:10:30 and later writes are not covered.
- Attribution uses agent transcripts plus filesystem metadata, not kernel audit records; a write performed through a path that never appears in the writing seat's transcript would be missed.
- `jj` snapshot ops produced by this auditor's own reads (13:06:13–13:06:23) are disclosed in F2 and excluded from the seat attribution; from 13:06:40 onward all lane jj reads used `--ignore-working-copy`.
- The frozen-byte certification covers the files named by the preregistration and the receipt dir; it does not certify that the receipts' contents are semantically correct — that is C1/C2's subject, not this seat's.
