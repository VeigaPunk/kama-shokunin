# ConnectorSiblings — sibling-overlap scan (round 29, wave 1)

Lane: kama-shokunin. Scope: read-only scan of `/home/vgpnk/Projects/shokunin/*-shokunin/`. No lane files edited; no absorption.

## (a) Province ownership of self-assessment / statement-at-writing checking or git-history auditing

- No sibling `PROVINCE.md` claims self-assessment statement checking at a writing revision, or git-history auditing as a domain. Grep of all `PROVINCE.md` for `self-assess`, `statement-at-writing`, `writing revision`, `git blame`, and `git history` returned no owner; the only `git history` hit is souji-shokunin `PROVINCE.md:34` refusing history rewrite (not auditing statements).
- Closest adjacent instruments, by tool name only (not province ownership):
  - `tsukuroi-shokunin/tools/check-self-assessment.py` — axis self-assessment for tsukuroi's own SCORECARD axes (round 26 C2), not statement classes at W.
  - `tsukuroi-shokunin/tools/check-owed-statements-r29.py` — tsukuroi's own owed statements O01–O12 (round 29 C1, axis depth), a different claim and base (`16e9ab2a`).
  - `kaidoku-shokunin/tools/round-25/a2/c1-calibration.py` — kaidoku's own fixed-item self-assessment mismatch count at one revision (I1–I4), not writing-revision statement classes.
- Conclusion: kama's C1 (69 base statements, P/H/N/C/T/Q, `git blame --line-porcelain` writing revision) has no sibling province owner; contested scope is nil, not absorbed.

## (b) Sibling instruments that duplicate C1

- Search across `*-shokunin/tools`, `*-shokunin/scripts`, `*-shokunin/verifiers` for `line-porcelain`, `mismatched_at_base`, `SA29`, `owed statements`, and `statement-at-writing` found only `kama-shokunin/.ufo/waves/round-29/count-c1.py` (plus tsukuroi's owed-statements tool, which uses different ids/rules).
- No sibling uses `git blame --line-porcelain` to assign a writing revision to a SCORECARD/SHONEN statement or checks the six classes P/H/N/C/T/Q. No duplicate instrument found.
- Adjacent but distinct: kotoba-shokunin `verifiers/check_sibling_census.py` and `corpus/knowledge/sibling-overlap-census-round49.md` audit sibling-overlap claims; they do not check statement truth at W.

## (c) Kama corpus content that belongs to another lane

- `corpus/knowledge/free-tier-provider-limits.md` (lines 1–13, 46–48): dispatch/load-test telemetry. Kama already hands alias/loopback re-derivation to operator/kumitate (`corpus/knowledge/alias-endpoint-normalization.md:70`; `corpus/knowledge/cross-lane-scope.md` §Consumer ownership). Contested only if read as a dispatch claim; keep as dated census + handoff, no absorption.
- `corpus/knowledge/context-capacity.md:235–237`: cites kengaku's production capture of 34113; kengaku owns the capture, kama cites it. Already a citation, not absorption.
- `corpus/knowledge/error-is-not-a-verdict.md`: mutation-testing vocabulary applied to kama's own `report-landing-audit.py` gates; adjacent to tameshi's method, but the instrument and defect class are kama's. No transfer.
- `corpus/knowledge/cross-lane-scope.md` is the lane's existing handoff ledger and already names owners for credentials (kagi), eval quality (kengaku), routing (kumitate), instruction text (kotoba), host config (operator). No new bleed found beyond those named handoffs.

## Pointers

- kama C1 definition: `preregistration.json` claim C1; counter `.ufo/waves/round-29/count-c1.py` (sha256 fe11d599…7383); base receipt `.ufo/waves/round-29/before/c1-base.json` (69 statements, 11 false at W).
- Routed repairs source: `corpus/lessons/round-28-verifier-spotcheck.md:220–247`.
- Sibling ownership references: `tsukuroi-shokunin/PROVINCE.md` (host operability; refuses endpoint health → kama), `kaidoku-shokunin/PROVINCE.md`, `kotoba-shokunin/PROVINCE.md` § Adjacent (kama adjacent).
- Kama handoff ledger: `corpus/knowledge/cross-lane-scope.md` (consumer ownership + contested scope table).

## Proposed move (bounded)

Add a short, append-only adjacency note to kama's existing handoff ledger (or a new `corpus/knowledge/sibling-overlap-r29.md`) recording the scan result: no sibling province owns statement-at-writing/git-history auditing, no C1 duplicate instrument exists, and the three handoff points above remain routed, not absorbed. Proposed text is in this out dir as `cross-lane-scope-addendum.md` for L1 integration. This improves adjacency without touching calibration evidence or runtime surfaces.

## Risks

- The note could be mistaken for an ownership ruling; it is a scan report only and defers to the integrator.
- `free-tier-provider-limits.md` remains a contested read if quoted as dispatch authority; keep its dated-census framing.
- No tracked lane file is changed by this seat.

## Verification

- `grep -rni "self-assess\|statement-at-writing\|writing revision\|git blame" *-shokunin/PROVINCE.md` → no owner (only souji refusing history rewrite).
- `grep -rl "line-porcelain" *-shokunin/tools *-shokunin/scripts *-shokunin/verifiers` → none.
- `grep -rl "SA29\|owed statements" *-shokunin/tools ...` → only tsukuroi's distinct owed-statements tool.
- Out dir contains only this file and `cross-lane-scope-addendum.md`.
