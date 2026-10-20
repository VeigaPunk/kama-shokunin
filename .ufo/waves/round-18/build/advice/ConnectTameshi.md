VERDICT: partial — cite tameshi's targeted-case and equivalent-probe rules in kama; do not defer C2's sweep.

Axes: calibration (7, lowest) and operability (8). The move below tightens how C2 classifies a mutant. It leaves the live server alone.

## Evidence

Read only `tameshi-shokunin/SKILL.md` (1934 lines) and `tameshi-shokunin/corpus/README.md` (281 lines). Neither file names kama. Neither file contains the string `fault-control`.

### Mutation doctrine C2 can cite

- `tameshi-shokunin/SKILL.md:96-97` — "load-bearing only when a disabled or attacked mechanism makes exactly the targeted cases fail."
- `tameshi-shokunin/SKILL.md:200-204` — "A kill can be token-only, not exit-only." "Adjudicate exit AND token/verdict; never exit alone."
- `tameshi-shokunin/SKILL.md:208-211` — "Inconclusive = no definitive verdict (timeout, crash before the summary, count not enumerated). Not a kill." "Kill rate = killed / (killed + survived) — inconclusive runs are excluded from the denominator and named beside it."
- `tameshi-shokunin/SKILL.md:214-223` — "If no observable input differs, the mutant may be equivalent code — record that as a calibration item, not as a gap."
- `tameshi-shokunin/SKILL.md:1794-1796` — "Show each survivor is not equivalent off-suite before calling it a gap."
- `tameshi-shokunin/SKILL.md:365-366` — "Mutation measures the suite, not the substrate."
- `tameshi-shokunin/SKILL.md:733-736` — "bind every rate to its composition." "a rate quoted without kill-aimed vs hole-aimed is not comparable across sweeps."
- `tameshi-shokunin/SKILL.md:1489` — "Equal nonzero controls, or command unavailable" → "Could not evaluate baseline" → "No mutation kill-rate claim."
- `tameshi-shokunin/corpus/README.md:60` — "NoCoverage candidates left U; "timeout counts as a kill" rejected."
- `tameshi-shokunin/corpus/README.md:266` — "a guard is covered only when its removal mutant is killed with a green pristine control."
- `tameshi-shokunin/SKILL.md:27-28` — "The substrate tree is never a mutation target."

The worked recipe (one exact edit, pre-registered `expect`, uniqueness gate, scratch under `/tmp`, restore by hash) is the method. Eight recorded cases exist since round 18 (`tameshi-shokunin/corpus/README.md:268` — "there are eight since round 18"). A headline rate without its kill-aimed / hole-aimed split is not a comparable number.

### Closest "fault-control" material, and it is not one doctrine

Three different bars sit in these two files:

1. Targeted cases. `SKILL.md:96-97` (quote above). This is the bar that matches C2's R5/R7 demand: the failed check is the targeted one.
2. Single-lane guard-disable, explicitly not fleet-general. `tameshi-shokunin/corpus/README.md:12` — "sensitivity = guard-disable in a disposable copy (binary per guard, no kill-rate tally — U8)" and "explicitly single-lane, NOT general."
3. Any-nonzero closure. `tameshi-shokunin/SKILL.md:1929` — "A guard probe is closed only when the pristine selftest exits 0 and the guard-removal mutant exits nonzero." README:266 says "killed" and does not say "the targeted case."

Importing (2) would drop C2's survivor count. Importing (3) alone would close a guard that failed some other check. Cite (1), plus the green-pristine half of README:266.

### Equivalent-mutant doctrine is a probe, and the generator frontier is open

- Worked rule: off-suite output must differ, or the mutant is a calibration item, not a gap (`SKILL.md:214-223`, `:1794-1796`).
- Round 18 still recorded a help-text delta as non-equivalent. `tameshi-shokunin/SKILL.md:1915-1916` — "four are non-equivalent, S_KIND differs only in --help output."
- `tameshi-shokunin/corpus/README.md:86` — F9 "LLM-era mutant generation + equivalence" is "open"; "no LLM-specific search run yet (U)."

There is no settled oracle that declares equivalence without an off-suite input. A verdict-text change (case-fold, strip, method, id form) is a gap once any retained string differs and the suite stays green. It becomes "equivalent code" only when no observable input differs.

### Contradiction (kept, not averaged)

The recipe and the harness grade a kill differently.

- Recipe: red is exit ≠ 0 or the PASS/token line broken, and the full case count still enumerated; a token-only kill counts (`SKILL.md:189-204`).
- Harness: `tameshi-shokunin/SKILL.md:846` — "KILLED (suite exit ≠ 0) / SURVIVED (exit 0) / INCONCLUSIVE (timeout 124, or 126/127 not runnable)."
- Round 16, for suites that print `mkdtemp` names: `tameshi-shokunin/SKILL.md:1786-1789` — "Grade by exit, not by stdout bytes." "`tools/mutate-and-run.sh` grades on exit only."

C2's named check.py mutants are verdict-text mutants. They are the recipe's case (token), not the mkdtemp exception. [INFERENCE] that check.py's verdict channel is a stable string: this seat did not open check.py; the round assignment describes H1 reason case, H2 `.strip()`, H3 method, H5 ids, H6 no-request, H7 last row.

Timeouts split the same way. A suite that dies before a verdict is inconclusive and stays out of k/(k+s) (`SKILL.md:208-211`; README:60 rejects "timeout counts as a kill"). A checker that still exits 0 while an escaped sleep runs is a survivor (exit 0), a real gap. Those two outcomes are different cells.

### What C2 must not treat as current fleet doctrine

- `tameshi-shokunin/corpus/README.md:7` — "no kill-rate harness or self-code fault injection anywhere in the corpus" is the kumitate survey row. The round-2 addendum still says the gates themselves do not embed one: `corpus/README.md:10` — "still no gate ships a kill-rate harness." Tameshi's later external harness is `tools/mutate-and-run.sh`. The survey sentence is not "the fleet has no mutation method."
- `tameshi-shokunin/SKILL.md:994-995` — "The ledger proves the instrument, not the gates." A tameshi `REGRESSION: PASS` would not say kama's checkers catch anything.
- `tameshi-shokunin/SKILL.md:879-881` — "a sweep measures what the suite can detect, never whether the gate's verdicts are right." A C2 kill rate is not an operability result for the live server.

## Contested scope

- `tameshi-shokunin/SKILL.md:1262` — refusal (e), "Credential material / endpoint health" is "out of province — report, never absorb," anchored `PROVINCE.md:14-18` and `PROVINCE.md:20`. This round's lane domain is local model serving and endpoint health. The shared phrase is the contest. These two files do not say whether hermetic `tests/probe-verdicts/` is inside that refusal. [INFERENCE] C1's live llama lifecycle is inside refusal (e) and inside refusal (d); C2's checkers are the suite the mutation method measures (`SKILL.md:365-366`). The province lines were not opened.
- `tameshi-shokunin/SKILL.md:1261` — "Live substrates / sessions" → "never read; a live-plane probe is a PATH-level stub, never the session."
- `tameshi-shokunin/SKILL.md:1258` — "no sweep — the queue is an offer, not a schedule."
- `tameshi-shokunin/SKILL.md:872-874` — "Recommendations-only — absorption stays with the owner."
- `tameshi-shokunin/SKILL.md:998-1000` — a sibling attestation returns a receipt; "the sibling's note is never edited."
- `tameshi-shokunin/corpus/README.md:9` — the cross-lane layer "audits and reports, never fixes siblings." Patterns are "called general only on ≥2 independent lanes." The sweep method has that bar for the measured shapes (`SKILL.md:762-763`). The guard-disable tally refusal does not (`README.md:12`).
- `tameshi-shokunin/corpus/README.md:139-140` — "Neither row changes province Core by self-attestation."

Deferring C2 to tameshi would ask an out-of-province, recommendations-only service to absorb the owner's checker. Citing the rules leaves ownership in kama. `service-limits.md` is the detail of record for the refusal table; `SKILL.md:1250-1254` says "a divergence between the two is the finding." That divergence was not checked.

## Proposed move

Keep the C2 sweep in kama. In the survivor tally, grade check.py / fault-controls mutants with the recipe:

- Killed only when the run is red on exit or on the verdict token, the case count is still enumerated, and the failing label is the targeted check (`SKILL.md:96-97`, `:200-204`).
- A green run is a gap only after an off-suite probe shows a difference (`SKILL.md:214-223`). No difference → calibration item, named, excluded from the gap count.
- No verdict (timeout, crash before the summary) → inconclusive, excluded from k/(k+s), named beside it (`SKILL.md:208-211`). Exit 0 despite an escaped sleep stays a survivor.
- A red or missing pristine control → no kill-rate claim (`SKILL.md:1489`).
- Report kill-aimed and hole-aimed counts separately (`SKILL.md:733-736`).

Leave these out of that tally: harness exit-only grading (`SKILL.md:846`, `:1789`), any-nonzero guard closure (`SKILL.md:1929`) as a sufficient close, and the single-lane "no kill-rate tally" pattern (`README.md:12`). Do not opt this lane into tameshi's mutation service this round.

Affected axes: calibration improves, because a token-only mutant and a wrong-case failure stop sharing one "survivor" or "closed" cell. Operability is untouched: no live listener, no endpoint bytes handed to tameshi, sensitivity stays a statement about the suite (`SKILL.md:879-881`).

## Risks

- Using exit-only grading on H1/H2 hides a token change that preserved the exit code. Using token grading on a suite whose stdout contains fresh temp paths false-kills it; that exception is `SKILL.md:1786-1789` and applies to mkdtemp noise, not to a stable verdict line.
- Citing README:266 without `SKILL.md:96-97` lets a non-targeted failure close the guard. That is the R7 targeted-conjunct hole, reintroduced by the weaker bar.
- Refusal (e)'s `PROVINCE.md` lines might be narrower than the table cell. The "do not defer" half still follows from the offer-not-a-schedule rule and from owner absorption, even if a later opt-in sweep of hermetic checkers were in province.
- Calling S_KIND-style help-only drift "equivalent" contradicts `SKILL.md:1915-1916`, which kept that drift as non-equivalent.

## Verification

This seat did not run `survivors.py`, any lane gate, or a server. L1's check, when it measures:

- An exit-preserving verdict-token mutant stays a named survivor until the targeted token assert exists, then dies on that case's label.
- A guard-removal that fails a different check stays open.
- A mutant with no off-suite difference is a calibration item, outside the gap count.
- A harness timeout with no summary is inconclusive; a checker exit 0 under an escaped sleep is a survivor.
- The pristine control red or missing produces no rate.

## Limitations

- `PROVINCE.md` and `corpus/knowledge/service-limits.md` were not opened. Refusal (e) is quoted from the SKILL table only.
- Applicability of the token grade to check.py's actual stdout is [INFERENCE] from the assigned mutant list.
- No install. Pacman pause left unused; no tool was required.

## Installs

none.
