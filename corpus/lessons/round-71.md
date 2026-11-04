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

## L1 integration addendum (round 71, measured at the report tip)

<!--WAVE-DISPOSITIONS-->

Final receipts at the tip: <!--FINAL-RECEIPTS-->
