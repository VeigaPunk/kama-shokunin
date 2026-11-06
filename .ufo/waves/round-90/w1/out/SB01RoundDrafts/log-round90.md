## Round 90 — 2026-11-06 (hostile listener answers stay bounded; the probe's reason codes get a wire-bound table)

Frozen plan `plans/round-90-claims.md` (freeze `6f6d7873`; base `99cdb4d6`). Motivating evidence: the round-89
probe accepted a 64 MiB `/v1/models` answer as `MODEL_OK` (H1/H2) and a 64 MiB `/props` answer as autoload
(H3), widened its table to 9 columns on an id carrying a tab (H4), left `--json` unparsed on a U+0001 id and on
an ESC in the `Server:` header or router status (H5/H7/H8), and printed raw ESC in table mode (H6–H8)
(`.ufo/waves/round-90/controls/c1-base.out`, `mismatches=8`).

- Tool install: none recorded — host curl 8.23.0 (the tag S587 documents) and Python 3.14.8 sufficed.
- **C1 operability (sourced S587/S588):** `tools/kama-probe.sh` caps every listener answer body at
  `MAX_BODY=4194304` (`curl --max-filesize` on the `/v1/models`, `/props` and `probe_short` fetches, plus a
  `wc -c` re-check for older curl); an oversize `/v1/models` answer is `FOREIGN_SERVICE body-too-large` (rc 63),
  an oversize `/props` is "not autoload"; ids are printed with C0/DEL/C1 as `\uXXXX` text, router ids/status
  values are filtered to `?`/dropped, `Server:`/`Content-Type` headers and curl error text lose control bytes
  (`strip_ctl`), and `jstr` escapes every U+0001–U+001F and DEL. Counter
  `tools/round90-hostile-answers.py` `mismatches=8 → 0`, positives 0 → 0 (`measured/c1.out`); harm suites
  unchanged (`measured/harm-M.out`: 77/77, 30/0, r89 cells 11/0, operator router `MODEL_OK
  router-unloaded-autoload`).
- **C2 depth:** SKILL §"Probe reason codes" — 24 rows (the 23 frozen reason codes plus `body-too-large`), each
  bound to a captured probe answer by `tools/round90-reason-rows.py`; receipt `measured/reason-cells.jsonl`
  (24 cells, every line naming the probe's sha256) produced by `tools/round90-reason-capture.py`; base
  `documented=0 missing=23`, M2 `documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1`
  (`measured/c2.out`, uncommitted at draft time; the L1 commits it).
- Knowledge `corpus/knowledge/probe-answer-bounds.md`; SOURCES S587/S588 (admit); README round-90
  coverage/frontier; lesson `corpus/lessons/round-90.md` (M1, M2).
- Wave 1 (13 seats, `.ufo/waves/round-90/w1/`): [L1 to append the seat outcomes; at draft time
  `EX02HarmLatency` and `MT02ReasonRowMutants` artifacts had landed, no seat report].
