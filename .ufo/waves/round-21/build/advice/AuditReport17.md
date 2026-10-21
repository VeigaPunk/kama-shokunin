VERDICT: confirm - r17 by-hand derivation matches the tool exactly (0 defects, 2 required lane commits, 0 post-report); no invisible defect in r17; 4 tool blind spots and 1 false positive reproduced, none triggered

# AuditReport17 - round-17 kama report, by-hand C1 re-derivation

Scope: `.ufo/reports/round-17/kama.md` (fleet commit 543437674, ct 1792524895, the only commit touching it). Lane `kama-shokunin` master tip a29bb84 (draft under attack); lane tool blob 728ebe19 equals `a29bb84:tools/report-landing-audit.py`. No tools installed. All exits observed.

## 1. By hand (git, not the tool)
- Lane master, author `kama-shokunin`, subject `round-17:` or `checkpoint(r17)`:
  - 54a29268e2083caa2b1e0d54ee1e7d90961302f3, ct 1792513497, parent cff9e62 (round start), "round-17: graded check.py ..."
  - 5e9ae6e93dce529a48229647e482f18a291463cd, ct 1792524834, parent 54a29268, "round-17: falsify wave evidence ..."
  - Excluded: e75cf680 (protocol-shokunin, "round-17 verifier spot-check", ct 1792525303, after cutoff). No `checkpoint(r17)` on any ref.
- Split at cutoff 1792524895: pre = 2, post = 0. Required = 2.
- `## Landed changes` (lines 46-56) cites `54a29268` (rows, lines 50-53) and `5e9ae6e9` (lines 54-55). Each is a unique prefix of a pre commit. Cited 2/2; landed-omitted 0.
- 40-hex tokens (lines 4, 5, 6, 59), `cat-file -t`: each is a commit in the lane (rc 0) and absent from the fleet (rc 128).
- 15 unique >=7-hex tokens in total:
  - 10 commit tokens, all lane commits: 54a2926 (21, 88), 5e9ae6e (7, 88), cff9e62 (87), b8e485c and ccc4bb3 (90), plus the three 40-hex tokens and the two Landed prefixes above.
  - 5 digest tokens, all reproduced: `753bfa73...` (145) is sha256 of the retained archive (22,240,468 bytes); `b853576e...` (64) is sha256 of check.py at cff9e62; `36b64978...` (17) is sha256 of tools/kama-probe.sh (blob ce45ea8e at all three commits); `bf9068d8...` (23) is the round-16 matrix digest (measure.py:286-290 construction, 9 files, identical at cff9e62 and 54a2926); `70418a0f...` (125) is sha256 of scripts/hyaku/ufo-wave-policy-v2.json (build/validation.json:40, falsify/validation.json:30).
- Start claim holds: parent(54a2926) = cff9e62. "Lane tip, pushed" holds: origin/master reflog has 5e9ae6e at 1792524836, before the cutoff; e75cf68 follows at 1792525304.
- Landed rows match content: every file named in rows 50-55 appears in the cited commit's `--stat`. 54a29268 changes 187 files (including tests/probe-verdicts/check.py, tools/sources-append-only.py, corpus/SOURCES.md); 5e9ae6e changes 96 files (73 falsify advice .md reports, SCORECARD.md, SKILL.md).

## 2. Tool
`python3 tools/report-landing-audit.py --rounds 17 --no-errata --json` gives rc 0. Round 17: cutoff 1792524895, round_commits 2, required 2, post_report [], defects []; status clean.
Agreement is exact. False negatives: 0. False positives: 0.

## 3. Defects the tool cannot see
Harness `build/out/AuditReport17-6/mutants-r17.py` gives rc 0, with control plus 10 mutants, 11/11 as expected. Mutants are copies of the report audited with `--report 17=COPY`.

| Case | Edit | Tool | Class |
|---|---|---|---|
| M1, M1b | Landed row 50 cites ccc4bb31 (kama r16) or cff9e62 (protocol) | clean | BLIND: other-round or non-kama commit accepted |
| M2 | header 40-hex replaced by blob ce45ea8e... | clean | BLIND: unresolved-full-hash accepts any object type |
| M4 | row 50 cites 896956536a (off-master jj object) | clean | BLIND: off-master object accepted |
| M5 | non-Landed `--from deadbee1` | clean | BLIND: short tokens outside Landed never existence-checked |
| M7 | Landed cites `5E9AE6E9` (uppercase) | landed-omitted | FALSE POSITIVE: citation regex is lowercase-only |
| M3, M6, M8, M9 | nonexistent 40-hex; dropped cites; nonexistent prefix; renamed heading | flagged | caught |

None of the BLIND or FP conditions holds for r17: every cited commit is a round-17 kama master commit (ancestry rc 0), all 40-hex tokens are commits, there is no uppercase hex, and no unresolved token sits outside Landed. No invisible defect was found in r17.

## 4. Notes
- `refs/jj/keep` holds 151 objects. Seven kama-authored off-master objects with committer time 1792500000-1792530000 have empty subjects [INFERENCE: jj intermediate versions]. No r17 citation uses them.
- The fleet add-commit also appends `.ufo/l0-questions.md` (+1). Not a lane commit; no defect.
- The fleet working-tree report blob equals HEAD (ba6b24f2), so the tool audits the committed text.
- Source reading: the tool's default fleet root is the lane's parent; cutoff is the committer time of the oldest `--diff-filter=A` commit; round_commits matches `%an` exactly and `^round-N:|^checkpoint(rN)` on master only.
- My control slip: `git rev-parse --verify` accepts a well-formed full hash without an existence check (rc 0 for a nonexistent one). The tool uses `cat-file -e` (rc 1 for the same string), so it is unaffected; re-checked with `cat-file`. A typo'd `rev-parse` (rc 128) was discarded.

## 5. Key commands (exit)
- `git -C <lane> log master --format='%H %an %ct %s'`: rc 0. `git -C <fleet> log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-17/kama.md`: rc 0.
- `git -C <lane> log master --grep='round-17' --grep='r17' --grep='checkpoint(r1'`: rc 0. `git -C <lane> log --all --grep='^round-17' --grep='^checkpoint(r17)'`: rc 0.
- `git -C <lane> merge-base --is-ancestor {cff9e62,54a2926,5e9ae6e} master`: rc 0 each.
- `git -C <lane> hash-object tools/report-landing-audit.py`: rc 0 (728ebe19). `git -C <lane> rev-parse a29bb84:tools/report-landing-audit.py`: rc 0 (728ebe19).
- `git -C <lane> cat-file -e 5e9ae6e93dce529a48229647e482f18a291463ce`: rc 1. Same with ...cd: rc 0. `git -C <lane> cat-file -t deadbee1`: rc 128.
- `sha256sum /home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`: rc 0. `git -C <lane> reflog show --date=unix refs/remotes/origin/master`: rc 0.
- Python subprocess cells ran the same git calls (census, `--disambiguate`, digests, keep refs) and the ten mutants; per-item rc is tabled above.

## 6. Installs and cleanup
None. Scratch `/tmp/kama-r21-AuditReport17-6` removed (rc 0, absent). Lane untouched by git: only new untracked files under `build/out/AuditReport17-6/` and `build/advice/AuditReport17.md`.
