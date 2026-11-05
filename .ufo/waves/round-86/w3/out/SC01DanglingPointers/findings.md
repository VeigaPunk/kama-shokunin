# SC01DanglingPointers — per-surface recon of the round-86 terminal record

Seat: `SC01DanglingPointers` (scout, w3). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Target record tip: `bafae7afb41843564ac2468d28beb8e0bb98e8e6` (ancestor of lane HEAD `84e6f4573c2a0120def1cb8a37821a8c000686bb`).
Surfaces read: `plans/round-86-claims.md` (full), `SCORECARD.md` §Round 86 (lines 5258–5357),
`LOG.md` §Round 86 (lines 3540–3595), `corpus/lessons/round-86.md` (109 lines),
plus the three instruments, the frozen counter, the debt selftest, `PROVINCE.md`, `corpus/SOURCES.md`.

Scratch: `/fast/scratch/hyaku/kama-r86/SC01DanglingPointers/` (a `git clone --shared` of the lane checked
out at the tip, plus a `git archive` copy). Removed before yield.

## Verdict per item

| # | Item | Verdict | Evidence (command → exact line) |
|---|---|---|---|
| V1 | Every path cited by the four round-86 surfaces exists at the tip | **PASS (86/86 lane-relative paths)** | `git cat-file -e bafae7a…:<path>` → every one of the 86 extracted lane-relative paths resolves. The only non-resolving extraction is `scripts/sources-census.sh`, which the plan cites as the **absolute fleet path** `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` — that file exists on disk (`-rwxr-xr-x … 35466 Oct 19`). `corpus/lessons/round-` is a regex fragment, not a path. |
| V2 | Every cited revision resolves | **PASS** | `git rev-parse --verify <h>^{commit}` → `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` (base), `c07e1f909414aafb2d8de5605a81fd3bd4e3550e` (freeze), `3e93febb0f40955b08dc80367e8ef658eaccdfd6`, `948dec784a9736b4a36d6a10d303fbee054b19c6`, `65665250e58f5deec028ad53809296e08373818a`, `c0d7fbd842b66d56483e7ca05b62752341c8b3c4`, `6abaf0a8d11a76b141f37a9e9f6144b797af0b24`, `bafae7af…`, `84e6f457…`, `239a8f39…`, `0f8a0980…`, `c5d71b7a…` all resolve. `base IS ancestor of freeze` = yes. |
| V3 | Frozen counter re-runs at base reproduce the frozen before receipts byte-for-byte | **PASS** | `count.py c1 --rev 3ff23da3…` → `RENDERED_CELLS facts=3 mismatches=3 gate=0 closure=0 disposition=0 newest_gate=85 newest_closure=85` (exit 1) = `.ufo/waves/round-86/measured/before/c1.out`. `c2` → `DEBT_MUTANT_OWNERS mutants=5 killed=3 escaped=2 invalid=0 arms=unknown cardinality=ok owners=3/5` (exit 1) = `before/c2.out`. `c3` → `could-not-evaluate: no tools/round86-pin-origin.py at 3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d` (exit 2) = `before/c3.out`. All three before receipts also exist at the freeze `c07e1f90`. |
| V4 | Counters re-run at the tip reproduce the recorded after receipts | **PARTIAL — 1 receipt does not reproduce** | `c1` at tip → identical to `after/c1.out` (`diff` empty). `c3` at tip → identical to `after/c3.out` **and live-verified today**: `PIN_ORIGIN rows=5 verified=5 mismatch=0 unreachable=0 bad=0` (network fetch of all 5 upstream ranges re-succeeds). `c2` at tip → **differs on line 7**: receipt `DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34` vs re-run `… pass=34 fail=0`. See **F1**. All three selftest receipts (`after/c1-selftest.out`, `after/c2-selftest.out`, `after/c3-selftest.out`) reproduce byte-for-byte: `pass=17 fail=0`, `pass=13 fail=0`, `pass=7 fail=0`. |
| V5 | The committed mutant driver re-runs and kills 10/10 | **PASS** | `python3 .ufo/waves/round-86/measured/after/c1-mutants.py .` → `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0` (exit 0) = committed `after/c1-mutants.out`. |
| V6 | Three capability rows named in the canonical capabilities table | **PASS** | `SELFDESC_CANON_V2 canon_round=86 canon_rows=52 demonstrated=0 total=52 invisible=0` (exit 0). `rendered-cell-identity`, `mutant-owning-arms`, `pin-origin-corroboration` each appear once in the canonical table (SCORECARD 5355–5357) and once in the mirror (176–178); the two 52-row sets are identical in names and order. |
| V7 | Three capability rows named in the PROVINCE.md surface list | **PARTIAL** | All three tools are named in `PROVINCE.md` (lines 408 `tools/round86-rendered-cells.py`, 411 `tools/round86-mutant-owners.py`, 415 `tools/round86-pin-origin.py`) — but in the Round-86 note paragraph, **not** inside the "Owns (surfaces)" table's lane-instruments cell (no `tools/round8*` appears in that cell). See **F9**. |
| V8 | The SCORECARD coverage row's surface hash / count re-derive | **PASS** | `sha256sum PROVINCE.md` → `c7589cc881cd21fb814be2ee9f4e0f7668deff2e192ca5103b0212b56826f95b` (matches the asserted hash) and `wc -l` → `419`; the asserted knowledge count re-derives as `57`. Both hold at `bafae7a…` **and** at lane HEAD `84e6f457…`. |
| V9 | Registry rows / counts the record cites | **PASS** | `SOURCES.md` at base = 317 rows / tier A 302 / mined 284; at tip = **319 rows / A 304 / mined 286** — matches "317→319 rows (A302→304, mined 284→286)". `S576` `used-by` = `corpus/lessons/round-85.md, corpus/lessons/round-86.md` (base: only round-85) ✓. `S578` (fenced, §4.5) and `S579` (indented, §4.4) both `status=mined opened=2026-11-04 recheck=on-release used-by=corpus/lessons/round-86.md` ✓. `sources-census.sh validate --root … kama` → `kama ok …/corpus/SOURCES.md`, exit 0, W04 duplicate-url warnings for S576/S578/S579 exactly as the lesson discloses. |
| V10 | CommonMark quotes the lesson cites are verbatim | **PASS** | Against the committed spec copy `.ufo/waves/round-86/w2/out/SC01SourcesCensus/receipts/commonmark-0.31.2.fetched.html`: "A fenced code block begins with a code fence, preceded by up to three spaces of indentation." FOUND; "An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation." FOUND; "The opening # character may be preceded by up to three spaces of indentation." FOUND. Section numbers confirmed from the same file: atx-headings = 4.2, indented-code-blocks = **4.4**, fenced-code-blocks = **4.5**. |
| V11 | The frozen predicate sentences match the instruments' own `PREDICATE` constants | **PASS** | C2 and C3 `PREDICATE` strings are byte-equal (whitespace-normalised) to the plan's blockquotes. C1 is byte-equal too once the plan's multi-line blockquote is joined (a single-line `startswith` comparison reports False — the sentence spans three lines). |
| V12 | Append-only acceptance rows the record cites | **PASS** | `registry/append-only-late.tsv` has exactly **15** rows whose note says "round-86 accepts", covering commits `3e93febb…` (1), `65665250…` (12), `948dec78…` (1), `c0d7fbd8…` (1) — the exact list the SCORECARD names. |
| V13 | The R84V5 erratum's own claim about round 84 | **PASS** | `git cat-file -e bafae7a…:.ufo/waves/round-84/measured/before/red-selfrecord.out` → MISSING (the plan's cited path really does not exist), while `.ufo/waves/round-84/measured/after/c2-red.out` exists with header `# rev=3e93febb0f40955b08dc80367e8ef658eaccdfd6` / `# cmd: python3 tools/round84-selfrecord-round83.py --repo . --no-corrections` — exactly the erratum's description. |
| V14 | Lesson M1's cited round-85 evidence | **PASS** | `.ufo/waves/round-85/w1/out/SN01Scope/receipts/fenced-shadow.md` exists and contains the described shape: a fenced block carrying both correct-looking cells, a live authority line "round84 is under terminal measurement", and a live calibration row naming round-83. `.ufo/waves/round-85/w1/out/CR01Cheats/receipts.json` exists. |

## Findings (content mismatches — the record's own numbers against committed bytes)

### F1 — HIGH — `.ufo/waves/round-86/measured/after/c2.out` (the C2 after-receipt) does not reproduce from committed bytes

SCORECARD §Round 86 cites this file as the C2 evidence. Its last line is

```
DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34
```

Re-running the frozen counter against the committed tree gives

```
DEBT_MUTANT_OWNERS_PRISTINE APPEND_DEBT_SELFTEST pass=34 fail=0
```

(`python3 .ufo/waves/round-86/count.py c2 --repo . --rev bafae7af… --work <scratch>` → `diff` reports exactly
line 7). The same mismatch appears when the leg is re-run at the receipt's own introducing commit
`c5d71b7a` — so the receipt is not reproducible at any revision, and its `arms=34` is the **pre-EX02GateArms**
summary shape (the debt selftest at `bafae7a` prints the round-81 shape
`print(f"APPEND_DEBT_SELFTEST pass={len(cases) - fail} fail={fail}")`, `tools/round81-append-debt.py:689`).
The record's own prose in the same section says "the summary keeps its round-81 shape"; its own cited
receipt shows the other shape. The claimed headline line (`mutants=5 killed=5 escaped=0 invalid=0 arms=34
cardinality=ok owners=5/5`) is unaffected — the defect is confined to the PRISTINE echo line.

### F2 — HIGH — the lesson quotes a token its cited receipt does not contain

`corpus/lessons/round-86.md:59-60` (M3):

> 7/7 source mutants are now killed by named arms (`RENDERED_CELLS_MUTANTS mutants=7 killed=7 escaped=0`, `.ufo/waves/round-86/measured/after/c1-mutants.out`)

The committed receipt at that path says `RENDERED_CELLS_MUTANTS mutants=10 killed=10 escaped=0`
(10 mutants, `killed=10`). The quoted token is absent from the cited file. SCORECARD and LOG both say
**10/10** ("10 source mutants each killed by a named arm"; "10/10 source mutants are killed by named
arms"), so the lesson is the outlier — it was written at `c5d71b7a` (7 mutants) and never refreshed when
`7a21aaa1` grew the population to 10. The stale 7/7 quote is still present at lane HEAD `84e6f457`
(that commit only appended a "Frontier and considerthese" section to the lesson).

### F3 — HIGH — lesson M6's "Fix" sentence contradicts the committed classifier and its own cited arm

`corpus/lessons/round-86.md:86-88` (M6):

> Fix: `classify()` now requires exactly one ARMS line (a summary with no declared population cannot reconcile) … arms `summary-without-arms-field`, `no-arms-line` and `stderr-noise` hold it (selftest 13/0).

Committed code, `tools/round86-mutant-owners.py:117-121`: the guard is `if len(arms_lines) > 1:` (i.e. **at
most** one; zero is allowed) and the whole reconciliation block sits under `if arms_lines:` — with no ARMS
line present, **no** cardinality clause is evaluated. Direct probe of the committed classifier:

```
classify("APPEND_DEBT_SELFTEST pass=0 fail=0\n", "", 0, "summary-cardinality")
  -> ('escaped', 'summary-cardinality', 'green summary')
```

i.e. a forged summary with **no declared population** reconciles green — the opposite of the lesson's
sentence. Source-level reproduction: deleting the ARMS print line and forging the summary to
`pass=0 fail=0` yields a selftest that exits **0** ("green summary"), classified `escaped` for every owner
label tried (`summary-cardinality`, `arm-count`). The instrument's own selftest arm is named
`no-arms-line-disclosed-limit` and expects `escaped` — it *documents* the limit, it does not "hold" the fix
as the lesson claims. There is no arm named `no-arms-line` in the instrument or in
`.ufo/waves/round-86/measured/after/c2-selftest.out` (which lists `stderr-noise`,
`summary-without-arms-field`, `no-arms-line-disclosed-limit`). Note the frozen plan's own clause is
"exactly one summary line and **at most one** `APPEND_DEBT_SELFTEST_ARMS` line" — the lesson, not the plan,
is the outlier. The plan's kill rule ("a cardinality clause that a forged summary can satisfy") is thus
arguably met by an undisclosed survivor; the lesson discloses only the *consistent-forgery* (b2) class.

### F4 — HIGH — the C1 gate fact's "coupled" assertion is satisfied by a revision the sentence does not name

The head banner at `bafae7a` says "Terminal gate measured at `948dec784a9736b4a36d6a10d303fbee054b19c6` …
receipt `.ufo/waves/round-85/measured/after/gate.out`". That receipt **does not exist at 948dec78**:

```
git cat-file -e 948dec78…:.ufo/waves/round-85/measured/after/gate.out   ->  fatal: path … exists on disk, but not in '948dec78…'
git log --oneline --diff-filter=A -- .ufo/waves/round-85/measured/after/gate.out  ->  6abaf0a8 round-85: publish measured results …
```

`gate_fact()` (`tools/round86-rendered-cells.py:311-318`) loops over **all** 40-hex revisions in the
paragraph and accepts if *any* ancestor carries the receipt with the token — and the same paragraph also
contains `6abaf0a8d11a76b141f37a9e9f6144b797af0b24` ("delivered `6abaf0a8…`"), which does carry it. Fixture
probe against the real tree:

```
authority naming only 948dec78  ->  [('gate', 'no revision among 1 is an ancestor carrying … with the exact token')]
authority + 6abaf0a8            ->  []            (green)
```

So `gate=1` at the tip is green through an incidental second revision, not through the revision the
sentence couples the receipt to. Lesson M5 and SCORECARD both state the fix as "the instrument now reads
`git show R:path`" / "the receipt is read at the revision the banner names" — the code does not do that.
(The plan's clause 5 wording, "a 40-hex revision `R` in the same paragraph", is loose enough to admit it,
so this is a record-vs-implementation divergence rather than a plan violation.) The lane later fixed the
symptom by re-pointing the banner to `0f8a0980` / `239a8f39` (`239a8f39`, `84e6f457`).

### F5 — MEDIUM — the record's counting-command cells carry unresolved placeholders at the tip

`SCORECARD.md:5271-5273` (Round-86 measured-results table) at `bafae7a` reads
`python3 .ufo/waves/round-86/count.py c1 --repo . --rev <measured> --work <scratch>` — the literal
placeholders `<measured>` / `<scratch>`, so the record's own counting command is not runnable as written
at the terminal commit. It was only pinned later, at `84e6f457`
(`--rev 239a8f39e33e252a44bb16c7202de6cd674f4614 --work /fast/scratch/hyaku/kama-r86/l1/<leg>`), together
with the new `.ufo/waves/round-86/measured/terminal/*` receipts.

### F6 — MEDIUM — the round-86 measured receipts carry no revision header and cannot be tip-bound

Round-85's receipts open with `# rev=…` / `# cmd=…`; round-86's `measured/before/*.out` and
`measured/after/*.out` open directly with the instrument's own output line (no header). Consequence,
against the round-86 record:

```
python3 tools/round72-receipt-tip-binding.py --repo . --round 86 --tip bafae7af…   ->  exit 2
  RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-86/count.py (SCORECARD.md:5262)
python3 tools/round74-receipt-claim-binding.py --repo . --round 86 --tip bafae7af…  ->  exit 2
  RECEIPT_CLAIM_V2 CouldNotEvaluate: base tool could not evaluate: …
```

Round 85 fails the same tool the same way (exit 2, on `round-85/w1/out/CR01Cheats/CR01Cheats.md`), so the
*class* is pre-existing — but round 86's measured receipts are consequently tip-unbindable, and the Round-86
section is the one that newly cites a `.py` path inside a table the tool scans.

### F7 — MEDIUM — the frozen plan's wave shape was exceeded without amending the frozen plan

`plans/round-86-claims.md` §Shape: "ONE v1 wave `w1`, 12 seats under `ufo-wave-policy.json` (band 8–16)",
dispatched through `.ufo/waves/round-86/w1.ready`. The lane actually ran **two** 12-seat waves
(`w1-spec.json`: EX01/EX02/EX03 executors, MT01/MT02 mutation-testers, RV01/RV02 reviewers, CR01 critic,
SC01 scout, SB01 scribe, CN01 connector, SN01 sentinel — exactly the plan's role map; and `w2-spec.json`
with a different mix: RV01/RV02 reviewers, CR01 critic, MT01/MT02 mutation-testers, EX01/EX02/EX03
executors, SC01 scout, SB01 scribe, SN01 sentinel, CN01 connector, `maxLanes: 16`) and has now dispatched
`w3`. LOG discloses this ("w1 12 seats, w2 12 seats") and the SCORECORD cites w2 seat receipts
(`.ufo/waves/round-86/w2/out/…`), but the frozen plan — which the record declares frozen at `c07e1f90` —
was not amended, so its "ONE v1 wave" clause is now contradicted by the committed round.

### F8 — LOW — the plan's frontier sentence pairs the CommonMark section numbers the wrong way round

Plan §Frontier: "(§4.2 ATX headings, row S576, opened this round; **§4.4/§4.5 fenced and indented code**,
new row)" — read as an ordered list this assigns §4.4=fenced and §4.5=indented. The committed spec copy
gives `indented-code-blocks` = **4.4** and `fenced-code-blocks` = **4.5**. The landed records are correct
(`S578` = §4.5 fenced, `S579` = §4.4 indented; the lesson's Gate table likewise) — only the frozen plan's
parenthetical ordering is off. (`tools/round86-rendered-cells.py:10` likewise cites "sections 4.4/4.5" for
the fence rule alone.)

### F9 — LOW — the three round-86 tools are named in PROVINCE.md but not in its surface table

`PROVINCE.md` names all three instruments in the Round-86 note (lines 408/411/415), which satisfies the
coverage row's "Round86 names the three round-86 instruments on the surface" at file level. Strictly, the
"Owns (surfaces)" table's `lane instruments (the capability repertoire, SCORECARD.md canonical list)` cell
names **no** `tools/round8*` at all — the round-80…83 instruments are likewise absent from that cell, so
the gap is a lane-wide convention, not a round-86 omission.

### F10 — LOW — stale prose in the axes block

`SCORECARD.md:182` still reads "Latest repertoire entries are round83 late-path-binding, pending-falls and
pin-recheck; round84 claims no additional repertoire entry", while the same line lists round **86** among
the first-working rounds and round 86 adds three entries. The sentence is unchanged at lane HEAD
`84e6f457`.

## What I did NOT run / open unknowns

- `scripts/sources-census.sh` was run from the fleet root (the absolute path the plan cites); it is outside
  the lane and therefore outside my write scope, but it was read/executed read-only.
- No tool was installed or upgraded (the tooling directive permits it; nothing in this seat needed it).
  Everything used was preinstalled: `git`, `python3`, `diff`, `grep`, `sha256sum`, `wc`.
- I did not re-run the frozen `pre-report-gate.py` at the tip (its 13-arm surface is round-83-bound and the
  round-86 instruments are deliberately not wired into it — a disclosed limit, routed to round 87).
- I did not fetch any upstream URL other than the five `registry/pin-recheck-rows.tsv` ranges, which the C3
  instrument itself fetches (it re-verified all five today: `verified=5`).
- The round-86 `w1`/`w2`/`w3` seat outputs are outside my item's scope; I read only the spec/dispatch
  metadata needed to compare the wave shape against the frozen plan.
