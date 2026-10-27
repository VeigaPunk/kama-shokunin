# J2SwapUnchecked — round 53 C1 ablation: swap after the check, replay's code check removed

**Verdict: the control behaves as designed — with `verify_code()` made a liar and `libggml-rpc.so` swapped after the member check, the ablated replay reports a matching rerun (`bind=1`, exit 0) yet the frozen C1 counter still reports `code=0 met=False` (exit 1), because both independent legs fire on all three receipts: the counter's own `/proc/<pid>/mem` byte comparison and the rerun receipt's `code_mappings` digest comparison.**

## Control construction

- Lane clone: `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane`, detached at the build `c22602bd8d83ab26349d1087e916ca537ee4f9d1` (`git -C $S/lane rev-parse --show-toplevel` = `$S/lane`, exit 0).
- Fixture commit `8536f6581b931b395169e17123dcd2de6908d2d4` (identity `fx <fx@invalid>`, `tools/kama-live-replay.py` only, +44/−25; full commit in `fixture-commit.txt`, plain diff in `fixture-swap-unchecked.diff`). Changes, all in the clone:
  - `tools/kama-live-replay.py:230` `swap_library()`: parses the ELF64 program headers of an unpacked library and rewrites one byte (`^0xff`) `delta` bytes into the first `PT_LOAD` with `PF_X`.
  - `tools/kama-live-replay.py:471` `swap_library(tree, need["server.member"], "libggml-rpc.so", 0x800)` — called immediately after the server member digest check (`:466-467`) and before the live child starts, so the swap is after the check and lands in the tree the loader maps.
  - `tools/kama-live-replay.py:339-354` `verify_code()`: the round-53 digest loop (build text at `:305`) is replaced by a lying return — `{"verified": True, "members": member_digests(archive, want), "host": [...]}`, i.e. every tree mapping is reported as its archive member at the archive digest without reading the file that was mapped.
- Flip site, from `readelf -lW` on the same b11909 library: the `R E` `PT_LOAD` is `Offset 0x012000 FileSiz 0x01f469`; `0x12000 + 0x800 = 0x12800`, inside `.plt` (`readelf -SW`: `.plt` at `0x12020`), byte `0xf3 -> 0x0c`. libggml-rpc.so is mapped by the loader but unused on the CPU path.

## Flip keeps the server startable (pre-test)

Copied `/home/vgpnk/.local/opt/llama-b11909` to `$S/inst`, flipped the same file offset, ran `$S/inst/llama-server --model model.gguf --host 127.0.0.1 --port <ephemeral> --ctx-size 64 --threads 1`:

```
ready True pid 2671885 exit None
7f2b69957000-7f2b69977000 r-xp 00012000 103:05 2096523142  .../inst/libggml-rpc.so
r-x 7f2b69957000-7f2b69977000 off 00012000 bytes@0x12800 0c0f1efa
```

`/health` returned 200 with the flipped byte mapped at the flipped offset. Server torn down (`pkill -f J2SwapUnchecked/inst/llama-server`; `pgrep` empty afterwards). The counter run below repeats the same start under the real replay and reaches ready in all 3 receipts (`bind b1/b2/b3 ... ok`).

## Counter run

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
  --repo $S/lane --tip 8536f6581b931b395169e17123dcd2de6908d2d4 --scratch $S --out $OUT/c1-j2.out
# exit 1
tip=8536f6581b931b395169e17123dcd2de6908d2d4
bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False
```

Frozen counter unchanged: `sha256sum tools/round53-replay-code-audit.py` = `1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f`, equal to `preregistration.json` `claims[0].counter_sha256`. `bind=1` is the ablation working: the patched replay accepted the swapped tree (`own_code.verified` true, its own result exit 0), so only the counter's independent legs fail it.

## Detail lines that catch it (all three receipts, verbatim from `c1-j2.out`)

```
detail: code b1: code: mapped bytes 7f6b22eb8000-7f6b22ed8000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
detail: code b1: code: rerun code_mappings has no entry /fast/scratch/hyaku/kama-r53/J2SwapUnchecked/r53c1-6zr2689h/work-b1/server/llama-b11909/libggml-rpc.so 103:05 815290869 with the archive digest
detail: code b2: code: mapped bytes 7f8f07ce6000-7f8f07d06000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
detail: code b2: code: rerun code_mappings has no entry /fast/scratch/hyaku/kama-r53/J2SwapUnchecked/r53c1-6zr2689h/work-b2/server/llama-b11909/libggml-rpc.so 103:05 955385118 with the archive digest
detail: code b3: code: mapped bytes 7ff224304000-7ff224324000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
detail: code b3: code: rerun code_mappings has no entry /fast/scratch/hyaku/kama-r53/J2SwapUnchecked/r53c1-6zr2689h/work-b3/server/llama-b11909/libggml-rpc.so 103:05 1821327599 with the archive digest
```

Line 1 of each pair is `code_observe()`'s own comparison of the mapped range with the counter's own download (`tools/round53-replay-code-audit.py:426-433`); line 2 of each pair is `bind_one()`'s comparison of the live tool's recorded mapping digest against the counter's archive member digest (`:624-629`), which the replay cannot forge because the live tool, not the replay, records `code_mappings`. All other legs held with the swap in place: `sealed b1/b2/b3` (sealed memfd, frozen server digest), `teardown` (3 descendants gone in 0.10 s, port refuses), `newrow` (S506 names proc_pid_mem(5)).

## Findings

1. **Minor, cosmetic (frozen counter): duplicated `code:` prefix.** Every `code_observe()` problem already begins `code: ` (`tools/round53-replay-code-audit.py:433`, `:628`), and the detail loop prefixes `code {tag}: ` again (`:656`), yielding `detail: code b1: code: mapped bytes ...`. Shown by the run above. Proposed fix (not applied; counter frozen) in `proposed-counter-detail-prefix.diff`: `detail.append(f"code {tag}: {pr.removeprefix('code: ')}")`. Display only; `code=0`/`met=False` unaffected.
2. **Limit observed: the replay-verification leg is forgeable.** `bind=1` was earned by an ablated replay whose `own_code` claims verification it did not perform. The claim's "the replay names them as verified" sub-clause is not independently provable from the receipt; what carries C1 in this control is the counter's own `/proc/<pid>/mem` read plus the live tool's recorded digest, both of which are outside the replay's control. Worth recording in the round-53 lesson limits; the ablation is still caught.
3. **Granularity:** the memory leg reports the whole `r-xp` row (`0x20000` bytes at `offset 00012000`), not the differing byte. A single-byte swap therefore shows as a range difference. This is the documented row-level comparison, not a false pass.
4. **Control dependency:** the swap site is only observable while the loader maps `libggml-rpc.so`; it does here (`c1-build.out` lists it among the 8 archive libraries, and the detail lines above name it). If a future loader stops mapping the RPC backend, this control loses its teeth without failing — choose a mapped library for round-54 reruns.

## Files written (absolute)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/c1-j2.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/c1-j2.run.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/commands.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/fixture-commit.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/fixture-swap-unchecked.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J2SwapUnchecked/proposed-counter-detail-prefix.diff`

Scratch `S=/fast/scratch/hyaku/kama-r53/J2SwapUnchecked` (clone, flipped install copy, model) removed with `rm -rf`; no J2 llama-server or replay process left (`pgrep -af` filtered on the scratch path: empty).
