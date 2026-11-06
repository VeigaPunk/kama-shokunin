# Round 89 — verifier spot-check (non-author closure)

author: hyaku closure (non-author integrator, @m_zfl)
date: 2026-11-06
subject: kama round 89. Lane HEAD `68bb020864a5488c0d25bdf99bf3eba73a8b20d5`, base `56174a1fa6a27faa91d3664ef4730b48dd3149c0`, freeze `4eb75c62f6deb1a586a291d611b71775049b34a6`.
report: `.ufo/reports/round-89/kama.md` (fleet repo, commit `26f888453145c195896b2c37568aad271362059b`, author `kama-shokunin <kama@shokunin.local>`, 2026-11-06T17:35:29-03:00)

Verdict: status `ok`, **admitted**. Both declared claims verify on their frozen predicates, re-measured live by this
closure (not only from receipts); no owned axis is harmed; the admit/reject sample agrees with the lane's gate.

Dispatch digest (`.ufo/watchdog.log`, mutable; copied):
`2026-11-06T16:37:39-03:00 launch kama round=89 pgid=652941 driver=hyaku-inline attempt=1` /
`2026-11-06T17:36:39-03:00 complete kama round=89; hyaku-inline attempt=1`.

## 1. Conformance (protocol step 1)

| check | command / source | observed | result |
|---|---|---|---|
| report committed by lane identity | `git log --format='%an %ae %H %cI' -- .ufo/reports/round-89/kama.md` | `kama-shokunin kama@shokunin.local 26f88845… 17:35:29` | ok |
| report lands after lane tip | `git log --format='%h %cI' 56174a1f..68bb0208` | tip `68bb0208` 17:34:08 < report 17:35:29 | ok |
| SHONEN heading, one line per box | report `## SHONEN`; `grep -c -E '^\s*- \[[ x~]\]' SHONEN.md` → `4` | 4 lines, all `[~]` with pointers, no `[x]` | ok |
| cited commits exist and are ancestors of `master` | `git cat-file -t <h>`; `git merge-base --is-ancestor <h> refs/heads/master` for `56174a1f 4eb75c62 4f9eacf7 21b9e36d c8db8586 5b1e0fb3 0d751aab 0f539b45 83297283 68bb0208 138a7543 9b4c7af1` | all `commit`, all ancestors | ok |
| lane pushed, no leftovers | `scripts/hyaku/jj-lane.sh state …/kama-shokunin`; `git status --porcelain`; `git ls-remote origin refs/heads/master` | `ahead=0 behind=0 tracked=0 untracked=0`; porcelain empty; remote `68bb0208…` | ok |
| fleet repo leftovers | `git status --porcelain` (fleet root) | ` M .scratch/run15-state.json`, `?? .scratch/run15-wrapup/…` (orchestrator-owned) | ok |
| prompt carries contract | `.ufo/prompts/kama-round-89.md` (923 lines, commit `98762e4e` by `kama-shokunin`) | §1 MISSION/AXES, §2 claims, §2b frontier step + census command, §3 L2 floor, §4 report contract, §5 commit/push/L0, §6 hyaku addendum | ok |
| counters frozen | `git show <r>:tools/round89-{unloadable-cells,signature-rows}.py \| sha256sum` at `4eb75c62 4f9eacf7 21b9e36d 5b1e0fb3 0f539b45 68bb0208` | `1d86194c27740a8a…` / `30f3af7fb9778024…` at every revision; only `tools/kama-probe.sh` changed (`99dd1ab8` → `a4f496bb` → `c15ffca8`) | ok (K3 not triggered) |
| source census | `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` | exit 0, `kama ok`; non-W04 warning only the pre-existing W01 on S481 | ok |
| census before → after | awk over committed `corpus/SOURCES.md` at base and tip | rows 322 → 326; tier A 307 → 311, B 11, C 4; mined 288 → 291, queued 8, rejected 26 → 27 | matches report |

Conformance defects (status-neutral):

- **D1** Terminal gate red on `round75-instruments` (`bad_rows=19`; `measured/gate-final.out` `PRE_REPORT round=89 arms=14 failed=1`). Carried from r87 R4 / r88 D3; cause now located (EX04) and an L0 question filed (`.ufo/l0-questions.md:381`). Status-neutral under §Gate standard, Closure consequence.
- **D2** `measured/harm-final.out` lines 14–27 carry `error: command not found: bc`, so the per-call seconds column of the operator-router rows is missing. The verdict/reason columns and the median `LATENCY` lines are intact; the receipt is degraded, not false.
- **D3** The probe is ~1.8× slower on the operator router (median 0.136 s → 0.251 s for a pinned id, 0.138 → 0.362 s for `*`; `harm-final.out` `LATENCY`). Disclosed by the lane, outside the frozen K2 harm rule; I do not grade it harm (sub-second GET probe, verdicts unchanged), but it is a cost that should carry a budget pin.

## 2. Claim re-checks

Method: **re-measured** = I ran it myself at the named revision against the committed bytes, with live lane-owned b12177 children where the counter requires them (scratch `/fast/scratch/hyaku/kama-r89-closure`, removed afterwards). The counters are round claim counters, not registered gates; the lane's pre-report gate was **not** executed — its committed receipt `measured/gate-final.out` was evidence-verified (D1).

### C1 — operability: unloadable router model files

Predicate: `python3 tools/round89-unloadable-cells.py --repo . --rev <M> --work <scratch>` → `cells=11 mismatches=0 positive_mismatches=0`, exit 0, counter bytes unchanged since freeze.

Re-measured:

```
$ python3 tools/round89-unloadable-cells.py --repo . --rev 68bb020864a5488c0d25bdf99bf3eba73a8b20d5 --work $S/w
ROUTER_UNLOADABLE cells=11 mismatches=0 positive_mismatches=0 probe=rev probe_sha256=c15ffca8f6b4…cc73238 server_sha256=ba272ee3…b362b0 rev=68bb0208…   exit=0
$ python3 tools/round89-unloadable-cells.py --repo . --rev 56174a1fa6a27faa91d3664ef4730b48dd3149c0 --work $S/w
U1-missing-preset / U2-not-gguf / U3-bad-header / U4-truncated-half / U5-deleted-after-list: oracle=MODEL_UNLOADED http=500 probe=MODEL_OK ok=0
ROUTER_UNLOADABLE cells=11 mismatches=5 positive_mismatches=0 probe_sha256=99dd1ab8…   exit=1
```

Reported: base `5/0` exit 1, M `0/0`, M′ `0/0` — **match** (tip probe bytes = M′ bytes `c15ffca8`). Evidence-verified:
forgeries F1 `3/3`, F2 `7/2` (`controls/c1-f1.out`, `c1-f2.out`, probe hashes match `138a7543`/`9b4c7af1`).

Harm conjunct (K1/K2):

- K1 `positive_mismatches=0` at tip — re-measured above.
- `tests/probe-verdicts/check.py` re-measured at tip: `tests=77 passes=77 failures=0`, exit 0 (72 base rows + 5 new `RouterUnloaded` rows); lane tree still clean afterwards. Base 72/72 evidence-verified (`controls/harm-base-probe-verdicts.out`); `harness-r5.out` shows the 3 `router-model-*` rows fail on the base probe, so the new rows discriminate.
- `test-snapshot.sh` 30/0, r88 oracle cells 0 mismatches, r88 frozen router-cells `mismatches=2` (C05, C12) — identical at base, M, M′ (evidence-verified, `controls/harm-base-*.out`, `measured/harm-M.out`, `measured/harm-final.out`).
- Operator router 1234 (GET only): `MODEL_OK router-unloaded-autoload` for all four ids at base, M, M′ (evidence-verified).
- Held-out (EX01, `measured/heldout-Mprime.out`): `cells=13 AGREE=3 FIX=6 INDETERMINATE=1 LIMIT=3`, no cell where base is right and M′ wrong.

Ruling: **verified**. Axis operability: **improved** (a known false green on autoload routers now matches the runtime's own answer; no frozen harm).

### C2 — depth: router error signatures bound to wire answers

Predicate: `python3 tools/round89-signature-rows.py --repo . --rev <M2>` → `rows=8 bound=8 unbound=0 duplicates=0`, exit 0.

Re-measured:

```
$ python3 tools/round89-signature-rows.py --repo . --rev 56174a1f…   → SIGNATURE_ROWS rows=0 bound=0 unbound=0 duplicates=0   exit=1
$ python3 tools/round89-signature-rows.py --repo . --rev 21b9e36d…   → SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0   exit=0
$ python3 tools/round89-signature-rows.py --repo . --rev 68bb0208…   → SIGNATURE_ROWS rows=8 bound=8 unbound=0 duplicates=0   exit=0
```

The receipt is a writable file (CR02's disclosed limit), so I recaptured it independently from live b12177 children:

```
$ python3 tools/round89-router-signatures.py --out $S/sig.jsonl --work $S/sw
ROUTER_SIGNATURES calls=9 build='version: 0.9.0-dev (build 12177, commit 6c01da627)'   exit=0
$ cmp $S/sig.jsonl .ufo/waves/round-89/measured/router-signatures.jsonl   → IDENTICAL (9 lines)
```

Reported values **match**. The counter binds endpoint/HTTP/message only (3 of 6 columns, disclosed); the trigger and verdict columns I spot-read against the receipt cases (`unloadable-file`, `unknown-id`, `missing-model-field`, `unloaded`, `unload-not-running`, `unload-unknown-id`, `load-unknown-id`, `load-already-running`) and found them consistent. Ruling: **verified**. Axis depth: **improved** (eight wire-bound rows reproduced byte-identically by a non-author; score held at 7 by the lane, which I do not change).

### Owned axes not claimed

`git diff 56174a1f 68bb0208 -- SCORECARD.md`: scores operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 — all unchanged; edits are the authority line, evidence pointers, two new capability rows (`router-unloadable-file-verdict`, `router-error-signature-table`), the `router-mode-readiness` re-point (r88 R2), §Planned (round 90) and §Round 89. No score lowered, no evidence pointer left dangling in the rows I read. freshness, coverage, calibration, adjacency: **unchanged**.

| axis | verdict | basis |
|---|---|---|
| operability | improved | C1 re-measured live, base 5/0 → tip 0/0; harm suites unchanged |
| depth | improved | C2 re-measured, 0 → 8 bound rows; receipt recaptured identical |
| freshness | unchanged | no claim; score 8 held |
| coverage | unchanged | no claim; score 9 held |
| calibration | unchanged | no claim; score 7 held |
| adjacency | unchanged | no claim; score 7 held |

## 3. Discernment spot-check (LEARNING.md)

Sample from `corpus/lessons/round-89.md` `## Gate`: two admits, one reject.

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S583 `tools/server/server-models.cpp` @ `6c01da62` | admit (A, code, mined) | `curl` raw URL; sha256 `cab14969…71108` = row; lines 1641/1956/1962 = `throw std::runtime_error("model name=" + name + " failed to load");`, `model '%s' not found`, `model is not loaded` | agree | The three oracle answers are in the source at the pinned build, and my live recapture shows the same wire messages. Quote present verbatim at line 1641, ≤25 words. |
| S584 `ggml/src/gguf.cpp` @ `6c01da62` | admit (A, code, mined) | `curl` raw URL; sha256 `51bd966a…5dd78` = row; line 512 `GGUFv1 is no longer supported, please use a more up-to-date version`; 511 `version == 1`, 515 `version > GGUF_VERSION` (`gguf.h:42` `#define GGUF_VERSION 3`), 679 `n_dims > GGML_MAX_DIMS`, 795 `ti.offset != ctx->size` | agree | The row's checks (v1 and >3 rejected, dims, exact running offset) are the loader's own; the probe rule mirrors what actually refuses a file. |
| S586 ggml `docs/gguf.md` @ `57e2c2ca` | reject | `curl` raw URL; sha256 `1dead27b…05020` = row; line 285 `// Must be \`3\` for version described in this spec, which introduces big-endian support.`; lines 147/334 speak of padding to alignment | agree | The loader accepts v2 (rejects only 1 and >3) and demands exact contiguity (`gguf.cpp:795`), so a spec-built rule would false-red v2 files; the held-out cell `06-version-2` (oracle `MODEL_OK`) confirms it empirically. Reject with a flip condition is right. |

Newly written `corpus/SOURCES.md` row re-opened: S583 (line 338) — quote `"throw std::runtime_error(\"model name=\" + name + \" failed to load\");" (line 1641)` is ≤25 words and present at that line of the fetched bytes. S586 (line 341) quote also located verbatim at line 285.

Census: `scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0, `kama ok`.

## 4. Trend verdicts

- **expansion: improved.** `corpus/knowledge/router-unloadable-model.md` covers ground the coverage map did not hold (pre-attempt unloadable entries are indistinguishable in the router listing), cites mined S583–S585 (all three verified above), and names its prior art; two capability rows added with re-runnable greens.
- **quality: improved.** Router readiness re-verified on the current release b12177 with my own live re-run; a known false green is now graded by the runtime's answer; the in-round CR02 SKILL row-2 correction landed (row now reads `router-unloaded-failed`). No admitted entry I read was found false.
- **discernment: improved.** This non-author spot-check agrees with the gate on 2 admits and 1 reject; the reject is additionally backed by a held-out live cell.

## 5. SHONEN (operator note; nothing promoted, no `[x]` written)

Box 1 (real decision tables/error patterns with sources) and box 2 (end-to-end task logged) are checkable by a non-author: I re-ran the C2 wire capture and the C1 live cells from the committed commands alone. Box 3 (executable without oral context): the `recheck:` commands in `router-unloadable-model.md` and SKILL ran unaided for me. Box 4 (no cross-domain bleed) I did not independently re-verify. Promotion stays operator-owned.

## 6. Routed defects (lane fixes next round)

- **R1** `round75-instruments` red (`bad_rows=19`), carried r87 R4 → r89 D1; awaiting the filed L0 answer on deleting 19 rows from `registry/append-only-late.tsv`. Keep it open until either the L0 answer lands or the audit's eligibility rule is fixed without an append-only rewrite.
- **R2** `measured/harm-final.out` timing column lost to a missing `bc` (D2): recompute in Python (or install `bc` and record it) and append a corrected receipt; do not rewrite the original.
- **R3** Probe latency rose ~1.8× (D3) with no persisted budget: add a pinned latency/step budget to a harm suite so a future slowdown is caught by a frozen rule rather than by a wave seat.
- **R4** SN01 F3 (no response-size cap on `/v1/models` and `/props`) and F4 (unsanitised ids), pre-existing, already in SCORECARD §Planned (round 90).
- **R5** Held-out LIMIT cells (chmod-000, split model with a missing shard, relative missing path) and the FIFO INDETERMINATE cell remain false greens; SC01's alias-pin `MODEL_MISMATCH` (present at base) is on the new frontier.
