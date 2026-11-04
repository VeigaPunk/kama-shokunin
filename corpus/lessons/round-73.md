# Round 73 lesson — kama (2026-11-03)

Carry-in: the round-72 non-author closure (`corpus/lessons/round-72-verifier-spotcheck.md`) ruled round
72 **admitted** (both claims verified on re-measurement; scores held operability 8 / calibration 7) and
routed seven status-neutral defects. Its §6 item 1 and item 6 are mined below as mistakes 1 and 2, items
2 and 3 are this round's C2 and plan, item 4 is the L1's `## Gate`, item 5 is the round-72 report's
stale-lane line, and item 7 is the receipt-pairing class this round's control repairs. The freeze is
`plans/round-73-claims.md`: base `6e961996` (the round-72 spot-check commit), freeze commit `24bc96ad`;
the wave spec was frozen by `bc9e3059`.

This lesson is written before the report tip. It cites instrument, plan and round-72 paths only — no
round-73 wave receipt is cited as a backticked token — so nothing written here can make the round's own
C2 run red by citing a receipt whose header predates the instrument commits. `## Gate` and `## Wave`
belong to the L1 and are not created here.

## Claims

### C1 — calibration: the round-scope counter kills the three survivors its own claim recorded

Frozen predicate (verbatim; the same sentence is the module's `PREDICATE` and the receipt label):

> `python3 tools/round73-round-scope-cases.py --repo <lane> --round <N> --tip <rev>` prints one `ROUND_SCOPE_V2 round=<N> cases=6 findings=<f>` line and exits 0 only when the round's frozen claims plan `plans/round-<N>-claims.md` exists at `<rev>` with a first heading naming round `<N>`, no path outside the declared record allow-list is uncommitted in the primary worktree or in any linked worktree of the repository, no path under a `.ufo/waves/round-<M>/` directory with `M >= <N>` is git-ignored, and every initialized submodule worktree has no uncommitted or untracked content; it exits 1 naming every finding as `ROUND_SCOPE_V2_FINDING <case> <detail>`.

Fixed case population, in order: `label`, `stray`, `ignored` (inherited from the byte-frozen
`tools/round72-round-scope.py`, imported not copied) plus `worktree` (A5: every linked worktree's
`git status --porcelain -uall` graded like `stray`), `ignored-older-label` (A6: every
`.ufo/waves/round-<M>/` directory with `M >= <N>`, its ignored records graded) and `submodule` (A7:
every initialized submodule's own porcelain, plus the parent at `--ignore-submodules=none`). Exit map:
`0` clean, `1` findings, `2` could-not-evaluate (CLI misuse, not a git repository, unresolvable `--tip`,
a git failure, an unbuildable fixture). Kill rule: the committed fixtures `c1_a5`, `c1_a6e`, `c1_a7sub2`
each exit 1 naming their new case and `c1_clean` exits 0.

### C2 — operability: every tip claim in the record names the revision its receipt measured

Frozen predicate (verbatim; the same sentence is the module's `PREDICATE` and the receipt label):

> `python3 tools/round73-receipt-claim-binding.py --repo <lane> --round <N> --tip <rev>` prints one `RECEIPT_CLAIM_BINDING round=<N> cited=<c> bound=<b> unbound=<u> shifted=<s> stale=<t> claims=<k> unbound_claims=<j>` line and exits 0 only when the base `RECEIPT_TIP_BINDING` verdict for `<rev>` is green and every self-record line that cites a receipt and answers it with a tip claim (`at the tip`, `at the report tip`, `report tip`) names a receipt whose own `tip=`/`rev=` header equals `<rev>`; it exits 1 naming each base finding and each `RECEIPT_CLAIM_FINDING stale-claim <path> :: <line>`, and 2 when the base tool or the self-record cannot be evaluated.

Composition: the module shells out to the byte-frozen `tools/round72-receipt-tip-binding.py` (same
`--repo/--round/--tip`, same default record paths) and echoes `cited/bound/unbound/shifted/stale`; it
adds `claims` (citing lines that carry a tip token) and `unbound_claims` (those where at least one cited
receipt's header is not the resolved tip). Exit map: `0` clean, `1` findings (base or claim), `2`
could-not-evaluate (base tool absent or exit 2, unreadable self-record, CLI misuse). Kill rule: the B6
fixture exits 1 naming `stale-claim`; a receipt whose header equals the tip exits 0; the base tool's own
classes are unchanged.

### C3 — freshness: a host move is caught by a counter, not by a prompt

Frozen predicate (verbatim; the same sentence is the module's `PREDICATE` and the receipt label):

> `python3 tools/round73-province-host-drift.py --repo <lane>` prints one `PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>` line and exits 0 only when `PROVINCE.md` carries at least one `Round-<N> host-identity block (YYYY-MM-DD)` whose recorded triple (`uname -s`, `uname -m`, the `ID` field of `/etc/os-release`) equals the live triple, the newest block being the one graded; it exits 1 naming `PROVINCE_HOST_DRIFT_FINDING <no-block|stale-host> <detail>` when no block exists or the newest block's triple differs from the live one.

Block grammar: a paragraph whose first line matches `Round-<N> host-identity block (YYYY-MM-DD)` and
whose text carries the three triple tokens; the newest block in file order is graded, so a host move is
answered by appending a block, never by editing the old one. A kernel-only update does not move the
triple; a machine or OS change does. Exit map: `0` clean, `1` findings, `2` could-not-evaluate
(PROVINCE.md unreadable or not UTF-8, a live probe failed, CLI misuse). Kill rule: `c3_stale` (a Windows
triple) exits 1 naming `stale-host`, a block-less fixture exits 1 naming `no-block`, and the live lane
exits 0 once the round's block is appended — observed both ways this round (no block: `blocks=0 …
stale=1`, exit 1; after the append: `blocks=1 recorded=Linux/x86_64/arch live=Linux/x86_64/arch
stale=0`, exit 0).

## Mistakes

Class · evidence pointer · captured-by · fix.

1. **A tally copied between records instead of re-run.** The round-72 report and its `SCORECARD.md`
   section recorded 942 lines, 14 selftest arms and a `pass=14 fail=0` line for
   `tools/round72-receipt-tip-binding.py`; the committed instrument is 961 lines with 16 arm calls and
   its committed selftest receipt prints `pass=16 fail=0`, and the lane's own `LOG.md` and lesson already
   said 16. The class: a number that is a *run fact* was carried by prose from one record to the next,
   so the round's own report contradicted the bytes it cited. Evidence pointer:
   `corpus/lessons/round-72-verifier-spotcheck.md` §6 item 1, against
   `tools/round72-receipt-tip-binding.py`. Captured-by: the round-72 non-author closure.
   Fix: this round re-derives every tally it writes by executing the command — the three new modules'
   `--selftest` runs are this seat's own (`pass=26`, `pass=13`, `pass=9`, plus the gate's `pass=12`) and
   the registry rows carry those lines; no round-73 tally is copied from another seat's report, and the
   `Pre-report gate` row keeps its round-72 `pass=8` as a dated measurement rather than being rewritten
   with a number that belongs to the new bytes.

2. **A control's exit code was re-derived from its script because the receipt did not carry it.** The
   round-72 before-control receipts hold the counter lines only, so the claimed exit 1 was read back out
   of `return 1 if green == 3` in the control sources — a reader cannot get the verdict from the bytes
   the claim cites. The class: a receipt that stops one datum short of the claim it is cited for; the
   claim is then certified by re-reading code, which is exactly what a receipt exists to avoid.
   Evidence pointer: `corpus/lessons/round-72-verifier-spotcheck.md` §6 item 6, against
   `.ufo/waves/round-72/measured/before/round-scope-control-old.out` and
   `.ufo/waves/round-72/measured/before/receipt-tip-control-old.out`. Captured-by: the round-72
   non-author closure. Fix: round 73's control prints one `exit=<n>` per scored fixture and a final
   `# exit=` line (the round-73 control script score-survivors.py under the controls directory), and the committed before receipt
   ends `# exit=0`; the same command is the after-measurement. One reading rule comes with it: the exit
   alone is not the verdict — `*_SURVIVORS c1 base_green=3 … v2=absent` is the do-nothing state and the
   same line with `v2=present v2_killed=3` is the target met, so a citing line quotes the `SURVIVORS`
   line and not the exit.

3. **An instrument was re-pointed without moving its own harness, so its selftest was red on the bytes
   that landed first.** The pre-report gate's arm spec was re-pointed at `tools/round73-round-scope-cases.py`
   while its selftest still wrote its stub as `tools/round72-round-scope.py` and still expected
   `ROUND_SCOPE round=70 cases=3 findings=1`; the first run this seat made of
   `python3 tools/pre-report-gate.py --selftest` printed `PRE_REPORT_SELFTEST pass=0 fail=8`, every arm
   dying on `can't open file …/tools/round73-round-scope-cases.py`. The class is the round-72 mistake 6
   repeating in a new place: a selftest's own harness is an input, and a registry row that quotes a tally
   is quoting a run — an unrun check has not passed. Evidence pointer: `tools/pre-report-gate.py`
   (`ARM_SPECS` versus its stub writer and expected-detail strings). Captured-by: this seat's
   registry-row selftest run, before the row amendment landed. Fix: the stub target and the expected
   `ROUND_SCOPE_V2 … cases=6` strings moved with the arm (and four arms were added for the new classes);
   the re-run prints `PRE_REPORT_SELFTEST pass=12 fail=0`. The row's `pass=8` stays as the round-72
   measurement and the new 12 is filed as this round's run, not substituted into the old cell.

## Gate

Candidates considered this round, each with the source opened live on 2026-11-03 and the located
quote that grounds its `teaches` cell (CORPUS.md rule 1). Retained bytes live under the SCR01Sources seat directory (its source/ subdirectory), and its
fetch log is fetch.out.

| Row / candidate | Located quote (≤25 words) | Verdict |
|---|---|---|
| `uname(1)` — new row **S544**, `corpus/SOURCES.md:296`; `https://man7.org/linux/man-pages/man1/uname.1.html`, accessed 2026-11-03 (`curl` exit 0, 9552 bytes, retained sha256 `416919a6f65a025a81ede8c72c663c6e38bae6b5f02aaafdbba48f9b5afdc60a`) | "-s, --kernel-name print the kernel name" and "-m, --machine print the machine hardware name" (6 + 7 words; §DESCRIPTION, options `-s, --kernel-name` and `-m, --machine`) | **admit** — C3's triple rests on what each field names: the kernel name and the machine hardware name are the two stable components the block records, and neither is the kernel release |
| `gitmodules(5)` — new row **S545**, `corpus/SOURCES.md:297`; `https://git-scm.com/docs/gitmodules`, accessed 2026-11-03 (`curl` exit 0, 55719 bytes, retained sha256 `548638aab97fce72f79769c02aa05bf3ecbd25ffd058cb2b93b35b6090742bba`) | "The submodule will never be considered modified (but will nonetheless show up in the output of status and commit when it has been staged)." (24 words; §submodule.<name>.ignore, anchor `#Documentation/gitmodules.txt-submodulenameignore`) | **admit** — C1's A7 case needs the documented meaning of `ignore=all`: the parent status is the surface the base counter read, so the page's sentence is what makes the survivor a real hole rather than a counter bug |
| S175 re-opened — `https://git-scm.com/docs/git-merge-base`, accessed 2026-11-03 (`curl` exit 0, 41397 bytes, sha256 `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644`) | "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not." (25 words; §OPTIONS `--is-ancestor`) | **holds** — fetched bytes equal the row's retained bytes, the anchor sentence is present, and the page's revision list carries "2.56.0 no changes"; `used-by` extended |
| S542 re-opened — `https://git-scm.com/docs/git-status`, accessed 2026-11-03 (`curl` exit 0, 100062 bytes, sha256 `22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180`) | "is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" (17 words; §OUTPUT, "Porcelain Format Version 1") | **holds, byte-identical** — the fetched sha256 equals the sha256 the row's anchor cell records from round 71, so no cell changes; `used-by` extended |
| own-work receipts — the round's freeze plan, its control scripts and before receipts (the round-73 freeze control file pins their shas) | `SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`, `SURVIVORS c2 base_green=1`, `SURVIVORS c3 base_green=1` (control exit 0) | **no row** — `REJECTED: lane-authored control bytes are evidence a counter reads, not a learnable external source; flip: none` |
| `shoukuknow/merge/kama/` package | not re-opened this round; the id-collision check ran against the staged rows (the seat's collision file empty for S544/S545 against 142 staged ids) | **Assimilation: none** — `REJECTED: no entry from the package was re-grounded in round 73, so no row it carries is admitted; flip: a later round that re-opens an entry in full and passes the per-entry PROVINCE.md scope and QUALITY.md bar checks` |

Registry rows 283 → 285 (S544, S545). Id-collision check: 142 staged ids vs 283 registry ids,
`comm -12` empty for the adopted ids; no renumber map needed. The scratch-mirror census gate
(the seat's census.out) exited 1 with three `E11 missing used-by corpus/lessons/round-73.md`
findings at the append decision (this lesson did not exist yet), then exited 0 on the fresh mirror
and 0 on the lane file (`kama ok …`, 285 rows, 0 E-codes, warnings 104 × W04 + 1 × W01).

`used-by` changes, old → new (CORPUS.md rule 2):

| Row | old | new |
|---|---|---|
| S175 | `corpus/knowledge/self-assessment-at-writing.md`, `.ufo/waves/round-29/count-c1.py` | adds `corpus/lessons/round-72.md`, `corpus/knowledge/receipt-tip-binding.md` (round 72) and `corpus/lessons/round-73.md` (round 73) |
| S542 | `corpus/knowledge/pre-report-gate.md`, `corpus/lessons/round-71.md` | adds `corpus/lessons/round-72.md` (round 72) and `corpus/lessons/round-73.md` (round 73) |
| S544 | `corpus/knowledge/host-identity-drift-gate.md` | adds `corpus/lessons/round-73.md` (the lesson's Gate table cites the row it grounds) |

Spot-check status: the round-73 outside non-author closure does not exist yet at this revision; the
admit/reject sample above is the author's own gate and carries no outside verdict. Round 74's lesson
records the closure's agree/disagree for these two admits and the two rejections.

## Wave and L1 integration

WAVE-DONE received from the orchestrator: all 15 seats settled; no replacement or residual wave.
The results handoff has 15 named outputs (its schema supplies output/note rather than status/id).
Role mix: four executor, three scribe, one scout, one connector, one revenger, one reviewer,
two critic, one mutation-tester, one sentinel. Attack share is 4/15, counting reviewer/critics/
mutation-tester only. L1 held the planner seat; SCT01 supplied its bounded data walk.

EX01/02/03 built the three modules; EX04 wired the gate; SCR01 opened S544/S545 and re-opened
S175/S542; SCR02 wrote the two entries/map/criteria; SCR03 wrote the registry/LOG/lesson.
SCT01 reproduced the survivors; CON01 mapped sibling prior art; LAB01 probed git semantics.
RVW01's 26 attacks found no frozen-kill violation. MT01 applied 44 mutants: 34 killed,
10 survivors, each a selftest-coverage finding rather than a green original implementation.
CRT01/CRT02 identified the scalar-exit shortcut and the hash-fixed-point limit: require the
actual survivor fields, direct module runs, and explicit measured revisions. A committed
receipt cannot name its own containing commit, so the real record's claim pass is green only
with zero three-token tip claims; the injected-reader clean branch is not committed evidence.

L1 repaired CRT01 F3 within the frozen predicate, without changing the scorer: recursively
grade nested submodules and scan newer-round ignored directories in every worktree. Both
reconstructed F3 fixtures now exit 1. Existing 26-arm scope selftest remains green; direct
post-commit receipts also name the final module digest, so stale seat hashes are not final proof.

Remaining limits: line-wrapped tip claims and unlisted phrase variants are outside C2's token
population; host-block append-only preservation is ungraded (C3 has no base-revision option);
the allow-list is CLI-only and empty when the gate calls it; unreadable linked worktree is
exit 1 rather than the generic exit-2 git-error class. C1's calibration classification is
contested by CRT01: the before/after compares three disclosed self-assessment mismatches,
but the executable instrument itself grades git state. Freshness C3 is not an assigned-axis
requirement; no assignment change is claimed.

SEN01's scope snapshot reports two JSON artifacts without the mandated first-line revision;
they remain unchanged as original evidence and are not record-cited receipts. Required public
documentation fetches used HTTP; no local registered consumer or serving unit was contacted.
The dispatched item count is 15, correcting the context string that still said 14.

## Final measurement correction and verdict

Final instrument revision is 2e3ca86788c0ef041b34b329d58db6d7953513fc; after-receipts were
re-run there and landed at 7f6c96e3. Final selftests are 26/14/9 for scope/claim/host and 12
for the gate; the earlier 13-arm claim tally is historical. Scope live `cases=6 findings=0`,
gate `arms=6 failed=0 uncommitted=0`, registry `85/0/0`, surface counter `uncovered=0`.

The full frozen C2 clean clause is unprovable on committed bytes, though B6 is killed and
the real record can bind green with explicit receipt revisions and zero three-token claims.
This is an honest stop on full round admission, not a universal tip-claim pass. C3 detects
differences in its three fields only; different physical hosts can share them. The knowledge
entry explicitly supersedes its broad physical-machine-change statement. Append-only host
history, wrapped claim text and the canonical-heading parser defect remain disclosed limits.
