# RVW01ClaimC1 report

Advisory attack leaf; calibration evidence only, no admission or axis-score verdict.

## Delivered files / L1 landing instructions

- `attack.md`: severity-ordered findings, ten-fact breakdown, exact attack edits, target acceptance distinction, closure requirements and gaps.
- `evidence.txt`: exact measured commands, stdout, stderr and exit codes for the original committed counter/selftest and both scratch mutants. Git-show byte payloads are identified by SHA-256/length rather than duplicated as source listings.
- `reproduce.py`: runnable evidence generator; extracts committed base blobs only, creates private scratch copies, and records all six command results. Do not land either mutant into tools/.
- Named report trailer: `.ufo/waves/round-70/w1/out/RVW01ClaimC1.md`.

These are evidence artifacts, not production candidate files. Exact L1 production paths requiring genuine repair are SCORECARD.md, PROVINCE.md, and the canonical run-fact harness in tools/round41-scorecard-reconcile.py; the final correct edit depends on the actual round-70 landing tree and must preserve all reconciler checks. This seat supplies no tracked-file patch.

## Pasteable reproduction

Run from fleet root:

```bash
S=/fast/scratch/hyaku/kama-r70/RVW01ClaimC1
trap 'rm -rf -- "$S"' EXIT
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-70/w1/out/RVW01ClaimC1/reproduce.py
```

Observed driver exit 0; six inner exit codes, in order: frozen counter 1, frozen selftest 1, blunt counter 0, blunt selftest 1, surgical counter 1, surgical selftest 0. Driver exit 0 means receipt collection succeeded, NOT that C1 is green. Full exact inner commands/output are in evidence.txt.

Before measurements, read skill://godspeed and controls/freeze.txt. Axes: operability + calibration; calibration 7 < saturation 8, nudge inactive.

## Byte provenance

Base `6035e952c2521999e192d6f236331f265ac98392`.

| Source | Git blob (base and then-HEAD were identical) | SHA-256 |
|---|---|---|
| tools/round42-selfdesc-reconcile.py | a4b25792980946677bb3df76436cdb128961aeb4 | 3d9aff8f9c2236c2cb9337b08846da82de718bc1d9e8f1d283f1a71a03acd5c0 |
| tools/round41-scorecard-reconcile.py | ea0f7b3797745cea7f44fba0633bd1b365078936 | eff934a27b3e7525226c78e376ce774f3ab0b225ab98427b19201e5312176cd6 |

The final run used TMPDIR inside private scratch and distinct per-variant tool directories; no shared-file extraction races. Each original selftest checks its cloned fixture's toplevel before its first fixture mutation (canonical lines 220-224). No lane git mutation occurred.

## Exploratory errors (not acceptance evidence)

1. Initial bash call used a nonexistent scratch cwd; tool refused before execution: `Working directory does not exist: /fast/scratch/hyaku/kama-r70/RVW01ClaimC1`. No process exit code was supplied by the tool.
2. Initial extracted round42 counter lacked its companion round41 module, raised FileNotFoundError for `.../round41-scorecard-reconcile.py`, Python exit 1. Extracting both committed modules resolved setup; this crash is NOT the reproduced mismatch result.
3. Two early parallel extractions wrote the same r41 scratch file; one transient hash was the empty-file SHA-256. It was not treated as provenance. A subsequent single-writer extraction and independent git-show SHA check both yielded eff934a2...; final reproduction uses distinct directories and the same immutable captured blob.
4. `read xd://lsp` returned `No such tool`; there was no server on which to perform status/references/definition/diagnostics. Text fallback was used and is not semantic proof.
5. An exploratory shell command filtered the committed SCORECARD extract with grep/head, contrary to the preferred specialized search routing. Its output was not used as independent acceptance evidence; the final frozen counter output is the cited fact measurement.

## Limits and cleanup

No final landing tip, proposed production diff, full host census execution, live model endpoint, or resume/rerouting contract was verified. Census 22 + reconciler registration was measured by AST-reading the committed literal MEMBERS list. No tools installed or upgraded. Only private out artifacts and private scratch were written; the final bash EXIT trap removed all seat scratch.

## Self-evaluation

Accuracy 4: exact original/mutant evidence; no landing-tip conclusion. Completeness 4: all four assigned attack questions answered; no proposed landing diff supplied for review. Clarity 4: acceptance and selftest blindness distinguished; evidence is split across adjacent files. Actionability 4: pasteable replay and precise closure requirements; L1 still owns repair. Conciseness 4: ten-fact table and full receipts necessarily duplicate some summary. Mean 4.0. Highest-impact improvement is to apply these controls to the actual landing SHA once available; user should agree this is bounded attack evidence rather than admission.
