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
| Handler installed implies SIGTERM necessarily terminates with 0 | reject S043's overclaim; S047 narrows it | Same pinned files: `server.cpp` install at 534 precedes call at 576, and `server-queue.cpp:279` resets the handler's `running = false;` at 134. An actual termination guarantee additionally needs locking/shutdown assumptions. |
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
