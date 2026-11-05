# MT01SelectorMutants (round 86, w3) — mutating C1's selector beyond the committed driver

Seat: leaf mutation-tester. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, terminal record
`bafae7afb41843564ac2468d28beb8e0bb98e8e6`. All source edits were made on copies under
`/fast/scratch/hyaku/kama-r86/MT01SelectorMutants/`; the lane was read-only (no git/jj mutation).
Receipts: `receipts/`, mutant sources: `src/`.

Pristine instrument identity (lane bytes vs scratch bytes):

```
$ sha256sum tools/round86-rendered-cells.py
f9d36b5be0683fdc486da343f6c3aa2e140f250efc94c377ddda1a36ba6e633b  tools/round86-rendered-cells.py
$ git -C <lane> show bafae7afb41843564ac2468d28beb8e0bb98e8e6:tools/round86-rendered-cells.py | sha256sum
f9d36b5be0683fdc486da343f6c3aa2e140f250efc94c377ddda1a36ba6e633b  -
```

## 1. Committed driver, re-run (task item 1)

```
$ python3 .ufo/waves/round-86/measured/after/c1-mutants.py <copy>
a-fence-off: exit=1 red_arms=fenced-shadow,tilde-fence-shadow,unclosed-fence-fails-closed
b-comment-off: exit=1 red_arms=comment-shadow
c-correction-off: exit=1 red_arms=correction-shadow
d-authority-indent: exit=1 red_arms=indent-shadow
d2-row-indent: exit=1 red_arms=indent-row-shadow
f-tilde-off: exit=1 red_arms=tilde-fence-shadow
e-receipt-bytes-off: exit=1 red_arms=contradictory-receipt,revision-carries-no-receipt
g-newest-path-off: exit=1 red_arms=names-other-receipt
h-container-off: exit=1 red_arms=list-fence-shadow
i-backtick-info-off: exit=1 red_arms=backtick-info-not-a-fence
RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0
exit=0
```

**Confirmed: mutants=10 killed=10, every kill attributable to a named arm** — not just "exit 1".
Baseline selftest in the same run: `RENDERED_CELLS_SELFTEST pass=17 fail=0`, exit=0
(`receipts/01-baseline.out`).

## 2. Five new mutants (task item 2), each a one-line source edit

Each row is a real edit of a copy of the committed instrument; `diff` and `--selftest` output are in
`receipts/02-mutant-<id>.out`. Verdict = does some selftest arm go red.

| id | rule disabled | edit (line of committed tool) | selftest | verdict |
|----|---------------|-------------------------------|----------|---------|
| **MA** | column-0 requirement on the **authority** paragraph | `select_cells`: `AUTHORITY.match(line)` → `AUTHORITY.match(line.lstrip())` (226) | `pass=16 fail=1`, red arm `indent-shadow` (`mismatches=2 gate=1`, expects gate=False and 3 mismatches) | **killed** |
| **MB** | column-0 requirement on the **calibration row** | `select_cells`: `CALIBRATION.match(line)` → `CALIBRATION.match(line.lstrip())` (229) | `pass=16 fail=1`, red arm `indent-row-shadow` (`mismatches=1 gate=0 closure=1 disposition=1`) | **killed** |
| **MC** | "first top-level cell wins" (accept a later top-level duplicate authority line) | `select_cells`: `if authority is None and AUTHORITY.match(line)` → `if AUTHORITY.match(line)` (226) | `pass=16 fail=1`, red arm **`backtick-info-not-a-fence`** (`mismatches=3 gate=0`, expects gate=True/closure=False/2) | **killed, but by an arm that does not own the rule** — see §3 |
| **MD** | coupled assertion (accept a banner whose receipt token belongs to a different paragraph) | `grade`: `gate_fact(tree, authority, gate_newest)` → `gate_fact(tree, authority + "\n" + rendered(score), gate_newest)` (353) | `pass=17 fail=0`, exit=0 | **SURVIVOR** |
| **ME** | first-wins on the calibration row (later duplicate row accepted) | `select_cells`: `if in_axes and row is None and ...` → `if in_axes and ...` (229) | `pass=17 fail=0`, exit=0 | **SURVIVOR** |

Diffs (verbatim, `receipts/02-*`):

```
226c226   MA:   - if authority is None and AUTHORITY.match(line):
                + if authority is None and AUTHORITY.match(line.lstrip()):
229c229   MB:   - if in_axes and row is None and CALIBRATION.match(line):
                + if in_axes and row is None and CALIBRATION.match(line.lstrip()):
226c226   MC:   - if authority is None and AUTHORITY.match(line):
                + if AUTHORITY.match(line):
353c353   MD:   - findings += gate_fact(tree, authority, gate_newest)
                + findings += gate_fact(tree, authority + "\n" + rendered(score), gate_newest)
229c229   ME:   - if in_axes and row is None and CALIBRATION.match(line):
                + if in_axes and CALIBRATION.match(line):
```

## 3. Survivor 1 — MD: the paragraph coupling is untested (finding)

A banner carrying revision + command + receipt path but **no** token, with the token in a separate
rendered paragraph, must be red (frozen clause 1 is one coupled assertion). The pristine tool is red;
MD grades green (`receipts/04-demo-md.out`):

```
### pristine
RENDERED_CELLS facts=3 mismatches=1 gate=0 closure=1 disposition=1 newest_gate=85 newest_closure=85
RENDERED_CELLS_FINDING gate no coupled PRE_REPORT token in the rendered authority cell
exit=1
### MD
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
exit=0
```

No arm in the 17-arm battery places a token outside the banner paragraph, so the "same paragraph"
requirement has **zero** discriminating coverage. (Live record unaffected: its banner carries its own
token, so MD leaves the terminal grade green — the survivor is invisible to both the battery and the
graded artifact.)

## 4. Survivor 2 — ME: the row's first-wins rule is untested (finding)

First `| calibration |` row stale (round-84), later duplicate row correct (round-85): frozen
population 2 says the **first** row is the live row, so red. Pristine red; ME green
(`receipts/05-demo-me.out`):

```
### pristine
RENDERED_CELLS facts=3 mismatches=2 gate=1 closure=0 disposition=0 newest_gate=85 newest_closure=85
RENDERED_CELLS_FINDING closure row names round-84 newest committed closure is round-85 (corpus/lessons/round-85-verifier-spotcheck.md)
RENDERED_CELLS_FINDING disposition row does not name `round85 rejected-honest-stop`
exit=1
### ME
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
exit=0
```

## 5. MC's kill is incidental: the authority first-wins rule is also unarmed (finding)

MC is killed only because arm `backtick-info-not-a-fence` happens to render a correct banner *before*
a stale one. Delete that one arm from the MC source and the mutant escapes:

```
$ diff mut/MC.py mut/MC2.py
466,467d465
<     arm("backtick-info-not-a-fence", fixture(stale_live=True, shadow="``` x`y\n" + correct + "\n"),
<         1, {"gate": True, "closure": False}, 2)
RENDERED_CELLS_SELFTEST pass=16 fail=0
exit=0
```

So MC is *covered by accident*, not by design: no arm's declared subject is the first-wins rule.
The rule is contract-load-bearing, as probe P2 shows (stale banner first, correct banner second):

```
### P2 pristine  RENDERED_CELLS facts=3 mismatches=1 gate=0 ... exit=1
                RENDERED_CELLS_FINDING gate declared round=84 newest terminal receipt round=85 (...)
### P2 MC        RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 ... exit=0
```

## 6. Probe P1 — the instrument does not enforce "inside the FIRST `## Axes` section"

Frozen population 2: "the first top-level `| calibration |` row **inside the first `## Axes` section**".
The selector only tests `in_axes` (any `## Axes` heading seen so far). With the row moved into a
*second* `## Axes` section and the first section carrying none, the pristine tool grades green:

```
### P1 pristine (row moved to a SECOND ## Axes section)
RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85
exit=0
```

Contract divergence, latent: the terminal SCORECARD has exactly one `## Axes` section (line 8) and its
first calibration row is line 18, so no live effect today.

## 7. Do the survivors/mutants move the graded artifact? (mutants vs the live record)

`receipts/07-live-record.out`, `--repo <lane> --rev bafae7af…`:

| instrument | line | exit |
|---|---|---|
| pristine | `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85` | 0 |
| MA | same as pristine | 0 |
| MB | same as pristine | 0 |
| MC | `mismatches=1 gate=0 … FINDING gate no coupled PRE_REPORT token in the rendered authority cell` | 1 |
| MD | same as pristine | 0 |
| ME | `mismatches=2 gate=1 closure=0 disposition=0 … FINDING closure rendered calibration row names no latest outside closure` | 1 |

The live SCORECARD has one round-86 banner at line 6 plus ~25 historical top-level banners, and two
`| calibration |` rows inside `## Axes` (lines 18 and 29). The terminal green therefore **depends on
document-order selection** (both MC and ME flip it red); MD changes nothing live.

## 8. Record audit against committed bytes

1. Reproduced `after/c1.out` exactly at `bafae7af…`:
   `RENDERED_CELLS facts=3 mismatches=0 gate=1 closure=1 disposition=1 newest_gate=85 newest_closure=85`, exit 0.
2. Reproduced `after/c1-selftest.out` byte-for-byte (only the receipt's `$ python3 …` prompt header is
   absent from my rerun): `RENDERED_CELLS_SELFTEST pass=17 fail=0`.
3. `newest_gate=85` is faithful: **no** round-86 `PRE_REPORT round=86` receipt exists anywhere in the
   tree (`grep -rln "PRE_REPORT round=86"` hits only w1/w2 seat reports, never a `measured/*.out`).
4. Arm-count expansion is disclosed: `SCORECARD.md:14` "selftest 17/0 at the terminal tree (11/0 at the
   freeze)" and `LOG.md` "the w2 falsification added six arms"; the frozen plan's 11 named arms are
   exactly the 11 in `measured/before/c1-selftest.out`.
5. **MISMATCH (record product, calibration class)** — `corpus/lessons/round-86.md:59-60`:

   ```
   7/7 source mutants are now killed by named arms (`RENDERED_CELLS_MUTANTS mutants=7 killed=7
   escaped=0`, `.ufo/waves/round-86/measured/after/c1-mutants.out`). Shown able to fail: each mutant run
   exits 1 naming its own arm.
   ```

   The cited receipt's committed bytes at the same revision read
   `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0` (`git show bafae7af…:.ufo/waves/round-86/measured/after/c1-mutants.out | tail -1`).
   `7/7` was the receipt's content at `c5d71b7a`; `d80d0896` and `7a21aaa1` raised it to 10 and the
   lesson text was not re-quoted. `SCORECARD.md` says "10 source mutants each killed by a named arm",
   so the lesson is the only stale copy — a quoted number that its own citation no longer supports.

## 9. Verdict

- Committed C1 mutant battery: **holds at the terminal record** (10/10, each on its named arm).
- The C1 selector's **column-0 rules** are properly armed (MA, MB killed).
- The C1 selector's **ordering and coupling rules are not**:
  **MD survives** (paragraph coupling), **ME survives** (row first-wins); **MC survives when its
  incidental killer arm is removed** (authority first-wins). Two of these three are live-load-bearing
  (they flip the terminal record red when mutated), and the battery cannot see any of them.
- One **record-product mismatch**: the round-86 lesson quotes `mutants=7 killed=7` against a receipt
  whose committed bytes say `10/10`.
- A **latent contract divergence**: "inside the first `## Axes` section" is not implemented.

## 10. Restoration / cleanup / tools

- Pristine bytes never modified: all edits on copies; `sha256sum` of the scratch instrument equals the
  commit's blob (`f9d36b5b…`) after all runs; the lane working tree was never written by this seat
  (`git status --porcelain tools/round86-rendered-cells.py` empty).
- Scratch `/fast/scratch/hyaku/kama-r86/MT01SelectorMutants/` removed before yielding; nothing written
  under `/tmp` beyond the committed driver's own `tempfile` (10 files < 10 KB).
- Tools installed/upgraded: **none** (python3 stdlib only; pacman not used).
