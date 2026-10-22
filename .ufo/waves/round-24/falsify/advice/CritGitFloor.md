# CritGitFloor — R23-H2 Git floor falsification (round 24, fresh)

Verdict: **HOLDS** (static official-source check only; no installs, no Git<2.56 execution).

- Snapshot: scratch clone `/fast/scratch/hyaku/kama-r24/falsify/CritGitFloor/repo`
  (`--no-hardlinks`), detached at `2e254a1763a9c08aa07fc53081287f506c447d84`
  (observed `git rev-parse HEAD`, exit 0); `git status --porcelain` empty. Base `0df800e8`.
- Pins observed at HEAD (sha256): `tools/report-landing-audit.py` ea51bc35…dd220,
  `tests/report-audit/promisor-grid.py` b034e159…cefa, `promisor-grid-expectations.json`
  d86b7bea…14cd1, `promisor-mutants.py` 6e0b9d62…60a2. All match the assignment.
- Oracle inputs read (sha256): preregistration 6dde0d72…, amendment-1 930b087a…,
  snapshot 1f5a4699…, supplement-2 4600a8c3…. supplement-2 `version_constraint`
  forbids `--missing=print-info` and `--missing-only`.

## Axis 1 — the new commands do not raise the floor above Git 2.45 (HOLDS)

Commands: `rg` for `print-info|missing-only|--missing` excluding `.ufo` (exit 0), plus a
per-file diff of option tokens between base and HEAD for the tool and the four test scripts.

- `print-info` and `--missing-only` appear nowhere in `tools/` or `tests/` except in the
  prohibition text (`promisor-grid-expectations.json:1501`).
- Git primitives new in the tool since base, with the earliest version that has each
  (from official git/git sources):

| argv (tool line) | present in v2.45.0? | evidence |
|---|---|---|
| `rev-list --objects --missing=print --no-object-names --stdin` (672-674) | yes | v2.45.0 `builtin/rev-list.c:408` `"print"`, `:644` `--no-object-names`; rev-list-options.txt:940,1023 |
| `--filter=blob:none` on that walk (677) | yes | v2.45.0 rev-list-options.txt:946,951 |
| missing **commits** reported by `--missing=print` | yes, since 2.43 | RelNotes 2.43.0:305 "`git rev-list --missing` did not work for missing commit objects, which has been corrected" |
| missing tips treated as missing (root appended at 662) | yes | v2.45.0 rev-list-options.txt (after 1023): "If some tips passed … are missing, they will be considered as missing too" |
| `-c core.commitGraph=false` (672) | yes | v2.45.0 config/core.txt:718 |
| `cat-file --batch-all-objects --batch-check=%(objectname) %(objecttype)` (640) | yes | v2.45.0 git-cat-file.txt:160; builtin/cat-file.c:320,323,974 |
| `log -1 --format=%T` (274), `cat-file --batch-check` with `^{}` (242) | yes | long-standing |

- Forbidden flags are newer than the floor, which confirms the constraint and shows the code
  does not use them: `--missing=print-info` arrived in RelNotes 2.49.0:33;
  `--missing-only` in RelNotes 2.56.0:160 (which, I infer, is why the local Git 2.56.0 would
  accept it without complaint).
- `lookup()` parses a ` excluded` status, which Git emits only for `cat-file --filter`
  (RelNotes 2.50.0:48; 0 occurrences in v2.45.0 `builtin/cat-file.c`). This parse is
  **inherited from base** (base line 165), adds no flag and never fires without `--filter`,
  so it does not raise the floor.
- The test harness only adds `clone --filter=blob:none --no-checkout` with
  `uploadpack.allowFilter` and `protocol.file.allow=always`, `repack -a -d`, and `config`;
  none of these need a Git newer than 2.45. The harness's own `--no-lazy-fetch` is the same
  inherited floor.
- Inherited floor confirmed: RelNotes 2.45.0:120 introduces `git --no-lazy-fetch`; v2.45.0
  `git.c:190` parses it. The floor stays exactly 2.45.

## Axis 2 — R23-H2 is still open at L0 and not operator-approved (HOLDS)

`rg 'R23-H2|2\.45'` at HEAD (exit 0). Every disposition statement keeps it open:

- `SKILL.md:852-853`: "not restored older-Git support or operator approval; R23-H2 is carried
  in the round24 L0 question".
- `SCORECARD.md:1212-1213`: "remains an unresolved R23-H2 operator decision".
- `corpus/README.md:353`: "remains open to operator disposition (R23-H2)".
- `corpus/lessons/round-24.md:83-84,144`: "explicitly not approved or repaired" and "carried,
  not discharged, pending the operator ruling".
- `tools/report-landing-audit.py:55,137` still states the requirement.

No file claims approval, closure, or older-Git support.

## Residual findings (not falsifications; smallest corrections)

1. **The floor is not enforced by any test (tradeoff, documentation only).** `version_constraint`
   is never read by `promisor-grid.py` or `promisor-mutants.py`, and no selftest or static check
   rejects `--missing-only` or `print-info` in the auditor. Because the dev host runs 2.56.0, a
   future regression that adds them would pass every grid. Smallest fix, which L1 can choose to
   apply later: one static selftest assertion in `promisor-grid.py` that the auditor source contains
   neither `print-info` nor `--missing-only`. Impacted axis: future floor drift only; no current
   defect.
2. **The round-24 `LOG.md` entry never names R23-H2.** The ScribeLog draft did:
   `build/out/ScribeLog/LOG-round-24-entry.md:22`. The LOG entry only says the supplement
   "forbids newer Git flags that would raise the existing version prerequisite" (LOG.md, round-24
   section). It makes no approval claim, and SKILL, SCORECARD, README and the lesson carry the
   open status, so there is no false provenance. Optional append-only fix: one LOG line stating
   "R23-H2 Git>=2.45 remains open L0, not operator-approved."
3. Observation outside this axis: the appended Round23 section of `SKILL.md` (lines 790-795)
   still lists a partial clone as refused. The later Round-24 section supersedes it as appended
   history. Routed to the doc reviewers, not judged here.

## Observed vs inferred

- Observed: commit/HEAD, file hashes, all grep and diff results, official release-note lines,
  and v2.45.0 source/doc lines (see `out/CritGitFloor/official-git-source-excerpts.txt`).
- `[INFERENCE]`, not executed: runtime behaviour under an actual Git 2.45 binary. No Git 2.45 was
  installed or run (installs were forbidden), so acceptance at 2.45 is established from
  official source and docs only. Also inferred: that 2.45 `--filter=blob:none` combined with
  `--missing=print` reports non-blob holes the same way 2.56 does.

## Files written

- `.ufo/waves/round-24/falsify/advice/CritGitFloor.md` (this file)
- `.ufo/waves/round-24/falsify/out/CritGitFloor/official-git-source-excerpts.txt`
- Scratch only: `/fast/scratch/hyaku/kama-r24/falsify/CritGitFloor/{repo,relnotes,tmp}`.

## Addendum — fixture lazy-fetch hazard (relayed by KamaR23-2.CaseFleetBlobless)

Reported hazard: a `--keep`'ed blobless fixture still has a reachable `file://` origin, so a
manual probe without `--no-lazy-fetch` hydrates its blobs and can turn a correct exit 2 into a
false exit 0. Observed: `promisor-grid.py:214-224` `blobless_clone` clones from
`file://{origin}` with the origin left in place, which matches the report. **No impact on this
lane:** none of my Git calls touched a promisor or blobless fixture. They were all static reads
of the pinned scratch clone (`log`, `diff`, `show`, `rev-parse`, `status`), and the grid was
not run. The floor result does not depend on fixture state. This does strengthen residual 1:
lazy-fetch safety, like the floor, depends on caller discipline rather than a mechanical guard.

No installs or updates were made, and no production, fleet, config, or service files changed.
Network use was limited to plain HTTPS GETs of official git/git RelNotes 2.6.0-2.56.0 and
v2.45.0 source/docs.
