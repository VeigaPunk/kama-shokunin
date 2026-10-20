VERDICT: confirm — every S045 cell and the lesson Gate quote agree with the opened PIT pages and the pinned commit; two non-falsifying notes.

# ReopenS045 — round 17 FALSIFY, S045 cell-by-cell

Seat: `KamaR17.ReopenS045` (scout, leaf). Target: `corpus/SOURCES.md:57` and
`corpus/lessons/round-17.md:68`, at lane commit
`54a29268e2083caa2b1e0d54ee1e7d90961302f3` (lane tip checked; row bytes in the
clone are identical to the worktree: sha256 `5d2c3b2b…396dd` both sides).

## What I attacked

The row as landed (not the build draft, which carried the rejected Jia & Harman
survey):

> `| S045 | PIT Mutation Testing — Basic concepts — https://pitest.org/quickstart/basic_concepts/ | docs | A | PIT's own vocabulary for mutant outcomes (killed, survived, no coverage) and mutation score; not a claim about test adequacy in general | §Running the tests, and https://pitest.org/quickstart/commandline/ §`--mutationThreshold`; pitest-site gh-pages 614bec6fd16670852e94c8cc03a002f6bf05db09 | "Killed means a test caught the mutation successfully." A survived mutant was not detected; kama reports killed over applicable per mutant and detector, never a bare pass/fail total. | mined | 2026-10-20 | 180d | corpus/lessons/round-17.md |`

and the Gate row `corpus/lessons/round-17.md:68`:

> `| A killed mutant is one a test caught | admit, vocabulary only (S045) | https://pitest.org/quickstart/basic_concepts/ §Running the tests "Killed means a test caught the mutation successfully." |`

Both URLs re-opened 2026-10-20; commit pin re-resolved through the GitHub API.

## Cell-by-cell

| Cell | Verdict | Evidence |
|---|---|---|
| `id` | agree | `S045` unique in the registry: the contract's duplicate-id census (`CORPUS.md:143`) prints nothing. |
| `source` | agree | https://pitest.org/quickstart/basic_concepts/ resolves; page title "Basic concepts"; row title matches the site (`PIT Mutation Testing`) and the page. |
| `kind` | agree | `docs` is in the enum (`CORPUS.md:91-92`); the page is PIT's own quickstart documentation, not the rejected survey. |
| `tier` (for scope) | agree | `CORPUS.md:93-95`: "A: primary or authoritative for that scope (spec, official docs, source code, original paper…)". PIT's official site is authoritative for "PIT's own vocabulary"; the scope explicitly excludes test adequacy. Not the survey that `round-17.md:69` rejects as paper/B. |
| `scope` | agree | §Running the tests lists `Killed`, `Survived`, `No coverage`; the commandline page grounds the score: "the fraction of killed mutations out of all mutations" (9 words). The hedge "not a claim about test adequacy" is load-bearing and true — the page only defines PIT outcomes. See note 1 on the non-exhaustive parenthetical. |
| `anchor` | agree | §Running the tests present on the live page and in `quickstart/basic_concepts.markdown`; `### --mutationThreshold` present on the live commandline page; commit `614bec6fd16670852e94c8cc03a002f6bf05db09` exists and the branch API reports it as the current `gh-pages` tip; raw `basic_concepts.markdown` at that commit contains the quoted sentence. |
| `teaches` | agree | First quote verbatim on §Running the tests: "Killed means a test caught the mutation successfully." (8 words). Survived clause matches "Survived means the mutation was not detected by the covering test." (10 words). The kama clause is lane-grounded, not PIT-grounded: `.ufo/waves/round-17/c1/mutants.py:1005-1013` emits `applicable`/`killed`/`survived` per cell, and `.ufo/waves/round-17/runs/mutants-grid.json` totals are 1/8, 7/8, 1/10, 10/10 — killed over applicable, per mutant and detector. See note 2. |
| `status` | agree | `mined` requires a citing `used-by` path (`CORPUS.md:103-104`); satisfied below. |
| `opened` | agree | 2026-10-20 matches the Gate preamble "All sources opened 2026-10-20" (`round-17.md:56`) and this re-open. |
| `recheck` | agree | `180d` is an allowed cadence (`CORPUS.md:105-106`); appropriate for a stable docs page. |
| `used-by` | agree | `corpus/lessons/round-17.md` exists and cites S045 at line 68 ("admit, vocabulary only (S045)"). A corpus-wide grep finds no other citing path, so the single path is complete. |
| row shape | agree | `awk -F'\|' … NF!=13` prints `shape_violations=0`; enum/tier-inflation check prints nothing; no `S045` duplicate. |

## Lesson `## Gate` quote

Agree. `corpus/lessons/round-17.md:68` quotes
"Killed means a test caught the mutation successfully." — verbatim in the live
page and in the pinned raw markdown, 8 whitespace-delimited words (≤25),
located at §Running the tests, under the Gate preamble "All sources opened
2026-10-20. Quotes are verbatim and at most 25 words." (`round-17.md:56`). The
row carries the URL; the access date is in the section preamble, the shape the
other new rows use.

## Notes (not disagreements)

1. The scope parenthetical "(killed, survived, no coverage)" is illustrative,
   not exhaustive: the same page also lists `Non viable`, `Timed Out`,
   `Memory error`, `Run error`. Since the cell says "vocabulary for mutant
   outcomes" without "only", nothing false is claimed; keep it read as
   illustrative if cited later.
2. The `teaches` kama clause ("kama reports killed over applicable per mutant
   and detector, never a bare pass/fail total") is grounded in the lane's
   mutant tool and grid JSON, not in the PIT page. That division is already
   signalled by the Gate's "vocabulary only (S045)" label; do not cite the
   clause as a PIT assertion. [INFERENCE] that this is the intended reading of
   the cell.
3. The pin `614bec6…` is the `gh-pages` branch tip, while
   `quickstart/basic_concepts.markdown` itself last changed at `e8995cd`
   (2025-10-24, an ancestor of the pin; commit message "replace 'Lived' with
   'Survived'"). The quoted sentence is present at the pinned revision, so the
   repo-level pin resolves for both anchor targets; no correction needed.

## Commands run (cloned lane, exit codes)

```
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/ReopenS045-clone \
  && git -C /tmp/ReopenS045-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3   # exit 0
git -C /tmp/ReopenS045-clone rev-parse HEAD
  # 54a29268e2083caa2b1e0d54ee1e7d90961302f3
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print "shape_violations="n+0}' corpus/SOURCES.md
  # shape_violations=0                                                              # exit 0
awk … if (i=="S045") printf "S045 kind=%s tier=%s status=%s NF=%d\n" …
  # S045 kind=docs tier=A status=mined NF=13                                       # exit 0
awk … mined used-by existence loop
  # no missing-used-by lines                                                       # exit 0
awk … duplicate-id uniq -d
  # no output                                                                      # exit 0
awk … enum/tier-inflation check (CORPUS.md:145)
  # no output                                                                      # exit 0
python3 - <<'EOF'  # walk mutants-grid.json totals
  # [0] applicable 8 killed 1 survived 7; [1] 8/7/1; [2] 10/1/9; [3] 10/10/0     # exit 0
EOF
printf '%s\n' 'Killed means a test caught the mutation successfully.' | wc -w
  # 8                                                                              # exit 0
git show HEAD:corpus/SOURCES.md | sed -n '57p' | sha256sum
sed -n '57p' <worktree>/corpus/SOURCES.md | sha256sum
  # 5d2c3b2bfef116c8406d6913ec1431215267d288996fd9ac7babc240902396dd (both)       # exit 0
```

URL evidence (read tool, 2026-10-20): `https://pitest.org/quickstart/basic_concepts/`
(native HTML; §Running the tests); `https://pitest.org/quickstart/commandline/`
(native HTML; §--mutationThreshold); `https://raw.githubusercontent.com/hcoles/pitest-site/614bec6fd16670852e94c8cc03a002f6bf05db09/quickstart/basic_concepts.markdown`;
`https://api.github.com/repos/hcoles/pitest-site/branches/gh-pages` (tip =
614bec6); `https://api.github.com/repos/hcoles/pitest-site/commits?sha=gh-pages&path=quickstart/basic_concepts.markdown`
(last change e8995cd); `https://github.com/hcoles/pitest-site/commit/614bec6…`
(merge PR #139, 2 files, 2026-06-03).

## Limitations

- Read-only check: no lane file, gate or count was executed outside the clone;
  no `jj`/git write.
- The live page was read as rendered text, not byte-diffed against the pinned
  markdown; the quote and both section headings are present in both, which is
  the claim under test.
- The PIT quote is documentation of PIT's reporting vocabulary; it is not
  evidence about kama's test adequacy, and the row's scope says so.
- No `lsp` device is mounted in this seat; this is a prose/registry check, and
  the evidence above is direct text read, not semantic code proof.
- C1's 1/8, 7/8, 1/10, 10/10 counts were read from `mutants-grid.json` totals
  only to ground S045's `teaches` clause; their own falsification belongs to the
  C1 seats.

## Installs

None. No tool was installed or upgraded.

## Scratch

`/tmp/ReopenS045-clone` removed after the report was written.
