VERDICT: partial - documented commands, exit maps for most cases, selftest counts and the decision row match a6617149; the grid exit-1 map and the audit read-scope claim are wrong, and the errata notation, grid write scope and "13 link mutations" are imprecise.

Attacked: round-21 section of kama-shokunin/SKILL.md at a6617149, lines 674-696 (header 674-679, instrument rows 683-685, checklist 687-691, decision row 693-696). SKILL.md is byte-identical in the lane working tree.
Method: scratch clone of a6617149 at /tmp/kama-r21-SkillRowsAccuracy/lane; all commands run with /usr/bin/python3; fleet passed via --fleet-repo because the tool's default fleet is the parent of the clone. 49 recorded runs (argv, exit, stdout, stderr) plus two in-process producer calls: falsify/out/SkillRowsAccuracy/probe-results.json. Lane not modified; no servers; ~/.local/opt/llama-b11755 read only (grid mirrors it). Fleet HEAD at run: 5d4a2eec.

## Inaccuracies (severity order)

1. Grid exit-1 map, row 685 (medium). Row: "1 an arm missed (the frozen round-start arm always does)". Observed: install-links-grid.py --tree <copy with libggml.so.0 -> libggml.so.9> --arm current --json -> exit 1; summary.current = {status "pass", wrong [], real_tree_gate_clean false}. No arm missed. Code: install-links-grid.py:249-253 (ok = ok and clean); :254-258 (--arm both: ok = ok and back-compat install_tree equality). Docstring lines 26-30 omit both causes. [INFERENCE, code-read, not exercised] a null cell flagged as changed also yields 1 (:241-242).

2. Audit read scope, row 683 (medium). Row: "stdout only; reads lane and fleet git objects". Observed: in a scratch clone of the fleet I appended token 0123456789abcdef0123456789abcdef01234567 to round-20/kama.md (working tree only). report-landing-audit.py --lane-repo <lane> --fleet-repo <scratch> --rounds 20 --no-errata -> exit 1, "UNCORRECTED unresolved-full-hash 0123...". Code: :168-169 reads the report from the fleet working-tree file; git supplies only the cutoff (:170) and token lookup. The uncommitted lane file already switches to git show HEAD:<rel> (see Working tree); the row is true only after that lands.

3. Errata notation, row 683 and docstring line 5 (low). Row: "[--errata PATH | --no-errata]". Observed: --rounds 10-20 --errata registry/report-landing-errata.tsv --no-errata -> exit 1 with nine raw defects; the ledger is silently ignored; no usage error. Code: :538-539 (no exclusive group); :226-227 (--no-errata returns [] first).

4. Write scope, row 685 (low). Row: "stdout; temporary mirror removed". Observed: with the pycache removed first, install-links-grid.py --selftest (exit 0) leaves tests/llamacpp-live/__pycache__/check-receipt.cpython-314.pyc; check-receipt.py --selftest (exit 0) leaves nothing. Cause: install-links-grid.py:88-92 loads the gate via spec.loader.exec_module. Gitignored (.gitignore:3), so no tracked change.

5. Count, row 684 (low). "13 link mutations": check-receipt.py has 11 mut("links-...") calls (:1992-2013). Named INVALID link cases total 14: those 11, links-absent-required (:1871), links-absent-with-pin (:1873) and links-retarget-pinned (:1990). The stated 13 holds only if the retarget pair is excluded. The selftest output itself (11 VALID, 1 NOT-EVALUATED, 91 mutations) is accurate.

## Verified (exit observed)
- Header: gate --selftest exit 0, "11 VALID and 1 NOT-EVALUATED receipts accepted; 91 mutations + unreadable case rejected". Round-start 7a6bc911 gate --selftest exit 0, "6 VALID and 1 NOT-EVALUATED ...; 77 mutations", so "(was 6 + 1 / 77 ...)" holds.
- Row 683 selftest exit 0, "selftest cases=32 failed=0"; case names cover splice, omissions, rebase/author-time cutoff, hex words, ledger matching/invalid corrections, exit-2 inputs and inherited GIT_DIR.
- Row 684 selftest: retarget VALID-unpinned and INVALID-pinned, legacy-absent VALID, canonical literal present; all inside the 11/1/91 run.
- Row 685 selftest exit 0, "selftest cases=13 failed=0", including symlinked-path tree, frozen misses link/subdir, dangling, missing-soname and unpinnable errors.
- Audit exits: 0 = --rounds 10-20 text/json, open range (11 reports), checklist draft (status=clean, round=21 required=5). 1 = --no-errata, checklist missing-last-commit, no-section, invalid correction. 2 = round 21 without report, --rounds 99-, 5-3, errata missing/malformed, draft missing/empty/directory, lane repo missing, closed stdout pipe ("could-not-evaluate: output: [Errno 32] Broken pipe").
- Gate exits: 0 = live six pins plus links pin, links pin only, no link args, r18 legacy plain. 1 = wrong links pin, r18 with --require-install-links, r18 with links pin, top-level list/scalar, server=5. 2 = missing file, not JSON, invalid UTF-8. Exit 3 is covered only by the selftest's own subprocess assertion (:2106, :2277-2280); I did not build a standalone NOT-EVALUATED receipt.
- Grid exits: 0 = --arm current (13/13 link, 1/1 subdir, 3/3 regular, 1/1 type, 0/1 null, real_tree_gate_clean true). 1 = --arm frozen (14 wrong cells), --arm both. 2 = missing tree, missing soname (libmtmd.so.0 removed), unpinnable tree (glibc-hwcaps dir).
- Checklist: --rounds 10-20 --report 21=<draft> exit 0; draft built from the documented git log --reverse --format='%H %s' 7a6bc911..master (5 commits); summary line present.
- Decision row (in-process on copies): soname retarget gives install_tree sha unchanged, install_links sha changed, no problems. glibc-hwcaps copy gives install_tree sha unchanged, links sha unchanged, problems ["glibc-hwcaps:not-regular-or-symlink"]; refusal at kama-llamacpp-live.py:1376-1379 is "install-tree-unpinnable:...".
- NEEDED_SONAMES: readelf -d on libllama-server-impl.so lists exactly the five names; llama-server lists only that library.
- S066 and S067 exist (corpus/SOURCES.md:78-79).
- Refuted hypotheses: a non-UTF-8 commit subject does not crash the audit (decoded; round 20 post_report=1; exit 1 comes from pre-existing defects); a closed pipe exits 2, not 120; non-object receipts exit 1 with reasons, no traceback.
- Two of my own expected exits missed (items 3 and the non-UTF-8 probe); the observed results are recorded above.

## Working tree (uncommitted, not a6617149; for the L1)
- check-receipt.py (mtime 08:21): adds case links-unicode-canonical-valid. Scratch copy: --selftest exit 0, "12 VALID and 1 NOT-EVALUATED ...; 92 mutations", so the header's 11/91 goes stale on commit.
- report-landing-audit.py: reads HEAD:rel (fixes item 2) and adds cases. Scratch copy: --selftest exit 0, 36 cases, all ok.
- kama-llamacpp-live.py: one added selftest assertion (key-sorted digest); not run, since its selftest starts stub servers.
- SKILL.md, install-links-grid.py and the errata ledger: identical to a6617149.

## Limits and provenance
- No tool installs or updates needed (readelf, python3 3.14.8, git already present); nothing recorded as installed.
- Scratch /tmp/kama-r21-SkillRowsAccuracy removed after writing this report.
