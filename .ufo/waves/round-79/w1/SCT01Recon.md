# SCT01Recon — does the C1 fact set catch a do-nothing round?

Round 79, wave 1, scout. Read-only recon; no lane file was written by any derivation. Scratch root
`/fast/scratch/hyaku/kama-r79/SCT01Recon/` was deleted after the receipts below were copied into
`.ufo/waves/round-79/w1/SCT01Recon/receipts/`.

- Base `ee53f1a25eab93a8ab55bbb877e49e2e731df535`; freeze `331037039c30909aa2163b2d1de22a7964f90420`
  (adds `plans/round-79-claims.md` + `tools/round79-selfrecord-round78.py`, 684 lines; the counter
  is byte-identical at `33103703` and at the seat's lane tip `f7442dea` — `git diff --stat` empty).
- Sealed `7a3cd98243b69fcbee0cc9e31878782bd8459320`; lane tip at run
  `f7442dea53bd8f474293a2252437b5d869801f49`; `git merge-base --is-ancestor 7a3cd98 master` → 0.
- Per-fact hand derivation, commands and outputs: `.ufo/waves/round-79/w1/SCT01Recon/facts.md`.

## 1. The six facts re-derive as the plan says

All six were re-derived from committed bytes at the sealed revision with `git show`/`git rev-parse`/
`git ls-tree` only (details and command output in `facts.md`). Result: F1–F4 fresh, F5 and F6 stale,
declared value strings byte-equal to the frozen §C1 table. Counter `--json` at the lane tip agrees
exactly. This matches the pre-freeze `measured/before/c1-enum.out`
(`SELFRECORD_R78_ENUM claims=6 stale=2 corrected=0`, exit 1).

Receipt: `.ufo/waves/round-79/w1/SCT01Recon/receipts/lane-tip-precorrection.out` —
`python3 tools/round79-selfrecord-round78.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin`,
exit 1, line
`SELFRECORD_R78 claims=6 mismatches=2 corrected=0 unbacked=0 | sealed=7a3cd98… tip=f7442de…`.

## 2. Do-nothing control (built in a scratch clone)

Construction: `git clone --shared <lane> $S/clone`; asserted
`git -C $S/clone rev-parse --show-toplevel` = the clone; `git -C $S/clone checkout -q -B master
33103703` (round-79 tree, plan + counter, no `corpus/lessons/round-79.md`); counter run with
`--repo $S/clone`.

- **V0, freeze tip, zero corrections** — exit 1,
  `SELFRECORD_R78 claims=6 mismatches=2 corrected=0 unbacked=0 | … tip=33103703…`.
  Receipt `receipts/v0-donothing.out`.
- **V1, a committed round-79 record with an empty `## Corrections` section** — exit 1, same
  `mismatches=2 corrected=0`. Receipt `receipts/v1-donothing-record.out`.

**Verdict: the fact set does catch a round that commits no correction.** Structurally, not just
empirically: F5's observed value is `is-tip:false` because `22cce544` is an ancestor of the sealed
revision and can never become it; F6's observed value is `absent` because the sealed tree's 76
blobs under `.ufo/waves/round-78` contain no `mismatches=1` (verified blob by blob). Both observed
values are immutable, so exactly two facts are stale forever, and `mismatches=0` ⟺ `corrected=2`.
A round with no correction blocks prints `corrected=0`, exit 1.

## 3. But a four-line round reaches the target line

The cheapest passing tree adds no change to the round-78 record and runs no instrument:

- **V2, restatement exploit** — a lesson whose blocks sit under `## Prose notes` (the `## Corrections`
  section says "None."), `date=2099-12-31`, a bogus block for a *fresh* fact, and a hand-written
  one-line blob `.ufo/waves/round-79/measured/fake/pre.out` containing only `mismatches=1`:
  exit 0,
  `SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0 | sealed=7a3cd98… tip=eeb994a6…`.
  Receipt `receipts/v2-restatement-exploit.out`.
- **V4, fenced quotation** — a lesson that says *"No correction is claimed this round"* and quotes
  the two block texts inside a ```` ```text ```` fence under "Syntax reference (quoted, not a
  correction)": exit 0, target line. Receipt `receipts/v4-fenced-example.out`.

So the fact set catches "no work landed", not "the work was real". What the claim actually requires
is the textual presence of two value strings and one blob containing a substring.

## 4. Vacuity — facts accepted without the record/tree saying it

1. **F6 is content-only and path-free.** The correction's `new` may be *any* committed path whose
   blob contains the literal `mismatches=1`; `verify_f6` (`:375-381`)
   checks nothing else. A one-line hand-written file satisfies "the pre-correction tip run …
   committed" — no counter invocation, no exit code, no claim count, no `SELFRECORD_R77` prefix, no
   binding to `.ufo/waves/round-78/`. Demonstrated by V2.
2. **Correction blocks outside §Corrections are accepted.** `corrections()` reads the whole
   `corpus/lessons/round-79.md` at the tip (`:387-394`) with no section scoping, unlike the plan's
   scope ruling ("The correction container is `corpus/lessons/round-79.md` §Corrections"). V2's
   blocks under `## Prose notes` answered both facts.
3. **Fenced quotation is not excluded.** The lane's own `receipt-scope` capability and
   `fenced-quotation-scope` knowledge entry exclude fenced quotation from citation populations; this
   counter parses a fenced syntax example as a live correction (V4), contradicting the lesson's
   prose. The regex runs over `norm(raw)`, i.e. one whitespace-collapsed line.
4. **`date` is format-checked, not bound.** `CORRECTION_RE` requires only `\d{4}-\d{2}-\d{2}`
   (`:383-384`); `date=2099-12-31` was accepted (V2).
5. **`at` is string-compared, not resolved.** `at_ok = block["at"].lower() == sealed.lower() and
   len(block["at"]) == 40` (`:412`); the plan says "40 hex, resolving to it". Only reachable
   difference is a false accept of an uppercase spelling of the sealed SHA (harmless) and no
   `git rev-parse --verify` at all (kill-rule language not implemented literally).
6. **A block for a fresh fact is silently dropped.** V2's `corrected F1 old=lowest-axis=calibration:7
   new=lowest-axis=calibration:0` (a `new` that cannot re-derive) is never examined because
   `matched` is computed only for stale facts (`:408-411`); the run reports `unbacked=0` and prints
   the target line. The plan's kill rule says the claim fails "if any correction's `new` value does
   not re-derive" — the counter does not enforce that for fresh or unmatched facts.

## 5. Insensitivity — a wrong record value survives the constant

Built with the counter's own `build_fixture()` (fixture repo asserted to be its own toplevel),
then committed a mutated sealed record and scored it.

- Record changed to say `attack 4/12 = 90 %` and `two new: \`entry-x\`, \`entry-y\`` (neither entry
  exists; the actual entries are `entry-a`/`entry-b`), plus corrections at the new sealed:
  exit 0, `claims=6 mismatches=0 corrected=2 unbacked=0`; F2 and F3 reported **fresh**.
  Receipts `receipts/insens-record-wrong-values.out`, `receipts/insens-enum.out` (`stale=2` only),
  `receipts/insens-scored.out`.
  - Cause: `value("wave", …)` omits `pct` (`:223-228`); the record's `= 33 %` clause is parsed into
    `declared["pct"]` and never compared. `value("population", …)` omits `names` (`:219-222`); the
    `f2()` name-set adjustment (`:303-307`) mutates a field the value string never reads — dead
    code.
- Record changed to `Population at \`rev=0000000\`` (a non-existent revision): F2 still **fresh**,
  `SELFRECORD_R78_ENUM claims=6 stale=2`. Cause: `f2()` never parses the named revision and
  `population_observed` always derives at `--sealed`.
- Sensitivity that does hold: a wrong `old=` token leaves the fact uncorrected —
  `mismatches=1 corrected=1`, exit 1. Receipt `receipts/v3b-wrong-old-explicit.out` (run with
  explicit `--tip v3`). Duplicate blocks also fail (counter's own `duplicate-correction` arm).

## 6. Three implementation defects/fragilities found on the way

1. **Module docstring describes a different fact set.** Lines 23–26 name F1 "axes" (the
   `"Scores hold: …"` sentence vs the `## Axes` table) and F2 "capabilities" (the canonical table),
   copied from round 78's `tools/round78-selfrecord-round77.py`. The code implements F1
   lowest-axis and F2 population, which is what the frozen plan's table says. The docstring
   contradicts both the plan and its own `Record.facts()`; an operator reading the module header
   would grade the wrong facts.
2. **`--tip` is split-brain.** `audit()` reads corrections at the passed `--tip`, but every
   `verify_f1…f6` hardcodes the literal `"master"` (`:349-381`), while the facts' *observed*
   derivations use the sealed revision. With the frozen command (`--repo .`, default `--tip
   master`) they coincide.
   In a clone with HEAD on another branch, `--repo .` graded `master`'s lesson, not the checked-out
   tree (receipt `receipts/v3-default-tip-is-master.out` shows the exploit tip's line while
   `v3` held the wrong-`old` lesson).
3. **Latent F1 tie.** `min(ASSIGNED_AXES, key=…)` returns the first minimal element, i.e.
   `operability` on a tie, while the declared axis is hardcoded `calibration`; a sealed table with
   both assigned axes equal would make the record's F1 sentence never fresh (correction-only). The
   sealed table is 8/7, so this is latent, not live.

## 7. Line-format caveat

The physical summary line is
`SELFRECORD_R78 claims=6 mismatches=0 corrected=2 unbacked=0 | sealed=<40-hex> tip=<40-hex>`.
The plan's target and the pre-freeze receipts quote only the prefix. An exact whole-line equality
check fails; the claim can only be graded by prefix/substring (or by stripping the `| …` suffix).

## 8. Answers to the assigned question

- **Does the fact set catch a do-nothing round?** Yes for a round that commits no correction blocks:
  control prints `mismatches=2 corrected=0`, exit 1, and can never reach `mismatches=0 corrected=2`
  (F5/F6 staleness is fixed by sealed bytes).
- **Can a round pass without doing the claimed work?** Yes: a lesson containing two value-bound
  blocks (outside §Corrections, future-dated, even fenced as a non-claim) plus a one-line blob
  containing `mismatches=1` prints the target line, exit 0. No instrument is run, no round-78 byte
  changes. The F6 "reproduced pre-correction receipt" can be hand-written.
- **Vacuity named:** F6 (any blob with `mismatches=1`), correction container (§Corrections not
  enforced), fenced-quotation exclusion (absent), correction date (format only), fresh-fact
  correction blocks (silently ignored despite the kill rule).
- **Insensitivity named:** F3 `pct` (90 % survives), F2 new-entry `names` (nonexistent entries
  survive), F2 named population revision (`rev=0000000` survives).

## Receipts (absolute paths, command, exit)

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-79/w1/SCT01Recon/receipts/`:

| File | Command (fixture/clone state) | Exit |
|---|---|---|
| `lane-tip-precorrection.out` | `python3 tools/round79-selfrecord-round78.py --repo <lane>` at `f7442dea`, no lesson | 1 |
| `v0-donothing.out` | `--repo $S/clone` with `master=33103703`, no lesson | 1 |
| `v1-donothing-record.out` | same clone, committed empty `## Corrections` lesson | 1 |
| `v2-restatement-exploit.out` | same clone, blocks under `## Prose notes`, `date=2099-12-31`, bogus F1 block, one-line `pre.out` | 0 |
| `v4-fenced-example.out` | same clone, blocks only inside a ```` ```text ```` fence, prose says none claimed | 0 |
| `v3-default-tip-is-master.out` | same clone, `--repo $S/clone` while HEAD on `v3`; graded `master` | 0 |
| `v3b-wrong-old-explicit.out` | same clone, wrong `old=` for F5, `--tip v3` | 1 |
| `insens-record-wrong-values.out` | `git show 2edc3012:SCORECARD.md` excerpt: `90 %`, `entry-x`/`entry-y` | 0 |
| `insens-enum.out` | `--sealed 2edc3012 --tip 65cfddc5 --enumerate` (mutated seal, corrections present) | 1 |
| `insens-scored.out` | `--sealed 2edc3012 --tip 65cfddc5` scored | 0 |

Failure text of the one dead run (mine, recorded honestly): the first attempt to run the synthetic
fixture's own `tools/round79-selfrecord-round78.py` failed with
`python3: can't open file '…/insens/fixture-golden/tools/round79-selfrecord-round78.py': [Errno 2]
No such file or directory` (the fixture carries no tool); the run was repeated with the lane
counter and `--repo <fixture>`, which is the receipt shown. No tool was installed or upgraded.

## Remaining unknowns

- `--selftest` was not run here (seat scope is C1 recon; the selftest tally belongs to C1's own
  certification / C2's gate arm). The nine arms are visible in source and match the docstring.
- The F1 tie case and uppercase `at=` were reasoned from source, not exercised on the lane.
- Whether a grader matches the target line exactly or by prefix is outside this seat; the physical
  line carries a `| sealed=… tip=…` suffix (see §7).
