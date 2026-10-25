# CriticC1Rewrite

Axis: calibration. Attacked object: `tools/round35-statement-audit.py` as the C1 kill "a rewritten r34 report must not pass." The fleet report was not edited. The predicate was not retargeted.

## Pin

Confirmed. `git -C /home/vgpnk/Projects/shokunin rev-parse 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` printed `7610d532696f5c6e214840fa2ec4112584589252`. `git cat-file -t` on that id printed `blob`. Same id is `REPORT_BLOB` at `tools/round35-statement-audit.py:34`. `16cf603211cd08240e640ef72969d8eddb1410bd` is an ancestor of fleet `HEAD` `0df83da5164cf40c4eb9d7e6deb9e617b1545217`. Working-tree `git hash-object` of `.ufo/reports/round-34/kama.md` is the same id (16816 bytes, 0 CR). `git replace -l` is empty; no `refs/replace`; no `info/grafts`. Live fleet is not currently rewritten.

## Which check fails when the fleet report blob changes

The check that fails is `report_unchanged`, not the four row-token checks.

`facts()` sets it at line 90:

```
"report_unchanged": git_blob(FLEET, REPORT_REV, REPORT_PATH) == REPORT_BLOB
```

`git_blob` is `git -C /home/vgpnk/Projects/shokunin rev-parse 16cf603211cd08240e640ef72969d8eddb1410bd:.ufo/reports/round-34/kama.md` (lines 54-63). `audit()` requires it at line 142:

```
met = uncorrected == 0 and false_corrections == 0 and got["report_unchanged"]
```

If that `rev-parse` prints any other id, the tool prints `report_unchanged 0` and `met False` and exits 1, even when every `row_ok` derived flag is still true. A rewrite that keeps the four sentinel substrings (`coverage map gains two entries`, `22 untracked`, `2 lane processes still live`, `dispatch-manifest.json` — each count 1 in the pinned blob) does not fail `row_ok`. Only the oid equality forces `met` false. That is the kill the preregistration names ("a changed r34 report blob keeps met False").

Two adjacent failures are not that check. If the path is missing at that rev, `git_show` raises before the equality runs and `main` exits 2. If the new blob drops a sentinel, `row_ok` also increments `false_corrections` and `uncorrected`. Neither is the blob-identity check.

`--selftest` never flips this conjunct. `controls/c1-selftest.out` (`pass=1`) does not prove the kill.

## Counterexample

A blob `git replace` rewrites the bytes `git show` reads while leaving the tree oid, and therefore `report_unchanged`, at 1. Sentinel-preserving replacement bytes still satisfy every `row_ok` derivation. `met` can stay True. The rewritten report passes.

Scratch repo (not the fleet), same command split the tool uses:

- Working-tree rewrite: `git hash-object` of the file became `3a692d60df6220337001df8494abc3c935f79975`; `git rev-parse <pin>:.ufo/reports/round-34/kama.md` stayed `daba433e091b96a66c4007543f8b775a90542f13`. A dirty worktree is outside the predicate (the blob at the pinned rev did not change). Not the defect.
- Blob replace of `daba433e…` with `36af6348c66f7d0065af0899113f1c3c1eed5930`: `git rev-parse <pin>:path` stayed `daba433e…` (also with `--no-replace-objects`). `git show <pin>:path` and `git cat-file -p <oldblob>` both printed `REPLACED coverage map gains two entries`. `--no-replace-objects show` printed the original first line.
- Commit replace is the opposite: `git rev-parse <pin>:path` followed the replacement and printed `331e745657ee0c36ad5979be284a970500823a32`; `--no-replace-objects rev-parse` stayed on the original blob. That case does fail `report_unchanged`.

So the tool's two readers disagree. Fact re-derivation is `git show` (lines 42-51, 75), which follows a blob replace. The kill is `git rev-parse <rev>:<path>` (line 90), which does not. Under a blob replace that keeps the four sentinels, the counter certifies committed-byte facts it did not read, with `report_unchanged 1`. That breaks the predicate's conjunction (correction iff row + re-derived committed-byte fact + unchanged blob) without changing `16cf603…` or the on-disk report. It is false provenance, not a score tradeoff.

Do not "fix" it by passing only `--no-replace-objects`. That would hide the commit-replace case, which today correctly moves the `rev-parse` oid and fails the kill.

## Impacted axis

Calibration only (C1). Coverage, adjacency, and the frozen predicate text are untouched. `MISSION.md:29` still says operability + freshness; this seat does not touch axis authority.

## Smallest safe correction

In `facts()`, set `report_unchanged` only when both are true: the existing `rev-parse` oid equals `7610d532696f5c6e214840fa2ec4112584589252`, and `git hash-object --stdin` of the raw `git show` stdout used for the sentinel checks equals that same id. Hash raw bytes, not `text=True` stdout. Do not change `REPORT_BLOB`, the predicate, or the fleet report. Do not treat a working-tree edit, or a later commit that leaves `16cf603…:path` on `7610d532…`, as a blob change. Re-run the pin command after the conjunction change; it must still print `7610d532696f5c6e214840fa2ec4112584589252`.
