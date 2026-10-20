# KQ21 — QUALITY.md append draft (ScribeQualityKQ21, 2026-10-20)

## Integration notes for L1 (NOT part of the append; delete before appending)

- Append target: `corpus/QUALITY.md`, after its last line (line 109 at access, the KQ19 row). Append-only; no existing line moves.
- ID check: no `KQ20` or `KQ21` exists in `corpus/`, `tools/`, `tests/` or `registry/` at access (grep 2026-10-20). Roster shows a sibling seat `ScribeQualityKQ20-2` drafting KQ20; L1 must append KQ20 before KQ21 or renumber. Not verified: whether that sibling will land KQ20 in this round.
- Criteria are tiered by the existing lane convention: KQ19 is the probe-verdict form of this rule; KQ21 generalizes it to every live-run check in a receipt. KQ19 remains in force unchanged.
- Gate gap (not fixed by this draft): `tests/llamacpp-live/check-receipt.py:53-63` `REQUIRED_CHECKS` lists ten check IDs and no label field; grep for `input-integrity` / `harness-integrity` in `tests/llamacpp-live/check-receipt.py` and `tools/kama-llamacpp-live.py` returned zero matches on 2026-10-20. The labels in the row are therefore prose-only until L1 decides whether the receipt schema carries them (schema change is a decision for L1, not this draft).
- Pointer resolution: `lessons/round-16-verifier-spotcheck.md` lives at `corpus/lessons/`; `Routed defects` item 6 is at line 187.

## Criteria added — round 17 (2026-10-20, author-appended; no outside review yet)

No earlier criterion is superseded. KQ19 (probe verdict for a documented
not-ready state) and KQ4 (fixtures are not runtime integration) remain in
force. KQ21 governs every live-run check whose result is written into a live
receipt and counted toward a claim about a running subject. It adds no served
identity, readiness or lifecycle claim; KQ1 and KQ13 still govern identity and
readiness.

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ21 | A live-run check that grades a running subject (a check written into a live receipt and counted toward a claim about the server or its lifecycle) is admitted as subject evidence only when a recorded subject-behaviour control, a fake or real server exhibiting the misbehaviour the check names, makes that same check fail in the same harness, and the control and its failing result are retained with the round's counting command. Every check carries one label by what its failure can come from: `subject` (a control flips it), `input-integrity` (the bytes of an input, e.g. the GGUF hash), or `harness-integrity` (receipt, bookkeeping or teardown plumbing). Only `subject` checks count toward a subject claim; a check no control flips is labelled, never counted. A captured field that no check grades is observation-only and cannot support a PASS or VALID claim. An internal fault (exception in setup, readiness, teardown or the receipt write) still emits a receipt that records the fault as `setup_error` or a failed check and exits nonzero; admission needs an injected-fault control in which the fault produces that receipt. | A receipt or gate reads PASS/VALID when a control in which the subject misbehaves leaves the check green (e.g. `/health` 200 with `{"status":"degraded"}`; self-exit rc 0 with no signal sent; SIGKILL rc -9 after an ignored SIGTERM); a check labelled `subject` is one a well-behaved subject cannot fail (port closed after a reaped process; model hash unchanged absent external mutation); a recorded observation such as `loading_envelope_exact` is read by no check; an exception inside teardown escapes without a receipt. A control flips a check only for the misbehaviour it names: the admission does not extend to misbehaviour no control exercises. | `lessons/round-16-verifier-spotcheck.md` Routed defect 6 (line 187); round-16 `.ufo/waves/round-16/falsify/advice/ReviewLiveHarnessCode.md` H1 (loading envelope ungraded), H2 (`teardown_exited` proves reaping only), M1 (health body ignored), M2 (`teardown_port_closed` vacuous on failed runs), M3 (`model_unchanged` self-sentinel), M4 (teardown exception destroys receipt); KQ19's frozen-fail/repaired-pass pattern (`corpus/QUALITY.md:109`) generalized to live receipts. Round-17 C2 instantiates the rule with its fake-server control suite (`tests/llamacpp-live/controls.py`); the C2 receipt version and its predicates are L1's decision and are not fixed here. |

Grounding for the rule: `corpus/QUALITY.md:5` — "new rows; supersession names the old criterion instead of erasing it." The round-16 review's direct answer, `ReviewLiveHarnessCode.md:57-59`, states that `teardown_exited` and `model_unchanged` "cannot fail for any behavior of the subject"; its fault row (`:34`) records `ESCAPED KeyError KeyError('returncode')`, `receipt_written False`.

## Unknowns (state, do not append)

- Whether the round-17 C2 harness will supply a `subject`-labelled control for every live check it keeps: unknown until the C2 build and controls run; not measured here.
- Whether the gate should reject receipts that carry no label: unknown; the schema has no label field today (see integration notes).
- Whether a fake server is acceptable as the control for a llama.cpp-scoped claim: this draft admits a fake server as a subject-behaviour fixture, because the round-16 review found no harness fault that needs a real build to flip; a real-build control would be stronger, and whether L1 requires one is a decision [INFERENCE].
- Whether `ReviewLiveHarnessCode.md`'s "fake server is not llama.cpp" limit (`:157-158`) is closed by any round-17 control: unknown; not checked here.
- Whether the llama.cpp `/health` body and the signal/shutdown path cited by C2 match the labels above: not opened by this scribe; no llama.cpp source is quoted in this draft.
