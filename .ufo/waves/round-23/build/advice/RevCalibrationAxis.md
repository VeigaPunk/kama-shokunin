# RevCalibrationAxis: round-23 C1 axis classification and scoring

Seat: CloseKama22.RevCalibrationAxis (leaf reviewer, read-only). Findings only: no production edits, no commits, no tool installs.

## Bottom line

- **Axis: calibration, not operability.** All movement is on fault cells. The defect is in the verdict/exit channel and in an overreaching self-description, which is the lane's calibration signature.
- **Score: calibration 7 → 7, delta 0, verdict "improved, narrow".** Do not move to 8. Operability stays 8 and is not claimed.
- **Not yet admissible as written.** Three High findings (§4): the f3 cell is a silent no-op without committer identity; the candidate refuses a clean partial-clone input (an undeclared trade); the measured tree is an uncommitted working-tree edit that changed during review.

## Bound revisions

- Frozen: `4fe9339f8fc3a4a4a479d9c938a850da12f1124d:tools/report-landing-audit.py`, blob sha256 `09ecd63bdc3a…`, 847 lines. Copy: `/tmp/kama-r23/RevCalibrationAxis/frozen-audit.py`.
- Current: lane working tree, **uncommitted**, sha256 `79d9e124e817…`, 919 lines at copy time. Copy: `/tmp/kama-r23/RevCalibrationAxis/current-audit.py`. The file was observed in three states during review (847 → 864 → 919 lines; sha `d0a96599…` → `79d9e124…`).

## 1. Classification: calibration

Discriminator: where does before→after move? Controls (normal repo, ASCII subject, valid report, historical ledger) give identical verdicts in both arms. Movement is only on fault cells, on the verdict/exit channel and on self-description.

Evidence:
- **The exit channel is the verdict channel.** Frozen docstring L42–45: exit 1 = failed, exit 2 = could-not-evaluate, "Errors are never verdicts." Frozen `git()` (L87–97) uses `text=True` and catches only `OSError`; frozen `main` catches only `EvalError` and `OSError` (L835–843). Measured: f1 and f2 exit 1 with `UnicodeDecodeError` traceback. An uncaught exception is indistinguishable from a failed verdict by exit code.
- **The lane names this class.** `corpus/knowledge/error-is-not-a-verdict.md:20–24`: a "traceback-only 1" is "visible error evidence and must not … produce a clean overall grid."
- **Same-lane precedent, all calibration 7 → 7:** round 16 C1 (`SCORECARD.md:610`, verdict misgrade); round 17 C1 (`:654–663`, "an instrument's self-description made true is a bounded calibration repair, not a mastery change"); round 20 C1 (`:871–873`, crash/abort versus credited rejection); round 22 C1 (`:1079`, "calibration7 → 7; verified narrow improvement", explicit refusals 0/18 → 18/18).
- **The only operability-labelled crash repair is round 3** (`:31–33`), where a gate could not run at all (`file=missing`). Here every control runs and yields its verdict.
- **Admissibility confirms the label.** `AXES.md:33–34` requires a claim on the lowest non-retired axis. Calibration 7 < operability 8, and the stagnation waiver is inactive (`SCORECARD.md:132`). An operability label would leave the round with no lowest-axis claim.
- **Not exploratory.** The verdict cells are countable; `AXES.md:43–50` reserves exploratory for uncountable moves.

The exec faults (lazy-fetch `core.sshCommand`, `log.showSignature`) are overreach of the "cannot redirect" self-description (frozen `git_env` docstring L80–81). They belong under calibration as D4 frontier ground, but they change no verdict in the grid.

## 2. Scoring: 7 → 7 (delta 0), "improved, narrow"

Why not 8:
1. Same-class precedent holds calibration at 7 (rounds 17, 22).
2. The grid is small and partly unstable: six demonstrated before-cells (two new in this review), one environment-conditional (f3), one not demonstrated (f6). See §3.
3. The added behaviour outruns the measurement: six new refusal classes (shallow, `info/grafts`, partial clone/promisor, non-sha1, non-top-level, ref-named citation). Only partial clone was tested against a clean input, and it flips (H2).
4. 8 is the saturation line on every owned axis (`SCORECARD.md:132`). A calibration 8 would arm saturation/retire/split rules that nothing here supports. "Errors are never verdicts" is still universal wording (M2).
5. Counts are the falsifiable evidence, not a 0–10 conversion (`SCORECARD.md:240–242`).

It is still a real move, not "no change": verdict-channel and exec-channel cells flip, and the historical ledger is byte-identical.

## 3. Measured grid

My fixtures live under `/tmp/kama-r23/RevCalibrationAxis/fx*`, with `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `example.invalid` remotes, and no network. Frozen probe run: `/tmp/kama-r23-probe/run.bc4O`. Current: `run.1aRD`.

| Cell | Frozen (09ecd63b) | Current (79d9e124) | Reading |
|---|---|---|---|
| control (ASCII, normal) | exit 0, clean, req 1 | exit 0, clean, req 1 | unchanged |
| f1 `i18n.logOutputEncoding=ISO-8859-1` + non-ASCII subject | exit 1, `UnicodeDecodeError` traceback | exit 0, clean (correct) | fixed |
| f2 invalid UTF-8 in committed report | exit 1, `UnicodeDecodeError` traceback | exit 2, "output is not UTF-8" | fixed (typed refusal) |
| f3 `refs/replace` hides omitted commit, **identity present** | exit 0, clean (false), req 1 | exit 1, landed-omitted, req 2 | fixed, **conditional** (H1) |
| f3, **no committer identity** | `commit-tree` rc 128, no replace ref, exit 1 landed-omitted (correct) | same as frozen | fault absent: fixture no-op |
| f4 `refs/replace/<fabricated 40-hex>` | exit 0, clean (false) | exit 1, unresolved + landed-unresolved (correct) | fixed |
| f5 promisor + `core.sshCommand` | exit 1, correct verdict, **marker created** | exit 2, partial-clone refusal, no marker | exec fixed; verdict already correct |
| f6 `log.follow=true` | exit 0, clean, req 1 | exit 0, clean, req 1 | **no before-flip; not creditable** |
| NEW signature: `log.showSignature=true` + `gpg.program`, signed commit | plain `git log` runs the program (marker created); audit exit 1, correct | exit 1, correct, no marker | exec fixed; verdict unchanged; not in L1 grid |
| NEW showRoot: report is the fleet root commit + `log.showRoot=false` in fleet | exit 2, "has no fleet commit" (false refusal) | exit 1, landed-omitted, req 2 (correct) | fixed (false refusal) |
| TRADE: partial clone, every cited object local | exit 0, clean, req 1 | exit 2, "partial clone (extensions.partialclone)" | **clean input flips to refusal (H2)** |
| `%an` vs `%aN` with `.mailmap` (`log.mailmap` unset vs true) | `kama-shokunin\|other` in both settings | same | `%an` is raw; no verdict channel |
| historical ledger `--rounds 10- --json` on the real lane and fleet, read-only | exit 0, clean, 13 reports, 9 defects (all errata-corrected), required 54, post-report 5 | byte-identical JSON | no harm |
| selftest (`--selftest`) | 50/50 | 50/50 | exercises none of the changed paths (M3) |

Real repos: `extensions.partialclone`, `remote.*.promisor`, `i18n.logOutputEncoding`, `log.follow`, `core.sshCommand`, `log.showSignature`, `gpg.program` are unset; `refs/replace` is empty in both repos; both are non-shallow sha1 (`git rev-parse --is-shallow-repository --show-object-format`).

Notes on the L1 run directories: 23 of them have frozen-like f1 and f2 crashes. Their f3 reads clean in 17 and failed in 6. The 31 directories mix AUDIT variants and pin no SHA, so I used none of them as evidence. The count shows that f3 is unstable, not what the verdict is.

## 4. Findings

### High

**H1. f3 is a silent no-op without committer identity.** The probe `/tmp/kama-r23-probe/probe.sh:43` runs `commit-tree` then `replace` without checking rc. Without an identity, `commit-tree` returns rc 128 ("Author identity unknown"), no replace ref is created, and the audit is correct in both arms. In my probe run `run.bc4O/f3/lane` has no replace ref, and `git var GIT_COMMITTER_IDENT` does not resolve in this environment. The false clean appears only where an identity resolves. Fix: assert rc == 0 and a non-empty `for-each-ref refs/replace` before the cell counts, and pass explicit `GIT_AUTHOR_*`/`GIT_COMMITTER_*`. If it still cannot be made stable, count f3 as conditional.

**H2. Undeclared trade: partial clones are refused, and a clean input flips.** The current copy (`/tmp/kama-r23/RevCalibrationAxis/current-audit.py`, the working tree at sha `79d9e124…`) L445–448 refuses any repo with `extensions.partialclone` or `remote.*.promisor`, even when every cited object is local. Measured: frozen exit 0 clean, current exit 2 `could-not-evaluate: … partial clone`. This violates the claim's own "controls unchanged" rule. Two honest options:
  - (a) Declare it as an operator-ruled behavior change. `AXES.md:35–36`: "a trade anywhere is not an improvement."
  - (b) Use a per-object policy: audit present objects; treat promised-but-absent objects as missing under `--no-lazy-fetch`. This matches the lead's stated direction, keeps the input clean, and the candidate diverged from it.
  Coverage and operability harm arises only if partial clones are in scope. For lane and fleet they are not (config unset, verified).

**H3. The measured candidate is uncommitted and moving.** `tools/report-landing-audit.py` in the lane checkout differs from HEAD `4fe9339f`. It changed during this review (see revisions). Receipts must bind a committed SHA. I wrote nothing to the lane tree.

### Medium

**M1. The docstring names channels that have no grid cell** (current L48–51: "refs/replace, lazy fetch, signature display, log re-encoding, log.follow and .mailmap are neutralized"):
  - refs/replace, lazy fetch, re-encoding: measured (f3, f4, f5, f1).
  - signature display: real exec channel, measured in this review (plain `git log` runs the configured `gpg.program`). Add the cell.
  - log.follow: no before-flip in any run (f6 clean with req 1 in both arms). Relabel "defensive, unmeasured", or build a flip fixture (an omitted lane commit dated between the first add and a later rename). I did not build it.
  - .mailmap: no verdict channel. `round_commits` matches `%an`, which is raw under both settings. Drop "neutralized".
  - showRoot (in `GIT_ISOLATION` L93, not in the docstring): a measured false-refusal channel. Add the cell and name it.
  - core.quotePath (L95): no effect on the round-path regex, which matches only ASCII names (reasoning, not run). Drop it or label it defensive.
  - Keep L51, "Audit trusted repositories only." It is the right calibration boundary.

**M2. "Errors are never verdicts" (current L46) is universal wording.** Only enumerated classes are covered. Unenumerated exceptions still exit 1 through Python's default. Narrow the sentence to the R23 grid. A blanket `except Exception → 2` would turn bugs into could-not-evaluate and reduce diagnosability; I would not add it inside this claim.

**M3. The selftest is no evidence for the change.** It is 50/50 in both arms, but no case touches encoding, replace, lazy fetch, showRoot, signature, or any new refusal. The grid is the only evidence. Say so in the claim.

### Low

**L1. Undeclared git floor.** `--no-lazy-fetch` is rejected by old git, which makes every run exit 2 (candidate L89–90). Not tested here (host git 2.56.0). Declare the minimum version.

**L2. Design size.** `git()` becomes bytes-mode with an `errors` parameter, and two callers use `surrogateescape`. The smaller convention-following change is text mode with `encoding="utf-8"` plus one `except UnicodeDecodeError` inside `git()`, which `load_source_urls` already does (frozen L212, L223). That is better for six-month maintainability.

## 5. Conditions for "improved, narrow" (all required)

1. Commit the candidate. Frozen is pinned to blob `4fe9339f…` (sha `09ecd63b…`); current is pinned to the committed blob SHA; every receipt records the AUDIT SHA.
2. H1 fixed: the fixture asserts commit-tree rc and a replace ref, with explicit identity.
3. Add the signature and showRoot cells. Relabel log.follow unless a flip fixture is built. Drop "neutralized" for .mailmap and core.quotePath.
4. H2 ruled by the operator as a declared trade, or changed to per-object policy. Add a partial-clone-with-local-objects row to the trade table.
5. M2 narrowed; L1 floor declared.
6. Re-run the ledger (`--rounds 10-`), the selftest, and the grid on the committed tree. Pre-commit results: ledger byte-identical, selftest 50/50.

Axes: operability has controls unchanged, and the partial-clone trade is the only harm candidate (declared, H2). Coverage has the same trade under the same condition. Freshness, depth, and adjacency touch no surface. Nothing else is harmed in the measured scope.

## 6. Not verified

- Git versions older than 2.56.0 (the L1 floor is untested).
- core.quotePath no-effect is reasoning only.
- `info/grafts`, `.git/shallow`, and sha256 object formats are not fixtured by me. The candidate refuses them, and the real repos pass its checks.
- The 31 L1 run directories are not re-run or adjudicated.
- The current ledger and selftest results bind the pre-commit working-tree bytes (`79d9e124…`), not a commit.
- Contract note: I ran the auditor, read-only (`--rounds 10- --json`, both arms), against the real lane and fleet repos. No fault fixture ran there. A strict reading would treat the ledger row as a normal audit run; flagged for the lead.
- D4 security adequacy beyond the enumerated exec channels: not assessed.

## 7. Files and commands

- Wrote: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/RevCalibrationAxis.md` (this report).
- Scratch under `/tmp` only: `/tmp/kama-r23/RevCalibrationAxis/` (`frozen-audit.py`, `current-audit.py`, `fx/`, `fx2/`) and the probe run directories `/tmp/kama-r23-probe/run.bc4O` (frozen) and `run.1aRD` (current), both created by `probe.sh`.
- Read-only on lane and fleet: `git show`, `rev-parse`, `for-each-ref`, `config --get`, `config --list --name-only`, `ls-tree`; the auditor with `--rounds 10- --json` (both arms) and `--selftest` (both arms).
- Installed: nothing.
