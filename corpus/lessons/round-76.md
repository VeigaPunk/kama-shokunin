# kama round 76 — lesson

Round 76 (attempt 1), base `b06cc612711560c53eef3ec21484c6963601262f`, freeze
`1a85a991fce5b76b60f88a5cab3df98d253b1a4a`, work tip `a3fbc629fa18c26ad1192adc5d8e762671dd1d79`.
Claims: C1 operability (receipt citation scope), C2 calibration (self-record facts), C3
freshness (append-only event accounting). Frozen plan: `plans/round-76-claims.md`.

## Verdicts

| Claim | Verdict | What the receipt says |
|---|---|---|
| C1 | **miss** | before exit 2 `RECEIPT_CLAIM_V2 CouldNotEvaluate … (.py)`; after exit 1 `RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=6 unbound=2 shifted=3 nonreceipt=0 unclassified=0` — the frozen target said `bound=9 shifted=0` |
| C2 | **verified** | before `SELFRECORD_FACTS claims=8 mismatches=5 corrected=0 unbacked=1` exit 1; after `claims=8 mismatches=0 corrected=5 unbacked=0` exit 0 |
| C3 | **miss** | before `events=232 … ungraded=83`, register graded 53; after exit 1 `APPEND_EXEMPT events=233 register=53 exempt=47 restored=91 disclosed=5 unaccounted=37 cutoff=10f37171 introductions=2 rotation_safe=1` — the frozen target said `exempt=83 unaccounted=0 introductions=1` |

## Mistakes

1. **`first-finding-freeze`** — a target sized from a control run that reports only the first
   offending record per item. At freeze I measured the round-75 citation population with a
   fence-stripped dry run; the base tool prints one `RECEIPT_TIP_FINDING` per receipt, so I read
   `PROVINCE.md touched by c9ab73d8` and concluded the self-description widening would take
   `shifted` to 0. The real deltas also touch `registry/append-only-contract.tsv` at `b8ed2568`,
   and `registry/` must keep shifting. C1's target was therefore unsatisfiable before any work
   ran.
   *Evidence:* `.ufo/waves/round-76/measured/before/c1-fence-dryrun.out` (one path named per
   receipt) vs `.ufo/waves/round-76/w1/EX01ReceiptScope/after.out` (all three receipts shifted
   by the contract file).
   *Captured-by:* none — the round contract asks for "the cheapest control"; it does not say the
   control must enumerate every finding, and a tool that prints one finding per item reads like a
   complete list.
   *Fix:* `tools/round76-receipt-scope.py --all-findings` prints every non-record path in each
   receipt's `rev..tip` delta. *Shown able to fail:* at the round-75 population it lists
   `registry/append-only-contract.tsv` alongside `PROVINCE.md` for the three before receipts,
   which is exactly the fact the freeze missed; the arm set keeps `shift-tools` red.

2. **`frozen-target-unsatisfiable`** — a predicate whose two clauses cannot both hold. C3 asked
   for (i) every audit event accounted once, (ii) class rows keyed by "the audit's own mechanical
   exemption class", and (iii) a single cutoff = the earliest commit adding *any* register.
   The audit serializes no class or section key, its `ungraded` bucket mixes exempt-section
   deletions with A-row/only-prefix carveouts (31 events), and five otherwise-classifiable
   events postdate the earliest register introduction, while adding the class register makes
   `introductions=2`. No register can satisfy all three.
   *Evidence:* `.ufo/waves/round-76/w1/EX03AppendExempt/register-rows.txt` (47 strict rows; 31
   wrong-class and 5 post-introduction events named) and `measured/after/append-exempt.out`
   (`unaccounted=37 introductions=2`).
   *Captured-by:* none at freeze — I wrote the cutoffs from the round-75 register's single-file
   shape without checking the audit's JSON keys or the second register's introduction date.
   *Fix:* the `## Planned (round 77)` item 2 in `SCORECARD.md`: independent per-register cutoffs,
   a class check over the *ungraded* lines against exempt titles, and a named class for the
   audit's `permitted` carriage. *Shown able to fail:* the counter's `rotation-reintroduced` arm
   already turns a re-add red, and the `audit-fixture-baseline` arm asserts the real
   `unaccounted=37` so a retargeted round cannot silently read it as green.

3. **`label-drift`** — a counter's verdict field order differing from the frozen predicate's
   sentence. `tools/round76-selfrecord-facts.py` first printed
   `claims=8 mismatches=5 unbacked=1 corrected=0` while the plan's predicate says
   `mismatches=0 corrected=5 unbacked=0`. Found by the integration run, fixed before the record
   cited it.
   *Evidence:* the pre-fix run in `.ufo/waves/round-76/w1/EX02SelfrecordFacts/before.out` against
   the plan's §C2 predicate sentence.
   *Captured-by:* the plan's own "same sentence in all three places" rule; nothing mechanical
   compared them.
   *Fix:* the print order now matches the predicate, and its two self-asserting arms were updated
   with it. *Shown able to fail:* the `red-at-base` arm asserts the literal summary string, so a
   reordering without updating the arm fails the selftest (observed: after the print-order change
   and before the arm update, `SELFRECORD_FACTS_SELFTEST pass=4 fail=1`).

4. **`gate-arm-missing-label`** — a gate defect-regex that did not match the new counter's
   finding label. `R76_FINDING_RE` listed `SELFRECORD_FACTS_FINDING`, but the plan's C2 label is
   `SELFRECORD_FACT <id> filed= derived=` (no `_FINDING`), so a red arm 9 was reported without
   the offending line. Caught by the gate's own new selftest case (s).
   *Evidence:* first `PRE_REPORT_SELFTEST pass=20 fail=1` naming `round76-instruments-red`.
   *Captured-by:* the selftest arm (s), written together with the arm.
   *Fix:* the regex now accepts `SELFRECORD_(FACT|CORRECTION)`; `PRE_REPORT_SELFTEST pass=21
   fail=0` (`measured/after/gate-selftest.out`). *Shown able to fail:* with the old regex the
   selftest arm (s) fails on the missing detail text.

## Gate

Sources opened or re-opened this round (contract v1):

- **S498** (CommonMark 0.31.2 §4.5, `https://spec.commonmark.org/0.31.2/#fenced-code-blocks`) —
  **admitted**: re-fetched live 2026-11-04, sha256
  `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`
  (`.ufo/waves/round-76/w1/SCR01Sources/source-open.out` records the retained bytes); the quote "characters inside
  fenced code blocks are treated literally" (20 words) sits at retained lines 2760–2761 in §4.5.
  The row was opened in round 50; this round re-located the quote in freshly retained bytes and
  the entry `corpus/knowledge/fenced-quotation-scope.md` now cites it.
- **S548** (own-work, `python3 tools/round76-selfrecord-facts.py`) — **admitted**: the lane's own
  re-runnable instrument, tier A by the contract's own-work clause; `teaches` records the
  revision-bound fact rule, `used-by` the new entry `corpus/knowledge/selfrecord-fact-binding.md`.
- **Rejected this round:** a new CommonMark row (originally drafted as S548) — rejected as a
  duplicate of S498 (same URL and anchor; census W04), the expansion being the entry and not the
  row. Flip: nothing; a correction of S498 would be a `supersedes` row instead.
- **Rejected this round:** a `gitrevisions(7)` row for the revision-read rule — rejected as a
  duplicate of the standing S070/S082 pair (S082 already supersedes S070 on that URL); the entry
  cites the existing rows. Flip: a correction of S082's anchor if the page moves.

Registry: 287 rows at base → 288 at the round tip (`sources-census.sh validate --root … kama`,
exit 0 at both ends; before: 287 + ok line, after: 288 + ok line, W04 warnings only).

Spot-check: no outside non-author check ran this round; the round-75 closure already admitted
round 75 and its eight routed defects are closed or routed again below.

### Gate supplement (2026-11-04, round-77 D4; produced by round 76)

- **S498** supersedes the paraphrase “characters inside fenced code blocks are treated literally” and its incorrect word count above. The verbatim retained sentence is: “The content of a code fence is treated as literal text, not parsed as inlines.” Located at retained HTML lines 2760–2761, `https://spec.commonmark.org/0.31.2/#fenced-code-blocks`, accessed 2026-11-04 in round 76; this supplement checks retained bytes, not a new live fetch. It is 17 whitespace-delimited words (the closure's “15 words” is also a counting error), still within 25.
- S498 `used-by` old→new: `corpus/lessons/round-50.md` → `corpus/lessons/round-50.md, corpus/knowledge/fenced-quotation-scope.md`, from base `b06cc612` to `c2aa7fb2`; status and recheck unchanged. Derivation:

```sh
python3 -c 'import re,subprocess; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=open(L+"/.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html").read(); q="The content of a code fence is treated as literal text, not parsed as inlines."; print("S498_QUOTE "+q); assert q in re.sub(r"\s+"," ",text); old=subprocess.check_output(["git","-C",L,"show","b06cc612:corpus/SOURCES.md"],text=True); new=subprocess.check_output(["git","-C",L,"show","c2aa7fb2:corpus/SOURCES.md"],text=True); print("S498_USED_BY_OLD "+next(s for s in old.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip()); print("S498_USED_BY_NEW "+next(s for s in new.splitlines() if s.startswith("| S498 |")).split("|")[-2].strip())'
```

- **S548** own-work, access date **2026-11-04**. Located quote/command receipt: `SELFRECORD_FACTS claims=8 mismatches=0 corrected=5 unbacked=0`, line 3 of `.ufo/waves/round-76/measured/after/selfrecord-facts.out`, recorded `rev=461d2adbf2b3fe596a53cb392e2bc6e82af79bfb`, exit 0. Exact re-runnable command (explicit historical revision prevents later record drift):

```sh
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round76-selfrecord-facts.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --rev 461d2adbf2b3fe596a53cb392e2bc6e82af79bfb
```

This is own-work execution evidence, not an external-source quotation; the new receipt is retained under `.ufo/waves/round-77/w1/SC03Corrections/after-ownwork.out`.

#### Correction to this supplement's word count (2026-11-04)

Supersedes only the supplement's “17 whitespace-delimited words” and its assertion that the closure's “15 words” is erroneous. Corrected: **15 words**; the closure's count was right. The exact retained sentence above is unchanged. Derivation: `python3 -c 'print(len("The content of a code fence is treated as literal text, not parsed as inlines.".split()))'` → `15`, exit 0. The initial hand-count error is preserved here rather than rewritten.


## Routed defects from the round-75 closure

| # | Item | Disposition |
|---|---|---|
| 1 | stale PROVINCE digest in the §Round 75 population sentence | closed — `### Correction (2026-11-04) — province-digest` (C2) |
| 2 | C2 after-receipt not a faithful capture | closed — full five-line re-capture, `measured/after/r75-survivors-recapture.out` |
| 3 | LOG work tip and mistake count stale | closed — two correction blocks (C2) |
| 4 | gate selftest tally had no committed receipt | closed — `measured/after/gate-selftest.out` (`PRE_REPORT_SELFTEST pass=21 fail=0`), recorded as historical-unbacked in the LOG correction |
| 5 | new knowledge entry lacked a coverage-map row | closed — `corpus/README.md` rows for `append-only-accepted-history.md`, `fenced-quotation-scope.md`, `selfrecord-fact-binding.md` |
| 6 | no QUALITY criterion for the round-75 mistake classes | closed — KQ126–KQ128 in `corpus/QUALITY.md` |
| 7 | `## Gate` recorded no round-local reject | closed — two rejects above (duplicate CommonMark row, duplicate gitrevisions row) |
| 8 | gate arm 7 red on the record's `.py` citation | **partly closed** — the scope is decided and armed, and the record now classifies instead of failing unread; the arm stays red on `shifted=3` (registry delta) and arm 7 still refuses the round-75 record at the tip because the frozen base tool is fence-blind. Routed to `### Planned (round 77)` item 1. CR01's two disclosed limits and MT01's escapes stay open and are listed in the report. |

## considerthese

`considerthese/2026-10-26.md` proposal 2 ("track what happens to my own proposals") has a
standing instance since round 75; this round extends it with the round-75 admission and the
round-76 dispositions of the eight routed defects (table above). No new proposal was mined: the
other three (flag next-morning deletions, running shortcut tally, morning pin gap) are landed
(`tools/append-only-audit.py`, `tools/shortcut-tally.py`, `tools/pin-watch.py`).

## Assimilation

`Assimilation: none`. Re-derived read-only at round time:
`reg_ids 287 · staged_ids 142 · collisions 9 · quarantine_rows 7`
(`.ufo/waves/round-76/assimilation/summary.out`).
The nine staged-id collisions (S330 S333 S334 S335 S346 S347 S352 S353 S363) are mass drift a
read-only merge cannot resolve; the guard proof shows an indented `| S330 |` row is caught by the
0–3-space extractor (column-zero-only pattern misses it), so nothing appends.

## Freeze divergences (recorded, not rewritten)

1. **C1 population tip.** The plan names the round-75 record as the population but not the
   revision. Landed reading: a round's self-record is graded at its own landing tip, i.e. the
   next round's base (`--base-rev`, default parsed from `plans/round-<N+1>-claims.md`); for round
   76, where no next plan exists yet, the default is `HEAD`. Diagnostic line
   `RECEIPT_SCOPE_POP` discloses it. Predicate, exit map and kill rule unchanged.
2. **C2 field order.** The plan's predicate sentence lists `mismatches corrected unbacked`; the
   first build printed `mismatches unbacked corrected`. The print order now matches the plan
   (mistake 3).
3. **C2 `log-tally` correction value.** The plan says a correction must state a value that
   re-derives; the historical tally cannot re-derive (no receipt ever existed). Landed reading:
   the correction states `historical-unbacked; PRE_REPORT_SELFTEST pass=21 fail=0` with a
   `Receipt:` pointer to a *committed* receipt, and the harness accepts it only when that receipt
   exists at the named revision. The claim target `corrected=5` is met this way, not by inventing
   a round-75 receipt.
4. **C3 register scope.** The plan says the class register holds one row per audit event; the
   landed register holds the 47 events the strict frozen rule admits and the counter names the
   other 36. The claim is reported as a miss rather than the register being widened.

## Wave

One v1 wave, 13 seats (3 executor, 3 scribe, 1 scout, 1 connector, 1 revenger, 1 reviewer,
1 critic, 1 mutation-tester, 1 sentinel; attack share 5/13 = 38 %), spec
`.ufo/waves/round-76/w1-spec.json`, dispatch `.ufo/waves/round-76/w1/w1-dispatch.json`,
reports under `.ufo/waves/round-76/w1/`. Two seats (`SC01Recon`, `REV01Semantics`) had not
reported at record time; their reports are named in the round report.


## Superseded bytes (held verbatim so the audit grades the edit restored)

Round 76 rewrote five lines of this lesson in place once (the record-citation repairs: a
seat-report `.md` path, a retained `.html` path, a brace-expanded assimilation path and two
wrapped lines). The contract's append-only rule for `corpus/lessons/*.md` forbids dropping the
first-filed bytes, so they are held here exactly:

```
   *Evidence:* `.ufo/waves/round-76/w1/EX03AppendExempt.md` (47 strict, 31 wrong-class, 5
   post-introduction) and `measured/after/append-exempt.out` (`unaccounted=37 introductions=2`).
  `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`, retained at
  `.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html`; the quote "characters inside
(`.ufo/waves/round-76/assimilation/{reg-ids,staged-ids,collisions,quarantine-slice,guard-proof.out}`).
```

### Correction (2026-11-04, round-77 D3) — post-cutoff events

Supersedes: §Mistakes item 2, “and five otherwise-classifiable events postdate the earliest register introduction”, and its evidence parenthesis “31 wrong-class and 5 post-introduction events named”.
Corrected: **6** events postdate the cutoff, not five; **31+6=37**, not 31+5=36. The six are five `SCORECARD.md` events plus `c2aa7fb2c02dd95a185b728d5863f9ae492ecef4`'s own `corpus/SOURCES.md` event. The committed `register-rows.txt` statement `post-introduction=5` is an earlier partial classification, not the complete after-receipt population. The round-76 C3 miss remains a miss.

Derivation reads the committed after receipt at the sealed base (its header revision describes the measured state, not the later receipt-introduction commit), then tests each finding's ancestry against cutoff `10f37171fb696c542586cbee96ea4a509ab74afc`:

```sh
python3 -c 'import subprocess,re,collections; L="/home/vgpnk/Projects/shokunin/kama-shokunin"; text=subprocess.check_output(["git","-C",L,"show","cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7:.ufo/waves/round-76/measured/after/append-exempt.out"],text=True); rows=re.findall(r"^APPEND_EXEMPT_FINDING unaccounted ([0-9a-f]{40}) (\S+)",text,re.M); cutoff="10f37171fb696c542586cbee96ea4a509ab74afc"; post=[(h,p) for h,p in rows if subprocess.run(["git","-C",L,"merge-base","--is-ancestor",h,cutoff]).returncode==1]; print("POSTCUTOFF pre=%d post=%d total=%d sum=%d"%(len(rows)-len(post),len(post),len(rows),len(rows)-len(post)+len(post))); print("\n".join(h+" "+p for h,p in post))'
```
