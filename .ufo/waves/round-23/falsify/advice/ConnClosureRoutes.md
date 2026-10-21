# ConnClosureRoutes — MANIFEST kama closure rows r20–r22 vs the round-23 lesson

Seat `CloseKama22.ConnClosureRoutes-2` (leaf; no dispatch, no REA devices, no installs).
Lane base verified before reading: `git -C /home/vgpnk/Projects/shokunin/kama-shokunin
rev-parse HEAD` → `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
Manifest read read-only: `/home/vgpnk/Projects/shokunin/MANIFEST.json`, sha256
`94ea37f370768e29bd032f5fe7cd77535328344585f0d028d0378a41a13f1ef5`, 423 round entries.
Rows read and identity-asserted (all `lane=="kama"`, `type=="closure"`, `admitted=true`):
`rounds[397]` (r20, `MANIFEST.json:10112`), `rounds[406]` (r21, `MANIFEST.json:10587`),
`rounds[418]` (r22, starts `MANIFEST.json:11567`; it has no `notes`/`promotions`/`minted` keys).
Only `notes` in these rows contains the word “rout” (python walk of every field).

## Verdict: **partially**

Round 23 discharges the one routed defect that names it as target — R21-D4 — in a narrowed,
grid-graded form, and keeps KQ32 for everything the grid does not grade
(`corpus/lessons/round-23.md:16-17`). Every explicit *defect* route into r21 and r22 was
already closed before round 23 (errata and r22 lesson, below).

But four open/routed-debt groups handed forward by the r20/r21 closures are **neither
addressed by round 23's commits nor carried** in `corpus/lessons/round-23.md`. The lesson's
`Open (both arms, reported not graded)` list (`:85-92`) is therefore not an exhaustive carry,
and one base line that does carry part of the debt is now stale. Gaps G1–G4 below.

## Route table (every route in the three rows)

| ID | Routed item (verbatim, ≤25 words) | Source | Disposition at 245a37f6 |
|---|---|---|---|
| R20-D1 | “Defects (status-neutral, routed to kama r21)”: spliced full hash `0957ce61…` | `MANIFEST.json:10112` | **closed r21** — `registry/report-landing-errata.tsv:3`; `corpus/lessons/round-21.md:63` |
| R20-D2 | same sentence: Landed list omits four round commits | `MANIFEST.json:10112` | **closed r21** — errata `:4-7` (four `landed-omitted` rows) |
| R20-R18 | “full 42-run R18 survivor measure not rerun (routed R18 comparison, outside C1/C2)” | `MANIFEST.json:10112` | **GAP** (G3) |
| R20-LIMITS | “v3-all-scalars 12 test.* values not individually compared”; “timeout reason precision unclaimed” | `MANIFEST.json:10112` | **GAP** (G3) |
| R20-L0 | “L0 kama\|round-17 llama archive question still open” | `MANIFEST.json:10112` | **GAP** (G4) |
| R21-D1 | “Routed status-neutral defects to kama r22”: SCORECARD final `7054dba1`/33-command | `MANIFEST.json:10587` | **closed r22** — `corpus/lessons/round-22.md:104-106` |
| R21-D2 | same: CORPUS v1 correction rows | `MANIFEST.json:10587` | **closed r22** — `round-22.md:107-110` (S078–S086) |
| R21-D3 | same: two-death accounting and late 66-report falsify total | `MANIFEST.json:10587` | **closed r22** — `round-22.md:111-115` |
| R21-D4 | “do not use audit on untrusted repos until hardened” (repo-local Git config/history + UTF-8/error/top-level) | `MANIFEST.json:10587` | **addressed r23, narrow** — `round-23.md:8-17,70-84`; commits `e0f0434`, `34b2376`; residual carried by “KQ32 stays in force” |
| R21-DEBT | “Remaining prelaunch-snapshot race,41-hop gate bound,JSON duplicate-key/Unicode edge cases and overbroad any-str-map injectivity docstring are routed debt” | `MANIFEST.json:10587` | **GAP** (G2) |
| R21-SELFTEST | “Late C1SelftestReview's vacuous uncommitted-now fallback and crash-only GIT_DIR assertion remain test debt” | `MANIFEST.json:10587` | **GAP in lesson** (G1); carried only in `SKILL.md:736` |
| R21-L0 | “Existing round16 fixture-ratification and round17 retained-archive L0 remain operator-owned” | `MANIFEST.json:10587` | **GAP** (G4) |
| R21-C2 | late C2DigestSentinel was against an older tree; final code covers it | `MANIFEST.json:10587` | **closed r21**; no r23 obligation |
| R22 | row has no routed item (`notes` absent); its lesson restates the unclaimed debts | `MANIFEST.json:11567ff`; `round-22.md:121-123` | feeds G1/G2 |

Round-23 changed-file check (`git log --oneline --name-only 4fe9339f..245a37f6`): only
`tools/report-landing-audit.py`, `tests/report-audit/repo-state-grid.py`,
`tests/report-audit/isolation-mutants.py`, `corpus/SOURCES.md`, `corpus/lessons/round-23.md`
plus probe evidence. `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`
and the audit selftest case set were not touched.

## Gaps

### G1 — R21-SELFTEST-DEBT not carried in the lesson; the weak cases are unchanged

- Source: `MANIFEST.json:10587` — “Late C1SelftestReview's vacuous uncommitted-now fallback
  and crash-only GIT_DIR assertion remain test debt.”
- Current code at base (read via `git show 245a37f6:tools/report-landing-audit.py`):
  - `:853-854` `check("uncommitted-draft-uses-now", rc == 0 and not doc["results"][0]["report_committed"])`
    — still only reachability, no discriminating fallback assertion.
  - `:878-879` `check("inherited-GIT_DIR-untouched", sorted(p.name for p in (decoy / "objects").iterdir()) == decoy_before)`
    — still asserts only that the decoy's object list is unchanged.
- Same two weak assertions at `4fe9339f:779-780,804-805`; the case population is unchanged
  (47 quoted `check("` names plus one 3-iteration loop = the reported 50 cases at both blobs).
  No grid row or mutant covers the selftest itself.
- Lesson absence: base `corpus/lessons/round-23.md` contains no `selftest`, `vacuous`,
  `uncommitted-now` or `GIT_DIR` token (keyword assertion below).
- Durable carry exists only at `SKILL.md:736-738` (“UTF-8/error/top-level handling and the
  late selftest fallback/GIT_DIR debt remain unclaimed until separately hardened”). The
  lesson — the artifact this check requires — does not carry it.

### G2 — R21-DEBT (four items) not addressed and not carried

- Source: `MANIFEST.json:10587` — “Remaining prelaunch-snapshot race,41-hop gate bound,JSON
  duplicate-key/Unicode edge cases and overbroad any-str-map injectivity docstring are routed
  debt outside static flat-tree count.”
- r22 already recorded them unclaimed: `corpus/lessons/round-22.md:121-123` — “Existing
  selftest fallback/GIT_DIR assertion debt, prelaunch races, chain bound, JSON
  duplicate-key/Unicode limits remain unclaimed.”
- Current code sites at base 245a37f6 (untouched by round 23):
  - prelaunch scan→launch race: `tools/kama-llamacpp-live.py:1418-1422` scans/hashes and
    refuses, then `:1497` `subprocess.Popen(server_argv, **popen_kwargs)` launches; no re-check.
  - 41-hop chain bound: `tests/llamacpp-live/check-receipt.py:181-199` follows `links` with a
    `seen` set but no hop cap (kernel `ELOOP` at 40); r21's falsifier built a 41-hop receipt
    at `.ufo/waves/round-21/falsify/out/C2DigestSentinel/attacks/c_gate.py:112-118`.
  - JSON duplicate-key/Unicode: `tests/llamacpp-live/check-receipt.py:2375-2377`
    `receipt = json.load(fh)` — last-key-wins, no `object_pairs_hook`.
  - overbroad injectivity docstring: `tools/kama-llamacpp-live.py:210-211` still reads
    “injective for any {str: str} map”.
- Lesson absence: no `prelaunch`, `snapshot`, `41-hop`, `chain bound`, `duplicate-key` or
  `injectiv` token in `corpus/lessons/round-23.md`.

### G3 — R20 honest limits / routed R18 comparison not carried

- Source: `MANIFEST.json:10112` — “v3-all-scalars 12 test.* values not individually
  compared”; “full 42-run R18 survivor measure not rerun (routed R18 comparison, outside
  C1/C2)”; “timeout reason precision unclaimed (2 diagnostic mutation survivors, class
  boundary intact)”.
- Documented at `corpus/lessons/round-20.md:188` and `:273`; neither r21, r22 nor r23 reran
  the 42-run measure, and round 23's lesson contains none of `42-run`, `R18`, `survivor`,
  `v3-all-scalars`, `timeout reason`.
- These are limits rather than defects, but the r21 closure carried R20-LIMITS forward as a
  route (its catalogued disposition was “carry-explicitly”), and the carry is still missing.

### G4 — Operator-owned L0 items not carried

- Sources: `MANIFEST.json:10112` — “L0 kama|round-17 llama archive question still open”;
  `MANIFEST.json:10587` — “Existing round16 fixture-ratification and round17
  retained-archive L0 remain operator-owned.”
- Fleet L0 log shows no ruling: `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:58`
  (kama round-16 fixture ratification) and `:68` (kama round-17 retained archive
  `~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz`); neither is followed by an `L0 ANSWER`.
  `fleet .ufo/reports/round-21/kama.md:72` still says the round-17 question “remains open”.
- Lesson absence: `corpus/lessons/round-23.md` contains no `L0`, `llama`, `round-17`,
  `fixture-ratification` or `retained-archive` token. Operator ownership does not remove the
  carry obligation; it only fixes who may act.

## Contradiction (stated, not smoothed)

`SKILL.md:736-738` at base says “UTF-8/error/top-level handling and the late selftest
fallback/GIT_DIR debt remain unclaimed until separately hardened.” Round 23 grades
UTF-8/error/top-level for the audit (strict decode, catch-all, top-level refusal;
`round-23.md:70-78`), so the first half is now stale, while the second half is still true
(G1). The pending uncommitted worktree append after `SKILL.md:772` says KQ32 is “narrowed by
KQ34 to graded rows” but does not correct the stale sentence, and the lesson does not carry
the surviving debt. Result: the round's written surface simultaneously understates the fix
and loses the carry. (Worktree edits were observed, not attributed; only the L1 integrates.)

## One bounded move (godspeed)

**Append a `## Carried prior debt (r20–r22)` block to `corpus/lessons/round-23.md` before
closure, and one append-only clarification after `SKILL.md:738`.**

1. Lesson block, four bullets, each naming the item, its source (`MANIFEST.json:10112` or
   `:10587`), and “not addressed by this round; status unchanged”:
   - R21-SELFTEST-DEBT: `tools/report-landing-audit.py:853-854,878-879`; selftest case
     population unchanged (50; no grid/mutant coverage).
   - R21-DEBT: prelaunch scan→launch race (`tools/kama-llamacpp-live.py:1418-1422`→`:1497`);
     no hop cap (`tests/llamacpp-live/check-receipt.py:181-199`); `json.load` last-key-wins
     (`:2375-2377`); injectivity docstring (`tools/kama-llamacpp-live.py:210-211`).
   - R20-LIMITS: v3-all-scalars 12 `test.*` values, 42-run R18 survivor comparison, timeout
     reason precision.
   - R20-L0 / R21-L0: llama archive; round-16 fixture ratification; round-17 retained archive
     — operator-owned, no ruling on record (`.ufo/l0-questions.md:58,68`).
   Keep the existing `Open (both arms…)` list; add that it covers graded grid residuals only,
   not prior-round debt.
2. SKILL clarification (append, never rewrite): “Round 23 grades UTF-8/error/top-level for
   this audit; the late selftest `uncommitted-draft-uses-now` and
   `inherited-GIT_DIR-untouched` assertions and the R21 routed debt remain open, not fixed.”
3. Do not touch code in this move; if the L1 instead fixes the selftest cases, replace bullet
   one with the new case names, commit, and the post-change `selftest cases=N failed=0`.

**Axes affected.** Calibration: the lesson becomes a true carry, matching the measured
surface without raising the 7→7 scalar. Discernment: `Open` stops reading as exhaustive.
Operability/expansion/quality: unchanged. No code, no behavior, no serving surface.

**Risks.** The lesson is committed at 245a37f6, so the append must be a new L1 commit and the
closure report/rechecks must cite the post-append lesson commit; appending changes the lesson
blob that this base check read. Do not word the carry as “addressed”, and do not extend
KQ34 credit to ungraded channels. If SKILL.md is left untouched, the stale sentence continues
to contradict the round's own claim.

**Verification (proposed, not run here).** After the append: substring-assert each of the four
blocks in `corpus/lessons/round-23.md`; `git status --porcelain` shows only intended paths;
`python3 tools/report-landing-audit.py --selftest` still prints `cases=50 failed=0` if
docs-only. Then re-run this same route scan to confirm zero gaps.

## What was run / observed

- `git rev-parse HEAD` → `245a37f69628c2c6bb29bbf17897d8fb5946c857`.
- `git log --oneline --name-only 4fe9339f..245a37f6` → three round-23 commits; files as
  listed above; no touch to `kama-llamacpp-live.py`, `check-receipt.py`, or selftest cases.
- Verbatim-substring assertions (python) of every routed quote against the exact `notes`
  strings of `rounds[397]` and `rounds[406]` → all `True`.
- Absence scan of `corpus/lessons/round-23.md`: `42-run`, `R18`, `survivor`,
  `v3-all-scalars`, `timeout reason`, `llama`, `round-17`, `fixture-ratification`,
  `retained-archive`, `L0`, `vacuous`, `uncommitted-now`, `GIT_DIR`, `prelaunch`, `snapshot`,
  `41-hop`, `chain bound`, `duplicate-key`, `injectiv`, `operator-owned`, `selftest` →
  all `False`.
- Line reads at base blobs (via `git show 245a37f6:…`) of the audit selftest, gate scan/launch
  path, receipt chain walk, receipt JSON load, injectivity docstring, plus `SKILL.md:732-738`,
  `registry/report-landing-errata.tsv`, `corpus/lessons/round-21.md:63-65`,
  `corpus/lessons/round-22.md:100-123`, and fleet `.ufo/l0-questions.md:58,68`.

## Not verified

- Did not execute `repo-state-grid.py`, `isolation-mutants.py`, the audit selftest, the ledger,
  or any fault fixture; L1's 26/26 faults, 22/24 mutants, 50/50 selftest, 0 tracebacks and
  no-harm results were not re-measured.
- Did not read the full r20 (67-line), r21 (76-line) or r22 (316-line) reports; used the
  manifest rows, the cited report lines (`round-21:72`, `round-22:198-201`), the lessons and
  the errata ledger.
- Did not verify r19 or r18 source rows beyond the r20 note text, other lanes' rows, or a
  future r23 closure entry (none exists).
- Did not verify who authored the uncommitted lane worktree edits; they are treated as
  observed state, never as evidence for the claim.
- No network use, no REA device, no install or upgrade. Tools installed/updated: none.

## Files written

- `kama-shokunin/.ufo/waves/round-23/falsify/advice/ConnClosureRoutes.md` (this file).
- `/tmp/kama-row-20.json`, `/tmp/kama-row-21.json`, `/tmp/kama-row-22.json` (scratch dumps of
  the three manifest rows, outside the lane).
