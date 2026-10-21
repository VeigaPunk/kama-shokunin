# RevControls: control set for the round-23 repo-state grid

Seat: CloseKama22.RevControls (reviewer, leaf). Scope: which clean and defective real-shape cases must stay identical between the FROZEN arm (`4fe9339f`) and the CURRENT arm (uncommitted worktree `tools/report-landing-audit.py`). Findings only; no production edits.

Result in one paragraph: on rounds 10–22 of real history both arms are byte-identical in stdout and stderr, with and without errata. On 39 synthetic fixtures, 36 are identical. The other three are deliberate or repair deltas, recorded in §3 as expected differences, not controls. The grid's eight control rows (C01–C08) omit whole classes: ambiguity, registered source URLs, errata-invalid and errata-unmatched, and drafts (§4).

## 1. Pinned inputs

| item | value |
|---|---|
| FROZEN | `4fe9339f:tools/report-landing-audit.py`, blob `fcc255ce5115a749dfbd09cf992ba9851a2dc90a`, sha256 `09ecd63b…f`, 847 lines |
| CURRENT | live worktree (uncommitted), blob `76fbf442e2bb818509bd0b3fdf83a66e8c39df1e`, sha256 `684764108872cea153284dfec89848d5efdf5b30dd37db026434dea2b623e210`, 924 lines; snapshot at `out/RevControls/candidate-684764.py` |
| lane master | `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` |
| fleet HEAD | `7f48c5ed…` in HistoricalNoHarm `pins.txt`; `58cde6b1…` at my final check (the fleet moved during review) |
| tools | git 2.56.0, Python 3.14.8; no installs |

The live file changed three times while I reviewed it: `d0a96599` (919 lines, the HistoricalNoHarm pin) → `79d9e124` (922) → `684764` (924). Every result below is for `684764`. HistoricalNoHarm's `no-harm-gate=PASS` therefore covers `d0a96599`, not the final file (see F6).

## 2. Controls that must stay identical

### 2a. Real history (rounds 10–22, read-only CLI runs)

- `--rounds 10-22 --json`, with and without `--no-errata`: stdout and stderr byte-identical across arms (`cmp` on `realrun/*`). Exit 0 with errata, exit 1 without, matching `baseline-counts.txt`.
- Shape: 13 committed reports; required 54; post_report 5; defects 9 = `landed-omitted` 8 + `unresolved-full-hash` 1. All 9 are corrected by the 9 committed errata rows. `errata_unmatched` 0, `errata_invalid` 0.
- The one `unresolved-full-hash` is the round-20 splice (15 hex of `0957ce61…`, 25 hex of `33a67778…`; errata line 3).
- Zero real cases of `landed-ambiguous`, `landed-unresolved`, `landed-section-missing`. Those classes have only synthetic controls (K14–K19).
- Source exemption fires once in real history: round 22, `704366d7…`, in census form at `round-22.md` lines 109–111 and 145–147 (llama.cpp @704366d76). The registry has 88 S-rows, all 13 cells; the census accepts 65 (Registry section, https).

### 2b. Synthetic fixtures (`out/RevControls/controls.py`, 39 cases)

Method: each case builds fresh repos under `/tmp` (no inherited `GIT_*`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`). Both arms run on identical inputs. Compared: exit code, stdout, and stderr (exit-only for could-not-evaluate rows). Output: `out/RevControls/controls-output.txt`.

Clean (exit 0 in both arms):

| ID | fixture (real shape copied) | observed | why it must stay identical |
|---|---|---|---|
| K1 clean-basic | bullets with 7/9/10-hex and full hashes; boundary commit (author time == cutoff) and rebased commit (committer later) required; post-report commit excluded (rounds 18–20 bullet form) | exit 0, required 5, post 1 | required-set arithmetic (author time, cutoff, `checkpoint(rN)`) is what a pin or peel change would move silently; `required` and `post_report` are contract |
| K2 clean-table-prose | table rows and `**Pushed lane HEAD: `hash`.**` prose (tables rounds 11, 13, 16, 17; prose rounds 12, 14) | exit 0 | Landed scanning must see table cells and prose |
| K3 clean-utf8-body | em dash and accented body text | exit 0 | strict UTF-8 decode in `git()` (lines 124–127) must not refuse valid text |
| K4 clean-crlf | CRLF committed report | exit 0 | CR normalisation moved into `git()`; must equal the old universal-newline read (grid C07/C08 also cover CR-only) |
| K5 clean-nonascii-foreign-author | non-ASCII author on a non-kama commit | exit 0 | `surrogateescape` in `round_commits` must not change the `<lane>-shokunin` match |
| K6 clean-i18n-utf8-config | `i18n.logOutputEncoding=UTF-8` with a non-ASCII subject | exit 0 | a benign value must not alter subjects or authors (hostile ISO-8859-1 is grid F01) |
| K7 clean-log-follow-config | fleet `log.follow=true`, no rename | exit 0 | pinning follow off must not change the first-add cutoff when no rename exists |
| K8 clean-alternates-clone-shared | `git clone --shared` lane (objects/info/alternates) | exit 0 | docstring promises borrowed objects resolve as local; `check_history_repo` must not refuse alternates (grid C05) |
| K9 committed-errata default | errata read from the pinned tip, one committed row | exit 0, 1 corrected | rounds 10–22 depend on the committed-registry path (9 rows) |

Defects (exit 1 in both arms, identical defect set):

| ID | fixture | observed | why it must stay identical |
|---|---|---|---|
| K10 omission-uncited | required commit B (full hash) absent everywhere | `landed-omitted` B | the audit's core signal; real rounds 10, 18, 20 are this class (8 rows) |
| K11 omission-cited-elsewhere | C cited only in Work performed | `landed-omitted` C, `cited_elsewhere: true` | the flag drives errata decisions; real errata evidence says "cited in Work performed" |
| K12 fabricated-full-hash | 40-hex in no repo, no replace ref | `unresolved-full-hash` | the replace and lazy-fetch pins must not "find" a normal miss (grid C03 covers) |
| K13 mashup-real-shape | 15-hex prefix of A + 25-hex suffix of B (round-20 defect) | `unresolved-full-hash` | the exact real defect class; must stay detected with the pins on |
| K14 landed-unresolved-typo | `deadbee1` in Landed | `landed-unresolved` | `checkable_abbrev` plus the peel path |
| K15 section-missing | no `## Landed changes` heading | `landed-section-missing` + 5× `landed-omitted` (grid C04 covers) | synthetic only; zero real cases |
| K16 section-prefix-not-heading | `prefix ## Landed changes` line | same as K15 | `landed_match` anchor |

Ambiguity (no grid row exists):

| ID | fixture | observed | why it must stay identical |
|---|---|---|---|
| K17 ambiguous-commit-commit | 7-hex prefix shared by two commits | `landed-ambiguous` | the bare-name pass must survive; the peel answers `missing` for ambiguous commit names |
| K18 ambiguous-commit-blob | 7-hex prefix shared by one commit and one blob | **clean (exit 0)** in both arms | type-sensitive: `^{commit}` resolves to the single commit, and the peel overrides the bare result. A "simplification" that flags every all-object collision would add false defects. Lane holds 5,857 packed objects, so real frequency is low ([INFERENCE] ≈ 2×10⁻⁵ per cited 7-hex abbreviation) |
| K19 ambiguous-blob-blob | 7-hex prefix shared only by blobs | `landed-ambiguous` | all-object ambiguity is kept when no commit candidate exists |

Errata:

| ID | fixture | observed | why it must stay identical |
|---|---|---|---|
| K20 errata-file-corrects-section-missing | `landed-section-missing` corrected by `-`, plus 5 omitted rows, via `--errata` | exit 0 | non-resolvable kinds must not require a commit correction |
| K21 errata-abbrev-correction-accepted | 10-hex abbreviation of a real commit corrects a mashup | exit 0 | the candidate's hex 7–40 rule must still admit abbreviations |
| K22 errata-unmatched | row for a selected round that matches no defect | exit 1, `errata_unmatched` 1 | fail closed on stale ledger rows |
| K23 errata-invalid-blob | correction names a blob | exit 1, `errata_invalid` 1 | a correction must be a commit |
| K24 errata-invalid-fabricated | correction is a non-existent 40-hex | exit 1, `errata_invalid` 1 | same |
| K25 errata-invalid-omitted-differs | `landed-omitted` correction differs from the omitted token | exit 1, `errata_invalid` 1 | a landed-omitted correction must be that commit |

Registered source URLs (no grid row exists; registry row = 13 cells, `## Registry`):

| ID | fixture | observed | why it must stay identical |
|---|---|---|---|
| K26 source-registered-scheme-cited | registered full URL in body | exit 0, `source_url_hashes` [704366d…] | exemption active; registry is read at the pinned tip |
| K27 source-registered-census-cited | census form (no scheme), the real round-22 shape | exit 0, same hashes | the only real exemption in history |
| K28 source-unregistered-url | same hash, different path | exit 1 | exemption is path-exact |
| K29 source-bare-copy | bare 40-hex of a registered hash | exit 1 | exemption applies to URL occurrences only |
| K30 source-url-inside-landed | registered URL inside Landed | exit 1 (`unresolved-full-hash` + `landed-unresolved`) | exemption excludes the Landed span |
| K31 source-malformed-row | registry row with 12 cells | exit 1 | a row must have 13 cells to register |
| K32 source-registry-absent | no `corpus/SOURCES.md` on branch | exit 1 | legacy: no exemption |

Drafts and could-not-evaluate:

| ID | fixture | observed | why it must stay identical |
|---|---|---|---|
| K33 draft-render-fleet-cutoff | `--report` draft; cutoff from fleet first-add | render identical, exit 1 | draft cutoff must come from the committed report |
| K34 draft-uncommitted-now | uncommitted draft; cutoff = now (render compared, JSON not comparable) | render identical, exit 1 | the "now" path |
| K35 missing-report | no committed report, no draft | exit 2 both; stderr wording differs (§3) | could-not-evaluate must never become a verdict |
| K36 unusable-lane | nonexistent lane path | exit 2 both; stderr wording differs (§3) | same |

## 3. Expected differences (not controls; the grid must record them as deltas)

| ID | fixture | frozen | current | status |
|---|---|---|---|---|
| E1 errata-refname-correction | correction is the branch name `master` | exit 0 (accepted via rev-parse) | exit 1, `errata_invalid` 1 | deliberate: only hex corrections are looked up (lines 390–393). Grid F17 (correction `HEAD`) expects the same exit 1, which corroborates the intent. The Errata docstring (lines 34–40) still says only "not a lane/fleet commit" (doc drift). Real ledger unaffected: all 9 committed corrections are full 40-hex (`errata.tsv` rows 3–11). |
| E2 expdiff-lane-path-is-subdirectory | lane path is `repo/sub` | exit 0 (audits the repo) | exit 2: `could-not-evaluate: …/lane/sub: not a repository top level` | deliberate and documented (docstring lines 48–55, non-top-level at line 52; check at lines 437–438). Grid F21 expects the same exit 2. Default CLI paths are top-level, so real history is unaffected. |
| E3 expdiff-tag-shadows-branch-omitted | lightweight tag `master` at round-1 commit A; B omitted | exit 0, `required` 1, silently drops B | exit 1, `landed-omitted` B | repair of the grid F12 fault (F12 expects exit 1 with `landed-omitted`). Not a control. |

Stderr wording on exit-2 rows (exit codes identical): missing report reads `…not committed in fleet HEAD` (frozen) vs `…cannot read … at fleet HEAD: git show HEAD:…` (current). Unusable lane reads `git rev-parse --verify master^{commit}` (frozen) vs `git rev-parse --show-object-format` (current). Treat stderr of could-not-evaluate rows as non-contract.

## 4. Coverage gap in `tests/report-audit/repo-state-grid.py`

Existing control rows (lines 496–506): C01 clean, C02 real omission, C03 fabricated full hash, C04 section-missing, C05 shared clone, C06 errata corrects omission, C07 CRLF, C08 CR-only.

Not covered as controls by any grid row: K2, K3, K5–K7, K11, K13, K14, K16, K17–K25 (all ambiguity and all errata invalid, unmatched, and abbreviation cases), K26–K32 (registered source URLs, no row at all), K33–K36 (drafts and could-not-evaluate identity). K9 is covered only through C06.

Recommendation: add these as `control` rows. Compare the full JSON (`required`, `post_report`, `source_url_hashes`), not only defect kinds. Use exit+stdout+stderr for verdict rows and exit+stdout for exit-2 rows.

## 5. Findings (severity order)

- **F1 MEDIUM. The selftest (50/50 both arms) covers none of the new refusals.** No hunk of the diff touches `selftest()`; the last hunk is in `run()`. Refusals for shallow, grafts, promisor, non-sha1, non-top-level, ref-named citations, and non-hex errata are reachable only through the grid. Evidence: both arms print `selftest cases=50 failed=0`.
- **F2 MEDIUM. The git floor is 2.45, and nothing enforces it.** The 2.45.0 release notes state: "`git --no-lazy-fetch cmd` allows to run `cmd` while disabling lazy fetching of objects from the promisor remote" (https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.45.0.adoc, accessed 2026-10-21, line 119). The same search of 2.44.0.adoc found no match. Inference, not executed: on git < 2.45 the unknown option makes `git()` raise EvalError (lines 120–122), so every run exits 2, including all clean controls. The docstring states the floor (line 55); nothing checks it. Pin `git --version` in the grid or fail fast with a clear message.
- **F3 LOW. Errata docstring drift.** Lines 34–40 define validity only as "a lane/fleet commit". Lines 390–393 now also reject non-hex corrections (E1).
- **F4 LOW. Unreachable handlers.** `load_source_urls` catches `UnicodeDecodeError` at lines 247–248 and 258–259. `git()` converts decode failures to EvalError at lines 124–127 before anything escapes, so those handlers can never fire. Harmless, but misleading to a maintainer.
- **F5 LOW. Ambiguity semantics are type-sensitive and undocumented.** Docstring line 20 says only "an ambiguous abbreviation". K18 is clean while K17 and K19 are flagged. Document the rule, or the next "fix" will flip K18.
- **F6 PROCESS. Moving target.** The live file changed three times during review. HistoricalNoHarm's gate pins `d0a96599`. I re-ran rounds 10–22 (both modes) and the selftest on `684764`: identical, and 50/50. I did not re-run their gate, which writes into their output directory. Re-run the gate on the final file before integration.
- **F7 INFO. Partial clones and grid tradeoff row.** A promisor lane is now refused (exit 2) rather than lazily fetched, as documented. Grid T01 (tradeoff) expects exit 0 for a blobless partial clone. I did not verify that expectation against the promisor refusal in `check_history_repo`. L1 should confirm T01's fixture.

## 6. Not verified

- Grid fault rows F01–F23 and open rows O01–O02 are not run by me. The only refusal I ran is E2.
- SHA-256 (64-hex) citations are invisible to `FULL` and `ABBREV` in both arms. Not tested.
- Behavior on git < 2.45 is inferred from the release notes and the candidate's own comment. No older git was installed.
- Real history covers rounds 10–22 only. Round 23 is an uncommitted draft.
- Callers: the only production entry point is the CLI. A grep over `tools/` and `tests/` found no other caller; the grid and isolation-mutants refer to it only as a subject. No LSP device in this seat, so the grep is the literal fallback, not semantic proof.
- Synthetic fixtures copy the structure of real shapes; they are not real commits, except in the real-history runs.

## 7. Installs and writes

- Installs and updates: none. Used git 2.56.0 and Python 3.14.8 as installed.
- Written: this report; `out/RevControls/controls.py` (harness; reads its frozen input from `/tmp/kama-r23-RevControls/frozen-audit.py`, byte-identical to `out/RevControls/frozen-4fe9339f.py`); `out/RevControls/controls-output.txt`; `out/RevControls/candidate-684764.py` (tested snapshot); `out/RevControls/frozen-4fe9339f.py`; `out/RevControls/frozen-vs-candidate-684764.diff`; `out/RevControls/realrun/` (the four real-history outputs).
- Scratch: `/tmp/kama-r23-RevControls/`. Fixture trees under `/tmp/revcontrols-*` were removed after the run.
- No writes to lane or fleet repositories, refs, the index, or `.jj`.
