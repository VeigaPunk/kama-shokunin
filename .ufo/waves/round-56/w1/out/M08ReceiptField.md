# M08ReceiptField — round 56 calibration probe

**Mutant:** In a scratch copy of `tools/round56-env-leg-battery.py`, changed `fields.get("ld_audit") == expected` to `expected in fields.get("ld_audit", "")`. Scratch-only path redirects (`OUT` and temporary directory) kept receipts out of shared lane paths. No lane source or state was changed.

**Expected detector:** Run the C1 battery on pristine/mutated harnesses and run the C2 `round56-prereg-check.py` on pristine/mutated/restored committed tips. A detector that validates the field comparison should reject the mutant.

**Actual outputs:**

- Pristine C1 battery: `base-old-counter: ld_audit=missed exit=0 -> pass`; `round56-counter: ld_audit=detected exit=0 -> pass`; `m-drop-ldaudit: ld_audit=missed exit=0 -> pass`; process exit `0`.
- Mutant C1 battery: same three output lines and exit `0` (survived).
- Pristine C2 checker at `efc6b3ec`: `present=1 roster_match=1 kills=1 controls=2 met=True`, exit `0`.
- Mutated C2 checker at scratch clone tip `b6ef8aa8`: `present=1 roster_match=1 kills=1 controls=2 met=True`, exit `0` (survived).
- Restored C2 checker at scratch clone tip `6a442de6`: `present=1 roster_match=1 kills=1 controls=2 met=True`, exit `0`.
- Substring counterexample: `expected=detected field=undetected substring_match=True`.

**Verdict:** **Survived** both battery and calibration checker. The battery sees only actual `missed`/`detected` values, so its real runs do not distinguish substring from exact equality. C2 parses only the battery's `ROSTER` AST literal and does not inspect the `run()` comparison. Thus this comparison defect is unguarded by both detectors; substring matching can accept `undetected` as `detected`.

**Restoration evidence:** Pristine battery SHA-256 before: `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`; mutant: `1d576f7c040634a0a2380e326591545079c15be9581ca18f5e35a1185ced41e2`; restored clone file and restored commit blob: `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`. The mutation was made and restored only in `/fast/scratch/hyaku/kama-r56/M08ReceiptField/clone`; final checker on restored tip was green. Copied raw battery receipts are in `w1/out/M08ReceiptField/`.

**Proposed fix:** Keep exact equality for the parsed `ld_audit` field; add a checker assertion for the behavior-bearing comparison if this calibration coverage is intended to protect it.
