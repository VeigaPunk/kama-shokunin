VERDICT: confirm — delivered the C2 named-survivor counter with frozen witnesses and conservative inconclusive handling.

## Axes
- Calibration (C2; primary): reproducible named-mutation measurement, frozen-before/current-after, raw-run and input evidence.
- Operability (adjacent lane axis): isolated scratch runs, protected-port guard, process-group teardown; no production endpoints or lane tools were executed from the lane checkout.

## Delivered files
- New counter: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/out/KamaR18.C2Survivors-2/survivors.py`
  - SHA-256: `2af03fed6ccb0b09e30061828843372cb503d5d5e3afae846bc3f5473ced411d`
  - New file, so no frozen-copy diff.
- This advisory: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/build/advice/C2Survivors.md`
- No other lane file was changed. No tools were installed or updated.

## Behavior and design
- CLI: `survivors.py --json --out PATH [--family a,b,c,d,e]`, with `--fault-controls`, `--check`, `--append-only`, and `--provenance` current-tool overrides, plus `--selftest`.
- Implements only the named round-17 H1/H2/H3/H5/H6/H7, three fault-controls self-mutants, two append-only self-mutants, refused-count provenance case, and three crash cases. Each mutation is an exact single-site source match on a scratch copy; missing, ambiguous, or uncompilable sites are reported, never silently skipped.
- Frozen witness vectors are explicit: H1/H2/H3/H5/H6/H7, FC-target/FC-f6cache/FC-f0gate, and AO-opened/AO-blank survived; frozen refused-count miscounted; frozen nested-json/bigint/escaped-sleep were accepted. A witness mismatch returns inconclusive/exit 2, not a favorable result. Fresh wave-2 mutants are explicitly excluded from this named denominator.
- Exit 2 and own-fault/cap/baseline failures remain inconclusive, never kills. For family a, exit 1 or accepted>0 kills only after a clean unmutated baseline (exit 0, accepted 0, healthy F0); exit 2 is inconclusive. For FC/AO self-mutants only the targeted selftest assertion is a kill; unrelated failures and own faults are inconclusive. Raw child argv, exit status, stdout/stderr digests and tails, tool/advice/evidence digests, outcome reasons, and frozen-witness comparison are recorded.
- Children run in process groups under a generated loopback-only bind guard, with lane-protected ports refused, port-0 redirected, teardown/straggler checks, and scratch cleanup.

## Verification and retained evidence
All commands were run in `/tmp/kama-r18-KamaR18.C2Survivors-2`.
- `python3 -m py_compile .ufo/waves/round-18/c2/survivors.py` — exit 0 (final run).
- `python3 .ufo/waves/round-18/c2/survivors.py --selftest` — initial exit 1 (55/56) from an invalid synthetic edit fixture; correcting it yielded exit 0 (56/56), then the exit-1/accepted-zero classifier case yielded exit 0 (57/57). On the final clean clone, the first attempt lacked ignored frozen inputs and exited 1 (35/44); after restoring the frozen set and pinned evidence, final `--selftest` exited 0 (57/57). It rechecked the four frozen-tool hashes, bind guard, child teardown, and frozen known answers.
- `python3 .ufo/waves/round-18/c2/survivors.py --family c,d --json --out /tmp/kama-r18-KamaR18.C2Survivors-2/scratch-cd.json` — exit 0. Scratch-only integration result: c `2 survived -> 2 killed`; d `1 miscount -> 1 correct`; overall named count `3 -> 0`. Frozen witnesses matched; no own faults or inconclusive outcomes. Output SHA-256: `dd0b9c0bf36d60fd40ad15a568c16b8963c5bc61e742687ab987746e787db5a1`. This is a scoped c,d check, not L1's official full counter measurement.
- Current tool inputs copied into the clone and observed by SHA-256: `check.py` `12367de62efafa02641c4acb497e50f1be5019b54879a9ac6da13efd5f8071a5`; `fault-controls.py` `58dac1f71346734532bddc60a2d20f95f640406e924b1aec00a0b750feed072a`; `sources-append-only.py` `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d`; `dispatch-provenance.py` `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f`.
- c,d integration JSON also pinned the round-17 refused-result evidence (`refused-result-1.json`: `7167991932f619a6b805346338799bf6500d0a86387269e95b4c09e208041a5c`; `attempts.json`: `85e4ba72793a4e76478fd227dbe27d8ff9f8cdd1639ef4814f313bd0c1`) and recorded the round-17 advice digests for the two exercised families. Its current c/d tool hashes match the values above.

## Limitations and blockers
- The counted universe is the explicitly named round-17 set; it does not discover unknown mutants or include fresh wave-2 mutants.
- This seat's one current-tool integration run exercised only c,d. Families a,b,e were covered by the final selftest's frozen known-answer cases and pure classifier tests, but their full frozen/current counts remain for L1's official run.
- Escape detection is nonce-based for the escaped-sleep child; the bind guard covers Python children only. Full counter execution is Linux-oriented (`/proc`, `ss`).
- No implementation blocker remains. L1 owns integration, the official full measurement, and post-integration verification.
