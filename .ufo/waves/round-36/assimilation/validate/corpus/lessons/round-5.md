# Actual round 5 — reconcile the interrupted current endpoint runbook

2026-10-15. Axis: freshness, the lower assigned LIVE axis in the inherited
SCORECARD (freshness 7, operability 8; those numbers are author assessments).
Start revision: `c390918f8f6d5d1b52787e4720c8642377fdcb8c` with inherited dirty
lane work. Plan: `plans/wwkd-round-5-interactive-freshness.md`. LOG entry:
`LOG.md` §Actual round 5 — interactive cutover and dispatch blocker.

This is a **blocked round attempt**, not an admitted or verified completed
round. The historical reports for rounds 1, 2 and 4 are preserved; round 3's
missing report stays named debt. The stopped headless launch counter 1 and
its inherited `round-1` relaunch prose do not reset the lane history or prove
an additional round. No historical report, corpus record, or native session
was overwritten.

## Gate

### Candidates and admitted evidence

1. **Admit the current registered-endpoint sample**, not a healthy-runtime
   promise. `.ufo/round-5/before-check.json` records the real command, complete
   stdout/stderr, exit 2 and baseline revision. All three rows are
   `DEAD` / `connection-refused`. The two UFO pins are `file_match=yes`; the
   builtin default is `inherited` / `raw`, not an effective URL observation.
2. **Admit the runbook correction** as a measured local delta: the same four
   dependent summary fields had three mismatches before and zero after.
   `.ufo/round-5/acceptance.json` retains the two measurements and every
   executed command's complete streams and exit. This is documentation
   agreement with sampled state, not four independent tests or endpoint
   recovery. The SKILL checklist no longer promises a live September pid,
   unit, eleven-row registry, or MODEL_OK positive control.
3. **Admit bounded producer shape**, not a host-wide absence claim:
   `.ufo/round-5/host-shape.json` records
   `LoadState=not-found`, `ActiveState=inactive`, `SubState=dead`, `MainPID=0`,
   and the two-port `ss` query's header without listener rows. This establishes
   neither permanent retirement nor absence of every possible serving process.
4. **Retain September corpus bytes as dated history** and explicitly supersede
   current-readiness interpretations through this lesson, corpus index and
   SKILL state banner. Stronger active instructions distinguish pin correctness,
   endpoint identity, liveness and runtime selection. The inherited registry
   note-only corrections, province clarification and author-asserted SHONEN
   marks are preserved, not silently discarded.

### Rejected candidates

- Treating the two historical positive controls as a current probe invariant:
  correct pins coexist with dead endpoints. Rejected by the sampled gate.
- Restoring/enabling a model service, repointing external consumers, installing
  a timer, or contracting the province: operator-owned and not authorized.
- Adding context-size reconciliation: a separate schema/feature move, not
  necessary for this runbook correction; no live serving context is established.
- Claiming the builtin fallback is the consumer's effective URL or that its
  override is unset: no environment value was inspected.
- Treating a rendered wave as dispatched or the local delta as a complete
  training round: the required native routes are unavailable. No task call ran.
- Repeating the already reported native Phase 0/self-iter failure: outside this
  lane's authority; the fleet report is retained as the failure evidence.
- Fabricating a receipt task key or hashes from arbitrary local files: the
  interactive launch supplies no fleet task binding. A display envelope is not
  an applicable task receipt or fleet acceptance.

### Spot-check

Not performed. Required native audit routes are unavailable, and there is no
outside non-author admit/reject verifier. No promotion `[x]`, discernment
improvement, native judgment, saturation, or verified-round increment is claimed.

## Measurement and smoke

Exact before/after counting operation (capture the real probe exit separately):

```sh
bash tools/kama-probe.sh check --json
```

Parse the document's `summary` sample and the captured command's `summary`;
compare exactly `registry_rows_evaluated`, `model_ok`, `drift`, `exit`.
Reproducible Python comparison, with probe output held in a local JSON file:

```python
import json, pathlib, re
actual = json.loads(pathlib.Path('.ufo/round-5/acceptance.json').read_text())
actual = actual['summaryMeasurement']['after']['observed']
text = pathlib.Path('SKILL.md').read_text()
expected = json.loads(re.search(r'`summary` = `([^`]+)`', text).group(1))
print('fields_checked=%d mismatches=%d' % (
    len(expected), sum(actual[k] != value for k, value in expected.items())))
```

Observed candidate result: `fields_checked=4 mismatches=0`; baseline against
its real current probe was `fields_checked=4 mismatches=3`.
The comparison above replays retained evidence; rerun the actual command for
new current-state evidence. The delivered revision and per-file digests are
bound in `.ufo/round-5/landed-evidence.json` after the work commit.

Full verdict lines from `.ufo/round-5/acceptance.json`:

```text
registry_rows_evaluated=3 model_ok=0 drift=3 exit=2
consumer_rows_evaluated=3 exit=0
RESULT pass=24 fail=0
snapshot=20261015T051015Z prev=- rows=3 model_ok=0 drift=3 transitions=0 exit=2
snapshot=20261015T051015Z prev=20261015T051015Z rows=3 model_ok=0 drift=3 transitions=0 exit=2
```

`check` and `check --json`: exit 2 (drift). `consumers`: exit 0 (listing).
`bash -n tools/kama-probe.sh tools/test-snapshot.sh`: exit 0.
`bash tools/test-snapshot.sh`: exit 0, 24 passed / 0 failed.
Both isolated real snapshots exited 2; their TSV/ledger hashes were equal.
The temporary isolated history was removed after capture; its normalized
baseline and ledger bytes are retained in acceptance.json. The default tracked
history was not advanced. No UI surface or real vLLM/Ollama integration was
exercised.

## Dispatch and continuation debt

`.ufo/round-5/wave-spec.json` contains 32 distinct scoped reviews;
`wave-validation.json` records canonical validator exit 0;
`wave-plan.json` and `wave-payload.json` retain the canonical plan and pure
rendered payload. No `run` registry, native agent handle or subagent outcome
was invented. `.ufo/round-5/route-preflight.json` names the missing authorized
role→alias bindings; the validator's route-family check is unprobed and does
not enforce this operator-specific alias contract.

The operator/global route owner must bind content roles to `@m_composer`,
audit roles to `@m_grok`, and connector to `@m_antigravity` with the requested
`@m_zfl` fallback. This lane cannot change that configuration. The interactive
Sighting row has no taskKey, resultPath, receiptPath, promptSha256 or
configSha256 (top-level or dispatch binding); an applicable task receipt cannot
be minted truthfully from it. The fleet integrator must provide a real binding
before acceptance/continuation can be released. Do not mark the mission complete.

A fresh session remeasures after those prerequisites are repaired; it does not
restart round 1, repeat this landed correction as new progress, or loop to a
second round inside this TUI. The cumulative verified-round total remains
unestablished; this attempt adds zero. Historical source-line anchors remain
named debt: re-anchor only still-live references in a separate falsifiable
freshness move, preserving dated corpus bytes through explicit new corrections.
