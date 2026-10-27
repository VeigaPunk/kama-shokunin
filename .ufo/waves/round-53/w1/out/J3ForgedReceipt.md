# J3ForgedReceipt — round-53 C1 ablation: everything lies except memory

**Verdict: PASS (predicted ablation).** With the live tool forced to record the archive member's digest for every unpacked tree file and the replay flipping one byte inside an executable range of an unpacked library after its member check, the frozen C1 counter still passes bind, sealed, teardown and newrow, and passes its own receipt/`own_code` cross-checks — and fails only on its `/proc/<pid>/mem` byte comparison, on all three receipts: `bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False`, counter exit 1. The memory leg is load-bearing: nothing else in the counter can see the swapped bytes.

## What the counter can and cannot see (contract)

`tools/round53-replay-code-audit.py:57-60` states the predicate: the mapped bytes are read *by the counter from `/proc/<pid>/mem`* and compared with *the counter's own download* of the release archive. Its code leg (`:600-608`) additionally checks the rerun receipt's `code_mappings` entries and the replay's `own_code` (`:616-630`) — both of which a forged receipt satisfies. The single comparison that reads the running process is `:431-433`:

```
                compared += 1
                if got != want:
                    probs.append(f"code: mapped bytes {f[0]} (offset {f[2]}) of {member} differ from the archive member")
```

The control therefore forges everything a receipt can carry and leaves only the process's memory disagreeing.

## Fixture (own `git clone --shared`, fixture identity)

- Clone: `/fast/scratch/hyaku/kama-r53/J3ForgedReceipt/lane` (`git rev-parse --show-toplevel` verified equal before the commit), checked out at the build commit `c22602bd8d83ab26349d1087e916ca537ee4f9d1`.
- Fixture commit: `bba18258a079b6823fc070daeb966190738e0cc5` ("fixture (J3ForgedReceipt ablation C1): forge archive digests; flip one libggml-rpc.so text byte after the member check"), parent `c22602bd…`, committed as `fx <fx@invalid>`.
- Two files, additive (`fixture.patch`, 118 insertions, 3 deletions):

1. `tools/kama-llamacpp-live.py` — the receipt lies about the bytes:
   - `:775` `_archive_member_digests(archive, members)`: sha256 of each named regular member read straight from the archive stream the tool was handed (`--server-archive`).
   - `:803` `code_mappings(pid, archive=None, tree=None)`; `:869-878` replaces the recorded `sha256` of every *opened* mapping under the unpacked tree with its archive member's digest. `dev`, `inode`, `size`, `uid` stay the ones `fstat()`/`/proc/<pid>/maps` gave, so the counter's `path/dev/inode` entry check still matches.
   - `:2361` the call site passes `args.server_archive` and the tree root derived from `server_real` minus the `--server-member` path components.
2. `tools/kama-live-replay.py` — the tree lies about the bytes:
   - `:229` `_exec_segment(fh)`: first `PT_LOAD` with `PF_X` from the ELF64 program headers.
   - `:259` `FLIP_DELTA = 0x1d000`, `:262` `flip_unpacked_library()`: XOR one byte at `p_offset + delta` in `r+b`, `fsync`.
   - `:513` called once, right after the server member's digest check (`:505-507`) and extraction, on `<member dir>/libggml-rpc.so`.
   - `verify_code()` itself is **unmodified** (`c22602bd:tools/kama-live-replay.py:305`); it hashes archive members by name (`:293`) and therefore agrees with the forged digests.

## The flip byte (deviation stated)

`readelf -lW` on the archive's `llama-b11909/libggml-rpc.so` (`elf-flip.txt`): the one executable `PT_LOAD` is `Offset 0x012000 FileSiz 0x01f469 Flg R E`. The operator's example `+0x800` into that segment is file offset `0x12800`, which the section table puts inside **`.plt`** (`.plt 0x12020 + 0xfe0`), where a corrupted stub can break an imported call. The fixture instead uses `+0x1d000` → file offset `0x2f000`, inside `.text` (`.text 0x13ff0 + 0x1d46a`), in a `std::_Hashtable<…>::_M_rehash` instantiation the CPU path never runs. Byte `0x08 -> 0x09`. `libggml-rpc.so` is mapped by the server (the build receipt lists 8 archive libraries including it) but unused by the CPU backend, so the server still starts.

## Frozen counter run (command + output)

```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-replay-code-audit.py \
    --repo /fast/scratch/hyaku/kama-r53/J3ForgedReceipt/lane \
    --tip bba18258a079b6823fc070daeb966190738e0cc5 \
    --scratch /fast/scratch/hyaku/kama-r53/J3ForgedReceipt/c1 \
    --out .../out/J3ForgedReceipt/c1-forged.out
exit=1
tip=bba18258a079b6823fc070daeb966190738e0cc5
bind=1 sealed=1 code=0 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=0/3 met=False
detail: counter vocabulary: 512 tokens from its own download
detail: counter archive: its own download, frozen digest
detail: bind b1: pid 2862508 port 44283 exe+listen+tree+env+mapped ok, child_pid joined, mapping dev 103:05 inode 1150293061 recorded, nonce 'kama witness d8ba3a14b64005ec' round-tripped
detail: code b1: code: mapped bytes 7f073127a000-7f073129a000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
detail: sealed b1: running image '/memfd:llama-server (deleted)' 00:01:193112 seals 15 is a sealed memfd with the frozen digest, recorded in server_exe and own_server
...
detail: code b2: code: mapped bytes 7fc500edb000-7fc500efb000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
...
detail: code b3: code: mapped bytes 7f9b43f96000-7f9b43fb6000 (offset 00012000) of llama-b11909/libggml-rpc.so differ from the archive member
...
detail: teardown: invoker SIGKILLed with 3 descendants; after 0.10 s alive [] port refuses ok
detail: newrow: 4 rows new since base; 1 name proc_pid_mem(5): ['| S506 |']
```

Full text in `c1-forged.out` (identical `c1-stdout.txt`); wall 23.5 s. **The only `code:` problems are the three `mapped bytes … differ` lines** — no `rerun code_mappings has no entry`, no `own_code … is not verified`, no `not-a-member`, `foreign`, `unopened` or `no-archive-library`. Bind/observe, sealed memfd, teardown and the S506 row are unaffected, so the server did start and behave.

## Independent confirmation that only memory disagrees

A standalone replay of the same fixture (not part of the counter, same commit; `smoke/replay.json`, `smoke/rerun-receipt.json`, `digests.txt`):

- archive member `llama-b11909/libggml-rpc.so` sha256 `4b6be3e1f065e93a1641ab8d80c6b01cc4e614a273141144b0271442199f338d`;
- the extracted (flipped) tree file sha256 `22b24bee23953c3d42f2c042b2d4106f7874c5c22f65ea1ebfbd3389ef32725a` — **the tree file is not the member**;
- the rerun receipt's `code_mappings` entry for that path records `4b6be3e1…` — **the member's digest**;
- `own_code.verified = True`, `own_code.members['llama-b11909/libggml-rpc.so'] = 4b6be3e1…`, replay `match=True`, `mismatches=[]`.

So both receipt-level checks the counter makes are satisfied by a lying tool; only a reader of the process's memory catches the diversion.

## What this control establishes, and what it does not

- Establishes: C1's `code` leg is not satisfiable by receipt/replay agreement alone. Forging the tool's digest and swapping a real code byte in an unpacked archive member while keeping the server healthy yields `code=0` with the exact diagnostic, so the counter's claim (the witnessed server executes the archive's own bytes) rests on `/proc/<pid>/mem`, as the predicate says.
- Limits (inherited, preregistration `limits`): only executable mappings are compared, host libraries are classed by ownership only, and the read happens once while the server is held.
- The control deliberately does not touch host files, the sealed memfd image, the model mapping or the teardown, so the other legs are expected to stay green (they did).

## Housekeeping / notes

- No lane file modified: edits live only in the fixture clone; lane git is untouched (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain tools/` shows the integrator's own in-flight `M tools/kama-live-replay.py` and `M tools/kama-llamacpp-live.py`, pre-existing, not mine — my measurement used `git archive` of my own commit, so the lane worktree did not influence it).
- No `llama-server` of mine left (`pgrep -af llama-server` shows only a peer's `K2Design` hold, not this seat's).
- Scratch `/fast/scratch/hyaku/kama-r53/J3ForgedReceipt` removed after collecting artifacts; no installs, no pacman, no services.
- Reproduce: clone the lane, `git checkout c22602bd…`, `git apply fixture.patch`, commit with a fixture identity, then run the counter with `--repo <clone> --tip <new commit> --scratch <empty dir>`; expect `code=0 met=False` exit 1 with the three `differ` lines.
