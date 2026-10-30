# MT34RegressLogic — C2 regression attribution (advisory)

Axes: operability + calibration. Tip: `23b3fdb1a925129a9961cf551f6d40bf251602cb`.
No claim verdict or integration recommendation is issued here.

## Method and boundaries

Read freeze/amendments, operator rules, and wave-b X02/X03 regression reports.
Used two shared clones under this seat's explicit scratch root; never modified lane tools or registry.
The counter and its Runner/SPECS/classifier were imported from the pinned tip.
Ran pristine counter, two independent base/regressed template batteries, counter mutants,
and restored counter. Every counter scoring run used a fresh work directory.
Full base/regressed stdout is in `out/MT34RegressLogic/rowout/`; counter lines and stderr
are in the same out directory. No tools installed. Own scratch commit only: the broken-TSV
fixture `b4da6e1b7d11ed4b8e88cc821cd0fe8bb3b09bc4` (not a lane commit).

## All twelve planted regressions: observed results and attribution

Here KILLED means the row template rejected its regressed copy, not a verdict on C2.
All ordinary base runs exit 0 / classify true; context-capacity exits 2 / host-busy.
All regressed runs classify false. Eleven lose their pattern; context retains it.
No complete regressed-template output contains Traceback, SyntaxError, ImportError or
ModuleNotFoundError. Sources' harness does report an inner invocation's runtime crash.
No shipped edit changes an unrelated constant: literal swaps are in the actual predicates.

| Row | Result | Regressed output / reason | Attribution |
|---|---|---|---|
| sources-registry | KILLED, rc=1 | `43/45 selftest cases passed`; both removal cases report `TypeError: 'NoneType' object is not subscriptable` | **Crash-mediated**, not clean silent acceptance. Disabling `new is None` falls through to subscripting `new=None`. Related defect, weak witness. |
| ollama-offline-evidence-replay | KILLED, rc=1 | passed=48 failed=3; identity_conflict_ps_digest_mismatch, whitespace_not_stripped, prefix_not_stripped observe loaded_same_digest | Right check: digest-mismatch classification suppressed. |
| live-llamacpp-lifecycle | KILLED, rc=1 | outcome fail; sole failed check `models_owned_by_llamacpp` | Related expectation-literal swap, not an unrelated constant. Real endpoint data reaches the edited check. |
| gguf-declared-identity-replay | KILLED, rc=1 | receipt_duplicate_json_key expected duplicate_json_key, observed accepted; passed=29/status=failed | Right duplicate-key guard. |
| context-capacity-receipt | KILLED, rc=2 | base host-not-idle-before-K1; regressed model-sha256-mismatch; both print identical zero-cell all_ports_closed=true summary | **Classifier-carried setup refusal**, not pattern disappearance or a cell-content regression. |
| instrument-agreement | KILLED, rc=1 | deterministic agree=0 disagree=3; nondeterministic agree=1 disagree=2; `IA_SELFTEST pass=0 fail=4` | Agreement calculation inverted; named checks fail. |
| pin-watch | KILLED, rc=1 | numeric-order/build-numbers newer=3; current newer=1/status=behind | Right off-by-one: counts pinned tag itself as newer. |
| digest-ledger | KILLED, rc=1 | base blob=130 unknown=0; regressed blob=0 unknown=129 | Right blob-digest collection disabled. Related type-dispatch constant. |
| hexrun-census | KILLED, rc=1 | base lane_oid=283 unknown=0; regressed lane_oid=0 unknown=280 | Right lane-OID recognition disabled. 40→41 is the actual length predicate, not an unrelated constant. |
| append-only-audit | KILLED, rc=1 | `AOA_SELFTEST pass=50 fail=1`; FAIL binding-v4 | Right non-wildcard self-path binding inverted. |
| live-receipt-replay | KILLED, rc=1 | FAIL match / v5-match etc.; `mism=['outcome:pass->pass']` | Right outcome comparison inverted: false-positive mismatch on equal outcomes. |
| live-ollama-lifecycle | KILLED, rc=1 | verdict FAIL; running-exe-digest passed=false, ready/version/listener-owned passed=true | Right running-executable digest check. |

### Pattern provenance finding

Context's final summary is rebuilt in `finally` and printed regardless of setup failure.
`all([])` is true, so the shipped regression does not touch the signal named in the pattern:
base AND regressed stdout contain `"all_ports_closed": true` with cells=0/observed=0.
The counter correctly uses its receipt/exit classifier instead. The mutated model check
runs before the host-idle gate, so no K1 cell is exercised by that sensitivity witness.
On a busy host, an edit confined after the idle gate is unreachable [code-path inference].
This is a scope limit of the witness, not evidence that the classifier accepted the wrong refusal.

## Counter flip-logic mutants

Baseline was met=True, so no baseline-failure kill is claimed.
Each variant was run against the same pinned tip. Exact counter stdout lines follow below.

| Variant | Mutation | Verdict and deciding check |
|---|---|---|
| M1 | Remove compile/except guard in apply_regression | **KILLED**; regress/syntax-break escapes; controls_rejected=119/120. |
| M1b (extra) | `flipped[cap] = st in ('flipped', 'regress-syntax')` | **SURVIVED at clean tip, latent/inert there**; 120/120. Do not call this an exercised false acceptance. Materialization below remains rejected. |
| M2 | flip_status accepts mutated outcome equal to base outcome | **KILLED**; flip-unchanged and flip-busy-unchanged escape; flip=9/11, controls_rejected=118/120. |
| M3 | rc==124 explicitly returns false/timeout in classify | **SURVIVED, outcome-equivalent**; 120/120. Pristine already credits timeout as false→flipped; real hang probe below establishes this is reachable. |

### Noncompiling regression materialization

Committed only the pin-watch TSV replacement with a missing closing parenthesis in the fixture.
Pristine reports regress_flipped=11/12, printers_rejected=11/12; baseline fails and controls
are withheld. M1b inflates both fields to 12/12, but the run **still rejects**: its baseline
plan contains regress-syntax, so regress/syntax-break cannot receive differential credit
(`expect not in base` fails). Result: 119/120, met=False. Thus this materialized M1b is
**KILLED overall**, despite incorrect flip/printer field accounting. No accepted bad tip claimed.

### Actual timed-out regressed execution (not just a synthetic outcome)

`hang.py` imports the shipped counter, sets RUN_TIMEOUT=15 as a disclosed feasibility knob
(shipped value 900), and overlays pin-watch's unique release_tags assignment with
`__import__("time").sleep(1200)` before the assignment. Uses shipped Runner/classify/flip_status.
Observed in `hang_out.txt`:

    base  : rc=0 outcome=true
    hang  : rc=124 out_marker=True outcome=false reason=pattern-or-rc
    flip_status(base='true', reg='false') -> 'flipped'
    => row credited as flipped: True

A killed/hung regressed process therefore supplies flip credit without producing its own
verdict. This probes the shipped scoring path with a shortened wait, **not** an end-to-end
met=True receipt for a hanging TSV tip under the shipped 900-second bound.
No rc=124/TIMEOUT negative control appears among the counter's 120 controls.
Suggested detector extension: distinguish timeout/execution error from semantic false and
plant a timeout outcome through the same flip-accounting path.
`probe_out.txt` also confirms timeout credit for plain and context specs; its A syntax probe
is inapplicable (find `def (` is absent) and is NOT evidence of syntax handling.

## Second regressions for three weakest witnesses

Ranking here is by attribution quality: context (setup/classifier-only), sources (crash),
digest (aggregate-only and a distinct rc-only failure channel). These are proposals, not lane edits.
Each find substring was measured to occur **exactly once** in its pinned tool and compiled/applied.
Each candidate was actually run with that row's template via `cand.py`.

| Row | Find → replace | Actual result |
|---|---|---|
| context-capacity-receipt | `'other_pids_seen': seen,` → `'other_pids_seen': [],` | base host-busy; reg rc=2/false reason=seen-empty; pattern retained; flipped. Targets busy-proof PID evidence rather than unrelated setup refusal. Busy-host-only; not a portable idle-host replacement. |
| sources-registry | `if old[c] != new[c]` → `if old[c] == new[c]` | base true; reg rc=1/false, pattern absent; 17/45, wrong violation sets rather than removed-row TypeError. Broad but clean semantic inversion. |
| digest-ledger | `elif cls == "unverifiable":` → `elif cls == "unverifiable" and False:` | base true; reg rc=1/false, pattern **retained**; unverifiable=0 ledger_bad=7 unknown=0. Flips via exit status, showing printed unknown=0 alone does not carry the verdict. |

Additional verified sibling: hexrun-census unique find
`if len(token) == 32 and token in self.md5s:` → append ` and False` before `:`;
base true → reg rc=1/false, pattern absent, flipped. This targets a distinct resolver branch.

## Exact counter stdout (one line per execution)

M1:

    tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=119/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=10/11,selftest=1/1,tally=8/8,work=3/3] met=False

M1b clean-tip:

    tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True

M2:

    tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=118/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=9/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=False

M3:

    tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True

Pristine broken-TSV:

    tip=b4da6e1b7d11 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=11/12 printers_rejected=11/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=0/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[] met=False

M1b broken-TSV:

    tip=b4da6e1b7d11 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=119/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=10/11,selftest=1/1,tally=8/8,work=3/3] met=False

## Restoration and limitations

`hashes.json` records every mutant SHA-256 and `restoration.json` records exact restored bytes.
Pristine SHA-256: `c8b725e57f6e761735e832d127ec6df622d4a9dff09893b5fa31131c64d93e2e`.
Every mutant copy was overwritten with those pristine bytes; restored full counter run:
exit 0, 120/120, met=True, same line as baseline below. Lane counter matches that SHA-256;
no lane tool or registry edit. Scratch clones/fixtures were removed after evidence preservation.
The first asynchronous baseline launcher produced no complete receipt; a fresh, unbounded
baseline completed in 24 seconds and supplied the actual baseline. No baseline-failure kill.
A failed evidence re-export of hang.py hit a reused work directory; the successful exported
hang receipt uses a fresh directory. No failed re-export is counted as behavioral evidence.

Self-evaluation: accuracy 4 (equivalent/latent survivors explicitly separated), completeness 4
(timeout is a shortened-bound scoring probe, not a 900-second full counter receipt), clarity 4
(two reporting levels distinguished), actionability 4 (concrete control extension and unique
candidate edits), conciseness 3 (long counter lines required). Average 3.8; improvements:
add a timeout control and keep semantic failure separate from execution failure. User-facing
findings are scoped evidence, not a claim verdict.

Pristine/restored counter line:

tip=23b3fdb1a925 population=12 covered=12/12 mismatches=0 pinned=13/13 deps_pinned=2/2 regress_flipped=12/12 printers_rejected=12/12 idle_ok=1 work_reuse_refused=1 closure_ptr=1 recon_mismatches=0 tally_disclosed=8/8 tally_selftest=1 sens_selftest=4/4 controls_rejected=120/120 errors=0 recon[closure_ptr=1,mismatches=0,maxN=64,met=True] tally[56:disclosed:shortcut+survivor,57:disclosed:shortcut+survivor,58:disclosed:survivor,59:disclosed:shortcut,60:disclosed:shortcut,61:disclosed:no-falsify,62:disclosed:no-falsify+shortcut,63:ok] families[canon=4/4,closure=5/5,flip=11/11,gate=16/16,idle=21/21,pattern=5/5,pins=5/5,printer=2/2,reconciler=11/11,registry=17/17,regress=11/11,selftest=1/1,tally=8/8,work=3/3] met=True
