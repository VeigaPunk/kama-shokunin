VERDICT: confirm - retrospective census 8bf99cae → 3389513f gives 56 → 57 rows (A 53→54, C 3, mined 45→46, queued 5, rejected 6). Census and validate both exit 0 with the same three W04, matching every round-19 report figure.

# CensusR19Retro: retrospective round-19 census receipts (round 20)

Axes: fidelity to the round-19 report figures, receipt reproducibility, and keeping errors separate from verdicts in the reconstruction.
Deliverables are new files in `.ufo/waves/round-20/build/out/CensusR19Retro/`. Lane HEAD is still 37bd4c5, and porcelain shows only `?? .ufo/waves/round-20/`. Scratch `/tmp/kama-r20-CensusR19Retro` is deleted (`ls` exit 2). Installs: none.
- `census-before-retro.txt` sha256 deaafbec…0c69 and `census-after-retro.txt` sha256 cba670eb…e242, 33 lines each. The `#` header gives: the RETROSPECTIVE (round-20) label; source revision with its commit date and subject; blob and sha256; both roots and both commands; script sha256 3fb72615…4d64e30; fleet rev 4a2bb5c; gawk 5.4.1; TODAY 2026-10-21; run date 2026-10-21T04:27:35-03:00. The body follows the round-20 `sources/census-before.txt` layout: validate, `exit=`, census, `exit=`, `measured_at=`.
- `run.log` (c5f633a7…): every command with its stdout, stderr and exit.
- `run-retro.sh` (876a47db…): `bash run-retro.sh OUT_DIR` reproduces everything. It only reads the lane (git show/archive), refuses to overwrite and deletes its scratch.
- `oracle-tally.py` (83f2038a…): an independent stdlib tally that never calls the census script.

## Commands and exits
| Command | Exit | Observed |
|---|---|---|
| `bash /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/CensusR19Retro/run-retro.sh /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/CensusR19Retro` | 0 | both receipts and run.log written; scratch gone |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /tmp/kama-r20-CensusR19Retro/before kama` | 0 | rows 56, A 53, B 0, C 3, mined 45, queued 5, rejected 6, missing 0 |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /tmp/kama-r20-CensusR19Retro/after kama` | 0 | rows 57, A 54, B 0, C 3, mined 46, queued 5, rejected 6, missing 0 |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /tmp/kama-r20-CensusR19Retro/before-tree kama` | 0 | W04 S031, S043, S056; `kama ok` |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /tmp/kama-r20-CensusR19Retro/after-tree kama` | 0 | same three W04; `kama ok` |
| `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /tmp/kama-r20-CensusR19Retro/{before,after}-tree kama` (separate invocations) | 0 / 0 | stdout byte-identical to the SOURCES-only roots |
| `grep -cE '^\\| *S[0-9]{3} ' /tmp/kama-r20-CensusR19Retro/{before,after}/kama-shokunin/corpus/SOURCES.md` (separate invocations) | 0 / 0 | 56 / 57 |
| `git show <rev>:corpus/SOURCES.md | python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/CensusR19Retro/oracle-tally.py -` for 8bf99cae, 3389513f and 7229fa9 (run.log has each exact command) | 0 / 0 / 0 | 56 A53 C3 m45 q5 r6 / 57 A54 C3 m46 q5 r6 / same as 3389513f |
| `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --numstat 8bf99cae7de2517fd4ebe209f3b940aeabb6b687 3389513f5107d5d77213cafa35ff2cbc18845100 -- corpus/SOURCES.md` | 0 | `7 0`: additions only, no cell rewritten since round start |
| `diff` of filtered lines (eval, python): before-retro census vs `round-18/sources/census-after.txt` | 0 | 16/16 identical |
| same: after-retro census, and its W04 lines, vs `round-20/sources/census-before.txt` | 0 / 0 | 16/16 and 3/3 identical |
| same: before-retro E/W lines vs after-retro E/W lines | 0 | 3/3 identical; S057 adds no W04 |

## Against the round-19 report
Source: `/home/vgpnk/Projects/shokunin/.ufo/reports/round-19/kama.md:97-100` at fleet commit ac9859f (file sha256 925876f1…57d0, clean). Quoted: "**56 → 57 rows**, exit 0 both times"; "Tiers A 53 → 54, C 3 → 3. Status mined 45 → 46, queued 5 → 5, rejected 6 → 6. `validate` exit 0 with three expected W04 duplicates (S031, S043, S056). Rows added: S057 (tier A, docs)."
Every figure matches. That covers rows, tier A and C, the three statuses, census exit 0 on both sides, validate exit 0 with the same W04 IDs, and S057 as the only added row (the oracle's last ID moves S056 → S057). The routed defect at `corpus/lessons/round-19-verifier-spotcheck.md:40-42,194` @37bd4c5 reads "The round-19 census receipts are uncommitted." These files can close it once the L1 commits them. [INFERENCE] Keep the `-retro` names under `.ufo/waves/round-19/sources/` so they never pass as the original receipts.

## Findings
1. Blob provenance (`git rev-parse <rev>:corpus/SOURCES.md`, exit 0):
   - 1b85a24 (round-19 start) and 8bf99cae: 1e09b779.
   - 7229fa9 (the report's measured commit): 7cca031c.
   - 5b108c1 through 3389513f and 37bd4c5: 166268c6, which also equals `git hash-object` of today's working copy.
   7229fa9 → 5b108c1 changed only S057's used-by cell, `registry/required-citations.json` → `SCORECARD.md` (numstat `1 1`). The counts are unchanged. So the retro after-census equals the round-20 start census.
2. The assigned recipe also needs a config file. With no `<root>/shokunin.conf`, both sides exit 2 (`ERROR: config not found` plus `unknown lane … kama`; run.log). Each root therefore gets a conf holding only the fleet `shokunin.conf:52` kama row. The fleet conf last changed in 10405f4 (2026-10-19), before round 19.
3. Errors are not verdicts, applied to this reconstruction. `validate` on the SOURCES-only roots exits 1 with 79 (before) and 81 (after) E11 "missing used-by" lines. Those paths were simply never written into the root, so these lines report a state the tool could not evaluate, not registry verdicts. The receipts take validate from the git-archive roots instead: 1349 and 1431 tracked paths, equal to the extracted counts. There E11 = 0 and validate exits 0. Each receipt's cross-check header line records this.
4. A hazard in the fleet script, routed because the lane does not own it. In `sources-census.sh`, `build_roster` calls `die` at :454, but it runs inside `roster=$(build_roster)` at :517. A missing conf therefore exits only the subshell, and `resolve_targets` falls back to a `[ -d "$arg" ]` check relative to the current directory (:521-523). I probed this from a directory containing `kama/`:
   - census exits 1 and prints `kama missing <cwd>/kama/corpus/SOURCES.md`;
   - validate exits 2;
   - with a non-registry file at `kama/corpus/SOURCES.md`, census exits 0 and prints `kama rows 0` (stderr still says config not found).
   The control run from /tmp exits 2. So a configuration error turns into a census verdict, which is the C1 error class. It is a candidate error-injection cell. [INFERENCE] Whether a fleet script belongs in the lane's frozen population is the L1's call.

## Risks / limits
- These runs measure committed blobs. The round-19 commands read the live working tree, whose states between commits I did not observe. Both committed after-blobs tally identically.
- The script bytes equal the round-19 CensusPrefetch sha (3fb72615…4d64e30), and the script last changed in 6a1dd8c on 2026-10-19. The gawk version used in round 19 is unrecorded.
- TODAY = 2026-10-21 is the round-19 UTC date. S057 was opened that day, so E08 would fire only with TODAY < 2026-10-21.
- The receipt `ok` lines name the deleted /tmp tree path; the round-20 receipt names the lane path instead.
- Checks for the L1: re-run `bash run-retro.sh <new dir>` (any new directory) and diff the bodies.
