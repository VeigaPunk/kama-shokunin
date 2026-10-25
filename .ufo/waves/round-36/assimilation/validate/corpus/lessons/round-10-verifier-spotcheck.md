# round-10 — non-author verification and spot-check (orchestrator, kaika)

Written by the integrator, not the lane (CORPUS.md: corrections and outside reviews are new
files; the lane owns `round-10.md`). Verifiers were fresh agents dispatched by the orchestrator
after the round landed at `40660352d`; full reports are committed in the fleet repo at
`.ufo/waves/kaika-w3/kama-review.md` and `kama-critic.md`.

## Spot-check (LEARNING.md — at least one admit and one reject)

| decision | sample | verifier | result |
|---|---|---|---|
| admit | three new entries (engine health endpoints across llama.cpp/vLLM/SGLang/Ollama, serving metrics, GGUF/quantization compatibility) — reviewer re-opened 10 rows (S001 `tools/server/README.md:486`, S005 §Supported Hardware); agree | W3ReviewKama | agree |
| reject | four rejections incl. S030 (the row citing the lane's own in-province gate runs, rejected so no claim rests on them) — agree (7/7 sampled decisions agree) | W3ReviewKama | agree |

## Adjudication

ADMITTED after post-review fixes `4066035` (SCORECARD axes erratum; Mistake-14 count retired; `validate-new-pointers.sh` rows=50 resolved=48 terminal=2 unresolved=0 with a negative control; C3 restated on knowledge entries). Orchestrator ruling D-1: read-only health checks against the lane's own registered local endpoints are inside kama's province; the campaign's documentation-only rule targeted external live targets — no violation, no claim rests on them. Per-axis: freshness improved (50 stale anchors → 0 uncorrected; A17/A51 corrected to explicit terminal states, not re-anchored; score 7→8), coverage improved (9→12 entries, 0→3 sourced; score 8→9; capability `sources-registry`, 30 rows, census ok), operability/depth/calibration/adjacency unchanged. Trends: expansion improved, quality improved (anchors corrected; KQ6–KQ10), discernment improved.
