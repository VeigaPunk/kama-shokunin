# ProvenanceR2 — falsification of the named R2 partial-output clarification

**Seat:** `KamaR15.ProvenanceR2` (leaf, no dispatch)
**Bound:** committed `round-14/advice/ExistingProbe.md`, `round-14/integration-review.json`, and the R2 text (draft `round-15/build/advice/R2Partial.md`, landed `corpus/lessons/round-15.md`, line 36–38). No session/history, no credential, no `agent.db`, no `omp` CLI. No checks, tests, builds, or smoke runs executed. Tooling: none installed or updated; no pacman transaction.

## Verdict

The landed clarification's core rule holds: a committed advice file is not terminal success of its seat, and a provider failure does not prove absence of partial output. Three landed phrases do not hold against the bounded record. One draft rule is defective and must not be imported. One draft finding is not established inside the bound.

## Evidence read (line-anchored)

- `integration-review.json:10` accepted row: "ScopeSimplifier/ExistingProbe contract: no basename/GGUF/case/implicit latest normalization; no integration with old live probe". Keyed to ScopeSimplifier's contract, not to seat `KamaR14.ExistingProbe`.
- `integration-review.json:23` `wave.dead_seats`: `KamaR14.ExistingProbe`, reason "Cursor RESOURCE_EXHAUSTED; provider unreachable", scope "read-only existing-probe reconnaissance; source convention independently held in SKILL and crosswalk". This is the only seat-keyed field in the file. The file has no replacement field and no date.
- `ExistingProbe.md#2AEF` header: `verified-at: actual review 2026-10-20 (UTC)`, self-declared. §6 "Limits & Evidence Grounding" presents the file as a complete read-only review. The file carries no marker of partiality.
- `ExistingProbe.md:102`: "remote tags or selected ps markers -> remote_inventory regardless digest".
- `ExistingProbe.md:118–123`: adversarial rows labelled C1–C6. `ExistingProbe.md:108`: "Calibration C1".
- `ExistingProbe.md:119` C2 expected: "`unknown` (exit 2) or `remote_inventory` (exit 1)".

## Findings against the landed clarification (`corpus/lessons/round-15.md:36–38`)

**F1 — misattribution risk (landed, fail as worded).** Line 38 says `integration-review.json` "credits that bounded contract", after "substantive partial normalization advice is committed". Read with the file, "that bounded contract" can point at the ExistingProbe file. The record credits ScopeSimplifier's contract (`:10`). Its `dead_seats` scope (`:23`) says the source convention is "independently held in SKILL and crosswalk", which means integration did not rely on the ExistingProbe output. The phrase admits a reading the record does not support. Bounded fix: say the accepted row cites ScopeSimplifier's contract and does not credit the file.

**F2 — "no replacement" unsupported in bound (landed, unsupported).** Line 38: "recorded with `Cursor RESOURCE_EXHAUSTED` and no replacement." The integration record states the dead status and the reason only. It says nothing about replacement. The only support I saw is a paraphrase in `ReceiptReview.md` quoting round-14 LOG, which is outside this bound and was not opened. Within bound this phrase is unverified.

**F3 — "partial" is an inference, not an observed property (landed, inference unlabelled).** Line 38 calls the file "substantive partial normalization advice". The file has no partial marker and self-describes as complete (§6). The "partial" label derives only from the seat's dead status. The landed text should mark it `[INFERENCE]` or drop the word. The core non-inference claim ("existence ≠ terminal success") does not depend on this word.

**Holds:** "Provider failure does not prove absent partial output. A committed advice file does not prove a successful terminal completion either." This is consistent with `dead_seats` and makes no provenance claim. The landed text correctly does not claim who wrote the file or when. The file's header date (2026-10-20) is self-declared and cannot be compared with the dead-seat record, because the record has no date.

## Findings against the draft (`round-15/build/advice/R2Partial.md`)

**F4 — draft terminal rule is not mechanically applicable (draft, defective; not landed).** Draft line 33: a seat is terminal "only when the integration record gives that seat an accepted disposition." `accepted` rows are not seat-keyed; the only seat-keyed field is `dead_seats`. The rule therefore cannot be applied as written to KamaR14.ExistingProbe. The landed lesson does not contain this rule. Do not import it.

**F5 — draft self-contradiction (draft, minor).** Draft §2 says the file "is complete as prose" and then calls it "partial output". Same unlabelled inference as F3.

**F6 — draft C2 conclusion not established inside bound (draft line 25; not landed).** The draft says the only correct C2 result is `unknown` (exit 2), citing "rulings rule 3", which is `rulings.json`. That file is outside this bound and was not read. Inside the bound, `ExistingProbe.md:102` reads "remote tags or selected ps markers -> remote_inventory", which can be parsed as remote tags needing no selection. The hedge at `:119` therefore traces to an ambiguous quote, not to a plain error. The draft's "only correct result" is stated as fact without support in the bound. L1 must read `rulings.json` before any owner is told the hedge is wrong. The C2 hedge is not in the landed text, so the landed artifact is not affected.

**F7 — identifier collision confirmed (ExistingProbe, pass).** `ExistingProbe.md:118–123` uses C1–C6 for adversarial rows, while `:108` and the wave's calibration claim also use C1. The draft's collision observation is correct. This affects the advice file only. The landed clarification does not cite the C-labels.

## Not verified (outside bound, not read)

`rulings.json`, `swarm-registry.json`, `tools/kama-probe.sh`, the round-14 LOG or ReceiptReview entries, and every citation in `ExistingProbe.md` §6. F2 and F6 depend on the first of these.

## Recommended handling for L1 (no new feature)

1. Keep the landed R2 text, with F1 wording fixed (credit goes to ScopeSimplifier's contract, not to the file) and F2 removed or sourced to a file L1 opens. F3 marked `[INFERENCE]` or the word "partial" dropped.
2. Do not append the draft §4 text as written. It contains F4.
3. Do not send the C2 hedge to an owner until `rulings.json` has been read (F6).

Files written: this report only. Files read: as listed under Evidence and Bound. No history or session files opened.

Report: .ufo/waves/round-15/falsify/advice/ProvenanceR2.md
