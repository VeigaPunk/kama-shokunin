# ConnectTameshi — overlap scan: tameshi (verification-fixture craft) × kama C1/C2

Seat: read-only connector. Axes scored: **calibration** (lowest at 7) and
**operability**. Read: `tameshi-shokunin/SKILL.md`, `PROVINCE.md`,
`corpus/QUALITY.md`, plus four corpus notes cited below; kama `PROVINCE.md`,
`SKILL.md`, `tools/test-snapshot.sh`, in-flight `tests/probe-verdicts/*.json`,
`tests/llamacpp-live/check-receipt.py`, `registry/endpoint-consumers.tsv`,
`tools/kama-probe.sh`, and the round-16 frozen snapshot. Measurements below are
read-only observations at 2026-10-20T13:31Z; matrix files are untracked and were
still being written (`ls -la tests/probe-verdicts`).

## 0. Verdict in one line

The overlap is **method, not product**: tameshi owns the reusable fixture craft
and explicitly refuses endpoint health and sibling gate code; kama owns the
verdict and must keep the matrix, the harness and C2. Two of tameshi's newest
rules are already satisfied by kama's in-flight design; one convention (a
*discriminating* red) is not yet expressed as an assertion, and one kama habit
(substring asserts) is below tameshi's bar.

## 1. What tameshi owns, and what it refuses

- Owns the method: "hermetic suites, mutation testing, fail-closed arms,
  verdict-line discipline, no-permissiveness audits, before/after proof"
  (`tameshi-shokunin/PROVINCE.md:3-5`), and it refuses product domains: "every
  lane's gate remains its own … Never edits a sibling's gate code"
  (`PROVINCE.md:14-17`). Endpoint health is named as kama's:
  "Credential material (→ kagi), endpoint health (→ kama)" (`PROVINCE.md:18`;
  again at `:45-46`).
- Refuses verdict truth: "Product semantics — whether a gate's verdicts are
  right | never measured — sensitivity ≠ truth" (`SKILL.md:1263`). So no
  tameshi artifact can certify that `MODEL_LOADING` is the *correct* verdict;
  only the cited upstream (`server-http.cpp:307-325`, README @ b11755) can.
- Refuses live substrates: "Live substrates / sessions | never read; a
  live-plane probe is a PATH-level stub, never the session"
  (`SKILL.md:1261`). C2 starts a real binary; it must never be offered as a
  tameshi sweep, and tameshi's refusal (e) covers it
  (`corpus/knowledge/service-optin-protocol.md:129-132`) [INFERENCE: an
  ephemeral lane-owned process is not the session, but tameshi has no measured
  precedent for a real-binary fixture — see §4].
- No prior commitment to kama: the service queue lists cite-check,
  surface-probe, round-gate, proxy-check, claims-check, kimi-census — not
  kama (`corpus/knowledge/fleet-suite-census.md:277-286`), and
  `corpus/SOURCES.md` has no kama row.

## 2. Reusable conventions — and where kama already matches

| Convention | Tameshi anchor | Kama evidence | Status |
|---|---|---|---|
| Hermetic suite: `mktemp -d`, `trap … EXIT`, no live path read | `SKILL.md:138-149` ("Run the control on the pinned bytes and require green") | `tools/test-snapshot.sh:13` `WORK=$(mktemp -d …)`, `:24` `trap cleanup EXIT INT TERM` | **already** |
| Literal per-case oracle in a data file, not computed from the tool | `SKILL.md:162-170` ("Pre-registration is what makes an expectation miss a calibration datum") | `tests/ollama-evidence/cases.json:14-16` (`expect`, `expected_exit`, `expected_finding`); round-16 matrix is the same schema family | **already** |
| Refuse malformed/hostile fixture input before running | `SKILL.md:171-176` (uniqueness gate; no-op refused) | `tests/ollama-corpus-guard/check.py:43-46` ("A missing, empty, or malformed matrix fails closed with `finding_id: test_failed` and exit 1") | **already** |
| A frozen witness declares prior exposure and is re-integrity-checked before replay | `corpus/QUALITY.md:39-42` ("records prior exposure and checks integrity before replay … reanalyzing an existing artifact is not a new gate") | `frozen/manifest.json` has `sha256`, `source_commit`, `capture` but **no prior-exposure field**; `measure.py` is instructed to verify the sha | **partial** (§3.1) |
| One checker rejects the old and accepts the repair | `QUALITY.md:50-55` ("The same checker must reject the old-null companion and accept the kind-only repair") | `measure.py` runs the same `check.py --probe P` for frozen and current | **already** (design) |
| Exit AND token, never exit alone | `corpus/knowledge/mutation-case-kagi-census.md:88-91` ("A suite asserting only exit would have passed this deletion") | harness grades "verdict, reason and exit all equal expected" | **already** |
| Pre-registered expectation table, misses kept as calibration | `corpus/knowledge/service-optin-protocol.md:208` ("Pre-register the expected table") | matrix authors are told to derive oracles "from the C1 rule text and `classify()` source — never computed by running the probe" | **already** |
| Positive control that kills the *opposite* overreach | `SKILL.md:104-107` ("Arm coverage is the floor, not the bar") | working-tree `SnapshotCompat` block: `MODEL_LOADING` accepted (`tools/test-snapshot.sh:170-176`) **and** `MODEL_LOADED` still dropped (`:182-184`) | **already, and correct** |

The practical conclusion: **reuse, don't invent a second dialect.** The
round-16 matrix schema is isomorphic to kama's own `cases.json` corpus plus its
corpus-guard runner, so `check.py` should keep kama's existing vocabulary
(`finding_id`, `--selftest` asserting literal exits) rather than adopting
tameshi's `n/m pass` grammar.

## 3. Where kama's current habit sits below tameshi's bar

### 3.1 Frozen manifest lacks prior exposure; the claim is stronger than the record

`frozen/manifest.json` records snapshot, sha256 `93ee4302…cd64`, source commit
and capture command, but not *who already ran it*. Tameshi's criterion is
explicit: "records prior exposure and checks integrity before replay"
(`QUALITY.md:39-42`). The round context itself discloses the prior run (L1 smoke
10:17 -03 on a stub of the loading body), so the disclosure exists in prose but
not in the artifact the replay will cite. A replay that does not carry its own
exposure line is, under tameshi's rule, not a new gate.
Fix: add `prior_exposure` and the expected red set to the manifest, or emit
them in `run-frozen.json` (see §5).

### 3.2 Exit 2 cannot discriminate — only the token can

The frozen probe returns exit 2 for *every* non-`MODEL_OK` verdict:
`if [ "$C_VERDICT" = "MODEL_OK" ] … else EV_DRIFT=1`
(`.ufo/waves/round-16/frozen/kama-probe-before.sh:804`),
`[ "$EV_DRIFT" -gt 0 ] && return 2 || return 0` (`:837`). The frozen loading
answer is `FOREIGN_SERVICE` / `non-2xx-non-model-http` (`:521`), and the
expected `MODEL_LOADING` also carries exit 2 (contract: "exit 0 iff MODEL_OK
else 2"). So **the red/green distinction is token-only** — the exact class
tameshi measured as B4: "the exit code still matched … A suite asserting only
exit would have passed this deletion"
(`tameshi-shokunin/corpus/knowledge/mutation-case-kagi-census.md:88-91`). The
in-flight harness already grades the triple, which is correct; this is recorded
because any future simplification to exit-only silently makes C1 vacuous, not
merely weaker.

### 3.3 `die` flattens usage into probe error 1

`die()  { … exit 1; }` (`frozen/kama-probe-before.sh:81`) is the same exit used
for "probe error" in the documented map "exit: 0 reconciled | 2 drift | 1 probe
error" (`:111`). Tameshi's round-15 criterion: "Explicitly classify
every nonzero exit, including usage"
(`QUALITY.md:77-82`), with the standard `0/1/2/64` lattice
(`SKILL.md:1676-1683`). The matrix harness must therefore treat **any** exit
outside the expected integer as a failure even when the expected integer is 2,
and it must not accept 1 as "roughly 2". The harness contract already does this
(`passed = verdict, reason and exit all equal expected`); the *registration*
must state the harness's own usage exit explicitly (§4, Scribe row).

### 3.4 Substring asserts are the weakest kama habit in the neighbourhood

`assert_contains()` greps a regex over the output
(`tools/test-snapshot.sh:28-29`), and tameshi names that shape as the weakest of
six gates: "A suite whose asserts are weaker than its contract carries a weaker
bar than it prints" (`SKILL.md:122-125`). The new matrix must not reuse this
style: parse `--json` and compare `rows[0].verdict` / `rows[0].reason` as
strings. The harness already promises the JSON parse; keep `assert_contains`
for prose lines (DELTA.md transitions), never for verdicts.

### 3.5 Contract-named `drift` is not assertable by the shared schema

C1 names "drift true" as part of the fix, and the probe emits a `drift` field in
`check --port` JSON (`frozen/kama-probe-before.sh:806`). But the shared
`expected` object is `{verdict, reason, exit}` only; a matrix author cannot
express it, and the harness records `drift` without comparing it. A repaired
probe returning `MODEL_LOADING` with `"drift": false` would pass the matrix while
violating the stated claim. This is exactly tameshi's "reported-but-unasserted"
survivor class (D10/B10, `SKILL.md:306`). Note the weaker point: drift is
`true` for both frozen `FOREIGN_SERVICE` and repaired `MODEL_LOADING` (`:804`),
so it cannot discriminate red from green — it is a **claim-completeness** gap,
not a red/green gap. Owner: `ReviewSchemaAmbiguity` (schema) and
`VerdictHarness` (record field already present). [INFERENCE: adding
`expected.drift` is a schema amendment L1 must rule on; I do not propose it as
this seat's move.]

## 4. Contested scope — absorb vs hand off

| Item | Absorb in kama? | Authority / owner | Why |
|---|---|---|---|
| Is `MODEL_LOADING` the right verdict for the b11755 envelope? | **Absorb** | kama `PROVINCE.md:41-43` ("kama answers … right now"); tameshi `SKILL.md:1263` | Product semantics; tameshi refuses it |
| `tests/probe-verdicts/check.py` (the gate) | **Absorb** | `VerdictHarness` (this wave) | Sibling gate code; tameshi never edits |
| Matrix family JSON files | **Absorb** | `Matrix*` executors | Domain oracles |
| `measure.py` counting command | **Absorb** | `MeasureRunner` (L1) | L1 runs measurements |
| C2 live harness + receipt gate | **Absorb** | `LiveHarness`, `LiveReceiptGate`; admissibility → `CriticC2ServiceBoundary` | Live plane; tameshi refuses (`SKILL.md:1261`) |
| Mutation sweep of `check.py` | **Hand off, post-round, opt-in only** | tameshi service (`PROVINCE.md:28-38`) | Needs committed pin + one-command hermetic suite; currently `git status --porcelain -- tools/kama-probe.sh` is non-empty, so tameshi's rule applies: "If the path is dirty: stop" (`SKILL.md:150-157`) |
| Generic fixture-craft findings (this note) | **Hand off** (report only) | tameshi lane; ground moves to its Core only through "an admitted, source-headed `knowledge/` entry" (`PROVINCE.md:40-42`) | tameshi's method is its own; kama cites it, does not fork it |
| Claim lines saying a replay "proves" teardown | **Absorb with corrected wording** (§4.1) | L1 + `ScribeSkillSection` | A replay proves recorded predicates, not re-execution |

### 4.1 C2: the receipt gate replays; only the harness proves teardown

`tests/llamacpp-live/check-receipt.py` states its own limit correctly: "it never
trusts a bare `\"passed\": true`" (`:5-7`) and re-derives nine named checks from
receipt data (`:24-32`). That matches tameshi's retained-receipt gate exactly —
and tameshi's limit applies verbatim: "A clean check replays recorded predicates
and pinned digest binding, never … a fresh measurement" (`SKILL.md:1686-1688`).
So the claim "proves teardown" must be split:

- **live harness (run time)**: pid gone, process group gone, port connect-refused,
  before *and* after — the actual negative proof;
- **receipt gate (later replay)**: re-derives those recorded facts; it does not
  re-check the host.

Otherwise L1's claim row overstates what the gate measured.

### 4.2 C2: `FORBIDDEN_PORTS` is a two-literal restatement of a registry claim

`FORBIDDEN_PORTS = {8080, 34113}` (`tests/llamacpp-live/check-receipt.py:33`)
and the failure text says "is a registered consumer port" (`:375-377`). The
registry is the authority and it is a 3-row TSV whose ports are exactly 8080 and
34113 (`registry/endpoint-consumers.tsv`, rows `omp-llama-cpp-default`,
`ufo-fsd-thetick`, `ufo-fsd-local-helper`). Today the literals agree with the
registry; tomorrow a fourth row would not be forbidden, and the claim "never a
registered consumer port" would be true of two constants, not of the registry.
Tameshi's exact failure class is a value that is reported but not re-derived
(`SKILL.md:306`, D10/B10). Fix: derive the port set from the registry at check
time (parse `declared_baseurl`), fail closed (`2` = could-not-evaluate) if the
registry is unreadable, and record the registry digest in the receipt. This is
the second instance of the §5 move.

## 5. Proposed move (one, bounded, no new fixtures)

**Derive every expected set from its declared authority and assert set
equality on named cases — never totals, never membership.**

Two instances, one rule. It costs one comparison per probe variant and changes
no fixture.

### 5.1 C1 instance — the red must be directional

The frozen probe cannot emit `MODEL_LOADING` (`grep -c MODEL_LOADING
.ufo/waves/round-16/frozen/kama-probe-before.sh` → `0`; its vocabulary line
lists six verdicts, `VOCAB="MODEL_OK MODEL_MISMATCH FOREIGN_SERVICE
UNAUTHORIZED_SERVICE DEAD NOT_HTTP"` at `:55`, and the 503 tail is
`non-2xx-non-model-http` at `:521`). Its non-loading behaviour is the repaired
behaviour on every non-loading route *if and only if* the patch is narrow.
Therefore, against the in-flight matrix (64 tests, measured at 13:31Z), the
**pre-registered expectation** — not a measurement; this seat ran no gate — is:

| Run | expected passes | expected failures | expected failure set |
|---|---|---|---|
| frozen `kama-probe-before.sh` | 49 | 15 | exactly `{t : expected.verdict == "MODEL_LOADING"}` |
| current `tools/kama-probe.sh` | 64 | 0 | `{}` |

Assert `set(record.name for record if not record.passed) == expected_failure_set`
and fail loudly when a **non-loading** case fails on the frozen run: that is
either a mis-specified expectation or a non-narrow patch, and in both cases it
is a finding, not noise. This is tameshi's "same checker must reject the old …
and accept the … repair" (`QUALITY.md:50-55`) made checkable, plus "A red
control has no denominator" (`SKILL.md:148-149`) in its differential form.
Today `measure.py` prints "the list of test names whose verdict differs"; a
printed diff is not a pre-registered expectation
(`service-optin-protocol.md:208`).

For the positive controls the contract already names, the same derivation gives
exact sets instead of "defeats":

- **constant-`FOREIGN_SERVICE` ("reject-all")** must fail every test with
  `expected.verdict != "FOREIGN_SERVICE"`;
- **`MODEL_LOADING` on any 503** ("loading-all", the overreach the C1 scope
  limit forbids) must fail exactly the near-miss set: tests whose
  `/v1/models` route answers 503 while `expected.verdict != "MODEL_LOADING"`.
  Measured at 13:31Z: 32 tests answer 503 on `/v1/models`; 14 of those expect
  `MODEL_LOADING`, **18 expect a non-loading verdict** (the remaining loading
  test exercises a different route). Re-derive from the files; do not quote
  the number.

The rule, not the count, is the deliverable: the count is a function of the
matrix and must be recomputed from it at run time. Tameshi's warning is exact:
"Never quote a case count from source" (`SKILL.md:99-103`).

### 5.2 C2 instance — the forbidden-port set is registry-derived

`forbidden = ports(parse(registry/endpoint-consumers.tsv))`, asserted against
the receipt's `port` and against `port_free_before`/`port_free_after`
(see §6.2). Registry unreadable → exit 2, no verdict.

Affected axes: **calibration** (primary — the red becomes a discriminating,
pre-registered table; a typo'd expectation and a broken stub become named
failures), **operability** (one derived constant instead of a stale literal).
No axis harmed: no new fixtures, no new process, no write outside the receipt /
run JSON the wave already writes.

## 6. Risks and second-order effects

1. **The directional assertion will surface real disagreements.** If a
   `Matrix*` author expected `MODEL_LOADING` on a body the repaired probe
   classifies differently, the repaired run fails (good) *and* the frozen run
   still "predicts" failure (so the directional check cannot distinguish a
   wrong oracle from a wrong probe on that case). Mitigation: attribute by
   comparing the repaired record's `reason`/`evidence` to the body, and report
   as a per-case finding — never relax the set. [INFERENCE]
2. **Port TOCTOU in `closed` mode.** The schema's `closed` mode "binds then
   closes a socket and probes that port"; if another process takes the port in
   the gap, the case fails for a reason unrelated to the probe. Treat a
   non-refused pre-check as **harness/setup** (exit 2 or a recorded resample),
   never as a probe failure; never retry-until-green
   (`SKILL.md:1686-1688` names the boundary). `ReviewHarnessDesignRisk` owns the
   analogous race in the live harness; the matrix's copy is unowned.
3. **Stub lifecycle.** One `ThreadingHTTPServer` per test on `127.0.0.1:0`
   must `shutdown()` + `server_close()` + join its thread; 64 tests × leaked
   server threads is an operability regression that looks like flakiness.
4. **`drift` wording.** Until `expected.drift` exists (or L1 rules it out),
   C1's claim table must say "drift is emitted true by the probe" and cite the
   JSON field, not "the matrix asserts drift true".
5. **Scope creep toward tameshi.** Do not ask tameshi to sweep `check.py` this
   round: the probe and `test-snapshot.sh` are both dirty
   (`git status --porcelain -- tools` → `M tools/kama-probe.sh`,
   `M tools/test-snapshot.sh`), and tameshi's intake refuses a dirty pin
   (`SKILL.md:150-157`). The hand-off is a post-commit opt-in.
6. **C2 admissibility is not mine to rule.** Whether an ephemeral lane-owned
   llama-server is an "enabled service" under KQ5 belongs to
   `CriticC2ServiceBoundary`; this note only says the *proof shape* (before/after
   negative, registry-derived ports) matches tameshi's restore discipline
   (`SKILL.md:375-400`, "proof the substrate never moved").

## 7. Verification L1 can run (after the wave's files land)

```bash
# 0. frozen integrity and absence of the new verdict (read-only)
sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh   # 93ee4302…cd64
grep -c MODEL_LOADING .ufo/waves/round-16/frozen/kama-probe-before.sh  # 0

# 1. same checker, two instruments
python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json
python3 tests/probe-verdicts/check.py --json
# expect: frozen failures == {tests with expected.verdict == MODEL_LOADING};
#         current failures == 0; both runs enumerate the same test count.

# 2. directional receipt
python3 .ufo/waves/round-16/measure.py
# expect run-frozen.json and run-current.json with disjoint failure sets,
# and the printed differing-name list == the loading-expectation set.
```

Do not read §5's 15/49/18 as fixed: re-derive from `tests/probe-verdicts/*.json`
at run time (the directory was still changing at 13:31Z).

## 8. Limitations / unknowns

- No tameshi artifact certifies C1's verdict truth; that rests on the upstream
  source cited in the claim, not on any fixture (`SKILL.md:1263`).
- Tameshi has no measured precedent for a real-binary ephemeral fixture (C2);
  its live-substrate ban is stated for sessions/host state, not lane-owned
  processes [INFERENCE]. Do not cite tameshi as authority for C2's admissibility.
- `tests/probe-verdicts/check.py` did not exist at read time; §3.3/§5 are advice
  to `VerdictHarness`/`MeasureRunner`, not observations of their code.
- No install or upgrade was performed by this seat. Read-only introspection
  only: `~/.local/bin/llama-server --version` reports
  `version: 0.7.0-dev (build 11755, commit 704366d76)`; no server was started,
  so this is not a C2 measurement.
