# Round 73 C1/C2/C3 attack — CRT01ClaimCritic

Axes: operability (assigned seat axis), with the calibration/freshness consequences of the three
frozen claims attacked in §6. Attack, not admission: I did not judge, edit, integrate or ship; the
freeze (`plans/round-73-claims.md`, sha256 `027893d7…`) is read-only and unedited.

Measurement state (disclosed, not hidden): every receipt in
`.ufo/waves/round-73/w1/CRT01ClaimCritic/` was written at lane `master =
bc9e30599b6c6133bb094f0e7abd1a9f512778ec`. At that typing, the three round-73 modules
(`tools/round73-{round-scope-cases,receipt-claim-binding,province-host-drift}.py`) and the
`PROVINCE.md` Round-73 block were **untracked/uncommitted work** by their owner seats; the two
byte-frozen base tools are byte-identical to `6e961996` (`git diff --stat 6e961996 -- …` empty,
sha256 `45321056…`/`a9a4e8d3…`). The receipts are critic evidence, not the round's evidence: none
of them can bind at a record tip (see §5, class 3). In this report `receipts/<name>` abbreviates
`.ufo/waves/round-73/w1/CRT01ClaimCritic/<name>` (the seat's own directory; there is no
`receipts/` subdirectory). Fixtures were built in
`/fast/scratch/hyaku/kama-r73/CRT01ClaimCritic/` (root removed at yield); no lane file outside
`w1/CRT01ClaimCritic.md` and `w1/CRT01ClaimCritic/` was written.

## 1. Do-nothing reachability — the counting command is green before any work

The frozen counting command is
`python3 .ufo/waves/round-73/controls/score-survivors.py` (C1's is that alone). Its exit code does
**not** gate the claimed work: a module that is *absent* is reported and skipped, never failed
(`score-survivors.py:98-100, 115, 139`; `ok` only fails when a **present** `v2` module is red on a
survivor). The pre-freeze receipt already proves it — it ends `# exit=0` with
`SURVIVORS c1 base_green=3 v2_killed=0 v2=absent`, `SURVIVORS c2 … v2=absent`,
`SURVIVORS c3 … v2=absent`.

Re-run in the do-nothing state (`receipts/reachability-do-nothing-scorer-green.out`; lane tree holds
only the two base counters):

```
V2_C1 absent: tools/round73-round-scope-cases.py does not exist
SURVIVORS c1 base_green=3 v2_killed=0 v2=absent clean=n/a
V2_C2 absent: tools/round73-receipt-claim-binding.py does not exist
SURVIVORS c2 base_green=1 v2_killed=0 v2=absent
V2_C3 absent: tools/round73-province-host-drift.py does not exist
SURVIVORS c3 base_green=1 v2_killed=0 v2=absent
# exit=0
```

So: **all three targets are "reachable" by doing nothing if the command's exit code is the
evidence.** The target exists only in the printed `SURVIVORS` lines (`v2=present v2_killed=3
clean=green` / `v2_killed=1`). The plan's "control that skips the claimed work … cannot satisfy the
target" is true of the *printed target*, but the counting command's exit status cannot distinguish
the before and after receipts. The L1 must quote the `SURVIVORS`/`V2_*` lines.

| # | cheapest skip | frozen target score | excluded by the frozen predicate/kill rule? |
|---|---|---|---|
| a | run the counting command with the modules absent | exit 0; `v2=absent` lines | **No** on exit code; yes only if the reader grades the `SURVIVORS` text |
| b | a module with the exact `PREDICATE` constant and no logic (exit 0 on survivors) | `v2=present`, `v2_killed=0` → scorer exit 1 | Yes — the scorer fails a *present* module that does not kill a survivor |
| c | a counter that greps/presence-detects the new cases | exit 0, all `v2_killed` | **No** — demonstrated in §2 |
| d | the harness "lying" about fixtures | exit 0, same lines | **No** — `--lane`/`--meta` are unvalidated and unprinted (`score-survivors.py:47-48`); no sha of `freeze.txt`, the builder, the meta, or the modules is read |

The exact-sentence obligation is real and checked at my tip (C1 selftest `PASS predicate`; C2 arm
`predicate … ok`; C3 `predicate: plan_chars=564 constant_chars=564`), but the **count** does not
check it: a module with no `PREDICATE` constant at all scores green (§2).

## 2. (c)/(d) demonstrated: three non-implementing stubs pass the frozen count

`receipts/reachability-stub-counting-command.out` — a throwaway lane tree whose three round-73
modules are deliberately weak:

* C1 stub: fires on the *presence* of a linked worktree / any `round-<M>` dir / any `.gitmodules`,
  never reads ignored content (`_ignored_older_findings` semantics never implemented);
* C2 stub: greps the record for `at the tip|report tip`, never resolves a citation or reads a
  receipt header;
* C3 stub: greps `PROVINCE.md` for `Windows`, never parses a block and never probes the live host.

Observed (same command as the round's counting command, `--lane` pointed at the stub tree):

```
V2_C1 c1_a5 exit=1 verdict=KILLED … c1_clean exit=0 verdict=GREEN
SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green
V2_C2 c2_b6 exit=1 verdict=KILLED …
SURVIVORS c2 base_green=1 v2_killed=1 v2=present
V2_C3 c3_stale exit=1 verdict=KILLED …
SURVIVORS c3 base_green=1 v2_killed=1 v2=present
# exit=0
```

The scorer prints none of `--lane`, `--meta`, module paths or hashes; its receipt is
indistinguishable from the real one. `score-survivors.py` parses **no** output field — not
`cases=6`, not the finding case, not the C2/C3 counters.

**Wrong-case stub** (`receipts/reachability-wrong-case-stub.out`): a C1 module keyed on the fixture
path, with no `PREDICATE` constant, printing `ROUND_SCOPE_V2_FINDING label …` and `cases=3` on every
survivor still scores:

```
V2_C1 c1_a5 exit=1 verdict=KILLED ROUND_SCOPE_V2 round=73 cases=3 findings=1
…
SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green
```

This is a direct counterexample to the frozen kill clause "exits 1 **naming its new case**": the
count grades exit 1 only.

**Clean-presence negatives the frozen fixture set lacks.** The frozen builder
(`build-survivors.py`, sha-pinned `fb42cf91…`) builds only the three dirty survivors plus
`c1_clean` (no worktree, no future-round dir, no submodule). I built the three missing negatives in
scratch; the stub kills every one while no dirt exists:

| fixture (clean, no dirt) | stub verdict | real module (for contrast) |
|---|---|---|
| linked worktree, clean (`clean-wt`) | exit 1 `worktree any linked worktree` | exit 0 (`c1-adversarial.out`) |
| `.ufo/waves/round-74/record.txt` tracked, nothing ignored (`clean-round`) | exit 1 `ignored-older-label` | exit 0 |
| initialized clean submodule (`clean-sub`) | exit 1 `submodule any submodule` | exit 0 |

The real module is not a presence detector; the *frozen kill set* cannot tell the two apart.

## 3. C1's universals do not enumerate their full sets

Two surviving counterexamples against the frozen C1 sentence, measured with the **real** module
(`receipts/c1-adversarial.out`, `receipts/c1-frozen-fixture-details.out`). Both are exit 0.

### 3a. "every initialized submodule worktree has no uncommitted or untracked content" — nested submodule escapes

`adv/nested-clean`: parent records `sub` (a submodule) at a commit whose `sub/.gitmodules` declares
`submodule.inner.path = inner` with `ignore = all`; `sub/inner` is initialized and has
`?? untracked-inner.txt`.

```
git -C nested-clean/sub/inner status --porcelain -uall   →  ?? untracked-inner.txt
git -C nested-clean            status --porcelain -uall   →  (empty)
git -C nested-clean            status --porcelain -uall --ignore-submodules=none → (empty)
git -C nested-clean/sub        status --porcelain -uall   →  (empty)
git -C nested-clean            submodule status           →  only `sub`
```

Module output: `ROUND_SCOPE_V2 round=73 cases=6 findings=0`, exit 0. Cause:
`_submodule_paths()` reads only the parent `.gitmodules` (`round73-round-scope-cases.py:209`), and
the parent probe runs only `if subs:` (`:255`); `sub/inner` is never enumerated. A8 class (nested
A7) survives the counter that claims A7 is closed.

### 3b. "no path under a `.ufo/waves/round-<M>/` directory with `M >= <N>` is git-ignored" — linked-worktree future round escapes

`adv/hybrid-wt`: primary worktree clean; a linked worktree has
`.ufo/waves/round-74/hidden.log` git-ignored.

```
primary status / primary status --ignored -- .ufo/waves   →  (empty)
linked  status --ignored -- .ufo/waves                    →  !! .ufo/waves/round-74/hidden.log
```

Module output: `ROUND_SCOPE_V2 round=73 cases=6 findings=0`, exit 0. `_ignored_older_findings`
iterates `root/.ufo/waves` (the primary) only (`:182`), and the `worktree` case runs plain
`status --porcelain -uall`, which cannot see ignored paths. The A5 fix covered *uncommitted* dirt in
linked worktrees; the A6 fix did not cross it with A5. The predicate's "present in the worktree" has
no declared denominator; the module's docstring silently chose "primary worktree" (`:32`). Either
reading is arguable, and that ambiguity is the defect: the claim does not pin the population.

### 3c. What does enumerate correctly

* `M >= N` is numeric: `adv/round-100` (ignored `round-100/hidden.log`, ignored `round-7/hidden.log`)
  yields exactly `ignored-older-label .ufo/waves/round-100/hidden.log`, exit 1; `round-7` is
  correctly outside. No lexical-compare defect.
* Clean linked worktree / clean future-round dir / clean submodule all exit 0 (real module), so the
  three new cases are not presence detectors.
* Frozen A7 (`c1_a7sub2`) exits 1 with three findings (`sub child.txt`, `sub leak.txt`,
  `parent-record=M sub`); frozen A5/A6 exit 1 naming `worktree`/`ignored-older-label`.

## 4. C2 — the bound branch is a git hash fixpoint; the claim is satisfiable only by omission

The frozen predicate requires that a tip claim "names a receipt whose own `tip=`/`rev=` header
**equals** `<rev>`". No committed receipt can satisfy this: the blob at commit `C` is fixed before
`C`'s hash exists, so a blob containing `# rev=C` is a fixed point of the hash function
(probability ≈ 2⁻¹⁶⁰). The r72 critic said exactly this (`.ufo/waves/round-72/w1/CRT01ReceiptAttack/
attack.md:175`: "The receipt cannot name its own commit, so 'header == tip' alone is unachievable"),
and the module's own `_claim_pass` docstring repeats it. Consequences:

* **`claims > 0` can never be green.** `_claim_pass` (`:185`) flags every cited receipt whose header
  `!= tip_sha` (`:221`); `audit` is clean only when `unbound_claims == 0` (`:299`). The round's own
  record therefore must reach `claims=0`; the plan's "`claims=0`-or-bound" has exactly one live
  branch.
* **The kill rule's clean fixture cannot be built.** "a clean fixture (receipt header equal to the
  tip) exits 0" is unimplementable end-to-end. The builder's instruction said
  "base-green + no tip claims -> exit 0, claims=0", and the module's selftest grades the comparison
  through an **injected blob reader**, not a committed fixture: `c2-selftest.out` prints
  `RECEIPT_CLAIM_BINDING_ARM claim-header-equals-tip expect=0 got=0 ok`, whose source says the
  equal-header receipt "is a git hash fixpoint and cannot be committed". This is a silent amendment
  of the frozen kill rule; the freeze must be *reported*, not edited.
* **The claim is a prohibition, not a binding.** The instrument kills the historical r72 shape
  (`a-lower` → `stale-claim`; `f-relative` → `stale-claim`) but can never produce a bound tip claim.
  A record that omits the three tokens is green: `c2-adversarial.out` `h-nochaim` and the selftest's
  `clean-no-tip-claim` arm both print `claims=0 unbound_claims=0`, exit 0.

### 4a. The token list is not the tip-claim population

`receipts/c2-adversarial.out` — eight `c2_b6`-shaped fixtures, real module, base green in each:

| variant | citing line (abridged) | exit | claims/unbound |
|---|---|---:|---|
| a-lower | `` `…/a.out` — the gate ran at the report tip.`` | 1 | 1/1 `stale-claim` |
| b-upper | `… — At The Report Tip the gate ran.` | 1 | 1/1 — case-insensitive works |
| c-recordtip | `… — the gate ran at the record tip.` | 0 | 0/0 |
| d-wrapped | citation line, then `the gate ran at the` / `report tip.` on the next lines | 0 | 0/0 |
| e-nocite | citation on line 1, `The gate ran at the report tip.` on line 2 | 0 | 0/0 |
| f-relative | `` `measured/a.out` — the gate ran at the tip.`` | 1 | 1/1 — section-relative resolves |
| g-hyphen | `… — the gate ran at the report-tip.` | 0 | 0/0 |
| h-nochaim | `… — no tip claim here.` | 0 | 0/0 |

The predicate's universal is only over lines that (i) carry one of the three literal tokens and
(ii) hold a citation resolvable *on that line*; every variant above is outside that population by
construction. "at the record tip" and the wrapped form are ordinary English tip claims and pass.

### 4b. Separability (§2 of the seat brief)

Module-level separability holds — each real module ran in a tree containing only its own base
dependency (`receipts/separability-c{1,2,3}-only.out`); each claim leg was green on its own:

* C1 tree: `SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green` … then BASE_C2/V2_C2
  absent, `# exit=1`.
* C2 tree: `SURVIVORS c2 base_green=1 v2_killed=1 v2=present` … `# exit=1` (C1 base counter absent).
* C3 tree: `SURVIVORS c3 base_green=1 v2_killed=1 v2=present` … `# exit=1`.

Command-level separability **fails**: the aggregate command cannot exit 0 for one claim in isolation
because `base_c1`, `base_c2` and the other legs are required by the `ok` aggregation. The plan's
sentence "each instrument runs and verifies with the other two absent" is true at module level and
false at counting-command level; the record should say which reading it means and paste the three
claim-specific lines.

## 5. KQ119 forward — citation classes the L1 must avoid, and where the frozen text conflicts

`receipts/kq119-citation-classes.out` runs the frozen base tool over shaped fixtures:

| class | observed | consequence |
|---|---|---|
| receipt measured before an instrument-input commit (`tools/new-instrument.py` in `<rev>..<tip>`) | `RECEIPT_TIP_FINDING shifted … :: tools/new-instrument.py touched by 7cf3def6bcb9` | **Avoid**: every `tools/**`, `plans/**`, `corpus/knowledge/**`, `registry/**`, `SKILL.md`, `PROVINCE.md`, `corpus/SOURCES.md` commit after a cited receipt's header makes it `shifted`. A C3 receipt measured before the `PROVINCE.md` block commit is shifted by the block commit itself. |
| backticked in-scope `.md` (wave-scoped seat report) | `RECEIPT_TIP_BINDING_UNREADABLE cited path is not a receipt file (.md)` | **Avoid**: cite no `.md`/`.py`/directory from the wave; repo-root `corpus/…`, `plans/…`, `tools/…` are out of scope (not findings). |
| backticked in-scope directory with no receipt | `… cited directory carries no receipt file` (exit 2) | **Avoid**: a wave directory cites every receipt beneath it (`dir-cite-full` → `cited=1 bound=1`); one unbindable member makes the round red. |
| ancestor header + record-only delta | `RECEIPT_TIP_BINDING … bound=1` | **Safe** and the only way to cite: header names an ancestor, delta touches only the record paths (````.ufo/waves/round-<N>/``, `corpus/lessons/`, `LOG.md`, `SCORECARD.md`, `corpus/README.md`). |
| header below line 5 / `# tip=master` | `unbound … no tip=/rev= header among the first 5 lines` | **Avoid**: `# rev=<40hex>` line 1. |
| tip token on a citing line | base green, C2 `stale-claim` (`tip-claim base exit=0` / `tip-claim c2 exit=1`) | **Avoid** all three tokens, case-insensitively: equals-tip is unachievable (§4). |

Sequencing implied for the round's own record (and checked against the predicates):

1. Land/commit all instrument inputs first (`tools/round73-*.py`, the `PROVINCE.md` block, any
   `corpus/knowledge/` and `SOURCES.md` rows), then measure the cited receipts. Any receipt whose
   header predates those commits is `shifted` and cannot bind.
2. C1's final run needs a **fully committed** worktree: the gate calls the module with no `--allow`
   (`pre-report-gate.py` `ARM_SPECS`), and every uncommitted path is a `stray`/`worktree` finding. A
   final C1 receipt must be measured after the last receipt/record commit; the next C1 run at the
   post-receipt commit is green again, and the receipt measured at the previous commit binds across
   a wave-dir-only delta.
3. C2's base tool needs `cited ≥ 1` (exit 2 otherwise). The committed round-73 lesson
   (`corpus/lessons/round-73.md`, currently untracked) explicitly cites no round-73 wave receipt, so
   the L1's `## Round 73` SCORECARD section must cite at least one bindable receipt — and none of
   those lines may carry a tip token.
4. C3 has no `--tip`: `evaluate()` reads the **worktree** `PROVINCE.md` (`:194`). A receipt can name
   `master` while grading uncommitted bytes. My own `c3-live-lane.out` is exactly that: header
   `bc9e3059`, `blocks=1 … stale=0`, while the block was not in `bc9e3059`'s tree. A bindable C3
   receipt must be measured after the block commit on a clean worktree and must carry evidence of
   byte equality (e.g. `git diff --quiet <rev> -- PROVINCE.md` exit 0, or `git status --porcelain
   PROVINCE.md` empty).

Frozen-text conflicts (report, do not edit):

* C2 kill rule's "clean fixture (receipt header equal to the tip)" is impossible (§4); the builder
  substituted `claims=0`.
* C1 non-goal "A round that needs an ignored file under its own wave dir declares it in this plan
  first (no `--allow-ignored` escape)": no code reads such a declaration; the gate passes no
  `--allow`, so a declared ignored file is still `ROUND_SCOPE_V2_FINDING ignored`. The sanctioned
  path does not exist.
* C1 "the declared record allow-list" has no declared contents in the plan; the only list is the
  CLI `--allow` (empty at the gate). A module could declare a default list without contradicting the
  sentence; the real module declares none, so no survivor is demonstrated, but the sentence is
  under-bound.
* C3's block-grammar bullet says a host move is answered by appending, never editing; the predicate
  grades only the newest block, so edit-in-place and delete-the-newest both pass (§6).

## 6. Append-only (C3) and the frozen C3 fixture set

`receipts/c3-adversarial.out` (real module):

| fixture / action | output | exit |
|---|---|---:|
| no block (`noblock`) | `PROVINCE_HOST_DRIFT_FINDING no-block …` | 1 |
| only `uname -m` differs (`Linux/aarch64/arch`) | `stale-host … recorded=Linux/aarch64/arch live=Linux/x86_64/arch` | 1 |
| only os-release `ID` differs (`Linux/x86_64/ubuntu`) | `stale-host …` | 1 |
| case differs (`linux/x86_64/arch`) | `stale-host …` | 1 |
| single stale block **edited in place** to the live triple | `blocks=1 recorded=Linux/x86_64/arch … stale=0` | **0** |
| `[live, stale]` then the **stale block deleted** | `blocks=1 … stale=0` | **0** |

The module checks all three triple components and the no-block arm (so the *module* is sound on
these), but the frozen kill set has no no-block and no component-only fixture: `build-survivors.py`
builds only `c3_stale` (its `meta["c3_stale"]`), and `score-survivors.py` runs only that one. A
`Windows`-grep stub passes both the survivor and the live lane (§2). The append-only discipline is
ungraded: the r71 counter had a `--base` rewrite check (`PROVINCE_HOST_CLAIMS_REWRITTEN`); C3 has no
equivalent.

## 7. Axes — calibration is the label; coverage is the move

AXES.md defines calibration as "self-assessment quality: … SHONEN.md/SCORECARD entries match
observed repo state". C1's instrument has **no self-assessment input**: it reads git state, never a
SCORECARD/SHONEN sentence and never a writing revision, so it cannot count a mismatch between a
record and the repo. Its calibration content is the *motivation* (r72's "cannot be satisfied
vacuously" was falsified by three survivors), not a graded quantity; `cases=6 findings=<f>` is a
coverage count. Under the assigned-axis duty (calibration 7, tied with depth/adjacency and the
lowest non-retired assigned score; `SCORECARD.md` §Axes/§Saturation; no axis is retired,
§Retired = "None") C1 does not move calibration as measured. Either the record states calibration
delta 0 with C1 counted as coverage, or it adds a real self-assessment-vs-repo count (the r29
`self-assessment-at-writing.md` form is the lane's precedent).

C2 is operability in the AXES sense (a runnable artifact: a gate that binds citations), and C3 is
freshness in the AXES sense (live host vs recorded host). But the plan's own Axes paragraph and
`SCORECARD.md` current authority say the assigned axes are **operability + calibration**
(`shokunin.conf` kama row; the `MISSION.md` freshness conflict stays open at
`/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:145`). C3 therefore moves an axis the lane's
authority does not assign; the record should label it contested, not an assigned-axis move. The
three claims are otherwise distinct (three inputs: git worktree/tip state, record blobs, PROVINCE
host block) and no claim's predicate depends on another's module.

## 8. Findings table (counterexample · evidence · axis · smallest safe correction)

| ID | Sev | Claim | Counterexample (observed) | Evidence | Axis | Smallest safe correction |
|---|---|---|---|---|---|---|
| F1 | P1 | all | counting command exits 0 with all three modules absent | `reachability-do-nothing-scorer-green.out`; the pre-freeze receipt ends `# exit=0` | operability | The record must quote the three `SURVIVORS`/`V2_*` lines, never the exit code alone; state the target as `v2=present v2_killed=3 clean=green` etc. |
| F2 | P1 | all | three presence/lexical stubs score `v2_killed=3/1/1`, exit 0; none prints `cases=6`, none names a case | `reachability-stub-counting-command.out`, `reachability-wrong-case-stub.out` | operability/calibration | Add module `sha256sum` + an argv-echoing direct run to the round's record; C1 has no direct lane run in its counting command, so add `--repo . --round 73 --tip <tip>` (or record why the gate's own run is the substitute); the frozen scorer cannot be edited after scoring. |
| F3 | P1 | C1 | nested initialized submodule with `?? untracked-inner.txt` → exit 0; ignored file under `round-74` in a linked worktree → exit 0 | `c1-adversarial.out` (hybrid, nested), statuses in §3 | calibration/coverage | In the module: recurse submodules (`git submodule status --recursive`/`foreach --recursive`, or walk every initialized `.git`) and enumerate `round-<M>` dirs in every worktree. Both are inside the frozen sentence and keep `cases=6`. If the module is not changed before scoring, the record must name both escapes as open. |
| F4 | P1 | C2 | `header == tip` is unachievable; every tip claim is red; `claims=0` is the only green | `c2-selftest.out` (`claim-header-equals-tip` via injected reader), module docstring, r72 attack :175 | operability | Record the round's C2 as `claims=0` and say the bound branch is not exercised; report the kill rule's "clean fixture (header equal to tip)" as unimplementable. Do not edit the freeze. |
| F5 | P2 | C2 | "at the record tip", line-wrapped claims, citation-on-another-line, "report-tip" all `claims=0`, exit 0 | `c2-adversarial.out` c/d/e/g | calibration | The L1 must not use any of those forms; the record must not claim "every tip claim" — only the three-token population. Next round widens the token list and joins wrapped lines. |
| F6 | P2 | C3 | edit-in-place and delete-the-newest both exit 0 | `c3-adversarial.out` | freshness | Record append-only as ungraded; next round adds `--base <rev>` rewrite detection (r71's pattern). |
| F7 | P2 | C3 | no-block fixture is not built or run by the frozen count; a `Windows`-grep stub passes | `c3-adversarial.out` noblock (real), `reachability-stub-counting-command.out` | freshness | Supplementary receipt running the real module on a block-less and three component-only fixtures; do not cite the scorer for the no-block clause. |
| F8 | P2 | all | kill-rule clauses the count does not verify: "naming its new case", "inherited r72 kill fixtures stay red", C2 clean fixture, C3 no-block | `reachability-wrong-case-stub.out` (`label`, `cases=3` → KILLED); scorer source `:69-100, 115, 139` | operability | The record states which clauses were exercised; a supplement runs the r72 kill arms and the missing fixtures. |
| F9 | P2 | all | one-module trees: each claim leg green, aggregate exit 1 | `separability-c{1,2,3}-only.out` | operability | Read the plan's separability sentence at module level; paste the three claim-specific lines and the aggregate exits. |
| F10 | P2 | C3 | live run grades worktree bytes; my receipt names `bc9e3059` but the block was uncommitted | `c3-live-lane.out`; `git status --porcelain PROVINCE.md` = ` M` | freshness | Bind a C3 receipt measured after the block commit on a clean worktree, with `git diff --quiet <rev> -- PROVINCE.md` in the receipt; or the next round adds `--tip`. |
| F11 | P3 | C1 | "declared record allow-list" / "declares it in this plan first" have no reader; the gate passes no `--allow` | `pre-report-gate.py` `ARM_SPECS` (round-scope tuple, no allow) | operability | State that the allow-list is the CLI `--allow` (empty at the gate); do not claim a plan-declaration escape exists. |
| F12 | P2 | axes | C1 counts git state, not a self-assessment mismatch; C3 is freshness while only operability+calibration are assigned | AXES.md calibration row; `shokunin.conf` kama row; SCORECARD current authority | calibration/freshness | Record C1 as coverage (calibration delta 0) or add a real self-assessment counter; label C3 contested-axis. |

## 9. What I did not find (so the L1 does not over-read this report)

* The real C3 module is correct on every component I varied: `uname -m`-only, `ID`-only,
  case-only, no-block, newest-wins (its selftest arm 5), unparseable triple, exit 2 on missing
  file and CLI misuse. Its defects are the frozen fixture set and the ungraded append-only clause,
  not its triple comparison.
* The real C2 module is case-insensitive, resolves section-relative citations, dedupes notations,
  and kills B6 with `RECEIPT_CLAIM_FINDING stale-claim`. Its defect is the frozen predicate/clean
  fixture, not its comparison.
* The real C1 module handles numeric `M >= N`, ignores older rounds, catches the three frozen
  survivors, returns exit 0 on all three clean-presence negatives, and its selftest (26 arms) and
  the frozen r72 selftest (16 arms) pass. Its defects are the two unenumerated universals and the
  fixture/command gaps above.
* No `__pycache__` or `.pyc` was left under the wave dir; no lane git/jj mutation was performed;
  the two r72 tool blobs are unchanged since `6e961996`.

## 10. Commands (all run with `PYTHONDONTWRITEBYTECODE=1`; full output in the named receipts)

| # | command | observed |
|---|---|---|
| 1 | `python3 .ufo/waves/round-73/controls/build-survivors.py --work <S>/controls-work --meta <S>/fixtures-meta.json` | 6 fixtures; exit 0 |
| 2 | `python3 tools/round73-round-scope-cases.py --selftest --work <S>/c1-selftest` | `ROUND_SCOPE_V2_SELFTEST pass=26 fail=0` |
| 3 | `python3 tools/round73-receipt-claim-binding.py --selftest --work <S>/c2-selftest` | `RECEIPT_CLAIM_BINDING_SELFTEST pass=14 fail=0` |
| 4 | `python3 tools/round73-province-host-drift.py --selftest --work <S>/c3-selftest` | `PROVINCE_HOST_DRIFT_SELFTEST pass=9 fail=0` |
| 5 | `python3 tools/round72-receipt-tip-binding.py --selftest` | `RECEIPT_TIP_BINDING_SELFTEST pass=16 fail=0` |
| 6 | `python3 .ufo/waves/round-73/controls/score-survivors.py` (real lane, my rebuilt meta) | `SURVIVORS c1 base_green=3 v2_killed=3 v2=present clean=green`, c2 1/1, c3 1/1, exit 0 |
| 7 | same with `--lane <S>/tree-base-only` | all `v2=absent`, exit 0 |
| 8 | same with `--lane <S>/cheat-tree` (stubs) | all `v2_killed`, exit 0 |
| 9 | same with `--lane <S>/wrongcase-tree` | C1 KILLED naming `label`, `cases=3`, SURVIVORS green |
| 10 | same with `--lane <S>/tree-c{1,2,3}-only` | claim leg green each; exit 1 each |
| 11 | `python3 tools/round73-round-scope-cases.py --repo <adv> --round 73 --tip master` ×6 | hybrid/nested exit 0; round-100 exit 1; clean ×3 exit 0; a7sub2 exit 1 |
| 12 | `python3 tools/round73-receipt-claim-binding.py --repo <c2v> --round 72 --tip master` ×8 | table §4a |
| 13 | `python3 tools/round73-province-host-drift.py --repo <c3e>` ×7 | table §6; live lane exit 0; c3_stale exit 1 |
| 14 | `python3 tools/round72-receipt-tip-binding.py --repo <kq119> --round 72 --tip <tip>` ×8 + C2 | table §5 |
| 15 | `git -C L rev-parse master`, `git -C L diff --stat 6e961996 -- tools/round72-*.py`, `sha256sum` | `bc9e3059…`; empty diff; `45321056…`, `a9a4e8d3…` |

Receipts (all start `# rev=bc9e30599b6c6133bb094f0e7abd1a9f512778ec`): `after-scorer-real-modules.out`,
`base-tool-selftest.out`, `c1-adversarial.out`, `c1-frozen-fixture-details.out`,
`c1-live-midwave.out`, `c1-selftest.out`, `c2-adversarial.out`, `c2-live-midwave.out`,
`c2-selftest.out`, `c3-adversarial.out`, `c3-live-lane.out`, `c3-selftest.out`,
`c3-stale-fixture.out`, `kq119-citation-classes.out`, `reachability-do-nothing-scorer-green.out`,
`reachability-stub-counting-command.out`, `reachability-wrong-case-stub.out`,
`separability-c1-only.out`, `separability-c2-only.out`, `separability-c3-only.out`.

Scratch `/fast/scratch/hyaku/kama-r73/CRT01ClaimCritic/` was removed at yield; the receipts are the
evidence.
