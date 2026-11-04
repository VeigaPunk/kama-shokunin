# Round 73 C1/C2/C3 instrument attack — RVW01Attack

Axes: calibration (primary), operability (command/receipt reproducibility).
Tested bytes (sha256, copies of the landed lane files; the lane files were never edited):

```
65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577  round73-round-scope-cases.py
888eb0755df7a5b3424900ad6dd1e862c5ea9ab90140867adb008b968503be54  round73-receipt-claim-binding.py
ec7bfd3fdf26be7338975c07443cdd15945f378d6f01774a70ef8e71934cd919  round73-province-host-drift.py
45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4  round72-round-scope.py          (sibling import)
a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd  round72-receipt-tip-binding.py  (sibling import)
```

Lane master at receipt-write time: `bc9e30599b6c6133bb094f0e7abd1a9f512778ec`
(freeze base `6e9619963fef5a3f8899324e9497416a00eab7e6` verified ancestor via
`git merge-base --is-ancestor`). The round-73 modules were uncommitted working-tree
bytes when copied; every attack ran against the copies above, never the lane files.

## Selftests (run first)

| module | command (PYTHONDONTWRITEBYTECODE=1, cwd = lane mirror) | line |
|---|---|---|
| C1 | `python3 tools/round73-round-scope-cases.py --selftest --repo <lane> --work <S>/selftest-c1` | `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0` |
| C2 | `python3 tools/round73-receipt-claim-binding.py --selftest --work <S>/selftest-c2` | `RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0` |
| C3 | `python3 tools/round73-province-host-drift.py --selftest --work <S>/selftest-c3` | `PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0` (after the `plans/round-73-claims.md` sibling was present; from a bare modules copy the predicate arm prints `plan_chars=absent` and the selftest says `pass=8 fail=1` — layout artifact, see N4) |

## Attack battery — verdict per class (26 attacks, full receipts in `RVW01Attack/receipts/`)

Every fixture built fresh in seat scratch; every git call names `-C <fixture>`; toplevel
asserted before the first commit; fixture commits use a throwaway identity. Live triple:
`Linux/x86_64/arch`. Invocation shape: `--repo <fixture>` plus `--round <N> --tip master`
(C1/C2). TOCTOU used a PATH `git` shim that renames the linked worktree exactly when the
counter calls `git worktree list` (deterministic ordering).

### C1 — round-scope v2 (10 attacks)

| attack | fixture shape | exit | observed (last line / findings) | verdict |
|---|---|---:|---|---|
| clean reference | clean clone | 0 | `ROUND_SCOPE_V2 round=73 cases=6 findings=0` | PASS (must-green) |
| TOCTOU moved worktree | linked wt renamed by shim at `worktree list` time | 1 | `worktree <wt> status=unreadable fatal: cannot change to ...` | PASS — not exit 0, no traceback; fail-closed finding (see N1) |
| bare repository | `git clone --bare` of the seed | 2 | `could-not-evaluate ... is not a git repository (fatal: this operation must be run in a work tree)` | PASS (exit 2 per exit map; not a finding, not a crash) |
| worktree path is a symlink | registered wt dir swapped for a symlink to the dirty dir | 1 | 2 findings: `LOG.md status= M`, `stray-in-wt.txt status=??` — both found through the symlink | PASS (must-kill) |
| uninitialised submodule | gitlink + `.gitmodules` committed, never checked out | 0 | `ROUND_SCOPE_V2_SKIP submodule sub reason=no-worktree`, findings=0 | PASS — outside the "initialized submodule" population, graded gracefully |
| submodule, untracked-only content | initialised sub, tracked clean, `sub/leak.txt` untracked | 1 | `submodule sub leak.txt status=??` + `submodule sub parent-record=M sub status= M` | PASS (must-kill — the A7-shaped hole is closed) |
| ignored file in `round-99` (future round) | `.ufo/waves/round-99/ghost.log` ignored, `--round 73` | 1 | `ignored-older-label .ufo/waves/round-99/ghost.log` | PASS (must-kill) |
| older-round ignored `__pycache__` | `.ufo/waves/round-50/__pycache__/mod.pyc` ignored | 0 | findings=0 | PASS (must stay green — `M >= N` bound honored) |
| linked worktree, ignored-only dirt | wt with only `scratch.log` (`*.log` ignored) | 0 | findings=0 | PASS (ignored content is not uncommitted content) |
| stale worktree entry | wt dir deleted without `worktree remove` (prunable) | 1 | `worktree <wt> status=unreadable` | PASS — not exit 0, no traceback (see N1) |

### C2 — receipt-claim binding (9 attacks)

| attack | record shape | exit | observed | verdict |
|---|---|---:|---|---|
| positive control: bound receipt, no tip token | header names an ancestor; citing line has no tip token | 0 | `cited=1 bound=1 ... claims=0 unbound_claims=0` | PASS (must-green) |
| B6 repro (frozen kill) | receipt at older X, record-only delta, "the gate ran at the report tip" | 1 | `RECEIPT_CLAIM_FINDING stale-claim .ufo/waves/round-72/measured/a.out :: 9: ...`, `claims=1 unbound_claims=1` | PASS (must-kill; base tool still accepts the same fixture) |
| tip claim, brace citation | `{measured/before/old.out,measured/after/new.out}` + "both at the tip", old header ≠ tip | 1 | two stale-claim findings (one per expansion), `cited=2 bound=2`, exit 1 | PASS (must-kill) |
| tip claim, glob citation | `measured/after/*.out` + "both at the tip", one expansion header ≠ tip | 1 | stale-claim, `cited=2 bound=2`, exit 1 | PASS (must-kill) |
| tip claim split across two lines | line 1 cites receipt + "ran at the", line 2 "report tip" | 0 | `claims=0 unbound_claims=0` | PASS — the predicate scopes claims to one line; no over-reach beyond the freeze |
| tip token, no citation | "the counter runs at the tip of master" (no backticked receipt) | 0 | `claims=0` | PASS (must NOT be a finding) |
| receipt header on line 6 | 5 preamble lines, then `# rev=<X>`; claim "at the tip" | 1 | base `unbound=1` (5-line window) + stale-claim | PASS (never exit 0) |
| two conflicting headers | `# tip=<X>` + `# rev=<tip2>` in window | 1 | base `unbound=1` (conflict) + stale-claim | PASS (never exit 0) |
| header names a descendant-of-tip shape | header names a sibling-branch commit, not an ancestor of the tip | 1 | base `shifted=1` ("not an ancestor") + stale-claim | PASS (never exit 0; see N2 for the literal-descendant form) |

### C3 — province host drift (7 attacks)

| attack | PROVINCE.md shape | exit | observed | verdict |
|---|---|---:|---|---|
| clean control | newest block records the live triple | 0 | `blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0` | PASS (must-green) |
| no block | no host-identity paragraph | 1 | `PROVINCE_HOST_DRIFT_FINDING no-block ...`, `blocks=0` | PASS (must-kill) |
| stale triple (frozen kill repro) | Windows/AMD64/win | 1 | `stale-host ... recorded=Windows/AMD64/win live=Linux/x86_64/arch` | PASS |
| two blocks, newest unparsable | older block matches live; newest block has no triple tokens | 1 | `stale-host line=5 round=73: triple not parseable`, `blocks=2`, `recorded=-/-/-` | PASS — newest block graded, not exit 0, no traceback |
| triple in different order | `ID` first, then `uname -m`, then `uname -s` | 0 | `blocks=1 recorded=Linux/x86_64/arch`, exit 0 | PASS — grammar fixes tokens, not order; no over-strictness |
| CRLF file | block with `\r\n` endings, live triple | 0 | `blocks=1`, exit 0 | PASS (CRLF normalized) |
| case-differing triple | `LINUX/X86_64/ARCH` vs live `Linux/x86_64/arch` | 1 | `stale-host ... recorded=LINUX/X86_64/ARCH live=Linux/x86_64/arch` | PASS — strict equality per the frozen "equals" sentence |

## Frozen-kill cross-check (read-only control rerun)

`python3 .ufo/waves/round-73/controls/score-survivors.py` (cwd = lane) →
`SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green`,
`SURVIVORS c2 base_green=1 v2_killed=1 v2=present`,
`SURVIVORS c3 base_green=1 v2_killed=1 v2=present`, `# exit=0`.
The three r72 survivors (A5 linked worktree, A6 valid older-round label, A7
`submodule.<name>.ignore=all`) are killed by the v2 counters naming their new cases
(`worktree` / `ignored-older-label` / `submodule`), `c1_clean` stays green, the B6
fixture is killed by the claim pass, and the stale-triple fixture by `stale-host`.
**Frozen-kill violations: none. Calibration survivors (vacuous greens, missed kills):
none of the 26 attacks.**

## Observations (none is a survivor; severity: notes)

- **N1 — unreadable worktree maps to a finding, not exit 2.** The freeze's exit map puts
  "a git command failure" under exit 2, but the C1 module grades a moved/deleted linked
  worktree as `worktree <path> status=unreadable` (exit 1). Both readings are red for a
  broken state, so the direction is fail-closed and no vacuous green exists; flagged only
  because the exit code diverges from the map's letter (asymmetry vs the primary `stray`
  case, which raises ScopeError → 2).
- **N2 — a committed "at the tip" claim can never bind.** A receipt header equal to the
  commit that contains it is a git hash fixpoint (the module's own D2 note); therefore any
  real record line that both cites a receipt and carries a tip token is a permanent
  `stale-claim`, and the only exit-0 path with `claims>0` is the selftest's injectable
  blob reader. Consequence for the round: the round's own record must cite receipts with
  explicit revisions instead of tip claims — which the frozen non-goal sentence already
  sanctions. Literal descendant-of-tip headers are likewise unconstructible on committed
  bytes; my fixture realizes the nearest realizable shape (sibling-branch commit).
- **N3 — brace citations with fully-qualified members get double-prefixed.**
  `` `{.ufo/waves/round-72/a.out,.ufo/waves/round-72/b.out}` `` is treated as
  section-relative before brace expansion, yielding phantom paths
  (`.ufo/waves/round-72/.ufo/waves/...`) graded `stale` at base (observed first run:
  `cited=2 bound=0 stale=2`). The canonical brace shape (`{before,after}/x.out`-style
  relative members) expands correctly and kills the claim. Calibration surface is narrow
  (noncanonical citation form) and errs toward false-positive findings, not green.
- **N4 — selftest layout expectations.** C1's selftest crashes with an uncaught inherited
  `ScopeError` traceback when run from a non-git cwd (needs `--repo <git repo>`); C3's
  predicate arm fails (`plan_chars=absent`) when `plans/round-73-claims.md` is not the
  sibling of the module copy. Both hold in the lane layout; disclosed for reproducibility.
- **N5 — my own builder defect, fixed and rerun.** The first C3 battery pass showed
  `blocks=0` because my template emitted literal `{n}`/`{date}` in block headers (Python
  double-brace escaping), so the fixtures carried unparsable headers; after the fix all
  seven C3 attacks were rerun and are reported above. Likewise the brace fixture was
  rebuilt in canonical shape after N3 was diagnosed. The receipts carry the corrected runs.

## Commands (all PYTHONDONTWRITEBYTECODE=1)

1. Fixture build: `python3 attack_builder.py` → 26 fixtures + `attack-meta.json`
   (`{"live": {"id": "arch", "m": "x86_64", "s": "Linux"}, "fixtures": 26}`).
2. Byte copies + digests: `sha256sum round7*.py > SHA256SUMS` (see header block).
3. Selftests: the three `--selftest` invocations above (receipts:
   `receipts/selftests-and-control.out`).
4. Battery: `python3 run_attacks.py --modules <S>/lanemirror/tools --meta
   <S>/work/attack-meta.json --receipts <W>/RVW01Attack/receipts` → 26 `ATTACK ...` lines,
   `REV_AT_WRITE bc9e30599b6c6133bb094f0e7abd1a9f512778ec`, runner exit 0.
5. Control rerun: `python3 .ufo/waves/round-73/controls/score-survivors.py` → `# exit=0`.
6. Scratch deleted after receipt preservation (`rm -rf` of the seat scratch root).

## Files written

- `.ufo/waves/round-73/w1/RVW01Attack.md` (this report; copy at
  `.ufo/waves/round-73/w1/RVW01Attack/RVW01Attack.md`)
- `.ufo/waves/round-73/w1/RVW01Attack/receipts/<attack-id>.out` — 26 per-attack receipts,
  each starting `# rev=bc9e3059... seat=RVW01Attack ... tested_sha256=<module sha256>`
- `.ufo/waves/round-73/w1/RVW01Attack/receipts/selftests-and-control.out`
- `.ufo/waves/round-73/w1/RVW01Attack/receipts/{attack-meta.json,attack-results.json,SHA256SUMS}`

No lane file was edited; no git mutation outside scratch fixtures; no `__pycache__` under
the wave dir; no tool installations.
