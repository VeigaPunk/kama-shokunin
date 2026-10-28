# X03Regress2 - round 64 wave b, C2 sensitivity rows (3 caps)

Base tip f6a4ea9 (scratch clone, trees via `git archive`: T0 unmutated, T1 mutated by out/apply.py).
Deliverable: `out/X03Regress2/capability-regress-r64.part2.tsv` (4 TAB cells: cap, tool_path, find, replace; no header).
NOTE: `find`/`replace` carry LEADING SPACES (indentation) for two rows - the consumer must not strip cells; split on "\n" then "\t" only.
apply.py asserts `count(find)==1` in the tool (all 3: occurrences 1). Mutated files stay importable/parseable (ran).
Run templates executed exactly as in registry/capability-claims-r63.tsv (%T = tree, %S = scratch); log: out/X03Regress2/run1.txt.

| cap | edit (one line) | unmutated | mutated |
|---|---|---|---|
| gguf-declared-identity-replay | gguf-identity.py:364 `if key in result:` -> `if key in ():` (duplicate-JSON-key guard dropped) | exit=0, `"status": "passed"` PRESENT | exit=1, `"status": "failed"`, pattern ABSENT (case receipt_duplicate_json_key accepted) |
| instrument-agreement | instrument-agreement.py:75 `digest == results[0]["digest"]` -> `!=` (agreement count inverted) | exit=0, `IA_SELFTEST pass=4 fail=0` | exit=1, `IA_SELFTEST pass=0 fail=4` (pattern prefix still present, exit != 0 => verdict false) |
| context-capacity-receipt | kama-context-capacity.py:756 `if receipt['model_sha256'] != MODEL_SHA:` -> `==` | (host busy now) exit=2, stderr `host-not-idle-before-K1`, cc.json host_idle.other_pids_seen=[242776,1706355,3262613], error host-not-idle-before-K1 | exit=2, stderr `model-sha256-mismatch:270cba1b...`, cc.json `host_idle` absent (None), error model-sha256-mismatch |

## Context-capacity caveats (read before wiring the counter)
- Outcome is NEITHER host-busy NOR idle-pass in both host states: the model-sha check runs before wait_for_host_idle, so the mutant never reaches the idle gate. On a busy host it is exit 2 with error != host-not-idle-before-K1 and no `host_idle` block; on an idle host unmutated would be exit 0 while the mutant stays exit 2. I could only observe the busy host (3-4 foreign llama-servers present); the idle unmutated outcome was NOT observed here.
- IMPORTANT: the stdout summary `{"all_ports_closed": true, "cells": 0, ...}` is printed on ANY SetupError (all([]) is True) - including the refusal and the mutant. The pattern `"all_ports_closed": true` therefore does NOT distinguish refusal from idle-pass; the counter must classify by exit code + cc.json `error`/`host_idle` (not by pattern alone), and the mutant is only seen as flipped by that classification (exit 2 + error not host-not-idle + no printed foreign pid set), not by pattern absence. A one-line edit making the pattern itself absent would need to touch 'all_ports_closed': all( at lines 813/833 which occur twice (not unique), so I did not invent one.
- Supplementary mutant (not in the tsv; targets the busy-outcome rule "printed foreign pid set equals pgrep"): line 792 `'other_pids_seen': seen,` -> `'other_pids_seen': [],` (occurs once). Run on the busy host: exit 2, error host-not-idle-before-K1, host_idle.other_pids_seen=[] while pgrep -x llama-server showed 4 pids => busy outcome unprovable => should be rejected by that rule. Unaffected on an idle host (idle-pass remains), so it is a control for the host-busy branch only.

## Rows not invented / refusals
None refused; all three live targets fail by a single-line edit. The live-capable tool row (context-capacity) is the only one whose flip is by outcome classification rather than pattern.

## Install/tool record
No installs. No lane files edited; scratch rm'd at yield.
