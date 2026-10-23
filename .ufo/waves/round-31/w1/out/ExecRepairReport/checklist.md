# Round-30 report-commit and digest checklist

Advisory repair evidence only; no claim is served. Checked `.ufo/reports/round-30/kama.md` against round-30 lane tip `043ba425b20ff846bdec17e35273feb2c7df6065`, the tip named by `corpus/lessons/round-30-verifier-spotcheck.md`. The scratch clone itself was checked out at the task-frozen `0e6f8ed6891c09d5208ac1fdcb294ed9a842832e`; all Git commands below target that clone, never the lane worktree.

## 1. Enumerate round commits; Landed-changes rule

For a round, take the freeze/start commit and the round-end lane tip from its records, then list the complete commit range with:

```sh
git -C /tmp/r31w1-ExecRepairReport log --format='%H %cI %s' 52ac3af8614b5040ba5e17f17a2c7af029706e6c..043ba425b20ff846bdec17e35273feb2c7df6065
```

**Rule:** the report's `## Landed changes` table must name every commit in this command's output, by a resolvable commit token. Run the range command again at report finalization if another round commit lands; the table must include it too.

Observed output (exit 0):

```text
043ba425b20ff846bdec17e35273feb2c7df6065 2026-10-23T17:16:02-03:00 round-30: lesson calibration note from the CtlEditInPlace arm (what carries the append-only rejection)
f41dce3712e049714cc6a50e8b7defbb03738859 2026-10-23T17:13:51-03:00 round-30: late control evidence (CtlEditInPlace, CtlTamper, CtlDoNothing, CtlBaseTree variants) and wave registry; summary correction
d0e8c4c4647b590772341504f7f189c19d1f18fb 2026-10-23T17:13:13-03:00 round-30: final C1 receipt at 026eede9 (fresh clone, met True), census end, control corrections and seat findings
026eede9f46abd4eeea204eb4262bbbb31a4facb 2026-10-23T17:09:59-03:00 round-30: SCORECARD round-30 section (C1 measured row, C2 capability row, planned), lesson with seat findings
4d498001b1f9c7f1af0903aebdaa9d9a8f7282c6 2026-10-23T17:07:30-03:00 round-30: C1 data (two SA30 correction rows over the recall population); S178/S179, KQ40, knowledge entry, README/PROVINCE, C2 receipts, LOG
14bb1a322f5d487d91f00051ae41bf68d20d8154 2026-10-23T17:06:00-03:00 round-30: pre-data control call receipts (14 arms; no shortcut meets; reference policy green) before any correction row
1d3e8ba4d421672e49003695d9ebe0f6d3caf0ad 2026-10-23T17:00:51-03:00 round-30: C2 instrument (run-agreement tool + selftest + first receipt), wave spec/taskCall and control-call items
fdf8cda19c0719f57e0c2af27e838b42304b0f56 2026-10-23T16:53:58-03:00 round-30: C1 freeze (calibration): recall-population counter, preregistration, base receipt, census start; before any seat
```

The report table (`kama.md` lines 59–64) lists six; it omits `f41dce3712e049714cc6a50e8b7defbb03738859` and `043ba425b20ff846bdec17e35273feb2c7df6065`. Thus this historical report does not meet the every-round-commit rule.

## 2. Resolve report commit tokens and prove ancestry

Extract distinct 7–40-hex tokens from the report, classify with `git cat-file -t`, and for every token of type `commit`, require `git merge-base --is-ancestor <token> <lane-tip>` to succeed:

```sh
set -o pipefail; repo=/tmp/r31w1-ExecRepairReport; report=/home/vgpnk/Projects/shokunin/.ufo/reports/round-30/kama.md; tip=043ba425b20ff846bdec17e35273feb2c7df6065; python3 -c 'import re,sys; text=open(sys.argv[1],encoding="utf-8").read(); print("\n".join(dict.fromkeys(re.findall(r"(?<![0-9a-fA-F])[0-9a-fA-F]{7,40}(?![0-9a-fA-F])",text))))' "$report" | while IFS= read -r h; do kind=$(git -C "$repo" cat-file -t "$h" 2>/dev/null) || kind=absent; if [ "$kind" = commit ]; then if git -C "$repo" merge-base --is-ancestor "$h" "$tip"; then printf '%s commit ancestor\n' "$h"; else printf '%s commit NOT-ANCESTOR\n' "$h"; exit 1; fi; else printf '%s %s non-commit\n' "$h" "$kind"; fi; done
```

Observed output (exit 0):

```text
2aa46e24 commit ancestor
fdf8cda1 commit ancestor
026eede9 commit ancestor
c3f16ef1 absent non-commit
14bb1a32 commit ancestor
4d498001 commit ancestor
4a6f7c911e absent non-commit
ea72c3ea commit ancestor
422b431349 absent non-commit
92b14625 commit ancestor
026eede9f46a commit ancestor
1d3e8ba4 commit ancestor
24ce96bc3905 absent non-commit
52ac3af commit ancestor
db4c39bbbdfd absent non-commit
40b122d commit ancestor
6de225c2 commit ancestor
227dd1ee commit ancestor
d0e8c4c4 commit ancestor
026eede9f46abd4eeea204eb4262bbbb31a4facb commit ancestor
```

All 15 extracted commit tokens resolve as commits and are ancestors of the round-30 lane tip. The five absent tokens are digest/SCORECARD statement-id material, not commit citations. This checks cited-token resolvability/ancestry, not completeness of the Landed-changes table (checked separately above).

## 3. Compare completion time with lane-tip committer time

**Rule:** a round completion digest's completion time must be no later than the committer time of that round's lane tip. The closure record quotes the completion as `2026-10-24T~00:25Z`; for numeric comparison below, `~00:25Z` is represented as `2026-10-24T00:25:00Z` (an approximate value, not a more precise claim).

```sh
repo=/tmp/r31w1-ExecRepairReport; tip=043ba425b20ff846bdec17e35273feb2c7df6065; completion=2026-10-24T00:25:00Z; tip_time=$(git -C "$repo" show -s --format=%cI "$tip"); completion_epoch=$(date -u -d "$completion" +%s) && tip_epoch=$(date -u -d "$tip_time" +%s) && printf 'completion=2026-10-24T~00:25Z (compared as %s)\ntip_committer=%s\n' "$completion" "$tip_time" && if [ "$completion_epoch" -le "$tip_epoch" ]; then printf 'result=not-postdated\n'; else printf 'result=POSTDATES\n'; fi
```

Observed output (exit 0):

```text
completion=2026-10-24T~00:25Z (compared as 2026-10-24T00:25:00Z)
tip_committer=2026-10-23T17:16:02-03:00
result=POSTDATES
```

This reproduces the date defect against the historical round-30 tip. The approximate completion timestamp is still over four hours later than the tip's committer time; do not present it as a valid completion timestamp.