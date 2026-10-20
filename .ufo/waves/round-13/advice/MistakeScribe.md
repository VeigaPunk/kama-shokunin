# Round 13 — MistakeScribe draft: KQ15 two-proposition wording row

Author advisor (leaf, no delegation). Draft only. The lesson, QUALITY.md, SKILL.md, fidelity.py and all other lane files were not edited. Start revision `941bb32c3f591bc63cbf7579b2b6c552228307cd` (`round-13/inherited-state.json`, `round-13/claims.json` `before_commit`).

Executed: read-only static inspection only: `git cat-file blob HEAD:<path>` with `grep -c -F` / `grep -n` / `wc`, `sed`/`cat` of lane files, `man -P cat git-show | col -b`. No build, test, linter, formatter, gate (`fidelity.py`, `reproduce.py`), selftest, or endpoint command was run. Tools installed or updated: none.

Denominator: two routed KQ15 propositions, as declared in `.ufo/waves/round-13/claims.json` (C1, before 2, after target 0): (P1) exit/finding distinction; (P2) capture/comparison method. Score 7 → 7, delta 0. Calibration only; no runtime, serving, freshness, capability or expansion claim.

## 1. Measured red-before (static, pre-edit)

Command: `git cat-file blob 941bb32:corpus/QUALITY.md` (HEAD at scribe time; blob has 49 lines). Counts of literal strings:

| String | Count in start blob | Meaning |
|---|---:|---|
| `distinct nonzero exits` | 1 | P1 defect present (QUALITY.md:49) |
| `git show <pinned-commit>:<source-path>` | 1 | P2 defect present (QUALITY.md:49) |
| `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` | 0 | P1 required assertion missing |
| `capture: git show; comparison: git cat-file blob` | 0 | P2 required assertion missing |
| `git cat-file blob` | 0 | no KQ criterion names the comparison command |

Red-before = 2 missing assertions, 2 defective formulations. Fix counts (2 → 0) may be reported only after the probe measures the post-edit blob and isolated red controls; neither has been run by this seat.

## 2. Grounding outside round-12 D1

Verified from the working tree and committed files; quotes located:

- **P1 exit mapping.** `.ufo/waves/round-12/fidelity.py:24-25`: "Exit codes: 0 clean; 1 source_mismatch; 2 snapshot_tampered, source_unavailable, snapshot_unavailable, manifest_invalid, unpinned or internal_error." Line 319: `exit_code = 0 if finding == 'clean' else (1 if finding == 'source_mismatch' else 2)`. Selftest records `snapshot-tampered` and `source-unavailable` both expect exit 2 with different finding IDs (`fidelity.py:501-502`, `:518-519`). So "distinct nonzero exits" is false for tamper vs unavailable; they share exit 2. Distinguishing feature is the stable finding ID (`finding` key; selftest `ok` requires exit AND finding, `:423-425`).
- **P1 registry agrees with code.** `SKILL.md:396`: "0 clean; 1 failed (`source_mismatch`); 2 could-not-evaluate (`snapshot_tampered`, `snapshot_unavailable`, `manifest_invalid`, `source_unavailable`, `unpinned`, `internal_error`)".
- **P2 gate comparison command.** `fidelity.py:271-273`: `git_run(repo_path, 'cat-file', 'blob', f'{SOURCE_REVISION}:{SOURCE_PATH}')`. Selftest reference read `fidelity.py:442-444` also `cat-file blob`. `reproduce.py:80`: `git("cat-file", "blob", SPEC, ...)`. No `git show` call exists in `fidelity.py` or `reproduce.py` (grep verified).
- **P2 registry is half-consistent.** `SKILL.md:396`: snapshot "captured byte-exactly via `git show`". `SKILL.md:406-407`: comparison described only as "immutable git blob at the code-constant revision and path". The string `cat-file` does not occur in `SKILL.md` (grep: zero hits).
- **P2 lesson.** `corpus/lessons/round-12.md:14-15`: "Capture uses `git show` (S032); the same measurement command independently reads the pinned historical blob with `git cat-file blob` for comparison." `round-12.md:180`: "the actual gate reads source bytes using `git cat-file blob`".
- **P2 capture provenance.** `.ufo/waves/round-12/spec.json:9`: "Capture bytes directly subprocess.check_output git show (permitted artifact generation, not tests)". `frozen/expected.json` contains no capture-command field (schema keys: schema, snapshot_path, snapshot_sha256, source_revision, source_path, source_oid, source_sha256, source_bytes, expected_verdict). So the `git show` capture claim is spec/lesson-reported, not recorded in a committed receipt. [INFERENCE on the historical capture command; byte equality does not distinguish `git show` from `cat-file` output.]

**Correction to D1's grounding.** `round-12-verifier-spotcheck.md:147` says KQ15 should distinguish `git show` capture from `git cat-file blob` comparison "as the lesson and registry already do." The lesson does; the registry names `git show` for capture but never names `cat-file` for comparison. KQ16 must not cite the registry as support for the comparison command; cite `fidelity.py:271-273` and `round-12.md:14-15`.

**Unverified advisor claim not to reuse.** `.ufo/waves/round-12/advice/ReviewGateInterface.md:45` says `git show` applies textconv and config filters. The local `git-show` manual (git 2.55.0) states only that textconv is "enabled by default only for git-diff(1) and git-log(1), but not for git-format-patch(1) or diff plumbing commands" (man page lines 1357-1362); it does not state the blob-`git show` behavior. Not verified by any run here. KQ16 should state the command split without a textconv rationale.

## 3. Draft Mistakes row (one row, round-12 table shape)

Round-12 columns: `| Class | Evidence pointer | Captured-by | Fix / falsification obligation |` (`corpus/lessons/round-12.md:59-66`). Class word below is a proposal, not in the round-12 vocabulary [INFERENCE: no existing class fits].

| Class | Evidence pointer | Captured-by | Fix / falsification obligation |
|---|---|---|---|
| criterion-wording (proposed) | `corpus/QUALITY.md:49` (KQ15, appended round 12 with "no outside review yet") states mismatch, tamper and unavailable source have "distinct nonzero exits" (P1) and names `git show <pinned-commit>:<source-path>` as the comparison blob fetch (P2). Code: `.ufo/waves/round-12/fidelity.py:24-25,319` (exits 1, 2, 2; IDs distinct) and `:271-273` (comparison by `git cat-file blob`); registry `SKILL.md:396,406-407`; lesson `corpus/lessons/round-12.md:14-15,180`; spec `.ufo/waves/round-12/spec.json:9`. | KQ15 (defective; KQ16 supersedes only its two formulations). Round-12 KQ14 content correspondence does not name either formulation. | Append KQ16 (new dated row; KQ15 bytes preserved) containing the exact literal phrases `source_mismatch=1; snapshot_tampered=2; source_unavailable=2` (shared exit 2; stable distinct finding IDs discriminate) and `capture: git show; comparison: git cat-file blob`. **Red-before (measured, static, start blob):** literal assertions 0/2 present; defective phrases 1 + 1. **Post-fix target:** assertions 2/2 present; defective phrases still present only in historical KQ15 bytes. **Red controls (not run by this seat; probe owns):** (a) mutant with KQ15 wording restored must fail; (b) mutant altering `exit 2` or the literal finding list must fail; (c) mutant dropping `git cat-file blob` from the KQ16 comparison phrase must fail. |

## 4. Limits

- Only P1 and P2 are in scope. Other KQ15 clauses (manifest fields, unpinned rule, correction procedure) were read and match the code but are not counted here.
- The `git show` capture command for `frozen/corpus/SOURCES.md` is spec/lesson-reported; no committed receipt records it. Byte equality (`9dc40d25…`, 18898 bytes) is closure-observed and not re-executed here.
- Textconv and replace-ref behavior of `git show` vs `cat-file` is not verified here; the gate passes `--no-replace-objects` on every git call (`fidelity.py:95`, `:387`; `GIT_NO_REPLACE_OBJECTS` at `:84`).
- The lesson cites Git 2.56.0 for S032; the local git is 2.55.0. Version difference not tested.
- Counts above are literal-string greps of one blob, not semantic proof. Probe and criterion seats own the post-edit measurement.
- No Mistake row here is execution evidence. The row defines red-before, fix and falsification for the probe to run once after integration.
