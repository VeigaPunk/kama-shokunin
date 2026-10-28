# M08C1AttackThe — C1 counter falsification probe (round 62, w1, kama)

Seat: mutation-tester, attack item "falsify the C1 predicate via the outside family".
Date: 2026-10-28. Lane tip: `65d7cad0fce90e34de37527cde22e97b63b118bf` (master, unchanged
throughout this seat). Axes: operability (primary), calibration (freeze-integrity side-finding).
Bounds kept: no git/jj mutations, no lane source edits, no installs, live runs only via lane
tools on unregistered loopback ports, scratch `/fast/scratch/hyaku/kama-r62/w/M08C1AttackThe`
(deleted before yield; all receipts copied to `out/M08C1AttackThe/` first).

## Method

- Replica = the counter blob itself, extracted byte-for-byte, imported unmodified
  (`importlib`); module `NONCE` set explicitly the way `main()` sets it. Zero transcription drift.
  - master-tip blob: `round62-c1-counter.py` sha256 `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d`
  - working-tree blob: sha256 `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415`
- Live receipts produced in my scratch by real counter runs at the frozen tip
  (`--repo <lane> --tip 65d7cad0… --work <scratch>/runN`); driver `forgeries.py` feeds
  `score()` forged (receipt, witness) pairs and prints ACCEPTED (`met=True`) / REJECTED with
  the verbatim score dict.

## Headline finding 0 — the COMMITTED counter bytes fail their own honest baseline at the frozen tip

The working tree carries an **uncommitted** fix to `tools/round62-c1-counter.py`
(`git status`: ` M tools/round62-c1-counter.py`; master still `65d7cad0…`). Diff of
master blob vs working tree (3 hunks):

```diff
-    u = cj.get('usage') or {}
+    u = (cj or {}).get('usage') or {}
-    t = cj.get('timings') or {}
+    t = (cj or {}).get('timings') or {}
-    if 'hold' in (receipt.get('checks') or {}):
+    if 'hold_released' in (receipt.get('checks') or {}):
```

Consequences, both reproduced end-to-end at tip `65d7cad0…`:

1. Working-tree counter: `tool_present=1 live_ok=1/1 … errors=0 met=True`, exit 0
   (reproduces the measured state — with the **uncommitted** bytes).
2. Master-tip counter: the live leg grades the honest receipt `met=False`
   (`inconsistent: ["unexpected-checks"]` — `grade()` only recomputes `hold_released`
   when a bare `'hold'` checks-key exists, but the tip tool writes flat
   `checks.hold_released`, so `set(stored) != required` always), and then **crashes**
   on its own `outside` control before printing any summary:

```
  File ".../round62-c1-counter.py", line 440, in main
    s = score(ctl, witness)
  File ".../round62-c1-counter.py", line 191, in score
    recomputed, inconsistent = grade(receipt)
  File ".../round62-c1-counter.py", line 130, in grade
    u = cj.get('usage') or {}
AttributeError: 'NoneType' object has no attribute 'get'
tipblob-counter-exit=1
```

So "C1 met=True at tip 65d7cad0…" is reproducible **only** with uncommitted working-tree
bytes; the frozen instrument as committed cannot complete a run at the frozen tip.
Freeze-integrity side-finding (calibration axis); reported, not fixed — the L1 owns commits.

## Baselines for the forgery battery

- Fixed (working-tree) verifier + its own live receipt `run2` (nonce `r62-367a4c86dd`,
  port 42947, child_pid 1391247): `V0-baseline ACCEPTED met=true, inconsistent=[]` —
  verdicts below are **conclusive**.
- Committed (master) verifier + its live receipt `run3` (nonce `r62-cffb869ac1`):
  `V0-baseline REJECTED, inconsistent=["unexpected-checks"]` — baseline failure; per
  mutation-testing discipline every TIP-battery verdict is **inconclusive**, recorded
  verbatim in `tip-battery.txt` anyway. Its `live` sub-verdicts still show the same
  witness-gate acceptances (F3/F5/F9a/F9b `live=true`) masked only by the baseline defect.

## Forgery results — fixed verifier (conclusive), all score() outputs verbatim in wt-battery.txt

| Probe | Forgery | Verdict |
|---|---|---|
| V0 | pristine receipt + receipt-derived witness | ACCEPTED (baseline sanity) |
| F1 | witness `sent_prompt` lacks the nonce | REJECTED `live=false` |
| F2a/b/c | witness pid/port belong to a foreign spawned process (both / port-only / pid-only) | REJECTED ×3 `live=false` |
| **F3** | **synthetic witness, zero live contact** (pid dead: `/proc/1391247` absent; port 42947 closed: ECONNREFUSED; `listener_owned=true` self-attested; every other field cross-copied from receipt bytes) | **ACCEPTED** |
| F4a | outside control shape: completion body `model → "other-alias"`, no rehash | REJECTED `alltrue=false inconsistent=[completion_envelope, completion_finish_reason, completion_model_id, completion_fingerprint, completion_usage, completion_timings, completion_deterministic]` |
| F4b | same + capture sha re-derived | REJECTED (`completion_model_id`) |
| F4c | same + colluding witness `model="other-alias"` | REJECTED (`completion_model_id`) |
| **F5** | **witness prompt = `junk <nonce> tail`** (nonce containment satisfied, no request ever made) | **ACCEPTED** |
| F6 | cross-run splice: committed measure receipt + run2 witness fields | REJECTED `live=false` |
| F7 | module `NONCE` unset (`''`) | REJECTED `alltrue=false` via `nonce_match` |
| F8a–d | negative gates: `listener_owned=false` / `fingerprint="b1-x"` / wrong model sha / wrong server sha | REJECTED ×4 |
| **F9a** | **colluding swap: `receipt.child_pid := <live foreign sleep pid>` + witness `pid` equal to it** | **ACCEPTED** |
| **F9b** | **colluding swap: `child_pid+port := <live foreign listener I spawned>`** (pid 1684948, port 35621, owned by my python process) | **ACCEPTED** |

### ACCEPTED forgeries, verbatim (falsifications of the C1 predicate at the graded verifier)

```
[WT:V0-baseline] ACCEPTED  score={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
[WT:F3-synthetic-witness] ACCEPTED  score={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
[WT:F5-nonce-substring] ACCEPTED  score={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
[WT:F9a-foreign-live-pid] ACCEPTED  score={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
[WT:F9b-foreign-live-pid+port] ACCEPTED  score={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true}
```

Against the committed (master-tip) verifier the same four are REJECTED — but only because
its baseline already fails (`unexpected-checks`); its `live` gate accepts them identically
(`live=true` in tip-battery.txt). Inconclusive there, accepted here.

## Reading (coverage finding, not a contract change)

- Root cause of all four acceptances: **every "live" clause of `score()` is either
  self-attested by the witness (`listener_owned`, `sent_prompt`/`nonce_prompt`) or
  cross-copied from the same receipt bytes (`pid`, `port`, `fingerprint`, digests,
  model)**. `grade()` never re-derives `child_pid`/`port` ownership; nothing binds
  witness provenance to an actual HTTP round-trip. Per the freeze's own kill rule —
  "a receipt the verifier accepts without its own live nonce-bound contact" — F3/F5
  are exactly that acceptance; F9a/F9b additionally show the pid/port equality gate
  defends nothing once receipt and witness are forged as a pair (`teardown.port_closed`
  and `checks.listener_owned` are receipt-self-reported, never recomputed).
- Scope: these are `score()`-level falsifications requiring witness-dict injection or
  receipt+witness collusion. The deployed counter builds the witness in-process from its
  own `post()` during the hold window, so the end-to-end instrument is not forgeable by
  receipt tampering alone — the outside-RECEIPT family (F4a–c) is genuinely rejected,
  double-defended (capture sha256 + ALIAS pin in `grade()`). Surviving mutants = coverage
  findings: the predicate's "the counter's OWN outside request" clause rests entirely on
  witness provenance, which `score()` cannot see.
- Defense that would close the class (for the L1 to weigh, not applied): have the tool
  capture the counter-nonce request/response into a sha-pinned capture pair the counter
  re-derives, and re-derive listener ownership from `/proc/net/tcp` at hold time inside
  `grade()`, instead of trusting witness/receipt attestation.

## Artifacts (this directory: `.ufo/waves/round-62/w1/out/M08C1AttackThe/`)

- `receipt-committed-measure-c1b.json` sha256 `568f762731d10a2465b39999ebbdb80b792e5d50aa42d1fdf9f63ae67ad650d6` (L1's frozen receipt, read-only reference)
- `receipt-run1-counter-replica.json` sha256 `b1483ff78c717c01aa5bf1bb91c8be80139cd39b51ec2f44c718ea498afa4410`
- `receipt-run2-worktree-counter.json` sha256 `2ed95eee1c7c832a164216241c6bf7a306f830981086fe3984b6f3016a6454a8`
- `receipt-run3-tipblob-counter.json` sha256 `0b2e6e0fb01cfaf3eabca0f4cf0d17e9fc3200583c52b448227d07930d00d9fb`
- `counter-blob-master-tip.py` / `counter-blob-worktree.py` (sha256s above), `forgeries.py`, `wt-battery.txt`, `tip-battery.txt`

Installs: none (python3 + git only). Processes SIGKILLed: only my own spawned `sleep` and
throwaway HTTP listener. No registered consumer port contacted.

## One-line tallies

```
worktree-counter : tool_present=1 live_ok=1/1 fake_rejected=2/2 stale_rejected=1/1 tamper_rejected=8/8 log_rejected=1/1 predead_rejected=1/1 sigterm_rejected=1/1 hold_rejected=1/1 outside_rejected=1/1 errors=0 met=True  (exit 0)
master-tip-counter: AttributeError crash at grade() line 130 on its own outside control; no summary line; exit 1 (live leg had already graded the honest receipt met=False via "unexpected-checks")
forgery tally (fixed verifier): 4 ACCEPTED (F3 synthetic witness, F5 nonce-substring prompt, F9a/F9b colluding foreign pid/port) / 12 REJECTED; committed-verifier battery: inconclusive (baseline failure)
```

Report: .ufo/waves/round-62/w1/M08C1AttackThe.md
