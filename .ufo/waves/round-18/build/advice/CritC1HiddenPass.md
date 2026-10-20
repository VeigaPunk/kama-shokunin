VERDICT: partial — the zero-observation 1→2 reclassification is KQ21-mandated (R4) and not a weakening *if* the null license is re-derived from evidence, fail dominates null, null is id-scoped, and counting keeps a third class; two required falsifiers are absent from the declared control list, and the tool's exit-3 model-digest path collides with the new gate-3 semantics.

# CritC1HiddenPass — is exit-1→exit-2 a hidden pass?

Axes: operability (exit-code truthfulness), calibration (does "not evaluated" launder a bad run).
Scope: frozen `tools/kama-llamacpp-live.py`, `tests_llamacpp-live_check-receipt.py`,
`tests_llamacpp-live_controls.py` (= commit `e75cf680`); QUALITY.md KQ21; round-17
verifier-spotcheck §Decision/R4; round-17 lesson §Kept as debt.

## 1. The move is a re-classification, not a weakening — under conditions

**Current (frozen) behaviour:** `loading_envelope_graded` passes only when
`receipt.get('loading_observed') is True and loading_envelopes_all(bodies) is True`
(frozen tool `tools_kama-llamacpp-live.py:1347-1348`), and the exit is
`0 if all(...passed is True...) else 1` (lines 1376-1378). A zero-observation run
records `passed: false` and exits 1 — it *asserts a refutation of a property that was
never exercised*.

**Why 1 is the wrong class, not just the wrong verdict:** the round-17 closure observed
the trade directly — under 32x load a healthy run captured zero 503s and still
"v2 refuses to certify a property it did not observe, which is what KQ21 requires"
(`corpus/lessons/round-17-verifier-spotcheck.md:21-22`), but the same ruling named the
defect: "zero observation should be could-not-evaluate (exit 2), not failed (exit 1)"
(line 24-25, routed R4 at line 234). The lesson's own kept-debt entry agrees:
"the rule is fail-closed by design (KQ21 rejects vacuous passes); the honest next move
is to classify zero observation as could-not-evaluate (exit 2) rather than a failed
check" (`corpus/lessons/round-17.md:251-255`).

**Why it does not have to be a hidden pass:** neither tool exit 2 nor gate exit 3 is 0.
Every `exit != 0` consumer still counts the run as *not passed* — the reclassification
preserves rejection of certification while fixing the reason class. The pytest
precedent (sibling recon, `.ufo/waves/round-18/build/advice/ScoutPytestExitCodes.md`)
confirms the convention: "No tests were collected" = exit 5, a *separate non-zero*
status, and pytest's exit-1 text scopes failure to runs where "Tests were collected
and run". Zero-observation → a distinct non-zero class is the correct upstream-shaped
fix, not a pass channel.

So: improvement requires that "not evaluated" stays a *non-pass, non-acceptance*
everywhere — tool exit set, gate exit set, controls predicates, and the before/after
counts. The failure modes below are all ways the move can quietly become a hidden pass.

## 2. What must hold for improvement with no harm

### H1 — the null license must be re-derived, never claimed
The strongest counterexample to "this is safe": take a K2-class receipt where the
server *did* emit 503s (a `transitions` row with `status: 503` carrying a non-exact
body), then rewrite the receipt to `passed: null`, `evaluated: false`,
`not_evaluated_reason: "no-loading-503-observed"`, `loading_observed: false`, and
delete `loading_503`/`loading_503_bodies`. If the v3 gate trusts the declared null,
it exits 3 (NOT-EVALUATED) on a run that genuinely failed — the reclassification
channel launders a real defect into the benign class.

The frozen gate already has exactly the re-derivation needed and it must be ported
into the v3 path verbatim in substance:
- `loading_observed != (loading_503 is not None)` → bad (frozen gate
  `tests_llamacpp-live_check-receipt.py:445-446`);
- `loading_observed false but transitions record a status-503 row` → bad
  (lines 441-450);
- v2's "no loading_503 body stored, nothing graded" (lines 913-915) must become, in
  v3, *the entry to the licensed-null path* — still INVALID if the stored evidence
  contradicts `no-loading-503-observed`, and INVALID if the reason token or
  `evaluated:false` marker is absent/wrong.

**Falsifier F-launder:** forged v3 receipt = K2 evidence + declared null as above →
must exit 1 INVALID. The declared forged-control list (self-declared v1, extra argv,
non-exact 503 in transitions) does **not** include this case — it is the single most
important missing control.

### H2 — fail must dominate null, on both the tool and the gate
The contract says tool exit is 2 only for "any null check with none false". If the
implementation orders `any_null → 2` before `any_false → 1`, a run with a real failure
*and* no loading window (health-degraded server that was already ready at first poll)
exits 2 — a real observed failure reclassified as could-not-evaluate. Same on the
gate: "the only shortfall a legitimately-null check" means INVALID whenever any
re-derived check is false even alongside a legit null.

**Falsifier F-precedence (missing from the declared list):**
- forged v3 receipt: `probe_mismatch.passed: false` + legitimately-null
  `loading_envelope_graded` → gate must exit 1, never 3;
- live: a fake that is health-degraded (K1 shape) *and* emits zero loading 503s →
  tool must exit 1, receipt outcome must be "fail" not "not-evaluated".
Neither the retained bad controls (each flips its one named check) nor the
zero-loading good control exercises the mixed state; the precedence ordering is
currently unfalsified.

### H3 — null is licensed for exactly one check id + one reason token
`passed: null` on `probe_mismatch`, or `evaluated: false` on `health_ready`, or
`passed: true` + `evaluated: false` on anything, must each be INVALID. A gate that
admits null generically converts every per-check failure into "not evaluated".

**Falsifier F-scope (missing from the declared list):** receipt matrix mutating
`passed`→null / `evaluated`→false / dropping `evaluated` / wrong
`not_evaluated_reason` on each of several check ids → INVALID each. Note the frozen
gate's `passed is not a boolean` rejection (lines 647-649) is the *v2* contract; the
v3 path needs its own combination table, and a v3 receipt run under
`--require-schema v2` must still hit the v2 boolean demand (INVALID), never silently
take v3 rules. [INFERENCE: the schema dispatch is by declared schema string; a
v3-doc-as-v2 fall-through would be caught by the self-declared-v1 control only in the
down direction — the up direction needs its own case.]

### H4 — the gate-flip arm must reach the new state
`_gate_flip` (frozen controls `tests_llamacpp-live_controls.py:463-490`) flips only
`passed is False` rows (lines 471-474), and `_failed_checks` collects only
`passed is False` (lines 431-438). For the zero-loading good control `failed` is
empty → the flip arm returns None → the *new* tri-state gets zero gate-flip coverage.
KQ21's arm requires the gate to reject a receipt "with only the failing check flipped
to passed" (`corpus/QUALITY.md:121-122`); the null analogue is flipping `null→true`,
which the gate must still refuse to certify as VALID (evidence shows no 503 → at best
NOT-EVALUATED, never VALID).

**Falsifier:** flip the legit-null `loading_envelope_graded` to `passed: true` →
gate must not exit 0 (expect 3 if NOT-EVALUATED, 1 if treated as claim-mismatch; the
contract should pin which). If the flip arm is not extended to `None`, R7's
MutControlsSelf class re-opens for exactly the new code path.

### H5 — counting must carry a third class, or the lane re-scores its own fix as harm
The bad-control predicate is `tool_exit != 0 or gate_exit != 0` (frozen controls
lines 557-559) — correct for bad controls. If the zero-loading *good* control is
scored by the same "nonzero = rejected" predicate, it lands in `good-rejected` and
the round reports a regression it just introduced; if it is scored by K0's
`exit == 0` predicate it is either falsely failed or, worse, silently re-bucketed.
The zero-loading control needs its own arm asserting exactly tool 2 + gate 3, and
`measure.py` needs a `not_evaluated` bucket distinct from `accepted`,
`good-rejected`, and `misclassified`. A zero-observation run landing in `accepted`
or `good-rejected` *is* the harm signature the before→after counts exist to catch.

### H6 — the tool's undeclared exit 3 collides with gate 3
Frozen tool `tools_kama-llamacpp-live.py:1018-1023`: model-digest mismatch
"refusing to launch" → `return 3`, no receipt. The v3 contract enumerates tool
exits 0/1/2 only, and the gate's new 3 means NOT-EVALUATED. Keeping tool 3 both
violates the declared exit set and creates a semantic collision: a hard integrity
refusal misreadable as the benign "nothing to grade" class by any consumer keying on
3. Fold it into 2 (setup error; stderr already names the reason). [INFERENCE that any
external consumer exists; the collision is internal-visible regardless.]

### H7 — `_check(..., None, ...)` must not silently re-become False
The constructor is `'passed': bool(passed)` (frozen tool line 832). Passing `None`
through it yields `passed: false` — the *old* verdict and a quiet no-op of the fix,
still exiting 1. Tri-state needs a constructor path that preserves `None` and adds
`evaluated`. A mutant leaving `bool()` in place reproduces the frozen exit-1 exactly;
the zero-loading good control expecting exit 2 is the falsifier (it must assert the
receipt field `passed is null`, not just the process exit).

### H8 — `bodies_dropped` edge must not take the no-observation reason
`loading_envelopes_all` returns None both when no 503 was seen *and* when bodies were
dropped/capped (`tools_kama-llamacpp-live.py:560-567`, `231-236`). If `loading_observed`
is true but the stored bodies were all dropped, the check must not claim
`no-loading-503-observed` — observation happened; the evidence was truncated. That
state should be INVALID or a separately-reasoned not-evaluated, never the licensed
null. [INFERENCE: contract fixes the reason token to the zero-503 case only; the
dropped-bodies case needs an explicit rule.]

## 3. The consumer-side condition (the residual risk that remains by design)

Tool exit 2 now carries three meanings — setup-error, internal-fault, not-evaluated —
distinguished only by receipt `outcome` and `setup_error`/`internal_fault`. A
retry-on-2 consumer is unharmed; an alarm-on-2 consumer now alarms on healthy
servers; a consumer doing `==1` for failure *misses* a class it previously caught.
That last one is the actual hidden-pass direction: `bad run` → old exit 1 → now exit 2
is safe only because nothing observed can be "bad"; but a consumer treating 2 as
"skip" for *all* classes also skips setup errors that were already class-2 before.
Net: no new hiding for behaviour that was previously detected — the only new benign
class is attached to a state (zero observation) that was previously *falsely
failed*. Harm is confined to consumers that never read the receipt; `outcome` must
therefore be treated as a graded, re-derived field, not trusted text — a forged
`outcome: "pass"` over a legit-null receipt must be INVALID.

## 4. Falsifier summary (named attacks the round must survive)

| ID | Attack | Required result | Covered by declared controls? |
|---|---|---|---|
| F-launder | real 503 evidence + declared null | gate 1 INVALID | **no — add** |
| F-precedence | false check + legit null (forge + live) | tool 1 / gate 1 | **no — add** |
| F-scope | null/`evaluated:false`/missing `evaluated` on other ids | INVALID each | no — add |
| F-flip-null | legit null flipped to `passed:true` | never gate-VALID | needs flip-arm extension |
| F-consistency | `passed:true`+`evaluated:false`, bad reason token, forged `outcome:"pass"` | INVALID each | no — add |
| F-zero-good | zero-loading good server | tool 2, gate 3, receipt `passed:null` field (not `false`) | declared ✔ |
| F-tool-exit3 | model-digest refusal still exits 3 | off-contract; fold to 2 | no — fix |
| F-schema-floor | v3 doc under `--require-schema v2` | INVALID via v2 boolean rule | partial (self-declared v1 covers only the down direction) |

## 5. Answer to the assigned question

Reclassifying zero-observation from exit 1 to exit 2 is **not** a weakening of
detection — it removes a false failure and matches KQ21's reject column ("an
unobserved state passes vacuously") and the closure's R4 routing — **provided**
H1–H5 hold: the null license is re-derived from `transitions`/`loading_503`/
`loading_observed` consistency, false dominates null, null is restricted to the one
check + one reason, the flip arm reaches null, and every counting surface keeps the
third class non-accepting. The falsifier is a receipt-level laundering attack: any
declared `passed:null`/`evaluated:false`/`not_evaluated_reason`/`outcome` claim the
gate takes on trust converts the fix into a channel that reclassifies genuinely bad
runs as "not evaluated" — a hidden pass in everything but name. The declared forged
controls test argv, schema floor and transitions exactness but none of the
null-declaration conjuncts; that is the smallest safe correction — add the
F-launder and F-precedence cases at minimum.

## Limitations

- Read-only seat; no code executed, no ports bound, no lane files written.
- The v3 tool/gate/controls do not exist yet (`.ufo/waves/round-18/build/out/` is
  empty at review time); H-items are contract-level requirements the delivery must
  satisfy, not observed defects.
- `measure.py` is not yet written (`.ufo/waves/round-18/c1/` empty); H5 is stated
  against its declared counting contract.
- All quotes are verbatim from the cited paths; inferences are marked.
- Installs: none.
