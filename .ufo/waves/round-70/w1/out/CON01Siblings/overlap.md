# CON01Siblings — cross-lane overlap scan (round 70, kama lane)

Seat: connector, advisory leaf. Read-only on every sibling repo. No sibling file was
written; no lane file was written. Scratch: `/fast/scratch/hyaku/kama-r70/CON01Siblings/`
(removed at end of run).

Question: does any sibling lane hold an instrument that

- **(a)** reconciles a lane's self-description with its tree, or
- **(b)** grades a test-runner / census verdict fail-closed on not-evaluated members —

and does kama's province already cover its own version of either?

Scope of evidence: `/home/vgpnk/Projects/shokunin/*-shokunin` as present on this host,
`tools/`, `scripts/`, `SCORECARD.md`, `PROVINCE.md` at each lane's working tree. Only
`grep`, `ls`, `head`/`sed`, and one read-only import of kama's own census module were
used. Wave artifacts under `.ufo/waves/` were read only to disambiguate instrument vs
seat artifact; they are not counted as lane instruments.

## (a) Self-description reconcilers — who else owns one

Every reconciler below is scoped to **its own lane's** committed documents. Not one of
them reads kama's tree, and none of them is registered as a cross-lane service.

| lane | path | what it does | kama overlap? |
|---|---|---|---|
| kama | `tools/round42-selfdesc-reconcile.py` | grades SCORECARD head/axes/planned/retired/saturation/capabilities/receipts + README + PROVINCE against the tip; prints `... mismatches=N maxN=N met=B` | — (owner) |
| kaidoku | `tools/round-44/c2-counter.py` (+ `c2-rubric.json`, `round-49/c2-mismatch.py`) | re-derives a frozen rubric of self-assessment statements at `--rev` (evidence pointers, headline numbers, `path:line`, planned rows, claim verdicts vs receipt exit, coverage-map count); **exit 0 iff `mismatches==0`, every entry evaluable and ≥1 evaluated**; exit 2 = could-not-evaluate | **adjacent** — same instrument class, different tree; no shared object |
| kaidoku | `SCORECARD.md:3400,3414` (R36-C2, R38-C2 rows) | records c2 counters whose object is explicitly "SCORECARD `## Owned axes` / `## Capabilities`, SHONEN boxes, PROVINCE Core/Frontier vs observed repo state" | **adjacent** — object is kaidoku's own head, not kama's |
| souji | `tools/souji-declared-evidence.py` | re-derives machine-checkable assertions of a self-assessment file at `--rev` (paths, revision tokens, digests); line `assertions= resolved= skipped= mismatches=`; exit 0 iff M==0 | **adjacent** — same class; its `skipped` class does not gate (see row below) |
| souji | `tools/souji-capability-agreement.py`, `tools/souji-capability-cells.py` | SCORECARD row literals re-run at a private clone at REV; `SUMMARY items= bound_run= bound_record= unbound= mismatches=`; **UNBOUND counts into `mm`** (cells.py:303-307; return at :318) so an unbound cell forces exit 1; exit 2 = could-not-evaluate | **adjacent, closest single analogue** — same class *and* fail-closed on "did not run" |
| souji | `SCORECARD.md:171` | capability row "declared-evidence calibration audit (r22 attempt 2)" — the reconciler is registered as a **capability**, not just a tool | **adjacent** — precedent for registration, see §Province |
| kake | `scripts/freshness-sweep.mjs` | re-executes every quantified standing claim: §paths every cited FS path in SKILL.md + `corpus/**/*.md` vs live FS; §history shapes; §armed pins; exit `0 clean · 1 drift · 2 unreadable/invalid` | **adjacent** — same class, per-lane tree |
| kumitate | `scripts/claims-check.mjs` | re-derives the SCORECARD row's "yes — note" claim by resolving the note's member sections, anchors and symbol existence; `CLAIMS MATCH/DRIFT` | **adjacent** — capability-cell claims, not head reconciliation |
| mori | `tools/mori-pin-check.py` | reconciles pinned tallies/digests in SKILL.md vs the tree; `PIN_CHECK=met|unmet ... mismatches= unparsed= dropped= rebound= ...`; met requires nine zero counts | **adjacent** — same class, its own pins |
| mori | `tools/mori-retention-reconcile.py` | reconciles committed retention accounting against git objects (`RETENTION_RECONCILED` / `_MISMATCH`) | **adjacent** — ledger vs git, not prose vs tree |
| chousa | `tools/claims-audit-v2.py` | flags self-assessment statements in a frozen claims file that committed files contradict (rule TSV → re-derive from committed bytes) | **adjacent** — claims file, chousa's own freeze |
| chousa | `tools/inference-ground.py` | grounds each `#### Inference` bullet of a knowledge entry in cited source spans (polarity flip refused) | **adjacent** — knowledge entries, not lane head |
| mado | `tools/mado-receipt-citecheck.py` | extracts repo-relative citations from caller-named artifacts and resolves each at `--rev`; `MISSING` named, never silently skipped | **adjacent** — receipt citations |
| mori | `tools/mori-gate-registry.py` | audits the lane's stated gate standard against committed bytes: every registry table with the eight standard cells, each row's entry path resolving at the audited revision, and a real `--selftest` argv branch (a mention in a comment or docstring does not count) | **adjacent** — registration-layer audit; the shape kama's own `SKILL.md:1433` row already has |
| tabi | `scripts/check-freshness.mjs` | pinned expected-table + sha256/newline comparison over declared public targets, fixture list for the selftest; `fail(...)` carries the exit | **adjacent** — pin freshness, not head reconciliation |
| tsukuroi | `tools/check-path-reconciliation.py` | reconciles two historical counting methods over frozen inputs; exit 0 explained / 1 unexplained / 2 could not evaluate | **adjacent** — historical census, not live head |

No sibling names kama's `tools/round42-selfdesc-reconcile.py`, `tools/round65-host-census.py`
or `HOST_CENSUS` in any tracked file. Command: `grep -rn 'round42-selfdesc|round65-host-census|HOST_CENSUS|REFUSED_MEMBER'`
over all non-kama repos → only fleet-level `.ufo/prompts/` and kama's own records; **0 sibling hits**.

## (b) Fail-closed verdicts on not-evaluated members — who else owns one

| lane | path | what it does | kama overlap? |
|---|---|---|---|
| kotodama | `tools/harness/claims-freshness.py` | freshness gate over claim clauses: `summary: N fresh, N stale, N could-not-evaluate ...; clauses N (N hold, N contradict, N not evaluated)`; exit map `0 fresh · 1 stale · 2 malformed · 3 could-not-evaluate`; docstring: a claim with no declared checks "is *could-not-evaluate*, never fresh: part 3 must exit non-zero for it" (lines 44-48, 62-65) | **adjacent** — exact rule, claims not census members |
| kaidoku | `tools/round-44/c2-counter.py` | "Exit 2 means COULD-NOT-EVALUATE, never 'not a pass': it never counts toward the target"; exit 0 requires every entry evaluable | **adjacent** — exact rule |
| souji | `tools/souji-capability-cells.py` | "Exit 0 iff mismatches=0", and UNBOUND (a cell naming no binding) is incremented into `mm` → **cannot pass unrun**; exit 2 could-not-evaluate | **adjacent, closest** — "did not run" is a failure, not a pass |
| tsukuroi | `tools/tsukuroi-census.sh` | six-plane host census; "any plane unreadable live -> BLOCKED arm fires, never a fake pass" (docstring lines 18-19); exit `0 HEALTHY · 1 DEGRADED · 2 BLOCKED`, worst plane wins | **adjacent** — same rule, host planes; name collision with kama's "host census" only |
| tameshi | `tools/arm-liveness.py` | every declared red arm must have a committed input that moves its tally; `ARM_DEAD` for an arm that cannot fire; **vacuous manifest (zero rows) exits 2** | **adjacent** — degenerate/never-run arms are not passes |
| kake | `scripts/freshness-sweep.mjs` | exit 2 on unreadable/invalid input | **adjacent** |
| kumitate | `scripts/claims-check.mjs:1000,1003` | **contrast**: a topic-form row with no member section prints `ROW_NO_SECTIONS` as a *warn* and exits 0 (`CLAIMS: MATCH`); only `--strict` promotes it to exit 1 | **adjacent (contrast)** — a lane that deliberately keeps an unevaluable row advisory |
| mado | `tools/mado-receipt-citecheck.py:118-140` | **contrast**: files over the 4 MiB read cap are `skipped_large`, counted in the verdict line, and do **not** gate (`return 0 if not missing else 1`) | **adjacent (contrast)** — same fail-open shape as kama's base census, at citation scope |
| souji | `tools/souji-declared-evidence.py:116-164,205-208` | **contrast**: `skipped` spans (unclassifiable backticked tokens, digests whose cell names no single path) are counted but the exit is `0 iff mismatches==0` | **adjacent (contrast)** — sized, not gated |

So: the "not-evaluated is not a pass" rule is not novel on this host. It is already
implemented in at least four lanes (kotodama, kaidoku, souji, tsukuroi) and two lanes
deliberately do the opposite at a different surface (kumitate warn, mado capped-skip).
kama's C2 is one more instance; the fleet's reusable craft is tameshi's by province.

## Province answer

**Question 1 — is any of this another lane's ground?**
No. Each reconciler and each census verdict grades *its own lane's* documents or members.
Tameshi's province settles the method question explicitly: it owns "the reusable craft
(a pattern is admitted from evidence in TWO independent lanes before it is claimed
general)" and "every lane's gate remains its own" (`tameshi-shokunin/PROVINCE.md:7-15`).
The method class is therefore tameshi's ground; kama's *instance* is kama's. Nothing in
this scan is kama's to absorb, and nothing in it absorbs kama.

**Question 2 — does kama's province already cover its own version?**
Partially, and asymmetrically:

- `tools/round65-host-census.py` **is** named in `PROVINCE.md`, but only in two round notes:
  `PROVINCE.md:248` (round-65/67 note, "records the adaptation") and `PROVINCE.md:265`
  (round-65 census note). It is **not** in the Owns instruments row (`PROVINCE.md:17`).
- `tools/round42-selfdesc-reconcile.py` is **not named anywhere in `PROVINCE.md` by path**
  (`grep -c 'round42' PROVINCE.md` → 0). The only allusion is `PROVINCE.md:269`
  ("the round-42 self-description reconciler selftest ... refuse fail-closed on this host"),
  which names the *selftest* as a host-limit case, not the instrument as owned surface.
- Neither instrument is in the SCORECARD canonical capability list. The list's last
  table is **`Capabilities — canonical list as of round 69`** (`SCORECARD.md:3669`) with
  **15 rows**, and `grep` for `selfdesc|self-description|host-census` over all
  capability-shaped rows (`First working round` headers) returns zero such capability.
  Existing capability names: sources-registry, ollama-offline-evidence-replay,
  live-llamacpp-lifecycle, gguf-declared-identity-replay, context-capacity-receipt,
  instrument-agreement, pin-watch, digest-ledger, hexrun-census, append-only-audit,
  live-receipt-replay, live-ollama-lifecycle, worktree-landing-check,
  receipt-pointer-audit, newest-closure-counter.
- **Observed concurrent worktree change (not mine).** At the end of this scan
  `git -C …/kama-shokunin status --porcelain` printed ` M PROVINCE.md`,
  ` M SCORECARD.md` plus the round-70 out dir; `git diff -- PROVINCE.md` is one line, and a
  byte compare shows the Owns row at line 17 growing 1625 → 2086 chars (HEAD's row ends
  `... compare every check; round 47) |`; the worktree appends the round-67/68/69
  instrument entries). That in-flight repair is naming canonical capability-row tokens —
  exactly the class the `province` fact can see — and it leaves the round-42 reconciler and
  round-65 census unnamed, because neither is a capability row. It is the L1's edit; this
  seat neither made nor reverted it, and the anchor quoted in §Proposed move is the
  post-repair one (verified present, unique: `grep -cF` → 1).
- Registration that *does* exist: (i) tier-A census member
  `("A", "round42-selfdesc-reconcile selftest", ["tools/round42-selfdesc-reconcile.py", "--selftest", ...])`
  (`tools/round65-host-census.py:59-60`, census member count **22**); (ii) a SKILL.md
  registry row at `SKILL.md:1433` naming the counter command and its 0/1/2 exit map.
- "Registered" can be made mechanical: mori's `tools/mori-gate-registry.py` audits a stated
  gate standard against committed bytes — an eight-cell row whose entry path resolves at the
  audited revision and whose tool carries a real `--selftest` argv branch. kama's reconciler
  already satisfies that shape twice (the `SKILL.md:1433` row and the census tier-A arm), which
  is why clause 1 of the move below is a declaration fix, not a registration fix.

**Is kama's claim clean of overlap?** Yes, in object and in tree: no sibling reads kama's
head, no sibling claims kama's census, and no sibling registers kama's instruments. The
residual is not overlap, it is **self-coverage**, and it is a genuine blind spot rather
than a contradiction:

- The reconciler's `province` fact is defined as "every `tools/` or `registry/` token in a
  **canon** row's evidence cell" must appear in PROVINCE.md
  (`tools/round42-selfdesc-reconcile.py:47-48,373-379`). A token that is in no canonical
  capability row can never be forced into PROVINCE by any fact of the reconciler. An
  instrument that measures the lane's self-description is exactly such a token while it
  is unregistered.
- The census *does* cover the reconciler's execution (tier-A arm above), so this is not
  "the reconciler is unverified". It is "the reconciler is unregistered in the layer that
  the reconciler grades".
- A sibling hit this identical class and fixed it explicitly: `mori-pin-check.py:898-901`
  — "the registry floor and `dropped` cannot see the reconciler's own row — the row is new
  since the baseline — so deleting it left the registry green at 30 pins"; mori added a
  self-pin arm so the instrument's own row counts as `dropped` and the verdict goes
  `unmet`. Same shape, different surface: a self-referential check whose population
  excludes the checker itself.
- Sibling precedent for closing it at registration: souji registers its reconciler as a
  capability (`souji-shokunin/SCORECARD.md:171`), tameshi registers `counter-arm liveness
  check` as a capability (`tameshi-shokunin/SCORECARD.md:256`), kaidoku records its c2
  counters as claim rows with a census/measurement command (`kaidoku-shokunin/SCORECARD.md:3400,3414`).

**Second-order effect, operability (C2).** kama's census derives its exit from `failed`
alone: `return 0 if failed == 0 else 1` (`tools/round65-host-census.py:158`), while both
the refusal-marker path and the `subprocess.TimeoutExpired` path increment `refused`
(lines 129 and 143). Two routes to "member did not run", one of them (budget timeout) is
not exercised by the frozen round-70 control, whose synthetic members are a passing
member and a refusal-marker member only
(`.ufo/waves/round-70/controls/refused-member-control.py:36-45`). The frozen pair
(`refused_fixture_exit=1`, `allpass_fixture_exit=0`) is satisfiable by a repair that
handles only the refusal marker; the timeout member would still read as a pass. That is
a discriminator gap in the control, not in the predicate.

## Proposed move (one, two clauses; no frozen counter is touched)

1. **Calibration (the lowest assigned axis, 7).** Declare both round-70 instruments in
   `PROVINCE.md:17`'s Owns instruments row — `tools/round42-selfdesc-reconcile.py`
   (self-description reconciliation at the measured tip) and `tools/round65-host-census.py`
   (tier-A/B host self-test census) — with no new SCORECARD canonical row and no
   capability claim. This is purely declarative: the reconciler's `province` fact only
   walks canonical rows, so the move cannot change any `mismatches` count, and it removes
   the "instrument invisible to the layer it grades" asymmetry in the same round the lane
   asserts `mismatches=0`. It also makes the frozen C1 phrase "the **registered**
   reconciler" unambiguous, since its only registrations today are the census arm and
   `SKILL.md:1433`.
2. **Operability (C2 implementation constraint).** Make the census's `not_evaluated`
   tally the single counter for both not-run routes (refusal marker and budget timeout)
   and derive the exit from it, so the printed verdict line's `not_evaluated=` is the same
   number the exit is computed from. The frozen control cannot distinguish the two, so
   without this the repair can pass the pair while a hung member still reads as a pass.

Risks: (0) the Owns row is being edited concurrently by the L1's round-70 record repair;
apply the insertion against the current cell text, anchored on the round-69 entry, and
re-read the row immediately before the edit (the file changes between reads are the L1's).
(i) clause 1 adds two backticked paths to a row read by citation checks; both files
exist at the tip, so `round53/54-cited-path-check`, `round65-province-host-audit` and
`round67-worktree-landing-check` should be re-run at the landing tip to confirm no new
citation debt. (ii) Clause 1 changes no capability count, so
`tools/capability-repertoire-audit.py` (`listed 15 … missing 0`) is unaffected; a
canonical-row version of the same idea would change `listed` and would be a capability
claim, which is why it is not proposed. (iii) Clause 2 changes the printed verdict line
shape; the C2 target's required `not_evaluated=1` / `not_evaluated=0` remain satisfiable,
and the real-census target `pass=22 fail=0 not_evaluated=0 total=22` still needs the C1
arm green.

Verification: after landing, run — `python3 tools/round42-selfdesc-reconcile.py --repo .
--tip <tip>` → `closure_ptr=1 mismatches=0 maxN=70 met=True`, exit 0; `python3
tools/round42-selfdesc-reconcile.py --selftest` → `pass=5 fail=0`, exit 0 (arm count
unchanged); `python3 .ufo/waves/round-70/controls/refused-member-control.py
tools/round65-host-census.py` → `refused_fixture_exit=1 allpass_fixture_exit=0`, exit 0;
`python3 tools/round65-host-census.py` → `HOST_CENSUS pass=22 fail=0 not_evaluated=0
total=22`, exit 0; `python3 tools/capability-repertoire-audit.py --selftest` →
`CAP_SELFTEST pass=2 fail=0`; `python3 tools/round53-cited-path-check.py` /
`round54-cited-path-check.py` re-run clean.

## Report-don't-absorb handoffs (for the round report, not the tree)

- **tameshi:** the fleet method "a verdict derived in part from not-evaluated members is
  not a pass" now has ≥4 independent lane instances (kotodama, kaidoku, souji, tsukuroi)
  plus two deliberate counter-examples (kumitate warn-mode, mado capped-skip); the
  two-lane admission rule in `tameshi-shokunin/PROVINCE.md:14-15` is already satisfied if
  tameshi wants the craft entry.
- **souji:** `souji-declared-evidence.py` counts `skipped` spans in its verdict line but
  derives its exit from `mismatches` alone; whether that is a defect depends on whether a
  skipped span can carry a claim — souji's call, not kama's.
- **mado:** `mado-receipt-citecheck.py` counts `skipped_large` without gating; same
  question, mado's call.
- **tsukuroi:** the name "host census" is used for both tsukuroi's six-plane host health
  census and kama's lane self-test census; no domain conflict found, but a round-report
  sentence distinguishing them prevents a later reader conflating host health with lane
  instrument health.

## What I could NOT verify

- I did not execute any sibling instrument (no sibling test suites, selftests or censuses
  run). Their exit semantics above are read from their docstrings and code paths, not from
  observed runs; every row names the file, and the line numbers are from the working tree
  at this host.
- Sibling scores/axes were not read; overlap is judged on instrument object and province
  text only.
- kama's base-state reconciler output (freeze: `mismatches=10`, `province=4`) was **not**
  re-run; it is taken from the frozen freeze text. The four province facts are therefore
  not enumerated here — only the fact definition (`:47-48,373-379`) is cited.
- The census member count 22 and the reconciler's tier-A registration were verified by
  importing `tools/round65-host-census.py` read-only (`len(MEMBERS)` → 22), not by running
  the census.
