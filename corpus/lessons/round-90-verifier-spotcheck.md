# Round 90 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-06
subject: kama round 90. Lane HEAD `db247186b43e66f399cf277f13aa8748676cd90d`, base `99cdb4d6270455494dd27901efe84a0f3b342062`, freeze `6f6d7873dac936ba407398ce81b464d77d0fcf32`.
report: `.ufo/reports/round-90/kama.md` (fleet repo, commit `ab58f3e4652996003baa8def3fdf3c9968bdd065`, author `kama-shokunin`, committed 2026-11-06T18:43:36-03:00)

Verdict: status `ok`, **admitted**. Both declared claims verify on their frozen predicates, re-measured live by this
closure at every measured revision; no owned axis is harmed; the admit/reject sample agrees with the lane's gate.

Dispatch digest (`.ufo/watchdog.log`, mutable; copied):
`2026-11-06T17:41:55-03:00 launch kama round=90 pgid=950419 driver=hyaku-inline attempt=1` /
`2026-11-06T18:44:23-03:00 complete kama round=90; hyaku-inline attempt=1`.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %H' -- .ufo/reports/round-90/kama.md` | `kama-shokunin ab58f3e4…` (committed 18:43:36) | ok |
| prompt committed by lane identity | same for `.ufo/prompts/kama-round-90.md` | `kama-shokunin 1097dd77…` (17:41:53, before launch 17:41:55) | ok |
| report lands after lane tip | `git log --format='%h %cd' 99cdb4d6..db247186` | tip `db247186` 18:42:28 < report 18:43:36 | ok |
| SHONEN heading, one line per box | report `## SHONEN` | 4 lines, all `[~]` author assertions with pointers, no `[x]` | ok |
| cited commits exist and are ancestors of `master` | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> refs/heads/master` for `6f6d7873 f968fb19 2ee0b55f a09effae 1f8eed67 8f8211a2 f1b12a20 8213ed0a 546cb40c d45ede25 db247186 99cdb4d6` | all `commit`, all ancestors | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `ahead=0 behind=0 head=detached tracked=0 untracked=0`; porcelain empty; remote `db247186…` | ok |
| prompt carries contract | `.ufo/prompts/kama-round-90.md` (927 lines) | §1 MISSION/AXES, §2 claims, §2b frontier step + census command, §3 L2 floor, §4 report contract, §5 commit/push/L0, §6 hyaku addendum, §7 scratch | ok |
| round shape | prompt line 145 (8–16 seats, ≥25 % attack) vs report | 13 seats, attack 6/13, 0 dead, WAVE-DONE | ok |
| counters frozen (C1 K3, C2 K1) | `git show <r>:tools/round90-{hostile-answers,reason-rows}.py \| sha256sum` at `6f6d7873 f968fb19 2ee0b55f a09effae 1f8eed67 db247186` | `345b12b386bfa825…` / `fa4c31771783e533…` at every revision; probe `c15ffca8` → `c197912f` (M) → `b71c309a` (M′ = tip) | ok |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`; only non-W04 warning the pre-existing W01 on S481 | ok |
| census before → after | awk over committed `corpus/SOURCES.md` at base and tip | rows 326 → 331; tier A 311 → 315, B 11, C 4 → 5 | matches report |

Conformance defects (status-neutral):

- **D1** Terminal gate red on `round75-instruments` (`bad_rows=19`; `measured/gate-final.out` `PRE_REPORT round=90 arms=14 failed=1 uncommitted=0`, `# rev=d45ede25`). Carried from r87; L0 at `.ufo/l0-questions.md:381` still open. Evidence-verified, not executed (§Gate standard, Closure consequence).
- **D2** Freeze commit `6f6d7873` carries author date 17:40:52, one minute before the launch line (17:41:55); its committer date is 17:53:45. The author date equals the base commit's (jj stamps a change at creation), so this is a timestamp artefact, not pre-dispatch work.
- **D3** Answering models still absent from `w1-results.json` (r88 D4 class), disclosed by the lane.

## 2. Claim re-checks

Method: **re-measured** = run by me against committed bytes at the named revision (scratch `/fast/scratch/hyaku/kama-r90-closure`, removed afterwards; lane tree clean afterwards). The counters are round claim counters, not registered gates. The pre-report gate was **evidence-verified** only (D1).

### C1 — operability: hostile listener answers bounded

Predicate: `python3 tools/round90-hostile-answers.py --repo . --rev <M> --work <scratch>` → `cells=13 mismatches=0 positive_mismatches=0 probe=rev`, exit 0, counter bytes = freeze.

Re-measured:

```
--rev 99cdb4d6…  H1/H2/H3 ok=0 sent=67108864 verdict=MODEL_OK; H4 header_cols=9 empty_header_cols=2; H5 json=unparsed; H6 esc=1; H7 json=unparsed; H8 table_rc=2 json=unparsed
                 HOSTILE_ANSWERS cells=13 mismatches=8 positive_mismatches=0 probe_sha256=c15ffca8…  exit=1
--rev f968fb19…  HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=c197912f…  exit=0
--rev a09effae…  HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=b71c309a…  exit=0
--rev db247186…  HOSTILE_ANSWERS cells=13 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=b71c309a…  exit=0
```

Reported: base `8/0` exit 1, M `0/0`, M′ `0/0`, tip `0/0` — **match**. Forgeries F1 `6/5`, F2 `9/1`, F3 `7/1` evidence-verified from `controls/` (frozen with the plan).

Harm (K1/K2):

- K1 `positive_mismatches=0` at M, M′, tip — re-measured above.
- `tests/probe-verdicts/check.py` re-measured at tip: `tests=77 passes=77 failures=0`, exit 0.
- `tools/round89-unloadable-cells.py --rev db247186` re-measured: `cells=11 mismatches=0 positive_mismatches=0 probe_sha256=b71c309a…`, exit 0.
- `test-snapshot.sh` 30/0 and operator router 1234 `MODEL_OK router-unloaded-autoload`: evidence-verified (`measured/harm-final.out`; no `command not found` lines this round).
- Held-out: `repair/rv01-matrix-base-M-Mprime.out` (Mp hash `b71c309a…` = committed M′ probe). At M three rows were harm (`badutf8server` base `MODEL_OK` → M unparsed; `big401` base `UNAUTHORIZED_SERVICE` → M `FOREIGN_SERVICE`; `router-ctlid-loading` base exit 2 (JSON unparsed, the report's table reading `MODEL_LOADING`) → M `MODEL_OK` exit 0). At M′ the three read `MODEL_OK/matched`, `UNAUTHORIZED_SERVICE/http-401`, `MODEL_LOADING/router-loading`. Every other M′≠base row is a base defect (unparsed JSON, raw ESC, `MODEL_OK` on 64 MiB) or `props-big`, which is frozen cell H3. EX01 at M: HARM 0 (`w1/EX01HeldOutCells.md`).

Ruling: **verified at M′** (`a09effae`, the final measured commit; tip probe bytes identical). The predicate also held at M, but M carried held-out harm the wave found; the repair landed in-round and re-measures clean, per the r89 precedent. Axis operability: **improved**.

### C2 — depth: probe reason codes bound to captured answers

Predicate: `python3 tools/round90-reason-rows.py --repo . --rev <M2>` → `population=23 documented=23 … unbound=0 missing=0 duplicates=0`, exit 0.

Re-measured:

```
--rev 99cdb4d6…  REASON_ROWS population=23 documented=0 rows=0 bound=0 unbound=0 missing=23 duplicates=0 receipt=absent  exit=1
--rev 2ee0b55f…  REASON_ROWS population=23 documented=23 rows=24 bound=24 unbound=0 missing=0 duplicates=0 additional=1 receipt=current probe_sha256=c197912f…  exit=0
--rev 1f8eed67…  same counts, probe_sha256=b71c309a…  exit=0
--rev db247186…  same counts, probe_sha256=b71c309a…  exit=0
```

Receipt independently recaptured (CR02's limit: the counter trusts any receipt carrying the right probe hash):

```
$ python3 tools/round90-reason-capture.py --repo . --rev db247186… --work $S/cw --out $S/reason-cells.jsonl
REASON_CAPTURE cells=24 probe_sha256=b71c309a…  exit=0
$ cmp $S/reason-cells.jsonl .ufo/waves/round-90/measured/reason-cells.jsonl   → IDENTICAL (24 lines)
```

K2 (trigger text vs receipt cell): I read all 24 rows of `SKILL.md` §"Probe reason codes"; each row's verdict and cell match its receipt line, and the triggers agree with the stub cells' names and the rc mapping (7/28/52/56/63). No contradiction found. Ruling: **verified**. Axis depth: **improved** (score held at 7 by the lane; not changed by me).

### Owned axes not claimed

`git diff 99cdb4d6 db247186 -- SCORECARD.md` (+133/−7): axis scores operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 at both ends. The 7 removed lines are the authority banner, the depth/coverage/calibration evidence pointers (re-pointed to round 90 / the r89 closure), saturation and mirror lines; two capability rows added (`hostile-answer-bounds`, `probe-reason-table`); no row deleted, no score lowered.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured live: base 8/0 → M′/tip 0/0; harm suites unchanged; held-out M harm repaired at M′ |
| depth | improved | C2 re-measured: 0 → 24 bound rows; receipt recaptured byte-identical |
| freshness | unchanged | no claim; score 8 held |
| coverage | unchanged | no claim; score 9 held |
| calibration | unchanged | no claim; score 7 held |
| adjacency | unchanged | no claim; score 7 held |

## 3. Discernment spot-check (LEARNING.md)

Sample from `corpus/lessons/round-90.md` `## Gate`: two admits, one reject. All fetched with `curl -sfL` this session.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S587 curl `max-filesize.md` @ `curl-8_23_0` | admit (A, docs, mined) | raw.githubusercontent URL; sha256 `4bbc00ec…ea038f` = row; lines 34-35 "Starting with curl 8.4.0, this option aborts the transfer if it reaches the threshold during transfer." | agree | Pinned to the host's curl (`curl --version` → 8.23.0); my C1 re-run shows the 64 MiB cells stop at the cap and grade `FOREIGN_SERVICE`, the behaviour the doc states. |
| S588 RFC 8259 §7 | admit (A, spec, mined) | rfc-editor `rfc8259.txt`; sha256 `61a5378f…cd2d7` = row; lines 429-431 "…the control characters (U+0000 through U+001F)." | agree | Normative MUST that the base `jstr` broke; base H5 is `json=unparsed` in my re-run. |
| S591 curl `max-filesize.d` @ `curl-8_3_0` | reject (C) | raw URL; sha256 `c9e9489b…418a2b` = row; quote "for such files this option has no effect even if the file transfer ends up being larger than this given limit." present (starts end of line 21, runs 22-23) | agree | It describes pre-8.4.0 curl, the opposite of the installed behaviour; keeping it only as the reason for the written-size re-check, with a flip condition, is the right call. |

Newly written `corpus/SOURCES.md` rows re-opened: S590 (line 345) — `return CURLE_FILESIZE_EXCEEDED;` at line 291 of `lib/sendf.c` @ `curl-8_23_0` (sha256 `deb44efc…bfb51` = row), after the `failf` "Exceeded the maximum allowed file size" at 288; ≤25 words. S589 (line 344) quote present at RFC 8259 lines 485-486.

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, `kama ok`.

## 4. Trend verdicts

- **expansion: improved.** `corpus/knowledge/probe-answer-bounds.md` covers ground the coverage map did not hold (the probe's own answer boundary; the prior `snapshot-history.md:51` rule is cited as prior art), cites mined S587–S590 (all re-opened above, digests equal), and two capabilities with re-runnable greens were added.
- **quality: improved.** Three base defects (64 MiB answer graded `MODEL_OK`, unparseable `--json` on control bytes, table column forging) are fixed with failing-before controls I reproduced; the wave-found M harm was repaired and re-measured clean. KQ145 is grounded in lesson M4. No admitted entry I read was found false (D-routed R2 below is a stale pointer, not a false fact).
- **discernment: improved.** This non-author spot-check agrees with the gate on 2 admits and 1 reject; the new criterion KQ145 comes from a mined wave disagreement (M4).

## 5. SHONEN (operator note; nothing promoted, no `[x]` written)

Box 1 (decision tables with sources) and box 2 (end-to-end task logged): checkable by a non-author — I re-ran the C1 cells, the C2 capture and both harm suites from committed commands alone. Box 3 (executable without oral context): the capture/counter commands in SKILL §"Probe reason codes" ran unaided for me and reproduced the receipt byte-for-byte. Box 4 (no cross-domain bleed) not independently re-verified. Promotion stays operator-owned.

## 6. Routed defects (lane fixes next round)

- **R1** `round75-instruments` red (`bad_rows=19`), carried r87 → r90 D1; open until the L0 answer lands or the eligibility rule is fixed without an append-only rewrite.
- **R2** `corpus/knowledge/probe-answer-bounds.md` `verified-at:` names the M probe `f968fb19` / `c197912f…`, which carried held-out harm; the shipped probe is M′ `a09effae` / `b71c309a…`. Append a dated correction re-pointing verified-at (body line 39 already names the repair).
- **R3** Held-out cell `router-esc` prints reason `router-?` at M and M′ (a router status value with a control character collapses to `?`): a printed reason outside the 23-code population and the SKILL table. Either escape it as text or document it as a row.
- **R4** r89 R3 latency budget: the lesson routes it to seat EX02 (≤10 % latency measured), but no persisted budget pin entered `tests/` or `tools/` this round (`git diff 99cdb4d6 db247186 -- tests tools | grep -ci 'budget\|latency'` → 0). Still open.
- **R5** Counter limits disclosed by the lane and carried to SCORECARD §Planned (round 91): C1 counter satisfied by other implementations (1 MiB cap, no `jstr` loop, rc 63 → `DEAD`); wire bound needs curl ≥ 8.4.0; no time bound (SN01: 207 s for a 4 MiB answer of 200k ids, present at base); C2 counter binds hidden/blank rows and any receipt with the right probe hash.
- **R6** r89 R5 held-out LIMIT cells and alias pins: not worked, carried.
