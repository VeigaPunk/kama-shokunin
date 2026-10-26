# S8Sample2 — KQ65 hand-read claim-outcome sample (round 46, lane kama)

**Verdict: delivered — 148 hand-labelled claim-outcome lines from the two named
sources over rounds 22-33, every row byte-equal to `git show` bytes
(148/148, 0 mismatches, 23 sources); no claim-outcome reader was written, run
or invoked.**

Axes named (Godspeed): calibration is the judged axis. This seat moves it by
committing the unannotated-before sample that round-45 closure D1 requires to
exist before any reader is frozen; the sample's own quality proxies are
recall (24/24 named sources read end to end, 4,181 physical lines) and
integrity (all 148 rows re-read from git bytes, 0 mismatches).

## What was produced

- `sample.tsv` — 148 rows, header
  `round	claim	side	path	rev	line	outcome	phrasing	text`,
  tab-separated, exactly 9 fields per row (`awk` check: `malformed_rows=0`,
  exit 0). Paths are repo-qualified (`fleet:` = `/home/vgpnk/Projects/shokunin`,
  `lane:` = `kama-shokunin`) so a path+rev pair identifies one file
  unambiguously. Tabs inside line text are escaped as `\t` (none occurred).
  sha256 `c27b223df55348a0b9c1299c84cbad8ad2def01e398445bd9016dc4cd56b1e36`.
- `build_sample.py` — assembler only, no classifier: every label is literal
  table data, and the script asserts each hand-picked line number still carries
  the hand-read text before writing the TSV.
- `sample-lines.out` — the 148 fetched lines (truncated to 220 chars) with
  source revisions; the audit surface for the labels.
- `unlabeled.md` — the note of lines **not** labelled plus every boundary
  decision (15 items).
- `checks.out` — commands, outputs and exit codes below.

## Sources, revisions, and why rounds 22-23 use MANIFEST.json

```
$ git -C /home/vgpnk/Projects/shokunin show HEAD:.ufo/reports/round-N/kama.md      # N=22..33
   exit 0 for all 12; fleet HEAD = 9b676be886e1e2a428fa81321a05a16363ca68ac
$ git -C .../kama-shokunin show 4a2a4d55...:corpus/lessons/round-22-verifier-spotcheck.md
   exit=128   (absent)
$ ... round-23-verifier-spotcheck.md
   exit=128   (absent)
$ ... round-24-verifier-spotcheck.md
   exit=0     (N=24..33 all exit 0)
$ git -C /home/vgpnk/Projects/shokunin show HEAD:MANIFEST.json
   exit 0; 26,385 lines; closure entries at MANIFEST.json:11333-11394 (round 22)
   and 12023-12066 (round 23)
```

Lane closure revision `4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`; fleet
revision `9b676be886e1e2a428fa81321a05a16363ca68ac`. Per-source line counts and
sha256 of every dump are in `checks.out`.

## Claim declarations per round (the key the sample labels against)

Extracted from each round's frozen preregistration (`git show
4a2a4d55...:.ufo/waves/round-N/preregistration.json`, exit 0) and the report's
own declaration:

| round | declared claims | source of declaration |
|---|---|---|
| 22 | C1 | report line 5; `MANIFEST.json:11355` `claims.C1` |
| 23 | C1 | report line 5 |
| 24 | C1 | `preregistration.json` key `claim`; report line 5 |
| 25 | C1, C2 | `preregistration.json` `claims` |
| 26 | C1 | `preregistration.json` `claims` |
| 27 | C1, **X1** | C1 in `preregistration.json`; X1 in `.ufo/waves/round-27/a3/plan.json` |
| 28 | C1 | `preregistration.json` `claims` |
| 29 | C1 | `preregistration.json` `claims` |
| 30 | C1, C2 | `preregistration.json` top-level `C1`,`C2` |
| 31 | C1, C2, C3 | top-level `C1`,`C2`; `preregistration-c3.json` |
| 32 | C1, C2 | `preregistration.json` `claims` |
| 33 | C1, C2 | `preregistration.json` `claims` |

## Method (hand read; no reader)

Both sources per round were dumped and read end to end (4,181 physical lines,
plus the two MANIFEST closure entries). A line entered the sample when it names
a claim id — or sits in a block that names one (a `### C1` heading, a per-claim
table, a `Claim verdicts` paragraph) — **and** carries an outcome (verdict word,
or a predicate value such as `met True` / `unresolved 0` / `complete=n/4`).
Declarations and targets without a verdict word were excluded. `outcome` is the
claim's status as the line states it:

- `met` — predicate/target satisfied or claim verified (64 rows)
- `not-met` — miss / `NOT ACHIEVED` / predicate False on the claim's own
  revision (34 rows)
- `unprovable` — not established, does not verify, not admitted, or cannot
  discriminate (30 rows)
- `partial` — bounded part verified, whole clause unproven, or a disclosed
  harm/limit attached (16 rows)
- `unprovable-but-better` — the closure's exact label (3 rows, round 27 X1)
- `mixed` — one line carrying differing outcomes (1 row)

`phrasing`: `measurement-only` 43, `outcome-word` 33, `table-row` 30, `other`
21, `qualified-met-not-admitted` 10, `manifest-field` 8, `multi-claim-line` 3.
`side`: `self` 85 (lane report), `outside` 63 (closure).
`claim`: C1 109, C2 15, C3 3, X1 6, `(multi)` 6, `(entry)` 9.

## Findings for the future reader (each is a calibration trap this sample encodes)

1. **Claim ids are not stable across rounds; `(round, claim)` is the only safe
   key.** C1 is the *calibration* claim in 22, 23, 25, 29, 32, 33 but the
   *depth* claim in 26, 27, 28, 31; round 30's C1 is calibration while round
   31's C2 is calibration and its C1 is depth. A reader keyed on the claim id
   alone will merge different surfaces. Evidence: the preregistration table
   above plus `sample.tsv` columns 1-2.
2. **Round 23's closure entry has no claim-keyed outcome at all.**
   `fleet:MANIFEST.json:12024-12066` carries `admitted`, `verdict`, `verdicts`
   (axis-keyed) and prose `notes`, but no `claims` block (round 22 has one at
   `11355`). The only claim-level statement is inside prose:
   `MANIFEST.json:12065` ("REJECTED-HARMED despite verified bounded C1").
   Shown by `grep -n '"report": ".ufo/reports/round-2[23]/kama.md"' MANIFEST.json`
   → `11381` and `12051` (exit 0), then a line-range print of `MANIFEST.json:
   12023-12066`; the file is 26,385 lines.
   Proposed fix (not applied — the file is frozen and outside this seat):
   require a `claims.<id>.verdict` field in every future lane closure entry, and
   record round 23 as a known asymmetric gap rather than retro-fitting it.
3. **The axis map is ambiguous with the claim verdict.**
   `MANIFEST.json:12037-12043` maps axes; `12038` (`calibration: improved`)
   is the only structured value that matches round 23's declared claim, and it
   coincides with the closure's axis trend. I labelled `12038` as claim C1 with
   `phrasing=manifest-field`; a reader must not treat an axis value as a claim
   verdict without checking the claim's declared axis.
4. **Counter-level `met True` is not claim credit.** Round 26's own report
   records the frozen counter met by a 12-row echo shortcut
   (`fleet:.ufo/reports/round-26/kama.md:124`), round 28's by a type-only
   control (`:57`), round 31's C1 by a twelve-row no-op and C3 by an
   occurrence-only gate (`fleet:.ufo/reports/round-31/kama.md:81`, `:91`).
   Ten rows in the sample carry `phrasing=qualified-met-not-admitted`
   ("met on the frozen counter; NOT admitted"); all are `unprovable` as claim
   outcomes. A text reader that matches `met True` will score 10 rows wrong.
5. **Before-state receipts are not claim failures.** Eight rows print
   `met False` / `met=False` at a base revision (round 28:126, 29:98,
   30:17-18, 32:74, 33:83 and 89, spot:29:28, spot:30:30). They are labelled
   `not-met` *revision-relative*; read as claim failures they inflate the
   failure count by 8.
6. **Round 22's fleet report has no per-claim verdict section.** Its C1 outcome
   exists only inside the declaration line `:5` ("verified narrow improvement")
   plus component rows `:69-70`. A reader that requires a `Verdict:` or a
   per-claim heading finds nothing and scores round 22 as "no claim outcome".
7. **Round 27 declares X1 outside the C1..C3 namespace.** X1 is the round's
   real discernment claim and the only claim the closure ruled
   `unprovable-but-better` (`spot:corpus/lessons/round-27-verifier-spotcheck.md:25`,
   `:91`, `:176`). A reader restricted to C1..C3 loses 6 rows and the round's
   only favourable non-met ruling. The sample uses claim id `X1`.
8. **Axis rows are not claim rows.** `spot:round-24-verifier-spotcheck.md:140`
   (`| operability | unprovable |`) and
   `spot:round-30-verifier-spotcheck.md:47-50` ("no depth claim", …) are axis
   verdicts / non-claim declarations; round 24's only claim is on calibration.
9. **Round-level admission fields need a label of their own.** `MANIFEST.json`
   entry-level `admitted` / `verdict` (22:11345-11346, 23:12035-12036) are not
   keyed to a claim; the sample labels them claim `(entry)` (9 rows) instead of
   guessing an attribution.

## Limits / out of scope

- Only the two sources the item names were sampled. The lane's own
  `corpus/lessons/round-N.md`, each round's `SCORECARD.md` row, and the
  `MANIFEST.json` `verification`/`notes` prose for rounds 24-33 also carry claim
  statements; they are outside this control and were not labelled.
- Reproduction: `build_sample.py` reads the dumped sources under
  `/fast/scratch/hyaku/kama-r46/S8Sample2/src/` (dump commands in its
  docstring; source sha256s in `checks.out`). That scratch tree is removed, so
  re-running requires re-dumping the same revisions first; the TSV itself is
  the committed artifact and every row re-reads byte-exact from git (see
  `checks.out`, `rows=148 mismatches=0`).
- The sample is one seat's hand read. There is no second reader by design: the
  control exists so a *future* reader can be scored against it, and writing one
  now would defeat round-45 closure D1.
- Known inter-reader disagreements inside the sample: `r24:5` carries two
  verdict words for one claim ("NOT ACHIEVED" and "unprovable in full");
  `r26:123` carries a before and an after value on one row; `spot:r31:25`
  carries a control `met True` and "Claim falsified" on one line. These are
  recorded, not resolved away.
- No counter (C1/C2 of round 46), no frozen control, and no lane file was
  written; `preregistration.json`, the two counters and `controls/` were not
  touched. This seat has no round-46 claim to score.

## Hygiene

- No reader written or executed; no subagents; no services started/stopped;
  no `pacman`; no tool installed or upgraded (nothing was needed).
- Lane and fleet repos read-only: all commands were `git show` / `git ls-tree`
  / `git log` reads. Nothing in `kama-shokunin` was edited except this report
  and `w1/out/S8Sample2/`.
- Scratch `/fast/scratch/hyaku/kama-r46/S8Sample2` removed after the receipts
  below were written.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2/sample.tsv`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2/build_sample.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2/sample-lines.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2/unlabeled.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2/checks.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-46/w1/out/S8Sample2.md` (this report)
