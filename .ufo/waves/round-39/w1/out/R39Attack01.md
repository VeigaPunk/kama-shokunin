# R39Attack01 — C1 calibration claim (7→7) / no-op inspection

Scout findings on committed/working evidence only (read-only; no edits, no spawn).

## Claim under test

C1 calibration `7 → 7` frozen at base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`:
"Round lesson Gate has an admit and at least one package-theme reject with reason and
flip; admitted source S472 is newly cited by the amendment, and its located quote
resolves at Markdown line 17." Control: at base no round-39 lesson/entry or S472
exists, so predicate is false.

## Observed facts

### 1. Base control verified (predicate false at base)
- `git show 6a4afdfe:corpus/SOURCES.md` → 203 registry rows, **0** S472 matches.
- `git show 6a4afdfe:corpus/lessons/round-39.md` → absent.
- `git show 6a4afdfe:corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` → absent.
- Recorded base control `assimilation/c1-noop.out`: `admit=0 reject=0 source_rows=203 met=False exit=1` — matches the frozen control claim.

### 2. Frozen predicates unchanged
- `preregistration-frozen.json` ≡ `preregistration.json` (identical claims, base, controls, `frozen_before_data: true`). No drift.

### 3. Working-tip evidence present (claim is NOT a no-op)
- **S472 row** added in `corpus/SOURCES.md` (line ≈216): OpenAI List models URL, tier A, `mined`, opened `2026-10-25`, recheck 90d, used-by = the amendment file; selector §List models → Returns → `created`, line 17; quote: `The Unix timestamp (in seconds) when the model was created.`
- **Quote resolves at line 17**: `assimilation/openai-list.md` = 1,657 bytes, sha256 `2bbf06bb7a1687dbc9d25ce86c5d249b3f9d1e2c60efc32dbf7af2e4d052793f` (matches recorded hash); the quote is exactly at line 17 of that file.
- **Lesson Gate** `corpus/lessons/round-39.md` records:
  - 1 admit: "Admit the amendment `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` …" (`grep -c 'Admit the amendment'` = 1);
  - 1 staged reject (reason + flip): "Reject staged `runtime-health-surface-matrix-amendment-2026-10-24-r16.md` …" (`grep -c '^Reject staged'` = 1);
  - plus a second reject: "Also reject `hosted-health-route-configuration.md` … Flip: …" (superset of the ≥1 reject requirement).
- **Amendment file exists** at `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` (3,994 B), cites S472, and contains a "Round 39 opened-source correction — 2026-10-25" section (re-open + located description). It differs from the read-only fleet package original (`…/merge/kama/knowledge/corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`, 3,551 B, sha `9e1e7405…`) exactly by that appended correction section → consistent with porting + re-grounding, not silent rewrite.
- **SCORECARD.md** tip row (round 39) states C1 `admit 0→1, rejects 0→1, sourced_rows 0→1`, calibration held `7 → 7` with explicit "held … not a promotion" note.
- Registry rows 203 → 204 (single new row S472) reproduced.

## Possible weak points (noted, not falsifying)
- The amendment filename/title is round-16 dated (2026-10-24) but the file is absent from kama's history at base; it is ported from the fleet merge package and extended this round. C1's predicate does not require the amendment to be new, only that S472 is newly cited by it — satisfied.
- The quote literally supports "created = creation timestamp"; the lesson's framing ("created is catalog metadata, not artifact identity") is an interpretive step beyond the quote bytes, but it matches the S016 row's recorded semantics.

## Conclusion
No falsification observed. The frozen base control is correct (no lesson, no S472, predicate false at base), the tip predicate holds (admit + rejects with flips; S472 newly cited; quote resolves at line 17), and the claim is not a no-op: S472, the lesson Gate decisions, and the amendment's S472 citation are all concretely present at tip and absent at base. Calibration stayed 7→7 as declared.
