# Sc2Scoring — round 55 integration prose drafts (kama)

**Verdict: three adoptable drafts delivered (SCORECARD §Round 55, LOG round-55 entry, corpus/README frontier disposition), every quoted number traced to a committed receipt; while tracing them I found that the frozen C1 kill rule fires on its own terms (two of the four mutants the freeze names print `met=True`), so the drafts record C1 as "not discharged" and assert no admission — reported as defect D1, not fixed in place.**

## Method (read-only)

No counter, tool, replay or server was run. No file under the lane, fleet repo, or shokuknow was written; no git/jj state was mutated. Scratch `/fast/scratch/hyaku/kama-r55/w1/Sc2Scoring` was created empty and removed. No tool was installed (nothing needed). I started no `llama-server`; the two `llama-server` PIDs visible during the seat belong to peer `J5EnvNames` (`pgrep -af llama-server` → PIDs 3521908, 3523374, both under `/fast/scratch/hyaku/kama-r55/w1/J5EnvNames/`).

Commands run and what they established:

| Command | Observed |
|---|---|
| `git log --oneline -6` (lane) | tip `8abadfed`, freeze `9c60eae6`, base `3a600d2f`; `8abadfed` is the commit that adds `measured/*` and `c1/battery/*` |
| `git show --stat --oneline 9c60eae6` | freeze commit: preregistration, both counters, both base controls, `census/start.out`, S511 HTML copy, SOURCES/S510 used-by, `registry/cited-path-corrections.tsv`, `corpus/lessons/round-55.md` |
| `git show --stat --oneline 8abadfed` | 17 files: `measured/c1-build.out`, `measured/c2-build.out`, 7 battery `.out` + `run-battery.py`, `w1/spec.json`, `dispatch.json`, `validate.*`, `w1.ready` |
| `git show 9c60eae6:tools/round54-replay-code-audit.py \| sha256sum` | `c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af` — equals `preregistration.json:16` |
| `git show 9c60eae6:tools/round54-cited-path-check.py \| sha256sum` | `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` — equals `preregistration.json:27` |
| `grep -n '^tip=\|^bind=\|^fixture=\|newrow: \|dropped citation\|rehash b1:\|envnames b1:' <11 receipts>` | the line numbers every draft cites (`controls/base.c1.out:2,24`, `measured/c1-build.out:2,5,7,9,10,23,24`, `controls/base.c2.out:2,22`, `measured/c2-build.out:2`, `c1/battery/*.out:2`) |
| `python3 -c json.load(...w1/spec.json)` | `wave=kama-r55-w1`, `maxLanes=64`, `items=64` |
| `python3 -c json.load(MANIFEST.json)['rounds']` slice | index 812 → `round=67 lane=kumitate`; index 814 → `round=54 lane=kama lane_round=54` |
| quote cross-check script (exact line-2 strings of 10 receipts against the four drafts) | all ten `QUOTED`; re-run after fixing three abbreviated mutant cells: all `QUOTED` |
| `ls .ufo/waves/round-55/census/`; `git ls-tree 8abadfed -- .ufo/waves/round-55/census/` | only `start.out`; no `end.out` at HEAD or at `8abadfed` |

## Deliverables

| Draft | Path | Shape |
|---|---|---|
| SCORECARD §Round 55 | `.ufo/waves/round-55/w1/out/Sc2Scoring/SCORECARD-round55.md` | heading, authority paragraph with both counter hashes and the C2 BASE rationale, 5-column claim table matching round 53's shape, scores/capabilities line, exit-code provenance note, `### Kill-rule disposition (round 55)` (C1 four-mutant table + runner divergence; C2 discharge), `### What met=True does not show (round 55)` pointing at seat K3MetTrue plus the freeze's own `limits`, assimilation line |
| LOG round-55 entry | `.ufo/waves/round-55/w1/out/Sc2Scoring/LOG-round55.md` | heading, opening paragraph naming the round-54 wrap-up it answers (`.ufo/reports/round-54/kama.md` @ fleet `e2e2d10f`, lane tip `1406a91e`, MANIFEST `rounds` index 814 `rejected-honest-stop`, outside closure `corpus/lessons/round-54-verifier-spotcheck.md` @ `3a600d2f`, routed defects 1–5 + operator-owned 6), then C1, C2, C1-kill-rule, freeze/wave, census and lesson bullets in round-53's style |
| corpus/README frontier disposition | `.ufo/waves/round-55/w1/out/Sc2Scoring/README-frontier-round55.md` | `## Frontier disposition — round 55 (appended)`; moved-to-held-ground (3), not-shown (4), still-frontier, integration line |
| Proposed fix text | `.ufo/waves/round-55/w1/out/Sc2Scoring/proposed-errata.md` | append-only errata block for `corpus/lessons/round-55.md` + a next-freeze mutant-list option; explicitly forbids editing frozen artifacts |

## Evidence map (number → receipt:line → draft)

| Number(s) as drafted | Receipt | Draft |
|---|---|---|
| C1 base `bind=1 sealed=1 code=1 teardown=1 newrow=0 … rehash=0 met=False` | `controls/base.c1.out:2` | SCORECARD table, LOG bullet 1 |
| C1 build `… newrow=1 … met=True` | `measured/c1-build.out:2` | SCORECARD table, LOG bullet 1 |
| `newrow: 0 rows…[]` → `2 rows…['\| S511 \|']` | `controls/base.c1.out:24`, `measured/c1-build.out:24` | both |
| 8 archive files / 16 executable ranges / 13 root-owned host files | `measured/c1-build.out:5` (also `controls/base.c1.out:5`) | SCORECARD build-leg cell |
| 2 byte-identical passes over 16 range reads | `measured/c1-build.out:7` | SCORECARD build-leg cell |
| 3 binds, `child_pid` joined, nonce round-tripped | `measured/c1-build.out:9` | SCORECARD build-leg cell |
| `/memfd:llama-server`, seals 15, frozen digest | `measured/c1-build.out:10` | SCORECARD build-leg cell |
| teardown 3 descendants, port refuses | `measured/c1-build.out:23` | SCORECARD build-leg cell, README |
| C2 base `… dropped=1 met=False`; build `… dropped=0 met=True` | `controls/base.c2.out:2`, `measured/c2-build.out:2` | both |
| `dropped citation SCORECARD.md: corpus/lessons/round-52-verifier-spotcheck.md` | `controls/base.c2.out:22` | both, README |
| `superseded` row → `corpus/lessons/round-53-verifier-spotcheck.md` | `registry/cited-path-corrections.tsv:46` | both, README |
| 15 `fixture ok` lines, superseded pair at `:17`; 4 advisories `:18`–`:21` | `measured/c2-build.out:3-17,18-21` | both, README |
| `m-ldpreload` / `m-text-flip` / `m-member-flip` / `m-ldaudit-foreign` / `m-ldaudit-writable` / `control` line 2, all seven verbatim | `.ufo/waves/round-55/c1/battery/{control,m-ldpreload,m-text-flip,m-member-flip,m-ldaudit-foreign,m-ldaudit-writable}.out:2` | SCORECARD kill-disposition table + runner paragraph, LOG bullet 3, README |
| freeze mutant list = `m-ldpreload`, `m-ldaudit-writable`, `m-ldaudit-foreign`, `m-member-flip`; each named mutant must print `met=False`; falsified if any prints `met=True` | `preregistration.json:44`, `:19`, `:20` | SCORECARD, LOG, README, errata |
| 11 capabilities; axes 8/7 | `SCORECARD.md:57` (capabilities), `SCORECARD.md:12-19` (axes table) | SCORECARD closing line |
| wave `kama-r55-w1`, 64 lanes / 64 items | `.ufo/waves/round-55/w1/spec.json` | LOG bullet 4 |
| `census_start_exit=1`, `E11 S510 missing used-by corpus/lessons/round-54.md`, S511 at SOURCES line 264 | `census/start.out:102`, `:101`; `corpus/SOURCES.md:264` | LOG census bullet, README |

What the drafts deliberately do **not** assert: any exit code for a battery receipt (the receipts carry no exit, and `run-battery.py:146`'s summary was not committed); any admission for C1; any end-of-round census exit; any axis or capability change.

## Findings

### D1 (high) — the frozen C1 kill rule fires: two named mutants print `met=True`

- Where: `.ufo/waves/round-55/preregistration.json:19` ("kill battery: each named mutant receipt prints `met=False` (exit 1) with its named leg failing"), `:20` ("falsified … if any battery mutant prints `met=True`"), `:44` (`"mutants": ["m-ldpreload (envnames leg)", "m-ldaudit-writable (code leg)", "m-ldaudit-foreign (hostlibs leg)", "m-member-flip (rehash leg)"]`).
- Show it:
  ```
$ grep -H '^bind=' .ufo/waves/round-55/c1/battery/{control,m-ldpreload,m-ldaudit-writable,m-ldaudit-foreign,m-member-flip}.out
  .ufo/waves/round-55/c1/battery/control.out:bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
  .ufo/waves/round-55/c1/battery/m-ldpreload.out:bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=0/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=False
  .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out:bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
  .ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out:bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True
  .ufo/waves/round-55/c1/battery/m-member-flip.out:bind=1 sealed=1 code=1 teardown=1 newrow=1 bound=3/3 sealedruns=3/3 coderuns=3/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=3 met=False
  ```
- Secondary half of the same defect: the landed runner does not build the freeze's set. `run-battery.py:26,38,57,69` builds `m-ldpreload`, `m-text-flip`, `m-ldaudit-foreign`, `m-member-flip`; `m-ldaudit-writable` is absent, and `m-ldaudit-foreign` is reclassified `"vector"` (`:57-60`) with `ok = rc == 0 and met` (`:137`). The commit message of `8abadfed` ("kill battery green (3 live kills + 1 vector analysis)") describes the runner's reading, not the freeze's.
- Proposed fix: `proposed-errata.md` §1 (append to `corpus/lessons/round-55.md` §Errata, append-only — the frozen prereg and receipts stay) and §2 (next freeze declares each entry's expected outcome, and names `m-text-flip` for the `code` leg or supplies a non-root mutant that reaches `hostlibs`).

### D2 (low) — the freeze's MANIFEST index is wrong

- Where: `.ufo/waves/round-55/preregistration.json:8` — "the round-54 outside closure (MANIFEST rounds[812], …)".
- Show it: `python3 -c "import json;d=json.load(open('/home/vgpnk/Projects/shokunin/MANIFEST.json'))['rounds'];print([(i,d[i]['round'],d[i]['lane']) for i in (812,814)])"` → `[(812, 67, 'kumitate'), (814, 54, 'kama')]`.
- Impact: none on the claim; the closure file and commit cited in the same sentence are correct, and the LOG draft uses 814.
- Proposed fix: `proposed-errata.md` §1 third item (record the correct index; the frozen prereg is not edited).

### D3 (medium) — the lesson's battery sentence is contradicted by a receipt in the same directory

- Where: `corpus/lessons/round-55.md:75-76` — "each battery mutant receipt names the leg it kills".
- Show it: `sed -n '2p' .ufo/waves/round-55/c1/battery/m-ldaudit-writable.out` → `… hostlibs=3/3 anon=0 twopass=3/3 rehash=0 met=True` (names no failing leg); `m-extra-in-tree.out:2` also reads `met=True` (a vector note, not a mutant; `run-battery.py` does not build it).
- Proposed fix: `proposed-errata.md` §1 first item.

### D4 (low) — the lesson cites an end census receipt that does not exist

- Where: `corpus/lessons/round-55.md:101` ("After (round end): same command → exit 0 required (receipt `.ufo/waves/round-55/census/end.out`)") and `:95`.
- Show it: `git ls-tree 8abadfed -- .ufo/waves/round-55/census/` → only `start.out`; `ls .ufo/waves/round-55/census/` → `start.out`.
- Impact: the receipt is the round-end obligation, so this may be pending rather than false; the LOG draft therefore says "not committed at these two commits, so no end exit is claimed here". If the L1 lands `end.out` during integration, the LOG line should be updated then (one sentence), not before.

### Observation (not a defect) — C1's measured delta is bookkeeping

`controls/base.c1.out:2` already reads `bind=1 sealed=1 code=1 teardown=1 … bound=3/3 sealedruns=3/3 coderuns=3/3 … twopass=3/3 rehash=0` at the round-54 tip; the only leg that changes is `newrow` (`0` → `1`, the S511 source row). The drafts state this plainly so the section cannot be read as new served-identity evidence.

### Observation (not a defect) — routed defect 2's X5 half has no committed receipt yet

`corpus/lessons/round-54-verifier-spotcheck.md:79` (routed defect 2) asks for committed receipts for the X5 sabotage re-verification *and* the C2 fixture smoke. The C2 half is served by the counter's own fixture run (`measured/c2-build.out`, 15/15 scenarios at `8abadfed`) — that is the frozen counter's fifteen scenarios, not a re-run of the round-54 14/14 smoke; the X5 half is not: `git show --stat 8abadfed` lists no X5 receipt, and the only X5 artifacts on disk are a running seat's logs (`find .ufo/waves/round-55 -iname '*x5*'` → `.ufo/waves/round-55/w1/out/X5ReplaySelftest/sabotage-{c,d}-*.log`, untracked, wave seat `X5ReplaySelftest`). The LOG draft says "pending" rather than claiming it; if that seat lands, the sentence is the one to update.


## Touched surfaces

- Written (4 drafts + this report), all under `.ufo/waves/round-55/w1/out/Sc2Scoring/` and `.ufo/waves/round-55/w1/out/Sc2Scoring.md`.
- Read-only reads of the lane tree, `.ufo/waves/round-55/*`, `corpus/lessons/round-54-verifier-spotcheck.md`, `MANIFEST.json`, `.ufo/reports/round-54/kama.md`, `.ufo/watchdog.log`.
- No write to `SCORECARD.md`, `LOG.md`, `corpus/README.md`, `corpus/lessons/round-55.md`, `preregistration.json`, `measured/`, `c1/battery/`, `corpus/`, `registry/`, or any fleet-root file.

## Out of scope

Counter execution and re-verification (main agent / wave seats own it); admission or scoring (canonical judge); the L1's adoption and merge of the drafts into the three target files; the round-54 wrap-up defects beyond naming them; the operator-owned `ed135b3c` ruling.

## Artifact paths written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc2Scoring.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc2Scoring/SCORECARD-round55.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc2Scoring/LOG-round55.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc2Scoring/README-frontier-round55.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-55/w1/out/Sc2Scoring/proposed-errata.md`
