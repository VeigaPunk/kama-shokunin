# FinalPM03 — canonical operator PM03-skip-required-object-availability, pinned source 92063cfc60e217fa7e2098c568578119b16a1b95

**VERDICT: killed (bounded sample, 2 cells per tool).** The EXACT registered PM03 operator, applied with the pinned mutator's own `apply_mutation()` to a private copy of the pinned auditor, turns both declared opaque-hole cells from the content-derived refusal (exit 2) into an ordinary failed finding (exit 1): a changed substantive verdict, class `actual-verdict` on the pinned runner's taxonomy. No timeout, no traceback, no `internal_error`, no harness leak, no acquired object, no twin mismatch.

**Provenance.** `git clone --no-hardlinks` of `/home/vgpnk/Projects/shokunin/kama-shokunin` → `/fast/scratch/hyaku/kama-r24/postfix/FinalPM03/clone`, detached at 92063cf. Contract identities matched on disk: auditor `b9be4f42…`, grid `30483830…`, mutator `971c3ecb…`, manifest `d86b7bea…` (47 graded + PG40 open) — byte-identical before and after (`hashes-before.txt` / `hashes-after.txt`).

**Mutation (no re-anchoring, no retargeting).** Alternative match counts `[regex x0, regex x1]` → applied alternative **1** (unique applicability), compiles=True; one-line change `self._missing = missing_reachable(self.path, self.root)` → `self._missing = (set(), set())` (`PM03-applied.diff`). Pristine `b9be4f42…` → mutant `4085069e…` (private copy under my own scratch only).

**Detector.** Pinned grid, `--arm current` only, `--case PG46-opaque-tree-hides-cited-blob --case PG47-opaque-tree-with-unresolved-fabricated-token` — 2 cells per tool; the other 45 graded cells and PG40 never ran; the mutator's default/main sensitivity path was never invoked.

| cell | pristine | mutant | class (pinned `classify_row`) |
|---|---|---|---|
| PG46-opaque-tree-hides-cited-blob | exit 2, met=true, problems [] | exit 1, met=false, problems `['exit 1 != 2']` | `actual-verdict` |
| PG47-opaque-tree-with-unresolved-fabricated-token | exit 2, met=true, problems [] | exit 1, met=false, problems `['exit 1 != 2']` | `actual-verdict` |

Both failures show in the graded (amended) view and in the original view. Mutant defects: PG46 `unresolved-full-hash 2f62e7ff9e9e4c2e972dab0989d414e027012348`, PG47 `unresolved-full-hash 0123456789abcdef0123456789abcdef01234567`; the pristine refused with "unavailable required object: … could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6". Arm summaries: pristine `violations 0, amended_view_met 2/2`; mutant `violations 2, violating_cases=[PG46,PG47], amended_view_unmet=[PG46,PG47], original_view_unmet=[PG46,PG47]`, `tracebacks 0, timeouts 0, harness_leaks 0`, `objects_acquired {lane:[],fleet:[]}` on both sides.

**Twins.** PG46/PG47 register `twin: null`, so `twin_compared 0`: no twin constraint was exercised and no twin mismatch is claimed. The kill rests on the graded exit change alone.

**Attribution.** At this pin PM03's `expect_rows` = PG13–PG21, PG33, PG34, **PG46, PG47** — both executed cells are inside the frozen envelope (`expected_match` true for both). The envelope was not widened; no row was re-targeted; no expectation byte was edited.

**Negative control — pinned runner `main(argv)` on the runner's own `STUB_GRID`/`CANDIDATE` (no repository, no fixture).** All four: exit **2**, `killed=False`, `status=could-not-evaluate`, `killed_ids=[]` — a channel kill was never credited.
- `GRID_STUB_MODE=unmet`: the mutant's ONLY failed row is complete-state `PG01-complete-lane-promisor-config` (outside the envelope) → reason "violated rows outside the attribution: PG01-complete-lane-promisor-config"; that row itself classifies `refusal-2` (over-refusal), never availability credit.
- `traceback_row` → "grid: row PG06-traceback-row raised a traceback"; `internal_row` (canonical `internal_error` flag) → "grid: row PG07-internal-row reported internal_error".
- `missing_metadata` (`expected_exit` absent) → exit 2, killed False, `classify_row` = `unclassified` (no guessed class credit).
- Canary logs (`canary-*.log`) prove the pristine AND the mutant were both actually run in each mode.

**Restoration.** The mutation exists only in my scratch copy; production `tools/`, `tests/` and the 47-cell manifest are byte-identical before and after, and `git status` shows only untracked wave artifacts. No source, fixture, expectation or manifest byte was edited.

**Residuals.** (1) Bounded sample: 2 cells per tool; both discriminate here, and this is **not** a global-equivalence claim about the other 45 graded cells or PG40. (2) `twin=null` on both cells → the twin constraint is untested by this selection. (3) The original unknown clause stays WITHDRAWN/NOT-ACHIEVED; only the amended views are measured. (4) Gitfloor H2 stays open; no score promotion or self-admission. (5) No tools installed or updated (base Python/Git sufficed).

**Raw evidence:** `.ufo/waves/round-24/postfix/out/FinalPM03/` — `commands.json` (argv/env/exits), `apply-pm03.json`, `PM03-applied.diff`, `mutant/`, `grid-pristine-PG46-PG47.json`, `grid-mutant-PG46-PG47.json`, `row-classification.json`, `negative-control.json`, `canary-*.log`, `hashes-before.txt`, `hashes-after.txt`.

Report: .ufo/waves/round-24/postfix/advice/FinalPM03.md
