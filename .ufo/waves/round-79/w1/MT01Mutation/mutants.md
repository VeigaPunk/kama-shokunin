# MT01Mutation — round-79 wave-1 mutation probes

Seat: MT01Mutation (mutation-tester, kama r79 w1). Date: 2026-11-04.
Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Base `ee53f1a25eab93a8ab55bbb877e49e2e731df535`;
freeze commit `331037039c30909aa2163b2d1de22a7964f90420`.

## Provenance and method

Mutants were applied ONLY to a scratch clone:

- `$S=/fast/scratch/hyaku/kama-r79/MT01Mutation`, `TMPDIR=$S`; clone at `$S/clone` via
  `git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin` (clone HEAD `f7442dea53bd8f474293a2252437b5d869801f49`).
- The three mutated modules landed in the lane as uncommitted working-tree bytes during the
  wave, so the clone's `tools/` was synced BYTE-EXACT from the lane working tree after a
  hash-settle poll (3 consecutive stable 30 s checks). Snapshot sha256:
  - `tools/kama-probe.sh` `0943fb461d0226e29d1b8a3b6af67740d4fe6863505ee6ed771719a30fdc3d19`
  - `tools/round79-unregistered-census.py` `25daa98937ee0b52f216a80662b32ff86457511b42370d23fcf0f536cbc4c1d3` (supersedes mid-flight bytes `a193b0bc…`; see `logs/census-midflight.diff`)
  - `tools/pre-report-gate.py` `9b2ff3b453e2aca35a9936684f126ce4a3f0eb50316e186952526ecb27e2e4d8068f6`
- L1 later committed exactly these bytes: commit `5ac1a8dd94b151548b5d5a6256938da381366e20`
  (`git log -1 -- tools/` at report time). The graded snapshot equals the committed artifact.
- Per mutant: pristine → apply diff → run the shipped detector → capture → restore pristine
  bytes → verify sha256. After mutant 5, the restored clone re-ran BOTH detectors green
  (see `logs/pristine-final-*.log`). Scratch tree deleted at yield.

## Pristine baselines (detectors must pass pre-mutation)

| Detector | Command (cwd `$S/clone`) | Result |
|---|---|---|
| C2 selftest | `TMPDIR=$S python3 tools/pre-report-gate.py --selftest` | `PRE_REPORT_SELFTEST pass=26 fail=0`, exit 0 (`logs/pristine-gate-selftest.log`) |
| C3 counter | `TMPDIR=$S python3 tools/round79-unregistered-census.py --repo .` | `UNREGISTERED_CENSUS port=59865 unregistered=1 governed=1 class_missing=0 rows=1`, exit 0 (`logs/pristine-census.log`) |

## Verdict summary: 5 built, 5 KILLED, 0 survived, 0 inconclusive

| # | Mutant | File / point | Killer (owner) | Exit | Verdict |
|---|---|---|---|---|---|
| A | `registered=yes` for every model listener | `kama-probe.sh` `classify_registration` | `round79-unregistered-census.py --repo .` | 1 | KILLED |
| B | summary keys present, `registered` column omitted | `kama-probe.sh` `cmd_listeners` | same | 1 | KILLED |
| C | registry port extraction reads column 3 not 4 | `kama-probe.sh` `read_registry_ports` | same | 1 | KILLED |
| 4 | arm 10 runs only the first instrument | `pre-report-gate.py` `_round78_instruments` | `pre-report-gate.py --selftest` | 1 | KILLED |
| 5 | arm 10 treats nonzero instrument exit as pass | `pre-report-gate.py` `_round78_instruments` | `pre-report-gate.py --selftest` | 1 | KILLED |

---

## Mutant A — probe: `registered=yes` for every model listener

Drops the registry relation: the ungoverned-model-listener branch of `classify_registration`
prints `yes` unconditionally. Diff (`logs/mutA-probe-all-yes.diff`):

```diff
@@ -748,7 +748,7 @@
       [ "$declared" = "$port" ] && { printf 'yes'; return 0; }
     done
   fi
-  printf 'no'
+  printf 'yes'
 }
```

- Killer command: `cd $S/clone && TMPDIR=$S python3 tools/round79-unregistered-census.py --repo .`
- Expected: negative leg broken — fixture classifies `yes` under the non-declaring registry,
  so `unregistered`/`governed` cannot reach 1 and the counter exits 1.
- Actual output (`logs/mutA-probe-all-yes.log`):
  - `UNREGISTERED_CENSUS port=38257 unregistered=0 governed=0 class_missing=0 rows=1`
  - `UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=8 unregistered=0 ports=-`
  - exit 1
- Verdict: **KILLED** — the frozen target line `unregistered=1 governed=1 class_missing=0`
  was not printed; the live leg exposes the dropped relation (all 8 host model listeners read
  governed, `ports=-`).
- Restoration: clone `kama-probe.sh` sha256 back to `0943fb46…` (restored-run hash printed
  in the same killer command's output).

## Mutant B — probe: summary keys present, `registered` column omitted

The per-row class is dropped from both renderings of `listeners` (TSV header, TSV row, JSON
row) while `classify_registration` still feeds `n_governed`/`n_unregistered` and the summary
keys stay. Diff (`logs/mutB-probe-column-omitted.diff`):

```diff
@@ -765,7 +765,7 @@
-  table+=("$(printf 'port\tbind\towner\tverdict\treason\tserved_model\tevidence\tregistered')")
+  table+=("$(printf 'port\tbind\towner\tverdict\treason\tserved_model\tevidence')")
@@ -782,12 +782,11 @@
-    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
-      "$port" "${scopes[i]}" "${OWNER[$port]:--}" "$C_VERDICT" "$C_REASON" "$C_SERVED" "$C_EVIDENCE" "$reg")")
-    json_rows+=("$(printf '    {"port":%s,"bind":%s,"owner":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s,"registered":%s}' \
+    table+=("$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s' \
+      "$port" "${scopes[i]}" "${OWNER[$port]:--}" "$C_VERDICT" "$C_REASON" "$C_SERVED" "$C_EVIDENCE")")
+    json_rows+=("$(printf '    {"port":%s,"bind":%s,"owner":%s,"verdict":%s,"reason":%s,"served_model":%s,"evidence":%s}' \
       "$port" "$(jstr "${scopes[i]}")" "$(jstr "${OWNER[$port]:--}")" \
-      "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")" \
-      "$(jstr "$reg")")")
+      "$(jstr "$C_VERDICT")" "$(jstr "$C_REASON")" "$(jstr "$C_SERVED")" "$(jstr "$C_EVIDENCE")")")
```

- Killer command: `cd $S/clone && TMPDIR=$S python3 tools/round79-unregistered-census.py --repo .`
- Expected: counter's `classify()` finds no per-row `registered` → `class_missing=1`, exit 1
  (the frozen "probe without the class" path).
- Actual output (`logs/mutB-probe-column-omitted.log`):
  - `UNREGISTERED_CENSUS port=51381 unregistered=0 governed=0 class_missing=1 rows=1`
  - `UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=0 unregistered=8 ports=-`
  - exit 1
- Verdict: **KILLED** — `class_missing=1` exactly as the C3 predicate requires; note the
  summary keys still moved (`unregistered=8` in the live leg), confirming the mutant is
  precisely "column omitted, summary present".
- Restoration: clone `kama-probe.sh` sha256 back to `0943fb46…`.

## Mutant C — probe: registry port extraction reads column 3 instead of 4

`read_registry_ports()` binds `declared` to the 3rd TSV column (the `resolver` spec, e.g.
`grep::`) instead of the 4th (`declared_baseurl`, the column carrying the port). Diff
(`logs/mutC-probe-col3.diff`):

```diff
@@ -724,7 +724,7 @@
-  while IFS=$'\t' read -r id cpath spec declared rest || [ -n "${id:-}" ]; do
+  while IFS=$'\t' read -r id cpath declared spec rest || [ -n "${id:-}" ]; do
```

- Killer command: `cd $S/clone && TMPDIR=$S python3 tools/round79-unregistered-census.py --repo .`
- Expected: `url_port` on `grep::` yields no digit port → `REG_PORTS` empty under BOTH
  scratch registries → the declaring registry cannot classify the fixture `yes` → `governed`
  stays 0, exit 1.
- Actual output (`logs/mutC-probe-col3.log`):
  - `UNREGISTERED_CENSUS port=48297 unregistered=0 governed=0 class_missing=0 rows=1`
  - `UNREGISTERED_CENSUS_LIVE model_endpoints=8 governed=0 unregistered=8 ports=1234,8788,8789,8790,8791,8793,8795`
  - exit 1
- Verdict: **KILLED** — the yes-leg (`class_b == "yes"`, `sum_b.governed == 1`,
  `sum_b.unregistered == 0`) can never fire, so the frozen line is unreachable.
- Restoration: clone `kama-probe.sh` sha256 back to `0943fb46…`.

## Mutant 4 — gate: arm 10 runs only the first instrument

`_round78_instruments()` iterates `ROUND78_MODULES[:1]` — only
`round78-selfrecord-round77.py` runs; `round78-append-registers.py` and
`round78-live-reconcile.py` are never executed. Diff (`logs/mut4-gate-first-only.diff`):

```diff
@@ -427,7 +427,7 @@
-    for script_name, prefix in ROUND78_MODULES:
+    for script_name, prefix in ROUND78_MODULES[:1]:
```

- Killer command: `cd $S/clone && TMPDIR=$S python3 tools/pre-report-gate.py --selftest`
- Expected: selftest case (v) `round78-instruments-red` (red stub on the SECOND module
  never runs → arm stays green), (x) `round78-instruments-green` (detail lacks
  `round78-live-reconcile.py exit=0 ok`), and (y) `round78-instruments-malformed` (foreign
  prefix on the THIRD module never runs) all fail → `fail>0`, exit 1.
- Actual output (`logs/mut4-gate-first-only.log`):
  - `FAIL round78-instruments-red :: exit=0 want 1; … detail lacks 'round78-append-registers.py exit=1 FAIL' (got 'round78-selfrecord-round77.py exit=0 ok SELFRECORD_R77_SELFTEST pass=8 fail=0')`
  - `FAIL round78-instruments-green :: … detail lacks 'round78-live-reconcile.py exit=0 ok' …`
  - `FAIL round78-instruments-malformed :: exit=0 want 1; … detail lacks 'missing valid final selftest summary' …`
  - `PRE_REPORT_SELFTEST pass=23 fail=3`
  - `PRE_REPORT_SELFTEST_FAILED round78-instruments-red,round78-instruments-green,round78-instruments-malformed`
  - exit 1
- Verdict: **KILLED** — three of the four arm-10 wiring cases caught it; the shipped
  composite selftest exercises every instrument position.
- Restoration: clone `pre-report-gate.py` sha256 back to `9b2ff3b4…`.

## Mutant 5 — gate: arm 10 treats a nonzero instrument exit as pass

The arm-10 ok-gate inverts its exit check: `ok = code != 0 and …`. Diff
(`logs/mut5-gate-nonzero-pass.diff`):

```diff
@@ -437,7 +437,7 @@
-        ok = code == 0 and error is None and re.fullmatch(
+        ok = code != 0 and error is None and re.fullmatch(
             rf"{prefix} pass=[0-9]+ fail=0", summary) is not None
```

- Killer command: `cd $S/clone && TMPDIR=$S python3 tools/pre-report-gate.py --selftest`
- Expected: green stubs (exit 0) now FAIL the arm, so every `evaluate()`-based green case
  breaks — most directly `round78-instruments-green`; red fixtures with valid summaries
  would pass. `fail>0`, exit 1.
- Actual output (`logs/mut5-gate-nonzero-pass.log`):
  - `FAIL round78-instruments-green :: exit=1 want 0; failed=1 want 0; round78-instruments ok=False want True; … (got 'round78-selfrecord-round77.py exit=0 FAIL missing valid final selftest summary: SELFRECORD_R77_SELFTEST pass=8 fail=0 | round78-append-registers.py exit=0 FAIL … | round78-live-reconcile.py exit=0 FAIL …')`
  - `PRE_REPORT_SELFTEST pass=5 fail=21`
  - `PRE_REPORT_SELFTEST_FAILED green,wave-uncommitted,stale-newest-closure,…,round78-instruments-green` (21 labels)
  - exit 1
- Verdict: **KILLED** — because `evaluate()` composes all ten arms, the inverted arm-10 gate
  poisoned every green case fleet-wide (`pass=5 fail=21`); the arm-10 green case is named
  explicitly. No survivor.
- Restoration: clone `pre-report-gate.py` sha256 back to `9b2ff3b4…`.

## Survivors

None. All five assigned mutants were killed by the shipped counter/selftest of the claim
they attack (C3 counter for A–C, gate selftest for 4–5). No additional mutants were probed.
