# EX03 — kama r90 w1: the probe's no-python3 (HAVE_PY=0) path

## Scope
`tools/kama-probe.sh` at B=`99cdb4d6270455494dd27901efe84a0f3b342062` (sha256 `c15ffca8…`) and
M=`f968fb19bb2a0c2afe271bfe606f11b52d10823f` (sha256 `c197912f…`, identical to tip M2
`2ee0b55f…`), run with a PATH that has no `python3` (`command -v python3` → ABSENT, receipt
`nopy-python3-check.txt`). Cells: H4–H8 equivalents (JSON-escaped text, exactly as the frozen
counter builds them) plus raw-byte variants of the same ids/headers, and held-out DEL / U+0085 /
U+0000 / raw-newline ids. Stub servers are lane-owned, in-process, on free loopback ports; the
probe is the only client. No lane file was modified.

## Commands and outputs (true exit codes)
1. `PATH=<nopy> python3 tools/round90-hostile-answers.py --repo . --rev f968fb19… --work <scratch>`
   → **exit 1**, `cells=13 mismatches=2 positive_mismatches=2 probe=rev probe_sha256=c197912f…`
   (`counter-M-nopy.out`); failing cells P3-unicode-id, P4-json-specials.
2. same with `--rev 99cdb4d6…` → **exit 1**, `mismatches=5 positive_mismatches=2
   probe_sha256=c15ffca8…` (`counter-B-nopy.out`); failing H1, H2, H7, P3, P4.
3. `python3 tools/round90-hostile-answers.py --repo . --rev f968fb19…` (normal PATH) → **exit 0**,
   `cells=13 mismatches=0 positive_mismatches=0` (`counter-M-py.out`) — predicate corroborated.
4. `python3 runner.py` (13 cells × {B,M} × {HAVE_PY=1,0}, table + `--json`) → **exit 0**, 52 rows
   (`results.jsonl`, `summary.tsv`).
5. `bash jstr_test.sh jstr-M.inc` / `jstr-B.inc` → M `"a\u0001b\u001bc\u007fd\te\nf"`, 0 raw control
   bytes; B leaves 0x01/0x1b/0x7f raw (3 bytes).
6. `ss -ltnpH` on a listener whose `/proc/self/comm` is `ev\x1b[2Jx` → ss prints `"ev.[2Jx"`; no
   control byte reaches the probe's `OWNER` field.

## Findings

**F1 DEFECT — C1's id sanitization is python-only; raw control bytes still reach table output on M
with HAVE_PY=0.** The python branch escapes controls via `clean()` (`tools/kama-probe.sh:413`,
inside the `HAVE_PY=1` block at :386); the grep fallback (:427) has no equivalent, and every table
row prints `"$C_SERVED"` raw (`tools/kama-probe.sh:1164` listeners, `:1216-1217` check --port,
`:1234` registry). Measured at M, HAVE_PY=0:
- raw TAB in an id → header widens to **10 columns, 3 empty** (7 at M with python); the served cell
  splits into `good,evil | FORGED-ROW | x | MODEL_OK` (`capture.json` H4raw-tab/M; the frozen H4
  pass condition "no row carried more tab-separated fields than the header names" would read ok=0).
- raw ESC in an id → `0x1b` on stdout (`capture.json` H6raw-esc/M, table bytes
  `... | MODEL_OK | matched | good,\x1b[31mRED | ...`).
- raw `0x01` and raw DEL in an id → both bytes on stdout (DEL/U+0085 bodies are **valid** JSON per
  RFC 8259 §7, so this needs no malformed answer).
Base behaves identically on all four (B vs M byte-for-byte in the table cell), so C1 neither
introduced nor fixed it.

**F2 DEFECT (pre-existing, not caused by C1) — the grep fallback false-reds legitimate ids.** Under
HAVE_PY=0 the frozen counter fails P3-unicode-id and P4-json-specials at **both** B and M
(`served-id-mismatch`): `json.dumps` writes `\u00e8`/`\"`, and the fallback compares the escaped
text. A real model server with a non-ASCII or quote-bearing id therefore grades MODEL_MISMATCH
(exit 2, drift) on a python-free host. This is the only remaining mismatch pair at M in that
environment, and it is a positive (harm) class in the frozen counter.

**F3 NOTE — the JSON path is *not* python-only at M.** `jstr` (`:204-222`) escapes U+0001–U+001F and
DEL in pure bash; with HAVE_PY=0, M emits parseable JSON where base emitted invalid JSON
(H5raw-u0001 B `json=unparsed:Invalid control character`, M `ok`; H6raw-esc same; H7 B unparsed, M
ok). Verified independently by the `jstr` unit test (command 5).

**F4 NOTE — header/Content-Type/curl-error stripping is shell-only and works.** `strip_ctl`
(`:226`) runs in `fetch` for `F_CT`, `F_SERVER`, `F_ERRMSG` (`:350,354,358`). H7 (`Server: evil\x1b[2Jx`)
passes at M with HAVE_PY=0 (`esc=0`, JSON ok) and fails at base (`esc=1`, JSON unparsed).

**F5 NOTE — the body cap is shell-only and works.** `--max-filesize` + `wc -c` re-check (`:340-347`)
hold without python: H1 sent=458824 (base 67108864), H2 sent=5374024 (base 67108864), both
FOREIGN_SERVICE.

**F6 NOTE — router refinement is python-only, so H8/H3 degrade silently without python.** At
HAVE_PY=0 `router_entries`/`router_autoload` return nothing (`:743,748,759`): H8 grades
`MODEL_OK matched` (M with python: `MODEL_UNLOADED router-?`), and H3 never fetches `/props`
(`sent=0`) so its "oversize /props" pass condition is vacuous. No leak, but the verdict is weaker
than the frozen cell claims.

**F7 NOTE — the frozen counter cannot see F1.** Its H4–H6 ids are JSON-escaped text, which the grep
fallback passes through literally (no real TAB/ESC/U+0001 ever reaches the table), and the counter
inherits the caller's PATH, so it always exercises HAVE_PY=1. A raw-byte H4 would fail at M.

**F8 NOTE — escape ranges differ between the two paths.** `clean()` escapes 0x7F–0x9F; `jstr` escapes
only 0x01–0x1F and 0x7F. U+0085 (NEL, valid UTF-8 in valid JSON) is escaped at M with python and
reaches the table raw without it (`capture.json` X-u0085-raw/M).

**F9 NOTE — no test covers HAVE_PY=0.** `grep -rn HAVE_PY tests/ tools/*.py` finds nothing; the
probe warns and degrades (`:1553-1554`) while `SKILL.md:195` lists python3 as a probe dependency.

## Deliverables (out dir)
`results.jsonl` (52 measured rows), `summary.tsv`, `capture.json` (raw table bytes per leak cell),
`counter-M-nopy.out`, `counter-B-nopy.out`, `counter-M-py.out`, `runner.py`, `capture.py`,
`jstr_test.sh` + `jstr-M.inc`/`jstr-B.inc`, `bin-nopy.list`, `nopy-python3-check.txt`,
`probe-hashes.txt`.

VERDICT: partial — C1's frozen predicate holds (13/13, 0/0 with python3 at M, corroborated), but the id sanitization is python-only: with HAVE_PY=0 raw TAB/ESC/U+0001/DEL still reach table output at M, and two positive cells false-red.
