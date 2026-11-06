# Round 91 — frozen claims (kama)

Base revision `c06838c5b94576971ea33ac465bf2c935e9037f9` (lane `master` at round start; `jj-lane.sh state`
ahead=0 behind=0, tree clean). L1 `KamaR91` (holds the §3 planner seat). Frozen in the commit that adds this
file; nothing below changes after that commit. Every control named here was executed before this file was
committed; its receipt is committed with it under `.ufo/waves/round-91/controls/`.

Closure history read before declaring: `corpus/lessons/round-90-verifier-spotcheck.md` (r90 **admitted**; routed
R1–R6) and `round-89-verifier-spotcheck.md` (r89 admitted). Rounds 86–88 were rejected-honest-stop (MANIFEST);
their lesson — a frozen expectation written from lane prose — is why both claims grade observable output only:
C1 the probe's own verdict and wall time on stub listeners, C2 bytes fetched live from pinned upstream URLs.
Routed R5 (r90: "no time bound … SN01: 207 s for a 4 MiB answer of 200k ids") and SCORECARD §Planned (round 91)
items 1 and 6 are C1.

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7.
Lowest non-retired: depth / calibration / adjacency (7). C2 works depth.

## C1 — operability: a large answer under the 4 MiB cap is graded in bounded time

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round91-answer-time.py --repo . --rev <M> --work <scratch>` prints
`ANSWER_TIME cells=12 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured commit M,
the counter's bytes being identical to this freeze commit.

- Cells (12, lane-owned stub listeners, each body under the 4 MiB cap; every pass condition includes
  "finished within 20 s wall", a run is killed at 120 s): T1 200 000 ids then `good` (MODEL_OK matched), T2 the
  same without `good` (MODEL_MISMATCH), T3 a router listing of 80 000 `loaded` entries then `good` (MODEL_OK),
  T4 one 3 900 000-byte id then `good` (MODEL_OK matched), T5 one id of 1 900 000 `a/` pairs ending
  `/good.gguf` (MODEL_OK matched); positives P1 plain, P2 `/models/sub/good.gguf` → `good` matched, P3
  `good.gguf.gguf` vs `good` MODEL_MISMATCH (one `.gguf` stripped per side), P4 non-ASCII id verbatim, P5 `"`/`\`
  id verbatim, P6 `other` vs `good` MODEL_MISMATCH, P7 wildcard. `positive_mismatches` counts P1–P7 (harm).
- Do-nothing control (base probe `b71c309a…`): `controls/c1-base.out`.
- Forgery controls (`--probe-file`, print `probe=override`, can never meet the predicate), built by
  `controls/c1-forgeries.sh` from the base bytes: F1 count cap (only the first 1000 served ids are compared)
  `controls/c1-f1-count-cap.out`; F2 exact match (no `normalize_id`, so no fork) `controls/c1-f2-exact-match.out`.
- Rule to implement (intent; the claim is judged only by the counter): the per-id `$(normalize_id …)` fork in
  `model_matches` and the per-entry `model_matches` call in `router_refine` are replaced by one linear pass
  over all served ids (no count cap), with the same rule — drop through the last `/`, strip ONE trailing
  `.gguf`, compare bytes. Sourced: S592 (POSIX.1-2024 `awk`, pubs.opengroup.org: an assignment operand's value
  is read "as a STRING token", i.e. with escape processing, while `ENVIRON` holds "the value of that variable"
  verbatim — so ids with `\` must reach awk through the environment, not `-v`) — opened this round before freeze.
- Kill rules (any one → C1 not verified): K1 `positive_mismatches>0` at M; K2 a harm suite regresses against its
  base receipt `controls/harm-base.out` (run by `controls/harm.sh`): `tests/probe-verdicts/check.py` 77/77,
  `tools/test-snapshot.sh` 30/0, `round89-unloadable-cells.py` 11/0/0, `round90-hostile-answers.py` 13/0/0,
  operator router 127.0.0.1:1234 (GET only) `MODEL_OK router-unloaded-autoload`; K3 the counter changes after
  this commit.
- Held-out (not in the predicate): wave seats build unseen large/slow answers after M (models[] instead of
  data[], name/model keys, the python-free path, long router ids, many duplicate ids, CRLF/NUL in ids). Each is
  reported with base and M verdicts and times; a held-out cell where base is right and M wrong is harm.

## C2 — depth (lowest axis, 7): serving timeout and limit thresholds, each bound to a pinned upstream line

**Predicate:** `python3 tools/round91-threshold-rows.py --repo . --rev <M2>` prints
`THRESHOLD_ROWS rows=<n> bound=<n> unbound=0 duplicates=0 engines=<e> fetch_failures=0 …` with n >= 10 and
e >= 3, and exits 0 at the measured commit M2, counter bytes identical to this freeze commit.

- Population: rendered rows of `SKILL.md` `## Serving timeout and limit thresholds` (outside HTML comments and
  fences, column 0). A row binds only when its source `S###` is a mined tier-A/B `corpus/SOURCES.md` row whose
  https URL names the engine and the row's pin (no moving ref), the URL fetched live now has the row's
  sha256, the declared line holds the backticked literal, the value occurs in the literal and the threshold
  cell names (backticked) a parameter that occurs in the literal (counter docstring B1–B7).
- Do-nothing control: base `rows=0`, exit 1 (`controls/c2-base.out`).
- Forgery battery on a scratch fixture repo (`controls/c2-forgeries.py` → `controls/c2-forgeries.out`): V1 one
  legit S587 row binds (`rows=1 bound=1`, exit 1: under 10); V2 ten prose rows on an absent source
  (`unbound=10`); V3 one legit row + T02 wrong line, T03 value not in literal, T04 moving ref, T05 digest
  mismatch, T06 pin not in URL, T07 engine not in URL, T08 queued source, T09 duplicate, T10 empty cell, T14 no
  parameter named (`rows=11 bound=1 unbound=9 duplicates=1`), with comment/fence/indented rows uncounted; V4
  ten genuinely bound rows from one engine (`engines=1`, exit 1). All exit 1.
- Known counter limit (disclosed before data): a row that names a real parameter on a real numeric line binds
  whatever its prose says; the semantic fit of name, value and decision to the line is K2, a reviewer read.
- Kill rules: K1 counter changes after this commit; K2 a non-author reviewer finds a row whose threshold name,
  value or probe decision misstates its line (reported per row; any such row → C2 not verified); K3 a row cites
  a source row not opened this round without re-opening it.

## Separability, sources, carried defects

- C1's counter never reads `SKILL.md` or `SOURCES.md`; C2's counter never runs the probe. Either verifies with
  the other unlanded.
- Sourced claims: C1 rests on S592 (POSIX awk assignment operand vs `ENVIRON`), C2 rows on the pinned upstream files opened this round
  (llama.cpp `common/common.h` @ b12177, Ollama `envconfig/config.go` @ v0.40.11, vLLM `vllm/envs.py` @ v0.32.0),
  each a new SOURCES row with this round's access date, sha256 and located quote.
- Carried from the r90 closure: R1 (`round75-instruments` `bad_rows=19`, L0 open) stays open, not claimed; R2
  (`probe-answer-bounds.md` verified-at names M not M′): dated correction this round, lesson mistake; R3
  (`router-?` reason) and R4 (latency budget pin) are wave items; R5 is C1 (time) plus disclosed limits; R6
  (held-out LIMIT cells, alias pins) carried.
