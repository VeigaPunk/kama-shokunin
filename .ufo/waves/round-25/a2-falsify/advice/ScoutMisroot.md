# ScoutMisroot: write-scope compliance for kama round 25, attempt 2, wave 2

Verdict: **defect found**. The wave pins a tip that is not master, the lane working tree moved under the read-only wave, and the fleet root still carries two stray files with intent-to-add index entries that the lesson's fleet-root sweep does not mention. Everything below is read-only observation; I started no server, made no install, and ran no git or jj writing command.

## What I ran

- `git -C /home/vgpnk/Projects/shokunin status --porcelain` (exit 0), `--porcelain=v2`, `ls-files -s`, `ls-tree HEAD`, `log`, `reflog --date=iso`, `check-ignore -v`, `hash-object` (all exit 0).
- `git -C /home/vgpnk/Projects/shokunin/kama-shokunin` status, `rev-parse HEAD`, `merge-base --is-ancestor`, `log`, `show <rev>:<path>`, `diff`, `ls-files` (all exit 0).
- `find` / `stat` / `grep` / `sha256sum` / `strings` over the fleet root, the lane and `/tmp` (exit 0 except `grep` "no match", exit 1, where noted).
- No `jj` command was run at the fleet root (contract). I read `.jj/working_copy/tree_state` and `.jj/repo/op_heads` mtimes only.
- Disclosure: `git status` can refresh the fleet `.git/index` stat data. The intent-to-add entries below were already present in my first command at 07:11, before any status call of mine could matter.

## D1 (moderate): the pinned tip is not the branch tip, and the working tree keeps changing during wave 2

Observed:

- Wave context says `Lane branch master tip fa3b62ae6475d111eb466d79af616aeebb08bbb9` at `.ufo/waves/round-25/a2-falsify/spec.json:4` and `.ufo/waves/round-25/a2-falsify/dispatch.json:259`.
- `git -C kama-shokunin rev-parse HEAD` -> `46be41cf674301953837c8863cd2026e8a21fcb0`, commit time `2026-10-22T06:57:14-03:00`. The spec file was written at 06:57:04, ten seconds earlier; the commit itself adds the wave harness (`.ufo/waves/round-25/a2-falsify/{spec.json,dispatch.json,advice/swarm-registry.json}` and `report-draft.md`, 4 files, 971 insertions).
- `git merge-base --is-ancestor fa3b62ae HEAD` -> exit 0, so `fa3b62ae` is the last content commit, not the tip.
- At 07:06 `git status --porcelain` showed 4 modified files; at 07:13 it showed 6. New during wave 2: `SCORECARD.md` (mtime 07:13:10, +15 lines, correction paragraph at `SCORECARD.md:1278` citing wave-2 advice `CriticC1AxisFit.md`), `corpus/knowledge/context-capacity.md` (mtime 07:12:11), `corpus/lessons/round-25.md` (mtime 07:13:18). `git diff --numstat` now: `SCORECARD.md 15/0`, `corpus/knowledge/context-capacity.md 88/40`, `corpus/lessons/round-25.md 18/8`, plus the three wave-1 files.
- The lesson bytes differ between tip and working tree: `git show fa3b62ae:corpus/lessons/round-25.md` and `git show HEAD:corpus/lessons/round-25.md` both hash `9d7ec2953b39469b7094ee830c429a5ac7c3a6add72625d77a2e856592476a16` and contain 0 occurrences of `misroot`; the working-tree file at 07:13 hashes `c26728b01de53fb6fe272f98d32ae972df2a211121edf0039144d5b40c73e188` and contains 1 (`corpus/lessons/round-25.md:51`).

Why it matters: the context tells every seat to read absolute working-tree paths (`Read first: .../corpus/lessons/round-25.md`), while the wave-2 reviewers `ReviewerLessonMistakes`, `ReviewerRoutedDefects` and `ReviewerSupersession` judge "as landed" text. They were served bytes that are in neither tip. The wave-2 reporter `ReviewerReportDraft` also reviews `report-draft.md`, which at `HEAD:...:60` still records `fa3b62ae...` as the landing row.

Confidence: observed for hashes, mtimes and the ancestor check; **[INFERENCE]** that no seat was told to prefer `git show` over the working tree (the context text says the opposite).

Smallest correction: in the wave context and the report draft, say "reviewed content tip `fa3b62ae`; master is `46be41cf`, which adds only this wave's harness", and have reviewer seats read `git show fa3b62ae:<path>` where the question is "as landed". If post-dispatch edits are meant to count, commit them before the report is scored, otherwise the falsify findings and the scored bytes are different trees.

## D2 (moderate): two stray files sit at the fleet root, and the fleet index has intent-to-add entries for them

Observed:

- `/home/vgpnk/Projects/shokunin/write` - 25 bytes, mode 100644, mtime `2026-10-21 19:52`, content exactly `'agent://U100N079H334f935b'` (one line, no trailing newline; `grep -c '' write` -> 1).
- `/home/vgpnk/Projects/shokunin/scripts/hyaku/__pycache__/append-closure.cpython-314.pyc` - 10,738 bytes, mtime `2026-10-22 05:01:42`. `strings` shows the hyaku `append-closure` docstring and `/home/vgpnk/Projects/shokunin`; `strings | grep -i kama` -> no match (exit 1). A `.pyc` is written only on import, not on running a script as `__main__`; **[INFERENCE]** some process imported `scripts/hyaku/append-closure.py` without bytecode suppression, inside the fleet repository.
- Both are absent from `HEAD`: `git -C /home/vgpnk/Projects/shokunin ls-tree HEAD -- write scripts/hyaku/__pycache__/append-closure.cpython-314.pyc` prints nothing (exit 0), and `git log --oneline -1 -- write` is empty.
- Yet the index holds them as intent-to-add: `git status --porcelain=v2` gives `1 .A N... 000000 000000 100644 0000...0000... write` (and the same shape for the `.pyc` and `.scratch/goal-20261022-hyaku-12h.md`). `git diff --cached --stat` is empty, and `git ls-files -s` records blob `e69de29b` (the empty blob) for all three, while the real working-tree hashes are `bad9ad9e`, `d4c79e7e` and `2ba39fc3`. Empty blob in the index plus worktree-side ` A` is the intent-to-add state, which only `git add -N` / `git update-index` creates.
- This is not jj's colocated snapshot: the lane `kama-shokunin` is colocated the same way, and its untracked wave-2 files appear as `?` in `--porcelain=v2` (11 of them), not as `.A`. Fleet jj last wrote its working copy at 05:21 (`.jj/working_copy/tree_state`, `.jj/repo/op_heads/heads` mtimes), and `write` (19:52) and the `.pyc` (05:01) both predate that snapshot, so a jj snapshot would have stored real blobs.

Reading: a wrong tool call created `write` by treating the tool name as a path, and an imported module left bytecode in the fleet tree. Neither names kama round 25 (both greps empty), and `write` predates round 25 (`2026-10-21 19:52`, before the attempt-2 window and before `.jj` existed at 00:49). They are pre-existing fleet-root debris that the misroot row at `corpus/lessons/round-25.md:51` does not account for.

Confidence: observed for paths, bytes, hashes and the intent-to-add shape; **[INFERENCE]** that a seat or the orchestrator ran `git add -N` for these paths and that the `.pyc` came from an import (no shell log or transcript names the command; I found no `append-closure` import site in `/tmp` or the lane).

Smallest correction: remove both files and clear their index entries (`git restore --staged write scripts/hyaku/__pycache__/append-closure.cpython-314.pyc` then delete), and ignore `__pycache__/` at the fleet root. Run the hyaku closure helper as `python3 -B scripts/hyaku/append-closure.py` so no bytecode is written.

## D3 (minor): the misroot lesson row cites a section that does not exist

Observed:

- `corpus/lessons/round-25.md:51` cites "`a2-build/advice/ReviewerC1Patch.md` §Mis-write disclosure".
- `grep -n '^#' .ufo/waves/round-25/a2-build/advice/ReviewerC1Patch.md` lists 12 headings; there is no section with that name. The disclosure is a bullet at `ReviewerC1Patch.md:94` under `## Files I wrote`, and the detail it points to is `out/ReviewerC1Patch/evidence.md:73` (section 9), which names `literal-id-checks.py`, `m17-reachability-probe.py` and the three fleet directories removed at 06:45.
- Both files differ between working tree and `HEAD` (mtime 07:02:57 for both, after the 06:57 dispatch), so the bullet moved while the wave read it.

Confidence: observed. Smallest correction: cite `ReviewerC1Patch.md:94` and `evidence.md:73`, or add the named section.

## D4 (minor): the row's "/tmp two seats" count is already stale

Observed, all outside the declared wave scratch `/fast/scratch/hyaku/kama-r25a2w2/<Name>/`:

- `/tmp/mutants-green.json`, 5,959 bytes, mtime 07:05, sha256 `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1` - byte-identical to `a2-build/out/ReviewerC1Patch/full-mutants.json` and to the cited C1 evidence `final/c1/c1-tip-mutants.json` (`cmp` exit 0; same hash for all three).
- `/tmp/x.py`, 6,193 bytes, mtime 07:06:22, sha256 `7bf3f9cd...` - byte-identical to `.ufo/waves/round-25/count-c2.py`.
- `/tmp/__probe_sources_placeholder`, 105,436 bytes, mtime 07:07:05, sha256 `45810d49...` - byte-identical to `corpus/SOURCES.md`.
- The row names only `CriticC1Calibration.md` and `ScribeQualityCriterion.md`; their own disclosures do resolve: `a2-build/advice/CriticC1Calibration.md:79` names `/tmp/ccal-aud-tip.py` (present, 82,288 bytes, 06:33) and `a2-build/advice/ScribeQualityCriterion.md:50-51` names `/tmp/mutants-red.json` (0 bytes, 06:33) and `/tmp/mutants-green.json`.

Reading: three more lane byte copies entered `/tmp` in the same attempt-2 window, at least one of them the C1 evidence file itself, so "two other seats" is not the whole set. I cannot name the writers (no shell log or transcript), and a single script copy is light scratch, so this is a scope deviation, not a claim failure. Note that most kama-named `/tmp` content predates attempt 2 (`/tmp/kama-r25-server.cpp` 24,572 B, `kama-r25-server-context.cpp` 264,205 B, `kama-r25-server-common.cpp` 75,061 B, `kama-r25-fit.cpp` 52,124 B, all 05:29-05:30), and the 145 MB `/tmp/*-r25` clones are clones of `tameshi-shokunin` at `c9ff09f`, not kama; I did not attribute those to kama.

Confidence: observed for bytes, hashes and mtimes; writer identity unknown.

## D5 (positive): the reviewer's own fleet-root cleanup holds

- `find /home/vgpnk/Projects/shokunin -name 'literal-id-checks.py' -o -name 'm17-reachability-probe.py'` returns only the two lane copies under `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/`; no fleet-root copy remains.
- The fleet root has no `.ufo/waves/round-25/a2-build/` directory (`ls .ufo/waves` shows only `aggregator-*`, `arc3-*`, `hyaku`).
- No `.jj` file is newer than 06:40 (`find .jj -type f -newermt '2026-10-22 06:40'` prints nothing), so the 06:45 miswrite was never snapshotted into the fleet repository's own history.

## D6 (positive): the lane index is clean of wave-2 writes

- `git -C kama-shokunin ls-files .ufo/waves/round-25/a2-falsify` lists exactly the three files committed in `46be41cf` (`advice/swarm-registry.json`, `dispatch.json`, `spec.json`). Every wave-2 output is `?` (untracked), not `.A`; no seat staged or committed. Wave-2 advice reports and `out/<Seat>/` files are all inside their sanctioned directories.

## Answer to the assigned question

Untracked fleet files whose content names kama round 25: only `.scratch/goal-20261022-hyaku-12h.md` (17,367 bytes, mtime 2026-10-22 04:54; `kama` at lines 31, 82 and 106, where line 106 is the round-25 lane row). It is the hyaku session goal at the fleet-level `.scratch/` path that seats cite by absolute path, so I read it as an intended orchestrator artifact, not a seat misroot, but it is an untracked fleet-index path and should be declared. `write` and the `.pyc` name no kama round-25 content.

Stray files at the lane: the four `??` entries at wave level (`dispatch-attempts.json`, `dispatched-payload.json`, `spawn-result.txt`, `a2-falsify/out/`) are the orchestrator's dispatch artifacts, outside any seat's `out/<Name>/`; no stray file at the lane root or in `corpus/`. `ScribeQualityCriterion.md` (untracked, 07:05:52) is a wave-1 advice file written after the wave-2 dispatch.

## Remaining unknowns

- Who created `write` (mtime 2026-10-21 19:52, before round 25) and who imported `append-closure` at 05:01:42: no transcript or log names either command.
- Whether the fleet orchestrator's routine closure step is the source of the intent-to-add entries (three new lane `.report-baseline` paths share the same state), and so whether `git add -N` at the fleet root is standing workflow rather than a seat act. Either way the junk paths are in that index and must be dropped.
- Whether wave-2 seats that read `corpus/lessons/round-25.md` before 07:06 saw the same bytes I did at 07:13; the file changed twice in that window.

## Files I wrote

- This report: `.ufo/waves/round-25/a2-falsify/advice/ScoutMisroot.md`
- Raw captures: `.ufo/waves/round-25/a2-falsify/out/ScoutMisroot/raw-captures.txt`

No tool was installed or upgraded. No llama-server child was started. No git index, commit, or jj state was written by me.
