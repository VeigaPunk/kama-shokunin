# X1Stable — round 47, item X1Stable (C1 D2 evidence + window-maximum attack)

**Verdict:** v2's two closure repairs hold and are stable at every audited tip — deleted counts equal `git numstat` byte-for-byte (v1 loses 4 + 2 `--` lines on the lane) and `restored_max` never falls when the tip moves (v1 falls 24→1 and 2416→2409 on the same events) — **but v2's window maximum is a real blind spot for the append-only claim**: an event fully restored and then deleted again in sub-threshold commits is reported `restored` with exit 0 forever, even when the tip holds **none** of the deleted lines (fixture: `held_at_tip=0`, file 43 of 100 lines, exit 0). The lane already runs that mechanism: 7 of the 2421 lines from 0718b6ab's SCORECARD deletion are gone at 3a09a1d9 via three sub-threshold commits (8/2/14 lines), invisible to the event list; the status only stays red because that event was already `partial`.

Tooling: nothing installed, no `pacman`, no network used (C2 not touched). All runs are read-only against a `git clone --shared` of the lane; the contract/preregistration/counters were not modified.

## 1. Method and the eight tips

```
S=/fast/scratch/hyaku/kama-r47/X1Stable
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin $S/lane
git -C /home/vgpnk/Projects/shokunin/kama-shokunin show bbcc6dc2fbd7fc04b1d91a97ffa239a6601cd5ba:tools/append-only-audit.py > $S/v1/append-only-audit.py
# v1 = sha256 793dab9ffe0c41c7a5427324fd6f8bf0c3b40b0f9083d417e38d5e5792a7227f
python3 $S/v1/append-only-audit.py --repo $S/lane --to <tip> --json
python3 <lane>/tools/append-only-audit.py --repo $S/lane --to <tip> \
        --contract <lane>/registry/append-only-contract.tsv --json
```

The requested window is `git rev-list --topo-order --reverse 172b8ad040d51ce8c011238c1408d4e0b6aa9595^~40..3a09a1d93dcc16799cf6c4b48786e6440af134c4` = 43 commits. The eight tips below are spread across it, with the two round-45 event boundaries (T6 = the 0718b6ab deletion event, T7 = its restoration at 82b5e9d3) kept in the sample; `#` is the 1-based index in that rev-list:

| tip | # | rev | note |
|---|---|---|---|
| T1 | 1 | 45e6f1a9637f | oldest revision in the window |
| T2 | 7 | 596921fccd6a | |
| T3 | 13 | 372fc011f9dc | |
| T4 | 19 | ef76777e5fbd | |
| T5 | 25 | 85977699b4af | last tip before the 0718b6ab deletion |
| T6 | 27 | 0718b6abbda6 | the 2292/2421-line deletion event itself |
| T7 | 28 | 82b5e9d33a19 | the restoration commit |
| T8 | 43 | 3a09a1d93dcc | the build tip |

All 16 runs exited **1** (both tools always find at least one partial event); per-run exit codes and output sha256s are in `runlog.txt`. The contract is passed as a *file* because it does not exist at T1–T5; `registry/append-only-contract.tsv` was not in the tree before 3a09a1d9.

## 2. Per-event table (v1 deleted / restored_at_tip / status vs v2 deleted / restored_max / status)

Full table: `table.md`; raw JSON for all 16 runs: `res/v1-<rev>.json`, `res/v2-<rev>.json`.

| tip | event | file | v1 del | v1 tip | v1 status | v2 del | v2 max | v2 status |
|---|---|---|---|---|---|---|---|---|
| T1–T5 | dd9f5dc6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T6 | 0718b6ab | LOG.md | 2290 | 280 | partial | **2292** | 0 | unrestored |
| T6 | 0718b6ab | SCORECARD.md | 2417 | 511 | partial | **2421** | 0 | unrestored |
| T6 | 0718b6ab | corpus/QUALITY.md | 375 | 102 | partial | 375 | 0 | unrestored |
| T6 | 0718b6ab | corpus/README.md | 663 | 138 | partial | 663 | 0 | unrestored |
| T6 | dd9f5dc6 | SCORECARD.md | 31 | **1** | partial | 31 | 24 | partial |
| T7 | 0718b6ab | LOG.md | 2290 | 2290 | restored | 2292 | 2292 | restored |
| T7 | 0718b6ab | SCORECARD.md | 2417 | 2416 | partial | 2421 | 2420 | partial |
| T7 | 0718b6ab | corpus/QUALITY.md | 375 | 375 | restored | 375 | 375 | restored |
| T7 | 0718b6ab | corpus/README.md | 663 | 663 | restored | 663 | 663 | restored |
| T7 | dd9f5dc6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |
| T8 | 0718b6ab | LOG.md | 2290 | 2290 | restored | 2292 | 2292 | restored |
| T8 | 0718b6ab | SCORECARD.md | 2417 | **2409** | partial | 2421 | 2420 | partial |
| T8 | 0718b6ab | corpus/QUALITY.md | 375 | 375 | restored | 375 | 375 | restored |
| T8 | 0718b6ab | corpus/README.md | 663 | 663 | restored | 663 | 663 | restored |
| T8 | dd9f5dc6 | SCORECARD.md | 31 | 24 | partial | 31 | 24 | partial |

### D1 — deleted counts (v1's `--` blind spot), closed

```
$ git -C $S/lane diff --numstat 0718b6ab^ 0718b6ab -- SCORECARD.md LOG.md corpus/QUALITY.md corpus/README.md
5	2292	LOG.md
9	2421	SCORECARD.md
4	375	corpus/QUALITY.md
2	663	corpus/README.md
# deleted content lines starting with `--` (diff file header excluded):
SCORECARD.md 4   LOG.md 2   corpus/QUALITY.md 0   corpus/README.md 0
```

v2 prints 2292 / 2421 / 375 / 663 — equal to numstat on all four. v1 prints 2290 / 2417 / 375 / 663; the deficits are exactly the deleted lines whose text begins `--` (4 SCORECARD, 2 LOG), which v1 discards because the diff renders them as `---…` and v1 filters on that prefix (`$S/v1/append-only-audit.py`, `dele = [x[1:] for x in d.split("\n") if x.startswith("-") and not x.startswith("---")]`). The round-46 closure D1 numbers reproduce on the lane.

### D2 — tip motion, v1 falls, v2 does not

- `dd9f5dc6 SCORECARD` v1 `restored_at_tip`: 24 (T1–T5) → **1** (T6) → 24 (T7–T8). Nothing re-deleted dd9f5dc6's content between T5 and T6; the SCORECARD head was re-anchored and the audited tip moved. This is a 23-line fall with no new deletion event.
- `0718b6ab SCORECARD` v1: 2416 (T7) → **2409** (T8) — the 7-line fall the round-46 closure recorded.
- `0718b6ab LOG/QUALITY/README` v1: 0 at T6 (tip = the event commit itself) → 2290/375/663 at T7–T8, i.e. v1's number is a function of where the tip sits.
- v2 `restored_max` on the same events across T1…T8: 24/24/24/24/24/24/24/24 and 2292/375/663 appearing at T7 and **equal at T8**; 2420 at T7 == 2420 at T8. **No v2 value falls at any of the eight tips.** (`table.md`, "Monotonicity" section.)

So both routed repairs behave as claimed on the lane. The rest of this report is the attack on that definition.

## 3. Attack 1 — restore, then erase below the threshold (fixture)

`attack_window_max.py` (sha256 5eb68ce9…) builds a fresh repo under `$S/attack` (toplevel asserted equal to the fixture dir before the first commit; throwaway identity passed with `git -c` only inside it):

| commit | change |
|---|---|
| c1 `0d47d644` | seed `LOG.md` with 100 unique lines + `AGENTS.md` + a contract row for `LOG.md` |
| c2 `b49a7f84` | delete 57 lines in one commit → event (`deleted=57 >= 20`) |
| c3 `6bc88263` | restore all 57 → `restored_by = c3` |
| c4 `fe81d367` | delete 19 of the restored lines (no event) |
| c5 `5f246df9` | delete 19 more (no event) |
| c6 `e537b368` | delete the last 19 (no event) — tip holds **43** of 100 lines |

```
$ python3 <lane>/tools/append-only-audit.py --repo $S/attack --to <tip> --contract <lane>/registry/append-only-contract.tsv --json
v2 after-restore 6bc882632622 rc=0 events=[{... "deleted": 57, "restored_max": 57, "restored_by": "6bc88263…", "status": "restored"}]
v2 after-1st-19  fe81d36724e2 rc=0  … restored_max 57, status restored
v2 after-2nd-19  5f246df9f6df rc=0  … restored_max 57, status restored
v2 after-3rd-19  e537b368ef28 rc=0  … restored_max 57, status restored
# independent recomputation under the frozen definition (held_at_tip.py):
{"deleted": 57, "held_at_tip": 0, "tip_line_count": 43, "restored_lines_present_at_tip": 0}
```

Answer to the item's question: **yes, v2 reports it restored forever** — at every post-restore tip, including the tip that holds none of the 57 lines, the event is `status=restored`, `restored_max=57`, summary has `partial=0 unrestored=0`, and the tool **exits 0** ("no event partial or unrestored"). The later 19-line commits are not events at all (`|D| >= 20` gate), so they never enter the window as anything but "held" checks, and the window maximum was attained at c3 and cannot fall. For contrast, v1 at the final tip prints `deleted=57 restored_at_tip=0 status=unrestored`, rc=1 — v1 is tip-sensitive (D2) but not blind here; v2 traded that failure mode for this one.

Is it a blind spot for the append-only claim? **Yes, and it is frozen into all three artifacts, not an implementation slip:**

- Tool definition, `tools/append-only-audit.py:28-35` — `restored_max the maximum held(x) over the window`; `status restored (max == |D|)`.
- Tool code, `tools/append-only-audit.py:199` (`if ns[f] < threshold: continue`) and `:208-220` — the window loop `break`s at the first full restoration and `status` is derived from the maximum only; nothing measures `held(<to>)`.
- Tool selftest, `tools/append-only-audit.py:402-413` (`t_window_max`) — "restored fully, then re-trimmed below threshold: the window maximum keeps it restored" asserts `status == "restored"` **and `exit_code(res) == 0`**. The blind spot is asserted as a pass.
- Counter definition, `tools/round47-append-audit-v2-check.py:46-50` (`restored_max` / `status`) and `:84-85` ("the window maximum must keep it restored"); its fixture E3 at `:490-498` builds exactly this shape and expects `"status": "restored"`.
- Counter `stable` leg, `tools/round47-append-audit-v2-check.py:577` — `t["restored_max"] < e["restored_max"]` is the only failure, i.e. monotone non-decreasing; a rising tip can never fail.
- The C1 `limits` in `preregistration.json` name only contract coverage ("a lane file declared append-only but missing from the contract is not detected"); they do not name threshold-chunked re-deletion. The claim sentence ("restoration is a byte-exact multiset measure maximised over the event's own window, so a later head re-anchor cannot lower it") is satisfied; the *verdict* that the claim is append-only is not.

## 4. Attack 2 — split the whole loss from the start (no event at all)

`attack_split_only.py` (sha256 bc7b415b…) deletes 57 lines from an append-only contract file in three commits of 19, with no restoration:

```
{"commits": 4, "tool_rc": 0, "events": [], "summary": {"events": 0, ...}, "tip_line_count": 43, "seed_line_count": 100}
```

v2 prints no event and exits **0**; `held` is never computed for that file because nothing crosses 20 in one commit. This is the more basic form of the same weakness: the threshold is a sampling device per `(commit, file)`, so the append-only claim is never actually checked — only "large deletions that were later re-added somewhere". A single commit deleting 19 lines from each of several contract files is invisible too (the gate is per file, so N×19 lines can leave in one commit).

## 5. The mechanism is live on the lane (not only in a fixture)

`held_at_tip.py` (sha256 715156c5…) recomputes `held(<to>)` with its own diff/line reading at `3a09a1d9` (`held_tip.json`):

| event | file | deleted | restored_max | held_at_tip | gap |
|---|---|---|---|---|---|
| 0718b6ab | SCORECARD.md | 2421 | 2420 | **2413** | **7** |
| 0718b6ab | LOG.md | 2292 | 2292 | 2292 | 0 |
| 0718b6ab | corpus/QUALITY.md | 375 | 375 | 375 | 0 |
| 0718b6ab | corpus/README.md | 663 | 663 | 663 | 0 |
| dd9f5dc6 | SCORECARD.md | 31 | 24 | 24 | 0 |

The 7 missing lines leave through three post-restoration commits, all below the 20-line gate (`post-restore-subthreshold.txt`):

```
4340cf2f… deletions=8   (round-46 integration, SCORECARD head re-anchor)
4991ecc2… deletions=2
42ea1204… deletions=14
```

The lane is saved only by the SCORECARD event already being `partial` (2420/2421), so exit is 1 for an unrelated reason; the 7-line loss is nowhere in the tool's output. Had 0718b6ab's SCORECARD deletion been fully restored like LOG/QUALITY/README, these three sub-threshold commits would have turned a fully-lost restoration into a green audit. The shape also matches the lane's own declared expectation (contract note: SCORECARD head re-anchor is an expected partial), which is precisely why a per-tip verdict — not a window maximum — is needed to distinguish "expected head re-anchor" from "restored then erased".

## 6. Defect and proposed fix

**Defect (instrument definition, not a miscount):** `tools/append-only-audit.py:218` derives `status` from `restored_max` alone and `tools/append-only-audit.py:239-241` exits 0 on `restored`, so a restored event whose lines are deleted again below the threshold stays green forever; the counter shares and asserts that definition (`round47-append-audit-v2-check.py:46-50,84-85,490-498,577`).

**Command that shows it:** `python3 <lane>/tools/append-only-audit.py --repo $S/attack --to e537b368ef282c639e2b02edd869bdc7cfccd195 --contract <lane>/registry/append-only-contract.tsv` → `status=restored`, exit 0, tip holds 43/100 lines, `held_at_tip=0`.

**Proposed fix (v3, full text + unified diff in this directory, nothing applied to the lane):** keep `restored_max` (D2 comparability) and add the tip verdict:

- `held_at_tip = held(<to>)` computed after the window loop (the loop `break`s at `:215-217`, so it must not be read from the loop variable);
- `tip_status` = `held` / `lost` / `partial`;
- `regressed` count in `summary` and in `exit_code` (`tools/append-only-audit.py:239-241`), so `status=restored` with `tip_status != held` exits 1;
- `t_window_max` flips from asserting exit 0 to asserting `held_at_tip=20 / regressed=1 / exit 1`, plus a new `t_laundered` case for the 3×19 full erasure.

Verification of the proposal (`proposed-append-only-audit-v3.py`, sha256 8f2c90c5…; diff `proposed-append-only-audit-v3.diff`, sha256 4b1b7b1a…, `patch -p1 --dry-run` clean against the lane bytes):

- `v3 --selftest`: `AOA_SELFTEST pass=16 fail=0`, rc=0 (`v3-selftest.out`).
- attack fixture: `status=restored held_at_tip=0 tip_status=lost … regressed=1`, rc=1 (`v3-attack.out`).
- lane at 3a09a1d9: same 5 events, same `restored_max` values, `held_at_tip` 24/2292/2413/375/663, `regressed=0`, rc=1 unchanged (`v3-lane.out`) — the fix adds no false positive on the lane.
- Not fixed by v3: the split-only case (no event exists to regress). If the "append-only" claim is to be enforced rather than sampled, a future round needs an applied-only leg (per-commit numstat additions/deletions against each contract rule, with the declared head-region exceptions), not a threshold-gated event list. `attack_split_only.out` and `v3-split.out` show both v2 and v3 exiting 0 on a 57-line loss.

Because the counter is frozen, the counter's fixture E3 expectation (`:496-498`) and its `stable`/status recomputation must change in the same future round as v3 lands; as it stands, a correct v3 would *fail* the frozen counter's fixture leg (E3 expects `restored` with exit 1 overall from E2, so the fixture cannot distinguish this case). Route: round-48 C-candidate — add `held_at_tip`/`regressed` to both the tool and the counter and an applied-only leg for the split case.

## 7. Limits and risks

- My recomputations (`held_at_tip.py`, `attack_*.py`) implement the *same frozen definition* on an independent code path; they are not independent ground truth for the definition itself. Independent ground truth here is `git diff --numstat` (deleted counts: confirmed equal) and the fixtures' construction (all fields: confirmed).
- v1 runs use the v1 default five-file set (v1 has no contract option); its event set therefore never includes `corpus/lessons/*.md`. That does not affect the D1/D2 comparison, which is on events both tools can see.
- T1–T5 v2 runs pass the build contract as a file, so `files` includes `corpus/lessons/*.md` at tips where the contract was not yet committed; the tool checks only the `declared_at` format; the counter additionally requires the file to exist at the tip and the line to contain `append`.
- No C2 path was touched; no network was used; nothing was installed; no lane/fleet/jj/Git state was modified (lane access was `git show/rev-list/diff/numstat/ls-tree/cat-file/log` only). Fixtures live under `/fast/scratch/hyaku/kama-r47/X1Stable/` and the clone was removed after the evidence was copied here.

## 8. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/table.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/runlog.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/res/` (32 files: `v1-<rev>.json`, `v2-<rev>.json`, stderr)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/v1-append-only-audit.py` (freeze v1, sha256 793dab9f…)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/attack_window_max.py`, `attack.out`, `attack-fixture.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/attack_split_only.py`, `attack_split_only.out`, `attack-split-fixture.log`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/held_at_tip.py`, `held_tip.json`, `post-restore-subthreshold.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/proposed-append-only-audit-v3.py`, `proposed-append-only-audit-v3.diff`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-47/w1/out/X1Stable/v3-selftest.out`, `v3-attack.out`, `v3-lane.out`, `v3-split.out`
