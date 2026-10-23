# VerifyKnowledgeEntry — round 29 w2

## Verdict

The core baseline claims in `corpus/knowledge/self-assessment-at-writing.md` are supported by committed round-29 artifacts: the baseline receipt records 69 statements and 11 mismatches, and the cited frozen counter SHA-256 matches both the committed receipt and the counter at freeze/HEAD. S174–S177 are present in the current `corpus/SOURCES.md`. Findings below concern provenance for the added interpretation and precision of the class descriptions.

## Findings (severity order)

### Medium — added Confirm/Critic claims have no committed receipt

`corpus/knowledge/self-assessment-at-writing.md:24-31` attributes the explanation of failures and the claims about the four P referents and several Q outputs to the wave-1 critic/Confirm seats, citing `.ufo/waves/round-29/w1/out/CriticAxisFit/critique.md` and `.ufo/waves/round-29/w1/out/ConfirmM01..11/verdict.json`. At lane HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`, neither cited path is committed: `git cat-file -e HEAD:<path>` reported `NOT-COMMITTED` for both the CriticAxisFit critique and (for example) ConfirmM03's verdict, while `git status --porcelain` reports `?? .ufo/waves/round-29/w1/`. The working-tree verdicts do contain the stated P-referent determinations, but they are not committed receipts. In particular, the wording “in a later commit” at line 31 is not supported by the cited verdict path's commit status. These added factual claims therefore fail the requested committed-receipt traceability; this does not undermine the baseline counts.

### Low — class descriptions overstate the accepted token/path syntax

Lines 11–14 present the P/H/C forms as the class definitions but omit constraints in the frozen implementation. The committed `.ufo/waves/round-29/count-c1.py` at `827d136546b85059a984b34970f5b493d9a71290` defines the P/H path extension allowlist in `EXT` (line 62; used by `RE_P` at 63 and `RE_HN` at 70), so e.g. a `.png:L` reference is not extracted. Its H/C token regexes at lines 70–74 accept lowercase `[0-9a-f]` only; the H token length is bounded at 8–64. The prose's unqualified “hex” and “at least 8” read more broadly than the extractor. This is a precision/recall limitation, not a discrepancy in the 69-statement baseline result; the bounded-extractor caveat at line 22 partially signals the general limitation but does not make these class definitions exact.

## Checks and evidence

- Baseline evidence is committed: `.ufo/waves/round-29/before/c1-base.out` says `statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 2aa46e2481d2`. Its JSON at lines 627–640 records `by_class` C27/H2/N2/P10/Q25/T3, the frozen counter SHA-256, and 11 mismatches; lines 742–745 record 69 statements and 11 unresolved. The receipt is tracked at HEAD.
- The cited frozen SHA-256 is `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`: `sha256sum .ufo/waves/round-29/count-c1.py` and `git show 827d136546b85059a984b34970f5b493d9a71290:.ufo/waves/round-29/count-c1.py | sha256sum` both returned that value. The committed counter and preregistration are present at the freeze commit and unchanged at HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`.
- The `source:` line at knowledge-entry line 1 cites all of S174, S175, S176, and S177. They exist in the current `corpus/SOURCES.md` at lines 186–189. However, these are additions in the modified working tree: `git show HEAD:corpus/SOURCES.md | grep -E 'S174|S175|S176|S177'` returned no rows. The stated existence requirement is met in the current file, but the citations are not yet durable in the committed tree.
- Class behavior was compared against the frozen counter's committed definitions (`count-c1.py:11-32,62-74,124-125,232-264`) and C1 predicate in committed `preregistration.json:14-24`. No fresh counter run was performed; the `--help` invocation only confirmed CLI options. The visible `final/` receipt is untracked and was not used as committed evidence.

## Residual risk / verification gaps

The rule set is a bounded extractor, not a semantic proofreader, as the entry itself states at line 22. No fresh-clone run was performed in this seat. No tools were installed.