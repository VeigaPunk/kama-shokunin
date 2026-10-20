VERDICT: confirm — v1/v2 gate branches survive the frozen→current rewrite byte-equivalently on the recorded legacy oracle and forged-boundary probes; no accidental v1/v2 semantic shift found.

# RevGateDelta — reverse intent review of gate (check-receipt.py) frozen→current

Seat: KamaR18.RevGateDelta (leaf, no subagents). Scope: `tests/llamacpp-live/check-receipt.py`
(the receipt gate), frozen comparator `.ufo/waves/round-18/frozen/tests_llamacpp-live_check-receipt.py`
(captured at `e75cf680b53484a61709ee1b2787d8dbc6419f74`, frozen/manifest.json "revision"), oracle =
five legacy receipt pairs (`legacy-frozen-N`/`legacy-current-N`, N=0..4) plus `legacy-wrong-probe-pin`
under `.ufo/waves/round-18/runs/`. Assignment: trace frozen→current gate changes; identify every
v1/v2 branch whose semantics may have shifted accidentally; check code against the recorded legacy
oracle.

## Method and environment

- Isolated clone `/tmp/kama-r18-falsify-RevGateDelta` = `git clone -q <lane>` then
  `git switch -c seat/RevGateDelta 1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (HEAD verified
  `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`; parent `c6dc46f round-18: classify missing
  observations…`; grandparent `e75cf68` = frozen capture revision). All runtime checks ran inside
  this clone only; scratch artifacts created inside the clone were deleted; `git status --short`
  clean at finish. No jj/git writes in the lane. No tool installs (none needed — nothing added or
  upgraded; pacman untouched).
- Frozen vs current diffs: `diff` = 39 hunks gate (1136 lines), 51 hunks tool (1002 lines);
  probe/matrix unchanged (`.ufo/waves/round-18/runs/probe-matrix-identity.json`: all `same: true`,
  `tools/kama-probe.sh` before=after=`36b64978ee3a…`).
- Every version-branch site in the current gate was enumerated: `is_v3`/`is_v2` occurrences at
  lines 268–270, 280, 471–477, 499, 528–531, 548–551, 557, 605, 731, 789, 821, 829, 880, 904, 930,
  954, 976, 1005, 1041, 1054, 1067, 1102, 1118, 1136, 1142, 1177, 1337, 1346, 2088–2099
  (`check-receipt.py` in the clone). Shared code = everything not under `is_v3`/`is_v2`.

## Finding inventory

**F-1 (confirmed, no defect). All 25 legacy oracle cells reproduce.** Official
`commands.json`: legacy-frozen-0..4 and legacy-current-0..4 all `exit=0 want=0 ok=true`, plus
`legacy-wrong-probe-pin exit=1 want=1 ok=true`. Re-executed in the clone with each receipt's own
recorded probe pin: frozen v1 pair (receipt.json, receipt-frozen-probe.json) exit 0 VALID both
gates; v2 trio (round-17 receipt-1/2/3.json) exit 0 VALID both gates; wrong-probe-pin forged
request exit 1 `INVALID` both. No verdict changed frozen→current on any recorded oracle input.

**F-2 (confirmed). v1/v2 branches are textually unchanged in shared code.** The only shared-block
edits are additive `is_v3` conditionals:
- `check-receipt.py:1054` `if not is_v2 and "teardown_exited" in by_id:` — identical text to
  frozen `:834` (v1-only re-derivation).
- `check-receipt.py:1142` `if is_v2 and not is_v3 and "loading_envelope_graded" in by_id:` — the
  `not is_v3` clause is provably redundant (`is_v2 = schema in (V2, V3)` at `:270` excludes v3),
  added for clarity; v2 behavior identical to frozen `:908`.
- Probe-row checks `check-receipt.py:700–748` are byte-for-byte the frozen `:640–669` block
  (MODEL_OK/exit-2 coupling, drift polarity, MODEL_MISMATCH reasons, expected_model_id,
  declared-endpoint). New `is_v3` blocks (:731–737) sit beside, not inside, them.

**F-3 (confirmed). `--require-schema` is purely additive and floors are minimum-bound.**
Frozen gate has no such flag (argparse exit 2 `unrecognized arguments` — executed). Current:
`check-receipt.py:2088–2096` floors `{"v1":1,"v2":2,"v3":3}`, rejects only `version < minimum`.
Executed matrix on the current gate: r16 v1 receipts `v1:0 v2:1 v3:1`; r17 v2 receipts
`v1:0 v2:0 v3:1`; r18 v3 receipt `v1:0 v2:0 v3:0`. A v2 receipt correctly passes the v1 floor
(minimum semantics, not equality). Official legacy runs passed no flag, so recorded oracle cells
are unaffected.

**F-4 (confirmed). v1/v2 ignore all v3-only fields — verified by forgery.** Injected into real
legacy receipts: `outcome` ∈ {not-evaluated, fail, setup-error}, `evaluated:false` on checks,
tampered `source_binding`, `internal_fault` — frozen and current verdicts identical in every case
(v1: all exit 0; v2: exit 1 where a real v2 check fails, exit 0 otherwise). The v3-only branches
(outcome re-derivation `:1346–1368`, `internal_fault` mirror `:280–286`, source-binding
validation `:829–831`, `require_observed` calls) are all gated on `is_v3`.

**F-5 (confirmed). v3-only tightenings do not leak into v1/v2.**
- models-capture status 200: enforced only under `is_v3` (`:904–912`, `:930–940`); executed probe
  with `captures.models.status=503` on the v1 and v2 receipts → both gates exit 0 VALID (frozen =
  current); same mutation on a real v3 receipt → exit 1 with four problems including
  `models_alias_id: captures.models.status 503 != 200 (round-18 RevTriStateDesign)` — M7's
  counterexample is real and v1/v2 are untouched, as the lesson's M7 row states ("v1/v2
  unchanged").
- loading_503.path: `:528–531` — v3 accepts only `/v1/models`; v1/v2 keep `/v1/models|/health`.
  Executed: v1 receipt with the 503 moved to `/health` (loading_observed=true preserved) → VALID
  on both gates.
- loading-503 transition-body grading, body_sha256/repeats/truncation, `loading_503_bodies`
  coverage and `loading_bodies_dropped` re-derivation: all inside `is_v3` (`:557–567`,
  `:1177–1335`). Executed: v1 receipt with a non-exact 503 transition body → VALID on both gates
  (v1 never graded transitions; unchanged).
- `require_observed` (`:849–857`) is v3-only everywhere it appears.

**F-6 (confirmed). Tri-state (passed null + evaluated) is v3-only.** `:790–825` — the legacy
`passed is not a boolean / passed is false` checks now live in the `else` branch of
`if is_v3:`; a v1/v2 receipt with `passed:null` still rejects identically (frozen and current
share the else path; frozen executed on the same receipts gives the same verdicts). Legacy forgery
F-4 confirms no behavioral delta.

**F-7 (confirmed). NOT-EVALUATED exit 3 is v3-schema+outcome-gated.** `:2105–2109` requires
`schema == RECEIPT_SCHEMA_V3 and outcome == "not-evaluated"`. Executed: forged
no-loading variant of receipt-1 (transitions stripped of the /v1/models 503, envelope fields
zeroed, check nulled with `no-loading-503-observed`) → exit 3 `NOT-EVALUATED`; v1/v2 receipts
with `outcome:"not-evaluated"` injected → still exit 0 (F-4); schema-forged
`kama-llamacpp-live/v9` → exit 1 (never 3). No legacy path can reach exit 3.

**F-8 (confirmed, non-blocking observation). v3 label is not a producer proof.** A round-17 v2
receipt relabeled `kama-llamacpp-live/v3` + `outcome:"pass"` + `model.arg` added +
`observed.status:200` on the two models checks + `evaluated:true` on all eleven checks validates
through the current v3 gate (exit 0, 0 problems — executed; the same file under the frozen gate
exits 1 on the v3 schema string). This is not a v1/v2 shift: it is inherent to schema-label
upgrades (the gate cannot authenticate which producer wrote the bytes; `--expect-tool-sha256`
pins the recorded tool hash, and a v2-era receipt records the v2-era tool hash, so official
pin-carrying invocations of such a forgery would still fail on tool-pin mismatch). Recorded here
so L1 knows the v3 floor rejects schema strings, not v2-produced content.

**F-9 (confirmed). Tool-side delta does not alter v1/v2 gate semantics.** The producer tool diff
(swallowed `Exception`→`BaseException` receipts via `_record_internal`, `_outcome_exit`
pass/fail/not-evaluated/setup-error mapping, tcp6 word-reversal parser `_tcp6_is_loopback` +
`_proc_listener_inode` replacing the suffix-prefix heuristic, `loading_503` capture narrowed to
`/v1/models` at tool level, `--model/--model-sha256` now optional-with-selftest) emits only v3
receipts (`SCHEMA = 'kama-llamacpp-live/v3'`, tool diff `@@ -47,7 +46,7 @@`). The gate's legacy
branches consume recorded evidence only; producer changes cannot retroactively change what the
frozen-oracle v1/v2 cells mean. Tool selftest in the clone: `python3 tools/kama-llamacpp-live.py
--selftest` exit 0, `selftest: ok; closed tcp6 listeners ::1:35353, ::ffff:127.0.0.1:41181`
(ephemeral loopback binds closed before return; both addresses recognized as loopback).

**F-10 (confirmed). Gate selftest parity.** Executed in the clone: current
`check-receipt.py --selftest` exit 0 — `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted;
61 mutations + unreadable case rejected` (adds the four require-schema cases and 22 v3 mutations
to frozen's `2 valid; 39 mutations + unreadable case all rejected`, which also re-executed exit
0). The frozen selftest's v1/v2 cases still pass against the current code paths (shared block).

**F-11 (confirmed). Controls harness on the clone's tool+gate: zero uncontrolled cells.**
Executed `python3 tests/llamacpp-live/controls.py --tool tools/kama-llamacpp-live.py --gate
tests/llamacpp-live/check-receipt.py --probe tools/kama-probe.sh --json` in the clone (fake
llama-servers only, no real model/binary): exit 0, `accepted_bad=0 good_rejected=0
misclassified=0 gate_flip_bad=0 inconclusive=0`, 23 controls, `gate_flip_arms=17`,
`receipt_schemas=['kama-llamacpp-live/v3']`. k16 = not-evaluated (tool exit 2 / gate exit 3),
k19 = rejected-targeted with `schema 'kama-llamacpp-live/v1' is below --require-schema v3` —
the schema floor's red arm is exercised. k7 `rejected-untargeted` matches its declared
expectation (ready-timeout setup error). Runtime ~21 s, no ports beyond per-control ephemeral
loopback binds inside the harness child processes (all reaped; `ss -ltnp` shows no
llama/RevGateDelta listener at finish).

## Limitation

- No real-server run was launched from this seat (the official live receipts were re-validated
  read-only with full pins above: all three exit 0 VALID under `--require-schema v3` with the
  recorded four-pin set recomputed from installed read-only artifacts). First-SIGTERM window,
  models-503 live behavior and loading-body dedup live behavior belong to the tool-side review
  (RevToolDelta) and the executor seats.
- The frozen comparator is the round-17 tip (`e75cf680`), not the round-16 original; earlier
  v1/v2 history is outside this round's declared frozen set (frozen/manifest.json lists exactly
  ten files at that revision).

## Verdict rationale

Every v1/v2 branch site is either byte-identical to frozen text or guarded by an additive
`is_v3`/`--require-schema` condition whose legacy path was executed against the recorded legacy
oracle (all 25 cells reproduce) and against forged-boundary probes (outcome/evaluated/source_
binding/internal_fault injection, models-503 capture, /health loading path, non-exact transition
bodies, forged null checks, require-schema floors, exit-3 reachability). No case showed a frozen
vs current verdict divergence on a v1 or v2 receipt. Findings F-1..F-11 are all confirmations;
the single non-blocking observation is F-8. C1's "v1/v2 unchanged" compatibility statement is
consistent with observed code and executed behavior.
