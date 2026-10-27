# Round 18 — observed, failed and not-evaluated; detectors checked against their survivors

Steered round 18, hyaku phase 2. Start `e75cf680b53484a61709ee1b2787d8dbc6419f74`
(branch master); initial lane state clean, no earlier round-18 dead/no-report attempt.
Outside round 17: `round-17-verifier-spotcheck.md` admitted both bounded claims and
routed R1–R7. R8 was answered by the orchestrator: operator per-role routing governs,
not a lane defect. Assigned axes operability 8 + calibration 7; calibration is lowest,
no stagnation waiver. No service restoration, registered-consumer health or model
quality is claimed. The live fixture and retained archive questions stay with L0.

## Declared claims

- **C1 operability, sourced, 8 → 8:** harden the existing live-llamacpp-lifecycle
  capability. v3 separates an unobserved loading state (tool 2 / gate 3,
  NOT-EVALUATED) from observed failure (1), adds retained controls for six checks,
  closes the specified schema/argv/loading-transition receipt holes, fixes tcp6
  ownership and contains internal BaseException faults. Sources S048/S050 determine
  the ownership predicate; S051 determines the exception boundary; S054 supports
  exact argv. S052 is convention precedent only, never authority for lane numbering.
- **C2 calibration, lowest axis, 7 → 7:** bind the lane's statements about its own
  detectors to the named round-17 survivors: H1–H3/H5–H7 on check.py; F0/cache/target
  detector-self holes; opened/blank-line append-only holes; refused-count zero;
  malformed-decoder and timeout-child debts. This is a bounded named-survivor
  repair, not evidence that an unseen mutant cannot survive.

**Separation:** C1 owns the live tool, receipt gate, live controls and round-18 c1
counter. C2 owns check.py, fault-controls, sources-append-only, round-18 provenance
and c2 counter. The probe and nine matrix JSON files are unchanged shared inputs.
Neither claim's detector depends on the other's changed production files.

## Gate

All sources below opened **2026-10-20**, by the named wave seats and/or L1. Quotes
are verbatim and ≤25 words; source bytes/pins and opening reports are under
`.ufo/waves/round-18/`. Newly written rows S048–S054 are all tier A within their
narrow scopes (S053 rejected as a basis). Existing S047 receives its missing Gate
row here, not by editing round 17's lesson.

| Candidate | Decision | URL, location and quote |
|---|---|---|
| A handler-install → task-loop-start reset window limits first-SIGTERM claims | admit necessary ordering condition (S047; R1) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-queue.cpp `terminate()` 132–136 and `start_loop()` 278–280: `running = true;` (279); deciding read `if (!running) {` (141). |
| Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `start_loop()` overwrites `terminate()`'s `running = false` (134) with `running = true` at `server-queue.cpp:279`. An actual termination guarantee additionally needs locking/shutdown assumptions. |
| tcp6 address fields are four native numeric words, not a network-order hex string | admit S048, scoped to opened v7.2 implementation | https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c:2176 `src->s6_addr32[0], src->s6_addr32[1],` (format at 2173); `include/uapi/linux/in6.h:38` defines `__be32 u6_addr32[4];`. |
| proc_net_tcp.rst defines IPv6 byte order or 0A state codes | reject that reading; admit its narrower S049 scope | https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst:8: "Note that these interfaces are deprecated in favor of tcp_diag." The only address example is IPv4. |
| IPv6 loopback is exact ::1 | admit S050 | https://www.rfc-editor.org/rfc/rfc4291.txt §2.5.3:474: "The unicast address 0:0:0:0:0:0:0:1 is called the loopback address." |
| Mapped addresses represent IPv4 nodes | admit S050; mapped 127/8 prefix is lane derivation | Same RFC §2.5.5.2:551–552: "This address type is used to represent the addresses of IPv4 nodes as IPv6 addresses." Layout at 570 has 80 zero bits, 16 ones, IPv4. |
| Exception-only guards contain SystemExit/KeyboardInterrupt | reject; admit S051 hierarchy | https://docs.python.org/3.14/builtins/exceptions.html §SystemExit: "It inherits from BaseException instead of Exception so that it is not accidentally caught by code that catches Exception." |
| Empty observation can have a distinct non-zero result | admit S052 as precedent only | https://docs.pytest.org/en/stable/reference/exit-codes.html §Exit code 5: "No tests were collected"; failure is separately code 1. The page states no pytest release version. |
| Automake defines the lane's exit numbers | reject S053 as basis | https://ftp.gnu.org/gnu/automake/automake-1.19.tar.xz member `doc/automake.texi`:9776–9777: "an exit status of 77 a skipped test, an exit status of 99 a hard error". Canonical www.gnu.org page timed out. |
| llama.cpp rejects duplicate flags itself | reject; admit S054 last-wins warning | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp:836: "DEPRECATED: argument '%s' specified multiple times, use comma-separated values instead (only last value will be used)". |
| The frozen parser recognises real IPv6 loopback listeners | reject, observed counterexample | `.ufo/waves/round-18/build/advice/ProbeTcp6Format.md`: real `::1` and `::ffff:127.0.0.1` listeners yield raw hex ending `01000000` and `0100007F`; frozen `port_owned_by` returns None for both, IPv4 True. |
| A green lane-owned fixture certifies registered-consumer health | reject | Registry consumers still have no new sample; no run in this round binds 8080 or 34113. |
| Three v3 runs on the real pinned fixture evaluate and pass, with four-pin schema-floor validation | admit bounded own-work S055, opened 2026-10-20 | `.ufo/waves/round-18/live/receipt-1.json` JSON path `outcome`: `"pass"`; `checks`: 11 evaluated true; `runs/live-gate-1.stdout`: `VALID`; commands/exits and the other two receipts in `runs/commands.json`. |
| All repeated llama.cpp options are last-wins and warn | reject the general S054 reading; admit S056 correction, opened 2026-10-20 | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/arg.cpp:3538: `params.api_keys.push_back(key);`; scalar port assigns at 3354, spec-type appends at 4321 and is warning-exempt at 833. |

Existing SOURCES rows' status/recheck/used-by cells remain unchanged unless an
explicit old→new addition is recorded below. S001–S047's immutable cells stay intact.
Rows S048–S054 were written only after opening. Search scope: kernel tcp6/tcp4 row
printers, proc_net_tcp, RFC4291, Python3.14 exception hierarchy, pytest/Automake exit
codes, llama.cpp argument parsing. Stop: each proposed teaching located; Automake
numbering rejected as a duplicate convention precedent. A new own-work live row
will be recorded only after measured v3 runs, not before.

## KQ23 application — a fail-capable mined-mistake fix

Motivation: round-17 M8 had no criterion. The admission at S043 cites the handler,
`terminate()` and final return but does not account for the post-install reset
`running = true` or the deciding `if (!running)` read. KQ23 **rejects** the
unconditional first-SIGTERM claim. The source bytes were already pinned in round
17; merely possessing them did not catch the mistake.

Positive control: S047's **necessary ordering condition** accounts for both writes
(134,279), deciding read (141), install (534), handler and return (590), and names
the interval where reset overwrites termination. KQ23 admits that bounded
condition, not a guarantee of successful shutdown. Targeted negative control:
remove the reset citation/accounting from S047 and retain the conclusion: reject.
`build/advice/RevKQ23FailCapable.md` records the in-memory positive/negative
application and a blind counterexample (the first S047 Gate draft accidentally
strengthened “only once” into sufficiency). This lesson uses necessary wording.
Unexamined shutdown calls, locking and platform signal assumptions limit any
stronger termination guarantee; no runtime reproduction of that window occurred.

## Mistakes

| ID | Class | Evidence pointer | Captured-by | Fix / shown able to fail |
|---|---|---|---|---|
| M1 (mined round-17 M8) | Control-path overclaim: handler write + final return treated as a sufficient path | `round-17.md:309`; outside R2; S043 vs S047; reviewer `RevKQ23FailCapable.md` | none before KQ23; external source reopening caught the reset | KQ23 + application above: S043 reject, necessary-condition S047 admit, reset-omission mutant reject. |
| M2 | An unobserved property classified failed instead of could-not-evaluate | outside R4; round-17 `LiveUnderLoad.md` zero-503 run | KQ21 caught vacuous pass, but had no third-outcome rule | KQ24, v3 null license and zero-loading control; fail must dominate null. Counts appended after execution. |
| M3 | Kernel format guessed from address spelling | frozen tool `_listen_inodes`: network-order suffix and 24-vs-22-char prefix | round-17 ownership review disclosed debt; no sourced format test | S048/S050 + real IPv6 selftests and mapped-good control; frozen real bind gives None for both IPv6 forms. |
| M4 | Detector reports success while named weakening survives | outside R7; `MutBaselineH.md`, `MutBaselineDetectors.md`, `MutBaselineControls.md` | KQ20's named mutant/control rule; external falsifiers | C1/C2 detector self-checks and survivor counter; bounded results appended, not general immunity. |
| M5 | Refusal provenance counts structured keys but ignores refusal prose | `RevengerRefusedZero.md`; round-17 refused result has 82 distinct labels | outside R7 | round-18 provenance `--selftest` 30/30; frozen refused 0 → repaired 82, spawned 0 on same input. |
| M6 | Integration-only source URL mismatch hidden by synthetic selftest | delivered gate and its synthetic receipts both dropped `tools/server/` from source-binding URLs | first L1 real v3 smoke: tool 0 / gate INVALID with five URL problems | L1 corrected validator and synthetic builder to full pinned path; real receipt VALID and selftest re-ran. |
| M7 | Later /v1/models capture's HTTP status ungraded | `RevTriStateDesign.md`: ids-intact 503 can retain null loading grade | fresh reviewer in build wave | tool and v3 gate now require models capture 200 for both identity checks; new `v3-models-capture-503-ids-intact` mutation against no-loading receipt rejects. v1/v2 unchanged. |

## Routed defects from round-17 outside check

R1: missing S047 Gate row supplied above. R2: KQ23 and fail/positive controls above.
R3: README append names S047; historical row untouched. R4: C1 tri-state classifier.
R5: six retained targeted controls in C1. R6: v3 schema floor, exact argv,
transition-body grading, tcp6 ownership, BaseException receipts, exact K6 exit and
Python3.14 citation; compatibility remains a required no-harm check. R7: C2 named
survivors/provenance and C1 controls-self mutations; fresh wave-2 attacks must not
be confused with an outside non-author review. Final measurements and residual
limits are appended below. No helper/routing/fleet source changes are absorbed.

## Build-wave provenance

The initial validated 95-seat payload was wholly refused (95 job-limit messages,
zero spawned). Thirty capacity checks never reached ≤5 running jobs. L1 fixed the
wave to 75 genuine items (not split) and revalidated; the 20 dropped prompts remain
in `dispatch-95.json` and are L1-held/low-yield (including trend/report drafting).
75 seats dispatched as one unchanged validator taskCall at 20:59Z; role mix and
terminal counts are in build validation/assignments/completion evidence. L1 holds
the planner seat; connector seats perform sibling-overlap scans. Every production
writer used its own /tmp clone; L1 integrates delivered files. No seat commits.

## Calibration ledger — statement → adversary → detector

The following is the declared C2 universe, fixed from round-17 routed evidence,
not a random sample of possible weaknesses. No scalar mastery increase is inferred.

| Statement being calibrated | Named adversary / fault | Repair's detector |
|---|---|---|
| reason grading means exact expected reason | H1 case-insensitive reason | fault-controls F9 case-only corruption |
| verdict grading uses the emitted token, not a silently cleaned value | H2 verdict strip | F10 whitespace on loading row (avoids the served-id confound) |
| required route is GET /v1/models, not only the path | H3 ignores method | F11 non-GET cached replay |
| reported served id is exact raw expected evidence | H5 normalises the reported id | F12 case/suffix variant on a non-dash id |
| a probe that made no request does not pass | H6 bypasses no-request failure | F13 no-request cached replay |
| documented first-row grading really uses the first row | H7 grades last row | F14 contrasting two-row output |
| a reject-everything subject cannot give the detector credit | fault-controls F0 bypass | F0 adversarial check instrument in selftest |
| route replay uses the corresponding row's output | shared F6 cache | per-row cache self-check |
| rejection must be attributable to the targeted conjunct | drops targeted-conjunct requirement | off-target-only failure self-check |
| all immutable registry cells include opened | append-only drops opened comparison | independently expected opened-only edit selftest |
| blank lines do not erase later registry rows | append-only truncates after blank | post-blank-row edit selftest |
| refused task attempts count actual refused labels | provenance prose-blind refusal count | same committed 82-refusal input plus refusal selftest |
| malformed probe output stays a row error, not a traceback | deeply nested JSON | F15; check.py malformed-successor selftest |
| decoder integer limits stay row errors | 5,000-digit integer | F16; check.py malformed-successor selftest |
| a probe timeout does not leave same-group sleep alive | background sleep after probe timeout | F17 liveness observation and cleanup; deliberately detached sessions remain outside the boundary |

`build/advice/MutBaselineH.md` independently exercised distinguishing witnesses
for all six H rows (pristine/restored reject the fault; each mutant accepts).
`MutBaselineDetectors.md` exercised the five self-detector rows, and
`RevCheckPyCrashes.md` exercised the three crash/cleanup faults. The survivor
counter reports their exact outcomes and invalid/inconclusive baselines rather
than deriving success from this prose table. Fresh wave-2 mutants stay a
separate set; their survival does not disappear into this named denominator.

Source bookkeeping: S047 used-by old `corpus/lessons/round-17.md` → same plus
`corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`.
No old status/recheck or immutable cell changes. New-row edits before their first
commit are drafts, not retroactive changes to an admitted row.

## Official measurement pass and counter-integration defects

Measured production revision `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`.
`python3 .ufo/waves/round-18/runs/run.py` executed 32 commands; 30 met their
declared exits. All ten selftests, real v3 runs/gates (three each), five legacy
receipt pairs, wrong-probe-pin rejection, snapshot clone and round-16 measure
clone passed their expected outcomes. Raw commands, exits, stdout/stderr and
digests are retained under `runs/`, not inferred from seat reports.

Two official counting commands were **could-not-evaluate**, not quietly called
pass: c1 measure exit 2 on a top-level/per-row `misclassified` mismatch in its
before arm; c2 exit 2 on two family-b composite outcomes despite targeted red
selftests (the independent main arm refused its deliberately broken instrument).
Both failures are routed to their original counter owners, with regression
fixtures required. Original failed evidence remains; corrected reruns are new
artifacts, never overwritten to conceal the failure.

C1 raw subject/control cells at that pass: accepted-bad **5 → 0**,
good-rejected **1 → 0**, misclassified **1 → 0**, uncontrolled-check count
**0 → 0** under the new control suite. The last number measures retained control
coverage on both subjects, not a claim the six check predicates were absent in
v2. Controls-self mutants all three killed by selftest. C2 raw named universe:
15 before; current six H kills, three handled crash/cleanup faults, two
append-only kills, refused-count correct82, one FC self kill and two FC
inconclusives. A corrected counter must preserve those raw arms.

S055 was added only after reading the three real v3 receipts and gate outputs.
Its Gate row above is own-work evidence, not a first-party upstream contract.

## Execution conformance disclosures

- The complete canonical protocol reread occurred **after** build dispatch,
  rather than in the required load order. The earlier prompt/fleet-axis/skill
  reads do not excuse that ordering defect. No exemption is claimed.
- The ProbeArgvEffects item conflicted with its wave's loopback-only rule by
  explicitly asking for a duplicate `--host 0.0.0.0` launch. Its report records
  an actual wildcard listener for 14.2 ms, immediately killed without HTTP,
  followed by a separate isolated-network-namespace experiment; final PID/ss
  checks found none of that seat's processes. This was unnecessary exposure,
  not a safe pattern to copy. All new fake/receipt forgery checks keep the
  wildcard argv as **data**, never a host launch instruction. No persistent
  service or registry state was changed.

## Fresh source/provenance corrections

- S056 supersedes S054's over-general reading: scalar `--port` and clearing
  `--host` are last-wins; api-key/spec-type options append, and spec-type is
  warning-exempt. `ReopenS054.md` located the omitted caveats; L1 re-read the
  pinned handlers. Exact argv remains the lane's policy regardless of option
  semantics. S054's immutable cells are untouched; Gate correction above.
- S049 used-by old `corpus/knowledge/loopback-listener-ownership.md` → same plus
  `corpus/lessons/round-18.md`. S050 old same ownership entry → same plus
  `corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-18.md`.
  Their status/recheck/immutable cells do not change.
- S048's support header is now retained byte-exact as
  `sources/linux-in6.h`, sha256 `4b70a423…6b27d`, matching the already cited
  upstream header digest. The source-pins capture manifest is not retroactively
  presented as having originally saved it.
- Dispatch precision: attempts.json contains **32** capacity observations in
  total, minimum15, none≤5; thirty refers only to the long gated loop. The reused
  validator registry retains95 declarations from the wholly refused plan, of
  which exactly75 received IDs. Actual spawning is75, not95. Version/band and
  this qualification are in `build/validation-supplement.json`; final-output
  resource observations for all75 are in `build/terminal-evidence.json`.

Fresh residual, not falsely closed: `ConnectTsukuroi.md` shows that the current
four-pin gate's server pin identifies the launcher executable, not an external
expected digest for `libllama-server-impl.so`. The receipt records implementation
and install-tree digests and checks internal consistency, but a consistent swap
is not authenticated by those four pins. No install file was changed. A future
implementation-digest precondition is distinct from this round's named R6 fixes.

### Gate location/hierarchy clarifications (falsify)

The earlier `tcp_ipv6.c:2176` citation meant a file plus line, not a literal URL
path. The working source location is
[tcp_ipv6.c#L2173-L2177](https://github.com/torvalds/linux/blob/v7.2/net/ipv6/tcp_ipv6.c#L2173-L2177):
`src->s6_addr32[0], src->s6_addr32[1],`. Full observed Gate strings are
`::1` → `00000000000000000000000001000000` and `::ffff:127.0.0.1` →
`0000000000000000FFFF00000100007F` (`ProbeTcp6Format.md`, repeated in ReopenS048).
S048's support header is retained now; its digest was already correctly cited.

S051's parenthetical “canonical /3.14/library/exceptions.html” is imprecise:
that path is a redirect alias to the versioned builtins page used by this round.
The page's unversioned canonical link serves Python3.15 and was not the source.
The abbreviated three-example list is not the complete BaseException hierarchy:
Exception is also a direct child and BaseExceptionGroup can escape an
Exception-only guard. The integrated tool catches BaseException itself.
ReopenS051 found only a footer rebuild in the live page bytes; no strict
`pin.py --verify` pass is claimed (only the retained offline selftest passed).

KQ23's three comparative M8 citation-component controls are retained as
`kq23-controls.py`: S043 negative, S047 necessary-condition positive, and S047
with the reset citation removed. This is deliberately not a semantic/NLP gate
or a proof that all shutdown calls are read; the human judgement remains named
in the earlier review and outside sampling remains pending.

## Falsify wave and recovery attempt 2 (2026-10-21)

Falsify wave: 76 seats validated under policy v2 (`falsify/validation.json`, spec
sha256 `ecf2668a…`, band 64–100) and spawned as one unchanged taskCall at
23:15:12Z. Roles: reviewer 24, scout 16, critic 8, scribe 7, executor 5,
mutation-tester 4, connector 4, revenger 4, sentinel 2, simplifier 2. 66 seats
returned a verdict-bearing report before the coordinator's quota death:
**28 confirm, 34 partial, 1 refute, 3 nonconformant** (format only; their bodies
carry partial/confirm verdicts); 10 seats left no report and stay dead —
they were not respawned. `falsify/advice/` retains all 66 reports; the count
command is `python3 .ufo/waves/round-17/count-verdicts.py
.ufo/waves/round-18/falsify/advice --expect-names .ufo/waves/round-18/falsify/spec.json --json`.

Attempt 1 ended on provider quota with `lane-dead-no-report` and left pushed
checkpoint `101f3991d3570bc9350fbf9c5561f4be1185699d` (unadmitted, 96 retained
paths). Reused after re-verification: the implementation commits `c6dc46f` and
`1c325b2`, both wave specs/registries/advice, live receipts, frozen manifest,
strict canonicalisation tooling and the corpus/appends already integrated in
the checkpoint (S047/S051/S054/S056 text, README precision paragraph,
knowledge entries). Discarded: the 20 never-assigned build members (declared in
`build/advice/swarm-registry.json`; `dispatch-95.json` is the refused payload),
the 10 dead falsify seats (no output), and the
pre-repair `runs/c2-survivors.json`, kept under `runs/pre-repair/` as the
counter-defect record after its corrected rerun.

Fixed from falsify findings in this attempt (each with a fail-capable case):

| Finding | Fix | Detector |
|---|---|---|
| `PrivacyScope` **refute**: `child_env_keys` element interpolated into gate output, echoing any `NAME=<value>` | constant problem text, never the element | new `env-key-value-echo` mutation + loop assertion that the secret is absent from stdout/stderr |
| `GateCaptureHashes` H1: `/health` 503 carrying the exact loading envelope accepted NOT-EVALUATED | envelope rows on any producer route contradict `loading_observed=false`; null license refuses them | `v3-health-loading-envelope-null-license` mutation on the no-loading receipt |
| `ConnectTsukuroi`: four pins bind the 17,864-byte loader stub, not the 7.67 MB impl; three consistent swaps print VALID | `--expect-server-impl-sha256`; official runner passes the observed impl digest as a fifth pin | `impl-sha-mismatch-expect`, `impl-digest-absent-expect`; real receipt-1 re-validated with five pins |
| `CounterC1` F1/F2/F3: CLEAN forgeable by under-reported `accepted_bad`/`good_rejected` rows, an undeclared `model_unchanged` label, and a conflicting `gate_flip_arms` | row-vs-count under-report faults; exclusion only when declared in `input_integrity_checks`; arms below the row count fault (above = note) | `model-only-undeclared`, laundering-row, bucket-gap and arms unit cases; selftest 45/45 |
| `KnowledgeOwnership` 3f: honest limit missing (no live IPv6 join; selftest only) and the endianness rule stated as parser behaviour | appended two bullets in `corpus/knowledge/loopback-listener-ownership.md`; 3a–3e (race, namespace, wildcard case D, anchors, prior overlap) were already corrected in the checkpoint's "Round-18 falsify source anchors and limits" section and re-verified | falsifier pointers, `ResidCorpus.md` |
| `ReopenS047` F2: window-exclusion inference from `/health` ordering | appended correction: receipts' `returncode 0`/`sigkill_sent false` is the deciding evidence; order argument marked [INFERENCE] | receipts + `ReopenS047.md` confirmed-6 |
| `ReopenS047` F1, `ReopenS051`, `ReopenS054`, S047/R3 README precision | landed at the checkpoint (README precision paragraph with both window endpoints, `returncode 0` path and static-only caveat; S051 redirect/canonical clarification and BaseExceptionGroup in the knowledge entry; S056 supersedes S054's general wording) and re-verified this attempt | `ResidCorpus.md` F1–F6; `corpus/SOURCES.md:209-213` |
| four-pin knowledge limit superseded by the fifth pin | appended correction in `corpus/knowledge/llamacpp-loading-lifecycle.md`, including the one-of-51-members residual | runner argv + gate selftest |

Deferred as named debt, not silently closed (falsifier reports retained):
`GateCaptureHashes` M1–M4 (props/slots digests and statuses, capture/teardown
`error` fields, optional probe `summary`, non-model transition rows and the
final-transition/`captures.health` cross-check), the fresh mutants surviving in
`FreshGate` (4/4), `FreshControls` (2), `FreshAppend` (3/4), `FaultF0`
(vacuous empty fault list; unanchored fault records), `FaultTarget`
(multi-row-only guard loss), `GateLoadingTransitions` (repeat/dedup rewrites),
`GateModelsStatus` (tool selftest blind to a relaxed model-status check),
`GateNullLicense` (two transition-row encodings), `AppendCells`
(comparator-normalisation and exit-mapping survivors), `ConnectTameshi`
(counter conventions refused this round), `ConnectKagi` (handoff line),
`ConnectKumitate` (producer-shape note), `MistakesFailCapable` (M7 producer side
has no fail-capable detector; KQ23 prose-applied). `PrivacyScope`'s informational
leaves stay as recorded: dummy credential-shaped test values in build advice and
intentional host-path provenance in retained receipts.

## Mistakes — recovery attempt

| ID | Class | Evidence pointer | Captured-by | Fix / shown able to fail |
|---|---|---|---|---|
| M8 | Measurement-publication gap: both official counters ended exit 2 at the checkpoint, and the published head counter bytes no longer matched the retained run | `ReportNumbers.md`, `MistakesFailCapable.md`, `C2Admission.md`, `ConnectTameshi.md`; `runs/c1-measure.exit`/`c2-survivors.exit` at 101f399 | falsify wave 2's re-run duty; the coordinator treated counter repair as done without re-running | both corrected counters exit 0 on the official invocation (C1 5→0/1→0/1→0/0→0; C2 15 named, after 11 killed/1 correct/3 handled); the stale artifact is retained under `runs/pre-repair/`; the run records measured argv and exits |
| M9 | Counter trusts its child for 3 of 4 counts (row-vs-count divergence), and an exclusion label was trusted without a declaration | `CounterC1.md` E1/E3/E5 | fresh falsifier attacked the counting command, not just the subject | row-vs-count under-report faults, declared-exclusion requirement, arms-below-rows fault; unit cases added |

### Residual falsification call (7 seats; no GRANT needed)

The recovery had ≤49 seats of the ≤200 round budget, so it ran **no 64–100
wave**: one ordinary `task` call of 7 reviewer/critic seats (the ≤8 residual
allowance). They attacked the fixes above in `/tmp` copies of `101f3991` plus
the working-tree bytes. Verdicts: five confirm (`ResidPrivacy`, `ResidHealth`,
`ResidImplPin`, `ResidCounterC2`), two partial (`ResidCounterC1`, `ResidCorpus`),
plus `ResidClaims` partial on C1's commit labelling and the overwritten-receipt
defect. Reports: `.ufo/waves/round-18/residual/advice/`.

Integrated from the seats: off-allowlist raw-token regression case and the
non-string `child_env_keys` crash (`ResidPrivacy` P2/P3); impl
field↔`install_tree` cross-check and a softened pin claim (`ResidImplPin`
P2/P3); the bucket-gap cross-check hole, the `good_ok=false` contradiction and
over-report notes (`ResidCounterC1`); C2's implemented kill rule, its 42-run
count and `combine_arms([])` (`ResidCounterC2`); live receipts restored from
`101f3991` with recovery receipts moved to `live-recovery/`, and a clean-tree
refusal in `run.py` (`ResidClaims` F1/F2); removal of a duplicated ownership
correction and naming of the checkpoint-integrated Reopen items
(`ResidCorpus` F1–F6); guarded finalizer signal-handler restore with a hostile
mapping unit test (`ToolFaultPaths` P2, previously undispositioned).

Disposition of the remaining non-confirm falsify reports not named above:
report-draft advisories (`LessonResiduals`, `ReportNumbers`, `ReportSources`,
`ReportTrends`, `ReportWork`, `ReportWaves`, `ReportHandoff`) described the
pre-recovery state (both counters exit 2, no final report); the measured pass
and this round's report supersede them. `C2Admission`'s missing full counter
arm is the post-repair rerun. `SurvivorUniverse` is disclosed below. `ReopenS053`'s
bookkeeping nits (tier/status wording) are noted and left as written.

Named residuals from the residual call, not silently closed:
- only 1 of 51 install-tree members is pinned; `libllama-common`/`libggml`/
  `libllama` swaps stay internally VALID under the fifth pin;
- a `/health` 503 with a truncated or non-JSON body stays NOT-EVALUATED (exit 3),
  never VALID;
- `gate_flip_arms=0` with no flip rows is internally consistent and passes;
- the C2 selftest-kill arm has no full-enumeration check, so an early-abort
  selftest carrying the target literal reads as killed (ConnectTameshi D4);
- FC-target's 600-byte retained tail truncates the matched problem line;
- `counts.after.total` folds inconclusive (exit 2 still blocks a pass);
- named detector-self mutant (b) "any nonzero exit counts" is absent from
  family b: the C2 denominator is the ledger's 15, not the full (a)–(d) set
  (`SurvivorUniverse.md`), and adding it needs a frozen-vs-current comparison
  shape this counter does not implement.

## Official measurement pass — recovery attempt 2

This supersedes the earlier "Official measurement pass and counter-integration
defects" section's could-not-evaluate state for the current bytes; that failed
pass at `c6dc46f` remains as history, not overwritten.

Measured tree: `eb78788b35b832d08887d4c366d1d0c1df3a6c19` (branch tip at run
start with a clean tree; `runs/commands.json` `measured_commit`). Work commit
`0c75c611474cfc9f3c549e056fb0b736b20b854f`; evidence commit
`888cd384a9cd06dd93d3fe6b05a9d829b9972122` carries the residual seats and
censuses; the harness fix is `eb78788b`. `python3
.ufo/waves/round-18/runs/run.py` executed 32 commands and all met their declared
exits (harness exit 0), including three live v3 runs and their five-pin gates
`VALID`, five legacy receipt pairs, the wrong-probe-pin negative control (exit 1),
the snapshot and round-16 clone measures, both counters exit 0, and the
probe-matrix identity check over all ten inputs.

C1 (`runs/c1-measure.json`): accepted-bad **5 → 0**, good-rejected **1 → 0**,
misclassified **1 → 0**, uncontrolled **0 → 0**, gate_flip_arms 16 → 17,
counter exit 0, faults `[]`, frozen pins verified, no leaked processes.

C2 (`runs/c2-survivors.stdout`, the counter's JSON document; its `--out` stays
exclusive): 15 named (a6 b3 c2 d1 e3); before survived 11 / miscount 1 /
accepted 3 → after killed 11 / correct 1 / handled 3; inconclusive 0/0; frozen
witnesses 15 with 0 mismatches; exit 0; tool sha256 `ac934794…`.

Recovery live receipts are `live-recovery/receipt-{1,2,3}.json` (tool
`83eac5c0…`, outcome `pass`, ports 40999/36277/43877). The checkpoint receipts
under `live/` were restored to their cited bytes (tool `dc036d7d…`, ports
33769/44109/45359), so S055's citation resolves to the bytes it describes.

## Erratum — round-19 routed defects (appended 2026-10-21)

- **Residual verdicts (routed defect 1).** The residual call's committed
  verdicts are **4 confirm** (`ResidPrivacy`, `ResidHealth`, `ResidImplPin`,
  `ResidCounterC2`) and **3 partial** (`ResidCounterC1`, `ResidCorpus`,
  `ResidClaims`), not "five confirm, two partial" plus a separate claims
  partial. Dispatch record (defect 4):
  `.ufo/waves/round-18/residual/assignments.json` — 6 reviewer, 1 critic.
- **S055 / Gate-row pointer revision (defect 2).** S055's commands and exits
  exist at `1c325b2`/`101f3991`; `runs/commands.json` does not exist at the
  cited measured commit `c6dc46f`. At the tip, `runs/commands.json` (measured
  `eb78788b`) and `runs/live-gate-*.stdout` describe the **`live-recovery/`**
  receipts (tool `83eac5c0…`), while the `live/` receipts are the checkpoint
  bytes (restored; tool `dc036d7d…`). The round-18 Gate admission row therefore
  holds for `live/` at `1c325b2`; `live-recovery/` is the tip's separate
  observation, not a replacement.
- **SCORECARD C2 command (defect 3).** The official counting invocation is
  `python3 .ufo/waves/round-18/c2/survivors.py --json`; its JSON document is
  `runs/c2-survivors.stdout`. The `--out PATH` wording in the C2 declaration
  row is superseded (the counter's `--out` is exclusive-create by design).
  `runs/c2-survivors.json` (04:08Z) is a pre-official corrected run retained
  beside the official stdout (05:11Z); the two agree.

## Round-19 citation provenance (appended 2026-10-21)

The routed revision defects are now machine-checked by
`tools/citation-provenance.py` against `registry/required-citations.json`
(token shape `cite(<rev>, <path>, sha256=<digest>)`):

- S055's commands/exits exist at the checkpoint revision:
  cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/commands.json, sha256=ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a)
- The checkpoint gate output describes `live/` (revision-qualified):
  cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15)
- The recovery gate output describes `live-recovery/`:
  cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7)
- The official C2 document is the stdout, not a surviving `--out` file:
  cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/c2-survivors.stdout, sha256=ea2e3e0258346410a04cef27a79c1ec0bbe1fd8ce8db13e683da327950cf272d)

## Round-20 correction — filed wording and retrospective roster

Commit `30ed378` rewrote the Gate rejection row at line 42 instead of appending
its correction. Original wording (verbatim at `8bf99cae` and `30ed378^`):

> | Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `server-queue.cpp:279` resets the handler's `running = false;` at 134. An actual termination guarantee additionally needs locking/shutdown assumptions. |

Superseding wording (the line retained from `30ed378`):

> | Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `start_loop()` overwrites `terminate()`'s `running = false` (134) with `running = true` at `server-queue.cpp:279`. An actual termination guarantee additionally needs locking/shutdown assumptions. |

The decision stays reject; the mechanism attribution is corrected. This
appendix records the original text and the process defect; it does not
legitimize rewriting filed lessons. Source: round-20 `Lesson18Line42.md`.

The round-19 erratum's label "Dispatch record" for
`.ufo/waves/round-18/residual/assignments.json` is superseded: it is a
retrospective roster first committed in round 19 (`7229fa9`), not original
spawn/task-call evidence. The 4/3 verdict split is supported by the advice
files; the asserted 6 reviewer / 1 critic role split still lacks independent
dispatch evidence. See adjacent `assignments.PROVENANCE.md`.

Line-anchor qualification: the S051 prose cited as `SOURCES.md:209-213` is
at those lines at `8bf99cae`; S057 was appended after S056 (not inserted
mid-table) and shifted later prose by one. Refer to the heading "S051
identity-label clarification" at that revision rather than unqualified tip
line numbers. Future appended registry rows shift it again.


## Round-20 additional material citation pins

These are the reconstructed 13 material revision/path instances (12 distinct
paths; two C2 JSON generations). The original material-citations scanner is
not tracked, so this is a named selected population, not all material citations.

- S055 receipt: cite(1c325b2e58fcfdc6761f645b44cedfb1d65243e6, .ufo/waves/round-18/live/receipt-1.json, sha256=e616f67e2e2bec196402f56ed3a45fb68f78c9f4e927f0ea7d8acd170caf6d75)
- Build supplement: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/build/validation-supplement.json, sha256=b081d09c0c89c8b463610b6b2523a19e1934d36543897284b6b3310412511f03)
- Terminal evidence: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/build/terminal-evidence.json, sha256=44b0694d00c03c2b7af9c0f93e7e83aef073be115bb37fc5d8a33051fd2e371f)
- Falsify validation: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/falsify/validation.json, sha256=5644346ed0d9b543e1934b4ee32cf7c287bd12d0aed67594bf1201f9e4cbcf5c)
- Falsify spec: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/falsify/spec.json, sha256=ecf2668ad0829c09c27d318bbc5046513254392b15ce4aa9d8834632f3d904df)
- Build registry: cite(c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d, .ufo/waves/round-18/build/advice/swarm-registry.json, sha256=a2eb60512cb83da62a895280310d4b6dc1ba6256e48254fbaf526d6e013c11f0)
- Refused payload: cite(c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d, .ufo/waves/round-18/build/dispatch-95.json, sha256=59ec84c1fa30c392f8de8b27277550dcad15d006585b4462086e479b92b36744)
- Pre-repair C2 JSON: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/runs/c2-survivors.json, sha256=bd217de0030d1b69f07c0ac3cc334ccdac192896441a177bb13eb3c308509829)
- Checkpoint C1 exit: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/runs/c1-measure.exit, sha256=5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985)
- Checkpoint C2 exit: cite(101f3991d3570bc9350fbf9c5561f4be1185699d, .ufo/waves/round-18/runs/c2-survivors.exit, sha256=5f8bd21203fdbe78b3339b6c8102f5a67cea53316e7b8797aa7aea63e498d985)
- Recovered C1: cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/c1-measure.json, sha256=83e8a1ed95d0c71739aef9f5e1295e14f05d9cc004b56ad19c796ebe1864e1b3)
- Retrospective roster (not original dispatch): cite(7229fa95eb122310e9e5334ad799ee3006293ebd, .ufo/waves/round-18/residual/assignments.json, sha256=8d3a9aee251e700319f93210de7bdd945730fdb3d83fc17e5f109451ef389226)
- Corrected pre-official C2: cite(1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e, .ufo/waves/round-18/runs/c2-survivors.json, sha256=8cc59a65d1a23119479354a1a370f29dbc95ed204135761781ae8cf095582f13)

Agreement qualification for "they agree" at 407–408: the pre-official JSON and
official stdout agree on 15 item outcomes, counts, frozen witnesses and 42
run-status tuples, not entire documents. Tool hashes, paths, time/PID/stream
provenance and bind-guard distinct-port statistics differ (1382 versus 1376).
Both binds totals are 1464. Source: round-20 `R18CitationRows.md` and its full
comparison transcript. No new execution of the old 42-run counter is implied.


## Restored lines (round 52)

Lines this file lost in place, re-appended verbatim in round 52 (claim C2): the file is declared append-only with corrections appended (`registry/append-only-contract.tsv`), and `tools/append-only-audit.py` v6 graded each line below as deleted and no longer held (round-51 rows of `registry/append-only-disclosures.tsv`). They are historical bytes, kept so that no declared line is lost; where this file's later text replaced them, the later text stands. One fenced block per deleting commit, in history order.

Deleted by `1b85a24eca4d` (round-18: measured pass on eb78788b, recovery receipts, scorecard and log):

`````text
| M8 | Measurement-publication gap: both official counters ended exit 2 at the checkpoint, and the published head counter bytes no longer matched the retained run | `ReportNumbers.md`, `MistakesFailCapable.md`, `C2Admission.md`, `ConnectTameshi.md`; `runs/c1-measure.exit`/`c2-survivors.exit` at 101f399 | falsify wave 2's re-run duty; the coordinator treated counter repair as done without re-running | corrected counters now exit 0 on the official invocation; the stale artifact is retained under `runs/pre-repair/`; the run records measured argv and exits |
`````

Deleted by `f1790e25b421` (round-19: empty-tree rejection, C1 scope erratum, separability correction, final receipts):

`````text
  cite(eb78788b35b832d08887d4c366d1d0c1df3a6c19, .ufo/waves/round-18/runs/live-gate-1.stdout, sha256=b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15)
`````

Deleted by `028235e6f28d` (round-19: checkpoint Gate citation row; four-row C1 registry):

`````text
- The recovery gate output describes `live-recovery/`, not the checkpoint `live/`:
`````

Deleted by `30ed37837782` (round-19: full-digest diagnostics; 279 wording):

`````text
| Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `server-queue.cpp:279` resets the handler's `running = false;` at 134. An actual termination guarantee additionally needs locking/shutdown assumptions. |
`````
