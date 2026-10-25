# kama — round 34 lesson (2026-10-24, attempt 1)

## Claims

Frozen set: `.ufo/waves/round-34/preregistration.json` (base
`7c35289da5f4b94e062cd900eb086919e5094003`). Two claims, distinct axes,
causally separable; the axis scores are held (calibration 7, operability 8).

- **C1 calibration 7 → 7 (lowest assigned non-retired axis).** The lane's
  SCORECARD capability self-assessment must list every capability the lane
  demonstrated. Frozen predicate: `python3 tools/capability-repertoire-audit.py
  --repo . --tip <full-commit>` prints `listed L observed O missing M
  unsubstantiated U met B`; before `missing 3` (met False, exit 1), after
  `missing 0 and unsubstantiated 0` (met True, exit 0). Before: `listed 3
  observed 6 missing 3 unsubstantiated 0 met False` (exit 1) at base
  `7c35289`; after: `listed 6 observed 6 missing 0 unsubstantiated 0 met True`
  (exit 0) at the data tip `29f9d1e1b20ef6e16e578e6e039f95f4f3fb4007`
  (`.ufo/waves/round-34/c1-before.out`, `.ufo/waves/round-34/c1-after.out`).
  Do-nothing control: a scratch SCORECARD whose canonical table repeats the
  three missing capability NAMES with no resolving evidence pointer reads
  `listed 6 observed 6 missing 0 unsubstantiated 6 met False` (exit 1,
  `.ufo/waves/round-34/controls/c1-noop-control.out`) — the control does not
  reach the target.
- **C2 operability 8 → 8.** The lane's own instrument-registry gate must
  evaluate every tracked round-scoped counter, including the two round-33
  counters that live in `tools/` and were named only in prose. Frozen
  predicate: `python3 tools/gate-registry-check.py --rev <full-commit>` prints
  `registered R unregistered U defective D`. Before (widened population at
  base): `registered 10 unregistered 2 defective 0` (exit 1,
  `.ufo/waves/round-34/c2-before.out`); after: `registered 12 unregistered 0
  defective 0` (exit 0, `.ufo/waves/round-34/c2-after.out`). Do-nothing
  control: the base revision, whose SKILL.md names both tools in prose only,
  still reads `registered 10 unregistered 2 defective 0` (exit 1,
  `.ufo/waves/round-34/controls/c2-prose-only-control.out`). The gate's own
  selftest stays green: `GATE_SELFTEST pass=6 fail=0` (exit 0).

## Gate

Item-10 assimilation, ONE theme — **how a served model name / alias is
resolved across local serving stacks**. Package read read-only from
`/home/vgpnk/Projects/shokuknow/merge/kama/`; nothing was written there and no
campaign tool was run there. Id-collision check in scratch
(`.ufo/waves/round-34/assimilation/`): the lane registry holds 194 ids
(S001–S194), the staged package 129 (S195–S323), and `comm -12` is EMPTY — no
collision, so no renumber map was needed and the adopted ids continue the
lane's space. The guard was proved once before the first append: a scratch
registry whose `  | S195 | …` row is indented yields a NONEMPTY `collisions`
with the 0–3 leading-space pattern while a column-zero-only pattern extracts
nothing (`guard-collisions`, `guard-ids-03space`, `guard-ids-col0`).

Scratch transformation and validation before any append: the staged rows were
rewritten to the fleet census schema (11 columns, no literal or escaped pipe in
any cell, `recheck` reduced to a bare `90d`, `status` `mined`, `used-by` naming
exactly the admitted entries). The mirror
(`.ufo/waves/round-34/assimilation/validate/`) holds a copy of the lane's
`corpus/`, the append block in the Registry table and the two admitted entries
at their repo-relative paths; `sources-census.sh validate --file` on that mirror
exits **0** (`validate-census.out`) BEFORE the first registry append.

Admitted (2 entries, 5 rows) — every source re-opened by the L1 on 2026-10-24:

| id | source | located quote (≤25 words) | recheck result |
|---|---|---|---|
| S196 | https://docs.vllm.ai/en/v0.17.0/cli/serve/ §Named Arguments → `--served-model-name` | "The model name in the model field of a response will be the first name in this list." | `first name in this list` count=1 |
| S205 | https://docs.sglang.io/docs/developer_guide/bench_serving §Fair embedding comparison | "`--flush-cache` calls `/flush_cache` for SGLang and `/reset_prefix_cache` for vLLM after warmup." | `reset_prefix_cache` count=2 |
| S206 | https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ §调用示例 → 模型名称获取方式 | "对于vLLM/SGLang，可通过模型列表接口`<EAS_ENDPOINT>/v1/models`获取。" | `v1/models` count=4 |
| S209 | https://www.alibabacloud.com/help/ja/ack/cloud-native-ai-suite/user-guide/deploy-standalone-llm-inference-services §ステップ 3 | `curl http://localhost:8000/v1/chat/completions ... -d '{"model": "/models/Qwen3-32B", "messages": ...}'` | `chat/completions` count=1 |
| S223 | https://docs.gitlab.com/administration/gitlab_duo_self_hosted/supported_llm_serving_platforms/ §Find the model name | "the model name is the value of the `data.id` field in the response" | `data.id` count=1 |

S206 was on the payload-absent quarantine slice; it was hand-checked this round
(fetched and its quote located) before it was appended. Stripped from the
staged recheck cells: the re-verify sentences and the `SOURCES-PROPOSED.md`
pointers — they are recorded here, not in the row.

Refused, with reason and flip:

| candidate | reason | flip |
|---|---|---|
| `corpus/knowledge/served-model-id-resolution-amendment-2026-10-24-r7.md` | an amendment whose base chain (r3–r6) is not adopted this round; adopting one link of a dated amendment chain leaves the corpus's amendment history incomplete | adopt the full r3–r7 chain together in a later round |
| `corpus/knowledge/cross-literate-endpoint-venues.md` (S206, S209's second `used-by`) | it is the lit-erature survey entry, not the served-name contract; this round takes ONE theme | adopt as its own theme in a later round |
| staged row S224 | on the payload-absent quarantine slice and not cited by an admitted entry | hand-check the cited source, then admit |
| staged rows S200, S202, S210, S211, S230 | on the payload-absent quarantine slice, not cited by an admitted entry | hand-check the cited source, then admit |

Quarantine slice (kama, 7 rows, every row carrying an S-id):
`S200 S202 S206 S210 S211 S224 S230`, all with the class cell `payload-absent`.
S206 was hand-checked and adopted; the other six stay out until hand-checked.

`considerthese/2026-10-23.md` was mined, never edited. One still-unimplemented
proposal is carried as this lesson's frontier item 1 (the shortcut-class
ledger), grounded through the lane's own bar — the round-26 to round-28
shortcut classes and the KQ37/KQ42 criteria.

Own-work row opened this round: **S324** (the widened instrument-registry
population in `tools/gate-registry-check.py`), tier A, `used-by` `SKILL.md`.

## Mistakes

| # | class | evidence | captured-by | fix (shown able to fail) |
|---|---|---|---|---|
| 1 | reference-drift | The lane's own instrument gate could not see two live counters (`tools/round33-claim-audit.py`, `tools/round33-gate-receipts.py`): its population regex named only `.ufo/waves/round-*/count-*.py`, and SKILL.md documented both in prose. The round-33 closure routed this. | none — no criterion required the gate's population to cover the `tools/` location, nor required a named instrument to be in a registry row | C2 widens the population and adds the two rows; the control (base revision, prose only) still reads `unregistered 2` (exit 1), and the gate's selftest stays 6/6 |
| 2 | scope / self-assessment | The SCORECARD's canonical repertoire table listed 3 of the 6 capabilities the lane had demonstrated; the other three lived in per-round append sections only. | none — AXES.md asks for a repertoire table but no criterion measured it against what the lane demonstrated | C1's counter closes the gap (`missing 3 → 0`); the names-only control still fails (`unsubstantiated 6`) |
| 3 | provider | The first wave dispatch died at spawn for all 33 seats: `error: Cannot combine --prompt with --auto.` — the Kimi CLI refuses that pair. No seat work ran. | none — the wave contract did not pin the seat CLI's flag compatibility | re-dispatched the same validated `taskCall` with `--auto` removed, under `setsid nohup` so the dispatcher survives the parent's exit; the failed attempt is recorded in `.ufo/waves/round-34/w1/out/dispatch-manifest.json` |
| 4 | number-drift | The first census mirror exited 1 with five `E11 missing used-by` findings: the mirror held only `corpus/`, so the admitted entries' paths did not exist under the mirror root. | CORPUS.md census clause (used-by paths must exist) | the mirror was rebuilt with the referenced paths copied in; the gate then exits 0 (`validate-census.out`) |

## Frontier

1. `considerthese/2026-10-23.md` proposal 1 — a shortcut-class ledger across
   rounds (echo literals r26, help text r26 A0, type conversion r28 A0,
   declared-bounds projection r28 A1), with the next class flagged before the
   next depth round. Not implemented this round; it is a lesson-level pointer,
   and a ledger that only lists classes is not a measurement.
2. The `capability-repertoire-audit.py` population is the SCORECARD's own
   tables: a capability demonstrated only in a lesson is still invisible to it.
3. The served-name theme's remaining staged material: the r3–r7 amendment
   chain, the lit-erature survey entry, and the six still-quarantined
   payload-absent rows.
4. The round-33 wave's late-arriving seat outputs are inherited evidence, not
   round-34 seats; the round-34 wave census is in the fleet report.
