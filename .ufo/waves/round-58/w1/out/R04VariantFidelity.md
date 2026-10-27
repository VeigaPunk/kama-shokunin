# R04VariantFidelity — Round 58 C1 variant audit

**Verdict: no actionable finding in scope.** Audited frozen bytes at `dcd69473dd7e33b316e2ba238a48e5119a6cd809`; checked build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`, current HEAD `e4f207f544315612a6ea55b5b7a1cc2d2d4b4a79`, and working tree.

## Axes and results
- **Coverage / calibration:** frozen directory has exactly 15 `.py` files: genuine, B1–B3, N01–N11; names exactly match `tools/round58-c1-counter.py`'s one genuine + three BENIGN + eleven NOOPS enumeration.
- **Fidelity:** reproduced all 15 byte-for-byte from `tools/round56-env-leg-battery.py` using the frozen `make-variants.py`; each variant equals its named transformation. Genuine is byte-identical to that battery. Every asserted-unique edit anchor checked occurs once.
- **Compilation:** in-memory Python `compile(source, filename, 'exec')` succeeds for all 15.
- **ROSTER:** AST dump of the literal is identical to genuine for all 15, including N01–N11. B3 retains all three keys.
- **Name semantics:** static AST evidence confirms B1 pure identifier rename/comment; B2 helper delegates to `run` and wraps three calls; B3 concatenations fold to the original labels; N01 calls removed; N02 false branch; N03 unused `_legacy_main` plus `main` returning 0; N04 early return before leg calls; N05 environment guard; N06 `run` returns True before old body; N07 mutant assertion returns True before old body; N08 main guard is `pass`; N09 empty loop; N10 global `run` rebound to True lambda before `main`; N11 leg calls only in `try/else` after an unconditional raise.
- **Drift:** all 15 blobs match freeze, build tip, HEAD, and working tree.

## Verification commands / outputs
1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree -r --name-only dcd69473dd7e33b316e2ba238a48e5119a6cd809 -- tests/round58-battery-variants/` — exit 0; listed exactly the 15 files above.
2. `python3 <scratch>/make-variants.py <scratch>/in/genuine.py <scratch>/out` (generator and genuine sourced by `git show` at freeze rev) — exit 0, stdout `15 variants`; byte comparisons: 15/15 equal.
3. In-memory compile check across 15 frozen blobs — 15/15 pass; no files executed.
4. AST ROSTER comparison across 15 frozen blobs — 15/15 equal; all 11 N-variants retain the literal.
5. Per-variant blob equality checks across freeze/build tip/HEAD/working tree — 15/15 unchanged. `git status --porcelain -- tests/round58-battery-variants/ tools/round58-c1-counter.py tools/round56-env-leg-battery.py` — exit 0, empty output.

## Residual risk / verification gap
- No variant was executed: the battery defines a hard-coded lane `OUT` path and `main()` creates it. Execution would write outside this seat's permitted output directory. The name/no-op checks are static AST checks plus byte-for-byte reproduction; runtime harness behavior remains outside this seat's scope.
- N05 intentionally runs its leg body when `KAMA_R56_RUN_BATTERY=1`; this is the named environment-guard variant, not a fidelity defect. N06/N07 retain unreachable old code after an unconditional `return True`, also exactly as generated.

Machine-readable per-file receipt: `.ufo/waves/round-58/w1/out/R04VariantFidelity/variant-fidelity-receipt.json`.
