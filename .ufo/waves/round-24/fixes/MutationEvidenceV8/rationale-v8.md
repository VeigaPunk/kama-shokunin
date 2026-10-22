# MutationEvidenceV8 — round 24 C1 mutation contract, inventory version 8 (final cleanup)

**Proposal only; no production file is edited by this seat.** Version 7 (and
versions 2–6) stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `b04c3812186e1a6c72f39f1a6a79adb632ee1efecaab687aa0d3c1fee7eed757` | 66844 |
| `promisor-mutants-v8.patch` | `b448b4ff584bdf3533354733cb0386a29bcf67b7b9b411c3f08a811318ef331e` | 49045 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged since V4) |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV8` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## What changed — one cleanup only

The agreed grid protocol carries **one canonical internal-error signal**:
the per-row boolean `internal_error`, true when the auditor's full stderr
contains the catch-all prefix `could-not-evaluate: internal:`. Version 8
therefore:

* keeps only that name: `INTERNAL_FLAGS = ("internal_error",)` — the two
  speculative aliases (`internal_errors`, `internal`) are **removed**, and
  no compatibility promise for another spelling is kept;
* keeps the stderr checks as **diagnostics on the same catch-all message**
  (the grid's stderr and each row's `stderr_tail`), with the comment
  corrected: the per-row boolean is authoritative, and a long message can
  push the prefix out of the kept tail;
* changes **nothing else**: the operators, their alternatives, their
  attribution, the class taxonomy, the aggregates, the harness-fault set,
  the attribution-before-credit rule, the review-only PM08 note, the
  legacy empty-selection guard and the fixture data are all unchanged from
  version 7 (the inventory file of version 7 stands; no data changed).

## API note

There is **no exported `run_inventory`**: the runner exposes `main(argv)`
and the existing `STUB_GRID` / `CANDIDATE` helpers, and the main agent's
wave-3 negative control uses those directly. No new API was added in this
version.

## Checks run

Source compile only (`python3 -m py_compile`): the file compiles. Per the
instruction, the selftest and the sensitivity pass were **not** re-run in
this version; version 7's receipts stand (34 assertions, 0 failed) and the
only difference is the flag list and its comment.
