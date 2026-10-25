# ScribeCoverage — round 35 wave 1

Seat: ScribeCoverage. Leaf. No subagent dispatch. Judged on: coverage.
Draft only. This seat did not land C2 and does not claim `met True`.

## Behavior

Drafted a paste-shaped coverage-map section and a separate correction sentence. Did not edit `corpus/README.md`, did not create `corpus/knowledge/endpoint-health-probe-conventions.md`, did not edit `corpus/lessons/round-35.md`, did not rewrite the r34 fleet report, and did not change either frozen predicate. No tools installed. No pacman. No git or jj mutation. No service restoration.

## Gates

C2 counting command, observed once against the frozen base and once against the worktree after the draft existed. Neither run reads `block.md`.

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
named 0 file_exists 0 cited_row 0 met False
exit 1
```

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
named 0 file_exists 0 cited_row 0 met False
exit 1
```

Local check of the draft only (not the counting command, not a tip score): imported `block_names` from `tools/round35-coverage-audit.py` and applied it to `block.md`. Heading present once; the em dash is U+2014; `block_names` = 1; the entry string occurs once in the file and once in the counted body. The correction sentence is after the next `\n## ` and is outside the counted body.

A later paste of only the coverage section into `corpus/README.md` would supply the `named=1` conjunct. It would not supply `file_exists` or `cited_row`. The counter's kill line still applies: a heading with no file keeps `met False`.

C1's counting command was not run. The fleet report blob id below is a `git rev-parse` observation, not a C1 audit result.

## Touched surfaces

- Wrote `.ufo/waves/round-35/w1/out/ScribeCoverage/block.md` (seat draft).
- Wrote `.ufo/waves/round-35/w1/out/ScribeCoverage.md` (this report; assigned trailer path, parent of the seat directory).

`git status --porcelain` scoped to `corpus/README.md`, `corpus/knowledge/endpoint-health-probe-conventions.md`, `corpus/lessons/round-35.md`, and the two output paths, after `block.md` existed and before this report: only `?? .ufo/waves/round-35/w1/out/ScribeCoverage/block.md`. README was clean. Neither output was committed.

## Out of scope

- Editing `corpus/README.md` (forbidden by the seat task).
- Creating or sourcing `corpus/knowledge/endpoint-health-probe-conventions.md`.
- Citing an S-id. This seat did not re-open staged sources. The Covers cell restates the assigned frontier theme; it is not an admission and not evidence the file exists.
- Naming `hosted-health-route-configuration.md` in the coverage block (candidate reject; not this seat's admit).
- C1 correction rows (`R34-MAP` and the other three). Owned by ScribeCorrection. This sentence is not a `| R34-MAP |` row and was not written into `corpus/lessons/round-35.md`.
- Quarantine rows, `considerthese`, sibling repos, fleet report bytes, `MISSION.md`, `shokunin.conf`.
- Axis-authority edits. Conflict named below and not acted on.

## Findings

### Draft

`block.md` contains:

1. Heading exactly `## Coverage map — round 35 addition`.
2. One table row whose Entry cell is `` `knowledge/endpoint-health-probe-conventions.md` ``. That is the only occurrence of `knowledge/endpoint-health-probe-conventions.md` in the file.
3. A following heading `## Correction — r34 coverage-map sentence`, then one sentence: the r34 report's coverage-map sentence is false at 719655f, because `16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` says the coverage map gains two entries (`corpus/knowledge/serving-alias-contract.md`, `corpus/knowledge/served-model-id-resolution.md`), and `719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md` contains neither filename.

The separator heading is so a wholesale append does not fold the correction into the counted coverage body. It is not a second coverage-map block.

### r34 coverage-map sentence, re-derived

Committed fleet blob `16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` is `7610d532696f5c6e214840fa2ec4112584589252` (`git rev-parse`). That matches the blob constant in `tools/round35-statement-audit.py`. This seat did not write that file.

The phrase `coverage map gains two entries` occurs once, at lines 186–188:

```
  coverage map gains two entries on the served-name/alias theme
  (`corpus/knowledge/serving-alias-contract.md`,
  `corpus/knowledge/served-model-id-resolution.md`).
```

At `719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md` (35771 bytes), counts are: `serving-alias-contract.md` 0, `served-model-id-resolution.md` 0, `endpoint-health-probe-conventions.md` 0, `## Coverage map — round 35 addition` 0, `## Coverage map` 5, `## Coverage map — round 34` 0. HEAD is that commit (`719655f round-34 verifier spot-check (integrator, hyaku): non-author admit/reject`).

Those two knowledge files are present in the tree at that commit (`git ls-tree`). `corpus/SOURCES.md` used-by cells name them. The falsity is the coverage-map claim, not file absence. A different report sentence (lines 29–33) says two entries were admitted; this seat did not re-audit that sentence and does not call it false.

`corpus/lessons/round-34-verifier-spotcheck.md:87` already routes the same coverage-map sentence as false because README does not name the two files. That line is corroboration. The counts above were re-derived from `git show` / `git grep` / `git ls-tree`, not copied from the spot-check as the measurement.

### C2 base, observed

None of the three C2 conjuncts hold at `719655f12517a9ce6b1a5ca44316897fed8420b0`: the round-35 coverage heading is absent, `corpus/knowledge/endpoint-health-probe-conventions.md` is absent (`ls-tree` did not list it; worktree `is_file()` is false), and there is therefore no cited S-id in that file. Predicate text was not changed.

### Conflict (verbatim; not acted on)

Preregistration `mission_conflict`:

> MISSION.md:29 still says operability + freshness. shokunin.conf and the round prompt say operability + calibration. MISSION.md was not edited. C1 works calibration because it is the lowest non-retired numeric axis (7, tied with depth and adjacency). The conflict is named and does not change either predicate.

Observed, read-only:

- `/home/vgpnk/Projects/shokunin/MISSION.md:29`: `kama:       { cwd: kama-shokunin/,   axes: "operability + freshness (local model serving/endpoints)" }`
- `/home/vgpnk/Projects/shokunin/shokunin.conf:52`: `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`

This seat did not edit either file and did not change C1 or C2.

## Commands

Read-only git and the counter. Outcomes are in Gates and Findings. Commands that produced the counts:

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse HEAD
git -C /home/vgpnk/Projects/shokunin/kama-shokunin log -1 --oneline 719655f12517a9ce6b1a5ca44316897fed8420b0
git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -n -e serving-alias-contract.md -e served-model-id-resolution.md -e endpoint-health-probe-conventions.md -e 'Coverage map — round 35' 719655f12517a9ce6b1a5ca44316897fed8420b0 -- corpus/README.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only 719655f12517a9ce6b1a5ca44316897fed8420b0 -- corpus/knowledge/serving-alias-contract.md corpus/knowledge/served-model-id-resolution.md corpus/knowledge/endpoint-health-probe-conventions.md
git -C /home/vgpnk/Projects/shokunin rev-parse 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show 719655f12517a9ce6b1a5ca44316897fed8420b0:corpus/README.md | python3 count of the five needles above
git -C /home/vgpnk/Projects/shokunin show 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md | python3 line filter for the map phrase and the two filenames
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 719655f12517a9ce6b1a5ca44316897fed8420b0
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round35-coverage-audit.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin
```

`ls-tree` printed only the two alias/resolution paths. README `git grep` printed no hits. Report blob id `7610d532696f5c6e214840fa2ec4112584589252`.

## Known limits

- `block.md` is a draft. It is not corpus evidence and does not move C2.
- The Covers cell is the assigned theme, not a quote from a re-opened source.
- Worktree status was scoped to the paths listed under Touched surfaces, not a full-tree census.
- The two r34 knowledge files existing at `719655f` is not a finding that the coverage map names them.
- No install. `/home/vgpnk/.omp/agent/RULES.md` was read; nothing in it was required for this draft.

## Artifact paths

- `.ufo/waves/round-35/w1/out/ScribeCoverage/block.md`
- `.ufo/waves/round-35/w1/out/ScribeCoverage.md`
