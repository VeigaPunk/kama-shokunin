# SN01AnswerSafety — round-90 answer-boundary review (M f968fb19)

Scope: can a loopback listener (a) fill TMPDIR/RAM through headers or the probe_short calls,
(b) bypass `--max-filesize`, (c) inject into the snapshot TSV/history, (d) make the probe hang
past `--timeout`? Probe measured: `tools/kama-probe.sh` at
`f968fb19bb2a0c2afe271bfe606f11b52d10823f`, sha256
`c197912f8b3b5567e3ffd38178cb3a6e87187d7fb13136308c9a461ba8d2ef97`. Base probe at
`99cdb4d6270455494dd27901efe84a0f3b342062`, sha256 `c15ffca8…` (see evidence/probe-sha256.txt).
All stubs are lane-owned children on free loopback ports; 127.0.0.1:1234 was never contacted.

## Findings

| id | severity | one line |
|----|----------|----------|
| F1 | DEFECT | a 4 MiB `/v1/models` answer with 200k ids makes `check` run 207.2 s at `--timeout 5`; `listeners` classifies every loopback port, so any local listener can stall the census for minutes |
| F2 | DEFECT (latent) | the python3-absent grep fallback (`probe-M.sh:427-430`) does not strip C0/DEL: a raw TAB/ESC/DEL id forges table columns and reaches the terminal |
| F3 | NOTE | the `-D` header file is bounded by curl's 307,200-byte total-header cap (measured 311,313 B), not by the probe; `probe_short` writes no headers at all |
| F4 | NOTE | no `--max-filesize` bypass found: CL-lie, chunked, close-delimited, 1xx, trailers, HTTP/0.9, TE/CE gzip all stay bounded or fail closed |
| F5 | NOTE | U+2028/U+2029 survive `clean()`/`persist_clean()` into latest.tsv, DELTA.md and the snapshot JSON; `str.splitlines()` sees forged rows (no in-lane consumer does) |
| F6 | NOTE | per-row wall time is a multiple of `--timeout` (measured 10.05 s for `/` + `/metrics`), multiplied by registry row count |
| F7 | NOTE | TMPDIR/RAM stay bounded: per-row peak 5,048,680 B at M (vs 67,108,971 B at base), RSS 90.3 MiB (92,492 KiB) at the 200k-id worst case |

## Reproduce

```
cd <this dir>/repro
SCRATCH=/fast/scratch/hyaku/kama-r90/SN01AnswerSafety-repro ./repro.sh hdr|body|props|snap|nopy|slow|ids|router
```

`repro.sh` extracts the M probe from git (`git -C <lane> cat-file -p f968fb19:tools/kama-probe.sh`),
verifies sha256 `c197912f…`, copies `stub.py`/`run_case.py` into `$SCRATCH`, and runs the cases.
Each case starts one stub, runs `bash probe check --port N --expect stories260K` (or `snapshot`
with a scratch registry/history), measures wall time, peak TMPDIR bytes and the `*.hdr` peak, then
kills the stub's process group. `PROBE=<file>` overrides the probe (must still hash to M).

## Evidence map

- `evidence/results/*.json` — one result per case (rc, wall_s, tmp_peak_bytes, hdr_peak_bytes,
  requests, stdout/stderr tails).
- `evidence/results/ids200k_full.json` + `evidence/ids200k_full.time.txt` — 207.2 s, 92,492 KiB RSS.
- `evidence/results/ids50k_rss.json` + `evidence/ids50k_rss.time.txt` — 30.1 s, 31,576 KiB RSS.
- `evidence/snap/latest.tsv`, `DELTA-baseline.md`, `DELTA-transition.md`, `*.json` — snapshot
  persistence from a hostile id set (raw U+2028/U+2029 visible with `cat -A`; `splitlines`
  divergence: latest.tsv 4 vs 2 lines, DELTA 12 vs 10).
- `evidence/probe-sha256.txt` — M and base probe hashes.

## Notes

- The lane worktree currently carries an **uncommitted** edit to `tools/kama-probe.sh`
  (`git diff` shows "wave-1 EX03 F1": `grep -a` + `tr -d '\000-\011\013-\037\177'` in the grep
  fallback). It addresses F2 but is not at M; all measurements here are against the M bytes.
- The header cap is a curl property (8.23.0). The probe has no independent header-size check, so
  the bound moves with the curl build; S587 pins 8.23.0.
- `listeners` misclassifies a header-flood answer as `NOT_HTTP connection-reset` (rc 56); the
  evidence text carries curl's exact byte counts, so the report is honest even though the reason
  code is coarse.
