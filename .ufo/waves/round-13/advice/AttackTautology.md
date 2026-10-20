# AttackTautology — round 13 critic report

Seat: KamaR13.AttackTautology (critic, leaf, read-only except this file). Root `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Target: attack the use of the probe's literal-presence result as semantic proof; confirm that separate human source/code review is required and that no generic gate is claimed.
State at review: `measure.py` absent and no KQ16 row in `corpus/QUALITY.md` (grep `KQ16` found nothing). `corpus/lessons/round-13.md` (draft) was read. So the findings below cover the design and the shared contract, plus the landed lesson draft. They are not findings against landed probe code or KQ16 text. ReviewProbe owns the code re-review once the file lands.
Nothing was executed: no fidelity.py, reproduce.py, probe, selftest, build or test. The only code run was a stdlib JSON read of committed `round-12/acceptance.json` through the eval tool. Existing receipt values below are historical observations, not new runs. Tools installed or updated: none.

## Counterexamples

### T1 — red-before is guaranteed, not measured (tautology)
- **Evidence.** The shared contract fixes the literals `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` and `capture: git show; comparison: git cat-file blob` in this round. The criterion writer and the probe use the same contract. The start QUALITY (941bb32) has no KQ16. KQ15 at `corpus/QUALITY.md:49` contains neither literal.
- **Consequence.** "Before 2 missing → after 0" is true for any start text that lacks these invented strings. It shows that the writer adopted the probe's strings. It does not show that a discrepancy was corrected. The denominator of two comes from the outside human finding (`round-12-verifier-spotcheck.md:147` D1), not from the probe.
- **Lesson risk.** `lessons/round-13.md:50` cites "old criterion non-clean … corrected clean" as the fix obligation, but red-before carries no falsification weight.
- **Correction.** Attribute the 2 to D1. Describe the probe as a conformance and regression anchor whose before-count is fixed by construction.

### T2 — false green: literal present, semantics wrong
- **Evidence.** The exit code depends on the selected primary finding, not on each finding ID:
  - `fidelity.py:64-72` defines the PRIORITY order.
  - `fidelity.py:319`: `exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)`.
  - `fidelity.py:55-56`: "Every exit-2 finding outranks source_mismatch".
  - The outside review (`round-12-verifier-spotcheck.md:151`) says "a real source mismatch may coexist with an exit-2 integrity/manifest finding".
- **Counterexample text.** A KQ16 that says "any source mismatch exits 1 (source_mismatch=1; snapshot_tampered=2; source_unavailable=2)" passes a literal check but is false in the coexisting case. So would a KQ16 that puts the literal inside a negation or in the reject column.
- **Committed observation of coexistence (correction).** Earlier I wrote that no committed case exercises coexistence. That was wrong; L1 and ReceiptFacts pointed it out. The selftest `snapshot-tampered` check in round-12 `acceptance.json` records exit 2 with finding `snapshot_tampered` and `mismatches: 1`. Its command uses a mutant snapshot against the clean manifest; the record is at `fidelity.py:501-502`. This is a source mismatch alongside a tamper, and the exit-2 ID wins. By contrast, `pin-only-corruption-exact-snapshot` records exit 2 `snapshot_tampered` with `mismatches: 0`. I read both from the committed `result.records.selftest.stdout` checks and ran nothing new. The precedence reading is therefore observed in committed evidence, not merely inferred from the code.
- **Correction.** KQ16 should say "exit of the selected primary finding" and state that an ID listed in `findings` does not set the exit. The probe should match only inside KQ16's admit column if it can, and must not report verdict 0 as semantic truth.

### T3 — false red and paraphrase evasion in the wording mutant
- **False red.** The "reintroduced distinct-nonzero-exits" control flags a correct KQ16 that quotes KQ15's phrase in order to name what it supersedes.
- **False green.** Paraphrases ("each has its own nonzero code") get past a literal check.
- **Correction.** Report both as probe limits. Have KQ16 refer to "KQ15's exit-class sentence" rather than quoting it verbatim, or have the two owners coordinate the exclusion.

### T4 — capture provenance is author-attested, not verified by code or receipt
- **What is verified.** The comparison operation is fixed in code: `git cat-file blob` at `fidelity.py:271-273` and `reproduce.py:80`. Byte identity is recorded: `frozen/expected.json` has `snapshot_sha256 == source_sha256` (`9dc40d25…`). The outside C1 recount independently compared bytes through `cat-file blob` (spotcheck `:50-64`).
- **What is only attested.** That the snapshot was captured with `git show` rests on author statements: `round-12/advice/Fidelity.md:37` ("generated from `git show` raw stdout") and `lessons/round-12.md:14`. `expected.json` has no capture-command field, and identical bytes cannot reveal which command produced them.
- **Over-claim.** `lessons/round-13.md:42-43` says "actual round-12 code and receipt identify which operation was used for each half". That is true for the comparison only.
- **Correction.** Word it as: capture is author-recorded provenance whose output bytes are independently checked, and the comparison operation is fixed in code. Neither the probe literal nor S032 or S033 proves that a given capture ran.

### T5 — gate machinery is required construction evidence, not semantic evidence (revised)
- **Evidence.** `PROTOCOL.md:385-397` (Gate standard) sets three requirements:
  - a self-test over isolated fixtures that asserts the exit and the finding ID;
  - `expected.json` "MUST pin the digest of every snapshot input file";
  - an edited snapshot reports `snapshot_tampered` (could-not-evaluate).
  
  `:390` says "Self-test green is capability, not a measurement."
- **Withdrawn (my errors).** The frozen final-text pin is a required frozen-input snapshot digest, so Measure must keep it. `snapshot_tampered` is the protocol's standard finding ID, not fidelity's private ID, so the "ID collision" objection fails. Registry entry is mandatory because any script that can fail is a gate.
- **Remaining correction.** Present the pin, the selftest and the mutation controls only as frozen construction and control evidence. That evidence shows the textual checker works on its committed input. It is not evidence of semantic truth, and it is not a new generic, serving or gate capability. KQ15's reject column still applies: a matching digest or a green `--selftest` is never offered as correspondence or as proof of content.

## What is sound
- `lessons/round-13.md:30` rejects "Literal criterion checker alone proves semantic correctness".
- `:28` makes admission conditional on static code and receipt correspondence.
- `:31-32` reject treating new serving knowledge or gate machinery as quality.
- `:55-61` credit the round-12 D4 crosswalk interpretation, not gate machinery. This matches spotcheck `:122` and `:149`.
- The facts behind the proposed literals hold as a primary-finding map:
  - `fidelity.py:24-25` docstring: "Exit codes: 0 clean; 1 source_mismatch; 2 snapshot_tampered, source_unavailable, …".
  - `:319` computes the exit from the primary finding.
  - The receipt exits listed in T2 agree.
  - The two errors that D1 routed are real: KQ15 `:49` says "distinct nonzero exits" and gives `git show` as the fetch used for comparison.

## Primary-finding qualifier (required in KQ16)
`source_mismatch=1; snapshot_tampered=2; source_unavailable=2` is the exit of the **selected primary finding**. The PRIORITY order in `fidelity.py:64-72` picks the first matching ID, and `:319` maps it to an exit. Every exit-2 ID outranks `source_mismatch` (`:55-56`). A real source mismatch that coexists with an exit-2 finding therefore exits 2 (spotcheck `:151`). The committed round-12 selftest `snapshot-tampered` record shows this: exit 2, finding `snapshot_tampered`, `mismatches: 1`. The map is correct only for the finding that is selected. It does not mean that every observed condition sets its own exit. KQ16 must say so. A literal-presence probe cannot check this qualifier, so human code and receipt review must.

## L1 disposition (KamaR13 reply, accepted by this seat)
- **T4 accepted.** L1 will correct the newly drafted lesson wording: code and receipt identify the `cat-file blob` comparison, and the `git show` capture remains author-recorded provenance.
- **T1 resolved.** Red-before shows only that the stated literals were absent before the correction. It does not independently falsify semantic truth. Actual code review grounds D1's two formulations. The mutation controls show only that the text checker works within its bounds. This seat agrees, provided the lesson and report do not present red-before or the controls as semantic evidence.
- **T5 resolved; corrected by L1.** Registry entry is mandatory. The frozen final-text pin and `snapshot_tampered` are required by the Gate standard (`PROTOCOL.md:395-397`). I withdraw my earlier advice to drop the pin and to use probe-local IDs. My messages to Measure on those two points are superseded by a correction message. Remaining requirement: the pin, the selftest and the controls are construction and control evidence only. They are not semantic proof and claim no generic or serving capability.
- **T2 coverage corrected by L1.** The committed selftest `snapshot-tampered` record (exit 2, `mismatches: 1`) shows coexistence. See T2.
- **Open with owners:** T2 primary-finding qualifier and T3 wording in KQ16 (Criterion); scope and limits of the probe-output literals (Measure).

## Impacted axes
- Calibration (C1): the evidence for the 2→0 delta must rest on D1 plus the static code and receipt review. The probe is only a conformance record. Score stays 7→7.
- Discernment: T2 and T4 wording precision decides whether KQ16 fixes the routed defect or adds a new imprecision.
- Quality and expansion: unaffected if `:55-61` stand.

## Messages sent
- KamaR13.Measure: T1–T4 and T5. Delivered.
- KamaR13.Criterion: T2, T4, the T3 quoting risk, and the KQ14 boundary. Delivered.
- KamaR13 (L1, lesson owner): T4 over-claim at `:42-43`, T1 at `:50`, T5 drift. Delivered.

## Limits
- KQ16 and `measure.py` were absent when reviewed. Their final text must be re-read; this report does not clear or condemn them.
- Coexistence and precedence are observed in committed round-12 selftest evidence (`snapshot-tampered`: exit 2, `mismatches: 1`). Nothing was re-executed.
- How the capture was produced in round 12 cannot be observed here. It stays author-attested ([INFERENCE] that it matches is supported only by byte identity).
