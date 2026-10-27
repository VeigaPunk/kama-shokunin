# X1Rerun — independent C1 measurement (round 53, lane kama)

Verdict: **C1 reproduces independently at both tips.** At build `c22602bd8d83ab26349d1087e916ca537ee4f9d1` the frozen counter exits 0 with `bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True`; at base `4229ea1b9a789148dded1f159c20967d9a01373f` it exits 1 with `code=0 coderuns=0/3 newrow=0 met=False`, exactly as the base control. After masking only fields that vary by design, my receipts are **line-identical** to the L1's measured build receipt and to the frozen base control (0 residual diff lines in both). No defect found in the counter, the preregistration or the controls.

## Provenance of the instrument

The counter I ran is the frozen one, not a later edit:

```
$ for c in d01b2b6d48a54ffe0e475000737d3e302c62e28e c22602bd8d83ab26349d1087e916ca537ee4f9d1; do
    git -C $S/lane show $c:tools/round53-replay-code-audit.py | sha256sum; done
1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f  -
1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f  -
$ sha256sum kama-shokunin/tools/round53-replay-code-audit.py $S/lane/tools/round53-replay-code-audit.py
1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f  kama-shokunin/tools/round53-replay-code-audit.py
1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f  $S/lane/tools/round53-replay-code-audit.py
```

This equals `claims[0].counter_sha256` in `.ufo/waves/round-53/preregistration.json`, so the instrument hash matches the freeze. The build commit does not touch it:

```
$ git -C $S/lane diff --stat d01b2b6d… c22602bd… -- tools/ .ufo/waves/round-53/preregistration.json .ufo/waves/round-53/controls/
 tools/kama-live-replay.py   |  93 +++++++++++++++++++++++++
 tools/kama-llamacpp-live.py | 105 +++++++++++++++++++++++++++++++
 2 files changed, 198 insertions(+)
```

Only the two files under test changed. The counter docstring's PREDICATE sentence matches `claims[0].predicate` verbatim up to the trailing `bind=1 …` summary clause (the prereg appends it; the docstring puts it on the next line) — same sentence, no discrepancy.

Clone used for both runs (read-only lane, shared clone into my scratch):

```
$ S=/fast/scratch/hyaku/kama-r53/X1Rerun; export TMPDIR="$S"
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
$ git -C "$S/lane" rev-parse --show-toplevel   → /fast/scratch/hyaku/kama-r53/X1Rerun/lane
$ git -C "$S/lane" cat-file -t c22602bd…  → commit ; cat-file -t 4229ea1b…  → commit
```

## Commands, outputs, exit codes

Run 1 (build):

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
    --repo "$S/lane" --tip c22602bd8d83ab26349d1087e916ca537ee4f9d1 --scratch "$S/s1" \
    --out .ufo/waves/round-53/w1/out/X1Rerun/c1-build.out
tip=c22602bd8d83ab26349d1087e916ca537ee4f9d1
bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 met=True
detail: counter vocabulary: 512 tokens from its own download
detail: counter archive: its own download, frozen digest
detail: code b1: 8 archive files (8 executable ranges) byte-equal in /proc/<pid>/mem to the counter's own archive, 13 root-owned host files; recorded in code_mappings and own_code: ['libggml-base.so.0.27.0', 'libggml-cpu-zen4.so', 'libggml-rpc.so', 'libggml.so.0.27.0', 'libllama-common.so.0.7.0', 'libllama-server-impl.so', 'libllama.so.0.7.0', 'libmtmd.so.0.7.0']
detail: bind b1: pid 2564218 port 44979 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode <INODE> recorded, nonce 'kama witness <NONCE>' round-tripped
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:<PAGES> seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
   … b2, b3 identical in every must-agree field …
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']
exit=0
wall: 20.0 s
```

Run 2 (base):

```
$ python3 … --tip 4229ea1b9a789148dded1f159c20967d9a01373f --scratch "$S/s0" \
    --out .ufo/waves/round-53/w1/out/X1Rerun/c1-base.out
tip=4229ea1b9a789148dded1f159c20967d9a01373f
bind=1 sealed=1 code=0 teardown=1 newrow=0 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False
   … per run b1..b3, 9 code-failure lines each (see failure mode below) …
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 0 rows new since base; 0 name proc_pid_mem(5): []
exit=1
wall: 18.8 s
```

Both `--out` files carry the counter's own summary lines plus the `exit=<code>` marker I appended per the seat spec (`c1-build.out:16`, `c1-base.out:64`). Receipt hashes:

```
4b16a8bbc0047c90883fa2516d7135f53189e306082fcaff02e5212724354549  c1-build.out
4edaba82bfd4e2dfa739f30ad84589c46eda63601a3b0211c87387abb40d04e3  c1-base.out
```

Base failure mode (matches the control's, 9 lines per run — 1 verdict + 8 mapping rows):

```
detail: code b1: code: replay own_code 'None' is not verified with members
detail: code b1: code: rerun code_mappings has no entry …/work-b1/server/llama-b11909/libggml-base.so.0.27.0 103:05 <INODE> with the archive digest
detail: code b1: code: replay own_code.members['llama-b11909/libggml-base.so.0.27.0'] None != archive digest
   … the same pair for libggml-cpu-zen4.so, libggml-rpc.so, libggml.so.0.27.0, libllama-common.so.0.7.0,
       libllama-server-impl.so, libllama.so.0.7.0, libmtmd.so.0.7.0   (b1, b2, b3)
```

## Agreement, field by field

Comparison method: strip my `exit=` line and the L1's leading `$ python3 … (tip=…)` harness echo, then mask only fields that vary by design — pid, port, inode (both `inode N` and the bare `103:05 N` token), nonce hex, memfd page count (`00:01:N`), scratch path/`r53c1-*` temp tag, teardown elapsed seconds — and unified-diff. Result: **0 residual diff lines for build, 0 for base** (`c1-compare-build.diff`, `c1-compare-base.diff` are both empty).

| Field | X1 build | L1 measured build | X1 base | L1 base control | Must agree? |
|---|---|---|---|---|---|
| tip | c22602bd… | c22602bd… | 4229ea1b… | 4229ea1b… | yes — **agree** |
| bind/sealed/code/teardown/newrow | 1/1/1/1/1 | 1/1/1/1/1 | 1/1/0/1/0 | 1/1/0/1/0 | yes — **agree** |
| bound / sealedruns / coderuns | 3/3, 3/3, 3/3 | 3/3, 3/3, 3/3 | 3/3, 3/3, 0/3 | 3/3, 3/3, 0/3 | yes — **agree** |
| met / exit | True / 0 | True / 0 | False / 1 | False / 1 | yes — **agree** |
| archive libraries (8 names, per run) | libggml-base.so.0.27.0, libggml-cpu-zen4.so, libggml-rpc.so, libggml.so.0.27.0, libllama-common.so.0.7.0, libllama-server-impl.so, libllama.so.0.7.0, libmtmd.so.0.7.0 | identical list, identical order | none (leg fails) | none | yes — **agree, byte-identical list** |
| `N archive files` / `N executable ranges` | 8 / 8 per run | 8 / 8 per run | — | — | yes — **agree** |
| root-owned host files | 13 per run | 13 per run | — | — | yes — **agree** |
| mapping dev | 103:05 | 103:05 | 103:05 (failure rows) | 103:05 | yes — **agree** (dev is stable; host files deliberately not dev-compared) |
| memfd dev:major:minor / seals | 00:01 / 15 | 00:01 / 15 | 00:01 / 15 | 00:01 / 15 | yes — **agree**; page count varies (below) |
| teardown descendants / alive / port | 3 / [] / refuses ok, 0.10 s | 3 / [] / refuses ok, 0.10 s | same | same | yes — **agree** |
| newrow rows / names | 4 rows, 1 name `['\| S506 \|']` | 4 rows, 1 name `['\| S506 \|']` | 0 rows, 0 names | 0 rows, 0 names | yes — **agree** |
| pid | 2564218, 2572474, 2578085 | 2530913, 2533254, 2534535 | own | control's | no — fresh processes |
| port | 44979, 35115, 44793 | 40803, 44241, 46589 | own | control's | no — allocated per run |
| inode | fresh per unpacked tree | 2026804480, 1081905417, 550154254 | fresh per tree | control's | no — new unpacked tree each run |
| nonce | random per run | random per run | random | random | no — per-run challenge |
| memfd page count | 190317/183179/193086 | 184936/181765/190304 | 186868/199009/184947 | 186761/201881/186762 | no — live RSS-scale footprint |
| reply path / temp tag | `…/X1Rerun/s{0,1}/r53c1-*` | `…/L1/{ctl,meas-build}/r53c1-*` | — | — | no — scratch location |

So the fields that establish the claim — the eight archive library names, the 8→8 executable-range count, the 13 root-owned host files, the mapping dev, the sealed-memfd dev and seal set, teardown behaviour, the newrow counts and the leg summary — all agree exactly; only process-lifetime identity (pid/port/inode/nonce/memfd pages/scratch path) differs, which is by design and is exactly the set that must not be expected to reproduce.

## Risks / notes (no defects)

- **Foreign process left running:** `pgrep -af llama-server` shows pid 2671885 on 127.0.0.1:59307 with a model at `/fast/scratch/hyaku/kama-r53/J2SwapUnchecked/` — that is another seat's server, not mine (my two runs each reported teardown with `alive []` and their scratch work dirs are empty). Left running per the no-service-mutation constraint; flagged for the L1 in case it is a leaked fixture.
- The L1 receipts carry one extra leading line (`$ python3 … (tip=…)`) that is a harness echo, not counter output; my files therefore have 16/64 lines against 17/65. Not a defect, just a shape difference future comparisons should strip (I did).
- Preregistered limits apply unchanged to this reproduction: host libraries (libc, libstdc++, …) are only classed root-owned/not-writable, their bytes are not compared; non-executable mappings are out of scope; and bytes (not provenance) are compared, so a replay fed by the host's byte-identical install would also meet.
- No tool installs or upgrades were needed (no pacman, no uv/npx); nothing outside my scratch and out dir was written.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/c1-base.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/c1-compare-build.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/c1-compare-base.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/ref-L1-measured-c1-build.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun/ref-L1-controls-base-c1.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/X1Rerun.md` (this report)
