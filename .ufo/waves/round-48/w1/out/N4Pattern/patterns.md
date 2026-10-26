# Cross-claim instrument patterns

Axes: calibration and operability. Evidence below is from the current lane tree; the ranked items are residual patterns, not a claim that the tools are defective.

## Ranked by easiest useful exploit

1. **Self-declared `unverifiable` escape hatch (hexrun census):** `tools/hexrun-census.py:26-33` assigns a token to `unverifiable` if its ledger row's note has ten characters, and `:41-42` treats that class as passing. The note is not independently checked for why upstream evidence is unavailable. A submitter can therefore make an otherwise unknown 32–127-character token non-blocking by adding a sufficiently long assertion. This is the lowest-cost bypass: edit the classification ledger, not the cited artifact. C1's declaration-bound carve-outs are a useful contrast: they require a declaration at a located line, while this row's note length does not bind to evidence.

2. **Receipt is explicitly self-report (GGUF identity):** `tools/gguf-identity.py:8-10` explicitly labels receipt results receipt-self-report evidence; it accepts a supplied receipt via `--receipt` at `:4-6`. A receipt can state metadata correspondence without the tool acquiring the source artifact/runtime that generated the claim. The local file's own header and hash are real evidence, but do not independently authenticate a supplied receipt. A forged or stale receipt can be exploited first where downstream consumers treat receipt reconciliation as provenance rather than correspondence. This is materially weaker than C2's fresh acquisition and pre-execution digest checks.

3. **Embedded definition checked against the counter (context-capacity):** `tools/kama-context-capacity.py:599-616` imports the counter's `CELLS`; `:619-635` compares those cells to the tool's embedded cells. This catches drift, but agreement is not independent semantic validation: if both definitions are changed together, the shared contract can move without an external authority. An attacker would target the shared definition/counter pair, then retain matching tool output. This is a calibration weakness, not evidence of an observed exploit.

## Not ranked as residual acceptance

The `citation-provenance.py` contract at `:11-14` (tool lines) checks both an exact document token and SHA-256 of the Git blob at the named revision; that is not merely trusting a receipt. C1 and C2 are likewise the specified stronger patterns for their claims. `tools/hexrun-census.py:29-31` also independently checks upstream evidence bytes and repo text for the `upstream` class; the concern above is specifically its `unverifiable` arm.

## Bounded move

For hexrun, make the non-verifiable disposition require a separately grounded reason/evidence category rather than note length alone, or explicitly downgrade `unverifiable` from passing exit status. This improves calibration without altering upstream hashing behavior. For GGUF, keep the receipt-self-report label prominent at every downstream acceptance boundary; do not treat it as acquired runtime provenance. For context-capacity, bind accepted cell definitions to a separately frozen declaration/digest if the intended claim is independent calibration.

Risk/contradiction: eliminating the hexrun escape hatch can convert legitimately unavailable upstream material into a hard census failure; changing that verdict may harm operability. Keep the category but require auditable justification if a pass result is required. This report did not execute these instruments or test a proposed change; verification should include a forged long-note ledger case, a fabricated GGUF receipt case, and a coordinated embedded/counter definition mutation case.
