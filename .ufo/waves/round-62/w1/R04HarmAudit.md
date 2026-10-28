# Round 62 axis-harm audit — R04HarmAudit

Diff audited: `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3..master`; `master` resolved to `65d7cad0fce90e34de37527cde22e97b63b118bf`.

## Regression instruments

- `python3 tools/round42-selfdesc-reconcile.py --repo . --tip master` (run from lane): exit 1. Output:
  ```
  tip=65d7cad0fce90e34de37527cde22e97b63b118bf
  r41=1 banner=1 planned=2 retired=1 saturation=1 caps=1 receipts=0 readme=0 province=1 rel=0 mismatches=8 maxN=62 met=False
  detail: r41 coverage run `python3 -c "import glob;print(len([f for f in glob.glob('corpus/knowledge/*.md') if 'engine-sides' not in f and 'processes' not in f]))"` no stdout line == '36' (exit 0)
  detail: banner: head lacks 'Latest measured round: 62'
  detail: planned: section does not name '### Planned (round 63)'
  detail: planned: no line '### Planned (round 63)' followed by a numbered item
  detail: retired: does not state '12 capabilities'
  detail: saturation: does not state 'first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, 61'
  detail: caps: head names ['append-only-audit', 'context-capacity-receipt', 'digest-ledger', 'gguf-declared-identity-replay', 'hexrun-census', 'instrument-agreement', 'live-llamacpp-lifecycle', 'live-ollama-lifecycle', 'live-receipt-replay', 'ollama-offline-evidence-replay', 'pin-watch', 'sources-registry'] != canon (round 62) ['append-only-audit', 'context-capacity-receipt', 'digest-ledger', 'gguf-declared-identity-replay', 'hexrun-census', 'instrument-agreement', 'live-llamacpp-lifecycle', 'live-ollama-lifecycle', 'live-receipt-replay', 'ollama-offline-evidence-replay', 'pin-watch', 'sources-registry']
  detail: province: PROVINCE.md lacks registry/ollama-live-claims-r61.tsv (capability live-ollama-lifecycle)
  ```
- Capability census available: `tools/hexrun-census.py` (located). Not run: no capability census command/arguments were specified by the assignment. No `tools/check-receipt.py` exists at the checked path, so its requested `--selftest` is unavailable.

## Findings

- **Actionable axis-harm/instrument inconsistency:** the existing reconciliation instrument returns `met=False` with eight mismatches, including claims of canonical capability mismatch and missing PROVINCE pointer (command output above). Yet `SCORECARD.md:3280-3293` contains the 12 listed capabilities including `live-ollama-lifecycle`, while the same instrument reports a different list and specifically says it lacks that row. This is evidence of a broken/stale reconciliation expectation or inconsistent source state, not proof that the capability census passes.
- **No axis score regression in the round diff:** `SCORECARD.md:3269-3270` records operability `8→8` and calibration `7→7`; neither regresses. Both outcomes remain explicitly `PENDING`.
- **PROVINCE untouched by diff:** `git diff ... -- PROVINCE.md` produced no diff. The reconciliation tool's `province=1`/detail is nonetheless a regression-instrument failure; the diff itself did not modify PROVINCE.
- **Sibling-surface scope:** diffstat lists 16 files, all confined to `.ufo/waves/round-62/`, `SCORECARD.md`, `registry/`, and `tools/`; no sibling-surface paths appear. The detailed list is captured in the diffstat from the audit command.

## Verification gaps

Capability census was only located, not executed. `check-receipt.py` is absent. No install/update was performed. Scratch was removed before report completion.
