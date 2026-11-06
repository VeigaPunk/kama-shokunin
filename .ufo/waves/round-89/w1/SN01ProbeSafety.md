# SN01ProbeSafety — robustness/security review of the round-89 file-read surface

Reviewed bytes: `git show 4f9eacf720aa59ed806b31b758571e364658179b:tools/kama-probe.sh`
(sha256 `a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf`, 1467 lines).
No lane file was edited. Every server was a lane-owned stub on a free loopback port
(`scripts/srv.py`, start_new_session + killpg); port 1234 was never contacted.

## Scope
Can the new boundary — `status.args` paths taken from `GET /v1/models` — make the probe
(1) block / burn CPU / burn memory, (2) open files it should not, (3) emit output that breaks
the TSV/JSON contract, (4) lose to a stat→open race, (5) write outside TMPDIR. Out of scope:
the frozen C1/C2 predicates themselves (their cells are lane-owned and never return hostile
bodies); I only checked whether this surface can break them (it can stall or kill the counter,
never turn a red into a green).

## Commands and outputs (true exit codes)
`python3 drive.py CASE fx/b-CASE.json [--json|--strace]` → `bash probe-M.sh listeners --port N
--expect '*'`, wall/RSS from `/usr/bin/time -v`; rc=0 for every cell that finished (the two
killed id cells never returned) except the JSON injection cells (rc=1, F4). `python3 race.py`,
`race2.py`, `race3.py` (symlink regular↔FIFO flipper), `diskfill.py`. `strace -f -e
`trace=openat,open,creat,unlink,write` per cell, `strace -c` for the 1 MB id. Probe invocations
used default `--timeout 5` unless stated.

| hostile answer (rc) | wall | peak RSS | verdict |
|---|---|---|---|
| 219 B, 1 entry → 700 MB sparse GGUF, n_kv=1, array-of-arrays n=5e7 (0) | 41.44 s | 12 MB | MODEL_OK |
| 219 B, same shape n=1e7 (0) | 14.21 s | 12 MB | MODEL_OK |
| 7,668 B, 40 entries → 40 MB sparse, 1e6 tensor infos (0) | 78.07 s | 83 MB | MODEL_UNLOADED |
| 219 B, 1 entry → 40 MB sparse, 1e6 tensor infos (0) | 2.17 s | 80 MB | MODEL_UNLOADED |
| 219 B → huge key length (2 GB sparse, klen=2^40) / 1e5 KVs × 5e7-scalar arrays (0) | 0.22 / 0.20 s | 12 MB | invalid |
| 100k-deep / 1M-deep nested JSON arrays (0) | 0.17 / 0.18 s | 22/24 MB | FOREIGN_SERVICE (RecursionError swallowed) |
| 200 MB body, 50M-element string array (0) | 8.52 s | **598 MB** | MODEL_OK |
| 20 MB body, 5M `args` strings (0) | 1.13 s | 103 MB | MODEL_OK |
| 1 MB served id (0) / 4 MB (killed) / 64 MB (killed) | 17.59 / >200 / >110 s | 20 MB | MODEL_OK |
| FIFO / symlink→FIFO / /dev/zero / /dev/stdin / /proc/self/fd/0 / dir (0) | 0.24–0.26 s | 12 MB | router-model-invalid |
| symlink→/etc/passwd / /proc/self/environ (0) | 0.24–1.54 s | 12 MB | router-model-invalid |
| model chmod 000, args[0] = FIFO or dir (0) | 0.38–0.44 s | 12 MB | no change (MODEL_OK) |
| 1.5 GB streamed body (0) | 5.0 s | — | **52 MiB written to TMPDIR**, DEAD timeout |

## Findings

**F1 — DEFECT (new at M): unbounded per-answer CPU; `--timeout` does not cover it.**
`router_entries()` → `file_state()` → `gguf_state()` runs one Python process with no deadline.
Its only budgets are byte-position (`MAX_META`, probe-M.sh:500,529) and counts (`MAX_ARR=5e7`,
:500); `skip_value` iterates `for _ in range(n)` (:561), so a 512 MB position budget converts
into ~44 M interpreter loops. Cost is linear in entries and unbounded per entry: a **219-byte**
answer costs **41.4 s**; a **7,668-byte** answer (40 entries) costs **78.1 s**
(`receipts/c_cpu.json`, `c_amp40.json`), both under `--timeout 5`. Impact: any loopback
listener naming a crafted model path stalls `check`/`snapshot` (the gate) for minutes to hours
(a 1 MB answer ⇒ hours [INFERENCE, linear in entries]); the C1 counter's per-probe `timeout=120`
(`tools/round89-unloadable-cells.py:184`) then raises an unhandled `TimeoutExpired` — only
`CannotEvaluate` is caught (:301) — so the counter dies with a traceback, no summary.
Minimal fix: an iteration budget in `skip_value` (2 M calls → `Unknown()`), and
`done < <(timeout 5 router_entries "$body")` at :710 with timeout ⇒ no file state, keeping the
round-88 verdict exactly as the frozen rule already does for undecidable input.

**F2 — DEFECT (new at M): the listener chooses which local files the probe opens.**
`file_state` (:622) accepts any absolute path after only `os.path.isfile(args[0])`;
`gguf_state` uses `os.stat()` (:514) then `open()` (:523), both following symlinks. Measured:
the answer made the probe open `/etc/passwd` through a symlink and `/proc/self/environ`
(`receipts/s_linkpasswd.strace`, `d_procenv.strace`: `openat(AT_FDCWD,"/proc/self/environ",
O_RDONLY|O_CLOEXEC) = 3`). Read-only, and procfs content is not read (st_size 0 fails `need()`),
so disclosure is a path-existence / GGUF-validity oracle — but any loopback service now holds
that capability over the probe user's file system. Minimal fix: document the boundary and skip
`/proc`,`/sys`,`/dev` + check `realpath`, or require paths under a configured model root.

**F3 — DEFECT (new at M): no cap on the answer body; TMPDIR fills at wire speed.**
`fetch()` (:321-322) uses `curl -o` with `--max-time` only: no `--max-filesize`, and the body is
`json.load`ed afterwards. One 5 s hostile answer wrote **52 MiB** into the mktemp dir
(`receipts/diskfill.out`; a faster sender scales with link speed [INFERENCE]), and a 200 MB body costs
**598 MB RSS / 8.5 s** (`c_str50m`). On a tmpfs TMPDIR that is RAM. Minimal fix:
`curl --max-filesize 8388608` (also for `/props`) plus a `stat` size check before `json.load`.

**F4 — DEFECT (pre-existing at base 56174a1f, still live in the C1 counter's input): ids and
status values reach stdout unsanitised.** `served_ids` (:362) prints every `id` verbatim (no
`\t\r\n`/C0 filter — `router_entries` filters `id` for `\t\r\n` at :649 and `value` for `\t\n`
only at :657); `jstr` (:199) escapes only `\ " \t \n \r`. Measured on base and M: an id with
`\n`+tabs forges a whole extra table row with arbitrary columns (`i_inj-id-nl`); `\r` survives
into `reason`/`served_model`; a valid `\u0001` in an id or value makes `--json` **exit 1 with
empty stdout** and `kama-probe: internal error: generated JSON failed to parse (this is a probe
bug)` plus a traceback (`ij2_inj-id-esc2`), which makes the C1 counter raise `CannotEvaluate`
(round89-unloadable-cells.py:186). Impact: forged table rows (machine consumers of table mode),
and no verdict at all for the counter — never a false green. Minimal fix: apply the same
`\t\r\n`+C0 filter in `served_ids` and escape C0 in `jstr` (or emit with `json.dumps`).

**F5 — NOTE: TOCTOU between `os.stat` (:514) and `open` (:523); no `O_NONBLOCK`.**
A symlink flipped regular→FIFO in that window makes `open(path,"rb")` block on the FIFO.
Measured window: **87,914 / 858,088 (10.25 %)** of stat+open pairs had stat=regular and
open=FIFO (`receipts/race2.out`, `race.py`). End to end with that symlink as `--model`:
**45 of 200 probe invocations (22.5 %) blocked >3 s** and needed SIGKILL; the 155 that
completed ran ≤1.65 s (82 `MODEL_UNLOADED`, 73 `MODEL_OK`). Replication: 22/120 (`race3.out`);
`/proc/<pid>/syscall` of the stuck helper is `257` = **openat** (`race4.out`). FIFO /
symlink→FIFO / /dev/stdin / /proc/self/fd/0 are *not* reachable without the race — stat rejects
them first, so the direct vector is closed. Impact: a local writer who can swap a path hangs the
probe (read-only, so no wrong verdict). Minimal fix:
`fd=os.open(path, os.O_RDONLY|os.O_NONBLOCK)`; `os.fstat(fd)` + `S_ISREG`; `os.fdopen(fd,"rb")`.

**F6/F7 — NOTE: bounded memory plateau; `--timeout` bounds only curl.** 1e6 tensor infos (24 MB
sparse file) allocate **80 MB** before the layout check rejects them (`c_mem`); `MAX_KV`/
`MAX_TENSORS` make this a plateau, not a leak. No overall deadline exists (every hostile-cost
measurement above ran with `--timeout 5`); a slow listener surfaces as `DEAD timeout` — a false
red, the fail-safe direction, not MODEL_OK.

**F8 — NOTE: design-consistent non-findings.** Missing → `router-model-missing`; not-GGUF,
directory, FIFO, char devices, procfs size-0 files → `router-model-invalid`; unreadable file,
relative path, non-file `args[0]` → no change. No path string ever reaches output (only the
`missing|invalid|ok|-` enum), so path injection into the TSV/JSON is impossible. Base has no
file-read code at all (`git show 56174a1f:tools/kama-probe.sh | grep gguf_state` → one comment
at :1123), so F1–F3 and F5 are new surface; F4 predates M.

## Deliverables
`.ufo/waves/round-89/w1/out/SN01ProbeSafety/`
- `scripts/`: `probe-M.sh`, `probe-B.sh` (reviewed bytes), `srv.py` (hostile stub), `drive.py`,
  `mkbody.py`, `craft.py`, `mkbombs.py`, `race.py`, `race2.py`, `race3.py`, `diskfill.py`.
- `receipts/`: `CASE.json` per cell (rc, wall, `/usr/bin/time -v`, stdout, request log),
  `*.strace`, `*.requests.log`, `race*.out`, `diskfill.out`; large bodies are regenerated by
  `mkbombs.py` + `craft.py`.

VERDICT: partial — frozen classes and direct FIFO/device/procfs paths grade right, but listener-chosen paths burn unbounded CPU (41 s from 219 B), fill TMPDIR at wire speed and open any readable absolute path; a C0 id kills `--json`.
