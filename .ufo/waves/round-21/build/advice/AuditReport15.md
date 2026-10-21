VERDICT: confirm - round-15 has 0 landing defects by hand; tool agrees (0 defects, required 3, post 0); 8 tool blind-spot classes reproduced, none triggered here.
# AuditReport15 - round-15 kama report, C1 hand re-derivation
Scope: kama round 15 only. Lane /home/vgpnk/Projects/shokunin/kama-shokunin (master a29bb84, read-only); fleet /home/vgpnk/Projects/shokunin. Git run via Python subprocess; argv and exits in out/AuditReport15/by-hand-transcript.txt.
## 1. By hand (not the tool)
- Lane master: 82 commits. kama-shokunin with subject `round-15:` or `checkpoint(r15)`: 3 (no checkpoint(r15) exists). Fleet add of kama.md: 402b93b58868976096a3c58e3ed8f32ea8dd8f0c, ct 1792485831, sole add; committed blob == worktree (sha256 a9afc095...). Split at cutoff: pre 3, post 0.

| commit | ct | side | cited in Landed (>=7-hex) |
|---|---|---|---|
| 70af36c2b15b46d3b4b3c15ef20459cff640dfaf | 1792484951 | pre | yes, L27 |
| 4b1b4ad1ba31660cc44c82d204dc85c1355e36d2 | 1792485331 | pre | yes, L28 |
| b8bdc56efc43fe6baad9415d0ca75b7b81ffa952 | 1792485659 | pre | yes, L29 |

- Omitted 0; post-report round-15 0; Landed tokens matching no commit 0. Non-kama near-miss 20e392ea (protocol-shokunin, `round-15 verifier spot-check`, post). All refs: 4 round-15 subjects, all on master.
- Push times (`git reflog show --date=unix refs/remotes/origin/master`): 1792484953, 1792485333, 1792485661 for the three; next push 1792486297. Supports "pushed lane HEAD b8bdc56" and "pushed before this report".
## 2. Hex tokens (`git cat-file -e` exits, lane / fleet)
| token | len | lane | fleet | object |
|---|---|---|---|---|
| b8bdc56..., 4b1b4ad..., 70af36c... | 40 | 0 commit | 1 | the three commits above |
| e545ed99aaa519196a2a7779b0a293b2ce4c765c | 40 | 0 commit | 1 | round-14 commit, body only ("original source revision") |
| 783004569af9072afdeb32c6eeacc462868eb76b | 40 | 0 blob | 1 | = `rev-parse e545ed99...:.ufo/waves/round-14/measure.py`; its sha256 = fda61e... as reported |
| fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d | 64 | 128 | 128 | SHA-256 digest, not an object (correctly ignored) |

Landed has exactly 3 hex tokens, all lane commits; body has no 7-39-hex tokens; no wrong hash. Content ([INFERENCE] from file lists): 70af36c 98 files incl. tests/ollama-corpus-guard; 4b1b4ad 49 files incl. guard-only-red, frozen; b8bdc56 12 files, receipts + LOG/SCORECARD/lesson only. `git diff --quiet 4b1b4ad b8bdc56 -- tests tools .ufo/waves/round-14 .ufo/waves/round-15/frozen corpus/knowledge` exit 0: no code after the measured revision. LOG.md at b8bdc56: `## round 15` at line 854, 923 lines = report's "LOG.md:854-923".
## 3. Tool (cwd lane)
| command | exit | result |
|---|---|---|
| `tools/report-landing-audit.py --rounds 15 --no-errata --json` | 0 | cutoff 1792485831; round_commits 3; required 3; post []; defects []; clean |
| `... --rounds 15 --json` (errata on) | 1 | failed: errata_unmatched 9 (rounds 10, 18, 20); uncorrected 0 (F1) |
| `... --json` (all rounds, errata on) | 0 | clean: corrected 9; uncorrected 0 |

Hand and tool agree on count, cutoff, pre/post and cited set. No FN/FP on this report.
## 4. Blind spots (probe out/AuditReport15/blindspot_probe.py, exit 0)
Mutants via `--report 15=PATH` (cutoff=now) and two synthetic lane/fleet repos. Tool code at a29bb84: FULL/ABBREV lowercase-only (L50-51); author `kama-shokunin` + `^round-N:|^checkpoint\(rN\)` (L88, L92); Landed `is_object(...,"commit")` over lane OR fleet (L128); body check accepts any object (L117).

| case | tool | should flag? | class |
|---|---|---|---|
| M1 Landed cites round-14 e545ed99 (40-hex) | 0 | yes | FN: other-round commit accepted as landed |
| M2 same, 7-hex e545ed9 | 0 | yes | FN: same |
| M4 Landed cites fleet commit 402b93b5 | 0 | yes | FN: fleet object accepted as landed |
| M11 body e545ed99 swapped for fleet commit 215ba746 | 0 | yes | FN: wrong hash resolves to unrelated object |
| M8 body uppercase nonexistent 40-hex | 0 | yes | FN: uppercase never matched (git accepts uppercase) |
| M10 body nonexistent 10-hex | 0 | spec gap | FN: 7-39-hex outside Landed unchecked |
| S1 kama `Round-15 - ...` pre-report, uncited | 0 | yes | FN: subject regex misses variants |
| M7 Landed uppercase 70AF36C2... | landed-omitted | no | FP: commit is cited, uppercase ignored |
| M13 prose "effaced" in Landed | landed-unresolved | no | FP: a-f-only word read as hash |

Caught correctly: M3 blob in Landed (`^{commit}`), M5/M12 nonexistent in Landed, M6 dropped row, M9 nonexistent body hash, S2 uncited pre commit. Not checkable by the tool: push time (reflog only); `%ct` committer time is author-set.
## 5. Findings
- F0 round 15: no landing defect; hand and tool agree.
- F1 (tool scope, low): errata rows for rounds outside `--rounds` count as unmatched, so a subset run exits 1 "failed" with uncorrected 0. Full run is clean. Fix: scope unmatched to in-scope rounds. Not applied.
- F2: section 4 items are real FN/FP classes, none triggered by round 15. Hardening (not implemented): lane-ancestry and round check for Landed tokens, case-insensitive hex, body abbreviated-token check, prose-word guard, subject variants.
## 6. Files, tools, cleanup
- Out: out/AuditReport15/ {by-hand-transcript.txt, by-hand-summary.json, tool-r15-errata-mode.json, tool-all-rounds-errata-mode.json, origin-master-reflog.txt, blindspot_probe.py, blindspot-probe.out, blindspot-probe.json}.
- Tools installed/updated: none (python3 stdlib, git). No tracked lane file, index or git state changed; new files only under out/AuditReport15/ and this file. Scratch removed; tool bytes verified equal to a29bb84 (sha256 a60acc3a...).
- Not run: `--selftest`, round-21 `--report` (out of scope). [INFERENCE]: reflog clock = push time; content from file lists, not diffs; lane status after push not checkable now.
