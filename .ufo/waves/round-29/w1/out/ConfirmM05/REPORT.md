# ConfirmM05 — C1 first falsifier, base receipt (pre-data)

**sid:** `SCORECARD.md:P:312b3e69b1:0` — SCORECARD.md line 740 at base 2aa46e24, class P, token `round-17-verifier-spotcheck.md:217–221`.
**Verdict: `confirmed-false`** — the statement was false at its writing revision W; the counter's `p:absent` is correct.

## How it was established (independently of the counter — never executed)

1. **W confirmed** — `git blame -L 740,740 --line-porcelain 2aa46e24 -- SCORECARD.md` names
   `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d` (round-18 commit, summary "classify missing
   observations and bind detector survivor claims") for line 740.
2. **Statement read** — line 740 at base (with its 739–741 sentence) is the tail of
   "Round-17 outside review … judged **discernment improved** (`round-17-verifier-spotcheck.md:217–221`),
   superseding the pending author reading at line 702."
3. **P rule applied by hand** — path as written `round-17-verifier-spotcheck.md` does not start
   with `../`, `/`, `~`, or a URL scheme, so the rule applies. `git cat-file -e
   c6dc46fa:round-17-verifier-spotcheck.md` fails: *path 'round-17-verifier-spotcheck.md' does not
   exist* → **p:absent** (the line-count arm is never reached).
4. **Intended referent exists at W** — `corpus/lessons/round-17-verifier-spotcheck.md` exists at W
   (`cat-file -e` exit 0), 276 lines (≥ 221), committed in `e75cf680b53484a61709ee1b2787d8dbc6419f74`
   — the blame `previous` commit, one commit before W. It is the *only* tree location of the
   basename at W (`ls-tree -r | grep`). Lines 217–221 at W contain exactly the
   "discernment: improved" outside-judgment passage (S042/S044 admits, 3/3 rejects) that line 740
   asserts. So the referent is unambiguous: the citation is a truncated pointer, not a phantom.
5. **Receipt cross-check (data, not trust)** — base receipt c1-base.json records for this sid:
   W, line 740, token, `observed: "p:absent"`, `holds: false`. Identical to independent findings.

## Findings by severity

- **Confirmed defect (the statement):** P pointer missing its `corpus/lessons/` prefix; the blob
  `W:round-17-verifier-spotcheck.md` does not exist. False at W as written. Cause (correction row):
  *"The pointer omitted the corpus/lessons/ prefix; the cited span existed at W only as
  corpus/lessons/round-17-verifier-spotcheck.md (276 lines)."* (17 words)
- **Convention note (sibling risk):** adjacent line 742 cites `` `lessons/round-18.md` `` — also a
  corpus-relative path with no top-level blob at W (`cat-file -e W:lessons/round-18.md` → 128).
  SCORECARD round-18 wrote corpus-relative paths habitually; this statement additionally dropped
  the `lessons/` segment. Other statement cited with `lessons/...` prefixes may fail the same
  literal way — out of scope here, but a candidate systemic finding for the L1.

## Verification gaps / residual risk

- None for this sid: W, statement text, referent, and observed value all confirmed from committed
  objects (read-only git only; no counter executed; no working-tree reads).
- General limit: the counter's class rules are applied by hand in this review; a full receipt-level
  audit of all 69 statements is not this item's scope.

## Tooling

No tools installed; no packages changed (none needed — read-only git suffices). Outputs:
`verdict.json`, this report, and `.ufo/waves/round-29/w1/advice/ConfirmM05.md`.
