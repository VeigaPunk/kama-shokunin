# CritEvidence — r23 count corrections (69 vs 68; 40 of 56)

## Verdict

Both corrections are directionally right, but the text already committed
for them (`LOG.md:1417-1420` and `preregistration.json` expected_after[6],
commit `d1b9d95`) has two defects.

1. **It names the wrong file (false provenance).** It corrects "filed
   `.ufo/reports/round-23/kama.md`: 69 … not 68". The filed report never
   says 68 falsify reports. Its accounting (73 seats, 4 dead) already
   comes to 69. The stale "68" is in the lane lesson
   `corpus/lessons/round-23.md:178`.
2. **It repeats an overclaim.** "40 of the 56 killed FIFO-process
   identities were retained" still treats all 56 as FIFO-blocked `git`.
   The retained rows disprove that: 2 of the 40 are `gpg-agent` and
   `scdaemon`. The 56 is a grep count under a different pattern from the
   40-row listing.

Smallest safe fix: one more append-only entry, as drafted in
`out/CritEvidence/r23-corrections-append.md`. It names the filed report,
the lesson, and the `d1b9d95` text it supersedes. No file filed in r23
is rewritten. Impacted axes: calibration and honesty of evidence
(provenance). C1's grid, oracle and operability are not affected.

## Evidence: the 69-vs-68 count

- Filed report (fleet `410b511`), `/home/vgpnk/Projects/shokunin/.ufo/reports/round-23/kama.md`:
  - `:143` "Wave 1 build: 68 seats". This is the only 68 in the file, and
    it counts build seats, not reports.
  - `:148-155` "Wave 2 falsify: 73 seats … Dead: 4 … RowC01Clean,
    RowF07LogFollow, RowF09SignatureProgram … CritOpenHonesty". 73 − 4 = 69.
  - No line gives a falsify report count.
- Lane lesson (`0df800e`), `corpus/lessons/round-23.md:178`: "73 seats
  dispatched (68 reports; dead: RowC01Clean, RowF07LogFollow,
  RowF09SignatureProgram, CritOpenHonesty". This contradicts itself,
  since 73 − 4 = 69.
- `LOG.md:1405-1407` (r23 section) gives 73 seats with 4 dead, which is
  consistent.
- The closer's spot-check text (`MANIFEST.json`, commit `e6a5eea`) says
  "not report's 68". That is where the misattribution started; `d1b9d95`
  then repeated it.
- Measured counts:
  - `.ufo/waves/round-23/falsify/advice/*.md` = 69 files.
  - `spec.json` has 73 item names. The names with no report are exactly
    {CritOpenHonesty, RowC01Clean, RowF07LogFollow, RowF09SignatureProgram},
    and every report file has a matching spec name.
  - Build wave: `build/spec.json` has 68 items and `build/advice/*.md` has
    67 files.
  - So the closure's "141 seats and 5 missing reports" holds.
- RowC03 check: `falsify/advice/RowC03FabricatedFull.md` is 6618 bytes,
  modified 13:10:15 −03 (16:10:15Z), sha256 `0ef4878b…2f95`. That matches
  the closure's "wrote 6618 bytes at 16:10:15Z".
- Unverified: the closure's "68 final session replies" (I did not count
  session reply files).

## Evidence: the 40-of-56 identities

Source: the KamaR23-2 session transcript
`~/.omp/agent/sessions/-Projects-shokunin/2026-10-21T16-10-39-768Z_01a15f3a-9f17-7238-ae23-4fe77ffa6530/KamaR23-2.jsonl`
(sha256 `114ffef5…60db`). This file is outside the lane.

**What the 16:33:38Z command did (transcript line 154).** One command
produced two different outputs:
- A listing: `ps -eo pid,lstart,args | grep -E 'repo-state-grid-|kama-r23|refusal' | cut -c1-200 | head -40`
- A count: `ps -eo pid,args | grep -E 'repo-state-grid-|/tmp/kama-r23' | wc -l`

The result (transcript line 156) is 40 rows plus the count `56`. I copied
it verbatim to `out/CritEvidence/r23-ps-listing-line156.txt` (sha256
`96c21f6f…15bc`).

**The kill.** Transcript line 157 (16:33:46Z) ran
`pkill -f -- '-C /tmp/repo-state-grid-'` and `pkill -f -- '/tmp/kama-r23w2/'`.
Line 159 shows the count afterwards was `0`.

**No overlap with the L1's own probe.** That probe ran from 16:33:13Z to
16:33:14.938Z (transcript lines 145 and 147), before the count. Nothing
the L1 was measuring was killed.

**What the 40 retained rows are** (classification in
`out/CritEvidence/r23-ps-classification.txt`):
- Programs: 38 `git`, 1 `gpg-agent`, 1 `scdaemon`. The two daemons ran
  with `--homedir /tmp/kama-r23w2/ExecOldGitRun/gnupg`, which comes from
  the falsify seat ExecOldGitRun. This falsifies "56 blocked `git`
  processes" (lesson `:174`) and "56 orphaned FIFO-blocked git processes"
  (filed report `:34-35`).
- Start times: 12:18:54 to 13:29:37 −03. This matches M7's 12:18–13:29.
- Membership in the 56: 37 rows provably match the counting pattern. The
  other 3 had their argv cut at 200 columns before the path, so their
  membership can't be shown.
- Grid rows. Row indices are stable across `e0f0434`, `34b2376`,
  `245a37f` and `e876b95`: 0 = C01, 20 = F13, 21 = F14 mailmap-fifo,
  37 = F30 include-fifo.
  - 19 rows tie to FIFO fixtures: row 21 ×17 (15 frozen arm, 2 current
    arm), row 37 ×1, and one `/tmp/kama-r23w2/c02/variants/fifo` path.
  - 5 rows sit at frozen-arm rows 20 (×4) and 00 (×1). Neither is a FIFO
    row. In the final frozen grid, only F14 and F30 timed out
    (`.ufo/waves/round-23/final/grid-both.json`, `timed_out`).
  - 14 rows have no grid index after truncation.
  - [INFERENCE] Seat-run variant grids may have used other row orders, so
    the index mapping is not certain for those processes.
- The remaining 16 counted processes have no retained identity anywhere.

## Counterexample to the current correction text

The correction says "40 of the 56 killed FIFO-process identities were
retained". The retained rows themselves contradict it:
- Row 20 is `882563 … gpg-agent --homedir /tmp/kama-r23w2/ExecOldGitRun/gnupg`.
- Row 21 is `882565 … scdaemon …`.

These two are counted among the "FIFO-process identities" but are neither
`git` nor FIFO-blocked. Only 19 of the 40 rows can be shown to be FIFO
fixtures.

## Smallest safe correction

Append the block in `out/CritEvidence/r23-corrections-append.md` to the
round-24 `LOG.md` section and/or `corpus/lessons/round-24.md` (L1's
choice). It does four things:
- Points the 68→69 correction at `corpus/lessons/round-23.md:178`, and
  states that the filed report's falsify accounting (73 seats, 4 dead) is
  already correct.
- Restates the 56 as a count of round-owned fixture processes (`git` plus
  at least 2 gpg daemons) that were killed, with 40 identities retained in
  the session transcript and only 19 of those shown to be FIFO fixtures.
- Names `d1b9d95` `LOG.md:1417-1420` as the text it supersedes, without
  editing that text.
- Leaves the bytes of fleet `410b511` and lane `0df800e` unchanged.

If L1 keeps the prereg wording, the r24 report should still carry this
qualification. Otherwise r24 inherits a provenance error inside its own
correction. ScribeFrontier.md:94-99 independently places both numbers in
the lesson (`:174`, `:178`), not in the filed report.

## Not done / unverified

- No build, test, grid or full-suite run.
- No edits to `LOG.md`, the lesson, the prereg or the fleet report.
- Session reply counts not verified.
- Per-PID FIFO wait state was not observable after the fact; the process
  list in the transcript is the only identity source.
- No tools installed.

Artifacts in `.ufo/waves/round-24/build/out/CritEvidence/`:
- `provenance.txt`
- `r23-ps-listing-line156.txt`
- `r23-ps-classification.txt`
- `r23-corrections-append.md`
