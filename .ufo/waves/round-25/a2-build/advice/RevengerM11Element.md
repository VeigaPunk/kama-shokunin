# RevengerM11Element: M11 element check at 1fc41e3

**Verdict: SAME ELEMENT.** At 1fc41e3, M11 still removes only the `errors="surrogateescape"` argument of the fleet report listing call (`tools/report-landing-audit.py:681-683`). The re-anchored literal removes that argument, its separating comma and its line break, and nothing else. The original and the mutated auditor both compile. One behavioural check agrees: on grid row F20 the pristine auditor passes and the M11 mutant fails.

Scope: M11 and the listing call only. No llama-server was started and no port was used. Git-writing work ran only in my clone. The lane was not written, except for this report and the out folder.

## 1. Inputs and pins

- Clone: `/fast/scratch/hyaku/kama-r25a2/RevengerM11Element/clone`, detached at `1fc41e346853afd98cbd7010af5db4e54dc877f7`. Git 2.56.0.
- `git show 1fc41e3:tools/report-landing-audit.py | cmp - <clone copy>`: exit 0 (`git-history.log`).
- `git diff --stat 92063cf 1fc41e3 -- tools/report-landing-audit.py`: no output, exit 0. The auditor has not changed since 92063cf (round-24 commit, 2026-10-21 21:50:32 -0300). Commit 1fc41e3 (2026-10-22 06:28:44 -0300) changed only `tests/report-audit/isolation-mutants.py`: 30 insertions, 3 deletions.
- Line numbers below refer to the auditor at 1fc41e3 unless marked otherwise. The lane file is byte-identical to the clone file.
- The `lsp` device is not mounted here: `xd://lsp` returned "No such tool. Mounted devices: ast_edit, debug". Call sites were therefore checked with Python's `ast` and `tokenize` modules on the pinned file. Plain text search was used only to find line numbers.
- Tools: no installs or upgrades. Python 3.14.8 was used as found.

## 2. When the listing call wrapped (git history)

The table comes from ten auditor snapshots (`git show <sha>:tools/report-landing-audit.py`), read by `m11_check.py`. "Round-23 literal" is the old M11 search text `"--", ".ufo/reports", errors="surrogateescape"`. "Re-anchored literal" is the text in the 1fc41e3 registry.

| Commit | Listing form (file lines) | Round-23 literal count | Re-anchored literal count |
|---|---|---|---|
| a29bb84 | no `".ufo/reports"` literal | 0 | 0 |
| 1471344 | working-tree glob, not git (275-278) | 0 | 0 |
| 7054dba | `git ls-tree`, two lines (293-294) | 0 | 0 |
| 6c9f58c | two lines (386-387) | 0 | 0 |
| 80a6d07 | two lines (381-382) | 0 | 0 |
| e0f0434 | two lines (420-421); `errors="surrogateescape"` added to line 2 | 1 | 0 |
| 34b2376 | two lines (417-418) | 1 | 0 |
| e876b95 | two lines (429-430) | 1 | 0 |
| ed1cc3a | two lines (607-608) | 1 | 0 |
| **92063cf** | **three lines (681-683), inside a new `try:` with `except EvalError`** | **0** | **1** |
| 1fc41e3 | same bytes as 92063cf | 0 | 1 |

Answer: the call first became a git listing in 7054dba, already split over two lines. It was re-wrapped to three lines, and moved inside a new try/except, in **92063cf** (`round-24: correct local object scope and measurement provenance`). That is the commit that stopped the round-23 search text from matching. `git blame -L 680,684 1fc41e3` attributes lines 680-683 to 92063cf.

The round-24 diff of the listing region is in `ed1cc3a-to-92063cf-auditor.diff`, hunk at lines 332-357. It shows the new `try:` and the `"HEAD",` token moving to the second line.

## 3. The re-anchored M11 literal

- Registry, `tests/report-audit/isolation-mutants.py:65-67`:
  ```
  ("M11-listing-surrogates",
   '"--", ".ufo/reports",\n                             errors="surrogateescape"',
   '"--", ".ufo/reports"'),
  ```
- The literal's indentation is 29 spaces. Auditor lines 681, 682 and 683 have 16, 29 and 29 leading spaces, so the literal matches the wrapped call.
- Occurrences of the re-anchored literal in the 1fc41e3 auditor: 1 (`anchor_now_count_in_1fc41e3`).
- The registered counting command (`preregistration.json`, C1), run in the clone: `registered 28 stale 0 []`, exit 0 (`c1-counting-command.log`).

## 4. Unified diff, original versus mutated (M11 applied)

File: `M11-original-vs-mutated.diff`. `diff -u` exit 1, which means the files differ, as expected. Line count 1639 becomes 1638.

```
--- a/tools/report-landing-audit.py
+++ b/tools/report-landing-audit.py
@@ -679,8 +679,7 @@
             # committed fleet reports only, never working-tree drafts
             try:
                 listed = git(fleet_repo, "ls-tree", "-r", "--name-only",
-                             "HEAD", "--", ".ufo/reports",
-                             errors="surrogateescape")
+                             "HEAD", "--", ".ufo/reports")
             except EvalError as exc:
                 # the listing is evidence the audit needs
                 tree = root_tree(fleet_repo, "HEAD", exc)
```

What exactly changed:

- **Token level.** The tokens removed are `,` then `errors` `=` `"surrogateescape"`. The comma is the separator before the keyword, and it has to go or the call would not parse. Every other token keeps its order (`token_stream_equals_original_minus_removed: true`).
- **Syntax-tree level.** Dropping the `errors` keyword from the listing call gives exactly the mutated syntax tree (`ast_equal_after_dropping_listing_errors_kw: true`). The number of `errors=` keywords goes from 3 to 2. The two that remain are untouched: `proc.stderr.decode(errors='replace')` (line 181) and the lane log call with `surrogateescape` (line 355, the M10 element).

## 5. Compile result

- `python3 -m py_compile` on the original file: exit 0.
- `python3 -m py_compile` on the mutated file: exit 0.
- `compile()` inside `m11_check.py`: "OK" for both.

## 6. Same-element verdict

The element is the surrogateescape decoding of the fleet report listing. The `git()` docstring (lines 157-160) says this is the designed use: "Callers that only match ASCII fields and never emit the text (lane log records, report path listing) pass surrogateescape."

Evidence, all from executed checks:

- The round-23 commit e0f0434 added the kwarg to this call and registered M11 for it. The grid row F20 was added in the same commit (`git log -S'F20-quotepath-open-range'` names only e0f0434). F20 expects exit 0 with no kinds, both at e0f0434 and at 1fc41e3.
- The listing call's syntax tree is identical from e0f0434 to 1fc41e3 (short hash `bc7a92aa2d7b` in every snapshot), and in every snapshot the enclosing function is `parse_rounds`. The wrap and the new try changed layout and error handling, not arguments.
- Behaviour, one grid run each in the clone (`repo-state-grid.py --arm current --current <auditor> --json`, `grid-pristine.json` and `grid-M11.json` in scratch; summary in `m11-grid-check.log`):
  - Pristine 1fc41e3: grid exit 0, 46 rows, no failed rows. F20: exit 0, `met: true`.
  - M11 mutant: grid exit 1, failed rows `['F20-quotepath-open-range']`. F20: auditor exit 2, `met: false`, stderr tail `...output is not UTF-8: 'utf-8' codec can't decode byte 0xe9 in position 16: invalid continuation byte`.
  - F20 fixture (`repo-state-grid.py:434-444`): a committed path `.ufo/reports/caf\xe9.md` with raw Latin-1 bytes, and `core.quotePath=false` so that `ls-tree` prints them unquoted. The row is at line 670.

So M11 weakens the same element as at round 23, and F20 is the fixture that shows it.

## 7. Divergences and observations

1. **The round-24 commit changed the error path as well as the layout.** Since 92063cf, the listing call sits inside `try:` with `except EvalError as exc:`, which calls `root_tree` and then `required_read` (lines 680-690). M11 does not touch that handler. With M11 applied, the strict decode error (`git()`, lines 182-187) reaches the new handler. `required_read` (lines 343-347) turns it into an `EvalError`, and `main()` returns 2 (lines 1620-1622). Before 92063cf the same error had no local handler and also reached `main()`. The exit code is the same either way. [INFERENCE from source: the round-23 path was not run.]
2. **The M11 search text depends on layout.** It contains a newline and 29 spaces. Any further re-wrap of this call breaks it again, which is what 92063cf did. The counting command catches this as "stale", but the repair is another re-anchor, not a fix. [INFERENCE about future edits; the failure itself is observed.]
3. **The kill mechanism is a refusal.** On F20 the mutant makes the auditor exit 2, which the grid scores as a failed fault row, so the grid exits 1. The kill comes from the auditor refusing the input, not from a wrong verdict. Mutation seats reading M11's kill should keep that in mind.
4. **Attempt-1 claim.** `build/ATTEMPT-1-DISPOSITION.md` says an earlier M11 re-anchor was killed by F20. The single-row check above is consistent with that at 1fc41e3. I reused no attempt-1 output.
5. **First run of my check returned DIVERGES, and I fixed my check, not the auditor.** The first run compared the keyword against the text `errors=surrogateescape`, but `ast.unparse` renders the constant with single quotes (`'surrogateescape'`). The check now compares the constant value. The second run gives SAME ELEMENT. The auditor and the mutant were not touched.

## 8. Not run, not claimed

- The full 28-mutant run and the other 27 mutants were not run. Other seats own those.
- The round-23 grid was not run. The round-23 kill is an inference from the identical syntax tree, the identical kwarg, and the unchanged F20 row.
- No llama-server was started. No port was used.
- In the lane, only read-only git was used, through the clone. No jj command was run.

## 9. Confidence

- Diff, token and syntax-tree results, and the compile result: high (executed, exit codes recorded).
- Wrap commit (92063cf) and the snapshot table: high (git log, blame, snapshots).
- Same element: high (identical call syntax tree and kwarg history; F20 behaviour observed at 1fc41e3). Round-23 behaviour: inference.
- Registered count 28 and stale 0: executed.

## 10. Files I wrote

Lane, under `.ufo/waves/round-25/a2-build/`:
- `out/RevengerM11Element/m11_check.py`: check script (parses only; writes the mutant copy to scratch).
- `out/RevengerM11Element/M11-check-result.json`: check results (verdict SAME ELEMENT).
- `out/RevengerM11Element/m11-check-run.log`: stdout of the final check run.
- `out/RevengerM11Element/M11-original-vs-mutated.diff`: the unified diff in section 4.
- `out/RevengerM11Element/compile-and-diff.log`: diff output, py_compile exit codes, line counts.
- `out/RevengerM11Element/git-history.log`: cmp, diff-stat, commit metadata, blame, commit list.
- `out/RevengerM11Element/c1-counting-command.log`: registered 28 stale 0.
- `out/RevengerM11Element/ed1cc3a-to-92063cf-auditor.diff`: round-24 auditor diff (copy of the scratch file).
- `out/RevengerM11Element/m11-grid-check.log`: pristine and M11 grid summary, F20 rows.
- `out/RevengerM11Element/mutant-checksums.sha256`: SHA-256 of the original and mutated auditor copies.
- `advice/RevengerM11Element.md`: this report.

Scratch, `/fast/scratch/hyaku/kama-r25a2/RevengerM11Element/`:
- `clone/`: clone at 1fc41e3, detached. Nothing in it was edited.
- `hist/audit-<sha>.py` (10 auditor snapshots) and `mut-hist/mutants-<sha>.py` (6 mutant-file snapshots), made with `git show`.
- `mut/report-landing-audit.1fc41e3.py` and `mut/report-landing-audit.M11.py`, plus `mut/__pycache__/` from py_compile.
- `diff-ed1cc3a-92063cf.diff`, `grid-pristine.json`, `grid-pristine.err`, `grid-M11.json`, `grid-M11.err`.
