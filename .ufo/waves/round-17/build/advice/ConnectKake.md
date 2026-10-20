VERDICT: confirm — health-body grading is kama's for local endpoints, kake's for remote surfaces; no contested implementation, one reusable convention pair, and C2 must keep the liveness/identity split explicit.

# ConnectKake — overlap scan (kake ↔ kama C1/C2)

Round 17, BUILD wave, advice only. Read-only in both lanes; nothing written
outside this file. Kake sources were the three permitted files
(`SKILL.md`, `PROVINCE.md`, `corpus/QUALITY.md`); no kake file was modified.

## Evidence

1. **The boundary is already drawn, and the shared token is `/health`.**
   kake `PROVINCE.md:37`: "`kama` owns local model-serving endpoints; kake owns
   remote web properties." kama `PROVINCE.md:13` claims "liveness/readiness probe
   conventions | `/health`, `/props`, `/slots`". Same word, disjoint objects:
   loopback child vs published property.
2. **The only kake row that is an HTTP service with a health surface is remote
   and has no kake grader.** kake `SKILL.md:28`: "Render web service
   (`ds4cc-marketplace-app`, Docker)" for `app.ds4cc.com`. Neither kake gate in
   `SKILL.md:212` or `:387` names that row, so there is no body expectation to
   merge and kama must not adopt one.
3. **Kama already owns the grading rule in prose; C2 is a tooling gap.**
   kama `SKILL.md:173`: "Process alive; says **nothing** about which model".
   `SKILL.md:252-253`: "**Reading `/health` as identity.** A healthy answer does
   not establish which model is served." C2's repair therefore does not import a
   foreign convention — it makes the existing one fail-capable.
4. **Kake convention A — status is not proof.** kake `SKILL.md:65-66`:
   "Raw `200` is not proof: kimi-pro serves `200 + 5995B preview-404 body`";
   ":66-67": "trust `expect`, not status alone"; ":67": "Trust hierarchy: live
   probe > config fields." C2 `health_ready` is exactly this failure mode: 200
   `{"status":"degraded"}` passes at `tools/kama-llamacpp-live.py:937-939`
   (`checks.append(_check('health_ready', health_status == 200,` …
   `{'status': health_status})`)). C1's `served_model` gap is the same shape one
   layer up: the field is captured (`tests/probe-verdicts/check.py:337`) and
   never compared — `passed` is only verdict/reason/drift/exit (`:340-346`).
5. **Kake convention B — a detector that survives mutations is not a detector.**
   kake `SKILL.md:319-321`: "they passed 12 cross-body swap mutations";
   `:322`: "a `null` marker is worse (foreign-200 serves flip to silent pass)".
   This is the direct prior art for round-16's 5/5 surviving mutants and for C2's
   ungraded evidence: a recorded field with no consuming check is a `null`
   marker in practice.
6. **Kake convention C — a validator names what it cannot prove.**
   kake `corpus/QUALITY.md:16`: "A validator claim names the generating
   mechanism, decodes the literal, and states what it cannot prove".
   Applied to C2: a body-graded `health_ready` proves the ready envelope, not
   weights, identity, or capacity (kama `SKILL.md:173`, `:252-253`).
7. **Kake convention D — counting claims name their population and verdict map.**
   `corpus/QUALITY.md:18`: "Every dead-path or count claim names its population"
   and the command; `:10`: "names the source revision or script digest, exact
   argv, full verdict and exit". Kake's own gate rows carry entry command,
   verdict map, self-test, pinned proof and write scope (`SKILL.md:212`,
   `:387`). C1 `mutants.py` and C2 `controls.py` are this round's counting
   commands and should carry that shape; kama already has an analogous table at
   `SKILL.md:303-306`.

## Contested scope

| Surface | kake claim | kama claim | Disposition |
|---|---|---|---|
| local llama-server `/health` body grading | none | `PROVINCE.md:13`; `SKILL.md:173`, `:252-253` | **kama** — C2's repair belongs here |
| `app.ds4cc.com` Render service | `SKILL.md:28` (property row) | none | **kake** — kama must not probe or grade it |
| status-vs-body semantics ("200 can hide a 404") | `SKILL.md:65-67` | C1 probe-contract property | principle shared; implementations stay in-lane |
| mutation-survival discipline | `SKILL.md:319-322` | C1/C2 fault controls | shared principle, separate suites |
| receipt schema, child lifecycle, SIGTERM/port ownership | none | `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/` | **kama exclusively** |

No file overlap and no competing implementation. Kake is a *convention donor*,
not a scope claimant, on this surface.

## Hand-off — kama must not absorb

- Any remote host/URL check (Render `app.ds4cc.com`, Pages, kimi): kake owns the
  property rows (`SKILL.md:28`); kama's province is loopback endpoints.
- Hosting-platform semantics (soft-404/preview bodies, Pages artifact set, ETag
  meaning): kake (`SKILL.md:65-67`; `QUALITY.md:16`).
- Kake's probe tooling and paths are not executable here: `SKILL.md:58-59`
  marks `~/Projects/webzites/bin/webzites.mjs` absent with a local absence
  annotation. Kama must not cite or import those paths.
- Kama's local fixture lifecycle (child ownership, SIGTERM grace, pdeathsig)
  stays kama; kake must not import it for remote services. [INFERENCE]
- Kake `PROVINCE.md:6` sets the reciprocal rule: "anything outside this domain;
  report cross-domain evidence back to the orchestrator rather than absorbing
  it." Any future local-endpoint finding in kake goes to kama, not into kake's
  gate registry.

## Reusable convention for C1/C2

Grade the literal expectation, not the transport; treat an evidence field with
no consuming check as a deficit, not a pass.

- C2 `health_ready` v2: 200 **and** the parsed documented ready envelope
  (`{"status":"ok"}`), with `documented_by` stating it proves liveness only
  (kama `SKILL.md:173`; kake `QUALITY.md:16`).
- C2 `teardown_exited`: harness-initiated SIGTERM, no SIGKILL, documented
  graceful returncode. Today the predicate is only
  `receipt['teardown']['returncode'] is not None`
  (`tools/kama-llamacpp-live.py:1025-1028`; mirrored at
  `tests/llamacpp-live/check-receipt.py:745-757`). A child that self-exits
  before teardown skips the signal branch (`tools/kama-llamacpp-live.py:663`,
  `if proc.returncode is None:`) and records `sigterm_sent: false` while the
  check still passes.
- C2 `loading_envelope_exact`: promote from field to consuming check, or
  declare it non-graded. `check-receipt.py:420` states it is "a receipt FIELD
  (bool|null), not a check"; a false envelope is only consistency-checked
  (`:421-432`), so a 10/10 gate can carry `loading_envelope_exact: false`.
- C2 `teardown_port_closed`: state the falsifiable claim ("no stranger rebound
  the port after the child exited"), because after `proc.wait()` the kernel
  closes the child's sockets and the check is otherwise tautological. Note the
  ownership precondition is already receipt-required: `check-receipt.py:434-440`
  fails any receipt whose `port_listener_ownership` is not `"child"`; the gap is
  that `checks[]` does not show it (`tools/kama-llamacpp-live.py:1029-1032`).
- C1: compare `served_model` and the stub request list, not just
  verdict/reason/drift (`tests/probe-verdicts/check.py:337-346`).
- Counting commands: name the mutant/control population and the 0/1/2 exit map
  (kake `QUALITY.md:10`, `:18`; kama `SKILL.md:303-306`).

## Proposed move (one, bounded)

**Make the v2 check set closed over the receipt's graded evidence, version-branched
at the schema.** In receipt `kama-llamacpp-live/v2`, add a small
`graded_evidence` manifest naming every check-relevant field — health body
status, `sigterm_sent`, `sigkill_sent`, `returncode`, `port_refuses` +
`port_listener_ownership`, `loading_envelope_exact` — and one check that fails
when any listed field is neither consumed by a check nor explicitly declared
non-graded. Implement `health_ready` and the teardown checks against that
manifest, and keep v1 receipts on their original status-only/non-null semantics
by branching on `receipt["schema"]` (today a single hard pin at
`check-receipt.py:174-175`). The round-16 receipt already stores what v2 needs:
`.ufo/waves/round-16/live/receipt.json` has
`captures.health.body = "{\"status\":\"ok\"}"`, `health_ready.observed =
{"status": 200}`, and `teardown = {returncode 0, sigterm_sent true,
sigkill_sent false}` — so v2 is re-derivation, not new capture.

Affected axes: **calibration** (primary — the gate can now fail a `degraded` 200
and an unconsumed false envelope) and **operability** (a `checks[]` reader sees
which evidence is actually graded; v1 receipts keep parsing). No axis is harmed:
no new file enters `tests/probe-verdicts/`, the nine matrix JSONs stay
byte-identical, and the manifest is derived from fields the tool already writes.

## Contradictions stated, not smoothed

1. C2's "health body exactly the documented ready body" reads as a readiness
   claim, while kama's own corpus says `/health` "says **nothing** about which
   model" (`SKILL.md:173`) and "Liveness may pass while identity is wrong"
   (`SKILL.md:252-253`). These are compatible only if the check is named and
   documented as *envelope conformance*, with identity left to `/v1/models`.
2. C2's "port-closed only after the port was proven owned by the child" is
   partly redundant: receipt validity already requires
   `port_listener_ownership == "child"` (`check-receipt.py:434-440`). The real
   repair is visibility inside `checks[]`, not a second ownership gate.
3. Kake's "live probe > config fields" (`SKILL.md:67`) means the receipt's
   recorded `checks[].passed` is a snapshot. Re-derive from evidence, never from
   `passed`, or the closure manifest becomes a third source of truth.

## Risks

- A hand-maintained manifest becomes a second schema; derive the field list from
  the receipt schema and fail on a check id naming an unknown evidence key.
- Byte-exact body grading binds to JSON serialization; parsed-field equality on
  the documented envelope is safer while still failing `degraded`. [INFERENCE]
- The v1/v2 branch must preserve v1 predicates exactly; "v1 skips the new
  checks" would silently weaken the historical gate.
- Importing kake's marker lexicon would carry deployment-churn assumptions into
  a local server whose body is fixed by upstream code: keep the principle
  (body beats status), not the vocabulary. [INFERENCE]

## Verification (L1-owned; not run here)

- `python3 tests/llamacpp-live/check-receipt.py` on the round-16 v1 receipt →
  still clean.
- `tests/llamacpp-live/controls.py` accepted-bad controls: 200
  `{"status":"degraded"}`; self-exit rc 0 with `sigterm_sent: false`; SIGKILL
  -9; non-exact loading 503; `loading_envelope_exact: false` → each must fail.
- `python3 .ufo/waves/round-17/c1/mutants.py` → survivors below the frozen 5/5;
  `served_model` and route-match mutants killed.
- `tests/probe-verdicts/*.json` set digest remains `bf9068d8…`.

## Limitations

- Read-only; no kama or kake file edited, no gate/measurement/llama-server run,
  no network probe (contract forbids).
- Kake's three permitted files expose conventions, not a Render health grader;
  "kake owns that surface" is a scope statement, not an existing check.
- Beyond the three permitted kake files, targeted reads of kake
  `corpus/knowledge/` entries occurred during citation verification; none of
  those paths is relied on in this report and nothing in kake was modified.
- Kama's round-16 receipt was read as data; its fields are not re-verified here.

## Installs

None. No tool installed or upgraded.
