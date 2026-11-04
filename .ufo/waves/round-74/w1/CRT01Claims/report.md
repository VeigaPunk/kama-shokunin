# CRT01Claims — round-74 w1 critic report

Seat: CRT01Claims (critic; falsify C1/C2/C3). Axis: calibration.
Full attempt log with commands and outputs: `attack.md` (this directory).
Working receipts (pre-scratch-deletion): `receipts-full.txt` (this directory).

## Verdict

**No claim refuted on its own terms.** All three v2 modules survived every fixture
this seat constructed — 11 new attack fixtures plus 5 randomized-path copies of the
frozen set — with verdicts and counts matching the critic's oracle counters across
the whole matrix. Four freeze-level under-specification defects are routed
report-only (F1b, F2b, F2c, F2g; F3c is a semantics note): the "the frozen fixtures
cannot distinguish two minimally-compliant implementations" class — calibration
findings about the claims, not contradictions. The freeze was not edited.

Landed modules and their receipts:

| Module | sha256 (graded bytes) | Selftest | Frozen scorer |
|---|---|---|---|
| `round74-selfdesc-canon.py` (C1) | `2f4e473f5ad9f999042155edcf01995cdf8e05c477dedaafc516657f3608eea7` | `SELFDESC_CANON_V2_SELFTEST pass=11 fail=0` | c1 v2_killed=1 clean=True |
| `round74-receipt-claim-binding.py` (C2) | `0f231fac27a2b49e99a8d186162f62942a7f9328bf0dcb8d987eabc98051ab44` | `RECEIPT_CLAIM_V2_SELFTEST pass=15 fail=0` | c2 v2_killed=2 clean=True |
| `round74-province-host-drift.py` (C3) | `118ae079a7f5a18fa40548940eea8d5e8b6fdfbf28c953c997b911f2dba6bad7` | `PROVINCE_HOST_DRIFT_V2_SELFTEST pass=10 fail=0` | c3 v2_killed=1 clean=True |

C2 build attribution per the integration commit `07994dfc`: "EX02 dead at spawn;
C2 built by L1" — EX02ClaimV2's provider died on a 429 during the wave; the module
was landed and revised during this seat and its tested bytes are what this seat
graded. EX02's preserved receipts live under `.ufo/waves/round-74/w1/EX02ClaimV2/`.

C1/C3 bytes were byte-stable across this entire seat (sha256 before/after diff
empty). C2 byte volatility after grading is disclosed below (F2h).

## What was run (evidence: attack.md + receipts-full.txt)

1. Frozen fixtures rebuilt into my scratch with the committed builder
   (`KAMA_R74_SCRATCH=.../CRT01Claims/fixtures`); base legs reproduce the
   frozen holes: BASE_C1 canon_round=71/rows=3; BASE_C2 claims=0 GREEN on
   wrapped+offset; BASE_C3 stale=0 GREEN on edited.
2. Frozen selftests re-run at this run time, all green: r42 5/5, r72 16/16,
   r73-c2 14/14, r73-c3 9/9.
3. Oracle counters (the critic's own reference implementations of the three
   frozen predicates) validated against every frozen expectation, then used to
   grade the executors' modules on the attack fixtures. The C2 oracle has one
   deliberate literal-vs-context fork documented at F2c; it grades the literal
   reading, which the landed C2 module matches.
4. Frozen counting command `score-survivors.py` over the committed
   controls-work fixtures, final state: c1 v2_killed=1 clean=True; c2
   base_green=2 v2_killed=2 clean=True; c3 v2_killed=1 clean=True.
5. PREDICATE constants: whitespace-normalized byte-match against the plan's
   frozen blockquotes for all three modules.

## Routed defects (freeze under-specification; report-only per kumitate r42)

- **F1b — C1 `total` semantics.** Record with a demonstrated table OLDER than the
  newest bold canon (`nc1_old_demo`): the v2 prints total=7 (bold ∪
  demonstrated-newer-than-bold), my oracle prints total=8 (union over all
  recognized tables). The freeze's "`total` counts the distinct names across the
  newest-by-round resolution" admits both; the frozen fixtures cannot distinguish
  them. Smallest safe correction (future round): pin `total` to the hand census
  with an older-demonstrated fixture.
- **F2b — C2 finding-kind enumeration gap.** One paragraph citing two receipts with
  one tip claim and no explicit revision (`nc2_two_receipts`): unbound, but not
  wrapped-claim, not offset-claim, not literally stale-revision. The module's
  repair — one `stale-revision` finding per unbound receipt — is accepted for this
  wave (contested and closed with EX02ClaimV2); the oracle's r73-inherited
  `stale-claim` is the other compliant repair. Both exit 1; the verdict is
  unaffected. Smallest safe correction: pin the kind in the predicate sentence.
- **F2c — C2 "names an explicit 40-hex revision" is context-free.** A `recorded at
  <hex>` content-id clause (`nc2_recorded_at_hex`) binds under the literal reading
  (module + literal oracle: exit 1 stale-revision) and is ignored under a context
  reading (exit 0). The frozen fixtures cannot distinguish the readings. Smallest
  safe correction: define the binding context, or affirm the literal semantics.
- **F2g — C2 finding `<path>` field unpinned.** The v2 names the receipt path;
  r73 and the oracle name the record path. No verdict impact (scorer greps the
  kind); pin in a future freeze.

## Scorer blind spots named (arm 2) — all three closed by the landed modules' selftests

- C2: the frozen set never contains an explicit-revision mention ≠ receipt header
  (F2a: `nc2_stale_explicit`, module: exit 1 stale-revision), never a two-receipt
  claim (F2b), and keeps the lesson blob a stub (F2f: `nc2_lesson_only`, module:
  exit 1 wrapped-claim at the lesson line). A never-stale-revision / lesson-blind
  v2 passes all four frozen fixtures; the landed module does neither.
- C3: the frozen set is single-block-only, so a "preserve only the newest block"
  gut passes `score-survivors.py`. Catch fixture: `nc3_newest_no_token` (edited
  older block under a clean newest; module: exit 1 edited-block — it grades every
  token-carrying block).

## Arm 3 (mixed-case) — load-bearing, refutation of the arm FAILS

Case-sensitive strawman (`strawman-casesensitive.py`, a 1-line mutation of the
oracle) exits 0 on `c2_clean_realizable` and fails `c2_mixed_honest` twice: a
`stale-revision` finding (exit 1) and `bound_revisions=0` against
score-survivors.py's `bound_revisions=1` check. Exact record text and the honesty
proof (upper-case hex == the receipt's own commit) are in attack.md F2d.

## Arm 4 (score-survivors gaming) — gaming fails for all three modules

Acceptance criterion (pre-registered): honest grading must reproduce named-fixture
verdicts on byte-identical copies at randomized paths (`zz-*`, no fixture token in
the name). Receipts — every zz-copy verdict is identical to its named fixture, for
both the v2 modules and the oracle (full lines in attack.md F1d/F2e/F3e and
receipts-full.txt). Grep of all three grading paths: no `sys.argv`/basename/
fixture-name branching (the C2 module's 7 fixture-name hits are all selftest-scoped
lines 483-727). Selftests build fixtures under `tempfile.mkdtemp` with generic
names. No hardcoded fixture paths.

## Disclosures (process)

- **F2h — C2 live-path volatility.** After EX02's tested bytes (0f231fac) were
  fully graded, `tools/round74-receipt-claim-binding.py` was observed rotating
  through further digests (fb34f3d9 → ac7dc369 → 5c6174c4 within ~4 minutes,
  mtime 01:25, size 24570 vs EX02's 32144) under concurrent mutation-testing
  activity. An earlier overwrite (8d7329e7, unimportable) is preserved by
  EX02ClaimV2 at `.ufo/waves/round-74/w1/EX02ClaimV2/receipts/
  overwritten-peer-version.py`. Every observed variant was re-run against my C2
  matrix and remained oracle-consistent on verdicts and counts; at least one
  variant fails the module's own selftest (`blob-reader-seam`), which is the
  mutation kill mechanism working as intended. My graded-verdict receipts pin
  0f231fac; the L1 should re-run `score-survivors.py` after the mutation-testing
  seats settle and confirm the live bytes return to a selftest-green digest.
- C1 v2 selftest without `--repo` from a cwd lacking `plans/` dies with a raw
  FileNotFoundError traceback rather than a usage error; with `--repo` it is
  11/11 green. Robustness nit, not a predicate violation.
- C1 v2 prints `canon_round=71 canon_rows=3` on `c1_invisible` with `total=7` —
  bold-canon identity alongside union total; consistent with one predicate reading;
  unscored. F1b covers the adjacent ambiguity.
- C3: the freeze's literal "byte-identical at `<rev>`" is unimplementable for the
  frozen fixtures (the block does not exist at rev A there); the landed module
  resolves first-appearance bytes in A..tip (`resolved-at=` in its finding), the
  same semantics as the oracle. Receipt-level observable, not a defect.

## Hygiene

- No frozen file edited; no mutating git/jj command anywhere (fixture repos under
  my scratch only, fixture identity, toplevel asserted, `init -b master` to match
  the committed builder).
- No installs/upgrades needed (python3 stdlib only).
- Scratch dir `/fast/scratch/hyaku/kama-r74/CRT01Claims/` deleted after receipts
  were copied into this out dir. No /tmp evidence cited.
