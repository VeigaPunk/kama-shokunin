# rev=b06cc612711560c53eef3ec21484c6963601262f
# RV01 — frozen-predicate attack, round 76

Reviewed the full plan at freeze `1a85a991fce5b76b60f88a5cab3df98d253b1a4a`. Axes: operability, calibration, freshness; non-regression axes: depth, coverage, adjacency. This is a recommendation, not admission. No frozen rule or implementation was edited. No round-76 counter was run. No tool was installed, scratch created, runtime service invoked, or git mutation performed. `xd://lsp` is unavailable (device lookup returned “No such tool”); source inspection below is textual, not semantic LSP evidence.

## Findings, highest severity first

### High: C1's target contradicts its frozen record-path rule

`plans/round-76-claims.md:55–69` permits only self-description deltas in addition to round72's record set and explicitly retains `tools/` and `registry/` shifting. All three before receipts carry `rev=dc58e51315e79d36df5fc530c95fbd3aecbf7593`. Their ancestry to the base contains actual runtime/registry changes, not merely the first PROVINCE finding printed by the dry run:

| Commit | Non-record paths under the frozen C1 scope |
|---|---|
| `0908bab5cbf0ab6b435144fc525a3e18443dc08f` | `plans/round-75-claims.md` |
| `10f37171fb696c542586cbee96ea4a509ab74afc` | `registry/append-only-accepted.tsv`, `registry/append-only-contract.tsv`, `registry/append-only-declarations.md`, `tools/pre-report-gate.py`, `tools/round74-receipt-claim-binding.py`, `tools/round75-append-accepted.py`, `tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py` |
| `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a` | `registry/append-only-contract.tsv`, `registry/append-only-declarations.md` |

The affected paths are `.ufo/waves/round-75/measured/before/c1-mutants.out`, `.../c2-mutants.out`, `.../c3-audit.out`. Independently applying the declared extension yields **live=11, bound=6, unbound=2, shifted=3**, not bound=9/shifted=0. The committed dry run reports only the FIRST offending change; removing that first cause does not remove subsequent causes. An honest implementation cannot print the exact frozen after-line on these bytes. Later tool commits also remain non-record changes. Do not widen the rule or silently reclassify before measurements: disclose the contradiction under freeze discipline.

### Medium: the finite kill arms are not a complete anti-cheat admission rule

The tables distinguish predicate violations from *demonstrated arm coverage*. No selftest execution occurred. In particular C1 has no declared independent hardcoded-output arm; C2's “own cheat arm” is not specified enough in the frozen plan to establish its mechanics; C3's audit-fixture arms need to drive the production output path. A selftest that asserts an internal helper while the normal CLI prints constants does not certify that CLI. These are review gaps in the frozen kill rules, not claims that a particular landed module contains these defects.

## C1 table — operability

| Cheat | Frozen caught-by arm | Verdict |
|---|---|---|
| Hardcode the normal after-line while a separate selftest passes | No explicit production-CLI constant-printer arm | **Hole in kill coverage.** “prints one … line and exits 0 only when … population is classified” (52–56) prohibits the behavior but does not independently establish that classification occurred. Need an external changed-input observation; none is frozen as a distinct arm. |
| Strip every citation / select only fenced receipts | `fence-none-live`; `fence-unclosed` for an unterminated fence | Caught if these arms exercise the same normal CLI: empty live population is exit 2, not success. |
| Ignore only selected live citations while leaving a nonempty population, or fabricate `live_citations=11` | No population-completeness mutation named | **Hole in kill coverage:** empty-population detection does not establish that every live citation was collected. Exact printed totals alone are forgeable. |
| Treat a live script/non-receipt as harmless quoted history | `fence-live-nonreceipt` | Caught for the live non-receipt fixture, exit 1. |
| Admit every revision delta, including tools | `shift-tools` | Caught for that fixture. Registry-only and plan-only deltas are also forbidden but have no separately named arm. Selectively allow registry deltas and retain tools rejection: no stated arm necessarily catches it. |
| Recognize only unindented backticks; ignore tildes, indentation, closing-length or backtick-info rules | No explicitly enumerated CommonMark-boundary arms | **Hole in kill coverage:** “inside a CommonMark fenced block” (53–54) is more precise than the four listed arms. The committed dry-run helper itself recognizes only column-zero backticks; it is not general CommonMark proof. |
| Reclassify the three historical before receipts as bound merely because the first PROVINCE offender is exempt | `shift-tools` supports the general prohibition, but no historical-before arm is named | **Actual target contradiction**, above. An ordinary real tools/registry delta survives beyond the masked first finding. |
| Drop missing files / stale revisions rather than classifying them | No specifically named missing/stale arm | Forbidden by the predicate's stale/unreadable exit map; named-arm coverage unestablished. |

**Admission: hole: bound=9 is unreachable under the frozen scope on the committed before population; the kill list also lacks independent population/production-output coverage.**

## C2 table — calibration

| Cheat | Frozen caught-by arm | Verdict |
|---|---|---|
| Print `claims=8 mismatches=0 corrected=5 unbacked=0` without reading | “module's own cheat arm” | Declared caught, but arm input/assertions are unspecified here. Must independently perturb a fact through the same CLI, not merely test a helper. Not executed. |
| Discover zero facts / omit the tally or closure / grade ten checks as ten claims | Declared fixed eight-fact population; no individually named omission arm | Predicate rejects it, but **hole in named kill coverage**. The ten ids combine the two digest/line pairs into eight facts, not ten claims. |
| Append “corrected” with no value, no superseded locator, no date, before the original, or in another file | `correction-wrong-value` catches a wrong value, not necessarily these structural bypasses | **Hole in kill coverage.** Predicate (107–110) requires an appended dated block naming superseded bytes and a re-derived value; conditions (119–122) also require same-file/later placement. No frozen separate arm establishes all these conditions. |
| State a concrete wrong corrected digest | `correction-wrong-value` | Declared caught, remains a mismatch; no execution claimed. |
| Copy a previously correct digest but name another revision, use worktree bytes, or ignore the line-count half of a paired fact | No explicit revision-binding / paired-value arm | Forbidden by “from the blob at the revision it names” (107–110); **hole in named kill coverage**. |
| Back the LOG tally with a newly repeated assertion rather than a captured selftest receipt | No specifically named receipt-authenticity arm | **Predicate provenance limit.** “LOG gate-selftest tally's backing receipt” (106–107) does not define byte-level provenance or a command rerun. A text match alone cannot prove the selftest ran. Explicitly preserve distinction between an observed tally and a correction retracting an unsupported historical assertion. |
| Relabel stale original sentences without a value-bound later correction | Five independently recorded base discrepancies; `correction-wrong-value` for wrong values | Rejected by the predicate. The base evidence establishes the stale population, not every future correction-validation branch. |

**Admission: hole: declared wrong-value protection is useful, but correction structure, revision binding and tally provenance lack complete frozen kill coverage.** Base target arithmetic is supported; the after counter has not been exercised.

## C3 table — freshness

| Cheat | Frozen caught-by arm | Verdict |
|---|---|---|
| Print fixed totals without running the audit | Selftest audit-fixture arms | Declared caught only if changed fixture results reach the production CLI. Auditing once then ignoring its output is not independently excluded by the arm descriptions. |
| Accept all events / omit an event's row | `missing-row` | Declared caught when both row routes are removed. Does not alone prove all alternate routes are mutually exclusive. |
| Put one event in accepted AND exempt, or restoration AND disclosure, count it twice but hide duplication in totals | No named `duplicate` arm | Predicate (152–156) says “exactly once” and names `duplicate` in exit map, but **hole in named kill coverage**. Need classification precedence or overlap rejection, not merely category totals. |
| Copy audit numbers into a class row without checking class, sections, graded=0 | `wrong-class`; `wrong-count` | The explanatory kill rule explicitly requires these; legitimate copying of authoritative counts is NOT itself cheating when event binding, sections and graded=0 are independently checked. Section-set and graded>0 bypasses have no separately named frozen arms. |
| Use a row with wrong deleted-line count | `wrong-count` | Declared caught, exit 1. |
| Read only accepted register's most recent introduction / delete and re-add it | `rotation-reintroduced` | Declared caught for that fixture, exit 1. |
| Read only one register; exempt register alone is rotated or introduced earlier | No explicit two-register/earliest-exempt fixture | **Hole in kill coverage.** Predicate (156–158) says “earliest commit adding any accepted-history register”; rotation clarification (166–169) explicitly says “either register.” A fixture rotating only accepted does not establish the union. |
| Accept younger rows by treating ancestry as chronological timestamp order, or choose latest introduction | `rotation-reintroduced` partially covers it | Required graph-ancestor relation is explicit (167); branch/merge topology coverage is not established by the single named fixture. |
| Skip audit failures, missing register, or unmatched audit categories as zero population | Audit-fixture arms; `missing-row` partially | Exit 2 is frozen for audit failure/missing register. Specific arm coverage is not named; no runtime assertion made. |

**Admission: hole: two-register rotation and exclusive classification are required but not fully pinned by named frozen arms.** Arithmetic is correct; no claim of rotation-safe implementation or executed after-line.

## Re-derivations, actual commands and exits

All source objects were fetched using Python `subprocess.run(['git','-C',R,'show',REV+':'+PATH], capture_output=True)`, where `R=/home/vgpnk/Projects/shokunin/kama-shokunin`. All referenced successful `git show` and `git ls-tree` calls exited 0. Hashing/counting used the returned committed bytes, never the worktree.

### C1: target disagreement, not a pass

1. `git show 1a85a991fce5b76b60f88a5cab3df98d253b1a4a:.ufo/waves/round-76/measured/before/c1-fence-dryrun.out` — retrieval exit 0. Its stored observation is `cited=11 bound=6 unbound=2 shifted=3 stale=0`, tool exit 1; strip-all tool exit 2. These are stored exits, not new runs.
2. Fetched base `tools/round72-receipt-tip-binding.py`, `tools/append-only-audit.py`, `SCORECARD.md`, and `corpus/lessons/round-75.md` with `git show`. Executed their definitions in isolated Python namespaces (`__name__` not `__main__`); no file writes. Masked fenced lines using the audit's committed `fence_open`/`fence_close`, asserted both files end outside a fence, selected round75 with `_round_section`, resolved tokens with `_citations`/`_resolve_citation`, deduplicated paths, then evaluated each path using `_evaluate` with `default_record_paths(75)+['PROVINCE.md','SKILL.md','corpus/**']`. Analysis cell completed successfully. Result: **11 paths; 6 bound, 2 unbound, 3 shifted**. This is a frozen-function projection, NOT an execution of a new round76 counter.
3. Both unbound paths are exactly `.ufo/waves/round-75/assimilation/summary.out` and `.ufo/waves/round-75/controls/freeze.txt`; neither has a header among its first five lines. Six after receipts are bound (`append-only-audit.out`, `c1-pins.out`, `c2-survivors.out`, `c3-append-accepted.out`, `population.out`, `selftests.out`). All three before receipts remain shifted. `_rev_list` plus `_diff_paths` and `_record_match` produced the offending commit/path table above; underlying `git rev-list` and `git diff-tree --no-commit-id --name-only --no-renames -r -m COMMIT` calls succeeded.
4. Therefore **6+3 is not a legitimate bound=9 conversion**: the removed first PROVINCE finding masks other forbidden deltas. The committed dry-run is insufficient evidence for the claimed reachability.

### C2: eight facts / ten checks, five mismatches, one unbacked

At `c9ab73d842051db5f8320bced4357bf13cf14108`, fetched blobs using `git show REV:PATH` (each exit 0), computed `hashlib.sha256(stdout).hexdigest()` and `len(stdout.splitlines())`:

| Fact/check | Filed | Re-derived | Grade |
|---|---|---|---|
| SKILL digest / lines | `f18c9bcc7db5de4280fecd33337613b852fb650e757563621fa676745fe9a421` / 1736 | same / 1736 | match (one fact, two checks) |
| PROVINCE digest / lines | `0e8dc562f99367c3668c5ac2375c49828efa3152aa61fc235f28e896b271b5c4` / 322 | `af459acfa975d418a389f0ce19b8f1f40dd7e08d15c7eb0e9f2eb27e45d45697` / 322 | one mismatch (one fact, two checks) |
| SOURCES rows | 287 | 287 (`^\| S\d+\s*\|`, multiline) | match |
| Filtered knowledge entries | 45 | 45 (`git ls-tree -r --name-only REV -- corpus/knowledge/`, `.md`, exclude names containing `engine-sides` or `processes`) | match |
| LOG work tip | `b8ed256829589a13a0ba2249a8ae9e2b8800fb5a` | `c9ab73d842051db5f8320bced4357bf13cf14108` | mismatch |
| LOG mistake classes | four | numbered lesson entries 1,2,3,4,5 | mismatch |
| LOG selftest backing | `PRE_REPORT_SELFTEST pass=18 fail=0` | no committed round75 wave file contains this exact tally | mismatch AND unbacked |
| Axes calibration closure | round74 spotcheck | round75 spotcheck at base | mismatch |

Work-tip derivation used `git diff-tree` for every commit in `c9ab73d8..b06cc612`: none touches outside round72's default record paths. `git show --format=fuller --stat c9ab73d8` exits 0 and shows PROVINCE capability evidence changed; its path is non-record under the work-tip convention. Thus LOG's older tip is stale.

Tally derivation: `git ls-tree -r --name-only BASE -- .ufo/waves/round-75/` returned 83 files; fetched every committed blob and tested the exact tally substring; zero matches, all fetches successful. This establishes absence of that exact backing tally, not an unobserved historical selftest failure.

Closure evidence: freeze-committed `c2-closure.out` retrieval exits 0; its recorded counter lists thirteen closure members through round75, resolves newest round75, reports `row_current=false`, stored exit 1. Independently ran `git ls-tree -r --name-only BASE -- corpus/lessons/`, selected `round-N-verifier-spotcheck.md` with N>=63 and fetched all thirteen committed blobs (every call exit 0). Their first declared dates are 63:2026-10-28, 64:2026-10-30, 65–69:2026-11-01, 70–72:2026-11-03, 73–75:2026-11-04. Highest round on the latest date is 75. Extracted live `## Axes` calibration closure pointer names round74 (the same section also retains historical round71 evidence). Thus the newest-pointer mismatch independently re-derives from committed bytes; no new closure counter run was claimed.

Total: three fully matching facts + five mismatching facts = **8**; tally also contributes **unbacked=1**. No corrections were accepted or an after-line executed in this review.

### C3: actual audit rerun from committed source

Fetched BASE `tools/append-only-audit.py` (exit 0) and ran:

`subprocess.run(['python3','-c',committed_audit_source,'--repo',R,'--to',BASE,'--json'], capture_output=True, text=True, env={...,'PYTHONDONTWRITEBYTECODE':'1'})`

Actual audit exit **1** (expected unresolved audit history, not an evaluation failure). Parsed JSON: commits=591, files=146, events=232, restored=91, partial=0, unrestored=53, ungraded=83, disclosed=5, ungraded_lines=341, bad_declarations=0, regressed=0, vanished=0, unmatched=0, binary=0. Independently counted event `status` values: restored 91, ungraded 83, unrestored 53, disclosed 5. Python integer sum: **53+83+91+5=232**. This reruns the frozen existing audit, not a round76 counter. Freeze-committed `c3-register.out` records existing register grade `events=53 accepted=53`, stored exit 0; not rerun here.

## Causal separability and shared inputs

No actual absent-other-counter exit-0 proof exists in this review: the assignment forbids running not-yet-built counters, and C1's frozen exact target already fails the committed-data projection. Do not promote a dependency sketch to an executed result.

- C1 can use frozen round72/audit fence definitions without C2 or C3 modules. It shares SCORECARD and round75 lesson bytes with C2, and reads git history, including runtime/registry changes used by C3.
- C2 can derive blobs, rows, lesson counts, receipts and newest closure without invoking C1/C3. It shares SCORECARD, the round75 lesson, wave receipt storage and ancestry with C1; its corrections change self-record data.
- C3 can use the existing audit, contract/disclosures and accepted/exempt registers without C1/C2 modules. The audit covers self-record files whose changes C2 makes, including SCORECARD exempt-head changes.
- Consequently module-removal independence is plausible **[INFERENCE]**, but data/history independence is false. C1's receipt revision interval includes any subsequently committed C2/C3 tool/registry changes; those remain forbidden deltas. C3's exact events=232 is a base snapshot, not proof the final audit population cannot change. Counters must read one named committed revision consistently; working-tree mixtures are not an independence test.

## Axis harm evidence and residual gaps

| Axis | Possible harm | Evidence that would expose it |
|---|---|---|
| Operability | C1 rejects all valid historical before measurements or widens runtime scope to force green | Before-header ancestry table above; committed CLI result on both runtime and registry-only shifts |
| Calibration | Corrections are unbound assertions; constant counters receive credit; stale tally relabelled as an observed run | External changed-input controls, correction placement/revision cases, actual captured selftest stdout, exact receipt headers |
| Freshness | One-register cutoff reopens; overlaps hide events; final audit population drifts | Two distinct register introduction histories including exempt-first/rotation, duplicate classifications, final committed audit JSON |
| Depth | CommonMark claim rests on a simplistic backtick stripper | Tilde/indent/closing-length/backtick-info and unclosed-fence boundary fixtures; audit fence implementation reused rather than an independent narrower parser |
| Coverage | New module/fact/register branches remain unregistered or untested | Gate registry/QUALITY mapping and omission/paired-value/section-set fixtures; no score increase inferred here |
| Adjacency | Domain coverage is claimed from self-description-only work | Concrete cross-domain adopted source/application, rather than another instrument asserting coverage |

No runtime identity rerouting or resume path is changed by this predicate review; `resume_continuity_v1` preflights and canonical runtime admission are not applicable to the assigned three claims. Registered consumers being DEAD cannot be relabelled saturation or runtime recovery by these counters. Residual risk: landed implementations and final committed-tree after receipts remain unreviewed by this seat, deliberately; findings concern frozen predicates and committed reachability evidence.

Self-evaluation: accuracy 4 (committed-byte derivations distinguish projections from executed counters; future CLI semantics remain unobserved); completeness 4 (all claims/cheat categories covered, future implementation unexecuted); clarity 4 (separates stored exits from observed exits); actionability 4 (specific frozen contradictions/arm gaps, no unauthorized repairs); conciseness 3 (tables retain distinct missing-arm cases rather than collapsing them). Overall 3.8/5. Highest-impact recommendation: reject C1's exact after target under the current freeze; preserve this disagreement, and require external production-path attacks before any other admission.
