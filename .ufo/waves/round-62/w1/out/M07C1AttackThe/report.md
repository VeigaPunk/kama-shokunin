# M07C1AttackThe — C1 hold-family falsification (round 62, w1)

**Axis:** operability. **Milestone:** falsify C1 counter. **Instrument:** the tip blob
`git show 65d7cad0fce90e34de37527cde22e97b63b118bf:tools/round62-c1-counter.py`,
sha256 `275610b51eb1be219cdaa3c3e15e3568b590f35e7a1b3ceb42ab0374243f4d8d`
(preserved byte-exact as `tip-counter.py` beside this report).
No pacman, no tools installed. No lane source outside my two report paths was
created or modified; `measure/c1b` was read read-only; live runs used the lane
tools on unregistered loopback ports only.

## 1. Method

- `score()`/`grade()` were **not** re-typed: the exact tip blob was imported as a
  module and its own functions were called (`attack-driver.py` beside this
  report, sha256 `52b4bed5a0db9a9b31f8fa31907f7f9d325033df957cd6b3d45ba61f34b29507`).
- A genuine `(receipt, witness, nonce)` triple was produced by replicating the
  counter's `witness_run` verbatim (same argv, hold.json polling, POST payload
  `{prompt: '<nonce> under the', n_predict: 4, temperature: 0.0, seed: 3}`,
  same witness dict, same release write) against the tip tool extracted from
  tip blobs, in my isolated scratch. Final run: nonce `r62-61f4c588ff`, port
  41339, child pid 1918879, verdict `REQUEST_OK` (`genuine-receipt.json`,
  `genuine-witness.json`, `genuine-nonce.txt`). The receipt's `hold` section is
  `{"dir": …/battery/hold, "released": true}` — the receipt schema carries **no
  release timestamp** (the tool unlinks `hold.json` at release; the receipt
  records only dir+released), and `checks` has 17 keys including
  `hold_released`, with no `hold` key.
- Every battery item below is `score(receipt_mut, genuine_witness)` with the
  tip module's own functions and `NONCE` set the way `main()` sets it. The
  witness is the counter-equivalent in-run observation (`listener_owned`
  evaluated during the hold window while the child was alive); forgeries touch
  only receipt-side hold fields. Raw output: `battery-stdout.txt`.

## 2. End-to-end (official command shape, my scratch)

- **Tip blob: crash, no tally, exit 1.** `AttributeError: 'NoneType' object has
  no attribute 'get'` at `counter.py:130` (`u = cj.get('usage') or {}` —
  unguarded when a mutation makes the completion capture fail its body-sha
  check, so `cap('completion')` returns None), raised at `main()` line 440
  inside the controls loop, i.e. on the first `tamper` family item
  (`tipcounter-crash.txt`; the receipt it had already graded is
  `tipcounter-receipt.json`). Independently confirms E01/E06/W03.
- **Lane worktree file** `tools/round62-c1-counter.py` (NOT my instrument —
  uncommitted edits, sha256 `a3498308938ed4715cfdf1ce5c9a2e4ddf9cb5f9befbba29857980721fe8c415`):
  `tool_present=1 live_ok=1/1 … errors=0 met=True`, exit 0
  (`worktree-counter-line.txt`, `worktree-receipt.json`). The spec-time
  `met=True` is reproducible only from non-tip bytes (agrees with E06).

## 3. Battery — each forgery/mutation verbatim

```
[B0-pristine] REJECTED score()={"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true} | tip counter vs its own genuine receipt
[H0-released-false-checks-intact] REJECTED score()={"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true} | the 'hold' control family mutation
[H0-vs-B0] rejection JSON identical to pristine: True (non-discriminative if True)
[H1-gate-on-hold-key-released-false] REJECTED score()={"alltrue": false, "inconsistent": ["hold_released", "unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
[H2-gate-on-released-true-no-dir] REJECTED score()={"alltrue": true, "inconsistent": ["missing-checks", "unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
[F4-fs-probe] hold dir on disk: {"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
[F4-fs-probe] hold dir absent : {"alltrue": true, "inconsistent": ["unexpected-checks"], "live": true, "met": false, "verdict_ok": true}
[F4-fs-probe] identical: True
[F1-released-true-no-timestamp-no-dir] ACCEPTED score()={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true} | hold window semantics broken; receipt carries no hold evidence
[F2-released-false-no-timestamp-no-dir] ACCEPTED score()={"alltrue": true, "inconsistent": [], "live": true, "met": true, "verdict_ok": true} | never-released hold accepted once vacuous entry is stripped
```

Item definitions:
- **B0** pristine genuine pair. **H0** the counter's own hold-family mutation
  (`hold.released=false`, otherwise pristine).
- **H1** doctored `checks['hold']={'passed':true,...}` added (gate forced on),
  `released=false`. **H2** `checks['hold']` replacing `hold_released`,
  `hold={'released':true}` with no dir/schema fields.
- **F1** (assigned): `hold_released` check entry absent, `hold={'released':true}`
  (no release timestamp — the schema has none, no dir field), hold dir moved
  away on disk. **F2** mirror of the hold family: same shape, `released=false`.
- **F4** pristine receipt scored with hold dir present vs absent on disk.

## 4. Findings

- **F-1 (ASSIGNED — ACCEPTED forgery → falsification of the C1 predicate).**
  The grading core accepts `released=true` with the hold window semantics
  broken (no release timestamp — none exists in the schema — no hold dir
  reference, dir absent on disk) with `met=true, inconsistent=[]`. The counter
  never checks the hold doc schema (`kama-completion-hold/v1`), the hold.json
  release timestamp (`at`), or the hold dir: `grade()` is a pure function of
  the receipt dict (F4: byte-identical score with the dir present vs absent),
  and the receipt's `hold.released` boolean itself is unreachable — see F-4.
- **F-2 (stronger).** The mirror forgery `released=false` — a lifecycle that
  never released the hold — is likewise **ACCEPTED** (`met=true`) once the
  receipt stops carrying the unaudited `hold_released` check entry. The hold
  family's claimed detection is therefore accidental, not semantic.
- **F-3 (vacuous control family).** The pristine genuine receipt is REJECTED
  (`unexpected-checks`), and the hold family's rejection (H0) is byte-identical
  to the pristine rejection. `hold_rejected=1/1` carries zero differential
  signal: the family rejects everything, its own genuine input included.
- **F-4 (dead-logic proof).** `grade()` reads `receipt['hold']['released']`
  only under `if 'hold' in checks`. Acceptance requires
  `set(stored) == required` where `required = set(out) - {'nonce_match'}`:
  - if `hold ∈ stored` → gate fires → `hold_released ∈ out` → `hold_released ∈
    required` → but `stored = required` forces `hold ∉ stored`. Contradiction.
  - if `hold ∉ stored` → gate off → `hold_released ∉ out/required` → acceptance
    forces `hold_released ∉ stored` (H2 shows gate-on receipts rejected by
    `missing-checks`/`unexpected-checks`; H1 shows the gate's released-read
    firing only on an already-rejected receipt).
  Hence **in every accepting path `grade()` never evaluates the hold boolean**:
  the hold window is unaudited by construction. Empirical counterpart: F1/F2.
- **F-5 (instrument divergence, corroborates peers).** Tip bytes: crash + the
  key-set defect (`grade()` gates on `'hold' in checks` while the tip tool
  writes `checks['hold_released']`, so `required`/`stored` never match on a
  genuine receipt — B0). Worktree bytes (3 uncommitted edits incl. that gate
  line, per E06): `met=True`. The committed instrument cannot produce the
  spec-time line; the uncommitted worktree state that can is lane-dirty.

## 5. Mutation-tester verdict

- Mutant: receipt asserts the hold window with its evidence removed
  (`released=true`, and even `released=false`; no timestamp, no dir, no schema).
- Expected detector: hold control family / `hold_released` recomputation.
- Output: §3 verbatim. Verdict: **SURVIVED** — a coverage finding, reported as
  such; no contract or lane source was changed. Baseline caveat: the tip
  counter also rejects its own pristine receipt (B0) and crashes end-to-end
  before any tally, so as committed the instrument is not merely attackable —
  it cannot complete.

## 6. Artifacts (this directory)

`tip-counter.py` (exercised tip blob, sha `275610b5…`), `attack-driver.py`
(`52b4bed5…`), `battery-stdout.txt` (`9f169823…`), `genuine-receipt.json`
(`32d5b21f…`), `genuine-witness.json` (`9d04e75e…`), `genuine-nonce.txt`
(`125bebdb…`), `tipcounter-crash.txt` (`9985a266…`), `tipcounter-receipt.json`
(`2746f6e5…`), `worktree-counter-line.txt` (`ebd352b1…`),
`worktree-receipt.json` (`6517bb17…`). Scratch
`/fast/scratch/hyaku/kama-r62/w/M07C1AttackThe` removed after preservation.
Restoration evidence: the tip blob hash before/after all probes is unchanged
(`275610b5…`); the lane worktree counter hash read-only before/after:
`a3498308…` (unmodified by me).

Report: .ufo/waves/round-62/w1/M07C1AttackThe.md
