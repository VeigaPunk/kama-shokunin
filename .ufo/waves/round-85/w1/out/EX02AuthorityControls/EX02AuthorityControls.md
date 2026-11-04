# EX02AuthorityControls — round85 w1

Axes: calibration (primary), operability. Author-side advice only; no admission or production changes.

## Deliverables

- `authority-controls.py`: stdlib-only executable importing the unchanged frozen counter. Requires explicit `--repo` and owned `--work` paths; disables import bytecode. Reads actual stale first authority and calibration cells verbatim from base `4401b72f64a2202fd30f26479c463e9b9d9cabad`. Expected cells are selected independently from literal base lines, not by the function under test.
- `receipts.txt`: complete command transcript, true exits, full actual stale cells, fixture commit revisions, exact CLI outputs and control verdicts.

Requested report trailer `.ufo/waves/round-85/w1/EX02AuthorityControls.md` is outside the owned directory. Per explicit write-only contract, this report is retained here for L1 integration instead.

## Executed evidence

Command (exit 0):

```sh
TMPDIR=/fast/scratch/hyaku/kama-r85/EX02AuthorityControls PYTHONDONTWRITEBYTECODE=1 python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-85/w1/out/EX02AuthorityControls/authority-controls.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --work /fast/scratch/hyaku/kama-r85/EX02AuthorityControls
```

Result: `AUTHORITY_CONTROLS pass=27 fail=0`.

Every case checked exact `cells()` outputs, exact imported `calibration()` output/return, and full frozen c1 CLI output/exit/stderr against a committed minimal fixture. All 81 comparisons passed. Git root guard executed before each fixture add/commit; only one private scratch repository was initialized, no clones. Every CLI was pinned to its fixture commit, not a moving branch. All source git commands were read-only.

Coverage:

- Actual stale first cells: `facts=2 mismatches=2 gate=0 closure=0`, exit 1.
- Repaired synthetic live cells: `facts=2 mismatches=0 gate=1 closure=1`, exit 0. The positive fixture's receipt wording is synthetic fixture content, not a claimed production receipt.
- Correct witness tokens in unrelated text, including later fake authority and calibration lines, leave actual stale cells unchanged.
- For each 0/1/2/3-space correction heading: later fake witnesses cannot green stale cells; a fake FIRST authority before the real stale cell is excluded; fake-only authority cannot replace missing live authority; corrected live cells after the closing heading still pass.
- Four-space pseudo-heading does NOT open correction exclusion; the following repaired cells remain visible and pass.
- Missing authority, missing calibration row, wrong arms, wrong revision, wrong failed count, stale phrase alongside correct tokens, and wrong closure all fail as expected.

Frozen commit: `7d3c987c0e3a6ee62673c18c26ecdd22f39e5cdd` (also observed source HEAD). Counter bytes matched that commit exactly before import. SHA256: `e550a24786d7c3e073c549a8dcb03d456579696ba92a7f2a15ea2e7c04bedca9`. The freeze identifier is a git revision, not a file digest.

Environment: Python 3.14.8, git 2.56.0. No tools installed or updated. No LSP device is exposed in this seat; symbol work used direct frozen source reads. No build, lint, formatter, unrelated test, endpoint sampling or source acquisition performed.

## Findings / limitations

No counter defect was observed in these 27 assigned controls. This is bounded fixture evidence, not a proof over arbitrary Markdown, and not admission of production C1. The script deliberately requires the base and freeze commits to remain available. L1 owns integration and the real committed-master predicate. Suggested integration check is the exact command above using L1-owned scratch via `--work`, followed by the frozen c1 production predicate.

The first setup command failed before execution because its requested cwd did not yet exist; the directory was then explicitly created from the fleet cwd. An exploratory import initially wrote Python bytecode beside the counter; that artifact is removed during cleanup and subsequent imports disable bytecode. Neither affected counter source bytes. Fixture commits were confined to owned scratch and removed after retaining receipts.

Self-evaluation (advisory): accuracy 4/5 (bounded rather than universal Markdown coverage); completeness 4/5 (report staged inside owned directory instead of forbidden trailer); clarity 4/5 (full transcript is intentionally verbose); actionability 4/5 (requires retained history and git); conciseness 4/5 (retains detailed receipts for reproducibility). Overall 4.0/5. Improvement: L1 should preserve this report and script under its chosen integrated paths and run its own committed-master gate. User agreement expected because all limitations and true exits are explicit.
