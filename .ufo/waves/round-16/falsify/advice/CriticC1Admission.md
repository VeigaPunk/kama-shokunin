VERDICT: partial — C1 (MODEL_LOADING) as a calibration move under AXES.md, and its 7 → 7 score

Seat: KamaR16.CriticC1Admission (critic, leaf). Target: landed lane commit `b8e485c` (= origin/master).
This is advice, not a judgment. Paths are relative to the lane root unless absolute.

## Bottom line

- **The score is honest.** 7 → 7 is right. Nothing landed supports a mastery change, and a remaining
  overreach in the same class (F2) argues against any increase.
- **The calibration label holds only because of uncounted text.** The real calibration content is:
  - the frozen evidence string calling a model server "a non-model service";
  - the stale "vocabulary is fixed" and "six verdicts" statements;
  - mined mistake M1 and KQ19.

  The counting command measures none of these. What it measures is probe behaviour. That is an
  operability signal (`AXES.md:13`, "scripts that run … produce the stated outcome").
- **Why the label matters.** If the judge reads C1 as operability, C1 and C2 sit on one axis and count as one
  claim (`AXES.md:31-33`). Calibration, the lowest axis, is then unworked, and the round fails the
  lowest-axis rule.
- **Precedent for the label.** Round 15's verifier admitted a guard repair as calibration: "Repairing a
  falsified executable assessment promise" (`corpus/lessons/round-15-verifier-spotcheck.md:7`). The probe is
  the lane's assessment instrument, so the label is defensible. But the measured before→after does not show
  it. That is a fixable defect, not a fatal one.

## Axes named

calibration (claimed axis), operability (the axis C1 could collapse into), freshness/depth (prior-knowledge
framing), plus the no-harm check on SCORECARD/LOG versus repo state.

## What I ran (all from the lane root unless noted; scratch `/tmp/kama-r16-CriticC1Admission/`, now removed)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `git show 836b018:tools/kama-probe.sh \| sha256sum`; `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh` | 0 | both `93ee4302…cd64` = manifest sha. The frozen arm is the real pre-round probe. |
| 2 | `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` | **1** | `tests=72 passes=55 failures=17` (the 17 MODEL_LOADING rows). Reproduces L1. |
| 3 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` | **0** | `tests=72 passes=72 failures=0`. Reproduces L1. |
| 4 | 5 matcher mutants of `tools/kama-probe.sh` (in /tmp) through the real matrix (`check.py --probe MUTANT --json`) | not captured\* | All 5 killed. `m1` plain `==`: 1 fail (`code-float-503.0`). `m2` no type check: 2. `m3` substring "loading": 4. `m4` any `unavailable_error`: 12. `m5` any status: 7 (all `NonLoadingStatuses`). |
| 5 | Copy of `check.py` in /tmp with my own rows, run against both probes | current **1** / frozen **0** | Current grades MODEL_LOADING for: an extra key *inside* `error`; a duplicate `message` key (first `"Service paused"`); a duplicate `error` object (first `no slot available`); the envelope plus a `data[]` array; a `\u0061`-escaped message. Rejected (FOREIGN): `503e0`, `0503`. |
| 6 | Same harness, 503 `no slot available` and 500 `server_error` envelopes with `Server: llama.cpp` | **0** | Both `FOREIGN_SERVICE non-2xx-non-model-http`, evidence `"(Server: llama.cpp) (non-2xx HTTP from a non-model service)"`. |
| 7 | Standalone 503-envelope stub; current and frozen probe run with `PATH` holding every `/usr/bin` entry except `python*` | 2 / 2 | Without python3, current gives `FOREIGN_SERVICE non-2xx-non-model-http`, the same as frozen. With python3, current gives `MODEL_LOADING`. Matches the documented fallback. |
| 8 | `pgrep -x llama-server` | 1 | No server is running. I started no llama-server and contacted nothing on 8080 or 34113. |

\* In run 4 the background subshells' `.rc` files were not written, so I do not report those exit codes. The
counts above are read from each run's JSON `records`.

Timing: my runs finished by about 11:01. The lane working tree then picked up uncommitted edits at
11:03 (`git diff --stat`: 17 files). In `tools/kama-probe.sh` and `check.py` those edits touch only the
header comment and docstring, and `classify()`/`body_is_llamacpp_loading()` are byte-unchanged. The results
above therefore hold for `b8e485c`.

## Findings

### F1 — The counting command measures operability, not calibration (impacted: calibration, operability)

- **No document is read.** `grep -iE '\.md|SKILL|corpus|vocab|correction'` over
  `.ufo/waves/round-16/measure.py` finds nothing. The committed copy and the working-tree copy, with its new
  breadth pin, are the same on this point.
- **The doc corrections are invisible to it.** Commands 2 and 3 give the same 55/17 → 72/72 whether or not
  any lane doc was corrected. Those corrections are the actual calibration content.
- **The red arm is red by construction.** `MODEL_LOADING` is not in the frozen `VOCAB`, so the frozen probe
  cannot pass any row that expects it. The lesson presents this as "Shown able to fail: the frozen probe
  fails exactly the 17 expected-loading rows" (`corpus/lessons/round-16.md:64`). Round 12 named the same
  pattern "a construction check, not a discovery" (`SCORECARD.md:320`).
- **Where the discriminating power really comes from.** It is the 55 negative rows, and they do
  discriminate (command 4: every overbroad mutant is killed). That is the gate's strength. But it is evidence
  for the operability/coverage of the classifier, not for a calibration before→after.
- **The build wave already flagged this, and it was not adopted.** CriticC1Honesty F1
  (`.ufo/waves/round-16/build/advice/CriticC1Honesty.md:36`): "make C1's counted before→after include the
  doc/tool contradiction count".

### F2 — The overreach is narrowed for one body; the class remains, and the correction says otherwise (impacted: calibration)

- **The correction scopes the overreach to one case.** `corpus/knowledge/endpoint-identity.md:190-191`
  (landed, and still in the working tree): Rule 5 "overreached for one exact case and is narrowed, not
  deleted."
- **The same correction keeps known llama.cpp bodies on rule 5.** `:205-207`: "The no-slot (`no slot
  available`) and router-stream … `unavailable_error` bodies stay on rule 5". The lane's own lesson
  attributes both bodies to llama.cpp model-server code (`round-16.md:44`).
- **Counterexample (command 6).** A 503 carrying llama.cpp's own error envelope with `Server: llama.cpp`
  still prints `(Server: llama.cpp) (non-2xx HTTP from a non-model service)`. That is self-contradictory
  evidence produced by `tools/kama-probe.sh:565`.
- **"One exact case" is therefore a new overstatement.** Any non-2xx JSON error from a model server gets the
  unsupported "non-model service" text. The score stays honest because SCORECARD already says "one overreach
  caught on one envelope" (`SCORECARD.md:586`).

### F3 — The prior-knowledge framing overstates what the lane documented (impacted: calibration, freshness)

- **SCORECARD and the lesson both claim prior knowledge.**
  - `SCORECARD.md:579-580`: graded FOREIGN "since round 1, although the lane documented the loading body in
    round 10".
  - `round-16.md:15-16`: "The lane's own matrix (round 10 …) already documented the body".
- **But the round-10 row puts that body on `/health` only.** `runtime-health-surface-matrix.md:14`, liveness
  column `GET /health`.
- **And the lane's round-11 correction pointed the other way for `/v1/models`.** `:55` records "nullable
  `/v1/models` `meta` while loading", which predicts a 200. The new lifecycle entry admits this: "This entry
  adds the code-level path that puts the same body on `/v1/models`" (`llamacpp-loading-lifecycle.md:19`).
- **So the refuting fact is round-16 knowledge.** It comes from S036/S037, which is depth/freshness ground,
  not a self-assessment that sat next to its own refutation.
- **No misgrade was ever observed.** No receipt shows the probe misgrading a real runtime. On b6000–b7502,
  `/v1/models` was exempt from the gate (`llamacpp-loading-lifecycle.md:80-83`). The only real-runtime sight
  of the envelope on `/v1/models` is an unreceipted L1 smoke: "10:17 -03, not receipted"
  (`llamacpp-loading-lifecycle.md:105-106`, `LOG.md:930`).
- [INFERENCE] "since round 1" describes a latent code path, not an observed historical misgrade.

### F4 — As landed, SCORECARD/LOG/lesson point at measurements that do not exist (impacted: calibration — the AXES.md:15 signal itself)

- `corpus/lessons/round-16.md:93-94`: "Final numbers at the measured commit are in
  `.ufo/waves/round-16/acceptance.json`". That file is absent (`ls .ufo/waves/round-16/` at `b8e485c`).
- `SCORECARD.md:598`: "Measured values are appended below after execution." It is the last line of the file
  (598 lines).
- `LOG.md:953`: "Measured results follow in the next entry." It is the last line (953 lines).
- `endpoint-identity.md:214-215` calls a mid-load `MODEL_OK` not expected, "consistent with the round-16
  live receipt". That receipt has `loading_observed: false` and `loading_503: null`, so it never saw the load
  window. Calling it consistent is support in name only.
- Until L1 fills these in, the SCORECARD/LOG entries do not match repo state. That would be a calibration
  harm, not an improvement. The fix is easy: integrate before closure.

### F5 — "Exact envelope" is a parsed-predicate match, and the probe's own comment overclaims (impacted: calibration, minor)

- **The comment claims full exactness.** `tools/kama-probe.sh:423-425`: "Exact match only — any deviation …
  falls through".
- **The code does not do that.** Command 5 shows extra keys inside `error`, duplicate keys (last one wins)
  and a co-present `data[]` all grade MODEL_LOADING.
- **KQ19 does not cover nested extras.** It allows extra *top-level* keys only and says nothing about keys
  inside `error`.
- [INFERENCE] Real b11755 emits none of these shapes, so this is wording drift, not a false-pass risk. Exit
  stays 2.

## What survives (positive evidence)

- The frozen arm is genuine (command 1).
- The matrix kills five plausible overbroad matchers (command 4).
- The documented python3-less fallback behaves as stated (command 7).
- Vocabulary corrections exist in each place I found an old six-verdict list: `SKILL.md:507-511`,
  `consumer-registry.md:406-412`, `endpoint-identity.md:188-190`, `registry/endpoint-consumers.tsv:32`, and
  the probe header/help (`:28-30`, `:117`).
- The MODEL_LOADING evidence string carries graded confidence: "runtime identity and served model
  unverified". This absorbs the build-wave F2 finding.

## 7 → 7 judgement and the governance tradeoff (for the judge, not fixable by L1)

- **7 → 7 is honest.**
- **The pattern behind it.** Calibration has now been claimed "improved, delta 0" in rounds 11, 12, 13, 14,
  15 and 16 (`SCORECARD.md:266, 299, 379, 445, 522, 586`).
- **Why that makes the lowest-axis rule vacuous.**
  - Calibration stays at 7, below saturation line 8 (`SCORECARD.md:132`).
  - So it is always the lowest axis, the stagnation nudge never fires, and whatever the lane builds gets the
    calibration label.
- This is a rule-level tradeoff for the canonical judge, not a defect in C1.

## Smallest safe corrections (no verdict/reason/exit change, no matrix change)

1. **Add a counted calibration before→after to C1's record.**
   - Tally the lane statements that the landed state contradicts, before vs after. Pin each one by path:line
     (for example `endpoint-identity.md:3`, `:17`, `:163`; `SKILL.md:11-14`; `consumer-registry.md:84-85`;
     `registry/endpoint-consumers.tsv:32`; the frozen evidence string at `frozen/kama-probe-before.sh:522`).
   - Use one reproducible grep or ledger command. This is the round-10 pattern ("uncorrected … 50 → 0").
   - Keep `measure.py` as the no-harm/operability control.
2. **Fix the evidence text at `tools/kama-probe.sh:565`.**
   - Change it to "non-2xx HTTP; no model list; service identity unverified". Reason `non-2xx-non-model-http`
     stays for compatibility.
   - The snapshot baseline does not store evidence. `registry/history/latest.tsv` columns are
     `id verdict reason served_model port file_match`, so no transition noise follows.
   - The matrix grades verdict/reason/exit/drift only (`check.py:340-347`), so all 72 rows stay green.
3. **Reword `endpoint-identity.md:190-191`.** Change "overreached for one exact case" to "overreaches for any
   model-server error response; narrowed here for one documented not-ready state".
4. **Reword the prior-knowledge claim.** In `SCORECARD.md:579-580` and `round-16.md:15-16`, say the round-10
   row documented the body on `/health`, and that its `/v1/models` placement is round-16 code evidence
   (S036/S037).
5. **Land or remove the forward pointers before closure.** These are `acceptance.json`, the SCORECARD
   measured block and the LOG measured entry. Also drop "consistent with the round-16 live receipt" at
   `endpoint-identity.md:214-215`, or state that the receipt did not observe the load window.
6. **Optional.** Match the probe comment and KQ19 to the parsed-triple behaviour (nested extras and
   duplicate keys accepted), or tighten the predicate to reject extra keys inside `error`.

## Limitations

- I did not start llama-server (not authorized for this item), so I have no live MODEL_LOADING
  observation. F3's "no misgrade was ever observed" rests on the absence of a receipt plus the lane's own
  prose.
- I did not run `.ufo/waves/round-16/measure.py`, per the contract.
- I did not search sibling lanes for consumers of the seventh verdict.
- The working tree had uncommitted edits from other seats/L1 after my runs. Findings are against `b8e485c`.
  The working-tree `endpoint-identity.md` still carries the F2 sentence, and the working-tree `measure.py`
  still reads no document.

## Installs

None.
