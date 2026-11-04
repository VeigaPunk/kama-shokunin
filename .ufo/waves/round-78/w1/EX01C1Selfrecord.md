# EX01C1Selfrecord — round 78 wave 1, seat report

Seat: EX01 (executor, C1 counter build + four-repair demonstration). Lane tip at report:
`2bd07a8aeef822bd6b8b9137df4439f1499b08c9` (`git -C <lane> rev-parse master`). Base
`c62ffd3aea930b98375f805cc3dfb821a703148b`; sealed revision
`6c1550a14babaca092cfcc3106f792d695652200` (verified: object exists, is ancestral to master,
subject "round-77: record the L1's mutating-git breach as a lesson mistake").

## What was built

`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round78-selfrecord-round77.py` (new, 826 lines,
the only file this seat wrote inside the lane besides its receipts/report). It embeds the frozen
§C1 predicate blockquote verbatim as its `PREDICATE` constant, derives F1–F6 from the tree
(`## Axes` table; newest `Capabilities — canonical list as of round <N>` table; the
`| Pre-report gate |` row bound by AST to the gate module's `ARM_SPECS`/`ARM_ORDER` and to the
round-77 committed receipt's tally read at the sealed revision — never by running the gate; the
record's last `corpus/lessons/round-77.md` §-pointer sentence; the knowledge entries introduced
in (record base .. sealed] with `source:`/`source-correction:` `S###` lines; README coverage-map
rows), and grades corrections in `corpus/lessons/round-78.md` §Corrections of the exact frozen
bullet shape. A block is valid only with `at` == the sealed revision, one prose line, a parseable
date; `old` must re-derive at `at` from committed blobs (`git show`, never a checkout), `new`
must equal the frozen value and the live derivation; the second block naming one fact is
reported `duplicate` and reds the run (frozen rule (b) + kill rule). Structural absence of a
graded fact's ground is reported `cheat` (exit 1); missing/unreadable input files, an unreadable
gate module/receipt or CLI misuse exit 2; a missing round-78.md lesson is not exit 2 (it carries
no corrections — the unrepaired base state).

Calibration note (load-bearing): the F3 `newest` component is the gate module's newest arm
(authority), not the row's own max-`arm N` name — the committed pre-freeze enumeration
`.ufo/waves/round-78/measured/before/c1-facts.out` derives F3's stale value as
`gate=arms:8/word:eight/newest:round77-instruments/tally:18` ("newest named=False"), and the
landed counter reproduces that string exactly (plus the module's own 9/round77-instruments and
the receipt's 22 in its consistency check).

## Evidence (absolute paths, command, exit)

1. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/measured/after/c1-selftest.out`
   — `TMPDIR=/fast/scratch/hyaku/kama-r78/EX01C1Selfrecord python3 tools/round78-selfrecord-round77.py --selftest --work …/selftest`, exit 0.
   All eight arms PASS: `base-red`, `green-control` (exact frozen line on the repaired fixture),
   and the six frozen kill arms — `cheat-constant` (deleted gate row → `cheat F3`; a constant
   printer cannot produce a red-with-findings verdict), `stale-uncorrected` (reverted row, no
   block change → `mismatch F3`, corrected=3), `correction-wrong-value` (new=arms:10 →
   `mismatch F3`, not unbacked), `unbacked` (old=arms:7 → `unbacked F3`), `pointer-wrong`
   (record's last pointer sentence names §Mistakes 4 again → `mismatch F4`; last-wins), and
   `duplicate-correction` (second valid F3 block → `duplicate F3`, corrected stays 4, exit 1).
   Final line `SELFRECORD_R77_SELFTEST pass=8 fail=0`. Fixtures live and die under the scratch
   root only; fixture git mutations (init/add/commit) ran with `rev-parse --show-toplevel`
   asserted, mirroring the committed `round76-selfrecord-facts.py` harness; no lane git write.
2. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/measured/after/c1-real-tree.out`
   — `python3 tools/round78-selfrecord-round77.py --repo .` at the lane, exit 1:
   `SELFRECORD_R77 claims=6 mismatches=2 corrected=2 unbacked=0`, findings `mismatch F4`
   (record still points at §Mistakes 4) and `mismatch F5` (register-cutoff-split.md still has no
   `S###` source line). F3 and F6 already re-derive because sibling seats landed those repairs
   uncommitted during this wave (` M SKILL.md`, ` M corpus/README.md`) and SC02Lesson landed
   `corpus/lessons/round-78.md` §Corrections whose four `old` values all re-derive under the
   landed counter (F3/F6 blocks therefore count as corrected=2). The repairs are not this seat's
   to make; the exact old→new bytes for F3–F6 are filed in `repairs.md` (item 5 below) for the
   integration owner. After F4/F5 land, the same command must print the frozen line, exit 0.
3. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/EX01C1Selfrecord/scratch-run.out`
   — `cd /fast/scratch/hyaku/kama-r78/EX01C1Selfrecord/clone && python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round78-selfrecord-round77.py --repo .` after applying the four repairs + four correction blocks in the clone, exit 0:
   `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0` — the frozen line, verbatim.
4. Same directory, `clone-pristine.out` (clone as cloned: mismatches=4, all four stale facts
   named with their derived values — matching the committed enumeration byte-for-byte) and
   `clone-norepair.out` (four correction blocks present, repairs NOT applied:
   `mismatches=4 corrected=0 unbacked=0`, exit 1 — the plan's do-nothing control
   `measured/control/c1-norepair.out` expectation, reproduced).

## Files changed

- `tools/round78-selfrecord-round77.py` (new; imports the committed
  `tools/round76-selfrecord-facts.py` for its `git`/`blob`/`text`/`match`/`section` helpers, the
  established predecessor pattern — no new dependency).
- `.ufo/waves/round-78/measured/after/c1-selftest.out`, `c1-real-tree.out` (receipts above).
- `.ufo/waves/round-78/w1/EX01C1Selfrecord/{repairs.md,scratch-run.out,clone-pristine.out,clone-norepair.out}`.
- This report.

Untouched per seat rules: SCORECARD.md, SKILL.md, corpus/**, registry/**, LOG.md, and every
sibling file. The lane worktree was read only (read-only git: rev-parse/log/show/diff/status/
ls-tree/cat-file/merge-base). Scratch root `/fast/scratch/hyaku/kama-r78/EX01C1Selfrecord`
deleted after the receipts were copied out.

## Risks and blockers

- The real-tree green line depends on sibling/L1 landings (F4 record sentence, F5
  source-correction line — exact bytes in `repairs.md`). The counter is the C1 instrument only;
  C2/C3 counters are sibling seats' modules and were not exercised here.
- Finding-line classes extend the frozen enum with `duplicate` for the second block naming one
  fact (frozen rule (b) declares it "reported duplicate" and the kill rule requires red); all
  other lines match `SELFRECORD_R77_FINDING <mismatch|unbacked|cheat> <fact>` with k=v detail
  after the fact id, and the summary line is byte-stable.
- No installs or upgrades were needed (named item; system python3 + git only).
