# VerifyRow08 — hand-verification of correction row 8

**Sid under test:** `SA29:SCORECARD.md:Q:f1021c03db:0`
**Verdict:** `confirmed-false` — the base statement is false at its writing revision W, and the
correction row's last cell equals the hand-derived observed value exactly.
**Hand-derived observed value:** `q:no-artifact`

All checks below were performed by hand (git plumbing + sha256) on committed objects only;
the counter `count-c1.py` was never executed on the lane tree.

## 1. Base statement location

`git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` line 833 (1-based, matching the
counter's `enumerate` index + 1) is exactly:

```
`baseline=VALID members=3 rejected=0/3` exit 1, with `--tree-sha`
```

Verified by `xxd` (bytes `60 62 61 73 65 6c 69 6e 65 3d ... 60 0a`, LF-terminated) and
`sha256(line.encode())[:10] = f1021c03db3902...` → prefix `f1021c03db`, matching the sid's
line-hash component. Context (lines 830–836): the line sits inside the "C2 operability, 8 → 8"
prose describing the `install-tree-grid.py --gate check-receipt.py` run — the statement asserts
that the quoted gate output `baseline=VALID members=3 rejected=0/3` was observed.

## 2. Writing revision W

`git blame --line-porcelain -L 833,833 2aa46e2… -- SCORECARD.md` →

```
7229fa95eb122310e9e5334ad799ee3006293ebd 833 833 1
summary round-19: citation provenance, install-tree pin, r18 defect corrections
```

So W = `7229fa95eb122310e9e5334ad799ee3006293ebd` (a strict ancestor of base `2aa46e2`,
consistent with blame semantics). This matches the correction row's W column `7229fa95`.

Terminology note for the record: the sid's hash component (`f1021c03db`) is the sha256 of the
base *line content*, not of W; W itself is not encoded in the sid. Both identities were
confirmed independently (line-hash → sid, blame → W).

## 3. Q-class rule applied by hand at W

Class rule (counter docstring): a backticked span of 6–200 chars containing a digit and either
`=` or a space + one of met/registered/counted/stale/observed/verified/RESULT, not starting
with a command prefix — HOLDS iff the span occurs verbatim in ≥1 blob of the tree at W other
than `SCORECARD.md`, `SHONEN.md`, `LOG.md`, `corpus/**`.

Extractor sanity for index `:0`: the line contains two backticked spans;
span 1 `baseline=VALID members=3 rejected=0/3` (36 chars, digits + `=`, no command prefix)
qualifies as Q index 0; span 2 `--tree-sha` (10 chars, no digit) does not. Index `:0` correct.

Hand application of the check at W:

```
git grep -F -e 'baseline=VALID members=3 rejected=0/3' 7229fa95… -- \
  . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'
→ no output, exit 1
```

Cross-check without exclusions: the span occurs only at `SCORECARD.md:833` at W — i.e., the
only occurrence anywhere in the committed tree at writing is the self-assessment line itself.
No committed evidence artifact (e.g., `tests/llamacpp-live/` output or receipt) holds it.

Therefore the statement does NOT hold at W; the observed value the counter would print is
`q:no-artifact` (per `check()` line 264: `return p.returncode == 0, ("ok" if … else "q:no-artifact")`).

## 4. Correction row match

Tip SCORECARD.md at data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, heading
"## Round 29 — self-assessment corrections" (line 1443), 8th data row:

```
| SA29:SCORECARD.md:Q:f1021c03db:0 | SCORECARD.md:833 | Q | `baseline=VALID members=3 rejected=0/3` | 7229fa95 | quoted gate output; no committed file at W holds this text | q:no-artifact |
```

Every field corroborated independently: sid ✓, base line 833 ✓, class Q ✓, statement token ✓
(byte-exact span), W `7229fa95` ✓. The last cell (the correction parser strips surrounding
backticks; none present) is `q:no-artifact` — **exactly equal** to the hand-derived observed value.

## Conclusion

Correction row 8 is a valid correction: it names a real base statement, that statement is
false at W (the claimed observed gate output has no committed artifact at writing), and the
row's observed cell matches the counter's failure label `q:no-artifact` exactly.
Verdict: **confirmed-false**, observed `q:no-artifact`.

## Verdict JSON

```json
{"sid": "SA29:SCORECARD.md:Q:f1021c03db:0", "verdict": "confirmed-false", "observed": "q:no-artifact", "base_line": 833, "W": "7229fa95eb122310e9e5334ad799ee3006293ebd", "span": "baseline=VALID members=3 rejected=0/3"}
```

No tools installed; git/python3/sha256sum only. No lane files modified.
