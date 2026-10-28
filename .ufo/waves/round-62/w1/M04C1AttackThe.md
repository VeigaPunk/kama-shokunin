# M04C1AttackThe — C1 counter falsification, log family (capture-body sha256)

Seat: mutation-tester, round 62 w1 · Tip: `65d7cad0fce90e34de37527cde22e97b63b118bf`
(`git rev-parse master` at attack time) · Date: 2026-10-28 · Lane: kama-shokunin.
Scratch: `/fast/scratch/hyaku/kama-r62/w/M04C1AttackThe` (deleted before yield; evidence
copied to `.ufo/waves/round-62/w1/out/M04C1AttackThe/`). No verdict on the claims is
issued; findings are observed bytes and outputs only.

## Method

- `tools/round62-c1-counter.py` loaded from the tip via `git show master:…` (blob saved to
  scratch, exec'd verbatim as detector **D0**). `score()`/`grade()` also transcribed
  verbatim into `bin/reproduced_counter.py` and cross-checked: reproduction matched the
  tip module on every scoring call (`reproduction_matches_tip: true` in logs).
- Receipts: (a) measured live receipt `.ufo-wave` counter output
  `/fast/scratch/hyaku/kama-r62/measure/c1b/receipt.json`
  (sha256 `568f762731d10a2465b39999ebbdb80b792e5d50aa42d1fdf9f63ae67ad650d6`), and
  (b) a fresh genuine receipt produced by running the tip counter itself
  (`--work` in scratch; live leg ran on an unregistered loopback port):
  `counter-run/receipt.json` (sha256 `86259357e6db7b49cc625050743934be9401d8896…` — full
  hash below), nonce `r62-8eb8b407e7`, port 41709, pid 1449053. All capture bodies
  re-hashed clean on both receipts.
- Witness for `score()`: reconstructed canonically from receipt fields (pid/port/fingerprint
  `b11755-704366d76`/alias/model+server digests, nonce-bound prompt `r62-…  under the`),
  held fixed across the battery so every delta is attributable to the receipt mutation.

## Finding F1 — the committed counter cannot produce its recorded output (baseline inconclusive)

Running the committed tip counter end-to-end (`--repo <lane> --tip <tip> --work
<scratch>`): **exit 1, stdout empty, traceback** (`counter-run-stderr.txt`):

```
  File "…/round62-c1-counter.py", line 440, in main
    s = score(ctl, witness)
  File "…/round62-c1-counter.py", line 191, in score
    recomputed, inconsistent = grade(receipt)
  File "…/round62-c1-counter.py", line 130, in grade
    u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

Two independent structural causes, both confirmed on raw blob bytes:

1. **Schema guard mismatch** — line 165: `if 'hold' in (receipt.get('checks') or {})`.
   The companion tool stores the hold check as `checks['hold_released']`
   (`kama-completion-live.py:408`); `checks['hold']` never exists, so `hold_released` is
   never recomputed, `required` (16 names) ≠ `stored` (17 names) →
   `inconsistent=['unexpected-checks']` → `score().met=False` for **every** genuine
   hold-mode receipt. D0 on the pristine measured receipt:
   `{'alltrue': True, 'inconsistent': ['unexpected-checks'], 'live': True, 'met': False, 'verdict_ok': True}`.
2. **Unguarded captures** — lines 130 and 139 (`u = cj.get('usage') or {}`,
   `t = cj.get('timings') or {}`): the counter's own `tamper` family item 1 rewords the
   completion body, `cap()` then returns None, `cj` is None → AttributeError at line 130
   (had that been guarded, line 139 crashes next). `main()` has no guard around the
   control loop, so the process dies mid-battery and the summary line
   (`tool_present=… met=True`) is unreachable from these bytes.

Minimal repair set (scratch copy only, **D1**; exact diff in
`out/M04C1AttackThe/counter-repaired.py` vs `bin/round62-c1-counter.py`):

```diff
-    if 'hold' in (receipt.get('checks') or {}):
+    if 'hold_released' in (receipt.get('checks') or {}):
…
-    u = cj.get('usage') or {}
-    t = cj.get('timings') or {}
+    u = (cj.get('usage') or {}) if isinstance(cj, dict) else {}
+    t = (cj.get('timings') or {}) if isinstance(cj, dict) else {}
```

D1 on the same genuine receipt: `{'met': True, 'alltrue': True, 'verdict_ok': True, 'live': True, 'inconsistent': []}`
— i.e. those 3 lines are exactly the delta between the committed bytes and the recorded
claim behavior. D1 replays the counter's full 16-control battery **16/16 rejected**
(fake 2/2, hold 1/1, log 1/1, outside 1/1, predead 1/1, sigterm 1/1, stale 1/1, tamper 8/8):
the repairs do not neuter the detector. Per mutation-tester protocol the baseline failure is
recorded as **inconclusive instrument state**, not as a killed anything.

## Forgery battery (detector D1; ACCEPTED = forged receipt still scores met=True)

Target: fresh genuine receipt. For every ACCEPTED row the score() output was
**byte-identical to the pristine receipt's score** (`D1_delta_vs_pristine: {}`) — grading
is blind. Mutant files + sha256s in `out/M04C1AttackThe/mut/` and `attack_log2.jsonl`.

| id | mutation | verdict |
|----|----------|---------|
| R1 | `captures.health.body` reworded, sha NOT recomputed (counter's own log control) | REJECTED (`health_ready` False) |
| M1 | `captures.completion.error` set — capture claims the POST errored | **ACCEPTED** |
| M2 | `captures.completion.body_truncated=True` — graded bytes not the full server answer | **ACCEPTED** |
| M3 | `captures.bad_request.status` 400→500 (both inside the graded set) | **ACCEPTED** |
| M4 | adds `captures.server_log_tail` with a forged `llama-server build b11755` line (self-consistent sha) | **ACCEPTED** |
| M5 | `captures.health.status` 200→503 | REJECTED |
| M6 | `teardown.waited_ms` 3→999999 | **ACCEPTED** |
| M7 | `teardown.sigterm_sent` True→False (child never signalled) | **ACCEPTED** |
| M8 | `server_log` → `/nonexistent/forged/server.log` (cited log nonexistent) | **ACCEPTED** |
| M9 | `argv` → `["/bin/true","--forged"]` (pinned-server launch line forged) | **ACCEPTED** |
| M10 | `request.prompt` → `FORGED PROMPT 2+2=` (captured body is the answer to a different prompt) | **ACCEPTED** |
| M11 | `at` → `2019-01-01T00:00:00.000Z` | **ACCEPTED** |
| M12 | `checks.listener_owned.passed` True→False | REJECTED (grade derives this check *from* the stored value) |
| M13 | `completion`+`completion2` `choices[0].text` → `" FORGED-TEXT"`, both `body_sha256` **recomputed** (matched hash, wrong bytes) | **ACCEPTED** |
| M14 | `health` body → `{"status":"FAIL"}` + re-hash | REJECTED |
| M15 | `models` body `data[].id` → `["other"]` + re-hash | REJECTED |
| M16 | `child_pid` → 999999 | REJECTED (live leg binds pid) |
| M17 | `nonce` → `r60-deadbeef` | REJECTED (stale) |
| M18 | `model.sha256` → `0`×64 | REJECTED |
| M19 | `server.sha256` → `0`×64 | REJECTED (also `live` False) |
| M20 | `verdict` → `FAIL` | REJECTED |

## ACCEPTED falsifications, verbatim (required reporting)

All 11 ACCEPTED mutants produce this score() output, identical to the genuine receipt's:

```json
{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
```

- M1 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — mutant sha256 `087ef2554e9f56ba6f7dfde18713f0eecfc4fc401c3cbdb5481550c00243332f`
- M2 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `2b29c0335cadf7dc5d8e26810fb684900007b53182b48d9f5f4ebe6c1d954c43`
- M3 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `67aa2708d2d0c6b609dd0772bb6291d694b95f1975d9f236981bb10a00886f07`
- M4 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `d6ff1bc9cd740d68fce8a4a7cfe949e34573a800726f04d942f90dfa1950b982`
- M6 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `77fea9e71b5cd174ffd89cc6bf72cacae15d0cf49da8180a835eec23304bc354`
- M7 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `58705ab7f0261a512c258f879010a72f956809009837f6204105a5bf1f34c6e9`
- M8 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `2835d09659198cb543810cae1e73c00fa896d977b86425a664693eb077d0edd7`
- M9 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `f658becabcde8b261514c3affe8c75f5273c8abc9d2071b35bc6c322b1144260`
- M10 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `48bd78fb3b0ec43c4fddc0a806c6fd2dd3c4387dcdfda2bf77199bebd281491a`
- M11 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `6feb7f7f0b6deba9bfd8bb128235c19d1a0ce095f0d3a0a32601d130d3d1fd7b`
- M13 `{"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}` — `0bce06d00773f96bbfbddbf30e0f0e3994719401ceb5f0aad5ba88c54026619d`

## Reading

- The counter hash-verifies only `captures.<name>.body` vs its recorded `body_sha256`, and
  the hash lives inside the same attacker-writable receipt: M13 shows a re-hash forgery of
  the graded completion text sails through, and `score()` never compares its own live
  `witness.text` to the captured text, so the outside nonce leg binds model/fingerprint/
  digests/pid/port but **not captured content**.
- Entirely ungraded, unhashed receipt surface (blind): `argv`, `at`, `request.*`,
  `server_log`, `teardown.sigterm_sent/waited_ms`, per-capture `status` of `bad_request`
  (any value in {400,500}), `error`, `body_truncated`, and any extra `captures` entries
  (only `checks` is schema-checked, not `captures`).
- `checks.listener_owned` is not recomputed at all: `grade()` takes it from the stored
  value (M12 shows the derivation direction), so a fabricated receipt self-certifies it;
  only the counter's own live `port_owned_by` observation keeps it honest at runtime.
- Detector channels that do bite: health body/status, models id, listener_owned stored
  value, pinned model/server digests, pid/port/nonce binding, verdict string, and any
  body/sha mismatch (R1, M5, M12, M14–M20).

## Evidence inventory (`.ufo/waves/round-62/w1/out/M04C1AttackThe/`)

`receipt-c1b-measured.json` (568f7627…), `receipt-counter-run.json` (86259357e6db7b49cc625050743934be9401d8896 prefix — full: `86259357e6db7b49cc625050743934be9401d8849c3293c816966b18c20e874a`), `counter-run-stdout.txt` (empty),
`counter-run-stderr.txt` (traceback), `attack_log.jsonl`, `attack_log2.jsonl` (full battery
with per-mutant hashes), `counter-repaired.py` (D1), `attack_driver2.py`,
`reproduced_counter.py`, `mut/R1.json … mut/M20.json` (21 mutants).

## Hygiene

- Tools installed: **none** (python3 stdlib only; no pacman, no downloads).
- Writes: this report, `out/M04C1AttackThe/*`, scratch only. No git/jj mutation anywhere;
  lane and measure bytes read-only — c1b receipt hash unchanged before/after
  (568f7627… both checks), fresh receipt re-scored `met=True` on restored bytes.
- Scratch `/fast/scratch/hyaku/kama-r62/w/M04C1AttackThe` deleted after evidence copy.

```
M04C1AttackThe: tip=65d7cad0 committed_counter_end_to_end=CRASH(AttributeError grade:130) exit=1 stdout_empty D0_pristine_met=False[unexpected-checks] D1_minrepairs=3 controls=16/16 mutants=21 accepted=11 rejected=10 accepted_delta_vs_pristine=0 errors=0
```
