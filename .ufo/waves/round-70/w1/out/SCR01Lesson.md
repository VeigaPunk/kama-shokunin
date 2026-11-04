# SCR01Lesson — report (round 70, w1, lane kama)

Seat: `SCR01Lesson` (scribe, axes calibration + quality). Advisory leaf: read-only on the lane,
no subagents, no commits. Writes: this out dir and `/fast/scratch/hyaku/kama-r70/SCR01Lesson/`
(deleted before yield). Tool installs/upgrades: **none** (nothing was needed; no pacman, no uv/npx).
Measured lane HEAD: `0e14facd0c619f45a6461821d2bd80ddac9855b1`; frozen base `6035e952` is its parent.
Environment: Linux 7.2.11-arch1-1, python3 3.14.8, git 2.56.0.

## 1. Deliverables

| Path | What |
|---|---|
| `lesson.md` | exact bytes for `corpus/lessons/round-70.md` (Gate, Mistakes 1–4, Ceiling) |
| `report.md` | this file |
| `evidence/*.out` | re-runnable receipts cited by the lesson (see §4) |
| `w1/out/SCR01Lesson.md` | the Report-trailer copy of this file |

Nothing outside these paths was written. The lane tree was read with `git show`, `grep`, `wc`,
`sha256sum` and the registered tools only.

## 2. What I did

1. Read the frozen claims (`.ufo/waves/round-70/controls/freeze.txt`) and the round-69/68 lessons
   for shape (`wc -l` → 28 and 27 lines; headings `## Gate`, `## Mistakes`; no `## Ceiling` in
   either, so the Ceiling section follows the lane's SCORECARD idiom "What `met=True` does not
   show", e.g. SCORECARD §Round-42 measured results and §Round-43).
2. Verified each mistake candidate before mining it (below); did not assume any.
3. Used SCR02's landed gate block (`w1/out/SCR02SourceRow/gate-block.md`) for the pytest row and
   independently re-fetched the page to confirm the quote and the sha256.
4. Validated both registry landing routes (new S542 row; S052 used-by extension) on scratch copies
   with a lesson stub, because the lesson's Gate note must state the registry count honestly.
5. Wrote `lesson.md` in the lane's dense style (dense lines, `Class · evidence · captured-by · fix`).

## 3. Commands and outputs (exact; receipts under `evidence/`)

### 3.1 The nine census receipts, rounds 65–69 (Mistake 1)

```
$ for f in $(grep -rl 'HOST_CENSUS' .ufo/waves/round-65 .ufo/waves/round-66 .ufo/waves/round-67 \
      .ufo/waves/round-68 .ufo/waves/round-69 --include=*.out); do
      printf '%s :: ' "$f"; grep -o 'HOST_CENSUS[^|]*' "$f" | tail -1; grep -o '^EXIT=[0-9]*' "$f" | tail -1; echo; done
```

Result (full transcript `evidence/census-history-refusals.out`): nine receipts, each with
`refused=2`; both refused members are tier A in every receipt (`refused [A] test-snapshot harness`
and `refused [A] round42-selfdesc-reconcile selftest`). The verdict lines and exits:

```
r65 measured/host-census-at-tip.out      HOST_CENSUS pass=16 fail=1 refused=2 total=19 tierA_fail=0 tierB_fail=1
r66 measured/before/host-census-before   HOST_CENSUS pass=16 fail=1 refused=2 total=19 tierA_fail=0 tierB_fail=1
r66 measured/host-census-after.out       HOST_CENSUS pass=17 fail=0 refused=2 total=19 tierA_fail=0 tierB_fail=0
r67 measured/before/host-census-before   HOST_CENSUS pass=17 fail=0 refused=2 total=19 tierA_fail=0 tierB_fail=0  EXIT=0
r67 measured/host-census-at-tip.out      HOST_CENSUS pass=17 fail=1 refused=2 total=20 tierA_fail=1 tierB_fail=0  EXIT=1
r67 measured/host-census-final.out       HOST_CENSUS pass=18 fail=0 refused=2 total=20 tierA_fail=0 tierB_fail=0  EXIT=0
r68 measured/before/host-census-before   HOST_CENSUS pass=18 fail=0 refused=2 total=20 tierA_fail=0 tierB_fail=0  EXIT=0
r68 measured/host-census-final.out       HOST_CENSUS pass=19 fail=0 refused=2 total=21 tierA_fail=0 tierB_fail=0  EXIT=0
r69 measured/host-census-final.out       HOST_CENSUS pass=20 fail=0 refused=2 total=22 tierA_fail=0 tierB_fail=0  EXIT=0
```

Six carry `fail=0`; the three red ones are red for a `fail` (tier B in r65/r66-before; tier A in
r67-at-tip), never for a `refused`. Code: `tools/round65-host-census.py:158`
`return 0 if failed == 0 else 1`, with `refused += 1` on a separate counter
(`evidence/verdict-and-harness-lines.out`).

### 3.2 The base census on this Linux host (the member executes and fails)

```
$ grep -E 'refused \[A\]|FAIL \[A\] round42|HOST_CENSUS' .ufo/waves/round-70/measured/before/census-at-base.out
FAIL [A] round42-selfdesc-reconcile selftest: exit=1 tail='SELFDESC_SELFTEST newest=69 planted_stale=57
  ok:closure_ptr=1,mismatches=9 stale_ptr:closure_ptr=0,mismatches=10 stale_both:closure_ptr=0,mismatches=10
  stale_incl:closure_ptr=0,mismatches=10 no_ptr:closure_ptr=0,mismatches=10 pass=4 fail=1'
HOST_CENSUS pass=21 fail=1 refused=0 total=22 tierA_fail=1 tierB_fail=0
EXIT=1
```

(`evidence/census-tiers.out`; the file is the freeze's committed before-receipt.)

### 3.3 The r68 depth-row drift (what Mistake 1 hid)

```
$ git show 5d2d609e:SKILL.md | sha256sum
efb46d898c2f25eec9920ae98ebe33d2c991a93c61b1a834a34b6e2a83e7b78f  -
$ git show 5d2d609e:SKILL.md | wc -l
1707
$ git show 5d2d609e:SCORECARD.md | grep -m1 '^| depth'   # first 300 chars
| depth | **7** | `SKILL.md` sha256 `5c965f5564c7b9dd1cf692d084183cc68b8069180b277ac60757f4ab888e7c4b` (1706 lines); ...
```

(`evidence/r68-depth-row-drift.out`; the r69 lesson Mistake 4 records it was found only by the
round-69 pre-declare sweep.)

### 3.4 The closure-pointer pair (Mistake 3: scheduled staleness, not drift)

```
$ python3 tools/round69-newest-closure-counter.py --repo . --rev e552abbb --since-round 63
NEWEST_CLOSURE newest=corpus/lessons/round-68-verifier-spotcheck.md date=2026-11-01 round=68
  row_names=corpus/lessons/round-68-verifier-spotcheck.md row_current=true
EXIT=0
$ python3 tools/round69-newest-closure-counter.py --repo . --rev 6035e952 --since-round 63
NEWEST_CLOSURE newest=corpus/lessons/round-69-verifier-spotcheck.md date=2026-11-01 round=69
  row_names=corpus/lessons/round-68-verifier-spotcheck.md row_current=false
STALE_CALIBRATION row_names=corpus/lessons/round-68-verifier-spotcheck.md newest=corpus/lessons/round-69-verifier-spotcheck.md newest_date=2026-11-01
EXIT=1
```

(`evidence/closure-ptr-pair.out`; commit dates: green receipt `e552abbb` 12:23:14Z, non-author
closure `6035e952` 13:46:24Z, both 2026-11-01.)

### 3.5 The run-fact harness (Mistake 2)

```
$ grep -n 'git archive\|"tar"\|cwd=export' tools/round41-scorecard-reconcile.py
22:            CMD runs with bash in a throwaway export of --tip (git archive);
133:        p = subprocess.run(["bash", "-c", cmd], cwd=export, capture_output=True,
191:                subprocess.run(["tar", "-x", "-C", export], input=arc, check=True)
$ grep -n 'detail: r41' .ufo/waves/round-70/measured/before/reconciler-at-base.out
3:detail: r41 operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
4:detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)
$ grep -c selftest tools/round41-scorecard-reconcile.py
0
```

(`evidence/verdict-and-harness-lines.out`.)

### 3.6 The source row and its registry counts

```
$ git show 6035e952:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
281
$ git show 0e14facd:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
281
$ git show 6035e952:corpus/SOURCES.md | grep -m1 '^| S052 |'
| S052 | pytest exit codes — https://docs.pytest.org/en/stable/reference/exit-codes.html | docs | A | ...
```

(`evidence/registry-counts.out`.) Quote and bytes: SCR02's retained
`source/pytest-exit-codes.html` has sha256 `a403306a1d763fc8123749544905dd64e8e0cfa5ed46a416679001c3142e3977`;
my independent fetch of the same URL is byte-identical; `python3 verify-quote.py` exits 0 with
`MATCH 7 words: Exit code 5: No tests were collected`, `MATCH 10 words: Exit code 0: All tests were
collected and passed successfully`, `MATCH 10 words: The exit codes being a part of the public API`
(`evidence/quote-verification.out`).

Both landing routes, validated on scratch copies with a `corpus/lessons/round-70.md` stub:

```
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file <scratch>/v2/lane/corpus/SOURCES.md --today 2026-11-03
file	W04	S542 duplicate url docs.pytest.org/en/stable/reference/exit-codes.html across scopes
file	ok	<scratch>/v2/lane/corpus/SOURCES.md
EXIT=0            # 282 rows
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file <scratch>/v1/lane/corpus/SOURCES.md --today 2026-11-03
... (pre-existing W04 warnings only) ...
file	ok	<scratch>/v1/lane/corpus/SOURCES.md
EXIT=0            # 281 rows
```

(`evidence/validate-s542-row.out`, `evidence/validate-s052-extension.out`; the scratch copies are
deleted before yield — the validator runs are re-derivable by applying SCR02's
`evidence/row-s542.txt` or `evidence/row-s052-extended.txt` to a fresh export.)

## 4. What I could NOT verify

- The landing tip and any post-repair verdict: this seat does not commit, and the L1's record
  repair and the two tool repairs were not landed at my measurement time. `mismatches=0` at the
  landing tip, `SELFDESC_SELFTEST pass=5 fail=0`, `REFUSED_MEMBER_CONTROL refused_fixture_exit=1
  allpass_fixture_exit=0`, and the real `pass=22 fail=0 not_evaluated=0` line are the L1's to
  measure; the lesson does not claim them.
- The wave's attack results: RVW01/CRT01/MT01 had no landed report at my measurement time, so the
  Ceiling section is derived from the frozen counters' definitions and the committed receipt pair,
  not from attack survivors. If those seats land findings, the L1 may append them to the Ceiling
  paragraph.
- Which registry route the L1 lands (new S542 row vs S052 extension). Both were validated here;
  the lesson's count sentence gives both values with the per-revision command.
- A pytest version for the page: none is stated on it, so the row records `on-release`; I did not
  infer one. The served bytes may be a CDN copy (`cf-cache-status: HIT`, `last-modified
  2026-10-27T21:36:00Z`, SCR02's report §1.2); the sha256 pins what was read.
- The r69 closure's own admission reasoning: read from the committed
  `corpus/lessons/round-69-verifier-spotcheck.md` (§1, §7), not re-derived.

## 5. Exact bytes the L1 must land

1. `corpus/lessons/round-70.md` ← copy `w1/out/SCR01Lesson/lesson.md` byte-for-byte. If the L1
   lands SCR02's S542 row, the lesson's Gate note already names the 282-row value; if it lands the
   S052 extension, the note names 281 — both are in the sentence, so no edit is needed either way.
2. `corpus/SOURCES.md` ← SCR02's `evidence/row-s542.txt` inserted after `| S541 |` inside
   `## Registry` (rows 281 → 282), or `evidence/row-s052-extended.txt` replacing the S052 line
   (rows 281 → 281). The lesson's `used-by` dependency (`E11`) requires this file and the lesson
   at the same tip.
3. No other file. The lesson's evidence pointers are either lane-committed receipts
   (`.ufo/waves/round-65` … `.ufo/waves/round-70/measured/before/`), SCR02's landed out-dir files,
   or this seat's `w1/out/SCR01Lesson/evidence/*.out`; all resolve at the landing tip if the out
   dir is committed with the wave evidence, as the wave contract's mattress requires.

## 6. Findings beyond the lesson (advisory)

- The freeze's C2 wording "a refused tier-A member reads as a pass" is a statement about the exit,
  not the line: the census printed `refused` all along. The lesson states it that way; a closure
  quoting the freeze should not read the line as saying `pass`.
- The C2 target's real-census line is a population effect that requires C1: at base the census's
  single tier-A failure is the reconciler selftest (receipt §3.2). Separability holds for the
  frozen counters (C2's control loads synthetic member sets), but the real green line cannot be
  used as C2-only evidence.
- `tools/gate-registry-check.py:348` resolves `master`, so the repaired harness's gate fact
  certifies the branch tip rather than the detached checkout's HEAD (RVW02's probe printed
  `lane-tip 0e14facd0c61` in a checkout of `6035e952`). If the L1 measures at a tip that is
  `master`, the two agree; if not, the fact is green for a different revision.

## 7. Worktree observation at final check (not my edit)

At my last check (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin status --porcelain`) the lane
worktree showed `M PROVINCE.md` and `M SCORECARD.md` plus the untracked wave directories; the diff
is the L1's in-progress record repair (banner re-anchored to round 70, calibration row re-anchored
to `newest=round-69 … row_names=round-69 … row_current=true`, PROVINCE capability surfaces). This
seat wrote nothing outside `w1/out/SCR01Lesson/` and its scratch. Every value in `lesson.md` and in
this report is measured from committed revisions (`6035e952`, `5d2d609e`, `e552abbb`, `0e14facd`)
or from committed receipts; none is read from the dirty worktree.
