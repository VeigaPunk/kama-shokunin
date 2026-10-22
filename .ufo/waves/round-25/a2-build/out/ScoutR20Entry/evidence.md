# ScoutR20Entry — commands, outputs, source pins

Seat `KamaR25a2.ScoutR20Entry`, round 25 attempt 2, lane `kama-shokunin`.
All commands run from `/home/vgpnk/Projects/shokunin/kama-shokunin` unless a
scratch path is shown. Written 2026-10-22T09:40:48Z.

No llama-server child was started. No production file was edited. Scratch:
`/fast/scratch/hyaku/kama-r25a2/ScoutR20Entry/src/`.

## 1. Lane state

```
$ git rev-parse HEAD
c808ba07f09c4be55413d3d6516c542ab69b64f8

$ git diff --stat 1fc41e346853afd98cbd7010af5db4e54dc877f7 -- \
    corpus/knowledge/gguf-declared-identity.md SKILL.md SCORECARD.md \
    corpus/README.md corpus/lessons/round-20.md corpus/SOURCES.md \
    tools/gguf-identity.py .ufo/waves/round-20/
(no output; exit 0)

$ git merge-base --is-ancestor 1fc41e346853afd98cbd7010af5db4e54dc877f7 HEAD
exit 0
```

The assignment named 1fc41e3. The lane has since advanced to c808ba0
(amendment 3, committed C2 receipt). Every measured passage is byte-identical
between the two revisions.

## 2. X1/X3/K1 observed values (lane-committed receipt, not this seat's run)

```
$ python3 - <<'PY'
import json, hashlib
p='.ufo/waves/round-25/final/context-capacity-receipt.json'
raw=open(p,'rb').read()
print('receipt sha256', hashlib.sha256(raw).hexdigest(), 'bytes', len(raw))
d=json.loads(raw)
for c in d['cells']:
    if c['id'] in ('K1','X3','X1'):
        print(c['id'], c['args'], 'observed', c['observed'],
              'props', c['props_n_ctx'], 'slots', c['slots_n_ctx'],
              'pool', c['kv_pool_n_ctx'], 'candidates', c['kv_pool_candidates'])
PY
receipt sha256 fe378502e84a379badf94423ca7a34586503b410672450eaf5fb9fe3fe3c158b bytes 412737
K1 -c 0 observed True props 2048 slots [2048, 2048, 2048, 2048] pool 2048 candidates [2048, 2048]
X1 -np 4 --no-kv-unified observed True props 2048 slots [2048, 2048, 2048, 2048] pool 8192 candidates [2048, 8192, 8192]
X3 -np 4 --no-kv-unified --fit off observed True props 512 slots [512, 512, 512, 512] pool 2048 candidates [2048]
exit 0
```

```
$ python3 .ufo/waves/round-25/count-c2.py
registered 14 observed 14 bound True missing []
exit 0
```

Provenance: the receipt was committed by the L1 at `5ea4fc44`; this seat read
it and did not produce it. Amendment 3 (commit `c808ba0`) explains why the
first X1 pool candidate is 2048: fit measures a probe context, then sizes the
final pool.

Raw captures under `.ufo/waves/round-25/final/raw/` (exit 0 for every check below):

```
$ python3 - <<'PY'  # parse raw bodies
K1 models_sha f92b4d626092 meta.n_ctx 2048 train 2048 props 2048 slots_total 4
X1 models_sha 6d71970c7060 meta.n_ctx 2048 train 2048 props 2048 slots_total 4
X2 models_sha 6d71970c7060 meta.n_ctx 2048 train 2048 props 2048 slots_total 4
X3 models_sha ba87d55c9bf9 meta.n_ctx 512  train 2048 props 512  slots_total 4
exit 0

$ sha256sum raw/{K1,X1,X2}.slots.body
6939aec123597421f3b9735848e81e782c3b825ba4b88b7d46a85eab2a8e7d27  (all three identical)

$ grep -n 'llama_context: n_ctx ' raw/{K1,X1,X3}.server.log
K1: 284: n_ctx = 2048; 816: n_ctx = 2048
X1: 283: n_ctx = 2048 (fit probe); 812 and 1344: n_ctx = 8192
X3: 281: n_ctx = 2048
```

Parsed-body diff K1 vs X1: only `/data[0]/created` differs (1792662162 vs
1792662167) in `/v1/models`, and only `/media_marker` differs in `/props`
(per-run random token). X1 vs X2: only `created`/`media_marker`. X1 vs X3:
`n_ctx` 2048 vs 512 plus `media_marker`.

## 3. Round-20 predictor against X1

```
$ python3 .ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py --table
ctx	np	kvu	n_ctx_train	per_slot_n_ctx (source formula, not served)
256	auto->4	true	2048	256
256	4	false	2048	256
1024	auto->4	true	2048	1024
1024	4	false	2048	256
4096	auto->4	true	2048	2048
0	auto->4	true	2048	2048
0	4	false	2048	512
exit 0

$ python3 -c "import importlib.util as u; ... m.predict(0,2048,4,False,0) ..."
X1 predicted (512, 4, False)
exit 0
```

X1 is the tuple `0, 4, false, 2048`; the round-20 formula predicts 512, the
committed receipt observed 2048.

## 4. Fresh pinned sources (llama.cpp 704366d76, accessed 2026-10-22)

All fetched with
`curl -sS -f -L --max-time 60 https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/<path>`
and every fetch exited 0.

| Path | SHA-256 | Lines | Located quote |
|---|---|---|---|
| `common/fit.cpp` | `1f83da2a5dc460b893373365e07341695be80d6c662e53679032a138cce4dd58` | 1113 | line 196: "if memory can hold more than model's trained context size, we must extend the n_ctx to hold enough n_streams" (22 words) |
| `common/fit.cpp` | same | | lines 266-272: `n_ctx_max = min(hp_nct * n_streams, UINT32_MAX)`; `if (n_ctx_auto) cparams->n_ctx = n_ctx_max;` |
| `src/llama-context.cpp` | `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5` | 4719 | line 380: `cparams.n_ctx_seq = cparams.n_ctx / cparams.n_seq_max;` (padded at 381 to 256) |
| `tools/server/server-context.cpp` | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | 6320 | line 4654: "context size of a single slot, capped by --kv-unified-per-slot and by the training context of the model" (18 words) |
| `common/common.h` | `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9` | 57298 bytes | line 483: "whether to fit unset model/context parameters to free device memory" (10 words) |
| `common/arg.cpp` | `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d` | 224650 bytes | lines 1646-1648: "disable context reduction in llama_params_fit if the user explicitly requests the full context size" (15 words) |
| `tools/server/server.cpp` | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | 24572 bytes | line 170: "n_parallel is set to auto, using n_parallel = 4 and kv_unified = true" (14 words) |
| `common/common.cpp` | `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4` | 83694 bytes | line 1715: `cparams.n_seq_max = params.n_parallel;` |

Mechanism chain (all lines observed):

1. `common.h:483` fit is on by default; `common.h:457` n_ctx default 0.
2. `arg.cpp:1406` server default n_parallel -1; `server.cpp:169-173` auto
   resolves to 4 slots and `kv_unified=true`; explicit `-np 4 --no-kv-unified`
   leaves `kv_unified=false` (`common.h:580` default false).
3. `common.cpp:1715` sets `n_seq_max = n_parallel`.
4. `fit.cpp:197` `n_streams = kv_unified ? 1 : max(1, n_seq_max)` -> 4.
5. `fit.cpp:267` `n_ctx_max = hp_nct * n_streams` -> 8192;
   `fit.cpp:271-272` unset context is set to 8192.
6. `llama-context.cpp:377-383` pad 8192, split `8192 / 4 = 2048`.
7. `server-context.cpp:4654-4663` slot cap `min(2048, train 2048)` -> 2048.

For this fixture the fit reduce branch cannot lower the value: it requires
`n_ctx_max > n_ctx_min_total` (`fit.cpp:394`), and `n_ctx_min_total` is
`4096 * 4 = 16384` (`fit.cpp:268`, `common.h:485`), which is greater than
8192. The host-memory early return (`fit.cpp:322-329`) needs 1024 MiB free.

## 5. Snapshot comparison

```
$ cmp -s <fresh> .ufo/waves/round-16/sources/llama.cpp-704366d/<name>
server.cpp          identical
arg.cpp             identical
server-context.cpp  identical
```

`common/fit.cpp`, `common/common.h`, `common/common.cpp` and `common/fit.h`
are not in the round-16 snapshot; they were fetched fresh. `common/fit.h`
sha256 `907048c4fb974c0b405ffd4400d338c70e19f54f6983bc1ac3ec17174fcf3347`.

## 6. Files this seat wrote

- `.ufo/waves/round-25/a2-build/out/ScoutR20Entry/passage-inventory.json`
- `.ufo/waves/round-25/a2-build/out/ScoutR20Entry/evidence.md` (this file)
- `.ufo/waves/round-25/a2-build/advice/ScoutR20Entry.md`

No other path was written. No server, no model load, no install.
