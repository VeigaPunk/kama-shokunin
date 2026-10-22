# Advice — ScribeQualityCriterion (kama round 25, attempt 2, wave 1)

Verdict: KQ36 draft row delivered in `corpus/QUALITY.md`'s exact four-column
table format, with a verified red/green demonstration pair (C1 command at
efe58e96 versus landed tip 1fc41e346853afd98cbd7010af5db4e54dc877f7).

## Draft artifact

`corpus/QUALITY.md` row text (new row, no existing line moved):

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ36 | A counting command cited by a SCORECARD row is re-run, with the registered command pasted, at the round's landed tip before the row's value stands; an instrument that cannot evaluate (its unique-match guard aborts, exit 2) is reported as stale and the row is unverified at that tip — never a pass. | A SCORECARD row keeps its value while its cited counting command is stale at the landed tip; a could-not-evaluate or exit-2 abort is recorded as a pass, hidden, or counted as zero defects; the re-run happens at any revision other than the landed tip. | `lessons/round-24-verifier-spotcheck.md` §2 (registered M-series mutation source stale at the measured auditor); `preregistration.json` C1 (count command `registered 27 stale 2` at efe58e96 → `registered 28 stale 0` at 1fc41e34); `SCORECARD.md:1166` (registers `python3 tests/report-audit/isolation-mutants.py --json`) |

Scope: the rule covers only counting commands cited by a SCORECARD row; it
adds no universal claim about mutation-testing scores or other instrument
classes.

Full draft with red/green plan: `.ufo/waves/round-25/a2-build/out/ScribeQualityCriterion/KQ36-draft.md`.

## Observed evidence (all run fresh this seat, in a sandbox clone pinned per commit)

Red — commit efe58e96 (pre-repair):

1. C1 counting command (preregistration.json C1.command), exit 0:
   `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`
2. SCORECARD-registered command `python3 tests/report-audit/isolation-mutants.py --json`, exit **2**, stdout empty, stderr:
   `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`
   (no mutant ran; the account's fail-fast guard aborts the whole run).

Green — tip 1fc41e346853afd98cbd7010af5db4e54dc877f7 (repair landed):

3. C1 counting command, exit 0: `registered 28 stale 0 []`
4. SCORECARD-registered command, exit **0**:
   `{"killed": 26, "mutants": 28, "pristine": "passed"}`,
   survivors `M17-ref-shadow`, `M20-log-sha-shape` (reported, not hidden).

The red side of the pair is the criterion's core failure shape: the
SCORECARD row at `SCORECARD.md:1166` registers the counting command, but at
efe58e96 that instrument cannot evaluate (exit 2). The row's value must not
stand as a pass on a stale instrument; it must be reported stale/unverified
until the instrument is re-run at the landed tip.

## Touched surfaces

- Wrote: `.ufo/waves/round-25/a2-build/out/ScribeQualityCriterion/KQ36-draft.md`
  (draft row + red/green plan + evidence pointers).
- Wrote: this advice report.
- Clone (scratch): `/fast/scratch/hyaku/kama-r25a2/ScribeQualityCriterion/clone`.
- Temp outputs: `/tmp/mutants-red.json`, `/tmp/mutants-red.err`,
  `/tmp/mutants-green.json`, `/tmp/mutants-green.err`.
- No production file edited; no commit, push, or git mutation in the lane;
  no jj command run; no llama-server child started (no port touched).

## Out-of-scope / not claimed

- I did not edit `corpus/QUALITY.md` (L1 is the only writer of lane
  production files); the row text is delivered as a draft artifact.
- SCORECARD has no round-25 section yet at the tip (grep for `round-25|M11|M17|M33` on `SCORECARD.md`: no matches); the live registered row is `SCORECARD.md:1166` (round-23 table).
- `corpus/lessons/round-25.md` does not exist at the tip (glob: not found);
  the motivating-lesson pointer for round 25 is the round-24 verifier
  spot-check, which exists.
- No tools installed this seat (nothing needed; tooling-directive record: none).
