VERDICT: partial — write/VCS discipline holds: no pycache, no round-16 rewrite, and no stray file outside the declared set. One lesson sentence overclaims the frozen-copy scope.

Seat: KamaR17.SentinelWaveDiscipline (sentinel, read-only). Attacked: the file list of landed commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3` (cff9e62..54a2926) checked against `corpus/lessons/round-17.md`; lane working-tree writes since round start; committed and jj-snapshotted `__pycache__`/`.pyc`; `.ufo/waves/round-16` rewrites; frozen-copy integrity.

## Findings

### F1 — LOW (documentation overclaim): the frozen set covers 5 files, but the commit changes 21 tracked files outside round-17
- Evidence: `corpus/lessons/round-17.md:9` — "Pre-round copies of every file this round changes are frozen byte-for-byte in `.ufo/waves/round-17/frozen/`". `frozen/manifest.json` lists only 5 sources: round-13 `measure.py`, `check-receipt.py`, `check.py`, `kama-llamacpp-live.py`, `kama-probe.sh`. `git diff --numstat cff9e62 54a2926 -- . ':!.ufo/waves/round-17'` lists 21 paths. Of these, 16 are modified or new tracked files with no frozen copy: `.gitignore`, `AGENTS.md`, `LOG.md`, `PROVINCE.md`, `SCORECARD.md`, `SHONEN.md`, `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, three `corpus/knowledge/*.md`, and new `controls.py`, `fault-controls.py`, `sources-append-only.py`, `round-17.md`. `kama-probe.sh` is frozen but was not changed (it is the no-harm pin).
- Impact: none on any measurement. The frozen arms need only the 4 code files, and all 5 hashes match `git show cff9e62:<path>` (below). The sentence is still literally false, and a reader might take the frozen directory as a complete pre-round snapshot. Every omitted file can be recovered with `git show cff9e62:<path>`.
- Smallest remediation: append a correction that scopes the sentence: "every measured tool/gate this round changes (plus the probe pin)". Or point to `cff9e62` as the pre-round tree for the rest.

### F2 — INFO: lesson citations without a path base
- Evidence: `round-17.md:5` cites `.ufo/watchdog.log`, `:129` cites `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md`, `JjTrialKama.md`, and `:85` cites `CORPUS.md`. None exists under the lane (`os.path.exists` False); all exist at the fleet root `/home/vgpnk/Projects/shokunin/`. `grep -n 'lane-dead-no-report kama round=17' /home/vgpnk/Projects/shokunin/.ufo/watchdog.log` gives exit 1, which confirms the lesson's "nothing was inherited". Every other lane path cited in the lesson and in SCORECARD §Round 17 resolves in the tip tree.
- Remediation: prefix fleet-root cites (e.g. `<fleet>/.ufo/watchdog.log`).

## Invariants checked (all hold)
- **No `__pycache__`/`.pyc` committed.** `git ls-tree -r --name-only 54a2926 | grep -nE 'pycache|\.pyc$'` → no output, exit 1. The same scan over all 22 `refs/jj/keep/*` commits, including the nine empty-description jj working-copy snapshots, gives `pyc=0` for every one. No snapshot contains a file that is absent from the tip (`git diff --diff-filter=A 54a2926 <snap>` is empty for each), so no seat scratch ever entered a jj commit. Working tree: `find` for `__pycache__`/`*.pyc` (pruning `.git`, `.jj`, `interactive-sessions`) → nothing.
- **`.gitignore` matches the lesson.** Diff adds exactly `.ufo/state/` and `__pycache__/`, as `round-17.md:89,136-137` states. `git ls-tree` finds 0 `.ufo/state/` entries.
- **Round 16 untouched.** `git diff --name-status cff9e62 54a2926 -- .ufo/waves/round-16` → empty (exit 0). `git status` shows no working-tree change there. So no `run-*.json` was rewritten, which agrees with `round-17.md:144-148` (round-16 `measure.py` run only in a `/tmp` clone).
- **Probe and matrix byte-identical.** `git diff --name-only cff9e62 54a2926 -- tests/probe-verdicts tools/kama-probe.sh` lists only `check.py` and `fault-controls.py`. The 9 matrix `*.json` and the probe are unchanged, as `round-17.md:30` claims.
- **Frozen copies are true pre-round bytes.** `git show cff9e62:<p> | sha256sum` for all 5 sources equals both `manifest.json` and `sha256sum frozen/*` (2399d64d…, 6b9576a1…, b853576e…, b8c5e8d4…, 36b64978…).
- **No seat-written file outside `.ufo/waves/round-17/` in the lane.** I listed every file modified since round start (`find -newermt 2026-10-20T11:50:45-03:00`, pruned) outside round-17. The result is exactly the 21 committed paths, and `git status --porcelain` shows none of them dirty. Untracked files are only under `.ufo/waves/round-17/falsify/` (wave dispatch files). Ignored non-`.jj` files are `registry/history/.lock` and two `20261014T*.json`, with mtime 2026-10-14, so they predate the round. At the fleet root, the only top-level file newer than round start is `MANIFEST.json` (fleet-managed). I found no misrooted round-17 file at depth 1.
- **Branch state.** `refs/heads/master` = `refs/remotes/origin/master` = `54a2926`, so the commit is pushed.
- **Single commit.** `git log cff9e62..54a2926` contains one commit. All `.ufo/waves/round-17/**` entries in it are wave artefacts. The largest is vendored upstream llama.cpp source, `.ufo/waves/round-17/sources/llama.cpp-704366d76/` (≈477 KB, 6 files), pinned by `sources/pins.json`. I did not judge it.

## Commands (cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`, read-only git; exit codes)
- `git log --oneline cff9e62..54a2926` → 0; `git diff --name-status cff9e62 54a2926` → 0
- `git ls-tree -r --name-only 54a2926 | grep -nE 'pycache|\.pyc$'` → 1 (no match)
- `git diff --name-status cff9e62 54a2926 -- .ufo/waves/round-16` → 0, empty
- `git diff cff9e62 54a2926 -- .gitignore` → 0
- `git status --porcelain=v1 --ignored --untracked-files=all -- . ':!.ufo/interactive-sessions'` → 0
- `find . \( -path ./.ufo/interactive-sessions -o -path ./.git -o -path ./.jj \) -prune -o -type f -newermt <cff9e62 %cI> -print` → 0; same prune with `-name __pycache__ -o -name '*.pyc'` → 0, empty
- `git show cff9e62:<p> | sha256sum` ×5; `sha256sum .ufo/waves/round-17/frozen/*` → 0
- `git for-each-ref`; per `refs/jj/keep/*`: `git ls-tree -r` pyc count, `git diff --diff-filter=A/M 54a2926 <c>` → 0
- `git diff --numstat cff9e62 54a2926 -- . ':!.ufo/waves/round-17'` → 0
- A Python path-existence check of backticked paths in `round-17.md` and SCORECARD §Round 17 (read-only). `ls -la` and `grep` on the fleet-root `.ufo/watchdog.log` (grep exit 1). `find /home/vgpnk/Projects/shokunin -maxdepth 1 -type f -newermt …` → 0

## Limitations
- I could not inspect jj operation-log contents beyond the git-visible `refs/jj/keep` commits (no `jj` allowed). A file written and deleted between jj snapshots without any jj command running would be invisible to me. [INFERENCE] Such a file would also never have been committed.
- The mtime sweep cannot see a file whose mtime was restored, or a write that was later reverted byte-for-byte.
- The fleet-root check covered depth 1 only. Deeper misroots belong to the MisrootSweep seat.
- I ran no lane tools, so I needed no clone. I created no scratch under `/tmp` and left nothing to remove.

## Installs
None.
