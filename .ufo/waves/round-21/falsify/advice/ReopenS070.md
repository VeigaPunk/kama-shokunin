VERDICT: partial - anchor, 2.56.0 pin, verbatim quote, status and used-by agree; teaches drops "within the repository" and the §Gate quotes only its first clause.
Attacked: S070 row, corpus/SOURCES.md:82 (commit a6617149; identical at b76727f3 and in the working tree); round-21.md §Gate line 46; CORPUS.md contract v1 copy. Lane not modified.

## Re-open (2026-10-21)
- https://git-scm.com/docs/gitrevisions fetched (reader and HTML). Header: "gitrevisions last updated in 2.56.0"; version table lists 2.56.0 (2026-09-28) as latest.
- git.git tag v2.56.0 (`git ls-remote --tags`, exit 0): tag object 2478544319491bbd2a42cc57a83e3d2f4730a280, peeled commit a018953688f1b10bddf91bff8747068f5f4746a4. Documentation/revisions.adoc sha256 b23a9eb17d9b193adccee6b79cb1c1fef450703dae925a33b8a1c6f6639d82ff, 424 lines (matches the build seat's pin).

## Field verdicts
| Field | Row value | Verdict | Evidence |
|---|---|---|---|
| id | S070 | AGREE | unique (census dup-ids empty); introduced once, commit 1471344 (`git log -S`) |
| source | Git gitrevisions(7), canonical URL | AGREE | URL serves 2.56.0 now; /docs/gitrevisions/2.56.0 has the same normalised length (18,408 chars) and all six probes. Unversioned URL drifts at next release; recheck on-release covers it |
| kind, tier | docs, A | AGREE | official documentation for this scope |
| scope | abbreviations + `<rev>^{<type>}` peeling, 2.56.0, not report policy | AGREE, minor gap | build draft's "not endpoint truth" exclusion was dropped |
| anchor | `<sha1>` line 16; `<rev>^{<type>}` lines 175–176; v2.56.0 | AGREE | adoc: `<sha1>` entry line 14, quote line 16; `<rev>^{<type>}` heading line 173, sentence 175–176 |
| teaches | unique leading substring; `^{commit}` peels; cited token must resolve uniquely to a commit | DISAGREE (partial) | see next section |
| opened, recheck | 2026-10-21, on-release | AGREE | opened today; valid cadence |
| status, used-by | mined; corpus/lessons/round-21.md | AGREE | census mined=60 of 74; lesson cites S070 at lines 19 and 46; path exists; mined-used-by-missing empty |
| format | 11 cells | AGREE | census NF!=13 = 0; tier/status/kind enum and inflation checks empty |

## Teaches vs page
1. "unique leading substring": the page says "a leading substring that is unique **within the repository**" (adoc 16). The row drops the qualifier, and it matters: `lookup()` (tools/report-landing-audit.py:93–117, repos at :176) runs `cat-file --batch-check` in lane and fleet and marks a token found if any repo resolves it, so uniqueness is judged per repository and then unioned.
2. Peel clause agrees (adoc 175–179; HTML): "<rev>^{commit} describes the corresponding commit object". Omitted: the page's failure case, "or the object cannot be dereferenced anymore (in which case, barf)".
3. "so a cited token must resolve uniquely to a commit" is not on the page. [INFERENCE] lane design, consistent with the tool's `^{commit}` lookups (:189–190, :250–251, :296–297). Mark it or drop it. The cell also bundles two facts and a consequence; the contract asks for one grounded benefit.

## Gate (round-21.md line 46)
- URL, revision and location agree; line 16 verified. Quote "a leading substring that is unique within the repository." is verbatim (adoc 16, both HTML renders, man page): 9 words, within 25.
- Access date sits once in the §Gate preamble (2026-10-21). Agree at section level.
- DISAGREE on grounding: nothing quotes the peel clause. The build draft (build/advice/SrcGitRevisions.md:10) had the 14-word quote "dereference the object at '<rev>' recursively until an object of type '<type>' is found" (adoc 175–176); the Gate table dropped it. Contract rule 1 requires the quote to ground teaches.

## Contract v1
- Rule 1: met except the peel-clause grounding above.
- Rule 2: S070 is new this round; no in-place change is logged. Any teaches fix must be a `supersedes S0NN —` row.
- Rule 5: search log at SOURCES.md:105 (12 identified, 12 screened, 9 included, 3 excluded, stop rationale). Its "S066–S073 mined, S074 queued" matches the census.
- CORPUS.md copy equals .ufo/waves/kaika/SOURCES-CONTRACT-v1.md after whitespace and heading-depth normalisation (### vs ## on Shape, Rules, Census). AGREE.

## Probe (git 2.56.0, scratch repo, removed)
- `v1^{commit}` (annotated tag) rc 0 → commit. `<tree>^{commit}` rc 128, "expected commit type, but the object dereferences to tree type". `<blob>^{commit}` rc 128. `<blob>^{blob}` rc 0.
- Unique 7-hex prefix rc 0. Colliding 4-hex prefix `c508` rc 128, "short object ID c508 is ambiguous"; `--disambiguate` lists 2 objects.

## Proposed (L1 decides; lane untouched)
1. Add the 14-word peel quote with location (adoc 175–176, v2.56.0) to the Gate. No row change needed.
2. Teaches: either a superseding row (rule 2), or record "within the repository" and clause-3 inference status in the round-21 Gate.
3. Optional: pin source to https://git-scm.com/docs/gitrevisions/2.56.0.
4. Side observation: the lane working tree's tool is 617 lines (repos at :184, lookups at :198/:259), unlike the 562-line tool at a6617149 and b76727f3. Not examined further; C1 line cites above use the measured commit.

## Commands and exits (all executed)
- curl adoc, HTML latest, HTML 2.56.0: 0, 0, 0. sha256sum: 0. `git ls-remote --tags`: 0.
- `git clone -q` lane: 0; `git checkout -q a6617149…`: 0; `git --version`: 0 (2.56.0).
- Census (CORPUS.md commands, clone at a6617149): every command rc 0. Rows 74; malformed 0; tiers A70 B1 C3; status mined60 queued7 rejected7.
- `git show` of SOURCES.md and round-21.md at a6617149 and b76727f3: rc 0. S070 row, SOURCES.md and lesson identical across tip, measured commit and working tree.
- `git log -S'| S070 |'`: rc 0. `man --nh --nj 7 gitrevisions`: rc 0 (both quotes present). `man -w 7 gitrevisions`: rc 0, sha256 29d3cb61….
- Installs: none (curl, git 2.56.0 and man were present). Scratch /tmp/kama-r21-ReopenS070 removed: rm exit 0; absence check exit 1.
