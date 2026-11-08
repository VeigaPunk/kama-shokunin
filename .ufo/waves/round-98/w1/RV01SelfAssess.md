# RV01 — C1 self-assessment instrument, attack report (kama r98 w1)

Seat `RV01SelfAssess`. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only), fixtures under
`/fast/scratch/hyaku/kama-r98/RV01SelfAssess/` (shared clones; scratch removed before yield). No tracked lane
file was edited; `git -C <lane> status --short --untracked-files=no` at the end shows only a sibling seat's
`corpus/lessons/round-98.md` (not mine, left alone).

Instrument under attack: `tools/round98-self-assessment-audit.py` (frozen at `34ad44e9`).
Claim under attack: `plans/round-98-claims.md` §C1 — *"the lane's graded self-assessments match the repo,
heading included"*, measured at M1, `checks=20 mismatches=0 met=True`, exit 0.

Receipts: `out/RV01SelfAssess/receipts/*` (verbatim command output + exit code).

---

## 1. Base and freeze runs (as instructed)

```
$ python3 tools/round98-self-assessment-audit.py --repo <lane> --rev 681c80a4
SELF_ASSESS98 checks=20 mismatches=4 met=False rev=681c80a4e3c745c22559f74b2c2a1917bdc66fc6 skill_sha256=863eb35d…  exit=1
$ python3 tools/round98-self-assessment-audit.py --repo <lane> --rev master
SELF_ASSESS98 checks=20 mismatches=3 met=False rev=34ad44e9f783b35a804f020d6b02c48c04ade481 skill_sha256=863eb35d…  exit=1
```

`master` is the freeze commit `34ad44e9`, one commit past base: the counters, plan and controls are in, the
measurement-time prose is not, so **the C1 predicate is unreachable at freeze by construction** — exactly the
do-nothing control the plan declares. Per-check instrumentation shows which checks carry the mismatch:

| rev | checks that fire |
|---|---|
| `681c80a4` (base) | 15 (r98 counters absent → their docstrings unreadable), 16, 19, 20 |
| `34ad44e9` (freeze) | 16 (depth row "four" + docstring "adds two cells"), 19 (heading "three" vs 5 mutants), 20 (no W18/W19/overcharge surface) |

The committed control `controls/c1-base.out` is honest: its bytes are identical to a live run at `681c80a4`
(`receipts/00-lane-base.out`).

**Discrimination test.** A fixture that rolls the four count surfaces forward exactly as C1's "After"
describes (heading `five`; §Round 97 body `five probe variants` + W18/W19/overcharge; SCORECARD depth row
`five graded probe forgeries` + W18/W19/overcharge; budget docstring `adds six cells`; depth row sha/lines/
sections re-anchored) is green:

```
$ python3 tools/round98-self-assessment-audit.py --repo <fixture> --rev 42b95d76
SELF_ASSESS98 checks=20 mismatches=0 met=True rev=42b95d76…  exit=0        # receipts/10-fixture-green.out
```

So the instrument can pass, and it separates base/freeze from green. The question is what else passes.

---

## 2. Shape verdicts

### (a) Heading count word disagrees with the counter's mutant count, **words only** — **CAUGHT (check 19)**

Fixture rev `87096418`: green baseline with `the five graded forgeries` → `the four graded forgeries` in the
heading line only.
`SELF_ASSESS98 checks=20 mismatches=1 met=False`, exit 1; instrumentation shows the mismatch enters at check 19
and nothing else fires. `receipts/11-shape-a-word-only.out`, `receipts/13-shape-c1-headings.txt` (baseline).

### (b) Heading spells the count **numerically** — **CAUGHT, but as a false red (check 19)**

Fixture rev `8f60c7d1`: heading `the 5 graded forgeries` (a *true* statement, five mutants).
`SELF_ASSESS98 checks=20 mismatches=1 met=False`, exit 1, mismatch at check 19 only.
`tools/round98-self-assessment-audit.py:348` matches `the (\w+) graded forgeries` and `:72-73` maps only the
word forms `zero…nine`; a digit is `None` and therefore always a mismatch. The check grades the *spelling*,
not the count: a correct heading written as a numeral is rejected, and `ten` or any count ≥ 10 would be
rejected for the same reason once the population grows (`WORDS` stops at nine).
`receipts/12-shape-b-numeric.out`.

### (c) Two headings, only one read — **NOT CAUGHT (two independent shapes, both `met=True`)**

`check 19` (`:346-347`) and `section()` (`:95-105`) both take the **first** line that `startswith("### Round 97
correction")`, with no fence/comment/rendered-identity filter and no duplicate detection.

**(c1) duplicated live heading, second one contradicts.**
Fixture rev `888436be`: green baseline plus a second, live (unfenced) heading appended at EOF.

```
SKILL.md:2443  ### Round 97 correction (… the five graded forgeries; …)
SKILL.md:2475  ### Round 97 correction (… the nine graded forgeries; …)
$ … --rev 888436be → SELF_ASSESS98 checks=20 mismatches=0 met=True  exit=0
```
`receipts/13-shape-c1-duplicate-heading.out`, `receipts/13-shape-c1-headings.txt`.

**(c2') a fenced/quoted copy of the section placed before the live one shadows it.**
Fixture rev `fbfb8bf7`: the *live* heading and body are left at the freeze text (`three graded forgeries`,
`four probe variants`), and a ```` ```markdown ```` block carrying a correct copy of the section is inserted
above it — a realistic "quoted example" artifact.

```
SKILL.md:2444  ### Round 97 correction (… the five graded forgeries; …)      ← inside the fence
SKILL.md:2464  ### Round 97 correction (… the three graded forgeries; …)      ← the rendered, live heading
SKILL.md:2487  is enforced: four probe variants survive all 13 of its cells   ← the rendered, live body
$ … --rev fbfb8bf7 → SELF_ASSESS98 checks=20 mismatches=0 met=True  exit=0
```
`receipts/20-shape-c2prime-fenced-decoy.out`, `receipts/20-shape-c2prime-headings.txt`.
This is the round-97 defect reproduced verbatim — the rendered document says *three*, the instrument says met
— with one extra line of indirection. Check 16's `sec97` (`:302`) reads the same shadowed region, so the
body count is wrong too and still passes.

### (d) Check 20 is substring presence — **NOT CAUGHT**

Fixture rev `4f2b32b8`: green baseline, then the SCORECARD depth row and the §Round 97 body are extended with
explicit *negations* of the claim while keeping the tokens `overcharge`, `W18-800k-nd1`, `W19-520k-nd4`:

> "… with the overcharge mutant; although the overcharge mutant is not graded and W18-800k-nd1 /
> W19-520k-nd4 are not cells"
> "… which W18 and W19 decide — although no overcharge mutant is graded and W18-800k-nd1 and
> W19-520k-nd4 are not cells."

```
$ … --rev 4f2b32b8 → SELF_ASSESS98 checks=20 mismatches=0 met=True  exit=0
```
`tools/round98-self-assessment-audit.py:356-360` is `"overcharge" in depth.lower()` and `all(w in depth …)`;
no polarity, no proximity, no link to the cell/mutant sets. `receipts/30-shape-fprime-negation.out`.

### (e) Check 7's "binding" scan is line-scoped and block-scoped — **false green and false red**

`tools/round98-self-assessment-audit.py:191-207` builds `region` from the *contiguous* `#` lines touching the
`MAX_STEPS =` line and flags only when `"binding"` and one of `1 000 000 / 6 steps / 6 read` are on the **same
line**. Two fixtures:

- rev `e76c4804`: `# binding figure: 1 000 000 tensor headers and 6 steps per header …` placed two lines
  below `MAX_STEP_BYTES`, outside the block → `mismatches=0 met=True`, exit 0
  (`receipts/40-check7-escape.out`; the script prints the scanned region `563..587` and confirms the text is
  outside it).
- rev `e1351844`: a *truthful* line inside the block — `# not binding: 1 000 000 headers is the MAX_TENSORS
  constant, not the ceiling` → `mismatches=1 met=False`, exit 1 (`receipts/41-check7-false-red.out`).

The live probe survives only because the true negative sentence happens to be split across lines 579/580.

---

## 3. Coverage re-derivation: numbers the audit does not grade

Both frozen counters were run against a fixture that carries **eight** table rows (the two C3 rows added with
correct arithmetic) while every *stated count* in the same section stays `six`:

| surface | states | re-derives to | graded by |
|---|---|---|---|
| `SKILL.md:2449` | "The **six** rows below are the two boundary classes…" | 8 rows (`SKILL.md:2453-2460` + the two new rows) | **nothing** |
| `SCORECARD.md:17` (depth row) | "six KV-free rows at nd=1 and nd=4" | 8 | **nothing** |
| `SKILL.md:2466` | "all **13** of its cells" | `cells=13` in `.ufo/waves/round-96/measured/c1.out` | nothing (check 13 grades a different needle) |
| `SCORECARD.md:17` | "SKILL.md grew **2441 → 2473** lines" | `git show <rev>:SKILL.md \| wc -l` (2473 at freeze; ≠ at M1) | nothing — check 2 grades only the `(N lines)` capture |
| `SKILL.md:2466-2471` | "900,000 headers", "constant 6 steps", "100 MiB", "four preamble steps", "833,333-header nd=1" | `MUTANTS` + fixture sizes in `tools/round98-router-budget.py:169,184-193` | nothing (check 16 grades only the W-ids' presence) |
| `SCORECARD.md:6369,6373,6379` | `SELF_ASSESS97 checks=18`, `ROUTER_BUDGET97 cells=17`, `DEPTH_BOUNDARY97 rows=6 checks=10` | re-run the round-97 counters at `be590351` (I did: `SELF_ASSESS97 checks=18 mismatches=0 met=True`) | nothing — checks 13-14 grade round-96 receipts only |
| `SCORECARD.md:6` | "**Current authority (round 96)** … Latest measured round: 96" | lane round history | nothing |

Command that produces the table-row count and the green verdict in one pass:

```
$ python3 tools/round98-depth-boundary-audit.py --repo <fixture> --rev 7de98c69
DEPTH_BOUNDARY98 rows=8 checks=12 mismatches=0 met=True            # receipts/32-shape-gprime-c3.out
$ python3 tools/round98-self-assessment-audit.py --repo <fixture> --rev 7de98c69
SELF_ASSESS98 checks=20 mismatches=0 met=True                      # receipts/31-shape-gprime-c1.out
$ git show 7de98c69:SKILL.md | sed -n '2449p'   → "The six rows below …"        # receipts/31-shape-gprime-counts.txt
$ git show 7de98c69:SCORECARD.md | grep -o 'six KV-free rows'   → "six KV-free rows"
```

Both frozen counters green, both statements of the row count false. `tools/round98-depth-boundary-audit.py:130`
enforces `rows == 8` from the *parsed table*, never from the sentence; C1 never reads the sentence either.
This is the same defect class C1 exists to close (a stated count disagreeing with the graded population),
sitting one line above the heading it now grades.

### Checks whose proof is presence, not recomputation

| check | proof | note |
|---|---|---|
| 6 (`:169-184`) | both evidence paths *exist* at the pointer commit | content never read |
| 7 (`:186-207`) | substrings in a contiguous comment block + one whole-file substring | demonstrated false green/red above |
| 10-11 (`:236-252`) | field equality on one SOURCES row | recomputes nothing about the spec |
| 13-14 (`:261-276`) | needle present in receipt **and** SCORECARD | disclosed |
| 15 (`:278-289`) | `"512"`, `"4 + T"`, `"5 + nd"` as substrings; only `MAX_STEPS` is recomputed | disclosed |
| 18 (`:322-342`) | line-set equality over the probe's loop | disclosed as source shape, not behaviour |
| 20 (`:352-362`) | substring presence | demonstrated defeated above |
| 19 (`:344-350`) | *does* recompute `len(mutants)` — but only over the first matching line, and additionally hardcodes `len(mutants) != 5` | demonstrated defeated above |

Genuine recomputation: checks 1-3 (sha256/line count/`^## ` count), 4-5 (sha256/pipe-line count), 9
(§Round 96 rows from `MAX_STEPS`), 12 (byte equality), 16 (against `NEW_CELLS`/`MUTANTS`), 17 (id uniqueness),
and the arithmetic half of 19.

---

## 4. Findings by severity

**F1 — HIGH — check 19 reads one heading line and nothing else; duplicate and fenced/shadowed headings pass.**
`tools/round98-self-assessment-audit.py:95-105,344-350`. Evidence: `receipts/13-shape-c1-duplicate-heading.out`
(`met=True` with a live "nine graded forgeries" heading at `SKILL.md:2475`) and
`receipts/20-shape-c2prime-fenced-decoy.out` (`met=True` while the rendered heading at `SKILL.md:2464` says
"three" and the rendered body at `:2487` says "four probe variants"). This reproduces the exact round-97 defect
the check was added to close, in the same file, with no change to any graded number.

**F2 — HIGH — check 20 grades token presence, so a self-assessment that denies the claim passes.**
`…:352-362`; `receipts/30-shape-fprime-negation.out` (`met=True` with "the overcharge mutant is not graded and
W18-800k-nd1 / W19-520k-nd4 are not cells" written into the depth row and the section body).

**F3 — HIGH — the section's own row count is stated, re-derivable, and graded by neither counter.**
`SKILL.md:2449` and `SCORECARD.md:17`; `receipts/31-shape-gprime-c1.out` (`mismatches=0`) +
`receipts/32-shape-gprime-c3.out` (`rows=8 mismatches=0`). C1's predicate ("the lane's graded self-assessments
match the repo, heading included") and C3's (`rows=8`, every row recomputed) are both met while two count
statements in the graded section disagree with the section. A reviewer reading the section, not the counters,
is misled.

**F4 — MEDIUM — check 7's binding scan is same-line and same-block only.** False green on a real
"binding 1 000 000 / 6 steps" claim one blank line outside the block (`receipts/40-check7-escape.out`), false
red on the truthful negation (`receipts/41-check7-false-red.out`).

**F5 — LOW — check 19 rejects a truthful numeral and stops at `nine`.** `…:72-73,348`;
`receipts/12-shape-b-numeric.out`. Not a false green, but it means the heading check grades orthography, and
never scales past a population of nine.

**F6 — LOW — check 16 forces one reading of an ambiguous sentence.** `Round 98 adds two cells past that (new
set = six cells, mutants = five)` is true on its face (round 98 adds two cells to the round-97 four) and red
under the check, which requires the word after "adds" to equal `len(NEW_CELLS)` (`…:305,309`). The green
fixture has to rewrite it to `adds six cells`. The instrument therefore rewards a rewrite that a reader cannot
distinguish from the original claim.

**F7 — INFO — historical counts (SCORECARD round-97 paragraph) are ungraded but currently true**
(`SELF_ASSESS97 checks=18 mismatches=0` re-derived at `be590351`). No live mismatch; listed so the next
successor knows the surface is unowned.

---

## 5. Is C1's sentence wider than the instrument?

The *predicate* is honest: it names a command, an exit code and a disclosed limit ("the audit grades exactly
the 20 named surfaces"), and the base control it declares is real (verified byte-identical to a live run).
The instrument can go green and goes red at base and freeze for the declared reasons.

The **defect statement** is wider. C1's Before (a) says the round-97 audit could not see the heading "because
`section()` excludes the heading at `start + 1`", and the After says check 19 now grades "the heading's count
word against the counter's parsed mutant count". What check 19 actually closes is *the first `### Round 97
correction` line in the file, when the count is spelled as an English word*. Still open, and demonstrated
inside the same frozen claim:

1. any later heading line in the same file (F1/c1), including the rendered one behind a quoted copy (F1/c2');
2. the same count-statement class in the prose beside the table and in the SCORECARD depth row (F3) — which
   is the *identical* defect shape (a stated count that disagrees with the graded population) one line above
   the heading the check now reads;
3. the polarity of the check-20 tokens (F2).

A reviewer could therefore accept `SELF_ASSESS98 checks=20 mismatches=0 met=True` at M1 while the lane's
rendered §Round 97 correction still says "three graded forgeries", "four probe variants" and "six rows", and
while its SCORECARD depth row says "six KV-free rows". That is a false self-assessment passing the frozen
calibration instrument — the question C1 was filed to answer, answered "yes, it still can".

Suggested (not applied; this wave does not edit the counter — K1): a successor that (i) selects the *rendered*
heading by the round-86 rendered-cell rule (fences/comments excluded), (ii) fails when more than one heading
line with that prefix exists, (iii) grades the section's own row-count sentence against the parsed table and
the SCORECARD depth row's row count, and (iv) replaces check 20's substring tests with the cell/mutant sets.

---

## 6. Residual risk and verification gaps

- Everything above was measured on **fixtures I built** to reach a green state, not on the lane's M1 (which does
  not exist yet). The green baseline is my construction of C1's "After"; the lane's real M1 wording may differ,
  and the findings hold for any wording that satisfies the 20 checks.
- (c2') is the strongest shape because it keeps the *live* text at its current, defective value; (c1) is the
  minimal one. Both are `met=True`; neither requires editing the instrument.
- The fenced-decoy shape depends on `section()` having no fence awareness; I did not test a decoy inside an
  HTML comment (`<!-- -->`), which `startswith` would also match, but the mechanism is identical
  (`:346-347` has no filter at all).
- I did not re-run the C2/C1 counters under host load; C1's instrument is CPU-free and its verdicts were stable
  across every call above.
- No lane file was modified; the only tracked change in the lane at yield time is a sibling seat's
  `corpus/lessons/round-98.md`.
- Tooling: none installed or upgraded.
