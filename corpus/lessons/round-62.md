# Round 62 lesson — kama (2026-10-28, attempt 2)

Claims: C1 operability — lane-owned live `/v1/completions` request plane (`tools/kama-completion-live.py`); C2 calibration — 12-capability self-assessment bound to live re-execution (`registry/capability-claims-r62.tsv`). Freeze `.ufo/waves/round-62/controls/freeze.txt`, base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`.

## Gate

| Source / candidate | Accessed | Located quote (≤25 words) | Verdict |
|---|---|---|---|
| S526 `https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md` | 2026-10-28 | §POST `/v1/completions`: “Given an input `prompt`, it returns the predicted completion.” (README line 1316) | **admit** — tier A pinned-build docs; new route scope not held by S035/S112, grounds `completion-request-plane.md`; response fields are separately marked observed, not docs-backed |
| `considerthese/2026-10-26.md`, suggestion 3 | 2026-10-28 | “Keep a running count of counters that a shortcut can satisfy” | **reject/defer** — this round's eight C2 families are a one-round measurement, not the proposed longitudinal tally of shortcut controls, surviving mutants and falsify-wave outcomes; flip: publish a per-round aggregate that carries those counts across rounds and names the frozen source counters |
| `merge/kama/` staged package | 2026-10-28 | not opened as admitted evidence this round; r61 spot-check quarantined the entire seven-row kama slice as payload-absent | **reject/defer** — no staged entry appended; flip: hand-check every candidate against its cited source and locate the quote before adoption |
| Round-62 outside spot-check | 2026-10-28 | pending WAVE-DONE; this lane's seats do not count as non-author | **pending** — no gate admission is claimed until a fresh non-author closure re-opens at least one admit and one reject |

SOURCES registry census at start: `.ufo/waves/round-62/census/start.out`; 265 rows, exit 0, with existing duplicate-URL W04 and used-by W01 warning classes. New S526 opened directly from the pinned b11755 README; raw file SHA-256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`. `considerthese/2026-10-26.md` was opened directly; proposal 3 is deferred rather than re-adopted because this round's count is not longitudinal. Package adoption remains closed.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| `attribution` — attempt 1 stopped on a generic wrap-up notice before freezing or filing; exact watchdog line `.ufo/watchdog.log` 2026-10-28T08:59:38-03:00 says `lane-dead-no-report kama round=62` | none | `KQ47` (attempt/restart history must be recorded) | attempt 2 re-verified inherited drafts and executed the complete freeze → wave → report path; the failure is explicitly named in this lesson/report |
| `vacuous` — C1 counter's tamper control body-hash mismatch made `cap()` return `None`, then `grade()` crashed at `cj.get('usage')` instead of grading the malformed receipt as rejected | `.ufo/waves/round-62/measured/c1-before-fix.txt` | none | guard nested usage/timings reads with `(cj or {})`; keep the frozen predicate unchanged; the same tamper family then rejects 8/8 and C1 reaches `met=True` |
| `reference-drift` — C1 counter tested for a nonexistent `checks['hold']` key, while the tool emits `checks['hold_released']`; the round's live receipt was rejected with `unexpected-checks` despite every check passing | `.ufo/waves/round-62/measured/c1-hold-key-before-fix.out` | `KQ20` (each graded check must have a distinguishing failure) | gate on the actual `hold_released` key; fresh nonce-bound remeasurement yields `live_ok=1/1`, `errors=0`, `met=True` |
| `reference-drift` — `kama-live-replay.py --selftest --scratch <nonexistent-dir>` called `tempfile.mkdtemp(dir=root)` before creating `root`, raising `FileNotFoundError` | `.ufo/waves/round-62/measured/kama-live-replay-scratch-red.out` | none | `os.makedirs(root, exist_ok=True)` before `mkdtemp`; repeat gives `KLR_SELFTEST pass=48 fail=0` |
| `number-drift` — adding the completion tool introduced a new SHA-256 citation for the pinned b11755 server binary, but the digest ledger did not classify it | `.ufo/waves/round-62/measured/digest-ledger-before.out` (`unknown=1`, exit 1) | `KQ50` (digest inventory at landed tip) | append an `external` row after re-hashing the installed binary; flip demonstrated by the final scan at the committed row's tip, `unknown=0`, exit 0 |
| `vacuous` — `round62-c2-counter.py` sensitivity calculation replaces every occurrence of its own pattern before checking for the same pattern; for any nonempty pattern, `pattern in out.replace(pattern, MUT)` is false by construction, so `sensitive` is always true and the declared sensitivity predicate is not demonstrated | `tools/round62-c2-counter.py` lines 265–271 (pre-wave code) | `KQ20` (sensitivity needs a detector that fails when comparison is removed) | **open defect** — do not claim semantic sensitivity or calibration credit from that conjunct; wave attack A05C2Sensitivity must independently confirm. Frozen predicate must not be amended after data; closure must treat C2 as not verified if the frozen sensitivity conjunct is false/vacuous |

Attempt 1 leftovers reused after re-verification: `.ufo/waves/round-62/controls/c1-base.txt`, `c2-base.txt`, census start, and assimilation ID/collision scratch. Attempt 1's tool/counter drafts were re-read and smoke-tested; no unreviewed scratch was inherited. The non-authored `.ufo/scopes/kama-r57-w1/swarm-registry.json` remains untouched.

## Sources opened this round

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md — fetched 2026-10-28; S526, §POST `/v1/completions`, line 1316 quote above.
- `considerthese/2026-10-26.md` — opened 2026-10-28; suggestion 3 quote above.
- `/home/vgpnk/Projects/shokuknow/merge/kama/` was not modified; the staged package remains deferred/quarantined per the r61 spot-check.

## Wave results

Pending WAVE-DONE. Wave `w1` is a single policy-v2 wave with 64 seats (32 attack-role seats); results handoff will be recorded here after the orchestrator settles it.
