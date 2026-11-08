# SN01StepFlips — final output (verbatim from w1-results.json by the L1)

Seat `SN01StepFlips`, agent `sentinel`, wave kama r97 w1. This file is the seat's final
output string copied verbatim from `.ufo/waves/round-97/w1-results.json`; the L1 added only
this header. The seat's own receipts sit beside it.

```
{
  "seat": "SN01StepFlips",
  "lane": "kama-shokunin",
  "wave": "round-97 / w1",
  "report": "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-97/w1/SN01StepFlips.md",
  "out_dir": "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-97/w1/out/SN01StepFlips/",
  "scratch_removed": "/fast/scratch/hyaku/kama-r97/SN01StepFlips (deleted; 2.4G freed)",
  "task": "Measure the real probe's step boundary without the counters; verify the -/invalid split; check whether the - fixtures decide by size guard or MAX_TENSORS.",
  "method": {
    "probe_bytes": "git show HEAD:tools/kama-probe.sh (never a working-tree copy); HEAD moved 9e605d41 -> e057166e under this seat, probe bytes byte-identical (sha256 0897ebff...)",
    "paths": [
      "end-to-end: bash kama-probe.sh check --port P --expect good --json against a lane-style stub router (same Stub/router_body/Runner.check pattern as tools/round97-router-budget.py)",
      "parser-level: ROUTER_PY extracted from probe bytes and run standalone with scratch-only instrumentation naming the deciding guard",
      "mutant: same paths re-run against byte-patched probes"
    ],
    "fixture_families": "famA = counter-identical layout (no data section; invalid via start+off+nbytes>size); famB = real data section with tensor 0's offset broken by 64 (invalid via off!=expect; size guard cannot fire); famC = well-formed (correct offsets + real data)",
    "fixture_byte_identity": "counter's own rb.gguf(900000,1,False) / rb.gguf(700000,1,False,nd=4) / rb.gguf(833333,1,False) are byte-identical to my independently written famA files (sha256 0e0a51cf..., 868d489b..., 90d60f50...)"
  },
  "fixture_table": [
    {
      "T": 833332,
      "nd": 1,
      "steps": 4999996,
      "verdict": "MODEL_UNLOADED/router-model-invalid",
      "reason": "offset/data check (decided)",
      "wall_s": 2.76,
      "match": true
    },
    {
      "T": 833332,
      "nd": 1,
      "fam": "B",
      "steps": 4999996,
      "verdict": "MODEL_UNLOADED/router-model-invalid",
      "reason": "offset chain off!=expect (decided)",
      "wall_s": 2.46,
      "match": true
    },
    {
      "T": 833333,
      "nd": 1,
      "steps": 5000002,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget (steps:5000001)",
      "wall_s": 2.71,
      "match": true
    },
    {
      "T": 833333,
      "nd": 1,
      "fam": "B",
      "steps": 5000002,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.63,
      "match": true
    },
    {
      "T": 900000,
      "nd": 1,
      "steps": 5400004,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.59,
      "match": true
    },
    {
      "T": 900000,
      "nd": 1,
      "fam": "B",
      "steps": 5400004,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.4,
      "match": true
    },
    {
      "T": 700000,
      "nd": 4,
      "steps": 6300004,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.44,
      "match": true
    },
    {
      "T": 700000,
      "nd": 4,
      "fam": "B",
      "steps": 6300004,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.26,
      "match": true
    },
    {
      "T": 555555,
      "nd": 4,
      "steps": 4999999,
      "verdict": "MODEL_UNLOADED/router-model-invalid",
      "reason": "offset/data check (decided)",
      "wall_s": 2.25,
      "match": true
    },
    {
      "T": 555555,
      "nd": 4,
      "fam": "B",
      "steps": 4999999,
      "verdict": "MODEL_UNLOADED/router-model-invalid",
      "reason": "offset chain (decided)",
      "wall_s": 2.33,
      "match": true
    },
    {
      "T": 555556,
      "nd": 4,
      "steps": 5000008,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.21,
      "match": true
    },
    {
      "T": 555556,
      "nd": 4,
      "fam": "B",
      "steps": 5000008,
      "verdict": "MODEL_OK/router-unloaded-autoload",
      "reason": "step budget",
      "wall_s": 2.36,
      "match": true
    }
  ],
  "step_boundary_verdict": {
    "split_matches_claim": "YES - 12/12 across two byte-layout-independent families",
    "formula_confirmed": "the probe's own step counter reads ok:steps=4999996 (833,332@nd1) and ok:steps=4999999 (555,555@nd4) - exact match to the table's stated numbers",
    "contrast_row": "700,000 at nd=1/2/3/4 -> invalid/invalid/-/- ; SKILL.md's 'decides invalid at nd<=2 and stays - at nd>=3' confirmed",
    "size_guard": "does NOT decide any - fixture (size_guard=False for all six shapes); reachable but not firing - truncating the same declared count below n_tensors*24 flips it to invalid-SIZE-GUARD",
    "max_tensors": "does NOT decide any - fixture (all T below 1,000,000); at T=1,000,001 the probe returns -MAX_TENSORS(n=1000001) in 0.00s - a different, much cheaper '-'",
    "which_guard_fired": "the step budget decides all four - cases, and it fires first"
  },
  "findings": [
    {
      "id": "F1",
      "severity": "HIGH",
      "axis": "depth",
      "title": "C3's table states 'invalid' where the probe says 'ok'; the counter cannot express the truth",
      "evidence": [
        "tools/kama-probe.sh:768 has return \"ok\" - gguf_state has four outcomes (missing/-/invalid/ok), but tools/round97-depth-boundary-audit.py:39-41 ROW regex accepts only (invalid|-); 'ok' is not in its vocabulary",
        "well-formed file T=833332 nd=1 -> probe ok:steps=4999996, router MODEL_OK/router-unloaded-autoload; table says invalid",
        "well-formed file T=555555 nd=4 -> probe ok:steps=4999999, router MODEL_OK/router-unloaded-autoload; table says invalid",
        "the counter's OWN oracle has the same wrong model: fixture_class(WELL-FORMED T=833332 nd=1) = 'invalid' where the probe says 'ok'",
        "mutation A (table verdict -> 'ok', the probe's truth) -> DEPTH_BOUNDARY97 rows=4 checks=8 mismatches=2 met=False - the counter REJECTS the truth"
      ],
      "note": "Same defect class as round 96, one level down: round-96's C3 counter required the false string '6 steps per tensor header'; round-97's requires the false verdict token 'invalid'. SKILL.md:2449-2450 states the same over-generalisation ('decides it (invalid) when that sum fits').",
      "remediation": "widen ROW's verdict vocabulary and reword the rows (e.g. 'decided'), or qualify the rows by file class; correct fixture_class() the same way. Counter bytes change -> K1 -> next round."
    },
    {
      "id": "F2",
      "severity": "HIGH",
      "axis": "depth",
      "title": "C3 grades the formula, not the probe: a probe charging 6+nd per header keeps every counter green while the table is false",
      "evidence": [
        "tools/round97-depth-boundary-audit.py never runs the probe; it reads only MAX_STEPS (lines 69-73) and hardcodes PREAMBLE = 4 (line 35) and the '5 + nd' per-header term (line 103)",
        "mutation B (probe patched to charge +1 step per tensor header): real probe flips 833,332@nd1 and 555,555@nd4 from invalid to '-' -> two table rows now false; yet C3 -> DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=0 met=True rc=0 and C1 -> SELF_ASSESS97 checks=14 mismatches=0 met=True rc=0",
        "mutation C (preamble 4 -> 5): same result, both counters green, and the probe's counter reads ok:steps=4999997 while the table still states 4,999,996",
        "the +1 mutant survives ALL 17 C2 cells: new 'cells=4 cells_ok=4 survived=1' and legacy 'cells=13 cells_ok=13 survived=1' (real counter, --probe-file override)"
      ],
      "remediation": "C3 should derive preamble and per-header costs from the probe's bytes instead of hardcoding them; C1 check 7 should compare the probe's comment against that derived value, not the literal '5 + nd'; adding a plus1 mutant to C2 (anchor already unique) is the cheaper half."
    },
    {
      "id": "F3",
      "severity": "MEDIUM",
      "axis": "operability",
      "title": "C2's cells are sized past the four named forgeries, but a per-header mischarge slips through all 17",
      "evidence": [
        "frozen controls/c2-new-mutants.out re-verified: flat6 caught at W15, maxmeta at W16, undercharge and nopreamble at W14/W17 - the cells are correctly sized for the named classes (flat6 flips only at nd=4, as the rank arithmetic predicts)",
        "but the +1-per-header mutant survives new cells (cells_ok=4 survived=1) AND all 13 legacy (cells_ok=13 survived=1)",
        "W14's 900,000 tensors sit only 100,001 below the MAX_TENSORS=1,000,000 cliff (T=1,000,001 -> -MAX_TENSORS, 0.00s), so the discriminator is fragile"
      ],
      "note": "The plan's disclosed limit (a) arguably covers a per-header mischarge as ungraded; the severity is that it is the mutation that falsifies C3's table while every counter stays green."
    },
    {
      "id": "F4",
      "severity": "MEDIUM",
      "axis": "calibration",
      "title": "SKILL.md says 'three graded forgeries' and 'W14, W15 and W16'; the counter grades four mutants over four new cells (W14-W17)",
      "evidence": [
        "SKILL.md:2443 heading: '### Round 97 correction (step-budget boundary table and the three graded forgeries; dated 2026-11-08)'",
        "SKILL.md:2467: 'grades each with W14, W15 and W16 respectively'",
        "tools/round97-router-budget.py:146 NEW_CELLS has four (W14-W17); :163-176 MUTANTS has four (flat6, undercharge, maxmeta, nopreamble); frozen controls/c2-new-mutants.out has a fourth block 'mutant=nopreamble ... caught=1'",
        "plans/round-97-claims.md:83-91 correctly says 'four graded mutants' and lists W17 - so the PLAN is right and SKILL.md is stale",
        "grep of tools/round97-self-assessment-audit.py for W14/W15/W16/W17/forgeries: no check grades the enumeration, so C1 stays green on the false sentence"
      ],
      "impact": "The omitted forgery is the preamble-drop - the one that pins the '4 +' preamble term C3's table is built on. A reader auditing forgery coverage under-counts.",
      "remediation": "Cheapest highest-value fix in this report: correct SKILL.md:2443 and :2467 to say four forgeries / 'W14, W15, W16 and W17' and name the preamble-drop forgery. SKILL.md-only, no counter change, no K1 event."
    },
    {
      "id": "F5",
      "severity": "LOW",
      "axis": "operability",
      "title": "C2's predicate is host-speed-conditional; the lane caught this itself (amendment 1)",
      "evidence": [
        "tools/round97-router-budget.py:157 MARGIN=1.25 requires W03 natural >= 75s; frozen controls/c2-could-not-evaluate.out records exit 2 (W03 55.0s) and all four legacy-receipt W03 timings (59.11/53.62/61.84/70.95s) are below 75s",
        "the lane's own plans/round-97-amendment-1.md (commit e057166e, 'recorded before any C2 cell scored') adds --slow-files 72; counter bytes UNCHANGED (sha256 24e2fad7... at both 9e605d41 and e057166e) so K1 holds, and the guard is sized, not bypassed - a legitimate repair, not a finding against the lane",
        "my own independent run (legacy cells, --burners 0, real probe at e057166e): cells=13 mismatches=0 positive_mismatches=0 load_cells=13 load_stable=1, w03_seconds=214.6, load1_nat=87.28 - the margin is satisfied only because the host was loaded; idle it is ~55s and the predicate exits 2"
      ],
      "remaining_gap": "plans/round-97-claims.md's disclosed limits never mention the margin or the host-speed dependence, and never reference plans/round-97-amendment-1.md - a reader working only from the frozen plan would not know the predicate command now carries --slow-files 72."
    },
    {
      "id": "F6",
      "severity": "INFO",
      "axis": "calibration",
      "title": "Both base controls reproduce exactly - neither counter is vacuous",
      "evidence": [
        "C3 at base 40763bd2: DEPTH_BOUNDARY97 rows=0 mismatches=1 met=False rc=1 - identical to frozen controls/c3-base.out",
        "C1 at base 40763bd2: SELF_ASSESS97 checks=14 mismatches=9 met=False rc=1 - identical to frozen controls/c1-base.out (base mismatches=9 as the task states)"
      ]
    },
    {
      "id": "F7",
      "severity": "INFO",
      "axis": "depth",
      "title": "C3 does catch a wrong step count - the counter's arithmetic half is sound",
      "evidence": [
        "mutation D (row 833,332's stated step count 4,999,996 -> 4,999,995) in a scratch fixture repo: DEPTH_BOUNDARY97 rows=6 checks=8 mismatches=1 met=False rc=1"
      ],
      "note": "Combined with F2, the counter's blind spot is specifically the verdict and the probe-behaviour link, not the arithmetic."
    }
  ],
  "falsification_verdict": {
    "C3_step_arithmetic": "CONFIRMED - 12/12 fixtures reproduce end-to-end; probe's own counter matches to the digit; mutation D caught",
    "C3_minus_invalid_split": "CONFIRMED for the counter's fixture class; the verdict column is over-general (F1)",
    "C3_recompute_from_probe_MAX_STEPS": "PARTIAL - arithmetic recomputes from MAX_STEPS, but PREAMBLE=4 and 5+nd are hardcoded so a differently-charging probe keeps the counter green (F2)",
    "C2_cell_sizing_named_mutants": "CONFIRMED",
    "C2_catches_per_header_mischarge": "NOT GRADED - survives all 17 cells (F3)",
    "C2_predicate_reachability": "HOST-CONDITIONAL, repaired by the lane's own amendment 1 (F5)",
    "C1_14_checks": "REPRODUCE (base 9, HEAD 0) but do not grade SKILL.md's description of its own tooling (F4)",
    "summary": "No C3 row's real verdict differs from the claim for the counter's fixture class; C2's cell expectations are met on the real probe. The falsifications are of the counters' coverage (F1, F2) and of SKILL.md's self-description (F4) - not of the six-row table's numbers."
  },
  "bounds_compliance": {
    "lane": "/home/vgpnk/Projects/shokunin/kama-shokunin",
    "wrote_only": [
      ".ufo/waves/round-97/w1/SN01StepFlips.md (the Report: path)",
      ".ufo/waves/round-97/w1/out/SN01StepFlips/ (5 JSON receipts + scripts/)"
    ],
    "tracked_lane_files_edited": "none",
    "git_mutations_on_lane": "none (no add/commit/stash/checkout/switch/reset/pull/push; only read-only show/log/diff/rev-parse/status)",
    "fixture_repos": "two separate git init trees under scratch (c3fix.*, fixclone), each asserted git rev-parse --show-toplevel == its own path before any commit; both deleted with the scratch dir",
    "scratch_deleted": true,
    "subagent_dispatch": "none (leaf member)",
    "pacman": "never run",
    "process_killing": "none"
  },
  "tooling": {
    "installed": "none",
    "used": [
      "python3 3.14.8 (system, pre-existing)",
      "git (system, pre-existing)"
    ],
    "reason": "no new tooling needed; the probe, stub router and fixtures were driven with stock python3 and git"
  }
}
```
