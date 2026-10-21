VERDICT: partial - round-18 defect set reproduced by hand exactly (3 landed-omitted, 0 unresolved, 0 FN/FP on this report); tool blind spots and two failure modes in §4.

# AuditReport18 - round-18 landing audit, independent re-derivation
Seat KamaR21.AuditReport18-6, 2026-10-21. Read-only on lane and fleet; writes only under the lane's `out/AuditReport18-6/` and this file. Installs: none (git and python3 only). Processes started: none. Scratch `/tmp/kama-r21-AuditReport18-6` removed after archiving fixtures.

## 1. Hand derivation (git only; the audit tool ran only after this was written down)
- `git -C kama-shokunin log --format='%H %an %at %ct %s' master`, exit 0: 82 commits. Author `kama-shokunin` and subject `round-18:` or `checkpoint(r18)`: 7.
- `git -C fleet log --diff-filter=A --format='%H %ct' -- .ufo/reports/round-18/kama.md`, exit 0: `23bdc3f8c92d4be74abead0de4015acf9a749e39` ct 1792561152, the only commit touching the path. Cutoff 1792561152.
- Report blob, committed and on-disk: `df4ea71` (equal). Tool blob at a29bb84 and on-disk: `728ebe1` (equal). `git rev-parse` / `git hash-object`, exit 0.

| commit | ct | split | subject | paths | Landed L73-86 | elsewhere |
|---|---|---|---|---|---|---|
| c6dc46fa | 1792535629 | pre | round-18: classify missing observations | 169 | NO | L26 |
| 1c325b2e | 1792538038 | pre | round-18: retain measured arms | 116 | NO | L27 |
| 101f3991 | 1792539394 | pre | checkpoint(r18): ...unadmitted | 96 | NO | L19 |
| 0c75c611 | 1792558682 | pre | round-18: close falsify seams | 8 | yes L75 | - |
| 888cd384 | 1792558700 | pre | round-18: residual falsification evidence | 10 | yes L78 | - |
| eb78788b | 1792559122 | pre | round-18: harness clean-tree guard | 1 | yes L80 | L67, L90 |
| 1b85a24e | 1792561115 | pre | round-18: measured pass on eb78788b | 27 | yes L82 | L91 |

- 7 required, 0 post-report. All 7 are ancestors of master (`merge-base --is-ancestor`, exit 0 x7). Closest pre-report commit 1b85a24 is 37 s before the cutoff. Landed cites 4; 3 are omitted.
- Omitted: 381 paths (2 binary tarballs, both in checkpoint 101f3991), +153,085/-1,287 lines. Cited: 46 paths, +9,133/-1,061 lines.
- 40-hex tokens (4 distinct): `git cat-file -t` = commit in lane, absent in fleet (exit 128). Short tokens at L19, L26, L27, L67, L91 each disambiguate to exactly one lane commit. Landed tokens are the 4 full hashes, all commits.
- No wrong hash and no cross-round citation: each cited subject matches its context. Non-master refs hold 114 commits, none round-18 kama.

## 2. Tool comparison
- `python3 tools/report-landing-audit.py --rounds 18 --no-errata --json`: exit 1, status failed, defects 3, all `landed-omitted` (101f3991, 1c325b2, c6dc46f); cutoff 1792561152, required 7, post 0. Hand = tool: FN 0, FP 0.
- `--rounds 18 --json` (lane ledger): exit 1. corrected 3 (rows 8-10), uncorrected 0, but errata_unmatched 6 (rows 3-7 for r20, row 11 for r10), so status failed.

## 3. Defects the tool cannot see (this report)
- Contract `.ufo/prompts/kama-round-18.md:107-108`: "every change tied to a LOG.md entry and to the commit hash that carries it." LOG.md at 1b85a24, L1086: "Landed implementation `c6dc46fa...`". L1105-1106 names checkpoint 101f3991 and reused commit 1c325b2. The omissions contradict the report's own vocabulary, not only the tool's rule.
- Magnitude: the omitted commits are most of the round's work (381 vs 46 paths); the tool counts each omission as 1. [INFERENCE: c6dc46f is the C1 classification change, from its subject.]
- Narrative: L85-86 "Every change above is recorded there; the lane tip contains all four commits." Literally true, but it presents four as the whole round (seven).
- Label: L91 calls 1b85a24 the "evidence commit"; LOG L1125 calls 888cd384 the "evidence commit".
- Fleet-side kama round-18 commits (d7beee2..., f4c9ae5...) fall outside the lane-only rule and are not counted. [INFERENCE: policy question.]

## 4. Tool defects (probes on scratch drafts of this report; fixtures in out/AuditReport18-6/fixtures/)
- P1 scoped errata: whenever the ledger holds rows for rounds outside the run, `--rounds N` exits 1 (errata_unmatched 6 here). Design defect [INFERENCE]; the docstring says unmatched rows fail the run.
- P2 errata gate is structural: E10 rows `18 landed-omitted <tok> <any resolvable commit>` with corrections a29bb84 (lane tip) and 23bdc3f (fleet commit) give exit 0, status clean. "corrected" counts defects matched by a ledger row; the committed report is unchanged. Registry rows 8-10 use each omitted commit as its own correction.
- P3 `--report N=PATH` sets cutoff=now even for committed reports (tool L110-113; docstring L23-24 limits this to uncommitted reports). Round 19 committed: default exit 0, post 4. With `--report 19=<committed>`: exit 1 with 4 false positives (3389513, 464ea5a, 60e8fd8, 8d9191f). E0b: r18 via --report shows report_committed=false.
- P4 Landed citations accept any commit in lane or fleet with no round or subject check (tool L127-128). E1 (round-17 lane commit 5e9ae6e) and E2 (fleet commit 23bdc3f): no defect.
- P5 full-hash check accepts any object type (`cat-file -e`, tool L73). E3 (tree c562b73d... of eb78788) in non-Landed text: no defect.
- P6 uppercase hex and tokens under 7 characters are invisible (regex, tool L50-51). E5 (absent uppercase 40-hex) and E6 (absent 6-hex): no defect. Control E4 (absent lowercase 40-hex in Landed): 2 defects. E7 (7-hex c6dc46f cited): landed-omitted 3 -> 2.
- P7 the report is read from the working tree (tool L105), not the committed blob; report_committed only means the path has an add commit (L110-111). No effect on r18, since blobs are equal.

## 5. Notes for L1
- Do not read `corrected` as repair. Scope errata by round before using `--rounds N` as a gate.
- Selftest and other rounds' reports were not run (out of scope).

Out: `.ufo/waves/round-21/build/out/AuditReport18-6/`: derivation-r18.txt, nonmaster-and-numstat-r18.txt, tool-r18-no-errata.json, tool-r18-with-errata.json, probes-r18.json, probe-errata-unrelated-r18.json, fixtures/ (8 files).
