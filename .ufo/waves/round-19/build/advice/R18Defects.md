VERDICT: partial - D1 and D3 are fixed in committed text (D3's "they agree" needs scoping); D2's pins are corrected but the checkpoint Gate pin was dropped; D4 is a committed roster, not a dispatch record; an uncommitted in-place rewrite of round-18 `runs/commands.json` removes the official C2 entry from the working tree.

# R18Defects — routed round-18 defects 1–4 at the working tree

Source: `corpus/lessons/round-18-verifier-spotcheck.md:128-146`.
Anchor: lane HEAD `f1790e25b421f02596798ad665488b066541ae3a` (commit `f1790e2`), verified in snapshot `/tmp/kama-r19-R18Defects-snap4`. The lane advanced during verification (8bf99ca → 7229fa9 → 5b108c1a → f1790e2); each verdict is for the state named here.
Receipts: `/tmp/kama-r19-R18Defects/out/` — `verify-r18-defects.py` (run as `python3 out/verify-r18-defects.py /tmp/kama-r19-R18Defects-snap4`, exit 0, 53 commands, script sha256 9fff941d…), `verify-r18-defects.{json,txt}`, full write-up `R18Defects-evidence.md`.

| # | Defect | Verdict | Committed fix (file:line) | What is still wrong |
|---|---|---|---|---|
| 1 | Residual verdicts miscounted | FIXED (counts) | `corpus/lessons/round-18.md:389-392`; `LOG.md:1139-1140`, `LOG.md:1165-1169` | No pointer to `round-18.md:316-318` or `LOG.md:1122` (original text intact). The corrections call `assignments.json` a "dispatch record" (see D4). |
| 2 | S055 / Gate-row pointer drift | PARTIAL | tokens `round-18.md:417` (1c325b2), `:419` (1b85a24 + `1cb5a41b…`), `:421` (1b85a24); registry `registry/required-citations.json:2-22` with `doc` binding; `corpus/SOURCES.md:217-221` | Checkpoint Gate pin dropped: `b2043ba8…` (`VALID …/live/receipt-1.json`) appears in no doc or registry row, yet `round-18.md:400-401` says the Gate row "holds for live/ at 1c325b2". `SCORECARD.md:781` still cites `live-gate-{1,2,3}` as the measured VALID. |
| 3 | SCORECARD C2 command | FIXED (argv) | `SCORECARD.md:809-813`; `round-18.md:403-408` | "they agree" (`SCORECARD.md:812-813`, `round-18.md:407-408`) is over-broad: counts, exit, inputs and frozen witnesses match, but `tool.sha256` differs (`87cad1ca…` at 04:08:39Z vs `ac934794…` at 05:11:40Z). |
| 4 | Residual role split has no dispatch record | PARTIAL | `.ufo/waves/round-18/residual/assignments.json` (committed 7229fa9; roles at lines 8/13/18/23/28/33/38; totals 42–46) | Roster only: no spawn, dispatch or taskCall evidence; committed `residual/` has no such file; `ResidClaims.md` states no role, so the "critic" label is unsourced. |

## Checks run (exit codes; all from the snapshot)

- `python3 tools/citation-provenance.py` → 0: `required=3 found=3 verified=3 missing=0 mismatch=0`. `--json` → 0. `--selftest` → 0 (`selftest: ok (15 cases)`).
- Fail-capable before-state (copy-1 HEAD docs with the copy-1 tool) → 1: `missing=3`.
- `git cat-file -e c6dc46f:.ufo/waves/round-18/runs/commands.json` → 128 (absent). `1c325b2:` same path → 0. `eb78788:…/live-recovery/receipt-1.json` → 128; `1b85a24:` → 0.
- Committed verdicts (`ls-tree` + blob, seven advice files): 4 confirm / 3 partial; every `assignments.json` seat verdict matches (verifier: True).
- `git ls-files --error-unmatch -- …/assignments.json` → 1 at 8bf99ca (untracked), 0 from 7229fa9.
- Proposed registry with a restored checkpoint row (`out/proposed/`) → 0, `required=4 found=4 verified=4`.

## Fixes needed before the C1 claim holds

1. D2: restore the checkpoint Gate pin, `cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15)`, beside `round-18.md:401`, with a matching registry row (verified in `out/proposed/`).
2. D3: scope "agree" to counts and outcomes; name the two counter builds (`87cad1ca…`, `ac934794…`).
3. D4: relabel `assignments.json` as a roster, not a dispatch record (`round-18.md:393`, `LOG.md:1139-1140`, `LOG.md:1167-1169`), or add the residual dispatch and spawn evidence.
4. D1: add a pointer from the corrections to `round-18.md:316-318` and `LOG.md:1122`.
5. Restore round-18 evidence in the working tree to HEAD bytes (or move round-19 harness output out of `.ufo/waves/round-18/`) before committing. Uncommitted: `runs/commands.json` (HEAD `b8dadf30`, measured eb78788, 32 commands, `c2-survivors` present; working tree `c82dbfa0`, measured 7229fa9, 34 commands, `c2-survivors` absent), `live-recovery/receipt-{1,2,3}.json`, `runs/c1-*`, and `runs/*-selftest.stdout`.

## Other findings

- `SCORECARD.md:781` (C1 measured row) cites `live-gate-{1,2,3}.stdout` as the measured VALID. At the tip these describe `live-recovery/` receipts. Same drift class as D2, not covered by the erratum.
- `round-18.md:385` ("resolves to the bytes it describes") is not annotated in place.

## Limits

- The citation tool verifies bytes against digests and `doc` binding, not prose labels. The mislabelled gate token (`eb78788`/`b2043ba8`, labelled "recovery") passed it at 8bf99ca.
- Not checked: fleet report `.ufo/reports/round-18/kama.md` (commit 23bdc3f8, not in the lane).
- [INFERENCE]: the working-tree rewrite comes from a round-19 run of the round-18 harness (inferred from `measured_commit` 7229fa9 and the added `tree-grid-*` commands). "Corrected" for the 04:08Z JSON is supported by its `tool.sha256` (`87cad1ca`, the arm-combination build, killed 11 vs 9 pre-repair).
- Installs: none. Servers: none. Lane writes: this file only (per the trailer). Copy-side work is under `/tmp/kama-r19-R18Defects/out/`.
