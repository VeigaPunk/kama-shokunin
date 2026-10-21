# RowC07CrlfReport — falsification of grid row C07-crlf-report

**Verdict: HOLDS.** Independent hand-built fixture (no grid import) reproduces
the claimed outcome on both arms; the expectation (exit 0, no defects) is the
semantically correct verdict; 21 near variants of the report line-ending
channel produced no crash, flip, hang, or execution on the current auditor —
only one pre-existing cosmetic kind-misclassification, identical in the frozen
arm (so not a calibration regression).

## Scope

- Row: `("C07-crlf-report", "control", c_crlf, 0, [])` —
  tests/report-audit/repo-state-grid.py:537 @ 245a37f6.
- Builder: `c_crlf` — grid:170-174. Lane commit by `kama-shokunin` @1000
  "round-1: work"; fleet commits `.ufo/reports/round-1/kama.md` @2000 with
  every `\n` replaced by `\r\n`.
- Expectation: exit 0, zero defects, no traceback/timeout/execution — i.e. a
  CRLF report must audit exactly like the LF original.

## Evidence — (1) premise real, observed as claimed

Hand-built fixture in /tmp (own helpers, `/tmp/kama-r23w2/.../c07_harness.py`,
clone HEAD verified `245a37f69628c2c6bb29bbf17897d8fb5946c857`). Premise
asserted directly on committed bytes, not by construction:

    git -C fleet cat-file blob HEAD:.ufo/reports/round-1/kama.md
    -> b'# kama round 1\r\n\r\n## Landed changes\r\n\r\n- <lc>\r\n'  (pure CRLF)

Runs (`python3 <auditor> --lane-repo lane --fleet-repo fleet --json --rounds 1
--no-errata`, env scrubbed of GIT_*, GIT_CONFIG_GLOBAL=/dev/null,
GIT_CONFIG_NOSYSTEM=1):

    [C07 frozen ] exit=0 kinds=[] defects=[] tb=False timeout=False met=True
    [C07 current] exit=0 kinds=[] defects=[] tb=False timeout=False met=True

Cross-check with the real grid in my clone:

    python3 tests/report-audit/repo-state-grid.py --arm both \
        --case C07-crlf-report --case C08-cr-only-report
    -> frozen/current C07: exit=0 kinds=[] tb=0 exec=0 timeout=0 met

Frozen arm behavior is explained, not magic: frozen `git()` used
`subprocess.run(..., text=True)` (frozen blob line ~91, sha256
09ecd63b… matching `4fe9339f:tools/report-landing-audit.py`), so Python's
universal-newline translation already mapped `\r\n`→`\n`. Current git()
(tools/report-landing-audit.py:127) does the same explicitly via
`out.replace("\r\n","\n").replace("\r","\n")` after a strict/surrogateescape
UTF-8 decode; the `--report` draft path (`read_report`, :209-215) uses
`Path.read_text` which is also universal-newline mode. Both ingestion routes
normalize before `landed_match` (:168-170) ever sees the text.

## Evidence — (2) expectation is the CORRECT verdict

The committed CRLF report is byte-equivalent to C01-clean modulo line
endings: real `## Landed changes` section, one cited full hash equal to the
only required lane commit, nothing else scannable. Exit 0 with an empty
defect set is the only truthful verdict; a `landed-section-missing` or
`landed-unresolved` here would itself be the fault. Confirmed the citation
resolves: `cat-file --batch-check` finds the 40-hex in the lane, and the
lane commit (author `kama-shokunin`, atime 1000 ≤ fleet first-add cutoff
2000, subject `round-1:`) is covered by its own citation → no `landed-omitted`.

## Evidence — (3) near variants of the channel

All variants: same lane/fleet shape as C07, report bytes mutated; both arms
run; auditors confirmed read-only between arms. Full results from harness
(run output preserved in /tmp/kama-r23w2/… scratch `/tmp/c07-hand-*`):

| variant | frozen | current | note |
|---|---|---|---|
| V1 mixed CRLF+LF | 0 clean | 0 clean | — |
| V2 `\r\r\n` endings | 0 clean | 0 clean | double-CR collapses to blank lines |
| V3 `\n\r` endings | 0 clean | 0 clean | — |
| V4 lone `\r` at EOF | 0 clean | 0 clean | — |
| V5/V6 no trailing newline (LF & CRLF) | 0 clean | 0 clean | — |
| V8 UTF-8 BOM + CRLF | 0 clean | 0 clean | BOM on `#` line harmless |
| V9 `\r` inside `## Landed changes` | 1 omitted+section-missing | identical | post-normalization `## Landed`≠heading; exit correct |
| **V10 `## Landed changes` as last line, no `\n`** | **1 omitted+section-missing** | **identical** | **see finding below** |
| V11 `\r` before `- ` item | 0 clean | 0 clean | blank line inserted |
| V12 CRLF + extra trailing CRLFs | 0 clean | 0 clean | — |
| VT/FF/NEL/U+2028 as sole separators | 1 omitted+section-missing | identical | non-Markdown endings; parity, defensible |
| mixed NEL inside CRLF doc | 0 clean | 0 clean | — |
| VT inside section body | 0 clean | 0 clean | — |
| CR-only doc (= C08) | 0 clean | 0 clean | — |
| CRLF draft via `--report 1=PATH` | 0 clean | 0 clean | read_report path also normalizes |
| `.gitattributes` `eol=crlf` / `working-tree-encoding` | n/a | blob bytes unchanged | `git show` does not convert (verified with od) |
| `.gitattributes` `filter=…` + `filter.*.smudge=touch /tmp/…/PWNED` (required) | n/a | **PWNED marker absent** | `git show` and `git log` do NOT run smudge filters; `git cat-file --filters` DOES (verified) — auditor never uses `--filters` |

No variant produced: traceback, timeout, marker execution, JSON-unparseable
stdout, or a verdict flip on a document whose Markdown is unchanged.

## Finding (minor, pre-existing, both arms)

`landed_match` (tools/report-landing-audit.py:169) requires the heading line
to end in `\n`: `^## Landed changes[^\n]*\n(.*?)(?=^## |\Z)`. A report whose
final line is exactly `## Landed changes` with **no trailing newline** is
misreported as `landed-section-missing` (+ `landed-omitted`) instead of only
`landed-omitted`. Exit code stays 1 (still a failure verdict), so this is a
kind-label inaccuracy, not a verdict flip — and the frozen arm behaves
identically, so it is outside C07's calibration delta. If the project wants
exactness, the fix is `(?=\n|\Z)` after `[^\n]*`.

`c_crlf` itself has no `require()` premise check (controls can't fail by
construction); I verified CRLF-ness on the committed blob bytes directly, so
the premise is real regardless.

## NOT verified

- Other grid rows, selftest, errata paths, ledger claims (out of scope).
- A live `git < 2.45` host: the `GIT_ISOLATION` `--no-lazy-fetch` floor is
  asserted only from the auditor's docstring/code (:88-96), not executed.
- Whether exotic separators SHOULD count as Markdown line endings — treated
  as defensible refusal-by-defect given both-arm parity.
- `git show` filter behavior on git versions other than 2.56.0.

## Files written

- This report (only lane-write): .ufo/waves/round-23/falsify/advice/RowC07CrlfReport.md
- /tmp/kama-r23w2/CloseKama22.RowC07CrlfReport-2/c07_harness.py — independent fixture/runner
- /tmp/kama-r23w2/CloseKama22.RowC07CrlfReport-2/frozen-audit.py — extracted frozen blob (sha256 09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f)

Tooling: no installs; git 2.56.0, python 3.14.8 (system).
