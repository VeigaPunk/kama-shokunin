# C1 counting-command attack — MutationAnchorSemantics (round 25, attempt 2)

Verdict: **no defective mutant found among the 28 registered mutants at the tip
1fc41e346853afd98cbd7010af5db4e54dc877f7**. Every registered literal occurs
exactly once, lands on the element its id claims, is not inside a
comment/string, differs from its replacement, and the mutated file both parses
and imports. The C1 stale-count criterion `src.count(old) != 1` is not fooled
by any of the four defect classes on the current source.

## What I ran

1. Counting command (verbatim from preregistration.json C1.command), in the
   clone checked out at the tip:

   ```
   python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
   ```
   Output: `registered 28 stale 0 []`, exit 0. Baseline confirmed.

2. Attack probe `probe-c1-mutants.py <lane-root>` (runs against the clone).
   For each of the 28 registered mutants it reports: `src.count(old)`
   (the command's own applies criterion), whether the mutated source parses
   (`ast.parse`), the changed line ranges (`difflib`), whether the whole
   matched span lies inside a STRING/COMMENT token (`tokenize`,
   merged spans), whether `new == old`, and the enclosing `def` of the
   occurrence. Output: `probe-results.json` (machine), `probe-table.txt`
   (human), `probe-summary.txt` (per-mutant table). Exit 0.

3. Import-level compile check `probe-c1-imports.py <lane-root>`: writes each
   mutated auditor and executes a full module import in a temp dir.
   Baseline pristine import OK; all 28 mutants import OK. Exit 0.

4. Hash evidence: pristine auditor sha256
   `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`
   (identical in the fleet worktree and the clone); each of the 28 mutated
   files has a distinct sha256 (listed in the report's table source
   `probe-results.json`), i.e. every replacement changes bytes.

## Per-mutant table (summary; full detail in probe-results.json)

All 28 rows: `count=1`, `applies=True`, `compiles=True` (ast.parse),
`import_ok=True`, `inert=False`, `identical=False`, exactly one occurrence.
Enclosing element and occurrence line:

| mutant | element | occurrence line | changed lines |
|---|---|---|---|
| M01-replace-objects | module (GIT_ISOLATION) | 138 | 138 |
| M02-lazy-fetch | module (GIT_ISOLATION) | 138 | 138 |
| M03-log-encoding | module (GIT_ISOLATION) | 139 | 139 |
| M04-log-follow | module (GIT_ISOLATION) | 140 | 140 |
| M05-log-showroot | module (GIT_ISOLATION) | 140 | 140 |
| M06-log-signature | module (GIT_ISOLATION) | 141 | 141 |
| M07-log-mailmap | module (GIT_ISOLATION) | 141 | 141 |
| M09-strict-default | git | 156 | 156 |
| M10-log-surrogates | round_commits | 355 | 355 |
| M11-listing-surrogates | parse_rounds | 682-683 | 682 |
| M12-shallow-check | check_history_repo | 710 | 710 |
| M13-grafts-check | check_history_repo | 714 | 714 |
| M15-object-format | check_history_repo | 706 | 706 |
| M16-top-level | check_history_repo | 708 | 708 |
| M17-ref-shadow | lookup (peel-guarded site) | 275-277 | 277 |
| M18-branch-heads | resolve_branch | 826 | 826 |
| M19-errata-hex | apply_errata | 628-629 | 628 |
| M20-log-sha-shape | round_commits | 367 | 367 |
| M21-newlines | git | 187 | 187 |
| M23-strict-decode-catch | git | 183 | 183 |
| M24-catch-all | main | 1629 | 1629 |
| M25-timestamp-shape | round_commits | 372 | 372 |
| M26-record-separators | round_commits | 358 | 358 |
| M28-correction-casefold | apply_errata | 626 | 626 |
| M30-fleet-history-check | run | 846 | 846 |
| M31-git-timeout | git | 164-165 | 164 |
| M32-grafts-content | grafts_effective | 817 | 817 |
| M33-ref-shadow-bare-objects | bare_objects (second site) | 212-214 | 214 |

## Defect-class results

- Literal inside a comment or string: none. Token-span coverage says the full
  matched span of every mutant includes executable code; none is fully inside
  a STRING/COMMENT token (e.g. M17/M33 span code plus one unchanged comment
  line; the changed line is the `raise`/`pass` swap).
- Replacement identical to original: none (`new == old` false for all 28).
- Mutated file that does not compile: none (all 28 parse and import).
- Literal that matches a different element: none. M17's literal lands only in
  `lookup()` (line 275, guarded by `not peel`), M33's only in
  `bare_objects()` (line 212, without the peel guard), matching the repair
  design (amendment 2 C1 repair_design). All other single occurrences land in
  the element their id names (table above).

## Notes / honesty

- The static checks do not prove behavioral kill on the grid
  (repo-state-grid.py); they bound the C1 counting command's blind spots. A
  full `isolation-mutants.py --json` run on the landed source is the
  supporting evidence handled elsewhere (ExecC1BaseRun seat) and was not run
  here.
- Wrinkle observed (not a defect): M05/M06/M07 replace a `, "-c", "flag"`
  pair with `""`; adjacent-string concatenation `"" "-c"` still leaves a
  parseable tuple with the flag pair dropped. The mutation is effective at
  the bytes/behavior level even though the injected text is not a clean
  argument list.
- No llama-server child was started. No production files outside the advice
  folder and the artifacts folder were written.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-c1-mutants.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-c1-imports.py`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-results.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-table.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-summary.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/MutationAnchorSemantics/probe-imports.txt`
- this advice report
