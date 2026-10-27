# F20C2MutationSensitivity — C2 mutation sensitivity
Axes: calibration; operability. Frozen C2 claims/population unchanged; no lane edits.
15 expressions exercised against pristine counter + committed receipt; receipt_ok=True, 10 captures.
False positives: `c['ps-before'] == c['tags-empty']` → True/True; distinct identical-body captures pass via independent path mutation.
`bool(c['version'])`, `bool(c['show']['model_info'])`, `len(c['version']['version']) > 0` → True/True (vacuous content/quote relevance).
`c['version']['version']=='0.40.11'` on arbitrary quote, constant-branch and `or True` dressings also pass mutation gate.
True identical-chain comparison and cross-capture length equality rejected; slice-read silently rejected; missing key evaluates None.
W1 synthetic vacuous registry still scored met=True and all five control families rejected; controls do not prove semantic relevance.
Smallest correction: enforce quote↔capture/field relevance; reject equality comparisons on distinct captures with identical committed bodies.
Detailed 15-case expressions/evaluations/classifications: `w2/out/F20C2MutationSensitivity/findings.md`.
Evidence: W1 MT04 report/results, frozen controls, direct counter probe; command exit 0. No installs; disk /home 35%, /fast 27% used.
