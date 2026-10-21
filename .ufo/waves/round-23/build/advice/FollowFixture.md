# FollowFixture: repo-local `log.follow` vs `report_cutoff()` (round 23, C1 calibration)

Seat: `CloseKama22.FollowFixture` (leaf, no dispatch). Base `4fe9339f8fc3a4a4a479d9c938a850da12f1124d`, git 2.56.0, Python 3.14.8. Oracle `tools/report-landing-audit.py` blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a` (lane and scratch agree). Docs accessed 2026-10-21.

## 1. Result

- **It flips.** A repo-local `log.follow=true` in the fleet repo changes the frozen auditor's cutoff and `required`/`post_report`; in two cases it also changes the verdict.
  - G1: report drafted at 1500, moved unchanged to the canonical path at 2500, round commit B at 2000 uncited. Cutoff 2500 -> 1500; verdict failed (`landed-omitted B`) -> clean.
  - G5: canonical report removed at 1100; a new report written at 1300 after B (1200, uncited); moved to canonical at 1500. Cutoff 1000 -> 1300; verdict clean -> failed (`landed-omitted B`).
  - G2 (move also cites B) and G3 (B precedes the draft): cutoff and `required`/`post_report` change; verdict does not.
  - Controls C0 and C1 (no rename) do not change.
- **Expected correct cutoff (lineage contract): 1500 for G1 and 1300 for G5.** That is the first add of the report file across its rename, i.e. `git log --follow --diff-filter=A -- <rel>`. Justification in section 3.
- **Recommendation:** pin `--follow` explicitly in `report_cutoff()` (candidate diff, section 4). Do not adopt `-c log.follow=false` as the pin unless the path contract is chosen on purpose: it removes the config dependence but keeps G1's failure and G5's clean, which are wrong under the lineage contract.

## 2. Reproduction

Fixture: `out/FollowFixture/follow_case.py`. `run_case(auditor, case, log_follow)` is the standalone per-case function; `run_matrix` loops over cases and configs. Each run builds fresh lane and fleet repos under `mkdtemp` in /tmp, sets `git config --local log.follow true` in the fleet fixture only, and runs `--lane-repo L --fleet-repo F --branch master --lane kama --rounds 1 --no-errata --json`. The oracle is `git show 4fe9339f:tools/report-landing-audit.py`, not the working tree. Times are author and committer unix seconds.

| case | lane commits (author time) | fleet commits (time) |
|---|---|---|
| C0 | A 1000, B 2000 | add canonical report, cites A @1500 |
| C1 | A 1000, B 2000 | add canonical @1500 (cites A); edit @2500, no citation |
| G1 | A 1000, B 2000 | add `drafts/kama-r1.md` @1500 (cites A); move to canonical @2500, unchanged |
| G2 | A 1000, B 2000 | as G1; the move @2500 also cites B |
| G3 | A 1000, B 1200 | as G1 |
| G5 | A 900, B 1200 | add canonical @1000 (cites A); remove @1100; add `drafts/kama-r1-second.md` @1300 (cites A); move to canonical @1500 |

Frozen auditor, observed (`out/FollowFixture/grid-output.txt`). `req` is the auditor's `required` count; labels in parentheses.

| case | log.follow | cutoff | required | post_report | verdict | omitted |
|---|---|---|---|---|---|---|
| C0 | unset | 1500 | 1 (A) | B | clean | - |
| C0 | true | 1500 | 1 (A) | B | clean | - |
| C1 | unset | 1500 | 1 (A) | B | clean | - |
| C1 | true | 1500 | 1 (A) | B | clean | - |
| G1 | unset | 2500 | 2 (A,B) | - | failed | B |
| G1 | true | 1500 | 1 (A) | B | clean | - |
| G2 | unset | 2500 | 2 (A,B) | - | clean | - |
| G2 | true | 1500 | 1 (A) | B | clean | - |
| G3 | unset | 2500 | 2 (A,B) | - | failed | B |
| G3 | true | 1500 | 2 (A,B) | - | failed | B |
| G5 | unset | 1000 | 1 (A) | B | clean | - |
| G5 | true | 1300 | 2 (A,B) | - | failed | B |

Harness self-check: unset rows match the path contract 6/6; `log.follow=true` rows match the lineage contract 6/6.

Git-level probe (scratch repo, G1 history, no auditor): `git log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md` gives `2500` with the key unset and `1500` with `log.follow=true`. `git log --follow --name-status` gives `2500 R100 drafts/kama-r1.md -> .ufo/reports/round-1/kama.md` and `1500 A drafts/kama-r1.md`. Without `--follow`, `--name-status` shows `A .ufo/reports/round-1/kama.md` at 2500.

Auditor lines: `report_cutoff` 165-168 (`git log --diff-filter=A --format=%at -- rel`, oldest entry); cutoff used at 270; `"required": len(pre), "post_report": ...` at 308-309.

## 3. Expected correct cutoff and justification

The contract I am asserting is that the cutoff is the first add of the report file, following renames. L1 must confirm this, since it is the one judgment in this report.

1. **git-log docs** (`https://git-scm.com/docs/git-log`, accessed 2026-10-21; same text in the installed `git-log.1` man page, git 2.56.0):
   - `--follow`: "Continue listing the history of a file beyond renames (works only for a single file)." (online lines 322-323; man page line 94.)
   - `log.follow`: "If true, git log will act as if the --follow option was used when a single <path> is given. This has the same limitations as --follow, i.e. it cannot be used to follow multiple files." (online lines 3515-3517, same text in git-config 5752-5754; man page 4916-4918.)
   - `--diff-filter=A`: "Select only files that are Added (A)..." (online line 2831.)
   - Reading: the auditor's query is `git log --diff-filter=A -- <rel>` with one file, which is the shape `log.follow` targets. The docs describe `--follow` as the option that continues a file's history beyond renames. Without it the listing stops at the rename, so the rename destination appears as an add (G1: 2500). With it the history reaches the draft add (1500).
2. **Auditor's own text.** `landed-omitted` applies to commits "no later than the author time of the fleet commit that first added the report" (docstring lines 21-24), and "Lane commits authored after the report are `post_report`" (line 30). In G1 the report content exists from 1500, and B (2000) is authored after it.
3. **Selftest consistency.** `first-add-cutoff-not-readd` (delete, then re-add the same content at the same path) gives the same cutoff under `--follow` as under the path query. Lab check: add 1200, rm 1400, re-add 1500 -> path `1500 1200`, follow `1500 1200`, cutoff 1200 in both.
4. **Invariant.** `git_env()` says "so neither the audited repos nor the selftest fixtures can be redirected" (lines 79-81). A fleet-local `log.follow` redirects the cutoff, so that invariant does not hold for this key. Whichever contract is chosen, the listing must be pinned in code.

Why the path value (2500 for G1, 1000 for G5) is not the correct one under this contract: it is an artifact of the rename listing. In G1 it makes B (authored after the report content existed) required, which is a false failure. In G5 it takes the cutoff from an earlier, different report at the same path, so the clean verdict is wrong because the report written at 1300 omits B.

Caveat: the frozen code's docstring never mentions renames, so the path reading is internally consistent. If L1 picks it, the correct pin is `-c log.follow=false` (section 4) and the expected values are the `path` columns.

## 4. Candidate pins (scratch only; no lane file changed)

| oracle | log.follow unset vs true | matches lineage | matches path |
|---|---|---|---|
| frozen 4fe9339f (base) | flips: G1, G5 (verdict); G2, G3 (cutoff only) | 8/12 | 8/12 |
| pin-path: `-c log.follow=false` in `report_cutoff` (`pin-path-alternative.diff`) | no flips | 4/12 | 12/12 |
| pin-lineage: `--follow` in `report_cutoff` (`pin-lineage-candidate.diff`) | no flips | 12/12 | 4/12 |

Historical ledger (read-only; bare mirror of the fleet at `/tmp/kama-r23/FollowFixture/fleet-mirror.git`; the real fleet and lane were not written):
- 20 `.ufo/reports/round-N/kama.md` paths at fleet HEAD. 0 have rename history (`git log --follow --name-status`). 0 have a first-add cutoff that differs with `--follow`.
- 0 merge commits touch these paths (the fleet has 17 merges in 1025 commits overall).
- `log.follow` is UNSET in the real fleet and lane (`git config --local --get log.follow`).
- So neither pin changes the real ledger. The flip stays latent until a report is renamed or the key is set.

Draft mode: `git log --follow --diff-filter=A -- <missing path>` returns empty with rc 0 (lab), so the uncommitted-draft "now" branch is unaffected.

The auditor's full selftest was not run on the candidate (seat rule: no tests while the wave is in flight). L1 must gate it.

## 5. Other findings

- **Same-path placeholder defeats the cutoff under both contracts.** Placeholder added at 1000, removed at 1100, real report added in place at 1300 (cites A, not B), B at 1200:
  ```
  frozen       log.follow=unset  cutoff=1000 verdict=clean required=1 post=['B']
  frozen       log.follow=true   cutoff=1000 verdict=clean required=1 post=['B']
  pin-lineage  log.follow=unset  cutoff=1000 verdict=clean required=1 post=['B']
  pin-lineage  log.follow=true   cutoff=1000 verdict=clean required=1 post=['B']
  ```
  `--follow` does not change this, because an in-place re-creation keeps the path's earlier add in both listings. This is the first-add-through-delete rule that the selftest asserts for identical content. It is a design question for L1, separate from the `log.follow` fault.
- **Doc attribution.** `ScoutLogFollow.md:163` attributes "does not work well on non-linear history" to `--follow`. That clause is not in the git 2.56.0 text (online or man page; grep count 0). Do not carry it into a registry row.
- **Docstring claim.** The `git_env` claim (lines 79-81) does not hold for repo-local `log.follow`, as the flips show. This is relevant to the C1 calibration axis.

## 6. Not verified

- Selftest of any candidate; full-ledger auditor run with a candidate (only a git-level cutoff comparison for the 20 paths).
- Rename-similarity effects: git's default threshold (50%) bounds `--follow` lineage; a heavily rewritten move breaks it. Not tested.
- Other repo-local keys (`diff.renames`, `log.showSignature`, ...), other git versions, promisor and replace-object faults (outside this item).
- Rename histories that contain merges: none of the kama report paths has a merge, so untested.

## 7. Tooling

No installs or updates performed. git 2.56.0 and Python 3.14.8 were already present. Man pages were read locally.

## 8. Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/FollowFixture.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/FollowFixture/follow_case.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/FollowFixture/grid-output.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/FollowFixture/grid.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/FollowFixture/pin-lineage-candidate.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/FollowFixture/pin-path-alternative.diff`

Scratch only, not deliverables: `/tmp/kama-r23/FollowFixture/` (clone; its `tools/report-landing-audit.py` is edited there and nowhere else), `/tmp/kama-r23/FollowFixture/experiments/`, `/tmp/kama-r23/FollowFixture-lab*/`, `/tmp/kama-r23/FollowFixture/fleet-mirror.git`.

## 9. Checks for the main agent

- Confirm the contract. If lineage: apply `pin-lineage-candidate.diff`, run the auditor selftest (expected 50/50, not yet run), then `follow_case.py --contract lineage` against the candidate (expected exit 0 for it).
- If path: apply `pin-path-alternative.diff` instead and run `--contract path`.
- Re-check the rounds 10-22 ledger after any pin (expected unchanged: 0 renamed kama report paths).
- Do not admit the "non-linear history" clause into any registry row.
