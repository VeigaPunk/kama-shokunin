# ConfirmM05 advice (scoped findings)

**Verdict: `confirmed-false`** for `SCORECARD.md:P:312b3e69b1:0` — the counter's `p:absent` is correct.

- Statement: SCORECARD.md line 740 at base: "… judged **discernment improved**
  (`round-17-verifier-spotcheck.md:217–221`), superseding the pending author reading at line 702."
- W = `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (blame-confirmed).
- Path as written `round-17-verifier-spotcheck.md` does not exist at W (`cat-file -e` → 128):
  P rule fails p:absent (line-count arm never reached).
- Intended referent: `corpus/lessons/round-17-verifier-spotcheck.md` at W — sole location, 276
  lines, committed one commit before W in `e75cf680`; lines 217–221 hold the "discernment:
  improved" passage the line asserts. Referent existed at W; only the path prefix was omitted.
- Correction-row cause (≤25 words): "The pointer omitted the corpus/lessons/ prefix; the cited
  span existed at W only as corpus/lessons/round-17-verifier-spotcheck.md (276 lines)."

**Sibling flag for the L1:** line 742 cites `` `lessons/round-18.md` ``; the path
`lessons/round-18.md` also has no top-level blob at W. SCORECARD round-18 wrote corpus-relative
paths without the corpus/ prefix, and this line dropped the lessons/ segment too. Other P/H/N/Q
statements citing `lessons/...` paths may fail the same literal way — worth a batch check of the
remaining 10 base P statements.

Outputs: `.ufo/waves/round-29/w1/out/ConfirmM05/verdict.json` and `REPORT.md`. No tools installed.
