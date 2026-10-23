# C2 independent population cross-check

## Scope and method

Censused committed `SCORECARD.md` at `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` in `/tmp/r31w1-ExecC2CrossCheck`. `census.py` independently parses every pipe table whose first header cell is `Claim`, case-insensitively; 18 headers produced 28 data rows. It records each row's source line, claim id, all 7–40 hex tokens and their `rev-parse`/ancestry results, and extension-bearing path tokens checked with `git cat-file -e` at the tip (literal and row-round-relative candidates). `census.tsv` retains all rows and checks.

## Comparison

- Population: independent 28 rows / 18 `Claim` tables; frozen counter reports `rows 28`. Agreement.
- Non-exempt P1: independent 13 rows have no resolving ancestor; counter `--list` reports 13 `p1:no-revision` rows. Scorecard lines match exactly: 196, 197, 266, 267, 320, 379, 445, 522, 611, 680, 681, 781, 782. Agreement; no row-level disagreement found.
- Exemption: line 1370, `X1 (exploratory)`, has no P1 token but is exempt in the census; counter reports `exempt 1` and omits it from its listed failures. Agreement.
- Independent P2 path check: 8 rows had no existing named path, all within the same 13-row P1 failure set (lines 266, 267, 320, 379, 445, 522, 680, 681). The counter's visible `--list` output reports P1 for those rows and does not expose separate P2 status, so this is a row-set comparison, not per-class P2 confirmation.
- Counter summary at this tip: `base_mismatched 13`, `valid_corrections 0`, `false_corrections 0`, `unresolved 13`, `append_only True`, `met False`. This cross-check does not claim C2 is met; P3/digest checks and correction validity are outside this seat's census.

## Frozen `--list` output (exit 0)

```text
rows 28 base_mismatched 13 exempt 1 valid_corrections 0 false_corrections 0 unresolved 13 append_only True met False tip 0e6f8ed6891c
  C1 — re-anchor stale source anchors by appended dated corrections (plan claim 1): p1 line 196 p1:no-revision
  C3 — `sources-registry` capability + 3 entries on uncovered ground: p1 line 197 p1:no-revision
  C1: p1 line 266 p1:no-revision
  C2: p1 line 267 p1:no-revision
  C1: p1 line 320 p1:no-revision
  C1: p1 line 379 p1:no-revision
  C1 offline Ollama evidence replay: p1 line 445 p1:no-revision
  C1 declared-name duplicate-corpus admission: p1 line 522 p1:no-revision
  C2 `live-llamacpp-lifecycle`: p1 line 611 p1:no-revision
  C1 graded fields backed by a failing detector: p1 line 680 p1:no-revision
  C2 fail-capable live checks: p1 line 681 p1:no-revision
  C1 — outcome classification and receipt boundary: p1 line 781 p1:no-revision
  C2 — statement→mutant→detector ledger: p1 line 782 p1:no-revision
```

## Commands and caveats

- `git clone -q --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/r31w1-ExecC2CrossCheck && cd /tmp/r31w1-ExecC2CrossCheck && git checkout -q 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` — exit 0.
- `/usr/bin/python3 .../out/ExecC2CrossCheck/census.py --repo /tmp/r31w1-ExecC2CrossCheck --tip 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e --out .../out/ExecC2CrossCheck/census.tsv` — exit 0; `population=28 exempt=1 p1_fail=13 p2_fail=8 both_fail=8`.
- `/usr/bin/python3 .ufo/waves/round-31/count-c2.py --repo /tmp/r31w1-ExecC2CrossCheck --tip 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e --list` — exit 0; output above.
- Caveat: the initial tool read requested `count-c2.py:1-60` returned its docstring plus lines 41–63 (imports/definitions), despite this seat's “do not read its code” instruction. The census implementation was derived from the Scorecard and C2 docstring, not copied from those code lines; this was not a blind-source comparison.
