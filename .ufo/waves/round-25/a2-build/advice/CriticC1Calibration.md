INVALID as framed as a SCORECARD/SHONEN calibration claim; the bounded anchor repair and its measured 27 → 28 denominator are valid evidence, not a judgment of admission.

## Axes

Calibration (self-assessment versus observed state), measurement reproducibility, denominator/identity preservation, and provenance honesty. No numeric promotion, serving capability, saturation, PM08 execution, or whole-isolation conclusion follows.

## Strongest counterexample: the cited self-assessment is historical

The binding prompt `.ufo/prompts/kama-round-25.md:342-350`, especially 347-348, requires calibration to count mismatches between SCORECARD/SHONEN self-assessment and observed repository state.

`SCORECARD.md:1155-1156` explicitly binds the round-23 measurement to auditor `e876b953e9da28d2dffd29c923052bc626148c27`. Line 1166 reports 30/31 killed, survivor M20, and cites `.ufo/waves/round-23/final/mutants.json`. Lines 1192-1195 retain those historical measurements while superseding author admission. Therefore a later broken instrument does not by itself falsify that historical self-assessment.

Observed inspection of committed round-23 JSON and instrument registries (Python reading `git show` output, exit 0):

```
e876b953 mutants 31 retired 0
147f5bd mutants 27 retired 4
1fc41e3 mutants 28 retired 4
147f5bd ids missing at tip: []  added: ['M33-ref-shadow-bare-objects']
r23 mutants.json: mutants 31 killed 30 surviving ['M20-log-sha-shape']
```

Amendment 2 line 15 bridges this gap by assertion: it treats each stale instrument literal as a mismatch with the SCORECARD self-assessment. But the counting command reads neither SCORECARD nor SHONEN, identifies no particular self-assessment contradicted by M11 or M17, and does not compare the dated round-23 claim with its dated repository state. The strongest counterexample is the repository itself: that historical 30/31 statement remains supported by its filed JSON while the later anchor count changes from two to zero. Repairing instrument applicability is useful, but does not establish two corrected self-assessment mismatches.

This is a claim-axis defect for the canonical judge, not an implementation defect in re-anchoring. Relabelling it cannot confer calibration credit or silently change the registered axis after landing.

## One-command value and denominator: reproducible

I used my own no-hardlinks scratch clone, not the lane index. The exact command registered in `preregistration.json:16`, executed from the clean checked-out lane root, was:

```
python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
```

Observed outputs, each exit 0:

```
147f5bdd3228ab712520b5f377346cb2d9a64769:
registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
efe58e96e6cf:
registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
5388b7cf1d5b:
registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']
1fc41e346853afd98cbd7010af5db4e54dc877f7:
registered 28 stale 0 []
```

Thus `stale 0` is a concrete value re-derivable with one command over clean committed bytes. The command ordinarily reads working-tree files; closure must use a clean committed checkout, not assume any dirty checkout is committed-byte evidence. Its exit 0 is not the claim value: the printed count is.

Tip SHA256 values observed (exit 0):

```
b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f  tools/report-landing-audit.py
bdd4250a1af29edcf9f7deed17663ff513b2b383b5ae033256221128a3e5ab9c  tests/report-audit/isolation-mutants.py
```

`git diff --quiet 147f5bd 1fc41e3 -- tools/report-landing-audit.py tests/report-audit/repo-state-grid.py` exited 0. Only the instrument changes in repair commit 1fc41e3. Its lines 65-67 re-anchor M11 to the wrapped listing; 81-87 retain M17's guarded lookup check; 117-123 add M33 for the other site. Auditor lines 212-214 and 275-277 are distinct refusal sites; line 246 reaches `bare_objects()` only for peeled lookup. The round-23 auditor lines 148-149 and 170-172 show the earlier recursive lookup and guarded refusal. No before id disappeared, no new retirement occurred, and the only new id is M33. Reporting 27 → 28 registered mutants is honest; do not describe it as an additional independent isolation element or serving capability.

## Smaller wording defect

`preregistration.json:14` says the command aborts "before any mutant runs". Instrument lines 186-203 run pristine and then iterate mutants, checking each anchor immediately before that mutant. An observed run in my separate clone at 147f5bd exited 2 with:

```
could-not-evaluate: M11-listing-surrogates: pattern matches 0 times
```

It produced zero JSON bytes. The abort happens on reaching M11, after earlier entries have been evaluated; it does not validate a completed mutation report. The tip full supporting run was cancelled without a completed result; I claim no fresh killed/surviving totals from it. Duplicate launch attempts were stopped; shared scratch exit files contain cancellation markers and are not clean full-run receipts.

## Smallest safe correction text

Append a correction without overwriting historical evidence or changing the registered target:

> C1's measured instrument repair is registered 27 stale 2 → registered 28 stale 0, with no removed or reused ids; M33 separately covers the second call site of the existing ref-shadow refusal. This counts instrument-to-auditor anchor mismatches, not demonstrated SCORECARD/SHONEN self-assessment mismatches. SCORECARD line 1166 is a historical round-23 measurement and remains historical. Calibration-axis fit is therefore not established; no calibration claim success or promotion is asserted. The before command aborts on reaching M11, after earlier mutants have run, and emits no completed JSON report. This repairs only the M-series portion of routed defect 2; PM08 remains outside the claim.

To claim calibration rather than disclose this miss would require a genuinely identified, revision-bound self-assessment mismatch and a counter comparing that statement with repository evidence, not a post-landing relabelling of this target.

## Files and scope

Repository file written: `.ufo/waves/round-25/a2-build/advice/CriticC1Calibration.md` only. Scratch writes were confined to `/fast/scratch/hyaku/kama-r25a2/CriticC1Calibration/`: `clone/`, `clone147/`, `mutants-full.json`, `mutants-full.err`, `mutants-full.exit`, `before147.json`, `before147.err`, and `before147.exit`. An exploratory shell also wrote `/tmp/ccal-aud-tip.py`, and Python compilation/grid runs generated temporary files outside the designated heavy-scratch root; this is a scope deviation, not claim evidence. No lane production edits, server child, consumer probe, package installation, or tool upgrade. Local repository sources only; no external source assertions.
