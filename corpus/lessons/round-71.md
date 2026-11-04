# Round 71 lesson — kama (2026-11-03)

Carry-in: the round-70 non-author closure (`corpus/lessons/round-70-verifier-spotcheck.md`) ruled round 70
**admitted** (both claims verified on re-measurement; no axis harmed; scores held operability 8 /
calibration 7) and routed five status-neutral defects. Round 71's freeze is `plans/round-71-claims.md`
(base `f3ee44f4`, freeze commit `b43e71a8`); its claims are C1 calibration (`pre-report-gate`), C2
operability (`census-waiver-boundary`), C3 freshness (`province-host-claims`).

## Gate

| Row / candidate | Located quote (≤25 words) | Verdict |
|---|---|---|
| S542 (new row, tier A) `https://git-scm.com/docs/git-status` | "is guaranteed not to change in a backwards-incompatible way between Git versions or based on user configuration" (17 words; §OUTPUT → "Porcelain Format Version 1", anchor `#_porcelain_format_version_1`; page "git-status last updated in 2.53.0", change panel "2.54.0 → 2.56.0 no changes"; accessed 2026-11-03; retained bytes sha256 `22ff28ff73f83696c4a503e9c92e7a15f4ded2f91d96cc5668ee79db0a1b0180` at `.ufo/waves/round-71/w1/SCR02SourceRow/source/git-status.html`; quote-extraction receipt beside it) | admit — the version-1 porcelain record is the script-stable machine surface the pre-report cleanliness arm parses; a shape break is an upstream guarantee break, not a parser bug |
| S052 re-opened this round (`https://docs.pytest.org/en/stable/reference/exit-codes.html`) | "Exit code 5: No tests were collected" and "Exit code 0: All tests were collected and passed successfully" (7 + 10 = 17 words; §Exit codes, anchor `#exit-codes`; live fetch 2026-11-03, retained bytes sha256 `a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977`; the page still names no pytest version) | no new row — the URL is already S052 (a second row would be `W04 duplicate url` row inflation, CORPUS rule 4); only `used-by` changes, old→new: `…, corpus/lessons/round-70.md` → `…, corpus/lessons/round-70.md, corpus/lessons/round-71.md` |
| own-work receipts — `measured/before/pre-report-shortcut.out`, `measured/before/census-shim-control.out`, the five shims, `w1/EX03ProvinceClaims/kill*.out` | `SHORTCUT_CONTROL arms=4 failed=0 uncommitted=26`; `SHIM_CONTROL shims=5 accepted=5 rejected=0`; `PROVINCE_HOST_CLAIMS … uncovered=14` / `…_REWRITTEN qwen-coder-unit` | no row — outputs of the lane's controls and fixtures are evidence (D2 discipline), not opened learnable sources |
| the closest sibling instrument, kengaku `plans/round51_surfaces.py` | read only through the connector's header/registry scan (`w1/CON01OverlapInventory/overlap.md`); the source itself was not opened this round | no row — an adjacency finding recorded in `corpus/knowledge/cross-lane-scope.md`, not a source; kengaku owns its own gate |
| `shoukuknow/merge/kama/` package (65 entries, 142 staged rows) | `MERGE-REPORT.md` read; no staged entry was re-opened and re-grounded under CORPUS rule 1 this round | no admission — `Assimilation: none`; adoption waits for a round sized to re-ground each cited source with this lane's own access date and quote |

Id collision check (scratch, before any append): lane ids 281 (`grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}'`),
staged ids 142, **collisions 9** (S330, S333, S334, S335, S346, S347, S352, S353, S363), union max **S541**,
next unused **S542** (absent from both lists). No staged row is adopted this round, so no renumber map is
needed; the collision set is the reason a bulk append here would have been wrong (the package was built
against an older registry).

Census: `validate --root /home/vgpnk/Projects/shokunin kama` → exit 0 at round start (281 rows) and exit 0
at round end (282 rows, S542 appended; the transient E11s for the two sibling deliverables cleared when
`corpus/knowledge/pre-report-gate.md` and this lesson landed). Warnings unchanged (104 W04 + 1 W01).

## Mistakes

Class · evidence pointer · captured-by · fix.

1. **population premise assumed from a filename, not from the counter's declared rule** · the freeze
   expected gate-registry `registered 79 → 82` for three new tools; `tools/gate-registry-check.py`'s
   contract declares its population as `.ufo/waves/round-*/count-*.py` or `tools/round<N>-*.py`, so only
   `tools/round71-province-host-claims.py` enters it: measured `79 → 80`, while `tools/pre-report-gate.py`
   and `tools/census-waiver-boundary.py` are documented SKILL rows outside that population ·
   captured-by the gate's own docstring (read before trusting the delta) · fix: a frozen population
   delta names the counter's declared population command, and the report states the measured value even
   when it misses the freeze's expectation.
2. **an uncommitted-count metric that depended on directory collapsing** · the freeze first fixed
   `uncommitted=14` (plain `git status --porcelain` entries); the shortcut control's clone printed
   `uncommitted=2` because the whole `w1/out/` directory was one entry there, and only `-uall` gave the
   comparable 26-file count · captured-by the control's own printed count against the lane's
   (`.ufo/waves/round-71/measured/before/pre-report-shortcut.out`) · fix: the freeze names the metric
   `-uall` files and quotes both counts (26 files / 14 entries).
3. **a base receipt cannot use the tool's own `--base` rewrite check** · `tools/round71-province-host-claims.py
   --base b43e71a8 --corrections .ufo/waves/round-71/measured/before/PROVINCE-base.md` exits 2
   (`git show b43e71a8:<path> failed: exists on disk, but not in b43e71a8`): the tool resolves the
   corrections path relative to the repo at the base revision, and the base copy is new this round ·
   captured-by the receipt's own could-not-evaluate exit · fix: the before receipt passes the base blob as
   `--corrections` without `--base`; the after receipt passes `--base` against the live file.
4. **a probe root chosen by the tool, not by the round's scratch contract** · the first province run
   without `--scratch` created its NTFS fixture under `/tmp/r71-province-claims-…` (`tempfile.gettempdir()`
   honours `TMPDIR`, so this was not the committed-tool defect rule 4 names, but it is not the round's
   scratch root either) · captured-by the fixture path in the counter's own evidence line · fix: every
   counter/probe receipt in this round passes `--scratch /fast/scratch/hyaku/kama-r71/…`.
5. **a self-record row cited its tool's output before the tool was committed** · at 21:39 the SCORECARD
   calibration row cited `PRE_REPORT …` while `tools/pre-report-gate.py` was still untracked (sentinel
   observation, `w1/SEN01BoundaryAudit/audit.md`) · captured-by the sentinel's write-scope scan · fix: the
   row and the tool land in the same commit and the row carries a `run` fact the reconciler re-executes at
   the tip; the gate receipt records the command with its `--tip`.


6. **a gate that runs an instrument cannot be that instrument's own `run` fact** · the calibration row
   briefly carried `run python3 tools/pre-report-gate.py … → PRE_REPORT …`; the gate's first arm is the
   selfdesc reconciler, which executes every `## Axes` `run` fact, so the fact would spawn the gate again
   (recursion); SCR01's F1 probe found it before the commit and the fact is now a receipt pointer
   (`.ufo/waves/round-71/measured/after/pre-report-at-tip.out`) · captured-by the scribe's
   `run-fact-recursion-probe.out` and the reconciliation itself · fix: an instrument that composes
   another is cited by receipt, never by a `run` fact in the composed instrument's table; the same rule
   is why the boundary tool is not a `run` fact either (its case 7 runs the census, whose members include
   the reconciler selftest — a second recursion path).

## Ceiling

What the green receipts at the tip do not show. **C1:** the gate grades arm exits and one porcelain
class; an uncommitted `corpus/knowledge/` entry or a `tools/` edit is invisible unless it is one of the
five declared self-record paths, and a child that exits 0 on an unevaluable state still reads green (the
entry names this limit; CRT01's attack on it is recorded in the wave dispositions). **C2:** `killed=5`
means five named shims are rejected by named checks; it does not prove a sixth hole absent — RVW01's new
shims are the test, and a survivor is a routed defect, not a pass. The boundary also does not grade the
census's *population* (22 members) beyond the verdict line. **C3:** `uncovered=0` means every contradicted
claim has a later correction whose verdict matches a live probe **on this host at this instant**; the
probe table is tool-declared, so a surface the tool does not declare is ungraded, and a host move
re-contradicts the markers without touching the corrections. No claim says the registered consumers
serve: they keep their last recorded `DEAD` state and nothing was sampled.

Scores held operability 8 / calibration 7: C1/C2 repair and consolidate instruments the lane already
counts on; C3 re-derives a dated record. The repertoire grows by two rows, but no axis score moves.

Wave findings that are **not** folded into a claim (routed, not hidden): C1 — a wrong `--round` name
is a vacuous green, round work outside the wave dir and git-ignored files inside it are invisible to the
cleanliness arm (CRT01 S1/S2/S3); C2 — `m7` (the `waiver_keeps_not_evaluated` check forced true) survives
because no fixture isolates it (MT01 F2); C3 — `m6` (the correction-date guard dropped) survives because
every fixture dates its corrections at today (MT01 F1), and a duplicated tag paragraph reads as a false
red (CRT01 iv). Three C3 attack routes *were* repaired before the landing commit — base-marker paragraph
identity (`REWRITTEN`), calendar-date validation (S541's rule), exit 2 on an unusable `--scratch` — with
receipts in `measured/hardening/`; the attack receipts name the pre-repair sha (`1f6bb43a…`), so the
hardening is disclosed rather than presented as attacked. Each open item is a round-72 counter
amendment with its own killing fixture, never a widened claim this round.

## L1 integration addendum (round 71, measured at the report tip)

Wave dispositions (12 seats, one v1 wave; role mix 3 executor / 2 scribe / 1 scout / 1 connector /
1 reviewer / 1 critic / 1 mutation-tester / 1 sentinel / 1 revenger probe; attack share 5/12):

- **EX01PreReportGate** built `tools/pre-report-gate.py` (five arms, re-entry guard, 6-arm selftest) and
  the control/green fixtures; its findings D1–D5 (freeze `--round` label, invalid population command,
  `79 → 80` not 82, the recursion class, the count timing) are integrated here (annex, Mistake 1/6) and
  its D4 recursion guard is kept.
- **EX02CensusBoundary** built `tools/census-waiver-boundary.py` (7 cases, 19 selftest arms, embedded
  byte-pinned shims, per-check rejection names). Its case 7 was red at `e2b860c8` (`pass=21 fail=1`,
  the reconciler selftest) because the tip's record still carried the two defects C1 fixed; at the report
  tip the census is green and so is the boundary (final receipt below).
- **EX03ProvinceClaims** built `tools/round71-province-host-claims.py` (7-arm selftest; kill receipts
  flipped=1, wrong-tag=14, `REWRITTEN` exit 1) and generated the corrections draft that the L1's
  `PROVINCE.md` block follows.
- **SCR01KnowledgeEntry** wrote `corpus/knowledge/pre-report-gate.md` and found the recursion path (F1)
  that removed the gate from the `## Axes` run facts; it also flagged the coverage count 40 and F4
  (the gate is red until the round is committed — correct behavior).
- **SCR02SourceRow** opened S542 live, ran the id collision check (9 collisions with the staged package,
  next unused S542), validated the append on a scratch mirror (exit 0) before the lane write, re-opened
  S052 and extended its `used-by`. Its after-census E11s (two sibling deliverables absent at write time)
  cleared when the knowledge entry and this lesson landed.
- **SCT01HostCensus** re-derived all 16 host surfaces independently: 14 contradicted, 2 matching
  (`qwen-coder-unit`, `janitor-md`); it named the `ufo-src` two-condition ambiguity and the stale
  `qwen-coder-unit` rationale (no systemd) while the tag verdict holds.
- **CON01OverlapInventory** found souji/kasegi pre-report gates, mado's waiver policy, tameshi's
  arm-liveness and receipt-tip gate, and kengaku r51's manifest surface check; the overlap rules are now
  in `corpus/knowledge/cross-lane-scope.md`. It also inventoried the five inherited defects: #1 closed
  at the freeze, #4 closed in kind by C2, #2/#3/#5 carried by the r70-lesson corrections.
- **LAB01WaiverProbe** probed the census semantics: H1 (waiver covers a failing member) and H2
  (prefix/glob waiver) refuted; H3 (waived member still counted, `waived=1`) and H4 (no silent second
  call) confirmed on a byte-identical copy.
- **SEN01BoundaryAudit** proved no committed waiver invocation (`git grep` hits are prose/parser only),
  0 secret-shaped strings in the scoped populations, every worktree path inside the lane's expected set,
  and no service/consumer contact; its F1 (a SCORECARD row citing an unexecuted run) is resolved by the
  receipt-pointer form the row now uses.
- **RVW01C2Attack** built four new sixth-shim candidates (H1 waiver-covers-pass, H2 forged waived token,
  H3 silent second call, H4 phantom not-evaluated); all four are killed by named checks on the final
  bytes (`7c759633`), so C2 HELD. It also documented a version-skew: the earlier v1 bytes let H3/H4
  survive, which is why tool bytes and the tested sha are recorded in every receipt.
- **CRT01ClaimsAttack** found three C1 survivors (a wrong `--round` name is a vacuous green; round work
  outside the wave dir and git-ignored files inside it are invisible) and several C3 gaps. Three C3 gaps
  are repaired in the landed tool before this commit — base-marker **paragraph identity** (delete+re-add,
  body edit and date rewrite now print `REWRITTEN`), `datetime.date` calendar validation for correction
  dates, and exit 2 on an unusable `--scratch` root; receipts in `measured/hardening/`. The C1 survivors
  stay open and are routed to round 72 (the frozen kill rule does not name them).
- **MT01MutantGates** ran 19 mutants: C1 6/6 killed; C2 6/7 killed with one survivor (`m7`, the
  `waiver_keeps_not_evaluated` check has no isolating fixture); C3 5/6 killed with one survivor
  (`m6`, the correction-date guard has no fixture — the freeze's kill rule does not name it). Both
  survivors are coverage findings routed to round 72 (a selftest arm each, no predicate change).



Final receipts at the tip: Final receipts at the report tip (`4b284653`, all committed under `.ufo/waves/round-71/measured/after/`):
`reconciler-at-tip.out` (`mismatches=0 met=True`, exit 0), `newest-closure-at-tip.out`
(`row_current=true`, exit 0), `receipt-audit-at-tip.out` (`unresolved=0`, exit 0), `wlc-at-tip.out`
(`paths=5 clean=5`, exit 0), `pre-report-at-tip.out` (`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0`,
exit 0), `province-claims-at-tip.out` (`markers=11 tags=12 extra=4 contradicted=14 uncovered=0 exit=0`),
`sources-census-at-tip.out` (`kama ok`, exit 0), `boundary-at-tip.out`
(`BOUNDARY cases=7 killed=5 survivors=0`, exit 0). A second gate run at `1375f51c` is
`pre-report-at-final.out` (`PRE_REPORT round=71 arms=5 failed=0 uncommitted=0`, exit 0); the lane tip
`9458c3d7` equals `ls-remote origin refs/heads/master`. The pre-report receipt measured at `4b284653`
remains valid at the later tips: the only commits after it add receipts under
`measured/after/` (this lesson's final-receipts block is the one non-receipt edit and touches no
instrument input).
