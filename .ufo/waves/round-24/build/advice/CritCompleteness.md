# CritCompleteness — reachability completeness of the r24 promisor repair

Seat `KamaR23-2.CritCompleteness-2` · lane base `0df800e896f6bce285a81e794ad4ae1d1e6c3a71` (observed `git rev-parse HEAD`) · git 2.56.0 · 2026-10-21.
No production file, grid, registry or fleet edit; no build/test/suite run. Installs: none.

## Verdict

**The per-call design holds, but completeness gates do not.** The current reads that need commits, trees and blobs already fail loudly on missing objects, so they need no change. Removing the refusal is a safe repair only if all of the following hold:

- The repair adds no completeness gate built on `rev-list`, `rev-list --objects --missing=print`, or `fsck --connectivity-only`. All three can exit 0 while required commits are missing (measured below).
- Every site where absence becomes a verdict goes through one "unknown in a promisor-backed repo" rule. There are three such sites, not two: the errata correction lookup also turns absence into a verdict.
- The oracle stops pinning F27 (filter-only promisor) at exit 1. Otherwise the grid rewards the most likely implementation slip.

## Evidence

The probe used local synthetic repos under `/fast/scratch/hyaku/kama-r24/CritCompleteness/probe`. The promisor URL points to a nonexistent local path. Every git call carried the audit's `--no-replace-objects --no-lazy-fetch` flags, with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`.

- Script: `out/CritCompleteness/probe.sh`
- Output: `out/CritCompleteness/probe-output.txt`

Fixture: four commits `init`, `round-1: a` (C2), `round-1: b`, `round-2: d`. The repo is marked as a partial clone with `remote.origin.promisor=true` and `extensions.partialclone=origin`.

| probe | missing object | command | observed |
|---|---|---|---|
| P1 | C2 (loose), no commit-graph | `log -z --format=%H%x00%an%x00%at%x00%s master` (= `round_commits`) | rc=128 `Failed to traverse parents` ✓ |
| P1 | same | `rev-list --missing=allow-any master` | **rc=0, 2 lines**: C2 and its ancestor C1 silently gone |
| P1 | same | `rev-list --missing=print master` | rc=0, 3 lines: ancestor C1 still unlisted (only the frontier `?C2`) |
| P2 | C2, commit-graph written first | `log -z --format=…%an…%s` (= `round_commits`) | rc=128 `cannot read commit object` ✓ |
| P2 | same | `rev-list master`, `log --format=%H` | **rc=0, 4 lines**: commit-graph masks the missing object |
| P2 | same | `rev-list --objects --missing=print master` | **rc=0, 0 `?` lines**: certifies "complete" while C2 is missing |
| P2 | same | `log --diff-filter=A --format=%at -- <report>` (= `report_cutoff`) | rc=0; graph-derived, faithful for an untampered graph |
| P3 | tip `corpus/` tree | `ls-tree master -- corpus/SOURCES.md` (= `load_source_urls`) | rc=1 `Could not read` ✓ |
| P4 | `.ufo/reports/round-1` tree | `ls-tree -r --name-only HEAD -- .ufo/reports` (= `parse_rounds A-`) / `show HEAD:<report>` | rc=1 / rc=128 ✓ |
| P5 | C1 root tree | `log --diff-filter=A -- <report>` | rc=128 `unable to read tree` ✓ |
| P6 | SOURCES blob; then C2 | `cat-file --batch-check` (= `lookup`) | **rc=0, `… missing`** for blob and for `C2abbrev^{commit}`: the only silent channel |
| P7 | blob; config is only `remote.origin.partialclonefilter=blob:none` | `cat-file --batch-check` without / with `--no-lazy-fetch` | without: lazy fetch attempted (`does not appear to be a git repository`); with: plain `missing`. Runtime confirms the filter-only remote is promisor-backed (SrcPromisorCode, static). |
| P8 | genuine `.promisor` pack holding C3 and C4; C2 and C1 absent | `rev-list --exclude-promisor-objects master` | **rc=0, 0 lines**: every commit hidden, so required=0 and the audit would report a false clean |
| P8 | same | `rev-list --missing=allow-promisor master` | rc=128 `unexpected missing commit object` after printing 2 lines |
| P8 | same | `fsck --connectivity-only --no-dangling --no-reflogs` | **rc=0**: missing promisor commits accepted as valid |

The real lane and fleet repos carry no promisor config keys and no `*.promisor` files. Both use split commit-graphs (`objects/info/commit-graphs`). Lane count-objects: 743 loose objects, 5857 in-pack. Fleet: 2694 loose objects, 6947 in-pack.

## Findings: counterexample, axes and smallest correction

**1. Completeness gates are unsound.** A repair that decides "complete, so absence is proof" from a closure walk fails three ways:

- With a commit-graph present (as in both real repos), `rev-list` and `rev-list --objects --missing=print` exit 0 with zero missing entries even though a commit object is gone (P2).
- `fsck --connectivity-only` exits 0 in a promisor repo with missing commits (P8). SrcFsck's limit was correct: the manual is not a certificate, and the runtime exempts promisor objects.
- Even a truly complete reachable closure says nothing about objects the remote holds outside the local refs. Counterexample: a lane cloned with `--filter=blob:none --single-branch`, every reachable object later backfilled, and a report citing commit C from an unfetched branch. The closure is complete and C is absent, yet C exists upstream. A closure-based upgrade from "missing" to "absent" yields exit 1 `landed-unresolved`. Preregistration line 4 requires exit 2.

`OracleLocalBlobType.md:115` records "0 `?` lines" for its fixture. That holds for that fixture, but must not be generalized into a gate.

Impacted axes: calibration (false failed verdict), operability. A whole-repo `--all` walk would also over-refuse on unrelated branches and reflogs. P2 fsck flagged the reflog, which is the r23 harm pattern again.

Correction: no closure, fsck, or connectivity gate. Required-object availability equals the existing per-call failures: `round_commits` reads every commit buffer, and `ls-tree`, `show` and `cat-file blob` fail on missing objects (P1–P5). Completeness never changes how a missing citation is classified.

**2. Commit enumeration must keep the default `--missing=error` and keep reading commit buffers.** P1 and P8 show that `--missing=allow-any`, `--missing=print` and `--exclude-promisor-objects` silently drop the missing commit and every ancestor behind it. A `round-1:` commit behind the gap stops being required, which produces a false clean or a lost omission.

`round_commits` (`tools/report-landing-audit.py:192-193`) is safe today only because its `%an`/`%s` format forces a buffer read for every walked commit. A `%H`-only pre-walk is graph-masked (P2).

Impacted axes: calibration, no-harm. Correction:

- Treat any `--missing=` other than `error`, any `--exclude-promisor-objects`, `--ignore-missing`, `%H`-only enumeration, or per-commit `log --no-walk <sha>` over a tolerant listing as a mutant. CaseMissingAncestor measured that last one at 2 of 4 commits seen and a false clean, exit 0 (`out/CaseMissingAncestor/`).
- Add a grid row: promisor-marked lane with a missing commit object in the middle of history and a `round-1:` commit behind it that is still present. Expected exit 2, with the reason pinned to the traversal failure. Build it with and without a commit-graph.
- Build the pack from an explicit object list that omits only the gap commit. Do not use the P8 `rev-list --objects tip ^C2` exclusion: it also drops the ancestor C1 and the trees and blobs C1 owns, so a report citing C1 hits the unknown-citation exit 2 instead (confound found by CaseMissingAncestor). P8 is valid only as evidence that tolerant enumeration hides commits.

**3. Absence becomes a verdict at three sites, all through `lookup()`.** P6 shows `cat-file --batch-check` is the only path that returns "missing" with rc 0. Its callers:

- `:324-327` produces `unresolved-full-hash`.
- `:335-342` produces `landed-unresolved`. Note that `^{commit}` reports "missing" even when the abbreviation matches a local non-commit, which is still unknown in a promisor repo.
- `:404-407` produces `errata-invalid`, the site most likely to be missed. Today a missing correction hash makes `status != "found"`, which yields `errata-invalid` and exit 1. That is a proof of absence: in a full clone exit 1 is correct, but in a promisor-backed repo whose upstream holds the correction, the true answer is exit 0.

Errata rows that correct an unknown token cannot be decided either. If the token resolves upstream, the row is `errata-unmatched` (exit 1); if not, the row matches (exit 0). So the result is exit 2.

Impacted axes: calibration. Correction:

- Classify inside `lookup()` after every repo has been consulted. Do not raise inside the per-repo loop: a token missing in a promisor lane but present in the fleet must be `found` (preregistration "resolved locally by another audited repository").
- Classify "missing in all, and any audited repo promisor-backed" as unknown, which yields exit 2 naming the tokens and repos. This covers all three callers, including the errata path.

**4. The F27 expectation rewards the likely slip.** `tests/report-audit/repo-state-grid.py:674-675` pins `F27-filter-only-promisor-remote` at exit 1 `["landed-unresolved", "unresolved-full-hash"]`. The detector at `tools/report-landing-audit.py:460-465` matches only `extensions.partialclone` and `remote.*.promisor`. It has no `partialclonefilter` case (rg: 0 hits).

If the r24 repair converts the refusal into classification and keeps this detector, F27 still gives exit 1 and the grid marks it met. Yet the filter-only remote is promisor-backed (P7; SrcPromisorCode `promisor-remote.c:148-163`).

Impacted axes: calibration, evidence (a false oracle). Correction:

- Document a policy-row change: F27 becomes exit 2, with a reason string for the unknown citation.
- F06 (`:651`) and F23 (`:670`) keep exit 2, but their REASONS pins (`:696`, `:704`) must change from the refusal text to the unknown-citation text. Otherwise a still-present blanket refusal passes them.

**5. Pin down the "promisor-backed" predicate before implementation.** Recommended members:

- `extensions.partialclone`, any value.
- `remote.<n>.promisor` unless it is a recognized false spelling. Git dies on an invalid boolean, so treating an unparseable value as backed only moves missing-citation rows to exit 2. Today's `git_bool` at `:482-486` treats `"maybe"` as false.
- `remote.<n>.partialclonefilter`, any value. `promisor=false` does not cancel it (SrcPromisorCode limit 3), so add a combined row with `promisor=false` plus a filter, expected to classify as backed.
- A `objects/pack/*.promisor` marker paired with its `.pack` (F23: config removed, marker left, cited blob truly upstream). Without this member F23 becomes a false exit 1.

An orphan marker (C10, `:680`) is ignored by git and may stay non-backed. Either way, add a preregistered row for an orphan marker with a missing citation.

Classification is metadata only and never refuses a repo, consistent with preregistration line 6.

**6. Precedence is unpinned.** It is not specified whether a report with a proven uncorrected defect (for example `landed-omitted`) plus an unknown citation gives exit 1 or exit 2. Both are sound:

- Exit 1 is monotone, because errata match on text, so the proven defect stays uncorrected however the unknown resolves.
- Exit 2 is the preregistration's literal "exit2 unless resolved locally".

Recommendation: unknown dominates (exit 2), because it is literal and simplest. Preregistration line 2's omission fixture must contain no unresolvable citation, and one row should pin the mixed case.

**7. "Same as full clone" is narrower than it reads.** It holds only for rows where every citation resolves. Unresolved rows deliberately diverge: a full clone gives exit 1, a promisor clone gives exit 2. Each grid pair must state which side it is on, or the pairing check will flag the intended divergence as harm (or hide a real one).

A "complete" fixture must also hold every cited blob and tree. The full-hash scan looks up any object type, so a blobless clone citing a historical blob is exit 2 by design. That is not a regression.

**8. Abbreviation uniqueness is local only.** `found` for a 7–39 hex abbreviation means unique among local objects. In an incomplete promisor repo, a remote-only object could make it `landed-ambiguous` upstream. `ambiguous` and `found` existence are monotone; uniqueness is not.

Correction: state this under `not_claimed` (ambiguity is judged over the audited local object set). Do not refuse, because refusing would kill preregistration line 1.

**9. Mutant inventory goes stale.** In `tests/report-audit/isolation-mutants.py`, M14 (`:46`), M22 (`:64-65`, exact `raise EvalError(... promisor pack)`), M27 (`:75`) and M29 (`:78`) target refusal strings that r24 removes. Unmatched, they become harness errors or vacuous survivors.

Correction:

- Retarget each one at the classification predicate members from finding 5.
- Add the finding 2 enumeration mutants.
- Add a mutant that raises the unknown inside the per-repo loop (finding 3 ordering).
- Add a mutant that skips classification for the errata lookup.

M02 (`:31`, dropping `--no-lazy-fetch`) becomes load-bearing once the refusal is gone. It should be killed by the F06 and F27 `executed` marker check (`repo-state-grid.py:747-751`). That kill is unrun and unverified.

## Not defects (checked)

- **`report_cutoff` with a commit-graph and missing non-add commit objects:** it succeeds (P2), but the result is derived from graph data that is faithful for an untampered graph. The add commit's `%at` still forces a buffer read. Tampered graphs fall under the existing trusted-repository scope.
- **`ls-tree` in `load_source_urls` and `parse_rounds`:** missing subtrees give rc 1, never silent partial listings (P3, P4). The silent "SOURCES absent means legacy" fallback (`:261-262`) cannot be triggered by a missing tree. A tree listing is authoritative, so only blob or commit absence is promisor-ambiguous.
- **Lazy fetch:** `--no-lazy-fetch` prevented the fetch attempt in P6 and P7. Without it, git attempted the configured remote.

## Unverified

- No auditor invocation, grid run, mutant run or selftest was performed.
- Rows proposed in findings 2, 4, 5 and 6 are unbuilt.
- The M02 kill is inferred.
- Timing of whole-repo walks against the real fleet under `GIT_TIMEOUT=20` is unmeasured.

Files: `.ufo/waves/round-24/build/out/CritCompleteness/probe.sh`, `.ufo/waves/round-24/build/out/CritCompleteness/probe-output.txt`.

Report: .ufo/waves/round-24/build/advice/CritCompleteness.md
