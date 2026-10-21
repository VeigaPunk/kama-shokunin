VERDICT: confirm - M1 drop-readlink-text mutant was killed by both assigned detectors; exact restoration passed.

# LinksGridMutants — scoped mutation probe
- Axes: operability (C2 symlink identity); calibration (bounded, evidence-backed coverage assessment). No score or admission judgment.
- Revision: `a29bb84abbb8b4d328f5970a89e448330a3a42ac`; isolated scratch `/tmp/kama-r21-LinksGridMutants-6/lane`.
- One mutant, per mutation-tester role: producer `tools/kama-llamacpp-live.py:225`, retaining the complete readlink map but hashing only link names.
- Original expression: `f'{n} -> {links[n]}\n' for n in sorted(links)`.
- Mutated expression: `f'{n}\n' for n in sorted(links)`.
- Grid source was unchanged: `tests/llamacpp-live/install-links-grid.py` exercised the producer on synthetic and real-tree mirror fixtures.
- Expected detector: `--selftest` and `--arm current` reject lost retarget sensitivity (exit 1), while pristine/restored bytes pass (exit 0).

## Executed commands and actual outputs
`mkdir -p /tmp/kama-r21-LinksGridMutants-6 && git clone -q --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r21-LinksGridMutants-6/lane && git -C /tmp/kama-r21-LinksGridMutants-6/lane checkout -q a29bb84abbb8b4d328f5970a89e448330a3a42ac` → exit 0; no output.
The following identical two commands ran at all three stages; cwd was the scratch lane, `PYTHONDONTWRITEBYTECODE=1`, timeout 180 seconds each. None timed out; every stderr was empty.
- S: `python3 /tmp/kama-r21-LinksGridMutants-6/lane/tests/llamacpp-live/install-links-grid.py --selftest`
- C: `python3 /tmp/kama-r21-LinksGridMutants-6/lane/tests/llamacpp-live/install-links-grid.py --arm current`

| Stage | S exit / stdout summary | C exit / stdout summary |
|---|---|---|
| Pristine | 0 / `selftest cases=12 failed=0` | 0 / `summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass` |
| M1 mutated | 1 / `selftest cases=12 failed=2` | 1 / `summary arm=current link=3/9 regular=2/2 type=1/1 null=0/1 wrong=6 status=fail` |
| Restored | 0 / `selftest cases=12 failed=0` | 0 / `summary arm=current link=9/9 regular=2/2 type=1/1 null=0/1 wrong=0 status=pass` |

Mutated S printed `FAIL current-catches-all` and `FAIL current-only-exit-0`; its other ten checks remained `ok`.
Mutated C changed these six cells from `current=changed` to `current=same`: `link-retarget-member`, `link-retarget-second`, `link-dangling`, `link-absolute-outside`, `link-dotdot`, `link-same-resolution-shortcut`.
Link deletion/addition/loop remained detected; regular/type controls remained 3/3 and null stayed quiet. Chain-problem diagnostics still appeared for dangling/outside/dotdot/loop; the grid rejected the identity regression independently of those diagnostics.
Full literal stdout, stderr, commands, exits, stage labels, and hashes: `detector-evidence.json` beside this report (six runs).
**Mutant verdict: KILLED by both detectors.** Neither baseline failure nor evaluation error was used as evidence of a kill.
Scope: no additional grid/producer mutant was run; this is not a general mutation-coverage or back-compat proof.

## Hashes and exact restoration
`sha256sum /tmp/kama-r21-LinksGridMutants-6/lane/tools/kama-llamacpp-live.py /tmp/kama-r21-LinksGridMutants-6/lane/tests/llamacpp-live/install-links-grid.py` ran pristine, mutated, restored; all exits 0.
- Producer pristine: `c05cd8bf36668b841246e9a8fdf9cf351b63a3d8423a154233230ceb69ae764e`.
- Producer mutated: `dcb4063c097b8a3b825a049c9277be1e79fe9432ef1e927fe3d90304aa07d4f0`.
- Producer restored: `c05cd8bf36668b841246e9a8fdf9cf351b63a3d8423a154233230ceb69ae764e` (identical to pristine).
- Grid all three stages: `4a538de21df3fdf301a168204a247f7f593c7297ee93829159cdadd67b7f8320`.
The original digest expression was restored before the final two detector runs and before scratch deletion.
`rm -rf -- /tmp/kama-r21-LinksGridMutants-6 && test ! -e /tmp/kama-r21-LinksGridMutants-6` → exit 0; no output; scratch removed.
No server/runtime/model was launched, no tool installed/updated, and no lane source/index or installed-tree bytes were edited; the grid mutated temporary mirrors only.
`git --version` → exit 0, `git version 2.56.0`; `python3 --version` → exit 0, `Python 3.14.8`.
Delivery is under the binding seat-only `build/out/LinksGridMutants-6/` scope; requested `build/advice/LinksGridMutants.md` was not written outside that allowed directory.
