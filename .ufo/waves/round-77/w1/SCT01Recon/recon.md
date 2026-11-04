# SCT01Recon — independent re-derivation of the round-77 base measurements

Seat: SCT01Recon (kama r77 w1). Read-only recon; no edits, no commits, no counter changes.
Base revision: `cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7`. Freeze commit: `7d60e2ab` (adds
`plans/round-77-claims.md`). Lane tip observed while writing: `d86ce85b` (the lane advanced
during this recon; every base measurement below is pinned to the explicit revision it names).
Lane working tree was clean except `.ufo/waves/round-77/w1*` at start; sibling seats wrote
`corpus/lessons/round-77.md`, `tools/round77-citation-baseline.py`,
`tools/round77-selfrecord-round76.py` and `.ufo/waves/round-77/measured/after/` while I ran.
I wrote only this report and the receipts in this directory.

Scratch: `/fast/scratch/hyaku/kama-r77/SCT01Recon/`, deleted before yield after the receipts
below were copied here. No tools installed (python3 and git only).

## Verdicts (summary)

1. **Base audit decomposition: confirmed.** `append-only-audit.py --to cc6e1d3c` reports
   241 events = 95 restored + 5 disclosed + 53 accepted-register + 47 exempt-row + 41
   ungraded-with-no-row. The 41 decompose as **28 fully permitted + 4 out-of-region + 9
   SCORECARD head + 0 neither**. My 41-event set is identical to the 41 findings in the
   committed `measured/before/c2-append.out`.
2. **Three baseline receipts: confirmed.** All three `measured/before/*.out` receipts are
   introduced by `10f37171`, name `rev=dc58e513`, and `dc58e513` is an ancestor of the
   introduction; their sha256 is identical at the introduction and at `cc6e1d3c` (and at
   `b06cc612`, the C1 population tip).
3. **Two named stale facts: confirmed. One additional stale fact exists.** The
   `filtered knowledge entries 46` value re-derives as **47**, and the `## Axes` closure
   pointer names round-75 while the newest at `cc6e1d3c` is round-76. In addition, the
   record's **work tip** `a3fbc629` does not re-derive under the lane's inherited
   closure-sealed rule: the rule derives `0e01f32f`. The base therefore has **three**
   mismatches, not two, and the landed counter prints `corrected=3`, not the frozen
   `corrected=2`. This is stated plainly in §3.3 and §4.5; it is a disagreement with the
   frozen after line, not a measurement gap.
4. **Counter-evidence: no event falls through all six classes** (241/241 covered with the
   planned 9 rows; 0 uncovered at base after classifying the 9 head-eligible events), **no
   baseline receipt has a non-ancestor introduction** (80/80 `measured/before/` paths, 75/75
   `.out` files), and **3 events carry both permitted and graded lines** (`5890d1a0`,
   `9c5a8644`, `ea33a78f`) — the class boundary ruling (d) is load-bearing. The exempt
   register's 9 new head rows include **4 events that postdate the register's own
   introduction**; the round-76 SN01 temporal cutoff would admit only 5, so `exempt=56`
   requires the scope-ruling-(a) reading (row admissible when its event commit is an
   ancestor of the audit revision). Exact figures in §4.

## 1. The 41 unaccounted events at `cc6e1d3c`

### 1.1 Instrument run

```
$ python3 tools/append-only-audit.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 --json > /fast/scratch/hyaku/kama-r77/SCT01Recon/audit-base.json 2> /fast/scratch/hyaku/kama-r77/SCT01Recon/audit-base.err
exit=1
```

`audit-base.err` is empty. Plain (non-JSON) run, same revision:

```
$ python3 tools/append-only-audit.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7
exit=1
summary commits=607 files=148 events=241 restored=95 partial=0 unrestored=53 ungraded=88 disclosed=5 permitted_lines=634 disclosed_lines=10 bad_disclosures=0 ungraded_lines=349 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0
```

The JSON `summary` object:

```
{"commits": 607, "files": 148, "events": 241, "restored": 95, "partial": 0,
 "unrestored": 53, "ungraded": 88, "disclosed": 5, "permitted_lines": 634,
 "disclosed_lines": 10, "bad_disclosures": 0, "ungraded_lines": 349,
 "regressed": 0, "vanished": 0, "unmatched": 0, "binary": 0,
 "bad_declarations": 0}
```

The audit exits 1 because `unrestored=53` (`exit_code()`: partial/unrestored/regressed/
vanished/bad_declarations/bad_disclosures), not because the JSON is unusable.

### 1.2 Independent join

I wrote my own join (`recon_classify.py`, copied here) rather than using
`round76-append-exempt.py`: it loads the audit JSON, the two registers from
`git show cc6e1d3c:registry/append-only-{accepted,exempt}.tsv`, the contract at the same
revision, and re-derives each event's parent section / deleted lines with the frozen
audit's own `sections`/`deleted_lines`/`file_regions` helpers (the audit is the instrument
under test's data source; the counter under test is not used). It classifies every ungraded
event as accepted-row / exempt-row / fully-permitted / out-of-region / head-eligible, and
counts the remainder.

```
$ python3 /fast/scratch/hyaku/kama-r77/SCT01Recon/recon_classify.py
exit=0
accepted rows: 389 exempt rows: 47
accepted header: ['commit', 'file', 'line_sha256', 'count', 'class', 'note']
exempt header: ['commit', 'file', 'class', 'count', 'sections', 'note']

decayed: ungraded 88 exempt-valid 47 unaccounted 41

== decomposition of 41 ==
fully permitted (permitted==deleted, graded==ungraded==0): 28
  PERMITTED 3285cdf7a50481694a36c4425cf32c915ab5e5f0 corpus/SOURCES.md
  PERMITTED e545ed99aaa519196a2a7779b0a293b2ce4c765c corpus/SOURCES.md
  PERMITTED 70af36c2b15b46d3b4b3c15ef20459cff640dfaf corpus/SOURCES.md
  PERMITTED b8e485cc6b201c8e4604a20808e58babbfe08e34 corpus/SOURCES.md
  PERMITTED c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d corpus/SOURCES.md
  PERMITTED 101f3991d3570bc9350fbf9c5561f4be1185699d corpus/SOURCES.md
  PERMITTED 5b108c1a7e943c571140df3a1d7e2e29bfdfb501 corpus/SOURCES.md
  PERMITTED c7311039bcbd76c38b0648d33197864331f34364 corpus/SOURCES.md
  PERMITTED 6433390a5c8f4412c2410c114309ffced5c0572f corpus/SOURCES.md
  PERMITTED 0df800e896f6bce285a81e794ad4ae1d1e6c3a71 corpus/SOURCES.md
  PERMITTED f1e755e0bebccec65bbfef5cc8dc0ffce8279f9d corpus/SOURCES.md
  PERMITTED 92063cfc60e217fa7e2098c568578119b16a1b95 corpus/SOURCES.md
  PERMITTED fa3b62ae6475d111eb466d79af616aeebb08bbb9 corpus/SOURCES.md
  PERMITTED 382d11b2107d335705875da1a4d889b074bd6fa6 corpus/SOURCES.md
  PERMITTED ef76777e5fbdc39a80ec7a93e41dc177366168db corpus/SOURCES.md
  PERMITTED 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c corpus/SOURCES.md
  PERMITTED 9c60eae6f7ed84f7da93d219a406aadc30958c6c corpus/SOURCES.md
  PERMITTED 750e76b9363bfc679fdf134340675c3c925772b6 corpus/SOURCES.md
  PERMITTED 9e9e3c79800f67794b200ef803e9e312193ff451 corpus/SOURCES.md
  PERMITTED 0e2e4ea18facfacad5b64394820d1611aa25c0ae corpus/SOURCES.md
  PERMITTED dc48ee2e9f454b9caf986d14cf81bbc5be28cae1 corpus/SOURCES.md
  PERMITTED e45a4f1b1720482dba7c27077cce4d7a65acc285 corpus/SOURCES.md
  PERMITTED 121e708ad891c5f20d1627ce163c0a32cc509393 corpus/SOURCES.md
  PERMITTED 910e674793e87929a9584791786b61dd0ee75db3 corpus/SOURCES.md
  PERMITTED e2b860c8907a4ba122dbbf5f2b2188695fb7c5f5 corpus/SOURCES.md
  PERMITTED 7c8350f3ca5495e1203ba5ceb6fcbbc43367d193 corpus/SOURCES.md
  PERMITTED e9c415545a6a6ebef310d0f90b965487165aa3f7 corpus/SOURCES.md
  PERMITTED c2aa7fb2c02dd95a185b728d5863f9ae492ecef4 corpus/SOURCES.md
out_of_region (only= contract, all deleted outside): 4
  OUT_OF_REGION 83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 corpus/knowledge/consumer-registry.md prefixes ['## Errata']
  OUT_OF_REGION ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 corpus/knowledge/consumer-registry.md prefixes ['## Errata']
  OUT_OF_REGION 1e41928aba2b81dd65ea75084918a7fadf453720 corpus/knowledge/consumer-registry.md prefixes ['## Errata']
  OUT_OF_REGION 726f737a942f1606d66e032f1efbcbb6f689ccf1 corpus/knowledge/consumer-registry.md prefixes ['## Errata']
exempt-head eligible (SCORECARD head): 9
  HEAD ba9f724800b7385fc3b732924ffebd143344367d SCORECARD.md deleted 2 ungraded 2
  HEAD 900e31b762d51b155fe79f2ef689ca52143e391e SCORECARD.md deleted 1 ungraded 1
  HEAD 11c08bdc0064b9566dc220821db8b9116c6cf788 SCORECARD.md deleted 1 ungraded 1
  HEAD b919f0cb35f40e444899b8de70ea79b813ece678 SCORECARD.md deleted 3 ungraded 3
  HEAD ac1c8538e391bb76cf1118da10d375b95cc4c1e9 SCORECARD.md deleted 2 ungraded 2
  HEAD 461d2adbf2b3fe596a53cb392e2bc6e82af79bfb SCORECARD.md deleted 1 ungraded 1
  HEAD 661622b50b6b49310321e8cb99618010cf65bb75 SCORECARD.md deleted 1 ungraded 1
  HEAD 417bbf811f2968a4567d3d3159ccf22b5d171e4d SCORECARD.md deleted 1 ungraded 1
  HEAD c1ae92d56f61786c22924553038578f23971875e SCORECARD.md deleted 2 ungraded 2
neither: 0

== totals ==
restored 95
disclosed 5
accepted 53 accepted-partial 0
statuses Counter({'restored': 95, 'ungraded': 88, 'unrestored': 53, 'disclosed': 5})
event total 241
permitted-and-graded events: [(('5890d1a0e20c02dd2ff7832a5f7cdc2a5f5ea1d2', 'corpus/SOURCES.md'), 6, 7, 1, 0), (('9c5a864461fadcb2d720a872ce7f83aac6a2ef85', 'corpus/SOURCES.md'), 276, 638, 362, 0), (('ea33a78f2b0bcbbebcde60d2851a81c54746baa8', 'corpus/SOURCES.md'), 277, 639, 362, 0)]
```

(The last tuple is `(commit, file), permitted, deleted, graded, ungraded`.)

### 1.3 Decomposition

| bucket | events | note |
|---|---:|---|
| restored | 95 | `status=restored` |
| disclosed | 5 | `status=disclosed`; commits `ccc4bb31`, `1471344b`, `54c6f4fe`, `8bc8e375`, `3d42897b` |
| accepted register | 53 | `status=unrestored`, every `undisclosed` entry matched by a `(commit,file,line_sha256,count,class)` row |
| exempt register | 47 | `status=ungraded`, class-bound `exempt-head` row with equal count and section list |
| **ungraded, no valid row** | **41** | decomposed below |
| **total** | **241** | 95+5+53+47+41 |

The 41:

| class | events | deleted lines | evidence |
|---|---:|---:|---|
| fully permitted (`permitted == deleted`, `graded == ungraded == 0`) | 28 | 75 | all `corpus/SOURCES.md`; audit's own v6 A-row carriage, commits listed above |
| `out_of_region` | 4 | 19 | all `corpus/knowledge/consumer-registry.md`; contract `only=## Errata`; every deleted line's parent section is outside it (sections: `## Consumer table (config pins)`, `## Correct-pin exemplars (the fix already exists on this box)`, `## Search roots that produced ZERO local-endpoint pins`, `## Open gaps (hand these to the next round)`, `## Correction — round 16 (2026-10-20): seven-verdict vocabulary`) |
| SCORECARD head-eligible (needs the 9 appended `exempt-head` rows) | 9 | 14 | 5 round-75 commits + 4 round-76 commits (see §4.4); parent sections within `## Axes`, `## Planned`, `## Retired`, `## Saturation`, `## Capabilities` |
| neither | 0 | 0 | — |

Cross-check against the committed base receipt: the set of 41 `(commit,file)` pairs from my
join is **identical** to the 41 `APPEND_EXEMPT_FINDING unaccounted` pairs in
`.ufo/waves/round-77/measured/before/c2-append.out` (40 lines copied; comparison script
printed `mine 41 receipt 41`, `identical: True`). The old counter's own base line at
`cc6e1d3c` is `APPEND_EXEMPT events=241 register=53 exempt=47 restored=95 disclosed=5
unaccounted=41 cutoff=10f37171… introductions=2 rotation_safe=1`, exit 1.

The audit invariant `permitted + graded + ungraded == deleted` holds for **all 241 events**
(0 violations), so no event can have `permitted == deleted` and a graded line at the same
time (`permitted == deleted` forces `graded == ungraded == 0`).

## 2. The three round-75 `measured/before/*.out` receipts

The three are `.ufo/waves/round-75/measured/before/{c1-mutants,c2-mutants,c3-audit}.out`.
They are the only `measured/before/*.out` paths the round-75 self-record cites (grep of
`git show cc6e1d3c:corpus/lessons/round-75.md` for `measured/before/` returns exactly those
three). The round-75 record's two `CITATION_BASELINE_UNBOUND`-class citations are instead
`.ufo/waves/round-75/assimilation/summary.out` and `.ufo/waves/round-75/controls/freeze.txt`
(neither is under `measured/before/`; neither carries a `rev=`/`tip=` header among its first
five lines).

### 2.1 Command and verbatim output

```
$ for f in c1-mutants.out c2-mutants.out c3-audit.out; do
    p=".ufo/waves/round-75/measured/before/$f"
    git show cc6e1d3c:$p | sed -n '1,5p'
    git log --diff-filter=A --format='%H %s' cc6e1d3c -- "$p"
    git merge-base --is-ancestor dc58e51315e79d36df5fc530c95fbd3aecbf7593 <intro>; echo "exit=$?"
    git show <intro>:$p | sha256sum
    git show cc6e1d3c:$p | sha256sum
  done
```

```
=== .ufo/waves/round-75/measured/before/c1-mutants.out ===
# round-75 C1 before-receipt (view of one control run; the pinned original is control.out)
# rev=dc58e51315e79d36df5fc530c95fbd3aecbf7593 round=75
# command: python3 .ufo/waves/round-75/controls/mutation-control.py --lane <lane> --work <scratch> --kept
# base: dc58e51315e79d36df5fc530c95fbd3aecbf7593 (freeze 0908bab5)
CONTROL_PRISTINE c1 rc=0
-- introduction --
10f37171fb696c542586cbee96ea4a509ab74afc round-75: interpretation pins (F1b/F2c), survivor probe + two C2 arms, accepted-history register and declaration repair, gate arm 8, S547 and wave evidence
-- merge-base --is-ancestor dc58e51315e79d36df5fc530c95fbd3aecbf7593 10f37171fb696c542586cbee96ea4a509ab74afc --
exit=0
-- sha256 intro / base --
0a2326ec72ba585e26399ef01a3b955fa420319d1cef3dd2abb68af8df2a65ea  -
0a2326ec72ba585e26399ef01a3b955fa420319d1cef3dd2abb68af8df2a65ea  -

=== .ufo/waves/round-75/measured/before/c2-mutants.out ===
# round-75 C2 before-receipt (view of one control run; the pinned original is control.out)
# rev=dc58e51315e79d36df5fc530c95fbd3aecbf7593 round=75
# command: python3 .ufo/waves/round-75/controls/mutation-control.py --lane <lane> --work <scratch>
# base: dc58e51315e79d36df5fc530c95fbd3aecbf7593 (freeze 0908bab5)
CONTROL_PRISTINE c2 rc=0
-- introduction --
10f37171fb696c542586cbee96ea4a509ab74afc round-75: interpretation pins (F1b/F2c), survivor probe + two C2 arms, accepted-history register and declaration repair, gate arm 8, S547 and wave evidence
-- merge-base --is-ancestor dc58e51315e79d36df5fc530c95fbd3aecbf7593 10f37171fb696c542586cbee96ea4a509ab74afc --
exit=0
-- sha256 intro / base --
208e80344488de033199398c176c5b0c5145fc35033b52c3d44189b460cf3d29  -
208e80344488de033199398c176c5b0c5145fc35033b52c3d44189b460cf3d29  -

=== .ufo/waves/round-75/measured/before/c3-audit.out ===
# round-75 C3 before-receipt (view of one control run; the pinned original is control.out)
# rev=dc58e51315e79d36df5fc530c95fbd3aecbf7593 round=75
# command: python3 .ufo/waves/round-75/controls/mutation-control.py --lane <lane> --work <scratch>
CONTROL_C3 summary commits=575 files=143 events=223 restored=87 partial=0 unrestored=53 ungraded=78 disclosed=5 permitted_lines=633 disclosed_lines=10 bad_disclosures=0 ungraded_lines=330 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=5
CONTROL_C3 exit=1
-- introduction --
10f37171fb696c542586cbee96ea4a509ab74afc round-75: interpretation pins (F1b/F2c), survivor probe + two C2 arms, accepted-history register and declaration repair, gate arm 8, S547 and wave evidence
-- merge-base --is-ancestor dc58e51315e79d36df5fc530c95fbd3aecbf7593 10f37171fb696c542586cbee96ea4a509ab74afc --
exit=0
-- sha256 intro / base --
e6aee72df7e88b94524030b8410fdb8508f4415315c026da4f11f5b20cc7fb7a  -
e6aee72df7e88b94524030b8410fdb8508f4415315c026da4f11f5b20cc7fb7a  -
```

### 2.2 Table

| receipt | 40-hex revisions in first five lines | introduction | `dc58e513` ancestor of intro | intro ancestor of `cc6e1d3c` | sha256 intro = sha256 `cc6e1d3c` |
|---|---|---|---|---|---|
| `c1-mutants.out` | `{dc58e51315e79d36df5fc530c95fbd3aecbf7593}` (named twice: `rev=` and `base:`) | `10f37171fb696c542586cbee96ea4a509ab74afc` | exit 0 | exit 0 | `0a2326ec72ba585e26399ef01a3b955fa420319d1cef3dd2abb68af8df2a65ea` |
| `c2-mutants.out` | `{dc58e513…}` (twice) | `10f37171…` | exit 0 | exit 0 | `208e80344488de033199398c176c5b0c5145fc35033b52c3d44189b460cf3d29` |
| `c3-audit.out` | `{dc58e513…}` (once) | `10f37171…` | exit 0 | exit 0 | `e6aee72df7e88b94524030b8410fdb8508f4415315c026da4f11f5b20cc7fb7a` |

Each introduction is a single `--diff-filter=A` commit (no re-add). The sha256 is also
unchanged at `b06cc612` (the C1 population tip):

```
sha at b06cc612: 0a2326ec…  (c1-mutants.out)
sha at b06cc612: 208e8034…  (c2-mutants.out)
sha at b06cc612: e6aee72d…  (c3-audit.out)
```

### 2.3 Population-tip note (not a contradiction)

The C1 base receipt's own first line is
`RECEIPT_SCOPE_POP round=75 tip=b06cc612711560c53eef3ec21484c6963601262f source=plan:plans/round-76-claims.md`.
The round-76 counter, run at that tip, reproduces the base line exactly:

```
$ python3 tools/round76-receipt-scope.py --repo . --round 75 --tip b06cc612711560c53eef3ec21484c6963601262f
exit=1
RECEIPT_SCOPE_POP round=75 tip=b06cc612711560c53eef3ec21484c6963601262f source=explicit:--tip
RECEIPT_SCOPE_QUOTED .ufo/waves/round-75/controls/build-spec.py
RECEIPT_SCOPE_UNBOUND .ufo/waves/round-75/assimilation/summary.out :: no tip=/rev= header among the first 5 lines
RECEIPT_SCOPE_UNBOUND .ufo/waves/round-75/controls/freeze.txt :: no tip=/rev= header among the first 5 lines
RECEIPT_SCOPE_FINDING shifted .ufo/waves/round-75/measured/before/c1-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_SCOPE_FINDING shifted .ufo/waves/round-75/measured/before/c2-mutants.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_SCOPE_FINDING shifted .ufo/waves/round-75/measured/before/c3-audit.out :: registry/append-only-contract.tsv touched by b8ed25682958
RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=6 unbound=2 shifted=3 nonreceipt=0 unclassified=0
```

At `cc6e1d3c` the same old counter prints `bound=0 … shifted=9` because the round-76 wave
paths enter `rev..tip`; that is a different population tip, not a contradiction of the C1
base receipt. The `registry/append-only-contract.tsv` touch at `b8ed2568` is the exact
non-record delta the baseline class must ignore.

## 3. The stale round-76 facts

### 3.1 `filtered knowledge entries 46` vs 47

The record sentence is at `SCORECARD.md:4189-4191` (base blob; `## Round 76` section). The
line that carries the value is line 4190:

```
$ git show cc6e1d3c:SCORECARD.md | nl -ba | sed -n '4186,4192p'
4186  Axis harm check: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 —
4187  no score dropped, no axis retired; the two misses are target defects, and neither the claim work
4188  nor its instruments harmed an axis (the harness's own before/after receipts show three stale
4189  values repaired). Population at `rev=c2aa7fb2`: gate registry unchanged; sources census 288 rows
4190  exit 0; filtered knowledge entries 46; `SKILL.md` 1736 lines sha256 `f18c9bcc…` (unchanged);
4191  `PROVINCE.md` 322 lines sha256 `af459acf…` (unchanged).
```

The count at the revision the record names (`c2aa7fb2`), by the record's own filter
(`engine-sides`/`processes` excluded, the coverage row's command):

```
$ git ls-tree -r --name-only c2aa7fb2c02dd95a185b728d5863f9ae492ecef4 corpus/knowledge/ | wc -l
49
$ git ls-tree -r --name-only c2aa7fb2c02dd95a185b728d5863f9ae492ecef4 corpus/knowledge/ | grep -v 'engine-sides\|processes' | wc -l
47
$ git ls-tree -r --name-only cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 corpus/knowledge/ | grep -v 'engine-sides\|processes' | wc -l
47
```

The raw directory has 49 `.md` files; the *filtered* population the record itself uses is
**47**. The `## Axes` coverage row at line 18 already prints `47`, and the round-76
closure's D2 states the same (`corpus/lessons/round-76-verifier-spotcheck.md:159`, with the
exact command above). **Mismatch confirmed: filed 46, derived 47.** The round-77 plan's
phrasing "`corpus/knowledge/` at `c2aa7fb2` holds 47" is true only under the filtered
population; the unfiltered tree holds 49.

### 3.2 `## Axes` calibration row's closure pointer

The row at `SCORECARD.md:18` contains, at offset 1430:

```
latest outside closure `corpus/lessons/round-75-verifier-spotcheck.md`
```

The newest closure at the base revision is round-76. The independent closure counter
(`round69-newest-closure-counter.py`, scope `--since-round 63` as the lane's contract pins):

```
$ python3 tools/round69-newest-closure-counter.py --repo . --rev cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 --since-round 63
exit=1
MEMBER corpus/lessons/round-63-verifier-spotcheck.md date=2026-10-28 source=body
MEMBER corpus/lessons/round-64-verifier-spotcheck.md date=2026-10-30 source=heading
MEMBER corpus/lessons/round-65-verifier-spotcheck.md date=2026-11-01 source=heading
MEMBER corpus/lessons/round-66-verifier-spotcheck.md date=2026-11-01 source=heading
MEMBER corpus/lessons/round-67-verifier-spotcheck.md date=2026-11-01 source=heading
MEMBER corpus/lessons/round-68-verifier-spotcheck.md date=2026-11-01 source=heading
MEMBER corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 source=heading
MEMBER corpus/lessons/round-70-verifier-spotcheck.md date=2026-11-03 source=heading
MEMBER corpus/lessons/round-71-verifier-spotcheck.md date=2026-11-03 source=heading
MEMBER corpus/lessons/round-72-verifier-spotcheck.md date=2026-11-03 source=body
MEMBER corpus/lessons/round-73-verifier-spotcheck.md date=2026-11-04 source=body
MEMBER corpus/lessons/round-74-verifier-spotcheck.md date=2026-11-04 source=body
MEMBER corpus/lessons/round-75-verifier-spotcheck.md date=2026-11-04 source=body
MEMBER corpus/lessons/round-76-verifier-spotcheck.md date=2026-11-04 source=body
SCOPE population=rounds>=63 members=14
NEWEST_CLOSURE newest=corpus/lessons/round-76-verifier-spotcheck.md date=2026-11-04 round=76 row_names=corpus/lessons/round-75-verifier-spotcheck.md row_current=false
STALE_CALIBRATION row_names=corpus/lessons/round-75-verifier-spotcheck.md newest=corpus/lessons/round-76-verifier-spotcheck.md newest_date=2026-11-04
```

Without `--since-round 63` the counter exits 2 on an undated round-10 closure in scope; the
lane's contract pins the fresh-start scope at 63. The round-76 closure is introduced by
`35babc5a` and amended by the base commit `cc6e1d3c` itself, both ancestors of the base.
**Mismatch confirmed: row names round-75, newest is round-76.**

### 3.3 Counter-evidence: a third stale fact (work tip) — the frozen `corrected=2` is wrong

The round-76 record files, at `LOG.md:3061`:

```
Frozen plan `plans/round-76-claims.md` (base `b06cc612…`, freeze `1a85a991…`); work tip `a3fbc629fa18c26ad1192adc5d8e762671dd1d79`.
```

The lane's inherited closure-sealed rule — the one the round-76 C2 correction used for
round 75 (`LOG.md:3027-3032`: "the last non-record commit of that round is `c9ab73d8…`" —
the `PROVINCE.md` capability-evidence row) — applied to round 76:

```
$ python3 (worktip replica; freeze=1a85a991, boundary=35babc5a, record paths = LOG.md,
  SCORECARD.md, corpus/README.md, corpus/lessons/**, .ufo/waves/round-76/**)
round-75 rule: ('c9ab73d842051db5f8320bced4357bf13cf14108',
                "round-75: name the three round-75 instruments in PROVINCE.md's capability evidence row")
round-76 rule: ('0e01f32f50a208595122b446db25c4902d379075',
                'round-76: province surface rows for the three instruments, lesson citation repairs, assimilation summary receipt')
```

`c9ab73d8` is exactly the corrected value in the round-76 LOG correction, so the rule is
validated on round 75. For round 76 it derives `0e01f32f`, not the filed `a3fbc629`.

The landed counter (`tools/round77-selfrecord-round76.py`, committed at `d86ce85b`)
implements that rule and reports, at the base revision:

```
$ python3 tools/round77-selfrecord-round76.py --repo . --rev cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7
exit=1
SELFRECORD_R76 claims=6 mismatches=3 corrected=0 unbacked=0
SELFRECORD_R76_FACT work-tip filed=a3fbc629fa18c26ad1192adc5d8e762671dd1d79 derived=0e01f32f50a208595122b446db25c4902d379075
SELFRECORD_R76_FACT knowledge-entries filed=46 derived=47
SELFRECORD_R76_FACT closure-pointer filed=corpus/lessons/round-75-verifier-spotcheck.md derived=corpus/lessons/round-76-verifier-spotcheck.md
```

At the integration tip the same counter prints:

```
$ python3 tools/round77-selfrecord-round76.py --repo . --rev d86ce85b72121617dc79795c8c046ffc94de33a4
exit=0
SELFRECORD_R76 claims=6 mismatches=0 corrected=3 unbacked=0
```

Three correction blocks landed at `d86ce85b`: `work-tip` (`LOG.md:3122`, `Corrected:
0e01f32f…`), `knowledge-entries` (`SCORECARD.md:4276`, `Corrected: 47`) and
`closure-pointer` (`SCORECARD.md:4288`, `Corrected:
corpus/lessons/round-76-verifier-spotcheck.md`). The `work-tip` block itself says:
"under the lane's inherited rule … the `PROVINCE.md` surface row commit `0e01f32f`
postdates the instrument-receipt commit the record named."

**Finding, stated plainly:** the base has **three** stale round-76 facts, not two. The
frozen C3 after line `SELFRECORD_R76 claims=6 mismatches=0 corrected=2 unbacked=0` is not
what the landed counter prints (`corrected=3`); the round's green state is
`mismatches=0 corrected=3`. This cannot be fixed by relabelling: either the frozen count
`corrected=2` is wrong, or the work-tip correction must be suppressed/defined away, which
would contradict the lane's own round-76 work-tip precedent. It is a freeze-target defect
in the same family as the round-76 C1/C3 misses, and it should be recorded as such, not
presented as a green C3. (The predicate sentence itself calls for "each of the six declared
… facts" to re-derive or be superseded; it does not forbid a third correction, but its
printed line pins `corrected=2`.)

The other four facts re-derive (my independent checks, matching the landed counter):

| fact | filed | derived | result |
|---|---|---|---|
| `gate-tally` | `PRE_REPORT_SELFTEST pass=21 fail=0` | same; backed by `.ufo/waves/round-76/measured/after/gate-selftest.out` | match |
| `capability-count` | 31 (`6 axes and 31 capabilities remain active`) | 31 (canonical table rows − 2 = 33 − 2) | match |
| `knowledge-entries` | 46 | 47 | **mismatch** |
| `sources-rows` | 288 | 288 (`^ {0,3}\|\s*S[0-9]{3,}` at `c2aa7fb2`) | match |
| `closure-pointer` | `corpus/lessons/round-75-verifier-spotcheck.md` | `corpus/lessons/round-76-verifier-spotcheck.md` | **mismatch** |
| `work-tip` | `a3fbc629…` | `0e01f32f…` | **mismatch** (third) |

## 4. Counter-evidence

### 4.1 An event that falls through all six accounting classes

**None.** With the 9 planned `exempt-head` rows, every one of the 241 events has exactly one
class:

```
class counts: {'restored': 95, 'exempt': 47, 'out_of_region': 4, 'permitted': 28,
               'disclosed': 5, 'accepted': 53, 'head-eligible-unrowed': 9} sum 241
fall-through events: 0
```

At the base register state (47 exempt rows, no 9 new rows) the 9 SCORECARD head events are
the only class-eligible events without rows; they are exactly the remainder after the 28
permitted and 4 out-of-region. The landed C2 counter, run with the current (56-row) register
and `--to cc6e1d3c`, prints the frozen line and exits 0:

```
$ python3 tools/round77-append-registers.py --repo . --to cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7
exit=0
APPEND_REGISTERS to=cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7 events=241 accepted=53 exempt=56 permitted=28 out_of_region=4 restored=95 disclosed=5 unaccounted=0 accepted_cutoff=10f37171fb696c542586cbee96ea4a509ab74afc exempt_cutoff=c2aa7fb2c02dd95a185b728d5863f9ae492ecef4 introductions=1/1 rotation_safe=1
```

### 4.2 A baseline receipt whose introduction is not an ancestor of `cc6e1d3c`

**None found.** I scanned every path under a `measured/before/` directory in the base tree
(80 paths, not just `.out`):

```
all measured/before paths at base: 80
no-add-commit: []
introduction not ancestor: []
first-five-lines name no 40-hex: 60
first-five-lines name >1 distinct 40-hex: 2
bytes changed intro->base: 1
```

The three round-75 receipts are among the 80; every introduction is an ancestor. The two
non-ancestor-like hazards I did find are **outside the round-75 citation population**, so
they do not change `bound=9`, but they are live instances of the class's other legs:

- **`baseline-edited` instance:** `.ufo/waves/round-72/measured/before/round-scope-control-old.out`
  changed bytes between its introduction `090a0b25…` and the base (sha differs). If it were
  cited by the round-75 record it would fail the byte-stability leg and stay `shifted`.
- **"one 40-hex revision" instance:** two baseline receipts name **two distinct** 40-hex
  revisions in their first five lines —
  `.ufo/waves/round-73/measured/before/sources-census-start.out`
  (`24bc96ad…`, `704366d7…`) and `.ufo/waves/round-76/measured/before/c2-facts.out`
  (`b06cc612…`, `c9ab73d8…`). Under the strict "name one 40-hex revision" clause they would
  be unbound/could-not-evaluate if cited. Neither is in the round-75 population.

The two round-75 receipts with no 40-hex in the first five lines are the expected
`CITATION_BASELINE_UNBOUND` pair (they are outside `measured/before/`): 
`.ufo/waves/round-75/assimilation/summary.out` and `.ufo/waves/round-75/controls/freeze.txt`
(the latter names `base_rev dc58e513…` but has no `rev=`/`tip=` header; under the baseline
class it is not a `measured/before/` path, so it remains unbound).

### 4.3 A permitted event that also carries a graded line

**Three events** carry `permitted > 0` *and* graded lines:

| commit | file | status | deleted | graded | ungraded | permitted | undisclosed |
|---|---|---|---:|---:|---:|---:|---:|
| `5890d1a0e20c02dd2ff7832a5f7cdc2a5f5ea1d2` | `corpus/SOURCES.md` | restored | 7 | 1 | 0 | 6 | 0 |
| `9c5a864461fadcb2d720a872ce7f83aac6a2ef85` | `corpus/SOURCES.md` | restored | 638 | 362 | 0 | 276 | 0 |
| `ea33a78f2b0bcbbebcde60d2851a81c54746baa8` | `corpus/SOURCES.md` | unrestored | 639 | 362 | 0 | 277 | 288 |

Ruling (d) (`permitted == deleted` ∧ `graded == 0` ∧ `ungraded == 0`) excludes all three;
`9c5a8644` and `5890d1a0` are restored, `ea33a78f` is an accepted-register event. A counter
that classified on `permitted > 0` would launder 362 graded lines in `ea33a78f` (and
misclassify the other two); the landed C2 counter has a `permitted-overclaim` selftest arm
for this. The audit invariant holds for all 241 events, so no event can satisfy
`permitted == deleted` while carrying a graded line.

### 4.4 Exempt-cutoff tension: 4 of the 9 head events postdate the exempt register

All 9 head events are ancestors of the audit revision (they are reported at `cc6e1d3c`), but
only 5 are ancestors of the exempt register's introduction `c2aa7fb2`:

```
9 head events ancestor of c2aa7fb2: 5 of 9
9 head events ancestor of 10f37171 (the accepted register's introduction): 0 of 9
```

The four post-introduction events are `461d2adb` (`## Axes`), `661622b5` (`## Axes`),
`417bbf81` (`## Saturation`) and `c1ae92d5` (`## Axes`), all round-76 head edits. The
round-76 SN01 rule ("a register row must not bless a deletion made at or after the register's
own introduction") would admit only the 5 pre-introduction head rows: `exempt=52`,
`unaccounted=4`, not the frozen `exempt=56 unaccounted=0`. The frozen line is reachable only
under C2 scope ruling (a): "a row is admissible when the event commit it names is an ancestor
of the audit revision". That is the reading the landed counter implements. The predicate's
phrase "under that register's own introduction cutoff" is ambiguous between the SN01 window
and the ruling-(a) ancestry window; the after line and the landed counter force ruling (a).
This is a **divergence from the round-76 temporal-cutoff rule** that the lesson/report should
record explicitly, not leave implicit in a phrase. The old round-76 counter at the current
tip demonstrates the difference: with the 9 rows present it prints 18 `rotation` findings
(9 rows × 2 loops), `unaccounted=41`, `rotation_safe=0` — it calls the new rows "rotation"
because it applies the single earliest cutoff, while the new counter correctly reserves
`rotation` for a re-introduction of the register path (C2 ruling (b)).

### 4.5 C3's frozen `corrected=2` vs the landed `corrected=3`

See §3.3. This is the strongest counter-evidence: the base has three stale facts under the
lane's own rule, the landed counter prints `mismatches=0 corrected=3`, and the frozen C3
line pins `corrected=2`. The two named stale facts in the plan are correct as far as they go;
the plan's population is missing the work-tip fact, which the round's own correction block
then had to add.

## 5. Reproducibility notes and cross-checks

- Audit/instrument: `python3 tools/append-only-audit.py --repo . --to cc6e1d3c --json`
  (exit 1, valid JSON). The exit is the audit's `unrestored=53`, not a failure; a counter
  that treats any nonzero audit exit as could-not-evaluate would exit 2 here.
- Registers at base: `git show cc6e1d3c:registry/append-only-accepted.tsv` = 389 rows (53
  events); `git show cc6e1d3c:registry/append-only-exempt.tsv` = 47 rows, all
  `SCORECARD.md` / class `exempt-head`; no event is in both accepted and exempt; no
  permitted event is in either register.
- Introduction cutoffs: accepted `10f37171` (single `--diff-filter=A`), exempt `c2aa7fb2`
  (single). All 389 accepted rows name events ancestral to `10f37171`; all 47 exempt rows
  name events ancestral to `c2aa7fb2`.
- My 41-event join == the committed 41 findings (set equality, both 41).
- The landed C1 counter at the current tree prints the frozen line:
  `CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0
  nonreceipt=0 unclassified=0`, exit 0 (population tip `b06cc612`, two unbound =
  `assimilation/summary.out`, `controls/freeze.txt`).
- The landed C2 counter prints the frozen line at `--to cc6e1d3c` (exit 0, above).
- The landed C3 counter does **not** print the frozen line: `corrected=3` at `d86ce85b`.

## 6. Receipts in this directory

All commands above were run from
`/home/vgpnk/Projects/shokunin/kama-shokunin` with read-only git and `python3`; no commits,
no `git add`, no writes to the lane outside this directory. Scratch
`/fast/scratch/hyaku/kama-r77/SCT01Recon/` was deleted after copying:

- `audit-base.json`, `audit-base.txt` — the base audit receipt (JSON + plain event list)
- `recon_classify.py`, `recon_classify.out` — my independent join and its output
- `counter_evidence.py`, `counter_evidence.out` — invariant/fall-through/baseline scan
- `decomposition-table.txt` — all 88 ungraded events with class, counts, sections
- `receipts-verify.out` — first-five-lines, introduction, ancestry, sha256 for the three
  round-75 before receipts
- `facts-verify.out` — population sentence, calibration pointer, knowledge counts
- `closure-base.out` — round69 newest-closure counter at `cc6e1d3c`
- `r76-append-at-head.out` — round76 append counter at the then-HEAD (rotation findings)
- `r76-scope-at-b06cc612.out` — round76 receipt-scope counter at the C1 population tip
- `c1-current.out`, `c2-current.out`, `c3-at-base.out`, `c3-at-integration.out` — the landed
  round-77 counters' relevant runs
- `knowledge-c2aa7fb2.txt` — the 49 `corpus/knowledge/` paths at `c2aa7fb2`

One run whose full output was not retained: `tools/round76-receipt-scope.py --repo .
--round 75 --tip cc6e1d3c --all-findings` (exit 1; summary
`RECEIPT_SCOPE round=75 fenced_quoted=1 live_citations=11 bound=0 unbound=2 shifted=9
nonreceipt=0 unclassified=0`; the 245 KB detail file was in scratch and is not copied
because it is out of the C1 population; the command is re-runnable).
