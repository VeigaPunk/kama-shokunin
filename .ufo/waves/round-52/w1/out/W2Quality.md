# W2Quality — round-52 QUALITY.md rows: ten remaining citation rows drafted, five defects found in the rows that landed while I scanned

Verdict: the ten KQ rows with no lesson-file citation (KQ39, KQ41, KQ42, KQ45, KQ47, KQ80–KQ84)
have an identified lesson and a drafted supersession each; the four rows this seat was asked to
draft for (KQ86/KQ87 supersessions, the C1 and C2 criteria) were already landed **uncommitted** in
`corpus/QUALITY.md` by a concurrent integration during this seat, and three of those five landed
rows cite lesson sections that do not exist (`round-52.md` Errata D7, `round-52.md` Mistakes) or
drop legs the frozen counter checks (KQ91) or limits the preregistration names (KQ92).

Axis moved: calibration (7) only. No counter was run by this seat (not in this seat's scope); every
`met=True` quoted below is read from the L1's receipts at the build.

## 1. State I measured

```
$ git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
34d8260051bbab8859485e8209fcf4be19dc9a2b
$ git -C … status --porcelain corpus/QUALITY.md
 M corpus/QUALITY.md
$ git -C … diff --stat corpus/QUALITY.md
 corpus/QUALITY.md | 12 ++++++++++++
 1 file changed, 12 insertions(+)
$ wc -l corpus/QUALITY.md
466 corpus/QUALITY.md
```

At the build `5dacf2c70f947ca6dc5fbbca6d45b8db5b0390c8` the file is 454 lines with rows
KQ1–KQ88 and `diff <(git show 5dacf2c7:corpus/QUALITY.md) corpus/QUALITY.md` was empty when this
seat started; it is no longer. The delta is a five-row round-52 section at
`corpus/QUALITY.md:456-466`: `KQ89 (supersedes KQ86)`, `KQ90 (supersedes KQ87)`,
`KQ91 (narrows KQ85)`, `KQ92`, `KQ93`. I did not write it; I snapshotted its bytes
(`landed-round52-rows.txt`, `quality-worktree.diff`, hashes in the rows file) and left the tree
untouched — re-running `git status` after my session shows the same ` M` and the same 12-line diff.

## 2. Scan: which rows lack a lesson-file citation (verify of the brief's quick list)

```
$ python3 .ufo/waves/round-52/w1/out/W2Quality/scan-rows.py corpus/QUALITY.md
total rows 93
== rows whose last cell names no lesson file == 12
289  KQ39  …  | 303  KQ41  cells=3  | 309  KQ42  | 322  KQ45  | 334  KQ47
435  KQ80  | 436  KQ81  | 437  KQ82  | 438  KQ83  | 439  KQ84
441  KQ86  | 442  KQ87
lesson refs 58 missing []
```

(the script is committed to my out dir; it skips the `## Restored lines (round 52)` fence, whose
restored `KQ46` row is historical bytes, not a live criterion). The brief's list of ten was
incomplete by exactly the two rows round-51 closure D7 named: KQ86 (`:441`) and KQ87 (`:442`).
After the five uncommitted rows, ten remain uncited — none of them is in the new section.

Lessons identified, all verified in the file they name:

| row | lesson that produced it | where |
|---|---|---|
| KQ39 | round-29 §Claims C1 (writing revision W, `git blame --line-porcelain`, S174) | `corpus/lessons/round-29.md:10-16` |
| KQ41 | round-31 §Claims C2 + Mistakes #2 | `corpus/lessons/round-31.md:15-22`, `:55` |
| KQ42 | round-31 Mistakes #7 (six `meaning` cells falsified) | `corpus/lessons/round-31.md:128` |
| KQ45 | round-30 Mistakes #3 (S174), round-32 spot-check §6 item 3 (S193); the round-36 measurement is in the fleet report only — finding F3 | `corpus/lessons/round-30.md:101`; `corpus/lessons/round-32-verifier-spotcheck.md:81` |
| KQ47 | round-38 §Frontier (proposal 4 adopted as KQ47; the round ran attempt 2) | `corpus/lessons/round-38.md:98` |
| KQ80, KQ81 | round-49 spot-check R1 | `corpus/lessons/round-49-verifier-spotcheck.md:103` |
| KQ82 | round-49 spot-check R2 | `…:104` |
| KQ83, KQ84 | round-49 spot-check R3 | `…:105` |
| KQ86 | round-50 spot-check R6 + round-51 Claims C2 (5 of 106 events at threshold 20) | `corpus/lessons/round-50-verifier-spotcheck.md:120`; `corpus/lessons/round-51.md:19` |
| KQ87 | round-51 Claims C2 (A-row permitted rule, 58 lines) | `corpus/lessons/round-51.md:19` |

## 3. Defects in the rows that landed while this seat scanned

These five rows are **uncommitted**, so they can still be corrected in place; after commit,
`corpus/QUALITY.md` is A-corr and each fix becomes a new appended row. Full replacement text for
RV3/RV4 is in `rows.md` §1.

**RV1 — `corpus/QUALITY.md:462` and `:463` end `…; \`corpus/lessons/round-52.md\` Errata D7`.**
That section does not exist, and `D7` is round-51's label:

```
$ grep -c '^## ' corpus/lessons/round-52.md
2
$ grep -n '^## ' corpus/lessons/round-52.md
9:## Claims
16:## Gate
$ grep -n 'D7' corpus/lessons/round-51-verifier-spotcheck.md | head -2
117:- QUALITY KQ85–KQ88 are present … neither names a lesson (D7).
150:- **D7 (lane, QUALITY citation).** … Append a superseding row or an erratum that names the lesson file.
```

Fix (both last cells):
`…; \`corpus/lessons/round-52.md\` (this round's lesson); \`corpus/lessons/round-51-verifier-spotcheck.md\` D7`.

**RV2 — `corpus/QUALITY.md:466` (KQ93) ends `C1; \`corpus/lessons/round-52.md\` Mistakes`.**
`round-52.md` has no `## Mistakes` section. The defect is real and filed:
`\.ufo/waves/round-52/w1/out/V2Review.md:5,9` (`LD_LIBRARY_PATH` added to `child_env`, recorded in
`child_env_keys`, rejected by the unchanged `tests/llamacpp-live/check-receipt.py`; the checker now
validates the key at `tests/llamacpp-live/check-receipt.py:638-657`). Fix: cite that report (or
append a `## Mistakes` section to the A-corr lesson and keep the citation).

**RV3 — `corpus/QUALITY.md:464` (KQ91) is weaker than the frozen counter.** The counter's `sealed`
leg requires the opened image's bytes to hash to the frozen server digest and the recorded seals to
be compared with its own `F_GET_SEALS` (`tools/round52-replay-memfd-audit.py:36-45`); the row
requires only dev and inode to be recorded, names no digest, carries no `Check:` command, and keeps
two of the preregistered limits (libraries-by-path, host memfd) while dropping the round-50 carried
ones. The build receipt shows both legs it omits:

```
$ sed -n '1,2p;6p' .ufo/waves/round-52/measured/c1-build.out
bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:155472 seals 15 is a sealed
        memfd with the frozen digest, recorded in server_exe and own_server
```

(that is the L1's observation, read by me; I did not run the counter). Fix: replacement row in
`rows.md` §1 RV3, restoring the digest leg, the `Check:` line and the carried limits.

**RV4 — `corpus/QUALITY.md:465` (KQ92) carries no `Check:` line and only one of the two
preregistered C2 limits.** `.ufo/waves/round-52/preregistration.json` `limits[3]` says the counter's
`exempt=` rule is simpler than the tool's (`SCORECARD.md` may grade fewer lines than the tool) and
`limits[4]` says re-appended lines are historical bytes, superseded where later text says so. Fix in
`rows.md` §1 RV4.

**RV5 (wording, not a defect) — `corpus/QUALITY.md:462` states "101 of 106" without its
measurement point.** The arithmetic is round-51's (`5 of 106 events` graded at threshold 20,
`corpus/lessons/round-51.md:19`); round-50 R6 records 97 at round-50's tip. The row already cites
round-51 C2 in the same cell, so the figure is traceable; quoting it as "graded 5 of the 106 events
v5 could see" would fix the revision for a reader.

## 4. What I delivered

`.ufo/waves/round-52/w1/out/W2Quality/rows.md` — §1 review of the landed rows with five defects and
replacement text; §2 ten ready-to-append rows (KQ94–KQ103 at the current next-free id: KQ94/KQ95
KQ39/KQ41, KQ96 KQ42, KQ97 KQ47, KQ98 KQ45, KQ99–KQ103 KQ80–KQ84), every row citing
`corpus/lessons/round-52.md` plus the lesson that produced the criterion, with the original
admission/reject cells explicitly preserved; §3 scan and findings F1–F5; §4 limits. Table shape
verified: 10 rows, 4 cells each, no unescaped pipe except the `\|` in the C1 seals expression.

Findings beyond the drafts: F1 twelve uncited rows, not two, and KQ41 has only three cells (`:303`,
`awk` check pasted in `rows.md`); F3 KQ45's round-36 measurement lives only in the fleet report
`.ufo/reports/round-36/kama.md:216-221` — `grep -c "S174\|S192\|S193" corpus/lessons/round-36.md`
→ `0` — so a lesson-file-only citation is unavailable without an appended round-36 correction;
F4 the round-52 lesson has two headings, which is RV1/RV2's root.

## 5. Out of scope / not done

- Ran no counter, started no server (my scratch stayed empty; the two `llama-server` processes on
  the host belong to seat M3Live's scratch, not mine), made no git or jj mutation in the lane or
  the fleet repo, wrote nothing in the lane.
- The integration items the brief names (SCORECARD §Round 52, LOG entry, README frontier, errata
  D2/D3/D4/D6) were not touched, as instructed.
- I did not decide whether RV3/RV4 are amended pre-commit or filed as supersessions, nor the final
  row numbers; `rows.md` states both routes.

## 6. Artifacts (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W2Quality.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W2Quality/rows.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W2Quality/scan-rows.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W2Quality/landed-round52-rows.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/W2Quality/quality-worktree.diff`
