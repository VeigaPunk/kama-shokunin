# ReviewerC1Patch: review of C1 patch 1fc41e346853afd98cbd7010af5db4e54dc877f7

**Verdict:** No literal, whitespace, escape, id-order, or scope defect in the patch, and the counting claim reproduces (registered 28, stale 0). One material problem with what the patch says: the re-anchored M17 can no longer be killed, because no caller in this tree can make its guard fire, and the patch does not disclose that.

Scope: `git show 1fc41e34` (one file, `tests/report-audit/isolation-mutants.py`, +30/-3), checked against the auditor at the same tip, against round 23 (e876b95), and against the registry parent (5388b7cf). Evidence and exit codes are in `out/ReviewerC1Patch/evidence.md`; the raw outputs are named in "Files I wrote".

## Findings

### F1. Major: M17 survives at the tip because its guard has no reachable caller; the patch and docstring present it as live

Locations: `tests/report-audit/isolation-mutants.py:29-32` (docstring), `:78-80` (comment), `:81-87` (anchor). The element: `tools/report-landing-audit.py:275-277` (tip).

Observed:
1. Round 23 kills M17. Targeted grid run at e876b95 (`out/ReviewerC1Patch/r23-changed-mutants.json`, run exit 0): M17 grid exit 1, failed row F13-ref-named-abbreviation.
2. The tip does not. Targeted grid run at 1fc41e34 (`out/ReviewerC1Patch/changed-mutants.json`, run exit 0): M17 grid exit 0, no failed rows. M33 (the copy in bare_objects) grid exit 1, failed row F13.
3. Cause: at e876b95 the bare-name check called `lookup()` again with no peel (`git show e876b95:tools/report-landing-audit.py` lines 148-149), so F13's abbreviation reached the guard at lines 170-172. That recursion was removed in ed1cc3a (`git log -S`, exit 0). At the tip the bare check is `bare_objects()` (`tools/report-landing-audit.py:190-214`), and it runs only when `peel` is set (`:246`).
4. The `lookup()` guard (`:275-277`) fires only when `peel` is empty. The only no-peel production call is `:538`, which takes its tokens from `classify_full_hashes` (`:463-479`; regex `FULL` at `:90` matches exactly 40 lowercase hex). For a 40-hex name, git returns the token's own object even when a branch of that name exists. Probe on git 2.56.0: `git cat-file --batch-check` on the full name returned object A, while the branch with that name pointed at B. So `parts[0].startswith(token)` is always true on that path. The selftest no-peel calls (`:1170`, `:1173`, `:1174`) cannot reach the refusal either: they hit an ambiguous name, a full object id, or an absent id.
5. Direct probe (`out/ReviewerC1Patch/m17-reachability-probe.out`, lines 2-6): the guard does fire for a non-40-hex name passed with no peel ("names a ref"), and the M17 mutant changes that result. No production or selftest caller passes such a name.

Consequence: M17 is not a coverage gap that a new grid row could close with today's callers. It is a guard that no caller in this tree can make fire. The registry now carries a survivor that cannot be killed by any current caller, and the round-23 kill is lost. The C1 measure (stale 0) is still correct, and "keeps its round-23 element" is still literally true. But the docstring and comment read as live coverage, and amendment 2's repair design (`.ufo/waves/round-25/preregistration-amendment-2.json`, `C1.repair_design`) does not consider reachability.

Requested disclosure (for the L1 to apply; I did not edit the lane). In the C1 report, list M17 as a survivor with this cause, and do not count it as re-anchored kill coverage. Suggested replacement for the comment at `isolation-mutants.py:78-80`:

```
    # round 25: the message now occurs at two call sites. M17 keeps the
    # round-23 site, the peel-guarded check in lookup(). No caller in this
    # tree can make that check fire (the no-peel caller passes 40-hex names,
    # which git resolves to their own object), so M17 survives the grid; the
    # second site, added in round 24 to bare_objects(), is the new mutant M33.
```

Decision outside this patch: keep M17 registered as a survivor. Retiring it needs the proof in `preregistration.json` C1 `non_narrowing_rules` (the element is gone, with attribution to the mutant that now carries the check). The element is still in the source, so that proof does not exist. Whether the no-peel refusal should exist at all is an auditor design question and a production change. It is not for C1.

### F2. Minor, outside the patch: stale counts in SKILL.md

- `SKILL.md:871` says "27 retained literals,4 retired IDs". `SKILL.md:989` says "holds 27 retained literals". The registry now has 28 entries (M33 added).
- `SKILL.md:803` says "31 single-literal mutants". That was already stale before this patch (27 at base).
- The commit touches only the mutants file, so these rows are integration work for the L1.

### F3. Minor, pre-existing: the M08 gap is not documented in the registry

- The registry has no M08 entry and no RETIRED entry (`isolation-mutants.py:52-124` and `:133-154`). M08 is absent at every commit since e0f0434 (`out/ReviewerC1Patch/literal-id-checks.out` lines 53-59).
- The only written reason is round-23 advice: `.ufo/waves/round-23/falsify/advice/ConnQualityRules.md:96-97` ("M08 was never defined (numbering skips it from e0f0434)").
- Not introduced by 1fc41e34. Optional: one sentence beside the RETIRED note.

### F4. Info: label reuse across instruments

- "M33" also labels `M33-now-fallback-removed` in `.ufo/waves/round-21/falsify/out/C1SelftestReview/mutation-harness.py:151`. M11 and M17 labels appear in round-21 harnesses too (`:67`, `:89`). Those are different instruments. Inside `isolation-mutants.py`, the 28 ids are unique.

## Checked, no defect

1. **Literals.** All 28 anchors occur exactly once at 1fc41e34 (`literal-id-checks.out` lines 6-33). The M11 continuation is 29 spaces and matches tip lines 682-683. The M17 and M33 continuations are 16 spaces and match tip lines 213-214 and 276-277. Each mutated auditor parses (28 of 28), so no mutant can be "killed" by a syntax error.
2. **Escapes and whitespace.** Only `\n` escapes, inside single-quoted anchors. The 30 added lines have no tabs, no CR, no non-ASCII characters, and no trailing whitespace. `git show --check` is clean (exit 0).
3. **Id order and uniqueness.** 28 unique, sorted ids. M33 is appended after M32. No id is removed or renamed. RETIRED ids M14, M22, M27, and M29 are not reused. Only the M11 and M17 tuples changed.
4. **Comments.** The docstring at lines 27-32 and the comments at lines 63-64, 78-80, and 115-116 were checked against the tip, e876b95, and 92063cf. Sites, function names, and round attributions are correct, and the round-24 change from `{repo}` to `{store.path}` is recorded correctly. The only gap is the omission in F1.
5. **Scope.** One file; 30 insertions and 3 deletions; file mode unchanged. The auditor is byte-identical from base to tip and from parent to tip (`git diff --quiet`, exit 0).
6. **Counting claim.** Before: `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`, reproduced against the tip auditor. After: `registered 28 stale 0 []`, exit 0.
7. **M11 element.** `git show e876b95:tools/report-landing-audit.py` lines 429-430 and tip lines 681-683 are the same `git(fleet_repo, "ls-tree", ..., ".ufo/reports", errors="surrogateescape")` call in `parse_rounds`. Both are killed by F20 in the targeted runs. Same element.
8. **M17 element, textually.** Round-23 lines 170-172 and tip lines 275-277 have the same guard, comment, and raise. Only `{repo}` became `{store.path}`.
9. **Two sites.** The text "names a ref" appears only at tip lines 214 and 277. There is no third refusal site.
10. **M33.** Killed by F13 at the tip (grid exit 1).
11. **Non-narrowing rules.** No retirement, no id reuse, and the denominator is reported as measured (28).

## Verification gaps and residual risk

- Full registry run (all 28 ids, tip): see the section below.
- I ran the three changed ids and the pristine run at the tip, and the same two ids at round 23. The other 25 anchors are unchanged by the patch (their tuples and the auditor are identical), so the patch cannot change their results. I have not measured their kill results beyond the full run.
- No `lsp` device in this seat. `xd://lsp` returned "No such tool. Mounted devices: ast_edit, debug." Caller checks used grep over the pinned clone as the literal fallback, plus the git probe, the grid runs, and the direct probe. None of this is a language-server reference graph.
- Git 2.56.0 only. The full-hex behaviour was observed on 2.56.0. For older git it is [INFERENCE] and was not checked. The lane's Git >= 2.45 approval is operator-owned.
- Not run: the auditor's own `--selftest`, the round-24 promisor instruments, and any llama-server work (out of scope for this seat).

## Full registry run (all 28 ids, tip)

Command: `python3 tests/report-audit/isolation-mutants.py --json`, cwd the scratch clone at 1fc41e34. Output: `out/ReviewerC1Patch/full-mutants.json`, `full-mutants.stderr`.

FULL_RUN_RESULT_PENDING

## Files I wrote

- `.ufo/waves/round-25/a2-build/advice/ReviewerC1Patch.md` (this report)
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/evidence.md` (commands and exit codes)
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/changed-mutants.json`, `changed-mutants.stderr` (tip, three ids)
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/r23-changed-mutants.json`, `r23-changed-mutants.stderr` (round 23, two ids; copied from scratch)
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/full-mutants.json`, `full-mutants.stderr` (tip, all 28 ids)
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/literal-id-checks.py`, `literal-id-checks.out`
- `.ufo/waves/round-25/a2-build/out/ReviewerC1Patch/m17-reachability-probe.py`, `m17-reachability-probe.out`
- Scratch only, not in the lane: `/fast/scratch/hyaku/kama-r25a2/ReviewerC1Patch/` (the clone, an e876b95 worktree named `r23`, the `gitprobe` repo, and the JSON copies).
- Disclosure: two of my files were first written to the fleet root by a relative path. I then copied them byte-identical into the lane folder and removed them from the fleet root, together with the three directories that write had created. Details are in `evidence.md` section 9. `.ufo/waves/round-25/build/` in the fleet root is untouched.

## Installs and updates

None. Git (2.56.0) and Python (3.14.8) were used as found. Nothing was installed or upgraded.
