VERDICT: confirm — delivered the C2 named-survivor counter with frozen witnesses and conservative inconclusive handling.

## Axes
- Calibration (C2; primary): reproducible named-mutation measurement, frozen-before/current-after, raw-run and input evidence.
- Operability (adjacent lane axis): isolated scratch runs, protected-port guard, process-group teardown; no production endpoints or lane tools were executed from the lane checkout.

## Delivered files
- New counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2Survivors-2/survivors.py`
  - SHA-256: `e0ba7ea4ab2f9f0daddec079360e3d6c1fe7d9512c9d09d0ebe753dc6154b28a`
  - New file, so no frozen-copy diff.
- This advisory: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C2Survivors.md`
- No other lane file was changed. No tools were installed or updated.

## Behavior and design
- CLI: `survivors.py --json --out PATH [--family a,b,c,d,e]`, with `--fault-controls`, `--check`, `--append-only`, and `--provenance` current-tool overrides, plus `--selftest`.
- Implements only the original 15 named round-17 items plus historical supplement FC-nonzero (16 total): H1/H2/H3/H5/H6/H7, four FC self-mutants, two append-only self-mutants, refused-count provenance, and three crash cases. FC-nonzero carries its prior round-17 frozen D/A 5/3 -> 6/2 evidence and its expected frozen outcome under this counter's current-check protocol. Fresh wave-2 mutants remain a separate denominator.
- Every mutation is an exact single-site source match on a scratch copy; missing, ambiguous, or uncompilable sites are reported, never silently skipped. The FC selftest kill is bound to the stable assertion `classifier: target-conjunct attribution: reason fault failed on verdict only`.
- Exit 2 alone and own-fault/cap/baseline failures are inconclusive, never kills. For FC self-mutants, a targeted selftest failure OR changed main-run decision is an independent kill; one conclusive kill wins over an inconclusive opposite arm, with both outcomes/reasons retained. Completed family results/counts survive later own faults; exit remains 2 and `partial_results`/`results_complete` expose coverage. AO kills require its named targeted assertion.
- Children run in process groups under a generated loopback-only bind guard, with lane-protected ports refused, port-0 redirected, teardown/straggler checks, and scratch cleanup.

## Verification and retained evidence
All commands were run in `/tmp/kama-r18-KamaR18.C2Survivors-2`.
- `python3 -m py_compile .ufo/waves/round-18/c2/survivors.py` — final exit 0.
- `python3 .ufo/waves/round-18/c2/survivors.py --selftest` — final exit 0, 65/65, including the historical denominator/provenance, stable classifier target, and partial-results-on-own-fault regressions; frozen mutation application and teardown checks passed. Earlier attempts (55/56 for an invalid fixture; 35/44 in a fresh clone missing ignored frozen inputs) were corrected before the prior 60/60 pass and this final run.
- Earlier command `python3 .ufo/waves/round-18/c2/survivors.py --family c,d --json --out /tmp/kama-r18-KamaR18.C2Survivors-2/scratch-cd.json` exited 0, before the family-b/history follow-ups. Scratch result: c `2 survived -> 2 killed`; d `1 miscount -> 1 correct`; overall `3 -> 0`, frozen witnesses matched, no own faults/inconclusive. Output SHA-256: `dd0b9c0bf36d60fd40ad15a568c16b8963c5bc61e742687ab987746e787db5a1`.
- That c,d run used current tool inputs with SHA-256: `check.py` `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`; `fault-controls.py` `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`; `sources-append-only.py` `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d`; `dispatch-provenance.py` `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f`. The new historical input hashes are `SurvivorUniverse.md` `7756f472cd0a31f526028033fcca719074dbd2520781a4eb668fd386bfad0c40` and `MutFaultControlsSelf.md` `c1d827c3f2f694e8091f8e764e1edb79ab73bac51ef5ae20acfded85d2520f44`; family b snapshots both.

## Limitations and blockers
- The counted universe is 15 original named items + 1 historical supplement = 16; fresh wave-2 is excluded. L1 reported its initial full run at `c6dc46f…`: FC-target and FC-f6cache had targeted selftest failures but main exit 2, and the composite was inconclusive. The independent-kill rule fixes that; L1 owns the requested family-b rerun. This seat did not run full current counts for a,b,e.
- Escape detection is nonce-based for the escaped-sleep child; the bind guard covers Python children only. Full counter execution is Linux-oriented (`/proc`, `ss`). No LSP endpoint was mounted; source references were inspected with direct reads/searches.
- No implementation blocker remains; L1 owns rerun/integration and post-integration verification.
