# W5Log — round-52 LOG.md entry (draft, append-only)

**Verdict: the round-52 LOG entry is drafted and every claim it makes is one I opened in the lane at the freeze, the base or the build; two bullets (re-verification, the wave's routed set) are shaped so that the L1 fills them from seat reports at integration, and the unfilled state of each is still true.**

## 1. Deliverable and how it lands

- Draft: `.ufo/waves/round-52/w1/out/W5Log/log.md` (9,513 B, 11 lines, heading `## Round 52 — …(2026-10-27)`, ends `- Lesson: corpus/lessons/round-52.md.`).
- Append it at the **end of `LOG.md`**, i.e. directly after line 2422, which is the closing five-backtick fence of the build's own `## Restored lines (round 52)` block (`tail -c 60 LOG.md` → `…lessons.\n`````\n`). Nothing is inserted before it, so the append is the only write.
- Placement is safe for grading: `LOG.md`'s contract row is region `*` with no exempt titles — `registry/append-only-contract.tsv:2` → `LOG.md\tA-corr\tREADME.md:16\t*\tround log; corrections land as new entries`. Every appended line is therefore graded, and a later in-place deletion of this entry will be caught by `tools/append-only-audit.py`.
- House style followed from the round-51 entry (`LOG.md:2348`–`:2355`): one dense bullet per claim with axis arrow, source row, motivating evidence as `file:line`, the build as tool/function names, the counter with its sha, the base control with its leg line, then freeze/build/wave, battery, re-verification, routed defects, lesson. Measured values are **not** restated: the draft points at `SCORECARD §Round 52 and §Round-52 measured results`, as instructed.
- I wrote this report and the draft once; neither was rewritten after completion (round-51 defect: a seat rewrote a committed report in place).

## 2. Evidence — commands, outputs, exits

| # | Command (cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`) | Output / exit |
|---|---|---|
| 1 | `sed -n '2348,2357p' LOG.md`; `tail -c 60 LOG.md \| od -c` | round-51 entry shape read; LOG ends with a closing 5-backtick fence + newline |
| 2 | `git log --format='%h %ci %s' -25` | `8551ba7f` freeze 01:42:07 -0300, `5dacf2c7` build 01:56:49, `34d82600` wave spec 02:05:19, base `9ff76b1f` 01:28:32 |
| 3 | `git show --stat 8551ba7f` | 7 files, +1977: preregistration, both counters, `census/start.out`, `controls/base.c{1,2}.out`, `c1/memfd_create.2.txt` |
| 4 | `git show --stat 5dacf2c7` | 29 files, +760/−200 (two tools, S500, 18 restoration files, ledger −155, SKILL, lesson, hexrun ×2, X7Regen pair) |
| 5 | `git show 5dacf2c7:tools/round52-replay-memfd-audit.py \| sha256sum`; same for the C2 counter | `053ff502…1121f5`, `29dfd886…c30853ea` — equal to `preregistration.json` `claims[*].counter_sha256` |
| 6 | `cat .ufo/waves/round-52/controls/base.c1.out` (`:2`) | `bind=1 sealed=0 teardown=1 newrow=0 bound=3/3 sealedruns=0/3 met=False`, `exit=1`; detail: `F_GET_SEALS … Invalid argument`, link count 1, neither record names the observed image |
| 7 | `cat .ufo/waves/round-52/controls/base.c2.out` (`:2`) | `fixture=1 lane=0 scenarios=8/8 corr_lost=151 row_lost=10 disclosed=165 met=False`, `exit=1`; 45 detail lines end `(restore by append)`; per-file map sums to 151 |
| 8 | `cat …/measured/c1-build.out` (`:3`) | `bind=1 sealed=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 met=True`, `exit=0`; three images `/memfd:llama-server (deleted)` seals 15 digest `35ac50fb…`; `teardown … after 0.10 s` |
| 9 | `cat …/measured/c2-build.out` (`:3`) | `fixture=1 lane=1 scenarios=8/8 corr_lost=0 row_lost=10 disclosed=10 met=True`, `exit=0`; lane `tool v6 … events 109 disclosed_lines 10; own graded 5868; own unheld A-corr 0, A/A-row 10` |
| 10 | `cat …/measured/{gate,r41,r42,r43,digest,hexrun,cap,sao,aoa,*-selftest,r48c2,r49c1,r50c1,r51c1,r51c2}-build.out` | gate `registered 50 unregistered 0 defective 0`; r41 `axes=6 facts=36 mismatches=0`; r42 `maxN=51 mismatches=0`; r43 `registered=50 mismatches=0`; digest `tokens=134 ledger_bad=0 wrong_unflagged=0 unknown=0`; hexrun `tokens=1930 ledger_bad=0 unknown=0`; cap `11/11 met True`; sao `added S500 (allowed)`; aoa `restored=67 partial=0 unrestored=0 regressed=0 disclosed_lines=10 bad_disclosures=0`; KLR `pass=31`, AOA `pass=51`, live `ok`, receipt `16 VALID and 1 NOT-EVALUATED`/107 rejected; r48c2/r49c1/r50c1/r51c2 `met=True`; r51c1 `bind=1 own=0 … met=False` |
| 11 | `grep -c $'\tW04\t'`/`W01` on `census/start.out` and `measured/census-build.out` | 94 / 1 in both; `exit=0` |
| 12 | `git show 5dacf2c7:registry/append-only-disclosures.tsv \| wc -l` + `cut -f1-3` | 11 lines = header + 10 rows: `corpus/SOURCES.md` 7 (`ccc4bb31`, `54c6f4fe` ×4, `8bc8e375`, `3d42897b`), `registry/report-landing-errata.tsv` 3 (`1471344b` ×3) |
| 13 | python counting script over `git show 5dacf2c7:<file>`, fence-content lines after the restored heading | `TOTAL 155 files 18`; per-file LOG 22, SCORECARD 23, README 20, QUALITY 2, 14 lessons 88 — matches the tool's per-file unheld map in `base.c2.out` plus its 4 SCORECARD lines (see `W5Log/restored-lines.txt`) |
| 14 | `git show 5dacf2c7:SKILL.md \| sha256sum; … \| wc -l; … \| grep -c '^## '` | `e749b350…c83f154`, `1558`, `40` — the SCORECARD depth anchor as re-anchored |
| 15 | `git diff 9ff76b1f 5dacf2c7 -- registry/hexrun-ledger.tsv` | `+39877b17…` (round-51 report fleet commit, evidence `.ufo/waves/round-52/hexrun-evidence/39877b17…txt`), `+907cdcc0a76f…c50725…` ledgered `wrong` beside the correct `…c0a50725…` |
| 16 | `grep -n` on `c1/memfd_create.2.txt` | quote `:81`–`:82` (wrapped), `Linux 3.17, glibc 2.27.` `:186`, `Linux man-pages 6.19  2026-02-08` `:465` |
| 17 | `python3 tools/prereg-time-check.py --repo . --path .ufo/waves/round-52/preregistration.json --rev 8551ba7f…` | `RESULT pass: no timestamp later than the committer time`, `exit=0` (`W5Log/prereg-time-check.out`) |
| 18 | `grep -n "Re-verification" LOG.md` | only the round-51 entry (`:2354`) carries the shaped bullet; the draft reproduces that shape |
| 19 | `cat .ufo/waves/round-51/measured/hexrun.out` | `unknown=0` already at round 51 — so the draft does **not** claim round 52 closes those two unknowns |
| 20 | `ls .ufo/waves/round-52/w1/out/` at draft time | 16 seat `.md` reports of the 70 dispatched; no `S1Source.md`, no `Sc2Watch.md` (drives finding F2) |

Not run, deliberately: both C1/C2 counters (seats X1Rerun, X2Rerun, X6Rerun own independent measurement), `measure.sh`, any `git`/`jj` mutation. No tool was installed or upgraded.

## 3. Findings

**F1 — `.ufo/waves/round-52/freeze/` is empty: round 52 commits no `prereg-time-check` receipt, where round 51 committed one.** `ls -la .ufo/waves/round-52/freeze/` → only `.`/`..`; `ls -la .ufo/waves/round-51/freeze/` → `prereg-time-check.out` (276 B) and `frozen-at-erratum.md`. The check itself passes on the frozen bytes (evidence 17: `RESULT pass`, exit 0, `frozen_at_utc` 7 s *before* the commit — the round-51 failure mode is absent), and seat Sc1Freeze is dispatched to re-run it, but that seat writes to `w1/out/Sc1Freeze/`, not to `freeze/`. The draft's freeze bullet carries the result and names the gap. Proposed fix: commit the receipt at integration as a new file (no existing line changes):

```
.ufo/waves/round-52/freeze/prereg-time-check.out
rev=8551ba7f2056f2465d20f5b50586978133212fe1 path=.ufo/waves/round-52/preregistration.json
committer_time=2026-10-27T01:42:07-03:00 max_future=86400
  ok   line 6: 2026-10-27T04:42:00Z (at/before commit)
RESULT pass: no timestamp later than the committer time
exit=0
```

**F2 — two of the entry's bullets depend on seats whose reports had not landed, so they are written as fill slots rather than as observed results.** `w1/dispatch.json` dispatches 70 seats; at draft time `w1/out/` held 16 `.md` reports, and it holds no `S1Source.md` and no `Sc2Watch.md`. `grep -c "S49[6789]" w1/dispatch.json` → 0, so no seat re-opens S496–S499; the only freshness subjects are S500 (S1Source) and the release/pin state (Sc2Watch). The re-verification line therefore states what is observed (no other source re-opened; S500's capture and its provenance lines) and brackets the fill: `[fill at integration: … S1Source's S500 verdict … Sc2Watch's …]`. If the bracket is left filled-in-words but never resolved, the remaining sentence is still true; if the seats report, replace only the bracket. The routed-defects bullet is written the same way, naming the frozen D5 split and deferring the wave's ablation/shortcut/mutation set to `SCORECARD §Round 52`.

**F3 — the draft reports round-51's counter at the build as superseded, not as a regression, and flags exactly why.** `r51c1-build.out:3` reads `bind=1 own=0 teardown=1 newrow=1 bound=3/3 owned=0/3 met=False`: C1 replaced the `own_server` path binding with a memfd binding, so this leg *must* fall. Two LOG conventions pull opposite ways here (a battery leg at `met=False` reads as a regression, but a superseded counter reads as progress); the draft keeps the leg visible with its line citation and the sentence "the round-51 path binding is superseded by C1, not regressed". Any integration edit that drops that sentence would turn a correct change into an apparent regression.

**F4 — verbatim restoration re-appends a *wrong* hash, and the build already accounts for it.** The restored block of `corpus/lessons/round-32-verifier-spotcheck.md` holds the pre-correction lane tip `907cdcc0a76f…c50725…` (one digit off `…c0a50725…`). `registry/hexrun-ledger.tsv` carries it as a `wrong` row naming the correct hash and the in-place correction `cc469803`, and `hexrun-census` at the build reads `ledger_bad=0 unknown=0`. Not a defect (claim C2 restores bytes, it does not re-assert facts), but a LOG reader meeting the hash in the entry now sees the ledger line that explains it.

**F5 — the entry's numbers reconcile, so the L1 can check the draft without re-deriving it.** 165 disclosed (round 51) = 155 A-corr + 10 A/A-row; the 155 ledger rows removed at the build (`git show --stat 5dacf2c7` → `registry/append-only-disclosures.tsv | 155 ---`) equal the 155 fence-content lines I counted independently across 18 files; the counter holds 151 of them and the tool 155 because the counter's simpler `exempt=` rule leaves 4 `SCORECARD.md` lines ungraded — the preregistered limit, and the reason `base.c2` prints `corr_lost=151` beside `disclosed=165`.

## 4. Out of scope / not touched

- Lane files are untouched: no edit to `LOG.md`, `SCORECARD.md`, the lesson, `registry/`, `corpus/`, or either counter; the entry exists only as a draft in my out dir. No `git add/commit/checkout/stash/reset`, no `jj`, no lane write outside my out dir.
- I did not run the claim counters, `measure.sh`, or any regression tool (evidence 10 reads the receipts the L1 committed at `34d82600`); I did not start or stop a server; `pgrep -af llama-server` was not needed.
- Sibling seats' own deliverables (SCORECARD §Round 52, measured results, QUALITY rows, README frontier, lesson Mistakes, errata) are not drafted here.

## 5. Artifacts

Written (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/`):

- `W5Log/log.md` — the draft LOG entry, ready to append after `LOG.md:2422`.
- `W5Log.md` — this report.
- `W5Log/prereg-time-check.out` — my run at the freeze revision (exit 0).
- `W5Log/restored-lines.txt` — independent per-file restored-line count at `5dacf2c7` (155 / 18 files).
- `W5Log/{base.c1.out,base.c2.out,c1-build.out,c2-build.out,aoa-build.out,r51c1-build.out}` — copies of the receipts the entry cites.

Scratch `/fast/scratch/hyaku/kama-r52/W5Log` removed (`rm -rf`); no path under `/tmp` is cited.
