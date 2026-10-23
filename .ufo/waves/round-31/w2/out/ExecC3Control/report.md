```RESULTS
Preparation command:
`mkdir -p /tmp/kama-r31w2/ExecC3Control /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Control && git clone --no-checkout /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r31w2/ExecC3Control/clone && git -C /tmp/kama-r31w2/ExecC3Control/clone checkout --detach 382d11b2107d335705875da1a4d889b074bd6fa6`
Exit: 0
Verbatim tail:
Cloning into '/tmp/kama-r31w2/ExecC3Control/clone'...
done.
HEAD is now at 382d11b round-31: SOURCES repair — S180-S191 relocated into ## Registry (census E12 exit 1 -> exit 0), lesson Mistakes row 4, census start/end receipts, two late seat artifacts

Run 1 — untouched clone:
Command: `set -o pipefail; python3 tools/gate-registry-check.py 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Control/01-baseline.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc"; exit "$rc"`
Exit: 1
Verbatim tail:
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1
EXIT_CODE=1
Raw log: `.ufo/waves/round-31/w2/out/ExecC3Control/01-baseline.log`

Between runs 1 and 2, in the scratch clone only, appended this five-column table row (counter path in Name; remaining columns blank):
`| .ufo/waves/round-29/count-c1.py | | | | |`

Run 2 — minimal row:
Command: `set -o pipefail; python3 tools/gate-registry-check.py 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Control/02-minimal-row.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc"; exit "$rc"`
Exit: 0
Verbatim tail:
registered 9 unregistered 0
EXIT_CODE=0
Raw log: `.ufo/waves/round-31/w2/out/ExecC3Control/02-minimal-row.log`

Between runs 2 and 3, removed that exact row from the scratch clone.

Run 3 — row removed:
Command: `set -o pipefail; python3 tools/gate-registry-check.py 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Control/03-row-removed.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc"; exit "$rc"`
Exit: 1
Verbatim tail:
unregistered .ufo/waves/round-29/count-c1.py
registered 8 unregistered 1
EXIT_CODE=1
Raw log: `.ufo/waves/round-31/w2/out/ExecC3Control/03-row-removed.log`

Between runs 3 and 4, in the scratch clone only, appended a row containing the tracked counter path in Name and nonexistent `.ufo/waves/round-999/count-c999.py` in Kind / entry command:
`| .ufo/waves/round-29/count-c1.py | .ufo/waves/round-999/count-c999.py | | | |`

Run 4 — nonexistent metadata path:
Command: `set -o pipefail; python3 tools/gate-registry-check.py 2>&1 | tee /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ExecC3Control/04-nonexistent-path.log; rc=${PIPESTATUS[0]}; printf 'EXIT_CODE=%s\n' "$rc"; exit "$rc"`
Exit: 0
Verbatim tail:
registered 9 unregistered 0
EXIT_CODE=0
Raw log: `.ufo/waves/round-31/w2/out/ExecC3Control/04-nonexistent-path.log`
```
FINDING: The target path's occurrence alone flips the gate from exit 1 to 0; removing it restores exit 1, and nonexistent metadata in the row does not prevent a pass.

LIMITS: This measures only the gate on a scratch clone at tip `382d11b2107d335705875da1a4d889b074bd6fa6`, with working-tree SKILL.md edits. It does not establish row-column accuracy, existence or validity of the fake path, committed-tip behavior after lane integration, or the full C3 predicate (counter digest and round-31 receipt). No tools were installed.
