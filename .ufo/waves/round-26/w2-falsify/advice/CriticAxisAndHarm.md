# CriticAxisAndHarm — round 26 wave 2 (falsify): C1 axis fit and the no-harm condition

ATTACK C1 depth-axis fit and the round-26 no-harm condition across six axes: **partial** — the claim and its counter run hold (17/17 rows genuine, independently re-verified), but at the landed tip two calibration statements are false, freshness overclaims the source snapshot, and the "depth 7 → 8" promotion is not supportable once the wave-2 shortcut shows the frozen counter is met 12/12 from the base tree. The uncommitted worktree at review time already repairs the first two and withdraws the promotion; I verified those repairs are true. No axis is harmed by the depth move itself.

Revision note: HEAD is `f4066979096e3452ae731c0e09e50155c6d8258a` (`git --no-optional-locks rev-parse HEAD`). While this seat ran, the L1 applied wave-2 repairs **uncommitted** to `LOG.md`, `SCORECARD.md`, `SKILL.md`, `corpus/lessons/round-26.md` and added three untracked snapshot files (`git --no-optional-locks status --porcelain`). Findings below state the revision they describe. The closure must judge the final committed bytes, not HEAD: the wave-2 late-write hazard (round-25 defect 7 class) is live.

## 1. Verdict per axis

| Axis | At HEAD f406697 | In the uncommitted worktree (verified) | Evidence |
|---|---|---|---|
| **depth** | **holds** | **holds** | The surface is a depth move, not a number: 17 named signatures with trigger/meaning/action/source at `SKILL.md:1084-1100` (HEAD; worktree `:1102-1118`). All 17 new at base: `git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` → rc=1 each. All 17 occur exactly once in the pinned file, on the exact SOURCES anchor line (`5366, 5408, 3084, 5453, 6132, 6137, 6151, 5803, 5476, 3657, 5998, 5655` server-context.cpp; `1272, 1114` server-common.cpp; `1021, 482` gguf.cpp; `2624` llama-context.cpp). I re-read every code span the rows cite; all match (e.g. guard 5365-5367; `slot_save_path.empty()` 5407 before `action` is read at 5422; `nread == 0` throw 3083-3085; `!body.is_array()` 5997; `graph_reserve` assert 2621-2624). Receipt statuses/exit match the rows (`c1-tip-receipt.json`: E26-10 `500`, E26-17 `-6`). The frozen counter re-ran at the tip f4066979: `registered 17 counted 17 target 12 met True`, exit 0, identical stdout and identical HTTP channel hashes (`w2-falsify/advice/RerunC1AtTip.md:47-58`). |
| **coverage** | **holds** | **holds** | SOURCES 113 → 135 rows (`grep -c '^| S[0-9]'`), 0 deleted row lines; frontier named in `corpus/README.md:402-410`. No coverage claim made. |
| **operability** | **holds** | **holds** | No existing tool/test bytes changed: `git diff --name-status 1560e4d8 f406697 -- tools/ tests/` → only `A tools/prereg-time-check.py`. New section carries a runnable re-derivation command; counter ran (`final/c1-tip.out`, exit 0). |
| **freshness** | **holds, one overclaim (F2)** | **holds** (F2 repaired: 3 files added, hashes equal pins; lesson amended at `:14-17`) | All 13 snapshot files byte-match a fresh 704366d fetch (16 unique files fetched from raw.githubusercontent.com, curl exit 0): server-context `dd1de0f2…`, server-common `b4f4aae7…`, gguf `7505d6a4…`, llama-context `2a25e556…`, etc. The 3 files added by the worktree hash to their anchor pins (`714c067b…`, `1f83da2a…`, `d0739eaf…`). Historical rows re-verified (`w1-build/advice/ScoutBaseOverlap.md:12-28`). |
| **calibration** | **HARMED (F1)** | **holds** — F1 corrected, and the corrected text is true (I verified both signatures) | HEAD `LOG.md:1682-1683` "SKILL.md held no live error signature for the b11755 runtime" and `SCORECARD.md:1323-1324` "held only the September sample from dead ports" are false. Base `SKILL.md:521-523` holds the `Loading model` 503 body and `SKILL.md:689` holds the round-25 HTTP 500 `Context size has been exceeded.` (both live b11755). Worktree `LOG.md:1682-1684` and `SCORECARD.md:1325-1330` now name both and are accurate. |
| **adjacency** | **holds** | **holds** | Connector path:line evidence: no sibling holds source-pinned llama-server signatures (`w1-build/advice/ConnectorSiblingOverlap.md:3-8`). The auth candidate was found and **not** registered (`ExecApiKey/candidates.json` → `"authentication_error"`; rejected as kagi's). No auth/OS/systemd/dispatch row among the 17. Worktree adds kumitate to the cited owners (`SKILL.md:1094`). |

**Counter discrimination (the strongest counterexample in the lane):** the wave-2 shortcut control met the frozen counter from the base tree with 12 echoed non-error literals (`registered 12 counted 12 target 12 met True`; mechanism: hide a source literal from `e_not_echoed` with a `\u00XX` escape, let `server-common.cpp:1375` echo it into a 400 — counter limit F2). This is on record at `SCORECARD.md:1332-1336` and `LOG.md:1697-1701`. It does **not** falsify the 17 rows — I verified each independently — but it means the counter alone cannot support a score promotion, and the prompt's rule ("a target must be one a do-nothing control cannot reach … if it meets the target, the counter or target is wrong") is violated by the target as frozen. The pre-freeze shortcut control was refused by the provider and never replaced before data (`corpus/lessons/round-26.md:79-80`).

## 2. Findings

### F1 — calibration: false before-state (HEAD). **Repaired in the worktree; repaired text verified true.**

- HEAD `LOG.md:1682-1683`, HEAD `SCORECARD.md:1323-1324`.
- Base truth: `git show 1560e4d8:SKILL.md | sed -n '519,529p'` → `521: Error signature (llama.cpp b11755 single-model, every non-frontend path while` / `523: {"error":{"message":"Loading model","type":"unavailable_error","code":503}}`; `… | sed -n '685,693p'` → `689: … every processing request fails with HTTP 500 `Context size has been exceeded.``. Base `SKILL.md:551-554` says the round-16 live receipt captured the 503 body.
- Why it matters: AXES defines calibration as self-assessment matching observed repo state; the round's no-harm condition depends on it. The claim's own frozen before is true (`registered 0 counted 0`), so the defect is narrative, not measurement.
- Smallest correction (as applied in the worktree, verified): state the two live b11755 signatures and that none of the 17 E26 strings was held. No data change. Independently found by wave-2 seat ReviewerScorecardLogTruth (`corpus/lessons/round-26.md:82`); this seat's check is a second sample, and I verified the newly added `:689` citation against the base revision.

### F2 — freshness: lesson claimed snapshot equality for rows not in the snapshot (HEAD). **Repaired in the worktree; hashes verified.**

- HEAD `corpus/lessons/round-26.md:13-15` "the fetched bytes equal the lane snapshot"; `git ls-files .ufo/waves/round-26/sources` → 13 files; `common/fit.cpp` (S131), `tools/server/README.md` (S134), `src/llama-kv-cache.cpp` (S135) absent.
- The pins were always correct (fresh 704366d fetches hash to `1f83da2a…`, `714c067b…`, `d0739eaf…`). Worktree adds the three files (untracked, hashes equal the anchor cells) and amends the sentence at `:14-17`, attributing the find to wave-2 seats ReopenS131/ReopenS134.
- Smallest correction: none further — commit the added files with the amended lesson.

### F3 — calibration: the "measured commit" cell points at a report that does not exist (value gap now closed by a wave-2 tip rerun; pointer still open)

- `SCORECARD.md:1322` (worktree) / `:1321` (HEAD): "the landed lane tip named in the round report (receipt …c1-tip-receipt.json)".
- Receipt binds to a scratch extract: `final/c1-tip-receipt.json:4` `"lane": "/fast/scratch/hyaku/kama-r26/tip-7e5ff9b5454dd27f0520cb36a3cbc3a995e48162"`; `final/c1-tip.out` `tree=7e5ff9b5…`. Two commits landed after the run (`3550523`, `f406697`). No round-26 `kama.md` exists in `/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/` or the lane.
- Why the receipt still stands: the round's own KQ36 qualification (`corpus/QUALITY.md:205-211`) admits a pre-landing run when measured source and instrument bytes are identical at the landing commit. Verified: `count-c1.py` blob sha256 `6501737c…6588` at a23c0e0, 84ec083, 7f84cd0, 7e5ff9b, 3550523, f406697; `git diff --name-only 7f84cd0 7e5ff9b` touches only round-25/26 wave artifacts, `git diff --stat 7e5ff9b f406697` only `final/*`, `w1-build/out/ExecRequestParams/*` and `LOG.md`. No measured byte differs at the tip.
- The value gap is closed independently: seat RerunC1AtTip ran the frozen counter under the host-wide lock in a `git archive` extract of f4066979 and printed the identical result, exit 0, with identical HTTP channel hashes (`w2-falsify/advice/RerunC1AtTip.md:47-58`). So "counted 17 at the tip" is measured now, not only inferred.
- Smallest correction: commit that tip receipt as the binding artifact and name the measured tree in the cell ("tip rerun receipt at f406697; landed receipt at tree 7e5ff9b, identical bytes"). One line; no re-run needed.

### F4 — maintenance hazard, do not touch this round (still open)

- `SKILL.md:1111` (worktree; `:1093` HEAD) registers `is too large to process. increase the physical batch ` with a trailing space inside the backticks. Counter clause (a) (`sig in row`) and (d) (`sig.encode() in source bytes`) are exact-substring checks; any future trim silently drops the row to `counted 16`.
- The predicate/pins are frozen after data, so this belongs to round 27 (the round already plans a stricter counter). Add the exact-byte note to the section header for editors.

### F5 — already addressed in the worktree

Five rows (E26-01, -02, -04, -05, -08) are one mechanism — an unset launch flag makes a handler refuse at entry. Worktree `SKILL.md:1086-1088` says so; this is the right way to keep the row count honest. Collapsing them to one decision class still leaves 13 classes, above the target 12 [INFERENCE: my classification], so the depth move survives its own rejection rule.

### F6 — already addressed in the worktree

`SKILL.md:1094` now cites kumitate for omp dispatch/route mapping, matching the connector's proposal (`ConnectorSiblingOverlap.md:3-4`).

## 3. Is "depth 7 → 8" supportable or overreach?

- At HEAD the cell was `depth 7 → 8 (author reading; the closure decides)` (`SCORECARD.md:1321`) while the authoritative axes table still recorded depth `1 → 7`, last change round 1 (`SCORECARD.md:21`) — so the round did not advance the stored score; the number was a labelled proposal, not an overreach in the authoritative field.
- The direction is supportable: the added surface is exactly what the depth axis names, the rows are new knowledge at base, and the addition exceeds the round-1 sample it extends (17 rows vs 11 signatures). The prompt's kaidoku clause ("re-scoring a rule the lane already holds on new inputs is quality work, never depth") does not bite: these are new decision rows, not a re-score.
- The **number** is not: no command distinguishes 7 from 8, the lane held 7 through round 16's comparable vocabulary append (`SCORECARD.md:687`), and 8 is the saturation line (`SCORECARD.md:132`). With the base-tree shortcut meeting the frozen target, the counter cannot carry a promotion at all.
- **Ruling: the promotion is overreach and the worktree's `7 → 7 (no promotion)` (`SCORECARD.md:1322`) is the correct ruling.** The depth *move* stands on the 17 verified rows; the *score* does not move. If a future round wants 8, it needs (a) a shortcut-proof counter and (b) a stated meaning for 8 that the closure can re-derive.

## 4. Other statements checked true (so the closure need not re-derive them)

- HEAD `SCORECARD.md:1321` "counter sha256 `6501737c…6588`, unchanged since a23c0e04" — verified at six revisions; `final/tip-counter-sha.txt` agrees.
- `LOG.md:1691-1694` "57 candidate entries; scout listed 8, 3 no executor found" — 57 counted over `w1-build/out/*/candidates.json`; of the scout's 8 (`w1-build/advice/ScoutFaultSurvey.md`), 5 appear in executor candidates and exactly 3 do not.
- Round-25 trend correction — fleet report `.ufo/reports/round-25/kama.md:120-129` ("quality: unchanged", "discernment: unchanged") and `corpus/lessons/round-25-verifier-spotcheck.md:189,194`.
- Lesson "Old-row changes: none" — 0 deletion lines in `git diff 1560e4d8 f406697 -- corpus/SOURCES.md`.
- A1 control honesty — `controls/A1-rescore/invalid-flag-usage-A1.out`: `registered 14 counted 0 target 12 met False`, exit 0.
- Worktree repair claims I spot-checked and found true: base `SKILL.md:689` carries the round-25 `Context size has been exceeded.` 500; `~/.local/opt/llama-b11755/libllama-server-impl.so` sha256 `e404b91a…b59ed` matches the new header; `server-context.cpp:3100-3102` is the restore catch answering 400; `server.cpp:507-511` returns 1 on model-load failure; `server-common.cpp:280-291` is `parse_lora_request`; `ReviewerCounterCode/findings.md` holds 14 findings (F1-F14); the three new snapshot files hash to the anchor cells.
- Provenance: every `found_by` in `registry/error-signatures-r26.json` names an existing wave-1 seat directory, and the row's signature appears in that seat's `candidates.json`.
- Blast radius: no change to `registry/endpoint-consumers.tsv`, `registry/history/`, root `README.md` or `PROVINCE.md`; `README.md`'s claims remain true.

## 5. Verification log (from `/home/vgpnk/Projects/shokunin/kama-shokunin`)

| Command | Output / exit |
|---|---|
| `git --no-optional-locks rev-parse HEAD` | `f4066979096e3452ae731c0e09e50155c6d8258a` |
| `cat .ufo/waves/round-26/final/c1-tip.out` | `registered 17 counted 17 target 12 met True not-counted []`; `exit=0 tree=7e5ff9b5…` |
| `sha256sum ~/.local/bin/llama-server ~/.cache/kama-shokunin/models/stories260K.gguf` | `b6a31a8e…cd804`, `270cba1b…256d` (match pins); symlink → `~/.local/opt/llama-b11755/llama-server` |
| `sha256sum .ufo/waves/round-26/count-c1.py` | `6501737c…6588` |
| fresh `curl` of 16 unique files at 704366d (scratch) | 13 snapshot files byte-equal; 3 pin-only files equal their anchor sha256; curl exit 0 each |
| per-signature `git grep -F -q -e <sig> 1560e4d8 -- SKILL.md corpus` | rc=1 ×17 |
| per-signature scan of pinned files | 1 occurrence each, on the anchor line (17/17) |
| receipt dump | 17 `counted true`, `checks_false []`; statuses/exit match SKILL rows |
| post-repair spot checks | base `SKILL.md:689`, lib sha256, `server-context.cpp:3100-3102`, `server.cpp:507-511`, `server-common.cpp:280-291,1375`, 14 findings — all as cited |
| `ss -ltn` (47560-47579); `pgrep -af llama-server` | no listener; no process (none started by me) |

## 6. Limits

- This seat did not run the counter (no port block in this item; such seats start no server). The tip value was measured by seat RerunC1AtTip under `/fast/scratch/hyaku/kama-r26/counter.lock`; my byte-identity check is consistent with it and adds the source-level verification the counter does not do.
- The round report does not exist yet, so F3's pointer cannot be checked today. The wave-2 tip receipt exists only under `w2-falsify/out/RerunC1AtTip/` (uncommitted).
- Wave-2 repairs were uncommitted when I read them; line numbers for the worktree state may shift again. I wrote nothing in the lane except this report.
- No tool installs or upgrades were needed or made.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-26/w2-falsify/advice/CriticAxisAndHarm.md` (this report)
- `/fast/scratch/hyaku/kama-r26w2/CriticAxisAndHarm/fresh/` — downloaded source files from raw.githubusercontent.com at commit 704366d, used only for sha256 comparison.
