# FinalPM11 — canonical operator PM11-any-hole-refusal, pinned source 92063cfc

**VERDICT: KILLED (attributed, `unexpected_rows=[]`).** Decisive row **PG48-opaque-unused-tree-no-unresolved-token**, class **refusal-2** (expected exit 0 → actual exit 2): a substantive verdict change, not a names/reason-only failure. The second declared discriminator PG47 fails **diagnostic-only** (2→2, only the required-object name is lost) and is therefore **not** counted as a substantive verdict change.

## Pin and identities (all observed)
- commit `92063cfc60e217fa7e2098c568578119b16a1b95` (clone `--no-hardlinks --no-local`, detached; `git status --porcelain` empty after all runs).
- mutator `tests/report-audit/promisor-mutants.py` = `971c3ecb…5af200`; grid `promisor-grid.py` = `30483830…f270`; manifest `promisor-grid-expectations.json` = `d86b7bea…14cd1` (**unchanged**, 47 cases + 1 open row); auditor `tools/report-landing-audit.py` = `b9be4f42…3b26f`.
- operator applied via the pinned module's own `apply_mutation`/`compiles` (no re-anchoring): alternative 0, anchor `if __name__ == "__main__":` ×1 (**unique**), `mutant_compiles=true`. Pristine `b9be4f42…3b26f` → mutant `37dcf63b…7502d`.

## Attempted falsification and decisive observations
- Bounded runs only: current arm, 2 cells per tool (`PG48`, `PG47`); the mutator's default/47-cell sensitivity path was **not** invoked. TMPDIR = own scratch per run.
- pristine: grid rc **0**, no violated row; PG48 exit 0 (clean verdict, document present), PG47 exit 2 (names the missing tree `2a675c1a…`).
- mutated: grid rc **1**; PG48 exit **2**, stderr `could-not-evaluate: …/lane: unknown: unavailable required object: 2 hole(s) in the store`; verdict document absent → `amended_problems=["exit 2 != 0", …]`. PG47 exit 2 with the name lost → `amended_problems=["reason does not name the unavailable object"]`.
- restored (pristine bytes again): grid rc **0**, PG48 exit 0 again — byte-exact restoration confirmed; clone and production untouched.
- Stock runner, same 2 cells (`--only PM11-any-hole-refusal`): `status=killed`, `killed=true`, `failed_rows=[PG47, PG48]`, `unexpected_rows=[]`, `classes={refusal-2:[PG48], diagnostic-only:[PG47]}`, `verdict_change=true`, `availability_credit=false`, `could_not_evaluate=[]`, runner rc 0. No timeout, leak, traceback, internal_error, or object acquisition (`objects_acquired` empty in every cell).

## New at this pin (source-level, observed in git history)
The pinned mutator registers PM11 as the **eager `build_store` gate**; the parent commit `ed1cc3a` registered the lazy `RepoStore.missing` gate. Consequently PG48 — which the earlier lazy mutant could not see — now fails with an unconditional over-refusal. The prior wave's F-1 ("PM11's `expect_rows` names PG48 but the mutant does not fail PG48") does **not** reproduce against this pin: PG48 is failed with a substantive refusal-2 class. The widened `expect_rows` (26 rows) contains both cells used.

## Residuals / scope limits
- Bounded sample of 2 cells; survival/kill is **not** a global equivalence claim. PG44/PG45 twins were not run (per-tool cap); PG48 and PG47 declare `twin: null`, so no twin-mismatch branch was exercised here.
- The grader artifact observed: PG48 has no `names_any_of`, so any exit-2 on PG48 also yields `reason does not name the unavailable object` (empty-names `any()` → False). The substantive PG48 signal is `exit 2 != 0`.
- `expect_rows` breadth beyond these two cells (26 rows) is unmeasured here. No source defect in the pinned auditor was found; the mutation contract itself behaves as registered.
- Tool installs: none (existing Python 3.14.8 / git 2.56.0 sufficed). No network used.

Report: .ufo/waves/round-24/postfix/advice/FinalPM11.md
