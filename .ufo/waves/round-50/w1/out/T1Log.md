# T1Log — round-50 LOG entry draft and build-state findings

**Verdict: the `## Round 50` LOG entry is drafted at `.ufo/waves/round-50/w1/out/T1Log/log.md` (ready to append to `LOG.md`); it records both claims' motivating evidence, the build, the freeze and the build-time battery, with explicit placeholders for the measured commit — and three integration-blocking findings surfaced while grounding it (F1 hexrun `unknown=1` traced to a fleet-repo commit cited as lane evidence; F2 the head calibration run line is stale at `35` vs 36 and fails two reconcilers; F3 the battery's last three legs have no receipt).**

## 1. Deliverable

`.ufo/waves/round-50/w1/out/T1Log/log.md` — the draft `## Round 50` section for `LOG.md`, in the shape of the round-49 entry (`LOG.md:2324`–`:2338`): two claim bullets (C1 operability 8→8, C2 calibration 7→7) with per-seat motivating evidence, one freeze bullet, one build/build-fix/wave/battery bullet, one routed-defects bullet, a `**Round-50 measured results:** pending` paragraph with fill-in cells, and the `- Lesson:` line.

Nothing in `LOG.md` was edited: the draft is a separate file, as the seat requires. Proposed head-row edits (F1, F2 below) are given as exact old/new text, not applied.

## 2. What I observed directly

Scratch `S=/fast/scratch/hyaku/kama-r50/T1Log`; one `git clone --shared` of the lane at `$S/lane` (`git rev-parse --show-toplevel` → `/fast/scratch/hyaku/kama-r50/T1Log/lane`); every tool run below used `--repo .` **inside that clone**, so the lane working tree and index were never touched.

| # | Command (cwd `$S/lane`) | Output | Exit |
|---|---|---|---|
| 1 | `sha256sum tools/round50-replay-bind-audit.py tools/round50-append-audit-v5-check.py` | `ff6ac2ace541ea35a4d240ceebb019653c11a2a08c025e514770f3f94a9c5e89`; `925f07a48a02ad54a9c89230aac7e54c8dafee4ba2e8a823dcb851b9cf48ca46` — equal to `preregistration.json` `claims[*].counter_sha256` | 0 |
| 2 | `python3 tools/hexrun-census.py scan --repo . --rev 97c864be… --details` | `tokens=1858 distinct=305 lane_oid=198 md5_blob=1 upstream_ok=94 unverifiable=9 wrong_flagged=2 ledger_bad=0 unknown=1`; the unknown token is `detail: f8cdb853aaff29393faeb0b6d4c2a2296778b698 len=40 occurrences=1 class=unknown` | 1 |
| 3 | same at the battery tip `3b79eadd… --details` | identical summary; same unknown token | 1 |
| 4 | `python3 tools/sources-append-only.py --repo . --from 26ecba64… --to 3d42897b…` | `added S496 (allowed)` / `added S497 (allowed)` / `added S498 (allowed)` / `no append-only violations` | 0 |
| 5 | same at tip `3b79eadd…` | identical | 0 |
| 6 | `python3 tools/append-only-audit.py --repo . --to 3b79eadd…` | `summary commits=330 files=94 events=5 restored=5 partial=0 unrestored=0 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 unmatched=0 binary=0 bad_declarations=0`; the `0718b6ab` SCORECARD.md event is `deleted=2421 graded=2349 ungraded=72 … restored` | 0 |
| 7 | `git cat-file -e f8cdb853aaff29393faeb0b6d4c2a2296778b698` (lane clone) | no object (`fatal: Not a valid object name`) | 1 |
| 8 | `git log --oneline -- .ufo/reports/round-49/kama.md` (lane clone) | empty; `ls .ufo/reports/` → `round-5` only | 0 |
| 9 | `git -C /home/vgpnk/Projects/shokunin cat-file -e f8cdb853…^{commit}`; `git show --stat f8cdb853…` (fleet repo, read-only) | object present: `f8cdb853aaff29393faeb0b6d4c2a2296778b698 kama-shokunin <kama@shokunin.local> 2026-10-26 21:00:10 -0300 round-49: kama report`; `.ufo/reports/round-49/kama.md \| 81 +` | 0 |
| 10 | `git show --stat 97c864be`, `git show --stat 601c8889`, `git log --format=%H` | build `97c864be…` 5 files +238/−53; freeze `601c8889…` 9 files +2402; fix `3d42897b…`; battery `3b79eadd…` | 0 |
| 11 | `ls .ufo/waves/round-50/measured/` | 18 receipts + `measure.sh`; **no** `r48c2`, `r49c1`, `r49c2` receipt although `measure.sh:37`–`:39` runs them | 0 |

Raw receipts of runs 1–8: `.ufo/waves/round-50/w1/out/T1Log/censuses.out` and `.ufo/waves/round-50/w1/out/T1Log/hexrun.out` (each records the command, the UTC date, the clone path and the exit code).

Consequences I draw from rows 1–11 and use in the draft: the freeze hashes still equal the preregistration at the battery tip; the lane's append-only state at the battery tip is exit 0 with five `restored` events and `ungraded_lines=89`; the Sources guard accepts S496–S498 after `3d42897b`; and exactly one cited hex run at both the build and the battery tip is unexplained.

## 3. Values I only read (committed receipts, not executed by me)

I ran **neither** round-50 claim counter. Every claim value in the draft is a committed receipt's bytes:

| Receipt | Value used | Note |
|---|---|---|
| `.ufo/waves/round-50/measured/c1-build.out` | `bind=1 teardown=1 newrow=1 bound=3/3 met=True`; pids 2876695/2920026/2958773 on ports 40197/41321/35623, mapping `dev 103:05` inodes 1082269665/613853333/1149932363; `teardown: … after 0.10 s alive [] port refuses ok`; `newrow: 3 rows new since base; 1 name proc_pid_maps(5): ['\| S496 \|']` | `tip=97c864be…`; **no `exit=` line in the file** (the draft therefore claims `met=True`, not an exit code) |
| `.ufo/waves/round-50/measured/c2-build.out` | `fixture=1 lane=1 scenarios=12/12 met=True`; per-scenario event dicts; `lane: tool exit 0 events 5 bad_declarations 0 regressed 0 ungraded_lines 89`, `dd9f5dc6c0e6 ungraded 17 <= 23`, `0718b6abbda6 ungraded 72 <= 72` | `tip=97c864be…`; no `exit=` line |
| `.ufo/waves/round-50/controls/base.c1.out` | `bind=0 teardown=0 newrow=0 bound=0/3 met=False`; canary in the server parent, `model_mapping None`, planted `sitecustomize` imported once, `after 30.06 s alive [531059, 568483, 573554] port ACCEPTS` | `tip=26ecba64…`; no `exit=` line |
| `.ufo/waves/round-50/controls/base.c2.out` | `fixture=0 lane=1 scenarios=9/12 met=False`; `order-b FAIL exit 1 (want 0)`, `fence FAIL exit 0 (want 1)`, `crlf-launder` `ungraded=25` (want graded 25); lane `ungraded_lines 82` | `tip=26ecba64…`; no `exit=` line |
| `.ufo/waves/round-50/freeze/prereg-time-check.out` | `RESULT pass`, `committer_time=2026-10-26T21:20:51-03:00`, one timestamp at/before it | `exit=0` present |
| `.ufo/waves/round-50/census/start.out` | 93 `W04`, 1 `W01`, `exit=0` | last line |
| `.ufo/waves/round-50/measured/*-build.out` (battery) | capability `listed 11 observed 11 missing 0 unsubstantiated 0 met True`; `AOA_SELFTEST pass=36 fail=0`; `KLR_SELFTEST pass=23 fail=0`; live `selftest: ok`; `check-receipt` `16 VALID and 1 NOT-EVALUATED … 107 mutations + unreadable case rejected`; digest `unknown=0`; planned-pointer `met=True`; gate `registered 44 unregistered 2 defective 0 exit=1`; `round41 … mismatches=1 met=False exit=1`; `round42 … mismatches=1 met=False exit=1`; `round43 … unreg=2 selftest=1 spot=1 mismatches=4 met=False exit=1`; hexrun `unknown=1 exit=1`; sao `error … unterminated table row … exit=2` | every receipt carries its `tip=` line; `sao-build.out` is measured at `97c864be`, i.e. **before** the `3d42897b` fix |
| `.ufo/waves/round-50/preregistration.json` | claim statements, predicates, targets, `frozen_at_utc`, base, kill conditions, limits, the seven named ablation controls | the contract |
| `.ufo/waves/round-50/w1/spec.json`, `w1/validate.out`, `w1/dispatch.json` | 66 seats; roles executor 22, reviewer 10, scribe 10, critic 6, connector 5, mutation-tester 4, scout 4, sentinel 3, revenger 1, simplifier 1; `spawn 66` | role counts computed by me from `spec.json` items' `role` field |

Durations (`46 s` / `5 s`) are **not** in any receipt; the draft omits them rather than repeat the lane prompt's figures as measured.

## 4. Findings

### F1 — one cited hex run is a fleet-repo object: `hexrun-census` is exit 1 at the build and at the battery tip

- Where: `corpus/lessons/round-49-verifier-spotcheck.md:21` — the conformance row reads `` … → one commit: `kama-shokunin <kama@shokunin.local> \| f8cdb853aaff29393faeb0b6d4c2a2296778b698 2026-10-26 21:00:10 -0300 round-49: kama report` `` and calls it pass.
- What it shows: `f8cdb853…` is the round-49 report commit in the **fleet** repository (`git show --stat` row 9 above: `.ufo/reports/round-49/kama.md`, 81 lines). In the lane it is not an object (row 7) and the path it names does not exist (row 8: the lane tracks only `.ufo/reports/round-5/kama.md`). A lane reader who re-runs the row's own command in the lane gets zero commits, and `tools/hexrun-census.py` classifies the run `unknown` because its class vocabulary has no cross-repo class (row 2/3: `unknown=1`, exit 1; the build receipt `measured/hexrun-build.out` agrees, `exit=1`).
- Proposed fix (integration-owned, append-only): append one row to `registry/hexrun-ledger.tsv`, seven TAB-separated fields, class `unverifiable` with a ≥10-character note, e.g.

  ```
  f8cdb853aaff29393faeb0b6d4c2a2296778b698	unverifiable				2026-10-27	fleet repo shokunin commit, round-49 kama report (.ufo/reports/round-49/kama.md, 81 lines, author kama-shokunin 2026-10-26 21:00:10 -0300); absent from the lane repo, whose .ufo/reports holds round-5 only
  ```

  and append (never rewrite) one sentence to the round-49 lesson or to the round-50 lesson's citation note saying which repository the hash belongs to. The class name is a misnomer for a real commit found in the sibling repo; the alternative is a new ledger class, which is a tool change, not a ledger row. Verify with `python3 tools/hexrun-census.py scan --repo . --rev <tip>` expecting `unknown=0` and exit 0.

### F2 — the head calibration run line is stale: `35` where the tree holds 36, so two reconcilers read `met=False` at the build

- Where: `SCORECARD.md:18` — `run \`python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"\` → \`35\` (outside closures on record)`; the same cell names `latest outside closure \`corpus/lessons/round-48-verifier-spotcheck.md\``. The tree holds 36 (`ls corpus/lessons/*verifier-spotcheck.md | wc -l` → 36; the 36th is the round-49 closure).
- Showing command: `python3 tools/round41-scorecard-reconcile.py` → `… run_bad=1 … mismatches=1 met=False` (exit 1), detail `run … no stdout line == '35' (exit 0)` (`.ufo/waves/round-50/measured/r41-build.out`); `python3 tools/round42-selfdesc-reconcile.py` → `r41=1 … mismatches=1 met=False` (exit 1) (`.ufo/waves/round-50/measured/r42-build.out`); `python3 tools/round43-registry-audit.py` carries the same fact as `spot: calibration row states 35, tree holds 36` (`.ufo/waves/round-50/measured/r43-build.out`).
- Proposed fix (head-row re-derivation, allowed for `## Axes`; the replaced text must be appended under `SCORECARD.md` §Superseded head banners per the round-48 rule): in `SCORECARD.md:18` replace `` → `35` (outside closures on record) `` with `` → `36` (outside closures on record) `` and `` latest outside closure `corpus/lessons/round-48-verifier-spotcheck.md` (admitted; re-anchored round 49) `` with `` latest outside closure `corpus/lessons/round-49-verifier-spotcheck.md` (admitted; re-anchored round 50) ``. Then both reconcilers and the round-43 audit's `spot` leg should read 0 for this fact. If the counters are frozen and the measured commit is taken before the edit, the round-50 measured paragraph must state `round41/round42 met=False` rather than claim green.

### F3 — the build battery's last three legs have no receipt

- Where: `.ufo/waves/round-50/measured/measure.sh:37`–`:39` run `r48c2` (`tools/round48-live-replay-v5-audit.py`), `r49c1` (`tools/round49-replay-witness-audit.py`) and `r49c2` (`tools/round49-append-audit-v4-check.py`); `ls .ufo/waves/round-50/measured/` (row 11) holds no `r48c2*.out`, `r49c1*.out`, `r49c2*.out`.
- What it costs: whether the round-48 v5 replay counter and both round-49 counters still pass when the v5 audit tool and the isolated replay replace their subjects is **unobserved** at the battery tip. `[INFERENCE]` The two round-49 counters are likely to be sensitive here: `tools/round49-append-audit-v4-check.py` recomputes v4 while the tool now grades v5 (the round-49 build already saw this class: `ungraded_lines tool=82 counter=89`), and `tools/round49-replay-witness-audit.py` observes a replay whose live child now runs under `python -I` with a reduced environment. Neither reading is a measurement.
- Proposed fix: either run those three legs at the battery tip and commit their receipts (the round-50 measured `measure.sh` will run them again at the measured commit, so this is cheap to fold in), or delete the three lines with a note that the round-49 counters are superseded — leaving them in `measure.sh` without receipts reads as "green" when nothing was run.

### F4 — the preregistration's seven ablation controls do not exist yet; only the two base controls are committed

- Where: `.ufo/waves/round-50/preregistration.json` `controls` names, for C1, no env allow-list, no replay parent-death signal, no `model_mapping` record and a decoy replay copying the original `child_pid`, and for C2 v4 fence-blind sections, byte-exact origin keys and v4 first-in-rev-list origin; `ls .ufo/waves/round-50/controls/` holds `base.c1.out` and `base.c2.out` only.
- What it costs: the claim's kill condition is "met=True on any control". Until those seven receipts land as `met=False`, the build proves the mechanism is present, not that each claimed mechanism is load-bearing. The wave's seats are exercising exactly these (J1NoEnv, J2NoPdeathsig, J3NoMapping, J4Decoy, J6Ablation, X11ModelSwap, X14FenceLane), so the receipts are in flight; the LOG draft deliberately leaves them as placeholders instead of asserting them.
- Proposed fix: commit the seven ablation receipts under `.ufo/waves/round-50/controls/` with their `met=False` lines before the measured commit, and let the measured paragraph cite each by file.

### F5 — re-observed, pre-existing: the gate selftest is documented as `pass=6 fail=0` and runs `pass=5 fail=1`

- Where: `tools/gate-registry-check.py` prints `GATE_SELFTEST pass=N fail=M` (`:354`); `round43-registry-audit.py` reads the documented pair from SKILL.md and compares — detail `selftest: documented 'GATE_SELFTEST pass=6 fail=0', run printed 'GATE_SELFTEST pass=5 fail=1' exit 1` (`.ufo/waves/round-50/measured/r43-build.out`). This was already recorded in round 43 (`LOG.md`, round-43 C1 bullet) and has not changed; I note it only so the round-50 measured paragraph does not present `round43 met=False` as new damage.

## 5. Limits of this seat

- No round-50 claim counter was run (neither C1 nor C2); no section-4 claim value is mine.
- No llama-server, replay or live tool was started by me; `pgrep -af "llama-server|kama-live-replay|kama-llamacpp-live"` shows processes only under sibling scratch roots (`/fast/scratch/hyaku/kama-r50/X8WitnessPort`, `…/X1Observe2`, `…/X12Zip`) — not mine, and not touched.
- No network fetch, no `gh` call, no install, no `pacman`; no service started or stopped.
- The lane was read-only: no `git add/commit/checkout/stash/reset`, no `jj` invocation; `git status --porcelain` in the lane shows only untracked wave-seat output, and the fleet-root repo showed a clean status (I wrote nothing there).
- The scratch clone `$S` and the hexrun stderr capture lived only under `/fast/scratch/hyaku/kama-r50/T1Log` and were removed at the end (see §7).
- The draft's claim statements are the preregistration's and the receipt's, not an independent re-derivation; its file:line pointers were each read in the tree at `3b79eadd`.

## 6. Out of scope here (other seats / integration)

`SKILL.md` instrument-registry rows for the two counters, `SCORECARD.md` §Round-50 measured results and head rows (except F2's exact proposal), `corpus/lessons/round-50.md`, `corpus/QUALITY.md`, `README.md`, PROVINCE, the wave's own reports and results, and the measured commit itself. The `used-by` cell of S496–S498 already names `corpus/lessons/round-50.md`; that lesson's landing is not mine.

## 7. Paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T1Log/log.md` — the draft `## Round 50` entry.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T1Log/censuses.out` — commands, outputs and exit codes for runs 1, 4, 5, 6, 7, 8.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T1Log/hexrun.out` — `hexrun-census --details` at `97c864be` and `3b79eadd` (runs 2, 3), including the unknown token's detail line.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T1Log.md` — this report.

Scratch `/fast/scratch/hyaku/kama-r50/T1Log` (shared clone + captures) removed.
