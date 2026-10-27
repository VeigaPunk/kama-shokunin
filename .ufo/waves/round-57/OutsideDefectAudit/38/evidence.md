# R57Item38OutsideDefectAudit — round-56 non-author routed defects re-evaluated against the tree

Axes: operability + calibration (lane `shokunin.conf` row and `SCORECARD.md:6`; `MISSION.md:29` conflicts and is not resolved here).
Seat role: revenger, leaf. Read-only against shared files. Writes only to this directory (`OutsideDefectAudit/38/`) and to `/fast/scratch/hyaku/kama-r57/R57Item38OutsideDefectAudit/`. No commits, no tool installs.

## Source of the defects (non-author, round 56)

`corpus/lessons/round-56-verifier-spotcheck.md:42-45` is the round's only non-author defect source; the round-56 wave seats were author-dispatched (this wave's own dispatch context: "dispatched seats are lane-authors"), so no wave seat report is non-author. Verbatim:

```
- Resolve the MISSION.md vs prompt/config/SCORECARD axis-authority conflict through the operator/L0 channel; do not silently claim calibration in place of freshness.
- Strengthen C2-style calibration gates to bind actual executed battery entries and test SCORECARD/SHONEN disagreement; a roster literal/no-op harness must fail.
- Revisit S513's rejection rationale and record the disagreement as a lesson/quality criterion if retained; round-56 S513 is an outside discernment miss.
- Existing report audit records inherited append-only audit exit 1 and invalid `declared_at`/SCORECARD bindings; route for repair rather than treating the audit as clean.
```

Numbered D1-D4 below in that order. The closure's Conformance section also states the axis conflict is "a conformance defect, not a status downgrade"; that is the same finding as D1 and is not counted twice.

## Tree pin

The re-evaluation ran while peer seats committed; HEAD moved under the audit: `7c873d7b` (start) → `7b74e2f2` (repair landed) → `8640e34c` → `16efcf5e` → `77e7f5ee` (checks-time). Every check names the commit it read; the append-only JSON receipts carry their own `to` field. Current checker at `77e7f5ee`: `sha256=dee6f922d0d93b10512f9a799b94f36a1e0f080404a525e08121a223b2e90ced` (`tools/round56-prereg-check.py`).

## Status per routed defect

| Defect | Status at checks-time tree | Lesson-addressed in `corpus/lessons/round-57.md` |
|---|---|---|
| D1 axis authority | open, disclosed, not resolved | no |
| D2 executed-entry binding + SCORECARD/SHONEN | partial: literal no-op fixed; expanded no-op survives; SCORECARD/SHONEN half absent | partial (line 25, no-op row only) |
| D3 S513 rationale / discernment record | open | no |
| D4 append-only audit + declared_at bindings | open | no |

### D1 — MISSION.md vs prompt/config/SCORECARD axis authority

Exact current text (no operator/L0 resolution artifact exists in the lane):

```
$ sed -n '29p' /home/vgpnk/Projects/shokunin/MISSION.md
  kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }
$ sed -n '52p' /home/vgpnk/Projects/shokunin/shokunin.conf
kama|kama-shokunin|operability + calibration (local model serving and endpoint health)
$ awk 'NR==6' SCORECARD.md (first 400 bytes)
**Current authority (round 57):** the assigned axes are operability + calibration (`shokunin.conf` kama row; `MISSION.md:29` still says operability + freshness, an open L0 question since round 35).
```

Re-evaluation: unchanged conflict. The "do not silently claim" half is satisfied — SCORECARD names the conflict and the lessons at rounds 33/34/35 already record it as operator-side. The "resolve through operator/L0" half is not done and is outside lane write scope. Scope of the open item: one fleet-root line (`MISSION.md:29`) against one config row (`shokunin.conf:52`); no lane artifact can close it.

### D2 — executed battery entries and SCORECARD/SHONEN disagreement

Counter identity is exact: the frozen round-56 checker bytes at `b89bdab2` hash to `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, which is the `counter_sha256` written in `.ufo/waves/round-56/preregistration.json` for C2. The current file hashes to `dee6f922...` and its added block binds each declared roster member to an AST call site (`run(...)` / `assert_mutant_breaks_detection(...)` first argument).

Independently reconstructed fixtures (scratch repos; `git rev-parse --show-toplevel` asserted equal to each fixture dir before commit; roster literal copied from the committed battery at `b89bdab2`):

```
old checker (b89bdab2) vs literal-roster no-op:   present=1 roster_match=1 kills=1 controls=2 met=True   exit=0
new checker (HEAD)     vs literal-roster no-op:   present=1 roster_match=1 kills=1 controls=2 met=False  exit=1
new checker (HEAD)     vs unreachable-call no-op: present=1 roster_match=1 kills=1 controls=2 met=True   exit=0
new checker (HEAD)     vs genuine lane battery:   present=1 roster_match=1 kills=1 controls=2 met=True   exit=0
old checker (b89bdab2) vs genuine lane battery:   present=1 roster_match=1 kills=1 controls=2 met=True   exit=0
```

- First half (literal roster, `main(): return 0`, no calls): the routed defect's exact example now fails, `exit=1`. Fixed.
- Residual: the same no-op with the three `run("<label>", ...)` calls present but dead (`if False:` guard, `main` returns 0) still reads `met=True exit=0`. The binding is call-site presence in the AST, not execution. So "a roster literal/no-op harness must fail" holds for the literal-only harness and fails for an expanded no-op that keeps the labels. This is a scope limit of the fix, observed, not a claim that the fix is worthless.
- Second half ("test SCORECARD/SHONEN disagreement"): no instrument implements it. `grep -c SHONEN tools/round42-selfdesc-reconcile.py` → `0` (exit 1). Only `tools/round53-cited-path-check.py` and `tools/round54-cited-path-check.py` name SHONEN, and their frozen scope is that cited paths in SCORECARD/SHONEN/SKILL resolve (docstring: "surfaces SCORECARD.md, SHONEN.md, SKILL.md"), not that the two assessments agree or disagree.

Status: partial. Receipts: `receipts/precheck.txt`, `receipts/old-check-b89bdab2.py`, `receipts/new-check-HEAD.py`, `receipts/battery-noop.py`, `receipts/battery-unreachable.py`.

### D3 — S513 rejection rationale / outside discernment miss

Tree today still carries only the round-56 rejection rationale; the outside disagreement is recorded only in the closure lesson itself:

```
$ grep -n 'S513' corpus/SOURCES.md
266:| S513 | ld.so(8) — https://man7.org/linux/man-pages/man8/ld.so.8.html | ... | REJECTED: this broad loader manual overlaps the dedicated rtld-audit(7) source S512 for the claim's only need ... | rejected | 2026-10-27 | on-release | — |
$ grep -n 'S513 — REJECT' corpus/lessons/round-56.md
15:- **S513 — REJECT, tier A, rejected.** ... Rejected because this broad loader manual overlaps the dedicated `rtld-audit(7)` source for the only fact C1 needs. ...
$ grep -c S513 corpus/QUALITY.md            → 0 (exit 1)
$ grep -c S513 corpus/lessons/round-57.md   → 0 (exit 1)
```

Status: open. No lesson row or QUALITY criterion records the disagreement or narrows the rejection rationale. The closure's `disagree` entry (`corpus/lessons/round-56-verifier-spotcheck.md:30`) is the only record.

### D4 — append-only audit exit 1 and invalid declared_at bindings

Re-run at three tips with `python3 tools/append-only-audit.py --repo . --to <tip> --json`; every run exits 1 and reports `bad_declarations=4`:

```
tip 7b74e2f2: commits=386 files=108 events=127 restored=75 partial=0 unrestored=2 ungraded=45 disclosed=5 permitted_lines=60 disclosed_lines=10 bad_disclosures=0 ungraded_lines=228 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=4
tip 16efcf5e: commits=388 events=131 restored=75 unrestored=6 ungraded_lines=229 bad_declarations=4
tip 77e7f5ee: commits=389 events=131 restored=75 unrestored=6 ungraded_lines=229 bad_declarations=4
```

The two inherited unrestored events at `7b74e2f2` are `e81d90e6` and `4bd7521a` (both SCORECARD.md head rederivations), as the round-56 lesson records. The four extra unrestored events at `16efcf5e`/`77e7f5ee` are this round's own in-flight edits (`8640e34c` SCORECARD.md; `16efcf5e` LOG.md, SCORECARD.md, corpus/lessons/round-57.md) and are not inherited round-56 defects.

The invalid declarations are unchanged from round 56, and each pointer lands on a line that does not declare the file append-only:

| Contract row | declared_at | Line content at that pointer | Actual declaring line |
|---|---|---|---|
| SCORECARD.md, corpus/QUALITY.md, corpus/README.md | `corpus/README.md:761` | "context-capacity rows' scope already excludes." | 766-768 ("sets the five files the lane treats as / append-only (SCORECARD.md, LOG.md, corpus/QUALITY.md, corpus/README.md, corpus/SOURCES.md)") |
| corpus/lessons/*.md | `corpus/README.md:1239` | "Carried over unchanged and not re-measured here: the b11906 ledger population at" | 1246 ("Lesson files under `corpus/lessons/` are append-only as the `A-corr` contract row declares ...") |

Status: open. The defect's repair route is exactly these pointer re-anchors (plus restoring the two inherited SCORECARD events); no row or pointer changed since round 56.

## Reconstructed contract vs observed behavior

Round 56's non-author closure contracted four follow-ups for round 57: resolve axis authority at L0 (D1); make calibration gates bind executed work and catch SCORECARD/SHONEN drift (D2); record the S513 discernment disagreement (D3); repair the append-only bindings instead of treating the audit as clean (D4). Observed against the tree: D1 is still disclosed-open, D2 is half-implemented with a surviving expanded no-op and no SCORECARD/SHONEN instrument, D3 is untouched, D4 is untouched. The round-57 lesson addresses only the literal no-op half of D2 (row `no-op-counter`, `corpus/lessons/round-57.md:25`); the other three defects do not appear in it (`grep -n 'Round-56\|round-56' corpus/lessons/round-57.md` returns only that row, and `grep -c S513 ...` is 0).

So, against the seat requirement "round-56 outside defects must be lesson-addressed": 0 of 4 fully addressed; 1 of 4 partially (D2, first half only).

## Divergences (observed, not resolved)

**V1 — claim ordering and axis labels disagree inside the same pre-data freeze.** `controls/freeze.txt` says `claims=C1 calibration stale canonical-table count; C2 operability canonical-row execution binding`. `controls/freeze-amendment.txt` (committed `7c873d7b`) and `SCORECARD.md` §Round 57 and `corpus/lessons/round-57.md` say the reverse: C1 operability = `tools/round56-prereg-check.py` call-site binding; C2 calibration = `round42-selfdesc-reconcile.py` count. The wave dispatch context given to seats (`w1-dispatch.json` taskCall.context) still repeats the `freeze.txt` ordering, with predicates ("stale canonical capability row count ... expected 46") that no in-tree receipt supports. Both orderings call themselves frozen before seat evidence.

**V2 — the dispatch's `maxN=56` / `expected 46` sentence is not the frozen predicate.** `base-c1.out` reads `r41=1 ... caps=0 ... mismatches=1 maxN=56 met=False`, and its detail names only the calibration run line (expected `42`, observed `43`); the capability-row check `caps` is `0`. `maxN` is defined as the greatest `^## Round (\d+)` heading (`tools/round42-selfdesc-reconcile.py:13,167-168`), not a capability row count; the canonical list at `SCORECARD.md:2844` has 11 capability rows. `46` is not the base-tree target: it is the counter's own `maxN` at the round-46 measured receipts (`.ufo/waves/round-46/measured/r42-tip.out`: `mismatches=0 maxN=46 met=True`) and it is also the hard-coded print in `controls/c1-noop.py` and the `noop-c2.out` summary. At base the frozen counter prints `maxN=56` and the frozen mismatch is `mismatches=1` (calibration line 42 vs 43), not a `maxN` or capability-row target. Direct confirmation that `maxN` tracks headings: `.ufo/waves/round-57/measured/c2-committed-tip.out` at `16efcf5e` reports `mismatches=0 maxN=57 met=True` once the round-57 heading was appended.

**V3 — the binding is syntactic, not execution.** Detailed under D2; an `if False:` guarded call inventory satisfies the repaired counter (`met=True exit=0`).

**V4 — the freeze committed canonical-binding fixtures that no claim or receipt uses.** `.ufo/waves/round-57/controls/canonical-noop/` (SCORECARD/README/PROVINCE/SKILL copies) and `.ufo/waves/round-57/controls/no-canonical/SCORECARD.md` (canonical headings only through round 48) were added by `89dc4f52`, but `grep -rn 'canonical-noop\|no-canonical'` over `corpus/lessons/round-57.md`, `SCORECARD.md`, `LOG.md`, `controls/*.out` and `measured/*.out` returns nothing. The dispatch describes a "canonical-row execution/content binding" claim; the amendment replaced it, leaving these frozen fixtures orphaned. [INFERENCE] on intent; the reference-absence is observed.

## Scope boundaries

- Re-evaluated: the four non-author routed defects above, against lane content at `77e7f5ee`, plus the disabled/partial states of their round-57 remediation.
- Not re-audited: conformance of the fleet report `.ufo/reports/round-56/kama.md` (fleet path; lane write scope excludes it), the truth of round-56's author claims beyond what their receipts show, and the broader host-library/archive/git-config routes that round 56 explicitly left open.
- No shared file was edited; no tool was installed (nothing to record).

## Confidence

- D1, D3, D4: high — direct file lines and three successful audit runs with exact exits.
- D2: high for every executed fixture result and for the SHONEN-reference count; medium on whether the expanded no-op is in scope for the defect as authored ([INFERENCE]).
- V1, V2, V4: high on artifact contents; low on author intent, flagged where inferred.

## Receipts

`receipts/checks.txt` (all commands with exits), `receipts/precheck.txt` (fixture results), `receipts/append-only-summary.txt`, `receipts/append-audit-at-{7b74e2f2,16efcf5e,77e7f5ee}.json`, `receipts/old-check-b89bdab2.py`, `receipts/new-check-HEAD.py`, `receipts/battery-noop.py`, `receipts/battery-unreachable.py`.

Report: .ufo/waves/round-57/OutsideDefectAudit/38/evidence.md
