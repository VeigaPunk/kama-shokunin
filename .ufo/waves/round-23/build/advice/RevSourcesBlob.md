# RevSourcesBlob: `load_source_urls` review (replace refs, decode)

Scope: `tools/report-landing-audit.py`, `load_source_urls` and the decode/replace path it depends on. Findings only; no production edits. Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`, base `master=4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (git 2.56.0, Python 3.14.8).

Revisions reviewed (sha256 of `tools/report-landing-audit.py`):
- base `4fe9339f` (via `git show`): `09ecd63b…`, 847 lines.
- snapshot A: `d0a96599…`, 919 lines (first review).
- live at report time: `79d9e124…`, 921 lines. Diff A→live is one addition: a `--show-prefix` refusal in `check_history_repo` (live 434-435). The file is still being edited by sibling seats; line refs below are live `79d9e124` unless marked base.

## Answers

**1. Can a replaced SOURCES.md blob change classification?**
- Base `4fe9339f`: yes. A replaced registry blob, a replaced branch commit, or a replaced `corpus` subtree that lists a fabricated 40-hex URL turns an unresolved citation into an exempt one (exit 0, rows V2-V4).
- Live: not through `refs/replace`. `GIT_ISOLATION` (91-95) puts `--no-replace-objects` on every git call. `git()` (113) is the only `subprocess` call site. `load_source_urls` reads via `ls-tree` (244) and `cat-file blob` (255), and both are covered. A repo-local `core.useReplaceRefs=true` does not re-enable replacement: the flag beats repo config and command-line `-c` (plain-git probe below; row V5 rc 1).
- Ref-name channel: base resolves `--branch` by name, so `refs/tags/master` shadows `refs/heads/master` (base rc 0). Live pins the lane tip with `resolve_branch` (451-457, heads first) and passes the SHA on (`tip`, 477, 479), so the shadow case is rc 1.
- Still open: writers of `.git/objects` (not refs). See F2.

**2. Is decode already safe here?** Yes for SOURCES.md. No traceback path remains on this route.
- Live `git()` decodes stdout strictly and converts failure to `EvalError` (122-125). D1 (non-UTF-8 byte in registry): rc 2, `could-not-evaluate: git cat-file blob … output is not UTF-8`.
- Base bug, now fixed: base `audit_round` (283-286) caught only `EvalError` around `git show HEAD:<report>`. D2 (non-UTF-8 byte in a committed fleet report) crashed with `UnicodeDecodeError`, rc 1. Live: rc 2.
- The `except UnicodeDecodeError` clauses in live `load_source_urls` (245-246, 256-257) can never fire, because `git()` converts first. Dead code (F4).
- Caveats: BOM (F3). Strict decoding means one stray byte in the registry makes every audit exit 2. That is consistent with the contract but is an availability cost.
- Real registry on lane `master`: 85,060 bytes, valid UTF-8, no BOM, no CRLF, 65 census rows (read-only `cat-file`, census function from snapshot A; identical in live).

## Verification

Fixtures: fresh temp repos under `/tmp` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`. Tool run as `--branch master --lane kama --rounds 1-1 --no-errata --json`. "Cite" means `https://example.invalid/fake/commit/<fake40>` unless noted. rc: 0 clean, 1 failed, 2 could-not-evaluate.

| Case | base `4fe9339f` | live `79d9e124` |
|---|---|---|
| V0 control: registry lists the URL, cite URL | 0 | 0 |
| V1 registry lacks the URL | 1 unresolved-full-hash | 1 |
| V2 replace SOURCES blob with fake registry | **0 (false clean)** | 1 |
| V3 replace branch commit with fake tree | **0** | 1 |
| V4 replace `corpus` subtree | **0** | 1 |
| V5 = V2 + repo `core.useReplaceRefs=true` | **0** | 1 |
| V6 `refs/replace/<fake40>` to existing blob, bare cite | **0** | 1 |
| V7 replace committed fleet report blob | **0** | 1 |
| Tag `master` shadows branch (fake registry) | **0** | 1 |
| D1 non-UTF-8 byte in SOURCES.md | 2 | 2 |
| D2 non-UTF-8 byte in committed fleet report | 1 (traceback) | 2 |
| D3 CRLF registry control | 0 | 0 |
| D4 UTF-8 BOM before `## Registry` | 1 (false failure) | 1 (false failure) |
| D5 non-UTF-8 byte in draft via `--report` | 2 | 2 |
| L-i unresolvable `a1b2c3d` in 2nd `## Landed changes` | **0** | **0** |
| L-ii registry URL with 40-hex cited in 2nd section | **0** | **0** |
| L-iii real commit cited only in 2nd section | 1 (false failure, landed-omitted) | 1 |
| L-iv same commit cited in 1st section (control) | 0 | 0 |
| Forged loose object under the real SOURCES blob name | not run | **0** |

Plain git 2.56.0, blob replaced by fake: default `cat-file -p` returns fake; `--no-replace-objects` returns real; `--no-replace-objects` plus repo `core.useReplaceRefs=true` returns real; `--no-replace-objects` plus `-c core.useReplaceRefs=true` returns real.

Forged loose object: `cat-file -p <real>` returns the forged bytes both by default and with `--no-replace-objects`. `git fsck --full` reports `hash-path mismatch` (rc 3). Git does not verify object hashes on read, and the tool never runs `fsck`.

## Findings

### F1. High (live; adjacent to the target): a second `## Landed changes` section is ignored
- `landed_match` (167-169) uses `re.search`, so only the first section is seen. `audit_round` derives the forced-check span (311-313, `classify_full_hashes` 272-288), `cited` (324), and `cited_anywhere` (332) from that one section.
- Result: L-i and L-ii are false cleans (rc 0). L-iii is a false failure (a real commit cited only in the second section is reported as `landed-omitted`).
- Contract: the module docstring (about lines 12-26) describes a single section. `unresolved-full-hash` exempts URLs only "outside `## Landed changes`", which excludes every section.
- Fix direction (not implemented): treat all `## Landed changes` sections as the section, or fail closed (`EvalError` or a defect) on more than one. Add selftest fixtures for L-i through L-iv. Selftest not run.

### F2. Medium, decision (residual; already a declared non-claim): object-store writers defeat content-keyed classification
- `GIT_ISOLATION` neutralizes refs and repo config. Nothing verifies object content. A forged loose object under the registry's real blob name gives live rc 0 (FORGE row).
- The docstring already scopes this out (lines 48-51: "other repository-local channels are not claimed"). Recommendation: keep that scope and name "object-store writers" explicitly, so `refs/replace` neutralization is not read as integrity.
- Optional, untested: for SOURCES.md only, hash the raw `cat-file blob` bytes (not `git()`'s CRLF-normalized text, line 126) and require `sha1(b"blob %d\0" % len(raw) + raw) == fields[2]`, else `EvalError`. That would catch replaced or forged registry blobs without the flag. It does not cover commits or reports.

### F3. Low, false failure: UTF-8 BOM disables the registry
- `census_source_urls` heading test (218) fails on `\ufeff## Registry`. `in_registry` never turns on, `forms` is empty, and `load_source_urls` returns `None` (legacy). D4: cited URL gives rc 1 in base and live.
- Fix: strip a leading `\ufeff` from the SOURCES text inside `load_source_urls`, not globally in `git()`. Decoding is otherwise safe.

### F4. Low, cleanup: dead handlers and misleading parameter
- `load_source_urls` `except UnicodeDecodeError` at 245-246 and 256-257 never fire (`git()` converts at 122-125). Delete both; no shims.
- The parameter `branch` (241) now receives a commit SHA from `run()` (479). Rename it to `tip`, so the error text `cannot read {branch}:{SOURCES}` stops presenting a SHA as a branch name.

### F5. Info: `resolve_branch` fallback
- `resolve_branch` (451-457) retries as `<name>^{commit}` on any `EvalError`. If `refs/heads/<name>` is absent and a same-named tag exists, the tag binds. This matches the docstring ("other revisions as given"). No change needed unless the lead wants fail-closed when the heads ref is absent.

### F6. Info: scale is not a concern at realistic sizes (snapshot A; live differs only in `check_history_repo`)
- Registry with 20k rows compiles in 1.46 s, with 60k rows in 4.40 s (pattern 9.5 MB). No non-`EvalError` is raised.
- 2000 URLs against a 1 MB report: 2.50 s. 200 URLs against 1 MB: 0.21 s. 4000 FULL hashes inside URLs: 0.39 s. `classify_full_hashes` is O(F·U) with early exit, which is fine at these sizes.

### F7. Info (live): `check_history_repo` refuses a lane subdirectory (`--show-prefix`, 434-435)
- Read from the diff only; not exercised.

## Not verified
- git versions other than 2.56.0; the base's locale-dependent decode; commit-graph or `objects/info/alternates` forgery; grafts and shallow (refused by live `check_history_repo`, not exercised).
- `--selftest` not run. No audit run against real lane or fleet repos; the real registry was read with `git cat-file` only.
- Line numbers are pinned to live `79d9e124`; the file is still changing under sibling seats.
- Recommended changes are untested except where a matrix row says so.

## Files written
- `.ufo/waves/round-23/build/advice/RevSourcesBlob.md` (this report).
- Scratch outside the lane tree: `/tmp/rsb/{base,cur,cur2}/report-landing-audit.py` (pinned copies of base, snapshot A, live); fixtures in `/tmp/rsb-e1-vzwb4h6x/` and `/tmp/rsb-e2-pgmcw7l_/`.
- No lane tracked files, no git index writes, no commits. No tools installed or updated (used the existing git 2.56.0 and Python 3.14.8).
