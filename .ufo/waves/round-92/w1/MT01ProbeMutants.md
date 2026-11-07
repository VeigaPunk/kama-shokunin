# Round 92 / wave 1 — `MT01ProbeMutants`

## Scope

Mutation test of the **C2 operability** change: `tools/kama-probe.sh` at **M2 =
`fa8aedb73d18448383c7a4d75405aba448fe8e38`** (probe sha256
`36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962`; byte-equal to the lane's
`tools/kama-probe.sh` at HEAD `d5a06431`, where the C1 receipts were landing). **19** single-point mutants were built in
seat scratch from pristine M2 bytes, each confined to a round-92 construct (`AWK_JSTR` / `jstr`
fast path / `LC_ALL`, `router_refine`'s `cand` array, `served_persist`'s awk: trailing-comma rule,
`NR>1 exit`, TAB/CR→space, control delete, empty→`-`, `n==0`). Each was judged by the three
assigned detectors, plus a distinguishing-input harness and a BASE differential. Host load:
42.34 at baseline, 48.51 at the restoration rerun.

## Commands and outputs (exit codes)

1. `round92-linear-paths.py --repo … --rev fa8aedb7… --work <scratch>/w --probe-file M2-probe.sh`
   → `LINEAR_PATHS cells=15 mismatches=0 positive_mismatches=0 probe=override
   probe_sha256=36631d49… base_sha256=0aa43573… rev=fa8aedb7…`, **exit 0**, 16.46 s
   (largest cell L1 2.03 s vs 20 s budget). Receipt: `out/base-counter.out`.
2. `KAMA_PROBE=M2-probe.sh bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0`, **exit 0**, 1.0 s
   (`out/base-snapshot.out`).
3. `check.py --probe M2-probe.sh` → `tests=77 passes=77 failures=0`, **exit 0**, 43.6 s
   (`out/base-check.out`).
4. Per mutant (19 × 3, driver exit 0): `out/run/summary.json`, `out/run/logs/<mutant>/*.out`.
5. Distinguishing harness (152 case rows, exit 0): `out/run/distinguish.out`,
   `out/dist/distinguish.json`; gap evidence pairs under `out/dist/<mutant>-<case>/`.
6. BASE differential (`BASE-probe.sh` sha256 `0aa43573…`, the counter's `base_sha256`) on six
   edge inputs: **same=1** on all six (`out/base-vs-m2.out`).
7. Restoration: pristine M2 rerun → 15/15, mismatches 0, **exit 0**, 19.96 s
   (`out/restored-counter.out`); lane `tools/kama-probe.sh` still
   `36631d49…`, `git status --porcelain -- tools/kama-probe.sh` empty. Scratch removed.

## Findings

### Killed — 7 / 19

| mutant | expected killer | actual |
|---|---|---|
| `fp_drop_backslash` | counter D1/L1 | counter: D1, L1 (mis=2) |
| `fp_drop_quote` | counter D2/L2 | counter: D2, L2 (mis=2) |
| `jstr_split_quote_only` | counter D1/D2 | counter: D1,D2,D5,D6,L1 (mis=5) |
| `jstr_quote_unescaped` | counter D2 | counter: D2,D5,D6,L2 (mis=4) |
| `cand_failed_filter` | check router matrix | check 76/77: `router-unloaded-failed` → MODEL_OK/exit 0 |
| `nbad_le` | check router matrix | check 74/77: `router-model-missing`, `-invalid-non-gguf`, `-invalid-gguf-v1` → MODEL_OK/exit 0 |
| `persist_empty_dash_off` | counter D6 | counter: D6 (mis=1) |

`test-snapshot.sh` killed nothing on its own (30/30 on every mutant); it is insensitive to all
round-92 constructs, since its fixture serves one plain id.

### Survived — 12 (8 equivalent, 4 real coverage gaps)

**DEFECT (detector coverage; not a BASE/M2 behaviour change) — 4 survivors change observable
output on reachable input and no assigned detector notices:**

1. `persist_trail_comma_off` — served id `abc,`: M2 persists `abc`, mutant `abc,-`
   (`out/dist/persist_trail_comma_off-trail_comma_id/{m2,mut}.out`, latest.tsv served column).
   No D cell or matrix row has a trailing comma in a served id.
2. `ncand_const1` — autoload router, two unloaded candidates (one undecided `-m`-less, one with a
   missing `-m` path): M2 `MODEL_OK`/`router-unloaded-autoload` exit 0, mutant
   `MODEL_UNLOADED`/`router-model-missing` exit 2 (`out/dist/ncand_const1-ncand_one_good_one_bad/`).
   The matrix only has one-candidate cases and D9's three candidates all have `status.args=None`,
   so `nbad=0` hides the count.
3. `jstr_del_map_wrong` — registry note containing raw DEL: M2 `"notes": "NOTE-a\u007fb\u0001c"`,
   mutant `"…\u00ff…"` (`out/dist/jstr_del_map_wrong-registry_note_del/`). Controls cannot reach
   `jstr` through served ids or headers (both escape/strip them) but can through registry notes.
4. `jstr_nr_join_space` — `check --port --expect $'a\nb' --json`: M2 `expected_model_id: "a\nb"`,
   mutant `"a b"` (`out/dist/jstr_nr_join_space-expect_newline/`). No cell feeds a multi-record
   value to `jstr`.

All four are identical at BASE and M2 (`out/base-vs-m2.out`), so they are uncovered edge behaviour,
not a regression introduced by the round-92 rewrite.

**Equivalent — 8 (no reachable input distinguishes them from M2):**

- `lc_local_jstr`, `lc_awk_jstr` — every value `jstr` sees is ASCII or valid UTF-8 (json-decoded
  ids, `\uXXXX` text, `strip_ctl`'d headers, line-based registry fields); gawk emits identical
  bytes; an invalid-UTF-8 note fails both variants identically at `emit_json` (rc 1).
- `jstr_tab_map_dropped` — the BEGIN loop still maps TAB to `\u0009`, so the output is
  JSON-equal; with python present `emit_json` re-serialises anyway (`out/tab-map-equivalence.out`,
  `--expect $'a\tb'` identical, rc 2).
- `cand_quoted` — `$idx` is a python-enumerated integer field (digits only); quoting cannot change
  the word set or glob it.
- `persist_n0_off` — `served_persist` never sees an empty `$0`: `C_SERVED` defaults to `-` and `-`
  early-returns; delta call sites use `${EV_SERVED[i]:--}`.
- `persist_nr_exit_off` — the served value is single-line by construction (`served_ids` escapes LF
  as `\u000a`, `paste -sd,`), so `NR>1` is unreachable.
- `persist_tabcr_delete`, `persist_ctl_nul_only` — `served_ids`/`ROUTER_PY` convert every
  C0/DEL/C1 byte to `\uXXXX` text before persistence (verified: ids `tab\there`, `a\x01b`,
  `c\rd`, `d\x7fe` persist as `tab\u0009here,a\u0001b,c\u000dd,d\u007fe`); no raw TAB/CR/control
  byte can reach `served_persist`.

### NOTE — linearity core is well pinned

The counter kills every mutant that weakens `jstr` escaping (fast-path predicate, backslash split,
quote escape) via D1/D2/D5/D6/L1/L2, and the supplied 1.9 MB cells stayed ≤ 2.03 s at load 42;
the harm matrix kills both router-verdict mutants. The 12 survivors concentrate in defensive
branches (empty/multi-line/control-normalisation) and in detector fixtures that never present
those inputs — a coverage finding for `round92-linear-paths.py` and the verdict matrix, not a
falsification of C2's predicate.

## Deliverables

`.ufo/waves/round-92/w1/out/MT01ProbeMutants/`: `M2-probe.sh`, `BASE-probe.sh`, `mutants.py`, `distinguish.py`,
`manifest.sha256`, `base-counter.out`, `base-snapshot.out`, `base-check.out`,
`restored-counter.out`, `base-vs-m2.out`, `tab-map-equivalence.out`, `run/driver.out`,
`run/summary.json`, `run/distinguish.out`, `run/mutants/*.sh`, `run/logs/<mutant>/`, `dist/`.

VERDICT: holds — M2 passes the frozen counter (15/15) and both harm suites (30/30, 77/77), killing
7/19 mutants; 4 survivor classes are real detector-coverage gaps (BASE-identical, outside the
frozen cells), 8 are equivalent.
