# SN01AnswerSafety — round-90 answer boundary (security review)

## Scope

Answer-boundary review of `tools/kama-probe.sh` at M `f968fb19bb2a0c2afe271bfe606f11b52d10823f`
(probe sha256 `c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`), compared with
base `99cdb4d6270455494dd27901efe84a0f3b342062` (probe `c15ffca8f6b4f07f19fe378d08b8495f2b345dd53face17b686c78ea5cc73238`).
Questions: (a) TMPDIR/RAM fill via `-D "$FHDR"` and the `/health`, `/`, `/metrics` probe_short
calls; (b) `--max-filesize` bypass (CL lie, 1xx, trailers, HTTP/0.9, TE/CE gzip); (c) injection
into snapshot TSV/history; (d) hang past `--timeout`. Stubs on free loopback ports only; 1234
never contacted; lane read-only (the worktree's uncommitted edits to `tools/kama-probe.sh`,
`SKILL.md`, `SCORECARD.md` and `corpus/*` are other seats'; this seat wrote only
`.ufo/waves/round-90/w1/`).
## Commands and outputs (probe exit codes)

Driver: `python3 run_case.py <case> <mode> [N] [KIB] [--probe PATH] [--sub snapshot --snapfix]`
(copy in `out/SN01AnswerSafety/repro/`; cases ran from `/fast/scratch/hyaku/kama-r90/SN01AnswerSafety`,
removed after the receipts were copied). The driver exits 0 and records the probe rc.

- `hdr1000 hdrflood 1000 8` → rc 2, hdr_peak 311,313 B, 0.03 s; evidence `rc=56 Too large response headers: 311313 > 307200`.
- `hdr30 hdrflood_slow 30 8` → rc 0 MODEL_OK, hdr_peak 245,831 B. `hdr40 hdrflood_slow 40 8` → rc 2, hdr_peak 311,313 B.
- `info1xx info1xx 500 8` → rc 2, hdr_peak 312,244 B, `rc=56 Too large response headers`.
- `trailers trailers 500 8` → rc 2, `rc=100 Out of memory in chunked-encoding` (CURLE_TOO_LARGE).
- `bigbody` (CL 64 MiB) → rc 2 FOREIGN_SERVICE `body-too-large`, tmp_peak 0. `cl_just_over` (CL 4,194,305) → rc 2 body-too-large.
- `chunked_big` / `close_big` (64 MiB) → rc 2 body-too-large. `cl_short` (CL 10, 64 MiB sent) → rc 2 FOREIGN_SERVICE `schema-unrecognized` (curl wrote 10 B).
- `http09` → rc 2 NOT_HTTP `no-http-response` (`rc=1 Received HTTP/0.9 when not allowed`). `te_gzip` → rc 2 (`rc=61 Unsolicited Transfer-Encoding`). `ce_gzip` → rc 2 `schema-unrecognized` (no decompression).
- `router_unloaded` (/props 64 MiB) → rc 2 MODEL_UNLOADED `router-unloaded`, 0.15 s. `router_autoload_ok` → rc 0 MODEL_OK `router-unloaded-autoload`.
- `mixed_hdrflood` (/v1/models HTML; `/` and `/metrics` flood) → rc 2, tmp_peak 92 B, `/` → `err-56`.
- `huge_ids 200000` (body 4,000,028 B) → rc 2, **wall 207.2 s**, tmp_peak 5,048,680 B, max RSS 92,492 KiB.
- Scaling `huge_ids`: 5k 3.99 s, 10k 9.72 s, 20k 11.73 s, 50k 40.47 s; match path `--expect m0000000` 20k 27.76 s.
- Base: `B_bigbody` tmp_peak 67,108,971 B, MODEL_MISMATCH (64 MiB written and parsed); `B_ids20k` 15.86 s; `B_inject` table carries raw TAB/ESC/DEL.
- `snap_inject inject_id --sub snapshot --snapfix --json` → rc 2, 0.18 s; latest.tsv/DELTA.md/JSON inspected.
- `nopy_inject inject_raw --path <bin-without-python3>` → rc 2, 0.07 s; table carries raw TAB/ESC/DEL.
- `mixed_slow` → rc 2, 10.05 s (`/` 5 s + `/metrics` 5 s). `health_slow` → rc 0, 5.10 s. `slow_body` → rc 2, 5.03 s. `chunked_hang` → rc 2, 5.04 s. `body_then_hang` → rc 0, 0.10 s (curl stops at Content-Length).

## Findings

### F1 DEFECT — the answer boundary is not time-bounded (answers (d): yes)

A 4,000,028-byte `/v1/models` answer (under `MAX_BODY=4194304`) carrying 200,000 ids makes
`check` run **207.2 s** with `--timeout 5` (41×), exit 2, RSS 92,492 KiB (90.3 MiB). Cause: `model_matches`
forks `$(normalize_id "$s")` once per id (`probe-M.sh:437-446`); `router_refine` calls
`model_matches` per router entry (`probe-M.sh:777-785`), doubling the cost when the expected id
matches (20k: 11.73 s → 27.76 s). A 20k-fork microbenchmark takes 11.6 s, so the cost is the
fork, not JSON parsing. `cmd_listeners` classifies **every** loopback port (`probe-M.sh:1151`),
so any local listener can stall `kama-probe.sh listeners` for minutes; `check`/`snapshot` on a
declared hostile port inherit it. Base has the same behaviour (`B_ids20k` 15.86 s), so this is a
carried gap, not a C1 regression; the C1 predicate (13 cells) does not cover it, but the claims'
held-out list names "very long ids". Extrapolation to the shortest unique ids (~320k) is
~5.5 min [INFERENCE from the linear fit]. Smallest remediation: cap the id count (e.g. first
4096) before `model_matches`/`router_refine`/`print_table`; inline `sn=${s##*/}; sn=${sn%.gguf}`
instead of `$(normalize_id …)`; add a `SECONDS`/`timeout` guard around post-processing.

### F2 DEFECT (latent) — the python3-absent grep fallback does not strip control bytes

`probe-M.sh:427-430` extracts ids with `grep -oE` and `sed` only; the python path escapes
C0/C1/DEL (`probe-M.sh:413-416`). With python3 absent from PATH (an explicitly supported mode,
probe header line 86), a raw TAB in an id splits the table into extra columns and raw ESC/DEL
reach the terminal (evidence: `evidence/results/nopy_inject.json`; table shows `evil` then
`TAB,evilSC,evilDEL,...`). Default host has python3, so latent. NOTE: the lane worktree now
carries an uncommitted EX03 edit to exactly these lines (`git diff tools/kama-probe.sh`:
`grep -a` + `tr -d '\000-\011\013-\037\177'`); all measurements here are against the M bytes.
Remediation: apply that same filter to the fallback.

### F3 NOTE — the header bound is curl's, not the probe's; measured and sufficient

curl 8.23.0 caps total response headers at 307,200 B: 240 KiB of headers is accepted
(hdr_peak 245,831 B, MODEL_OK), 320 KiB aborts with `rc=56 Too large response headers: 311313 >
307200` (hdr_peak 311,313 B), and 500 × 8 KiB 1xx blocks abort the same way (312,244 B). Trailers
hit `rc=100` (CURLE_TOO_LARGE). `probe_short` passes no `-D`, so `/health`, `/`, `/metrics`
write no headers at all (mixed_hdrflood tmp_peak 92 B). So the seat's (a) hypothesis is
falsified: `-D "$FHDR"` cannot fill TMPDIR on this curl. Residual: the probe has no independent
header-size check, so the bound tracks the curl build (S587 pins 8.23.0), and a header flood is
reported as `NOT_HTTP connection-reset` (coarse reason, honest evidence text).

### F4 NOTE — no `--max-filesize` bypass found

Truthful CL 64 MiB, CL 4,194,305, chunked 64 MiB and close-delimited 64 MiB all abort at the cap
with `body-too-large`; the probe truncates the partial body, so the retained file is 0 B, but a
chunked/close-delimited transfer writes up to ~MAX_BODY before the abort (measured 3.89/3.94 MB
transient). A CL lie (CL 10, 64 MiB sent) makes curl stop at the
declared length, so only 10 B reach `FBODY` and the answer cannot be graded MODEL_OK. HTTP/0.9 is
refused (`rc=1`), `Transfer-Encoding: gzip` is refused (`rc=61`), `Content-Encoding: gzip` is not
decompressed (schema-unrecognized). A 64 MiB `/props` answer means "not autoload" (0.15 s).

### F5 NOTE — U+2028/U+2029 survive into latest.tsv, DELTA.md and the snapshot JSON

`clean()` escapes C0/C1 (U+0085 included) but not U+2028/U+2029, and `persist_clean` strips only
`[:cntrl:]`; both code points land raw in the ledger (evidence: `evidence/snap/latest.tsv` bytes
`342 200 250` / `342 200 251`; `DELTA-transition.md`). `str.splitlines()` then sees 4 lines in a
2-line latest.tsv and 12 in a 10-line DELTA.md, i.e. forged rows for any Python splitlines
consumer. No in-lane consumer does that (the probe uses bash `read`), so no current impact; the
claims list U+2028 as a held-out cell. Commas in ids are not escaped either, but
`served_persist` splits and rejoins them, so the persisted string is unchanged. Remediation:
escape U+2028/U+2029 in `clean()`/`persist_clean`.

### F6 NOTE — per-row wall time is a multiple of `--timeout`

`mixed_slow` takes 10.05 s (fast `/v1/models`, then `/` and `/metrics` at 5 s each); `health_slow`
5.10 s; `slow_body` 5.03 s; `chunked_hang` 5.04 s. `--timeout` bounds one transfer, not a row, and
`snapshot` multiplies by row count. A declared hostile port can cost ~10-15 s per run.

### F7 NOTE — TMPDIR and RAM stay bounded

Per-row TMPDIR peak 5,048,680 B at M (200k-id case) versus 67,108,971 B at base (64 MiB body);
the `-D` header file peaks at ~311 KiB; `/props` and the body share the 4 MiB cap. Peak RSS
92,492 KiB at the 200k-id worst case and 31,576 KiB at 50k. No disk or memory fill.

## Deliverables

- `.ufo/waves/round-90/w1/out/SN01AnswerSafety/README.md` — findings index and evidence map.
- `…/out/SN01AnswerSafety/repro/{repro.sh,stub.py,run_case.py}` — reproducers; `repro.sh` extracts
  the M probe from git, verifies `c197912f…`, and runs the case groups (`hdr body props snap nopy
  slow ids router`).
- `…/out/SN01AnswerSafety/evidence/results/*.json` — per-case rc/wall/TMPDIR/header measurements.
- `…/out/SN01AnswerSafety/evidence/{ids200k_full,ids50k_rss}.time.txt`, `probe-sha256.txt`.
- `…/out/SN01AnswerSafety/evidence/snap/` — hostile-id latest.tsv, DELTA.md and snapshot JSON.

VERDICT: partial — body/header/TMPDIR/RAM bounds hold at M, but the answer boundary is not time-bounded (4 MiB/200k-id answer → 207 s at --timeout 5) and the python-free fallback still emits raw C0/DEL to the table.
