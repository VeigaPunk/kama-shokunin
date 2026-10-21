# O01 alternates channel — ownership-gate design

VERDICT: **design found (holds at prototype level)** — the audit can distinguish
lane-owned from borrowed objects by re-scoping "resolved" from *store presence*
to *reachability from the audited repo's own refs*, with the gate armed only
when `objects/info/alternates` exists. This closes O01's missing
`unresolved-full-hash` half while keeping control C05 (`clone --shared` lane)
clean. Two naive fixes are **falsified by evidence**: scoping via
`GIT_ALTERNATE_OBJECT_DIRECTORIES=""` (ineffective — file alternates still
apply) and any blanket own-store-membership requirement (breaks C05, where
every lane object is borrowed). Blanket alternates refusal would also break
C05. All fixtures fresh under /tmp; the lane, fleet and sibling lanes were
never touched.

## Axes

- A1 soundness: borrowed decoy must defect (O01), borrowed-but-reachable must not (C05).
- A2 safety: no crash/hang/program-exec added to the C1 surface; alternates paths never executed.
- A3 cost: zero added spawns when no alternates; one `rev-list` per alternates-bearing repo otherwise.
- A4 fit: one choke point (`lookup`) already feeds both O01 defect kinds.

## Ground truth at 245a37f69628c2c6bb29bbf17897d8fb5946c857

- `tools/report-landing-audit.py:52-54` (docstring): "Objects borrowed through
  objects/info/alternates or a .git gitfile still resolve as local" — the gap
  is admitted, not guarded. `check_history_repo` (:427-448) refuses shallow /
  grafts / promisor / non-sha1 / non-top-level but **not** alternates.
- `lookup()` (:131-165) resolves report tokens per repo via
  `cat-file --batch-check`; `audit_round` emits `unresolved-full-hash`
  (:313-315) and landed-row `landed-unresolved`/`landed-ambiguous`
  (:326-330) from that same helper — one integration point.
- Grid: `O01-alternates-foreign-object` expects exit 1 with exactly
  `{landed-unresolved, unresolved-full-hash}`
  (`tests/report-audit/repo-state-grid.py:570-571`, fixture :481-489:
  donor commit `foreign` cited in fleet report, lane alternates → donor
  objects). Control `C05-shared-clone-clean` (:534, fixture :153-159) must
  stay exit 0. Open rows are reported, never graded (:626-639).

## Design (prototype-verified)

1. **Ownership rule.** Token resolved in repo R iff
   (a) `cat-file --batch-check` finds it (existing `lookup`), **and**
   (b) it is in `reachable(R)` = `git rev-list --objects --no-object-names
   <roots_R>` run through the tool's existing `git()`/`GIT_ISOLATION`
   (`--no-replace-objects`, `--no-lazy-fetch`, pinned `-c` log flags).
   Roots: lane = the already-resolved audited branch tip (`resolve_branch`);
   fleet = `HEAD^{commit}`. Explicit resolved tips only — never `--all`,
   never `--alternate-refs` (see S7).
2. **Arming.** Compute `reachable(R)` only when
   `git rev-parse --git-path objects/info/alternates` lexists for R
   (memoized per repo per run). No alternates → behavior byte-identical
   to today, zero added processes.
3. **Classification.** Inside `lookup()`: found-but-not-reachable ⇒ report
   `missing`. Reuse the existing kinds — do not invent a new defect kind —
   so the grid's pinned O01 expectation is met verbatim and errata
   correction validation inherits the tightened semantics automatically.
4. **Docstring/ledger.** Replace the :52-54 caveat with the ownership rule
   and declare the semantic tightening: "resolved" now means "an object of
   the audited history"; citations of dangling objects, other branches'
   objects, or donated decoys become defects (same class of declared
   narrowing as T01). Grid: move O01 open→fault; add a control
   "alternates lane citing its own reachable objects stays clean".

## Evidence (git 2.56.0; harness /tmp/kama-r23w2/lab/drive.py; fixtures /tmp/kama-r23w2/lab/fix/*; every git subprocess ran with scrubbed GIT_*, GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1, explicit identity)

| # | command (fixture) | observed |
|---|---|---|
| S1 | `python3 tools/report-landing-audit.py --lane-repo fix/lane --fleet-repo fix/fleet --rounds 1 --no-errata --json` on the exact `o_alternates` mirror | `(0, [])` — current arm passes clean; **neither** expected O01 kind fires (the widened lookup silences both) |
| S2 | same on the `c_shared_clone` mirror (`--lane-repo fix/shared`) | `(0, [])` — C05 clean today |
| S3 | `git cat-file -e <foreign>` in lane, default env vs `GIT_ALTERNATE_OBJECT_DIRECTORIES=""` | `rc=0` both — **env pin does not disable file alternates** |
| S4 | `git cat-file --batch-all-objects --batch-check` counts | lane default `6` (3 own + 3 donor), lane with empty env `6` (still includes alternates), donor `3` — no native single-store scoping knob |
| S5 | `git rev-list --objects --no-object-names <tip>` | lane set (size 3) contains `lc`, **not** `foreign`; shared-clone set contains `lc2` (borrowed ∧ reachable) |
| S6 | `git merge-base --is-ancestor <foreign> <tip>` in lane / `<lc2> <tip>` in shared clone | `rc=1` (decoy not in own history) / `rc=0` (borrowed tip is) — cheap commit-only alternative probe |
| S7 | lane `core.alternateRefsCommand=<script writing marker + echoing foreign as refs/heads/decoy>`; `rev-list --objects --all` / `rev-list --objects <tip>` / `log -1 <tip>` | `--all`: foreign_in=False, **exec=0**; explicit tip: foreign_in=False, exec=0; log: exec=0 — plain `--all` does not import alternate refs and no audit-reachable command executes that config (docs: `.ufo/waves/round-22/residual/FinalSources/raw/gitlog.txt:1106-1113` — `--alternate-refs` is the opt-in option it modifies) |
| S8 | chained relative alternates lane→donor→`../../../donor2/.git/objects` | `cat-file -e foreign2` `rc=0` (resolves transitively) yet `foreign2 in reachable(lane)` = False — gate is transitivity-proof; per-store enumeration would need recursive file parsing instead |
| S9 | alternates file with a dangling target and a `with space/dir` junk line | `cat-file -e <own>` `rc=0`, `log -1` `rc=0` — no crash added by arming the gate |
| S10 | prototype `resolve()` (batch-check ∧ reachable-set membership) | O01: `foreign → found+borrowed-unreachable`, `lc → found+reachable`; C05: `lc2 → found+reachable` — exactly the O01-defect / C05-clean split |
| S11 | gitfile-redirected repo: `rev-parse --git-path objects/info/alternates` | resolves into the redirected store (`fix/real/.git/objects/info/alternates`) — detection stays correct under redirects; ownership scoping under gitfile redirect itself is O02's channel |

## Falsified alternatives

- **Refuse any repo with alternates** (round-21 F4 fail-closed spirit): breaks
  C05 — a `clone --shared` scratch lane has alternates by construction and
  must audit clean.
- **Own-store membership via `GIT_ALTERNATE_OBJECT_DIRECTORIES=""`**: S3 —
  the env var does not suppress the file; every shared-clone token would
  still be "found", and forcibly ignoring alternates would flip C05 to
  failed. Unsound in both directions.
- **Per-store `--batch-all-objects` attribution (D2)**: S4 — the command
  always includes all transitively reachable stores and there is no
  scoping flag; attributing a token to a store requires parsing
  `objects/info/alternates`, chasing relative paths and chains recursively,
  and synthesizing a gitdir per raw store. `rev-list` reachability subsumes
  it with one process per repo.

## Not verified / residual

- The actual patch, grid rerun (`open`→`fault` move), selftest and ledger
  byte-comparisons are the build wave's work; I prototyped the gate's
  mechanics only (task scope: design + /tmp prototype).
- Fleet-repo-with-alternates end-to-end through the real tool was exercised
  only via the prototype classifier, not a patched-tool grid run.
- Stale `core.commitGraph` lying about parents is unexamined (same
  repo-derived-data trust class as the `git log` the audit already runs).
- Combined gitfile-redirect + alternates topologies belong to O02
  (`RevengeGitfile-2`); S11 only fixes the detection path.
- Pre-existing exposure unchanged: a hostile alternate store can feed git
  bigger object graphs (cost), and alternates targets are paths that git
  opens but never executes (S7).
- /tmp hygiene note: the wave filled /tmp to 100%; I deleted only my own
  clone's `.git` at /tmp/kama-r23w2/RevengeAlternates (HEAD 245a37f
  verified before deletion; worktree kept for reads) — no peer files
  touched. No tools installed (python3 + git sufficed).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RevengeAlternates.md` (this report)
- `/tmp/kama-r23w2/lab/drive.py` (harness; disposable)
- `/tmp/kama-r23w2/lab/fix/*` (disposable fixtures)
- `/tmp/kama-r23w2/RevengeAlternates/` (clone, worktree only — `.git` removed by me for space, HEAD verified pre-removal)
