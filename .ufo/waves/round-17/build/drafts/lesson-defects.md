# Round 17 lesson draft — routed defects and jj risks

Draft by ScribeLessonDefects (build wave, round 17). Append-ready prose for L1 to integrate. Not integrated; no lane doc was edited. Access date for every source below: 2026-10-20. Lane tip read as `master` = `cff9e62f05aa7cfb9059444f62eb787100719713`; the round-16 audit snapshots were pinned at `726f737`, so each audit fact below is marked either "re-verified at master" or "audit-reported, not re-verified".

## Routed defects from round-16-verifier-spotcheck.md

Source list: `corpus/lessons/round-16-verifier-spotcheck.md:180-189` (`## Routed defects (kama, next steered round)`, items 1–6; identical at master line 180). Each disposition below states what the round-17 state is, what this draft verified, and what L1 must decide.

| # | Routed defect | State at master `cff9e62` | Draft disposition |
|---|---|---|---|
| 1 | Wave provenance (policy version, falsify `validation.json`, `taskCall` canonicalization, pending spawns) | Open. Parts confirmed; the producer of the build digest is unlocated | Carry forward; L1 decides fix owner |
| 2 | Falsify `verdict_first_lines` 36/41/2 vs committed count | Open. Lesson's committed count re-derived as correct | Appended note only |
| 3 | `SOURCES.md` S041 anchor/teaches amended in place | Open. Contract rule confirmed; amendment confirmed | Superseding row or disclosure (L1 decides) |
| 4 | "every non-frontend path" must exclude OPTIONS | Open. Line anchors confirmed; scope is wider than the lesson names | Append correction; widen scope decision for L1 |
| 5 | Install disclosure precision (tarball, no `/usr/bin/llama-server`) | Open. Both facts confirmed on the host | Name in L0 follow-up; install unchanged |
| 6 | Carried debt: surviving `check.py` mutants; live-harness weak checks; `finally` leak; M3, M7 | Open. Count not re-measured in this draft | Carry as debt; C1/C2 build seats own the repair |

### 1. Wave provenance

Routed text (`round-16-verifier-spotcheck.md:182`): "Record the policy version in every wave's validation, and give falsify a `validation.json` with a policy block."

- Re-verified: `.ufo/waves/round-16/build/validation.json` exists and contains a `"policy": {` block. `.ufo/waves/round-16/falsify/` has no `validation.json` (directory listing, 2026-10-20). The routed gap is real.
- Re-verified: `.ufo/waves/round-16/falsify/provenance-ledger.json` records `"spawned": 0` and `"refused": 0`. The routed claim that the ledger shows zero spawns for 79 seats is consistent with that file.
- Re-verified by code reading: `.ufo/waves/round-16/dispatch-provenance.py:155` reads: "any dict key literally "refused" or "spawned" carrying an int adds". The file contains zero occurrences of the string `pending` (`grep -c pending`), so async pending spawns are not counted. This is a code reading, not an execution.
- Re-verified: `dispatch-provenance.py:92` and `:130` use `ensure_ascii=False`. The audit's build `taskCall` digest `cdf02ba7…` was reported to reproduce only with `ensure_ascii=True`. This draft did not locate the code that computed that digest in the lane tree (`make_spec.py:225` writes a spec with `ensure_ascii=False`, which is not the digest). [L1 fills: the producer path for `cdf02ba7…` and for the falsify digest `72e81bc6…`.]
- Decision for L1: whether the `ensure_ascii` canonicalization and the `pending` counting are fixed in round 17 or carried.

### 2. Falsify summary accuracy

Routed text (`round-16-verifier-spotcheck.md:183`): "Correct `verdict_first_lines` by an appended note: 36/41/2 recorded vs 36/43/0 committed."

- Re-verified: `.ufo/waves/round-16/falsify/completion-summary.json:22-26` records `"confirm": 36, "partial": 41, "refute": 2`.
- Re-verified by counting the 79 advice files in `.ufo/waves/round-16/falsify/advice/`: a `VERDICT:` line exists in all 79. Under "VERDICT on line 1": 74 files (34 confirm, 40 partial, 0 refute). Five files open with a `#` heading and carry VERDICT on line 3: `ConnectSiblingCollision.md` (partial), `ExecNoPythonFallback.md` (confirm), `ReviewLesson.md` (partial), `ScribeNumbersLedger.md` (partial), `ScribeReportWaves.md` (confirm). Any-line total: 36 confirm / 43 partial / 0 refute.
- The routed count `36/43/0` is therefore correct under "any line", and "5 of 79 do not open with VERDICT" is correct under "line 1". The appended note must state which definition it uses. The recorded `36/41/2` in `completion-summary.json` is not reproduced by either definition.
- Disposition: appended note in the round-16 lesson or in the round-17 lesson. Do not edit `completion-summary.json`, which is a committed record.

### 3. Append-only SOURCES (S041)

Routed text (`round-16-verifier-spotcheck.md:184`): S041's anchor and teaches cells "were amended after the row's first commit in `b8e485c`."

- Contract rule, re-verified at `.ufo/waves/kaika/SOURCES-CONTRACT-v1.md:49-51`: "Only `status`, `recheck` and `used-by` change in place, and each change". Line 50–51: "A correction is a new row whose `teaches` opens `supersedes S0NN —`."
- Re-verified with `git show b8e485c:corpus/SOURCES.md` line 53 and `git show master:corpus/SOURCES.md` line 53: the anchor cell differs. The first-commit text cites receipt `13:49:38.040Z–13:49:38.170Z`, port 32845, "10 checks". The master text cites `14:06:27.859Z–14:06:27.974Z`, port 37527, and `tool sha256 b8c5e8d4…`. `git log -- corpus/SOURCES.md` shows `726f737` and `ccc4bb3` as the two later commits touching the file.
- The contract also says each in-place change is logged old→new in the round lesson. [L1 fills: whether the round-16 lesson §Gate logs the `726f737`/`ccc4bb3` S041 changes old→new; not re-read in this draft.]
- Options for L1: (a) record the disclosure in the round-17 lesson and leave S041 unchanged; (b) add a new row that opens `supersedes S041 —` for the 14:06:27Z receipt. Option (b) is the contract's only sanctioned correction route. Restoring the `b8e485c` text in place would itself be an anchor change, which rule 2 does not allow. The recommended option is (b) plus the disclosure.
- Hint for the sibling building the fail-capable checker (`tools/sources-append-only.py`, not present at master): the check must compare each row's `anchor` and `teaches` against its first-commit blob and allow only `status`, `recheck` and `used-by` to differ. Under that rule the current S041 fails. The checker needs a documented grandfather or the superseding row. [L1 decides which.]

### 4. Wording precision (every non-frontend path, OPTIONS)

Routed text (`round-16-verifier-spotcheck.md:185`): "Narrow "every non-frontend path" (corpus README §Round-16 row, S036 cell) to exclude OPTIONS".

- Source, re-opened 2026-10-20: `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp`.
  - Line 312: "no endpoints are allowed to be accessed when the server is not ready". Lines 314 `res.status = 503`, 318 `"Loading model"`, 319 `"unavailable_error"`, 320 `503`.
  - Line 346: "If this is OPTIONS request, skip validation because browsers don't include Authorization header". Lines 347–352 are the OPTIONS branch and its `return`. The state gate is called at line 354, after the OPTIONS branch, so OPTIONS bypasses it.
  - Lines 241–248 (frontend paths) and 309–311 (frontend exemption) match the lesson's citations.
- Lesson's routed item asks for a 319–320 citation alongside 318. Both are confirmed above.
- Scope found by this draft, wider than the routed item names: the phrase "every non-frontend path" appears in:
  - `corpus/SOURCES.md` S036 registry row (the routed "S036 cell"; the only occurrence in that row).
  - `corpus/README.md:206` (the §Round-16 row).
  - `corpus/knowledge/endpoint-identity.md:202` ("answers every non-frontend path with that 503 body while not ready"). This file is not named in routed item 4.
  - `corpus/SOURCES.md:135-136` already carries an OPTIONS note; the same file's S036 row does not.
- Disposition: appended corrections, not rewrites. [L1 decides whether `endpoint-identity.md:202` is in the round-17 correction set.]

### 5. Install disclosure precision

Routed text (`round-16-verifier-spotcheck.md:186`): "name the retained tarball `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` under L0 question (b)."

- Re-verified on the host, 2026-10-20: `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` exists (22,240,468 bytes, mtime 2026-10-20 10:17). Its `sha256sum` begins `753bfa7327a75b477d4d`, matching the upstream asset digest the round-16 lesson records (`sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`, lesson line 111).
- Re-verified: `test -e /usr/bin/llama-server` is false. `readlink -f ~/.local/bin/llama-server` → `/home/vgpnk/.local/opt/llama-b11755/llama-server`. The PATH link shadows nothing.
- Disposition: text for the L0 follow-up. The install is operator-owned and is not changed by this draft. No tool was installed or removed by this seat.

### 6. Carried debt

Routed text (`round-16-verifier-spotcheck.md:187`): "Five `check.py` harness mutants survive."

- Not re-measured by this draft. The counting command belongs to L1 (`.ufo/waves/round-17/c1/mutants.py`). [L1 fills: surviving-mutant count after the C1 repair.]
- Carried items from the same routed defect: live checks `health_ready`, `teardown_*` and `loading_envelope_exact` (C2 scope); the harness `finally` leak (C2 scope); M3 (harness hang design, still open); M7 (session-store traversal recurrence, still open). For M7, the exclusions must be stated verbatim in each wave context. This draft does not restate any session content.
- Open L0 question, operator-owned, unassessed here: `kama | round-16 | Ratify or reject the lane-owned live llama.cpp fixture …` (round-16 lesson line 189).

## Routed jj-migration risks

Sources:
- `.ufo/waves/hyaku/jj-w1/reports/JjAuditKama.md` §3 R1–R3 (lines 152–158) and §6 recommendations 1–6 (lines 176–183), with §5 [INFERENCE] at line 174. The audit was pinned at `726f737`.
- `.ufo/waves/hyaku/jj-w1/reports/JjTrialKama.md` §Recommendations 1–4 (lines 110–115), with §Step 4 at lines 67–72.
- Helper `scripts/hyaku/jj-lane.sh` read at its current lines. Not executed. The lane is not touched by `jj`; all checks below are `git show`, `git grep`, `grep` or `nl` reads.

| Risk | State at master `cff9e62` | Draft disposition |
|---|---|---|
| R1 round-13 gate reads HEAD and reports exit 1 `documentation_mismatch` | Open; gate unchanged | Procedural ordering rule; code fix not in scope |
| R2 unborn HEAD aborts two gates | Open; both sites present | Bootstrap-only; no action after first commit |
| R3 `jj commit` on untracked paths exits 0 with an empty commit | Mitigated in the helper; post-commit check absent | Decision for L1 |
| §6.6 `round-16/measure.py:116` lacks replace-objects guard | Open | Parity fix |
| Trial rec 2 `.gitignore` for `.ufo/state/` and `registry/history/.lock` | Partly open; the `.lock` claim is refuted | Correct the claim; commit or drop the worktree edit |
| Trial rec 3 colocated-lane doc rule | Open | Decision for L1 |

### R1 — round-13 gate ordering

- Re-verified: `.ufo/waves/round-13/measure.py:385` `head_quality = git_read(['cat-file', 'blob', f'{head}:{QUALITY_GIT_PATH}'], commands)` and `:397` `worktree_matches_head = final == head_quality`.
- Audit text (`JjAuditKama.md:154`): "Mitigation is ordering: helper `commit` before the gate." The audit's stricter fix (separate divergence as its own finding) is code, and was not made.
- Disposition: add to the round procedure that the helper `commit` runs before any round-13 live gate. [L1 decides where the procedure lives.]

### R2 — unborn HEAD

- Re-verified: `.ufo/waves/round-12/fidelity.py:449` `head, head_error = git_run(source_repo, 'rev-parse', 'HEAD')`; `.ufo/waves/round-13/measure.py:295` `oid = git_read(['rev-parse', 'HEAD'], commands)`.
- Audit text (`JjAuditKama.md:156`): "Only the pre-first-commit window matters". The window closes at the first helper commit. Disposition: no action beyond the note.

### R3 — silent empty commit

- Re-verified in the helper: `jj-lane.sh:199` `nothing to commit (no such paths)` with exit 0; `:209-214` `jj file track` for files and directories; `:218-219` a pre-commit check, `jj diff --summary -- "${existing[@]}"`, that prints `nothing to commit` when the diff is empty. The helper's own text at `:230` runs `commit -m "$msg" -- "${existing[@]}"`; `:231` reads `hash=@-`; `:233` runs `bookmark set`.
- Not present: a post-commit check that the new commit is non-empty. The audit's recommendation 5 (`JjAuditKama.md:182`) is still open. The audit's original R3 wording: "creates an empty commit, and **exits 0**".
- Disposition: decision for L1 whether to add the post-commit non-empty check. Helper-routed commits are protected by the pre-commit check; hand-run `jj commit` is not.

### §6 recommendations (audit lines 178–183)

- 1 (leave git reads): no action. The audit's class-D count (15) is audit-reported; `round-16/measure.py:116` is one of them.
- 2 (gate ordering): see R1.
- 3 (use `refs/heads/master`, not `HEAD`, `@{u}`, `--abbrev-ref`, `--show-current`): helper `jj-lane.sh:59` `show-ref -q --verify refs/heads/master` and `:71` `rev-parse --verify -q "refs/heads/$branch"` match the audit's description. Open as a convention; no lint enforces it.
- 4 (no `.gitattributes`, no hooks): re-verified `git ls-files | grep -c gitattributes` = 0 at master. Policy, not a gate.
- 5 (`jj file track` and a post-commit check): pre-commit half present (see R3); post-commit half absent.
- 6 (parity fix at `round-16/measure.py:116`): re-verified. Line 116 is `["git", "-C", str(LANE), "cat-file", "blob", spec]` and `grep -c no-replace-objects` on master returns 0. Open. This is a robustness fix, not a jj-compatibility fix, as the audit says.

### Trial recommendations (`JjTrialKama.md:110-115`)

- Rec 1 (keep helper `init` config: `snapshot.auto-track="none()"`, `trunk()=master@origin`, lane identity): not re-verified. This seat may not run `jj` in the lane; the config values are audit-reported from `JjTrialKama.md` Step 2.
- Rec 2 (`.gitignore`: `.ufo/state/` and `registry/history/.lock`):
  - Master `.gitignore` contains one line, `.ufo/interactive-sessions/` (`git show master:.gitignore`). `.ufo/state/` is therefore not committed-ignored.
  - The lane worktree `.gitignore` has an uncommitted second line, `.ufo/state/` (`git diff --stat -- .gitignore`: one insertion). That edit is not this seat's and was not committed or reverted. L1 must decide whether to commit it.
  - Refuted: `registry/history/.lock` is already ignored. `registry/history/.gitignore` contains the line `.lock` (and `*.json`). The audit's claim that `registry/history/.lock` is not gitignored is wrong at master.
  - Audit text (`JjTrialKama.md:113`): "both are runtime artifacts currently protected only by pathspec discipline". The `.lock` half of that sentence is wrong; the `.ufo/state/` half holds at master.
- Rec 3 (document "colocated — never `git add`/`git commit`…" in a lane doc): `git grep -c -i colocat master -- '*.md'` returns zero matches. Open. [L1 fills: which lane doc takes the rule.]
- Rec 4 (size override): not re-verified. The audit's largest commit-eligible file, 369 KB, is audit-reported.

### [INFERENCE] carried from the audit

- `JjAuditKama.md:174` [INFERENCE]: if the helper's bookmark move fails after `jj commit`, HEAD still advances and a gate could read an unpushed commit. Not exercised. Helper ordering at `:230-239` is consistent with the inference. The guard is the citation rule, not a gate.
