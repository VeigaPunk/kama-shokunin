# Proposed PROVINCE.md edit

One clause appended to the existing "lane instruments" row (`PROVINCE.md:17` at
`4a2a4d55d09dfacf83dc62d1b3fddae5f6d2a050`), before the row's closing pipe:

```
; `tools/append-only-audit.py` with `tools/round46-append-audit-check.py` (append-only audit of the five append-only self-description files: every commit deleting >= 20 lines from one of them, how many of those lines the file holds again at the audited revision and the commit that restored them; round 46)
```

Why it is required: `tools/round42-selfdesc-reconcile.py` leg `province` demands
that every backticked `tools/`/`registry/` token in a canonical capability row's
evidence cell appears verbatim in `PROVINCE.md`. Without the clause the patched
tree reads `province=2` (`receipt/04-selfdesc-patch.out`):

```
detail: province: PROVINCE.md lacks tools/append-only-audit.py (capability append-only-audit)
detail: province: PROVINCE.md lacks tools/round46-append-audit-check.py (capability append-only-audit)
```

Consequence: `PROVINCE.md` sha256 `36d6bb3ac93b1cc20e07969b373fd89d473fc476647f69c2f7e1ae4333a9b6aa`
→ `659a5101ce0a8bc08d2c63a23d52049cd97e183d92f226568607ebf11bc9fc49`,
186 lines unchanged; the coverage head row must be re-anchored in the same commit
(`proposed-scorecard-head-edits.md` item 5).
