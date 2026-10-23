```RESULTS
Command: `mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ScribeTrend && set +e; /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin kama > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ScribeTrend/sources-census.log 2>&1; rc=$?; printf 'exit_code=%s\\n' "$rc"; cat /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-31/w2/out/ScribeTrend/sources-census.log; exit 0`
Exit code: wrapper 0; census 0.
Verbatim tail:
exit_code=0
kama	rows	191
kama	tier.A	186
kama	tier.B	2
kama	tier.C	3
kama	status.mined	172
kama	status.queued	8
kama	status.rejected	11
FLEET	rows	191
FLEET	tier.A	186
FLEET	tier.B	2
FLEET	tier.C	3
FLEET	tier.invalid	0
FLEET	status.queued	8
FLEET	status.mined	172
FLEET	status.rejected	11
FLEET	status.invalid	0
FLEET	missing	0
FLEET\tmissing\t0

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet HEAD -- corpus/SOURCES.md corpus/QUALITY.md corpus/knowledge/chat-adapter-outcomes.md corpus/lessons/round-30.md corpus/lessons/round-31.md`
Exit code: 0.
Verbatim tail:
bda324bbc5c1d7db93553adb13c5f380492c3c93

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin log --oneline 382d11b2107d335705875da1a4d889b074bd6fa6..HEAD && git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --stat 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD -- corpus/SOURCES.md corpus/QUALITY.md corpus/knowledge/chat-adapter-outcomes.md corpus/lessons/round-30.md corpus/lessons/round-31.md SCORECARD.md`
Exit code: 0.
Verbatim tail:
addeb57 round-31 attempt 2: C3 — SKILL instrument-registry row for the round-29 counter (gate 8/1 exit 1 -> 9/0 exit 0), round-31 re-run receipt
bda324b round-31 attempt 2: C3 freeze (instrument-registry coverage), C3 before receipt, wave-2 spec/plan/taskCall, round-start census
The `diff --stat` portion emitted no output.

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet HEAD -- SCORECARD.md`
Exit code: 0.
Verbatim tail: (empty output).

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/w1/out/ExecCensus/counts.txt`
Exit code: 0.
Verbatim tail:
.ufo/waves/round-31/w1/out/ExecCensus/counts.txt

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 382d11b2107d335705875da1a4d889b074bd6fa6:.ufo/waves/round-31/w1/out/ExecCensus/counts.txt`
Exit code: 0.
Verbatim tail:
SOURCES census at the frozen lane tree, before Round 31 rows are landed:
Rows matching the item’s `| S[0-9]` registry-row rule: 179 (S001–S179).
Tier-column distribution: A=174, B=2, C=3 (total 179).
Count operation: parsed `corpus/SOURCES.md` registry rows and tier column in Eval; completed successfully (no process exit code). The requested shell spelling is `grep -c '^| S[0-9]' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`; shell grep was not used due to the specialized-search policy.

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 382d11b2107d335705875da1a4d889b074bd6fa6 -- .ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt .ufo/waves/round-31/controls/RefRepair/receipt.txt`
Exit code: 0.
Verbatim tail:
.ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt
.ufo/waves/round-31/controls/RefRepair/receipt.txt

Command: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet 382d11b2107d335705875da1a4d889b074bd6fa6 HEAD -- .ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt .ufo/waves/round-31/controls/RefRepair/receipt.txt && git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet HEAD -- .ufo/waves/round-31/controls/CtlTypeGuess/receipt.txt .ufo/waves/round-31/controls/RefRepair/receipt.txt`
Exit code: 0.
Verbatim tail: (empty output).
```

FINDING: Expansion and the correction standard improved; quality remains bounded and discernment is not independently established for round 31.
- **expansion — improved:** The committed pre-round baseline records 179 registry rows (an Eval parse with no process exit); the current requested census returns 191, a +12 counted-row delta. `SOURCES.md` now has S180–S191, and `corpus/knowledge/chat-adapter-outcomes.md` is a new entry sourced to S180–S191, dated 2026-10-23 and bounded to the pinned b11755 fixture and its listed observability limits. Current census counts: 186 tier A, 2 tier B, 3 tier C; mined 172, queued 8, rejected 11; zero invalid/missing.
- **quality — improved (bounded):** `corpus/QUALITY.md` adds KQ41 requiring unique correction identities or a round-qualified key and reporting unexpressible failures. `SCORECARD.md` appends ten `p1:no-revision` correction rows; its three same-label C1 failures remain unexpressible. The committed `RefRepair` receipt's scratch counter run records `valid_corrections 10 false_corrections 3 unresolved 3 ... met False`; this is a stronger stated rule and trace, not a completed calibration result.
- **discernment — unprovable-but-better:** The committed `CtlTypeGuess` control receipt records only 1/12 guessed rows counted (`met False`), a self-run falsification signal, not an outside judgement. The non-author `round-30-verifier-spotcheck.md` explicitly assesses round 30 and says discernment was unchanged there; it cannot verify round 31. No non-author round-31 spot-check is in the named evidence.

LIMITS: The before count is a committed seat's Eval parse, not a census command receipt; the current shell census counts registry rows but does not prove the sources' semantic correctness. The control receipts are cited as committed evidence, not rerun by this scribe. No C1/C2 counter, live endpoint check, or outside round-31 spot-check was run here. The read-only commit comparison found no change to the named corpus/SCORECARD surfaces between dispatch commit `382d11b2` and current HEAD `bda324bb`; the later commits listed above therefore do not change these cited content surfaces.

Artifacts: `.ufo/waves/round-31/w2/out/ScribeTrend/sources-census.log`, `.ufo/waves/round-31/w2/out/ScribeTrend/git-provenance.log`, `.ufo/waves/round-31/w2/out/ScribeTrend/report.md`, `.ufo/waves/round-31/w2/out/ScribeTrend.md`.