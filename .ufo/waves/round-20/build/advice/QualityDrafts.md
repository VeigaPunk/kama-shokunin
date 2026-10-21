VERDICT: partial - three KQ25-27 rows drafted and each observed; the (a) red cell reproduced, but the documented-exit-2 red is not current at 37bd4c5 and the round-20 lesson is not filed.

Scope: draft rows for corpus/QUALITY.md (C1 errors-are-not-verdicts, lesson append-only, count re-derivation). Lane pinned at 37bd4c5bd456a2f8a54d3312c28495c321715856; work in /tmp/kama-r20-QualityDrafts/lane (clone + checkout), scratch deleted. No lane edit, no install, no network, no model.

## Drafted rows (last existing row is KQ24; new ids start at KQ25)

Section header to append: `## Criteria added — round 20 (draft, author-appended; no outside review yet)`, then one sentence: "No earlier criterion is superseded. KQ7's append-only rule and KQ14's semantic-human boundary remain in force; KQ25 applies KQ20/KQ21's rule that a grading counts only when it can fail to the error path; KQ26 extends KQ7 to undated wording; KQ27 applies KQ22's append-only discipline to counts."

| ID | Admit only when | Reject or limit when | Motivating lesson |
|---|---|---|---|
| KQ25 | A lane instrument counts a subject as killed, rejected, refused or failed only when it observed that subject's emitted verdict (the stdout line and exit code the subject documents for that verdict, e.g. the gate's `INVALID ` line with exit 1). A crash (uncaught exception exit 1, silent exit 1, signal), an unusable git/doc/registry/receipt input, or an early-abort selftest is could-not-evaluate or error with its documented non-verdict exit, never a kill. Error-injection cells over the instrument (crash-only subject, unusable input, aborted selftest) are retained and must score as error on the same run that scores a real verdict as rejected. | An exit 1 alone is counted as rejected (`tests/llamacpp-live/install-tree-grid.py:110`, `code == 1`): a crash-only gate scores `rejected=3/3` exit 0 (observed, below). A documented non-verdict exit is recorded as a kill. The round-18 C2 early-abort selftest that prints the target literal is counted as killed (reported in the round-19 critic list; [INFERENCE], not reproduced here). Not a current red at 37bd4c5: `citation-provenance.py` on a non-git lane exits 2 (observed, below). | `lessons/round-19-verifier-spotcheck.md` lines 106–110 (grid kill = `code == 1`) and routed item 7 lines 199–205; `lessons/round-20.md`: NOT YET FILED, L1 to name it at integration. |
| KQ26 | A correction to any filed lesson line, including a wording-only or decision-neutral change, leaves the original line's bytes in place and appends a named, dated correction that quotes the original text, names the commit it corrects, and states what changed. The correction commit's `git show --numstat` for that lesson file shows zero deleted lines. | A filed lesson line is rewritten in place for wording (`30ed378`, `corpus/lessons/round-18.md:42`, numstat `1 1`: the `start_loop()` / `terminate()` reset wording replaced the original `server-queue.cpp:279` wording; original recovered by `git show 30ed378^:corpus/lessons/round-18.md`). A correction that omits the original text is rejected. A rewritten line cited as the filed claim is rejected. An undated wording change is outside KQ7's "dated line" limit and is rejected here. | `lessons/round-19-verifier-spotcheck.md` lines 53–58 and routed item 4 lines 192–193; `lessons/round-20.md`: NOT YET FILED. The "PROTOCOL §Evidence standard" cited at spotcheck line 57 has no tracked `#…Evidence standard` heading at 37bd4c5 (`git grep` empty), so this row restates the rule. |
| KQ27 | Every count quoted in SCORECARD, LOG or a lesson (`required=`, `found=`, `verified=`, `missing=`, selftest case or mutation count, registry row count, digest count) names its exact command, the commit it was measured at and its exit. When a measured artifact changes (registry row, checker, selftest, grid or gate), each quoted count of that artifact is re-derived at the new commit, or the stale count is named as superseded by an appended dated line. A pre-final figure in a dated section is labelled pre-final by an appended line. | A count from before a change is repeated after it: `required=3` and `selftest 5 cases` (SCORECARD.md:823–824), `verified=3` (LOG.md:1146), and "three registry-row digests" (SCORECARD.md:846, LOG.md:1172) after the registry became four rows at `028235e` (observed: 3 rows at `7229fa9` and `f1790e2`, 4 rows at `028235e` and `37bd4c5`) and the selftest became 15 cases. A count quoted without command, commit or exit is rejected. A count from a dirty worktree (`evidence/final-selftests.txt`, `5b108c1a`, per spotcheck lines 103–105) is rejected. | `lessons/round-19-verifier-spotcheck.md` routed item 2 lines 184–187 and §Per-axis lines 128–130; `lessons/round-20.md`: NOT YET FILED. |

## Observed evidence (lane clone at 37bd4c5; all from /tmp/kama-r20-QualityDrafts/lane, scratch since deleted)

| Command (cwd = lane clone) | Exit | Observed |
|---|---|---|
| `git rev-parse HEAD` (lane) | 0 | `37bd4c5bd456a2f8a54d3312c28495c321715856` |
| `python3 tools/citation-provenance.py` | 0 | `required=4 docs_unreadable=0 found=4 verified=4 missing=0 mismatch=0 off_ref=0` |
| `python3 tools/citation-provenance.py --selftest` | 0 | `selftest: ok (15 cases)` (stderr: an expected unreadable-doc message) |
| `python3 tools/citation-provenance.py --registry /nonexistent/x.json` | 2 | `[Errno 2] No such file or directory` (documented exit 2 holds) |
| `python3 tools/citation-provenance.py --registry <row missing sha256>` | 2 | `invalid registry row:` (no traceback) |
| same, with `sha256: 12345` (int) | 2 | `invalid registry row:` (no traceback) |
| `python3 tools/citation-provenance.py --lane <empty dir>` | 2 | `lane is not a git repository` (round-19 critic's exit 1 not reproduced at this commit) |
| `python3 -c` count of `registry/required-citations.json` at 37bd4c5 | 0 | 4 rows |
| `git show <c>:registry/required-citations.json` row count, `7229fa9` / `f1790e2` / `028235e` | 0 | 3 / 3 / 4 |
| `python3 tests/llamacpp-live/install-tree-grid.py --selftest` | 0 | `selftest: baseline, member rejection, absent member and bad receipt passed` |
| grid with fake crash gate (`out/QualityDrafts/crash-gate.py`: VALID for `baseline.json`, else `raise RuntimeError`), receipt `out/QualityDrafts/receipt.json` | 0 | `baseline=VALID members=3 rejected=3/3 tree_pin=on`; grid exit 0 with no INVALID line emitted |
| `git show --numstat --format= 30ed378 -- corpus/lessons/round-18.md` | 0 | `1	1` |
| `git grep -n '^#.*Evidence standard' 37bd4c5 -- '*.md' > /dev/null` | 1 (re-run, no output) | no heading; PROTOCOL file not in lane |
| `grep -n` stale counts in SCORECARD.md, LOG.md, lessons/round-19.md | 0 | lines as cited in the rows |

Receipts kept: `.ufo/waves/round-20/build/out/QualityDrafts/` (crash-gate.py, receipt.json, int-sha.err). Crash-gate output is the grid's stdout above.

## Findings and limits

- (a) C1 red cell reproduced: the grid counts a crash-only gate as 3/3 rejected, exit 0, at the frozen commit. Verdict-observation rule therefore has a live counterexample in the lane.
- (a) Not reproduced: the documented-exit-2-but-exits-1 checker cell in the round-19 critic list. At 37bd4c5 it exits 2 for non-git and unreadable registry input. Not run at an earlier commit; `git log -- tools/citation-provenance.py` shows the file last changed at `30ed378`, so the exit-1 observation (round-19 critic, at 8bf99ca) is not re-derived here. The row is kept because the rule is still required.
- (b) Confirmed: one in-place wording rewrite (numstat `1 1`). `grep` of `30ed378`, `start_loop` and `:42` across `corpus/lessons/round-18.md`, `round-19.md`, `LOG.md`, `SCORECARD.md` (exit 0) finds no correction naming it; round-18.md already carries appended errata elsewhere (lines 284–286, 387), which were not used for this line.
- (c) Confirmed: the count sites above name registry-size 3 or `verified=3` after the registry grew to 4 rows; the current re-derived counts are 4/4 verified and 15 selftest cases.
- Round-20 lesson does not exist in the lane (`ls corpus/lessons | grep 20` empty). Every row carrying it is marked NOT YET FILED for the L1.
- Coverage vs existing rows: KQ7 (dated-line rewrite), KQ14, KQ20/KQ21 (grading that can fail), KQ22 (SOURCES append-only). KQ25–27 do not duplicate them except as noted in each row.

## Tooling

No installs or updates. Tools used: git, python3 (host stdlib), grep, sed, cp. No network, no model, no persistent process started; no fake listener.

Report: .ufo/waves/round-20/build/advice/QualityDrafts.md
