# rev=1a85a991fce5b76b60f88a5cab3df98d253b1a4a
# SC01 — reconnaissance: is the C2 fact population the right one?

Read-only seat. The only file written is this report. Plan read in full
(`plans/round-76-claims.md`, frozen at `1a85a991…`). Sections read in full:
`SCORECARD.md` §Round 75 (4053–4131 at reading time, both fenced superseded blocks
included), `LOG.md` §Round 75 (2999–3022), plus `corpus/lessons/round-75.md` and
`corpus/lessons/round-75-verifier-spotcheck.md` §6.

**Revision note.** The lane tip moved under this seat four times (five revisions:
`1a85a991` → `c2aa7fb2` → `a3fbc629` → `461d2adb` → `661622b5` → `dc222228`). The *filed*
values graded below are round-75 values, so they were derived at the revision the record
itself names (`c9ab73d8…` for the population sentence and the LOG work tip) and
cross-checked at the freeze. Byte comparison against `1a85a991`: `SCORECARD.md:4055,4065,152`
and `LOG.md:3002,3016,3017` are **SAME** at `661622b5` and still at the same line numbers in
the committed blob at `dc222228`; `SCORECARD.md:18` changed only by the round-76
closure-pointer re-anchor (an exempt-head re-derivation plus the correction block at
`SCORECARD.md:4147`, landed at `461d2adb`). Round-76 corrections for five of the eight facts
landed at `461d2adb` (§2.4); they are not the filed state this recon grades. All line
locators were re-verified against the committed blobs (`git show <rev>:SCORECARD.md`) —
resolve them that way if the worktree is mid-write. No tools were installed or upgraded (all
pacman transactions are paused host-wide and nothing was needed).

## 1. Fact inventory — every re-derivable round-75 assertion

Legend for the ruling column:

- `IN <id>` — one of the eight declared C2 facts (plan §C2 fact-population bullet).
- `OUT-pop` — not one of the eight; the population is declared, not discovered.
- `OUT-run` — run fact with no receipt requirement (only `log-tally` carries one).
- `OUT-narr` — narrative/prose with no committed denominator.
- `OUT-fence` — quoted history inside a CommonMark fence (C1's scope; C2 declares none).
- `OUT-hist` — historical prose about work done in round 75.
- `OUT-fwd` — forward plan item, not a completed assertion.
- `OUT-canon` — capability canon / registry row, outside the C2 id set.

### A. SCORECARD §Round 75 population sentence — `SCORECARD.md:4065`, rev `c9ab73d8`

| # | Fact | Filed | Derived | Derivation | Ruling |
|---|---|---|---|---|---|
| A1 | `SKILL.md` sha256 | `f18c9bcc7db5de4280fecd33337613b852fb650e757563621fa676745fe9a421` | same | `git show c9ab73d8:SKILL.md \| sha256sum` | **IN skill-digest** |
| A2 | `SKILL.md` lines | `1736` | `1736` | `git show c9ab73d8:SKILL.md \| wc -l` | **IN skill-lines** |
| A3 | `PROVINCE.md` sha256 | `0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4` "(unchanged)" | `af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697` | `git show c9ab73d8:PROVINCE.md \| sha256sum` (same value at freeze and at tip) | **IN province-digest — MISMATCH** |
| A4 | `PROVINCE.md` lines | `322` | `322` | `git show c9ab73d8:PROVINCE.md \| wc -l` | **IN province-lines** |
| A5 | `corpus/SOURCES.md` registry rows | `287` (census exit 0) | `287`; census `kama ok` exit 0 | `git show c9ab73d8:corpus/SOURCES.md \| grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`; `…/scripts/sources-census.sh census --file corpus/SOURCES.md` | **IN sources-rows** |
| A6 | filtered `corpus/knowledge/*.md` entries | `45` | `45` | `git ls-tree -r --name-only c9ab73d8 corpus/knowledge/ \| grep '\.md$' \| grep -v engine-sides \| grep -v processes \| wc -l` | **IN knowledge-entries** |
| A7 | gate registry | `registered 92 unregistered 0 defective 0` | same | `python3 tools/gate-registry-check.py` (registry unchanged `c9ab73d8..HEAD` at reading time) | OUT-run |
| A8 | axis vector | `8,8,7,9,7,7` | identical to §Axes rows 14–19 | read `SCORECARD.md:14-19` | OUT-pop (restatement; a counter would only re-read the table) |
| A9 | population revision | `rev=c9ab73d8…` | `c9ab73d8…` is the round-75 work tip | `git diff --name-only c9ab73d8 b06cc612` → only `SCORECARD.md`, `corpus/lessons/round-75-verifier-spotcheck.md`, `.ufo/waves/round-75/measured/after/*` | OUT-pop (locator, not a fact id) |

### B. SCORECARD §Round 75 header — `SCORECARD.md:4055`

| # | Fact | Filed | Derived | Derivation | Ruling |
|---|---|---|---|---|---|
| B1 | round-75 base revision | `dc58e51315e79d36df5fc530c95fbd3aecbf7593` | exists; `0908bab5^ == dc58e513` | `git rev-parse 0908bab5^` | OUT-pop (commit id) |
| B2 | round-75 freeze revision | `0908bab5cbf0ab6b435144fc525a3e18443dc08f` | exists; adds `plans/round-75-claims.md`, controls, before receipts | `git show --stat 0908bab5` | OUT-pop |
| B3 | work tip in SCORECARD | `c9ab73d842051db5f8320bced4357bf13cf14108` | `c9ab73d8…` is the last commit in the round range touching a non-record path under the round-72 default set | `git diff --name-only c9ab73d8 b06cc612` | OUT-pop (the graded copy is the LOG one, `log-worktip`) |
| B4 | claim → axis mapping (`C1 calibration, C2 operability, C3 freshness`) | as filed | `plans/round-75-claims.md:29,85,135` headings agree | `grep -nE '^## C[0-9]' plans/round-75-claims.md` | OUT-pop |

### C. SCORECARD §Round 75 claim table — `SCORECARD.md:4059-4061`

| # | Fact | Filed | Derived | Derivation | Ruling |
|---|---|---|---|---|---|
| C1 | C1 before | `CONTROL_C1 killed=0 escaped=2` at `dc58e513` | same (committed receipt) | `cat .ufo/waves/round-75/measured/before/c1-mutants.out` | OUT-pop (claim baseline) |
| C2 | C1 after | `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0`, exit 0 | byte-identical, exit 0 | `python3 tools/round75-interpretation-pins.py --repo . --work <scratch>` | OUT-pop |
| C3 | C2 before | `CONTROL_C2 killed=3 escaped=2` at `dc58e513` | same | `cat .ufo/waves/round-75/measured/before/c2-mutants.out` | OUT-pop |
| C4 | C2 after | `SURVIVORS2 mutants=5 killed=5 escaped=0`, exit 0 | byte-identical, exit 0 | `python3 tools/round75-survivor-probe.py --repo . --work <scratch>` | OUT-pop |
| C5 | module selftest | `RECEIPT_CLAIM_V2_SELFTEST pass=11 fail=0` | same | `python3 tools/round74-receipt-claim-binding.py --selftest` | OUT-pop |
| C6 | C3 before | `unrestored=53 bad_declarations=5` | same | `cat .ufo/waves/round-75/measured/before/c3-audit.out` | OUT-pop |
| C7 | C3 after | `APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0`, exit 0 | byte-identical, exit 0 | `python3 tools/round75-append-accepted.py --repo .` | OUT-pop |
| C8 | audit after | `unrestored=53 … bad_declarations=0` | `events=232 restored=91 unrestored=53 ungraded=83 disclosed=5 bad_declarations=0` (event totals grew; the graded values hold) | same run, summary line | OUT-pop |
| C9 | register size/class | `389 register rows over 53 events, all class in-place-edit` | 389 data rows (390 lines incl. header), 53 distinct `(commit,file)`, 389/389 `in-place-edit` | `tail -n +2 registry/append-only-accepted.tsv \| wc -l`; `… \| awk -F'\t' '{print $1"\|"$2}' \| sort -u \| wc -l`; `… \| cut -f5 \| sort \| uniq -c` | OUT-pop (C3 register fact) |
| C10 | "no register" at base | as filed | `git cat-file -e dc58e513:registry/append-only-accepted.tsv` → fatal, absent | as shown | OUT-pop |

### D. SCORECARD §Round 75 required duties — `SCORECARD.md:4063`

| # | Fact | Derived | Derivation | Ruling |
|---|---|---|---|---|
| D1 | coverage map indexes `knowledge/host-block-base-revision.md` and states seven remaining gaps | `corpus/README.md:1665` heading; row present; "7 files still unindexed" | `sed -n '1665,1680p' corpus/README.md` | OUT-pop (duty) |
| D2 | three QUALITY criteria KQ123/KQ124/KQ125 | all three present with the described subjects | `grep -nE '^\| ?KQ12[345]' corpus/QUALITY.md` | OUT-pop |
| D3 | erratum filed in the round report | no locator is named, so not mechanically derivable from this sentence | — | OUT-pop (no committed denominator) |
| D4 | cross-domain line in the round report | same as D3 | — | OUT-pop (no denominator) |
| D5 | RVW01 exit-map note in the lesson | 1 occurrence | `grep -c RVW01 corpus/lessons/round-75.md` | OUT-pop |
| D6 | item 7 "renames the newest outside closure `round-74-verifier-spotcheck.md`" | true when written; at tip newest is `round-75-verifier-spotcheck.md` | `python3 tools/round69-newest-closure-counter.py --repo . --since-round 63` exit 1 | OUT-hist (second occurrence of the closure-pointer class; §3 F-H) |

### E. SCORECARD §Saturation (live head, `SCORECARD.md:152`)

| # | Fact | Filed | Derived | Derivation | Ruling |
|---|---|---|---|---|---|
| E1 | capability first-working-round list | `…, 73, 74, 75` | canon includes 75 | `python3 tools/round74-selfdesc-canon.py --repo .` → `canon_round=75 canon_rows=28` | OUT-pop (matches) |
| E2 | highest-canon pointer | `highest canonical list, §Round 74` | `§Round 75` | same resolver | OUT-pop — **MISMATCH, unnamed by the plan** (§3 F-A) |
| E3 | last capabilities entered | `round 74's selfdesc-canon, receipt-claim-v2 and province-host-drift-v2` | round 75's `interpretation-pins`, `survivor-probe`, `append-accepted` (`SCORECARD.md:4096-4098`, first-working 75) | canon rows + resolver | OUT-pop — **MISMATCH, unnamed by the plan** (§3 F-B) |

### F. LOG §Round 75 — `LOG.md:2999-3022`

| # | Fact | Filed | Derived | Derivation | Ruling |
|---|---|---|---|---|---|
| F1 | work tip | `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a` | `c9ab73d842051db5f8320bced4357bf13cf14108` | `git diff --name-only c9ab73d8 b06cc612`; `git show --name-only c9ab73d8` (PROVINCE.md only) | **IN log-worktip — MISMATCH** (under the round-72 default record-path set; §3 F-F) |
| F2 | base / freeze | `dc58e513…` / `0908bab5…` | match | `git rev-parse 0908bab5^` | OUT-pop |
| F3 | mistake-class count | `four mistake classes` | `5` (`unarmed-rule`, `disclosed-not-graded`, `carried-red`, `generated-artifact-shape`, `record-cites-control`) | `grep -cE '^[0-9]+\. \*\*`[a-z-]+`\*\*' corpus/lessons/round-75.md` | **IN log-mistakes — MISMATCH** |
| F4 | gate-selftest tally + receipt | `PRE_REPORT_SELFTEST pass=18 fail=0` | value reproduces at `c9ab73d8`; **no committed receipt carries it** | `git grep -n 'PRE_REPORT_SELFTEST pass=18' 1a85a991 -- .ufo/waves/round-75/` → no output; `git archive c9ab73d8 \| tar -x -C $S && (cd $S && python3 tools/pre-report-gate.py --selftest)` → `PRE_REPORT_SELFTEST pass=18 fail=0`, exit 0 | **IN log-tally — UNBACKED** |
| F5 | register rows/events | `389 rows over 53 events` | same as C9 | as C9 | OUT-pop |
| F6 | wave shape | `one v1 wave, 13 seats (3 executor, 3 scribe, 1 scout, 1 connector, 1 revenger, 1 reviewer, 1 critic, 1 mutation-tester, 1 sentinel)` | `seats=13`, 13 results, `agent` mix exactly that | §4 | OUT-pop (seat count/roles) |
| F7 | RV01 attacks | `both pins load-bearing with four cheat attempts caught` | report lists four rejected attacks (hardcoded, equal declaration, no-op mutant, non-discriminating fixture) | `.ufo/waves/round-75/w1/RV01PinsReview.md:561-562` | OUT-narr |
| F8 | SN01 cutoff | `SN01's fresh-damage finding adopted as the register's temporal cutoff` | tool credits SN01 (`tools/round75-append-accepted.py:71-72`); SN01 itself called it a policy disagreement requiring authorization (`SN01Register.md:40`) | grep both | OUT-narr (textually supported, with SN01's caveat) |
| F9 | axis harm | `8,8,7,9,7,7` | same | `SCORECARD.md:14-19` | OUT-pop |
| F10 | S547 | `S547 (gitattributes(5))` | row present, title matches | `grep -E '^\|\s*S547\s*\|' corpus/SOURCES.md` | OUT-pop |
| F11 | three QUALITY criteria | as filed | present | as D2 | OUT-pop |
| F12 | round-74 coverage-map block | as filed | present | as D1 | OUT-pop |
| F13 | declarations file | `five unbound contract pointers re-pointed, register declared append-only` | file has 7 declarations: 5 contract surfaces + register + exempt head-section line | `cat registry/append-only-declarations.md` | OUT-pop |
| F14 | gate arm 8 | `round75-instruments` | arm 8 named in the committed gate receipt | `sed -n '8p' .ufo/waves/round-75/measured/after/pre-report-gate.out` | OUT-pop |
| F15 | undisclosed events | `53 post-ledger undisclosed events` | `unrestored=53` | `c3-audit.out` / C7 run | OUT-pop |
| F16 | unbound declarations | `five unbound contract declarations since round 51` | `bad_declarations=5` at base | `c3-audit.out` | OUT-narr (history) |

### G. SCORECARD §Planned (round 76) — `SCORECARD.md:4114-4118`

| # | Fact | Filed | Derived | Ruling |
|---|---|---|---|---|
| G1 | ungraded exempt-section deletions | `81 events` | `81` at `c9ab73d8` (`.ufo/waves/round-75/measured/after/c3-append-accepted.out:2`), `83` at base `b06cc612` (`.ufo/waves/round-76/measured/before/c3-audit.out:2`) | OUT-fwd — revision-scope trap, not a defect (§3 F-I) |
| G2 | items 1–2 prose | — | — | OUT-fwd (no denominator) |

### H. Fenced superseded blocks — `SCORECARD.md:4106-4112` and `4122-4131`

| # | Fenced assertion | Locator | Ruling |
|---|---|---|---|
| H1 | work tip `b8ed2568…` | 4107 | OUT-fence (quoted history; must not be graded) |
| H2 | population at `b8ed2568…`: PROVINCE `0e8dc562`, 45 entries, 287 rows | 4111 | OUT-fence |
| H3 | `PRE_REPORT_SELFTEST pass=15` (twice on one line) | 4124 | OUT-fence |
| H4 | `SKILL.md c4e03810…` (1733 lines) | 4125 | OUT-fence |
| H5 | coverage row `→ 44`, PROVINCE `0e8dc562…` | 4126 | OUT-fence |
| H6 | `6 axes and 25 capabilities remain active` | 4129 | OUT-fence |

### I. Capability canon — `SCORECARD.md:4067-4098`

| # | Fact | Derived | Ruling |
|---|---|---|---|
| I1 | canon row count and highest round | 28 data rows; `canon_round=75`; last three first-working `75` | OUT-canon |
| I2 | head mirror at `SCORECARD.md:115-148` | identical rows, round-75 included | OUT-canon |

## 2. The eight declared facts and the before count

### 2.1 Per-fact state at the freeze (the state the claim's before line describes)

| id | filed | derived at the named revision | state |
|---|---|---|---|
| `skill-digest` | `f18c9bcc…` | `f18c9bcc…` | match |
| `skill-lines` | `1736` | `1736` | match |
| `province-digest` | `0e8dc562…` | `af459acf…` | **mismatch** |
| `province-lines` | `322` | `322` | match |
| `sources-rows` | `287` | `287` | match |
| `knowledge-entries` | `45` | `45` | match |
| `log-worktip` | `b8ed2568…` | `c9ab73d8…` | **mismatch** |
| `log-mistakes` | `4` | `5` | **mismatch** |
| `log-tally` | `pass=18 fail=0` | value true, **no receipt** | **unbacked** |
| `closure-pointer` | `round-74-verifier-spotcheck.md` | `round-75-verifier-spotcheck.md` | **mismatch** |

Totals: **8 facts, 5 defective (4 value mismatches + 1 receipt-unbacked), 3 clean.**
The plan's `claims=8 mismatches=5 unbacked=1` is **CONFIRMED**: `mismatches` counts the
unbacked fact as well (the plan says so: "the tally counts both mismatch and unbacked"),
and the finding set is exactly the five ids above. No other declared id is defective.

### 2.2 No additional *declared* mismatch

I re-derived all ten checks; the three clean facts (`skill`, `sources-rows`,
`knowledge-entries`) are clean at the revision they name, including the census exit code
(`kama ok`, exit 0) and the filter used by the record's own coverage row.

### 2.3 The before count is correct only if two derivations stay pinned

- `sources-rows` and `knowledge-entries` must be derived from the **named revision**
  (`c9ab73d8`), not the worktree. At tip `661622b5` the worktree has **288** rows and
  **47** filtered entries (this round's frontier row and two knowledge entries). A
  worktree-reading counter reports 7 defective facts and breaks the before line.
- `log-worktip` must use the **round-72 default record-path set**, not C1's extended set
  (§3 F-F). Under C1's set the mismatch disappears (3 defective facts).

### 2.4 Observed end state (not part of the filed state)

The round-76 corrections landed at `461d2adb` (blocks at `SCORECARD.md:4134`, `4147`,
`LOG.md:3025`, `3035`, `3044`) and cover exactly the five defective ids. The committed
harness then prints the frozen after line:

```
# rev=a3fbc629… (before corrections)
SELFRECORD_FACTS claims=8 mismatches=5 corrected=0 unbacked=1   exit 1
# rev=461d2adb… (after corrections)
SELFRECORD_FACTS claims=8 mismatches=0 corrected=5 unbacked=0   exit 0
```

Both lines match the plan's declared before/after exactly. The harness's own extraction
(first `Axis harm check:` line in the section, first `work tip` in LOG, blob reads at the
declared revision, receipts restricted to `.ufo/waves/**` with `.out/.txt/.stdout/.log`)
implements the rulings in §3 F-C/F-D/F-E/F-F. Note that the `log-tally` correction's
"Corrected" value is a **round-76** value (`PRE_REPORT_SELFTEST pass=21 fail=0` with the
round-76 receipt), while the historical value is declared unbacked; whether that satisfies
the plan's "a corrected value which itself re-derives" for a round-75 tally is a C2
reviewer judgment I did not resolve — the harness accepts it.

## 3. Findings the plan does not name (for EX02's scope, with exact bytes)

**F-A — `SCORECARD.md:152` names the wrong canon heading.** Exact bytes:
`highest canonical list, §Round 74); the assig…`. Derived: `SELFDESC_CANON_V2
canon_round=75 canon_rows=28 demonstrated=0 total=28 invisible=0`, exit 0. The live
pointer is one round stale; it is not one of the eight ids, so no correction block names
it (verified: the only `### Correction (2026-11-04)` blocks are the five in §2.4).

**F-B — `SCORECARD.md:152` names the wrong last capabilities.** Exact bytes:
`The last capabilities entered are round 74's `selfdesc-canon`, `receipt-claim-v2` and `province-host-drift-v2``.
Derived: the canon's last three rows are `interpretation-pins`, `survivor-probe`,
`append-accepted`, all first-working round 75 (`SCORECARD.md:4096-4098`). Neither F-A nor
F-B is graded by any instrument: `tools/round42-selfdesc-reconcile.py:325-335` checks the
score vector, the first-working list and the nudge string only, and the committed gate
receipt reports `selfdesc … saturation=0 mismatches=0`. These are the only live,
re-derivable, defective round-75 assertions outside the declared eight.

**F-C — the plan's "no committed round-75 file carries the tally" is over-strong.** The
plan's motivating sentence says "no committed round-75 file carries" the tally; closure
item 4 repeats the phrase but its parenthetical ("the round's receipts hold only the four
module selftests and the gate run") shows the intended scope is receipts. Three committed
round-75 record files do carry `PRE_REPORT_SELFTEST pass=18 fail=0`:
`SKILL.md:309`, `SCORECARD.md:14` (twice on the one line) and `LOG.md:3016` (added by
commits `10f37171`, `ac1c8538`, `ba9f7248`). What is absent is a **receipt** — the
`c2-tally.out` grep is scoped to `.ufo/waves/round-75/` and returns 0. The fact id is
receipt presence, not line absence; a counter that greps the tree cannot reproduce
`unbacked=1` (it would read the tally as backed by SKILL/SCORECARD/LOG).

**F-D — C2 declares no fence scope, but the §Round 75 section carries live-looking
duplicates.** `SCORECARD.md:4106-4112` and `4122-4131` are fenced blocks that restate six
of the eight facts with different values (H1–H6 above). `0e8dc562` occurs three times in
`SCORECARD.md` (4065 live, 4111 fenced, 4126 fenced); `work tip `b8ed2568` occurs at
`LOG.md:3002` and `SCORECARD.md:4107`. C1 declares a fence rule; C2 does not. The landed
harness survives by taking the *first* match in each declared section — a positional
accident, not a declared rule. The claim record should state the occurrence rule it uses
(first live match in the declared section, fences excluded) before a later edit reorders
the section.

**F-E — revision pinning is load-bearing.** At `661622b5` the worktree is 288 rows / 47
entries against the named blob's 287 / 45. Any counter that reads the worktree instead of
the named blob adds two spurious mismatches. The predicate already says "blob at the
revision it names"; this is a warning for the selftest, where a fixture must not inherit
the live worktree.

**F-F — "record path" has two different sets in the one frozen plan.** C1 ruling (b)
(`plans/round-76-claims.md:66-68`) extends the record-path set with `PROVINCE.md`,
`SKILL.md`, `corpus/**`. C2's motivating sentence (`:94`) calls `c9ab73d8` "the last
non-record commit", but that commit changes only `PROVINCE.md` (`git show --name-only
c9ab73d8`), and the round-72 tool's docstring says `PROVINCE.md` is "never a record path"
(`tools/round72-receipt-tip-binding.py:76-78`); the round-75 closure uses the same
convention (`corpus/lessons/round-75-verifier-spotcheck.md:191-192`). So: under the
round-72 default set the plan's mismatch is right (derived `c9ab73d8`); under C1's
extended set the last non-record commit is `b8ed2568` and the LOG's filed value is right.
C2 must pin the default set; sharing C1's constant flips the before count from 5 to 4.

**F-G — unbacked is not false.** The tally reproduces at `c9ab73d8` (`PRE_REPORT_SELFTEST
pass=18 fail=0`, exit 0, from a `git archive` extraction of the committed tree). The
defect is exactly the missing retained receipt; a counter that re-executes the gate would
read green and lose the claim. The fact must grade receipt presence (the landed harness
does).

**F-H — `SCORECARD.md:4063` holds a second, historical closure pointer**
(`item 7 — this row renames the newest outside closure
`corpus/lessons/round-74-verifier-spotcheck.md``). It is a statement about round-75 work,
true when written; the live pointer is the `## Axes` calibration row (corrected at
`461d2adb`). Do not grade the 4063 copy, and do not "fix" it in place — the dated section
is append-only.

**F-I — 81 vs 83 is a revision difference, not a defect.** `SCORECARD.md:4118` says 81;
that is the `c9ab73d8` audit value. The base audit (`b06cc612`) says 83, which is the
round-76 plan's number. Both are correct at their own revisions.

**F-J — `mismatches=5` legitimately includes the unbacked fact.** Do not "fix" the counter
to print `mismatches=4`; the plan states the tally counts both, and the landed harness
prints exactly `claims=8 mismatches=5 … unbacked=1`.

**F-K — low-confidence wording residual.** `LOG.md:3017` says "four mistake classes, each
with a fix shown able to fail". The count is the corrected part; the "each with a fix
shown able to fail" clause is unqualified for M5 `record-cites-control`, whose fix is
recorded as "the remaining work is a counter-scope decision" (`corpus/lessons/round-75.md`
M5). Prose judgment, out of population.

## 4. Wave evidence and cited paths

**Seats.** `.ufo/waves/round-75/w1/w1-results.json`: `lane=kama`, `round=75`, `wave=w1`,
`seats=13`, `results` length 13. All 13 entries have non-empty `output` (853–6265 bytes);
no `status` field exists. Roles are the `agent` field:

```
3 executor (EX01Pins, EX02Survivors, EX03Accepted)
3 scribe   (SCR01Sources, SCR02QualityMap, SCR03Know)
1 scout (SC01Recon), 1 connector (CON01Overlap), 1 reviewer (RV01PinsReview),
1 critic (CR01Falsify), 1 mutation-tester (MT01Mutants75), 1 sentinel (SN01Register),
1 revenger (REV01Semantics)
```

`w1-spec.json` agrees: milestone "13 seats: 3 executor, 3 scribe, 1 scout, 1 connector,
1 revenger, 1 reviewer, 1 critic, 1 mutation-tester, 1 sentinel", `maxLanes=13`. The LOG's
wave sentence re-derives exactly; "completed" is implied by the 13 outputs, not by a
status key (F-L).

**Cited paths.** Every backticked path in `SCORECARD.md` 4053–4124 and `LOG.md` 2999–3022
(two section-relative `measured/…` receipts resolved under `.ufo/waves/round-75/`) was
tested with `git cat-file -e <rev>:<path>`: **45 checked, 0 absent** at `1a85a991`. This
includes the ten `measured/{before,after}/*.out` receipts, the three round-75 tools, the
register, the declarations file, the lesson, the closure, and the seat reports cited by
name (`RV01PinsReview.md`, `SN01Register.md`, `EX01Pins/report.md`,
`EX03Accepted/report.md`). No cited receipt is missing at the tip.

## 5. Commands and exits

`$` lines are the commands; `->` is the observed result. Where a pipeline was used the
exit is marked "not captured" rather than asserted.

```
$ git rev-parse HEAD -> 1a85a991fce5b76b60f88a5cab3df98d253b1a4a (exit 0; later 461d2adb, 661622b5)
$ git show c9ab73d8:SKILL.md | sha256sum -> f18c9bcc… (exit 0)
$ git show c9ab73d8:SKILL.md | wc -l -> 1736 (exit 0)
$ git show c9ab73d8:PROVINCE.md | sha256sum -> af459acf… (exit 0)
$ git show b8ed2568:PROVINCE.md | sha256sum -> 0e8dc562… (exit 0)
$ git show dc58e513:PROVINCE.md | sha256sum -> 0e8dc562… (exit 0)
$ git show c9ab73d8:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' -> 287 (exit 0)
$ git ls-tree -r --name-only c9ab73d8 corpus/knowledge/ | grep '\.md$' | grep -v engine-sides | grep -v processes | wc -l -> 45 (exit 0)
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file corpus/SOURCES.md -> kama ok, 287 rows (exit 0)
$ python3 -c "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') if 'engine-sides' not in f and 'processes' not in f]))" -> 45 at freeze, 47 at tip (exit 0)
$ python3 tools/gate-registry-check.py -> registered 92 unregistered 0 defective 0 (exit 0)
$ git show --name-only c9ab73d8 -> PROVINCE.md (exit 0)
$ git diff --name-only c9ab73d8 b06cc612 -> SCORECARD.md, corpus/lessons/round-75-verifier-spotcheck.md, 7 × .ufo/waves/round-75/measured/after/* (exit 0)
$ git rev-parse 0908bab5^ -> dc58e513… (exit 0)
$ grep -cE '^[0-9]+\. \*\*`[a-z-]+`\*\*' corpus/lessons/round-75.md -> 5 (exit 0)
$ grep -c 'PRE_REPORT_SELFTEST pass=18' SKILL.md -> 1 (exit 0)
$ git grep -n 'PRE_REPORT_SELFTEST' 1a85a991 -- .ufo/waves/round-75/ -> no output (no match)
$ git archive c9ab73d8 | tar -x -C $S && (cd $S && python3 tools/pre-report-gate.py --selftest) -> PRE_REPORT_SELFTEST pass=18 fail=0 (exit 0)
$ python3 tools/pre-report-gate.py --selftest -> pass=20 fail=1 at 1a85a991 (exit not captured, piped); pass=21 fail=0, exit 0 at 461d2adb
$ python3 tools/round75-interpretation-pins.py --repo . --work $S/pins -> INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0 (exit 0)
$ python3 tools/round75-survivor-probe.py --repo . --work $S/surv -> SURVIVORS2 mutants=5 killed=5 escaped=0 (exit 0)
$ python3 tools/round75-append-accepted.py --repo . -> APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0 (exit 0); summary events=232 restored=91 unrestored=53 ungraded=83 disclosed=5 bad_declarations=0
$ python3 tools/round74-receipt-claim-binding.py --selftest -> RECEIPT_CLAIM_V2_SELFTEST pass=11 fail=0 (exit 0)
$ python3 tools/round69-newest-closure-counter.py --repo . --since-round 63 -> NEWEST_CLOSURE … row_current=false, STALE_CALIBRATION … (exit 1)
$ python3 tools/round74-selfdesc-canon.py --repo . -> SELFDESC_CANON_V2 canon_round=75 canon_rows=28 … (exit 0)
$ python3 tools/round74-selfdesc-canon.py --repo . --rev HEAD -> error: unrecognized arguments (exit 2)
$ python3 tools/round76-selfrecord-facts.py --repo . -> at a3fbc629: claims=8 mismatches=5 corrected=0 unbacked=1 (exit 1); at 461d2adb: claims=8 mismatches=0 corrected=5 unbacked=0 (exit 0)
$ tail -n +2 registry/append-only-accepted.tsv | wc -l -> 389 (exit 0)
$ tail -n +2 registry/append-only-accepted.tsv | awk -F'\t' '{print $1"|"$2}' | sort -u | wc -l -> 53 (exit 0)
$ tail -n +2 registry/append-only-accepted.tsv | cut -f5 | sort | uniq -c -> 389 in-place-edit (exit 0)
$ git cat-file -e dc58e513:registry/append-only-accepted.tsv -> fatal: path … does not exist (nonzero)
$ python3 tools/pin-watch.py selftest -> selftest pass=9 fail=0 (piped)
$ python3 tools/capability-repertoire-audit.py --selftest -> CAP_SELFTEST pass=2 fail=0 (piped)
$ python3 tools/round68-receipt-pointer-audit.py --selftest -> 9/9 selftest arms passed (piped)
$ python3 tools/round69-newest-closure-counter.py --selftest -> 10/10 selftest arms passed (piped)
$ python3 tools/round72-round-scope.py --selftest -> ROUND_SCOPE_SELFTEST pass=16 fail=0 (piped)
$ python3 tools/round74-selfdesc-canon.py --selftest -> SELFDESC_CANON_V2_SELFTEST pass=11 fail=0 (piped)
$ python3 tools/round74-province-host-drift.py --selftest -> PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0 (piped)
$ python3 tools/citation-provenance.py --selftest -> selftest: ok (24 cases) (piped)
$ sha256sum tools/kama-probe.sh tools/test-snapshot.sh -> 4393ab81…/236c23c1… (exit 0); wc -l -> 1138 / 194
$ path-existence check over 45 cited tokens (git cat-file -e) -> 0 missing (exit 0)
```

Scratch (`/fast/scratch/hyaku/kama-r76/SC01Recon`, including the `git archive` tree and the
gate-selftest output) is deleted before this seat yields; no receipt file is needed because
this item names no receipt path.

## 6. Answer, confidence, and remaining unknowns

**Answer.** For the claim as frozen, the population is the right one: the eight ids cover
every defect the round-75 closure routed, and the derived state is exactly 4 value
mismatches + 1 receipt-unbacked = 5 defective facts, which both the plan's before line and
the landed harness confirm. It is **not** the population of *every* re-derivable round-75
assertion: two live §Saturation sentences (`SCORECARD.md:152`) are stale and no instrument
or correction grades them (F-A/F-B). If the claim is ever read as "every declared round-75
self-record fact re-derives", the population is too narrow by those two; as frozen, they
are out of scope and should be reported, not folded in.

**Confidence.** High for all file-derived values (digests, line/row/entry counts, commit
ids, register counts, seat/role mix, path existence). High for the three counter
reproductions. Medium for F-A/F-B's *classification*: whether the head §Saturation section
counts as "the round-75 self-record" is an interpretive call, but the section was rewritten
by round-75 commit `e87f1f3c` and states the round-75 canon, and the stale sentences are
re-derivable by the same resolver that already reports `canon_round=75`.

**Remaining unknowns.**

1. The `log-tally` correction's "Corrected" value is a round-76 run; whether the frozen
   "corrected value which itself re-derives" allows a later-round value for a historical
   tally is a C2 reviewer judgment (§2.4).
2. Closure items 5–7 (coverage-map row, QUALITY criteria with `captured-by: none`,
   round-local Gate reject) are prose duties outside my item; I checked presence only
   (D1/D2) and did not grade their semantics.
3. The conservation note in `SCORECARD.md:4063` for items 3/4 ("erratum filed", "cross-domain
   line") names no locator, so those two duties are not mechanically re-derivable from the
   record as written.
