# R06C2Semantics — Round 58 C2 review

Axes: operability and calibration. Scope: `tools/round58-c2-counter.py` at build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`; counter parsed from working bytes matching that committed version. LSP unavailable (`command -v lsp` produced no path); review used direct source inspection, not semantic-reference evidence. No files outside this seat output were changed.

## Finding — high: regex accepts a false calibration pointer

Attacks frozen C2 claim and its `CLAIM`/`INCL` parsing in the counter. `CLAIM` is an unanchored `search` and accepts any non-`)` token; it neither requires the full pointer phrase/row structure to be the sole pointer nor constrains TOKEN to a verdict token. `INCL` independently finds any `including round N` anywhere in the row. Thus appended contradictory prose can leave a valid matching prefix while asserting a different pointer/verdict elsewhere, yet the checker counts only the first matches and can report green. Concrete SCORECARD edit: append `; latest outside closure [...]`? No: exact viable edit is add a second claim-shaped clause to the calibration row after the real pointer, e.g. `; latest outside closure `corpus/lessons/round-56-verifier-spotcheck.md` (admitted), including round 57` while preserving the original round-57 rejected-honest-stop pointer and including phrase. The parser's first-match behavior checks only the valid first claim and first inclusion, so later contradictory claim is ignored. This violates singular, truthful pointer semantics even though the frozen textual predicate only requires it to carry a matching pointer; explicitly a robustness limit/survivor, not a retroactive change to the frozen predicate.

## Remaining scoped checks

`axes_row` selects the first exact top-level `## Axes` encountered and returns the first calibration row before the next `## ` heading; ordinary historical `## Axes` later do not replace it. This matches the documented first-section rule. It will fail closed (no row) if the first section has no calibration row, rather than search later; reasonable for that rule.

Manifest selection filters `type=closure`, `lane=kama`, and presence of `lane_round`, but dictionary construction overwrites duplicate records for the same lane_round in rounds-array order. A matching earlier closure can be overwritten by a correction-free/latest closure or vice versa; intended authority among duplicate closure rows is unspecified by the stated `(type,lane,lane_round)` lookup. This is a robustness limit, not established false green at the frozen manifest revision.

`maxN` derives from exact top-level tree entries matching the verifier-spotcheck filename regex and takes integer maximum; directory scope is `corpus/lessons/`. No false-green found in that derivation for ordinary git trees.

## Verification record

- `command -v lsp` — no output; LSP server unavailable.
- `git -C /home/vgpnk/Projects/shokunin show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:tools/round58-c2-counter.py` — exit 0; source matched the reviewed parser.
- Read-only inspection of counter lines 33–36, 50–60, 89–103 and frozen SCORECARD calibration row (working copy) performed. No counter execution or fixture mutation performed.
- No tools installed.