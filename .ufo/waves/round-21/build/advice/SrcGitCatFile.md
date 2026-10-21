VERDICT: partial - git-cat-file's documented `-e` clause supports C1's existence test; the manual defines no missing-object status and no `^{commit}` peel (gitrevisions); C2 has no bearing.
# SrcGitCatFile: SOURCES draft, kama round 21 (accessed 2026-10-21)
## 1. Registry check
- Draft commit a29bb84 `corpus/SOURCES.md`: 65 rows. S033 already registers https://git-scm.com/docs/git-cat-file for OUTPUT `<type>` raw bytes and OPTIONS `<type>`/`--textconv`/`--filters`; it does not cover `-e`.
- Same URL, distinct scope, no supersession: a new row is admissible; S033 stays untouched (append-only, rule 2).
- Next unused id: S066 (none in corpus/ or round-21/; ScorecardDraft placeholder reads "S066–S0NN", so L1 renumbers if a sibling lands first).
- `^{commit}` is documented in gitrevisions(7), not git-cat-file. One row only, so the peel is a candidate second row (§3).
## 2. Sources and verbatim quotes
- git-cat-file manual, https://git-scm.com/docs/git-cat-file, "last updated in 2.56.0"; latest version 2.56.0 (2026-09-28). Local `man -P cat git-cat-file | col -b` (exit 0) footer "Git 2.56.0 2026-09-27"; its `-e` text matches (justified spacing aside).
  - Q1, 12 words, OPTIONS `-e`, sentence 1: "Exit with zero status if <object> exists and is a valid object."
  - Q2, 17 words, OPTIONS `-e`, sentence 2: "If <object> is of an invalid format, exit with non-zero status and emit an error on stderr."
  - Q3, 11 words, OUTPUT: "If -e is specified, no output, unless the <object> is malformed."
- gitrevisions, https://git-scm.com/docs/gitrevisions, "last updated in 2.56.0" (2026-09-28).
  - Q4, 14 words, SPECIFYING REVISIONS, `<rev>^{<type>}`: "dereference the object at <rev> recursively until an object of type <type> is found"
- Negative sweep of the full 677-line manual text for missing|absent|not exist|cannot be resolved: every hit sits in BATCH OUTPUT or --follow-symlinks text. Non-batch `-e` states no missing-object status.
## 3. Draft SOURCES row (contract v1; L1 pastes after S065; not written to the lane)
| S066 | Git git-cat-file manual, OPTIONS `-e` — https://git-scm.com/docs/git-cat-file | docs | A | exit status of `git cat-file -e` as an existence-and-validity test for one object name, at Git 2.56.0; not the status for a missing object, not `^{commit}` peeling | OPTIONS `-e`, first sentence “Exit with zero status if <object> exists and is a valid object.”; OUTPUT `-e` clause; manual last updated in Git 2.56.0 (2026-09-28); installed git 2.56.0 man page has the same text; opened 2026-10-21 | `-e` is an existence-and-validity test: zero when the object exists and is valid, non-zero with a stderr error when the format is invalid. No status is documented for a well-formed missing object, so test `== 0` only. [INFERENCE] Bare `-e` also passes trees and blobs, so a commit-only claim needs `^{commit}` from gitrevisions (not this row). | queued | 2026-10-21 | on-release | — |
- Gate (rule 1): URL https://git-scm.com/docs/git-cat-file; accessed 2026-10-21; quote Q1 at OPTIONS `-e`.
- Search log (rule 5): 2026-10-21 round-21 `git cat-file -e` source. Question: does the documented -e clause define existence/validity, a missing-object status, or `^{commit}` peeling? Where: git-cat-file 2.56.0 (OPTIONS, OUTPUT, BATCH OUTPUT); gitrevisions 2.56.0 (SPECIFYING REVISIONS); local git 2.56.0 man page. Identified 3, screened 3, included 1 (S066), excluded 0; gitrevisions Q4 quoted, not registered (one-row limit). Stop: the `-e` clause and the absence sweep located.
- Status queued (opened; C1's `is_object` rests on this clause). mined needs an existing used-by path; none yet. Flip to mined when a knowledge entry or lesson cites S066 by path; flip to rejected only if a versioned page changes the `-e` wording (then a supersedes row).
- Candidate second row, not drafted: gitrevisions, tier A, anchor SPECIFYING REVISIONS `<rev>^{<type>}`, 2.56.0 (2026-09-28), Q4, queued.
## 4. Executed probe (git 2.56.0)
Script `out/SrcGitCatFile/probe-cat-file-e.py`, transcript `out/SrcGitCatFile/probe-cat-file-e.out`; run this session, exit 0.
| token | `-e` rc | `-e` stderr | `-t` rc |
|---|---|---|---|
| commit, commit^{commit}, commit^{tree}, short 7-hex, v1^{commit}, lightweight ref | 0 | none | 0 |
| tree, blob, annotated tag | 0 | none | 0 |
| tree^{commit}, blob^{commit} | 128 | "expected commit type, but the object dereferences to tree/blob type" | 128 |
| missing 40-hex | 1 | none | 128 "could not get object info" |
| missing 40-hex^{commit}, missing 7-hex, nosuchref, zzz | 128 | "Not a valid object name" | 128 |
- F1: a well-formed absent object exits 1 at full length (silent) but 128 when abbreviated (stderr). The manual specifies neither; test `== 0` only.
- F2: bare `-e` accepts tree, blob and tag; `^{commit}` refuses tree and blob with 128 (gitrevisions "barf").
- F3: unresolvable names exit 128 with stderr; the manual's "invalid format" does not name them. A gap, not a contradiction.
## 5. C1 / C2
- C1, draft `tools/report-landing-audit.py` (read, not run): `is_object` L70-76 runs `git cat-file -e` on the token or `token^{kind}` and treats rc 0 as present. Unresolved-full-hash (L117-118) uses bare `-e`, consistent with F2; landed-unresolved (L127-129) uses `^{commit}`, consistent with F2. Both F1 non-zero codes count as absent.
- Why partial: the success direction (zero for an existing valid object) is documented; absent-to-non-zero is observed (F1), not stated, and the peel lives in another page.
- [INFERENCE, not executed] An ambiguous abbreviation would exit 128 and count as absent; only 7–39-hex landed tokens could be affected.
- C2: no bearing. The only symlink text is `--follow-symlinks` for `tree-ish:path` in batch mode (git tree entries). Install-tree soname symlinks are filesystem state; S066 neither supports nor refutes C2.
## 6. Census (CORPUS.md §Census on a scratch copy; bash rc 0, both runs)
- before: rows 65; malformed 0; tier A=62 C=3; status mined=52 queued=6 rejected=7; dup ids none; enum violations none; mined used-by missing none.
- after S066 appended (scratch only): rows 66; malformed 0; A=63 C=3; mined=52 queued=7 rejected=7; all else unchanged.
## 7. Commands, records, cleanup
- `read` git-scm cat-file and gitrevisions: ok. `man -P cat git-cat-file | col -b`: rc 0. `git clone -q` lane to scratch: rc 0; `checkout -q a29bb84…`: rc 0; `rev-parse --verify a29bb84…^{commit}`: rc 0; `cat-file -e a29bb84…^{commit}`: rc 0; `ls-tree -r --name-only a29bb84… -- tools`: rc 0. Probe: rc 0. Census: rc 0 ×2. Greps: ok.
- Installs/upgrades: none; system git 2.56.0 equals the latest documented version. man-db and util-linux `col` were already present.
- Scratch `/tmp/kama-r21-SrcGitCatFile` removed (`rm -rf`, then absence test rc 0). Lane, fleet and siblings untouched; no processes started.
