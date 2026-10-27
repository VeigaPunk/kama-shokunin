# V3Review — round 51, code review of `tools/append-only-audit.py` v6 (lane kama)

**Verdict: the v6 diff is sound on every leg the C2 counter exercises — selftest 47/47 and counter `fixture=1 lane=1 scenarios=9/9 met=True` reproduced on my own clone at 138af25b — but two latent divergences from `tools/sources-append-only.py` (the tool the A-row contract row cites as the rule) are real defects: (V3R-1) `row_cells` splits on GFM-escaped pipes `\|`, grading permitted status/recheck edits of such rows as losses; (V3R-2) `permitted_edits` matches a deleted row against any same-id row anywhere in the commit blob, so an immutable-cell mutation hidden by a re-added copy of the old row passes with exit 0 where the lane guard refuses the state (exit 2). Neither fires on the corpus today; both are fail-open paths the frozen counter shares, so C2 cannot catch them.**

Scope: full diff `git diff 57a2e25b..138af25b -- tools/append-only-audit.py` (487 lines, read in full) plus the named areas; every finding demonstrated on a fixture repo in my scratch with the tip's own bytes (`git show 138af25b:tools/append-only-audit.py`). The tool, counter, preregistration and controls were treated as frozen: no in-place edits; proposed fixes are report artifacts.

## Findings

### V3R-1 (Medium, latent) — `row_cells` does not honour `\|` escapes; permitted A-row edits of escaped-pipe rows are graded as losses

- Defect: `tools/append-only-audit.py:486-506` (`row_cells`) splits cells on every `|` outside backtick code spans, with no escape handling (`@ 138af25b`, loop at lines 497-504). `tools/sources-append-only.py:91-133` (`split_cells`, lines 106-111) treats `\|` outside a code span as cell content, kept verbatim; its docstring (lines 51-54) states the lane deliberately allows `\|` escapes in registry rows. The contract row for `corpus/SOURCES.md` (rule `A-row`) cites `tools/sources-append-only.py` as the rule.
- Unit evidence (probe batch 1, `probe-batch1.log` `[parser escaped]`): for `| S102 | doc 2 | docs | A | scope a\|b | sec | lesson 2 | mined | 2026-09-02 | 60d | a.md |`, v6 `row_cells` → **12 cells** (cell 5 = `scope a\`), sources `split_cells` → **11 cells**.
- End-to-end (probe batch 2, `probe-batch2.log` `[F1r]`): same fixture (`## Registry` table, contract `SRC.md A-row`), a commit changing only `status` and `recheck` of the escaped-pipe row:
  - v6 tool: `exit=1`, event `SRC.md status=unrestored permitted=0 graded=1`, `undisclosed` names the row key `f6f92b3c…` with class `in-place-edit`.
  - `sources-append-only.py` on the identical pair: `exit=0` "no append-only violations".
- Reachability today: `grep -F '\|' corpus/SOURCES.md` at 138af25b → 0 occurrences; census over all 240 lines matching the `ROW` regex at the tip: **0** cell-count disagreements between the two splitters (`probe-batch4.log` `[census]`). So the build receipts and the `permitted_lines=58` at the tip are unaffected — this is latent, not live.
- Why it matters: the preregistration predicate says v6 "permits exactly the A-row status/recheck/used-by cell edits". The lane's own guard permits escaped-pipe rows that v6 grades as lost lines (exit 1) — the first future registry row using GFM escaping flips every its in-place edit into an undisclosed loss. The frozen counter shares the blind spot: its own `cells()` (round51-append-audit-v6-check.py, ~lines 117-131) splits identically, so its lane leg compares tool-vs-counter with the same wrong reader and always agrees.
- Fix: `out/V3Review/proposed-fix-v6.1.md`, Fix 1 (escape-aware `row_cells`, cells byte-identical to sources' including the retained backslash).

### V3R-2 (Medium, latent) — `permitted_edits` matches against any same-id row in the blob; an immutable-cell mutation hidden by a re-added old-row copy passes exit 0 where the guard refuses

- Defect: `tools/append-only-audit.py:508-523` — `rows[c[0]].append(c)` (line 515) collects every 11-cell row of the commit's blob keyed by id, and line 520 permits on `any(keep(n) == keep(c) for n in rows.get(c[0], ()))`. A commit that mutates an immutable cell of `S102` in place and re-adds a copy of the old `S102` row satisfies the match against the copy: the mutation escapes grading. The scan covers the whole blob, not the registry section.
- End-to-end (probe batch 4, `probe-batch4.log` `[F2y]`): base table S101/S102/S103; commit mutates `teaches` on S102 and appends the old S102 row after S103:
  - v6 tool: `exit=0`, event `SRC.md status=ungraded deleted=1 permitted=1 graded=0` — the immutable-cell edit is silently permitted.
  - `sources-append-only.py` on the identical pair: `exit=2` `duplicate id S102` — the guard refuses to grade this state at all.
- An earlier variant without the `## Registry` heading shows the same tool verdict (`probe-batch1.log` `[F2 duplicate-id decoy]`: exit=0, permitted=1); `F2x` (batch 3) shows git's hunk regrouping can add a collaterally deleted row that is still graded — the evaded line itself is `permitted=1` in every variant.
- Why it matters: the docstring defines permitted as "the in-place change the A-row rule allows" — a `teaches` mutation is not allowed by the A-row rule, yet v6 reports exit 0 on a state the lane's guard refuses to certify. Fail-open where the guard fails closed. The frozen counter's lane-leg permit loop (round51-append-audit-v6-check.py, `new[cc[0]].append(...) ... in new.get(cc[0], [])`) has the same shape and cannot catch it.
- Fix: `out/V3Review/proposed-fix-v6.1.md`, Fix 2 (require the id held exactly once; duplicated id permits nothing, so the state is graded, not waved through).

### Reviewed clean (each named area, evidence in probe logs)

- `parse_disclosures` (`:525-542`): 5-field row (missing note) → exit 2 (`probe-batch1.log` `[F7a]`); note containing a tab (7 fields) → exit 2 (`[F7b]`); empty note / trailing tab accepted (`[F4a]` rows end in `\t`, exit 0) — harmless, the note is never machine-read, and the generator (`build_ledger.py`) always writes `"deleted in place by: " + subject` with tabs neutralized, so it never emits an empty or tab-carrying note; `count=0` rejected by the `[1-9][0-9]*` regex. Header/CR checks match the generator's output.
- Duplicate ledger rows for the same key: counts sum — two 1-rows clear a 2-line loss, `disclosed=2`, exit 0 (`probe-batch1.log` `[F4a]`); over-count rejected per row — first row ok, second `count 1 > unheld graded lines 0 with that key`, `bad_disclosures=1`, exit 1 (`probe-batch3.log` `[F4d]`). Ledger at tip: 166 rows, 0 rows with ≠6 fields, 0 duplicate (commit, file, key).
- Unheld/disclosed accounting (`:670-695`): `Mto`/`K` baseline and `n - min(n, max(0, Mto-K))` match the counter's own recomputation; restored lines are not disclosable (tool selftest `v6-restored-not-disclosable` passes); partial disclosure leaves `unrestored` with `disclosed=1` (counter fixture); `held_at_to = h` reuses the window-loop variable — safe, `rev-list --topo-order --reverse` always ends at `<to>` so the last iteration is the tip. Identity `graded + ungraded + permitted == deleted` held in every fixture (e.g. F2y: 1+0+1).
- `undisclosed` JSON (`:709-711`): only positive remainders, `+unheld` drops decremented zeros, classes from non-permitted deleted lines; matches what `build_ledger.py` consumes (single-class assertion, one row per key, count aggregated).
- Subject fetch condition (`:678-679`): fetched iff a disclosure names the event or `unheld` is non-empty — exactly the two consumers of `cls` (disclosure class check, `undisclosed.classes`); no event can surface a wrong class. End-to-end revert: subject `Revert "fx"` + class `revert` → ok, exit 0; class `removal` → `class removal is not ['revert']`, exit 1 (`probe-batch2.log` `[F8]`).
- Render/summary keys: `definition=v6`, `threshold=1`, `summary.{unrestored,partial,regressed,bad_disclosures,bad_declarations,disclosed,permitted_lines,disclosed_lines,…}` all present and are exactly the keys the counter's lane leg reads; text render adds `permitted=`/`disclosed=` and `disclosure … bad:` lines.
- Exit code (`:757-763`): adds `bad_disclosures` to the v5 condition — malformed ledger → exit 2 (F7a/F7b), bad disclosure rows → exit 1 (F7c/F8/F4d), unmatched patterns stay informational (F7d: `unmatched=1` with exit driven by the unbound declaration, per the docstring).
- Docstring/implementation agreement: permitted definition (11 cells, mutable cells 8/10/11 = 0-based 7/9/10 = `MUTABLE_COLS`), `arow` requires rule exactly `A-row` (only `corpus/SOURCES.md` in the tip contract), ledger auto-read only with the default `<to>` contract.

## Grounding (not re-reported as findings)

- Tool selftest at tip bytes: `AOA_SELFTEST pass=47 fail=0`, exit 0 (`out/V3Review/selftest.log`).
- C2 counter on my own `git clone --shared` at 138af25b: `fixture=1 lane=1 scenarios=9/9 lost=142 disclosed=166 met=True`, exit 0 — matches the build receipts (106 events, 166 disclosed lines, 58 permitted) (`out/V3Review/c2-receipt-V3Review.out`).
- No tool installs or upgrades were needed (system python3/git only); no services started (the C2 counter is git-only); lane and fleet repos untouched (read-only git; fixture repos lived in scratch with `rev-parse --show-toplevel` asserted).

## Residual risk and verification gaps

- The unchanged v5 legs (binding, regions, origin, fences, restoration) were reviewed only as touched by the diff (na threading, perm skip) — a full v5 re-derivation was out of scope for this seat.
- Non-UTF-8 bytes in an A-row file: v6 `row_cells` → None → the line graded (fail-closed, exit 1); `sources-append-only.py` exits 2. Divergence exists but in the safe direction; not fixture-tested.
- No fuzzing of backtick runs (double backticks), CRLF-terminated rows, or merge-commit hunks in A-row files; both splitters toggle `code` on every backtick identically, so exposure looks minimal, but it is unverified.
- If Fix 1/2 are adopted in a later round, the frozen counter (`cells()`, lane-leg permit loop) must be re-derived with them, otherwise tool and counter diverge in the opposite direction.

## Absolute paths written

- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review.md (this report; trailer path `.ufo/waves/round-51/a2w1/out/V3Review.md`)
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/proposed-fix-v6.1.md
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/c2-receipt-V3Review.out
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/selftest.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/probe-batch1.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/probe-batch2.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/probe-batch3.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/probe-batch4.log
- /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/V3Review/drive.py, drive2.py, drive3.py, drive4.py (fixture drivers)
