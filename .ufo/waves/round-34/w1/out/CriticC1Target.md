# CriticC1Target — attack on the C1 target

## Verdict

**The claimed `missing 3` is a convention artifact, not a demonstrated self-assessment mismatch.** The round-16 table is not labelled “frozen”, but it is explicitly a canonical list **“as of round 16”**; the later per-round `capabilities: append` tables are themselves repertoire rows, not merely uncounted demonstration notes. Their absence from the old physical table therefore does not make them absent from SCORECARD's live repertoire.

The local evidence supports a narrower defect: **the consolidated canonical roster is still the three capabilities named in rounds 16–17, while the distributed repertoire has six rows.** A consolidated index may be useful, but creating one does not correct a previously false capability self-assessment.

**Impacted axis:** calibration — no false statement at the before revision has been identified. C2/operability is unaffected. This is a fixable target defect, not an axis tradeoff to net out.

## Exact lines that decide it

1. The fleet contract defines a repertoire and its admission rule, but does **not** designate one physical canonical table as the exclusive place where every current row must appear:

   - `AXES.md:59-64`: “`SCORECARD.md` therefore carries a separate `capabilities:` table — name → what it can now do (one line) → evidence pointer (command or path) → first-working round. Rows enter only through a round that demonstrates the capability running”.
   - `AXES.md:80` likewise says “The repertoire table (see Capabilities)”. Neither sentence says that later per-round append tables are outside the repertoire or that an old canonical table must be edited.

2. Round 16 is time-qualified, not declared the permanently exhaustive current table:

   - `SCORECARD.md:621-622`: “**Capabilities — canonical list as of round 16** (supersedes the one-row table at lines 122-128 without editing it; rows enter only with a demonstration)”.
   - `SCORECARD.md:692`: “**Capabilities — canonical list as of round 17:** unchanged from round 16”. This reinforces the dated-snapshot convention; it does not say “frozen forever”, but neither does it make the round-16 physical table the exclusive live union.

3. Round 20 expressly makes its append row part of the repertoire:

   - `SCORECARD.md:909`: “### capabilities: append — first working round 20”.
   - `SCORECARD.md:913` lists `gguf-declared-identity-replay` with its demonstration and first-working round.
   - Most decisively, `SCORECARD.md:915`: “**The three canonical round-16 capabilities remain; this adds one repertoire row.**” It does not say “this adds a historical demonstration outside the repertoire”.

4. The same convention carries the other two supposedly missing capabilities:

   - `SCORECARD.md:1298-1302`: `### capabilities: append — first working round 25`, followed by `context-capacity-receipt` and its demonstration.
   - `SCORECARD.md:1551-1555`: `### capabilities: append — first working round 30`, followed by `instrument-agreement` and its demonstration.
   - `SCORECARD.md:1609-1610` subsequently says “`instrument-agreement` (round 30) is unchanged”, treating that append row as part of the then-current repertoire.

5. Prior local review explicitly rejected the premise that this placement is wrong. `.ufo/waves/round-25/a2-falsify/advice/ReviewerScorecardLog.md:61-63` says that round 25 “uses the per-round `### capabilities: append` form, which round 20 also uses”, and concludes: “**so the row is not in the wrong place.**”

6. Calibration requires an actual before-state mismatch, not merely a less convenient layout. `AXES.md:15` defines its signal as “SHONEN.md/SCORECARD entries match observed repo state”. The routed outside closure at `corpus/lessons/round-25-verifier-spotcheck.md:230-232` is even more specific: “**A calibration claim must count statements in SCORECARD or SHONEN that are false against the repo at the before revision.**” The dated round-16 statement was true as of round 16, and the three later rows exist. Neither is a false before statement.

## Strongest counterexample to C1

At the base, a document-wide reading already finds six uniquely named, demonstrated capability rows:

- the round-16 canonical rows: `sources-registry`, `ollama-offline-evidence-replay`, `live-llamacpp-lifecycle`;
- the later append rows: `gguf-declared-identity-replay`, `context-capacity-receipt`, `instrument-agreement`.

Thus `listed` and `observed` can already both be 6 with `missing 0` when the repertoire is read as the append-only union. The preregistration's expected `missing 3` arises only by defining `listed` as membership in the old physical table while defining `observed` across the later tables too. That asymmetric population manufactures the red-before.

Conversely, if `listed` means only the newest canonical table, then a **pure duplicate-table control** defeats the claimed improvement: append a “canonical as of round 34” table repeating the three already-declared later rows and their existing evidence. No capability is acquired, no demonstration changes, and no previously false SCORECARD statement is corrected, yet the proposed count can move 3/6 to 6/6. The frozen kill rule rejects invented names and names without resolving evidence, but it does not reject this redundant duplication of already-valid rows. A counter that passes it does not separate a self-assessment correction from a presentation-only no-op.

This review does not certify `U == 0`; an unresolved evidence token would be a separate, concrete defect. It does not rescue the asserted `missing 3`.

## Smallest safe correction

The smallest wording that is true under either interpretation is:

> **The consolidated canonical roster (the round-16 table, restated in round 17) covers only three of the six capabilities already declared across SCORECARD's canonical and per-round append tables.**

If index consolidation is the intended work, replace the claim surface with:

> **Consolidated-index completion only:** SCORECARD already lists six demonstrated capabilities in its distributed repertoire. Append a round-34 index that references all six existing authoritative rows; before consolidated-index coverage is 3/6, after 6/6. No new capability and no correction of a false capability statement is claimed.

Use references to the existing rows rather than duplicate full descriptions, avoiding two authorities that can drift. That wording makes the documentation work honest, but **does not establish calibration credit**; under the quoted calibration rule, C1 should honest-stop unless a separate false before statement is named.

If the intended convention is instead that the canonical table is the exclusive live repertoire, that authority rule must be stated prospectively; it is not in `AXES.md` and is in tension with round 20's “this adds one repertoire row” and the prior placement review. Under that new convention the honest claim is still only “the consolidated canonical roster omits three otherwise declared capabilities”, never “SCORECARD failed to list three capabilities”.

## Review boundary

Static target/contract review only. `tools/capability-repertoire-audit.py` was absent when inspected, so no counter output is claimed. `git diff --exit-code 7c35289da5f4b94e062cd900eb086919e5094003 -- SCORECARD.md` exited 0, binding the quoted SCORECARD text to the preregistered base. No tools installed; no lane source or history modified.
