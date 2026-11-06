# Round 89 — frozen claims (kama)

Base revision `56174a1fa6a27faa91d3664ef4730b48dd3149c0` (lane `master` at round start; `jj-lane.sh state` ahead=0 behind=0).
L1 `KamaR89` (holds the §3 planner seat). Frozen in the commit that adds this file; nothing below changes after
that commit. Every control named here was executed before this file was committed; its receipt is committed with it.

Fresh-start reads before declaring (the lane's last six closures are rejected: r83 `rejected-harmed`, r84–r88
`rejected-honest-stop`): `corpus/lessons/round-86-verifier-spotcheck.md`, `round-87-verifier-spotcheck.md`,
`round-88-verifier-spotcheck.md` (all honest stops). The r88 root failure was a frozen expectation written from
lane prose that the runtime's own answer contradicted (R1, R7, KQ141). This round therefore carries **no canned
expectation**: every C1 cell's expected verdict is the router's answer to a real request at run time, and every C2
row binds to a captured wire answer.

Domain discovery that motivates C1 (pre-freeze recon, L1 scratch, then reproduced by the committed control): on
both the pinned b11755 and the current release b12177, a router entry whose `--model` file is missing, not GGUF,
or corrupt is listed `unloaded`; with default autoload the round-88 probe grades it `MODEL_OK
router-unloaded-autoload`, while a real request answers `500 {"error":{"code":500,"message":"model name=<id>
failed to load","type":"server_error"}}`. The operator's live router (127.0.0.1:1234, autoload on) has four such
entries; their files exist and carry GGUF magic (GET-only read, `controls/harm-base-operator-1234.out`).

## C1 — operability (sourced: S583, S584, S585): router entries whose model file cannot load

**Predicate (one sentence, same in counter docstring and receipt label):**
`python3 tools/round89-unloadable-cells.py --repo . --rev <M> --work <scratch>` prints
`ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev …` and exits 0 at the measured commit M,
the counter's bytes being identical to this freeze commit.

- Oracle (frozen, from S583 `tools/server/server-models.cpp` @ `6c01da62` lines 1641, 1956, 1962): HTTP 200 →
  `MODEL_OK`; 400 with `model is not loaded` → `MODEL_UNLOADED`; 500 with `failed to load` → `MODEL_UNLOADED`;
  anything else is could-not-evaluate (exit 2), never a verdict.
- Cells (11, live, lane-owned b12177 children, sha256 `ba272ee3…b362b0`; model stories260K sha256 `270cba1b…`):
  U1 missing preset path, U2 not-GGUF bytes, U3 GGUF magic + garbage, U4 first half of a valid file, U5 file
  deleted after listing, P1 valid unloaded (autoload), P2 valid loaded, N1 valid unloaded without autoload, N2
  bad header without autoload, P3 sleeping, P4 relative `--models-dir` with the probe in another cwd.
  `positive_mismatches` counts P1–P4, N1, N2.
- Do-nothing control (base probe `99dd1ab8…`): `mismatches=5 positive_mismatches=0`, exit 1 —
  `.ufo/waves/round-89/controls/c1-base.out` (U1–U5 graded `MODEL_OK router-unloaded-autoload`).
- Forgery controls (real historical probe bytes, so no forged file is needed):
  F1 blanket refusal = round-88 measured probe `138a7543` (`unloaded`/`sleeping` always drift):
  `mismatches=3 positive_mismatches=3` (`controls/c1-f1.out`); F2 pre-router probe `9b4c7af1` (any listed id
  is `MODEL_OK`): `mismatches=7 positive_mismatches=2` (`controls/c1-f2.out`). Both exit 1.
- Rule to implement (intent; the claim is judged only by the counter): for a matching `unloaded`, not-failed
  entry on an autoload router, resolve the absolute `--model`/`-m` (and `--mmproj`/`-mm`, `--model-draft`/`-md`)
  paths in `status.args`; only when `status.args[0]` names an existing local file (the router's binary as this
  host sees it). A missing path → `MODEL_UNLOADED router-model-missing`; a path that is not a regular file, or a
  GGUF whose header the loader rejects (bad magic, version 1, version above 3 or byte-swapped, alignment not a
  power of two, more than 4 dims, ne[0] not a multiple of the block size, non-contiguous tensor offsets, tensor
  data past end of file — S584 `ggml/src/gguf.cpp` @ `6c01da62`; type sizes from S585 `gguf-py/gguf/constants.py`
  `GGML_QUANT_SIZES`) → `MODEL_UNLOADED router-model-invalid`. Unknown tensor type, a parse budget exceeded,
  an unreadable file (permissions), a relative path or a non-local router → no change (a false red is worse
  than the known false green). Any loadable matching entry still wins.
- Kill rules (any one → C1 not verified): K1 `positive_mismatches>0` at M (harm); K2 a harm suite regresses vs
  base at M: `tests/probe-verdicts/check.py` 72/72, `tools/test-snapshot.sh` 30/0, round-88
  `.ufo/waves/round-88/repair/oracle-cells.py` 0 mismatches, round-88 frozen `tools/round88-router-cells.py`
  `mismatches=2` (C05, C12 only), operator router 1234 probe verdict `MODEL_OK router-unloaded-autoload`
  (GET only) — base receipts `controls/harm-base-*.out`; K3 the counter changes after this commit.
- Held-out cells (not in the predicate): wave seats build unseen unloadable classes after M (e.g. near-end
  truncation, a directory or FIFO at the path, unreadable permissions, a missing mmproj, a split shard). Each is
  reported with base and M verdicts; a held-out cell base grades right and M grades wrong is reported as harm.

## C2 — depth (lowest-scoring axis, 7): router error signatures bound to wire answers

**Predicate:** `python3 tools/round89-signature-rows.py --repo . --rev <M2>` prints
`SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0` and exits 0 at the measured commit M2, counter bytes
identical to this freeze commit.

- Population: rows of the table under `## Router error signatures (llama.cpp router mode)` in `SKILL.md`. A row
  is bound only when its receipt at M2 holds a captured answer from the pinned b12177 binary with the same
  endpoint, HTTP code and exact `error.message` (`<id>` substituted with the requested model).
- Receipt (pre-freeze input, not the claimed work): `.ufo/waves/round-89/measured/router-signatures.jsonl`
  from `tools/round89-router-signatures.py` (9 calls, 8 error answers on two lane-owned children).
- Do-nothing control: base `rows=0 bound=0`, exit 1 (`controls/c2-base.out`). Forgery battery on a scratch
  fixture repo (true row, duplicate, fabricated message, wrong code, source text instead of wire text, wrong
  build, missing receipt, row outside the section): `rows=7 bound=1 unbound=5 duplicates=1`, exit 1
  (`controls/c2-forgeries.out`).
- Kill rules: K1 counter changes after this commit; K2 a row carries a message the receipt does not hold.

## Separability, sources, carried defects

- C1's counter never reads `SKILL.md`; C2's counter never runs the probe or a server. Either verifies alone.
- Sourced claim: C1 rests on S583/S584/S585 (rows written this round after opening each source).
- Carried from the r88 closure: R1 is answered by C1's oracle-only design (no canned cells); R2/R3 are
  re-pointed in SCORECARD this round (not claims); R5 (`tests/probe-verdicts/check.py` and `MODEL_UNLOADED`)
  and R4 (`round75-instruments` `bad_rows=19`) are investigated by wave items and dispositioned in the lesson;
  R6 answering model per seat is recorded from `w1-results.json` if present; R7: the opened sources were swept
  against the frozen oracle mapping before freeze (S583 lines 1641/1956/1962 match the three mapped answers).
