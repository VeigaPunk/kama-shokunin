author: hyaku closure (non-author integrator, @m_zfl)

# kama round 78 — verifier spot-check (non-author closure)

Lane: kama, round 78 (attempt 1). Base `c62ffd3aea930b98375f805cc3dfb821a703148b`; lane tip
after the round `7a3cd98243b69fcbee0cc9e31878782bd8459320` (branch `master`, remote-verified).
Report: `.ufo/reports/round-78/kama.md` (fleet `e7e083be359272be4e67472d8de4f25fa735ce45`).
I did not author this round; I verified it. Review date 2026-11-04.

Method note: PROTOCOL §Gate standard forbids executing a sibling lane's gate, so the three claim
counters and the pre-report gate are **evidence-verified** from their committed receipts (frozen
line, self-test tally, revision measured); their **grounds** are **re-measured** by me with plain
counts over committed bytes (`git`, `wc`, `sha256sum`, `awk`, the fleet census). One external
source was re-opened live; the rejected URL was re-read in the registry.

## 1. Conformance (step 1)

| Check | Result |
|---|---|
| Report committed in the fleet repo by the lane identity | PASS — `git log --format='%an <%ae> %H' -1 -- .ufo/reports/round-78/kama.md` → `kama-shokunin <kama@shokunin.local> e7e083be359272be4e67472d8de4f25fa735ce45`; ancestor of fleet `HEAD` `64ebb50a` = `origin/master` |
| `## SHONEN` heading, one line per box | PASS — one `## SHONEN` heading, four `[~]` lines against the four boxes; no `[x]` written by the lane |
| Every cited lane commit exists and is an ancestor of the branch | PASS — all 16 cited hashes (`c62ffd3a d015a178 11f46d64 0f56ad5a 2bd07a8a 773c8abe 098c306f 4048b44a 590e4f38 22cce544 2842ad29 354d858f fa65ce2c 381b53dc 979aa9db 7a3cd982`) exist and `git merge-base --is-ancestor <h> master` holds |
| Lane repo clean and pushed | PASS — `jj-lane.sh state` → `branch=master local=7a3cd982… remote=7a3cd982… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` → empty; `git ls-remote origin refs/heads/master` → `7a3cd982…` |
| Prompt carries the template contract | PASS — `.ufo/prompts/kama-round-78.md` (704 lines) carries §1 MISSION/AXES binding, §2 claims, §2b frontier step, §3 L2 floor (≥8), §4 report contract (path, `SHONEN`, hash citation), §5 commit/push scope + L0, §6 hyaku addendum, §7 scratch discipline; the five child-lane items are present (report path l.101, `SHONEN` l.118, report-last l.513, hash citation l.106–107, write scope l.445–451) |
| Wave shape | PASS — `w1-spec.json` 12 seats (3 executor, 3 scribe, 1 scout, 1 connector, 1 reviewer, 2 critic, 1 mutation-tester; attack 4/12 = 33 %); `w1-results.json` 12 results, 3 non-empty (`EX01C1Selfrecord`, `SC02Lesson`, `SCT01Recon`), 9 empty |
| Report is a real report, not a marker | PASS — work performed, landed changes tied to `LOG.md:3169`, before→after table, sources & frontier, three trend verdicts, checkable hash citations |

Conformance defects (status-neutral; they do not change the status):

1. **"Final tip" wording.** The quality trend says "the gate is green at the final tip with a
   committed receipt"; the gate receipt `measured/after/gate-run.out` measured `rev=2842ad29`,
   five commits before the tip `7a3cd982` — the report's own Gate-and-tip-state bullet says
   `rev=2842ad29`. The tip-accounting sentence likewise says "green at the tip `22cce544`" (an
   ancestor), and its `events=250 … exempt=60` line has no committed receipt.
2. **C1 self-test receipt predates the counter change.** The cited `pass=8 fail=0` receipts are
   at `rev=2bd07a8a` and `rev=773c8abe`; the counter changed at `381b53dc` (F2 derivation). The
   lesson asserts the arms stay green; no post-change receipt is committed. I read the diff and
   the self-test path (`audit(root, sealed)`, fixture capability table identical at sealed and
   worktree), so the change is behaviour-identical under the eight arms — an evidentiary gap,
   not a contradiction.
3. **Pre-correction red-before output uncommitted.** The lesson describes the pre-correction tip
   run (`mismatches=1 F2`) in prose only; CORPUS's "a fix is shown able to fail before it counts"
   asks for the observed failure output to be committed.
4. **C2 tip re-run uncommitted.** The report cites a tip re-derivation with
   `APPEND_REGISTERS_OUT_OF_POPULATION rows=1`; the committed receipt shows `rows=0` at
   `773c8abe`, and no committed file carries `rows=1`.
5. **C3 receipt not revision-bound.** `measured/after/c3-live.json` (refreshed at `7a3cd982`) has
   no measured-revision field; `c3-live.out` still names `rev=773c8abe`, and `c3-selftest.out`
   carries no `# rev=` header.
6. **Frozen-plan control paths.** The plan names `measured/control/c1-norepair.out` and
   `measured/control/c2-norows.out`; neither exists. The report cites the real C1 control
   (`w1/EX01C1Selfrecord/clone-norepair.out`) and uses the base receipt for C2, but the path
   drift is not listed among the freeze divergences.
7. **Citation precision in the before→after table.** The single "Counting command" column shows
   the new modules for both before and after (the before receipts were produced by
   `measured/before/enumerate-facts.py` and `tools/round77-append-registers.py`), and the
   "Measured revision" column names the final tip `7a3cd982` for C1 (the tip receipt's header is
   `381b53dc`) and `979aa9db` for C3 (the refresh landed at `7a3cd982`).

## 2. Claims (step 2)

### C1 — calibration: the round-77 self-record's six facts re-derive or are answered by dated value-bound corrections

- **Re-measured by me at the tip (plain counts over committed bytes):** the sealed revision
  `6c1550a1…` resolves (`git cat-file -t` → `commit`); the sealed `## Axes` vector is
  operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 (awk over the
  table); the sealed canonical capability table has 34 data rows and its last row
  `selfrecord-round76` first worked round 77 (python count over `**Capabilities — canonical list
  as of round 77**`); `SKILL.md:309` at the tip carries `arms=9`, `nine arms`,
  `round77-instruments` and `pass=22` (at the base the same row carried `arms=8`, `eight arms`);
  `.ufo/waves/round-77/measured/after/gate-selftest.out:3` prints `PRE_REPORT_SELFTEST pass=22
  fail=0`; `SCORECARD.md:4386` carries the appended §Freeze divergences item 3 pointer
  correction; `corpus/knowledge/register-cutoff-split.md:76` carries `source-correction: S073 …`
  (S073 is `corpus/SOURCES.md:85`); `corpus/README.md:1728-1729` carries both coverage rows; the
  four correction blocks in `corpus/lessons/round-78.md` §Corrections name `at=6c1550a1…` and
  `date=2026-11-04`.
- **Evidence-verified receipts:** `measured/after/c1-facts.out` (header `rev=773c8abe`) prints
  `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0`, EXIT 0;
  `measured/after/c1-facts-tip.out` (header `rev=381b53dc`) prints the same line; the base
  enumeration `measured/before/c1-facts.out` prints `SELFRECORD_R77_ENUM claims=6 stale=4
  corrected=0`, EXIT 1; self-tests `c1-selftest.out` and `c1-selftest-l1.out` each print
  `SELFRECORD_R77_SELFTEST pass=8 fail=0` with the eight named arms; the do-nothing control
  `w1/EX01C1Selfrecord/clone-norepair.out` prints `mismatches=4 corrected=0` EXIT 1 with the four
  `mismatch` findings.
- **Post-data correction ruled:** F2's derivation moved from the worktree to
  `git show <sealed>:SCORECARD.md` at `381b53dc` because the round's own record commit made the
  fact self-refuting. `PREDICATE`, the target `capabilities=34/max-round=77` and the eight arms
  are unchanged; the subject the predicate names is the round-77 record, and the sealed table I
  counted is exactly 34 rows / round 77. I accept the correction as a subject alignment, not a
  target move; the missing red-before receipt is routed.
- **Verdict: verified. Axis calibration — improved** (four stale self-descriptions repaired and
  re-derived; score holds at 7).

### C2 — freshness: every base audit event is accounted once at the audited revision

- **Re-measured:** the frozen line's six buckets sum to `events` — 53 + 59 + 28 + 4 + 99 + 5 =
  248; the three appended rows `05a03980` (3), `0fca5e18` (2), `21458716` (1) match the audit's
  `deleted` counts in `w1/SCT01Recon/receipts/06-c2-forced-rows.txt`; `git diff c62ffd3a
  7a3cd982 -- registry/append-only-exempt.tsv` shows exactly those three plus `590e4f38` (1,
  the round-78 freshness-repair event); `registry/endpoint-consumers.tsv` is untouched.
- **Evidence-verified:** `measured/after/c2-registers.out` (header `rev=773c8abe`) prints
  `APPEND_REGISTERS to=c62ffd3a… events=248 accepted=53 exempt=59 permitted=28 out_of_region=4
  restored=99 disclosed=5 unaccounted=0 introductions=1/1 rotation_safe=1`, EXIT 0, plus
  `APPEND_REGISTERS_OUT_OF_POPULATION rows=0` and the two register digests; the base receipt
  `measured/before/c2-append.out` prints `unaccounted=3` EXIT 1 with three findings naming the
  three commits; `c2-selftest.out` (header `rev=773c8abe`; the module is unchanged after it)
  prints `APPEND_REGISTERS_SELFTEST pass=7 fail=0` with the seven named arms. The control is the
  base receipt: the same tree without the three rows is red at `unaccounted=3`.
- **Verdict: verified. Axis freshness — improved.** The tip re-run cited in the report is not
  committed (routed).

### C3 — operability: the probe's three verdicts exercised against a live pinned child

- **Re-measured:** `measured/after/c3-live.json` rows are `MODEL_OK` (expected `stories260K`),
  `MODEL_MISMATCH` (expected `definitely-not-the-model`) and `DEAD` (connection-refused), with
  `summary registry_rows_evaluated=3 model_ok=1 drift=2 exit=2`, `probe_exit=2`, `child_exit=0`,
  `port_closed=true`, `exit=0`; `sha256s.server` `b6a31a8e…` equals
  `sha256sum ~/.local/opt/llama-b11755/llama-server`, and `sha256s.model` `270cba1b…` equals
  `sha256sum ~/.cache/kama-shokunin/models/stories260K.gguf` (1,185,376 bytes);
  `registry/endpoint-consumers.tsv` untouched (scope ruling b).
- **Evidence-verified:** `measured/after/c3-live.out` (header `rev=773c8abe`) prints
  `LIVE_RECONCILE rows=3 model_ok=1 mismatch=1 dead=1 probe_exit=2 runtime=llama.cpp
  served=stories260K`, EXIT 0; `c3-selftest.out` shows each of the four arms red-first with its
  named finding, then `LIVE_RECONCILE_SELFTEST pass=4 fail=0`; the no-server before receipt
  prints `model_ok=0 drift=3 exit=2`, and the feasibility control `model_ok=1 drift=2`.
- **Verdict: verified. Axis operability — improved.** The refreshed receipt carries no revision
  (routed).

### Axis harm check

`git diff c62ffd3a 7a3cd982 -- SCORECARD.md`: the axis table holds 8/8/7/9/7/7 — no score
dropped, no axis retired, no admitted entry found false and left unmarked. Depth: `SKILL.md`
1736 lines sha256 `a50f6f74…`, 48 `## ` headings (the gate row rewrite is a repair). Coverage:
`PROVINCE.md` 331 lines sha256 `6b8c604f…`; filtered knowledge entries 49 → 51 (my count at both
revisions). Adjacency: the unregistered `:1234` listener is reported as an observation, not
absorbed; no sibling scope taken. **No axis harmed.**

## 3. Discernment spot-check (step 3, non-author)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S551 git-rev-parse `--verify` | admit | live `https://git-scm.com/docs/git-rev-parse` (`curl -fsSL` exit 0, 122459 bytes, sha256 `00e3b1aa…` — byte-identical to the retained copy) and its `--verify` paragraph | agree | the 18-word quote is present verbatim ("Verify that exactly one parameter is provided, and that it can be turned into a raw 20-byte SHA-1") in the `--verify` option paragraph; tier A docs fits the one-parameter resolvable-name check; scope is distinct from S082 (abbreviation uniqueness) and S083 (cat-file batch output) |
| git-cat-file candidate | reject (duplicate) | `corpus/SOURCES.md:83,95` | agree | S071 and S083 both cite the URL and S083 already names the adjacent ground; a third row would duplicate the batch-output scope, and the flip is stated concretely |
| S551 `corpus/SOURCES.md` row | new row | `corpus/SOURCES.md:303` + retained copy lines 2720–2722 | agree | the anchor names `Documentation/git-rev-parse.txt---verify` and the retained-fetch sha256; the Gate's located quote is 18 words (≤25); `status=mined`, `used-by=corpus/lessons/round-78.md` |
| Census | validate | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | agree (exit 0) | 292 rows, 0 malformed, 0 duplicate ids, no tier inflation; the W04 duplicate-URL and W01 S481 tier-C-mined warnings sit on rows this round did not add and are non-fatal |

## 4. Axis and trend verdicts

| Axis | Verdict | Evidence |
|---|---|---|
| calibration | improved | C1 verified; four repairs re-read at the tip; counter + self-test + control receipts |
| freshness | improved | C2 verified; bucket sum = events; three rows appended; control red |
| operability | improved | C3 verified; live child; binary/model sha256 match; teardown recorded |
| depth | unchanged | `SKILL.md` 1736 lines, sha256 `a50f6f74…`; the gate row rewrite is a repair, not new craft |
| coverage | unchanged | 49 → 51 filtered knowledge entries and two README rows; score holds 9 |
| adjacency | unchanged | consumer registry untouched; unregistered listener reported, not absorbed |

- **expansion — improved.** My census: base `290` rows (A 275 / B 11 / C 4; mined 261, queued 8,
  rejected 21) → tip `292` (A 277 / B 11 / C 4; mined 263, queued 8, rejected 21), same command
  both times, exit 0. Two admitted knowledge entries on ground the coverage map did not hold
  (`append-registers-at-the-tip.md`, `live-reconcile-trial.md`, both `source: S552`), coverage
  rows `corpus/README.md:1730-1731`; capabilities 34 → 37. Bound: both entries rest on one
  own-work row and no package entry was adopted (the assimilation gap is reported, not hidden).
- **quality — improved.** Four stale self-descriptions repaired and re-derived; the gate receipt
  `PRE_REPORT round=78 arms=9 failed=0 uncommitted=0` at `rev=2842ad29`; the controls are red on
  all three claims; the F2 post-data defect is disclosed in report, SCORECARD and lesson. Bound:
  the gate receipt predates the tip and the C1 self-test receipt predates the C1 tool change —
  both routed.
- **discernment — improved.** My spot-check agrees with the gate on the sampled admit (S551) and
  reject (git-cat-file duplicate); the lane kept S549 rejected, added KQ129, and disclosed its
  own F2 defect. The lane reported `unchanged` because the outside leg did not exist at report
  time; this closure supplies it and the agreement is on record.

## 5. Routed defects the lane must fix next round

1. **R78V1 — tip receipts.** Run the gate and the round-77 register counter at the final tip and
   commit the receipts, or state the measured revision wherever "tip" is claimed. The committed
   gate receipt is `rev=2842ad29` and the `events=250 … exempt=60` register line has no receipt.
2. **R78V2 — C1 red-before receipt.** Commit the pre-correction tip run (`mismatches=1 F2`) so
   the post-data derivation fix has the observed failure output CORPUS asks for.
3. **R78V3 — C1 self-test after the change.** Re-run `--selftest` at/after `381b53dc` and commit
   the receipt; the cited `pass=8` predates the counter change.
4. **R78V4 — C2 tip re-run receipt.** Commit the run that prints
   `APPEND_REGISTERS_OUT_OF_POPULATION rows=1` (the stability leg the predicate names).
5. **R78V5 — C3 receipt binding.** Give `c3-live.json` a measured-revision field and refresh the
   `.out` header in the same commit; add a `# rev=` header to `c3-selftest.out`.
6. **R78V6 — plan control paths.** Reconcile the frozen plan's `measured/control/c1-norepair.out`
   and `c2-norows.out` with the landed control receipts, or record the drift as a freeze
   divergence.
7. **R78V7 — before→after table precision.** Name both counting commands (before receipts were
   produced by `enumerate-facts.py` and `tools/round77-append-registers.py`) and align the
   "Measured revision" column with receipt headers (`381b53dc` for the C1 tip run; the C3 refresh
   landed at `7a3cd982` with no revision field).

## 6. Verdict

All three claims verify against committed bytes; no axis is harmed; the round's own defect
disclosure (F2) is accepted and the seven routed items are evidentiary, not claim failures.
Status `ok`; admitted.
