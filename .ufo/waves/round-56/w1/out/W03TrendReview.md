# W03TrendReview — expansion / quality / discernment trends from committed work (round 56)

Seat: W03TrendReview (leaf; no subagents). Lane: `kama-shokunin`. Judged on calibration.
Scope: committed lane history only. Commits read: `438127bc` (round-48 tip), `eb7b16cf`
(round-52 tip), `0b75a84c` (round-53 tip / round-54 base), `e10b6d39` (round-55 tip /
round-56 base), `efc6b3ec` (round-56 freeze; `git rev-parse HEAD`).

No axis score is assigned here. Counts are reproduced by the commands in §7; labels for
rounds 50–55 are quoted from the committed outside closers in `corpus/lessons/`.

Provenance rule used throughout: a receipt is "committed" only if it is in the HEAD tree.
The round-56 `measured/` receipts, `corpus/lessons/round-56.md`, `w1/spec.json`,
`w1/dispatch.json`, `w1.ready.partial` and the `SCORECARD.md` header edit are **untracked**
at HEAD; they are reported as working-tree state, never used as evidence for a verdict.

## 1. Counted evidence (committed trees)

Commands in §7. `spot` = `corpus/lessons/*verifier-spotcheck.md` blobs.

| Commit (round) | `SOURCE` rows | `knowledge/*.md` | QUALITY `KQ` rows | lessons | spot | `tools/` | wave seats |
|---|---|---|---|---|---|---|---|
| `438127bc` (r48) | 234 | 36 | 75 | 83 | 35 | 59 | 69 (r48 spec) |
| `eb7b16cf` (r52) | 246 | 36 | 94 | 90 | 38 | 67 | 70 (r52 spec) |
| `0b75a84c` (r53) | 250 | 36 | 98 | 93 | 40 | 69 | 66 (r53 spec) |
| `e10b6d39` (r55) | 252 | 36 | 98 | 96 | 42 | 72 | 64 (r55 spec) |
| `efc6b3ec` (r56 freeze) | 254 | 36 | 98 | 96 | 42 | 76 | (r56 spec untracked) |

Capabilities: the canonical `SCORECARD.md` §Capabilities table carries 11 data rows at every
one of the five commits above (recounted per commit, §7; the section is a mirror pinned to the
round-49 canonical list). The round sections agree in wording: §Round 48–52 print `Capabilities
11 → 11`, §Round 53 "capabilities remain 11", §Round 55 "no capability enters".

Round-56 freeze composition (`git show --stat efc6b3ec`): 10 files, +2634/−0. Four are
instruments: `round56-replay-code-audit.py` 973 lines, `round56-prereg-check.py` 75,
`round56-env-leg-battery.py` 55, `round56-env-leg-test.py` 36. Two are source snapshots
(`sources/ld.so.8.html`, `sources/rtld-audit.7.html`), one preregistration, two committed
base controls, one `SOURCE` append (+2 rows, below).

## 2. Expansion — unchanged

Evidence:

- **Knowledge coverage is flat, not merely slow.** `corpus/knowledge/*.md` = 36 at `438127bc`,
  `eb7b16cf`, `0b75a84c`, `e10b6d39` and `efc6b3ec` (§1). Eight rounds, zero new entries.
  Round 56's own gate admits a *source*, not an entry, and the untracked
  `corpus/lessons/round-56.md` §Claims says it "does not claim to close the broader
  host-library byte-provenance, archive attribute, or git-config-hermetic routes". The
  committed `S512` row bounds the same claim to the variable name alone: "LD_AUDIT must be on
  BAD_ENV even when a particular non-audit DSO is refused by glibc".
- **Registry growth at r56 is +2, one of which is a refusal.** At HEAD, `S512` is
  `status=mined, tier=A` (rtld-audit(7)) and `S513` is `status=rejected, tier=A` (ld.so(8),
  rejected as overlapping S512, flip named). Rows 234→254 over eight rounds (+20, ≈2.5/round)
  while knowledge is flat: row growth in this horizon is grounding depth, not coverage.
- **Capabilities 11 → 11.** No capability row entered in rounds 50–56 (`SCORECARD.md`
  §Round 50–55 each state it; the round-56 prereg claims `8 -> 8` and `7 -> 7` on existing
  axes).
- **Instrument growth at the freeze is mostly one copy.** `tools/round56-replay-code-audit.py`
  is `tools/round54-replay-code-audit.py` with 7 inserted / 6 replaced lines over 3 hunks
  (`diff` in §7): the docstring, `BASE` moved from `3a600d2f…` to `e10b6d39…`, and
  `BAD_ENV` gaining `"LD_AUDIT"` (line 147). `env_leg` (line 430) is byte-identical between
  the two files. Novel instrument logic in the freeze is 166 lines (`env-leg-test` 36 +
  battery 55 + checker 75); 966 of the new counter's 973 lines are identical to round 54's.
- **Wave capacity is flat-to-shrinking.** Committed specs: 69 (r48), 71 (r49), 66 (r50),
  70 (r52), 66 (r53), 64 (r55). The r56 spec (64 items, untracked) repeats r55's size.

Counter-evidence I will not smooth over: registry rows continue to rise, and one of the two
new rows is a *new* dynamic-linker surface (LD_AUDIT) the lane's instrumented gate did not
name before. If the lane's own bar were "new surface ⇒ expansion", this would count. The bar
on record (`CORPUS.md` SOURCES rule 4; `LEARNING.md` improved-row; applied by the round-55
closer): expansion is knowledge entry or capability, not rows. Under that bar: unchanged.

What would move it: an admitted `corpus/knowledge/*.md` entry on ground no entry holds, or a
capability row whose demonstration runs at the reporting tip. Neither is present at
`efc6b3ec`.

## 3. Quality — improved at the freeze seam, bounded; measurement unobserved at HEAD

The freeze artifacts are structurally stronger than the round-55 freeze, and the improvement
is inspectable byte-for-byte:

1. **Frozen digests reproduce at HEAD.** `git show HEAD:tools/round56-replay-code-audit.py |
   sha256sum` = `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` and
   `git show HEAD:tools/round56-prereg-check.py | sha256sum` =
   `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, equal to
   `preregistration.json:12` and `:22`. Both controls are committed before any measurement
   receipt: `.ufo/waves/round-56/controls/base-c1.out` (`ld_audit=missed … exit=0`,
   `tip=e10b6d39…`) and `base-c2.out` (`present=0 roster_match=0 kills=0 controls=0
   met=False`, `exit=1`).
2. **The graded object is now the roster itself.** C2's counter parses the battery's `ROSTER`
   with `ast.literal_eval` and compares it to `preregistration.json` `battery.roster`
   (`round56-prereg-check.py:57-65`), requiring `kills == 1 and controls == 2`. I reproduced
   the equality statically: `ROSTER == prereg roster` → `True`; and the battery's one-line
   mutant anchor occurs exactly once in the frozen counter (`anchor_count=1`), so the
   `raise SystemExit("mutant anchor is not unique")` guard (`env-leg-battery.py:48`) is live.
   This is the direct answer to round-55 defect 1 (battery roster diverged from the immutable
   preregistration).
3. **Per-leg field assertions and exit codes replace line-presence tests** for C1
   (`env-leg-battery.py:30`: `ok = p.returncode == 0 and fields.get("ld_audit") == expected`;
   every receipt body carries `exit=<n>`). That lands round-55 defects 4 and 5 for the C1
   battery — the outside closer's own complaint was that "run-battery.py's leg assertion is a
   substring presence test".
4. **The new checker is git-config hermetic** (`round56-prereg-check.py:17-25`: strip `GIT_*`,
   `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`), closing for this counter the
   inherited-config limit the round-55 closer filed (Sec1) and the round-55 plan named.
5. **New source rows carry the revision element** the round-55 contract required: S512/S513
   cells include "Linux man-pages 6.19 (2025-05-17)" (defect 6 fix on new rows only; S511's
   row is unchanged).

Counter-evidence, same commit:

- **C2's red-before state is file absence, not divergence.** `present=0` at the base tip
  because `preregistration.json` and the battery do not exist there (`round56-prereg-check.py:41-42`).
  The control proves the checker is red when its inputs are missing, not that it discriminates
  a wrong-but-present roster. The discriminating clause is C2's kill rule ("a one-field
  designation mutation remains green"), and **no committed receipt at HEAD exercises it** —
  mutants are in flight in the untracked wave.
- **C2's frozen digest does not bind the battery bytes.** `preregistration.json:22` hashes the
  checker; the battery's sha256 (`79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`)
  is nowhere in the prereg. Roster equality constrains the battery's `ROSTER` literal only.
- **Receipt exit codes are only partly self-recorded.** C1 body includes `exit=`; the C2
  checker does not write one, and the untracked `measured/build-c2.out` carries no `exit=` line.
- **Dead weight in the frozen bytes**: `round56-prereg-check.py:12` `BASE` is never used (the
  base tip is reached through `--tip`); `env-leg-battery.py:27` `expected_result` is computed
  and discarded.
- **Untracked working-tree statement ahead of committed evidence**: `SCORECARD.md` line 6
  (working-tree diff) reads "Latest measured round: 56 … froze and measured C1 … and C2 …
  (SCORECARD §Round 56)". At HEAD there is no `## Round 56` section (grep: only line 6
  matches "Round 56") and **zero** committed `measured/` receipts under
  `.ufo/waves/round-56/` (`git ls-tree … | grep -c measured` → 0). The untracked receipts
  themselves do say `ld_audit=detected`, `met=True` at `tip=efc6b3ec…`. As committed, the
  header sentence would be an unbacked claim; whether integration lands the section with it
  is the round's own gate.

Verdict on the *seam*: improved — the freeze enforces a stronger contract than round 55's
frozen artifacts, and the outside-routed defects 1, 5 and 4-for-C1 are mechanically addressed in
committed bytes. Verdict on *measurement*: unobserved at HEAD; I do not upgrade an uncommitted
receipt.

## 4. Discernment — unchanged pending an outside sample

- **Gate at the freeze is discriminating, self-assessed.** One admit (`S512`, 15-word located
  quote at §DESCRIPTION) and one reject (`S513`, 16-word quote, refused as overlapping S512
  "for the only fact C1 needs", flip named). Refusing a broad loader manual against a dedicated
  manual is the same bar the r55 closer agreed with for proc(5) vs held proc rows — but this
  sample is the lane's own Gate, and author seats are not credited as outside review
  (`corpus/lessons/round-12-verifier-spotcheck.md:97`).
- **Outside coverage is broad but has not been consolidated for 12 rounds.** 41 of the 45
  rounds 11–55 have a committed non-author spot-check; rounds 20–23 have none, and 15 verdict
  keys are recorded as `absent` in the ledger. `registry/verdict-ledger.tsv` carries 204 rows,
  six per round, **stopping at round 43** (§7). Rounds 44–55 outside verdicts exist in the
  lesson files (r50, r51, r52, r53, r54, r55) but are not in the ledger, so the lane's own
  agreement instrument cannot be recomputed past r43. `SCORECARD.md` states the scope honestly
  ("self against outside for rounds 10–43: `agreement=69/87 overclaim=2 underclaim=16
  other=0 absent=15`").
- **Recent author/outside labels agree.** r53 author unchanged/harmed/unchanged vs outside
  unchanged/harmed/unchanged (round rejected); r54 all unchanged both sides; r55
  unchanged/improved/improved both sides, outside admitted. r52's author `discernment:
  unprovable-but-better` was upgraded to `improved` by the outside closer — an underclaim, the
  dominant error class in the ledger (`agreement=69/87 overclaim=2 underclaim=16 other=0
  absent=15`, the 15 absent keys outside the 87-key denominator).
- **Responsiveness is real but is routing, not discernment.** Round-55 routed defects 1, 2, 4,
  5, 6, 7, 9, 10 and round 56's prereg names them (`preregistration.json:6`). Status in
  committed bytes at `efc6b3ec`: 1 addressed (C2), 4 addressed for C1 only, 5 addressed for
  C1, 6 addressed for new rows only, 2 partially (correction text lives in the untracked
  `corpus/lessons/round-56.md`), 7 **open** (41 round-55 paths still dirty at HEAD: 2 modified
  + 39 untracked), 9 **open** (the untracked r56 spec carries per-item `role`, no attack
  classification field), 10 partially (depth/calibration row re-anchors exist only in the
  uncommitted `SCORECARD.md` diff). Closing routed defects quickly is a quality signal; it does
  not substitute for a fresh adopt/reject sample.
- **Defect class recurrence, caught here rather than by a standing gate.** Committed `S512`'s
  `used-by` cell names `corpus/lessons/round-56.md`, which does not exist in `efc6b3ec`
  (`git cat-file -e HEAD:corpus/lessons/round-56.md` → exit 128, "exists on disk, but not in
  'HEAD'"). This is the same class as the round-54 dangling `used-by` (census E11) that the r55
  closer agreed was repaired. The round's cited census
  (`scripts/sources-census.sh validate --root … kama`) validates the *worktree*, so an untracked
  lesson satisfies it while the commit is inconsistent. Reported as state, not as a verdict;
  integration can close it by committing the lesson.

Verdict: unchanged. A single self-produced admit/reject pair, with the outside sample absent at
HEAD and the ledger unconsolidated since r43, does not support `improved`. What would move it:
a committed non-author spot-check of r56 that agrees on the admit and the reject (the r50–r52
pattern), plus ledger rows for 44–55 so the agreement figure is recomputable.

## 5. Calibration notes on this report

- Every label above is bounded to the commits named; nothing is inferred from the untracked
  wave. The two places I cite untracked material (r56 `measured/*.out`, r56 spec) are labeled
  and excluded from verdicts.
- I do not assert that round 56 will measure green; I assert the untracked receipt says
  `met=True` at `tip=efc6b3ec…` and that no such receipt is committed.
- [INFERENCE] The flat knowledge count across eight rounds is most likely a deliberate bar
  (row growth is not coverage), not neglect: r55's lesson explicitly refuses to count S511 as
  knowledge growth, and r56 refuses S513 while admitting S512 for one narrow need.

## 6. Findings for integration (each with a proposed fix)

1. **F1 (calibration, open at HEAD):** `S512.used-by` → `corpus/lessons/round-56.md` is absent
   from `efc6b3ec`. Fix: commit the lesson with the round (or point the cell at a committed
   path); add a tree-scoped used-by existence leg — the worktree census cannot see this.
2. **F2 (calibration, working tree):** `SCORECARD.md:6` claims "measured … §Round 56" with no
   such section and no committed measured receipt. Fix: land §Round 56 with the receipts, or
   soften the header until the measured commit exists.
3. **F3 (quality, pending):** C2's discriminating clause has no committed receipt. Fix: commit
   the one-field designation mutant receipt alongside `build-c2.out` (the wave's
   `R11C2Mutation`/`M05RosterDelete` seats are the likely source).
4. **F4 (quality, small):** `round56-prereg-check.py:12` unused `BASE`; `env-leg-battery.py:27`
   unused `expected_result`; C2 receipt lacks `exit=`. Fix: drop the two dead lines, append
   `exit=$?` in the receipt writer.
5. **F5 (quality, inherited):** round-55's dirty tree (defect 7) is still dirty at HEAD. Fix:
   the round-55 sweep the closer asked for, or a named wrap-up exception.

## 7. Commands run (all read-only; exit codes)

- `git rev-parse HEAD` → `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`, exit 0.
- Counts (§1), per commit, exit 0 each:
  `git show <c>:corpus/SOURCES.md | grep -cE '^\| *S[0-9]{3}'`;
  `git ls-tree --name-only <c> corpus/knowledge/ | grep -c '\.md$'`;
  `git show <c>:corpus/QUALITY.md | grep -cE '^\| *KQ[0-9]+'`;
  `git ls-tree --name-only <c> corpus/lessons/ | grep -c '\.md$'` and `… | grep -c 'verifier-spotcheck'`;
  `git ls-tree --name-only <c> tools/ | grep -c '\.py$\|\.sh$'`.
  (One call over five commits returned exit 0; the round-56 `measured` count returned exit 1
  by design — `grep -c` with no match prints `0`.)
- Seats: `git show HEAD:.ufo/waves/round-<r>/w1/spec.json | python3 -c '…len(items)'` for
  r48/49/50/52/53/55 → 69/71/66/70/66/64, exit 0.
- Capability rows: inline `python3` over `git show <c>:SCORECARD.md`, counting `|` rows
  between `## Capabilities` and the next `## `, minus header and separator → 11 at each of the
  five commits, exit 0. The four counter files used in the delta line are tracked and clean
  (`git status --porcelain tools/` printed nothing), so the working-tree `diff` equals a
  blob-to-blob `diff`.
- Hashes: `git show HEAD:tools/round56-replay-code-audit.py | sha256sum`,
  `git show HEAD:tools/round56-prereg-check.py | sha256sum`,
  `sha256sum` of `tools/round56-env-leg-battery.py` → the three digests in §3, exit 0.
- Statics: `python3` inline AST read of `tools/round56-env-leg-battery.py` `ROSTER` vs
  `preregistration.json` → `roster_equal=True anchor_count=1`, exit 0.
- Deltas: `diff <(git show e10b6d39:tools/round54-replay-code-audit.py) <(git show
  HEAD:tools/round56-replay-code-audit.py)` → 3 hunks, +7/−6; `diff` over
  r49→r50→r51→r54 counters → +301/−171, +116/−83, +429/−95, exit 0.
- Tree checks: `git show HEAD:corpus/SOURCES.md | grep -E '^\| S51[23] '` → `mined`/`rejected`;
  `git cat-file -e HEAD:corpus/lessons/round-56.md` → exit 128 (absent);
  `git status --porcelain | grep -c round-55` → 41; `git ls-tree -r HEAD .ufo/waves/round-56 | grep -c measured` → 0.
- `awk -F'\t' 'NR>1{print $1}' registry/verdict-ledger.tsv | sort -n | uniq -c | tail` →
  six rows per round, last round 43, exit 0.
- No lane tool, gate, census or counter was executed; no lane file was written except this
  report. Scratch `/fast/scratch/hyaku/kama-r56/W03TrendReview/` was created and removed.
- Tool installs: none.
