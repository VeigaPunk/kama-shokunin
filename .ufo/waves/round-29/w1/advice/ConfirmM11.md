# Advice — ConfirmM11 (C1 first falsifier)

## Verdict: `confirmed-false`

Base statement `SCORECARD.md:P:17a7db7c81:0` (SCORECARD.md:1375 at base
2aa46e24) was false at its writing revision W = `d183ec572a5eed5bedeb4bce0da02707d51df3dd`:

- `git blame -L 1375,1375 --line-porcelain 2aa46e24 -- SCORECARD.md` names W.
- The line: `request text (round-26 \`count-c1.py:384\`), a base-tree shortcut met it 12/12,`
- Hand-applied class-P rule: `W:count-c1.py` does not exist (`git cat-file -e` → fatal, exit 128) → `p:absent` correct → statement false at W. Counter is not a false positive.

**Intended referent:** `.ufo/waves/round-26/count-c1.py:384` — exists at W,
423 lines, line 384 = `c["e_not_echoed"] = sig not in req_bytes` (raw-bytes echo
check). The statement omitted the `.ufo/waves/round-26/` directory prefix; the
bare-filename shorthand is also used in corpus/lessons/round-26-verifier-spotcheck.md:109,234.

**Cause for correction row (≤25 words):** SCORECARD line 1375 omits the
`.ufo/waves/round-26/` prefix of the referenced counter path, so the path as
written does not exist at W.

**Recommendation for L1:** if a correction row is written for this sid, observed
value `p:absent` (the counter's exact string). Suggest the SCORECARD section
records the full path `.ufo/waves/round-26/count-c1.py:384` in a follow-up
knowledge/self-assessment entry to remove the ambiguity, but the frozen counter's
observed value for this row is `p:absent`.
