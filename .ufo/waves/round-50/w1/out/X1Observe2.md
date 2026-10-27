# X1Observe2 - independent outside observer of the round-50 C1 witnessed replay (kama)

**Verdict: all six assigned bind legs hold for all three witnessed replays at
`97c864bead3ee4a2f629574e77263d33834ec98a` (18/18, my own observer, no counter code read),
and no leg disagrees with the frozen C1 counter (`bind=1 teardown=1 newrow=1 bound=3/3
met=True`). One discrimination finding: the assigned env surface read at the server pid
(`/proc/<server>/environ`) also passes at the base `26ecba64...`, so it cannot separate the
pre-build leak from the build; the live tool's environ and the planted sitecustomize marker
do, and with those added my observer also fails at the base - same verdict as the counter.**

Observer: `.ufo/waves/round-50/w1/out/X1Observe2/observer.py` (sha256
`f51e107a34fa72dc34258a63ef25c25be3ddc3267a899676398d4a79155e70ea`), written without reading
`tools/round50-replay-bind-audit.py`. Comparison tool: `compare.py` (sha256
`d2ab5282ed8f52e6295b7d613e003dd6f4c76bc73bedd0e3943ea2745b6ba1d1`). The counter I ran is
the frozen one: `sha256sum tools/round50-replay-bind-audit.py` =
`ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`, equal to
`preregistration.json:19` (`counter_sha256`).

## 1. What was run (clone at the measured tip, scratch under /fast/scratch)

All commands from `$S=/fast/scratch/hyaku/kama-r50/X1Observe2`, `TMPDIR=$S`, one shared clone
(`git clone --shared <lane> $S/lane`, `git -C $S/lane checkout -q <tip>`; `rev-parse HEAD` =
`97c864bead...`, `rev-parse --show-toplevel` = `$S/lane`).

| # | command (abridged) | exit | result |
|---|---|---|---|
| 1 | `python3 observer.py --repo $S/lane --tip 97c864bead... --receipts round-48/c2/live/receipt-{1,2,3}.json --scratch $S/obs --out $S/observer.json` | 0 | `met=True`, 3/3 replays, 6/6 legs each (wall 7.5 s) |
| 2 | `python3 tools/round50-replay-bind-audit.py --repo $S/lane --tip 97c864bead... --scratch $S/counter --out $S/counter.json` | 0 | `bind=1 teardown=1 newrow=1 bound=3/3 met=True` (wall 14.9 s) |
| 3 | `git -C $S/lane checkout -q 26ecba64...` then observer with `receipt-1.json` only | 0 | six assigned legs pass, **extended verdict false** (wall ~3 s) |
| 4 | counter from the tip tree against `--tip 26ecba64...` | 1 | `bind=0 teardown=0 newrow=0 bound=0/3 met=False` (wall 44.6 s) |
| 5 | `python3 compare.py --observer $S/observer.json --counter $S/counter.json --base-observer ... --base-counter ...` | 0 | `disagreements=0` (`compare.md:17`) |
| 6 | `python3 probe-tokenizer.py` (own loopback port, killed after; evidence of tokenizer/`/completion` conventions) | 0 | `probe-tokenizer.out` |

Then `git -C $S/lane checkout -q 97c864bead...` restored the clone HEAD (asserted by
`rev-parse HEAD`). No pacman, no installs; python3 3.14.8, git, curl, ss as installed; the
b11909 binary used only through the lane tools plus three direct loopback probes on ports
38421/38423/38427 that I started and killed (`pgrep -af 'llama-server|kama-.*\.py'` shows no
process carrying my scratch path `/fast/scratch/hyaku/kama-r50/X1Observe2`; entries carrying
other seats' scratch paths were visible during the wave and are not mine).

## 2. Method (what each leg measures, from outside the replay)

The observer starts `tools/kama-live-replay.py` under `python3 -I` (as the counter does) with
`KAMA_R50_CANARY=observer-<hex>` and a `PYTHONPATH` pointing at a `sitecustomize.py` that
appends its pid to a marker file (planted canary vectors). `--witness-dir`/`--witness-timeout
120` make the live tool publish `<wdir>/ready.json {port,pid}` and hold the server
(`tools/kama-llamacpp-live.py:326`); the observer reads that file and checks while the server
is up, then creates `<wdir>/release`.

- **exe** (`observer.py:422`): `/proc/<pid>/exe` readlink, hash the file, compare with the
  receipt's `server.sha256`.
- **listen** (`observer.py:429`, `listening_inodes` at `:111`): parse `/proc/net/tcp` and
  `/proc/net/tcp6` for `LISTEN` sockets on the announced port, take their inodes, and map
  inode -> pid over `/proc/*/fd` (`socket_owners` at `:134`). Pass only if the listening inode has exactly one
  owner and that owner is the server pid from `ready.json`.
- **tree** (`:438`, `ancestry` at `:90`): walk `/proc/<pid>/status PPid` from the server up to
  pid 1; pass only if the replay pid the observer started is in the chain.
- **mapped** (`:447`, `model_maps` at `:172`): collect `/proc/<pid>/maps` lines whose pathname
  is an absolute `*.gguf` path, re-`stat` it and require the maps `dev`/`inode` to equal
  `st_dev`/`st_ino`, reopen the path `O_NOFOLLOW`, hash it, and compare with the receipt's
  `model.sha256`. A `(deleted)` mapping fails.
- **env** (`:466`): `/proc/<pid>/environ` split on NUL; no key may be `KAMA_R50_CANARY`.
  `:477` additionally records the server's *parent* (the live tool) environ and the
  sitecustomize marker; those two decide the "extended" verdict (`:535`).
- **nonce** (`:288`, own-vocabulary decode `:202`/`:258`): fresh `observer nonce <16 hex>`
  per replay. (a) `POST /tokenize` the nonce; every id must lie in the model's vocabulary
  parsed by the observer from the GGUF header it hashed (`tokenizer.ggml.tokens`, 512 for
  stories260K); decoding those ids through that vocabulary (concatenate pieces, `U+2581` ->
  space) must reproduce `" " + nonce`; a second, different nonce must tokenize differently.
  (b) `POST /completion` the nonce greedily (`temperature 0`, `top_k 1`, seed 424242,
  `n_predict 16`): content must be non-empty, its `/tokenize` ids must stay inside the
  vocabulary, the observer's own decode of those ids must equal `" " + content`, and the
  identical request must return the identical content.

## 3. Per-replay evidence at the tip (`observer-tip.json`)

| replay | pid / port | exe sha256 | listening inode -> owner | ancestry (server ... replay) | mapped dev:inode sha256 | server env keys | nonce -> decode | completion (16 tok) | rerun receipt: child_pid, mapping |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 3989554 / 42885 | `35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0` | 704861535 -> [3989554] | 3989554 <- 3987861 <- **3976693** | 103:05 / 553359105 `270cba1b...d256d` | HOME, LANG, PATH, TMPDIR | `observer nonce a27ff1bd7ca8e8c3` -> 1:1 | `. She liked to see a big box. She want` | 3989554, 103:05/553359105 (`mapped` true) |
| 2 | 4006851 / 38269 | same digest | 704906797 -> [4006851] | 4006851 <- 4005255 <- **3992209** | 103:05 / 2028491973 `270cba1b...d256d` | HOME, LANG, PATH, TMPDIR | `observer nonce 431a40a3ce3de26c` -> 1:1 | `here she went. She was very excited to s` | 4006851, 103:05/2028491973 |
| 3 | 4024797 / 33177 | same digest | 704979270 -> [4024797] | 4024797 <- 4022894 <- **4009408** | 103:05 / 1755783268 `270cba1b...d256d` | HOME, LANG, PATH, TMPDIR | `observer nonce 199f20ce513119fa` -> 1:1 | `ver. She wanted to see what was insid` | 4024797, 103:05/1755783268 |

Frozen digests: server `35ac50fb...d7ff0` (round-47 b11909 install, here the replay's extracted
copy under `work-N/server/llama-b11909/llama-server`), model
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (replay download under
`work-N/download/stories260K.gguf`, 1,185,376 bytes; the 22,475,032-byte asset tarball was
re-fetched and digest-checked per replay). In every replay the observed pid equals
`ready.json.pid` equals the rerun receipt's `child_pid`, and the dev/inode/sha256 the observer
read from `/proc/<pid>/maps` equal the rerun receipt's `model_mapping`
(supplementary `mapping_join=true`, `child_pid_join=true`; `rerun-receipt-{1,2,3}.json`).
Every replay's own output is `match=true, mismatches=[]` (`replay-out-{1,2,3}.json`).

## 4. Agreement with the frozen counter (`compare.md`, `compare.json`)

Counter at the tip (`counter-tip.txt:2`): `bind=1 teardown=1 newrow=1 bound=3/3 met=True`;
per replay (`counter-tip.txt:4-6`) `exe+listen+tree+env+mapped ok, child_pid joined, mapping
dev 103:05 inode <N> recorded, nonce 'kama witness <hex>' round-tripped`.

| leg | replay 1 (mine/counter) | replay 2 | replay 3 |
|---|---|---|---|
| exe | True/True | True/True | True/True |
| listen | True/True | True/True | True/True |
| tree | True/True | True/True | True/True |
| mapped | True/True | True/True | True/True |
| env | True/True | True/True | True/True |
| nonce | True/True | True/True | True/True |

**Disagreements: 0** (`compare.md:17`). The counter's mapping inodes differ from mine
(`2092475926/1022670727/552660834` vs `553359105/2028491973/1755783268`) because the counter
and I each ran our own replays and each replay downloads the model into its own work dir;
those are per-run instance facts, so `compare.py` compares dev/inode **within** a run (my
observed values vs that rerun's own `model_mapping`) and only records the cross-run values.
The counter's `teardown`/`newrow` legs are outside my assignment and were not re-observed by
me; its teardown line (`counter-tip.txt:7`) is its own measurement.

## 5. Finding: the assigned env surface does not discriminate base from build

At the base `26ecba64ad6fb571d09074b07202d1618a46ecd1` my observer ran the same witness on
`receipt-1.json` (`observer-base.json`): **all six assigned legs pass**, including `env`
(server environ = `HOME, LANG, PATH, TMPDIR`, 4 keys, no canary). The server's environ is
already filtered by the live tool at the base; the leak the build closes is in the live tool
process itself and in the interpreter's import path:

- server parent (live tool) environ at base: `HOME, KAMA_R50_CANARY, LANG, PATH, PYTHONPATH,
  TMPDIR` (`observer-base.json` supplementary `parent_env`); at the tip it is `HOME, LANG,
  PATH, TMPDIR` on all three replays.
- the planted `PYTHONPATH` sitecustomize **fired** at base (marker file written) and does not
  fire at the tip (`canary_marker_file` false on all three tip replays).
- the rerun receipt at base has `model_mapping` absent (`mapping_join=false`).

The frozen counter catches exactly this: `counter-base.txt:4` `server parent pid 209409
carries the planted KAMA_R50_CANARY`, `:5` `rerun model_mapping None does not record the
observed mapping`, `:6` `planted sitecustomize imported by 1 interpreter(s)`, i.e.
`bind=0 ... met=False` (`counter-base.txt:2`), the same verdict shape as the committed control
(`.ufo/waves/round-50/controls/base.c1.out:4-6`). So at the tip my observer and the counter
agree on every leg, but the predicate as worded in `preregistration.json:17` ("free of the
canaries" with the observer's `<pid>` being the server) is satisfiable at the base too.

Proposed fix (for a future round; the round-50 counter is frozen and I did not touch it): the
env leg should name both processes - `/proc/<server>/environ` **and**
`/proc/<server-parent>/environ` must lack `KAMA_R50_CANARY`/`PYTHONPATH`, and the
sitecustomize marker must be absent - or the predicate should state that only the live tool's
environ binds. My observer implements this as the "extended" verdict (`observer.py:477`,
`:535`): 3/3 at the tip, false at the base.

## 6. Two method notes (not lane defects)

1. `llama-server` b11909 returns `"tokens": []` in `/completion` even with
   `tokens_predicted: 16` (`probe-tokenizer.out`), and its `/detokenize` keeps the
   sentencepiece leading space (`' observer nonce ...'` for ids tokenized from
   `observer nonce ...`). A nonce leg built on `/completion.tokens` or on byte-exact
   `/detokenize` equality would be vacuously empty or always false; the leg must re-tokenize
   the returned content and decode it through the model's own vocabulary. I found this on my
   first observer iteration (nonce leg false on both counts) and changed only my observer,
   never the counter.
2. My leg values are per-run instance facts except digests: ports, pids, and mapped inodes
   differ between my replay and the counter's; only the exe/model digests, the vocabulary and
   the verdicts are comparable across runs.

## 7. Limits

- Legs observed exactly as specified for C1 bind; teardown (invoker SIGKILL, 30 s, port
  refusal) and the `newrow` source row are the counter's legs and were not re-measured here.
- One witness hold per replay (released ~200 ms after `ready.json`, per the rerun receipts'
  `witness.waited_ms=200`), so only requests I made were served.
- Canary vectors I plant are an env variable and a `PYTHONPATH` sitecustomize; `LD_PRELOAD`
  and a replaced `python` on PATH are outside my observation (same gap the counter declares
  in `preregistration.json` limits).
- Network: https to the two recorded URLs only, as the replay does; no interception, loopback
  server only.
- The counter's receipt is text (`--out` writes the human report), so leg comparison is
  aggregate ("exe+listen+tree+env+mapped ok") plus its named join/nonce tokens; a future
  counter would make head-to-head comparison mechanical with one boolean per leg.

## 8. Deliverables (all under `.ufo/waves/round-50/w1/out/X1Observe2/`)

- `observer.py`, `compare.py`, `probe-tokenizer.py` (tools; only these write nothing outside
  their `--out`/`--scratch` arguments)
- `observer-tip.json` (3 replays, 6 legs, supplementary joins), `observer-base.json`
- `counter-tip.txt`, `counter-base.txt` (the frozen counter's `--out` text, my runs)
- `compare.json`, `compare.md` (leg-by-leg table, `disagreements=0`, base block)
- `rerun-receipt-{1,2,3}.json` (the replays' own receipts: `child_pid`, `model_mapping`,
  `witness`), `replay-out-{1,2,3}.json`
- `probe-tokenizer.out` (b11909 `/tokenize`, `/detokenize`, `/completion` conventions)

Scratch `/fast/scratch/hyaku/kama-r50/X1Observe2` was removed after the copies; no process of
mine remained (`pgrep -af llama-server`).
