# MT01Mutants — round85 w1

Axes: calibration + operability; assigned judgment axis: operability. Author-side mutation evidence only; no claim admission or integration.

## Subject and frozen before-control

Revision: `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`. The delivered `tools/round81-append-debt.py` is identical at original base `4401b72f64a2202fd30f26479c463e9b9d9cabad` and freeze. SHA256: `0b26cf34bf355a44b0ecd056f8f090de4fceeedf661dc78c08b0dcbae9ca7da6`.

Executed the frozen counter separately at both revisions:

`python3 <repo>/.ufo/waves/round-85/count.py c2 --repo <repo> --rev <revision> --work /fast/scratch/hyaku/kama-r85/MT01Mutants`

Both exited **1**, stderr empty, with M2/M3/M4 each exit0/pass31/fail0 and:

`DEBT_MUTANTS mutants=3 killed=0 escaped=3 invalid=0`

This measures the delivered file, not the historical spec fallback. The condition at delivered line266 occurs once; M4's bad()/continue block at lines267–269 occurs once. Exact M2/M3/M4 replacement strings were extracted from the frozen counter's AST assignments; no redefinition or counter weakening. Counter SHA256: `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`.

## Independent design and candidate checks

Three selftest-only additions, leaving grade behavior and existing wrong-subject/unresolvable arms intact:

- Equality: deletion79=subject79, accepting81>79, expected acceptance; kills comparison against accepting (M2).
- Direction: deletion80>subject79, accepting82>80, expected wrong-deletion finding; kills `<` instead of `!=` (M3).
- Exact summary: deletion78!=subject79; expect events2/accepted1/late0/pending1/unaccepted1/bad_rows1/bad_declarations0/out_of_population0 and ordered finding classes `[note-wrong-deletion-round,count-short]`. Kills M4's row being covered after the bad() call.

Independent candidate SHA256: `7a0e13d3acbf868e2df1f4ffd4e6d0c74150c3d8f7ca7f3b323ae8ebb919f246`.

EX01's output was initially absent. Following the explicit candidate-ready delivery message, copied its announced candidate once; no polling. EX01 candidate SHA256 independently measured: `7683c8b0cc9ae2e32546ac03eb6d58fe8a0de72e2d726aa3ed7dce6f799fb3c4`.

Every command was `python3 <owned-scratch>/build/<subject>.py --selftest`, with TMPDIR inside owned scratch. Full stdout/stderr, command vectors, exits, and hashes are in `receipts.json`.

| Mutant | Exact behavior change | Independent candidate | EX01 candidate | Owning EX01 failure |
|---|---|---|---|---|
| M1 | Replace dynamic subject binding with constant None (binding neutralized; not a dangling-variable crash) | exit1 pass31/fail3 | exit1 pass31/fail3 | note-subject-mismatch; note-deletion-above-subject; note-subject-exact-summary |
| M2 | Compare deletion!=accepting | exit1 pass33/fail1 | exit1 pass33/fail1 | note-deletion-equals-subject |
| M3 | Compare deletion<subject | exit1 pass33/fail1 | exit1 pass33/fail1 | note-deletion-above-subject |
| M4 | Remove only continue after wrong-deletion bad() | exit1 pass33/fail1 | exit1 pass32/fail2 | note-deletion-above-subject; note-subject-exact-summary |
| M5 | Drop None guard, so deletion!=None is a mismatch | exit1 pass25/fail9 | exit1 pass25/fail9 | note-subject-unresolvable |

All ten candidate mutant runs are **semantic kills**, not errors: exit1, valid completed nonzero-failure tally, named note-* failure, empty stderr. Both pristine candidates exit0/pass34/fail0. The delivered baseline separately preserves M1 (exit1/pass30/fail1) and M5 (exit1/pass22/fail9) semantic kills, while its frozen M2/M3/M4 survive. A surviving baseline mutant is a coverage finding, not a contract change.

## Restoration and limits

Each mutable probe file was restored in a finally block to its exact original bytes after every mutant; the same detector was then run on restored bytes. All 12 restored runs exit0 (delivered pass31/fail0; candidates pass34/fail0), and all before/restored SHA256 pairs match. Per-mutant changed-byte SHA256 hashes are retained in receipts. No source/sibling/index/jj edits, production commits, pushes, clones, installations, or live endpoints. Selftests create their own disposable committed fixtures under owned TMPDIR and assert their repository roots before committing.

Retained: independent candidate, copied EX01 candidate, delivered baseline, runner, and receipts. Scratch removed after retention; cleanup receipt records the result. The frozen final committed-candidate counter measurement and real-register/round84 checks remain L1/EX01 responsibilities, not claimed here.

The requested trailer path `.ufo/waves/round-85/w1/MT01Mutants.md` is outside the explicitly exclusive owned output directory. Accordingly this report is retained at `.ufo/waves/round-85/w1/out/MT01Mutants/MT01Mutants.md` for L1 to place; no unauthorized write at the trailer path.

Self-evaluation: accuracy4 (bounded mutation evidence, not claim admission); completeness4 (all assigned mutant checks covered, final integration deliberately outside scope); clarity4 (table links failures to mutations); actionability4 (runner and exact receipts retained); conciseness4 (raw outputs kept separately). Overall4.0. Improvement: L1 should use EX01's stronger exact summaries for all new arms rather than the independent candidate's separate exact-summary check. The user can distinguish exercised checks from integration responsibilities.
