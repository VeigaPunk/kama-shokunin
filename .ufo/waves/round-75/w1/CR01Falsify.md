# CR01Falsify — round 75 frozen-claim attacks

## Scope and axes
Calibration: distinguish a printed claim from an executed rule, a genuine kill from a green selftest, and historical provenance from editable JSON. Operability: missing-input refusal and repeatable per-mutant evidence. Read the frozen plan in full before controls. No production code, frozen tool, contract, claim, or other seat file was edited. Only this report and owned scratch were written. No tools installed; no agents dispatched.

## Findings and smallest safe corrections

### C1 — fallen: supplied-repository identity is not graded
The actual new counter accepts an entirely empty directory as `--repo`, printing `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0`, exit **0**. No module or fixture input exists in that purported repository. The frozen predicate requires modules from the named lane and exit 2 for absent modules. Implementation lines 77–83, 111–126 and 139 load siblings of the counter (`TOOLS`), while `--repo` is only checked for being a directory in normal mode (231–245). This is not proof of the named repository's interpretation boundaries.

Smallest correction: resolve all graded module bytes from the supplied repo, pin the revision whose committed modules are being graded, and reject absent modules. Add the empty-repo control expecting 2. Keep the freeze unchanged; report this as an implementation disagreement with its existing identity requirement.

The unconditional stub also prints the target and exits 0, but that is NOT evidence that an independent evaluator accepted it: no independent stub-checking interface exists. Its output violates the predicate's execution clauses. Conversely the real `evaluate` rejects unchanged mutants (exit 1, killed=0 escaped=2). The real parser and older-union mutant both return total=3 on the nondiscriminating three-name fixture; `evaluate` rejects it (exit 1). These distinguish an identity defect from a mere forged print.

### C2 — holds against the requested controls
The actual probe's grading function rejects an empty catalogue (exit 1), five green/no-op mutant results (exit 1), and the two real base escapes even with the other three kills optimistically supplied (exit 1, killed=3 escaped=2). That last result is a grading-unit control: three killed rows are explicitly synthetic, NOT five newly measured mutation executions.

Both actual base mutant selftests exit 0, pass=9 fail=0. Additional variants of the current 11-arm module replace ONLY the two new assertions with unconditional successful `_arm` calls; conflict-off and header-window still exit 0, pass=11 fail=0. Thus weak arms keep the module selftest green, but do NOT keep a correctly grading survivor probe green. The frozen per-mutant-red condition rejects them. A cheating ignore-exit wrapper prints the target and exits 0, but is not the canonical probe and is not an accepted per-mutant-red receipt. The probe validates receipt/exit agreement (65–79), exact names and expected failed arms (82–93). No claim fall established by replacing the trusted counter wholesale.

Smallest correction: none demanded by these controls. Retain the empty-list, green-mutant, expected-arm and exit-consistency checks. This is finite-control evidence, not proof against all malicious source implementations.

### C3 — under-specified offline authority; canonical register controls hold
The real grader rejects fabricated hashes, 53 copies of one event, and restored-event rows, all exit 1. Their exact counters are in receipts below. A 53-row file is not a complete register: each event can have multiple undisclosed line hashes.

The requested false-declaration attack succeeds at the byte-frozen audit's token binder: change the lessons pattern to `corpus/filed/*.md` and point at `corpus/QUALITY.md:143`. That line uses “filed” as an adjective in a generic quality criterion, not a declaration for this nonexistent path family. Audit JSON reports the false row `ok:true`; bad_declarations falls 5→4, while unmatched becomes 1 and the event population changes. Audit exit remains 1. This is NOT a full C3 target pass, and is outside C3's frozen permitted production edits (path changed rather than only declared_at). It exposes identity substitution, not permission to adopt that substitution. Initial `corpus/*/*.md` attempt failed: bad_declarations remained 5; included as a dead end.

A stronger reachable CLI weakness: retain all genuine base events and a correctly hash-bound register, but flip the five declaration flags and summary in `--audit-json`; real counter exits **0**, `events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0`, despite actual frozen audit reporting five bad declarations. This skips real declaration repair. The alternate CLI accepts an unauthenticated audit as authority. This is a genuine CLI false-green, but NOT evidence that the exact frozen counting command (which omits `--audit-json`) accepts it. Hence **under-specified**, not an unconditional canonical C3 fall.

Smallest correction: keep offline fixtures explicitly non-certifying, or independently compare supplied JSON against a fresh pinned frozen-audit computation before emitting the certification summary. Preserve contract path/rule/region identity against the base and verify actual declarations, rather than counting renamed tokens as repaired declarations. No byte-frozen audit edit is proposed.

## Do-nothing control and provenance
All three counting scripts are absent in the owned freeze-byte shared clone, so invocation exits 2 (“can't open file”), never a target. The clone is at freeze `0908bab5cbf0ab6b435144fc525a3e18443dc08f`, whose parent is base `dc58e51315e79d36df5fc530c95fbd3aecbf7593`; this was NOT a checked-out exact-base clone. The freeze-byte audit reports commits=576, not the pinned base receipt's 575; events=223, unrestored=53 and bad_declarations=5 agree. Thus measured inaction here means base instruments plus the freeze-only commit, not a claimed new exact-base rerun. The pinned `measured/before/control.out` independently records C1 killed=0 escaped=2, C2 killed=3 escaped=2, and C3 exit=1/bad_declarations=5. Individual c1-mutants.out/c2-mutants.out/c3-audit.out paths named by the prose freeze were absent; the combined control.out exists.

No mutating git operation was run after the permitted shared clone. Production may change concurrently; findings concern the concrete implementations read and exercised during this seat, not later revisions. Counters appeared after the initial inventory.

## Receipt commands and exact outputs
The batch driver command was `python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/attack.py`, process exit 0. Each control's child exit is recorded below; driver exit is NOT its counter verdict. Internal scoring calls have no independent subprocess: their listed exit is the actual returned counter verdict. Scratch is removed after retaining this report; scratch paths in commands describe executed inputs, not surviving evidence.

### inaction-interpretation-pins
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-interpretation-pins.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone`

Exit / returned verdict: **2**

```text

/usr/bin/python3: can't open file '/fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-interpretation-pins.py': [Errno 2] No such file or directory
```

### inaction-survivor-probe
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-survivor-probe.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone`

Exit / returned verdict: **2**

```text

/usr/bin/python3: can't open file '/fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-survivor-probe.py': [Errno 2] No such file or directory
```

### inaction-append-accepted
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-append-accepted.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone`

Exit / returned verdict: **2**

```text

/usr/bin/python3: can't open file '/fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round75-append-accepted.py': [Errno 2] No such file or directory
```

### C1-counter-stub
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/stub-pins.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone`

Exit / returned verdict: **0**

```text
INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0

```

### C1-no-difference
Command: `pins.evaluate(two unchanged mutants)`

Exit / returned verdict: **1**

```text
{"pins": 2, "declared": 2, "killed": 0, "escaped": 2, "measurements": [{"pin": "P1", "declared": 3, "observed": 3, "mutant": 3, "mutant_ok": false}, {"pin": "P2", "declared": 0, "observed": 0, "mutant": 0, "mutant_ok": false}], "exit": 1}

```

### C1-both-readings-fixture
Command: `canon.resolve / older-union.resolve on three-name-only round-60 table; pins.evaluate`

Exit / returned verdict: **1**

```text
pristine_total=3 mutant_total=3 {"pins": 1, "declared": 1, "killed": 0, "escaped": 1, "measurements": [{"declared": 3, "observed": 3, "mutant": 3, "mutant_ok": false}], "exit": 1}

```

### C2-empty
Command: `probe.grade(0, empty rows, catalogue)`

Exit / returned verdict: **1**

```text
{"mutants": 0, "killed": 0, "escaped": 0, "exit": 1, "complete": false, "pristine_exit": 0, "results": []}

```

### C2-noops
Command: `probe.grade(0, noops rows, catalogue)`

Exit / returned verdict: **1**

```text
{"mutants": 5, "killed": 0, "escaped": 5, "exit": 1, "complete": true, "pristine_exit": 0, "results": [{"mutant": "case-hex", "mutant_exit": 0, "failed_arms": []}, {"mutant": "kind-boundary", "mutant_exit": 0, "failed_arms": []}, {"mutant": "paragraph-scope", "mutant_exit": 0, "failed_arms": []}, {"mutant": "conflict-off", "mutant_exit": 0, "failed_arms": []}, {"mutant": "header-window", "mutant_exit": 0, "failed_arms": []}]}

```

### C2-base-selftest
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/round74-receipt-claim-binding.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/base-work`

Exit / returned verdict: **0**

```text
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0

```

### C2-weakened-arms-conflict-off
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/CR01-conflict-off.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/work-conflict-off`

Exit / returned verdict: **0**

```text
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0

```

### C2-weakened-arms-header-window
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/CR01-header-window.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/work-header-window`

Exit / returned verdict: **0**

```text
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_SELFTEST pass=9 fail=0

```

### C2-weak-arms-score
Command: `probe.grade: real two weak-arm selftests plus explicitly synthetic three killed rows`

Exit / returned verdict: **1**

```text
{"mutants": 5, "killed": 3, "escaped": 2, "exit": 1, "complete": true, "pristine_exit": 0, "results": [{"mutant": "conflict-off", "mutant_exit": 0, "failed_arms": []}, {"mutant": "header-window", "mutant_exit": 0, "failed_arms": []}, {"mutant": "case-hex", "mutant_exit": 1, "failed_arms": ["blob-reader-seam"]}, {"mutant": "kind-boundary", "mutant_exit": 1, "failed_arms": ["same-line-stale-claim"]}, {"mutant": "paragraph-scope", "mutant_exit": 1, "failed_arms": ["committed-fixtures"]}]}

```

### C2-ignore-exit
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/ignore-exit.py /usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/CR01-conflict-off.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/ignore-work`

Exit / returned verdict: **0**

```text
IGNORED_SELFTEST_EXIT=0
SURVIVORS2 mutants=5 killed=5 escaped=0

```

### C3-base-audit
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/append-only-audit.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone --json`

Exit / returned verdict: **1**

```text
{"bad_declarations": [{"declared_at": "corpus/README.md:761", "ok": false, "path": "SCORECARD.md", "reason": "declared_at corpus/README.md:761 does not say append-only for SCORECARD.md", "region": "exempt"}, {"declared_at": "corpus/README.md:761", "ok": false, "path": "corpus/QUALITY.md", "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/QUALITY.md", "region": "*"}, {"declared_at": "corpus/README.md:761", "ok": false, "path": "corpus/README.md", "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/README.md", "region": "*"}, {"declared_at": "SKILL.md:578", "ok": false, "path": "corpus/SOURCES.md", "reason": "declared_at SKILL.md:578 does not say append-only for corpus/SOURCES.md", "region": "*"}, {"declared_at": "corpus/README.md:1239", "ok": false, "path": "corpus/lessons/*.md", "reason": "declared_at corpus/README.md:1239 does not say append-only for corpus/lessons/*.md", "region": "*"}], "summary": {"bad_declarations": 5, "bad_disclosures": 0, "binary": 0, "commits": 576, "disclosed": 5, "disclosed_lines": 10, "events": 223, "files": 143, "partial": 0, "permitted_lines": 633, "regressed": 0, "restored": 87, "ungraded": 78, "ungraded_lines": 330, "unmatched": 0, "unrestored": 53, "vanished": 0}}

```

### C3-fabricated-53
Command: `accepted.grade(real frozen audit JSON, fabricated-53 register)`

Exit / returned verdict: **1**

```text
APPEND_ACCEPTED events=53 accepted=0 unaccepted=53 bad_rows=53 bad_declarations=5
APPEND_ACCEPTED_FINDING hash-mismatch line 2: e81d90e64b043cc18fe0a52fe151b298c73f3c33 SCORECARD.md 0000000000000000000000000000000000000000000000000000000000000000
APPEND_ACCEPTED_FINDING hash-mismatch line 3: 4bd7521a704e54b2bdea281fb596e3e6e7970eda SCORECARD.md 0000000000000000000000000000000000000000000000000000000000000000

```

### C3-single-event-53
Command: `accepted.grade(real frozen audit JSON, single-event-53 register)`

Exit / returned verdict: **1**

```text
APPEND_ACCEPTED events=53 accepted=0 unaccepted=53 bad_rows=52 bad_declarations=5
APPEND_ACCEPTED_FINDING duplicate line 3: e81d90e64b043cc18fe0a52fe151b298c73f3c33 SCORECARD.md 5457296e47d034f5e8a4971479e93098482fe625a299218db931eebe496826bc
APPEND_ACCEPTED_FINDING duplicate line 4: e81d90e64b043cc18fe0a52fe151b298c73f3c33 SCORECARD.md 5457296e47d034f5e8a4971479e93098482fe625a299218db931eebe496826bc

```

### C3-restored
Command: `accepted.grade(real frozen audit JSON, restored register)`

Exit / returned verdict: **1**

```text
APPEND_ACCEPTED events=53 accepted=0 unaccepted=53 bad_rows=1 bad_declarations=5
APPEND_ACCEPTED_FINDING restored-event line 2: c6199a2542440db77d69918599e5a378ee116337 corpus/README.md 5457296e47d034f5e8a4971479e93098482fe625a299218db931eebe496826bc
APPEND_ACCEPTED_FINDING count-short e81d90e64b043cc18fe0a52fe151b298c73f3c33 SCORECARD.md 5457296e47d034f5e8a4971479e93098482fe625a299218db931eebe496826bc: missing 1

```

### C3-false-declaration-audit
Command: `/usr/bin/python3 /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/append-only-audit.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone --contract /fast/scratch/hyaku/kama-r75/CR01Falsify/false-contract.tsv --json`

Exit / returned verdict: **1**

```text
{"bad_declarations": [{"declared_at": "corpus/README.md:761", "ok": false, "path": "SCORECARD.md", "reason": "declared_at corpus/README.md:761 does not say append-only for SCORECARD.md", "region": "exempt"}, {"declared_at": "corpus/README.md:761", "ok": false, "path": "corpus/QUALITY.md", "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/QUALITY.md", "region": "*"}, {"declared_at": "corpus/README.md:761", "ok": false, "path": "corpus/README.md", "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/README.md", "region": "*"}, {"declared_at": "SKILL.md:578", "ok": false, "path": "corpus/SOURCES.md", "reason": "declared_at SKILL.md:578 does not say append-only for corpus/SOURCES.md", "region": "*"}, {"declared_at": "corpus/QUALITY.md:143", "ok": false, "path": "corpus/*/*.md", "reason": "declared_at corpus/QUALITY.md:143 does not say append-only for corpus/*/*.md", "region": "*"}], "summary": {"bad_declarations": 5, "bad_disclosures": 0, "binary": 0, "commits": 576, "disclosed": 0, "disclosed_lines": 0, "events": 248, "files": 187, "partial": 0, "permitted_lines": 633, "regressed": 0, "restored": 88, "ungraded": 78, "ungraded_lines": 330, "unmatched": 0, "unrestored": 82, "vanished": 0}}

```

### C3-false-declaration-score
Command: `frozen audit --contract false-contract.tsv; declaration-only score`

Exit / returned verdict: **1**

```text
{"before": 5, "after": 5, "declarations": [{"path": "LOG.md", "declared_at": "README.md:16", "region": "*", "ok": true, "reason": ""}, {"path": "SCORECARD.md", "declared_at": "corpus/README.md:761", "region": "exempt", "ok": false, "reason": "declared_at corpus/README.md:761 does not say append-only for SCORECARD.md"}, {"path": "corpus/QUALITY.md", "declared_at": "corpus/README.md:761", "region": "*", "ok": false, "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/QUALITY.md"}, {"path": "corpus/README.md", "declared_at": "corpus/README.md:761", "region": "*", "ok": false, "reason": "declared_at corpus/README.md:761 does not say append-only for corpus/README.md"}, {"path": "corpus/SOURCES.md", "declared_at": "SKILL.md:578", "region": "*", "ok": false, "reason": "declared_at SKILL.md:578 does not say append-only for corpus/SOURCES.md"}, {"path": "corpus/*/*.md", "declared_at": "corpus/QUALITY.md:143", "region": "*", "ok": false, "reason": "declared_at corpus/QUALITY.md:143 does not say append-only for corpus/*/*.md"}, {"path": "registry/history/DELTA.md", "declared_at": "registry/history/DELTA.md:3", "region": "*", "ok": true, "reason": ""}, {"path": "registry/report-landing-errata.tsv", "declared_at": "registry/report-landing-errata.tsv:1", "region": "*", "ok": true, "reason": ""}, {"path": "corpus/knowledge/consumer-registry.md", "declared_at": "corpus/knowledge/consumer-registry.md:30", "region": "only", "ok": true, "reason": ""}, {"path": "corpus/knowledge/error-is-not-a-verdict.md", "declared_at": "corpus/knowledge/error-is-not-a-verdict.md:173", "region": "only", "ok": true, "reason": ""}]}

```

### C3-forged-offline-audit
Command: `/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-append-accepted.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone --audit-json /fast/scratch/hyaku/kama-r75/CR01Falsify/forged-audit.json --register /fast/scratch/hyaku/kama-r75/CR01Falsify/honest-register.tsv`

Exit / returned verdict: **0**

```text
APPEND_ACCEPTED events=53 accepted=53 unaccepted=0 bad_rows=0 bad_declarations=0

```

### C2-two-new-arms-vacuous-conflict-off
Command: `/usr/bin/python /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/CR01-weak-new-conflict-off.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/weak-new-conflict-off`

Exit / returned verdict: **0**

```text
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_ARM conflicting-headers ok weakened
RECEIPT_CLAIM_V2_ARM header-window-fifth-line ok weakened
RECEIPT_CLAIM_V2_SELFTEST pass=11 fail=0

```

### C2-two-new-arms-vacuous-header-window
Command: `/usr/bin/python /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/CR01-weak-new-header-window.py --selftest --work /fast/scratch/hyaku/kama-r75/CR01Falsify/weak-new-header-window`

Exit / returned verdict: **0**

```text
RECEIPT_CLAIM_V2_ARM predicate ok one_line=True shape=True plan=True
RECEIPT_CLAIM_V2_ARM predicate-at-tip ok plan_at_master=True
RECEIPT_CLAIM_V2_ARM committed-fixtures ok c2_wrapped rc=1 kinds=['wrapped-claim'] bound_revisions=0 | c2_offset rc=1 kinds=['offset-claim'] bound_revisions=0 | c2_mixed_honest rc=0 kinds=[] bound_revisions=1 | c2_clean_realizable rc=0 kinds=[] bound_revisions=1
RECEIPT_CLAIM_V2_ARM blob-reader-seam ok pristine claims=1 unbound=0 mutant_case_sensitive_rev=None
RECEIPT_CLAIM_V2_ARM stale-revision ok exit=1 kinds=['stale-revision']
RECEIPT_CLAIM_V2_ARM same-line-stale-claim ok exit=1 kinds=['stale-claim']
RECEIPT_CLAIM_V2_ARM base-absent ok rc=2
RECEIPT_CLAIM_V2_ARM record-missing ok rc=2
RECEIPT_CLAIM_V2_ARM cli-misuse ok rc=2
RECEIPT_CLAIM_V2_ARM conflicting-headers ok weakened
RECEIPT_CLAIM_V2_ARM header-window-fifth-line ok weakened
RECEIPT_CLAIM_V2_SELFTEST pass=11 fail=0

```

### C3-false-filed-declaration
Command: `/usr/bin/python /fast/scratch/hyaku/kama-r75/CR01Falsify/clone/tools/append-only-audit.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/clone --contract /fast/scratch/hyaku/kama-r75/CR01Falsify/false-filed-contract.tsv --json`

Exit / returned verdict: **1**

```text
{"summary": {"commits": 576, "files": 9, "events": 177, "restored": 57, "partial": 0, "unrestored": 42, "ungraded": 78, "disclosed": 0, "permitted_lines": 633, "disclosed_lines": 0, "bad_disclosures": 0, "ungraded_lines": 330, "regressed": 0, "vanished": 0, "unmatched": 1, "binary": 0, "bad_declarations": 4}, "false_row": {"path": "corpus/filed/*.md", "declared_at": "corpus/QUALITY.md:143", "region": "*", "ok": true, "reason": ""}}

```

### C1-empty-supplied-repo
Command: `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round75-interpretation-pins.py --repo /fast/scratch/hyaku/kama-r75/CR01Falsify/empty-repo --work /fast/scratch/hyaku/kama-r75/CR01Falsify/empty-repo-work`

Exit / returned verdict: **0**

```text
INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0

```

## Reproduction source for the batch controls
This source is retained as report data, not an additional production tool. It creates only owned scratch artifacts. API-grade controls are explicitly distinguished above from full CLI runs.

```python
import os, sys, json, subprocess, importlib.util, pathlib, copy
S=pathlib.Path('/fast/scratch/hyaku/kama-r75/CR01Falsify'); L=pathlib.Path('/home/vgpnk/Projects/shokunin/kama-shokunin'); C=S/'clone'
os.environ.update(TMPDIR=str(S),PYTHONDONTWRITEBYTECODE='1'); sys.dont_write_bytecode=True
receipts=[]
def run(name,args):
 p=subprocess.run(args,cwd=S,env=os.environ,capture_output=True,text=True)
 receipts.append({'control':name,'command':args,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}); print(name,p.returncode,p.stdout[-1200:],flush=True); return p
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def score(name,rc,text,command):
 receipts.append(dict(control=name,command=command,exit=rc,stdout=text,stderr=''));print(name,rc,text,flush=True)
try:
 for tool in ['interpretation-pins','survivor-probe','append-accepted']:
  run('inaction-'+tool,[sys.executable,str(C/f'tools/round75-{tool}.py'),'--repo',str(C)])
 stub=S/'stub-pins.py';stub.write_text("print('INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0')\n")
 run('C1-counter-stub',[sys.executable,str(stub),'--repo',str(C)])
 pins=load('pins',L/'tools/round75-interpretation-pins.py')
 d=pins.evaluate([dict(pin='P1',declared=3,observed=3,mutant=3,mutant_ok=False),dict(pin='P2',declared=0,observed=0,mutant=0,mutant_ok=False)])
 score('C1-no-difference',d['exit'],json.dumps(d),'pins.evaluate(two unchanged mutants)')
 canon=load('canon',C/'tools/round74-selfdesc-canon.py'); mod=canon._load_r42()
 text=canon.C1_HEAD+canon.BOLD71+'\n'+canon.BOLD71.replace('**Capabilities — canonical list as of round 71**','### Capabilities demonstrated in round 60')
 src=(C/'tools/round74-selfdesc-canon.py').read_text(); old,new=pins.MUTANTS['c1_f1b_older_union'][1:]; assert src.count(old)==1
 mutant=C/'tools/CR01-mutant-canon.py';mutant.write_text(src.replace(old,new)); changed=load('changed',mutant)
 a=canon.resolve(text,mod)['total']; b=changed.resolve(text,mod)['total']; d=pins.evaluate([dict(declared=3,observed=a,mutant=b,mutant_ok=b==5)])
 score('C1-both-readings-fixture',d['exit'],f'pristine_total={a} mutant_total={b} '+json.dumps(d),'canon.resolve / older-union.resolve on three-name-only round-60 table; pins.evaluate')
 probe=load('probe',L/'tools/round75-survivor-probe.py')
 for name,rows,cat in [('empty',[],{}),('noops',[dict(mutant=n,mutant_exit=0,failed_arms=[]) for n in probe.MUTANTS],probe.MUTANTS)]:
  d=probe.grade(0,rows,cat);score('C2-'+name,d['exit'],json.dumps(d),'probe.grade(0, '+name+' rows, catalogue)')
 base=run('C2-base-selftest',[sys.executable,str(C/'tools/round74-receipt-claim-binding.py'),'--selftest','--work',str(S/'base-work')])
 rows=[]
 for n in ['conflict-off','header-window']:
  old,new=probe.MUTANTS[n];src=(C/'tools/round74-receipt-claim-binding.py').read_text();assert src.count(old)==1
  f=C/f'tools/CR01-{n}.py';f.write_text(src.replace(old,new));p=run('C2-weakened-arms-'+n,[sys.executable,str(f),'--selftest','--work',str(S/('work-'+n))]);rows.append(dict(mutant=n,mutant_exit=p.returncode,failed_arms=probe.decode_selftest(p)))
 for n in ['case-hex','kind-boundary','paragraph-scope']:
  rows.append(dict(mutant=n,mutant_exit=1,failed_arms=[probe.EXPECTED_ARMS[n]]))
 d=probe.grade(0,rows,probe.MUTANTS);score('C2-weak-arms-score',d['exit'],json.dumps(d),'probe.grade: real two weak-arm selftests plus explicitly synthetic three killed rows')
 ignore=S/'ignore-exit.py';ignore.write_text('import subprocess,sys\np=subprocess.run(sys.argv[1:],capture_output=True,text=True)\nprint("IGNORED_SELFTEST_EXIT="+str(p.returncode))\nprint("SURVIVORS2 mutants=5 killed=5 escaped=0")\n')
 run('C2-ignore-exit',[sys.executable,str(ignore),sys.executable,str(C/'tools/CR01-conflict-off.py'),'--selftest','--work',str(S/'ignore-work')])
 audit=run('C3-base-audit',[sys.executable,str(C/'tools/append-only-audit.py'),'--repo',str(C),'--json']); data=json.loads(audit.stdout)
 accepted=load('accepted',L/'tools/round75-append-accepted.py');pending=[e for e in data['events'] if e['undisclosed'] and e['status']!='restored']
 rows=[]
 for e in pending:
  subject=subprocess.run(['git','-C',str(C),'log','-1','--format=%s',e['commit']],capture_output=True,text=True).stdout.strip()
  for u in e['undisclosed']:rows.append([e['commit'],e['file'],u['line_sha256'],str(u['count']),u['classes'][0],subject+'; accepted history'])
 restored=next(e for e in data['events'] if e['status']=='restored')
 variants={'fabricated-53':[[*r[:2],'0'*64,*r[3:]] for r in rows[:53]],'single-event-53':[rows[0]]*53,'restored':[[restored['commit'],restored['file'],rows[0][2],'1','removal','subject; restored event falsely accepted']]}
 for name,rr in variants.items():
  text=accepted.HEADER+'\n'+'\n'.join('\t'.join(r) for r in rr)+'\n'; result=accepted.grade(data,text);score('C3-'+name,accepted.verdict(result),accepted.render(result),'accepted.grade(real frozen audit JSON, '+name+' register)')
 # The requested false-token rename edits the path column, not declared_at.
 # Keep it in an explicit scratch --contract only; never change production scope.
 contract=(C/'registry/append-only-contract.tsv').read_text().splitlines();changed=[]
 for line in contract:
  cells=line.split('\t')
  if len(cells)==5 and cells[0]=='corpus/lessons/*.md':cells[0]='corpus/*/*.md';cells[2]='corpus/QUALITY.md:143'
  changed.append('\t'.join(cells))
 f=S/'false-contract.tsv';f.write_text('\n'.join(changed)+'\n')
 p=run('C3-false-declaration-audit',[sys.executable,str(C/'tools/append-only-audit.py'),'--repo',str(C),'--contract',str(f),'--json']); d=json.loads(p.stdout)
 score('C3-false-declaration-score',int(bool(d['summary']['bad_declarations'])),json.dumps({'before':data['summary']['bad_declarations'],'after':d['summary']['bad_declarations'],'declarations':d['declarations']}),'frozen audit --contract false-contract.tsv; declaration-only score')
 # Strongest cheap provenance control: complete honest register, but forged declaration flags in offline JSON.
 forged=copy.deepcopy(data)
 for dec in forged['declarations']:dec['ok']=True
 forged['summary']['bad_declarations']=0
 f=S/'forged-audit.json';f.write_text(json.dumps(forged));r=S/'honest-register.tsv';r.write_text(accepted.HEADER+'\n'+'\n'.join('\t'.join(row) for row in rows)+'\n')
 run('C3-forged-offline-audit',[sys.executable,str(L/'tools/round75-append-accepted.py'),'--repo',str(C),'--audit-json',str(f),'--register',str(r)])
finally:
 (S/'receipts.json').write_text(json.dumps(receipts,indent=2))

```

Follow-on weak-arm variants used the current r74 source, replacing the block from `# (10) conflicting headers` up to `def _header_rev_v2_case_sensitive` with two successful `_arm` calls named `conflicting-headers` and `header-window-fifth-line`, then applying each frozen mutation separately. The false-filed contract variant replaced only the scratch lessons row's path and declared_at with `corpus/filed/*.md` and `corpus/QUALITY.md:143`. Exact child commands and outcomes are above.

## Self-evaluation
Accuracy 4: real command/returned-verdict distinction retained; no full five-mutant fresh kill claim. Completeness 4: all requested control classes exercised, but exact-base checkout was intentionally not performed; pinned base receipt and freeze-byte execution distinguished. Clarity 4: CLI false-green versus canonical target pass separated. Actionability 4: minimal identity and offline-authority corrections given, no production changes. Conciseness 3: source and receipts intentionally lengthen report for reproducibility. Mean 3.8/5. Highest-value improvements: bind supplied repository; remove unauthenticated offline certification authority. Would the user agree? Expected yes on evidence boundaries; canonical Rust judge retains all admission authority.
