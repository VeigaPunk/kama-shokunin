# S03ScorecardAudit — SCORECARD / SHONEN mismatch audit and the exact self-assessment mismatch counter

Seat: `S03ScorecardAudit` (scribe), kama round 57, wave `kama-r57-w1`. Bounded leaf, no dispatch.
Axes audited: calibration + operability (`shokunin.conf:52` kama row = `operability + calibration`).
The `MISSION.md:29` = `operability + freshness` disagreement is recorded, not resolved.
Scope: read-only audit of the lane at pinned tips; **no lane source edits, no commits, no installs,
pacman untouched**. Scratch `/fast/scratch/hyaku/kama-r57/S03ScorecardAudit/`; every receipt was
copied to `.ufo/waves/round-57/w1/out/S03ScorecardAudit/` before any cleanup.
Distinct-case-8 evidence is a separate file: `.ufo/waves/round-57/reports/S03ScorecardAudit-case8.md`.

Tips that matter (all immutable git commits; the lane advanced through `89dc4f52`, `7c873d7b`,
`7b74e2f2`, `8640e34`, `16efcf5e`, `77e7f5ee`, `8a7f1976` during this wave, so every receipt below
carries its own `tip=`):

| label | commit | why |
|---|---|---|
| frozen base | `b89bdab2cc114735ec5d331c6c610134258f7864` | base of `controls/base-c1.out`; carry-in defect is measured here |
| round-56 measured implementation tip | `b9d5a091d25676e6c5078d330ebd6abd21a4fc7d` | last tip where the spot-check count was 42 |
| claim-ordering correction | `7c873d7b4e3839489a93d6334cdf93fe5d34d19f` | `controls/freeze-amendment.txt` |
| counter re-anchor | `7b74e2f2` | SCORECARD calibration row `42`→`43`, prereg checker call-site binding |
| round-57 section | `8640e34c` | `## Round 57` + measured receipts; `maxN` 56→57 |
| final at capture | `8a7f1976` | lane tip when this seat's receipts were generated (`MANIFEST.txt`) |

---

## Verdict

1. **The frozen self-description counter reproduces its frozen base receipt exactly, and the one
   real stale count is the calibration row's spot-check literal, not a capability row count.**
   At `b89bdab2` the counter prints `r41=1 ... mismatches=1 maxN=56 met=False` (exit 1) with
   `detail: r41 calibration run ... no stdout line == '42' (exit 0)`. The committed glob
   `corpus/lessons/*verifier-spotcheck.md` is **43** blobs at that tip and at every later tip.
   It was **42** at `b9d5a091`: the round-56 closure itself (`b89bdab2`, the round-56 verifier
   spot-check commit) added the 43rd blob and broke the row. Measured per tip below.

2. **The seat-context claim "counter reports `maxN=56` instead of `expected 46`" is false in
   direction.** `maxN` is the counter's declared derivation `max` over SCORECARD lines matching
   `^## Round (\d+)`; at the frozen base that is 56 and the head also says
   `Latest measured round: 56`, so the banner leg is 0. `46` is the *round-46* measured-receipt
   value (`SCORECARD.md:2676`, `… maxN=46 met=True`), i.e. a ten-round-old historical receipt, and
   its other appearance in this wave is the literal hard-coded by the do-nothing control
   `controls/c1-noop.py` (`print("mismatches=0 maxN=46 met=True")`, zero reads). A counter that
   expected 46 fails its own banner and planned legs (measured: `banner=1 planned=1 mismatches=2`).
   No tree surface states an expected 46. Repairing *toward* 46 would be a regression.

3. **The capability legs of the frozen counter are document-vs-document and carry no
   non-vacuity floor.** Three independent, measured attacks against the same tree differ only in
   `SCORECARD.md`, and the counter's vector is identical in all three (`mismatches=10`,
   `caps=0 retired=0 saturation=0 province=0`): an **emptied** capability repertoire (both the
   head mirror and the canonical table, with §Retired/§Saturation made self-consistent), a
   **renamed** capability across all eight capability-shaped tables, and a **fabricated
   `## Round 99`** heading with no measurement behind it. Only `maxN` changed (57→99) and even
   that produced no mismatch.

4. **The lane already owns a stronger capability binding than the round-42 counter, and it still
   does not bind names to artifacts.** `tools/capability-repertoire-audit.py` catches the emptied
   canonical table (`listed 0 observed 11 missing 11`) because it unions *all* capability-shaped
   tables and resolves each row's evidence path; it reports `met True` on the lane. It does **not**
   catch the consistent rename (`listed 11 observed 11 missing 0`) because `listed` and `observed`
   are both document-derived, and renaming a capability nowhere requires a matching tool.

5. **A real, undetected mirror drift exists in SCORECARD right now.** The head `## Capabilities`
   section declares itself "Mirror of the round-49 canonical capability list", but its
   `live-receipt-replay` row's evidence cell omits the token
   `.ufo/waves/round-49/measured/c1-build.out` that the canonical round-49 row carries. That file
   exists at the tip (`git cat-file -e` exit 0), so the mirror is short, not the canonical row.
   The `caps` leg compares **names only** (`sorted(hn) != sorted(names)`), so this is invisible.

6. **Prose staleness the counter never reads:** the highest canonical heading is **round 49**
   while the measured round is **57** (canonical 8 rounds behind); §Saturation still says
   "`tools/round42-selfdesc-reconcile.py` (kept current in round 49)"; §Capabilities' only stated
   registry-count derivation is `scripts/sources-census.sh census --file corpus/SOURCES.md`, and
   that path **does not exist in the lane tree** at the tip (`git cat-file -e` exit 128) — the
   script lives in the fleet root. Because the section restates no registry counts
   (`re.findall(r"\b(\d+) (opened|mined|queued|rejected)\b")` = `[]`), the counter's `census()`
   computation and its comparison loop never execute: the leg is dead code on this tree.

7. **SHONEN is audited by no counter at all.** Its four promotion bullets' evidence pointers all
   resolve (SKILL.md decision-table/error-signature/checklist/cited-sources sections;
   `LOG.md` rounds 1–3; `.ufo/waves/round-16/live/receipt.json` with schema
   `kama-llamacpp-live/v1` and 10 checks; round-17 receipts with 11 checks each;
   `corpus/knowledge/snapshot-history.md` §Run it; `PROVINCE.md` write boundary paragraph;
   `corpus/knowledge/cross-lane-scope.md`). But the counts and the claim/tree relation are unbound,
   and one anchor is imprecise: `PROVINCE.md` §"Write boundary" is a bold paragraph
   (`**Write boundary (hard):**` line 47), not a section. Only
   `tools/round53-cited-path-check.py` / `round54-cited-path-check.py` read SHONEN, and only to
   resolve the paths it cites.

8. **Exact measurable self-assessment mismatch counter — specification below (§Counter).** It
   re-derives every expected value at `--tip`, binds `maxN` to measured receipts rather than to
   headings, binds capability names to committed artifacts, adds SHONEN and the ledger legs, and
   carries the four fixtures proven here as its own selftest oracle (a do-nothing implementation
   must fail three of them).

---

## Exact evidence

All commands below ran from the lane with `TMPDIR` inside this seat's scratch. Every output quoted
is a receipt in `.ufo/waves/round-57/w1/out/S03ScorecardAudit/`.

### E1 — frozen base reproduces; the one stale count is 42 vs 43

```
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip b89bdab2cc114735ec5d331c6c610134258f7864
tip=b89bdab2cc114735ec5d331c6c610134258f7864
r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False
detail: r41 calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` no stdout line == '42' (exit 0)
exit=1                                                            [counter-base.out]
```

Identical to `controls/base-c1.out` (`mismatches=1 maxN=56 met=False`), so the frozen receipt is
reproducible and the base defect is real. Independent blob census:

| tip | `git ls-tree --name-only <tip> corpus/lessons/ \| grep -c verifier-spotcheck` |
|---|---|
| `b9d5a091` (round-56 measured implementation tip) | **42** |
| `b89bdab2` (round-56 verifier spot-check commit = frozen base) | **43** |
| `7c873d7b`, `7b74e2f2`, `8640e34`, `16efcf5e`, `77e7f5ee`, `8a7f1976` | **43** |

So the row was true when written and stayed true through the round-56 final lane tip `6e706d15`
(count 42 at every commit from `b9d5a091` through `6e706d15`); it was falsified only by the first
commit after that, the **non-author** round-56 verifier spot-check `b89bdab2`, which adds
`corpus/lessons/round-56-verifier-spotcheck.md` (that commit: 1 file, 46 insertions). The repair is the
calibration-row literal (E01CounterRepair measured the same one-token change; the lane integrated
an equivalent at `7b74e2f2`, and this seat does not claim that commit).

At the tips after the repair:

```
$ python3 tools/round42-selfdesc-reconcile.py --repo . --tip HEAD
tip=8640e34cad02adcd247ba0862da63f6fb2aab0df
r41=0 ... mismatches=0 maxN=57 met=True   exit=0            [counter-lane-HEAD.out]
tip=77e7f5eef2b0c759b7509056c7c511255477496d
r41=0 ... mismatches=0 maxN=57 met=True   exit=0            [counter-lane-HEAD2.out]
```

### E2 — `maxN=46` is not an expectation; it is rejected by the counter's own legs

Scratch copy of both counters (`round42-…` imports `round41-…` from its own directory), one edit
in scratch only — `maxn = max(rounds)` → `maxn = 46`:

```
$ python3 /fast/scratch/.../mut46/round42-selfdesc-reconcile.py --repo <lane> --tip HEAD
tip=16efcf5eedf4887df188790eec48afbb023e7991
r41=0 banner=1 planned=1 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=2 maxN=46 met=False
detail: banner: head lacks 'Latest measured round: 46'
detail: planned: section does not name '### Planned (round 47)'
exit=1                                                            [counter-maxn46-mutant.out]
```

The exact mutant bytes are kept as `mutant-maxn46-round42.py`
(sha256 `a464efe5c93e49df526f78a31630841adc59b4308215935a3f808e7786d9f0a7`); line 168 reads
`maxn = 46` and nothing else differs from `tools/round42-selfdesc-reconcile.py`
(sha256 `9736923e…00f9ef0`).

Independent derivation census at the same tree: `max(^## Round N headings)=57`,
`max(**Current authority (round N)**)=57`, `highest canonical-list heading=49`,
`canonical first-working max=47`. 46 appears only in `SCORECARD.md:2676` (round-46 measured
receipt) and in the do-nothing control literal.

### E3 — differential fixtures: three attacks, zero added mismatches

Design: four scratch git repos built from one `git archive HEAD` subset
(`SCORECARD.md README.md PROVINCE.md SKILL.md corpus tools registry tests`; no `.ufo`, which is
why the constant `r41=1 receipts=9` appears in all four). Only `SCORECARD.md` differs, so any
counter delta is attributable to the variant. Every fixture asserted
`git rev-parse --show-toplevel` = the fixture before any commit.

| fixture | SCORECARD change | variant sha256 | counter summary | exit |
|---|---|---|---|---|
| `faithful` (control) | none | `883b91b5…a8163d` | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=9 readme=0 province=0 rel=0 mismatches=10 maxN=57 met=False` | 1 |
| `f1-empty` | 11 canonical rows **and** 11 head-mirror rows deleted; `6 axes and 11 capabilities`→`0 capabilities`; `first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47`→`(none)` | `dcabef00…52adbf` | `… mismatches=10 maxN=57 met=False` (identical) | 1 |
| `f2-rename` | `\| pin-watch \|`→`\| pin-watch-renamed \|` in all 8 capability-shaped tables | `2f74bec1…62a699c` | `… mismatches=10 maxN=57 met=False` (identical) | 1 |
| `f3-maxn` | fabricated `## Round 99` heading; `Latest measured round: 57`→`99`; `### Planned (round 58)`→`(round 100)` | `0f1dc27c…27f4ec` | `… mismatches=10 maxN=99 met=False` (identical count; only `maxN` moved) | 1 |

`caps`, `retired`, `saturation`, `province` are **0 in all four runs**: emptying, renaming and
round-inflation each add **zero** mismatches. Receipts: `counter-{faithful,f1-empty,f2-rename,f3-maxn}.out`,
diffs `variant-*.diff`, commits `fixtures.txt`, generator `make-variant.py`.

Same four fixtures through the existing capability census:

```
faithful : listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1
f1-empty : listed 0  observed 11 missing 11 unsubstantiated 0  met False  exit 1
f2-rename: listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1
f3-maxn  : listed 11 observed 11 missing 0  unsubstantiated 1  met False  exit 1
lane     : listed 11 observed 11 missing 0  unsubstantiated 0  met True   exit 0
                                                    [census-*.out, census-lane-HEAD.out]
```

`unsubstantiated 1` is the fixture artifact (the subset omits
`.ufo/waves/round-16/live/receipt.json`); it is constant across the four and absent on the lane.
Conclusion: the census **does** kill deletion (`missing 11`) and does resolve evidence paths, but
**does not** kill a consistent rename.

### E4 — undetected mirror drift (live at the tip)

```
canonical round-49 row `live-receipt-replay`, evidence cell (149 chars):
  `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`;
  `.ufo/waves/round-49/measured/c1-build.out`; `.ufo/waves/round-48/c2/live/receipt-1.json`
head `## Capabilities` mirror row, evidence cell (104 chars):
  `tools/kama-live-replay.py`; `tools/kama-llamacpp-live.py`;
  `.ufo/waves/round-48/c2/live/receipt-1.json`
first difference at character 79
$ git cat-file -e HEAD:.ufo/waves/round-49/measured/c1-build.out   → exit 0 (the token resolves)
```

The other ten rows are byte-identical between the two tables. `caps` compares
`sorted(head_names) != sorted(canon_names)`, so a shortened evidence cell is graded 0.

### E5 — prose/derivation staleness the counter never reads

| item | observed at tip | command / receipt |
|---|---|---|
| canonical heading round vs measured round | `49` vs `57` | `grep "canonical list as of round"`, `grep "^## Round "` |
| §Saturation provenance label | "`tools/round42-selfdesc-reconcile.py` (kept current in round 49)" while measured round is 57 | `SCORECARD.md:137` |
| §Capabilities registry derivation | `scripts/sources-census.sh` — `git cat-file -e HEAD:scripts/sources-census.sh` → `fatal: … does not exist`, exit **128** | lane tree has no `scripts/` |
| §Capabilities restated registry counts | `[]` — the `\b(\d+) (opened\|mined\|queued\|rejected)\b` loop never fires, so `census()` is computed and unused | `census()` in `tools/round42-selfdesc-reconcile.py` |
| claim-shaped numbers no declared fact consumes | `204 rows`, `126 rows`, `63 claims` (bound only by `tools/round44-…` / `round45-…`, never by this counter) and `11 checks` (SHONEN round-17 claim, bound by nothing) | `unbound-int.py`, refined pass |

Whole-integer inventory at the tip: **56** integers in the head + current `## Axes` rows lie
outside any HASH/LINES/RUN fact; the claim-shaped subset (number + *rows/claims/checks/closures/
cases/rounds/entries/lines/capabilities/axes/pairs*) is **9**, of which **4** are genuinely
unbound by this counter (`204 rows`, `126 rows`, `63 claims`, `11 checks`) and 5 are accounted for:
`6 axes` and `11 capabilities` (derived by the `retired` leg), `20 lines` (a declared deletion
threshold inside the `append-only-audit` row), and `3 rows`/`38 rows` in the explicitly superseded
round-3 table. I report both numbers with their definitions rather than a single headline.

The two ledger figures do verify today, by hand and by their own counters:

```
registry/verdict-ledger.tsv       205 lines = 204 data rows; max round 43  → "204 rows …, rounds 10–43" holds
registry/claim-outcome-ledger.tsv 127 lines = 126 data rows; 63 distinct (round,claim) in rounds 10–44 → "126 rows, the 63 claims" holds
```

They are stale-able: nothing in the round-42 counter fails when they drift.

### E6 — SHONEN claim audit (no counter binds it)

| SHONEN bullet | pointer | resolves at tip | bound by a counter |
|---|---|---|---|
| SKILL.md decision tables / error patterns / checklists / cited sources | `SKILL.md` §§Decision table, (Historical) error signatures, Checklist, Cited sources | yes (4 headings) | no (path only, via `round53/54-cited-path-check.py`) |
| one end-to-end task in LOG.md + round-16 receipt "10/10 checks" | `LOG.md` rounds 1–3; `.ufo/waves/round-16/live/receipt.json` | yes; schema `kama-llamacpp-live/v1`, `len(checks)=10` | no; the 10/10 *pass* result is a cited claim, not re-derived |
| round-17 receipts "11/11 checks each" | `.ufo/waves/round-17/live/receipt-{1,2,3}.json` | yes; schema `kama-llamacpp-live/v2`, `len(checks)=11` each | no |
| instructions executable without oral context | `SKILL.md` §Checklist; `corpus/knowledge/snapshot-history.md` §Run it | yes (`## Run it` at line 7) | no |
| no cross-domain bleed | `PROVINCE.md` §Write boundary; `corpus/knowledge/cross-lane-scope.md` | the anchor exists but as `**Write boundary (hard):**` (line 47), **not** a heading; the file resolves | no |

No SHONEN claim contradicts the tree today; the gap is that nothing re-derives its counts or its
claim/tree relation, and one anchor is described as a section when it is a bold paragraph.

---

## Counter — exact specification of a self-assessment mismatch counter

Not implemented by this seat (no edits). This is a contract precise enough to implement and to
mutation-test, built from the four measured failures above.

```
python3 tools/self-assessment-mismatch.py --repo <clone> --tip <rev> [--out FILE] [--selftest]
```

**Surfaces read at `--tip`, all required (a missing or empty surface is exit 2, never 0):**
`SCORECARD.md`, `SHONEN.md`, `README.md`, `PROVINCE.md`, `SKILL.md`, `corpus/SOURCES.md`,
`registry/verdict-ledger.tsv`, `registry/claim-outcome-ledger.tsv`, and every `.ufo/waves/round-*/`
path cited by the two latest round sections.

**Derived quantities — never taken from prose:**

| symbol | derivation |
|---|---|
| `A` | data rows of the first table after `## Axes`; axis = first word of cell 1 (lower, `**` stripped), score = last integer of cell 2 |
| `M` | **measured** round: max `r` such that the tip contains at least one file under `.ufo/waves/round-<r>/measured/` **and** the round section carries a `Measured`/`met=` receipt line. A `## Round r` heading alone contributes nothing |
| `H` | max `r` over `^## Round (\d+)` headings (the current, unbound `maxN`) |
| `C` | data rows of the highest `canonical list as of round N` table → `(name, evidence cell, first round)`; `N_c` = that heading's round |
| `S` | union of capability names over **all** capability-shaped tables (delegate to `capability-repertoire-audit.py` semantics) |
| `V` | the `## Axes` integer vector; `F` = first-working rounds from `C` |
| `L_v`, `L_c` | row count, round span and `agree/over/under/other/absent` recomputed from the two ledgers |
| `K` | SHONEN per-bullet pointer list and stated counts (`10`, `3`, `11`), and receipt-derived `len(checks)` |

**Legs (each failing item adds 1 to its counter):**

1. `axes` — import `round41-scorecard-reconcile.py` unchanged (score/hash/lines/run/path/hollow,
   6 expected axes). Its hard 6-axis floor is the model for legs 4–6.
2. `measure` — require `M == H`; a heading ahead of its receipts is a mismatch (kills `f3-maxn`).
   Require the head to state `Latest measured round: M`.
3. `planned` — §Planned names `### Planned (round M+1)` and that line exists, followed by a
   numbered item.
4. `caps` — `C` equals the head mirror **cell for cell** (name, what, evidence, first round, in
   order), not by name set (kills the live mirror drift). Plus `S − C = ∅`, `|C| ≥ 1`, and every
   capability name must occur as a whole word in at least one committed artifact reachable from its
   own evidence tokens (tool stem, `PROVINCE.md`, `corpus/knowledge/*.md`) — kills `f2-rename`;
   `|C| ≥ 1` plus the census `missing`/`unsubstantiated` legs kill `f1-empty`.
5. `currency` — `N_c == M` whenever any capability row changed in `(N_c, M]`; otherwise the
   §Capabilities/§Saturation prose must not assert "kept current in round `N_c`". (Today: 49 vs 57.)
6. `retired` — states `<len(A)> axes` and `<len(C)> capabilities`, with `len(A)==6`, `len(C)>=1`.
7. `saturation` — vector string from `V` in head order; `first-working rounds <F>` with `F` non-empty;
   `nudge inactive iff min(V[operability], V[calibration]) < 8`.
8. `ledgers` — `L_v`/`L_c` equal the figures the calibration row quotes (`204 rows`, `10–43`,
   `69/87`, `2,16,0,15`; `126 rows`, `63 claims`, `58/61`, `1,2,1,1`).
9. `shonen` — every backticked path resolves at tip; the stated counts equal `len(checks)` of each
   receipt; a `[x]` bullet needs a named non-author verifier that resolves, a `[~]` bullet needs an
   explicit "Author assertion" clause; section anchors must match a heading **or** be labelled as
   prose.
10. `unbound` — every claim-shaped integer (`<n> rows|claims|checks|closures|cases|rounds|entries|
    lines|capabilities|axes|pairs`) outside a declared fact is a mismatch, unless it is consumed by
    legs 6/8/9 or lies in a section marked superseded. Today this reports 4.
11. `receipts` — every backticked `.ufo/...` token in the sections of rounds `M-1` and `M` resolves.

**Non-vacuity / do-nothing kill:**

- floor: `len(A)==6`, `len(C)>=1`, `F` non-empty, both ledgers non-empty, and a printed
  `reads=` census (SCORECARD, SHONEN, PROVINCE, README, SOURCES, ledger rows, receipt files) in
  which every count is `> 0`; a `met=True` with any `reads=0` is itself a mismatch.
- fail-closed: missing/empty surface, missing canonical heading, missing mirror table → exit 2.
- `--selftest` oracle, exactly the four fixtures measured here, each re-run at a pinned fixture
  commit with expected verdicts: `faithful` → reproduces the lane's own verdict for the same tree
  (control), `f1-empty` → **1**, `f2-rename` → **1**, `f3-maxn` → **1**. A stub that prints
  `mismatches=0 met=True` fails three of four, which is precisely the round-56/57 no-op defect.

**Exit:** `0` iff every leg is 0 and the selftest oracle passes; `1` otherwise; `2` on a missing
surface. The summary line keeps the existing field order and adds `measure=`, `currency=`,
`shonen=`, `unbound=`, `reads=` so prior receipts stay comparable.

**Migration cost, measured:** legs 4, 5 and 10 are red at today's tip (mirror cell, canonical
round 49 vs measured 57, four unbound numbers). That is the honest state; a counter that reports
green today is reporting the vacuity documented in E3.

---

## Sibling overlap (for the connector seats)

- `E01CounterRepair` measured the same base/tips and the same `maxN` falsification and the
  `42→43` one-token repair. This seat agrees and does not re-claim it; E2/E1 here are independent
  reproductions.
- `R57Item04CanonicalBinding` built a content-bound canonical-row prototype with a
  `canonical_reads` non-vacuity rule and an omission control. My E3 `f1-empty`/`f2-rename` measure
  the *existing frozen counter's* blindness, which that prototype does not cover; `f2-rename` is a
  gap its `distinct`/`mirror` legs also do not close (both are document comparisons).
- `R57Item16CanonicalMutation` mutates canonical rows; my `f1-empty` deletes the whole repertoire in
  both surfaces *and* adjusts §Retired/§Saturation so the document stays internally consistent —
  that self-consistent variant is the one the frozen counter cannot see.
- No seat audits SHONEN (E6) or the ledger/label staleness (E5).

## Round-level items outside this seat (advisory only)

- **S515 re-open** (Git config runtime environment pairs): owned by `S01SourcesReopen`,
  `R05SourcesGate`, `R57Item06/R57Item13`. This seat did not re-open the URL and claims no quote;
  as a lane author I have no non-author admit/reject authority, per the wave's own rule.
- **Admit/reject spot-check**: the round-56 lesson's S512–S515 decisions were taken by a non-author
  (`.ufo/waves/round-57/…`, `corpus/lessons/round-56-verifier-spotcheck.md`); any re-check this round
  is advisory from a lane seat and cannot be filed as non-author judgment.
- **Round-56 outside routed defects** belong to `S02LessonDraft` / `Q01CritiqueRound56` /
  `R57Item07` / `R57Item18`. This seat's contribution to that list is E4–E6: the mirror cell drift,
  the canonical-round currency gap, and the entirely unbound SHONEN surface — each of which the
  round-56 spot-check named ("test SCORECARD/SHONEN disagreement") without a counter to do it.

## Limits

- Fixture counters show `r41=1 receipts=9` because the fixtures are a `git archive` subset without
  `.ufo`; this is constant across the control and the three variants, and the lane runs are the
  reference for absolute values.
- The lane moved during the audit (`b89bdab2` → `8a7f1976`). Every receipt states its own `tip=`;
  no receipt is valid without it.
- I did not run `tools/round44-verdict-ledger-audit.py` / `round45-claim-outcome-audit-v2.py`
  (both require `--fleet`); the ledger figures were checked by direct row counting only.
- I did not execute the counter specification; its legs are derived from measured failures, and
  the three attacks are the evidence that the legs would fire. No score, capability or verdict is
  claimed.

Report: .ufo/waves/round-57/w1/out/S03ScorecardAudit.md
Case-8 evidence: .ufo/waves/round-57/reports/S03ScorecardAudit-case8.md
