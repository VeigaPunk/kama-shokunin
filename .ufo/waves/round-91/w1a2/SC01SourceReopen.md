# SC01SourceReopen — kama round 91, wave w1a2

Seat: independent source re-opening (S592-S595) + SGLang v0.5.22 threshold candidates. Lane
read-only; nothing tracked was edited. Host load 37.8 at fetch time (no timing claim is made).

## Scope
1. Re-fetch S592-S595 live: sha256 vs the `corpus/SOURCES.md` row; quote present at the stated lines; quote <= 25 words; tags exist upstream.
2. Re-verify the 14 rendered rows of `SKILL.md` `## Serving timeout and limit thresholds` against the live bytes (counter B2/B6/B7 by hand).
3. SGLang v0.5.22 defaults (port, watchdog, startup/keep-alive timeouts) -> CANDIDATE rows only, in my out dir. Not appended to SKILL.md or SOURCES.md.

## Commands and outputs (exit codes)
```
$ curl -sS -o s592.html https://pubs.opengroup.org/onlinepubs/9799919799/utilities/awk.html ; http=200 bytes=144111
$ curl -sS -o s593.h https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/common.h ; http=200 bytes=58830
$ curl -sS -o s594.go https://raw.githubusercontent.com/ollama/ollama/v0.40.11/envconfig/config.go ; http=200 bytes=16343
$ curl -sS -o s595.py https://raw.githubusercontent.com/vllm-project/vllm/v0.32.0/vllm/envs.py ; http=200 bytes=118996
$ sha256sum s592.html s593.h s594.go s595.py        ; exit 0
  6df7d0776af4b28dbc3ec667a02a18e51ccd5066ea45a22166214e7e3832f898  s592.html
  c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073  s593.h
  0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895  s594.go
  e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694  s595.py
```
All four == the sha256 recorded in the SOURCES row (rows 347-350). S592 re-fetched 4x
(3s apart): identical sha256 each time -> the digest is stable, not a one-shot page.

```
$ git ls-remote --tags <repo> 'refs/tags/<pin>*'   ; exit 0 for every repo
  llama.cpp refs/tags/b12177     6c01da6278ab6c69ed67d9124806b50d2b299ba7
  ollama    refs/tags/v0.40.11   675150d6ad2747df1e218ef59de9194bc4a7e538
  vllm      refs/tags/v0.32.0    5df63a7203cdb9328d824a27b682e77c7b9928be
  sglang    refs/tags/v0.5.22    35ce313293052f8362e0829e7512bc9bc3d336c9
            refs/tags/v0.5.22^{} baa9befa381511cd4d56f83980951e5a45fffc6d
```
All four pins exist upstream. Independently, the git blob SHA-1 of each fetched file equals the
blob SHA in that tag's GitHub tree (the four round-91 files + six SGLang files): MATCH on all —
the bytes are the tagged tree, not a moving ref.

## Findings

**NOTE — S592-S595 all corroborate; no mismatch.** Each located quote is present at the stated
lines of the live bytes; each quote <= 25 words:
- S592 `s592.html:107-108` (OPERANDS/assignment): "shall be interpreted as if they appeared in the
  awk program preceded and followed by a double-quote" — 17 words; present after HTML tag stripping
  (raw line carries `<i>awk</i>`; rendered text verbatim). `s592.html:793-797` (ENVIRON) confirmed
  verbatim. POSIX says an assignment operand is read as a STRING token while ENVIRON holds the
  variable's value — the S592 row's use of it is sound.
- S593 `s593.h:634` `int32_t timeout_read        = 3600;          // http read timeout in seconds` (10 words).
- S594 `s594.go:130` `keepAlive = 5 * time.Minute` (5 words); doc comment `s594.go:128`
  `// Default is 5 minutes.` is also at the stated line.
- S595 `s595.py:809` `# Timeout in seconds for waiting for engine cores to become ready` (11 words).
Evidence: out dir `receipts.txt` (full text of every stated line).

**NOTE — the S592 claim is upheld by direct experiment (host GNU awk 5.4.1).** The probe's rule
(handoff via `ENVIRON["KAMA_EXP"]`, string compare via `x ""`) behaves as claimed; the compare is
byte-wise, not numeric:
```
$ printf 'a\\b\n' | awk -v e='a\b' '{print e}'                 -> "a"   (backslash eaten: -v escape-processed)
$ printf 'a\\b\n' | KAMA_EXP='a\b' awk '{print ENVIRON["KAMA_EXP"]}' -> "a\b" (verbatim)
$ awk '... s=norm($0); if (s==e) hit=1 ...' served=007 exp=7  -> rc=1 (no match)
$ same: served=7 exp=007 -> rc=1 ; 1e3 exp=1000 -> rc=1 ; 0.5 exp=.5 -> rc=1
$ same: served=a\b exp=a\b -> rc=0 ; good.gguf exp=good -> rc=0 ;
$ same: served=x/y/good.gguf exp=good -> rc=0 ; good.gguf.gguf exp=good -> rc=1
```
So `x ""` really forces string comparison (no numeric coercion of "007" vs "7"), and one
`.gguf` is stripped per side — consistent with POSIX awk S592.

**NOTE — all 14 rendered C2 rows bind against the live bytes** (counter B2/B6/B7 applied by hand):
each stated line contains the backticked literal, the value token occurs in it, and a backticked
parameter token of the threshold cell occurs in it. T01-T07 -> S593:632/634/636/644/669/703/464;
T08-T12 -> S594:23/130/150/277/281; T13/T14 -> S595:26/111. All 14 sit inside the line ranges the
SOURCES rows claim (S593 "464-705", S594 "23-281", S595 "26,111,809-813").

**NOTE — cross-checks of the C2 decisions against upstream (K2 material for the reviewer).**
- llama.cpp b12177: `tools/server/server-http.cpp:116` `port = params.port;` and
  `common/arg.cpp:3318-3323` (`--port`, env `LLAMA_ARG_PORT`) -> T01's "read the port from the
  unit argv" is sound. `--models-max` help "for router server, maximum number of models to load
  simultaneously (default: %d, 0 = unlimited)" -> T06; `--sse-ping-interval` "-1 = disabled" -> T03;
  `--sleep-idle-seconds` "-1 = disabled", rejects 0 -> T05; `-to/--timeout` sets `timeout_read`
  and `timeout_write` -> T02; `--cache-ram` "maximum cache size in MiB (default: %d, 0 for
  decision models, -1 - no limit, 0 - disable)" -> T04.
- Ollama v0.40.11: `envconfig/config.go:21-22,42` default host `127.0.0.1` + `defaultPort` -> T08;
  `server/sched.go:540` `numParallel := max(int(envconfig.NumParallel()), 1)` -> T11.
- vLLM v0.32.0: `vllm/v1/engine/core_client.py:738-750` polls engine-core ready with
  `timeout=VLLM_ENGINE_READY_TIMEOUT_S * 1000` -> T13; `vllm/entrypoints/launchers/api_server/
  entry.py:153` `timeout_keep_alive=envs.VLLM_HTTP_TIMEOUT_KEEP_ALIVE` -> T14.

**NOTE — semantic caveat for the reviewer (not a counter failure).** SGLang's HTTP port is 30000
by default, but `python/sglang/srt/environ.py:370` `SGLANG_PORT = EnvInt(None)` is the *base port
hint* for ephemeral sockets and `utils/network.py:18-31` `get_open_port()` walks upward from a busy
port. The HTTP listener binds `get_serving().port` (default 30000), so the S15-equivalent wording
holds, but a candidate row must not claim 30000 is a hard-unique pin.

**NOTE — SGLang v0.5.22 candidates (CANDIDATE ONLY; out dir `sglang-candidates.md`).** Five rows
proposed with raw URL, line, exact line text and sha256: S15 default port 30000
(`arg_groups/fields/serving.py:66`), S16 hard watchdog 300 s (`arg_groups/fields/device.py:66-69`),
S17 startup health-check timeout 20 s (`entrypoints/http_server.py:207`), S18 startup weights-ready
wait 120 s (`:208`), S19 idle HTTP keep-alive 5 s (`environ.py:337`).

**DEFECT (candidate row S16 only; no landed row is affected)** — the watchdog default is split
across lines 66-69: `watchdog_timeout` is on line 66, the value `300` on line 69 (`] = 300`). No
single line holds both, so a row citing line 69 fails counter B7 (name token must occur in the
literal) and a row citing line 66 fails B2 (value token must occur in the literal). The
hard-watchdog default is NOT bindable by the frozen counter's B1-B7 as written; it needs a
one-line source or a counter change. I did not change the counter.

**NOTE — environment.** No tool installed or upgraded (no uv/npx/pacman/release-binary install);
`~/.local/bin` untouched. No loopback process started; no POST/load/completion to 127.0.0.1:1234.
Scratch /fast/scratch/hyaku/kama-r91/SC01SourceReopen removed before yield.

## Deliverables (in .ufo/waves/round-91/w1a2/out/SC01SourceReopen/)
- `receipts.txt` — fetch log, sha256 table (fetched vs SOURCES-expected), full text of every
  stated line for S592-S595. `sglang-candidates.md` — SGLang v0.5.22 candidate rows with raw URLs,
  line numbers, exact line text, sha256 and the B1-B7 caveat for the watchdog row.
  `src/` — the fetched source bytes (S592-S595 + six SGLang files), for re-verification.

VERDICT: holds — S592-S595 re-open byte-identical to SOURCES digests with quotes at stated lines; 14/14 C2 rows bind; SGLang v0.5.22 gives 5 candidates (hard watchdog not bindable by B1-B7 as written).
