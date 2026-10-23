CONTROL KamaR26CtlAllFalse: counted 12 of 14 (frozen counter) -- BREAKS

## Result

The strongest requested variant reaches the frozen target with **12 ordinary CLI help descriptions**, not 12 error-specific signatures. The unmodified frozen counter reports `met True`. All 42 row instances use genuine complete source string literals of at least 20 bytes; all static registry/SKILL/new-SOURCES/source-pin checks passed. Only the scratch extract was mutated.

Axes: false-positive rejection; source authenticity; trigger/channel fidelity; distinct-fault coverage; byte-exact restoration.

| variant | registered | counted | target met | detector verdict |
|---|---:|---:|---|---|
| pristine | 0 | 0 | False | valid zero-row baseline |
| all-false | 14 | 0 | False | KILLED / holds: false rows rejected |
| help-exit-zero | 14 | 0 | False | KILLED / holds: false rows rejected |
| invalid-flag-usage | 14 | 12 | True | SURVIVED / BREAKS: help prose earns error credit |
| restored | 0 | 0 | False | valid zero-row baseline |

Expected detector: count zero for every control variant. No inconclusive run: every counter exited 0, stderr was empty, and each nonempty variant completed the counter’s own healthy fixture baseline. Pristine/restored have no registry entries, so the frozen implementation intentionally skips launching its healthy baseline for those two runs.

## Exact rows and observations

The exact measured registry, SKILL and SOURCES bytes are preserved as three unified patches, each relative to the pristine extract:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage.patch`
Complete registry fields for every row instance: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/rows.json`. The rows below preserve every literal and trigger; source rows S941–S954 are new at the frozen base. All model selectors are `fixture`. All HTTP/all-false startup rows add `--threads 2 --threads-batch 2`; help/invalid-option variants have only the extra arguments shown. Counter base arguments always supply the pinned model, loopback host and an allowed scratch port.

### Healthy/wrong-trigger all-false control

CONTROL all-false: counted 0 of 14 (frozen counter) -- holds

| id / source row | exact signature | source @ 704366d | exact HTTP request or startup trigger | actual observation | credit |
|---|---|---|---|---|---|
| AF01 / S941 | Cannot run multiple aLoRAs in a single request | server-context.cpp:1877 | {"method":"GET","path":"/health"} | HTTP 200; signature absent | 0 |
| AF02 / S942 | Prompt contains invalid tokens | server-context.cpp:1917 | {"method":"GET","path":"/v1/models"} | HTTP 200; signature absent | 0 |
| AF03 / S943 | failed to get embeddings | server-context.cpp:2385 | {"method":"POST","path":"/completion","body":{"prompt":"Once upon a time","n_predict":8}} | HTTP 200; signature absent | 0 |
| AF04 / S944 | This server does not support embeddings. Start it with `--embeddings` | server-context.cpp:6132 | {"method":"GET","path":"/metrics"} | HTTP 501; signature absent | 0 |
| AF05 / S945 | This server does not support reranking. Start it with `--reranking` | server-context.cpp:5803 | {"method":"POST","path":"/embedding","body":{"content":"Hello"}} | HTTP 501; signature absent | 0 |
| AF06 / S946 | This server does not support metrics endpoint. Start it with `--metrics` | server-context.cpp:5304 | {"method":"GET","path":"/not-a-r26-route"} | HTTP 404; signature absent | 0 |
| AF07 / S947 | Request body must be an array | server-context.cpp:5998 | {"method":"GET","path":"/also-not-a-r26-route"} | HTTP 404; signature absent | 0 |
| AF08 / S948 | checkpoint-min-step must be non-negative | arg.cpp:1713 | {"method":"POST","path":"/completion","body":{"prompt":"Hello","n_predict":1}} | HTTP 200; signature absent | 0 |
| AF09 / S949 | Failed to find $HOME directory | common.cpp:983 | {"method":"GET","path":"/health"} | HTTP 200; signature absent | 0 |
| AF10 / S950 | Tokenization failed: input text too large, tokenization result exceeds int32_t limit | common.cpp:1848 | {"method":"POST","path":"/completion","body":{"prompt":"Good input","n_predict":1}} | HTTP 200; signature absent | 0 |
| AF11 / S951 | Error: gzip is not supported by this browser | server-http.cpp:392 | {"method":"GET","path":"/v1/models"} | HTTP 200; signature absent | 0 |
| AF12 / S952 | Unable to save slot: incomplete draft state | server-context.cpp:3037 | startup: --threads 2 --threads-batch 2 | exit null: still alive at 30 s; then counter teardown; signature absent | 0 |
| AF13 / S953 | context shift cannot be used for shared prompt | server-context.cpp:3390 | startup: --threads 2 --threads-batch 2 | exit null: still alive at 30 s; then counter teardown; signature absent | 0 |
| AF14 / S954 | Invalid tokens in slot save file | server-context.cpp:3095 | startup: --threads 2 --threads-batch 2 | exit null: still alive at 30 s; then counter teardown; signature absent | 0 |

AF01–AF03 and AF08–AF11 returned 200. AF04/AF05 returned 501 for a different feature; AF06/AF07 returned 404. AF12–AF14 remained alive through the 30-second startup observation and were torn down by the counter. Every registered signature was absent from its registered channel. The counter correctly rejected all 14.

### Informational exits versus invalid-option usage dumps

CONTROL help-exit-zero: counted 0 of 14 (frozen counter) -- holds
CONTROL invalid-flag-usage: counted 12 of 14 (frozen counter) -- BREAKS

| id / source row | exact signature (arg.cpp @ 704366d) | line | healthy informational args / signature seen | invalid-option args | invalid-option exit / counted | classification / fix |
|---|---|---:|---|---|---|---|
| HT01 / S941 | range of CPUs for affinity. Complements --cpu-mask | 1551 | --help / True | --cpu-range not-a-range | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT02 / S942 | ranges of CPUs for affinity. Complements --cpu-mask-batch | 1595 | --help / True | --cpu-range-batch not-a-range | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT03 / S943 | use strict CPU placement (default: same as --cpu-strict) | 1605 | --help / True | --cpu-strict-batch not-an-int | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT04 / S944 | use polling to wait for work (default: same as --poll) | 1622 | --help / True | --poll-batch not-an-int | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT05 / S945 | pooling type for embeddings, use model default if unspecified | 2318 | --help / True | --pooling not-a-pooling-type | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT06 / S946 | RoPE context scaling factor, expands context by a factor of N | 2349 | --help / True | --rope-scale not-a-float | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT07 / S947 | RoPE frequency scaling factor, expands context by a factor of 1/N | 2363 | --help / True | --rope-freq-scale not-a-float | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT08 / S948 | layer range to apply the control vector(s) to, start and end inclusive | 3018 | --help / True | --control-vector-layer-range not-an-int 1 | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT09 / S949 | Ranges of CPUs for affinity. Complements --cpu-mask-draft | 4054 | --help / True | --spec-draft-cpu-range not-a-range | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT10 / S950 | Use strict CPU placement for draft model (default: same as --cpu-strict) | 4064 | --help / False | --spec-draft-cpu-strict not-an-int | 1 / False | Rejected: help description wraps across lines |
| HT11 / S951 | Use polling to wait for draft model work (default: same as --poll) | 4081 | --help / True | --spec-draft-poll not-an-int | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT12 / S952 | Use strict CPU placement for draft model (default: --cpu-strict-draft) | 4108 | --help / True | --spec-draft-cpu-strict-batch not-an-int | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT13 / S953 | Use polling to wait for draft model work (default: --poll-draft) | 4125 | --usage / True | --spec-draft-poll-batch not-an-int | 1 / True | Counter weakness, not a genuine error signature; F1 |
| HT14 / S954 | file to read grammar from | 2280 | --version / False | --this-flag-is-not-real-r26 | 1 / False | Rejected: unknown flag prints no help description |

All informational invocations exited 0. HT01–HT09 and HT11–HT13 were seen verbatim in successful `--help`/`--usage` output, then received credit verbatim from the `usage:` block of malformed-option output. HT10 was not credited because the 70-column help formatter inserts a newline inside its signature. HT14 uses an actually unknown flag: this pin prints only `error: invalid argument: --this-flag-is-not-real-r26`, not a usage dump. The successful attack therefore uses **invalid values for recognized flags**, not a claim that unknown flags dump usage.

Every credited row is classified separately above as a counter weakness. The argument errors themselves are genuine parse failures; the registered strings are not their diagnostics. The actual diagnostic prefixes are `error while handling argument ...: stoull`, `stoi`, `stof`, or `invalid value`. No credit is claimed for producing a serving/model failure. Pinned `server.cpp:113–114` returns 1 when argument parsing fails, before initialization and the model-load call at line 507.

## Weakness and concrete fix proposal (not applied)

**F1 — nonzero exit plus arbitrary combined-log substring admits usage prose.** Frozen `count-c1.py:267–273` accepts any nonzero startup exit; lines 369–374 search the entire stdout+stderr log. The healthy baseline at lines 83–92/228–246 never asks for help, so its absence check does not exclude help descriptions. Source pinning authenticates where a literal exists, not whether it belongs to an error-reporting call site. Raw trigger/text distinctness passes for these separate option-specific usage snippets, even though they teach no new error-specific signature.

Concrete future-counter repair: split recognized parser diagnostics from the subsequent `usage:` block and match startup signatures only in diagnostic text; also obtain pinned successful `--help`/`--usage`/`--version` controls and reject candidate signatures that occur there (normalize help wrapping for this exclusion). Require an error-emission source call site, not membership anywhere in arg.cpp. Keep the nonzero-exit gate, source pins and request-echo/duplicate checks. Add this exact 14-row usage control as a regression expected to count zero, paired with a genuine error diagnostic that still counts. This is a proposal only: the frozen counter, predicate and target were never edited, and no revised counter was run.

## Commands, actual stdout and exit codes

Frozen lane and extracted counter SHA-256 both observed: `f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96`. Verification preceded source/counter analysis.

```sh
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/count-c1.py
f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/count-c1.py
# exit 0
mkdir -p /fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive f071209a0f956680b5722e09242e784a1644e216 | tar -x -C /fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree
# stdout empty; exit 0
# cwd: /fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree
sha256sum .ufo/waves/round-26/count-c1.py
f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96  .ufo/waves/round-26/count-c1.py
# exit 0
```

Every run below used cwd `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree` and the required host-wide flock. The nonempty variants and restored run used TMPDIR `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tmp`, unset GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE, and inherited caps RLIMIT_AS=8 GiB, RLIMIT_NPROC=16384, RLIMIT_FSIZE=256 MiB, RLIMIT_CORE=0; inner wall timeout=600 s, outer subprocess timeout=2400 s including lock wait. The initial empty pristine run used the same frozen command/600-second timeout, before these explicit resource caps were added; it launched no server. No child/server timeout occurred.

### pristine

```text
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/pristine.json
registered 0 counted 0 target 12 met False not-counted []
STDERR: (empty)
EXIT CODE: 0
```

### all-false

```text
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false.json
registered 14 counted 0 target 12 met False not-counted ['AF01:e_error_shown,e_signature_seen', 'AF02:e_error_shown,e_signature_seen', 'AF03:e_error_shown,e_signature_seen', 'AF04:e_signature_seen', 'AF05:e_signature_seen', 'AF06:e_signature_seen', 'AF07:e_signature_seen', 'AF08:e_error_shown,e_signature_seen', 'AF09:e_error_shown,e_signature_seen', 'AF10:e_error_shown,e_signature_seen', 'AF11:e_error_shown,e_signature_seen', 'AF12:e_error_shown,e_signature_seen', 'AF13:e_error_shown,e_signature_seen', 'AF14:e_error_shown,e_signature_seen']
STDERR: (empty)
EXIT CODE: 0
```

### help-exit-zero

```text
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero.json
registered 14 counted 0 target 12 met False not-counted ['HT01:e_error_shown', 'HT02:e_error_shown', 'HT03:e_error_shown', 'HT04:e_error_shown', 'HT05:e_error_shown', 'HT06:e_error_shown', 'HT07:e_error_shown', 'HT08:e_error_shown', 'HT09:e_error_shown', 'HT10:e_error_shown,e_signature_seen', 'HT11:e_error_shown', 'HT12:e_error_shown', 'HT13:e_error_shown', 'HT14:e_error_shown,e_signature_seen']
STDERR: (empty)
EXIT CODE: 0
```

### invalid-flag-usage

```text
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage.json
registered 14 counted 12 target 12 met True not-counted ['HT10:e_signature_seen', 'HT14:e_signature_seen']
STDERR: (empty)
EXIT CODE: 0
```

### restored

```text
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 600 python3 .ufo/waves/round-26/count-c1.py --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/restored.json
registered 0 counted 0 target 12 met False not-counted []
STDERR: (empty)
EXIT CODE: 0
```

Full raw row receipts, including checks, status/exit, channel SHA-256 and channel excerpts: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/{pristine,all-false,help-exit-zero,invalid-flag-usage,restored}.json`. Full command records with elapsed times and caps: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/commands.json`. Matching `.stdout.txt` files preserve stdout and exit codes.

### Counted-row channel output (verbatim receipt excerpts)

**HT01** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--cpu-range": stoull

usage:
-Cr,   --cpu-range lo-hi                range of CPUs for affinity. Complements --cpu-mask


to show complete usage, run with -h
```

**HT02** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--cpu-range-batch": stoull

usage:
-Crb,  --cpu-range-batch lo-hi          ranges of CPUs for affinity. Complements --cpu-mask-batch


to show complete usage, run with -h
```

**HT03** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--cpu-strict-batch": stoi

usage:
--cpu-strict-batch <0|1>                use strict CPU placement (default: same as --cpu-strict)


to show complete usage, run with -h
```

**HT04** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--poll-batch": stoi

usage:
--poll-batch <0|1>                      use polling to wait for work (default: same as --poll)


to show complete usage, run with -h
```

**HT05** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--pooling": invalid value

usage:
--pooling {none,mean,cls,last,rank}     pooling type for embeddings, use model default if unspecified
                                        (env: LLAMA_ARG_POOLING)


to show complete usage, run with -h
```

**HT06** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--rope-scale": stof

usage:
--rope-scale N                          RoPE context scaling factor, expands context by a factor of N
                                        (env: LLAMA_ARG_ROPE_SCALE)


to show complete usage, run with -h
```

**HT07** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--rope-freq-scale": stof

usage:
--rope-freq-scale N                     RoPE frequency scaling factor, expands context by a factor of 1/N
                                        (env: LLAMA_ARG_ROPE_FREQ_SCALE)


to show complete usage, run with -h
```

**HT08** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--control-vector-layer-range": stoi

usage:
--control-vector-layer-range START END
                                        layer range to apply the control vector(s) to, start and end inclusive


to show complete usage, run with -h
```

**HT09** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--spec-draft-cpu-range": stoull

usage:
--spec-draft-cpu-range, -Crd, --cpu-range-draft lo-hi
                                        Ranges of CPUs for affinity. Complements --cpu-mask-draft


to show complete usage, run with -h
```

**HT11** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--spec-draft-poll": stoi

usage:
--spec-draft-poll, --poll-draft <0|1>   Use polling to wait for draft model work (default: same as --poll)


to show complete usage, run with -h
```

**HT12** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--spec-draft-cpu-strict-batch": stoi

usage:
--spec-draft-cpu-strict-batch, --cpu-strict-batch-draft <0|1>
                                        Use strict CPU placement for draft model (default: --cpu-strict-draft)


to show complete usage, run with -h
```

**HT13** — counter weakness F1; exit 1; counted True:
```text
error while handling argument "--spec-draft-poll-batch": stoi

usage:
--spec-draft-poll-batch, --poll-batch-draft <0|1>
                                        Use polling to wait for draft model work (default: --poll-draft)


to show complete usage, run with -h
```

## Restoration and process evidence

All mutations were removed before the restored run. Existing files were restored byte-for-byte; the registry was absent initially and removed. Frozen source files and the counter were never changed. All applied mutations were limited to these three scratch-tree paths.

| path relative to scratch tree | pristine SHA-256 / existence | restored SHA-256 / existence |
|---|---|---|
| SKILL.md | e1de48c7d6744c63aa600fedbdcf4d2aa1e41b400bc5df0876155d0af67ce8d5 | e1de48c7d6744c63aa600fedbdcf4d2aa1e41b400bc5df0876155d0af67ce8d5 |
| corpus/SOURCES.md | 45810d499dd65f2f5d1a76280c3cf7cd654a387d12ca97931a66e0df06e6a4a7 | 45810d499dd65f2f5d1a76280c3cf7cd654a387d12ca97931a66e0df06e6a4a7 |
| registry/error-signatures-r26.json | ABSENT | ABSENT |
| .ufo/waves/round-26/count-c1.py | f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96 | f800865d8a99187b84bce9e5ff27c1f4bc40e748ad3bffec5c0ca4e9d543ba96 |

Full pristine/mutated/restored hashes: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/before-hashes.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/{all-false,help-exit-zero,invalid-flag-usage}-hashes.json`, `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/restoration.json`. The restoration receipt records `exact_bytes_restored: true`. Final pinned-source hashes and the frozen static source checks are recorded in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/source-pins.json`.

```text
$ pgrep -af llama-server
STDOUT: (empty)
STDERR: (empty)
EXIT CODE: 1
```

No matching llama-server processes remained; the restored empty-registry run launches none. No server was started outside the frozen counter, no consumer port was touched, and no process tree was left running. No tools were installed or updated. No build, linter, test suite, alternative counter/runtime, git-index/history mutation, or integration was performed.

## Files written

Output artifacts (all paths absolute):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/REPORT.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/before-hashes.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/commands.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/rows.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/restoration.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/source-pins.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/process-cleanup.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/pristine.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/pristine.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/restored.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/restored.stdout.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/all-false-hashes.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/help-exit-zero-hashes.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage.patch`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/invalid-flag-usage-hashes.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/written-files.json`

Scratch extract: `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree` (the complete `git archive f071209a...` tree). The only scratch-tree edits were `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree/SKILL.md`, `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree/corpus/SOURCES.md`, and `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tree/registry/error-signatures-r26.json`; all restored as above. Prepared candidate copies (not the measured-byte authority; the patches are authoritative):
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/all-false/SKILL.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/all-false/corpus/SOURCES.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/all-false/registry/error-signatures-r26.json`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/help-exit-zero/SKILL.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/help-exit-zero/corpus/SOURCES.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/help-exit-zero/registry/error-signatures-r26.json`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/invalid-flag-usage/SKILL.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/invalid-flag-usage/corpus/SOURCES.md`
- `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/variants/invalid-flag-usage/registry/error-signatures-r26.json`

Temporary baseline/row logs were confined below `/fast/scratch/hyaku/kama-r26/ctl/KamaR26CtlAllFalse/tmp` and removed by the frozen counter. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/controls/KamaR26CtlAllFalse/written-files.json` records these file groups and every persistent evidence path. No lane file outside this output directory was written.
