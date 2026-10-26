# K1Cheat — C1 shortcut attack

**Verdict: the frozen counter rejects isolated shape/selftest shortcuts, but accepts an implementation that merely copies its own recomputation and accepts hard-coded five-event output when paired with that copied implementation.** This exposes a bounded independence gap, not evidence that the lane's actual v3 auditor is incorrect.

Axes: calibration, measurement independence, fixture resistance.

## Evidence

Baseline on a shared scratch clone of the lane at `380bcdff9c8af06997c482f6eb03db926a794a2b`:

```text
python3 tools/round48-append-audit-v3-check.py --repo <clone> --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch <scratch>
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True
exit=0
```

Each attack below replaced only `tools/append-only-audit.py` in a fixture clone of that tip, committed with fixture identity, then ran the frozen counter with `--scratch`. Full first-line receipts and tips are copied beside this report.

| Attack | Counter receipt | Result / classification | Check to catch it |
|---|---|---|---|
| Shape-based fixture-name detector/playback | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` (tip `ee62626bbc6ee956c3420ea03deb5788aa45ad0f`) | **Shortcut.** It only checks for four familiar fixture filenames then delegates to copied behavior; the eleven fixtures share those names/conventions, so the gate cannot establish generalization. | Randomized fixture filenames, paths, declarations, row order, and unrelated decoy files; include novel generated cases and ensure tool output follows actual contract/history rather than fixture shape. Current frozen fixture leg checks fixed examples (counter lines 500–623). |
| Recompute/row-binding code copied under another name | same `met=True` receipt (tip `afbf7db1e0b0bf88383a0a49a7a6a3c07c5988da`) | **Shortcut / duplicate authority.** Reproduces the counter's own semantics rather than independently implementing the v3 audit. The counter's docstring explicitly limits independence: lane equality is against its own recomputation (counter lines 24, 258–389). | Not distinguishable by the lane-equality leg. Require independent oracle/evidence (e.g. externally generated expected output for lane history plus mutation/metamorphic tests) or disclose this limitation; do not treat copied recomputation as independent confirmation. |
| `--selftest` prints `AOA_SELFTEST pass=27 fail=0` only | `selftest=1 contract=0 lane=0 fixture=0 stable=0 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=0 fixture_fail=11 met=False` (tip `a6339b9e053dd91f8efce40a43eecce2a4f4abd1`) | **Shortcut rejected.** It cannot serve contract JSON, fixture outcomes, or stable runs. | Existing contract, lane, fixture and stable legs already catch it; selftest leg alone is intentionally just output/exit/threshold validation (counter lines 654–663). |
| Hard-coded five lane events, reused on every invocation | `selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True` (tip `7d704a060e3f1c701970e4778f683b6ee463b10e`) | **Shortcut accepted.** The output captured from this lane tip passes lane equality; stable compares the frozen base's events across base/tip but does not prove the tool actually recomputes arbitrary histories. It was paired with the copied implementation's fixture/selftest behavior, while its lane JSON was a fixed observed snapshot. | Run lane leg against a fresh adversarial history that adds/removes/reorders commits and alters append-only files; require output to respond to the supplied `--to` and contract. Could also mutate historical event content while preserving fixture shapes. |

Counter evidence: `diff_result` compares the lane tool JSON against `recompute()` (`round48-append-audit-v3-check.py:408–436`); fixtures compare only eleven predefined expected scenarios (`:500–623`); stable only checks base events in tool outputs (`:737–759`). Thus correct challenge performance on those fixed examples is not proof of independent or generalized auditing. The copied recompute and hard-coded event snapshot both obtain `met=True`; this is a fixable measurement limitation. The literal echo alone does not pass.

No tooling installed or updated. Scratch clones and generated driver remained under `/fast/scratch/hyaku/kama-r48/K1Cheat`; the required receipts are included in the output directory.
