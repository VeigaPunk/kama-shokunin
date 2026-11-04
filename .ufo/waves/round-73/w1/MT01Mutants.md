# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec

## kama r73 w1 · MT01Mutants — mutation test of the three modules and the gate wiring

Leaf mutation-tester seat. Scope: apply believable defects to the four round-73 artifacts, run each
artifact's own bounded detector on pristine and mutated bytes, and record killed / survived with the
killing check by name. No lane byte was modified: every mutant lived in a throwaway mirror lane under
`/fast/scratch/hyaku/kama-r73/MT01Mutants/lanes/`, deleted before yield.

**Result: 44 mutants applied — 34 killed, 10 survived.** The 10 survivors are coverage findings about
the detectors, not failures of C1/C2/C3: each one was confirmed with a hand-built distinguishing
fixture that the mutant answers differently (`probes-survivors.out`).

### 1. Tested bytes

Stamped with the revision read at write time: `git -C L rev-parse master` =
`bc9e30599b6c6133bb094f0e7abd1a9f512778ec`.

| artifact | sha256 |
|---|---|
| `tools/round73-round-scope-cases.py` | `65d9a753067e1d2e72eb58e082e317c8aa9242d2495e65f3b4123c837527c577` |
| `tools/round73-receipt-claim-binding.py` | `888eb0755df7a5b3424900ad6dd1e862c5ea9ab90140867adb008b968503be54` |
| `tools/round73-province-host-drift.py` | `ec7bfd3fdf26be7338975c07443cdd15945f378d6f01774a70ef8e71934cd919` |
| `tools/pre-report-gate.py` | `59842d4604a2d0b85db428b7b79a6758ca0dd1ffdbdc651a31a53bfbd94893e9` |

Each mutant is a one-line (or few-line) semantic replacement in a copy of exactly these bytes; the
`source.count(old) == 1` assertion in the driver refuses a mutant whose anchor is not unique
(the one such rejection, `c3-m10` on its 2-occurrence anchor, was rewritten against a unique context
and re-run).

Mirror-lane layout (required for two reasons: `round73-round-scope-cases.py` imports its inherited
graders from `tools/round72-round-scope.py` beside it, and `round73-province-host-drift.py` derives
`LANE` from `Path(__file__).resolve().parent.parent` and reads `plans/round-73-claims.md` there):

```
lanes/<mutant-id>/tools/<module>.py      mutated copy (+ its sibling base tool)
lanes/<mutant-id>/plans/round-73-claims.md   byte copy of the frozen plan
```

### 2. Baselines (pristine bytes, own fixtures)

`python3 tools/<module> --selftest --work <fresh>` with `PYTHONDONTWRITEBYTECODE=1`:

| artifact | selftest | exit |
|---|---|---|
| `round73-round-scope-cases.py --selftest --repo L` | `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0` | 0 |
| `round73-receipt-claim-binding.py --selftest` | `RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0` | 0 |
| `round73-province-host-drift.py --selftest` | `PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0` | 0 |
| `pre-report-gate.py --selftest` | `PRE_REPORT_SELFTEST pass=12 fail=0` | 0 |

A mutation verdict is only meaningful against a green baseline; all four are green at the tested
bytes, so every red row below is caused by the mutation.

Live lane (mid-wave, `lane-live.out`): `PROVINCE_HOST_DRIFT blocks=1
recorded=Linux/x86_64/arch live=Linux/x86_64/arch stale=0` exit 0;
`ROUND_SCOPE_V2 round=73 cases=6 findings=144` exit 1 (seats' uncommitted wave files — expected
before the report-tip commit); `round73-receipt-claim-binding.py --round 73` exit 2,
`SCORECARD.md at master carries no '## Round 73' section` (the r73 record does not exist yet, so C2
cannot be scored at this revision — the module's fail-closed path, not a defect).

### 3. Pre-freeze control reproduced

`python3 .ufo/waves/round-73/controls/score-survivors.py` (receipt `control-repro.out`) reproduces
the frozen control exactly, and the v2 counters kill the same fixtures:

```
BASE_C1 c1_a5     exit=0 GREEN  ROUND_SCOPE round=73 cases=3 findings=0
BASE_C1 c1_a6e    exit=0 GREEN  ROUND_SCOPE round=71 cases=3 findings=0
BASE_C1 c1_a7sub2 exit=0 GREEN  ROUND_SCOPE round=73 cases=3 findings=0
SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green
BASE_C2 c2_b6     exit=0 GREEN  RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0
SURVIVORS c2 base_green=1 v2_killed=1 v2=present
BASE_C3 c3_stale  exit=0 GREEN  block-exists-shortcut blocks=1
SURVIVORS c3 base_green=1 v2_killed=1 v2=present
```

Per-fixture invocations of the v2 counters over the same fixture dirs (also in `control-repro.out`):
`c1_a5 → 1 worktree`, `c1_a6e → 1 ignored-older-label`, `c1_a7sub2 → 3 submodule`,
`c1_clean → 0`; `c2_b6 → exit 1, RECEIPT_CLAIM_FINDING stale-claim, claims=1 unbound_claims=1`;
`c3_stale → exit 1, PROVINCE_HOST_DRIFT_FINDING stale-host`.

### 4. Matrix

| module | applied | killed | survived |
|---|---|---|---|
| C1 `round73-round-scope-cases.py` | 12 | 11 | 1 |
| C2 `round73-receipt-claim-binding.py` | 11 | 7 | 4 |
| C3 `round73-province-host-drift.py` | 13 | 8 | 5 |
| gate `pre-report-gate.py` (arm 6 wiring) | 8 | 8 | 0 |
| **total** | **44** | **34** | **10** |

Full ledger with the mutation text and the killing check for every row: `mutants.tsv`
(44 data rows). Raw matrices: `mutants-c1.out`, `mutants-c2.out`, `mutants-c3.out`,
`mutants-gate.out`. Per-mutant selftest output was captured in the scratch logs and is summarised
by the matrix rows.

Notable kills (one per detector mechanism):

* **C1** — dropping `worktree` from `CASE_ORDER` is caught by the `want_line` `cases=6` assertion and
  by a `ValueError` in `findings.sort` on any worktree finding; dropping the parent
  `--ignore-submodules=none` probe is caught only by `submodule-ignore-all`; inverting the
  `M >= N` bound is caught by `older-label-green` (an old-round `__pycache__` leftover must stay
  green) as well as `older-label-red`.
* **C2** — dropping the `"at the tip"` token is caught only by `lesson-tip-claim` (the B6 arm text is
  `"at the report tip"`, which the other token still matches); removing the tip-token guard is
  caught by `clean-no-tip-claim` and `measured-at-rev-no-tip-token`; ignoring the base exit is caught
  by `base-red-echo`.
* **C3** — first-block-instead-of-last is caught by both `newest-matches` and `newest-differs`;
  `stale=0 whenever a block exists` is caught by three arms; dropping the finding detail's
  `line=` pointer is caught by `unparseable-triple`.
* **gate** — pointing arm 6 back at `round72-round-scope.py` fails 11 of 12 arms (the stub is written
  under the v2 name and the real module is copied only later), so the wiring mutation is detectable;
  reverting `VERDICT_RE` to `"ROUND_SCOPE "` is caught by `verdict-selector`, the only arm that
  distinguishes the chosen detail line.

### 5. Survivors — each confirmed with a distinguishing input

A survivor is not "the claim is wrong"; it is an input class the artifact's own fixtures do not
exercise. Each was re-run against a fixture that isolates the mutated behaviour, original vs mutant
(`probes-survivors.out`).

| mutant | mutated behaviour | observed difference (original → mutant) |
|---|---|---|
| `c1-m10` | linked-worktree status without `-uall` | nested untracked dir: `worktree … sub/dir/leak.txt status=??` → `worktree … sub/ status=??`. Detection survives, **path precision is lost**; no arm places an untracked file below the worktree root. |
| `c2-m2` | absent receipt header treated as bound | headerless cited receipt on a tip-claim line: `unbound_claims=1` + `RECEIPT_CLAIM_FINDING stale-claim` → `unbound_claims=0`, **no claim finding** (exit still 1 via the base tool). |
| `c2-m7` | `line_no` without the scorecard section offset | finding names `7:` → `5:`. Every finding arm is either in the lesson file (offset 0) or asserts no line number. |
| `c2-m8` | case-sensitive token scan | `— Read At The Report Tip.` → original exit **1** (claims=1 unbound_claims=1), mutant exit **0** (claims=0). A real false-green. |
| `c2-m10` | no per-line citation dedupe | one line citing the same receipt twice prints **two** identical `stale-claim` lines instead of one. |
| `c3-m6` | compare only `uname -s` | recorded `Linux/x86_64/ubuntu` on this host: original exit 1 (stale-host), mutant exit 0 — and the mutant's summary still prints `stale=1`, i.e. it introduces an internal exit/summary disagreement. |
| `c3-m7` | live ID hard-coded `"unknown"` | correct live triple `Linux/x86_64/arch`: original exit 0 → mutant exit 1. `live-match` cannot see this because it builds its fixture from the module's own `live_triple()`. |
| `c3-m8` | newest block by round number instead of file order | `Round-74` (Windows) appended **above** `Round-73` (live): original exit 0 (file order wins), mutant exit 1 (round number wins). No arm has out-of-order blocks. |
| `c3-m9` | empty `no-block` finding detail | finding becomes `PROVINCE_HOST_DRIFT_FINDING no-block ` with nothing after the token; the arm asserts only the token, never a detail. |
| `c3-m11` | JSON payload `blocks=1` whenever any block exists | `--json` with two blocks: `"blocks": 2` → `"blocks": 1`. No selftest arm exercises `--json`. |

### 6. Coverage findings (for the module owners; no contract change proposed)

Ordered by consequence, strongest first:

1. **`c3-m7` / self-referential `live-match`** — the only arm that proves "the recorded triple is the
   live triple" constructs its expected value by calling the very function under test
   (`live = live_triple()`), so any consistent fault in `live_triple()`/`os_release_id()` passes.
   The live-lane run does discriminate in practice, but the selftest cannot. A fixture with a
   hard-coded, independently obtained triple (e.g. `Linux/x86_64/arch` written literally, or a
   `--os-release`/probe injection point) would close this.
2. **`c2-m8` / token case-folding** — the only false-green class found: a mixed-case claim
   (`Read At The Report Tip`) passes the claim pass. One arm with a capitalised token on a
   non-tip receipt closes it.
3. **`c2-m2` / headerless claimed receipt** — the predicate explicitly counts a missing header as a
   finding, but no arm isolates a headerless cited receipt (the `both` arm pairs it with a
   tip-mismatched receipt, so `unbound_claims` stays 1 either way).
4. **`c1-m10` / nested untracked path in a linked worktree** — no arm places an untracked file below
   the worktree root; the case still fires but names the directory instead of the offending path,
   which weakens the finding's diagnosability.
5. **`c3-m11` / `--json` payload** — `blocks` (and the rest of the JSON document) has no arm; the
   control script and any consumer read the human line, so this is low-consequence today.
6. **`c2-m7`, `c2-m10`, `c3-m8`, `c3-m9`** — line-number precision, duplicate emission, out-of-order
   block append, and empty detail. Each is one fixture away from being caught.

### 7. Observations (no freeze disagreement)

* The freeze's kill rules and the counters' behaviour agree at every point I exercised. I found no
  rule in the claim that the implemented module violates.
* **C1 double-reports the current round's ignored file.** With an ignored path under
  `.ufo/waves/round-<N>/`, the selftest prints both `ignored` and `ignored-older-label` for the same
  file (`ignored-in-wave`: `findings=2`). This follows from the frozen case population (`ignored`
  covers `round-<N>`, `ignored-older-label` covers `M >= N`), so it is a property of the claim, not
  a deviation — but a consumer that sums findings over one path will see it twice.
* **C2's `cli-misuse` arm prints `expect=0 got=0`** because the arm folds two sub-invocations
  (`rc_missing == 2 and rc_zero == 2`) into one synthetic `0`; the real exit-2 behaviour is asserted
  by that arm's `must_out=["missing=2 zero=2"]`, so this is a reporting artefact of the arm harness,
  not a weakened check.
* **Byte flux during the wave.** At 23:38 the gate file was mid-rewrite: a run against the older
  snapshot failed `round-scope-red` with
  `detail lacks 'ROUND_SCOPE round=70 cases=3 findings=1' (got 'ROUND_SCOPE_V2 round=70 cases=6 findings=1 | …')`,
  while the stable bytes hash-identical to the table above pass 12/12. Any seat that ran the gate
  selftest in that window would have recorded a red that no longer exists. Report the sha256 with any
  gate verdict.
* A C3 mutant copy placed outside a lane-shaped directory cannot pass the `predicate` arm
  (`plan_chars=absent`) because `LANE` is derived from the tool's path — this is why all mutants ran
  in `<scratch>/lanes/<id>/tools/` with `plans/round-73-claims.md` beside it, and why the pristine
  baseline was re-run in the same shape before scoring any mutant.

### 8. Commands run (exact)

All with `PYTHONDONTWRITEBYTECODE=1`, from the fleet root or the scratch dir, never with a relative
write outside the scratch/mirror dirs.

```
sha256sum L/tools/pre-report-gate.py L/tools/round73-*.py
python3 L/tools/round73-round-scope-cases.py --selftest --work $S/w-c1 --repo L      # 26/0
python3 L/tools/round73-receipt-claim-binding.py --selftest --work $S/w-c2           # 14/0
python3 L/tools/round73-province-host-drift.py --selftest --work $S/w-c3             # 9/0
python3 L/tools/pre-report-gate.py --selftest --work $S/w-gate                       # 12/0
python3 L/.ufo/waves/round-73/controls/score-survivors.py                            # exit 0, 3/1/1 killed
python3 L/tools/round73-round-scope-cases.py --repo <c1_a5|c1_a6e|c1_a7sub2|c1_clean> --tip master
python3 L/tools/round73-receipt-claim-binding.py --repo <c2_b6> --round 72 --tip master
python3 L/tools/round73-province-host-drift.py --repo <c3_stale>
python3 L/tools/round73-round-scope-cases.py --repo L --round 73 --tip master        # exit 1, 144 findings (mid-wave)
python3 L/tools/round73-receipt-claim-binding.py --repo L --round 73 --tip master    # exit 2, no '## Round 73' section
python3 L/tools/round73-province-host-drift.py --repo L                              # exit 0
python3 $S/c1_run.py | $S/c2_run.py | $S/c3_run.py | $S/c3_extra.py | $S/gate_run.py  # matrices
python3 $S/c1_probe.py ; python3 $S/c2_probe.py ; python3 $S/c3_probe.py              # survivor probes
```

Each mutant is `cp module → lanes/<id>/tools/`, one string replacement, then the module's
`--selftest` in that mirror lane; the driver refuses a non-unique anchor and records the failing arm
names from the `[FAIL]` / `FAIL label ::` / `_ARM … FAIL` lines.

### 9. Files written (exact)

Under `W = L/.ufo/waves/round-73/w1/MT01Mutants/`:

* `MT01Mutants.md` — this report
* `mutants.tsv` — 44 rows: `module, mutation, verdict, killing-check`
* `selftests.out` — the four selftest runs at the tested bytes
* `control-repro.out` — `score-survivors.py` plus the eight per-fixture counter invocations
* `mutants-c1.out`, `mutants-c2.out`, `mutants-c3.out`, `mutants-gate.out` — raw matrices
* `probes-survivors.out` — the ten survivor probes, original vs mutant
* `lane-live.out` — live lane C1/C2/C3 runs at the stamped revision
* `tool-bytes.out` — sha256 of the four mutated artifacts

Scratch (deleted before yield): `/fast/scratch/hyaku/kama-r73/MT01Mutants/` (mirror lanes, probe
fixtures, selftest work dirs, driver scripts, logs). No `__pycache__` was created anywhere — every
python invocation carried `PYTHONDONTWRITEBYTECODE=1` and every subprocess inherits it.

No tool was installed or upgraded; nothing outside the paths above was written.
