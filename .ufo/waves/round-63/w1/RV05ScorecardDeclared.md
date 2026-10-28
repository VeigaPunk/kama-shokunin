# RV05ScorecardDeclared — round 63 SCORECARD / freeze / append-only review

Seat: RV05ScorecardDeclared (reviewer, leaf). Item: review the SCORECARD.md "Round 63" section
against `controls/freeze.txt`; the canonical-list byte identity with round 62; any score, admission
or live-completion capability claim before measurement; `tools/append-only-audit.py` against the
committed history and `registry/append-only-contract.tsv` for violations by the freeze commit.

Refs: base `7ee8cbdf160f8c945954e4737e7a2f797e3b2987` (round-62 close-out); freeze `675cac02c966b7db5429d335e6b91158c8dd59cf`;
amendment 1 `03a6a1d850902a66a13dfad33f89cf3a8b759a09` (tip under test). Measured by reading committed bytes
(`git show`, `git diff`) and by running `tools/append-only-audit.py` and `tools/round42-selfdesc-reconcile.py` on a
clone of the lane at each revision. No commit, edit, or live server run was made. Receipts: `out/RV05ScorecardDeclared/`.

## Findings (by severity)

### F1 — the section's "no lane-authored untracked paths" claim is contradicted by the worktree (prominent)

SCORECARD round-63 intro: "the lane worktree now has no lane-authored untracked paths".
`git ls-files --others --exclude-standard` in the lane lists one untracked path that is not round-63 wave output:

- `kama-shokunin/.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` (nested `kama-shokunin/` directory at the lane root).
  - mtime `2026-10-28 09:26:49 -0300`, which predates freeze `675cac02` (base 10:43, export 19:05).
    A file with that mtime existed at freeze time, so the claim was false when written.
  - Content is a lane-authored round-62 seat draft. It differs from the tracked copy
    `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md` (tracked since `7ee8cbdf`) at line 3 and later lines (`cmp` differs at byte 168).
  - This is the same class as routed defect 3 in `corpus/lessons/round-62-verifier-spotcheck.md` (untracked round-62 wave files), which the section says is closed.
- Current `git status` (read-only, at observation time): 3 modified tracked files (F4) and untracked round-63 wave output. The round-63 wave output post-dates the freeze and does not bear on the claim; the nested draft above is the only untracked path that predates it.

Recommended: remove or land the nested draft (owner: the round-62 seat's lane; not this seat), and either drop the
claim or scope it to the freeze-time worktree.

### F2 — the round-63 heading pre-states outcomes that the freeze does not claim (prominent, calibration)

Heading: "Round 63 — strict outside-bound request plane (operability) and a sensitivity test that can fail, with the
self-description reconciled (calibration) (2026-10-28)".

- "with the self-description reconciled" is a result. The freeze's own text says the reconciler stays at 8 at the tip
  ("base: 8; it is still 8 at 03a6a1d8 on purpose"). Measured:
  `tools/round42-selfdesc-reconcile.py --repo <clone> --tip 03a6a1d8` → `... mismatches=8 maxN=63 met=False` (exit 1;
  `out/RV05ScorecardDeclared/rec-tip.out`). Base gives the same 8 (`rec-base.out`).
- "a sensitivity test that can fail" asserts the C2 sensitivity result before measurement.
- The same section's body frames these as pending ("Claim rows are filled in … once measured"), so the heading and the
  body disagree in tense.

Recommended: retitle as an aim ("aims at …"), or re-title at closure with the measured numbers. This is the L1's
call; the section should not state a reconciled self-description at a tip where the reconciler reports 8.

### F3 — the section's freeze pointer omits amendment 1 (moderate, disclosure)

The section points to `.ufo/waves/round-63/controls/freeze.txt` and gives base `7ee8cbdf`. Amendment 1 (`03a6a1d8`)
changed that same file: it added the collateral cap, the 3-plant evaluator self-test, and the AMENDMENT 1 paragraph, and
it changed `tools/round63-c1-counter.py` (+46/−10) and two control files. Verified with `git diff 675cac02 03a6a1d8 --numstat`:

    2 2 .ufo/waves/round-63/controls/c1-base.txt
    15 0 .ufo/waves/round-63/controls/c1-mutants-prewave.txt
    2 2 .ufo/waves/round-63/controls/c1-relabel.txt
    14 2 .ufo/waves/round-63/controls/freeze.txt
    46 10 tools/round63-c1-counter.py

`freeze.txt` discloses the amendment itself, so the claim is disclosed in the file; the SCORECARD section does not
mention it. Recommended: name both the freeze commit and amendment 1 in the section (at closure is fine).
The amendment only adds checks: the diff removes `hit = (not s['met']) and expect in s['fails']` in favour of
`is_hit(...)` with a cap, so it tightens credit and does not loosen it. No loosening found.

### F4 — uncommitted working-tree prose asserts request-plane status before measurement (moderate)

`git diff` in the lane (not committed; HEAD is `03a6a1d8`):

- `PROVINCE.md` +2: "Round-63 note — the request plane moves from frontier to held fixture ground, and the claim
  registries enter the province (2026-10-28)." This is a status claim about the live request plane before C1 is measured.
  The freeze says "the SCORECARD head, PROVINCE.md pointers and Planned section are re-derived by the L1 AFTER measurement".
- `corpus/knowledge/completion-request-plane.md` +47/−3: a "Round-63 strict response grading" section with "observed"
  values from "the round-63 run" (`620 bytes`, `8 = 8`). These are dev-run observations, not the measured tip receipt,
  and the section describes the nine checks as graded.
- `corpus/SOURCES.md` +2: S527/S528 rows. Frontier rows are allowed by the freeze; the append is clean (see F6).

No score, admission or `live-completion-request-plane` capability row appears in the committed SCORECARD, the canonical
list, or `registry/capability-claims-r63.tsv`. The concern is sequencing: if these uncommitted edits land before the
measured tip, they claim a status (moved / graded / observed) that is not yet measured. Recommended: hold the PROVINCE
note and the knowledge-doc status sentences until the L1's post-measurement re-derivation.

### F5 — the lane's own append-only scan exits 1, and the bound C2 row cannot see it (calibration gap, not caused by the freeze)

`tools/append-only-audit.py --repo <clone> --to <rev> --json` on the clone (`out/RV05ScorecardDeclared/aoa-*.json`):

| rev | commits | events | restored | unrestored | disclosed | bad_declarations | exit |
|---|---|---|---|---|---|---|---|
| 7ee8cbdf (base) | 451 | 160 | 80 | 17 | 5 | 5 | 1 |
| 675cac02 (freeze) | 452 | 160 | 80 | 17 | 5 | 5 | 1 |
| 03a6a1d8 (tip) | 453 | 160 | 80 | 17 | 5 | 5 | 1 |

- `bad_declarations=5`: `declared_at` pointers no longer say append-only for their paths. `SCORECARD.md`,
  `corpus/QUALITY.md`, `corpus/README.md` point at `corpus/README.md:761`, which now reads "context-capacity rows' scope
  already excludes."; `corpus/SOURCES.md` points at `SKILL.md:578`; `corpus/lessons/*.md` points at `corpus/README.md:1239`
  ("Carried over unchanged and not re-measured here…"). Those pointers drifted before the freeze.
- `unrestored=17` includes round-62 commits, not only older ones: `a25dd0d9` (`corpus/lessons/round-62.md`, 5 lines deleted),
  `a837c8f7` (`SCORECARD.md` 2, `corpus/lessons/round-62.md` 2), `77bfaaa5` (`SCORECARD.md` 3). None restored.
  The round-62 closure (`corpus/lessons/round-62-verifier-spotcheck.md`) did not list these.
- The round-63 canonical row `append-only-audit` describes the full scan ("set the lane's contract-declared
  append-only self-description … against its git history"). Its bound run in
  `registry/capability-claims-r63.tsv` is `append-only-audit.py --selftest --scratch %S/aoa` (pattern `AOA_SELFTEST pass=`),
  which passes 51/51 (`out/…/aoa-selftest-03a6a1d8.out`). So the row would read `true` while the lane's own history scan
  is at exit 1 with 5 unbound declarations and 17 unrestored events. This is the calibration gap: the bound command
  does not execute the claim the canonical text makes.

Recommended for C2 / L1: either bind the scan (`append-only-audit.py --repo %R --to TIPREV`, with its exit semantics
stated) or narrow the canonical text to "self-test battery". Do not claim append-only self-description as bound
until the five declarations bind.

### F6 — ordering and reproducibility notes (minor)

- Timestamps (git metadata): freeze `675cac02` author `10:43:47`, committer `19:05:56` (jj export; reflog
  `7ee8cbdf` 10:43:47, `675cac02` 19:05:56). Amendment `03a6a1d8` author `19:05:56`, committer `19:15:45`.
  Freeze-tree files are dated `census/start.out` 18:38 and `fleet-commit-evidence.json` 19:01 (on-disk mtimes, not
  authoritative). Pre-data is not provable from git metadata beyond these; the freeze's "before any measured tip data"
  is consistent with them but not demonstrated [INFERENCE].
- Wave ordering: amendment committer `19:15:45` < `w1-dispatch.json` / `swarm-registry.json` `createdAt`
  `2026-10-28T22:16:07Z` (= 19:16:07 -03). So "amendment committed before the wave was dispatched" holds against the
  dispatch record. But `.ufo/waves/round-63/w1.ready` is dated 19:09:31, before the amendment export, and names the
  dispatch file that was created at 19:16:07. Ready-marker semantics are not in the freeze; the L1 should say which
  marker is "dispatched".
- `controls/c1-mutants-prewave.txt` cites its mutants as "scratch clone `/fast/scratch/hyaku/kama-r63/L1/cl1 @ 785f7709`".
  `785f7709` is not in the lane (`git cat-file -t` fails), so the pre-wave mutant receipt cannot be re-derived from lane
  history. The scratch clone does exist at that path with HEAD `785f7709`. Recommend copying its receipts into the lane.
- `MAX_COLLATERAL = 5` and `ENVELOPE_CAP = 30` (amendment) have no recorded derivation in the freeze. They were set in
  the same pre-wave amendment that followed the L1's own mutants [INFERENCE: chosen after observing the m2 cascade].
  The C1 calibration seat should check that the constants are not fit to the mutants.
- Counter display (for the mutation seats): the `escape` detail prints `sorted(s["fails"])[:4]`. Cap-size evidence
  beyond 4 names is hidden, so an escape by cap cannot be distinguished from an escape by name from the output alone.

## Checked and found consistent (no finding)

- Base, freeze and amendment identities. SCORECARD round-63 says base `7ee8cbdf…`, which matches `controls/freeze.txt`.
  `7ee8cbdf` is the round-62 close-out commit. `675cac02` and `03a6a1d8` are descendants of it in order.
  The freeze path `.ufo/waves/round-63/controls/freeze.txt` resolves at the tip.
- Canonical list byte identity. Extracted the round-62 table (SCORECARD.md at `7ee8cbdf`, section "canonical list as
  of round 62") and the round-63 table (at `675cac02`/`03a6a1d8`). Header and separator are identical, data rows are
  identical (12/12), and the sha256 of the table block is identical: `2d66d83462b762d81fef8c52da39b72d2106f70592a9564a2ada214bcd4bca47`
  (`out/RV05ScorecardDeclared/canonical-list-compare.txt`). The section says "twelve rows" and the freeze says the
  frozen population is 12, and both match. `live-completion-request-plane` is excluded from the list and the section says so.
- Append-only shape of SCORECARD.md. `git diff --numstat 7ee8cbdf 675cac02 -- SCORECARD.md` → `23 0`. The amendment
  does not touch SCORECARD.md. The round-62 section and all earlier sections are unchanged (zero `-` lines).
- No score move, admission or capability claim in the round-63 section. It has no score table, no "admitted" claim,
  and no `live-completion-request-plane` row. The section's only score-shaped text is the pointer
  "Claim rows are filled in `### Round-63 measured results` … once measured", which is a forward reference.
- Round-62 closure routing, as the section cites it. `round-62-verifier-spotcheck.md` rates both r62 claims unprovable
  and routes three defects: the vacuous sensitivity expression, the unsettled C1, and the untracked files. The section
  lists these correctly (F1 is the third one persisting).
- Hexrun ledger row `795b7be5…` (`registry/hexrun-ledger.tsv:125`) matches the round-62 closure's citation (line 7 of the
  spot-check) and the freeze-tree evidence file `.ufo/waves/round-63/census/fleet-commit-evidence.json`. Not verified against the fleet repo (out of bounds).
- Freeze and amendment against the append-only contract. `tools/append-only-audit.py --to 675cac02` and `--to 03a6a1d8`
  produce the same 160 events as base, with zero events from either commit. `registry/append-only-contract.tsv` and
  `registry/append-only-disclosures.tsv` do not change between base and tip. The freeze commit deletes lines only in
  non-contract files (`tools/kama-completion-live.py` −20, not in the contract). So the freeze commit introduces **no**
  append-only violation. The audit's exit 1 is inherited (F5).
- Audit selftest: `AOA_SELFTEST pass=51 fail=0` at the tip (exit 0).
- Reconciler: `mismatches=8` at both base and tip (F2), as the freeze states.

## Verification gaps

- Did not run the C1/C2 counters (other seats own them). Did not re-run the lane's mutants.
- Did not check the fleet repo for `795b7be`. Did not check the round-63 `census/start.out` content beyond its existence.
- Did not verify that `SKILL.md:578` and `README.md:16` declared lines are the intended rule sources (only that the
  audit reads them as not-append-only).

## Tools

No tool installs or upgrades. Used `git`, `python3` (stdlib), and the lane's own `tools/append-only-audit.py`
and `tools/round42-selfdesc-reconcile.py` on a clone. Scratch
`/fast/scratch/hyaku/kama-r63/w/RV05ScorecardDeclared/` removed before yield; receipts copied to
`.ufo/waves/round-63/w1/out/RV05ScorecardDeclared/`.

## Tally

`aoa(base=exit1 freeze=exit1 tip=exit1) events_base=160 events_freeze=0 events_tip=160 bad_declarations=5 unrestored=17 selftest=51/51 canonical_rows_identical=12/12 sha256=2d66d834…bcd4bca47 scorecard_numstat_freeze=23/0 reconciler_mismatches_tip=8 freeze_introduced_violations=0 stray_untracked_pre_freeze=1 findings=F1-F6`
