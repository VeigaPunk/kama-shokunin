# ReviewManifestDiff

Recommendation: **discard** the unstaged working-tree edit of `.ufo/waves/round-34/w1/out/dispatch-manifest.json`. Do not stage it. This review did not stage it and did not revert it.

Judged axis: calibration. C1 and C2 predicates were not retargeted. Axis authority was not edited. `MISSION.md` is not in this lane; `SCORECARD.md:192` and `LOG.md:277` still record `MISSION.md:29` as operability + freshness, which conflicts with this seat being judged on calibration. That conflict is named, not resolved.

## Asked facts

Command run: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff -- .ufo/waves/round-34/w1/out/dispatch-manifest.json`.

HEAD is `719655f12517a9ce6b1a5ca44316897fed8420b0`. The path's blob at HEAD, at `719655f`, and at `b784e1ab273472eaa750fc10918ca4be67fa7697` is the same object: `b32113564fd019bfaa60d14511abd91d080cfe74` (7131 bytes). The index blob is that same object. `git diff --cached` for this path is empty. Status is ` M` (unstaged only). Working-tree sha256 is `88022991d988ade1fcc1622f58a36399e95d2814c29f2a15e59e2fc96fd9d772` (8086 bytes). Numstat: 70 insertions, 36 deletions.

The working tree **does add** the sentence `Cannot combine --prompt with --auto`. Count is 1 in the working tree and 0 in the HEAD blob. The only occurrence is inside the new `note` string, as `'error: Cannot combine --prompt with --auto.'`.

The working tree **drops none** of the 33 seat names. HEAD has 33 unique names; the working tree has the same 33 in the same order. `name`, `role`, `pid`, `report`, and `log` are unchanged on all 33. Role mix is unchanged (scout 6, executor 5, reviewer 4, critic 4, scribe 3, connector 3, mutation-tester 3, revenger 2, sentinel 2, simplifier 1). `taskCall.json` also has those 33 names and zero occurrences of `--auto`.

## Findings

### High — the dirty file is not a safe keep

The edit is not an annotation on top of a stable receipt. It rewrites fields the committed blob already recorded, and the new failure sentence is not backed by a CLI stderr capture in this lane.

Changed besides the note:

- `dispatchedAt` moves from `2026-10-24T20:37:01-0300` to `2026-10-24T20:45:36-0300`.
- `transport` gains `--add-dir <fleet> --add-dir <shokuknow>`. The committed transport already lacks `--auto`. The note describes removing `--auto`; the transport delta is a different edit.
- Every seat gains `pid2` (`1983097` through `1983129`, 33 contiguous values). `pid` stays the first-attempt id.

The new `dispatchedAt` equals the working-tree file mtime (`2026-10-24T20:45:36.920223` local), not a separate launch receipt. Untracked `.ufo/waves/round-34/w1/dispatch.log` is two lines: `launched 33 seats at 20:49:17` and `all seats settled`. It does not contain the flag sentence. Untracked `swarm-registry.json` `updatedAt` is `2026-10-24T23:37:01.925Z`, which is the committed `20:37:01-0300`, not `20:45:36`.

The note says the first attempt died at spawn, 33 seats did no work, and the same task list was re-dispatched. Seat-name equality with HEAD and with `taskCall.json` supports "same 33 lanes, none replaced." The failure half does not have a stderr receipt here. `dispatch.log` lacks the sentence. 32 of 33 `seat.log` files lack it. The one that has it, `ScribeLesson/seat.log`, quotes this manifest. All 33 seat logs exist and are longer than 500 bytes (smallest 2355). Thirteen open with `kimi version` and then `error: failed to run prompt: provider.api_error: 429 ...`. Twenty open with seat reasoning. That is seat work on disk, under a 429 failure mode, not a captured `--prompt`/`--auto` rejection. Those logs may be a later attempt whose files overwrote an earlier one; they are not evidence for the note's "no seat work ran."

Keeping this diff makes the working-tree path contain the sentence while the committed blob the C1 counter reads still lacks it. `tools/round35-statement-audit.py` sets `manifest_lacks_error` from `git show b784e1ab273472eaa750fc10918ca4be67fa7697:.ufo/waves/round-34/w1/out/dispatch-manifest.json`, not from the working tree. Committed `corpus/lessons/round-34.md` mistake row 3 and committed `wave-census.md` already say the failure is recorded in this path. That citation is false of blob `b321135`. Keeping the dirty file sustains the false citation for anyone who opens the path, and it does not correct the committed-byte fact.

Discard restores the on-disk file to the blob that lacks the sentence, keeps all 33 names, and does not require staging. The sentence, if it is to be corrected, belongs in a correction row that says the committed blob lacks it — not in a rewrite of the cited file.

### Medium — no single canonical runtime id

Same seat identity is preserved (`name` / `role` / `pid` / `report` / `log`). Process identity is not. Each seat now has two pids, and nothing in the file says which one is canonical. A reader of `pid` still gets the pre-rewrite id. A reader of `dispatchedAt` gets the file-mtime rewrite, which disagrees with `dispatch.log`'s `20:49:17`.

A Python scan of the 33 seat logs found own `pid` in 0 logs and own `pid2` in 2 (`MutAppendBlock` line containing `1983124 ... kimi-code`, `SentinelReceipts` line containing `1983128 ... kimi-code`). Those two lines are consistent with those pid2 values having been live `kimi-code` processes at a `ps` snapshot. They do not bind the other 31 pid2 values, and they do not show which attempt `pid` versus `pid2` names. The Read tool refused those two logs as non-UTF-8; the lines above are from a Python scan.

No in-lane resume caller mutates from this file. `taskCall.json` `resumeSends` length is 0. `tools/round35-statement-audit.py` reads the fixed committed rev. `.ufo/waves/round-35/w1/launch-wave.py` and `wait-seats.py` use round-35's own `dispatch-manifest.json`, not this path. A failed first spawn therefore has no resume path here that must be allowed to rewrite this receipt. The committed blob is the zero-mutation record. The dirty file is the mutation. The index was not mutated.

### Not a defect

Missing trailing newline is true of both the HEAD blob and the working tree. It is not introduced by this diff.

Seat-name preservation is real. It is not a reason to keep the rewrite: the names are already in blob `b321135`.

## Residual risk

Discarding the working-tree file drops the only copy of the `note` text and the 33 `pid2` values from this path. The note text is quoted above. `pid2` runs `1983097`–`1983129`. Two of those values also appear in the untracked seat logs named above. Discarding does not change blob `b321135` and does not, by itself, move `manifest_lacks_error`.

Keeping the dirty file would leave a path-level split: open-the-file shows the sentence; `git show` of the audited rev does not. That split is the calibration bug already named in `corpus/lessons/round-34-verifier-spotcheck.md`.

This review did not stage the file. Staging or committing it would publish the rewrite. It still would not change the counter's read of `b784e1ab:path` unless that history were rewritten, which this seat must not do.

## Verification gaps

- No lane file captures the Kimi CLI stderr of a first spawn. The flag sentence was not re-derived from a command log. It was re-derived only as text added by this diff.
- `dispatch.log` does not identify pids. pid2 is corroborated for 2 of 33 seats only, and only as a `ps`-like line, not as this seat's spawn record.
- Whether current seat logs overwrote a first attempt is not decidable from the logs alone.
- The fleet report blob `7610d532696f5c6e214840fa2ec4112584589252` was not re-hashed in this review. This diff does not touch that repo. The counter's `report_unchanged` check is independent of this working-tree file.
- `MISSION.md` was not opened; it is not in the lane. The operability + freshness citation is from `SCORECARD.md:192` and `LOG.md:277` only.
