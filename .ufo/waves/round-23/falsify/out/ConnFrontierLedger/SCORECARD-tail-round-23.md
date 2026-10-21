## Round 23 — repository-local git state and the auditor's exit class

Declared C1 calibration **7 → 7**, narrow (lowest assigned non-retired axis).
Frontier **D4 partially advanced** — report-audit repository trust, not
untrusted-repository safety (KQ32 stays in force). Round base `4fe9339f`;
lane master `245a37f6`. The counts below were re-run at `245a37f6` by the
falsify connector on 2026-10-21; the L1's post-integration run remains the
record of authority.

| Arm | Graded fault rows | Controls | Tracebacks / executed / timeouts |
|---|---|---|---|
| Frozen commit `4fe9339f` (blob `fcc255ce`) | 0/26 | 8/8 | 9 / 2 / 1 |
| Current | 26/26 | 8/8 | 0 / 0 / 0 |

Commands: `python3 tests/report-audit/repo-state-grid.py --arm both --json`
(exits 1 because the frozen arm is red by design; frozen counters reproduced
three times) and `python3 tests/report-audit/isolation-mutants.py --json`
(24 committed mutants, 22 killed; survivors `M02-lazy-fetch` and
`M20-log-sha-shape`).

The 26 is not 26 independent isolation wins: falsify's patched-frozen probes
show F17/F21/F23 record contract changes and five more rows pin current's
wording, leaving at least 18 fair frozen failures. The mutant population is
not complete: supplementary single-line mutants outside the committed 24
survive the current grid (detector-coverage findings, MutRetestA–D), and
`M02` is load-bearing against `remote.*.partialclonefilter`, where removing
the flag lets a repository-configured `core.sshCommand` execute once (P01).
The lesson's `8 tracebacks` is corrected here to 9: seven strict-decode
`UnicodeDecodeError` rows and two integer-digit `ValueError` rows (F24/F26).

Operability is a **trade, not unchanged**. On complete local lane/fleet
fixtures, frozen exits 0 while current exits 2 for an inert zero-byte
`*.promisor` marker, `remote.origin.promisor=false`, and a non-UTF-8
`branch` config name (reproduced by this seat). The `--shared` clone recipe
bypasses the promisor refusal entirely and yields a false
`unresolved-full-hash` for an object present only on the promisor (both
arms). Dated incident: four zero-byte `.promisor` markers in the real fleet
root refused the real rounds 10–22 gate at exit 2 when observed at 12:50 and
again at 12:58 -0300; they were absent when rechecked at 13:05, after which
both arms are byte-identical again on the real population (clean exit 0,
`--no-errata` exit 1, sha256 `1ae84922…`/`13b17b1c…`).
The writer has not been identified. The presence-only marker check remains a
code fragility independent of that incident (fixtures above).

Frontier disposition: **D4 partially advanced** on the graded channels.
Still open: alternates (O01) and `.git` gitfile redirect (O02) resolve as
local; peel/cross-repo ambiguity overwrite (F1); first-`## Landed changes`
section only; CR inside an errata line; `log.follow` path contract;
`citation-provenance.py` and `sources-append-only.py` unisolated; the
`--shared` promisor-status hole and the over-refusal class above. Routed
debt not re-measured here: prelaunch snapshot race, 41-hop chain bound, JSON
duplicate-key/Unicode limits, selftest fallback/GIT_DIR assertions, and the
R20 limits/L0 items. Declared tradeoffs: shallow and partial clones are
refused even when every cited object is local; `--no-lazy-fetch` sets a
git ≥ 2.45 floor. Other frontier unchanged: external-system-library
identity, receipt-header minimization, historical crash-as-kill leaves,
K05/other-engine serving and real registered-consumer reconciliation. No
endpoint sample, service restoration or new capability row is asserted.
