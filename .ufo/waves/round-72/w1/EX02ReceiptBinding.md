# EX02 — C2 receipt-tip binding (kama r72, wave w1)

Seat `EX02ReceiptBinding`. Built `tools/round72-receipt-tip-binding.py` (new, uncommitted) against
base `d30a8696` (freeze `090a0b25`). Tool bytes: sha256
`a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd`, 961 lines. Write scope
respected: the tool path and this wave dir only — `tools/pre-report-gate.py`, `SCORECARD.md`,
`LOG.md`, `corpus/`, `SKILL.md`, `plans/` were read, never written. No tool install was needed.

## 1. Frozen predicate (verbatim, byte-equal to the plan)

> `python3 tools/round72-receipt-tip-binding.py --repo <lane> --round <N> --tip <rev>` prints one
> `RECEIPT_TIP_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t>` line and
> exits 0 only when every receipt path cited by the round's self-record (`SCORECARD.md`'s
> round-`<N>` section and `corpus/lessons/round-<N>.md`) exists at `<rev>`, carries a
> `# tip=<40-hex>` or `# rev=<40-hex>` header, names a revision that is an ancestor of `<rev>`,
> and every commit in `<rev>..<tip>` touches only declared record paths; it exits 1 naming each
> `RECEIPT_TIP_FINDING <unbound|shifted|stale> <path>`.

Checked mechanically, not by eye: the C2 blockquote was joined into one line from
`plans/round-72-claims.md` and compared to the module's `PREDICATE`; both are 604 characters and
`sent == PREDICATE` is `True` (checked at `plans/round-72-claims.md`, the first blockquote in §C2).

## 2. Semantics as built

| Aspect | Implemented rule |
|---|---|
| Population sources | `SCORECARD.md`'s `## Round <N>` section (that heading to the next `## ` heading) and the whole of `corpus/lessons/round-<N>.md`, both read as **blobs at `--tip`** (never the worktree, never the index) |
| Citation notations | full `.ufo/waves/round-<N>/...`; section-relative `measured/…`, `w1/…`, `controls/…` resolved against the wave dir; brace alternatives `{a,b}` (cartesian, each alternative a separate cited path); `*`/`?`/`[...]` globs matched by name against the tip tree; a cited directory denotes the receipt files beneath it at the tip |
| Out of scope | tokens with whitespace/`<`/`>`/`$`/quotes/`...`; other rounds' `.ufo/` paths; repo-root-relative paths (`tools/`, `corpus/`, `plans/`, …); a section-relative token that neither carries a receipt extension nor exists at the tip (a bare revision such as `b43e71a8`). A **fully qualified** wave path is never filtered — it is classified strictly |
| Receipt extensions | `.out`, `.txt`, `.log`, `.json` only |
| Header | first **5** lines, first `# tip=`/`# rev=`/`tip=`/`rev=` **40-hex** match; short revisions are not headers; two different revisions in the window are `unbound` (no header shopping) |
| Class precedence (one class per receipt) | absent → `stale`; no header → `unbound`; header rev not a commit or not an ancestor → `shifted`; delta `rev..tip` touches a non-record path → `shifted` (detail names the path and the commit); else `bound` |
| Record paths | default `.ufo/waves/round-<N>/`, `corpus/lessons/`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`; `--record-path` **replaces** the list; a spec ending `/` is a prefix, a spec with `**` (crosses `/`) / `*` (does not) / `?` / `[...]` is a glob, anything else is exact |
| Exit | `0` iff `cited == bound` and `unbound+shifted+stale == 0`; `1` with one finding line per finding; `2` for CLI misuse, an unreadable self-record (missing `SCORECARD.md`, missing `## Round <N>` section, missing lesson), a cited non-receipt path, a cited directory holding no receipt, or a self-record that cites no receipt at all |
| Output | finding lines then the one summary line; `--json` prints one document (`round`, `tip`, `tip_commit`, `record_paths`, the five counts, `findings[]` with `detail` and the citing token, `line`, `exit`). The exit-2 path writes `RECEIPT_TIP_BINDING_UNREADABLE <reason>` to **stderr** and nothing to stdout |
| Read-only | `rev-parse`, `cat-file`, `ls-tree`, `merge-base`, `rev-list`, `diff-tree` only |

Two fail-closed declarations, stated because they are readings of the frozen text, not additions to
it: (a) an empty population is exit 2 — a round with no cited receipt cannot be *evaluated*, and the
control this claim replaces accepted exactly that count-based shortcut (S052: a check that collected
nothing must not print success); (b) the finding line keeps the frozen head `RECEIPT_TIP_FINDING
<class> <path>` and appends ` :: <detail>`, because the seat brief requires a `shifted` finding to
name *the path and commit* that moved — the detail carries `tools/… touched by <commit>`.

## 3. Selftest

`python3 tools/round72-receipt-tip-binding.py --selftest --work $W` → `RECEIPT_TIP_BINDING_SELFTEST
pass=16 fail=0`, exit 0 (receipt `selftest.out`). Sixteen arms, all hermetic throwaway `git init`
fixtures (own throwaway identity, `rev-parse --show-toplevel` asserted equal to the fixture dir
before the first commit, every call naming `-C <fixture>`):

| # | arm | expected |
|---|---|---|
| 1 | `predicate-one-line` | `PREDICATE` is one line carrying both output shapes |
| 2 | `clean` | exit 0, `cited=1 bound=1` (full path in `SCORECARD.md`, `measured/…` shorthand in the lesson, deduped) |
| 3 | `kill-unbound` | exit 1 `unbound` |
| 4 | `kill-stale` | exit 1 `stale` (cited receipt never committed) |
| 5 | `kill-shifted` | exit 1 `shifted`, text detail names `tools/counter.py` and the commit |
| 6 | `kill-shifted-json-detail` | `--json` detail names `tools/counter.py` |
| 7 | `cited-non-receipt` | exit 2 naming `…/notes.md` |
| 8 | `qualified-absent-non-receipt` | exit 2 naming a qualified, never-committed `.md` |
| 9 | `bare-revision-token` | exit 0 `cited=1` — a bare 8-hex token is not a receipt citation (the false positive the round-71 record would produce) |
| 10 | `empty-population` | exit 2 (`cites no receipt path`) |
| 11 | `missing-round-section` | exit 2 (`carries no '## Round 72' section`) |
| 12 | `brace-and-glob` | exit 0 `cited=3 bound=3` |
| 13 | `record-path-replaces` | default exits 1 `shifted` on `docs/note.txt`; with `--record-path … docs/` exits 0 |
| 14 | `non-ancestor-header` | exit 1 `shifted` for a real divergent commit named by the header |
| 15 | `json` | `--json` counts and `exit` field agree with the text run |
| 16 | `cli-misuse` | missing `--round` and `--round 0` both exit 2 |

## 4. Receipts (all under `.ufo/waves/round-72/w1/EX02ReceiptBinding/`)

| File | Command | Exit | Observed line |
|---|---|---|---|
| `clean.out` | `python3 tools/round72-receipt-tip-binding.py --repo $S/fix/clean --round 72 --tip <fixture-tip>` | 0 | `RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0` |
| `kill-unbound.out` | same, `--repo $S/fix/unbound` | 1 | `RECEIPT_TIP_FINDING unbound .ufo/waves/round-72/measured/after/bound.out :: no tip=/rev= header among the first 5 lines` + `… unbound=1 …` |
| `kill-stale.out` | same, `--repo $S/fix/stale` | 1 | `RECEIPT_TIP_FINDING stale .ufo/waves/round-72/measured/after/absent.out :: absent at <tip>` + `… stale=1` |
| `kill-shifted.out` | same, `--repo $S/fix/shifted` | 1 | `RECEIPT_TIP_FINDING shifted …/bound.out :: tools/round72-example-counter.py touched by 331e4d11df72` + `… shifted=1` |
| `kill-non-receipt.out` | same, `--repo $S/fix/nonreceipt` | 2 | stderr `RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.md): .ufo/waves/round-72/w1/EX01Seat/notes.md (SCORECARD.md:9)` |
| `selftest.out` | `python3 tools/round72-receipt-tip-binding.py --selftest --work $W` | 0 | `RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0` |
| `real-lane-at-base.out` | `python3 tools/round72-receipt-tip-binding.py --repo . --round 72 --tip d30a8696…` | 2 | `RECEIPT_TIP_BINDING_UNREADABLE SCORECARD.md at d30a8696… carries no '## Round 72' section; the round's self-record cannot be read` |
| `real-lane-at-freeze.out` | same with `--tip 090a0b25…` | 2 | identical reason at the freeze commit |
| `diagnostic-round-71-at-base.out` | same with `--round 71 --tip d30a8696…` | 2 | `RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.py): .ufo/waves/round-71/controls/pre-report-shortcut.py (SCORECARD.md:3766)` |

`$S` = `/fast/scratch/hyaku/kama-r72/EX02ReceiptBinding`, deleted before this yield; the fixture
shape is reproduced by `--selftest` (arms 2-8) and each receipt records its fixture tip commit.

The three real-lane runs are exit 2 **by design**, and each says why: during round 72 the round's
self-record does not exist yet (no `## Round 72` section in `SCORECARD.md`, no
`corpus/lessons/round-72.md` at either `d30a8696` or `090a0b25`), so the tool refuses to print a
`cited=0` green. The round-71 diagnostic runs the same code on landed bytes and stops on the first
cited non-receipt: round 71's record cites its control **scripts** under the wave dir.

## 5. Measured observations the closure needs (operability, not claim edits)

1. **Headers are the bottleneck, not the tool.** On the worktree today, 36 `.out` files exist under
   `.ufo/waves/round-72/`; 15 carry no `tip=`/`rev=` 40-hex header (`EX03GateArm6/{live-scored,selftest,stub-red}.out`,
   `SCR01SourceRow/{fetch,reopen,validate-lane,validate-mirror-preE11,validate-mirror}.out`,
   `SCR03RegistryLog/selftests.out`, `SCT01ReceiptRecon/{commands,ignored-fixture,report71}.out`,
   `measured/before/{populations,receipt-tip-control-old,round-scope-control-old}.out`). Citing any
   of them in the round record reads `unbound` (exit 1) — the claim working, and a list the scribe
   can act on.
2. **At the freeze commit the wave dir holds 5 blobs, 3 of them receipt files, and all 3 are
   `unbound`** (`controls/freeze.txt`, `measured/before/receipt-tip-control-old.out`,
   `measured/before/round-scope-control-old.out`). Both before-measurements the plan cites are in
   that set, so a round record that repeats those citations reads `unbound=3` before it reads
   anything else; either add a `# tip=<40-hex>` line to those two receipts or cite the plan.
3. **Citation class is a hard gate.** Any cited wave path that is not `.out/.txt/.log/.json` is exit
   2 — seat reports (`.md`), control scripts (`.py`), fetched sources (`.html`), `.tsv`, `.ufo`
   ready markers. The round-72 record must cite receipt files, not directory contents, or C2's own
   after-run cannot print a verdict. This is the rule as frozen in the seat brief; flagged here
   because it constrains how the record is written, not because the tool is being lenient.
4. **Post-landing re-take.** A receipt whose header names a revision before the instrument commit
   reads `shifted` once `tools/round72-receipt-tip-binding.py` lands (the delta then touches
   `tools/`). These nine receipts header the lane base `d30a8696` + "tool bytes uncommitted", which
   is honest for the bytes they graded; the round's *after* receipt must therefore be re-taken at
   the report tip with that tip in its header, and the record should cite the re-taken file.
5. `--record-path` replacement is proven (arm 13): record paths are declared, not inferred, and the
   instrument inputs (`tools/`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md`,
   `corpus/knowledge/`, `registry/`, `plans/`) are never record paths.
6. **Registry population.** The tool matches `tools/gate-registry-check.py`'s declared population
   (`tools/round<N>-*.py`), so `registered` grows by one when it is tracked. The SKILL.md row that
   the plan requires (predicate in the tool, the registry row and the receipt label) is **not mine
   to write** — a scribe owns it.

## 6. Disagreements reported, never edited

1. **Non-ancestor header class.** The plan's §C2 kill rule says "a header naming a non-ancestor or a
   revision whose delta touches `tools/` (`shifted`)"; this seat's brief says the same clause is
   `stale`. Both readings exit 1 and name the receipt, so no verdict moves. Implemented the **frozen
   plan's** mapping (`shifted`), because the round's plan is the frozen claim and SCR02's knowledge
   entry records that mapping; the `::` detail names the revision and says "not an ancestor of
   <tip>", so the record reads correctly under either class name. Told `SCR02KnowledgeEntry` in one
   line.
2. **Freeze base line.** `.ufo/waves/round-72/controls/freeze.txt` now reads
   `base=090a0b25a71298ed1a58e1f81315d850f4932e74` (`amended_at=2026-11-03T22:41`), while
   `plans/round-72-claims.md` states "Base revision `d30a8696` (lane `master`, == remote at freeze)".
   Observation only: this seat ran the base receipt at the brief's `d30a8696` and a second receipt at
   `090a0b25` so the closure can see both. Not edited, not judged here.
3. The plan requires the predicate sentence in the SKILL.md registry row; that file is outside this
   seat's write scope, so the row is handed off (see 5.6).

## 7. Files written

- `tools/round72-receipt-tip-binding.py` (new; sha256 above)
- `.ufo/waves/round-72/w1/EX02ReceiptBinding/{selftest,clean,kill-unbound,kill-stale,kill-shifted,kill-non-receipt,real-lane-at-base,real-lane-at-freeze,diagnostic-round-71-at-base}.out`
- this report

Nothing was committed (receipts and tool are uncommitted by instruction). No other lane file was
modified; `git status --porcelain -uall` shows exactly the eleven paths above (tool, nine receipts,
this report). The other tracked modifications in that listing (`LOG.md`, `SKILL.md`,
`corpus/*`, `plans/round-72-claims.md`, `tools/pre-report-gate.py`) belong to sibling seats.

## 8. Risks

- The exit-2 citation-class rule (5.3) is the sharpest edge: a round record that cites one `.md`
  seat report or one `controls/*.py` gets no verdict at all. This is the frozen rule, and the
  closure should treat the record's citation list as something to curate deliberately.
- `stored`/shallow repositories are not handled: `rev-list`/`diff-tree` are used as-is, so a shallow
  clone could hide the instrument commit and read `bound`. The lane is not shallow; a `--depth`
  mirror would need an explicit guard this claim does not provide.
- The tool proves binding, not honesty of contents (the claim's declared non-goal); a receipt whose
  bytes lie still binds if its header and delta are clean.
