VERDICT: partial — attacked whether each KQ19 admit/reject clause maps to a check that the matrix or gates actually perform. The three measurement claims reproduce exactly and the widening/substring near-misses are genuinely gated; but three clause conditions have no gate (served identity/readiness, integer `code` value, document corrections), the probe-CLI gate alone cannot detect a trimmed matrix, and "drift graded" is only a self-consistency check.

Item: `corpus/QUALITY.md:109` (KQ19), round-16 row. Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`, HEAD `b8e485c`.

## Revision drift observed during the review

At start `git status` showed only the untracked `falsify/` tree at HEAD `b8e485c`. Mid-review a concurrent falsify integration modified 15 tracked files (all uncommitted). I did not edit them; I re-checked every file this item depends on and reran the current bytes:
- `tools/kama-probe.sh`: diff is comment-only header prose; matcher/gate code unchanged. Current sha256 `36b64978…`; full matrix on it → **exit 0, 72/72** (run 11).
- `tests/probe-verdicts/check.py`: diff is docstring/help text only (`3` → `4` malformed tests); logic and cited line numbers unchanged.
- `.ufo/waves/round-16/measure.py`: gains a matrix-breadth pin (see the first finding); the pinned digest equals the digest I computed over the 9 current matrix files (run 12).
- Consequence for L1: `run-before.json` / `run-after.json` still record the pre-integration probe sha `6edd3c4c…`; the worktree probe is now `36b64978…` (comment-only diff) and run 11 reproduces 72/72. A byte-level receipt check will flag this drift until `measure.py` is rerun after integration.

## What I ran (all commands from the lane root; exit codes as observed)

1. `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` → **exit 0**, `tests 72 passes 72 failures 0`.
2. `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → **exit 1**, `tests 72 passes 55 failures 17`; failed-row set == the 17 `expected.verdict == MODEL_LOADING` rows; triple `(verdict, reason, probe_exit)` changed on exactly those 17.
3. Mutation probe `/tmp/.../probe/mut-code-any-int.sh` (`code == 503` → `code >= 0`) through the full matrix → **exit 0**, `tests 72 passes 72 failures 0`.
4. Mutation probe `mut-any-503.sh` (any non-empty 503 body → `MODEL_LOADING`) → **exit 1**, `tests 72 passes 49 failures 23`.
5. Mutation probe `mut-served-identity.sh` (`C_SERVED=stories260K` in the `MODEL_LOADING` branch) → **exit 0**, `tests 72 passes 72 failures 0`; row `LoadingEnvelope.canonical-alias` recorded `served_model=stories260K`, `passed=True`.
6. Deletion experiment: copied `check.py` + the 5 non-reject families (`EnvelopeShapes`, `ForeignControls`, `LoadingEnvelope`, `LoadingRace`, `ReadyControls`) to `/tmp/.../matrix/`, omitting `NearMissTriple`, `Overbroad503`, `NonLoadingStatuses`, `AuthAndDead`. Current probe (pre-integration bytes, sha `6edd3c4c…`) → **exit 0**, `tests 42 passes 42 failures 0`, `loading rows 15`; frozen probe → **exit 1**, `before_failed 15 == loading 15`, `changed 15 == loading 15`. Emulating `measure.py`'s then-current directional predicate (now at `:379-390`) on those two runs → `directional: True` (corroborates measure.py PASS; measure.py itself not run, forbidden by assignment).
7. Empty matrix (only `check.py` copied) → **exit 0**, `tests 0 passes 0 failures 0 sources []`.
8. No-python3 run: `env PATH=/tmp/.../bin` (symlinks to `/usr/bin/*` minus `python3*`) → **exit 1**, `tests 72 passes 55 failures 17`, every failure `FOREIGN_SERVICE / non-2xx-non-model-http` (e.g. `LoadingEnvelope.canonical-alias`).
9. Digest checks: `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh` = `93ee4302…` = `git show 20e392e:tools/kama-probe.sh | sha256sum` = `run-before.json` `parsed.probe_sha256`; `sha256sum tools/kama-probe.sh` = `6edd3c4c…` = `run-after.json` `parsed.probe_sha256`; pinned `server-http.cpp` = `24ede172…` = `sources/pins.json` digest, `located.middleware_server_state_block {start:307,end:328}`.
10. Source reads (no exit-code weight): pinned `server-http.cpp:307-328` (state middleware; 503 envelope 314-325), `:354` state gate before `:357` API-key gate; `check.py` grade block `:337-347`; `measure.py:379-390`; `tools/kama-probe.sh:428-446,503-506`.
11. After the concurrent integration: `sha256sum tools/kama-probe.sh` → `36b64978…`; full matrix on those bytes → **exit 0**, `tests 72 passes 72 failures 0`, `probe_sha 36b64978ee3a`.
12. Recomputed the new `measure.py` matrix pin from `measure.py:286-291`: 9 files, set sha256 `ad8f44d30afd75cb8257fa4f31616b2fce3b181b0e4818cf2ac1900d01ae995e`, exactly equal to `EXPECTED_MATRIX_SHA256`; row count 72 and loading count 17 match `EXPECTED_TESTS` / `EXPECTED_LOADING`.

## Findings, by severity

### MEDIUM — coverage is pinned only in `measure.py` and only as of the uncommitted worktree; `check.py` on its own still accepts a trimmed or empty matrix

KQ19 admits a verdict only when "The matrix carries exact-triple near-misses (… case/space/punctuation variants, float/bool/string code, non-503 statuses, auth statuses)" and rejects a claim when "a green run lacks … the near-misses".

At the revision measured (HEAD `b8e485c`) nothing pinned breadth. `check.py:152` loads whatever `*.json` siblings exist; `check.py:493` exits 0 whenever `failures == 0`; `measure.py` then derived `loading_names`, `before_failed` and `changed_names` from the matrix it found, so its directional predicate passed any reduced matrix that still contained a flipping loading row. Run 6 is the concrete falsification: with `NearMissTriple`, `Overbroad503`, `NonLoadingStatuses` and `AuthAndDead` removed (42 rows, 15 loading; 4 of the 5 enumerated reject-side categories gone), a copied `check.py` still exits 0 at 42/42 and the directional predicate evaluates true. Run 7: a zero-row matrix exits 0 with `tests 0`.

During the review the concurrent integration added the missing pin to `.ufo/waves/round-16/measure.py` (uncommitted): `EXPECTED_MATRIX_SHA256` (`:281`), `matrix_digest()` (`:286`), an early digest-mismatch return (`:307-310`), and `breadth` on counts (`:382`) folded into `ok` (`:389`). Run 12 verifies the pin is correct: the computed digest over the 9 current `*.json` files is `ad8f44d3…`, equal to the pinned value, and 72 rows / 17 loading rows match. So the documented counting command (`SKILL.md:531`) now rejects a trimmed matrix, which closes KQ19's "green run lacks … the near-misses" condition **for that command**.

Residual gap: `corpus/knowledge/endpoint-identity.md:184` calls `python3 tests/probe-verdicts/check.py` the "lane gate", and that gate remains vacuous by itself (runs 6-7, copied checker with identical logic; the current `check.py` diff is help text only). Advice: give `check.py` the same 72/17 minimum or import the pinned digest, or word KQ19 so coverage is enforced by the pinned counting command rather than by the probe CLI gate. Note the digest pin covers matrix content only; a regression inside `check.py`'s grade block would not be detected.

### MEDIUM — the "not served identity" limit is not graded; a probe claiming a served model on a loading row passes

KQ19 rejects a claim where the verdict "is read as runtime identification, served identity or readiness". `check.py:337` copies `served_model` and `evidence` into the record, but `:341-347` grades only `verdict`, `reason`, `probe_exit`, and a drift invariant. Run 5 confirms the hole: a `/tmp` probe that sets `C_SERVED=stories260K` on every `MODEL_LOADING` row still scores 72/72 exit 0, with `served_model=stories260K` present in the machine document. The shipped probe honestly emits `-` on all 17 loading rows (run 1 receipt), but nothing locks that. Advice: for rows whose expected verdict is `MODEL_LOADING`, assert `served_model == "-"` and that `evidence` carries the "unverified" caveat.

### MEDIUM — the integer `code` value 503 is not exercised by any row; exactness rests on type only

KQ19 defines the triple as `message` exactly `Loading model`, `type` exactly `unavailable_error`, and "an integer — not bool, float or string — `code` 503", then claims "exact-triple near-misses". All nine matrix files contain no row whose integer `code` differs from 503 (checked by parsing every `body_json`), so only the *type* axis is exercised. Run 3 falsifies the coverage claim: relaxing the matcher to `code >= 0` keeps 72/72 exit 0. The shipped matcher is correct (`tools/kama-probe.sh:443` compares `code == 503`), but the mutation survives the entire gate. Advice: add one row with `code: 500` (optionally 0) and `status: 503`; expected stays `FOREIGN_SERVICE`, and the matrix digest pin must be bumped with it.

### LOW — "drift … graded" is a self-consistency invariant, not an expectation

`check.py:346` asserts `record["drift"] == (record["verdict"] != "MODEL_OK")`, and `expected` schema explicitly excludes drift (`EXPECTED_KEYS = {"verdict","reason","exit"}`, `check.py:56`). Because drift is algebraically derived from the graded verdict, it adds no independent signal: it can only fail if the probe contradicts itself. The clause's sentence is literally satisfied; the wording overstates what is measured. Advice: either grade a per-row `drift` expectation or reword to "drift consistency is asserted".

### LOW — the document-correction condition has no gate and is applied inconsistently at the edges

"Every lane document that enumerates the vocabulary or routes the state elsewhere gets an appended correction in the same round" is not checked by any test (no `tests/`, `tools/` or `registry/` file references `corpus/QUALITY.md` or `corpus/knowledge`; `round-13/measure.py` has no `KQ19` reference). The prose appends are present (`endpoint-identity.md:182`, `consumer-registry.md:406`, `listener-census.md:389`, `served-identity-crosswalk.md:136`, `runtime-health-surface-matrix.md:60`, `snapshot-history.md:106`, `ollama-evidence-replay.md:376`, `SKILL.md:507-531`). Two literal counterexamples exist: `registry/endpoint-consumers.tsv:32` was edited inline rather than "appended", and `registry/history/20261014T124232Z.json:5` still declares the six-verdict `verdict_vocabulary` with no correction. The latter are dated receipts that must not be rewritten, and `corpus/knowledge/alias-endpoint-normalization.md:55` references "the binding verdict vocabulary" without a round-16 append but makes no loading claim. Advice: scope the clause to prose documents and state that immutable receipts are exempt; accept inline machine-header edits.

## Clause atoms that are genuinely enforced (confirmed)

- Pinned cite is exact: `sources/pins.json` locates `middleware_server_state_block {start:307,end:328}`, the saved file digest matches the pin, and `:354` (state) precedes `:357` (API key) in `server-http.cpp`.
- Literal stub matrix through the probe CLI: `check.py:273-278` invokes `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1`; `--port` mode only.
- Frozen-red/repaired-green/changed-set claims: runs 1-2 independently reproduce 55/17 with failed == the 17 loading rows, 72/72, and changed triple set == the same 17; the directional/breadth/exits predicates are in `measure.py:379-390`, and `verify_frozen` checks the frozen sha256 against both `manifest.json` and the `20e392e:tools/kama-probe.sh` git blob; run 11 re-baselines the post-integration bytes at 72/72.
- Reject "widened to any 503 / any `unavailable_error` / a substring" is load-bearing: run 4's mutation fails 23 rows (`Overbroad503.nginx-html-503`, `…no-slot-available`, `…lowercase-loading`, `…code-string`, all `NearMissTriple` code/message variants, auth-adjacent `ForeignControls` rows).
- Reject "/health or / is used as the trigger" is behaviourally covered by `LoadingRace`: `HealthExplicit404`, `HealthUnlisted`, `HealthConnClosed` still expect `MODEL_LOADING`, and `InverseHealthLoadingModelsOk` expects `MODEL_OK`; a health-gated implementation fails these.
- Reject "the python3 precondition is unstated" is false today: stated at `tools/kama-probe.sh:30-36` and `SKILL.md:522`, and run 8 proves the fallback fails closed (17 failures, never a false MODEL_LOADING green).
- Reject "router mode, sleeping, other engines or other builds are claimed" is handled as prose limits (`endpoint-identity.md:200-215`, `llamacpp-loading-lifecycle.md:69-78`); it is not gateable from one envelope, and no gate claims it.

## Residual risk and verification gaps

- `measure.py` was not executed (assignment forbids it); the directional result for run 6 is an emulation of its pre-integration predicate on two real `check.py` runs over the reduced matrix, and the post-integration breadth pin is verified by recomputing its digest (run 12), not by running it.
- Mutation probes are `/tmp` copies made from `tools/kama-probe.sh` sha256 `6edd3c4c…`; that file's mid-review diff is comment-only (current sha `36b64978…`, run 11 green). They show gate sensitivity, not lane-probe behaviour. No lane file was edited; `/tmp/kama-r16-ReviewQualityKq19` is removed after writing.
- Deletion coverage was tested for the four reject families only; further absent-family combinations (including a matrix with zero loading rows) were not run, though `bool(loading_names)` shows measure.py would fail the zero-loading case.
- No `lsp` tool was mounted in this session, so caller/definition checks were done by full-function reads plus execution of the gates rather than semantic references.
- C2's live receipt and llama.cpp startup were out of scope; I started no server and did not probe 8080/34113.

Installs: none. No pacman/uv/npx transaction was run.
