VERDICT: n/a — advisory no-harm enumeration for C1 (receipt schema v3, tcp6 fix, tri-state checks, retained/forged controls); 34 harm paths, each with a concrete ruling check.

Seat: KamaR18.CritC1NoHarm-2 (critic, read-only). Scope: every way the C1
changeset could harm an axis under the no-trade rule, plus the check that rules
it out. Evidence anchors: lane files at round-start commit `e75cf680…`; live
host probes where marked. This is not a review of landed code — `build/out/` is
still empty at writing time — it is the harm surface L1 must verify against the
integrated diff.

Host facts established by this seat (scratch sockets, torn down; `ss -ltn`
clean afterwards, no registry port touched):
- `/proc/net/tcp6` prints `::1` as `00000000000000000000000001000000` and a
  dual-stack (`IPV6_V6ONLY=0`) `::ffff:127.0.0.1` listener as
  `0000000000000000FFFF00000100007F`. Observed directly, matching
  `falsify/advice/LoopbackOwnership.md:9`. `net.ipv6.bindv6only=0` on this host;
  Python 3.14.8.
- Therefore the suspected defect is REAL: `tools/kama-llamacpp-live.py:332-335`
  tests `endswith('00000001')` for `::1` and compares `addr_hex[:24]` against
  the 22-char literal `'0000000000000000FFFF00'` — both can never match.
- A round-17 receipt (`live/receipt-1.json`) stores `/v1/models` 503 transitions
  with the exact envelope and one `/v1/models` `status: null` row
  (ConnectionRefused). `loading_503.path` can be either `/v1/models` or
  `/health` (`tools/kama-llamacpp-live.py:568-576`, `:599`).

== A. Historical receipt verdict integrity (calibration + operability) ==

A1. Default `--require-schema` regresses old verdicts. If the flag defaults to
v3 (or the gate stops accepting v1/v2), every historical receipt flips to
INVALID — a silent axis regression. Current dispatch admits only v1/v2
(`check-receipt.py:204-208`, "schema is {schema!r}, want ..."; `:653`
`required = REQUIRED_CHECKS_V2 if is_v2 else REQUIRED_CHECKS_V1`).
Check: replay the 5 pinned receipts — `.ufo/waves/round-16/live/receipt.json`,
`receipt-frozen-probe.json`, `.ufo/waves/round-17/live/receipt-{1,2,3}.json` —
bare and under `--require-schema v1|v2|v3`. Required: bare keeps today's
verdicts (VALID ×4, and the frozen-probe receipt still INVALID only under the
current probe pin, exit 1 — `GateV1Compat.md:15-17`); declared-below-required
→ INVALID(1); `--require-schema v1` on all five → unchanged VALIDs.

A2. Schema dispatch must stay exact and one-validator-per-schema. A loose match
(`startswith`, `in`, regex) could route a v3 receipt through the v2 validator —
which hard-rejects `passed` non-bool (`check-receipt.py:647-648` "passed is not
a boolean") — or route v1/v2 through v3 conjuncts and retroactively demand
`evaluated`/`outcome` keys they never carried.
Check: dispatch on exact schema string; `evaluated`, `outcome`,
`observed.not_evaluated_reason` are REQUIRED on v3 and FORBIDDEN-from-required
on v1/v2. Forged controls: v2 receipt + injected `evaluated` fields must stay
VALID-or-INVALID only by v2 rules, never re-graded by v3 rules.

A3. v1/v2 `passed` type strictness must survive any shared loop refactor. The
v3 `passed: null` channel must not leak into v1/v2 handling.
Check: v1 receipt with `"passed": null` → INVALID; gate `--selftest` retains
all v1+v2 mutation rejections (round-17 selftest printed "39 mutations +
unreadable case all rejected" — `round-17-verifier-spotcheck.md:132`); new v3
selftest cases are additive.

A4. New top-level fields must not create an unvalidated side channel. v3 adds
`outcome` and per-check `evaluated`; if the gate reads them at all, they must
be re-derived, not trusted — same failure mode as `internal_fault`, which the
gate never validates today (`GateForgeries.md` F4: "The string appears nowhere
in `check-receipt.py`"; mutant 16 `internal_fault: "internal:RuntimeError"`
with `setup_error: null` → VALID).
Check: forgeries — `outcome:"pass"` + failed check; `outcome:"setup-error"` +
`setup_error:null`; `internal_fault` non-null + `setup_error:null` (decide:
either INVALID or explicitly left as documented residual debt F4 — but a v3
receipt whose `outcome` contradicts `setup_error`/checks must be INVALID).
[INFERENCE] the minimum-consistent rule is outcome ≡ derived(exit logic), and
`internal_fault != null` ⇒ `setup_error != null`, matching the producer mirror
at `tools/kama-llamacpp-live.py:1370-1373`.

== B. False failures on healthy servers (the axis C1 owns) ==

B1. tcp6 over-match. The natural fix `addr_hex.endswith('7F')` on the tcp6
branch accepts `2001:db8::…:xx7f` — a routable non-loopback address — as
loopback-owned. That silently weakens the fail-closed ownership gate that R1
built (`tools/kama-llamacpp-live.py:311-318` "not counted as the loopback-port
owner — fail-closed").
Check: unit-table over literal strings — accept exactly
`00000000000000000000000001000000` and `0000000000000000FFFF0000??????7F`;
reject `0000000000000000FFFF0000??????80` (128/8 mapped), any global v6 ending
in `7F`, `…:0001` (another byte order), `0.0.0.0` (`00000000`) and `::`
(tcp4 `00000000`; tcp6 all-zero) — wildcard fail-closed must be retained
(`LoopbackOwnership.md:13-14`). The v6-mapped control must be REJECTED if
ownership comes back `unproven`/`foreign` — that is the false failure the
contract names.

B2. v6-mapped control environmental flake. `IPV6_V6ONLY=0` and IPv6 enabled
are host properties, not the tool's; a kernel with IPv6 off or V6ONLY forced
makes the good control fail for an unrelated reason (this host has
`bindv6only=0`, verified).
Check: control wrapper probes `socket.socket(AF_INET6)` + bind first; on
unavailability the row is INCONCLUSIVE (controls-machinery, exit-2-style),
never `accepted`/`rejected`/`good-rejected`. Fake must set `IPV6_V6ONLY=0`
explicitly and bind only `::1` or `::ffff:127.0.0.1` — never `::` (exposes the
fake off-loopback; also violates the suite's loopback rule).

B3. Null-scope drift in `loading_envelope_graded`. Contract permits
`passed:null` ONLY when no `/v1/models` 503 was observed. But the producer's
`loading_observed` is set on ANY 503 including `/health`
(`tools/kama-llamacpp-live.py:554-576`, `:1153` `loading_observed = loading_503
is not None`). A run observing only a `/health` 503 has `loading_observed:
true` with zero models-503s — neither clean null nor clean evaluated.
Check: boundary receipts — (a) `/health`-only 503, (b) `transitions` 503 rows
with `loading_observed:false`, (c) `passed:null` + `loading_observed:true` —
must be INVALID or evaluated-non-null; and `passed:null` requires the exact
`not_evaluated_reason "no-loading-503-observed"` (a null with wrong/missing
reason → INVALID). The tool's `loading_observed` semantics must be made
explicit (rename in prose or scope to models-503) so producer and gate agree.

B4. K0 regression into not-evaluated. If the null channel misfires on the good
server (e.g. health-503 counted, or ordering bug), tool exit becomes 2 and
`k0` fails `good_ok` — visible, good. But a subtler harm: `passed:null` on a
*non-loading* check. Contract allows null only on `loading_envelope_graded`.
Check: k0 row must still be tool 0 / gate 0 / all checks `evaluated:true,
passed:true`; any other check arriving `evaluated:false` or `passed:null` →
INVALID, and a control forging exactly that is retained.

B5. argv exact-re-derivation must not reject the producer's own argv. The
receipt records `argv[0]=server_real` (`tools/kama-llamacpp-live.py:1088-1097`),
`-m` = the resolved model path, `--host 127.0.0.1`, `--port <chosen>`,
`-c/-t`, tail `--no-webui --offline`. If the gate re-derives from the wrong
field (`server.arg` vs `server.realpath`, or `model.path` mismatch), its own
producer fails — good-server rejection. Also the current helper
`argv_flag` (`check-receipt.py:169-176`) returns the FIRST occurrence — a
totality check built on it still accepts duplicated flags
(`GateForgeries.md` F2: `--host 0.0.0.0` inserted after the checked value →
VALID).
Check: gate reconstructs the exact argv list from receipt fields and requires
set/list equality — k0 receipt VALID; forged controls (extra `--api-key X`,
second `--host`, second `--port`, `--metrics` with still-501 capture) each
INVALID, and each must be exercised in controls (F2 forgeries 11-15 were all
accepted today). Caution: apply the totality rule to SERVER argv only —
probe `argv` records (`check-receipt.py:535-550`) are validated by flag
presence; extending totality there breaks real receipts.

B6. Transitions-envelope rule scope. Contract: "every 503 row in `transitions`
for `/v1/models`". Producer can also record `/health` 503 rows and `status:
null` rows (`_transition_row`, `:436-449`; `/health` 503s are served by the
same llama.cpp gate and get the same envelope [INFERENCE from
`server-http.cpp` gate applying to every non-frontend path — the stored
`loading_503_bodies` list already dedups BOTH paths, `:562-565`]). Applying
the check to all 503 rows is stricter than contract; applying it only to
`loading_503_bodies` repeats the F3 hole (`GateForgeries.md` F3: transitions
503 body never parsed).
Check: rule applies to each transition row with `status==503` —
contract-minimum `/v1/models`; if `/health` rows are included, that is a
design widening that must be named in the receipt contract (a server legally
answering a different 503 envelope on `/health` would then be false-rejected
— no such upstream divergence is known, but the widening is a decision, not a
default). One shared envelope predicate (`loading_envelope_ok`,
`check-receipt.py:107-116`) must serve all three consumers (loading_503,
loading_503_bodies, transitions) — a third copy is a duplicate-authority drift
risk. A 503 row with `body:null`/`body_over_cap:true` must be INVALID, not
skipped.

B7. Zero-loading control determinism. The new good-server control must
produce ZERO models-503s AND a ready server AND graceful teardown, else it
cannot exercise the not-evaluated path (today every fake serves ≥3
loading 503s — `controls.py:166` `LOADING = {'/v1/models': 3, '/health': 1}`).
Check: control row asserts tool exit 2, gate exit 3, receipt `outcome:
"not-evaluated"`, and the run's own transitions prove the zero-503 premise
(otherwise the control tests nothing).

B8. v3 `evaluated:false` creep. On setup-error runs (K7 ready-timeout, K6
fault) the tool appends checks in `finally` (`tools/kama-llamacpp-live.py:
1310-1366`). If v3 marks never-run checks `evaluated:false`, contract is
violated (null allowed only for `loading_envelope_graded`).
Check: every K-series receipt audited — `passed:null`/`evaluated:false`
appears only on `loading_envelope_graded`; unrun checks are absent, not null.

== C. Exit-code / classification coherence ==

C1. Tool exit∔outcome divergence. Two code paths set the exit today:
`:1240` `exit_code = 0 if all(c['passed'] ...) else 1` and the authoritative
`:1375-1378`. A refactor that adds the null branch to only one produces
receipts whose `outcome` disagrees with the process exit (e.g. outcome
`"fail"` with exit 2).
Check: derive `outcome` and `exit_code` from ONE function; every control row
asserts both. Mapping: any `passed:false` → 1/fail; no false + ≥1 null →
2/not-evaluated; all true → 0/pass; setup/internal fault → 2/setup-error.

C2. `main` still returns 3 for model-digest mismatch
(`tools/kama-llamacpp-live.py:1023`), outside the contracted {0,1,2}. The
contract enumerates exit 2 for "could-not-evaluate (setup error, internal
fault…)" — a pre-launch refusal is closest to that bucket.
Check: either remap to 2 or record the deliberate carve-out in the docstring
(`:16-20` lists only 0/1/2 today). Decide; do not leave undocumented.
[INFERENCE] remap-to-2 is contract-cleanest.

C3. Gate precedence and the new exit 3. Order must be: unreadable/not-JSON → 2;
any malformedness or re-derivation failure → 1; well-formed v3, all evaluated
checks re-derive true, only legit null → 3; clean → 0. Failure modes: a
*malformed* receipt exiting 3 (silent VALID-substitute); a doctored receipt
with `passed:false` flipped to `null` exiting 3 instead of 1; a receipt with
one false + one null exiting 3.
Check: exit matrix in controls — false+null → 1; claim-true/rederive-false →
1; flipped-null → 1; legit null only → 3; `setup_error` non-null → 1 (v3 well-
formed) while setup-error receipts keep tool side at 2. And
`controls.py:_gate_flip` (`:463-491`) treats only rc==0 as `accepted` — under
the new code space rc==3 on a flipped receipt must ALSO count as
`gate_flip_bad`, else a not-evaluated flip hides (the arm's `rejected` should
be `rc == 1` exactly; assert `rc not in (0,3)` counts bad).

C4. `--require-schema` unknown value. A typo silently changing semantics is a
misclassification surface.
Check: `choices=('v1','v2','v3')` → argparse error exit 2 (distinguishable from
INVALID=1); `v10`-style future labels rejected, not lexicographically
compared.

== D. Safety / cleanup regressions (operability harm via new escape paths) ==

D1. The BaseException handler must not leak the child group. Round-17 evidence
(`InternalFaultPath.md` observed): `teardown:KeyboardInterrupt` left a LIVE
listener, no receipt, handlers SIG_IGN. Catching `BaseException` without
reordering the kill/teardown/receipt sequence could preserve the leak while
now returning 2 — worse: the defect becomes invisible.
Check: the KBI control asserts ALL of — receipt written, exit exactly 2, port
refuses afterwards, no surviving pgid (assert via `ss`/pidfile), signal
handlers restored (in-process wrapper verifies, else the controls process
inherits SIG_IGN — the reason the K6 subprocess wrapper exists,
`controls.py:252-259`).

D2. Swallowing `SystemExit`/`KeyboardInterrupt` must not bypass the
last-chance killpg (`tools/kama-llamacpp-live.py:1286-1299`) or the
`_discard_bodies` ownership rule (`:613-624`) — a stranger's body must still
never reach the receipt.
Check: ownership-failure path still yields `setup_error` +
`port-listener-not-our-child` + no bodies (foreign-listener control);
teardown fault paths still probe the port after the backstop kill.

D3. pdeathsig/session hardening retained. `start_new_session=True`,
`_preexec_pdeathsig`, `stdin=DEVNULL`, env allowlist
(`tools/kama-llamacpp-live.py:1128-1135`) are the leak-kill backstop;
`receipt['pdeathsig'] = {'requested': True, ...}` at `:1141` and the gate's
optional check at `check-receipt.py:474-478` must stay.
Check: receipt still records `pdeathsig.requested:true`,
`child_env_keys` ⊆ {PATH,HOME,LANG,LC_ALL,TMPDIR}; K4 (ignores-SIGTERM) still
forces the SIGKILL escalation and fails `teardown_graceful`.

D4. Refused-port behavior retained. `pick_port`/`refused_ports`
(`tools/kama-llamacpp-live.py:246-308`) refuse 8080/34113/registry ports even
when explicit; a fix refactor must not drop the explicit-`--port` refusal
(`:291-292` `port-refused-registered:`) or the registry parse.
Check: controls still stage a registry listing the hard pins; a control run
with `--port` on a refused port → `setup_error`, no listener bound. After the
suite: `ss -ltnp` shows zero leftover listeners and no fake processes.

D5. Temp-log leak must not widen. Known (unrouted) residual: faulted teardown
keeps the log (`InternalFaultPath.md` P2). New KBI/SystemExit handling that
skips `teardown()` must not additionally skip log cleanup in paths that
currently clean it.
Check: KBI control asserts temp log removed or explicitly records the leak
limitation; no new retained-file paths introduced.

D6. Controls-suite hygiene. New controls spawn fakes per control; each must be
group-killed even on exception (existing `_kill_fake` + finally,
`controls.py:665-667`, `:346-371`), in-process arms must run in the
subprocess wrapper (as K6 does — else a tool escape corrupts the suite), and
all new fakes bind loopback only, one at a time.
Check: suite `finally` extended identically; post-suite `ss -ltnp` + leftover
temp-dir count = 0; `TOOL_TIMEOUT` still bounds every new control (180 s,
`:88`).

== E. Detector-of-detector / counting integrity (calibration axis harm) ==

E1. New bad controls must fail ONLY the targeted check. The contract wants
each of the six named checks to be *the* failed check of ≥1 control — but
`_attributed` is substring/any-match (`controls.py:454-460`;
`ControlsAttribution.md`: a bare `teardown_port_closed` failure "satisfies"
K4's `['teardown','sigkill','kill','graceful']` token list).
Check: each new bad control's `failed_checks` asserted to be exactly the
targeted singleton (or a declared minimal set); attribution for new controls
uses exact-id match, not substring.

E2. `not-evaluated` must get its own bucket. Under current classification
(`controls.py:556-570`) a tool-2/gate-3 control falls into `rejected` →
counted as detection of a bad server — wrong; but mapping it to `accepted`
inflates accepted_bad. `misclassified`/`uncontrolled-check` are new counters;
their definitions must be fixed before measure.py runs.
Check: the zero-loading control produces a dedicated classification
(`not_evaluated` verdict), excluded from accepted_bad/good-rejected, counted
in `misclassified` only when the tool/gate disagree with the tri-state
contract; definitions written in `measure.py`'s docstring.

E3. Frozen-arm behavior of new controls. `measure.py` runs frozen
tool+gate AND current tool+gate. Frozen gate has no `--require-schema`
(argparse exit 2) and no v3 path; frozen tool escapes KBI (wrapper exit 4 —
`MutControlsSelf.md` frozen K6 row: tool_exit 4, receipt_written false).
Check: for every new control the frozen arm's expected outcome is defined —
e.g. "frozen gate exits 2 (unreadable arg) on --require-schema ⇒ counted as
failure-to-reject, not crash"; "frozen tool KBI escape ⇒ accepted-bad".
Undefined arms silently equal "0 detected" — the exact MutControlsSelf (c)
survival mode (drop gate-flip arm → `gate_flip_bad=0` while doing zero flips).

E4. K6 tightening must preserve the fired-flag oracle. The K6 wrapper's
`k6.fired` file (`controls.py:272-280`, `:525-530`) is what stops a
silently-missed patch from passing vacuously; requiring `tool_exit == 2`
exactly must not drop it. The new KBI control needs the equivalent (a
fired-flag + `KeyboardInterrupt` raised from `teardown`, not from `main` — an
interrupt raised before teardown starts exercises a different, larger hole).
Check: `tool_exit == 2` exactly AND fired-flag AND receipt present AND
`setup_error`/`internal_fault` records the interrupt type; K0 predicate kept
as `tool_exit == 0 and gate_exit == 0` exactly (mutant (d) in
`MutControlsSelf.md` added `-15` acceptance and survived the numeric oracle —
the self-check for "K0 exit predicate weakened" must directly assert the
predicate, e.g. a self-check that parses/asserts on a synthetic row).

E5. New self-checks must be observable-failing, not ceremonial. Contract:
"self-checks that fail when its gate-flip arm or K0's exit predicate is
weakened (R7 MutControlsSelf)". A self-check that merely re-reads the same
constant it guards detects nothing.
Check: each self-check is tied to a control ROW (a mutated controls.py that
drops the arm or the K0 predicate demonstrably fails suite exit — the frozen
arm in E3 provides one natural detector: any arm that produces zero
gate_flip results while `gate_flip_bad==0` is indistinguishable unless the
arm count is asserted non-null).

E6. Forged-receipt controls must run the gate, not a subprocess stub, and must
assert `exit == 1` (INVALID) exactly — a gate crash (exit 2) on a forged
receipt is could-not-evaluate, i.e. the forgery escaped.
Check: each forged control row asserts `gate_exit == 1`; a row where the gate
timed out/crashed is `ControlsFault`, not a rejection.

== F. Duplicate authority, provenance, stale docs ==

F1. One envelope predicate, one outcome derivation, one argv derivation —
already covered under B5/B6/C1; restated because C1 touches three consumers.

F2. SOURCED rows must ground the *exact* predicates used. The tcp6 word-order
claim needs a kernel-source/doc row (the literal format), RFC 4291 for
v4-mapped, Python 3.14 BaseException docs for the catch scope, and an
exit-convention row — all append-only via `tools/sources-append-only.py` with
`opened` cells. A SOURCE row quoting the wrong line range or a reformatted
kernel literal is false provenance.
Check: `scripts/sources-census.sh validate` clean; each new row's ≤25-word
quote re-opened at the pinned URL; producer code comments cite the row id.

F3. `documented_by` strings embedded in receipts must stay true.
`tools/kama-llamacpp-live.py:60` `POPEN_RETURNCODE_DOC` uses `/3/` and must
move to `/3.14/` (host runs 3.14.8, verified; `/3/` now titles "Python 3.15.0
documentation" — `round-17-verifier-spotcheck.md:179`). The gate only
requires `documented_by` non-empty (`check-receipt.py:644-646`) so a stale
string passes the gate while lying to readers.
Check: `grep -n 'docs.python.org'` over C1 files → only `/3.14/`; the
`loading_envelope_graded` DOC text (`:136-145` "no 503 observed -> fail")
must be rewritten — it currently documents the now-removed fail behavior.

F4. Self-description drift: `SKILL.md:565` ("the tool now emits
`kama-llamacpp-live/v2` with 11 checks"), `PROVINCE.md:73` (same), the tool
docstring `tools/kama-llamacpp-live.py:21` ("Receipt schema:
``kama-llamacpp-live/v2``") and the exit-code list `:16-20`, the gate
docstring `check-receipt.py:2` ("v1 and /v2"), `main`'s
argparse description `:1359-1360`, and `controls.py` docstring's schema/count
claims all go stale on the v3 bump.
Check: diff review greps every occurrence of the schema string and "11
checks"/"exit 2" enumerations; `stale-statements.py`-style sweep for the
files C1 touches.

F5. Separability/file-set. C1 owns exactly
`tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`,
`tests/llamacpp-live/controls.py`, `.ufo/waves/round-18/c1/*`. Any edit to
`kama-probe.sh`, `check.py`, registry, SOURCES outside the assigned rows, or
the frozen copies silently couples the claims.
Check: `git diff --name-status e75cf68..master` post-integration — only the
four C1 paths (plus L1-owned lesson/SCORECARD/appends); `sha256sum -c
.ufo/waves/round-18/frozen/SHA256SUMS` clean; receipts' `probe.sha256`
unchanged (`36b64978…`).

== G. Attack surface expansion ==

G1. New receipt fields (`evaluated`, `outcome`, `not_evaluated_reason`) are
new forgeable surface; every added field needs a malformedness rule (types,
enum membership, reason string equality) or it repeats F4/F5
(`GateForgeries.md` F4-F6: unvalidated `internal_fault`, undigested
`body_sha256`, partial `observed` cross-checks — all VALID today).
Check: for each new field one forged control exercising a wrong type/enum;
decide whether `transitions[].body_sha256` is newly re-derived (F5 residual —
if not, record it as debt, don't silently claim it).

G2. No new network/env surface. The harness stays loopback-only
(`_NoRedirect`, no-proxy opener `:464-465`); the v6-mapped control binds
`::ffff:127.0.0.1`/`::1`, never `::`; no env values are recorded (names only,
`:83-84`); a forged `--api-key` lives only in a receipt string the gate now
rejects — do not add a receipt field that would record credential VALUES.
Check: grep the diff for new `os.environ` reads beyond `CHILD_ENV_KEYS`; new
control receipts contain no env values.

== Smallest safe corrections summary (for L1) ==

1. v3 gate: additive path, exact schema dispatch, `--require-schema` default =
   accept-any-declared; outcome/evaluated/null-reason all re-derived.
2. tcp6: exact-literal accept list for `::1` and `FFFF0000`-mapped 127/8 only.
3. Null channel: only `loading_envelope_graded`, only when zero `/v1/models`
   503s; `/health`-only observations stay evaluated — pick and document the
   semantic.
4. Exit coherence: single outcome/exit derivation; KBI/SystemExit → 2 +
   receipt + killed group + restored handlers, verified by the new control's
   four assertions.
5. Controls: dedicated `not_evaluated` bucket; frozen-arm expectations defined
   per new control; forged controls assert `gate_exit == 1`; attribution by
   exact id.
6. Docs: `/3.14/`, v3 in SKILL/PROVINCE/docstrings, `loading_envelope_graded`
   DOC text rewritten.

== Limitations ==

- `build/out/` is empty at writing time; this enumerates harm surfaces and the
  checks that rule them out — it is not a diff review. When the C1 executor's
  files land, each check above is directly runnable.
- The tcp6 observations are this host's kernel only; the kernel-format SOURCES
  row (F2) is the canonical grounding, my socket probe is corroboration.
- Whether `/health` 503 rows fall inside the contract's "every 503 row in
  `transitions` for `/v1/models`" is contract wording; scoped to models, a
  `/health`-only non-exact 503 forgery survives — flag for L1's ruling.
- The tool's exit 3 (model digest mismatch) sits outside the contracted
  {0,1,2}; whether to remap is a design decision, not a defect by itself.
- Installs: none. No tools installed or upgraded; Python 3.14.8 and stdlib
  sockets only.
