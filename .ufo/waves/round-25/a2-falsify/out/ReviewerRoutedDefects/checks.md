# ReviewerRoutedDefects: evidence log (round 25, attempt 2, wave 2)

Seat: KamaR25a2.ReviewerRoutedDefects. Item: the five routed defects of round 24.

Pinned committed bytes: lane master tip fa3b62ae6475d111eb466d79af616aeebb08bbb9.
Base: 147f5bdd3228ab712520b5f377346cb2d9a64769. Lane master is now
46be41cf674301953837c8863cd2026e8a21fcb0, which adds only
.ufo/waves/round-25/a2-falsify/{advice/swarm-registry.json, dispatch.json, spec.json, report-draft.md}.
No audited path changed in that commit.

Method notes:
- Code checks ran in my own clone, /fast/scratch/hyaku/kama-r25a2w2/ReviewerRoutedDefects/clone,
  detached at fa3b62ae, with PYTHONDONTWRITEBYTECODE=1.
- Lane reads were read-only: git show, log, ls-tree, cat-file, diff between two commits, and file reads.
- The lsp device is not mounted: `xd://lsp` returned "No such tool: xd://lsp. Mounted devices: ast_edit, debug."
  Caller and definition checks used text search plus direct reading of the auditor code.
- No llama-server was started. Read-only host checks: `pgrep -a llama-server` exit 1 (no process);
  `ss -ltn` filtered to 8080, 34113 and 47400-47419 showed no listener.
- Tool installs: none. Host git observed: git version 2.56.0.

## Checks

C1. `git rev-parse --verify` and `git merge-base --is-ancestor fa3b62ae… master` (exit 0):
    fa3b62ae is an ancestor of master 46be41cf.

C2. `git diff --no-ext-diff --name-status 147f5bdd… fa3b62ae…` (exit 0).
    Existing files changed: LOG.md, SCORECARD.md, SKILL.md, corpus/QUALITY.md, corpus/README.md,
    corpus/SOURCES.md, corpus/knowledge/gguf-declared-identity.md, tests/report-audit/isolation-mutants.py.
    New files: corpus/knowledge/context-capacity.md, corpus/lessons/round-25.md, tools/kama-context-capacity.py,
    and the round-25 wave tree. No path under .ufo/waves/round-24/, .ufo/reports/round-24/ or
    corpus/lessons/round-24*.md changed.

C3. `git diff -U0 147f5bdd… fa3b62ae… -- LOG.md` (exit 0): one hunk, `@@ -1633,0 +1634,45 @@`.
    Base lines 1495-1510 equal tip lines 1495-1510. The historical lines 1501-1502
    ("PM08 remains static-only") keep their bytes.

C4. `git diff -U2 147f5bdd… fa3b62ae… -- SKILL.md` (exit 0): hunks at 187-190 (16384 example),
    665-668 (S060 pointer), 673-688 (new Round-25 decision rows), 885-888 (promisor row PM08 wording;
    isolation row 28 literals), 990-993 (PM08 cutover paragraph), 1003-1006 (count 27 at round 24, 28 with M33).

C5. `git diff -U3 147f5bdd… fa3b62ae… -- tests/report-audit/isolation-mutants.py` (exit 0):
    docstring block "Round 25 re-anchor" at lines 27-40; M11 literal at 72-74 (spans the wrapped call);
    M17 literal at 88-93 (the lookup() if-block, raise replaced by pass); M33 added at 124-130;
    RETIRED list at line 140 unchanged (M14, M22, M27, M29).

C6. `git diff --stat 1fc41e34… fa3b62ae… -- tests/report-audit/isolation-mutants.py tools/report-landing-audit.py`
    (exit 0): only isolation-mutants.py changed, 7 insertions, all in the docstring (hunk `@@ -32,0 +33,7 @@`).
    tools/report-landing-audit.py is unchanged from base, so the measured auditor is the same bytes.

C7. C1 command from preregistration.json C1.command, run in clone at fa3b62ae (exit 0):
    `registered 28 stale 0 []`.

C8. Same command at efe58e96, from `git archive` into scratch (exit 0):
    `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`. Reproduces the lane's before-state.

C9. Literal counts in the tip auditor, from the same command (exit 0):
    M11 count=1, M17 count=1, M33 count=1.

C10. Anchor locations in tools/report-landing-audit.py at fa3b62ae (`git show | sed -n`, exit 0):
    - Lines 680-684: `listed = git(fleet_repo, "ls-tree", "-r", "--name-only", "HEAD", "--", ".ufo/reports",
      errors="surrogateescape")`. This is the M11 element (fleet report listing, surrogateescape).
      Lines 682-683 contain the M11 literal.
    - Lines 273-278, inside lookup(): `if not peel and not parts[0].startswith(token):` at 275,
      raise at 277. This is the M17 element.
    - Lines 210-215, inside bare_objects(): `if not parts[0].startswith(token):` at 212, raise at 214.
      This is the M33 element (no `not peel` guard).

C11. Id audit (exit 0). Tip ids: M01-M07, M09-M13, M15-M21, M23-M26, M28, M30-M33 (28 ids).
    RETIRED: M14, M22, M27, M29 (4). Base: the same ids without M33 (27). No id reused.
    M08 is absent at base and tip. The first version of the file (commit e0f0434, round 23)
    already lacks M08 (ids M01-M07 and M09-M23 there). `git grep` for M08 at fa3b62ae in SKILL.md, LOG.md,
    SCORECARD.md, corpus, tests and tools finds only PM08 matches.

C12. C1 full run. The committed file is at fa3b62ae (`.ufo/waves/round-25/final/c1/c1-tip-mutants.json`, parsed in scratch);
    the lesson records the run itself at 1fc41e34 (instrument unchanged since except its docstring, C6).
    `c1-tip-mutants.exit` content: exit=0. Killed 26; mutants 28; pristine passed;
    surviving ['M17-ref-shadow', 'M20-log-sha-shape']. M11 killed by F20-quotepath-open-range.
    M33 killed by F13-ref-named-abbreviation. M17 grid_exit 0, not killed.

C13. `python3 tests/report-audit/promisor-mutants.py --anchors tools/report-landing-audit.py --json` at tip
    (exit 0). Ten executable promisor mutants each have at least one applicable match and compile.
    PM08 is review-only and skipped. No stale executable promisor anchor. See promisor-anchors-tip.md.

C14. PM08 text at fa3b62ae. SKILL.md:887: "PM08 is a manual review-only note, unexecuted, uncredited,
    with no assertion of any kind (wording corrected in round 25)". SKILL.md:992-993: "PM08 rests on
    uncredited manual source inspection (not settled evidence; corrected in round 25)".
    A search for "static-only" or "settled" next to PM08 across SKILL.md, SCORECARD.md, LOG.md, README.md,
    corpus, tests and tools finds only historical lines: LOG.md:1501-1502;
    corpus/lessons/round-24-verifier-spotcheck.md:83-84; corpus/lessons/round-24.md:546-549 (quoting "not settled").

C15. Authority trail for the PM08 wording change.
    - preregistration.json line 14 (`repairs`) names only the M-series instrument.
    - preregistration.json line 26 (`not_claimed`) lists "PM08 execution credit" as not claimed.
    - A search for PM08 across preregistration.json, amendments 1-4, pilot.md, errata-attempt-2.json and
      count-c2.py finds no repair authorization.
    - SCORECARD.md:1270: "This repairs only the M-series portion of routed defect 2; PM08 remains outside the claim."
    - corpus/lessons/round-25.md:58-63 calls the PM08 wording a repair. LOG.md:1667-1668 says
      "PM08 wording in `SKILL.md` corrected". SKILL.md:887 says "(wording corrected in round 25)".
    - Report draft at 46be41c (.ufo/waves/round-25/report-draft.md, saved in scratch) line 40 lists it as a routed repair.

C16. Round-24 locator, `git ls-tree` at fa3b62ae (exit 0 each):
    - .ufo/waves/round-24/fixes/docs/ScribeLesson/ holds append-v1-labelled.txt, append-v2-labelled.txt,
      append-v2.txt, append-v3.txt, append.txt and supersession-index.json (six files).
    - .ufo/waves/round-24/falsify/out/ConnSources/verify.txt is blob size 7052.
    - .ufo/waves/round-24/sources/fixes/docs/ScribeLesson/ and .ufo/waves/round-24/build/out/ConnSources/
      return no entries (empty output).

C17. Round-24 root report.
    - `.ufo/reports/round-24/kama.md` is not in the lane tree at fa3b62ae. The tracked .ufo/reports holds only
      round-5/. `git log -- .ufo/reports/round-24/kama.md` is empty. The closure's commit 9eeecdcc… is not in
      the lane repo (`git cat-file -t` fails).
    - Fleet-root copy, read only: /home/vgpnk/Projects/shokunin/.ufo/reports/round-24/kama.md.
      mtime 2026-10-21 22:48. sha256 89b9f529d3ed323d9a2c9af0b3f3e2aeb324365971b19fa030cf6bb7dbd648ac.
    - Line 16, in part: "ScribeLesson's185-byte supersession headers were removed after preserving labelled copies,
      with creation-size/body but no prior original-SHA proof".
    - No recorded digest found. A grep of .ufo/waves/hyaku/parent-closures/kama24/ for the hash and for
      "round-24/kama.md" matched only closure-entry.json:38 (the path).

C18. Prepared-versus-landed lineage. .ufo/waves/round-25/build/out/ScribeLocatorErrata/evidence/03-prepared-vs-landed.txt,
    line 1: "lineage NOT resolved". The byte-containment table is mixed across the three prepared sets; in the v1 set,
    four of six files fail both containment tests against their landed files, while corpus/QUALITY.md and
    corpus/README.md pass both. corpus/lessons/round-25.md:72: "stays unresolved".

C19. Native-role wording. Case-insensitive grep for "native|alias|attest|answering|model.role|role binding"
    over the round-25 lesson, LOG.md:1634-1680, SCORECARD.md:1252-1296, SKILL.md:673-690,
    corpus/README.md:385-402, context-capacity.md, and the round-25 assignments and dispatch files:
    only corpus/lessons/round-25.md:73 (the disposition line). The round-24 text that carries the native-role
    limits is unchanged (C2).

C20. Original-clause wording. Grep for "47/47|amended47|unmet|original success|original clause|original-unmet|
    all cells|passes original" over round-25 new text: only corpus/lessons/round-25.md:56-57 (disposition item 1).
    No claim of original success.

C21. Overclaim wording. Grep for "no-effects|backend identity|continuous floor|continuous-floor|full isolation"
    over round-25 new text: only corpus/lessons/round-25.md:74, which negates them.

C22. H2 and promotion wording. Grep for "2.45|H2|floor|promotion|replay|next-round|endpoint" over round-25 new text:
    corpus/lessons/round-25.md:75-76 (H2 operator-owned); preregistration.json:26; SCORECARD.md:1291-1295
    (no promotion; "Outside closure alone decides admission" at SCORECARD.md:1294-1295); corpus/README.md:399-400 (fixture scope pending
    L0 ratification).

C23. C2 receipt (fa3b62ae:.ufo/waves/round-25/final/context-capacity-receipt.json, parsed in scratch).
    exit_code 0; 14 cells, 14 observed; ports 47400-47413, one per cell; port_closed true for all 14;
    child_returncode 0 for all 14; port_range [47400, 47419]; port_refusal_set [8080, 34113];
    summary.all_ports_closed true.

C24. C2 tool at fa3b62ae, tools/kama-context-capacity.py:
    DEFAULT_PORT_RANGE (47400, 47419) at line 60; HOST '127.0.0.1' at line 57; hard pins 8080 and 34113 required
    in the refused set at lines 760-764; start_new_session=True at line 310; teardown sends SIGTERM then SIGKILL to
    the process group and probes the port, lines 556-596. HTTP POST helper at line 129; POST to /tokenize at
    line 494; POST to /completion at line 520.

C25. corpus/README.md:399-400 (fa3b62ae): "The round-16 fixture scope is still pending L0 ratification; the L cells
    used POST `/completion`, beyond the GET-only round-16 admission." The lesson disposition (corpus/lessons/round-25.md:75-77)
    and the round-25 LOG entry (LOG.md:1634-1678) do not mention the POST scope.

C26. SCORECARD.md:1291-1293 (fa3b62ae), author trend readings: "expansion improved", "quality unchanged-to-improved",
    "discernment improved". Round-24 closure verdicts for comparison: quality harmed; discernment unchanged
    (corpus/lessons/round-24-verifier-spotcheck.md:144-145).

C27. SKILL.md:189-190 (fa3b62ae): "both slots share one 16384-cell pool". corpus/knowledge/context-capacity.md:178-185
    labels the basis as "another build, b1-d7bd3bf" and "historical, other-build evidence, not a kama observation".
    The SKILL line carries no such label.

C28. `git --version` on the host: "git version 2.56.0" (exit 0). The C1 full run uses --no-lazy-fetch, which SKILL.md:813-815
    says requires git >= 2.45. The host version is not an approval of the H2 floor.

C29. Report draft at 46be41c, saved to scratch as report-draft-46be41c.md: placeholders `LANE_TIP` (lines 6 and 68),
    `WAVE2_COMMITS` (line 61), `END_CENSUS` (line 77). Trend verdict lines 87-89 read "TBD".
