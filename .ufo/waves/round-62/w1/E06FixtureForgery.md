# E06FixtureForgery — round 62 v2 wave (kama)

Scope: hand-built receipt forgeries fed to `score()` of
`tools/round62-c1-counter.py`, plus the instrument-provenance consequence that
falls out of feeding them. Axes: operability + calibration.
Lane tip measured: `65d7cad0fce90e34de37527cde22e97b63b118bf`
(`git rev-parse master` == `HEAD`); frozen base of record `a959fd90` read from
`.ufo/waves/round-62/controls/freeze.txt`.
I edited no lane source. My only writes: this report and
`.ufo/waves/round-62/w1/out/E06FixtureForgery/`.

## Instrument provenance (read this before the table)

Two different bytes call themselves "the round-62 C1 counter" at this tip:

| instrument | bytes | authentic receipt | full counter run |
|---|---|---|---|
| committed tip blob `git show 65d7cad:tools/round62-c1-counter.py` | sha256 `275610b51eb1be21…f4d8d` | **REJECTED**, `inconsistent=["unexpected-checks"]`, `live=true` | **crashes**, no tally, exit 1 (`tip-counter-run.txt`) |
| lane worktree `tools/round62-c1-counter.py` (3 uncommitted edits, not mine) | sha256 `a3498308938ed471…8c415` | ACCEPTED, `met=true` | `tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True` (`wt-counter-run.txt`) |

The three divergent lines (tip → worktree, identical logic otherwise):

- `:130` `u = cj.get('usage') or {}` → `u = (cj or {}).get('usage') or {}`
- `:139` `t = cj.get('timings') or {}` → `t = (cj or {}).get('timings') or {}`
- `:165` `if 'hold' in (receipt.get('checks') or {}):` → `if 'hold_released' in (...)`

`score()` results below are therefore reported per instrument. The worktree
column is the one that can grade an authentic receipt at all; the tip column is
what a verifier pinned to the committed tip actually gets.

## Method

1. Staged the tip-pinned instruments into my scratch root exactly as the counter
   does (`git show 65d7cad:tools/kama-completion-live.py`,
   `tools/kama-llamacpp-live.py`, `registry/endpoint-consumers.tsv`), loaded both
   counter byte-sets as modules, and reused the counter's own `post()`/`grade()`.
2. Ran **one authentic hold-mode lifecycle** of the pinned tool (nonce
   `r62-d86c9fe6b5`, model sha256 `270cba1b…256d`, server sha256 `b6a31a8e…cd804`,
   unregistered loopback port `34969`, child pid `965906`, hold dir inside my
   scratch). During the hold I took the counter's witness shape **and** one
   second real `POST /v1/completions` with a different prompt (`A dog ran to the`
   → text `" park with"`, genuinely captured, distinct from the receipt's
   `" ground. She liked"`).
3. Kept the authentic receipt JSON and **hand-edited copies** of it (sha256
   recomputed wherever a body changed), then fed each copy to
   `score(receipt, witness)` with that **real** witness — never a forged witness
   (that is peer seat A03C1WitnessSpoof). `score(authentic, witness)` returns
   `met=true` on the worktree instrument, so every REJECTED below is a
   discrimination, not a setup fault.
4. `grade()`'s recomputed map and `score()`'s `alltrue`/`live`/`inconsistent`
   fields are the judges, as in the counter.

Commands (scratch root `/fast/scratch/hyaku/kama-r62/w/E06FixtureForgery`, explicit
`TMPDIR` inside it): `python3 forge.py` (lifecycle + a/a2/b/c), `python3 forge_d.py`
(synthetic receipt), `python3 forge_e.py` (self-consistent b2/c2), `python3 forge_f.py`
(tip-vs-worktree matrix + fixture e), `python3 counter-tip.py|counter-wt.py --repo
<lane> --tip 65d7cad… --work <scratch>`. No tool installed, upgraded or removed; no
pacman transaction; nothing created in any PATH directory.

## Results — the three required fixtures (a, b, c)

Judged with `score()`; "worktree" = sha `a3498308…`, "tip" = sha `275610b5…`.

| fixture (file, sha256 of JSON) | forgery | worktree | tip blob |
|---|---|---|---|
| a. `a_verdict_fabricated_real_failing_body.json` (`88c2be1d…`) | `completion2` replaced by a **real** second capture whose text differs, `completion_deterministic` recorded truthfully as failed, `verdict` forged to `REQUEST_OK` | **REJECTED** `alltrue=false` (only `completion_deterministic`), `inconsistent=[]`, `verdict_ok=true`, `live=true` | **REJECTED** `alltrue=false`, `inconsistent=["unexpected-checks"]` |
| b. `b_capture_bodies_reordered_across_keys.json` (`78a5d396…`) | `health`↔`models` bodies exchanged, each `body_sha256` recomputed (log gate passes), all stored checks forged true, verdict `REQUEST_OK` | **REJECTED** `alltrue=false`, `inconsistent=["health_ready","models_alias_id"]` | **REJECTED** `alltrue=false`, `inconsistent=["health_ready","models_alias_id","unexpected-checks"]` |
| c. `c_nonce_matches_alias_differs.json` (`32644aaf…`) | nonce unchanged (matches verifier), served alias changed to `kama-completion-other` in `completion`, `completion2`, `models`, `props`; shas recomputed; checks forged true; verdict `REQUEST_OK` | **REJECTED** `alltrue=false`, `live=false`, `inconsistent=["models_alias_id","props_alias","completion_model_id"]` | **REJECTED** `alltrue=false`, `live=false`, same three + `unexpected-checks` |

**Required three: 3/3 REJECTED on both instruments.**

### Supplementary fixtures (same channel, same witness)

| # | fixture | worktree | tip blob |
|---|---|---|---|
| a2 | `a2_verdict_and_check_fabricated.json` — same body swap, the failing check *also* forged `passed=true` | REJECTED `alltrue=false`, `inconsistent=["completion_deterministic"]` | REJECTED (`+unexpected-checks`) |
| b2 | `b2_reordered_consistent.json` — same exchange, stored checks rewritten truthfully (record self-consistent), verdict `REQUEST_OK` | REJECTED `alltrue=false`, `inconsistent=[]`, `live=true` | REJECTED (`unexpected-checks` only) |
| c2 | `c2_alias_differs_consistent.json` — alias drift, checks truthful | REJECTED `alltrue=false`, `live=false`, `inconsistent=[]` | REJECTED (`unexpected-checks` only) |
| d | `d_synthetic_receipt.json` — **wholly synthetic receipt**: invented completion bytes (`" the mat"`, fingerprint `b11755-cafebabe01234567`), invented usage/timings, invented `model.path`/`server.path`, clean teardown claims, every stored check true; port/pid/nonce copied from the real hold | **ACCEPTED** `met=true`, `alltrue=true`, `live=true`, `inconsistent=[]` | **ACCEPTED** (same) |
| e | `e_nonjson_completion_body.json` — authentic receipt whose `completion` body is `'<html>502 Bad Gateway</html>'` with its sha recomputed | REJECTED `alltrue=false` (`completion_envelope`, `…_finish_reason`, `…_model_id`, `…_fingerprint`, `…_usage`, `…_timings`, `…_deterministic`), clean | **raises `AttributeError`** at `grade():130` — no verdict |
| sanity | authentic receipt, `witness=None` | REJECTED `met=false` (`live=false`) — the live leg is load-bearing | REJECTED |

Raw dumps: `forgery-results.json`, `consistent-results.json`,
`synthetic-results.json`, `version-matrix-results.json`, `witness.json`,
`tip-counter-run.txt`, `wt-counter-run.txt`, `tipcounter-live-receipt.json` /
`worktree-live-receipt.json` (the receipts the two counter runs' own live legs
produced: both `verdict=REQUEST_OK`, clean teardown, ports 46429 / 41771 — the
tip counter rejects the first as `unexpected-checks`), `counter-tip.py` /
`counter-wt.py` (both instrument byte-sets), `server.log`.

## Findings

**F1 — the three specified forgeries are rejected, each through a distinct path.**
Verdict fabrication buys nothing: `grade()` recomputes every check from the
captured bytes and `score()` requires `alltrue` (worktree `:83-184`, `:189-215`),
so (a) is rejected with an internally consistent check map (`inconsistent=[]`,
`verdict_ok=true`), and forging the check map to match (a2) adds only the
disagreement report. Key re-ordering is caught twice (b by recomputation *and*
stored-vs-recomputed disagreement; b2 by recomputation alone). Alias drift is
caught by recomputation even when the nonce matches (c, c2) and by the live leg
as well, because `score()` requires the receipt's completion `model` to equal
`witness['model']` (`:211`).

**F2 — calibration gap: a receipt minted from scratch is ACCEPTED when the witness
is genuine (d, accepted by both instruments).** `score()` binds the receipt to the
live contact only via `nonce`, `child_pid`, `port`, completion `model` and the two
digest fields (`:189-215`); captured **content** is never compared to the
witness's answer. Concretely, the receipt's completion text is never compared to
`witness['text']` (`" floor"` real vs `" the mat"` invented), and
`system_fingerprint` is only regex-checked against `^b\d+-[0-9a-f]{9,40}$`
(`:127-129`), never compared to `witness['fingerprint']`
(`b11755-704366d76` real vs `b11755-cafebabe01234567` invented). d contains no
byte captured from the graded run and is still `met=true`. This does **not**
bypass the live requirement — the witness must come from a real held server owned
by `child_pid` on `port` (`:194-206`) — but "re-derived from captured bytes" is,
as implemented, *self-consistency of tool-written bytes*, not provenance of those
bytes. Whether that satisfies the frozen predicate is the L1's call; the minimal
closing change is two equalities in `score()` (receipt completion `text` and
`system_fingerprint` vs the witness answer).

**F3 (calibration) — the committed tip counter rejects its own authentic receipt.**
At the tip blob, `grade():165` registers `hold_released` only when the literal key
`'hold'` is in `checks`, which the tool never writes (it writes `hold_released`).
The authentic receipt carries 17 checks including `hold_released`, so
`set(stored) != required` → `inconsistent=["unexpected-checks"]` → `met=false` and
`live_ok=0/1`, even though every recomputed check is true and the live witness
passes. The measured state quoted in the seat spec (`live_ok=1/1`, `16/16`,
`errors=0`, `met=True`) is reproducible **only** with the worktree bytes
(`a3498308…`), whose third edit is exactly this line. The committed blob cannot
produce that line.

**F4 (operability) — the committed tip counter aborts instead of rejecting.**
`grade():130` dereferences `cj` unconditionally after a `body_sha256` mismatch
makes `cap('completion')` return `None` (`cj = jbody(c) if c else None`), so any
receipt whose `completion` body was edited without a sha update raises
`AttributeError: 'NoneType' object has no attribute 'get'`. The counter's own
control families hit this: running the tip blob end to end exits 1 with

```
File ".../counter-tip.py", line 440, in main
    s = score(ctl, witness)
File ".../counter-tip.py", line 191, in score
    recomputed, inconsistent = grade(receipt)
File ".../counter-tip.py", line 130, in grade
    u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
```

reproduced twice (`tip-counter-run.txt`); the crashing controls are `tamper[0]`
(completion body swap without sha) and `outside` (model replacement without sha).
No tally line is printed, so the committed instrument cannot report
`tamper_rejected=8/8`, `outside_rejected=1/1`, `errors=0` at all. The worktree's
first two edits (`(cj or {})`) turn both into clean REJECTEDs. This is a crash,
not a false accept — the kill rule (`errors≥1` ⇒ not met) still holds — but it is
reachable exactly through this seat's channel: a hand-supplied receipt.

**F5 — residual self-attested fields (bounded observation, not exercised).**
`listener_owned` is read back from the receipt's own check map rather than
recomputed (`:159-160`), and `teardown_clean` / `teardown_port_closed` are
computed from receipt fields (`teardown.child_pre_dead`, `returncode`,
`port_closed`, `:167-170`). The witness independently proves ownership during the
hold, so `listener_owned` is not load-bearing; post-run teardown has no
independent observer, so a receipt rewriting only those fields would stay
undetectable by `score()`. I did not build that fixture: it needs a genuinely
dirty-teardown run (hold/kill territory owned by peer seat A02C1HoldTamper), and
reporting it as rejected/accepted without that run would be ungrounded.

## Operability evidence (my own live leg)

- Model `~/.cache/kama-shokunin/models/stories260K.gguf` sha256 `270cba1b…256d`;
  server `~/.local/opt/llama-b11755/llama-server` sha256 `b6a31a8e…cd804`; both
  verified by the tool against the pinned constants.
- One lifecycle on unregistered loopback port 34969, pdeathsig child pid 965906,
  `hold.json` → `release` window released in time.
- Receipt `kama-completion-live/v1`: 17 checks all passed, `verdict=REQUEST_OK`,
  `teardown{child_pre_dead:false, returncode:0, sigterm_sent:true, port_closed:true}`.
- Witness (the counter's own observation during the hold): HTTP 200,
  `model=alias=kama-completion-probe`, `listener_owned=true`, fingerprint
  `b11755-704366d76`, nonce echoed in the prompt; `score()` ⇒ `live=true`.
- Post-run: `ps -p 965906` empty, port 34969 not listening — no orphan left.
- The worktree counter run reproduced `live_ok=1/1` and `16/16` controls
  (`errors=0`) in my scratch, independently of the C1 author's run.
- C1's 16 control families are peer seats' ground (E02/E04); I ran the counter only
  to establish the instrument divergence and did not re-audit the controls' design.

## Risks / blockers

- No blocker. Nothing in the lane was edited or committed; two live counter runs
  and one manual lifecycle all used unregistered loopback ports and my own scratch.
- F3/F4 are observations about which bytes are frozen, not a verdict on C1. If the
  freeze intends the worktree bytes as the instrument, the tip is not the frozen
  instrument; if it intends the tip blob, the measured `met=True` is not
  reproducible from committed bytes. The L1 owns that call. F2 is the only finding
  that would survive committing the worktree bytes as-is.

Tally: **fixtures fed to score(): 8 → worktree instrument 1 ACCEPTED
(`d_synthetic_receipt`) / 7 REJECTED; committed tip instrument 1 ACCEPTED (same d)
/ 6 REJECTED / 1 EXCEPTION (`e_nonjson_completion_body`, AttributeError);
required a/b/c = 3/3 REJECTED on both; authentic baseline worktree met=true,
committed tip met=false (`unexpected-checks`), authentic-without-witness met=false.**
