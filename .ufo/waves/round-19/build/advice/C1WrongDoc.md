VERDICT: confirm - citation-provenance.py enforces doc-scoped token presence: relocating the s055-commands cite() token verbatim from a scanned doc (corpus/lessons/round-18.md) into a non-scanned doc (corpus/lessons/round-17.md) yields missing=1 / exit 1 with the git blob digest still matching, and scanning round-17.md explicitly restores missing=0 / exit 0.

Axes: calibration (primary, axis 7->8 claim C1); operability untouched.

Probe (all commands executed in /tmp/kama-r19-C1WrongDoc, copy of lane tip tree, HEAD 8bf99cae; receipts in /tmp/kama-r19-C1WrongDoc/out — baseline.json, mutation.patch, mutated-default-docs.txt, contrast-including-r17.json, RECEIPT.md):

1. Baseline `python3 tools/citation-provenance.py --json` → exit 0, required=3 found=3 verified=3 missing=0 mismatch=0; all three tokens hosted only by corpus/lessons/round-18.md.
2. Mutation: moved the s055-commands bullet+token (round-18.md lines 416-417) byte-identically to the end of corpus/lessons/round-17.md. round-17.md is not in DEFAULT_DOCS (round-18.md, SOURCES.md, SCORECARD.md, LOG.md).
3. `python3 tools/citation-provenance.py` → exit 1, `required=3 found=2 verified=2 missing=1 mismatch=0`, row `s055-commands` status=missing with documents=[] while observed_sha256 still equals the token digest. Exactly the requested missing=1.
4. Contrast `--docs corpus/lessons/round-17.md <remaining defaults>` → exit 0, missing=0, s055-commands documents=["corpus/lessons/round-17.md"]. Confirms the failure is purely doc-scoping, not token bytes, registry, or git state.

Findings:
- Confirmed property: a required citation is only satisfied when its exact token appears in a scanned document; tokens in unscanned corpus files do not count. C1's machine-checkability holds under this mutation class.
- Minor UX (non-blocking): for a missing row the text output prints `expected=ce7dc79c9523 observed=ce7dc79c9523` (git verification still ran), which can read as a digest match; the JSON is unambiguous (`status: missing`, `documents: []`).
- Residual risk [INFERENCE]: `--docs` is caller-selected, so an invocation that widens the doc set can launder a relocated token back to exit 0 (demonstrated by the contrast run). Official measurements should invoke without `--docs` or with a pinned doc list so doc scoping stays part of the calibration guarantee.

No lane files modified other than this advice report.
