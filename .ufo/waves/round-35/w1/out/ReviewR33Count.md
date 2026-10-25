# ReviewR33Count

Seat: ReviewR33Count. Read-only recount. No files deleted. No git index change. No fleet-report write.

## Verdict

Recommendation: the spot-check sentences hold. `git status --porcelain` under `.ufo/waves/round-33` is 23 untracked paths and 1 modified path. The r34 fleet report's bare count of 22 does not match that command.

## Count command and output

Working tree: `/home/vgpnk/Projects/shokunin/kama-shokunin`. `HEAD` `719655f12517a9ce6b1a5ca44316897fed8420b0`. `git` 2.56.0. `status.showUntrackedFiles` unset, so porcelain uses the default `--untracked-files=normal` (one line per untracked directory, not per file inside it).

```
git status --porcelain -- .ufo/waves/round-33
```

```
 M .ufo/waves/round-33/w1/out/swarm-registry.json
?? .ufo/waves/round-33/w1/out/ConnInstrumentReuse.md
?? .ufo/waves/round-33/w1/out/ConnSiblingScope.md
?? .ufo/waves/round-33/w1/out/CriticC1Overreach.md
?? .ufo/waves/round-33/w1/out/ExecClaimAuditControl.md
?? .ufo/waves/round-33/w1/out/ExecGateReplay-evidence/
?? .ufo/waves/round-33/w1/out/ExecReceiptMutants-evidence/
?? .ufo/waves/round-33/w1/out/ExecReceiptMutants.md
?? .ufo/waves/round-33/w1/out/ExecS193Quote.md
?? .ufo/waves/round-33/w1/out/MutMissingCorrection-evidence/
?? .ufo/waves/round-33/w1/out/MutMissingCorrection.md
?? .ufo/waves/round-33/w1/out/MutReceiptExit-evidence-3/
?? .ufo/waves/round-33/w1/out/MutReceiptExit-evidence/
?? .ufo/waves/round-33/w1/out/MutReceiptExit.md
?? .ufo/waves/round-33/w1/out/MutReceiptOutput.md
?? .ufo/waves/round-33/w1/out/MutReceiptRevision-evidence/
?? .ufo/waves/round-33/w1/out/MutWrongCorrectionPath-evidence/
?? .ufo/waves/round-33/w1/out/MutWrongCorrectionPath.md
?? .ufo/waves/round-33/w1/out/ReviewerC2Reproduction-evidence/
?? .ufo/waves/round-33/w1/out/ScoutReceiptNames.md
?? .ufo/waves/round-33/w1/out/ScoutReportLineage.md
?? .ufo/waves/round-33/w1/out/ScoutS193Source.md
?? .ufo/waves/round-33/w1/out/ScribeLineageErratum.md
?? .ufo/waves/round-33/w1/out/ScribeS193Correction.md
```

Tally of that same output:

```
git status --porcelain -- .ufo/waves/round-33 | awk 'BEGIN{u=0;m=0;o=0} /^\?\?/ {u++} /^ M/ {m++} !/^(\?\?| M)/ {o++} END {print "untracked", u; print "modified", m; print "other", o; print "lines", u+m+o}'
```

```
untracked 23
modified 1
other 0
lines 24
```

NUL recount of the same pathspec: 24 records. Codes: 23 `??`, 1 ` M`. No quoted paths. No ignored paths (`git status --porcelain --ignored` under the same pathspec: 0 `!!`). Narrowing the pathspec to `.ufo/waves/round-33/w1/out` does not change the tally. The only tracked path under that `out/` directory is `swarm-registry.json` (`git ls-files` count 1). `git diff --numstat` for it is `34 34` (content change, not a mode-only or empty diff). Index is clean for that path (` M`, not `M ` or `MM`).

Modified path:

```
 M .ufo/waves/round-33/w1/out/swarm-registry.json
```

## Comparison

Spot-check sentence (`corpus/lessons/round-34-verifier-spotcheck.md:95`):

> Report says 22 untracked round-33 outputs; porcelain shows 23 untracked plus 1 modified registry.

Spot-check sentence (`corpus/lessons/round-34-verifier-spotcheck.md:82`):

> 24 round-33 leftovers: `M .ufo/waves/round-33/w1/out/swarm-registry.json` plus 23 untracked outputs. Inherited, named in the report (the report says 22 untracked; this count is 23).

| claim | number | this recount |
| --- | --- | --- |
| spot-check '23 untracked' | 23 | match (`??` lines) |
| spot-check '1 modified' | 1 | match (` M` line, path above) |
| spot-check '24 round-33 leftovers' | 24 | match (23 + 1) |
| r34 fleet report '22 untracked outputs' | 22 | does not match (short by 1) |

Cited fleet sentence, unchanged blob `/home/vgpnk/Projects/shokunin/.ufo/reports/round-34/kama.md` sha256 `ce9c360374064617b83234ea4ad31825f2e879d3b03c25a4a3e99cb0a20e5890`, mtime 2026-10-24 20:56:05 -0300, lines 114–115:

> and left 22 untracked outputs under `.ufo/waves/round-33/w1/out/`.

All 23 untracked paths and the modified file have filesystem mtimes between 2026-10-24 04:42:46 and 04:47:22 -0300, before that report mtime. The extra path is not explained by a file appearing after the report was written. The report does not record the command that produced 22, so this recount does not name which of the 23 lines was omitted.

## Findings by severity

### High

None.

### Medium

1. The r34 fleet report's round-33 untracked count is off by one against the command it is being checked with. Evidence: `git status --porcelain -- .ufo/waves/round-33` prints 23 `??` lines, all under `.ufo/waves/round-33/w1/out/`; the report says 22. The spot-check already named this (line 95). This recount agrees with the spot-check, not with 22. Recommendation only: do not carry 22 forward as the porcelain count.

### Low

1. Line 82 writes the modified path as `` `M .ufo/waves/round-33/w1/out/swarm-registry.json` ``. The porcelain code is ` M` (leading space, unstaged), not staged `M `. The count '1 modified' is still right. A later grep for `^M ` would miss the only modified path.

### Spot-check count

No defect. '23 untracked' and '1 modified' match this worktree.

## Residual risk and verification gaps

- Unit. Default porcelain collapses untracked directories. Eight of the 23 `??` lines are directories (`ExecGateReplay-evidence/`, `ExecReceiptMutants-evidence/`, `MutMissingCorrection-evidence/`, `MutReceiptExit-evidence/`, `MutReceiptExit-evidence-3/`, `MutReceiptRevision-evidence/`, `MutWrongCorrectionPath-evidence/`, `ReviewerC2Reproduction-evidence/`). `git status --porcelain --untracked-files=all -- .ufo/waves/round-33` is 104 `??` file paths plus the same 1 modified line (105 lines). That is a different unit. It does not falsify 23.
- Omitted-path identity. No saved count from the r34 report. Mtimes make a post-report addition unlikely, but mtime is not a git fact (`touch`, `cp -p`, or a clock step could lie). Not used as the count.
- Whole-tree dirt is not this count. At recount time the repo also had 62 `??` and 2 ` M` overall. The three `??` lines outside round-33 and round-34 were `.ufo/waves/round-35/`, `tools/round35-coverage-audit.py`, and `tools/round35-statement-audit.py`. They are outside the pathspec. Do not derive 23 by subtracting from the whole-tree total. The spot-check's closure total of 59 untracked is a different tree than today's whole tree; the round-33 slice still matches.
- This report path is `.ufo/waves/round-35/w1/out/ReviewR33Count.md`. Writing it does not add a round-33 porcelain line.
- Fleet report blob was read only. sha256 above is the observation, not a rewrite.
- No tools installed. Pacman is paused; none were needed.
