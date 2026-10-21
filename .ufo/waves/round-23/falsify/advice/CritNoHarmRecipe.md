# CritNoHarmRecipe: attack on the round-23 no-harm evidence and recipe

Seat: CloseKama22.CritNoHarmRecipe-2 (critic, leaf). Date 2026-10-21. git 2.56.0, Python 3.14.8.
Base: clone `/tmp/kama-r23w2/CritNoHarmRecipe`. `git rev-parse HEAD` returned `245a37f69628c2c6bb29bbf17897d8fb5946c857`, and the clone stayed clean.
Arms:
- **frozen** = blob `4fe9339f:tools/report-landing-audit.py`, sha256 `09ecd63b…3b3f`.
- **current** = committed `245a37f:tools/report-landing-audit.py`, sha256 `f228f174…a7`.
- The frozen-clone runs used a second clone of my own at `4fe9339f`. It has since been removed.

## Verdict: partially holds

**Holds, for the code at 245a37f.** The claimed no-harm results reproduce exactly in my clone. Frozen and current are byte-identical on every audit run over real history, whenever the fleet repo is uncontaminated.

**Falsified, for the recipe as evidence.** The draft `.ufo/waves/round-23/recipe.json` is untracked in the lane. Its no-harm lines are judged on exit code only, and none of them compares the two arms.
- **R2 (measured):** a verdict-changing mutant passes every audit-touching line in the draft. It makes round 22's landed commits stop being required, so required commits drop from 54 to 49. That mutant gets selftest 50/50, ledger exit 0, raw exit 1, grid current 26/26 with 8/8, and witness red-green-match.
- **R1 (measured):** the draft's history lines read the live, mutable fleet. In my run of the draft lines they flipped to exit 2 because the fleet had been contaminated meanwhile.

## 1. Reruns, frozen vs current (measured)

All commands are `python3 <arm>/tools/report-landing-audit.py … --json`, with explicit `--lane-repo` and `--fleet-repo /home/vgpnk/Projects/shokunin`. Fleet HEAD was `7235b8dd` at 15:47Z and had moved to `879df5ee` by 15:59Z.

| run | lane = my clone | lane = real lane checkout | frozen vs current stdout/stderr |
|---|---|---|---|
| `--selftest` | 0 / 0, `selftest cases=50 failed=0`, sha256 `91c3a6c9…` | n/a | identical, including case names |
| ledger `--rounds 10-21` | 0 / 0 | 0 / 0 | identical; `853d7fca…` equals round-22 receipt `80a6d07c` `audit-historical-ledger` |
| raw `--rounds 10-21 --no-errata` | 1 / 1 | 1 / 1 | identical; `110e1804…` equals receipt `audit-historical-raw` |
| ledger `--rounds 10-22` | 0 / 0 | 0 / 0 | identical; `1ae84922…`; 13 reports, 9/9 corrected, 54 required, 5 post-report |
| raw `--rounds 10-22 --no-errata` | 1 / 1 | 1 / 1 | identical; `13b17b1c…`; 9 uncorrected |
| default `--rounds 10-` (JSON and text) | 0/0; raw 1/1 | 0/0; raw 1/1 | identical; still 13 reports (no round-23 report yet) |

Counts for 10-22: defects by kind are `landed-omitted=8` and `unresolved-full-hash=1`.

I also ran the union of the round-22 recipe, the round-22 report-source-fix recipe and the round-23 draft: 41 distinct argv. Each arm ran via `.ufo/waves/round-22/run.py` in its own clean clone. Receipts: `out/CritNoHarmRecipe/union-{current,frozen}-commands.json`.
- **Round-22 lines:** all 34 meet their expected exit in both arms.
  - 20 are byte-identical across arms. These include install-io selftest, frozen, current and both (`31c9abb0…`, `d4ae3c8d…`, `87062895…`, `ba7081af…`). Install-io, the c2 grids, error-census, gguf selftest, citation selftest, snapshot and unpinnable all equal their round-22 receipt shas.
  - The rest differ only by clone path, ephemeral ports (producer selftest), or the allowed appended rows `added S089..S095 (allowed)` (append-only lines). The witness differs only in `candidate_sha256` (`09ecd63b…` vs `f228f174…`).
  - Citation is identical after path normalization: required, found and verified are all 17, with 0 missing, mismatched or off-ref.
- **Round-23 draft lines, current arm:**
  - Grid frozen 1, current 0, both 1.
  - Mutants exit 0: 22 of 24 killed, survivors `M02-lazy-fetch` and `M20-log-sha-shape`. All 22 kills are `grid_exit=1` fault-row kills.
  - `audit-historical-ledger` and `audit-historical-raw` returned **exit 2** (see R1).

## 2. Counterexamples

### R1: the history lines measure live fleet state, not the code (measured)
- In my union run, the round-22 history lines at 15:48:47Z passed. The round-23 draft lines at 15:53:54Z returned exit 2: `could-not-evaluate: /home/vgpnk/Projects/shokunin: partial clone (promisor pack)`.
- Over the same fleet, frozen returned exit 0 with `1ae84922…`.
- Cause: zero-byte `*.promisor` markers appeared in the fleet's `.git/objects/pack`. There were three on the real packs plus `pack-deadbeef.promisor`, created at 12:50:16 -0300. They were absent at 15:55:52Z and **re-created at 12:58:00 -0300**, then absent again at 16:00:14Z.
- At 15:58:39Z the lane's uncommitted WIP auditor (blob `62629d2d`, sha256 `3fc567ab…`) also refused all four history runs. Its tightened check, which requires a matching `.pack`, still fires because the markers sit on real packs.
- I did not write them: my clone is under `/tmp`, and every grid or mutant fixture uses `tempfile` with an explicit temp `--fleet-repo`. I did not find the writer. CritAxisScore reported the first occurrence; I messaged CloseKama22 about the recurrence. The lane's `falsify/fleet-contamination/` holds copies of both sets.
- **Impact:** the draft recipe cannot tell code harm from environment. A run that lands inside a contamination window fails, and a clean window passes, whatever the code does.
- Operability and calibration are affected.

### R2: exit-only judging cannot detect a verdict regression (measured)
- Mutant (`out/CritNoHarmRecipe/mutant-round22-blind.diff`, sha256 `a64e1c39…`): at `tools/report-landing-audit.py:198`, `… and pat.match(subject)` gains `and not subject.startswith("round-22")`.
- What it produced:
  - 10-22 ledger: exit 0 with required 49 (was 54), sha `0924a3d5…` (pinned `1ae84922…`).
  - 10-22 raw: exit 1, sha `cd0a7302…` (pinned `13b17b1c…`).
  - 10-21 ledger and raw: unchanged, `853d7fca…` and `110e1804…`. The 10-21 pins cannot see it.
  - `--selftest` 50/0.
  - Grid `--arm current --current <mutant>`: exit 0, faults 26/26, controls 8/8, 0 executed.
  - `red-green-witness.py --candidate <mutant>`: exit 0, `red-green-match`.
- Every audit-touching draft line therefore passes. The other draft lines (citation, install-io, sources) do not read the audit.
- `run.py` sets `as_expected = code == expected_exit` only. It records `stdout_sha256`, but nothing compares it.
- Calibration is affected: the no-harm claim is unfalsifiable by the recipe as written.

### R3: the draft drops round-22 no-harm lines it still has coverage for (measured)
The draft keeps citation `--json`, the witness and its selftest, `io-current`, sources validate and census, and append-only from `4fe9339f`. It drops the following lines, which pass today and are pinned by the round-22 receipts:
- citation `--selftest` (`63600acd…`)
- install-io `--selftest` (`31c9abb0…`), `--arm frozen` (exit 1, `d4ae3c8d…`) and `--arm both` (exit 1, `ba7081af…`)
- the 10-21 ledger and raw lines (`853d7fca…` and `110e1804…`, which equal receipt `80a6d07c`)
- long-range append-only from `10271460` to `{revision}`

They cost about 6 s in total. I found no causal path from the round-23 diff to install-io, citation or the census tool:
- `git diff 4fe9339f 245a37f --stat` touches only the audit, `tests/report-audit/*`, `corpus/SOURCES.md`, the lesson file and `.ufo` files.
- `error-verdict-census.py` pins its own sources (`:30-36`) and never references the audit.

Including them anyway keeps the whole-tree recipe comparable to round 22.

### R4: what the official run measures (measured)
- `run.py` refuses a dirty tree. The real lane currently shows 10 porcelain entries:
  - modified: `SKILL.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/knowledge/error-is-not-a-verdict.md`, `tools/report-landing-audit.py` (+62/-?) and `tests/report-audit/repo-state-grid.py` (+105)
  - untracked: `.ufo/waves/round-23/{build,falsify,recipe.json}`. These are not ignored: `git check-ignore` exits 1.
- So every result above is evidence for `245a37f` only. The integrated commit needs a full rerun.
- On the WIP blob I could measure only that `--selftest` is byte-identical (`91c3a6c9…`) and that the witness passes. Its history parity was unmeasurable at that moment because of contamination.

### R5: the mutant line counts environment errors as kills (from a peer, consistent with my data)
- ExecRecipeDryRun reports 23 killed, with M20 "killed" via ENOSPC (`unable to write new index file`, grid exit 2). `isolation-mutants.py` counts a grid that cannot evaluate as a kill.
- My run, before the disk filled, had 22 kills, all `grid_exit=1`.
- During this seat `/tmp` (`/dev/nvme0n1p1`, 128G) was 100% full at about 15:57Z. My frozen witness then returned exit 2 for that reason alone; rerun at 16:00Z it returned exit 0 `red-green-match`.
- The judge must not accept the mutants line on exit code alone.

## 3. Smallest safe correction: lines the final recipe must include

All lines below are in `out/CritNoHarmRecipe/proposed-noharm-lines.json` (17 lines) and `proposed-parity-line.json` (1 line). In my clean clone, `run.py` ran all 18 and every exit matched: rc 0, 6 s plus 8 s. Receipts: `proposed-commands.json` and `parity-commands.json`.

1. **`nh-history-parity` (required; fixes R2).** One `python3 -c` command runs current and the frozen `4fe9339f` blob over 10-21 and 10-22, each with and without errata. It exits 1 on any exit, stdout or stderr difference.
   - Exit 0 on `245a37f`.
   - **Exit 1 on the round-22-blind mutant** (10-22 both modes DIFF).
   - It also fails closed under contamination, because current refuses while frozen does not.
2. **`nh-fleet-clean-pre`, `nh-lane-clean-pre` and `nh-fleet-clean-post` (fixes R1 attribution).** A `python3 -c` probe exits 1 if the repo has any `objects/pack/*.promisor`, `refs/replace/*`, `info/grafts`, `shallow`, `objects/info/alternates`, `*.promisor` config, or `extensions.partialclone`.
   - Fleet and lane both returned `clean`, exit 0, at 16:01:39Z.
   - On a fixture repo holding a zero-byte `pack-deadbeef.promisor` it returned exit 1.
   - Bracket the history lines with it, so a failure can be attributed to code or to environment.
3. **Snapshot arms, for a contamination-proof code comparison.** `git clone -q --bare --no-local file:///home/vgpnk/Projects/shokunin {out}/fleet.git` (11M, 0 markers) is followed by current and frozen ledger (exit 0) and raw (exit 1) against it.
   - Current and frozen are byte-identical: `1fa97547…` and `7cf28de4…`.
   - After path normalization they equal `1ae84922…` and `13b17b1c…`.
   - Keep the live-fleet lines as well. They measure operability on the real population; the snapshot measures code.
4. **Inline frozen arm on the live fleet:** `nh-frozen-ledger-10-22` (exit 0, `1ae84922…`) and `nh-frozen-raw-10-22` (exit 1, `13b17b1c…`). This gives the judge a frozen stdout sha recorded in the same run.
5. **Restore the dropped round-22 lines (R3):** `nh-audit-ledger-10-21` and `nh-audit-raw-10-21`, `nh-citation-selftest`, `nh-io-selftest`, `nh-io-frozen`, `nh-io-both`, and `nh-sources-append-only-long`.
6. **Judge rules not expressible in `run.py`:**
   - require `stdout_sha256` pins: 10-21 `853d7fca…`/`110e1804…`, frozen 10-22 `1ae84922…`/`13b17b1c…`, citation selftest `63600acd…`, and the install-io pins above
   - require the mutants JSON to have `surviving == ["M02-lazy-fetch","M20-log-sha-shape"]` and every kill `grid_exit == 1` (R5)
   - require the selftest case-name set to be a superset of the frozen 50, compared by name, not count
   - run on the integrated commit with a clean tree (R4)

Witness and citation are needed as no-harm lines but are not discriminating. Both pass on frozen, current, WIP and the mutant. Only item 1 discriminates on real history.

## Not verified
- Who writes the fleet markers, or whether they recur after 16:03Z.
- History parity of the lane WIP blob `62629d2d`, and the integrated commit generally.
- Old git (< 2.45), other Python versions, and non-UTF-8 locales.
- `sources-validate`/`sources-census` read the real lane worktree via `--root /home/vgpnk/Projects/shokunin kama`, not `{lane}`. In my clone runs they therefore measured the real lane: exit 0 in both arms, byte-identical. That is not a clone measurement.
- Whether the snapshot arm stays marker-free under a contaminated fleet. It ran between 15:58:46Z (markers present) and 16:00:14Z (absent); the live state at that instant was not captured. A `file://` clone builds a fresh pack and copies no `.promisor` files `[INFERENCE from git transport behavior; not re-measured under contamination]`.
- The full 41-line union on the mutant. I ran only the selftest, history, grid current and witness lines.

## Installs
None.

## Files written
- `.ufo/waves/round-23/falsify/advice/CritNoHarmRecipe.md` (this report)
- `.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/proposed-noharm-lines.json`
- `.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/proposed-parity-line.json`
- `.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/proposed-commands.json` and `parity-commands.json` (run.py receipts)
- `.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/union-recipe.json`, `union-current-commands.json` and `union-frozen-commands.json`
- `.ufo/waves/round-23/falsify/out/CritNoHarmRecipe/mutant-round22-blind.diff`
- Scratch: `/tmp/kama-r23w2/CritNoHarmRecipe` (clone, clean) and `/tmp/kama-r23w2/CritNoHarmRecipe-probe/` (outputs, mutant copy, pinned WIP copy). The second clone `/tmp/kama-r23w2/CritNoHarmRecipe-frozen` and the snapshot repos were removed.
- Peer messages: two to `agent://CloseKama22` (disk-full and marker-recurrence blockers).

## Correction (appended)
- R4's line-count annotations: `git diff --stat` on the real lane reported `tools/report-landing-audit.py | 62` (mixed +/-), not "+62/-?". It reported `tests/report-audit/repo-state-grid.py | 105` (mostly +). Across 7 files the totals were 226 insertions and 37 deletions.

I made no commits or pushes, ran no jj commands, and wrote nothing to tracked lane files, the lane index or the fleet. The real lane and fleet were only read, by audit, citation and census runs and read-only git (`rev-parse`, `status`, `config --list`, `for-each-ref`, `cat-file`, `hash-object` without `-w`, `check-ignore`).
