# X11ModelSwap — model-identity corner (round 50, lane kama, C1 operability)

**Verdict: claim-preserving, one unstated limit.** Both round-50 model-identity surfaces fail closed against a model path swapped before their sample (live tool: path-exact record; counter: content hash of the mapped file), but the binding is a single-instant sample: an in-place rewrite of the model file *after* that sample changes the held server's generated tokens (`, there was a little girl` → `########`) while the rerun receipt, `model_unchanged`, the counter's bind mapped-leg condition and the replay verdict all still pass. The preregistration limit covers only *identical* bytes rewritten in place; the different-bytes case is neither stated nor caught after the sample.

Measured against lane clone `/fast/scratch/hyaku/kama-r50/X11ModelSwap/lane` at `3b79eaddf38246c637cc7ba1a94ab363422876b6` (`tools/` identical to the build commit `97c864bead3ee4a2f629574e77263d33834ec98a`: `git diff --stat 97c864b HEAD -- tools/` empty), witnesses over the frozen receipt `.ufo/waves/round-48/c2/live/receipt-1.json`. No lane file was edited, no counter was edited, no pacman/uv/npm install was needed (python3 + curl only).

## Method

Two witnessed replays of receipt-1 (frozen `tools/kama-live-replay.py`, unmodified) plus one run driven through the frozen counter's own plumbing, and one direct live-tool run:

| # | command (scratch `S=/fast/scratch/hyaku/kama-r50/X11ModelSwap`) | exit |
|---|---|---|
| R1 | `python3 -I $S/lane/tools/kama-live-replay.py --receipt $S/lane/.ufo/waves/round-48/c2/live/receipt-1.json --work $S/work1 --out $S/replay1.json --witness-dir $S/wd1 --witness-timeout 300` | 0 (`match true`) |
| R2 | same with `--work $S/work2 --out $S/replay2.json --witness-dir $S/wd2 --witness-timeout 200` | 0 (`match true`) |
| GAP | `python3 $S/gap.py` — imports the frozen counter and calls its `start_replay`/`wait_ready`/`observe`/`gguf_tokens`/`load`/`reap` on the same receipt | 0 |
| LIVE | `python3 -I $S/lane/tools/kama-llamacpp-live.py --server $S/work1/server/llama-b11909/llama-server --model $S/dl/stories15M.gguf --model-sha256 61b50d45…704a --alias kama-r48-live --ctx 256 --threads 1 --out $S/live-different-model.json` | 0 |
| REFUSE | frozen replay over a receipt **copy** (`$S/rcpt/receipt-swapped-digest.json`, receipt's three model digests set to stories15M's) | 2 |

Per-state observer `$S/state.py` (included in evidence): reads `/proc/<pid>/maps` rows naming the model directory, `/proc/<pid>/cmdline`, `/proc/<pid>/fd`, `stat()` of the path, sha256 of the path, then calls the two frozen functions unmodified — `kama-llamacpp-live.py:678 model_mapping(pid, path)` and `round50-replay-bind-audit.py:309 mapped_model(pid, probs)`. `$S/observe.py` calls the counter's whole `observe()` (line 343), and `$S/gap.py` the counter's `start_replay`/`observe`.

Frozen digests: model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (1 185 376 B), server `35ac50fb…7d8d7ff0`; dev of the scratch xfs is `103:05`.

Scratch `/fast/scratch/hyaku/kama-r50/X11ModelSwap` (clone, work dirs, downloads) was removed after copying the evidence below; every artifact cited here lives under this out directory, and receipt `path` fields keep the scratch paths the tools recorded.

## What was on the wire (baseline, both runs)

R1: `ready.json {"port":36833,"pid":2592273}`; R2: `{"port":40709,"pid":3778577}`.
Baseline `state-baseline.json` / `state-D0.json`, e.g.:

```
maps  dev=103:05 inode=1489810867  .../work1/download/stories260K.gguf   (1 row, 0x7f6b880d0000-0x7f6b881ef000)
path  dev=103:05 inode=1489810867 size=1185376 sha256=270cba1b…
live  model_mapping -> {"mapped":true,"dev":"103:05","inode":"1489810867","sha256":"270cba1b…","size":1185376}
counter mapped_model -> ["103:05","1489810867"]   probs=[]
```

`/proc/<pid>/fd` holds no descriptor to the model (4 fds total): the server keeps no fd, only the mapping.

## Swap A — a copy of the same bytes at the path

**A1** (`mv STORIES STORIES.orig; cp -p STORIES.orig STORIES`, `state-A1.json`): the map's pathname follows the rename, not the mmap-time name — `…/stories260K.gguf.orig` (no `(deleted)`), dev/inode unchanged.

```
maps   .../work1/download/stories260K.gguf.orig   dev=103:05 inode=1489810867
path   dev=103:05 inode=1489245611  (new inode)   sha256=270cba1b… (same bytes)
live   {"mapped":false,"reason":"model-path-not-in-maps"}          # kama-llamacpp-live.py:696 (f[5]==want)
counter ["103:05","1489810867"] probs=[]                            # round50…:309-339 — still passes
```

Restore (`mv STORIES.orig STORIES`, `state-A0b.json`): identical to baseline, same inode → both surfaces pass again.

**A2** (`cp STORIES copy; mv -f copy STORIES` — the mapped inode loses its only link, `state-A2.json`):

```
maps   .../work1/download/stories260K.gguf (deleted)   dev=103:05 inode=1489810867
path   dev=103:05 inode=1554739526 size=1185376 sha256=270cba1b…   (same bytes, new inode)
live   {"mapped":false,"reason":"model-path-not-in-maps"}
counter null  probs=["no mapping of pid 2592273 is a file hashing to the frozen model (24 file mappings)"]
```

Both fail closed; the counter's reason is the same string it uses for a hash mismatch (see D2).

## Swap B — a different model at the path

**D1** in place, same inode, `stories15M` (98 MB) while the server was held (`state-D1.json`):

```
maps   .../stories260K.gguf  dev=103:05 inode=1892273526   (unchanged row)
path   size=98357920  sha256=61b50d45…704a
live   {"mapped":true,"dev":"103:05","inode":"1892273526","sha256":"61b50d45…704a","size":98357920}
counter null  probs=["no mapping … (24 file mappings)"]      # skipped by the 64 MiB window, round50…:335
GET /health 200 {"status":"ok"}
POST /completion 200  before: ", there was a little girl"   after: "########"      (8 tokens both)
```

**D2** in place with `stories260K + 4096 zero bytes` (1 189 472 B, inside the counter's 1 KiB–64 MiB window, `state-D2.json`):

```
path   size=1189472 sha256=37bcbbf4…4125
live   {"mapped":true,…,"sha256":"37bcbbf4…4125","size":1189472}
counter null  probs=["no mapping … (24 file mappings)"]      # rejected by the hash, round50…:337
```

**D3** original bytes copied back in place (`state-D3.json`): `sha256=270cba1b…`, `live` mapped true with the frozen digest, `counter ["103:05","1892273526"] probs=[]`, `/completion` back to `, there was a little girl`.

The running server reads the mapping at generation time: D1 and D3 are the same process, same argv, same inode, only the file content changed. `/proc/<pid>/cmdline` never changes in any state (the `-m` argument is the same path throughout):

```
…/work2/server/llama-b11909/llama-server -m …/work2/download/stories260K.gguf --alias kama-r48-live --host 127.0.0.1 --port 40709 -c 256 -t 1 --no-webui --offline
```

## The counter's own mapped check against a swapped-path server

`observe-O0/O1/O2.json` (frozen `round50-replay-bind-audit.py:343 observe`, 512-token vocabulary from the counter's own `gguf_tokens` on the frozen file):

| state | `mapped` | nonce round-trip | probs |
|---|---|---|---|
| O0 baseline | `["103:05","1892273526"]` | ok | `[]` |
| O1 path swapped in place (D2 bytes) | `null` | **ok** | `["no mapping of pid 3778577 is a file hashing to the frozen model (24 file mappings)"]` |
| O2 restored | `["103:05","1892273526"]` | ok | `[]` |

So the maps sample is a live hash of the path (it flips with the file and flips back), and in this state it is the *only* leg that catches a swap: the nonce check passes because the tokenizer in memory is still the frozen model's.

## What the receipt recorded (it is recorded before the hold)

`kama-llamacpp-live.py:2003` records `model_mapping` immediately after the probes and **before** `hold_for_witness` (`:2008`). R1's rerun receipt, while A1/A2/B/C all happened inside its hold:

```
`evidence/rerun-receipt-run1.json`: model_mapping {"dev":"103:05","inode":"1489810867","mapped":true,
  "sha256":"270cba1b…","size":1185376}  child_pid 2592273  witness.released true waited_ms 81580
  model_unchanged pre=post=270cba1b… passed:true   outcome pass
R1 replay: match true, live_exit 0, mismatches []
```

The inode the receipt names (1489810867) was unlinked by A2 mid-hold and did not exist at teardown; the receipt still reports `mapped:true` with the frozen digest, and the replay matches. That is the "recorded before the hold" property working as designed — and it is also the size of the blind spot. R2 (`rerun-receipt-run2.json`) is identical in shape: inode 1892273526, frozen digest, `model_unchanged` pre=post, witness released, `match true`, exit 0.

## What a re-run after the swap would record

Two answers, both measured:

1. **A re-run whose model path already holds a different model** (direct live-tool run, `live-different-model.json`, exit 0):
   `model_mapping {"mapped":true,"sha256":"61b50d45…704a","size":98357920,"inode":1754344581}` → `kama-live-replay.py:348` would emit `model-mapping:sha256:270cba1b…->61b50d45…`.
2. **A replay actually started after the swap** cannot get that far: `acquire()` (`tools/kama-live-replay.py:181-187`, via `fetch` `:130-142`) re-downloads to `dest.part`, `os.replace`s the path, then hashes; a receipt pinned to the swapped digest is refused (`replay3.json`, exit 2):
   `refused=digest-mismatch:stories260K.gguf:want=61b50d45…704a:got=270cba1b…` — so a swap left in the download directory is erased, and a swap carried by the network is caught.

## Finding F1 (limit gap, the one thing to act on)

**Measured gap.** The frozen `limits` entry says only: *"a file rewritten in place after mapping with identical bytes is indistinguishable"*. Different bytes in place are also indistinguishable **after** the sample — and they change the subject:

`evidence/gap-result.json` (frozen counter's `start_replay` → `observe` → swap → completion → restore → release):

```
ready            pid 311806 port 38193
counter_observe  mapped ["103:05","22397072"] nonce ok probs []
completion       ", there was a little girl"
swapped_in_place inode 22397072 size 98357920        # after the sample, before release
completion       "########"                          # the held server is now answering from other weights
restored / release
after_release    replay_exit 0 match true mismatches []
                 rerun model_mapping {"mapped":true,"sha256":"270cba1b…","dev":"103:05","inode":"22397072"}
                 rerun child_pid 311806 ; model_unchanged pre=post=270cba1b… passed
                 bind mapped-leg condition (round50-replay-bind-audit.py:474-475) == true
```

The counter sampled once (line 359) and never again; the receipt is pre-hold; `model_unchanged` is post-restore. A per-token generator run inside such a window is graded as a full pass. (In the same run a *second* sample would have failed: `counter.mapped_model` returned `null` while the swapped file was in place — D1/D2.)

**Proposed fix (next round; not applied here, counters/preregistration are frozen).** Sample twice, at the two ends of the hold:

- `tools/kama-llamacpp-live.py:326-373` `hold_for_witness`: after the wait loop ends, call `model_mapping(proc.pid, model_path)` again and return it (e.g. `'model_mapping_end'`), so a receipt records both ends of the hold; compare the two before accepting the run.
- `tools/round50-replay-bind-audit.py:440-495` `bind_one`: re-run `mapped_model(pid, probs)` (and the same `(dev,inode)` comparison) immediately before writing `release` (`round50-replay-bind-audit.py:455-456`), and require both samples; keep the post-release receipt/model_unchanged checks as they are. A swap concurrent with the second sample still wins that race, but it can no longer happen "for free" anywhere in the hold.

**Proposed `limits` sentence** (preregistration, round 50): *"C1's mapped check is a point-in-time sample taken once during the hold, and the live tool's `model_mapping` is recorded before the hold: a model file rewritten in place after either instant — with identical bytes, or with a different model (which changes the running server's generated tokens, observed by D1/D3) — is indistinguishable to the recorded evidence. A rewrite that lands before the sample is caught by the hash (or by the 64 MiB window) and fails closed."*

## Informational

- **F2 (asymmetry, fail-closed but a false-negative corner).** The counter's `mapped_model` binds *content* over any file-backed mapping (any pathname that stats to the same dev/inode and hashes to the frozen digest) — it passes after the model file is renamed away (A1). The live tool's `model_mapping` binds the exact `--model` path (`kama-llamacpp-live.py:696` `f[5] == want`) and reports `model-path-not-in-maps` in the same state. Both refuse different bytes; but a receipt recorded after such a rename would say `mapped:false` and the replay would refuse even though the mapped bytes are the frozen model. Adversarial-only, worth a sentence in the limits at most.
- **F3 (counter value window).** `round50-replay-bind-audit.py:335` skips any mapping outside 1 KiB–64 MiB. A model larger than 64 MiB could never satisfy the mapped leg (latent false negative); for the frozen 1.19 MB model the window only makes a swapped-in 98 MB file fail with the same "no mapping … hashes to the frozen model" text as a hash mismatch (D1 vs D2), i.e. the reason text cannot tell "swapped for a big model" from "swapped for a same-size model".
- **Positive.** The mapping is the live weight source, not a load-time snapshot: one process, same argv, same inode; D1 changed its tokens and D3 restored them. That is what makes a hash of the mapped file a meaningful identity check in the first place, and it is why post-sample substitution matters.
- No pacman/uv/npm/binary installs were performed. `stories15M.gguf` (98 MB) came from the same pinned HF revision as the frozen model and is only a swap operand; it is not cited as a model of record anywhere.
- Leftover check: `pgrep -af X11ModelSwap` empty at finish; the two `llama-server` processes visible on the host belong to sibling seats (`X8WitnessPort`, `X1Observe2`), not to this seat.

## Evidence index (`…/round-50/w1/out/X11ModelSwap/evidence/`)

| file | shows |
|---|---|
| `state-baseline.json`, `state-A0b.json`, `state-D0.json`, `state-D3.json` | baseline/restored identity: mapped true, frozen digest, both surfaces pass |
| `state-A1.json` | same bytes, new inode + rename-aside: maps pathname follows the rename; live `model-path-not-in-maps`; counter passes |
| `state-A2.json` | rename over the mapped inode: maps `(deleted)`; both surfaces fail closed |
| `state-B.json`, `state-C.json` | run-1 remainder (mapped inode already unlinked), restore, release |
| `state-D1.json`, `state-D2.json` | in-place different model: live record follows the path (wrong digest); counter rejects (size window / hash) |
| `observe-O0/O1/O2.json` | frozen `observe()` on baseline / swapped / restored server |
| `rerun-receipt-run1.json`, `rerun-receipt-run2.json`, `replay1.json`, `replay2.json` | the receipts' pre-hold `model_mapping`, witness release, `model_unchanged`, `match true` |
| `gap-result.json`, `gap-before.json`, `gap-after.json` | counter sample passes, tokens change, every recorded check still passes |
| `live-different-model.json` | what a live-tool re-run over a swapped model records (`61b50d45…`) |
| `receipt-swapped-digest.json`, `replay3.json` | a replay pinned to the swapped digest is refused at `acquire` (exit 2) |
| `state.py`, `observe.py`, `gap.py` | the drivers (frozen modules imported unmodified) |
