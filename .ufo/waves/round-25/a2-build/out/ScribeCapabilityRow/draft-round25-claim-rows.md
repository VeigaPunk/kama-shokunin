# Draft — round-25 SCORECARD claim rows (C1 and C2)

Round 25, attempt 2. Author: `ScribeCapabilityRow` (scribe seat). Draft for
the L1 to paste into a round-25 section, after filling the placeholders from
committed bytes. Style follows the round-18/20 measured-results tables
(`| Claim | Axis / score | Before → after | Counting command | Evidence |`)
plus a measured-commit column; round-23 per-component style is offered below
as an optional C1 split.

## Measured now (2026-10-22, by this scribe)

- Sandbox clone at the lane tip
  `1fc41e346853afd98cbd7010af5db4e54dc877f7`:
  `/fast/scratch/hyaku/kama-r25a2/ScribeCapabilityRow/clone`.
- C1 registered counting command (preregistration.json `C1.command`, verbatim),
  exit 0:

  ```
  registered 28 stale 0 []
  ```

- C2 counter at the tip with no receipt present, exit 2 (stderr):
  `cannot read receipt: [Errno 2] No such file or directory: '.ufo/waves/round-25/final/context-capacity-receipt.json'`

## Main table

| Claim | Axis / score delta | Before → after | Counting command | Measured commit | Evidence |
|---|---|---|---|---|---|
| C1 — repair-first calibration: re-anchor the stale registered mutation anchors (M11, M17) and register the second M17 call site as M33 | calibration 7 → 7, delta 0 (no numeric promotion) | `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` at efe58e96 (amendment-2 author, before the re-anchor edit) → `registered 28 stale 0 []` at 1fc41e3 (measured by ScribeCapabilityRow, exit 0). Denominator 27 → 28 reported as measured; no id reused or retired | `python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"` | 1fc41e346853afd98cbd7010af5db4e54dc877f7 | [mutants.json receipt path]; supporting evidence not the claim value: one full `python3 tests/report-audit/isolation-mutants.py --json` run, exit code and killed/surviving list recorded as observed |
| C2 — learning claim, frontier K05: declared versus served context capacity | coverage 8 → 8, delta 0 (no numeric promotion; ground grows by one knowledge entry and one capability row) | receipt absent at efe58e96: `count-c2.py` exit 2 `cannot read receipt`; targeted after: `registered 14 observed 14 bound True missing []` | `python3 .ufo/waves/round-25/count-c2.py` | [measured commit] | `receipt path` (counter default: `.ufo/waves/round-25/final/context-capacity-receipt.json`). Prediction matches are calibration evidence only; the claim value is the observed count |

## Optional C1 component split (round-23 style)

| C1 component | Before → after | Counting command | Evidence |
|---|---|---|---|
| Registered anchors (MUTANTS entries whose literal does not occur exactly once in `tools/report-landing-audit.py`) | `registered 27 stale 2` at efe58e96 → `registered 28 stale 0 []` at 1fc41e3 | same command as above | [mutants.json receipt path] |
| Full isolation run (supporting evidence, not the claim value) | before: registered command aborted exit 2 before any mutant ran → after: one full run, exit code and killed/surviving list recorded | `python3 tests/report-audit/isolation-mutants.py --json` | [mutants.json receipt path] |

## Binding non-narrowing rules (from preregistration.json C1, must be kept in the section)

- M11 and M17 keep weakening the same element they weakened at round 23; a
  re-anchor targeting a different element is a miss.
- An id may move to RETIRED only if a revenger proves its element is gone,
  with attribution to the mutant that now carries the check.
- If the element now lives at two call sites (M17), both stay covered.
- The denominator at the landed tip is reported as measured; ids are never reused.
