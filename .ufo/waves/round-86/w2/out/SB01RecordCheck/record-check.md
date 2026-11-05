# SB01RecordCheck — round-86 self-record vs receipts

Seat: record-check (calibration axis). Lane: `kama-shokunin`.
Scope: the round's **uncommitted self-record text** (`git diff LOG.md`, `git diff SCORECARD.md`)
checked against the actual instrument output.

## Provenance of the text measured

The worktree moved under me twice during this seat. Two distinct record texts exist:

| text | state | how I measured it |
|---|---|---|
| **attempt-1** | uncommitted at dispatch; `git diff LOG.md`/`SCORECARD.md` showed the Round-86 LOG section and a `**Capabilities — canonical list as of round 86**` table with **no separator row** | copied into `/fast/scratch/hyaku/kama-r86/SB01RecordCheck/fixture`, committed there (fixture HEAD `6ffbd1b21fc35b7c16fa41fb1b1849fca946e0bc`), instruments run against it |
| **attempt-2** | uncommitted, then committed by the L1 as `c5d71b7a0455f8f2b46593f6ef48cc92ca765670` (worktree now clean) | measured at `c5d71b7a` directly, and re-measured in a second pristine clone `/fast/scratch/hyaku/kama-r86/SB01RecordCheck/fixture2` |

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse --show-toplevel` = the lane repo for
every read. All fixture commits asserted `rev-parse --show-toplevel` equals the fixture dir first.

## Item-by-item verdict — the numbers the record states

Every command below was run from the lane repo with read-only git; true exit codes are given.

### C1 — rendered-cell identity

| stated | command | output | exit | verdict |
|---|---|---|---|---|
| before `mismatches=3`, exit1 | `python3 .ufo/waves/round-86/count.py c1 --repo . --rev 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d --work $S/d1` | `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85` + 3 `RENDERED_CELLS_FINDING` lines | **1** | **CONFIRMED** — byte-identical to the committed `.ufo/waves/round-86/measured/before/c1.out` |
| after `mismatches=0`, exit0 | same counter, `--rev 67eddac89f44e768b670301ea0feff06e766f32d` | `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85` | **0** | **CONFIRMED** — reproduces `.ufo/waves/round-86/measured/after/c1.out` byte-for-byte at `c5d71b7a` too |
| selftest 11/0 (attempt-1 LOG) | `python3 tools/round86-rendered-cells.py --selftest` on the attempt-1 instrument | `RENDERED_CELLS_SELFTEST pass=11 fail=0` | 0 | **CONFIRMED for attempt-1** (frozen at `c07e1f90`) |
| selftest 14/0 (attempt-2 SCORECARD) | same, on the current instrument | `RENDERED_CELLS_SELFTEST pass=14 fail=0` | 0 | **CONFIRMED** — matches committed `.ufo/waves/round-86/measured/after/c1-selftest.out` (`pass=14 fail=0`) |
| 7 source mutants killed | `.ufo/waves/round-86/measured/after/c1-mutants.out` | `RENDERED_CELLS_MUTANTS mutants=7 killed=7 escaped=0` | 0 | **CONFIRMED** — receipt present and each arm red |

### C2 — owning arms and summary cardinality

| stated | command | output | exit | verdict |
|---|---|---|---|---|
| before `killed=3 escaped=2 arms=unknown` | `python3 .ufo/waves/round-86/count.py c2 --repo . --rev 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d --work $S/d2` | `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5`, M5/M6 `verdict=escaped` | **1** | **CONFIRMED** — byte-identical to committed `measured/before/c2.out` |
| after `killed=5 escaped=0 arms=34 owners=5/5` at the **record's own measured revision** | `python3 .ufo/waves/round-86/count.py c2 --repo . --rev c5d71b7a0455f8f2b46593f6ef48cc92ca765670 --work $S/r3` | `DEBT_MUTANT_OWNERS mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5`; `M6 owner=summary-cardinality verdict=escaped green summary`; `PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0` | **1** | **CONTRADICTED — see correction 1** |

The *same* counter run at the **previous** revision does reproduce the claim:

```
python3 .ufo/waves/round-86/count.py c2 --repo . --rev 67eddac89f44e768b670301ea0feff06e766f32d --work $S/r2
DEBT_MUTANT_OWNERS mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5   EXIT=0
```

So the receipt `.ufo/waves/round-86/measured/after/c2.out` (committed at `c5d71b7a`) is a
**true receipt of `67eddac`**, not of `c5d71b7a`. `diff` of the committed receipt against my
reproduction at `c5d71b7a` differs on three lines (the summary line, the M6 line, the pristine
line). Reproduced in a pristine second clone at the same result, so it is not worktree dirt.

**Mechanism** (`git diff 67eddac..c5d71b7a -- tools/round81-append-debt.py`): the same commit
reverted the debt selftest's summary line to its round-81 shape,
`APPEND_DEBT_SELFTEST pass=<n> fail=<n>` (dropping `arms=<n>`), to keep frozen gate arm 11's
`re.fullmatch(r"APPEND_DEBT_SELFTEST pass=[0-9]+ fail=0")` green. The mutant-owners classifier
(`tools/round86-mutant-owners.py`, `SUMMARY_RE` line 85) makes the `arms=` group optional:
`^APPEND_DEBT_SELFTEST pass=([0-9]+) fail=([0-9]+)(?: arms=([0-9]+))?$`. With `arms=` absent,
the `summary pass+fail != arms` cardinality clause (line 109) can never fire, and the ARMS-line
clauses (lines 111–115) compare the *ARMS* line against the summary's `fail` — never the summary's
`pass+fail` against the arm count. The M6 forgery (`pass=0 fail=0`) therefore reconciles as green.
The plan's frozen population names M6 explicitly (`M6 forge the summary (pass=0 fail=0) →
summary-cardinality`), so M6 is in the frozen population and its escape is a survivor, not a
no-op. The plan's kill rule: "Kill: any survivor, invalid execution, pristine regression, or a
cardinality clause that a forged summary can satisfy." Both clauses fire.

Note this is the same class of defect the round was opened to kill (R85V2: "a dropped arm and a
forged summary both passed"). The revert that fixed gate arm 11 re-armed the forged summary.

### C3 — pin origin corroboration

| stated | command | output | exit | verdict |
|---|---|---|---|---|
| before `could-not-evaluate`, exit2 | `python3 .ufo/waves/round-86/count.py c3 --repo . --rev 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d --work $S/d3` | `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` | **2** | **CONFIRMED** — byte-identical to committed `measured/before/c3.out` |
| after `rows=5 verified=5 mismatch=0 unreachable=0 bad=0`, exit0 | `python3 .ufo/waves/round-86/count.py c3 --repo . --rev c5d71b7a... --work $S/v3` | `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` + 5 `PIN_ORIGIN_ROW ... verdict=verified` | **0** | **CONFIRMED** — reproduces committed `measured/after/c3.out` byte-for-byte |
| selftest 7/0, fabricated-hash-consistent refused | `python3 tools/round86-pin-origin.py --selftest` | `PIN_ORIGIN_SELFTEST_PASS fabricated-hash-consistent verdict=mismatch want=mismatch`; `digest-lie verdict=bad`; `pass=7 fail=0` | 0 | **CONFIRMED** — matches committed `measured/after/c3-selftest.out` |

C3 is the only leg whose committed after-receipt reproduces at the committed tip.

### Source census

| stated | command | output | verdict |
|---|---|---|---|
| 317→319 rows | `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md` (tip) vs `--file $S/SOURCES-base.md` (base `3ff23da3`) | tip `rows 319`; base `rows 317` | **CONFIRMED** |
| A302→304 | same | tip `tier.A 304`; base `tier.A 302` | **CONFIRMED** |
| mined 284→286 | same | tip `status.mined 286`; base `status.mined 284` | **CONFIRMED** |
| `validate` exit0 | `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | `kama ok …/corpus/SOURCES.md`, W01/W04 warnings only | **CONFIRMED** |

### Lesson pointer

`corpus/lessons/round-86.md` is committed at `c5d71b7a`; its three claimed contents are present:
the fenced-shadow false green (line 30, citing the committed
`.ufo/waves/round-85/w1/out/SN01Scope/receipts/fenced-shadow.md` — verified to exist at the tip via
`git cat-file -e`), the round-69 date-ordering exit 2 (line 49, 92), and the R84V5 erratum
(line 80, citing `.ufo/waves/round-84/measured/after/c2-red.out`, verified present). **CONFIRMED.**

### Capability rows — attempt-1 vs attempt-2

| stated | command | output | verdict |
|---|---|---|---|
| 3 new capability rows in the round-86 canonical list | `python3 tools/round42-selfdesc-reconcile.py --repo . --tip c5d71b7a...` | `caps=1`, `detail: caps: head names […49 names…] != canon (round 86) […52 names…]` | **the round-86 list holds 52 names; the head `## Capabilities` mirror holds 49 and does not carry `rendered-cell-identity` / `mutant-owning-arms` / `pin-origin-corroboration`** — the mirror is stale in **both** attempts |
| attempt-1 canonical table is well-formed | `git diff SCORECARD.md` (attempt-1) → `grep '^+|---'` | no match: **no `|---|---|---|---|` separator row** | **CONTRADICTED — see correction 2** |

At attempt-1 the missing separator made the table unparseable by both lane instruments:
`tools/capability-repertoire-audit.py` reported `listed 49 observed 49` (it requires a separator row
whose cells are all in `":- "`, per its `tables()`), and `tools/round42-selfdesc-reconcile.py`'s
`canon()` returned **51** names — it drops the first data row (`late-delta`) because it slices
`rows[2:]`, assuming a header plus a separator. With the separator inserted in the fixture, the
same file yields `listed 52 observed 52 met True` and `canon_rows=52`. **attempt-2 fixed the
separator; the head mirror, §Retired count and §Saturation list are still stale at the tip.**

## Numbered corrections

Each correction gives the exact replacement sentence for the committed record.

### Correction 1 — C2's "after" measurement does not hold at the revision it is filed at

**Contradiction.** The record (LOG.md Round-86 section, and the SCORECARD `### Round-86 measured
results` C2 row) states `killed=5 escaped=0 arms=34 cardinality=ok owners=5/5` exit0 as the
"after" value, and `.ufo/waves/round-86/measured/after/c2.out` is committed with that line. At the
revision that receipt is committed at (`c5d71b7a0455f8f2b46593f6ef48cc92ca765670`), the frozen
counter prints `killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5` with
`M6 owner=summary-cardinality verdict=escaped green summary`, exit **1**. The receipt is a true
receipt of `67eddac`, filed at `c5d71b7a`. Reproduced in a pristine clone.

**Why.** The same commit reverted the debt selftest's summary to `APPEND_DEBT_SELFTEST pass=<n>
fail=<n>` (no `arms=`), to keep frozen gate arm 11 green; the mutant-owners classifier's
cardinality clause reads the optional `arms=` group, so with it absent a forged `pass=0 fail=0`
summary reconciles green and M6 escapes. The plan's kill rule fires ("any survivor" and "a
cardinality clause that a forged summary can satisfy").

**Replacement sentences.**

LOG.md, in the C2 paragraph, replace the after-value clause. Current text:

> `killed=5 escaped=0 arms=34 cardinality=ok owners=5/5` exit0. Production grading bytes unchanged
> outside the selftest.

Replace with:

> `killed=5 escaped=0 arms=34 cardinality=ok owners=5/5` exit0 **at `67eddac89f44e768b670301ea0feff06e766f32d`; at
> `c5d71b7a0455f8f2b46593f6ef48cc92ca765670` the same frozen counter prints `killed=4 escaped=1
> invalid=0 arms=34 cardinality=ok owners=4/5` with `M6 owner=summary-cardinality verdict=escaped
> green summary`, exit1** — the summary-line revert that kept frozen gate arm 11 green removed the
> `arms=` group the classifier's cardinality clause reads, so the M6 forged summary reconciles
> green. Production grading bytes unchanged outside the selftest.

SCORECARD.md, in the `### Round-86 measured results` table, replace the C2 row's before→after cell.
Current text:

> `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` exit1 → `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` exit0; selftest 10/0

Replace with:

> `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` exit1 → `mutants=5 killed=5 escaped=0 invalid=0 arms=34 cardinality=ok owners=5/5` exit0 **at `67eddac89f44e768b670301ea0feff06e766f32d`**; at the committed tip `c5d71b7a0455f8f2b46593f6ef48cc92ca765670` the same counter prints `mutants=5 killed=4 escaped=1 invalid=0 arms=34 cardinality=ok owners=4/5` (M6 `verdict=escaped green summary`), exit1 — selftest 10/0

Also file the correct receipt, or re-measure: `.ufo/waves/round-86/measured/after/c2.out` must
either be regenerated at the tip or carry the revision it measured.

### Correction 2 — the round-86 canonical capability table is not a well-formed table (attempt-1) and the head mirror is stale (both attempts)

**Contradiction.** In attempt-1 the new `**Capabilities — canonical list as of round 86**` table
had no `|---|---|---|---|` separator row, so `tools/capability-repertoire-audit.py` reported
`listed 49 observed 49` (the three new capabilities invisible) and `tools/round42-selfdesc-reconcile.py`'s
`canon()` returned 51 names, silently dropping `late-delta`. **attempt-2 added the separator**
(`git diff SCORECARD.md | grep '^+|---'` now matches at line 39 of the diff), so this half is fixed
and I no longer raise it against the committed tree.

What remains at `c5d71b7a` is the mirror half: the head `## Capabilities` table still lists the
round-83 repertoire (49 names) and does not carry `rendered-cell-identity`, `mutant-owning-arms`
or `pin-origin-corroboration`; §Retired still says "49 capabilities"; §Saturation's first-working
round list still ends at `83`. `tools/round42-selfdesc-reconcile.py --repo . --tip c5d71b7a...`
reports `mismatches=6 met=False` with `retired=1`, `saturation=1`, `caps=1`, `province=3`.

**Replacement sentences.**

SCORECARD.md §Retired — current text:

> None. 6 axes and 49 capabilities remain active.

Replace with:

> None. 6 axes and 52 capabilities remain active (the round-83 repertoire plus
> `rendered-cell-identity`, `mutant-owning-arms` and `pin-origin-corroboration`, first-working
> round 86).

SCORECARD.md §Saturation — current text (tail of the list):

> capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83 (highest canonical list, §Round83).

Replace with:

> capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61, 67, 68, 69, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 86 (highest canonical list, §Round86).

SCORECARD.md head `## Capabilities` — the mirror table's intro and three rows. Current intro ends:

> Mirror of the round-83 canonical capability list that §Round 83 carries

Replace with:

> Mirror of the round-86 canonical capability list that §Round 86 carries

and append the three rows to the mirror table (the canonical rows already committed at
`.ufo/waves/round-86/w2` are the source; copy the three `rendered-cell-identity`,
`mutant-owning-arms` and `pin-origin-corroboration` rows verbatim, with their
`|---|---|---|---|` separator intact).

PROVINCE.md — `tools/round42-selfdesc-reconcile.py` reports `province=3`: it lacks
`tools/round86-rendered-cells.py`, `tools/round86-mutant-owners.py` and
`tools/round86-pin-origin.py`. Each needs the one-line capability entry the round-83 entries
use (see PROVINCE.md lines 380, 393, 398 for the shape).

### Correction 3 — the committed after-receipts carry no revision header

**Contradiction.** The lane's receipt convention is a two-line header naming the measured revision
and command; every prior round's receipt has it (compare
`.ufo/waves/round-85/measured/after/c1.out`, which opens with
`# rev=948dec784a9736b4a36d6a10d303fbee054b19c6` and a `# cmd:` line). The five round-86 after
receipts at `c5d71b7a` open directly with the instrument line — no `# rev=`, no `# cmd:`.

This is not cosmetic. `tools/round72-receipt-tip-binding.py` classifies a receipt without a
`tip=`/`rev=` 40-hex header in its first five lines as **unbound**, and requires the header's
revision to be an ancestor of the tip. With no header, no round-86 receipt can be bound to the
revision it measured — which is exactly the defect that lets correction 1 sit unnoticed: the
receipt's content contradicts the tree, but nothing in the receipt's own header says which tree it
came from.

I could not measure the binding verdict on the real tree: the tool exits 2 before grading, on
`corpus/lessons/round-86.md:6` → `SCORECARD.md:5259`, citing `.ufo/waves/round-86/count.py` as a
receipt path (`RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py)`). The tool
treats a fully-qualified `.ufo/waves/round-<N>/...` token as strictly classified, so a citation of
the counter inside the round's own record section is exit-2, not a skip. **See correction 4.**

**Replacement.** Give each of the five after receipts the standard two-line header, e.g. for
`.ufo/waves/round-86/measured/after/c1.out`:

```
# rev=<the revision actually measured>
# cmd: python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-86/count.py c1 --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev <the revision actually measured> --work <scratch>
```

and use the same for `c2.out`, `c3.out`, `c1-selftest.out`, `c2-selftest.out`, `c3-selftest.out`,
`c1-mutants.out`. Where a receipt is filed at a revision it does not reproduce (correction 1),
either regenerate it there or name the revision it did measure.

### Correction 4 — the round's own record section makes the receipt-binding tools exit 2

**Contradiction.** `tools/round72-receipt-tip-binding.py --repo . --round 86 --tip c5d71b7a...`
exits **2**:

```
RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-86/count.py (SCORECARD.md:5259)
```

and `tools/round74-receipt-claim-binding.py --repo . --round 86 --tip c5d71b7a...` exits **2**
with `RECEIPT_CLAIM_V2 CouldNotEvaluate: base tool could not evaluate:
RECEIPT_TIP_BINDING_UNREADABLE …`. The tool's own docstring says a fully-qualified
`.ufo/waves/round-<N>/...` token "is never filtered: it is classified strictly, so an absent or
non-receipt qualified citation is exit 2, never a silent skip." `corpus/lessons/round-86.md:6`
(`counter `.ufo/waves/round-86/count.py``) and the SCORECARD Round-86 section both cite the
counter by its qualified wave path, and the counter is a `.py`, not a receipt.

I confirmed this is the sole blocker: in my fixture, removing that one qualified citation from
the lesson alone was not sufficient — the same citation in the SCORECARD Round-86 section
reproduces the identical exit 2 — and only when both are removed does the tool proceed to the
next class of finding (the missing receipt headers of correction 3). So both citations must
change, and both must change together.

**Replacement.** In SCORECARD.md's Round-86 section and in `corpus/lessons/round-86.md`, cite the
counter by a repo-relative path rather than a qualified wave path, e.g. replace

> `python3 .ufo/waves/round-86/count.py c1 --repo . --rev <measured> --work <scratch>`

with

> `python3 .ufo/waves/round-86/count.py c1 --repo . --rev <measured> --work <scratch>`

— i.e. keep the command text but ensure the *record prose* cites the counter as
`plans/round-86-claims.md`'s frozen counter rather than as a `.ufo/waves/round-86/...` token, for
example:

> the frozen counter `count.py` in the round's wave directory

so no qualified `.ufo/waves/round-86/...` token names a non-receipt file.

### Correction 5 — the attempt-1 LOG's "Selftest 11/0" is stale in attempt-2

**Contradiction (attempt-1 only).** attempt-1's LOG.md says "Selftest 11/0 with the round-85 false
green as a red arm." At the current instrument that is `pass=14 fail=0`. attempt-2's SCORECARD
already states "selftest 14/0 (11 before the w2 repair)", so the two record files now disagree
about the same number in the same round, and the committed LOG.md still carries the stale 11/0
(verified: `git show c5d71b7a:LOG.md | grep -n "Selftest 11/0"` → line 3555).

**Replacement.** In LOG.md's C1 paragraph, replace:

> Selftest 11/0 with the round-85 false green as a red arm.

with:

> Selftest 14/0 with the round-85 false green as a red arm (11/0 at the frozen freeze
> `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`; the w2 selector-mutant repair added three arms).

## Out of scope / not my seat

- **C2's M6 escape is a claim-level defect, not a record-text defect.** I report it because the
  record *states* a number that does not hold at the revision it is filed at; the fix belongs to
  the L1. I do not propose a repair to the classifier or to the debt selftest.
- The counter executing worktree instrument bytes rather than `--rev` bytes is disclosed in the
  record itself (w2 `CR01SizingControl`); I did not re-litigate it, but note it means every
  `count.py` measurement above is only trustworthy on a clean tree — which the pristine
  `fixture2` clone provides independently for C2.
- Gate arm 11's `re.fullmatch(r"APPEND_DEBT_SELFTEST pass=[0-9]+ fail=0")` is the constraint that
  forced the summary revert; changing it is a gate change and is the L1's call, not mine.
- I did not run `tools/pre-report-gate.py` (the round's own gate) — it is not part of my item and
  the record does not claim a gate result for round 86.

## Commands run (all read-only against the lane; fixtures under my scratch)

```
git -C <lane> rev-parse HEAD / status --porcelain / log --oneline / show / diff / merge-base --is-ancestor / cat-file -e / ls-tree -r
python3 .ufo/waves/round-86/count.py {c1,c2,c3} --repo . --rev {3ff23da3…, c07e1f90…, 67eddac…, c5d71b7a…} --work $S/<dir>
python3 tools/round86-rendered-cells.py --selftest
python3 tools/round86-mutant-owners.py --selftest
python3 tools/round86-pin-origin.py --selftest
python3 tools/round42-selfdesc-reconcile.py --repo . --tip {3ff23da3…, c07e1f90…, 67eddac…, c5d71b7a…}
python3 tools/capability-repertoire-audit.py --repo . [--tip <rev>]
python3 tools/round74-selfdesc-canon.py --repo .
python3 tools/round72-receipt-tip-binding.py --repo . --round {85,86} --tip <rev>
python3 tools/round74-receipt-claim-binding.py --repo . --round 86 --tip <rev>
python3 tools/round68-receipt-pointer-audit.py --repo . --file SCORECARD.md --file LOG.md
python3 tools/round72-round-scope.py --repo . --round 86 --tip master
python3 tools/round81-append-debt.py --repo . --round 86
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh {census,validate} --file … / --root /home/vgpnk/Projects/shokunin kama
```

Fixture repos: `/fast/scratch/hyaku/kama-r86/SB01RecordCheck/fixture` (attempt-1 text committed;
`6ffbd1b21fc35b7c16fa41fb1b1849fca946e0bc` + 3 probe commits) and
`/fast/scratch/hyaku/kama-r86/SB01RecordCheck/fixture2` (pristine clone of the lane at
`c5d71b7a`, unmodified). Both asserted `git rev-parse --show-toplevel` equals their own path
before any commit. Both removed before this report was written.

## Tooling

No tools installed or upgraded for this seat; no `pacman`, no service restart, no network beyond
the public URLs the round's own C3 instrument fetches (the frozen counter's C3 leg did the
live upstream reads; I did not add any).

## Verdict summary

| item | verdict |
|---|---|
| C1 mismatches 3→0, exit 1→0 | **CONFIRMED** (before receipt byte-identical; after receipt reproduces at the tip) |
| C1 selftest 11/0 → 14/0 | attempt-1 CONFIRMED; attempt-2 CONFIRMED; committed LOG.md still stale (correction 5) |
| C2 killed 3→5 escaped 2→0 arms=34 owners=5/5 | **CONTRADICTED at the committed tip** (correction 1) — holds at `67eddac` only |
| C3 exit2 → rows=5 verified=5 | **CONFIRMED** — byte-identical reproduction at the tip |
| census 317→319, A302→304, mined 284→286 | **CONFIRMED** |
| lesson pointer | **CONFIRMED** |
| capability rows | attempt-1 table malformed (fixed in attempt-2); head mirror / §Retired / §Saturation / PROVINCE.md still stale (correction 2) |
| receipt headers | absent (correction 3) |
| record section blocks receipt binding | exit 2 (correction 4) |
