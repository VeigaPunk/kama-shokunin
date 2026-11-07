| row | value cell | S | line | fetched line (trimmed) | help default | read |
|---|---|---|---|---|---|---|
| R01 | 9931 | S593 | 632 | `int32_t port                = 9931;          // server listens on this network port` | 9931 | exact |
| R02 | 3600 s | S593 | 634 | `int32_t timeout_read        = 3600;          // http read timeout in seconds` | 3600 | exact |
| R03 | 30 s | S593 | 636 | `int32_t sse_ping_interval   = 30;            // SSE ping interval in seconds` | 30 | exact |
| R04 | 8192 MiB | S593 | 644 | `int32_t cache_ram_mib       = 8192;  // -1 = no limit, 0 - disable, 1 = 1 MiB, etc.` | 8192 | exact |
| R05 | -1 (off) | S593 | 669 | `int sleep_idle_seconds = -1;   // if >0, server will sleep after this many seconds of id` | -1 | exact |
| R06 | 4 | S593 | 703 | `int models_max = 4;                 // maximum number of models to load simultaneously` | 4 | exact |
| R07 | -1 (auto) | S596 | 1373 | `params.n_parallel = -1;     // auto by default` | -1 | exact |
| R08 | 4 | S597 | 129 | `params.n_parallel = 4;` | (derived) | exact |
| R09 | 11434 | S594 | 23 | `defaultPort := "11434"` | - | exact |
| R10 | 5 min | S594 | 130 | `keepAlive = 5 * time.Minute` | - | exact |
| R11 | 5 min | S594 | 150 | `loadTimeout = 5 * time.Minute` | - | exact |
| R12 | 1 | S594 | 277 | `NumParallel = Uint("OLLAMA_NUM_PARALLEL", 1)` | - | exact |
| R13 | 512 | S594 | 281 | `MaxQueue = Uint("OLLAMA_MAX_QUEUE", 512)` | - | exact |
| R14 | 600 s | S595 | 812 | `os.environ.get("VLLM_ENGINE_READY_TIMEOUT_S", "600")` | - | exact |
| R15 | 5 s | S595 | 1144 | `os.environ.get("VLLM_HTTP_TIMEOUT_KEEP_ALIVE", "5")` | - | exact |

- R01: common.h:632 port = 9931; --help --port 9931
- R02: common.h:634 = 3600; --help -to/--timeout 3600
- R03: common.h:636 = 30; --help --sse-ping-interval 30
- R04: common.h:644 = 8192; --help -cram/--cache-ram 8192
- R05: common.h:669 = -1; --help --sleep-idle-seconds -1
- R06: common.h:703 = 4; --help --models-max 4
- R07: arg.cpp:1373 in the LLAMA_EXAMPLE_SERVER branch (1372); --help -np 0 -> -1; common.h:464 shared default 1 (decision cites 464, exact)
- R08: server.cpp:129 assignment inside the non-router branch (116); 127 is the SRV_TRC log line; derived, no option
- R09: config.go:23; doc comment 21 names 127.0.0.1:11434
- R10: config.go:130; doc comment 126-128 (Default is 5 minutes at 128)
- R11: config.go:150; doc comment 146-148 -- 'Default is 5 minutes' is at 148 and 'Zero or Negative' at 147, so the decision's '(doc comment line 146' points at the block's first line, not at the clause
- R12: config.go:277; doc comment 276
- R13: config.go:281; doc comment 280
- R14: envs.py:812 inside the environment_variables lambda (811); TYPE_CHECKING declaration is at 26; comments 809-810
- R15: envs.py:1144 in the lambda (1143); TYPE_CHECKING declaration is at 111; comment 1142
