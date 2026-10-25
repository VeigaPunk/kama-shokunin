# ExecClaimAuditControl — do-nothing control of the frozen C1 counter at the r32 base

## Verdict

**Control passes (one-sided floor).** At the pre-correction r32 base
`cc46980359278d0967cf65e785b41c27b8d9c36c` the frozen counter credits **no** corrections
that were never written:

```
valid_corrections=0 unresolved=3 met=False   exit code 1   stderr empty
```

with `false_at_writing=3`, i.e. the three routed false round-32 references are still
counted false at the base, and nothing is resolved there.

This control forbids a false positive at the base. It does **not** prove the counter can
credit a real correction; that sensitivity side is the corrected-tip receipt owned by
another seat. Do not cite this report as the 0→3 measurement.

## Instrument and pins

| item | value |
|---|---|
| instrument | `tools/round33-claim-audit.py` |
| blob | `3f1cbe5893689620c85bad9316c9a729ea31bb3c` (same blob at freeze `4fdd4e663ba8d3353b5cd431c2d21373d930a6c5` and lane tip `7c35289da5f4b94e062cd900eb086919e5094003`; `git hash-object` of the worktree file equals it) |
| sha256 (worktree file) | `e98d8c0ca5e118bc7a82e6d5ce3d2197c24c46c984fbf9a8816b29a9a6df10c5` |
| statement revision | `dc4258bdb08d658f1c5b15abc8378461659bd155` — tree `5c8fe6a3e18695715a5d03f44e909838335c3bf0` |
| evaluated (base) revision | `cc46980359278d0967cf65e785b41c27b8d9c36c` — tree `cd96f037cdcf6426ffc419aabb95ccc34c848604` |
| lane tip (reference only, not run) | `7c35289da5f4b94e062cd900eb086919e5094003` |
| ancestry | statement → base → tip all `merge-base --is-ancestor` rc=0 |
| runtime | Python 3.14.8, git 2.56.0; no tool installed or upgraded |

## Exact command, preserved stdout and exit code

Isolated repository copy (object-only, see below), cwd = copy root:

```
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/round33-claim-audit.py \
  --repo /tmp/execclaim-audit-control.sfOIXQ \
  --statement-rev dc4258bdb08d658f1c5b15abc8378461659bd155 \
  --tip cc46980359278d0967cf65e785b41c27b8d9c36c
```

stdout, verbatim (204 bytes, 1 line):

```
R33_CLAIM_AUDIT statement_rev=dc4258bdb08d658f1c5b15abc8378461659bd155 tip=cc46980359278d0967cf65e785b41c27b8d9c36c false_at_writing=3 valid_corrections=0 unresolved=3 legacy_mislabels_at_tip=3 met=False
```

- exit code: **1**
- stderr: **0 bytes**
- `sha256(stdout)` = `4c973856338ed3133f98715da8bd3e4579ba5c92ef4999b7e9ca98fb44cbfdf0`

Second invocation, declared shape (`--repo .`, cwd = copy root, same pins): stdout
byte-identical (`cmp` clean, same sha256), exit **1**, stderr 0 bytes. Two runs, same bytes.

## Isolation and non-mutation

- Isolation method: `cp -a <lane>/.git /tmp/execclaim-audit-control.sfOIXQ/.git` (44 MB),
  then the counter was executed against that copy. The counter opens only Git objects
  (`git rev-parse --verify`, `git show <rev>:<path>`) and reads no worktree file, so no
  working tree was needed. Both pinned revisions resolve in the copy before the run.
- No `git worktree add`, no checkout, no commit/stash/reset, no jj command, no index touch,
  no lane file edited. Only read-only git verbs were used (`rev-parse`, `show`, `cat-file`,
  `merge-base`, `hash-object`, `log`, `ls-files`, `status`). Lane `HEAD` unchanged at
  `7c35289da5f4b94e062cd900eb086919e5094003` throughout.
- Lane `git status --porcelain` taken before the write shows peer/orchestrator artefacts only
  (modified `swarm-registry.json`, other seats' untracked `*.md`/`*-evidence/`); none written
  here.
- Post-run byte check of every path this control reads: worktree `git hash-object` equals the
  lane-tip blob for `SCORECARD.md` (`f3656416…`), `tools/round33-claim-audit.py`
  (`3f1cbe58…`), and all six r32 control receipts (`0dc6fc95…` ×3, `199da61b…`, `9c8597a5…`,
  `17614c68…`). Instrument and fixture bytes are untouched.
- Note: a later re-run of `git status` failed with `fatal: unable to create threaded lstat:
  Resource temporarily unavailable` (host thread/fork exhaustion under the live fleet). That
  failure is recorded as measured unavailability; the hash comparison above, not status,
  carries the non-mutation evidence.

## Pinned input facts

| fact | measurement |
|---|---|
| `SCORECARD.md` blob at statement and at base | `639f2f508074ba9f8dfef954a3350822aa2fe35b`, 142 703 bytes — **identical at both revisions** |
| correction heading `### Round 33 — correction of round-32 gate-control receipt references` | 0 occurrences at statement, **0 at base**, 1 at lane tip (line 1835) |
| statement C2 row gates | contains `c2/controls/*-v2.out` (1) and `each fixture exits 1` (1), so the row-lookup guard passes |
| old receipts `thin-row-v2.out`, `empty-exit-v2.out`, `nonexistent-path-v2.out` at statement and base | all one blob `0dc6fc95f472af45219ce5e9ace45d0b958eb973`, 136 bytes, base-tree output (`registered 7 unregistered 2 defective 0`); none carries an expected `defective …` line — hence `false_at_writing=3` |
| corrected receipts at base | `thin-v2.out` `199da61b…` 205 B, `noexit-v2.out` `9c8597a5…` 98 B, `badpath-v2.out` `17614c68…` 131 B — present, with the exact expected lines |
| `legacy_mislabels_at_tip=3` | the same stale 136-byte blob still sits at all three old paths at the base tip |

## Falsification checks

1. **Not an error path.** Exit is 1 with the audit line printed, not 2 with
   `R33_CLAIM_AUDIT_ERROR`; the revision/row/receipt-existence guards all passed.
2. **`false_at_writing=3` is content-driven, not a missing-blob artefact.** All three old
   receipts exist at the statement revision (blob `0dc6fc9…`), so the counter took the
   "expected line absent" branch each time.
3. **`valid_corrections=0` is undeclared-correction-driven, not file-absence-driven.**
   `correction_rows` is empty at base (heading absent), so no row can be validated; the
   correct-path receipts that already exist at base receive no credit. The counter grades
   the declared row **and** its cited receipt, so a do-nothing state cannot be scored as a
   correction. This is the property the control exists to test.
4. **Determinism.** Two independent invocations (absolute path and `--repo .`) produced
   byte-identical 204-byte stdout, exit 1, empty stderr.

## Boundary

One-sided control. A counter hard-wired to `met=False` would also pass this run; the
sensitivity direction requires the landed-tip receipt from the seat that owns C1's 0→3
measurement. The declared-base tip used here is the r32 base, so
`legacy_mislabels_at_tip=3` describes the base, not the corrected lane tip. Synthetic r32
fixtures only — no service, endpoint-readiness, model-quality or consumer-health claim.
The `/tmp` copy and run artefacts are ephemeral; the verbatim stdout and its sha256 above
are the preserved evidence.

## Files changed by this seat

- `.ufo/waves/round-33/w1/out/ExecClaimAuditControl.md` (this report) — only write.

An untracked prior draft of this same path (6782 bytes, mtime 04:45) reported the same
numbers from a different object copy; this freshly measured version supersedes it.

## Blockers / confidence

No blockers. Confidence: high — deterministic two-run result, byte-pinned revisions,
blobs and instrument, verbatim stdout with sha256, and no lane writes.
