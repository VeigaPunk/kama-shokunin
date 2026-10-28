# MT12C1HollowExpect — C1 counter hollowing falsification (round 63, kama)

Seat: mutation-tester, leaf (advisory; no verdict on the claims, no commit to the lane).
Tip under test: `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (counter blob sha256 `35af5c98…dbcd`, identical in lane working tree and tip).
Method: per-mutant clones `--shared` of the lane under my scratch root, one committed mutation each (`mut-<m>` branch at the tip), counter run from `<clone>/tools/` with `--repo <clone> --tip <clone HEAD> --work <scratch>/work-<m>`. The live tool and `kama-llamacpp-live.py` are read from the tip blobs (unmutated). Patches saved in `out/MT12C1HollowExpect/<m>.patch`; receipts and stdouts in the same dir.
Tools: none installed or upgraded. Pacman not touched.

## Baseline (unmutated counter, tip 03a6a1d)

```
tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=3/3 listener=1/1 log=1/1 outside=1/1 predead=1/1 ptok=2/2 reqbind=2/2 schema=1/1 shape=4/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=4/4 trunc=2/2 witness=6/6]
exit=0
```

Live contact is real, not a stub: `base-receipt.json` carries a fresh nonce, child pid 2357927-class, port in the unregistered range, real generated text, `system_fingerprint` `b11755-704366d76`, server sha `b6a31a8e…d804`. A full hold-mode lifecycle plus the counter's own outside request takes ~1.5–2 s on the pinned small fixture, which is why the runs were quick; I checked the receipts rather than assuming the timing.

## Mutants and results (all one-line counter output verbatim, from `out/MT12C1HollowExpect/<m>.stdout`)

| id | mutation (committed in clone, diff in `<m>.patch`) | verdict | counter output |
|---|---|---|---|
| L1-m1 (reproduce) | `is_hit` → `return (not s['met'])` (named check and cap ignored) | **KILLED** (met=False) | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=1/3 errors=0 met=False families[… tamper=8/8 …]` |
| L1-m2 (reproduce) | `edit_body` no longer re-seals body hash (`reseal(c)` cut) | **KILLED** (met=False) | `tool_present=1 live_ok=1/1 controls_targeted=31/44 eval_selftest=3/3 errors=0 met=False families[digest=1/1 fake=2/2 hdr=2/2 hold=1/1 idcr=0/3 listener=1/1 log=1/1 outside=0/1 predead=1/1 ptok=1/2 reqbind=2/2 schema=1/1 shape=0/4 sigterm=1/1 stale=1/1 tamper=8/8 timing=0/4 trunc=2/2 witness=6/6]` |
| H1 (new) | `ENVELOPE_CAP = 30` → `99` | **SURVIVED** (met=True) | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[… tamper=8/8 …]` |
| H2 (new) | `MAX_COLLATERAL = 5` → `99` (the `is_hit` default follows it) | **KILLED, but only by the self-test**; the 44/44 line survives | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=2/3 errors=0 met=False families[… tamper=8/8 …]` |
| H3 (new) | H2 + self-test plant 2 edited to `is_hit(…, 'completion_envelope', cap=5)` (pinned literal, so the plant still "refuses") | **SURVIVED** (met=True) | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[… tamper=8/8 …]` |
| H4 (new, combined) | L1-m2 (no reseal) + H3 | **SURVIVED** (met=True) | `tool_present=1 live_ok=1/1 controls_targeted=44/44 eval_selftest=3/3 errors=0 met=True families[… tamper=8/8 …]` |

Notes on the reproductions:
- L1-m2 reproduced exactly: 31/44 and the same families (`idcr=0/3 outside=0/1 ptok=1/2 shape=0/4 timing=0/4`).
- L1-m1 reproduced as met=False, but my self-test count is **1/3**, not the 0/3 recorded in `controls/c1-mutants-prewave.txt`. With `(not s['met'])` the genuine receipt is met=True and so the third plant is refused, which gives 1/3. I did not find the L1's exact edit; the verdict (met=False) agrees, the self-test digit does not. Flagged, not resolved.
- H2's 44/44 is printed with `met=False` only because the evaluator plant 2 now passes. The control line by itself does not notice the hollowing.
- H3 is a "plants edited to match" hollowing in the sense that matters: the self-test is rewritten so that it refuses under the hollowed cap. Plants edited alone, without a hollowed constant, change nothing (no-op), so H3 is necessarily combined with the cap change.

## Verdict on the three requested hollowings

1. **ENVELOPE_CAP raised to 99 — SURVIVED.** The counter reports met=True. The only control that uses the envelope cap (`tamper` on `completion` object→`chat.completion`) has a measured re-score failure set of **26** checks (probe below). Any ENVELOPE_CAP ≥ 26 gives the same verdict; nothing in the 44-control set or the self-test pins the upper side. 30 is only "4 units of slack" over the measured cascade, and 99 is indistinguishable from it. The predicate sentence ("30 for the envelope break") is not machine-enforced.
2. **MAX_COLLATERAL raised to 99 — the 44/44 line SURVIVES; met flips only through `eval_selftest` (2/3).** The 44 targeted controls all pass `is_hit` with cap 99 and the counter still prints `controls_targeted=44/44`. Protection against this hollowing is therefore a single plant (self-test plant 2, the envelope break re-scored at the default cap). That plant is in the same file as the constant it tests.
3. **eval_selftest plants edited to match — SURVIVED when combined with (2)** (H3: met=True, 3/3). The self-test then tests a constant the author chose, not the frozen one. Nothing outside `round63-c1-counter.py` pins `MAX_COLLATERAL == 5` or `ENVELOPE_CAP == 30`; the freeze text is prose.

**H4 is the strongest finding:** with the body re-seal removed (m2) AND the cap raised AND the plant edited (H3), the counter prints `controls_targeted=44/44 eval_selftest=3/3 met=True` on a broken helper. The 13 capture-body controls that m2 un-seals are credited on the wrong reason (hash mismatch, not the named field). Under this counter, the cap is the only defence for the helper, and the self-test shares the constant's fate.

## Calibration measurements (probe; `out/MT12C1HollowExpect/probe-cascade.txt`, `probe-m2-tamper.txt`)

Measured re-score failure-set sizes at the tip (genuine receipt, fresh witness, nonce `r63-2afe53295c`):
- Envelope break (`completion` object→`chat.completion`, resealed): **26** fails, cap 30 → credited. The cap is therefore only 4 units above the real cascade, and any cap in [26, ∞) yields the same verdict. ENVELOPE_CAP ≤ 25 would make the envelope control escape (met=False) — derived from the measured 26 with `len(fails) <= cap`; not run as a separate clone.
- Largest one-field control: `tamper model_digest` at **5** fails = cap 5 exactly. Zero margin: a cap of 4 would make the model-digest control escape.
- Other one-field controls: 2–4 fails.

Wrong-reason credit under m2 (`probe-m2-tamper.txt`): with the reseal removed, the envelope control still re-scores at 26 fails, all 13 `inconsistent:completion_*` entries included, and `is_hit` credits it because `completion_envelope` is in the set and 26 ≤ 30. The counter's `is_hit` never looks at `inconsistent:*` entries, so a hash mismatch looks like a semantic envelope break. This is why `tamper=8/8` stays green in L1-m2 and H4. The `outside` control under the same m2 has 26 fails and is refused at cap 5 only by accident of cap size.

## Why the design does not protect itself (root cause)

- The constants (`MAX_COLLATERAL`, `ENVELOPE_CAP`, `EXPECT_CONTROLS`, `EXPECT_EVAL_SELFTEST`) and the self-test plants live in the same file as `is_hit`. The amended protection (3-plant self-test) checks the evaluator against itself, so a coordinated edit of constant and plant passes.
- `is_hit` credits any failure set that contains the named check and has size ≤ cap. It does not check that the mutated receipt is hash-clean before scoring, so an un-resealed mutation is credited through `inconsistent:*` cascades. Credit should require the mutation to be the only semantic change.
- Nothing pins the counter's own constants or code to the freeze. The freeze fixes the instrument by commit (`03a6a1d…`), but the mutants above are different commits that the counter would score without complaint; there is no hash of the counter blob in `freeze.txt` to compare.

## Suggested remedies (advisory; the L1 decides)

1. Pin the counter blob sha256 (`35af5c98…dbcd`) in `controls/freeze.txt` and have the reviewer/L1 compare it; any mutant then fails the pin before scoring. This catches H1–H4 regardless of the constants.
2. Inside the counter, assert the frozen constants against literal values from the predicate (`MAX_COLLATERAL == 5`, `ENVELOPE_CAP == 30`). Weak alone (editable), but it turns H2 into a visible error line.
3. Pin the cap boundaries with plants: a one-field control with 5 fails must be credited, one with 6 must be refused; an envelope control with 25 fails must be refused, with 26 credited. A cap raised to 99 then flips a plant, so the self-test catches it without relying on the envelope plant's default.
4. Require each control's mutated receipt to pass the capture hash check (or, equivalently, reject any control whose failure set contains an `inconsistent:` entry). This closes the wrong-reason credit that H4 exploits.
5. Make the control count visibly depend on the caps: print the per-control max fail count, so a 99 cap shows as `max_fails=26 cap=99` rather than a bare 44/44.

These are recommendations, not edits. No lane file was changed; no commit; no push.

## Caveats

- I did not reproduce the L1's 0/3 self-test figure for m1 exactly (see notes above).
- The probe that measured fail-set sizes (`cascade.py`, `reason.py`) lives only in my scratch and is copied into the evidence dir as output text, not as a runnable script; re-running needs the same scratch clone layout.
- Live runs: the counter launches its own llama-server child on an unregistered loopback port; no registered consumer port or foreign llama-server (1234, 45669) was touched.

## One-line tally

Hollowing matrix (K = killed, S = survived; 44/44 = controls credited):
- L1-m1 is_hit hollow: K (met=False, selftest 1/3)
- L1-m2 no reseal: K (met=False, 31/44)
- H1 ENVELOPE_CAP=99: **S** (met=True)
- H2 MAX_COLLATERAL=99: K only via selftest 2/3 (44/44 survives)
- H3 cap 99 + plant pinned: **S** (met=True)
- H4 no reseal + cap 99 + plant pinned: **S** (met=True, 44/44 on a broken helper)
Baseline: `met=True` at 03a6a1d.
