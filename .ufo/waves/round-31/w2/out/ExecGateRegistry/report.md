```RESULTS
mkdir -p /tmp/kama-r31w2/ExecGateRegistry/base /tmp/kama-r31w2/ExecGateRegistry/tip /tmp/kama-r31w2/ExecGateRegistry/freeze /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry
exit=0; verbatim output: (empty)

Initial three fresh shared, no-checkout clone probes used the current lane copy of the gate:
{ git clone --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecGateRegistry/base && python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/base --rev 07794a4d30a54a60ebdff50ac76d12c6df40a0f1; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-base.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-base.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
Cloning into '/tmp/kama-r31w2/ExecGateRegistry/base'...
done.
unregistered .ufo/waves/round-29/count-c1.py
unregistered .ufo/waves/round-30/count-c1.py
registered 5 unregistered 2
EXIT_CODE=1

{ git clone --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecGateRegistry/tip && python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/tip --rev 382d11b2107d335705875da1a4d889b074bd6fa6; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-tip.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-tip.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
Cloning into '/tmp/kama-r31w2/ExecGateRegistry/tip'...
done.
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1
EXIT_CODE=1

{ git clone --shared --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecGateRegistry/freeze && python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/freeze --rev 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-freeze.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-freeze.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
Cloning into '/tmp/kama-r31w2/ExecGateRegistry/freeze'...
done.
unregistered .ufo/waves/round-29/count-c1.py
unregistered .ufo/waves/round-30/count-c1.py
unregistered .ufo/waves/round-31/count-c1.py
unregistered .ufo/waves/round-31/count-c2.py
registered 5 unregistered 4
EXIT_CODE=1

Attempt to filter ls-tree using git pathspec magic:
git -C /tmp/kama-r31w2/ExecGateRegistry/tip ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- ':(glob).ufo/waves/round-*/count-*.py' | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/tracked-tip.txt; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/tracked-tip.txt; exit 0
shell wrapper exit=0; git exit=128; verbatim output:
fatal: :(glob).ufo/waves/round-*/count-*.py: pathspec magic not supported by this command: 'glob'
EXIT_CODE=128

Captured the full tip tree (then filtered the saved text using functions.grep, since shell grep is disallowed):
git -C /tmp/kama-r31w2/ExecGateRegistry/tip ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/tracked-tip-tree-all.txt; rc=$?; printf 'EXIT_CODE=%s\n' "$rc"
exit=0; terminal output: EXIT_CODE=0; full stdout is tracked-tip-tree-all.txt. functions.grep used pattern ^\\.ufo/waves/round-[0-9]+/count-.*\\.py$ on that file; it returned the nine paths listed below (the tool response does not expose a numeric exit status).

git -C /tmp/kama-r31w2/ExecGateRegistry/tip show 382d11b2107d335705875da1a4d889b074bd6fa6:SKILL.md > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/SKILL-tip.md; rc=$?; printf 'EXIT_CODE=%s\n' "$rc"
exit=0; terminal output: EXIT_CODE=0; full stdout is SKILL-tip.md. functions.grep searched that snapshot for the nine counter paths; the report inventory records the matches.

Re-ran each measurement using the gate script extracted from its evaluated commit:
{ git -C /tmp/kama-r31w2/ExecGateRegistry/base show 07794a4d30a54a60ebdff50ac76d12c6df40a0f1:tools/gate-registry-check.py > /tmp/kama-r31w2/ExecGateRegistry/base/gate-registry-check.py && python3 /tmp/kama-r31w2/ExecGateRegistry/base/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/base --rev 07794a4d30a54a60ebdff50ac76d12c6df40a0f1; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-base-commit-code.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-base-commit-code.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
unregistered .ufo/waves/round-29/count-c1.py
unregistered .ufo/waves/round-30/count-c1.py
registered 5 unregistered 2
EXIT_CODE=1

{ git -C /tmp/kama-r31w2/ExecGateRegistry/tip show 382d11b2107d335705875da1a4d889b074bd6fa6:tools/gate-registry-check.py > /tmp/kama-r31w2/ExecGateRegistry/tip/gate-registry-check.py && python3 /tmp/kama-r31w2/ExecGateRegistry/tip/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/tip --rev 382d11b2107d335705875da1a4d889b074bd6fa6; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-tip-commit-code.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-tip-commit-code.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1
EXIT_CODE=1

{ git -C /tmp/kama-r31w2/ExecGateRegistry/freeze show 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e:tools/gate-registry-check.py > /tmp/kama-r31w2/ExecGateRegistry/freeze/gate-registry-check.py && python3 /tmp/kama-r31w2/ExecGateRegistry/freeze/gate-registry-check.py --repo /tmp/kama-r31w2/ExecGateRegistry/freeze --rev 0e6f8ed6891c09d5208ac1fdcb294ed9a842832e; } 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-freeze-commit-code.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc" | tee -a /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecGateRegistry/gate-freeze-commit-code.log; exit 0
wrapper exit=0; gate exit=1; verbatim tail:
unregistered .ufo/waves/round-29/count-c1.py
unregistered .ufo/waves/round-30/count-c1.py
unregistered .ufo/waves/round-31/count-c1.py
unregistered .ufo/waves/round-31/count-c2.py
registered 5 unregistered 4
EXIT_CODE=1
```
FINDING: The expected same-single-missing result is false: base has 2 unregistered paths, freeze has 4, and landing tip has 1 (`round-29/count-c1.py`); the tip inventory is 8 registered + 1 unregistered.
LIMITS: The gate checks exact path occurrence only; it does not validate registry-row columns, correctness, or measurement quality. These runs do not establish the non-gate parts of C3's predicate (counter digest and round-31 receipt).

## Gate behavior

At an explicit `--rev`, `tracked_counters()` runs `git ls-tree -r -z --name-only --full-tree REV`; it filters names with `^\\.ufo/waves/round-[^/]+/count-[^/]+\\.py$`. Thus the docstring's glob is one level beneath `.ufo/waves/`, but the implementation's two path segments accept any non-slash text in the `round-…` and `count-…` parts, not only numeric rounds. At default/no-`--rev`, it lists indexed tracked paths via `git ls-files -z`. For an explicit revision, `SKILL.md` comes from `git show REV:SKILL.md`; by default it reads root `SKILL.md` from the filesystem. A path is registered iff its full repo-relative path is a verbatim substring anywhere in that text; missing paths print sorted, then `registered R unregistered U`.

Exit map: `0` means zero unregistered paths; `1` means one or more unregistered paths; `2` means it could not evaluate (e.g. non-repository, bad revision, missing/unreadable `SKILL.md`, git error/timeout). It resolves the repository root with `git rev-parse --show-toplevel`; git subprocesses have a 30-second timeout.

## Three requested revision runs

The version-specific reruns above used a fresh `--shared --no-checkout` clone per revision and each revision's own `tools/gate-registry-check.py`. The `--rev` argument selects the tree and `SKILL.md` being measured. Exact gate outputs:

| Revision | Gate output | Gate exit |
|---|---|---:|
| Base `07794a4d30a54a60ebdff50ac76d12c6df40a0f1` | `unregistered .ufo/waves/round-29/count-c1.py`<br>`unregistered .ufo/waves/round-30/count-c1.py`<br>`registered 5 unregistered 2` | 1 |
| Round-31 freeze `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e` | `unregistered .ufo/waves/round-29/count-c1.py`<br>`unregistered .ufo/waves/round-30/count-c1.py`<br>`unregistered .ufo/waves/round-31/count-c1.py`<br>`unregistered .ufo/waves/round-31/count-c2.py`<br>`registered 5 unregistered 4` | 1 |
| Landing tip `382d11b2107d335705875da1a4d889b074bd6fa6` | `unregistered .ufo/waves/round-29/count-c1.py`<br>`registered 8 unregistered 1` | 1 |

The freeze differs materially from the tip: it still leaves the round-30 and both round-31 counter paths unregistered. The tip additions repair those three occurrences, leaving round-29 C1. The base predates round-31 counters and also lacks round-30 C1's occurrence. All three gate scripts from their evaluated commits produced the same result as the initial current-script probe.

## Tip counter inventory

Source: `git ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6`, filtered by the task's `^\\.ufo/waves/round-[0-9]+/count-.*\\.py$` pattern; registration judged by verbatim occurrence in the tip's `SKILL.md` snapshot.

| Tracked counter path | Occurs in tip `SKILL.md`? |
|---|---|
| `.ufo/waves/round-17/count-verdicts.py` | Yes |
| `.ufo/waves/round-25/count-c2.py` | Yes |
| `.ufo/waves/round-26/count-c1.py` | Yes |
| `.ufo/waves/round-27/count-c1.py` | Yes |
| `.ufo/waves/round-28/count-c1.py` | Yes |
| `.ufo/waves/round-29/count-c1.py` | No |
| `.ufo/waves/round-30/count-c1.py` | Yes |
| `.ufo/waves/round-31/count-c1.py` | Yes |
| `.ufo/waves/round-31/count-c2.py` | Yes |

Evidence files beside this report: `gate-{base,tip,freeze}.log` (initial probes); `gate-{base,tip,freeze}-commit-code.log` (revision-specific reruns); `tracked-tip-tree-all.txt` (full tree listing); `SKILL-tip.md` (tip registry snapshot); `inventory-filter-attempt.log` (failed Git pathspec attempt). No tracked lane files were edited.