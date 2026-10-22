# ScribeSkillRows — advice report (round-25 attempt 2, wave 1)

Verdict: C2 SKILL.md decision-row draft delivered — 4 rows in the file's
decision-table format, each naming the knowledge entry, the registered cell ids
and the fixture scope, with an exact insertion point (after SKILL.md line 672,
before line 674). No llama-server child was started; SKILL.md was not edited
(lane production file, L1-writer only).

## Behavior

Read (read-only): preregistration.json (C2 cells K1–K8, measure, learning
artifacts), preregistration-amendment-1.json (strict counting rule), amendment-2
(X1–X3, L1–L3, launch rule, `-v` honesty notes, learning_artifacts),
count-c2.py (full: kv_pool_n_ctx + `llama_context: n_ctx` match at lines
55-57; strict cell_ok), pilot.md (K1–K3 observed rows), ATTEMPT-1-DISPOSITION.md,
CriticC2Sizing.md (fixture scope section 6; source lines S-a..S-h),
CriticLearningBar.md (fit.cpp 195-198/266-273; server-context.cpp 4301,
4318-4320; pool-vs-slot; round-20 supersession), SKILL.md around lines 120-175
(decision-table format), 642-678 (S060 sentence lines 665-667, round-20 section
close lines 669-672, round-21 start line 674), 724-1042 (existing prose decision
rows). No commands executed beyond reads; no tools installed; no ports opened.

## Gates

- Leaf seat: no subagent dispatch (none used).
- No llama-server child started (lives under ExecCapTool/ExecR20Supersede scope;
  my item names no port range).
- No writes outside `.ufo/waves/round-25/a2-build/out/ScribeSkillRows/` and the
  advice report path; no git/jj mutations; no SKILL.md edit.

## Findings (draft rows — acceptance items)

1. Reading `/props` `n_ctx` (per-slot, not pool): row 1. Ground: S060 sentence
   (SKILL.md:665-667), `/props`= `/slots`=`/v1/models` per-slot read
   (server-context.cpp:5236, 1437, 5186), pilot rows (pilot.md:14-16).
   Cells: K1–K8, X1–X3.
2. Unset `-c` + explicit `-np` + split cache (fit raises the pool): row 2.
   Ground: fit.cpp:195-198,266-273; X1 prediction pool 8192 / per-slot 2048;
   round-20 `nctx-crosscheck.py` 512 superseded; X3 (`--fit off`) fallback
   2048. Cells: X1, X2, X3.
3. Concurrency at full context on a unified pool: row 3. Ground: L1 prediction
   (shared 2048 pool, `Context size has been exceeded` server-context.cpp:4301,
   4318-4320); K1 vs X2 identical surfaces hide 4x full-context concurrency
   difference. Cells: L1, L2, L3.
4. When to require `-v` log evidence for the pool: row 4. Ground: pool printed
   only at `-v` (amendment-2 honesty notes), absent at `-lv 3`; counter requires
   kv_pool_n_ctx matching a captured `llama_context: n_ctx` line
   (count-c2.py:55-57). Cells: all 14.

Insertion point: after SKILL.md line 672, before line 674 (fallback: after line
667). Because C2 has not observed yet (receipt absent at base efe58e96 —
count-c2.py exit 2), the rows quote preregistered predictions and pinned source
lines; they must be re-anchored by L1 to the committed receipt after the claim
lands. No part of the draft claims observed values as served.

## Touched surfaces

- Wrote: `.ufo/waves/round-25/a2-build/out/ScribeSkillRows/rows.md`
  (the draft block + insertion point).
- This advice report.
- No other files touched.

## Out-of-scope

- SKILL.md edit (L1-only), commit/push, receipt, knowledge-entry file, tool
  installs, probe of registered consumers, any llama-server launch.

## Artifact paths (relative to kama-shokunin)

- `.ufo/waves/round-25/a2-build/out/ScribeSkillRows/rows.md`
- `.ufo/waves/round-25/a2-build/advice/ScribeSkillRows.md` (this report)
