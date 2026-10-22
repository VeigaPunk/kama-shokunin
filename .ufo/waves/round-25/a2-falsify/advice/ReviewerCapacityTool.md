# ReviewerCapacityTool: C2 tool correctness (round 25, attempt 2, wave 2)

**Verdict: defect found.** The committed receipt reproduces exactly from the committed tool bytes, and the registered counter scores it `registered 14 observed 14 bound True missing []`. The tool's own checks, its failure path and several receipt fields do not hold as written, and the counter does not check some fields the tool writes without observing them. Nothing below changes the 14-of-14 value for this receipt; the findings are about what the tool and counter would accept on the next run.

Target: `tools/kama-context-capacity.py` at fa3b62ae6475d111eb466d79af616aeebb08bbb9 (blob sha256 `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27`, equal to the receipt's `tool.sha256`). Counter `.ufo/waves/round-25/count-c2.py` (sha256 `7bf3f9cdcdf32ea36b5a44d3f9566b90216ee179dc1c7b03386b435e39574d5d`). Receipt `.ufo/waves/round-25/final/context-capacity-receipt.json`. Worktree copies of these files and of `tools/kama-llamacpp-live.py` and `registry/endpoint-consumers.tsv` compare byte-equal to fa3b (`cmp`, exit 0 each).

## Guardrails held

- No llama-server child started. `pgrep -x llama-server` exited 1 before and after the harness. `ss -ltn` before the run showed no listener in 47400-47447. The harness used 47420-47447 and never listened on them.
- Every child is a `FakeChild` stub that writes committed log bytes. `os.killpg` is recorded, never sent. One Python child (`crash_main.py`) ran with `Popen` forced to fail; no llama-server ran.
- Scratch clone: `git clone --no-hardlinks` into `/fast/scratch/hyaku/kama-r25a2w2/ReviewerCapacityTool/clone`, then detached checkout of fa3b62a (exit 0). The lane's refs, index and working copy were not written.
- Installs: none. Existing tools used: pyflakes 4.0.3, ruff 0.17.1, Python 3.14.8, git 2.56.0, iproute2 ss 7.2.0.

## What I checked

1. Bytes: `git show fa3b62ae...:<path>` equals the worktree for tool, counter, live module, registry and receipt (`same-as-worktree`, cmp exit 0).
2. Counter on the committed receipt, lane and clone: `registered 14 observed 14 bound True missing []`, exit 0.
3. Static: `pyflakes` on tool and counter, no output, exit 0. `ruff check --select F,E9`: `All checks passed!`, exit 0.
4. Raw integrity: 70 of 70 files in `final/raw/` hash to the receipt values.
5. Replay (`out/ReviewerCapacityTool/harness.py`, exit 0): all 14 cells rebuilt from committed raw bodies and logs through the tool's own `run_cell`. Each reproduces the receipt on argv, `props_n_ctx`, `total_slots`, `slots_n_ctx`, `models_n_ctx_train`, `kv_pool_n_ctx`, pool candidates, log lines, raw hashes and request statuses. The counter accepts all 14.
6. Argv (`tools/kama-context-capacity.py:292-297`): order matches the registered launch rule, `-v` comes before the cell args, and the replays reproduce it exactly.
7. Port safety: refused set holds 8080 and 34113 (receipt `port_refusal_set`). Port pick, listener ownership and the `ss` check (`:194-215`, `:341`) reuse the lane module. All 14 ports closed.
8. Readiness on `/props` 200 (`:329-334`) is sound. The lane module documents that every non-frontend path answers 503 until ready (`tools/kama-llamacpp-live.py:136-141`). No finding.
9. Committed entry `corpus/knowledge/context-capacity.md` against raw logs: `X1` cites lines 283, 812, 1344 and 1610, which match `X1.server.log`. `L1` release lines 1852 and 1866 (`n_tokens = 1025`) fall in the cited 1849-1866. L2 and L3 "600 tokens each, not truncated" match `L2.server.log` 12670, 12681 (eval 600 tokens) and 12676, 12687 (`truncated = 0`), and `L3.server.log` 11444, 21698 and 11450, 21704.

## Findings

### F1 Medium: the tool's own `observed` is weaker than the counter, so its summary and exit code can overstate

- `tools/kama-context-capacity.py:396-407` (config cells) only checks that the `/slots` list is non-empty (`:404`). It does not compare its length with `total_slots`, and it does not look for the `n_slots = ..., kv_unified = ...` layout line that the counter requires (`count-c2.py:90`).
- `:356-358` silently drops any `/slots` entry without an integer `n_ctx`.
- `:409-416` (load cells): `len(requests) >= 2` (`:412`; counter requires exactly two, `count-c2.py:97`); status any integer (`:413`; counter 100-599, `:100-101`); no overlap check (counter `:109-110`).
- Harness variants, one change each: V1 `/slots` has 3 entries for `total_slots` 4: tool observed True, counter False. V2 one slot entry lacks `n_ctx`: True, False. V3 log without the `n_slots` line: True, False. V5 concurrent L2 with non-overlapping request times: True, False.
- Effect: the tool's summary and exit code (`:817-820`) can report a cell observed when count-c2 does not count it. The committed receipt is not affected; both gates agree on all 14 cells.
- Smallest correction: `observed` calls the counter's `cell_ok` (copied or imported), and the exit code depends on it. Or delete the tool-side `observed` and let count-c2 decide.

### F2 Medium: a launch failure crashes the tool and writes no receipt; exit 1, not the documented 2

- `:288` sets `'teardown': None`. `:316` returns the record early on `OSError` from `Popen` (also `open(log_path, 'wb')` at `:306`).
- `main` then calls `c.get('teardown', {}).get('port_closed')` at `:814`, `:819` and `:834`. With `teardown` set to None, `.get` raises. The exception escapes the `finally` (`:827-837`), so the receipt file is never written.
- Observed: the wrapper with `Popen` forced to fail exited 1, `receipt_written: false`, and stderr ends `AttributeError: 'NoneType' object has no attribute 'get'` at tool line 834. The direct test gave `teardown: null`, `error: launch-failed:OSError`.
- Reachable on any setup fault that makes `Popen` or the log open raise after the version check passes. [INFERENCE on frequency; not seen in the lane.]
- Smallest correction: default `teardown` to a dict at `:288` (for example `{'port_closed': False, 'child_returncode': None}`).

### F3 Medium: load-cell `prompt_tokens` and `n_predict` are request constants, not server observations; `tokens_predicted` and `truncated` are recorded but never checked

- `:526-527` write `LOAD_PROMPT_TOKENS` and `LOAD_N_PREDICT` whatever the response says. The same constants appear in the early-return records at `:439-441` and `:477-479`. The gate at `:414-415` compares constants with constants. The counter's `prompt_tokens` and `n_predict` checks (`count-c2.py:102-105`) are the same vacuous test.
- `:542-543` record `tokens_predicted` and `truncated` from the response. Neither the tool's gate nor the counter checks them. Harness V6 (response with `tokens_predicted` 3, `truncated` true, `tokens_evaluated` 17): tool observed True, counter accepts L2.
- The committed values are right, and the raw logs corroborate them: 1000 prompt tokens (`L2.server.log:1260`, `:12669`), 600 generated (`:12670`, `:12681`), `truncated = 0` (`:12676`, `:12687`); L3 is similar (`:11443-11450`). `task.n_tokens = 1000` survives into the receipt's `log_lines`, because `LOG_KEEP` (`:94-96`) matches the `n_ctx` inside `n_ctx_slot`. So the server's own count is in the receipt, but nothing reads it.
- Smallest correction: take the prompt count from the server (the `task.n_tokens` line, or a response field; the response field name was not verified here). Gate `tokens_predicted == 600` and `truncated is False` for L2 and L3. Rename the constants as "requested". Changing the counter's rule needs a registered amendment.

### F4 Medium: `bound` and the tool's version check do not bind what the receipt names

- `count-c2.py:137-140` checks the top-level `server_version` (exact regex at `:51`) and the top-level and per-cell `model_sha256`. It does not check `server.sha256`, per-cell `server_sha256`, `tool.sha256` or `port_safety_module`. Harness counter cases: forged server sha256 gives bound True; forged tool sha256 gives True; changed port-module path gives True.
- `:729` records the port-safety module's path only. The module is loaded from the worktree (`:181-191`) with no hash.
- The tool's version check is a substring test: `SERVER_VERSION_MARK = 'build 11755'` (`:63`, tested at `:752`). Direct test: `build 117550` passes the tool (True); the counter's exact regex rejects it (False). Harness case `server_version_minor_changed`: bound False. So the tool proceeds on a wrong build.
- Smallest correction: `:729` records the sha256 of the live module. `:63` and `:752` use the counter's exact `(build 11755, commit 704366d76)` text. The counter checks that every cell's `server_sha256` equals `server.sha256`.

### F5 Medium: `http_post` silently truncates oversize bodies, and misses `HTTPException`

- `:139` reads `HTTP_BODY_CAP + 1` bytes, but `:140` (and `:148`, `:152`, `:155`) always report `body_truncated: False`. Direct test: a 70,000-byte body came back as 65,537 bytes with the flag False. `_completion` then records status 200, `tokens_predicted` null, `truncated` null, and `error` set to the first 500 characters of the body (else-branch `:541-552`). The load gate ignores `error` (`:413-416`), so the cell still counts.
- `:153` catches only `OSError`, `socket.timeout` and `TimeoutError`. Direct test: `http.client.IncompleteRead` and `http.client.BadStatusLine` escape `http_post`. The run then ends in the `internal:` path (`:824-826`) and the cell is missing from the receipt.
- Smallest correction: catch `http.client.HTTPException` alongside `OSError`. Set `body_truncated = len(raw) > HTTP_BODY_CAP`. Treat a 200 with `error` set as not observed.

### F6 Low: teardown signals a PID that may already be reaped

- `:565` and `:573` call `os.killpg(proc.pid, ...)` with no liveness check. `run_cell` can reap the child first (`:330-331`, early exit). The lane module refuses this (`tools/kama-llamacpp-live.py:869-872`, "F5: killpg only on a live child").
- Direct test: teardown of an already-reaped child recorded `killpg(pid, 15)`: `[[3900001, 15]]`.
- Smallest correction: `if proc.poll() is None:` immediately before each `killpg`.

### F7 Low: `host_idle` keeps only the last cell

- `:791-793` overwrite `receipt['host_idle']` on each pass. The committed receipt shows `{"cell": "L3", ...}` only.
- Smallest correction: append one entry per cell.

### F8 Low: tool and counter read the pool line differently

- Tool: `KV_POOL_RE` (`:97`) is unanchored. The pool is the last match in the whole log (`:386`).
- Counter: `POOL` (`count-c2.py:52`) requires the number at end of line. `pools[-1]` (`:88`) is the last matching line.
- Harness V4 (last pool line given a " (serving)" suffix): tool observed True. The counter accepts, using the earlier identical line. The registered rule "the pool equals the last `llama_context: n_ctx = N` line" is not enforced in this case.
- Smallest correction: the counter takes the last line matching `llama_context: n_ctx\s*=` and requires that line to match the strict form.

### F9 Low: receipt hygiene

- Child environment: `CHILD_ENV_KEYS` (`:64`, `:300-301`) is passed to the child, but the names are not recorded. The lane module records names (`tools/kama-llamacpp-live.py:82-84`).
- `argv[0]` is the realpath `/home/vgpnk/.local/opt/llama-b11755/llama-server` (`:734`). The registered rule says `~/.local/bin/llama-server`, which is a symlink to that file (`ls -l` verified). Same binary; note only.
- `_capture_raw` (`:346`, `:420-427`) ignores HTTP status and makes separate requests from the parsed values (`:347-349`). The hashed bodies and the parsed fields come from different requests, and no status is recorded.
- `_OPENER` (`:99`) follows redirects; the lane module refuses them (`tools/kama-llamacpp-live.py:547-556`). No effect on llama-server [INFERENCE].
- The summary is built twice (`:809-816` and `:829-836`); the `finally` overwrites the first.

### F10 Low: what the counter does not check

- `tokens_predicted` and `truncated` are not checked. The entry's "600 tokens each, not truncated" (`corpus/knowledge/context-capacity.md:109-110` at fa3b) is backed only by values the counter never reads.
- Status accepts any 100-599 by design. A 500 on L2 still counts (harness case `L2_status_500`: 14 observed). The claim value is the count, so this is by design; the entry should say so.
- Receipt values are not checked against the raw files they hash (harness case `K1_props_n_ctx_999` accepted). The raw files match today (70 of 70), so the risk is only an edited receipt.

## Process note

- The committed entry at fa3b and the worktree copy differ. My first read at the start of this seat matched fa3b, but the worktree has since gained fit-pass and shared-pool text (for example lines 91-93 and 154-158 in the worktree), which fa3b does not contain. I cited only fa3b bytes. The report draft must cite landed bytes.

## Smallest correction order

1. F2 (default `teardown`), F5 (catch `HTTPException`, honest body flag) and F6 (liveness check). Small, local fixes; no claim change.
2. F1: one shared check for `observed`, used by both the tool and the counter.
3. F3: server-side counts, and gates on tokens and truncation. Needs a registered amendment.
4. F4, F8, F9, F10: binding and hygiene. Counter changes need a registered amendment.

## Residual risk and verification gaps

- No live run. The real `urllib` socket path, real llama-server timing, and PID reuse were not exercised. The replays use committed bytes and stub the sockets.
- No live `/completion` body was captured. The field `tokens_evaluated` used in V6 is a stub value; whether b11755 returns a prompt count in its response is [INFERENCE], to be checked on a live run.
- Not checked: other seats' claims, the SOURCES rows, and the SKILL.md decision rows.
- `wait_for_host_idle` (`:241-259`) fails closed when any llama-server runs on the host. I did not test that branch with a foreign server.
- The harness reads the scratch clone; rerunning it requires `/fast/scratch/hyaku/kama-r25a2w2/ReviewerCapacityTool/clone` at fa3b62a.

## Files written

- `.ufo/waves/round-25/a2-falsify/advice/ReviewerCapacityTool.md` (this report)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerCapacityTool/harness.py` (new, 17,657 bytes; the write tool also set its executable bit)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerCapacityTool/results.json` (harness output)
- `.ufo/waves/round-25/a2-falsify/out/ReviewerCapacityTool/harness-run.txt` and `harness-stderr.txt` (harness stdout and stderr; stderr empty; `python3 harness.py` exit 0)
- Scratch only, outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReviewerCapacityTool/` (clone at fa3b62a, `harness-work/`, `tool-fa3b.py`, `count-c2-fa3b.py`, `pyflakes-*.txt`, `ruff.txt`)
