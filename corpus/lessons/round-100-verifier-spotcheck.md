# Round 100 — non-author verifier spot-check (integrator, @m_zfl)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-08

Lane `kama`, round 100. Base `6776c667372a0da8635ebfbda6cbc92d8fb17304`; measured commit M (freeze)
`2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`; lane tip before this file's commit
`4094f58a40bd5141a1c791b0cf8771d27efbd016`. Report: `.ufo/reports/round-100/kama.md` (fleet repo).
I authored none of the round's files. The lane counters (`tools/round100-record-audit.py`,
`tools/round100-props-status.py`) were not executed (Gate standard: the integrator verifies committed
evidence, it does not run a sibling's gate); C1 was re-derived independently from committed bytes with a
plain git/python reimplementation of its nine checks; C2 was re-derived from the probe diff and probe
digests, with the counter receipts evidence-verified; sampled upstream sources were re-opened with `curl`.

Driver digest (`.ufo/watchdog.log`, copied): `2026-11-08T19:51:47-03:00 launch kama round=100
pgid=162159 driver=hyaku-inline attempt=1`; `2026-11-08T21:03:47-03:00 complete kama round=100;
hyaku-inline attempt=1`.

## Step-1 conformance

| Check | Command | Observed | Result |
|---|---|---|---|
| Report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-100/kama.md` (fleet) | `kama-shokunin e8305d90…` (committer 21:03:03 -03:00: after the last cited lane commit `4094f58a` at 21:02:48, before the 21:03:47 completion line) | pass |
| `SHONEN` heading, one line per box | `grep -c '^## SHONEN'` report; `grep -cE '^- \[' SHONEN.md` | heading 1; 4 report lines for 4 SHONEN.md boxes, all `[~]`, each with evidence and "author-asserted"/seat caveat | pass |
| Cited commits exist and are ancestors of `master` | `git merge-base --is-ancestor <h> master` for 6776c667 2e27e6f1 3626e06c 6d0e3abc 6ca78b26 630cb8ec c6a9b8e7 a8d4566d 4094f58a | all resolve and are ancestors; round commits authored `kama-shokunin` | pass |
| Lane pushed, clean | `scripts/hyaku/jj-lane.sh state …`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `local=remote=4094f58a… ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty; remote `4094f58a…` | pass |
| Prompt carries template contract | `diff <(sed -n 1,140p kimi-shokunin/templates/round-prompt.md) <(sed -n 1,140p .ufo/prompts/kama-round-100.md)` | only `{{LANE}}/{{ROUND}}/{{FLEET_ROOT}}/{{AXES}}` substitutions differ; §6 hyaku addendum, §7 scratch, §8 pre-file ledger follow (1002 lines); prompt committed 19:51:46, before the launch line | pass |
| Prefile ledger | `python3 scripts/hyaku/prefile-falsification.py --lane kama --round 100` | `PREFILE-FALSIFICATION: pass claims=2 rows=16 attack_seats=7 findings=0`, exit 0 | pass |
| Census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | `kama ok …/corpus/SOURCES.md`, exit 0 (W04 duplicate-url-across-scopes incl. S629/S630, one W01 on S481; warnings only) | pass |

Ledger adjudication: 16 rows (8 per claim) over all 12 seats; 10 `falsifies-wording` rows (C1: RV01, CR01,
EX02, SB01, SC01, SN01; C2: EX01, SB01, SC02, SN01), each naming `plans/round-100-amendment-1.md`. Every row's
escape is named in the amendment's "Not claimed" lists (C1: presence-only substrings, seat names, words/`#L`/
case/symbolic/nested pointer spellings, phrase minimality, self-bound revisions; C2: `-L`, `000`-as-200,
204/304, query-path read, 404/other non-200). No row is spurious or unreconciled; no row is
`falsifies-number`. Six neutral rows read as stated.

## Per-claim re-check

Measured commit `2e27e6f1`; `git diff --stat 2e27e6f1 4094f58a -- tools/` is empty (instrument and probe
bytes at tip = freeze). Both claims are filed as narrowed by amendment 1 (written after wave 1, before filing).

**C1 calibration — round-99 records corrected, revision-bound.** Re-measured (independent reimplementation) + evidence-verified.
- Heading `## Round 100 correction — round-99 records`: count 0/0 in SCORECARD/LOG at 6776c667; 1/1 at 2e27e6f1 and 4094f58a.
- Each block (22 lines) at M and at tip: contains `4 of 12 (33%)`, `6 of 12 (50%)`, `12 seats, 0 dead`; after removing bound
  tokens the only digit percentages are `['33%', '50%']`; unbound `SCORECARD.md:`/`LOG.md:`/lessons pointers: none; 5 bound tokens
  per block, each phrase found on the cited line at the cited revision (`SCORECARD.md@6776c667:6500` "58% attack",
  `LOG.md@6776c667:4065` "CN01Overlap (attack)", `SCORECARD.md@00394f3b:6431`, `SCORECARD.md@6776c667:6446`,
  `LOG.md@6776c667:4040` "10 reported, 2 dead" — all true).
- Substance: `.ufo/waves/round-99/w1-spec.json` roles → policy attack 4/12 (RV01Wording, RV02Counter, CR01Records,
  MT01Mutants), ledger attack 6/12 (+SN01Bounds, CN01Overlap); `w1-results.json` 12 results, 12 non-empty — the
  correction's numbers are true. `r99-measured.json` C1/C2/C3 values are each a line of the round-99
  `measured/c{1,2,3}.out` (the `CONTROL_POP99`/`RECORD_AUDIT99`/`AUTOLOAD_STATES99` summary lines; files end `exit=0`).
- Receipts: `measured/c1.out` `RECORD_AUDIT100 checks=9 mismatches=0 met=True rev=2e27e6f1…`, exit 0; `controls/c1-base.out`
  `mismatches=9 met=False`, exit 1; `controls/c1-forgeries.out` P0 rc=0, F1–F7 rc=1 (checks 5,7,8,9,4+5,6,8), `C1_FORGERIES cases=8
  wrong=0 met=True`; `controls/c1-at-tip.out` met at `6ca78b26`. Matches report and `claims.json`.
- Verdict: verified as narrowed. Axis **calibration: improved** (7 → 7; the move is the re-derivable correction, answering
  round-99 spot-check defects 1, 2 and 4).

**C2 depth — `/props` body read only on HTTP 200.** Re-measured (probe bytes) + evidence-verified (counter receipts).
- `git diff 6776c667 2e27e6f1 -- tools/kama-probe.sh`: `router_autoload()` now captures `pcode=$(curl … -w '%{http_code}' …
  "http://127.0.0.1:$port/props") || return 2` then `[ "$pcode" = 200 ] || return 2` before the size check and JSON parse; no `-L`;
  header cites S629/S630. `grep -c pcode` 0 → 3. Probe sha256 `05ebee88…` (base) → `23b26d76…` (M = tip), matching the receipts'
  `base_sha256`/`probe_sha256`; mutant bytes `controls/c2-mutant-blanket.probe.sh` sha256 `4e6a4214…` matches its receipt.
- Receipts: `measured/c2.out` `ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`, exit 0
  (S1–S7 `MODEL_UNLOADED/router-autoload-unread/2`, P1 `router-unloaded/2`, P2 `MODEL_OK/router-unloaded-autoload/0`);
  `controls/c2-base.out` `mismatches=6`, four false `MODEL_OK` exit 0 (S2, S4, S5, S6), exit 1; `controls/c2-mutant-blanket.out`
  `mismatches=2` (P1/P2), exit 1 — the counter can fail a blanket refusal; `controls/c2-regression-r99.out` `AUTOLOAD_STATES99
  cells=8 mismatches=0 met=True`, exit 0.
- `SKILL.md` at tip: sha256 `7f8eed74…`, 2536 lines (2511 at base), 61 `## ` headings, §Round 100 `/props` status rule (line 1837)
  and widened decision row (line 1773) — matches the SCORECARD depth cell.
- Verdict: verified as narrowed. Axis **depth: improved** (7 → 7).

No exploratory claim. `SCORECARD.md` diff 6776c667→4094f58a: axis scores unchanged (operability 8, freshness 8, depth 7,
coverage 9, calibration 7, adjacency 7); banner, depth/calibration evidence cells, `### Planned (round 101)`, correction block,
§Round 100 and two capability rows change. Axes reconciler green at tip (`controls/axes-reconcile-tip.out` `mismatches=0
met=True`); `round97-self-assessment-audit` `mismatches=1` at base and tip (unchanged, pre-existing). No axis harmed.

## Per-axis verdicts

| Axis | Verdict |
|---|---|
| calibration | improved |
| depth | improved |
| operability | unchanged |
| freshness | unchanged |
| coverage | unchanged |
| adjacency | unchanged |

## Discernment spot-check (`corpus/lessons/round-100.md` §Gate)

Re-opened 2026-11-08 with `curl -sL https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>`.

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S631 `tools/server/tests/unit/test_router.py` | admit | HTTP 200, 33 103 B, sha256 `fed2ff44…` (matches) | agree | line 20 `assert res.status_code == 200` precedes line 23 `assert res.body["models_autoload"] is False` (line 17 `server.no_models_autoload = True`); also answers round-99 defect 3 at the correct path. Caveat: a server test pins the status, it does not prescribe client gating — fine as corroboration beside S629/S630 |
| S629 `tools/server/server-http.cpp` | admit | HTTP 200, 39 157 B, sha256 `aad15b75…` (matches) | agree | lines 291/295 `res.status = 401;` + `"Invalid API Key"`, lines 315/319 `res.status = 503;` + `"Loading model"` — refusals carry non-200 status and an error document |
| README `tools/server/README.md` as source for "`/props` returns 200" | reject | HTTP 200, 136 429 B, sha256 `eafc1b53…` (matches) | agree | line 930 is the `/props` heading; the only "HTTP status code 200" (line 489) sits under `/health`; `grep -c models_autoload` → 0 |

SOURCES row re-opened: S630 (`tools/server/server-common.cpp`) — HTTP 200, 79 532 B, sha256 `b686729e…` (matches); line 93
`json format_error_response(const std::string & message, const enum error_type type) {` and line 95 `int code = 500;` exactly
as quoted; quote ≤25 words, located. Agree.

## Trend verdicts

- **expansion: improved** — a new decision rule in core (`SKILL.md` §Round 100, +25 lines), `corpus/knowledge/router-props-autoload.md`
  §Round 100, three admitted A-tier code rows S629–S631 (census 368 → 371, validate exit 0), two capability rows.
- **quality: improved** — four base cells that graded a false `MODEL_OK` now read `router-autoload-unread`; the round-99 record
  defects are corrected with revision-bound pointers that re-derive; the freeze-broken axes reconciler is green at tip.
- **discernment: improved** — all four sampled decisions agree on substance; the round-99 S628 path error is answered by S631 at the
  right path; the lane's own wave falsified both frozen wordings and the narrowing is on record before filing (KQ153–KQ155).

## Defects (status-neutral) and routed items for round 101

1. Both claims were frozen wider than their counters (lesson M5, the Amendment-59 class); the narrowed wordings are close to
   counter restatements. Round 101 must land the routed killer cells (302→200 target, closed port with seeded body, seeded 204/304,
   query-keeping stub; KQ155) and C1's pointer-grammar/seat-name/multi-word-phrase/self-bound-revision checks (KQ153) so the next
   claims can be stated at the width the code actually has.
2. The freeze (`2e27e6f1`) turned `tools/round41-scorecard-reconcile.py` red (`mismatches=3`) until the integration re-anchor
   (lesson M6): run the axes reconciler before freezing, not only at tip.
3. Pre-report gate `failed=2` carried: `newest-closure` (round-97 closure has no ISO date) and `round75-instruments`
   (`APPEND_DEBT … unaccepted=38 bad_rows=19`; L0 r87/r89 open). `round97-self-assessment-audit` stays `mismatches=1`.
4. MT01 survivors (C1M2–M6, C2M1/M6/M8) and the round-92 `D3` differential cell red since round-99 amendment 1 (`w1/SN01Bounds.md`)
   remain open.
5. Observation only: the freeze commit's author timestamp (19:50:58) precedes the launch line (19:51:47); its committer
   timestamp (20:01:46) is after launch — jj working-copy author time, not future-dated evidence.

SHONEN: all four boxes remain `[~]`, author-asserted; none is fully checkable by a non-author from this round's evidence.
