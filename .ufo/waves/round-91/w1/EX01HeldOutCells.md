# EX01HeldOutCells — round 91 w1, held-out cells for C1 (operability)

## Scope
- Attack C1 outside its frozen predicate: run the base probe B and the measured probe M against
  21 lane-owned stub cells (the 9 listed cases, split where sharper = 14, plus 7 extra
  rule-discriminating cells H10–H15 + H12b), 42 probe runs.
- Revisions: B=`c06838c5b94576971ea33ac465bf2c935e9037f9` (probe sha256 `b71c309a…b48d7`),
  M=`3decfa36b0eba7e5197c034dd1547146bca1568a` (probe sha256 `0aa43573…75da`). The probe at
  current master `3f317ecd…` has the same sha256 as M's, so the probe is unchanged after M.
- Harness reuses the frozen counter's `Stub`, `jbody`, `ids_doc`, `run` (KILL=120 s, check invoked
  as `check --port P --expect E --timeout 5 --connect-timeout 2 --json`), so stub framing and the
  kill are identical to `tools/round91-answer-time.py`. It imports the counter with
  `sys.dont_write_bytecode` set, so no cache is written into the lane tree.
- Live-endpoint safety: only stubs on free 127.0.0.1 ports. The listeners cell used
  `listeners --port <stub>`, which takes the `OPT_PORT` branch (`probe-M.sh:1170`) and never runs
  `loopback_ports`/`ss`; no POST/load and no request to 1234. Receipts contain no `127.0.0.1:1234`
  (checked) and 35 distinct ephemeral stub ports, none 1234.
- Host load: 1-min load 28.02–75.61 on 32 cores during these runs (per-run load in heldout.tsv).
  Small cells were re-run at load 75.61 and stayed ≤ 0.43 s.
- Tools installed/updated: none.

## Commands and outputs
```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show c06838c5…:tools/kama-probe.sh > probe-base.sh   # rc 0
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 3decfa36…:tools/kama-probe.sh > probe-M.sh       # rc 0
python3 heldout-cells.py --base …/probe-base.sh --m …/probe-M.sh --out run  --work <scratch>  # rc 0 (21 cells)
python3 heldout-cells.py … --only H12-…,H13-…,H14-…,H15-…                                    # rc 0 (4 cells)
python3 heldout-cells.py … --only H12b-…                                                     # rc 0 (1 cell)
```
Cell stdout is JSON (`rows[0]`; listeners: `listeners[0]`). Full invocation times:
run.log 23:29:04Z→23:39:35Z, run2.log 23:40:29Z→23:42:36Z, run3.log 23:43:14Z→23:43:16Z.

## Table (verdict/reason/seconds; per-run load in heldout.tsv)
| cell | base | M |
|---|---|---|
| H1 models[] 200k `name` keys, expected last | killed@120.10 s | MODEL_OK/matched 1.65 s |
| H1b same, expected absent | killed@120.10 s | MODEL_MISMATCH/served-id-mismatch 1.26 s |
| H2 200k duplicate ids (199,999 `dup` + `good`) | killed@120.11 s | MODEL_OK/matched 1.17 s |
| H3a CRLF-pretty JSON body | MODEL_OK/matched 0.16 s | MODEL_OK/matched 0.16 s |
| H3b id contains `\r\n` + plain `good` | MODEL_OK/matched 0.18 s | MODEL_OK/matched 0.16 s |
| H3c only id `good\r\n` | MODEL_MISMATCH/served-id-mismatch 0.14 s | same 0.15 s |
| H4 80k router entries, `--expect '*'` | MODEL_OK/expected-wildcard 7.18 s | same 1.78 s |
| H5 80k router entries, expected `unloaded`, /props autoload | killed@120.10 s | MODEL_OK/router-unloaded-autoload 1.38 s |
| H6 router listing, one 3.9 MB id then `good` | killed@120.10 s | MODEL_OK/matched 1.71 s |
| H7 `--expect /models/good.gguf` | MODEL_OK/matched 0.12 s | MODEL_OK/matched 0.12 s |
| H8a ids `1.0`,`1`; expect `1` | MODEL_OK/matched 0.11 s | MODEL_OK/matched 0.11 s |
| H8b id `1.0`; expect `1` | MODEL_MISMATCH/served-id-mismatch 0.09 s | same 0.10 s |
| H8c id `1`; expect `1.0` | MODEL_MISMATCH/served-id-mismatch 0.09 s | same 0.09 s |
| H9 `listeners --port <stub>` | MODEL_OK/matched 0.31 s | MODEL_OK/matched 0.30 s |
| H10 router entry id `q\b`; expect `q\b` | MODEL_OK/matched 0.12 s | MODEL_OK/matched 0.12 s |
| H11 `--expect /` (normalizes empty) | MODEL_MISMATCH/unresolvable-id 0.09 s | same 0.09 s |
| H12 80k entries, expected `/models/sub/good.gguf` `unloaded`, autoload | killed@120.10 s | MODEL_OK/router-unloaded-autoload 1.76 s |
| H12b same rule, 1 entry (scale isolated) | MODEL_OK/router-unloaded-autoload 0.40 s | same 0.41 s |
| H13 `good.gguf.gguf` loading + `good` unloaded, autoload | MODEL_OK/router-unloaded-autoload 0.42 s | same 0.40 s |
| H14 path+.gguf entry `loading` | MODEL_LOADING/router-loading 0.26 s | same 0.30 s |
| H15 router `1.0` loaded / `1` unloaded, autoload | MODEL_OK/router-unloaded-autoload 0.34 s | same 0.43 s |

## Findings
- **BLOCKER: none.** No held-out cell where base is right and M is wrong. M met the expected
  verdict and reason on 21/21 cells, all ≤ 1.78 s against the 20 s budget, at load 28–45.
  Evidence: `heldout.tsv`, `raw/*.json` (verdict/reason/seconds/served bytes).
- **NOTE (equivalence):** on the 15 cells where base completed, base and M JSON is identical after
  normalizing the ephemeral stub port — same verdict, reason, `served_model` byte count and
  evidence text. Evidence: pairwise diff over `raw/*.json` (14 identical; H9 differs only the
  integer `port` field). This corroborates that `paste -sd,` (`probe-M.sh:935`) joins the same
  bytes as the old `tr`+`${C_SERVED%,}` (`probe-base.sh:915-916`).
- **NOTE (base time is per-entry forks, not just the join):** H2 is a non-router answer whose 200k
  entries dedupe to two served ids, yet base spent 120 s (killed) because `router_refine` forks
  `model_matches` once per entry (`probe-base.sh:792,802`); M filters with one awk pass
  (`probe-M.sh:467-471,820`) and finished in 1.17 s with the same verdict.
- **NOTE (filter correctness can only be seen through the status refinement):** H12/H13/H14/H15
  were built so a `router_match` rule bug that drops the expected entry shows up as a false green
  (`MODEL_OK matched` instead of `router-unloaded-autoload` / `router-loading`). Base agrees on the
  small replicas H12b/H13/H14/H15; M agrees on all four, including path-plus-`.gguf` matching
  (H12/H12b), one-`.gguf`-only stripping (H13), and numeric-string comparison (`1.0` ≠ `1`, H15).
- **NOTE (H4 wildcard):** with `--expect '*'` base is under budget (7.18 s) because wildcard mode
  skips the per-entry filter; M is 1.78 s. Low load separation here is expected, not a regression.
- **NOTE (CRLF):** CRLF body separators are irrelevant to the counter's JSON parse, and CRLF inside
  an id is escaped by `served_ids` to `\u000d\u000a` text before matching, so both probes compare
  text and cannot split a line (H3a-c).
- **NOTE (S592 path):** H10 passes the expected id `q\b` through `ENVIRON` and the router's awk
  filter matched it identically to the base bash compare; no backslash processing was observed.
- **LIMIT:** not covered by this seat: the python-free path (`HAVE_PY=0`, another wave seat's
  item), NUL-in-id, and a large router id whose own last segment is `good.gguf` (T5 covers that
  shape only on the `/v1/models` path). H6 covers a 3.9 MB non-matching router id and the
  resulting 3,900,005-byte `served_model` emission.

## Deliverables
`.ufo/waves/round-91/w1/out/EX01HeldOutCells/`: `heldout-cells.py` (final harness),
`heldout.tsv` (42 rows), `raw/` (42 elided-output JSON receipts with raw sha256/length),
`run.log`, `run2.log`, `run3.log`, `probes/` (probe copies for B and M), `probes.sha256`.
Lane tracked files untouched (`git status --porcelain` tracked_changes=0); scratch removed.

VERDICT: holds — 21/21 held-out cells agree with base semantics where base completed (15/15, JSON identical modulo stub port) and M stayed ≤ 1.78 s on every cell; the 6 base cells killed at 120 s are all M-passing; no harm cell found.
