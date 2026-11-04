# RV01 — C1 baseline-receipt review

Axes: operability (assigned attack), calibration (accurate scope of the conclusion).

## Findings by severity

No demonstrated implementation defect against the frozen C1 predicate. One important residual limitation: **bound baseline does not mean the measured runtime is unchanged or that the measurement was reproduced**. The implementation deliberately accepts the former without checking the latter. Do not present its result as current-runtime verification.

Inspected addition: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-citation-baseline.py`, SHA-256 `024cda1aa2457e5f69ad5bbdbcabedd643180c7cf7efe1115db43ded62132c6f`. It appeared during this review; initial absence was not treated as a failed implementation. No tool source was edited or executed.

## 1. Population — AGREE

At population tip `b06cc612711560c53eef3ec21484c6963601262f` (the round-76 plan's base, NOT the round-77 lane tip), manually resolved the round-75 SCORECARD section and lesson. Full qualified `assimilation/` and `controls/` directory citations expand to their receipt-extension files. Fenced `.py` history is excluded and deduplicates to one quoted path. Nine explicit measured citations plus two directory-expanded receipts give eleven live paths.

All paths below are relative to `.ufo/waves/round-75/`:

| Paths | Recorded revision | Old class | Baseline rule |
|---|---|---|---|
| `measured/after/append-only-audit.out`, `c1-pins.out`, `c2-survivors.out`, `c3-append-accepted.out`, `population.out`, `selftests.out` | `c9ab73d842051db5f8320bced4357bf13cf14108` | 6 bound | 6 bound |
| `assimilation/summary.out`, `controls/freeze.txt` | no header in first five lines | 2 unbound | 2 unbound |
| `measured/before/c1-mutants.out`, `c2-mutants.out`, `c3-audit.out` | `dc58e51315e79d36df5fc530c95fbd3aecbf7593` | 3 shifted | 3 bound |

For each after receipt, `git merge-base --is-ancestor <header> <population-tip>` exits 0 and `git log --format= --name-only <header>..<population-tip>` contains no paths outside the frozen record-path set. For each before receipt, that delta includes `tools/round74-receipt-claim-binding.py`, `tools/pre-report-gate.py`, registry files and the new tools; the ordinary rule cannot bind it.

Each before receipt's first addition is `10f37171fb696c542586cbee96ea4a509ab74afc`; recorded revision ancestry exits 0. SHA-256 at addition equals SHA-256 at population tip:

- c1: `0a2326ec72ba585e26399ef01a3b955fa420319d1cef3dd2abb68af8df2a65ea`
- c2: `208e80344488de033199398c176c5b0c5145fc35033b52c3d44189b460cf3d29`
- c3: `e6aee72df7e88b94524030b8410fdb8508f4415315c026da4f11f5b20cc7fb7a`

Thus frozen ordinary scope gives `bound=6 unbound=2 shifted=3`; adding only the baseline exception gives `bound=9 unbound=2 shifted=0`. No ordinary delta-rule widening is needed or justified. Source evidence: new module lines 54–81 (only before paths get the exception), imported round-76 scope lines 122–179.

## 2. Laundering — AGREE that it admits changed-runtime historical receipts; DISAGREE with any stronger freshness reading

Concrete existing counterexample, no invented fixture required: `.ufo/waves/round-75/measured/before/c2-mutants.out` records `CONTROL_C2 killed=3 escaped=2`, including escaped conflicting-header and fifth-line-header mutants, at `dc58e513…`. Its introducing commit `10f37171…` also changes the measured runtime surface `tools/round74-receipt-claim-binding.py`: the git diff adds the `conflicting-headers` and `header-window-fifth-line` selftest arms (42 added lines). Thus the receipt predates a relevant runtime change **even at its introduction**, yet is bound by the baseline class.

All three guard legs admit this actual path:

1. `/measured/before/` path: yes (module lines 54–56).
2. Header revision ancestor of introduction: yes, `git merge-base --is-ancestor dc58e51315e79d36df5fc530c95fbd3aecbf7593 10f37171fb696c542586cbee96ea4a509ab74afc` exits 0 (lines 68–74).
3. Receipt byte stability: yes, equal c2 digest above at introduction and tip (lines 75–81). This compares receipt bytes, not runtime bytes.

Negative-leg inspection: replacing the path segment with `measured/after/` delegates to the old delta rule (would shift); naming descendant `b06cc612…` in the header fails ancestry to introduction (`git merge-base --is-ancestor b06cc612711560c53eef3ec21484c6963601262f 10f37171fb696c542586cbee96ea4a509ab74afc` exits 1); editing the receipt after introduction fails the digest comparison. The path and edit variants are static deductions, not executed fixtures.

This is intentional under plan lines 36–40 and 52–60: the old result describes pre-round state, not the new runtime. It becomes laundering only if a consumer upgrades `bound` to a current-runtime claim. No such stronger guarantee is established by C1. Likewise, stable committed bytes and header ancestry do not establish that the original command actually ran; the frozen predicate does not demand execution replay.

## 3. Predicate / counter / label — AGREE

Parsed `PREDICATE` as a literal AST constant without importing the tool. After whitespace normalization it exactly equals plan lines 45–61: **210 whitespace-delimited words each**. The expected summary label is **9 words** (prefix plus eight fields):

`CITATION_BASELINE round=75 fenced_quoted=1 live_citations=11 bound=9 unbound=2 shifted=0 nonreceipt=0 unclassified=0`

It occurs identically in both predicates. New module lines 84–97 reuse the original summary and render paths with the prefix changed; inherited summary keys at round-76 lines 116–119 have exactly that field order. Lines 198–209 retain the frozen population selection, explaining why round-75 is graded at `b06cc612…` rather than the current master. The full 210-word predicate is not itself printed; the printed receipt label is the summary embedded in it. Literal whole-sentence printing would be a different requirement from the declared CLI output.

## 4. Selftest arms — AGREE: none is statically incapable of failure

Inspected module lines 100–174; did not run its selftest.

| Arm | Actual changing condition / assertion |
|---|---|
| `fence-none-live` | SCORECARD has no live citation; only receipt citation is fenced in lesson; requires exit 2 and empty-population error. |
| `fence-unclosed` | Lesson opens but never closes fence; SCORECARD still supplies a live citation; requires exit 2 and unclosed-fence error. |
| `fence-live-nonreceipt` | Unfenced fully-qualified `.py` citation; requires exit 1 and nonreceipt finding. |
| `shift-tools` | Non-before receipt introduced, then `tools/input.py` changes; requires exit 1 and shifted finding. Removing the baseline-path guard would wrongly bind this case. |
| `baseline-bound` | Receipt retains original header/body across a tools change; requires exit 0 and exactly one bound. This tests the intended exception, including the runtime-staleness limitation above. |
| `baseline-nonancestor` | Rewrites header to a tools-changing descendant committed after introduction; requires exit 1 and specifically `baseline ancestry leg:`. Although receipt bytes also change, merely failing the byte leg cannot satisfy the required marker. |
| `baseline-edited` | Keeps original ancestor header, changes `measurement=1` to `measurement=2`; requires exit 1 and specifically `baseline sha256 leg:`. |

The fixture mutation is real for every named condition; outcomes compare return code AND a condition-specific marker. This is static load-bearing analysis, not empirical mutation certification. No arm is claimed executed or green here.

## Evidence, commands, and exits

Primary command receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/git-derivation.json`. Each entry records its complete absolute `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ...` command, stdout, stderr and exit. All commands there exited 0 except the deliberate negative ancestry check above (exit 1). It includes the raw record blobs, tree expansion, each receipt header/body, per-receipt delta, introductions and ancestry checks, plus the concrete runtime diff. These are plain read-only git commands, not calls to the new counter.

Derived data (successful Python Eval cells; no standalone process exit code exists):

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/population.json`: per-path manual classification, SHA-256 of git-show bytes and ancestry exit codes; generated from the commands in `git-derivation.json`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/identity.json`: `ast.parse` / `ast.literal_eval`, whitespace comparison, word counts and inspected-source hash; no tool import/execution.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/review-evidence.json`: summarized counts and guard matrix, with unexecuted variants marked as deductions.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/predicate.txt`: normalized frozen blockquote used in comparison.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-77/w1/RV01Reviewer/module-inspected.txt`: exact inspected module snapshot.

`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` exited 0: `7d60e2ab58866a0366937d61c9712483be57b36e`. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log master --diff-filter=A --format=%H\ %s -- plans/round-77-claims.md` exited 0 and identified that same freeze commit. An initial `--all` log also exposed unrelated historical additions; they were not selected as the lane freeze.

## Residual risk and verification gaps

LSP device unavailable: `read xd://lsp` returned `No such tool: xd://lsp`; therefore no semantic references/definitions/diagnostics claim is made. Text/source inspection is the explicit fallback. Initial module read returned `Path '/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round77-citation-baseline.py' not found`; later appearance allowed the full review above.

No new-counter CLI, selftest, gate, runtime launch, or fixture Git mutation was performed. L1 should run the declared counting command and selftest against the landed bytes; static arm review is not a substitute for those results. The frozen full population is reproduced by independent git evidence, not a copied counter result. Canonical serving-runtime routing, resume preflight and saturation changes are outside this C1 addition; none was exercised or inferred.

No installs, no changes outside the seat report directory, no source edits, no VCS mutations. Scratch `/fast/scratch/hyaku/kama-r77/RV01Reviewer` was removed after saving evidence; it contained no fixture repository.

Self-evaluation: accuracy 4 (source-based, no dynamic arm certification); completeness 4 (all four requested items covered, CLI intentionally not run); clarity 4 (historical binding explicitly distinguished from freshness); actionability 4 (named L1 checks); conciseness 4 (full per-arm and command provenance retained). Mean 4.0. Improvement: add L1's exercised CLI/selftest receipts, without recasting historical binding as runtime freshness. Expected user agreement: yes, with the dynamic-verification limitation explicit.
