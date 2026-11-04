# EX01DebtControls — round85 w1

Axes: calibration + operability; assigned implementation improves operability. Author-side evidence only, no claim admission.

## Delivered

- Complete replacement: `tools/round81-append-debt.py` beneath this report's directory; SHA256 `7683c8b0cc9ae2e32546ac03eb6d58fe8a0de72e2d726aa3ed7dce6f799fb3c4`.
- `receipts.json`: exact commands, working directory, TMPDIR, true exit codes, complete stdout/stderr, revision and hashes.
- Only selftest additions/harness: 39 inserted lines. All legacy31 arms remain; grade behavior and frozen counter unchanged.
- New arms: `note-deletion-equals-subject` (subject79/deletion79/accepting81, verdict0), `note-deletion-above-subject` (subject79/deletion80/accepting81, verdict1 with binding finding), `note-subject-exact-summary` (subject79/deletion78/accepting81).
- Literal full expected summaries checked for all three arms. Both rejection controls require events2/accepted1/late0/pending1/unaccepted1/bad_rows1/bad_declarations0/out_of_population0 and exactly `[note-wrong-deletion-round, count-short]`. Equality requires late1/unaccepted0/bad_rows0 and no findings. Removing the binding `continue` cannot pass merely by preserving verdict1.

## Exercised checks

Read the full round85 claims including untruncated line21 before implementation. Source freeze: `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd`. One isolated clone, detached at freeze; guarded `git -C ... rev-parse --show-toplevel` equalled the exact candidate root before checkout/add/commit. Candidate commit: `c54c93a6cff9c04fbd76eba88c850f73ba15e6db`.

All execution used cwd `/fast/scratch/hyaku/kama-r85/EX01DebtControls` and TMPDIR there (except initial clone before that execution environment was constructed). Detailed argv arrays and outputs are in `receipts.json`.

1. `python3 /fast/scratch/hyaku/kama-r85/EX01DebtControls/candidate/tools/round81-append-debt.py --selftest`: exit0, `APPEND_DEBT_SELFTEST pass=34 fail=0`, empty stderr.
2. `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/count.py c2 --repo /fast/scratch/hyaku/kama-r85/EX01DebtControls/candidate --rev c54c93a6cff9c04fbd76eba88c850f73ba15e6db --work /fast/scratch/hyaku/kama-r85/EX01DebtControls/work`: exit0, `DEBT_MUTANTS mutants=3 killed=3 escaped=0 invalid=0`, empty stderr.
   - M2: exit1, equality arm fails; pass33/fail1.
   - M3: exit1, above-subject arm fails; pass33/fail1.
   - M4: exit1, above-subject and exact-summary arms fail; pass32/fail2. Exact-summary mutant wrongly changes late0→1/unaccepted1→0 and loses count-short; harness rejects it despite verdict remaining1.

Frozen counter SHA256: `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`.

Receipts retained before cleanup. `rm -rf -- /fast/scratch/hyaku/kama-r85/EX01DebtControls` (cwd `/fast/scratch/hyaku/kama-r85`) completed exit0, no output. No installs, production edits, external changes, services, or production commits. No other build/lint/test commands run.

## Integration / limits

L1 alone integrates and owns final committed-master gates. Copy staged tool to production and rerun the pristine selftest and frozen c2 at the integrated revision. No LSP tool is mounted in this seat, so supported-symbol navigation was unavailable; direct source reads used instead. No semantic refactor was attempted.

Mutation reviewer `MT01Mutants-9` was discoverable and directly messaged with candidate path, expectations and measured outputs; independent reviewer work remains advisory. Report is retained inside the owned output directory: the requested trailer path `.ufo/waves/round-85/w1/EX01DebtControls.md` is outside the contract's write-only owned directory, so L1 must place it there if needed. No implementation blockers; final integration/claim admission not performed here.
