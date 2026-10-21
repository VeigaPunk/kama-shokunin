# ScribeLog — round-24 append-only LOG draft: motivation and filed-evidence corrections

Seat: `ScribeLog` (leaf; no subagent dispatch). Lane base observed: `0df800e896f6bce285a81e794ad4ae1d1e6c3a71`
(preregistered base) is an ancestor of lane tip `d1b9d956a0beda9ac32a1a2cf6ced875faeada0d`
(round-24 preregistration commit). Scratch clone: `/fast/scratch/hyaku/kama-r24/ScribeLog`
(`git clone --no-hardlinks`, git 2.56.0, Python 3.14.8). No production file was edited.

## Verdict

**Draft complete; every number in the draft re-observed at source, and no round-24
outcome is claimed.** The draft is an append-only LOG block naming (1) the filed r23
report, (2) closure row 428, (3) the falsify-wave report count corrected to 69, and
(4) the identity limitation "40 of 56 killed FIFO-process identities retained, not
full identity evidence".

## Deliverable (draft only, out directory)

- `.ufo/waves/round-24/build/out/ScribeLog/LOG-round-24-entry.md` — the candidate
  append-only LOG block (`## round 24 — r23 report, closure row 428 and the
  filed-evidence corrections (2026-10-21, appended)`), 78 lines, in the round-21/22/23
  entry style.
- `.ufo/waves/round-24/build/out/ScribeLog/LOG-round-24-entry.patch` — unified diff of
  that block against `LOG.md` at `d1b9d95` (hunk `@@ -1428,3 +1428,82 @@`); `patch -p1
  --dry-run` against a pristine copy exits 0 and the applied result is byte-identical
  to the intended candidate.
- `.ufo/waves/round-24/build/out/ScribeLog/evidence.txt` — the re-observation transcript
  (append-only; one correction block appended at the end, see F4).
- `.ufo/waves/round-24/build/out/ScribeLog/collect-evidence.sh` — the script that
  produced `evidence.txt` (read-only; re-runnable).

## Verified observations (each re-run by this seat)

| # | observation | command | observed |
|---|---|---|---|
| O1 | preregistered base is an ancestor of lane tip | `git -C <scratch> merge-base --is-ancestor 0df800e8 HEAD` | exit 0 (ancestor) |
| O2 | closure row 428 is the kama round-23 closure, rejected-harmed | `python3 -c "json.load(MANIFEST.json)['rounds'][428]"` | `round 23`, `lane kama`, `type closure`, `admitted False`, `verdict rejected-harmed`, `verdicts.operability harmed`, `trends.quality harmed`, `report .ufo/reports/round-23/kama.md`, `commit kama-shokunin@0df800e8…`, `closed_at 2026-10-21T17:44:26Z`, `rejection_streak_impact 1` |
| O3 | the filed r23 report is the fleet report at commit `410b511` | `git -C /home/vgpnk/Projects/shokunin log --oneline -1 -- .ufo/reports/round-23/kama.md` | `410b511 round-23: kama report` |
| O4 | falsify-wave durable lane reports = 69 | `ls .ufo/waves/round-23/falsify/advice/*.md \| wc -l` | `69` (directory holds 70 entries; 1 is `swarm-registry.json`) |
| O5 | seat arithmetic agrees | 73 falsify seats − 4 dead seats | 69; the 4 dead seats (RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty) left no advice file (`ls …/advice/ \| grep -E 'RowC01Clean\|RowF07LogFollow\|RowF09SignatureProgram\|CritOpenHonesty'` → no match) |
| O6 | the build wave shows the same seats-vs-reports arithmetic | `ls .ufo/waves/round-23/build/advice/*.md \| wc -l` | `67` = 68 seats − 1 dead (RevClaimScope) |
| O7 | the missing report is RowC03, written before its response aborted | `stat -c '%s %y' .ufo/waves/round-23/falsify/advice/RowC03FabricatedFull.md` (lane path, read-only) | `6618 bytes`, mtime `2026-10-21 13:10:15 -03` = 16:10:15Z — matches the closure routed check ("wrote 6618 bytes at 16:10:15Z before aborted final response 16:10:50Z") |
| O8 | the miscount sits in the lesson | `sed -n '178,180p' corpus/lessons/round-23.md` | "73 seats dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow, RowF09SignatureProgram, CritOpenHonesty, killed with the host session, no output)." |
| O9 | only 40 of the 56 counted processes have retained identity rows | transcript `KamaR23-2.jsonl` lines 154/155/157/158 | 16:33:38.655Z command `ps -eo pid,lstart,args \| grep -E 'repo-state-grid-\|kama-r23\|refusal' \| grep -v grep \| cut -c1-200 \| head -40; ps -eo pid,args \| grep -E 'repo-state-grid-\|/tmp/kama-r23' \| grep -v grep \| wc -l` → result at 16:33:38.846Z = 40 identity rows (pid, lstart, args) + count line `56`; kill at 16:33:46.620Z `pkill -f -- '-C /tmp/repo-state-grid-' ; pkill -f -- '/tmp/kama-r23w2/'` → count `0` at 16:33:47.911Z |
| O10 | seat transcripts corroborate the 69-vs-68 split | `ls /home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-21T03-31-39-302Z_…/CloseKama22/*.jsonl \| wc -l`; `stat -c '%s' …/CloseKama22.RowC03FabricatedFull-2.md` | `141` seat transcripts (matches the closure's "exactly 141 seat jsonl files"); RowC03's session summary file is `0` bytes (its final response never landed; last jsonl record 2026-10-21T16:10:51.353Z, type `custom`, no assistant text) while its durable lane report exists (6618 bytes, 16:10:15Z) — i.e. 68 final session replies plus RowC03's durable lane output = 69 |
| O11 | the filed claims that this correction qualifies | `corpus/lessons/round-23.md:174` (M7) and `.ufo/reports/round-23/kama.md:34` | lesson: "56 blocked `git` processes … after the final grid run 0 such processes remained"; report: "grid timeout now kills the auditor's whole session (56 orphaned FIFO-blocked git processes from this round were killed)" |

## Findings

- **F1 — the r23 disposition is rejected-harmed, not admitted.** The author claim
  ("calibration 7 → 7, verified on the graded population", filed report
  `.ufo/reports/round-23/kama.md`) is the author's; `MANIFEST.json` `rounds[428]`
  records `admitted: false` / `verdict: rejected-harmed` with
  `verdicts.operability: harmed` and `trends.quality: harmed`. The draft states the
  author's claim and the closure's decision as two different things, in that order.
- **F2 — the closure's harm ruling is the motivation, and it is specific.** Its
  routed check (verbatim in the row): T01 "frozen exit0 correct clean verdict → current
  exit2 'partial clone (promisor pack)'", and "the old verdict is correct, not merely an
  unsafe false verdict being replaced by refusal"; F23 "frozen rc1/unresolved-full-hash →
  current rc2"; git ≥ 2.45 now required. Disclosure of a trade does not waive the
  no-trade rule. Route kama-R23-H1 is the round-24 repair; kama-R23-H2 (Git floor as an
  operator-approved prerequisite) stays open and is not claimed here.
- **F3 — "68" is the lesson's report count, and the filed report does not state it.**
  The closure's routed check phrases it as "the report's 68", but the filed report
  states seats and dead counts (73 falsify seats, 4 dead, lines 148-153) and never
  states a report count; the "68" figure lives in `corpus/lessons/round-23.md:178` and in
  the closure's own wording. The draft therefore locates the defect in the lesson line
  and quotes the closure's R23-C1 sentence rather than repeating "the report said 68".
- **F4 — evidence-file correction (appended, not rewritten).** The first stat of
  `RowC03FabricatedFull.md` in `evidence.txt` was taken inside the scratch clone, where
  mtimes are clone-time (14:54:46 -03) and are not evidence of the write time. The
  authoritative read-only stat of the lane file (13:10:15 -03 = 16:10:15Z) is appended
  at the end of `evidence.txt` and is the number the draft cites.
- **F5 — the two `ps` commands in the cleanup transcript do not match the same set.**
  The identity listing greps `repo-state-grid-|kama-r23|refusal` (broader) while the
  count greps `repo-state-grid-|/tmp/kama-r23`; the listing is additionally cut by
  `head -40`. So the 40 retained rows are a prefix of a match set that is not identical
  to the counted 56 — an independent reason the 56 cannot be treated as an identity
  inventory. The retained rows do show round-owned fixture paths and in-round start
  times (12:35-13:02 -03), so no unrelated victim is evidenced — and none is proved
  absent. The closure records the same limit: "no complete 56-PID inventory was
  retained: all 56 individual identities cannot now be independently proved".
- **F6 — an L1 round-24 LOG section already exists at the lane tip.** `LOG.md:1411-1430`
  (`## round 24 — repair-first preregistration (2026-10-21)`, commit `d1b9d95`) already
  states the rejected-harmed closure, the 69-vs-68 correction and the 40-of-56
  limitation in three bullets. The draft is an *appended* refinement that adds the
  provenance those bullets lack (which report, which row, which lesson line, which
  transcript lines, and that no round-24 outcome is yet measured). L1 may adopt,
  merge or drop it; the draft is not written to `LOG.md` by this seat.
- **F7 — no numeric outcome is invented.** The draft asserts only r23 observations
  (O2-O10), the two status-neutral corrections, and an explicit boundary line stating
  that the round-24 repair, grid, mutants and historical parity are unrun as of this
  entry. The preregistered expectations live in `.ufo/waves/round-24/preregistration.json`
  and are cited, not restated as results.

## Not run / unverified (stated, not implied)

- No round-24 measurement of any kind: `tests/report-audit/promisor-grid.py --arm both
  --json`, `tests/report-audit/isolation-mutants.py`, the auditor selftest, the
  historical-parity recipe and the sources census/validate were **not** executed by this
  seat. No round-24 exit code, count or finding ID is claimed anywhere in the draft.
- The r23 grid/mutant/selftest numbers (26/26 faults, 30/31 mutants, 50/50 selftest,
  13 reports / 54 required commits) were **not** re-measured here; the draft does not
  repeat them.
- The closure row's `verification`/`spotcheck`/`rechecks` text was read, not re-executed;
  the "56/40" limit inside it was independently confirmed from the primary transcript
  (O9), not taken on the closure's word.
- The falsify-wave session files under
  `/home/vgpnk/.omp/agent/sessions/-Projects-shokunin/2026-10-21T03-31-39-302Z_…/`
  were not parsed for seat accounting; the 141-seat and 5-missing-report figures quoted
  in the closure are cited as closure-stated where they appear.
- No source page was reopened online for this draft; no new `corpus/SOURCES.md` row is
  proposed.

## Touched surfaces

- Written (this seat): `.ufo/waves/round-24/build/out/ScribeLog/` only
  (`LOG-round-24-entry.md`, `LOG-round-24-entry.patch`, `evidence.txt`,
  `collect-evidence.sh`) and this report.
- Read-only: `LOG.md`, `SCORECARD.md`, `corpus/lessons/round-23.md`,
  `.ufo/waves/round-23/falsify/**`, `.ufo/waves/round-23/final/**`,
  `/home/vgpnk/Projects/shokunin/MANIFEST.json`,
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`, and the dead-L1
  transcript under `/home/vgpnk/.omp/agent/sessions/…/KamaR23-2.jsonl`.
- Not touched: `LOG.md`, `SCORECARD.md`, `corpus/**`, `tools/**`, `tests/**`, the
  fleet repo, `.jj`, any Git index. No commit, push, or jj command.

## Out of scope for this seat

The promisor-completeness repair itself, its grid/oracle/mutants, the r24 measurement
run and any SCORECARD, lesson, KQ or SOURCES append: those are other seats'. This seat
produced a LOG draft only.

## Installs / updates

None. No tool installed, upgraded or removed; no pacman transaction; no host service
or config mutation.

Trailer: `.ufo/waves/round-24/build/advice/ScribeLog.md`
