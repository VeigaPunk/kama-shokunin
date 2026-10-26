# V1Ctr — round-48 C1 counter review (tools/round48-append-audit-v3-check.py)

Verdict: the frozen C1 counter is sound as run on this lane — `met=True` reproduced
(exit 0), `recompute()` is genuinely independent of the tool, and all eleven fixture
expectations re-derive correctly by hand — but two latent coverage holes are real and
confirmed by minimal fixtures: the stable leg passes on a base with zero graded lines
(F1), and the contract leg's REQUIRED set is escapable by a duplicate narrowing row so
the lane verdict can be met while a required file's grading is silently dropped (F2).
Both are latent (the real contract at 380bcdff has 9 non-overlapping rows and the real
base has 5/5 events graded>0); neither affects today's verdict. Plus one minor
robustness crash (F3). Counter frozen — fixes proposed, not applied.

Measured commit: 380bcdff9c8af06997c482f6eb03db926a794a2b (base 33e005827742b29772b153cda036ec9f27f653be).
Below, "counter" = tools/round48-append-audit-v3-check.py, "tool" = tools/append-only-audit.py, both at the tip.

## Baseline (reproduction)

```
git clone --shared kama-shokunin $S/lane
python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff... --scratch $S/c1run
# selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5
# lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True   exit 0
```
Matches the L1's pre-wave dry run exactly. Receipt: out/V1Ctr/baseline-receipt.txt.

## Q1 — is recompute() independent of the tool? Yes.

- No import or exec of the tool: the counter only writes the tool's source to scratch and
  runs it as a subprocess (counter 641-647, run_tool 393-405). `recompute` (301-389) is
  its own code path: own contract parser (parse_region 170-186, parse_contract 188-208,
  token 210-215, binds 226-234, row_binds 236-257), own diff parsing from -U0 hunk
  headers (del_positions 277-287, cross-checked against numstat at 321-322), own
  sections (268-275), own eligibility/graded/held/status (339-377).
- Cross-validation: on all eleven fixture repos and on the lane, `diff_result` reports
  0 mismatches between tool and counter (out/V1Ctr/scenario-dump.txt, per-scenario
  "counter-recompute mismatches: 0"; baseline receipt lane=1).
- Residual (by design, not a defect): both implement the same frozen docstring spec, so a
  spec-level shared misreading would pass lane. The by-construction fixtures are the
  anchor; my hand re-derivation (Q2) found no divergence between the docstring spec and
  either implementation.

## Q2 — are the eleven fixture expectations written by construction? Yes; all re-derived by hand and correct.

Expectations are static literals in scenarios() (500-592); only commit ids are captured
at run time. Hand re-derivation from the scenario code against the docstring definitions
(threshold 20, first-parent diffs, section = last `## ` title at/before the line,
eligible = window max of count(T,x) >= count(T,parent), held over G with the max(0,.)
clamp):

| # | scenario | construction → derived expectation | matches literal? |
|---|---|---|---|
| S1 | threshold | base 40 lines; c1 keeps t20..t39 → deletes t0..t19 (20 ≥ 20 → event, graded 20); c2 keeps only t39 → 19 deletions < 20, no event; window never holds t0..t19 → unrestored, held 0, exit 1 | yes |
| S2 | exempt-rewritten | 24 `a` lines → `b` inside `## Axes`; count(## Axes) 25→25 → eligible → graded 0, ungraded 24, exit 0 | yes |
| S3 | exempt-gutted | 24 `a` → 1 `collapsed`: count 25→2 < 25 → graded 24, unrestored, exit 1 | yes |
| S4 | dated-rewritten | 25 `r` → `s` in `## Round 1` (not exempt) → graded 25, unrestored, exit 1 | yes |
| S5 | only-errata | body `## Body` deletion (25) outside `## Errata` prefix → ungraded; errata deletion (20) inside → graded 20, unrestored; exit 1 | yes |
| S6 | clamp | delete 20 dup + 20 uniques; K keeps dup:10; uniques return at c2 → h = 20·min(1,20) = 20 (without the clamp, dup would contribute min(20, 0−10) = −10 → 10) → restored_max 20 of 40, restored_best c2, restored_by None (h never reaches 40), held 20, partial, exit 1 | yes |
| S7 | merge-first-parent | side deletes 25 (event), main-tip appends (no event), merge vs first parent main-tip deletes the 25 (event, unrestored, held 0); exit 1, 2 events | yes |
| S8 | regressed | delete 20, restore at c2 (restored_max 20, restored_by c2), re-delete 5 (< 20, no event) → held_at_to 15 < 20 → regressed 1, exit 1 | yes |
| S9 | dashdash-crlf | 20 `-- dash i\r` lines deleted → graded 20, unrestored, exit 1 (`--` path separator + CRLF bytes survive) | yes |
| S10 | bad-declarations | decl without `append-only` / negation / pointer not naming `## Round 1` → 3 unbound rows, 0 events, exit 1 | yes |
| S11 | clean | ledger restored (restored, by c2, held 20) + score exempt rewrite (ungraded 24) → exit 0 | yes |

All eleven pass at the tip (out/V1Ctr/scenario-dump.txt; fixture=1 fixture_fail=0 in the
baseline). Soft spots, none of them wrong expectations: S7's summary subset is `{}` and
the side event is unconstrained — but the written expectations are order-independent
(flipping the unspecified sibling order makes the side event restored+regressed; exit 1,
nev 2 and the merge event are unchanged either way; sibling order observed stable across
three runs incl. forced dates 2000/2030). S1's summary subset omits `events` (pinned via
nev=1); S10 pins only bad_declarations/events (correct by construction).

## F1 (medium, latent) — the stable leg can be met with zero graded lines

Counter 744-757: `stab = len(eb) >= 1` (750) is the only floor, and the per-event check
(753-757) requires `isinstance(e.get("graded"), int)` on the base event — so graded
cannot be None on either side, but graded == 0 passes, and for such events
restored_max (0) and restored_best (None) compare 0==0 / None==None vacuously. Nothing
else in `met` requires any graded line: the lane verdict (719-720) needs only
ungraded_lines > 0, and REQUIRED (142-152) pins row presence/region, not graded
coverage. The docstring's "every base event (carrying an integer `graded`)" is
implemented as a type check, not a positivity requirement.

Fixture (out/V1Ctr/driver.py F1, log out/V1Ctr/f1-f2-fixture-log.txt): contract row
`ledger.md A NOTES.md:2 only=## Nope@NOTES.md:3` (pointer binds), file without a
`## Nope` section; base rewrite (40 deleted, graded 0) and tip rewrite (40 deleted,
graded 0). Verbatim replica of 748-757 → stab=True; lane-verdict replica of 719-720 →
True; tool exit 0; tool-vs-counter mismatches 0. So a lane where nothing is ever graded
satisfies stable=1 and lane=1.

On the real lane this is not active: the tool at the base (tip contract) reports 5
events, all graded>0 — SCORECARD 14, LOG 2292, SCORECARD 2349, QUALITY 375, README 663
(out/V1Ctr/base-events.json) — so the leg currently compares real graded values.

Proposed fix (one line, counter 750): replace `stab = len(eb) >= 1` with
`stab = any(isinstance(e.get("graded"), int) and e["graded"] > 0 for e in eb.values())`
(keep the "no event at base" detail branch), so the leg must compare at least one
actually-graded event.

## F2 (medium-high, latent) — REQUIRED is escapable by a duplicate narrowing row; the lane verdict can be met with a required file's grading dropped

The contract leg resolves rows per pattern with last-wins (`by_path = {r["path"]: r for
r in rows}`, counter 680; REQUIRED loop 681-689), while grading unions ALL matching rows
(counter 341-348: `exempt_titles |=`, `only_prefixes.append`) — and the tool does
exactly the same union (tool docstring 18-19 "a file matched by several rows takes the
union of their exempt titles and only prefixes"; file_regions 350-360; graded loop
413-419). Because tool and counter agree, the lane leg cannot catch it.

Fixture (out/V1Ctr/driver.py F2, log out/V1Ctr/f1-f2-fixture-log.txt): contract rows,
in order
```
LOG.md	A	NOTES.md:2	only=## Nope@NOTES.md:3	fixture   (narrowing, FIRST)
LOG.md	A	NOTES.md:2	*	fixture                   (required-shape, LAST)
```
both bind; a 40-line rewrite of LOG.md (no `## Nope` section) gives deleted 40,
graded 0, ungraded 40, exit 0. Verbatim replica of the REQUIRED loop passes for
LOG.md (by_path takes the LAST row, region `*`); recompute and the tool agree
(mismatches 0); the lane-verdict replica is True. Control: the same repo with only the
`*` row grades the same deletion 40/40 and exits 1. So a contract that keeps every
required row (correct region, last) and prepends one narrowing duplicate for it passes
contract=1 and lane=1 while the file's grading is silently dropped. The same union
mechanism lets an extra `exempt=` row on a required path ungrade whole sections in
either row order.

Not active on this lane: the tip contract (registry/append-only-contract.tsv) has
exactly 9 rows, no duplicates, no overlaps.

Proposed fix (counter, contract leg after 680): reject rows whose pattern matches a
required path with a region different from REQUIRED — e.g. for each required path,
collect `rows2 = [r for r in rows if r["path"] == path or <pattern matches the lane
file>]` and require every one to have the REQUIRED region (and, cheaper but narrower,
reject duplicate identical `path` keys outright). Symmetrically, `recompute` could
refuse a file matched by rows with conflicting region kinds.

## F3 (minor) — the stable leg crashes on a non-dict event instead of reporting

Counter 748-749 build `eb`/`et` without the `isinstance(e, dict)` filter that
diff_result (417) and the fixture leg (603) both have. A tool emitting
`"events": ["x"]` raises `AttributeError: 'str' object has no attribute 'get'`
(repro in transcript; two-line), which escapes main's `except EvalError` → traceback,
exit 1 with no summary line — conservative in direction (not met) but unstructured
instead of a `detail:` line or exit 2. Proposed fix: add the same `if isinstance(e,
dict)` filter at 748-749 and treat a filtered-out base event as a stability failure.

## Observations (checked, not defects)

- REQUIRED does not pin the `rule` cell — harmless: rule is unused for grading in both
  implementations (tool discards `_rule` at 212; counter never reads `row["rule"]` in
  recompute).
- The tool counts `unmatched` patterns (summary 444) but its exit_code (469-473) ignores
  them, and the counter's SUMKEYS never compares `unmatched` — a pattern matching
  nothing is silent in both. It cannot drop required coverage (REQUIRED looks up exact
  strings that exist on the lane), so noted as a gap, not a finding.
- Docstring placement nit: the contract-leg sentence "the tool's lane run reports
  exactly the expansion as files and every declaration ok" is implemented in the lane
  block (counter 692-699), not the contract block. Both are checked somewhere in `met`.
- Tooling installs: none (no pacman, no new tools; only python3/git already present).

## Residual risk and verification gaps

- Spec-level shared misreading between tool and counter cannot be excluded from the
  counter's own legs alone; mitigated by the by-construction fixtures (Q2) and my
  independent re-derivation finding no divergence.
- F1/F2 are latent: today's contract and base data do not trigger them. If the contract
  gains rows in a later round, F2 becomes live; the fix belongs in the round-49 counter
  or a lane-side contract lint, since this counter is frozen.
- I did not review the C2 counter or the live receipts (other seats' scope); the
  known integration items (unregistered counters, 33-vs-34 spot-check count, hexrun
  d0012618) are not re-reported.

## Paths written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr.md (this report)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/baseline-receipt.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/base-events.json
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/scenario-dump.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/f1-f2-fixture-log.txt
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/driver.py
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/V1Ctr/run-scenarios.py
