# VerifyRow03 — hand verification of correction row 3 (sid `SA29:SCORECARD.md:P:980355388a:0`)

Seat: kama-r29-w2-VerifyRow03, round-29 attempt-2 w2, lane `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master).
Counter never executed (per item); frozen counter file integrity checked by hash only.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:P:980355388a:0", "verdict": "confirmed-false", "observed_hand_derived": "p:absent", "row_last_cell": "p:absent", "last_cell_matches": true}
```

The base statement is FALSE at its writing revision W, and the committed correction row's last cell equals the hand-derived observed value exactly.

## Step 1 — base statement line

Base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`, `SCORECARD.md` line 192 (correction row names `SCORECARD.md:192`):

```
Steered round 10 (the 2026-10-18 plan `.ufo/round-10/plan.json`, never dispatched, finished here). Axis authority: `MISSION.md:29` — operability + freshness; the round prompt's "operability + calibration" is overridden by the mission file (the G5 recurrence). Measured at this round's commit on branch `kaika/round` (hash cited in the fleet report). Scores are self-assessed and pending non-author verification.
```

Class rule (read from `.ufo/waves/round-29/count-c1.py` docstring, P):
`path:L` / `path:L-M` (path not starting `../`, `/`, `~`, or a URL): the blob `W:path` exists and has at least `max(L,M)` lines; fails `p:absent` / `p:beyond-eof`.

RE-P match on line 192: exactly one — `` `MISSION.md:29` `` (preceded by a backtick, which is outside the token-start lookbehind class `[\w./~:-]`); path `MISSION.md` passes `in_lane`, L=29, no range → `end=29`. Single P token → index k=0 → sid suffix `:0`. Statement is checkable, class P. (`.ufo/round-10/plan.json` on the same line has no `:N` suffix; no other file:L pattern on the line.)

## Step 2 — writing revision W via blame

`git blame --line-porcelain 2aa46e2 -L 192,192 -- SCORECARD.md`:

```
1e41928aba2b81dd65ea75084918a7fadf453720 192 192 1
summary round-10: sources registry (30 rows) + 3 cross-engine entries; 50 stale anchors re-anchored by appended corrections; KQ6-KQ10
```

W = `1e41928aba2b81dd65ea75084918a7fadf453720` (committer time 2026-10-19 19:34:42 -0300). The correction row's W cell reads `1e41928a` — matches blame.

**Precision finding (not a defect in the row):** the item asked to "confirm W's prefix matches the sid". In the frozen counter (`extract()`), the sid's hash component is the **line-content digest**, not W: `lsha = hashlib.sha256(line.encode()).hexdigest()[:10]`. I computed it by hand: `sha256(base SCORECARD.md line 192 text)[:10] = 980355388a` — matches the sid. W's prefix lives in the row's W column (`1e41928a`) and matches blame. Both sid components therefore verified, but the sid↔W relation is "sid hash = line digest", never "sid hash = W prefix" (already falsified by rows where they visibly differ, e.g. row 1 sid `Q:f4c42debcc` with W `ea72c3ea`).

## Step 3 — P rule applied BY HAND at W

At W = `1e41928aba…`, the rule requires blob `1e41928aba…:MISSION.md` to exist with ≥ 29 lines.

- `git cat-file -e 1e41928aba2b81dd65ea75084918a7fadf453720:MISSION.md` → exit code 128 (no such path/blob) → per `check()`: `data is None → ("p:absent")`.
- `git ls-tree -r --name-only W` → no `MISSION.md` anywhere in W's tree (only `.ufo/round-5/mission-result{,-input,-validation}.json`).
- Context: the base root tree also lacks `MISSION.md`; the file the author meant is the fleet-level `../MISSION.md`, which RE_P/in_lane deliberately treat as uncheckable — the statement wrote the bare in-lane name, so it is checkable and fails.
- Independent line count check (would matter only if the blob existed): n/a, blob absent.

Hand-derived observed value: **`p:absent`** → statement FALSE at W. ✓

## Step 4 — correction row last cell

Data commit `513eba3ba51a142c9936553e3a85918345eb5c4c` (= lane HEAD), `SCORECARD.md`, heading `## Round 29 — self-assessment corrections` at line 1443, 11 data rows. Row 3 (3rd data row — matches the item's "row 3"):

```
| SA29:SCORECARD.md:P:980355388a:0 | SCORECARD.md:192 | P | `MISSION.md:29` | 1e41928a | names the fleet file ../MISSION.md (line 29 is the kama row); no lane path MISSION.md | p:absent |
```

- First cell sid = `SA29:SCORECARD.md:P:980355388a:0` ✓; row names base line `SCORECARD.md:192` ✓; W cell `1e41928a` = blame W prefix ✓.
- Last cell = `p:absent` — **exactly** equals the hand-derived observed value ✓.
- Sid appears exactly once at tip (11 total rows, 1 hit) → no duplicate ✓.
- Append-only context for this slice: base `SCORECARD.md` blob (104,553 bytes) is a byte-prefix of the data-commit blob (107,505 bytes); line 192 byte-identical base→data commit ✓.
- Cause narrative spot-check: fleet `/home/vgpnk/Projects/shokunin/MISSION.md` line 29 is indeed the kama lane row (`kama: { cwd: kama-shokunin/, axes: "operability + freshness (local model serving/endpoints)" }`) — the narrative cell is accurate (narrative is not part of the machine-checked contract; noted for completeness).

## Corroboration (artifacts = data only; derivation above is independent)

- `.ufo/waves/round-29/before/c1-base.json` @ 513eba3, `all_statements[11]` and `mismatches[2]`: `{"sid": "SCORECARD.md:P:980355388a:0", "class": "P", "line": 192, "W": "1e41928aba2b81dd65ea75084918a7fadf453720", "token": "MISSION.md:29", "holds": false, "observed": "p:absent"}` — consistent with my hand derivation.
- `sha256(.ufo/waves/round-29/count-c1.py on disk) = fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` — equals the frozen hash claimed in the assignment ✓ (rule text I applied is the frozen rule).

## Residual risk / verification gaps

- The counter was not run (forbidden for this seat); the observed value is hand-derived from the docstring rule + `check()` source, not machine-executed. My git primitives replicate the counter's exactly (`git --no-replace-objects`, blame `--line-porcelain` at BASE, cat-file at W).
- Blame-based W is the last commit touching the line before base — identical to the counter's semantics, so no divergence is possible by construction; no cross-check against an alternative W definition was made (out of scope).
- Item's "W prefix matches sid" is unsatisfiable as literally worded (sid carries the line digest); reported above. The row itself is internally consistent and correct.
- Did not verify the other 10 rows or the fresh-clone receipt (other seats' scope).

Tooling: none installed; used preexisting `/usr/bin/git` (repo git version) and Python 3.14 stdlib. No writes outside this report (both copies below) and no /tmp artifacts were needed.

Report copies (identical content):
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-VerifyRow03/report.md` (seat output dir)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/VerifyRow03.md` (item-named Report path)
