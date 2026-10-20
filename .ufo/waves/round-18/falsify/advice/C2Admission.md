VERDICT: confirm — C2's statement→mutant→detector ledger matches exercised evidence row-for-row; the only material defect is a residual evidence gap, not a claim flaw: at pushed head `1c325b2` the counting command has no retained full run of the committed counter (the retained official run exercised the pre-repair classifier). I independently reproduced the missing arm: head counter `--family b` → FC-target/FC-f6cache/FC-f0gate all `killed`, exit 0.

# Axes

C2 calibration (lowest assigned, 7→7): named-survivor statement→mutant→detector repair.
Review axes: statement/evidence match, causal separation, bound counts / no inflation, counter-correctness.

# Ledger ↔ exercised evidence (all 15 rows verified against `.ufo/waves/round-18/runs/c2-survivors.json`)

| # | Lesson ledger statement | Mutant/fault | Detector (recorded arm) | Recorded outcome |
|---|---|---|---|---|
| 1 | exact expected reason | H1 case-insensitive reason | F9 case-only corruption | killed, accepted_ids `['F9']` only |
| 2 | emitted verdict token, not cleaned value | H2 verdict strip | F10 whitespace on loading row | killed, `['F10']` only |
| 3 | GET /v1/models required | H3 ignores method | F11 non-GET cached replay | killed, `['F11']` only |
| 4 | exact raw served id | H5 normalises id | F12 case/suffix variant, non-dash id | killed, `['F12']` only |
| 5 | no-request probe does not pass | H6 bypasses no-request failure | F13 zero-request replay | killed, `['F13']` only |
| 6 | first-row grading | H7 grades last row | F14 contrasting two-row output | killed, `['F14']` only |
| 7 | reject-everything subject gives no credit | FC-f0gate (`if False and not positive["detected"]`) | "F0 gate: a reject-everything" selftest | killed (selftest kill + main survived) |
| 8 | route replay uses corresponding row's output | FC-f6cache shared cache | "F6: replay run shares one cache" selftest | killed* (selftest kill; main exit 2) |
| 9 | rejection attributable to targeted conjunct | FC-target (`if False and target:`) | "target-conjunct attribution" selftest | killed* (selftest kill; main exit 2) |
| 10 | immutable cells include `opened` | AO-opened `header[:8]` | "only `opened` changes" selftest | killed (targeted assertion) |
| 11 | blank lines do not erase later rows | AO-blank `break` at blank | "edit after a blank line" selftest | killed (targeted assertion) |
| 12 | refused attempts count actual labels | prose-blind provenance | same 82-refusal input, both tool versions | miscount (frozen refused 0) → correct (82, spawned 0) |
| 13 | malformed output stays a row error | nested-json 100k-deep | per-row error, no traceback | accepted → handled |
| 14 | decoder int limits stay row errors | 5,000-digit integer | per-row error (ValueError named) | accepted → handled |
| 15 | probe timeout leaves no same-group child | escaped-sleep | liveness scan; pid alive before, reaped after | accepted → handled |

*Recorded at `c6dc46f` as `inconclusive`; recomputed `killed` under the head `combine_arms` and reproduced by my rerun (below). No statement in the ledger exceeds its exercised evidence; H4 correctly absent (it was a non-surviving round-17 mutant); each kill attributes to the ledger's named fault — `accepted_ids` contain exactly the one targeted fault, never a diffuse accept.

# Strongest counterexample tried: `combine_arms` kill-over-inconclusive is defensible, but see the residual risk

The head change (`survivors.py:976-985`, `c6dc46f→1c325b2`) lets one conclusive "killed" arm dominate an inconclusive partner. Attack: could a mutant be credited "killed" when its behavioral arm produced no decision? Yes — FC-target's mutated fault-controls exits 2 ("F1: fault declares no target conjunct"). But the kill is not inferred from exit 2; `selftest_arm` (`survivors.py:928-953`) requires exit 1, a clean unmutated baseline selftest, and failure containing the named targeted assertion. The mutated tool fail-closes (refuses rather than accepting) and the meta-selftest independently proves the weakening is seen. `combine_arms` is also verified negatively: selftest rows "(b) no targeted selftest kill plus main exit 2 stays inconclusive" and "passing selftest plus main exit 2 remains inconclusive" passed (head selftest 60/60, exit 0, this seat, 43.4 s). Residual, disclosed-only risk: a future mutant that disables the targeted check *and* the selftest's table check could produce a missing targeted failure → inconclusive, not killed — the safe direction.

# Executed verification (my clone `/tmp/kama-r18-falsify-C2Admission` @ `1c325b2`, branch `seat/C2Admission`)

- `python3 .ufo/waves/round-18/c2/survivors.py --selftest` → exit 0, `selftest: 60/60 checks passed`. Note: the *recorded* `runs/c2-counter-selftest.stdout` shows 57/57 — it ran the c6dc46f counter; the 60-check head counter was not officially exercised before push.
- `python3 .ufo/waves/round-18/c2/survivors.py --family b --jobs 3 --json --out …/fam-b.json` → exit 0, 190.3 s, `own_faults: []`: FC-target/FC-f6cache/FC-f0gate `survived → killed`; frozen witness arms reproduced verbatim (`mutant_sha256` `3bd9d084…` for FC-target frozen identical to recorded). Scratch `/tmp/kama-c2-survivors-ryw3t9sv` removed by teardown; `ss -tln` shows no listener on 8080/34113; no marked process left.
- `python3 tools/sources-append-only.py --from e75cf68 --to c6dc46f` → exit 0 (S048–S054 added); `--from c6dc46f --to 1c325b2` → exit 0 (S055 added). KQ22 consecutive-pair check holds at head.
- Input identity at head: check.py `12367de6…`, fault-controls `58dac1f7…`, sources-append-only `4d786856…`, dispatch-provenance `93705f17…`, probe `36b64978…` — all match build-advice pins; `git diff c6dc46f→1c325b2 -- tests/ tools/` touches no C2 production file, so all recorded arms remain valid evidence for the head counters' inputs.

# Separation

survivors.py's inputs are exactly C2-owned files: `check.py`, `fault-controls.py`, `sources-append-only.py`, `dispatch-provenance.py`, frozen round-17 copies, the probe and nine matrix JSONs (unchanged shared). `grep` of survivors.py: no `kama-llamacpp`, `check-receipt`, or `controls.py` references. C1's `c1-self-mutants` set is not folded into C2's denominator.

# Bound counts / no inflation

- Denominator pinned at the 15 named round-17 items; `fresh_wave2: {included: false, mutants: 0}` — fresh mutants cannot inflate or hide.
- Score 7→7 delta 0; lesson calls it bounded repair, explicitly "not evidence that an unseen mutant cannot survive" (`round-18.md:24`, `:144-145`).
- Exit vocabulary keeps survived/site_missing/site_ambiguous/stillborn/not_exercised/accepted/miscount distinct (docstring lines 15-16: "NOT killed — never skipped"); recorded run has zero such rows but the classifier emits them (selftest rows exercise each).
- Inconclusive is never a kill in any arm (family a: `classify_a` maps exit 2 → inconclusive; family b: selftest/main exit 2 → inconclusive; only `combine_arms` lets an independently-attributed kill dominate).

# Findings

1. **Residual evidence gap (fixable, disclosed):** no retained full run of the committed head counter. `commands.json` shows `c2-survivors` exit 2 (as_expected false) under tool sha `2af03fed…` at measured revision `c6dc46f`; head counter sha is `87cad1ca…`. Lesson numbers ("two FC inconclusives") describe the old counter's composite, not what the committed counter reports. This is honestly disclosed (exit 2 reported as could-not-evaluate, raw arms retained, failures routed to owners), so it is not a concealment defect — but the official corrected artifact promised by "corrected reruns are new artifacts" does not exist in `runs/` at push time. Smallest safe correction: retain a `runs/c2-survivors-2.{json,stdout,stderr,exit}` full run of the head counter (expected exit 0; deterministic given identical inputs — family-b already reproduced; other arms' raw evidence is unchanged and pinned), or record the family-b reproduction as the corrected artifact with this note. Do NOT rewrite `c2-survivors.*` (original failed evidence must stay).
2. **Minor doc drift:** `runs/c2-counter-selftest.stdout` (57/57) is the pre-repair counter's selftest; head selftest is 60/60. Not a claim defect — commands.json pins the measured revision — but a reader diffing head against runs may misread it as regression. Optional: a one-line note in the final numbers table that runs/ artifacts are at `c6dc46f`.
3. **No inflation, no hidden survivals, no ledger row without exercised evidence.** All 15 ledger statements match a recorded arm outcome; attribution is per-named-fault; frozen witnesses (11 survived, 1 miscount, 3 accepted) reproduced exactly including frozen mutant sha `3bd9d084…`/`e20eb8c4…`/`636c419f…`.

# Impacted axes and admission advice

Calibration: **improved, bounded** — the repair is real, exercised and attributable; the named universe closed 15→0 bad outcomes under the corrected classifier (12 killed, 1 correct, 3 handled), subject to finding 1's retained-artifact correction. Discernment unchanged (own-wave review is not an outside spot-check). No axis harmed: probe/matrix bytes unchanged; append-only verified; no consumer port touched. Advise admission of C2 once the corrected-run artifact lands (or is replaced by an explicitly-noted family-b reproduction); the current pushed state is a documentation-of-evidence gap, not a counterexample to the claim.

# Install / environment record

No installs or updates. Host `python3` 3.14.8 used only; all runs inside `/tmp/kama-r18-falsify-C2Admission` (clone, `seat/C2Admission`). Scratch `/tmp/kama-r18-falsify-C2Admission` (clone) removed per contract note: retained for the wave duration? — my `fam-b.json`/`fam-b.stderr` remain inside it; remove the whole clone dir at wave end. No seat-owned listener remains (`ss -tln` checked).
