VERDICT: confirm - tool's round-20 output (5 defects: 1 unresolved-full-hash, 4 landed-omitted) matches my hand derivation exactly; 0 false positives, 0 false negatives, no hash-level defect the tool cannot see.

# AuditReport20 - independent C1 re-derivation, round-20 kama report

Scope: `.ufo/reports/round-20/kama.md`. Fleet add `04eb5d2d9b4712c5266bdc36fbb16c2fefd7b392` (ct 1792577594) is the only commit touching it; working blob `54b1aff4` = committed blob. Lane master = origin/master = `a29bb84`. My commands wrote no lane file (plain `git status` may have refreshed the index stat cache; see caveat). An uncommitted one-line blank insertion in `tools/kama-llamacpp-live.py` `_selftest` appeared after my first status check (`git diff --stat`: 1 insertion); not mine, not reverted. The audited `tools/report-landing-audit.py` was clean at that check.

Independence caveat: the tool ran (exit 1) and its source was read before my hand pass finished; a grep surfaced the MANIFEST closure text. The comparison rests on git commands run afterward. Plain `git status` ran in lane and fleet (may refresh index stat cache; no content change).

## 1. Population and split
- `git -C <lane> log master --author=kama-shokunin -E --grep='^(round-20:|checkpoint\(r20\))' --format='%H %an %ct %s'`: EXIT 0, 9 rows. `log --all` (196 commits) shows no other round-20 or checkpoint(r20) subject on any ref.
- All 9 ct <= 1792577449 < cutoff 1792577594: pre 9, post 0 (tool: required 9, post_report 0).

| commit | ct | in Landed | cited elsewhere | hand -> tool |
|---|---|---|---|---|
| 7a6bc911 | 1792577449 | yes (L19) | - | ok |
| 3ec5ea68 | 1792576964 | yes (L18) | - | ok |
| 9add96e4 | 1792576824 | yes (L17) | L11, L25-26, L28, L32, L50 | ok |
| 04de7a87 | 1792576704 | yes (L16) | L11 | ok |
| c7311039 | 1792576506 | yes (L15) | L11 | ok |
| 846e366d | 1792574702 | no | none | omitted -> landed-omitted (cited_elsewhere=false) |
| 92b14625 | 1792573685 | no | none | omitted -> landed-omitted (false) |
| 0957ce61 | 1792571024 | no | L7 (8-char), L10 (full) | omitted -> landed-omitted (true) |
| 33a67778 | 1792569678 | no | none | omitted -> landed-omitted (false) |

## 2. Hex tokens (23 boundary-free runs = 21 tokens + 2 glued English words)
- 40-hex, lane `git cat-file -t` / fleet `git cat-file -e`:
  - `0957ce619789d13d894ef21bc863486bcb35b56c` (L7): lane exit 128 ("could not get object info"), fleet exit 1. Nonexistent.
  - `0957ce619789d13bb5779606078fa1498114d2c7` (L10) and the five Landed hashes (L15-19; `9add96e4` also L25-26): lane `commit`, exit 0 each; fleet exit 1 (fleet holds no lane objects).
- 8-char prefixes `0957ce61`, `c7311039`, `04de7a87`, `9add96e4` (L7, L11, L25-50): `git rev-parse --disambiguate` lane exit 0, one candidate each, equal to the full hashes.
- `b11755` (L65, release tag) and `753bfa73` (L65, tarball digest): empty in both repos, exit 0; not commits.
- Wrong hash elsewhere: `git cat-file -t` over 46 git repos under /home/vgpnk/Projects (`find -maxdepth 4`): none. Grep (gitignore on) over /home/vgpnk/Projects/shokunin: 2 files, the report L7 and MANIFEST.json closure text quoting it.

## 3. Landed bullets and cited evidence
- `git show --name-only` (EXIT 0): c7311039 = 73 `falsify/advice/*.md`, SOURCES, LOG, SCORECARD, lesson, `tests/gguf-identity/expected.json` + `make_fixtures.py` (bullet 1 consistent). 04de7a87 = `c2/measure-reference.json`, `runs/c7311039/`. 9add96e4 = `c2/measure.py`, `runs/04de7a87/`. 3ec5ea68 = `runs/9add96e4/*`. 7a6bc911 = LOG.md. All five consistent.
- 20 in-repo cited paths exist at 7a6bc911 (`git cat-file -e`, exit 0 each). `scripts/sources-census.sh` is fleet-relative (`test -f`, exit 0).
- `runs/9add96e4/commands.json` (`git show 3ec5ea68:...`, EXIT 0): `measured_commit` 9add96e4 matches the table; 21 commands, `as_expected` 21/21; the three nonzero exits carry expected 1. Harness-exit file not read.
- The same file uses round-19 commit `37bd4c5b` as an `append-round --from` baseline. The report does not cite it.
- L10 claim: `git show 0957ce61:SKILL.md` lines 652-656 hold five routed gate rows (row 657 is the GGUF row).

## 4. Comparison
- `python3 tools/report-landing-audit.py --rounds 20 --no-errata --json` -> EXIT 1, status failed. Defects 5: unresolved-full-hash 1 (L7); landed-omitted 4 (846e366d, 92b14625, 0957ce61, 33a67778); landed-unresolved 0; landed-section-missing 0.
- Hand set equals tool set, same kinds. False positives 0; false negatives 0. The MANIFEST closure D1/D2 text, as quoted by grep, also matches; I did not rely on it.
- Tool-invisible hash defects: none. No non-commit object cited; no cited commit from another round; the one wrong hash resolves to nothing.
- Not a new defect kind [INFERENCE on severity]: 33a67778 is the first master add of `tools/error-verdict-census.py`, `tools/gguf-identity.py`, `tests/gguf-identity/expected.json` and `registry/error-injection-cells.json`. The measurement table cites those only by path, so Landed gives no hash route to them. The tool counts it like the record-only commits 846e366d and 92b14625.

## 5. Tool gaps (from source; none triggered here)
- G1 `FULL` (line 50) is lowercase-only: an uppercase 40-hex citation is invisible.
- G2 line 117 checks unresolved-full-hash with `cat-file -e` and no `^{commit}`: a 40-hex naming a blob or tree passes (Landed uses `^{commit}`, line 128).
- G3 7-39-hex tokens outside `## Landed changes` are never resolved.
- G4 `round_commits` (lines 85-94) reads only `--branch` (default master).
- G5 71 non-master commits with ct >= 1792560000 are reachable only from `refs/jj/*` (verified: 0 from other refs), all with empty subjects (62 kama-shokunin, 9 protocol-shokunin). None is on master or cited; spec and tool exclude them. [INFERENCE: pre-describe siblings of master commits]

## 6. Process
- Read-only git plumbing and file reads; wrote only the two deliverables; no installs or updates (none needed); no processes started; no /tmp scratch created.
- Files: `.ufo/waves/round-21/build/advice/AuditReport20.md` (this) and `.ufo/waves/round-21/build/out/KamaR21.AuditReport20-6/derivation.tsv` (31 rows: commands, exits, observations).
