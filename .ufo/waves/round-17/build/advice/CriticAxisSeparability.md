VERDICT: partial — C1 and C2 can be separated causally, but the axis labels currently rest on the wording, not on the counts. As drafted, an outside verifier can read C1's count as operability, which would merge C1 and C2 into one claim (AXES.md:31-33). Fixes are listed below.

Seat: KamaR17.CriticAxisSeparability-2 (critic, read-only). State attacked: lane tip `cff9e62` (`git rev-parse master`). The round-17 build-wave artifacts have not landed yet: `c1/` and `c2/` are empty, and `check.py`, `kama-llamacpp-live.py` and `check-receipt.py` still match their frozen sha256 values (`b853576e…`, `b8c5e8d4…`, `6b9576a1…`). So I attacked the declared claim structure and the build spec in `.ufo/waves/round-17/build/spec.json`. No built code existed to attack.

## Axes named
- **calibration** (C1, the lowest axis, 7)
- **operability** (C2, 8, at the saturation line)
- **separability** and **distinct-axis rules** (AXES.md:31-33)
- **lowest-axis rule** (AXES.md:33-34)
- **capability-row discipline** (AXES.md:62-64)
- **no-harm** on calibration from the C1 headline and the C2 DOC/capability wording

## Rules applied (protocol text)
- `AXES.md:31-33`: "Claims must be **causally separable** — each verifiable without the others having landed — and name **distinct axes**; two claims on one axis in one round count as one claim."
- `AXES.md:13`, operability: "A checklist item can be run and produces the stated outcome".
- `AXES.md:15`, calibration: "Self-assessment quality: gaps named honestly, confidence graded, overreach caught".
- `AXES.md:40-41`: a capability acquisition "still lands a per-axis verdict". A capability row is one claim type. It is not required for an axis move.
- `LEARNING.md:84-86`: "quality by `depth`, `freshness` and `operability`; discernment by `calibration`".

## Findings

### F1 — Causal separability holds, on one condition (separability: confirm)
- **C1 measure.** It runs on stubs and wrapper probes only. `C1MutantRunner` detectors run a mutated `check.py` with `--probe` set to the round-16 frozen probe or the current probe (spec item `C1MutantRunner`, "`pair` = run the mutated check.py … with `--probe …`"). Nothing in C1 reads the live tool.
- **C2 measure.** `controls.py` runs the live tool and receipt gate against a fake llama-server ("Writes a fake llama-server (python3 script in a TemporaryDirectory…)", spec item `C2Controls`). It never reads `tests/probe-verdicts/`.
- **Static check.** `grep` of `tools/kama-llamacpp-live.py` and `check-receipt.py` finds no reference to `probe-verdicts` or `check.py`.
- **The one shared input is `tools/kama-probe.sh`.** The live tool calls it (`tools/kama-llamacpp-live.py:54` "`DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'`"). The probe is currently byte-identical to the frozen copy (`36b64978…` both).
- **How that could break separability.** `C1HarnessGrading` is told that a row violating the new `served_model` invariant "is either a probe defect (a calibration finding)". If L1 then patches `kama-probe.sh` this round:
  - C2's `probe_model_ok` / `probe_mismatch` checks and its controls run on a changed probe.
  - C2 is then no longer "verifiable without the others having landed".
- **Precedent for keeping it separable.** Round 16 kept the claims separable with a frozen-probe receipt: "`receipt-frozen-probe.json`: 10/10 using the frozen probe … This shows the claims are separable" (`corpus/lessons/round-16-verifier-spotcheck.md:106`).

### F2 — C1's count measures detector power, which reads as operability; the collapse risk recurs (impacted: calibration, operability, the lowest-axis rule)
- **The round-16 critic named this pattern.** "The counting command measures none of these. What it measures is probe behaviour. That is an operability signal" (`.ufo/waves/round-16/falsify/advice/CriticC1Admission.md:15-16`).
- **It named the consequence.** "If the judge reads C1 as operability, C1 and C2 sit on one axis and count as one claim" (`:17-18`). Calibration, the lowest axis, would then be unworked, and the round would fail `AXES.md:33-34`.
- **Round 17 repeats the pattern.** "Surviving `check.py` mutants 5 → 0" counts the gate's detection power. It never reads a lane statement. The new invariants (served_model, route-match) and the malformed-output handling extend what the instrument can do. That is the "runnable artifact produces the stated outcome" reading (`AXES.md:13`).
- **The best counter-precedent is weaker than it looks.**
  - Round 15 admitted a gate repair as calibration: "Repairing a falsified executable assessment promise is a bounded improvement" (`round-15-verifier-spotcheck.md:7`).
  - The round-16 mutation seat also framed this axis as "**Calibration / detector sensitivity**" (`.ufo/waves/round-16/falsify/advice/MutateHarness.md:5`).
  - But round 15's promise had been shown false. The C1 promise has not (F3).

### F3 — C1's headline "check.py overclaims what it grades" is itself an overclaim (impacted: calibration, a no-harm risk)
- **The code does grade the fields.** `tests/probe-verdicts/check.py:340-346` folds `record["reason"] == expected["reason"]`, `record["probe_exit"] == expected["exit"]` and the drift contract into `passed`.
- **The docstring documents timeout as failure.** `check.py:25-26`: "1 on any test failure (including a probe timeout)". The code implements this.
- **The SKILL row is literally true.** `SKILL.md:533`: "grades verdict, reason, exit and drift". `served_model` and route-match are claimed nowhere, so leaving them ungraded is a gap, not an overclaim.
- **The gap was already named honestly at round start.**
  - `corpus/lessons/round-16.md:154-157`: "`check.py` grades reason, exit and drift but no row makes them load-bearing (5 harness mutants survive …), never grades `served_model`".
  - It was routed as debt at `round-16-verifier-spotcheck.md:187`.
- **The actual defect.** The lane's SKILL row states the grading with no graded confidence, while no detector backs it. The round-16 mutation advice called this "an exercised but redundant comparison" (`MutateHarness.md:7`).
- **Risk.** A verifier who re-reads `check.py:340-346` sees the claimed overclaim is false. The round would then carry a new overstatement inside its calibration claim: false provenance, which counts against calibration.

### F4 — The C2 operability label survives the merge attack, but only through one criterion that must be written down (impacted: operability, calibration)
- **The attack.** C2 has the same structure as C1: a documented predicate that the code does not enforce.
  - DOC: `tools/kama-llamacpp-live.py:78-80`, "GET /health returns 200 {"status":"ok"} once the model is loaded".
  - Code: `:938-939`, `_check('health_ready', health_status == 200, …)`.
  - Read as "overreach caught" (`AXES.md:15`), C2 joins C1 on calibration and the two count as one claim.
- **The defence is in the evidence.** The round-16 facts were true; only the instrument was weak. The v1 receipt records:
  - health body `"{\"status\":\"ok\"}"`
  - `"port_listener_ownership": "child"` (`.ufo/waves/round-16/live/receipt.json:224`)
  - `"sigterm_sent": true` (`:415`), returncode 0

  No admitted round-16 claim is falsified. C2 is not the correction of a false self-assessment.
- **The separating criterion: whose behaviour does the failing control change?**
  - C1's controls vary the lane's **own** instrument (wrapper probes, `check.py` mutants). That is self-assessment, i.e. calibration.
  - C2's controls vary the **external subject**: fake servers K1–K5 and K7 (spec `C2Controls`). They also vary harness faults (K6). That matches `ReviewLiveHarnessCode.md:1`: "six are falsifiable by subject behavior". This is operability: the runnable tool produces its stated outcome on real failure modes.
- **Leak 1: receipt-gate forgeries.** The v2 re-derivation and selftest in `check-receipt.py` vary the lane's own receipt, which is C1-shaped. Citing them as operability evidence would double-count under the earlier ruling "no double credit for regression machinery" (`round-15-verifier-spotcheck.md:151`).
- **Leak 2: one count, two axes.** The same count must not support "improved" on two axes (`.ufo/waves/round-14/advice/AttackDenominator.md:82`, "The same N→N count must not support 'improved' on more than one axis").

### F5 — C2 is a valid axis move without a new capability row; adding one would be pre-claiming (impacted: operability, calibration)
- **No capability row is required.**
  - `AXES.md:27-30` requires one verifiable improvement with a before→after.
  - Delta-0 "improved" verdicts have been admitted before: `SCORECARD.md:611`, operability "8 → 8, delta 0", admitted as improved at `round-16-verifier-spotcheck.md:112`.
- **A new row would be pre-claiming or a duplicate.** Rows enter "only through a round that demonstrates the capability running" (`AXES.md:62-64`). `live-llamacpp-lifecycle` already has first-working round 16 (`SCORECARD.md:628`).
- **What to do instead.** Append a supersession note that re-points the evidence to a v2 receipt. This follows the precedent "supersedes the one-row table … without editing it" (`SCORECARD.md:621-622`).
- **This is not mere re-verification.** Round 10 ruled "re-running unchanged gates is re-verification, not an operability move" (`SCORECARD.md:199`). C2 changes the tool's behaviour, so that ruling does not bite. It would bite if C2's evidence were only a re-run of v1.

### F6 — The lane's own plan states C1 and C2 as one move; the verifier did the same (impacted: separability optics)
- **The plan.** `SCORECARD.md:638-643` names a single "Next steered move … make the live checks fail-capable … and the matrix's reason/exit/drift grading load-bearing".
- **The verifier.** It also bundled both into one routed item (`round-16-verifier-spotcheck.md:187`, "Carried debt … Five `check.py` harness mutants survive … Live checks … weak").
- **The planned QUALITY rows show the shared principle.** Drafts KQ20 ("documented grading … admitted only when a detector exists") and KQ21 ("a live-run check is admitted only when a control in which the subject misbehaves flips it") are two instances of one fail-capability principle (spec items `QualityKQ20`, `QualityKQ21`).
- **Assessment.** This is not a rule violation: distinct axes are judged by what is measured, not by origin. But without F4's criterion written down, a verifier has textual grounds to merge the claims.

### F7 — Process items must earn no axis credit (impacted: calibration double-count, operability mislabel)
- The context declares `sources-append-only.py`, `count-verdicts.py` and `dispatch-provenance.py` "not claims". All three are honesty-of-own-records tools, which is calibration-shaped.
- If SCORECARD cites them in an axis verdict, there are two consequences:
  - On calibration they merge with C1 under `AXES.md:32-33`, which is harmless but earns no credit.
  - Anywhere else they mislabel an axis.
- Keep their before→after in the lesson only.

### F8 — Governance tradeoff for the canonical judge (not fixable by L1)
- Calibration has been claimed "improved, delta 0" in rounds 11–16 (`CriticC1Admission.md:143-144`). Round 17 would be the seventh such round.
- "So it is always the lowest axis, the stagnation nudge never fires, and whatever the lane builds gets the calibration label" (`:146-148`).
- `SCORECARD.md:132` sets saturation at 8. The lowest-axis rule (`AXES.md:33-34`) therefore binds indefinitely.
- This is a rule-level question, not a C1 defect.

## Would an outside verifier admit both?
[INFERENCE] Yes, if corrections 1–4 below land. That follows the precedents: round 15 (gate repair → calibration), round 16 (C1 probe-behaviour count admitted as calibration; C2 operability admitted at 8 → 8). Without corrections 1–2, a verifier has a citable path to rule C1 operability-shaped (F2) or self-overstated (F3). The path to a merged claim and an unworked lowest axis is open, not certain.

## Smallest safe corrections (no matrix, probe or frozen-copy change)
1. **Recount C1 against documented claims, not just mutants.** Use a ledger: documented grading sentence → mutant → detector → before survives / after killed.
   - Sentences: `SKILL.md:533` reason, exit, drift; verdict exact match; `check.py:25-26` timeout-as-failure.
   - Headline: "documented grading backed by a detector 0/5 → 5/5", replacing "check.py overclaims what it grades".
   - Append graded confidence to the SKILL row. This makes the count a claim-vs-evidence (calibration) measure, as `AXES.md:15` requires.
2. **Keep M6–M8 out of C1's delta.** M6 served_model, M7 route-match and M8 malformed-output exist only in the after code (`site_missing` before). Report them as after-only detector coverage of new grading, not as part of the calibration delta.
3. **Write the separating criterion in SCORECARD and the lesson.** "C1 varies the lane's own instrument; C2 varies the subject runtime or the harness fault path."
   - C2's operability evidence = `controls.py` accepted-bad before → after plus a real b11755 v2 receipt.
   - Do not cite `check-receipt.py` selftest or forgery counts as C2 evidence (F4 leaks 1–2).
4. **Keep `tools/kama-probe.sh` byte-identical this round** (`36b64978…`).
   - If a probe defect is found, record it as a finding for a later round, or declare it its own claim.
   - Either way, run the C2 real receipt with the frozen probe as well, as round 16 did.
5. **No new capability row.** Append a supersession note pointing `live-llamacpp-lifecycle` at the v2 receipt. Append an uncounted erratum: the v1 `health_ready` DOC (`kama-llamacpp-live.py:78-80`) stated a body predicate the code did not grade. This keeps calibration unharmed without counting it toward C1 or C2.

## Limitations
- The built C1/C2 artifacts did not exist when I reviewed (F1–F5 rest on the spec prompts and frozen code). Re-check F1 once `controls.py`, the v2 tool and `check.py` land.
- I ran no gate, measure, mutant runner or controls. I started no server and bound no port.
- The `LEARNING.md` at the fleet root differs from `kimi-shokunin/skills/shokunin/protocol/LEARNING.md` in wording only (diff at lines 46-50 and 86-90). The rules are the same.
- I did not read the outputs of sibling critics (C1Invariants, C2Predicates, NoHarm, SelfAuthoredDetectors).

## Installs
None.
