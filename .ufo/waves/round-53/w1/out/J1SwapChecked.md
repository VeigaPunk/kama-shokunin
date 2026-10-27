# J1SwapChecked — round 53 C1 ablation: a library swapped after the member check

**Verdict:** the build's C1 instrument is load-bearing — with one byte of an unpacked archive
library flipped after the replay's member-digest check and before the live child starts
(fixture commit `936cba5c` on `c22602bd`), the frozen C1 counter at that commit reports
`bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=0/3 met=False`,
exit 1 (two runs, identical legs), and the replay itself reports
`code-mapping:digest:llama-b11909/libggml-rpc.so:4b6be3e1…->d4981257…` — the control behaves
exactly as the preregistration's C1 control requires (no shortcut, no defect in the frozen
counter; two low-severity observations only).

## What the control does (fixture clone, not the lane)

```
$ S=/fast/scratch/hyaku/kama-r53/J1SwapChecked
$ git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
$ git -C $S/lane rev-parse --show-toplevel   ->  /fast/scratch/hyaku/kama-r53/J1SwapChecked/lane
$ git -C $S/lane checkout -q c22602bd8d83ab26349d1087e916ca537ee4f9d1
$ <edit tools/kama-live-replay.py>            # 45 insertions, 1 file
$ git -C $S/lane -c user.name=fx -c user.email=fx@invalid commit -q -m "round-53 control J1SwapChecked: …"
-> 936cba5c4ba5cd8b6f3a97ee20105d97a6ee2311
```

The patch (`swap.diff`, 70 lines) is one new function plus one call:

- `tools/kama-live-replay.py:105` — `import struct`.
- `tools/kama-live-replay.py:426-457` — `ablation_swap(tree, member, delta)`: opens the
  library, reads `e_phoff`/`e_phentsize`/`e_phnum` from the ELF64 header, picks the first
  `PT_LOAD` with `PF_X`, takes `p_offset + delta` (delta `0x800`), and writes one byte
  `old ^ 0xFF` in place (`r+b`, same inode).
- `tools/kama-live-replay.py:491-497` — called **after** `extract()` and **after** the
  server member's digest check (`if … got_srv != want_srv: raise Refused(member-digest-
  mismatch)` at `:489-490`), i.e. after every check the replay performs at that point and
  before `sealed_member()`/the live child; the record lands in `res["ablation_swap"]`.

Chosen library: `libggml-rpc.so` — mapped `r-xp` by the server (build receipt
`.ufo/waves/round-53/measured/c1-build.out`, the 8 archive files list includes it) but not on
the CPU inference path.

## Evidence

### 1. The flipped byte is inside an executable range (host b11909 install)

```
$ readelf -lW /home/vgpnk/.local/opt/llama-b11909/libggml-rpc.so
  LOAD  0x012000 0x0000000000012000 … 0x01f469 0x01f469 R E 0x1000     <- PF_X PT_LOAD
$ readelf -SW … | grep -E '\.plt |\.plt\.sec'
  [11] .plt      PROGBITS 0000000000012020 012020 000fe0 AX
  [13] .plt.sec  PROGBITS 0000000000013020 013020 000fd0 AX
```
`0x12000 + 0x800 = 0x12800` is inside `.plt` (0x12020–0x13000); `objdump -d` shows the stub
`12800: f3 0f 1e fa endbr64 / push $0x7d / bnd jmp …`, so the flipped byte is the first byte
of a real instruction of PLT slot `0x7d` = `.rela.plt` entry at `0x3d018 + 0x7d*8 = 0x3d400`
= `_ZN8socket_t5flushEv` (RPC-only). Flip observed by the fixture unit check:
`{'member': 'llama-b11909/libggml-rpc.so', 'offset': 75776, 'old': 243, 'new': 12}` (75776 =
0x12800, 243 = 0xf3, 12 = 0x0c).

### 2. The server still starts with the flipped library

Probe on a copy of the host install (loopback 48913, stopped by me; `probe-startup.txt`):

```
host install  4b6be3e1f065e93a1641ab8d80c6b01cc4e614a273141144b0271442199f338d  libggml-rpc.so
flipped copy  d49812574c5ae99b9596b928aeedcae98c39bec0e664c5973ee054194bda5cdf
health ok after 200ms
GET /health -> {"status":"ok"}
GET /v1/models -> {"models":[{"name":"probe",…
POST /completion -> {"index":0,"content":" upon a time,","tokens_predicted":4,…
maps r-x line: 7f641b4fa000-7f641b51a000 r-xp 00012000 … <probe>/llama-b11909/libggml-rpc.so
stopped rc=0 ; no leftover probe server
```
The same holds inside the measured runs: all three bind replays reached `ready.json`, were
witnessed and had their running image observed (`detail: sealed b1|b2|b3 … a sealed memfd`),
and the counter's own memory read found the mapped library
(`detail: code b1: code: mapped bytes … (offset 00012000) of llama-b11909/libggml-rpc.so
differ from the archive member`). No `no ready.json`, no `live-exit` line.

### 3. Frozen counter at the swap fixture

```
$ sha256sum tools/round53-replay-code-audit.py
1a7a144204ba8b7ea9791706ab5fc90f1dab55db12a824a1af5ae89a81b75d8f   == preregistration C1 counter_sha256
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
    --repo $S/lane --tip 936cba5c4ba5cd8b6f3a97ee20105d97a6ee2311 --scratch $S --out $S/c1-swap.out
tip=936cba5c4ba5cd8b6f3a97ee20105d97a6ee2311
bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=0/3 met=False
… 
detail: code b1: code: mapped bytes 7f74e909d000-7f74e90bd000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
detail: code b1: code: replay own_code "{'verified': False, 'members': {'llama-b11909/libggml-cpu-zen4.so': …" is not verified with members
detail: code b1: code: rerun code_mappings has no entry …/work-b1/server/llama-b11909/libggml-rpc.so 103:05 1956863188 with the archive digest
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:184984 seals 15 is a sealed memfd with the frozen digest
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']
exit=1
```
Receipt: `c1-swap.out` (run 1), `c1-swap-rerun.out` + `c1-swap-rerun.rc` (run 3, `counter
exit=1`; `diff` of the header lines of the two runs: `identical-legs`). `bind=0` is the
counter's `bind_one` folding the replay's own refusal into the bind leg
(`tools/round53-replay-code-audit.py:592`, `replay exit 1 match False refused None`) — the
replay correctly declines to match; the leg the control targets is `code`, and it is 0 as
required. `newrow=1` here vs `newrow=0` in the base control
(`.ufo/waves/round-53/controls/base.c1.out`) is only the tip difference (the S506 row exists
from the build on).

### 4. The replay-level mismatch (the mechanism the counter checks)

Direct replay of `receipt-1.json` with the fixture tool (`replay-swap.json`,
`rerun-receipt-swap.json`), exit 1:

```
match False refused None
ablation_swap {'member': 'llama-b11909/libggml-rpc.so', 'offset': 75776, 'old': 243, 'new': 12}
mismatches:
  code-mapping:digest:llama-b11909/libggml-rpc.so:4b6be3e1f065e93a1641ab8d80c6b01cc4e614a273141144b0271442199f338d->d49812574c5ae99b9596b928aeedcae98c39bec0e664c5973ee054194bda5cdf
own_code.verified False members 7 host 13
rpc mapping: {'path': '…/rw/server/llama-b11909/libggml-rpc.so', 'dev': '103:05', 'inode': '281467432',
              'opened': True, 'size': 319776, 'uid': 1000, 'sha256': 'd49812574c5ae9…'}
```
`own_code.members` holds the other 7 archive libraries; `libggml-rpc.so` is absent because
its mapped file's bytes are not the member's. The rerun receipt's `code_mappings` entry is
`opened: True` with the **same path/dev/inode** as the mapped file and only the digest
different — so the swap is invisible to path- and inode-identity (the live tool's
`/proc/<pid>/maps` + `fstat` match at `tools/kama-llamacpp-live.py:809-816`) and caught only
by the digest comparison against the archive stream.

### 5. What the control isolates

Under the swap, `sealed=1`, `teardown=1` and `newrow=1` all hold: the round-52 legs
(memfd image, tree teardown) and the SOURCES row are insensitive to a library swapped after
the member check, and only the new `code` leg reports it. At the build the same counter read
8 archive libraries byte-equal (`measured/c1-build.out`, `code=1 coderuns=3/3 met=True`); at
the swap fixture `coderuns=0/3`. The swap therefore removes exactly one claimed mechanism —
"the code the witnessed server maps is the release archive's own bytes" — and the receipt
shows the counter detects it in the server's memory and in the replay's `code_mappings`
simultaneously.

## Frozen-counter observations (not defects; nothing edited — counters are frozen)

1. `tools/round53-replay-code-audit.py:622-623` — when the replay's `own_code.verified` is
   not true the counter sets `om = {}` and then prints one
   `code: replay own_code.members['<member>'] None != archive digest` line for every mapped
   member (8 lines per run here), which hides which member actually mismatched. No evidence
   is lost: the responsible member and the byte range come from the counter's own line
   `:433` and from the replay's `code-mapping:digest` line. A future counter could print the
   returned `members` as-is and flag only the members present with a wrong digest.
2. `tools/round53-replay-code-audit.py:592` — a code-identity defect also zeroes `bind`,
   because `bind_one` treats `replay exit 1 / match False` as a bind problem, so the two
   legs are not independent for this failure mode (this control was expected to be
   `met=False` either way). No fix proposed: the preregistration's target set for C1 is
   already a conjunction and the detail prefixes (`bind …` / `code …`) separate the causes.
3. Not a defect, recorded for the record: the unpacked library the server maps is owned by
   uid 1000 (the replay's own extract), and the counter accepts it — archive files are
   compared by bytes, not ownership; the preregistration limits ownership checks to host
   files. The fixture's flip keeps the inode, so ownership and inode checks cannot catch it.

## Limits / risks of this control

- The flipped stub is `.plt` slot `0x7d` (`socket_t::flush`). That the stub is never executed
  is [INFERENCE] from the IBT layout (calls go through `.plt.sec` at `0x13020`, `.plt` at
  `0x12020` is the resolver region) and is confirmed empirically by the server starting and
  completing a request with the flip in place (§2) and by all three measured bind replays
  reaching `ready.json` (§3). A one-byte change in `.text` of an RPC-only function would be
  a stronger "functional" swap; the detection result would be identical, since the counter
  compares whole executable ranges and the replay hashes the whole file.
- The control swaps the library **after** the replay's member checks, inside the replay's own
  extract; it does not model a swap that happens between the live tool's `code_mappings`
  read and the counter's `/proc/<pid>/mem` read (the preregistration's "read once" limit).
- Only `libggml-rpc.so` is swapped; the counter's REQUIRED set (server-impl, ggml, ggml-base,
  a CPU backend) is untouched, so this control does not test the required-name check.

## Environment / hygiene

- No packages installed or upgraded (pacman is paused; nothing was needed); tools used: the
  frozen counter, the fixture replay, `python3` stdlib, `readelf`, `objdump`, `curl`,
  `sha256sum`.
- No tracer was used around the counter; the counter was not edited
  (`1a7a1442…` = preregistration `counter_sha256`).
- One probe `llama-server` on loopback 48913, stopped (`stopped rc=0`); no surviving
  `llama-server` from this seat (`pgrep -af llama-server` shows only other seats'
  `K2Design`/`Sim1` processes). Scratch `$S` and its single clone removed at the end.

## Files written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/J1SwapChecked/`:
`J1SwapChecked.md` (this report, at `.ufo/waves/round-53/w1/out/J1SwapChecked.md`),
`swap.diff`, `swap-fixture.bundle` (1 787 bytes, `git bundle verify` ok, prerequisite
`c22602bd…`: re-creates the exact fixture commit `936cba5c` instead of the removed scratch
clone; sha256 `1ee823c31aab8484baf6b8059a2d5b6e174107ec00a61025862fe7213a51e8fa`),
`c1-swap.out`, `c1-swap-rerun.out`, `c1-swap-rerun.rc`, `c1-swap-rerun.stdout`,
`replay-swap.json`, `rerun-receipt-swap.json`, `replay-swap.stdout`, `probe-startup.txt`.
