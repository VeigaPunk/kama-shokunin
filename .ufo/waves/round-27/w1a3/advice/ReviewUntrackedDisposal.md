VERDICT: holds — the attempt-2 w1-controls untracked tree is fully out of the lane (porcelain empty even with `--ignored`), nothing committed at 324d5d62 cites `w1-controls/advice` or `w1-controls/out` file contents as evidence, and the scratch dir holds 1846 regular files; the only blemish is the committed "1853 paths" figure matching neither 1846 files nor 2257 total paths.

# Scope
Claim served: inherited-state handling — attempt-2 untracked files (lesson header, `corpus/lessons/round-27.md:6-9`) moved out of the lane to `/fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/` (1853 paths claimed). I verified the three named checks only; I did not open any moved file's contents (instruction honored — filenames, mtimes and sizes only). Lane tip confirmed `git rev-parse HEAD` = `324d5d62e61276af312c8eb42f678004aec245d1`. Full transcript: `.ufo/waves/round-27/w1a3/out/ReviewUntrackedDisposal/commands.txt`.

# Findings

## LOW — committed count "1853 paths" does not match the observable scratch tree (accuracy defect, not a disposal defect)
`corpus/lessons/round-27.md:6` (committed at 324d5d62): "their uncommitted lane files (1853 paths under `.ufo/waves/round-27/w1-controls/advice/` and `out/`) were moved unread".
- `/usr/bin/find <scratch> -type f | wc -l` → **1846**; `-type d` → 411; `-mindepth 1` total paths → 2257. No reading of "paths" yields 1853 (files 1846; paths 2257; files+topdirs 1848).
- Post-move deletion is contradicted: 0 files with mtime after the 06:19:06Z orchestrator death; 0 directories modified after the move completed (~06:50:56Z, scratch-root mtime). The tree is untouched since the move.
- No mover manifest exists (scratch top level holds only `advice/` and `out/`; committed tree records no move log). [INFERENCE] 1853 was most likely a lane-side count taken before the move (repo-wide `git status --porcelain -uall`, or a pre-move `find` that still saw files later deleted during the 06:16–06:38Z ENOSPC/runaway cleanup). The parenthetical's scope ("under …/advice/ and out/") is what makes the sentence inaccurate.
- Impact: none on the claim's function — the files are out and uncited — but a reader recounting gets 1846, not 1853.

## No findings on the other two checks
- **Lane cleanliness:** `git --no-optional-locks status --porcelain[ --ignored] -- .ufo/waves/round-27/w1-controls/` → empty (exit 0). On disk the dir holds only the 6 committed metadata files (`git ls-tree` → 6). Supplementary, out of scope: the whole `round-27/` tree shows only `?? w1a3/` — this wave's sanctioned output dirs.
- **No committed evidence citations:** `git grep -l -E 'w1-controls/(advice|out)' 324d5d62` → 5 files (`dispatch.json`, `dispatched-payload.json`, `spec.json`, `spawn-result.txt`, `lessons/round-27.md`). Enumerating all 333 distinct matched path strings (`git grep -o`): every hit is a report/out **destination** declared to the dead seats inside committed dispatch metadata (`reportDir`, `Report:` trailer, `out/<SeatName>/` instructions, `advice/swarm-registry.json` path field) or the lesson's own disposal note. None references moved *contents* as evidence. `git grep 'w1-controls'` over `corpus/`, `a3/`, `repairs/` adds only two dir-name mentions (`a3/plan.json:8` "untrusted scratch"; `echo-discriminating-counters.md:64` history). A bare seat-name probe found no content citation outside those files.

## Consistency evidence for "moved" (not "copied-and-kept")
`advice/` and `out/` are absent from the lane dir; scratch mtimes line up with the timeline (out 06:10Z, advice 06:14Z, root 06:50:56Z ≈ move end; death 06:19:06Z). 24 files under `advice/` (23 seat reports + `swarm-registry.json`) and 25 seat dirs under `out/` vs 37 dispatched seats — the shortfall matches seats dying mid-run, not a partial move. No `sitecustomize*`/`.pyc` remnants; largest file 1.49 MB; the 262 GiB runaway (`.ufo/waves/round-27/a3/mistake-runaway/REMOVED-RUNAWAY.txt`, truncated 06:38:29Z) is not inside this scratch tree.

# Residual risk / verification gaps
- "Moved **unread**" is inherently unverifiable by me; I checked mtimes/citations only, never contents (and was instructed not to read them).
- I cannot exclude that other untracked attempt-2 files existed *outside* `w1-controls/` and were disposed elsewhere or remain; the claim and this item are scoped to `w1-controls/`. (Repo-wide porcelain beyond `round-27/` was not audited.)
- Directory mtimes prove no top-level churn since 06:50:56Z but file-level deletions inside pre-existing subdirs between move-end and now cannot be fully excluded by mtime alone; there is no independent manifest to diff against.
- The scratch path is declared untrusted by the round contract; this review only confirms the boundary was respected in committed files at the tip commit — it says nothing about scratch content.

# Commands (all read-only; exit 0 unless noted)
```
git rev-parse HEAD                                    → 324d5d62e61276af312c8eb42f678004aec245d1
git --no-optional-locks status --porcelain -- .ufo/waves/round-27/w1-controls/          → (empty)
git --no-optional-locks status --porcelain --ignored -- .ufo/waves/round-27/w1-controls/ → (empty)
git grep -l -E 'w1-controls/(advice|out)' 324d5d62…   → dispatch.json, dispatched-payload.json, spawn-result.txt, spec.json, lessons/round-27.md
git grep -o -E 'w1-controls/(advice|out)[A-Za-z0-9_./-]*' 324d5d62… | sort|uniq -c      → 333 hits, all destination strings + disposal note
/usr/bin/find /fast/scratch/hyaku/kama-r27/attempt2-untracked-w1-scratch/ -type f | wc -l → 1846
/usr/bin/find … -mindepth 1 -type d | wc -l → 411;  … -mindepth 1 | wc -l → 2257
/usr/bin/find … -type f -newermt '2026-10-23 06:19:06 +0000' | wc -l → 0
/usr/bin/find … -type d -newermt '2026-10-23 06:51:00 +0000' | wc -l → 0
```

Tooling directive: no installs or updates were performed or needed; all tools used (git, find, du, stat, ls) were already present.
