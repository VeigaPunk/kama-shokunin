# kama round 80 — the round-79 record is graded, every engine pin is related, the class gets a second engine

Lane: kama. Round 80 (attempt 1). Base `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`; frozen plan
`plans/round-80-claims.md` (freeze `fe7b978013bd1aa6d67a7e0fbf6369b8d7a9b023`); sealed revision
for C1 `a9b4543f14625d0f37daa42ef664ee6f6ea975ea` (the round-79 record tip).

## Gate

Every source below was opened this round with `curl`; the receipts are
`.ufo/waves/round-80/w1/SC02Sources/curl.txt` and `.ufo/waves/round-80/w1/SR02ScoutOllama/`.

| Candidate | Source | Accessed | Located quote (≤25 words) | Decision |
|---|---|---|---|---|
| S554 Ollama `docs/api.md` at v0.40.11 | https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md (HTTP 200, 54614 bytes, sha256 `96db0308…d0f5`) | 2026-11-04 | "List models that are available locally." — `## List Local Models`, after the `GET /api/tags` fence, line 1358 | **admit** (tier A, docs): the pinned release's own definition of the native model list; grounds the second-engine reading and bounds it to an inventory |
| S555 supersedes S553 — the model-list heading | https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md (HTTP 200, 135608 bytes, sha256 `8fd5abde…35c6`, byte-identical to S553's read) | 2026-11-04 | "If a model is not running, it will be added or updated according to the source" — `### GET /models: List available models`, note 1, line 2227 | **admit** as a supersession row (R79V6): the same bytes, the anchor moved from the region label `§Router mode` to the heading that actually carries note 1 |
| S556 llama.cpp `docs/preset.md` at 39febd2a | https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md (HTTP 200, 4090 bytes, sha256 `3e664354…f13`) | 2026-11-04 | "allows users to create reusable and shareable parameter configurations for llama.cpp" — `## Introduction`, line 5 | **reject** (R79V4): the round's census class reads a model list and no round-80 claim parses a preset file; flip: a round that grades preset-inherited request parameters on the pinned fixture |

Gate result: 2 admits (S554, S555), 1 reject (S556). Spot-check: **pending** — this round's
non-author closure samples one admit and one reject and records agree/disagree; the seat that
drafted the rows is the lane.

## Corrections

The round-79 record is graded by `tools/round80-selfrecord-round79.py`. Its F4, F5 and F6 facts
are stale at the sealed revision: the record states a verdict its own receipt contradicts. The
three corrections below are value-bound and re-derive at this round's tip.

`corrected F4 old=c2=verified new=c2=not-verified:failed=1 at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

`corrected F5 old=before-selftest=pass=26 new=before-selftest=pass=22 at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

`corrected F6 old=log=all-verified new=log=c2-not-verified at=a9b4543f14625d0f37daa42ef664ee6f6ea975ea date=2026-11-04`

- **F4** — the round-79 banner and the C2 row of its claim table say "C2 operability verified";
  the receipt that row cites, `.ufo/waves/round-79/measured/after/c2-gate.out` at `b756571e`,
  prints `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` with `EXIT=1`. The record's own
  §Gate and the fleet report say "honest stop"; the banner and the table did not follow.
- **F5** — the C2 row's before cell says `PRE_REPORT_SELFTEST pass=26 fail=0`; the committed
  before receipt `.ufo/waves/round-79/measured/before/c2-gate-selftest.out` prints `pass=22`.
- **F6** — `LOG.md` §Round 79 says "Three claims, three distinct axes, all verified on their
  receipts"; C2's receipt is red. The LOG correction is the appended entry under §Round 80
  (`LOG-CORRECTION round=79 claim=C2 verdict=not-verified`), never a rewrite.

## Mistakes

| Class | Evidence pointer | Captured-by | Fix |
|---|---|---|---|
| self-record-states-intent | `SCORECARD.md:6` and `SCORECARD.md:4587` at `a9b4543f` say C2 `verified`; `.ufo/waves/round-79/measured/after/c2-gate.out` prints `failed=1` | `none` at the round-79 base — the round-79 closure found it by reading (R79V1/R79V2), not by a counter; this round's F4/F5/F6 facts capture it mechanically | `tools/round80-selfrecord-round79.py` grades six declared facts against their own receipts and requires one value-bound correction per stale fact; `corpus/QUALITY.md` KQ132 |
| fixture-outside-owner | `.ufo/waves/round-80/measured/after/c3-llamacpp-recheck.out` live leg lists `ports=…,48175` — the L1's own manual `nohup ollama serve` probe outlived its shell and kept a listener until it was killed by hand | the round's own live-host leg (a census that names every model listener outside the registry) | the census counter owns its child's whole lifecycle (`start_new_session`, terminate/wait/kill, port-closure check); manual fixture runs are not evidence and are killed on sight |

## Freeze divergences (recorded, not rewritten)

1. **F5's receipt path.** The plan's fact table names
   `measured/before/c2-gate-arms.out` for the `pass=22` tally; that file carries the base
   `BASE_ARM_ORDER` line, and the tally lives in `measured/before/c2-gate-selftest.out`. The
   counter reads the selftest receipt. Value string and predicate unchanged.
2. **C2's commit-anchor clause.** The plan reads "a commit row's 40-hex anchor is not any
   upstream tag's peeled oid". Reconnaissance before the measurement found
   `39febd2adb947b70da35e95f9351b3bf58ad170a` **is** tag `b11963`'s peeled commit, so the row is
   labelled `tag:b11963` and the clause is graded as a label rule: `not-a-release-tag` rows must
   not be a tag tip, `tag:<name>` rows must re-derive that tip. Target line unchanged.
3. **C3's control.** The plan calls the control "the base probe copy (no `registered` class)"; the
   base for *this* round (`c45fc7d1`) already carries the class, so the control probe is the
   round-78 tip's `tools/kama-probe.sh` (sha256 `4393ab81…`), which has no class and scores
   `class_missing=1`, exit 1.

## Frontier position

The lane now holds: a self-record grader that mechanically refuses an intent-stated verdict
(C1), a dated relation for every ref it holds on three serving engines (C2, five refs over
llama.cpp/sglang/vllm), and a class-engine register proving the `registered` census class on two
engine fixtures (C3). Still open: K05 declared-versus-served context capacity across real
consumers, the three registered consumers (`DEAD`), and the inherited append-only register debt
that keeps the pre-report gate's arm 8 red (`4af44f7`; no post-introduction row can answer it).
