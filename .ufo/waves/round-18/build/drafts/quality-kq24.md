# KQ24 — QUALITY.md append draft (ScribeQualityKQ24, 2026-10-20)

## Integration notes for L1 (NOT part of the append; delete before appending)

- Append target: `corpus/QUALITY.md`, after its last line. At access (master `e75cf680b53484a61709ee1b2787d8dbc6419f74`) the last line is the KQ22 row at line 123; KQ21 is line 122. Append-only; no existing line moves.
- ID check: no `KQ24` exists in `corpus/`, `tools/`, `tests/` or `registry/` at access. `KQ23` is being drafted this round by sibling `ScribeQualityKQ23-2` (`.ufo/waves/round-18/build/make_spec.py:247`). L1 appends KQ23 before KQ24, or renumbers. Not verified whether KQ23 lands.
- Heading: if KQ23 is appended under the same round-18 heading, do not add a second heading. The heading below is a proposal.
- Scope versus the C1 contract: the round-18 C1 contract allows `passed: null` only for `loading_envelope_graded` when no 503 was observed. This row is written generically ("a graded property") with that check named as its instance. L1 chooses: keep the generic form, or narrow the row to the one trigger.
- Exit code: the row requires "a documented exit code distinct from pass and from fail" and fixes no number. Three numbers are already in the lane:
  - exit 4 is could-not-evaluate in the round-13 runner (`.ufo/waves/round-13/measure.py:474-477`; `corpus/lessons/round-17.md:131-133`);
  - exit 2 is the live tool's setup-error code, and its docstring lists only 0, 1 and 2 (`tools/kama-llamacpp-live.py:16-19`);
  - exit 3 is the live tool's digest-mismatch refusal (`tools/kama-llamacpp-live.py:954`, `:1023`).
  L1 must pick the live tool's number. Exit 2 would share the setup-error class unless the receipt reason separates them.
- Gate and tool gaps (not fixed by this draft; C1 owns them): `tests/llamacpp-live/check-receipt.py:647-649` rejects a non-boolean `passed` and accepts only `is not True`. `tools/kama-llamacpp-live.py:1240` is `exit_code = 0 if all(c['passed'] for c in checks) else 1`, so a null check exits 1 today.
- Pointer resolution: `lessons/round-17-verifier-spotcheck.md` is `corpus/lessons/round-17-verifier-spotcheck.md`, and R4 is at its lines 234-235.

## Criteria added — round 18 (2026-10-20, author-appended; no outside review yet)

No earlier criterion is superseded. KQ21 (a live-run check counts as subject evidence only when a retained control flips it) remains in force unchanged. KQ24 does not change when a check counts as subject evidence; it fixes the outcome of a check whose triggering state was not observed in a run, which KQ21's "unobserved state passes vacuously" reject does not cover. KQ17 (a could-not-evaluate finding does not erase a verified count) and KQ19 remain in force. KQ11 (controls must fail before a repair counts) governs the control requirement in KQ24.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ24 | A graded property (a check, verdict or grade that a run writes as pass or fail) names in its `documented_by` the triggering state it grades. When the run's own record does not show that the trigger was observed, the property is not graded as pass or as fail: its outcome is recorded as not-evaluated (a null in place of a boolean, with a reason that names the missing observation, e.g. `no-loading-503-observed`), and the run's outcome is could-not-evaluate with a documented exit code distinct from pass and from fail. A not-evaluated run counts neither for nor against any subject claim. The rule is shown by a retained healthy-subject control that never exhibits the trigger, which must classify as not-evaluated through the real tool and gate; and by mutants that map the not-evaluated outcome to fail or to pass, each killed by a control. | A trigger that was observed and then failed is recorded as not-evaluated (a red run relabelled as unevaluated). An unobserved trigger is recorded as fail: a healthy b11755 server failed `loading_envelope_graded` with `loading_observed` false in 1 of 60 loaded runs and exited 1 / gate INVALID (round-17 LiveUnderLoad). A not-evaluated run is cited as evidence that the state never occurred; "not observed" is never written as "did not occur". A not-evaluated run is replaced by a pass or fail from a later run that is not itself recorded. | `lessons/round-17-verifier-spotcheck.md` R4 (lines 234-235); `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md` lines 41-44 and 141-144; precedent `lessons/round-17.md` lines 131-133 (round-13 R1 to exit 4). |

Grounding for the rule: `corpus/QUALITY.md:5` — "new rows; supersession names the old criterion instead of erasing it." The round-13 precedent already separates this case: "content failures stay exit 1" (`corpus/lessons/round-17.md:133`) and a divergence that cannot be graded is exit 4.

## Unknowns (state, do not append)

- The number of the live tool's could-not-evaluate exit (2, 4, or a new code): unknown; L1 decides. Not measured here.
- Whether a retry before not-evaluated is admitted. `LiveUnderLoad.md:145-146` suggests a retry; the row admits none, because a retried pass is a different run. Unknown whether retries would change the observed rate.
- Whether the not-evaluated outcome is per check (C1 contract) or per run. The row says both; the gate must pick one.
- Zero-observation rate in production or under other loads: measured only as 1 of 60 at `cpu1024b` (`LiveUnderLoad.md:41-44`) and 0 of 20+3 idle (`corpus/lessons/round-17.md:252-253`). Not measured here.
- The round-17 `cpu1024b-1` receipt is not in the lane; `LiveUnderLoad.md` says its scratch was removed. The "shown able to fail" control for KQ24 therefore cannot be the historical receipt. [INFERENCE] a fake server that never serves a 503 tests the classification, not the scheduling race; the race is not deterministically reproducible (`LiveUnderLoad.md:134-136`).
- Whether `documented_by`'s claim "a real b11755 run shows dozens" (`tools/kama-llamacpp-live.py:141-142`) is accurate: `LiveUnderLoad.md:42` reports "23 of the 59 passing runs captured exactly one". Unknown for production load; the premise is not used by KQ24.
