# L02LogTail — completion tool server.log capture audit (round 62, w1)

Seat: leaf auditor, axis **operability**. Advisory only: no claim verdict, no commit, no
lane-source edit. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` at tip
`65d7cad0fce90e34de37527cde22e97b63b118bf` (= `git rev-parse master` = `HEAD`).
Frozen instrument audited: `tools/kama-completion-live.py` sha256
`71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f` (clean in `git status`,
byte-equal to the tip blob) with dependency `tools/kama-llamacpp-live.py`
`98d2e6bb48a90e60797df0d2bee895eac4a6cdd9859af2dc47b64bdb4a36fbe9` (clean). Fixture digests
re-verified before the runs: model `stories260K.gguf` `270cba1b…bd256d`, server
`~/.local/opt/llama-b11755/llama-server` `b6a31a8e…cd804` — both equal the tool's pins, so
every receipt below carries structurally true `model_digest`/`server_digest`.
`tools/round62-c1-counter.py` is dirty in the worktree (another seat's edit); I read only the
committed blob (`git show HEAD:…`, sha256 `275610b5…4f4d8d`) and never ran the dirty copy.

Ask: run the tool, then check that its `work/server.log` records llama-server stderr (model
load lines, port bind), that the receipt records the `server_log` path, and that no
credential-ish material lands in the log. No tools installed or updated; no pacman.

## What I ran

Every run: unregistered loopback port, `TMPDIR`/`TMP`/`TEMP` = my scratch, hold dir driven by
an outside observer that snapshots `hold.json` and drops `release`, work dir always passed
explicitly. Ports used (all `grep -c` = 0 in `registry/endpoint-consumers.tsv`, all closed
afterwards per `ss -ltn`, no child of mine left running): 43249, 33197, 45769, 43921, 46715,
37123, plus 36735 for the stream probe and 42933 (chosen but never bound, run 4).

| run | purpose | port | verdict | rc | log |
|---|---|---|---|---|---|
| 1 | baseline hold-mode lifecycle | 43249 | `REQUEST_OK` (17/17 checks) | 0 | `run1-server.log` 3012 B |
| 2 | poisoned environment (6 credential + 3 `LLAMA_ARG_*` vars) | 33197 | `REQUEST_OK` | 0 | `run2-poisoned-env-server.log` 3012 B |
| 3a/3b | two runs into the **same** `--work` | 45769 / 43921 | `REQUEST_OK` / `REQUEST_OK` | 0 / 0 | `run3-server.log.run-a/-run-b` |
| 4 | unwritable `--work` (log open fails) | 42933 unbound | `SETUP_ERROR` | 2 | none opened |
| 5 | whitelisted `LLAMA_ARG_THREADS=4` | 46715 | `REQUEST_OK` | 0 | `run5-threads-env-server.log` 3117 B |
| 6 | pre-planted `work/server.log` symlink | 37123 | `REQUEST_OK` | 0 | written through link → `run6-symlink-write-target.txt` |
| probe | same server, stdout and stderr split | 36735 | SIGTERM rc 0 | — | `streams-stdout.log` 0 B / `streams-stderr.log` 989 B |

Drivers and probes preserved: `out/L02LogTail/{run1-drive.sh,drive2-runs2-4.sh,drive3-run5.sh,
drive4-run6.sh,stream-probe.py,check-logs.py}`, extractor output `evidence-extracts.txt`,
per-receipt cross-check `crosscheck.txt`. All receipts, hold snapshots and logs copied into
`out/L02LogTail/`.

## Confirmed behaviours (the three things asked)

**1. `work/server.log` does record llama-server stderr — model load lines and port bind.**
Code path: `log_path = os.path.join(work, 'server.log')`, `open(log_path,'wb')`, then
`Popen(argv, stdout=log_f, stderr=subprocess.STDOUT, …)` — stdout and stderr merge into the one
file. Verified in all six runs. From `run1-server.log`:

- `load_model: loading model '/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf'` (line 4)
- `load_model: initializing, n_slots = 4, n_ctx_slot = 512, kv_unified = 'true'` (8) and
  `llama_server: model loaded` (9)
- `llama_server: listening on http://127.0.0.1:43249` (10) — the receipt's `port` = 43249
- `operator(): cleaning up before exit...` (29, last line) — the SIGTERM path, log complete
  (file ends in `\n`, no truncation; `teardown.returncode = 0`, `waited_ms = 3`)
- inference corroboration: exactly two slot generations of 8 predicted tokens each (tasks 0 and
  9), matching the receipt's two `POST /v1/completions` (n_predict 8, determinism re-request)

Stream split (`stream_probe.py`, no POST): llama-server writes **all** of this to stderr —
`stdout.log` 0 bytes, `stderr.log` 989 bytes containing `model loaded` and the bind line. So
the tool's claim to capture stderr holds, and the `stdout`-to-same-file merge is inert here.
The tool's own streams stay clean: `tool.stdout`/`tool.stderr` = 0 bytes in every run, i.e.
child output never leaks to the invoking process.

Mechanical cross-check over every receipt (`check-logs.py`, `crosscheck.txt`): for all six
receipts carrying `server_log`, the file exists at the recorded path, contains
`listening on http://127.0.0.1:<receipt.port>`, the model-load triple and the shutdown line,
and ends in a newline. `run4` correctly has no `server_log` key (no log was opened).

**2. The receipt records the `server_log` path** — `receipt['server_log'] = log_path` where
`work` was `os.path.abspath`'d, so the recorded value is absolute and inside `--work`
(observed: `/fast/scratch/hyaku/kama-r62/w/L02LogTail/run1/work/server.log`). It is set before
`wait_ready`, so a not-ready/lost-ownership run would still name its log. On log-open failure
(run 4) the exception precedes `Popen`: receipt is `SETUP_ERROR`, rc 2, no `child_pid`, no
`server_log`, no server ever started, and the message names the exact path
(`PermissionError: … work-ro/server.log`). Good failure semantics.

**3. No credential-ish material lands in the log.** Mechanism: the child env is whitelisted to
`PATH, HOME, LANG, LC_ALL, LD_LIBRARY_PATH, LLAMA_ARG_THREADS, XDG_CACHE_HOME`, so credential
vars never reach the server; llama-server reads no config file and no `--api-key` is passed.
Empirical negative control (run 2: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`AWS_SECRET_ACCESS_KEY`, `HF_TOKEN`, `GITHUB_TOKEN`, `KAMA_TOKEN`, `LLAMA_ARG_API_KEY`,
`LLAMA_ARG_LOG_VERBOSITY=5`, `LLAMA_ARG_HOST=0.0.0.0`, `LLAMA_ARG_PORT=1` all exported):

- sentinel/key-pattern scan over the log: **0 hits** (`SENTINEL`, `sk-`, `hf_`, `ghp_`, `AKIA`,
  `Authorization`, `Bearer`, `private key`); receipt: **0 hits**
- `verbosity = 3` unchanged (host `LLAMA_ARG_LOG_VERBOSITY` is dropped), so no caller can raise
  log verbosity into header/body territory via env
- bind stays `http://127.0.0.1:33197` (host `LLAMA_ARG_HOST`/`LLAMA_ARG_PORT` dropped)
- the log's only `api key` string is llama.cpp's own warning `security: no API key is set and
  CORS allows all origins` — a statement of absence, not a value; the only `token` occurrences
  are `tokenizer.ggml.*_token_id` and `n_tokens`
- run 5 shows the one whitelisted `LLAMA_ARG_*` cannot silently alter the graded run: the log
  itself prints `warn: LLAMA_ARG_THREADS environment variable is set, but will be overwritten
  by command line argument -t`, and `n_threads = 1` matches argv
- no prompt text, no completion text, no nonce, no receipt timestamp appears in the log, and
  there are **no HTTP access lines at all** (`grep -c '/v1/completions|POST |GET /'` = 0), so
  neither the 400 `bad_request` nor request headers/bodies can land there at verbosity 3

Aggregate: 19 166 log bytes scanned (5 direct logs 15 165 B + one symlink-written log 3 012 B +
989 B stream probe) and 6 receipts — 0 credential-shaped hits.

## Gaps found (advisory; nothing edited)

**G1 — `server_log` is an unbound path, so the receipt cannot prove the log it names is its
own child's.** The receipt carries no log digest, byte count or run identity, the log carries no
pid/nonce/alias/wall-clock, and no check grades the log (`checks` has no `server_log_*` entry).
No code reads it: `grep -c server_log` = **0** in the committed counter and 0 in the worktree
counter; the counter's `log` control family is a *capture body* sha256 mutation, not the server
log. Demonstrated by run 3: two runs with distinct ports (45769, 43921) into one `--work` —
`'wb'` truncates, both receipts record the identical `server_log` path, and after run 3b the
bytes at that path are run-b's (`sha256 56aa1e2b…` for both a and b samples); `check-logs.py`
therefore reports `bind=False` for receipt-a — an honest receipt whose named evidence has been
falsified by a later run, with both receipts still `REQUEST_OK`. A receipt that names a
deleted, empty or foreign log likewise still grades `REQUEST_OK`.

**G2 — the log is opened through symlinks.** `open(log_path,'wb')` follows a pre-planted
`work/server.log`. Run 6: a symlink to `canary.txt` was planted in `--work`; the tool truncated
the target and wrote the full server output there, the link survived
(`run6-symlink-listing.txt`), and the receipt reported `REQUEST_OK` with `server_log` pointing at
the symlink. Consequence: in a shared, reused or operator-supplied `--work`, a third party can
redirect and read the server log (and clobber an arbitrary writable file). The lane already
hardened exactly this class for the witness dir (`prepare_witness_dir`/`hold_for_witness` use
`O_CREAT|O_EXCL|O_NOFOLLOW`, round-49 Sen1Witness F1); the log path has no equivalent.

**G3 — cosmetic/robustness.** (a) File mode is 0644 (umask default) for a log that contains
absolute home paths. (b) `log_f` is not closed on the early `return` setup paths
(not-ready, listener-not-owned); harmless in practice because the process exits immediately, but
it means the except/finally block is not a single exit point. (c) The sibling
`kama-llamacpp-live.py` uses the opposite convention — temp log, tail kept only in the receipt,
`teardown.log_path = null`, file deleted — so the lane currently has two server-log policies;
the completion tool's keeper-log is the auditable one and is the one worth binding.

Observation (outside my bounds, untouched): five `llama-server` children from round-61 scratch
dirs (`/fast/scratch/hyaku/kama-r61*`, pids 2356333, 2990457, 3002015, 3011143, 3262613, ports
42317/37539/42665/38791/37323) are still running. Not mine, so not signalled — but they hold
loopback ports and should be reaped by whoever owns them.

## Smallest safe fixes (for the L1 / build seats; I made no edit)

1. Bind the log to the run, in the receipt: after teardown, record `server_log_bytes` and
   `server_log_sha256`, and add one graded check `server_log_captured` = file is a regular file
   (not a symlink), size > 0, contains `model loaded` and
   `listening on http://127.0.0.1:<port>`. This also makes the log an operability signal rather
   than a side artifact — the current instrument would pass with an empty log.
2. Open it safely: `os.open(log_path, O_WRONLY|O_CREAT|O_TRUNC|O_NOFOLLOW, 0o600)` (or refuse a
   non-empty/non-owned `--work`, or name the log `server.log.<child_pid>` so runs cannot
   truncate each other) — mirrors the witness-dir hardening already in the lane.
3. If the counter is to consume it, have it require `server_log` to resolve inside its own
   scratch `tool-work`, be a regular file, and match the recorded digest; otherwise treat the
   field as documentation, not evidence.

## Counter/tally

```
log capture: stderr recorded 6/6 (model-load 6/6, port-bind==receipt.port 6/6, shutdown 6/6,
complete-newline 6/6, stdout empty 1/1 split probe); receipt server_log abs path 6/6 success,
0/1 setup-error (no log opened, no child started); credential-shaped hits 0/19166 B + 0/6
receipts, env-drop 10/10 sentinel vars; binding gaps 2 (unbound path/digest G1, symlink-followed
target G2); lane-source edits 0; commits 0; tools installed 0
```
