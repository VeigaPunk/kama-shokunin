# SCT01 — independent re-derivation (kama round 78, w1)

Seat: scout, read-only. No lane edits, no commits, no subagents.
Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`.

Observation window: 2026-11-04, worktree snapshot
`receipts/09-worktree-snapshot.txt` (sha256s and `git status`). Sibling seats were
actively editing `SKILL.md` and `corpus/README.md` while this seat ran (I observed the
gate row change from eight to nine arms between two reads), so every statement below
names either a committed revision or the timestamped worktree, never a moving "now".

Revisions used:

| Ref | Value | How |
|---|---|---|
| base | `c62ffd3aea930b98375f805cc3dfb821a703148b` | plan §Base; `git cat-file -t` → `commit` |
| freeze commit | `11f46d644ed08d11758874a92d79214b3577a8a0` | parent `d015a178`; `d015a178^` = base |
| sealed revision | `6c1550a14babaca092cfcc3106f792d695652200` | round-77 tip; `git merge-base --is-ancestor <sealed> master` exit 0 |
| lane tip at observation | `2bd07a8aeef822bd6b8b9137df4439f1499b08c9` | `git rev-parse master`; 4 commits past base (`d015a178`, `11f46d64`, `0f56ad5a`, `2bd07a8a`) |

---

## 1. F3, F4, F5, F6 re-derived by hand

Method: committed bytes only for the "old" column (sealed `6c1550a1`), and the
timestamped worktree plus committed module bytes for "new". I did not run
`.ufo/waves/round-78/measured/before/enumerate-facts.py`; every value below comes from
git/grep/ast/python one-liners in `receipts/02-f3.txt` … `receipts/04-f5-f6.txt`.

### F3 — gate registry row vs gate module

| | Value | Independent derivation |
|---|---|---|
| plan old (implied, not printed) | `gate=arms:8/word:eight/newest:round75-instruments/tally:18` | sealed `SKILL.md:309`: "**(eight arms**", "`arms=8`", "`PRE_REPORT_SELFTEST pass=18 fail=0`"; last named arm `round75-instruments` |
| plan new (fixed string) | `gate=arms:9/word:nine/newest:round77-instruments/tally:22` | sealed `tools/pre-report-gate.py` `ARM_ORDER` = 5 `ARM_SPECS` + `round-clean` + `round74-v2` + `round75-instruments` + `round77-instruments` = **9**; newest = **round77-instruments**; sealed `measured/after/gate-selftest.out` = `PRE_REPORT_SELFTEST pass=22 fail=0`; sealed `gate-run.out` = `PRE_REPORT round=77 arms=9` |
| worktree (uncommitted) | row now reads "nine arms", `arms=9`, `pass=22`, arm 9 `round77-instruments`, "retired `round76-instruments` arm no longer runs" | `awk NR==309 SKILL.md`; `git diff --stat` = `SKILL.md \| 2 +-` |

**Verdict: both old and new re-derive. Disagreements the value string cannot express:**

1. The module's own docstring says *"Scored verdicts now carry `arms=10`"* and *"adds arm
   10, `round77-instruments`"* (`tools/pre-report-gate.py:182` and the round-77
   paragraph) while `len(ARM_ORDER) == 9` and the module prints `arms=9`. The fact string
   `gate=arms:9` is correct, but the module text contradicts its own count.
2. The module's `PREDICATE` constant still describes arm 9 as "the three round-76
   counters arm 9 composes (receipt scope, self-record facts, append-exempt accounting)",
   while the code's arm 9 is `round77-instruments`. Again a text/code split the value
   string cannot carry.
3. The plan never prints F3's `old` string. The correction block's `old=` must therefore
   be the string I derived above; if the landed counter derives any other spelling
   (e.g. no `newest:` component) the correction will be rejected as an unbacked/wrong
   value even though the sealed bytes are as stated.
4. Routed defect D1's wording "name arm 10 `round77-instruments`" is off by one: the arm
   is the 9th in `ARM_ORDER`; the worktree row now says arm 9, which is the correct
   reading.

### F4 — divergence pointer

| | Value | Independent derivation |
|---|---|---|
| plan old | `pointer=section:Mistakes 4` | sealed `SCORECARD.md:4379`: "it is documented in `corpus/lessons/round-77.md` **§Mistakes 4**" (the only `documented in` sentence in the sealed record) |
| plan new | `pointer=section:Freeze divergences item 3` | round-77 lesson `## Freeze divergences` item 3 is "**C3 correction scope**" (`corpus/lessons/round-77.md:95-98`), the correct target; `§Mistakes 4` is the unrelated `mutating-git-in-lane` breach |
| worktree | still `§Mistakes 4`; `grep -c 'Freeze divergences item 3' SCORECARD.md` = 0 | `receipts/03-f4.txt` |

**Verdict: old re-derives; new does not yet re-derive (no appended correction in the
worktree; F4 is C1's repair, not yet landed).**

**Derivations the string cannot express:**

1. `corpus/lessons/round-77.md` has `## Mistakes` at line 11 with items 1–3, then `## Gate`,
   `## Freeze divergences`, … and item **4** (`mutating-git-in-lane`) sits at line 240,
   *after* two `### Superseded bytes` blocks and outside any `## Mistakes` body. A
   section-scoped parser anchored on `## Mistakes` will not find "Mistakes 4"; a
   file-wide item-number parser will. The string `pointer=section:Mistakes 4` cannot say
   which parser the counter uses.
2. The new value depends on ruling (d) ("an appended correction supersedes the stale
   pointer"). The correction block lives in `corpus/lessons/round-78.md` §Corrections,
   not in `SCORECARD.md`; if the counter only scans the record, the pointer stays
   `Mistakes 4`. The counter is not landed (`tools/round78-selfrecord-round77.py` absent,
   `test -f` exit 1), so this reading is unverified.

### F5 — knowledge-entry provenance

| | Value | Independent derivation |
|---|---|---|
| plan old | `provenance=missing:corpus/knowledge/register-cutoff-split.md` | round 77 added exactly two entries (`d86ce85b`): `baseline-receipt-binding.md` (its `source:` cites **S550/S073/S175** → passes) and `register-cutoff-split.md` (its `source:` cites plan paths + `tools/…` line ranges, **no `S###`** → missing). Matches exactly |
| plan new | `provenance=missing:none` | worktree: both `source:` lines unchanged; `grep -n source-correction corpus/knowledge/*.md` exit 1 (no lines). New value does **not** re-derive yet |
| worktree | — | `receipts/04-f5-f6.txt` |

**Verdict: old matches; new not yet true.** The predicate accepts a `source-correction:`
line, so the repair is possible without rewriting the filed `source:` bytes; the scribe
seat's line has not landed at observation.

### F6 — coverage-map rows

| | Value | Independent derivation |
|---|---|---|
| plan old | `coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md` | sealed `corpus/README.md`: neither name appears; only `knowledge/selfrecord-fact-binding.md` was added at round 77. Matches |
| plan new | `coverage-map=missing:none` | worktree rows exist at `corpus/README.md:1728-1729` for both entries (uncommitted), **but** both entry cells are `| \`corpus/knowledge/…\`` while the 45 pre-existing `knowledge/`-prefixed row lines (42 distinct entries) are `| \`knowledge/…\`` and the README's own derivation regex is `^\| \`((?:knowledge/)[^\`]+)\`` (line 1721) |

**Verdict: old matches; new re-derives only under a tolerant path reading — and that is
the most likely failure mode for C1's F6.** Measured both readings:

- strict (`^\| \`knowledge/…\``, the README's own regex): `strict_row=False` for both →
  the counter would still derive `missing:both`.
- tolerant (`(?:corpus/)?knowledge/…`): `loose_row=True` for both → `missing:none`.

The landed counter does not exist yet, so I cannot say which it uses. If it reuses the
README's strict regex (the obvious implementation), the two new rows will not clear F6
even though they are present. This is a concrete, checkable risk, not a style note.

---

## 2. C2 base decomposition

### 2.1 `events=248`

Reproduced independently (not via `enumerate-facts.py`): walk
`git rev-list --topo-order --reverse --parents <base>`, diff each commit against its
first parent with `git diff --numstat -z --no-renames -- <the 11 contract pathspecs>`,
count every `(commit, file)` pair with ≥ 1 deletion.

```
commits 628   merge_commits 2   independent_events 248   event_files 34
```

The audit itself at `--to c62ffd3a` prints `summary.events=248`
(`ungraded=91`, `restored=99`, `unrestored=53`, `disclosed=5`,
`permitted_lines=634`); the audit process exits 1 at the base because those events
remain unresolved, which is expected and does not weaken the event count. Receipt:
`receipts/05-c2-events.txt`.

Base bucket arithmetic from
`.ufo/waves/round-78/measured/before/c2-append.out`:
`53 + 56 + 28 + 4 + 99 + 5 = 245`, plus `unaccounted=3` = **248**. Receipt:
`receipts/07-c2-base-and-commits.txt`.

### 2.2 The three unaccounted commits

All three are `SCORECARD.md` deletion events; the audit marks every one
`status=ungraded` with `graded=0`, `permitted=0`, `undisclosed=[]`:

| Commit | Deleted | Ungraded | Graded | Derived parent sections (sorted) | Contract-exempt? |
|---|---|---|---|---|---|
| `05a039805ba5dcca3e14091a447c88c07c971664` | 3 | 3 | 0 | `## Axes`, `## Capabilities`, `## Planned` | yes, all |
| `0fca5e18d408ab92717bbd9e26e7a4b4a1bcd7ac` | 2 | 2 | 0 | `## Axes` | yes |
| `21458716fbf3961312455ff78a12c9ca3a241a9e` | 1 | 1 | 0 | `## Planned` | yes |

Derivation: audit event JSON plus `round76-append-exempt.exemption_sections`, which
returns `(sorted parents, eligible) = (…, True)` for each. Contract row:
`SCORECARD.md  A-corr … exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities`
(`registry/append-only-contract.tsv:3`). All six deleted lines sit under one of the five
declared heads. Receipt: `receipts/06-c2-forced-rows.txt`.

**Does the contract put their deleted lines in exempt-head regions?** Yes — the
exemption set is exactly `## Axes|## Planned|## Capabilities` for these events.

**Audit marks them ungraded?** Yes: `status=ungraded`, `graded=0`, `ungraded == deleted`,
and `permitted=0`, so the `ungraded` bucket here is the exempt-head species, not a
permitted A-row carriage.

### 2.3 Are the three appended rows forced or chosen?

**Forced**, except the note text (and row order):

- *Register choice* is forced: an ungraded event with `undisclosed=[]` cannot satisfy the
  accepted register (its grader requires an `undisclosed` line hash), and the other
  computed buckets (`permitted`, `out_of_region`, `restored`, `disclosed`) are audit
  facts, not rows. `exempt` is the only absorbable bucket.
- *commit, file* = the event key — forced.
- *class* must be the literal `exempt-head` — forced by the grader comparison.
- *count* must equal `event.ungraded` (3 / 2 / 1) — forced (here also `deleted`).
- *sections* must equal `'|'.join(sorted(parents))` — forced, giving
  `## Axes|## Capabilities|## Planned`, `## Axes`, `## Planned` respectively.
- *note* must be non-empty; its wording is the only chosen cell.

After appending, `exempt` becomes `56+3=59` and the six buckets sum to `248`. The plan's
`<a>/<x>/<p>/<o>/<r>/<d>` are otherwise unchanged.

### 2.4 Frozen-predicate conflict (new, same form as D6)

The frozen C2 predicate (`plans/round-78-claims.md:127`) requires, literally:

> "each bucket row is committed at the audited revision or earlier"

The audited revision is `c62ffd3a`; the three required rows necessarily land in round-78
commits **after** it. On the literal reading the claim is unsatisfiable — `unaccounted=0`
cannot be reached by appending the rows. The untracked implementation instead binds each
row to `--commit-at` (default `master`) and reports worktree-only rows as `uncommitted`,
which is ruling (b), not the predicate sentence. This is structurally the same
predicate/ruling divergence D6 was opened to close; round 78 should either amend the next
round's wording or record the divergence explicitly. Confidence: high (text vs required
fix); the only escape is reading "bucket row" as the *event* rather than the register row,
which makes the clause redundant.

---

## 3. Nine round-77 routed defects (spot-check §5) against today's tree

Status vocabulary: **fixed** (bytes committed at `master`), **fixed-in-worktree**
(uncommitted edit observed), **fixed-in-tool** (untracked/committed code implements it),
**open**, **not-yet** (expected later in the round). Observation timestamp in
`receipts/09-worktree-snapshot.txt`.

| # | Defect | Status | Evidence (command → result) |
|---|---|---|---|
| D1 | Gate registry row | **fixed-in-worktree** | `awk NR==309 SKILL.md` → "nine arms", `arms=9`, `PRE_REPORT_SELFTEST pass=22`, arm 9 `round77-instruments`, "retired `round76-instruments` arm no longer runs"; `git show 2bd07a8a:SKILL.md` (HEAD) still "eight arms/arms=8/pass=18"; `git diff --stat -- SKILL.md` → `1 file changed` |
| D2 | Gate run at the tip | **not-yet** | `ls .ufo/waves/round-78/measured/after` → No such file; `find .ufo/waves/round-78 -name '*gate*' -o -name '*pre-report*'` → empty; round-77 receipt still names `rev=f9b0ab6c` |
| D3 | `append-exempt-class` capability row marked | **open** | `grep -n append-exempt-class SCORECARD.md` → rows 162/4241/4348 still name `tools/round76-append-exempt.py` with no partial/planned/probe marker |
| D4 | Coverage-map rows for the two entries | **fixed-in-worktree** (path-form caveat, see F6) | `grep -n 'baseline-receipt-binding\|register-cutoff-split' corpus/README.md` → rows 1728-1729; `git diff --stat -- corpus/README.md` → `15 +++++++++++++++` |
| D5 | `register-cutoff-split.md` source cites no `S###` | **open** | `head -1 corpus/knowledge/register-cutoff-split.md` → own-work plan/tool paths only; `grep -n source-correction` → exit 1 |
| D6 | C2 predicate/ruling wording | **fixed at plan level** | `plans/round-78-claims.md:138-139`: round-77 wording "is superseded by C2's own sentence and its text is not rewritten — routed defect D6"; the new predicate drops "under that register's own introduction cutoff". Successor conflict at line 127 (§2.4) |
| D7 | Registers read from the worktree | **fixed-in-tool (untracked)** | `tools/round78-append-registers.py`: `--commit-at` default `master` (line 254), per-row committed check with `uncommitted` findings (line 82), digest line `APPEND_REGISTERS_REGISTERS exempt=<hex12> accepted=<hex12>` (line 152). `git status` → `?? tools/round78-append-registers.py` |
| D8 | Same-commit growth hole | **open** | Ruling (c) `plans/round-78-claims.md:144-145` rejects a same-commit row "when the row's named event is **not ancestral** to that commit"; `git merge-base --is-ancestor <tip> <tip>` exits **0**, so a same-commit row is treated as ancestral and passes. `precedes()` in `round77-append-registers.py:64-69` is exactly that call; the new selftest arms (lines 166-167) contain no same-commit case. The hole is **not** closed by the plan or the tool |
| D9 | Two stale pointers | **open (both halves)** | fleet report `…/.ufo/reports/round-77/kama.md:69` still `LOG.md:3130`; the §Round 77 heading is at `LOG.md:3137` (`git show 6c1550a1:LOG.md \| grep -n '^## Round 77'` → 3137). Lane `SCORECARD.md:4379` still `§Mistakes 4`; `grep -c 'Freeze divergences item 3' SCORECARD.md` → 0 (exit 1) |

Note: D9's first half is in the fleet repo (outside this seat's write scope and outside
the lane), so only the L1 can fix it; the lane half is still untouched.

---

## 4. Sealed-revision verification

| Check | Result |
|---|---|
| `git -C <lane> cat-file -t 6c1550a14babaca092cfcc3106f792d695652200` | `commit`, **exit 0** |
| `git -C <lane> merge-base --is-ancestor 6c1550a1… master` | exit 0 (sealed is an ancestor of today's `2bd07a8a`) |
| `git -C <lane> cat-file -t 6c1550a141babaca092cfcc3106f792d695652200` | `fatal: Not a valid object name`, **exit 128** |
| `git -C <lane> rev-parse 6c1550a141…` | `fatal: ambiguous argument`, exit 128 |

**Where the 41-character string actually appears.** `git grep -n 6c1550a141` at base
`c62ffd3a` → no match; at sealed `6c1550a1` → no match. The only files in the lane that
contain it are `.ufo/waves/round-78/w1-spec.json:60` and `.ufo/waves/round-78/w1-dispatch.json:184`
(the round-78 seat dispatch, introduced at `0f56ad5a`; an orphan copy exists at
`44ab7037`). The fleet round-77 report at `822dc7ac` and at its current bytes cites the
correct 40-hex hash three times and the variant zero times; `grep -rl 6c1550a141` over
the fleet `.ufo` tree also returns nothing.

So the plan's premise — "round 77's own record cites a 41-character variant that no
object answers" — is **not re-derivable from any round-77 record I can reach**. The
variant is a round-78 dispatch artifact that the dispatch attributes to round 77. The
`cat-file` expectation (exit 128) still holds for the string itself. Receipt:
`receipts/01-tip-sealed-variant.txt`. Confidence: high for the searched population;
unresolved: a round-77 artifact outside the lane and the fleet `.ufo` tree (none is
named by any record I read).

---

## 5. Disagreements and remaining unknowns

1. **F3 module text vs count** — `arms=10`/"arm 10" in the gate docstring against
   `arms=9` printed and nine `ARM_ORDER` entries; the `PREDICATE` constant still names the
   retired round-76 arm as arm 9. Not expressible in the fact string.
2. **F4 `§Mistakes 4` placement** — item 4 lives outside `## Mistakes`, after the
   `### Superseded bytes` blocks; a section-scoped parser would not resolve the old
   pointer even though the item exists.
3. **F4 new-value mechanism** — ruling (d) says an appended correction supersedes the
   record pointer, but the correction block lives in `round-78.md`, not the record; the
   counter is absent so the mechanism cannot be checked.
4. **F6 path form** — the two new coverage rows use `corpus/knowledge/…` while the
   README's own coverage derivation counts only `knowledge/…`; strict reading still
   yields `missing:both`.
5. **C2 predicate line 127** — "each bucket row is committed at the audited revision or
   earlier" is unsatisfiable for the three rows the fix must append; the implementation
   uses `--commit-at`. A D6-shaped divergence inside round 78's own predicate.
6. **D8 is not closed** — ruling (c) and `precedes()` both accept a same-commit row
   because `git merge-base --is-ancestor X X` is true; no selftest arm covers it.
7. **41-character string provenance** — cited only by the round-78 dispatch, not by any
   round-77 record in the lane (base/sealed or current) or the fleet report.

Unknowns I could not close with the current tree: the exact regex/parse behavior of the
three round-78 counters (`round78-selfrecord-round77.py` absent at observation, the other
two untracked and unrun here), and the final C2 bucket values before EX02's rows land.

---

## 6. Receipts

All paths absolute. Every file contains the literal `$ command` lines, outputs, and
`exit=` codes from this run.

| Receipt | Commands covered | Exit codes |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-78/w1/SCT01Recon/receipts/01-tip-sealed-variant.txt` | `rev-parse master`, `cat-file -t` (40-hex, 41-hex), `merge-base --is-ancestor`, `git grep` at base/sealed, `grep -c` fleet report | 0 / 0 / 128 / 0 / 1 (no grep match) / 0 |
| `…/receipts/02-f3.txt` | sealed + worktree `SKILL.md` row, sealed `ARM_ORDER`, `gate-selftest.out`, `gate-run.out`, ast arm count | 0 |
| `…/receipts/03-f4.txt` | sealed `SCORECARD` 4375-4380, `documented in`, lesson `Mistakes`/`checkout`, item 4, `Freeze divergences`, worktree pointer | 0 (1 on the deliberate zero-match grep) |
| `…/receipts/04-f5-f6.txt` | sealed/worktree `source:` lines, `source-correction` grep, sealed/worktree coverage rows, round-77 additions, strict/loose regex test | 0 (1 on the zero-match grep) |
| `…/receipts/05-c2-events.txt` | audit `--json` summary, independent event counter, three commit stats | 0 |
| `…/receipts/06-c2-forced-rows.txt` | event JSON + `exemption_sections`, frozen predicate lines, scope rulings, exempt-register schema | 0 |
| `…/receipts/07-c2-base-and-commits.txt` | `before/c2-append.out`, bucket arithmetic, `c62ffd3a..master` log, freeze parent chain, `status --porcelain` | 0 |
| `…/receipts/08a-defects-d1-d5.txt` | D1-D5 commands and outputs | 0 |
| `…/receipts/08b-defects-d6-d9.txt` | D6-D9 commands and outputs, `--is-ancestor` self-test | 0 (1 on the zero-match grep) |
| `…/receipts/09-worktree-snapshot.txt` | timestamp, `rev-parse master`, `status --porcelain`, sha256s, tool inventory | 0 |
