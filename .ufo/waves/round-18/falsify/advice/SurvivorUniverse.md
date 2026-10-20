VERDICT: partial — denominators stay separate and inconclusive/site-failure items are counted, but named survivor MutFaultControlsSelf (b) is silently dropped from the universe and per-item outcomes are popped on any own fault.

Seat: `KamaR18.SurvivorUniverse` (critic, leaf). Attacked the C2 counting command
`.ufo/waves/round-18/c2/survivors.py` and its artifacts at pushed lane
`1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, in clone `/tmp/kama-r18-falsify-SurvivorUniverse`
(branch `seat/SurvivorUniverse`). Advisory evidence for L1, not admission. Scoped
to: named round-17 universe vs fresh wave-2 denominators; survived/equivalent/
site_missing/inconclusive visibility; frozen witnesses and prior kills retained.

# Finding 1 (main counterexample): MutFaultControlsSelf (b) is the one named detector-self item silently absent

`MutFaultControlsSelf.md:22-25` names four detector-self mutants (a)–(d). The
counter's family b carries only three — FC-target (a), FC-f6cache (c), FC-f0gate
(d) at `survivors.py:265-279`, FAMILY_TITLES at `:191`, `MUTANTS["b"]`. The
calibration ledger (`corpus/lessons/round-18.md:128-131`) maps exactly those
three. Mutant **(b) "any nonzero exit counts"** (`MutFaultControlsSelf.md:50-70`)
appears nowhere in `survivors.py`, the ledger, or `FROZEN_EXPECTED` (`:203-212`).

It is not a kill "already retained": its round-17 kill was produced only by an
*external* comparison of the frozen detector against the round-17 check.py
(5/3→6/2 accepted flip). Under survivors.py's own protocol — mutants staged
against **current** check.py — mutant (b) is `before: survived` (frozen baseline
on current check.py is already 17/0, decision identical), i.e. it satisfies the
universe definition of a named weakening the frozen detector cannot see. So
`named: b → 3` should arguably be 4 and `counts.named.total` 16, not 15.

Experiment (bounded, clone only, no listener opened — selftest uses port 0 and
stub check.py scripts):

```python
src = Path("tests/probe-verdicts/fault-controls.py").read_text()
old = '    positive = bool(fault.get("positive"))\n    target = fault.get("target")\n'
new = ('    positive = bool(fault.get("positive"))\n'
       '    if not positive:\n'
       '        return exit_code != 0, f"check exited {exit_code}; any nonzero exit counts"\n'
       '    target = fault.get("target")\n')
# src.count(old) == 1; mutant written to /tmp scratch
```

- `python3 tests/probe-verdicts/fault-controls.py --selftest --matrix-dir tests/probe-verdicts` → exit 0 (`passed: true`)
- `python3 /tmp/kama-r18-su-exp/fault-controls-b.py --selftest --matrix-dir ...` → exit 1, `passed: false`, problems include `classifier: target-conjunct attribution: reason fault failed on verdict only: got True, want False` plus 11+ sibling classifier cases.

So the current detector *would* kill (b) — the counter simply never measures it.
If a future round regresses that classifier coverage, nothing in this counter
(or its frozen-witness table, which expects only survived/miscount/accepted
rows) notices: the prior kill is not retained anywhere. Same class, lower
severity: `MutAppendOnlyGuard.md`'s killed mutants M1/M2/M3c/M4a are likewise
absent (defensible as "not survivors", but undocumented), and the n/a mutants
H4 (`MutC1Preregistered.md`) and H8 (`MutC1Preregistered2.md`) are excluded from
the denominator without a named exclusion in the round-18 ledger — precedent
says n/a items should stay visible as excluded, not vanish.

Impacted axes: calibration, provenance. Smallest safe correction: add
FC-nonzero (b) as a family-b item with `FROZEN_EXPECTED["b"]["FC-nonzero"]
= "survived"` (its expected before-outcome under this protocol) and a
`SELFTEST_TARGETS` entry naming the classifier attribution case; or record an
explicit named exclusion with rationale in the lesson ledger.
# Finding 2: own fault pops every measured item outcome

`survivors.py:1582-1585`: on any entry in `doc["own_faults"]`,
`doc.pop("results")` and `doc.pop("counts")` run. One family's invalid baseline
or unreadable input discards the *already measured* per-item before/after
outcomes of all other families from the output document (run records at `:1579`
survive, but per-item classifications do not). This directly contradicts the
claim "survived/equivalent/site_missing remain visible": a conclusive survivor
measured in family a is erased from the emitted JSON when family e own-faults.
Run validity stays 2 — correct — but visibility is destroyed rather than
preserved. Correction: keep `results`/`counts` and set `exit` 2; own faults are
already itemized in `own_faults`.

# Finding 3 (minor): fresh-wave-2 marker is a hardcoded stub, not a check

`survivors.py:1541-1544` emits `named_universe` and
`fresh_wave2: {included: false, mutants: 0, reason: ...}` unconditionally —
including under `--family a` (subset) and hypothetically even if a wave-2
mutant were later appended to `MUTANTS`. The separation claim holds today
(MUTANTS contains exactly the 15 named items; verified `results` ids =
{H1,H2,H3,H5,H6,H7,FC-target,FC-f6cache,FC-f0gate,AO-opened,AO-blank,
refused-count,nested-json,bigint,escaped-sleep}, `counts.named.total` = 15 in
`runs/c2-survivors.json`). The wave-2 side now has its own denominator
artifact: peer `KamaR18.FreshControls` reports
falsify/advice/FreshControls.md with 4 fresh mutants (FCN+FCF survived,
FCT+FCM killed by intended selftest assertions), explicitly not merged into
the named set — corroborating the separation claim. The stub itself is
still uncomputed; the label should either derive from the table or move to
schema docs.

# What checks out (no kill)

- `site_missing`/`site_ambiguous`/`stillborn` are produced by `apply_edit`
  (`:363-382`), carried into items (`:1141-1144, 1190-1192, 1254-1256`), counted
  as not-GOOD (`count()` `:1430-1449`) and forced exit ≥1 — never skipped.
  `selftest_pure` covers each status (`:1655-1661`). No "equivalent" status
  exists; `mutated != text` is asserted in selftest (`:1684-1688`).
- Inconclusive is a verdict class, never a kill: `classify_a` `:892-893`,
  `selftest_arm` `:933-936`, `main_arm` `:965-966`; `counts["inconclusive"]`
  `:1444-1448` and `inconclusive_reasons` `:1591-1601` keep items visible with
  before/after. The measured run recorded FC-target/FC-f6cache
  `after: inconclusive` with both arm whys retained.
- Frozen witnesses: frozen bytes are pinned against `frozen/SHA256SUMS`
  (`ctx.tool` `:737-743`), round-17 evidence files sha256-pinned (`EVIDENCE`
  `:170-177`), `frozen_witness_validation` (`:1450-1464`) compares
  before-outcomes to published values; the run shows 15/15 `matches: true`,
  `frozen_witness_mismatches: []`.
- `combine_arms` repair at tip vs measured `c6dc46f` is faithful to the
  docstring kill spec ("selftest exits non-zero where unmutated exits 0") and
  retains measured arms verbatim (raw `runs/c2-survivors.json` unchanged at
  measured revision, tool sha `2af03fed…` recorded inside it). The new
  killed-dominant rule is defensible: a targeted selftest kill is independently
  conclusive; main-arm exit 2 is a tool own-fault, not counter-evidence.
- Official command honesty: `runs/commands.json` `c2-survivors` records
  `expected_exit: 0, exit: 2, as_expected: false` — the could-not-evaluate is
  not called pass.
- Baseline dominance: invalid baselines downgrade to inconclusive before any
  kill is credited (`classify_a` `:884-889`, `selftest_arm` `:931-932`,
  `main_arm` `:957-962`).

# Limits and housekeeping

Experiment source is embedded verbatim above (mutant-b staging snippet + two
selftest commands). No production/frozen/advice files were modified; all reads
and runs were inside the clone. `selftest` ran stub-only; `pgrep`/`ss -ltnpH`
after the run show no seat process or listener. Clone `/tmp/kama-r18-falsify-SurvivorUniverse`
and `/tmp/kama-r18-su-exp` removed after report write per contract; the two
JSON selftest outputs are quoted inline. Installs: none. Tooling directive:
no pacman/uv/npm changes were needed.
