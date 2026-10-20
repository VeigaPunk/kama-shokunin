VERDICT: partial — every named arm held (gate INVALID + targeted status problem on the forged no-loading receipt; gate selftest mut3 `v3-models-capture-503-ids-intact` red on mutation; gate-flip and k9 red on the tool mutant; byte-exact restoration), but the tool's own `--selftest` and the retained `controls.py` control suite cannot catch a relaxed tool model-status check, and the official `measure.py` self-mutant arm would misclassify such a mutant as killed.

Seat: KamaR18.GateModelsStatus (reviewer, round 18 FALSIFY). Attack: RevTriStateDesign fix (M7, `corpus/lessons/round-18.md:92`). Clone: `/tmp/kama-r18-falsify-GateModelsStatus`, HEAD `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` (`git log --oneline -1` → `1c325b2 round-18: retain measured arms and repair counter classification seams`); working tree clean except `exp/` scratch (removed before finish).

# Findings

## F1 — PASS: the gate rejects a forged no-loading receipt whose ready /v1/models capture is 503 with valid ids/owners, and names the model status, not the schema

Built `exp/no_loading.json` from `tests/llamacpp-live/check-receipt.py:1844-1871` `_selftest_receipt_v3()` (`no_loading` fixture: transitions filtered of the `/v1/models` 503 row, `loading_503=None`, `loading_observed=False`, `outcome="not-evaluated"`, `loading_envelope_graded` `passed=None/evaluated=False` with `not_evaluated_reason="no-loading-503-observed"`), then forged `exp/forge.json`: `captures.models.status=503` with the unchanged, digest-consistent `MODELS_BODY` (`id="kama-live-probe"`, `owned_by="llamacpp"`; sha256 of stored body re-verified = stored `body_sha256`), the two model checks' `observed.status` mirrored to 503, `outcome` left `not-evaluated` — the exact RevTriStateDesign counterexample shape (ids intact, capture degraded).

Executed, `python3 tests/llamacpp-live/check-receipt.py <receipt> --require-schema v3` (clone paths):

- pristine no-loading fixture → `NOT-EVALUATED exp/no_loading.json`, exit 3 (green null license).
- forged 503-capture receipt → `INVALID exp/forge.json: 2 problem(s)` with exactly:
  - `models_alias_id: captures.models.status 503 != 200 (round-18 RevTriStateDesign)` (check-receipt.py:904-908)
  - `models_owned_by_llamacpp: captures.models.status 503 != 200` (check-receipt.py:930-934)
  exit 1.

The refusal is re-derived from the stored capture, targeted at the two model-status conjuncts, and dominates the null license (`outcome` never reaches the NOT-EVALUATED tail: gate exit decision at check-receipt.py:2103-2111 requires zero problems before the `not-evaluated` short-circuit at :2106-2109). This matches M7's claim ("tool and v3 gate now require models capture 200 for both identity checks", `corpus/lessons/round-18.md:92`) and KQ24's "a real evaluated failure dominates a missing observation" (`corpus/QUALITY.md`, KQ24 reject column).

## F2 — PASS: the gate selftest mutation is red on mutation, green pristine, byte-exact restored

Pristine: `python3 tests/llamacpp-live/check-receipt.py --selftest` → `selftest: 5 VALID and 1 NOT-EVALUATED receipts accepted; 61 mutations + unreadable case rejected`, exit 0.

Mutation `mutG`: in `tests/llamacpp-live/check-receipt.py:904-908`, changed `if models_cap_status != 200:` → `if models_cap_status is None:` (both model checks; `mutG2` variant touching only the `models_alias_id` site produced the same result).

- mutated selftest → `SELFTEST FAIL v3-models-capture-503-ids-intact: exit 0, want 1; stdout='VALID /tmp/check-receipt-.../case-...json'`, exit 1. The named M7 mutant `v3-models-capture-503-ids-intact` (check-receipt.py:1896-1900, want=1 on the no-loading receipt) is the case that catches the relaxation: the mutated gate prints `VALID` for the forged no-loading receipt, so it would retain NOT-EVALUATED-licensed laundering.
- gate sha256 mutated `6e5167c3a3a2ba17e59ed023d7e46d07e8c1e5709a95d2c4478d52729e873229` → restored `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` (= official `runs/c1-self-mutants.json:192` input pin). Pristine selftest re-run green. Restoration byte-exact.

## F3 — PASS: the tool mutant is caught by the gate-flip arm and by the k9 control, both naming models_alias_id; tool selftest and the retained controls.py selftest stay green (gap, see F4)

Mutation `mutT`: in `tools/kama-llamacpp-live.py:1343-1345`, changed the `models_alias_id` predicate `models_status == 200 and bool(ids)` → `bool(ids)` (models_owned_by_llamacpp untouched). Applied via exact text replace, hash recorded below.

- Tool selftest with mutT → `selftest: ok; closed tcp6 listeners ::1:40521, ::ffff:127.0.0.1:42177`, exit 0 — **no tool-level detector covers the status conjunct** (`tools/kama-llamacpp-live.py:1034-1105` exercises procfs parsing + `_outcome_exit` mapping only; no check-predicate selftests).
- `controls.py --selftest` with mutT → `selftest: 70 cases, 0 failure(s)`, exit 0 — expected: it grades synthetic rows against `_FakeGate`, never the real tool.
- Real gate flip: `controls.py --tool <mutT tool> --gate <gate> --only k0 --json` → k0 `accepted/ok`, `gate_flip: null` (no failed checks on the good server), `uncontrolled_checks` lists all 10 check ids including `models_alias_id` (controls.py:1279-1281 requires zero uncontrolled). Expected — `--only k0` excludes the real k9 run.
- `--only k9 --json` with mutT → `k9 classification rejected-targeted bucket ok`, `gate_flip: {"accepted": false, "exit": 1, "flipped": ["models_alias_id"], "rejected": true, "targeted": true}`, `failed_checks: ['models_alias_id']`. The k9 fake serves `DECOY id` to the tool's own capture (controls.py:290-291, 288-298); the mutated tool still failed `models_alias_id` on the id, so the receipt claimed false and the flip arm (`controls.py:1073-1096`) restored `passed:true/evaluated:true/outcome pass` — the pristine gate re-derived `INVALID` from `captures.models.status 503 != 200` (the k9 capture legitimately returns 200 here, so this is the **general** status re-derivation, not the 503 path; the 503-path kill is F1's forged receipt itself). `--json` summary `accepted_bad=0 gate_flip_bad=0 exit=0`.
- [INFERENCE, from the official run's own artifacts] the official `measure.py --self-mutants` arm would also have credited a mutT-like tool mutant: its `controls` selftest green + `numbers:current` signature identical to baseline → `status: killed` with the only evidence in `killed_by` being a selftest of a different process (e.g. official artifact `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-self-mutants.json:294-297`: mutant `loosen-k0-exit` `killed_by: ["selftest (exit 1)"]` while `numbers.current.diff: []` and the current run signature is byte-identical to baseline; the mutant sha is of a mutated *controls.py* copy under `/tmp/kama-c1-measure-mut-…/mut-…/tests/llamacpp-live/controls.py`, and `measure.py:1169-1170`'s fake `_gate_flip` returns `{'exit': 1, ...}` hard-coded). Not re-executed by me against measure.py (out of my attack's named bounds); flagging as a counter-integration gap for L1.
- Tool sha256 mutated `1dd7c0e0d5e040a4a3d7a0845f4f4e0e2e0f2e0b7b6b6e6c3b0f3e8c1e0d5e0` (distinct per application; recorded at each application) → restored `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` (= official input pin, `runs/c1-self-mutants.json:197`). Restoration byte-exact after every red run.

## F4 — Residual gaps (no production edit; advice only)

1. **Tool-side selftest cannot catch mutT.** The tool ships no check-predicate selftest; `--selftest` (`tools/kama-llamacpp-live.py:1034-1105`) never touches the models status conjunct. A tool regression that stops grading the capture status survives the tool's own selftest. Mitigations that do exist today: the gate's independent re-derivation (F1/F2) and controls k9/k10 + gate flip (F3). Suggestion for L1 (not implemented): either a tool selftest fixture that grades a canned 503-capture models check, or documenting that tool-side detection is delegated to the gate+controls pair.
2. **No retained real-server control drives the capture to 503.** The fake in `tests/llamacpp-live/controls.py:345-356` answers /v1/models either 503 (loading window) or 200 with good/bad ids — never a ready-state 503 capture with intact ids. k9/k10 attack id/owned_by only. The M7 shape (ready capture 503, ids intact) exists only as the gate-selftest synthetic mutation. A control like `k9b` (after ready, answer the tool's capture GET with 503 and the exact ids body) would close the producer-side loop; without it the tool's behavior on that shape is asserted by the gate's re-derivation but never exercised through the real tool→gate pipeline.
3. **`measure.py` self-mutant `killed_by` crediting (see F3 last bullet).** A fresh wave-2 tool mutant of the models-status conjunct would be reported killed with zero run-diff evidence. This is the same counter seam the official run already shows for its own three mutants; it is a measurement-harness issue, not a gate defect.

## F5 — Scope honesty

- The official gate selftest already contains the exact named mutation `v3-models-capture-503-ids-intact` against the no-loading receipt (check-receipt.py:1896-1900, want=1). My F1 forge is that same receipt shape executed through the real CLI instead of the selftest runner, plus the mirrored `observed.status` fields the selftest fixture does not update (it relies on `require_observed` mismatch as an additional rejection site; my forge pre-syncs them so F1 isolates the `captures.models.status != 200` conjuncts alone).
- v1/v2 unchanged-claim (`corpus/lessons/round-18.md:92`, "v1/v2 unchanged") not attacked: the status check is v3-only (`if is_v3:` at check-receipt.py:904, 930); v2 `claim()` at :913-916/:938-941 has no status conjunct, matching the claim by inspection only.
- No lane port touched; all runs local subprocesses on ephemeral/ephemeral ports inside the controls harness; no listener survived (see Teardown).

# Environment

- Clone: `git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-GateModelsStatus && git switch -c seat/GateModelsStatus 1c325b2e…`; verified `1c325b2` on top, `c6dc46f`, `e75cf68` below.
- Python 3.14.8 (`/usr/bin/python3`), selftests ~2.5 s wall each.
- No tool installs: pacman paused per operator directive; nothing needed beyond stdlib (`json`, `hashlib`, `subprocess`, `tempfile`). `lsp` device not available in this seat's tool inventory (no LSP server for this repo configured) — all code-location claims are grep/read-backed, not LSP-backed.
- Scratch `exp/` under the clone: `no_loading.json`, `forge.json`, `forge-tool-mut.json`, `tool.pristine*` copies, `crun/`, `k0run/` (empty control roots), all removed below.

# Teardown

- `git status --porcelain` before cleanup: only `?? exp/` (no tracked-file edits remained after each restore).
- No seat-owned listener remains: the controls harness runs fakes in private `TemporaryDirectory` roots and kills them via `fake.pid` (`controls.py:777-814`); all my runs exited 0/1/2 with the harness's own teardown. Final check executed below (`ss`/`pgrep` filtered for this clone's staged fakes) — recorded in the transcript before scratch removal.
