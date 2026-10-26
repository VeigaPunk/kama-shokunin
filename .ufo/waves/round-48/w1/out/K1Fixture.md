# K1Fixture — Round 48 C1 fixture-leg power attack (item K1Fixture)

**Verdict:** the C1 fixture leg (scenarios S1–S11) leaves **five v3 definition clauses unexercised** —
exempt-title exact match, per-file multi-row region union, binary-change handling, malformed-region
rejection, and unmatched-pattern exit neutrality — and a tool that is wrong **only** in any one of them
passes the *entire* counter (all four legs, `met=True`), including the lane and selftest legs. All other
clauses are exercised by at least one leg (fixtures and/or selftest and/or lane). 11 variants were built
and run; 5 escaped, 6 were caught (each by identifiable legs).

## Method

- Baseline: `python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S` on a `git clone --shared` of the lane → `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` (exit 0) — matches the L1 pre-wave dry run. Canonical lane events (tool JSON, `lane-json.txt`): 5 events, all `restored`, `held_at_to == restored_max`, `binary=0`, `unmatched=0`, `vanished=0`.
- Sum variant: fresh `git clone --shared` of the lane, `git checkout -q -b var 380bcdff…`, replace `tools/append-only-audit.py` with the patched source (asserted `rev-parse --show-toplevel` == clone dir before the commit), commit with a fixture identity, run the frozen counter with `--tip $(rev-parse HEAD)`.
- All receipts: `.ufo/waves/round-48/w1/out/K1Fixture/receipt_*.txt`; variant sources `*.py` in the same dir; counter canonical tool source extracted from `380bcdff…` (`aoa-canonical.py`, ev photos here).

## v3 definition clauses vs exercise coverage

Clause (definition, counter docstring lines 43–65 / `round48-append-audit-v3-check.py`) | Exercised by scenario (S1–S11) | Also exercised by selftest | On the lane (380bcdff…)
---|---|---|---
Threshold |20 deleted → event, 19 none| S1 (exact both sides) | t_below, t_exact_unrestored, t_threshold_flag | yes (5 events)
Commit walk: topo-order reverse, first parent, root has no event | S7 (merge-first-parent; every fixture root) | t_merge_first_parent | yes
Lines: split on `b"\n"`, final non-empty segment; byte-exact | S9 (CRLF, `--`, EOF) | t_crlf_and_eof, t_final_segment, t_crlf_restore_exact | yes
Deleted = `-U0` hunk positions, == numstat | S9 (`--` lines; hunk count) | t_dashdash | yes
**Binary change skipped** | — | t_vanished_and_paths (reporting only) | none (binary=0)
Section: title of last `## ` at/before; None before first; `\r`/trailing-blank strip | S2–S5 (multiple sections, None-before-first) | t_exempt_*, t_only_errata | yes
**Exempt-title exact equality** (vs prefix/contains) | S2/S3 (only exact titles exist) | t_exempt_* (exact titles) | none (verified: 61 distinct `## ` titles in SCORECARD.md history, zero prefix-extensions of the five heads)
Eligibility: window-max count(T,x) ≥ count(T,parent) | S2 (rewritten), S3 (gutted) | t_exempt_gutted_then_regrown (regrown later) | yes
Graded `*` (all deleted) | S1,S6,S7,S8,S9,S11 | many | yes
Graded exempt (skip lines in eligible exempt section) | S2,S3,S4 | t_exempt_rewritten/gutted/dated | yes
Graded only (keep only prefix-matching sections) | S5 | t_only_errata | yes (row exists; no events today)
**Multi-row region union per file** | — | — | no (each lane file matches ≤1 row)
Ungraded = |D|−|G| | S2,S5,all | all | yes
Held multiset: min(G[l], max(0, M_x[l]−K[l])) | S6 (clamp bites at c2), S8 | t_clamp, t_multiset, t_dup_kept_not_restored | yes
Window [event..tip] includes the event commit | — (tip endpoint via S8) | t_relocation (restored_by==event), t_partial | yes
restored_max / restored_best (first attainer, null when 0) | S6,S8,S11,S2 | t_restored, t_partial, t_exact_unrestored | yes
restored_by (first h==|G|, null if never) | S6 (None), S8/S11 | t_restored, t_exact_unrestored | yes
held_at_to | S8 (15) | t_window_max (20) | yes
status: ungraded/restored/unrestored/partial | S2/S5, S8/S11, S1/S3/S4/S5/S7/S9, S6 | all | yes
regressed (restored/partial and held<max → exit 1) | S8 | t_window_max | yes
Exit terms: partial, unrestored, regressed, vanished, bad declarations | S1,S3,S4,S5,S6,S7,S8,S9,S10,S11 | many | yes
Vanished detection → exit | — | t_vanished_and_paths | none (vanished=0)
**Unmatched patterns informational, never in exit** | — | t_vanished_and_paths (list only) | none (unmatched=0)
Declaration binding: phrase (`append-only`/`append only`), no negation, self-match or token | S10 (no phrase, negation); token positive via every ROW_* | t_contract, t_bad_declarations | yes (all 9 rows)
Exempt pointer: `re-derived` + every title | S10 (unnamed title) | t_bad_declarations, t_exempt_* | yes (SCORECARD row)
Only pointer: binds + prefix text | ROW_KNOW (positive only) | t_only_errata | yes (consumer-registry row)
Contract grammar: header, 5 cells, region forms | (fixture contracts all valid) | t_contract (4-cell/malformed region) | yes (strict parse in counter)
Wildcard token (parent-dir name) | — | t_contract (glob row binds via token) | yes (corpus/lessons/*.md)

## Variants: does any leg still catch a tool wrong only there?

Variant (one clause broken; diff vs canonical) | selftest leg | contract leg | lane leg | fixture leg | stable leg | Counter result
---|---|---|---|---|---|---
va — exempt-title match by `startswith` (line 417) | pass | pass | pass | pass | pass | **met=True — ESCAPED**
vb — regions from last matching row only (`file_regions`, line 350) | pass | pass | pass | pass | pass | **met=True — ESCAPED**
vf — binary change becomes a phantom event (line 393) | pass | pass | pass | pass | pass | **met=True — ESCAPED**
vi — empty region cell accepted as `*` (line 141) | pass | pass | pass | pass | pass | **met=True — ESCAPED**
vl — unmatched patterns enter the exit code (line 474) | pass | pass | pass | pass | pass | **met=True — ESCAPED**
vc — window excludes the event commit (line 404) | fail (4) | pass | fail (restored_best/by) | fail (3) | pass | met=False
vd — eligibility at the event commit, not window max (line 409) | fail (1) | pass | fail | pass | pass | met=False
ve — vanished never detected (line 377) | fail (1) | pass | pass | pass | pass | met=False
vg — regressed non-strict `<=` (line 442) | fail (2) | pass | fail | fail (S11) | pass | met=False
vh — only-pointer must also say `re-derived` (line 226) | pass | fail (tool decls) | fail | pass | pass | met=False
vj — held computed over D not G (line 424) | pass | pass | fail | pass | pass | met=False

Takeaways on leg complementarity: the selftest is the only catcher for `ve` (vanished) and one of two for `vd`/`vc`; the lane leg alone catches `vj` (held-over-G is fixed only by the real SCORECARD events, which carry ungraded lines); the contract leg alone catches `vh`; the fixture leg is the sole catcher of the exact-threshold/clean/regressed-boundary shapes but misses every variant above.

## Findings (escaped clauses)

Each variant is demonstrated wrong against the canonical definition on a bespoke repo (expectations by
construction) in `demos.log` (script `demos.py`).

1. **Exempt-title matching is prefix-tolerant (`va`).** `tools/append-only-audit.py:417` uses `if s in eligible:`. A `startswith` variant treats e.g. `## Axesomething` as an exempt title. Demo A: deleting 21 lines of `## Axesomething` → canonical `graded=21`/`unrestored`/exit 1; variant `ungraded=21`/exit 0. Lane verification: no near-miss title exists in SCORECARD.md history (61 distinct `## ` titles, zero prefix-extensions of the five heads), so the lane leg cannot tell. Fix: keep exact `in` matching (it is the definition: “section titled exactly Ti”).
2. **Per-file multi-row region union is untested (`vb`).** Definition: “a file matched by several rows takes the union of their exempt titles and only prefixes”. `file_regions` (line 350) accumulates; a last-row-only variant drops earlier rows. Demo B: two exempt rows `Axes|Plan` + `Axes`, 21 `## Plan` lines deleted then regrown later in the window → canonical `ungraded=22`/exit 0; variant `graded=22`/`restored`/max 22. No fixture, selftest case, or lane file matches >1 row (lane patterns are disjoint), so nothing exercises the union. Fix: add a fixture/contract case with two rows matching one file (e.g., two exempt rows with different titles, or two only rows).
3. **Binary changes can silently become events (`vf`).** Definition: a binary change is skipped (numstat `-`). Variant emits a phantom event (`deleted=0`, `ungraded`) per binary change. Demo C: binary edit to `bin.bin` → canonical `events=0`; variant `events=1`. The selftest asserts only the reporting list (`binary_changes==2`), not the absence of events; the lane has no binary file (canonical summary `binary=0`), so a future binary file would expose the divergence, but today it is invisible. Fix: assert no events on binary changes in selftest `t_vanished_and_paths` (and/or add a fixture).
4. **A malformed empty region cell is silently accepted (`vi`).** Definition: region must be `*`, `exempt=…@p:n` or `only=…@p:n`; otherwise exit 2. Variant accepts an empty cell as `*` (`parse_region` line 141). Demo D: contract row with empty region cell → canonical exit 2 (“could-not-evaluate”); variant audits and exits 1. The counter's own strict `parse_contract` would reject such a contract on the lane (contract leg), so this is latent; but nothing exercises a malformed *empty-cell* region (selftest bad-contract list has 4-cell and malformed-region strings only). Fix: add the empty-cell string to selftest `t_contract`'s malformed list.
5. **Unmatched patterns are not exit-relevant, but nothing proves it (`vl`).** Definition (tool docstring): `unmatched_patterns` is informational; exit terms are partial/unrestored/regressed/vanished/bad declarations. Variant adds `or s["unmatched"]` to `exit_code` (line 474). Demo E: clean repo + unmatched `nope/*.md` → canonical exit 0; variant exit 1. Lane has `unmatched=0`, so invisible. Fix: add a selftest/clean-fixture assertion that an unmatched pattern alone keeps exit 0.

Notes: `vc`–`vj` show the remaining clauses are guarded (wc by selftest crash + lane + fixtures; vd by selftest + lane; ve by selftest alone; vg by selftest + S11 + lane; vh by the contract/lane leg; vj by the lane leg alone). No tools were installed (existing python3/git used; no pacman/uv/network installs). No lane or fleet files were modified; all clones live under scratch and were removed (see cleanup below).

## Evidence files

- `receipt_*.txt` — frozen-counter receipts: baseline + one per variant (11).
- `va_startswith_title.py … vl_exit_on_unmatched.py` — the 11 variant sources (patch anchors annotated in `mkvariants.py` / `mkvariants2.py`).
- `demos.log` / `demos.py` — canonical-vs-variant divergence demos A–E.
- `lane-json.txt` — canonical tool JSON at 380bcdff… (5 events, binary=0, unmatched=0, vanished=0).
- `base.c1.out` — baseline counter receipt.
