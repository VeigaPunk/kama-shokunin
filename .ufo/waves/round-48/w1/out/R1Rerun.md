# R1Rerun — independent re-measurement of C1 (round 48, lane kama)

**Verdict: C1 independently reproduced.** Counter bytes match the frozen preregistration sha256; two runs at the build tip `380bcdff9c8af06997c482f6eb03db926a794a2b` both exit 0 with `met=True` and byte-identical receipts matching the frozen target; one run at the round-48 base `33e005827742b29772b153cda036ec9f27f653be` exits 1 with `met=False`, matching the frozen before-control. No run-to-run difference beyond wall time. No new defects.

## 1. Clone and byte verification

- Full clone (not `--shared`): `git clone /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r48/R1Rerun/lane` → ok.
- Clone HEAD is `b85783e889c261ff870da65d091ff1014ffe7c10` (the lane's default branch has advanced past the build commit). Ancestry verified: `git merge-base --is-ancestor` shows `33e0058…` → `380bcdf…` → `b85783e8…`. Both measured commits are present in the full clone; the measurement is pinned by explicit `--tip`, so the advanced HEAD does not affect it.
- Counter bytes vs frozen preregistration (`.ufo/waves/round-48/preregistration.json`, claim C1 `counter_sha256: 92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7`):
  - working tree: `sha256sum $S/lane/tools/round48-append-audit-v3-check.py` → `92b0f9f1027b8214c7a702d928f89e5a6d9fb814fc565c234f6deee3f2d82ac7` — **match**
  - measured-tip blob: `git cat-file blob 380bcdf…:tools/round48-append-audit-v3-check.py | sha256sum` → same — **match**
  - clone-HEAD blob: same — **match** (counter unchanged since the build tip)
- The executed script is therefore byte-identical to the frozen counter.

## 2. Run 1 — tip `380bcdff9c8af06997c482f6eb03db926a794a2b`

Command: `python3 $S/lane/tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S --out …/out/R1Rerun/c1-build.out`

Exit code: **0**. Wall 3.92 s. stderr empty. Receipt (`c1-build.out`, snapshot `c1-build.out.run1`), every line:

```
selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5 lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True
tip=380bcdff9c8af06997c482f6eb03db926a794a2b
```

Matches the frozen target `selftest=1 contract=1 lane=1 fixture=1 stable=1 met=True (lane_failures=0)` and the L1 pre-wave dry run (`lane_failures=0 ungraded_lines=89 met=True`).

## 3. Run 2 — same tip, same command

Exit code: **0**. Wall 4.57 s. stderr empty. Receipt snapshot `c1-build.out.run2`.

Run-to-run difference: `diff` of stdout run1 vs run2 → identical; `diff` of receipts run1 vs run2 → identical. Only wall time differs (3.92 s vs 4.57 s). Final `c1-build.out` (the named deliverable) is the run-2 receipt, byte-identical to run 1.

## 4. Run 3 — base `33e005827742b29772b153cda036ec9f27f653be`

Same command with `--tip 33e0058…`, `--out c1-base.out`. Exit code: **1**. Wall 0.97 s. stderr empty. Receipt (`c1-base.out`), every line:

```
selftest=0 contract=0 lane=0 fixture=0 stable=0 rows=0 files=0 lane_events=0 lane_failures=NA ungraded_lines=0 fixture_fail=11 met=False
tip=33e005827742b29772b153cda036ec9f27f653be
detail: selftest: exit 0 line AOA_SELFTEST pass=19 fail=0
detail: contract: header is not the v3 header (or CR present)
detail: fixture threshold: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture exempt-rewritten: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 0
detail: fixture exempt-gutted: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture dated-rewritten: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture only-errata: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture clamp: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture merge-first-parent: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture regressed: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture dashdash-crlf: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture bad-declarations: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 1
detail: fixture clean: no v3 JSON (exit 2; could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>note); exit 2 want 0
```

Matches the frozen before-control `selftest=0 contract=0 lane=0 fixture=0 stable=0 met=False` (`.ufo/waves/round-48/controls/base.c1.out`): `diff c1-base.out controls/base.c1.out` shows only the control's trailing `exit=1` line (the control records the exit code; the counter's own receipt does not) — content otherwise identical. The base failures are the expected honest before-state: at the base the lane tool is v2 (4-cell contract header), so the v3 contract leg fails and all 11 fixtures report `could-not-evaluate`. The `detail: selftest: … pass=19 fail=0` line is informational (the v2 tool's own selftest passes; the leg still requires the v3 selftest marker) and is consistent with the frozen `selftest=0`.

## 5. Findings

None new. No defect, no shortcut, no run-to-run instability observed in C1. Known integration items (gate-registry unregistered counters, spot-check count 33 vs 34, hexrun-census d0012618) are out of my scope and not re-reported. Tooling: nothing installed or upgraded (no pacman use, per the host guard).

## 6. Deliverables

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/R1Rerun/`:
- `c1-build.out` — final tip receipt (run 2)
- `c1-build.out.run1`, `c1-build.out.run2` — per-run receipt snapshots
- `c1-build.run1.stdout`, `c1-build.run1.stderr`, `c1-build.run2.stdout`, `c1-build.run2.stderr` — per-run streams (stderr empty in both)
- `c1-base.out`, `c1-base.stdout`, `c1-base.stderr` — base run
- `R1Rerun.md` — this report

Scratch `/fast/scratch/hyaku/kama-r48/R1Rerun` (incl. the clone) removed after the report was written.
