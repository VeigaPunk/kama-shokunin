# Rev1Loss — the ed135b3c LOG.md loss, reverse-engineered

**Verdict: the five `revert` rows are exactly the five substantive lines the revert removed — all of them canon/operator material landed under the host `ci` identity, not lane-authored round-log text; the removal was the mechanical consequence of a whole-commit `git revert` sent to withdraw the craft-hours canon fleet-wide (not a decision to edit LOG.md), and the correct disposition is the one already in force: **disclose, do not restore** — because the ≥10,000 craft-hour bar the entry announced is withdrawn at both tips, so re-appending it would assert a requirement nobody holds. No defect in the counters; two calibration corrections to the round-50/51 narrative.**

Measurements: lane tip `4eca4892acca6ca4072a0a6fad577d0dd78a5dda` (measured in a `--shared` clone at `/fast/scratch/hyaku/kama-r51/Rev1Loss/lane`, deleted after use). All git reads on the lane are read-only; no lane file was touched.

## 1. What `ed135b3c` removed

```
$ git -C <lane> show --numstat --format= ed135b3c
0       12      HOURS.md
1       7       LOG.md
$ git -C <lane> show ed135b3c --stat
 HOURS.md | 12 ------------
 LOG.md   |  8 +-------
 2 files changed, 1 insertion(+), 19 deletions(-)
```

`ed135b3c` (author/committer `ci <ci@local>`, 2026-10-13 17:04:57 −0300, parent `33b167ec`, grandparent `83bee7fa`) is the exact byte inverse of `33b167ec` ("HOURS.md: craft-hours ledger opened (§Craft-hours canon)", 16:56:38, same identity). Its LOG.md hunk deletes the section `33b167ec` had appended and restores the pre-canon "no newline at end of file" state of the line before it.

The seven deleted LOG.md lines, with the v5/v6 key hash and the v6 `held` measure recomputed from the definition (`$OUT/held-recompute.py`, `$OUT/held-recompute.out`):

| # | held | disclosed in ledger | sha256 (CR-stripped) | line |
|---|---|---|---|---|
| 1 | **1** | no | `d86779c34cc31fa9…3bfed35db` | `fallback. No failure was forced and no route/mission config was changed.` |
| 2 | 0 | **yes** | `2ee99d81fe2e492e…d76b2151` | `## 2026-10-13 — HOURS.md ledger opened` |
| 3 | **1** | no | `e3b0c44298fc1c14…7852b855` (`""`) | *(blank separator)* |
| 4 | 0 | **yes** | `df41705d9aab6a9b…9d0bf1edbd` | `- Operator seed per PROTOCOL.md §Craft-hours: shonen→shokunin now requires` |
| 5 | 0 | **yes** | `eb379fbf0bf9c52f…f6a2fdad5f285` | `  ≥10,000 verified craft-hours AND the SHONEN gate. Ledger starts at 0;` |
| 6 | 0 | **yes** | `eee7f85d24a865c3…6e6fb690ace` | `  instrumented rounds accrue collective in-domain lane-minutes.` |
| 7 | 0 | **yes** | `b0a06400ef3cb19d…6aa7c1f64` | `- Evidence: fleet commit; PROTOCOL.md §Craft-hours.` |

`deleted=7 held=2 lost=5`. The frozen tool agrees on its own code path (`$OUT/event-ed135b3c.json`):

```
$ python3 tools/append-only-audit.py --repo <clone> --to 4eca4892 --json   # exit 0
{"commit":"ed135b3cb869…","file":"LOG.md","deleted":7,"graded":7,"ungraded":0,
 "permitted":0,"restored_max":2,"restored_best":"ea72c3ea…","restored_by":null,
 "held_at_to":2,"disclosed":5,"status":"disclosed","undisclosed":[]}
```

Why the two non-disclosed lines are correctly not disclosed, and are **not** losses:

* line 1 was not removed in substance: `33b167ec` rewrote that line only to add a trailing newline (its own diff shows `-fallback. …` / `\ No newline at end of file` / `+fallback. …`), and the revert restored the no-newline form. The identical bytes are at the tip (count 1, kept-in-parent `K=0` ⇒ `held=1`). The "1 insertion" in numstat is this line.
* line 3 is a blank separator; `held = min(1, max(0, 300 − 28)) = 1` against 300 blank lines at the tip. Nothing was lost with it.

So the change count of "8" (7 deletions + 1 insertion) and the loss count of "7 lines" both overstate: **the content loss is 5 lines**, and the ledger's five rows are exactly those five (byte-hash match above; `registry/append-only-disclosures.tsv:11-15`).

## 2. Authorship: canon/operator side, not the lane

| evidence | command / file:line | result |
|---|---|---|
| identity of the lost entry | `git log --format='%h %an <%ae> %s' -6 ed135b3c -- LOG.md` | `33b167ec`/`ed135b3c` = `ci <ci@local>`; every round entry (`c6199a25` r1, `83bee7fa` r2) = `kama-shokunin <kama@shokunin.local>` |
| the entry says whose it is | deleted line 4 | "**Operator seed** per PROTOCOL.md §Craft-hours" |
| the content is not lane work | deleted line 5 / HOURS.md line 1-8 | a fleet rank bar (shonen→shokunin ≥10,000 verified craft-hours AND the SHONEN gate), not kama in-domain evidence; HOURS.md line 3 declares itself "Append-only" |
| provenance of the wording | fleet `git show 7e818675 -- PROTOCOL.md` | §Craft-hours text landed at the fleet root at **16:55:09**; the lane copy landed **16:56:38**, 89 s later, same identity — downstream of the fleet canon, same actor |
| the surrounding block is lane text and survived | `git blame -L 186,199 33b167ec -- LOG.md` | lines 186-198 ("Operator relay — model fallback … out of kama province") = `83bee7fa` `kama-shokunin`; the revert removed none of their content (line 199 only toggled the EOF newline) |

`ci <ci@local>` is the host/global identity, not a lane identity — the same conclusion the fleet's own `shokunin12h-20261014-p1-audit` wave reached (`members/KengakuIdentityAndTree.md:49-53`, `members/KakeIdentityAndTree.md:94`). **Authored by the canon side (the operator's rollout, executed under the host identity), not by kama.** Confidence: high.

## 3. Intent: the canon was withdrawn wholesale; LOG.md was collateral of the mechanism

Facts (all read-only git):

```
$ git -C kama-shokunin rev-parse 83bee7fa^{tree} ed135b3c^{tree}
be181d4f468f4657989afbdf8bbfd138a0444f36      # pre-canon
be181d4f468f4657989afbdf8bbfd138a0444f36      # after the revert — identical
$ git -C . (fleet) rev-parse 7e818675^{tree} 820eb26b^{tree} 7e818675^^{tree}
5a8471c5… (canon)   fad05e88… (after revert)   fad05e88… (before canon — identical)
```

* The revert message names one subject, `Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"`, and its only body line is `This reverts commit 33b167ec…`. **LOG.md is not named.**
* The diff is the exact inverse of the whole commit including the EOF-newline artefact, and the pair is tree-neutral (`83bee7fa^{tree} == ed135b3c^{tree}` = `be181d4f`). That is `git revert` on the whole commit, not a path-limited revert (`git revert -n … -- HOURS.md` would have left LOG.md alone).
* The same actor did the same thing to the fleet root 6 min earlier and 7 min before the lane revert: fleet canon `7e818675` 16:55:09 → fleet `Revert "canon: 10,000 craft-hour bar re-vendored…"` `820eb26b` 16:58:09, tree-exact inverse, **and it too dropped its LOG.md section** (`git show 820eb26b -- LOG.md`: −10 lines). Timeline: fleet add 16:55:09 → lane add 16:56:38 → fleet revert 16:58:09 → lane revert 17:04:57. One actor, one rollout, one rollback, LOG hunks included in both directions without being mentioned.
* The fleet's own record: `LOG.md:525-526` @ `f47ad6ba` — "Craft-hours mechanism fully reverted everywhere (upstream, fleet, all 13 lanes) — history retains add+revert." *Caveat: written 2026-10-25 by `protocol-shokunin`, i.e. retrospectively, not contemporaneously.*
* The withdrawal stuck: `git log -S 'HOURS.md ledger opened' -- LOG.md` returns only `33b167ec` and `ed135b3c`; no later commit in 50 rounds restores or mentions it; `HOURS.md` is absent from the tip and was never re-added (fleet-wide: `git log --all -- HOURS.md` is empty at the fleet root).

Reading: **the withdrawal of the canon (and of the LOG entry that announced it) was intended; there is no evidence anyone separately decided "LOG.md should lose a line"** — the mechanism did that, uniformly, in two repos. Confidence: high that the outcome was intended at the level of "undo the canon landing completely"; medium that the LOG hunk was consciously considered (no message or note names it; the fleet's statement is retrospective).

## 4. The five ledger rows are those lines

`registry/append-only-disclosures.tsv:11-15`, all `commit ed135b3c… / file LOG.md / count 1 / class revert`, note `deleted in place by: Revert "HOURS.md: craft-hours ledger opened (§Craft-hours canon)"`. Class `revert` is mechanically correct under the v6 rule (subject starts with `Revert "`). Hash-for-hash they are rows 2, 4, 5, 6, 7 of the table above — **exactly the five substantive lines, no more and no fewer**. Line numbers 2 and 4-7 in my table are the ledger's; the two left out (EOF-newline twin, blank separator) are the two the `held` multiset measure counts as present at the tip. The ledger's arithmetic and the tool's event agree independently (`held_at_to=2` + `disclosed=5` = `deleted=7`).

## 5. Recommendation: **disclose** (status quo), not restore-by-append

1. **The lost text is a retracted claim.** It asserts the ≥10,000 craft-hour bar. At the tip that bar is gone at every level: fleet `PROTOCOL.md` has no `Craft-hours` section (`git log -S 'Craft-hours' -- PROTOCOL.md` = `7e818675` + `820eb26b` only; `git grep` at fleet HEAD finds it only in the retrospective record `LOG.md:525`), the fleet tree has no `HOURS.md`, and the lane's `SHONEN.md`/`AGENTS.md`/`PROVINCE.md`/`SKILL.md` hold no craft-hour reference (0 matches at HEAD). Appending the five lines back would write a requirement no owner holds — the append-only rule protects history; it does not license re-asserting a claim its author withdrew.
2. **Restoration would also destroy the calibration datum R6 exists for.** The text survives only inside the reverted commits (`33b167ec` lane, `7e818675` fleet); copying it forward is possible but would flip the event from `disclosed` to `restored` in v6, i.e. the record would then say nothing was lost — the opposite of the fact round-50 closure R6 routes on (a threshold-20 audit really did hide this deletion, `corpus/lessons/round-50-verifier-spotcheck.md:120`).
3. **Disclosure is already the declared, passing terminal state.** `registry/append-only-disclosures.tsv` is the lane's own mechanism (v6 `disclosure` clause, `tools/append-only-audit.py:1-40`), the event grades `disclosed` with `undisclosed: []`, the tool exits 0, and the frozen counter passes: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0 (`$OUT/c2-counter.out`; re-run at `4eca4892`).
4. If the lane wants the event visible *inside* the log (rather than only in the ledger), the LOG.md A-corr rule (`registry/append-only-contract.tsv:2`, "corrections land as new entries") permits appending a **new correction entry** that names the pair and points at the ledger rows. That is a disclosure, not a restoration, and it changes no counter outcome. Text offered at `$OUT/proposed-log-append.md` — **proposal only, not applied** (lane files are read-only for this seat).

## 6. Calibration findings (the axis this seat is judged on)

* **F1 — premise confirmed, exactly.** "The five `revert` rows are those lines": yes, the five substantive ones, verified twice (independent hash recomputation and the tool's `held`/`disclosed` split).
* **F2 — the loss is 5 lines, not 7 or 8.** The seventh deletion is an EOF-newline twin whose bytes never left, and one is a blank separator held by 300 other blank lines. `restored_max: 2` in the JSON counts those two — mechanically correct, but it reads like "two lines came back"; neither carries content. Worth one clause in any closure text that quotes the number.
* **F3 — the commit's larger half is ungraded.** `ed135b3c` deleted **12 lines of `HOURS.md`**, and `HOURS.md` is not in the contract: `registry/append-only-contract.tsv` has 11 lines / 10 rows and **0** `HOURS` matches, `registry/append-only-disclosures.tsv` has **0** `HOURS.md` rows, and the tool's event list for the commit contains only `LOG.md` (`$OUT/event-ed135b3c.json`, `$OUT/audit-full.json`). Yet HOURS.md line 3 self-declared "Append-only". So "the real LOG.md loss at `ed135b3c`" (round-50 closure R6, `tools/append-only-audit.py:5`, `tools/round51-append-audit-v6-check.py:10`) undercounts the commit by 12 lines and by the one file that called itself append-only. This is not a counter defect — v2+ grades the contract, and the contract is the lane's declaration — and **no fix is proposed**: adding a retroactive `HOURS.md` row now would make the counter grade a removal the lane deliberately intends, and would demand a 12-line `removal` disclosure for a file that must not come back. Record it as a declared scope boundary if the lane wants it in `corpus/lessons/round-51.md`.
* **F4 — `held` is a multiset measure, so a re-appearing string is "restored".** For LOG.md (300 blank lines at tip) any single blank-line deletion is always `held`; a substantive line that happens to duplicate text elsewhere in the file would be held too and never disclosed. Benign for this event (the duplicated text is a byte-identical line the revert re-added), but a real property of v6 to keep in mind when a whole-file-graded file is large and repetitive.
* **F5 — authorship is separable by identity alone.** `ci <ci@local>` vs the lane's `kama-shokunin <kama@shokunin.local>` cleanly splits canon commits from round-log commits in this lane, so "who wrote the lost line" is answerable from `git log` without reading content — useful for any future closure that needs to decide restore vs disclose.

## 7. Confidence

| claim | confidence | basis |
|---|---|---|
| 7 lines deleted, 2 held, **5 lost**, ledger rows = those 5 | **high** | independent recomputation of the v6 definition + tool event `disclosed/undisclosed[]` + hash match; reproducible via `$OUT/held-recompute.py` |
| canon/operator-authored, not lane-authored | **high** | identity split, self-label "Operator seed", wording derived from fleet PROTOCOL §Craft-hours 89 s earlier |
| removal intended at the "withdraw the canon" level | **high** | tree-exact inverse pairs in both repos, same actor, 9-minute sequence |
| removal of the LOG hunk *specifically* considered | **medium — inference** | no message/note names LOG.md; the fleet's "fully reverted everywhere" statement is retrospective (`f47ad6ba`, 2026-10-25) |
| disclose (not restore) is correct | **high** | the bar is absent at both tips; v6 grades `disclosed`, counter met |

No llama-server was started; no pacman transaction or tool install was run. No defect in the frozen preregistration, counters, controls or ledger was found.

## 8. Paths written

* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss.md` (this report)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/held-recompute.py` + `held-recompute.out`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/deleted-lines.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/ledger-rows-ed135b3c.tsv`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/event-ed135b3c.json`, `audit-full.json`, `audit-header.json`, `audit-eventcount.json`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/c2-counter.out` (frozen C2 counter receipt at `4eca4892`, met=True, exit 0)
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/ed135b3c.diff`, `33b167ec.diff`, `ids.txt`
* `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/Rev1Loss/proposed-log-append.md` (proposal only, not applied)
