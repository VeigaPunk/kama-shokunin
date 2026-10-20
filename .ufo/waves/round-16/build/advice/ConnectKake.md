# ConnectKake — kama ↔ kake overlap scan (round 16, build wave)

Seat: read-only connector. Axes in play: **operability** and **calibration** (calibration 7, lowest).
Wrote nothing but this file. Ran no lane gate, harness, probe or test. Ran one `ss -ltn`, one
300-sample `bind(127.0.0.1:0)` sample, three `test -e`, and bounded file reads. No installs.

Map to the round's claims: **C1** → conventions 1–3 and the redirect note (§5.1–§5.3, §5.5);
**C2** → the port population and the proposed move (§2, §3, §6).

Read: `kake-shokunin/{SKILL.md,PROVINCE.md}`, `kake-shokunin/corpus/QUALITY.md`,
`kake-shokunin/corpus/knowledge/publish-queue.md`, `kake-shokunin/corpus/lessons/{round-9,round-10,round-1-aggregator-audit}.md`;
`kama-shokunin/{PROVINCE.md,SKILL.md}`, `kama-shokunin/corpus/knowledge/{cross-lane-scope,listener-census,consumer-registry}.md`,
`kama-shokunin/corpus/QUALITY.md`, `kama-shokunin/tools/kama-probe.sh`,
`kama-shokunin/registry/{endpoint-consumers.tsv,history/latest.tsv}`,
`kama-shokunin/.ufo/waves/round-16/build/spec.json`.

## 1. The domain boundary is already clean; the overlap is at the transport layer

- kake assigns the split explicitly: "`kama` owns local model-serving endpoints; kake owns remote web properties."
  (`/home/vgpnk/Projects/shokunin/kake-shokunin/PROVINCE.md:37`)
- kama refuses the reciprocal surface: "remote web surfaces (kake)"
  (`/home/vgpnk/Projects/shokunin/kama-shokunin/SKILL.md:29`; also `PROVINCE.md:40-41`).
- kama's existing handoff row is already honest: "no kake asset or probe was changed or absorbed"
  (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/cross-lane-scope.md:42`).

⇒ No domain contention to arbitrate. Two things still touch: **(a)** one loopback port another lane
owns, **(b)** the HTTP-verdict convention layer that both lanes use. Both are addressed below.

## 2. Contested resource: `127.0.0.1:9222` — owned elsewhere, and *not* bindable by C2

Ownership evidence:

- kake's shared browser lease is pinned to that port: "(`the-musketeer` profile, CDP `127.0.0.1:9222`)
  serializes the whole kimi fleet — one op at a time, machine-wide."
  (`/home/vgpnk/Projects/shokunin/kake-shokunin/SKILL.md:161-162`)
- The lease itself is contested and integrator-held, not kama's to settle: "The the-musketeer Chrome profile
  lease is contested scope (kagi/tabi/kake) and stays with the integrator."
  (`/home/vgpnk/Projects/shokunin/kake-shokunin/PROVINCE.md:35-36`;
  `/home/vgpnk/Projects/shokunin/kake-shokunin/corpus/lessons/round-9.md:65`)
- The port is intermittently free, so "a listener exists" is not a guard:
  "CDP :9222 was down r13" (`/home/vgpnk/Projects/shokunin/kake-shokunin/corpus/knowledge/publish-queue.md:131`).
  Observed this run: `ss -ltn | grep 9222` → no output (rc=1).

What kama currently records:

- A historical classification, correctly scoped: "`9222/v1/models` → HTTP 404 `text/html`; … **NOT_HTTP /
  FOREIGN_SERVICE** for model purposes" (`/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/consumer-registry.md:235`),
  and 9222 is in the sweep list (`:269`).
- The listener census classifies it `FOREIGN_SERVICE` (`…/listener-census.md:56`) but buckets it as
  "**Platform/system**" alongside cupsd and systemd-resolve (`:102`). That bucket hides its lane owner;
  it is lane tooling, not a host service.

What C2 would have to do about it — and why the obvious answer is wrong:

- The LiveHarness port rule is: "refuse and retry if it is 8080, 34113 or any port number appearing in
  …/registry/endpoint-consumers.tsv" (`…/.ufo/waves/round-16/build/spec.json`, items[10] `LiveHarness`).
  `9222` is not in that file (`grep -c 9222 registry/*.tsv` → `0`).
- **But `bind(127.0.0.1:0)` cannot return 9222 on this host.** `net.ipv4.ip_local_port_range` is
  `32768 60999`; 300 consecutive `bind(127.0.0.1:0)` samples landed in `32781–60957`, zero below
  32768, and never on 8080/34113/9222 (this run). 9222 lies outside the allocator's range.
- ⇒ Adding 9222 to a refusal set would be dead code defending an impossible event. kama must hand off
  9222's **state and lease**, not reserve its **number**.

[INFERENCE] If the harness ever gains an explicit `--port` flag (it has none in the current spec), the
range argument lapses and 9222 must then join the refusal set — as a cross-lane reserved port whose
owner is kake/integrator, not kama.

## 3. The port guard's real population is reachability, not registration

- Both registered consumer ports — `8080`, `34113` — are below the ephemeral range
  (`…/registry/history/latest.tsv:2-4`; rows declared in `…/registry/endpoint-consumers.tsv:35-37`).
  They cannot be handed out by `bind(:0)` either, so the spec'd "refuse and retry" branch cannot fire
  under the default sysctl. It is a **latent defence**, not a measured protection.
- The only *configured* (non-ephemeral, consumer-pinned) in-range port in kama's corpus is `40961`,
  the-janitor's control plane (pin `PORT="${THE_JANITOR_PORT:-40961}"`,
  `…/corpus/knowledge/consumer-registry.md:97`), recorded as
  "no listener" (`…/listener-census.md:179`) and owned by kagi per that row. Its files are absent on
  this host (`test -e` → absent ×3, this run), so it is a fossil, not a live consumer.
- One in-range listener exists right now (`36381`), but a bound port is never handed out by `bind(0)`.

⇒ There is **no reachable cross-lane port collision for the C2 binder today**. The correct C2 statement
is "the chosen port is outside every registered consumer range by construction", not "the harness
refused a registered port". The distinction matters because the second claim is unobservable here.

## 4. What kama must hand off rather than absorb

| Surface | Owner | kama may record | kama must not |
|---|---|---|---|
| `9222` CDP session, lease, tab/target set | kake; lease integrator (kake `PROVINCE.md:35-36`) | "a listener on 9222 is not a model endpoint — for model purposes" | record lease/session health, list targets, restart the browser, bind the port |
| any non-loopback host (`ds4cc.com`, `*.kimi.page/pro`, GH Pages) | kake | nothing; kama's probe targets `127.0.0.1` only | probe it, or reuse `FOREIGN_SERVICE` as a publishing-health signal |
| auth semantics on a 401/403 port | kagi | "A 401 endpoint is *evidence about identity*" (kama `SKILL.md:30-31`) | open it, handle keys, judge request safety |
| loopback serving identity (e.g. kake's `127.0.0.1:8766` preview, `consumer-registry.md:239`) | kama | model-scoped verdict; that row already says "DEAD (no listener)" | let kake read kama's DEAD as "the preview server is down for publishing" [INFERENCE: plausible misread, not observed] |

## 5. Reusable conventions (all kake-side, adopt one-way; kama keeps ownership of its own verdicts)

1. **Status is not proof; a declared body expectation is.**
   "Raw `200` is not proof: kimi-pro serves `200 + 5995B preview-404 body` — trust `expect`, not status alone."
   (`/home/vgpnk/Projects/shokunin/kake-shokunin/SKILL.md:65-66`)
   This is the mature form of C1's own 503-envelope rule. Apply it by keeping both directions: the loading
   envelope must match, *and* a ready `/v1/models` body must fail the loading predicate (negative control).
2. **Structured verdict is the interface; the exit code is a coarse gate.**
   "read its stdout, never gate on its exit code" (`…/kake-shokunin/SKILL.md:107-108`), with an explicit
   `0=clean`/`1=drift`/`2=could-not-evaluate`/`64=usage` map (`:212`).
   `MODEL_LOADING` adds a member to kama's exit-2 union (`…/tools/kama-probe.sh:36`, `:60`), so consumers must
   branch on `verdict`/`reason`. This is consistent with kama's own KQ4, which already requires the exact
   command/exit to distinguish drift from probe failure (`…/corpus/QUALITY.md:12`).
3. **Validator is not identity.**
   "An ETag flip read as a content change, a matching ETag read as byte identity"
   (`…/kake-shokunin/corpus/QUALITY.md:16`) is rejected. Translation for C1: a matched 503 envelope proves
   *that envelope*, not that the model will finish loading and not that it is the expected model. The
   header comment already scopes it well — "not ready, not a foreign service"
   (`…/kama-shokunin/tools/kama-probe.sh:504`) — keep documentation from upgrading that to "will be ready".
4. **Name the population of every count.**
   "Every dead-path or count claim names its population" (`…/kake-shokunin/corpus/QUALITY.md:18`).
   `listeners` now counts `MODEL_LOADING` in its own bucket and summary key
   (`…/tools/kama-probe.sh:721`, `:731`, `:741-742`), so `probed` still bounds the bucket sum — the
   convention is satisfied; cite `probed`, not the model bucket, when claiming "no model endpoints".
5. **Final URL is part of the expectation (not adopted here).**
   kake's tripwire includes "`expect.status`, final URL, title regex, marker literal"
   (`…/kake-shokunin/SKILL.md:64`). kama's `fetch()` passes no `-L` (`…/tools/kama-probe.sh:290-293`),
   so a 3xx is classified `FOREIGN_SERVICE non-2xx-non-model-http` even if `Location:` points at the
   model API. Unobserved on this box and outside this round's contract; recorded as a future calibration
   candidate only. [INFERENCE: the misclassification follows from the code path, not from a measured run.]

## 6. Proposed move (one, bounded)

**Restate C2's port guarantee on its actual basis — ephemeral-range exclusion — and demote the
refuse-and-retry code to a latent defence whose activation condition is recorded.**

Why this is the non-obvious move: the round cache states the guarantee as a behavioural one ("refuse and
retry if …", `spec.json` items[10] `LiveHarness`), and both the overlap scan and a reviewer's eye are
drawn to `9222` as the port to protect. Measurement says the guard can never fire and 9222 was never
bindable, so the honest, stronger guarantee is structural, not procedural. Without this, the round either
claims an unexercised control or spends a test proving an impossible refusal.

Smallest implementation (advice to the `LiveHarness` / `LiveReceiptGate` owners):

1. At launch, read `/proc/sys/net/ipv4/ip_local_port_range` (fail open to `32768 60999`) and compute
   `refused = {8080, 34113} ∪ ports(registry/endpoint-consumers.tsv)`, then
   `reachable = refused ∩ range`, `unreachable = refused − range`. Keep `bind(:0)` + refuse/retry
   unchanged — it costs nothing and becomes live if the range widens.
2. Record one non-`checks` metadata block in the receipt:
   `port_policy: {range:[lo,hi], refused:[…], reachable_refused:[…], unreachable_refused:[…]}`.
   Do not add or rename any check id, and do not assert refusal evidence.
3. In `tests/llamacpp-live/check-receipt.py`, assert `port ∉ refused` (generalising the existing
   `port not 8080/34113` predicate) and require `port_policy` to be present. Accept an empty
   `reachable_refused` as the expected normal state.
4. Round-report wording: "the chosen port is outside every registered consumer port and outside the
   ephemeral range that could produce one" — never "the harness refused a registered port".
5. Note the activation condition next to the code and in the C2 note: the guard becomes live if the
   sysctl range is widened to cover a refused member, or if an explicit `--port` flag is added (then
   9222 joins as a cross-lane reserved port).

Affected axes: **calibration +** (the port claim names its population and its evidence, instead of
resting on an unfireable branch — the exact KQ1/KQ4 failure shape), **operability +** (the guard's
trigger is written down, so a future operator can decide in one command whether it is live). No harm to
C1 (no `classify()` change), no harm to kake (no reservation or ownership claim), no new dependency, no
new check id.

## 7. Risks

- **Schema coupling.** `LiveReceiptGate` requires "every required check present exactly once" and validates
  `port not 8080/34113` (`spec.json`, items[11]). A new top-level block could trip a strict schema id.
  If the receipt owner freezes the schema, fall back to steps 1 and 4 only (prose + activation note) and
  leave the checker predicate at `{8080, 34113}`; do not smuggle the block in.
- **The premise is host-global and mutable.** `ip_local_port_range` is a sysctl; record it once at launch
  and treat a mid-run change as out of scope. Do not re-derive it at check time.
- **The registry is mutable.** Record the resolved `refused` union rather than re-reading the tsv during
  validation, or the check becomes unfalsifiable.
- **Redundant-by-construction.** Today `port ∉ refused` is guaranteed by the range; its value is
  future-proofing (`--port`) and auditability. Say so, so nobody claims it caught something.
- **Ownership tone.** 9222's lease is contested kake↔kagi and integrator-held; this report must not read
  as kama adjudicating it. kama's only claim: 9222 is not a model endpoint and this design cannot bind it.

## 8. Verification (L1-owned; none run here)

1. `python3 - <<'PY'` bind 300 samples on `127.0.0.1:0`; assert all inside `/proc/sys/net/ipv4/ip_local_port_range`
   and none in `{8080,34113,9222}` — re-derives the reachability premise at measurement time.
2. Live receipt: `port_policy.reachable_refused == []`, chosen `port ∉ refused`, checker exits 0.
3. Injected receipt with `port: 8080` → checker exits 1 (existing predicate, regression guard).
4. Injected receipt with a synthetic in-range refused member (temporary registry holding `40961`) and
   `port: 40961` → checker exits 1 (new predicate).
5. Injected receipt with `port_policy` removed → checker exits 1 (auditability).
6. Negative control: a normal receipt on an unrelated in-range port → exits 0.

## 9. Limits

- One `ss -ltn` observation (9222 absent at read time) and one 300-bind sample; both are dated samples,
  not constants.
- No live C2 run, no probe invocation, no gate, no harness, no lane test; all measurements above are L1's.
- The 9222 listener census rows are historical (chrome pid 3080080); the port's current state is the
  single observation above.
- `tools/kama-probe.sh` was being edited while this scan ran (the `MODEL_LOADING` branch and listener
  bucket appeared between reads); line citations were re-read after the change. No claim here rests on
  the earlier in-flight state.

Report: .ufo/waves/round-16/build/advice/ConnectKake.md
