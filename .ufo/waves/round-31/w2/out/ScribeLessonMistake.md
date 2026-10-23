```RESULTS
Command: mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ScribeLessonMistake /tmp/kama-r31w2/ScribeLessonMistake
Exit code: 0
Verbatim tail: (no stdout)

Command: git status --short --untracked-files=all -- .ufo/waves/round-31/c1/c1-382d11b2.json .ufo/waves/round-31/c2/c2-382d11b2.json
Exit code: 0
Verbatim tail:
?? .ufo/waves/round-31/c1/c1-382d11b2.json
?? .ufo/waves/round-31/c2/c2-382d11b2.json

Command: git ls-tree --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/c1/c1-382d11b2.json .ufo/waves/round-31/c2/c2-382d11b2.json
Exit code: 0
Verbatim tail: (no stdout; no receipt paths listed)

Command: git init -q /tmp/kama-r31w2/ScribeLessonMistake/repo && git -C /tmp/kama-r31w2/ScribeLessonMistake/repo config user.name ScribeLessonMistake && git -C /tmp/kama-r31w2/ScribeLessonMistake/repo config user.email scribe-lesson-mistake@example.invalid && git -C /tmp/kama-r31w2/ScribeLessonMistake/repo commit --allow-empty -qm baseline; rc=$?; printf 'setup_exit=%s\n' "$rc"; exit "$rc"
Exit code: 0
Verbatim tail:
setup_exit=0

Command: sh /tmp/kama-r31w2/ScribeLessonMistake/receipt-gate.sh /home/vgpnk/Projects/shokunin/kama-shokunin 382d11b2107d335705875da1a4d889b074bd6fa6; rc=$?; printf 'gate_exit=%s\n' "$rc"; exit 0
Exit code: 0 (gate probe exit: 1)
Verbatim tail:
missing .ufo/waves/round-31/c1/c1-382d11b2.json
missing .ufo/waves/round-31/c2/c2-382d11b2.json
gate_exit=1

Command: git -C /tmp/kama-r31w2/ScribeLessonMistake/repo add -- .ufo/waves/round-31/c1/c1-382d11b2.json .ufo/waves/round-31/c2/c2-382d11b2.json && git -C /tmp/kama-r31w2/ScribeLessonMistake/repo commit -qm fixture-receipts && sh /tmp/kama-r31w2/ScribeLessonMistake/receipt-gate.sh /tmp/kama-r31w2/ScribeLessonMistake/repo "$(git -C /tmp/kama-r31w2/ScribeLessonMistake/repo rev-parse HEAD)"; rc=$?; printf 'gate_exit=%s\n' "$rc"; exit 0
Exit code: 0 (gate probe exit: 0)
Verbatim tail:
present .ufo/waves/round-31/c1/c1-382d11b2.json
present .ufo/waves/round-31/c2/c2-382d11b2.json
gate_exit=0

Command: sha256sum .ufo/waves/round-31/c1/c1-382d11b2.json .ufo/waves/round-31/c2/c2-382d11b2.json .ufo/waves/round-31/w2/out/ScribeLessonMistake/c1-c1-382d11b2.json .ufo/waves/round-31/w2/out/ScribeLessonMistake/c2-c2-382d11b2.json
Exit code: 0
Verbatim tail:
6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e  .ufo/waves/round-31/c1/c1-382d11b2.json
a8060b93233f305838986b7e99941687fbab7614b0e3dafa0b038252fec8d4dd  .ufo/waves/round-31/c2/c2-382d11b2.json
6b58b4340886f602fd5e2a2f2795d4e7abf50dad9252d033c41050beba80331e  .ufo/waves/round-31/w2/out/ScribeLessonMistake/c1-c1-382d11b2.json
a8060b93233f305838986b7e99941687fbab7614b0e3dafa0b038252fec8d4dd  .ufo/waves/round-31/w2/out/ScribeLessonMistake/c2-c2-382d11b2.json
```
FINDING: Draft — uncommitted measurement receipts · evidence: `preregistration-c3.json:3-8`; both inherited receipts are `??` in attempt 2 and absent from the `382d11b2` tree · captured-by: none · fix: block handoff unless the frozen tip contains each receipt (`git cat-file -e "$tip:$path"`). The gate reports missing/missing (exit 1) at the frozen tip, present/present (exit 0) after both paths are tracked in a scratch fixture.
LIMITS: This establishes only untracked working-tree receipts absent from the pinned tree; it does not establish that an orchestrator loss occurred. No judgment on census ordering or wave-1 writes. No counter rerun. Raw receipts and tracking log are saved beside this report.
