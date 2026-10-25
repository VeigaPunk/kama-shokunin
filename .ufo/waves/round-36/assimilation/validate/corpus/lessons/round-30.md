# kama — round 30 lesson (2026-10-23, attempt 1)

Author: kama L1 round 30 (KamaR30). Base `2aa46e24`; freeze `fdf8cda1`. Two declared claims
(C1 calibration, C2 operability capability), the round-29 spot-check routed repairs, and the
frontier step. Wave evidence: `.ufo/waves/round-30/w1/` (v2 wave, 64 seats) and
`.ufo/waves/round-30/controls/` (14-seat pre-data control call).

## Claims

**C1 (measured, calibration).** Population: 141 self-assessment statements — the 69 the frozen
round-29 extractor finds in SCORECARD.md at base, plus the 72 that two independent round-29 sweep
seats enumerated as outside its reach (`RecallA/missed.json`, `RecallB/missed.json`, read at pinned
revision `6de225c2`). The round-30 counter re-derives each item's class check at its writing
revision W and appends one correction row per non-holding statement. Before: `statements 141
extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True
valid_corrections 0 false_corrections 0 unresolved 13 met False` (`c1/before/c1-base.out`, and the
rows-only arm at the round-29 tip reads `valid_corrections 11 unresolved 2 met False`,
`c1/before/c1-r29-tip.json`). After: see SCORECARD §Round 30 (measured commit and receipt there).

**C2 (capability acquisition, operability).** `tools/instrument-agreement.py` did not exist at base
(`git cat-file -e 2aa46e24:tools/instrument-agreement.py` exits 128). It now runs one instrument N
times over one tree, normalizes only declared volatile fields, and reports an agreement counter;
selftest `IA_SELFTEST pass=4 fail=0` (exit 0) with a nondeterministic arm reading `agree=2
disagree=1`, and two committed receipts read `IA runs=3 agree=3 disagree=0`.

## Gate

New SOURCES rows, each opened this round (sibling own-work, tier A scoped to the transferred
discipline):

| S### | source (path @ revision) | accessed (UTC) | located quote (<=25 words) | opened by |
|---|---|---|---|---|
| S178 | kumitate-shokunin/scripts/counter-rerun.mjs @ ce9aee5; decision note `.ufo/waves/round-48/r48/ReviewQualityDraft.md:123-125` @ 4e4f471 | 2026-10-23T17:0xZ | "the round-48 C2 instrument (scripts/counter-rerun.mjs, plan :107-109) mechanizes the run-agreement half" | L1 (read the sibling file and note this round; reviewer seat RevSourcesS178 re-opens) |
| S179 | mori-shokunin/tools/mori-source-drift.py @ e57c58b; entry `corpus/knowledge/source-drift-r36.md:21` @ 6827d6e | 2026-10-23T17:0xZ | "`fresh` proves only byte identity with the committed copy, never that the row's `teaches` is right." | L1 (same) |

Status: both rows new, `mined`, used-by `corpus/knowledge/instrument-run-agreement.md`. No existing
row changed. Census: 177 → 179 rows; validate exit 0 (`.ufo/waves/round-30/census-end.out`).

Decisions on seat findings: see §Seat findings below (filled from the relays; each row names the
seat and the disposition).

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| scope (the oracle was read at the measured tip, so the base run could not load it) | `.ufo/waves/round-30/c1/preliminary/` first run: `could-not-evaluate: oracle .ufo/waves/round-29/w1/out/RecallA/missed.json missing at tip`, exit 2 | the base receipt itself (exit 2 before any seat) | pin the oracle revision (`ORACLE_REV = 6de225c2…`) and read the oracle blobs at that revision, not at `--tip`; the base receipt at the pin prints `bound 72` |
| number-drift (the oracle sid scheme collided with the extractor's sids) | `count-c1.py` run before the `o` index: `could-not-evaluate: duplicate statement ids`, exit 2 | the counter's own duplicate-sid refusal | oracle sids take an `o` index (`SCORECARD.md:Q:<lsha>:o0`), which the duplicate check then proves unique |
| scope (the H fallback token regex capped at 40 hex chars, so four 64-char digests were unbound) | `c1/preliminary/long-digest-fix.json` run: `oracle 72 bound 68 unbound 4`, `oracle_unbound_items` naming lines 448/953/960/974 | the receipt's `oracle_unbound` field (a bound-completeness counter, not prose) | a long-hex token regex for H (`RE_HEXLONG`, 8-64 chars); the next run reads `bound 72 unbound 0` |
| attribution (the first control-call item for CtlBaseTree named a counter variant whose base-tree check does not reproduce the round-29 arm exactly) | `.ufo/waves/round-30/controls/CtlBaseTree/` | seat report | reported as a bounded arm; it scores the variant, not the lane counter, and its receipt says so |

Each fix is shown able to fail by the named receipt: the pre-fix run's exit/field is committed, and
the post-fix run in the same file set reads the corrected value.

## Run it

```
/usr/bin/python3 .ufo/waves/round-30/count-c1.py --repo <fresh clone> --tip <commit> --out <receipt>
python3 tools/instrument-agreement.py --selftest
python3 tools/instrument-agreement.py --runs 3 --out <receipt> -- <lane instrument>
```

## Seat findings

Pre-data control call (14 arms; receipts `controls/SUMMARY.md`, committed `14bb1a32`). Verbatim
summary lines from the arms' own receipts:

| Arm | Receipt line (tail) | Decision |
|---|---|---|
| CtlR29RowsOnly | `valid_corrections 11 false_corrections 0 unresolved 2 met False` | accept: the "inherit last round's rows" shortcut is real and refused |
| CtlPasteHolds | variant `mismatched_at_base 11 … unresolved 0 met False`; base `unresolved 11` | accept: the paste-holds shortcut is refused by the mismatch count, and its finding — `unresolved == 0` alone is not load-bearing at this tip — is recorded in the SCORECARD limits |
| CtlDuplicate | `valid_corrections 11 false_corrections 2 unresolved 4 met False` | accept: re-correcting a sid revokes the original row |
| CtlJunk | `valid 11 false 5 unresolved 7` | accept: sid identity, not wording |
| CtlNoOracle | `statements 101 oracle 32 … mismatched_at_base 12 unresolved 1` | accept: the population term is load-bearing (three conjuncts fail) |
| CtlAllOracle | `valid 13 false 70 unresolved 70` | accept: row count cannot manufacture the claim |
| CtlAllQ | `valid 6 false 42 unresolved 49` | accept: blanket class correction is charged per holding row |
| CtlLabelKeyed | `valid 0 false 13 unresolved 26` | accept: the observed cell must carry the counter's value |
| CtlWrongObserved | `valid 11 false 2 unresolved 4` | accept: value-keyed, not sid-keyed |
| CtlTamper | unchanged `valid 11 unresolved 2` | accept: replace refs/alternate store did not move the counter (`GIT_NO_REPLACE_OBJECTS=1`) |
| CtlBaseTree | lane copy on the same tree `valid 11 unresolved 2` | **limit**: the seat scored the lane copy; its variant receipt is evidence only, and the arm is not claimed to reproduce the round-29 base-tree result |
| CtlDoNothing | `valid 0 false 0 unresolved 13 met False` | accept: the empty arm |
| CtlEditInPlace | no receipt — a dead seat | record as dead; the append-only conjunct is exercised by the counter's byte-prefix test and by CtlDuplicate's revocation behaviour |
| RefInstrument | `valid 13 false 0 unresolved 0 met True` | accept: the reference policy performs the claimed work; a green here decides nothing about the other arms |

C1 corpus facts confirmed by the arms: the oracle population contains exactly two non-holding items
(both Q: lines 41 and 901), and the whole remaining gap at the round-29 tip was those two.

C2: the agreement tool's own selftest (`c2/selftest.out`) and two receipts (`c2/receipt-a.json`,
`c2/receipt-b.json`) agree 3/3; the corpus guard was refused as a subject
(`c2/receipt-b-corpusguard-refused.json`, `agree=1 disagree=2`) because its output embeds its own
staging path and a digest over the patched wrapper. Recorded in the entry, not normalized away.

Wave-1 seat reports land in `.ufo/waves/round-30/w1/out/<Seat>/`; the L1 integrates them after the
wave settles and reports any seat that dies in the round report.

## Repairs (round-29 verifier spot-check routed items, not claims)

| # | Item | Disposition | Evidence |
|---|---|---|---|
| 1 | two untracked round-29 w2 files | already committed at `40b122d` before this round; verified tracked (`git ls-files`) | `ExecRound29Repairs` evidence; no new write |
| 2 | LOG.md does not name `6de225c2`/`227dd1ee` | appended a hash-naming note in the round-30 LOG entry | `LOG.md` §Round 30 |
| 3 | S174 teaches verbatim mislabel | appended a decision-record correction (append-only) | `SOURCES.md` §Round-30 source correction |
| 4 | S176 teaches vs decision-record mismatch | appended a decision-record correction naming the landed cell | same section |
| 5 | SCORECARD note omits `corpus/lessons/round-2.md:49` | appended the missing location in the round-30 section | `SCORECARD.md` §Round 30 |

## Appended seat findings (round 30, after the control call)

- **CtlTamper** proved its tamper live: an unshielded counter copy on the tampered repo reads
  `mismatched_at_base 11 unresolved 0`, while the frozen counter reads `13 / 11 / 2` unchanged. The
  replacement-object shield is load-bearing; the pinned `mismatched_at_base == 13` independently
  blocks the "make the two lines true" route (it moves the count away from 13). No `refs/replace` or
  `refs/tamper/` remained in the lane after the arm.
- **CtlDoNothing** separated two readings the table conflated: an empty tip reads `unresolved 13`;
  the lane tip with the 11 round-29 rows reads `unresolved 2`. The summary's appended correction
  records both.
- **C2**: `tests/ollama-corpus-guard/check.py` is refused as an agreement subject — its output embeds
  its staging path and a digest over the patched wrapper, so `agree=1 disagree=2`
  (`c2/receipt-b-corpusguard-refused.json`). This is the entry's worked refusal, not a normalization
  gap to paper over.

## Appended calibration note — what carries the append-only rejection

The `CtlEditInPlace` arm (late) reported `append_only False … unresolved 141` for a mid-file rewrite
of the two false lines that cites real retained evidence. Its caveat is recorded here verbatim in
substance: the two oracle mismatches survive the rewrite *because* the counter reads its population
from the base blob (`extract`/`oracle_bind` read `BASE`), so the rejection of that arm rests on the
append-only byte-prefix rule; a future counter that read the tip blob for its population would let
the rewrite flip both oracle items to holding while `append_only` stayed False. Any amendment that
changes the population anchor must re-run this arm; the honest reading is that append-only, not
base-anchoring, is the load-bearing rule against in-place repair.
