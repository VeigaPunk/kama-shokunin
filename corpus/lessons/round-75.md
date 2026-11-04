# kama round 75 — lesson

Round 75 (attempt 1), base `dc58e51315e79d36df5fc530c95fbd3aecbf7593`, freeze commit
`0908bab5cbf0ab6b435144fc525a3e18443dc08f`. Claims: C1 calibration (interpretation pins), C2
operability (survivor probe + two arms), C3 freshness (append-only accepted-history accounting
+ contract declarations). Frozen plan: `plans/round-75-claims.md`.

## Mistakes

1. **`unarmed-rule`** — a documented rule with no selftest arm, caught only by mutation.
   `tools/round74-receipt-claim-binding.py`'s docstring declares that conflicting headers inside
   the first five lines "stay a finding source (`unbound`), never a crash", and that the header
   window is five lines; no arm graded either. Two semantic mutants of the shipped module
   (`c2_conflict_off`, `c2_header_window`) shipped green at `pass=9 fail=0`.
   *Evidence:* `.ufo/waves/round-75/measured/before/c2-mutants.out`
   (`CONTROL_C2 killed=3 escaped=2 … c2_conflict_off=escaped c2_header_window=escaped`).
   *Captured-by:* none at base — the round-74 mutation matrix (MT01) covered a prototype and the
   case-hex class, not these two; a docstring is not an arm.
   *Fix:* `tools/round75-survivor-probe.py` plus the two new module arms
   (`conflicting-headers`, `header-window-fifth-line`). *Shown able to fail:* with either arm
   reverted the probe prints `SURVIVORS2_FINDING c2_conflict_off|… escaped` and exits 1; the
   landed run is `mutants=5 killed=5 escaped=0`.

2. **`disclosed-not-graded`** — an interpretation disclosed in prose is not a graded reading.
   The round-74 record discloses two interpretation debts (F1b older-demonstrated `total`
   semantics; F2c revision-mention context) and the round-74 closure routed them. Mutating
   either reading in the shipped module leaves its full selftest green (`pass=11 fail=0` for
   `total`, `pass=9 fail=0` for the literal any-hex reading).
   *Evidence:* `.ufo/waves/round-75/measured/before/c1-mutants.out`
   (`CONTROL_C1 killed=0 escaped=2`).
   *Captured-by:* none — no instrument read either disclosure.
   *Fix:* `tools/round75-interpretation-pins.py` binds each reading to a boundary fixture with a
   mutated-reading leg. *Shown able to fail:* a pin whose mutant equals its declared value is
   reported `escaped` and exits 1 (`INTERPRETATION_PINS_FINDING`), and the selftest's cheat arm
   scores exactly that build red.

3. **`carried-red`** — a red counter with no owner is carried, not tracked. The append-only
   audit has reported five unbound contract declarations (`bad_declarations=5`) since its
   round-51 form; the round-73 closure routed it and round 74 disclosed it again without a fix.
   *Evidence:* `.ufo/waves/round-75/measured/before/c3-audit.out` (`CONTROL_C3 summary … bad_declarations=5`).
   *Captured-by:* the audit's own counter (it never passed silently); the miss is that a red
   with no due round is invisible to the round contract.
   *Fix:* the five `declared_at` pointers re-point at `registry/append-only-declarations.md`,
   and `tools/round75-append-accepted.py` fails on any unbound declaration.
   *Shown able to fail:* re-pointing one row back at the old line makes the tool print
   `APPEND_ACCEPTED_FINDING bad-declaration …` and exit 1.

4. **`generated-artifact-shape`** — a generated dispatch that the consumer cannot read. This
   round's first `ufo-swarm-wave.mjs plan --emit-tasks` output is a bare tasks array; the
   in-session dispatcher reads `taskCall.context` + `taskCall.tasks`
   (`/home/vgpnk/Projects/shokunin/scripts/hyaku/inline-dispatcher.py:250`), so that shape would
   have spawned nothing.
   *Evidence:* the round's spec generator (a control input, not a receipt) now asserts the
   shape; the rejected first output was not committed.
   *Captured-by:* none mechanical; the dispatcher contract document is the only trace.
   *Fix:* the generator asserts `taskCall.tasks` after emitting, and the ready file is
   written only after that assert. *Shown able to fail:* feeding it an `--emit-tasks` array raises
   `AssertionError` (the check is on the loaded JSON, not on a flag).

## Gate

Source opened this round (row S547, `gitattributes(5)`):

- URL: `https://git-scm.com/docs/gitattributes`, access date 2026-11-04 (live fetch).
- ≤25-word located quote (16 words): "Line endings are normalized to LF in the index every time
  the file is checked in" — located in the `text` attribute paragraph of the ATTRIBUTES section
  (the sentence continues "…even if the file was previously added to Git with CRLF line
  endings" and explains the round-65 `S537` LF re-land class).
- Tier A, status `mined`; used-by `corpus/knowledge/append-only-accepted-history.md`.
- Refusals: none this round; the assimilation package still refuses on its nine staged-id
  collisions (re-derived read-only, receipt under `.ufo/waves/round-75/assimilation/`).

## considerthese

One still-unimplemented proposal mined, from `considerthese/2026-10-26.md` (2026-10-26), proposal 2
("track what happens to my own proposals"): each daily file tracks whether its own proposals were
taken up, and nothing carries that disposition forward. This lesson is the first instance — every
proposal in the two newest files, re-opened this round, with the round or artifact that took it up:

| Proposal (file, number) | Disposition | Evidence re-opened this round |
|---|---|---|
| `2026-10-25.md` 1 — recompute every digest and S-id a new lesson cites | taken up: digests by round 42, hex/S-id runs by round 43 | `tools/digest-ledger.py`, `tools/hexrun-census.py` |
| `2026-10-25.md` 2 — watch version pins for upstream releases | taken up round 41 | `tools/pin-watch.py` |
| `2026-10-25.md` 3 — ledger of staged items the lane keeps rejecting | taken up | `registry/staged-refusals.tsv` |
| `2026-10-25.md` 4 — report seat yield per wave | taken up | `tools/seat-yield.py` |
| `2026-10-26.md` 1 — flag deletions in append-only files the morning after | taken up this round, lane-side and stronger (audit events + the accepted-history register), not as a daily GitHub pass | `tools/append-only-audit.py`, `registry/append-only-accepted.tsv`, C3 |
| `2026-10-26.md` 2 — track what happens to my own proposals | **this table is the first instance**; a standing ledger stays open | this lesson |
| `2026-10-26.md` 3 — running count of counters a shortcut can satisfy | taken up | `tools/shortcut-tally.py` |
| `2026-10-26.md` 4 — report the pin gap every morning | taken up | `tools/pin-watch.py` |

## Freeze divergences (recorded, not rewritten)

- The frozen plan §C3 says the five unbound `declared_at` pointers are re-pointed at declaration
  lines "appended to `corpus/README.md` (`## Append-only declarations (round 75)`)". The landed
  repair instead appends them to `registry/append-only-declarations.md`, which is the file the
  item spec names (it keeps `corpus/README.md` single-writer for the coverage-map duty). The
  claim's predicate, counter and target are unchanged: `APPEND_ACCEPTED … bad_declarations=0`.
- Sentinel SN01Register's high finding (a register row could bless a deletion made *after* the
  register's introduction) and its provenance finding (the register was read from the worktree)
  are adopted in the landed counter: every row's commit must precede the register's introduction
  commit (`post-introduction` finding) and the register is read from the audit's `to` revision
  (`git show <to>:registry/append-only-accepted.tsv`). Both tighten the counter; neither widens
  the claim.

## RVW01 exit-map note (round-74 routed defect 6)

Pinned, not retired: a plain-directory fixture and a non-git repository are both
*would-not-evaluate* for the round's counters, so exit 2 covers them together; the wording "not a
git repository" is the special case of the general could-not-evaluate class, and no counter claims
to distinguish the two. The ruling is recorded here so the next round does not re-open it.

## Assimilation

No `merge/kama/` entry is adopted this round (id-collision guard and quarantine slice re-derived
read-only). The rationale is in the report's Sources & frontier section.


## Superseded bytes (held verbatim so the audit grades the edit restored, not undisclosed)

Round 75 rewrote the §Mistakes 4 evidence pointer once in place; the register's cutoff forbids
accepting a post-introduction deletion, so the superseded lines are kept here byte-exactly and the
audit's event grades restored:

``````text
   *Evidence:* `.ufo/waves/round-75/controls/build-spec.py` (the emit step now asserts the
   *Fix:* `controls/build-spec.py` asserts `taskCall.tasks` after emitting, and the ready file is
   *Evidence:* the round's spec generator (a `.py` control input, not a receipt) now asserts the
   shape; the rejected first output was not committed.
   *Captured-by:* none mechanical; the dispatcher contract document is the only trace.
   *Fix:* `controls/build-spec.py` asserts `taskCall.tasks` after emitting, and the ready file is
   written only after that assert. *Shown able to fail:* feeding it an `--emit-tasks` array raises
   `AssertionError` (the check is on the loaded JSON, not on a flag).
``````

## Restored paragraph (the superseded Mistakes 4 text, kept verbatim)

The append-only contract forbids deleting the original pointer, so it is restored here exactly as
first filed; the reworded lines above stand as the correction:

```
   *Evidence:* `.ufo/waves/round-75/controls/build-spec.py` (the emit step now asserts the
   shape); the rejected first output was not committed.
```
