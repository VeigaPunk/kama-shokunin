# V2C2Delta — code review of the round-55 C2 delta (tools/round54-cited-path-check.py)

VERDICT: Two defects — (HIGH) the `superseded` clause never verifies the base citation resolved there, contradicting the frozen class text/PREDICATE, and I forged a real-tree tip that deletes a never-resolved base citation and prints `met=True` exit 0 (receipt-forge-570f2f4.txt); (MEDIUM) the fixture's forged-`superseded` arm is dead code — the per-scenario `hit` is clobbered by an unconditional `hit = bool(want(ok, c))` at line 810, so a killed clause-(b) still yields 15/15.

Scope: `git -C kama-shokunin diff 3a600d2f 9c60eae6 -- tools/round54-cited-path-check.py` (+81/−22). Counter sha256 of the tip blob `d70a1729174e4df8c71e5954da85b9580d409595e7c2e1f238a81b92a326510c` = preregistration `claims.C2.counter_sha256` (matches). Build measurement reproduced: `met=True` exit 0 at 9c60eae6; base control reproduced: `dropped=1 met=False` exit 1 at 3a600d2f. All work in `/fast/scratch/hyaku/kama-r55/w1/V2C2Delta` (shared clone `$S/lane`, forged commit `570f2f42e5d3a01b3dd43456db413ef0aedaab47`); receipts copied into this directory. No tools installed; none needed.

## Finding 1 (HIGH): `superseded` accepts an unresolved-at-base token — doc/predicate claim unenforced, demonstrable laundering

Docstring (counter-tip.py:96–103): "`superseded` ... the original token was cited in that surface at --base **and resolved there** (unlike `fixed`, which corrects an UNRESOLVED citation...)". Predicate (docstring:128–136 and preregistration C2, identical sentence): "`superseded` rows disclosing a **live** base citation re-pointed to a cited, resolving replacement".

Code (counter-tip.py:461–479) enforces only that the token was *cited* at base (`tok in base_citelines[surf]`, clause d). `base_citelines` comes from `citation_lines(base_text)` (evaluate:614–619) and includes unresolved citations. `base_unres` — already passed to `check_row` at :402 — is never consulted by the superseded block. A token that was cited but **unresolved** at base passes all four clauses, is exempted from `dropped` (:646–647), and dodges every `fixed` constraint (stem extension :423, same-line :430–442).

Demonstration on the real tree (scratch clone only, tip 9c60eae6 + 1 forged commit `570f2f42`):
- Edits: removed the one backticked citation `` `.ufo/waves/round-999/count-c999.py` `` (SCORECARD line 1844 — an absent-on-purpose control path, `never`-rowed at registry/cited-path-corrections.tsv); deleted that `never` row; added `SCORECARD.md .ufo/waves/round-999/count-c999.py superseded corpus/lessons/round-53-verifier-spotcheck.md` (a token cited at tip and resolving).
- Result: `fixture=1 lane=1 scenarios=15/15 cited=692 unresolved=13 disclosed=13 undisclosed=0 bad=0 stale=0 dropped=0 met=True`, exit 0 (receipt-forge-570f2f4.txt). A live-citation deletion plus a ledger-row deletion produced a passing build measurement.
- With the row kept instead, the stale check catches it (`stale=1`) — but the counter never enforces ledger append-only (it reads only tip rows, :386–400), so deletion is invisible; the `superseded` row is what launders the `dropped` count.
- Patched copy `counter-fixed.py` (fix-superseded-base-resolved.diff applied) on the same forged commit: `bad=1 met=False` exit 1; real tip still `met=True` exit 0; base control still `dropped=1 met=False` exit 1.

This is the round-54 externalized doc/code gap recurring in the new class: the docstring/predicate promise ("live", "resolved there", "(unlike fixed ...)") has no code. Severity HIGH because it is exploitable by construction, not hypothetical — the forged run above is the exploit.

Proposed fix: `fix-superseded-base-resolved.diff` (validated): after clause (d), add `if tok in base_unres.get(surf, set()): return "...unresolved at the base (a fixed-class correction, not a re-point)"`.

## Finding 2 (MEDIUM): fixture's forged-`superseded` arm is dead — `hit` clobber at line 810

`fixture()` (:673): the superseded case (:778–796) runs two evaluations — `lane` honest, `lane2` forged — and computes an extended verdict at :795–796: `hit = bool(want(ok, c)) and ok and c["dropped"]==0 and c["bad"]==0 and (not ok2) and c2["bad"]==1`. Line :810 then unconditionally runs `hit = bool(want(ok, c))` for every shape, overwriting the extended value. `want` is `lambda ok, c: ok`, so the scenario counts whenever the honest branch returns ok — `ok2`/`c2` and the honest-side `dropped`/`bad` assertions never gate anything.

Demonstration: patched `check_row` to return `None` for `superseded` rows (kills clause b → forged lane evaluates `ok2=True, bad=0`); fixture still prints `got=15/15`, `fixture ok: superseded ... (met=True {...})` — the forged arm passing is invisible (experiments.txt, last lines; the second evaluate result `(True, {'cited': 0, ..., 'bad': 0, ...})` is the unasserted forged call).

With `fix-fixture-superseded-hit.diff` applied, the same patch yields `fixture FAIL: superseded ...` and `got=14/15`; unpatched it still yields 15/15 (validated).

## Finding 3 (LOW): fixture covers none of clauses (a), (c), (d); docstring overclaims a "still-cited" arm that was never built

- All four clauses are reachable (demonstrated in synthetic repos, experiments.txt): (a) "still cited at tip" → bad; (b) replacement not cited → bad; (c) replacement cited but unresolved → bad (+undisclosed); (d) token not cited at base → bad. Only clause (b) is constructed in the fixture — and per Finding 2 it is unenforced anyway.
- The docstring says the fixture covers "`superseded` row whose **token is still cited**, or whose replacement is not cited at tip, is bad" (:119–121). No clause-(a) arm exists: `lane2` (:792) writes a surface with zero citations, never a still-cited token. Overclaim.
- Also unenforced because of the clobber: the honest-side assertions `c["dropped"]==0 and c["bad"]==0` (redundant today since `ok` implies them; a regression that met ok despite dropped>0 would be invisible).

## Seat checklist — all items verified

- **Four clauses reachable?** Yes, all; demonstrated at row level (experiments.txt). Clause order (a)→(b)→(c)→(d) is sensible.
- **`base_citelines` None path?** `evaluate` always passes a dict — `{}` when `base_lane=None` (:614) — so the `is not None` guard is dead through `evaluate`; a superseded row in a base-less evaluate is bad via clause (d) (conservative). Direct `check_row(..., base_citelines=None)` returns `None`; verified both directions (`None` → pass, `{}` → bad). Same conservative shape as `fixed`.
- **`bad_exp` None path?** The superseded block is inserted *before* `if not bad_exp: return None` (:480) and never reads `bad_exp` — correct, since a good superseded token is absent or resolving at tip (an unresolved tip citation is `tok ∈ cited_tip` → clause (a) bad).
- **stale-exempt / dropped-exempt sets?** Correct three-site wiring (:637, :641, :646–647): superseded rows never go stale (bad covers every failure), good superseded tokens are never in `unres` so disclosed-exclusion (:641) can't leak undisclosed drops, and `exempt` is (surface, token)-scoped so cross-surface exemption can't occur. One note: `exempt` counts *bad* superseded rows too — harmless since `bad>0` already fails met.
- **disclosed-accounting exclusion?** Consistent: a good superseded row's token is never an unresolved tip citation, so `undisclosed` needs no entry.
- **SCENARIOS 14→15?** `cases` list now 15 entries (8 round-53 + 6 round-54 + 1 superseded); `SCENARIOS=15`, docstring "fifteen", predicate "fifteen constructed scenarios", output "N/15", `fx = nfx == SCENARIOS` — all consistent.
- **Fixture superseded block?** `lane2` really leaves the replacement uncited ("closure re-pointed away in prose" has zero backticked tokens; `cited[SCORECARD]={}` → clause b). The honest branch really passes `dropped=0`: base cites only `tools/live.py`, exempt covers it, `met=True` reproduced. But both are unenforced per Finding 2. `at()` (:715) fully replaces the ledger; the pre-base `os.unlink` correctly prevents the fixed-honest row leaking into `scen_base`'s ledger. `w("SHONEN.md","x\n")`/`SKILL.md` keep other surfaces citation-free.
- **Docstring class text vs code?** Finding 1 ("resolved there"/"live" unenforced; the `fixed`-contrast comment at :468–469 is unenforced) and Finding 3 ("still cited" arm overclaimed). Everything else in the class text checks out: not-cited-at-tip (a), replacement cited (b) and resolving (c), stale/bad semantics (:105–106 wired at :637–641), dropped/stale exemption.
- **BASE?** `0b75a84c` (round-53 tip) with the explanatory comment; base control reproduces `dropped=1 met=False` exit 1 — the round-52→round-53 spotcheck re-point is exactly the drop the control catches.
- **Real lane leg facts?** At base, SCORECARD:18 cites `corpus/lessons/round-52-verifier-spotcheck.md` and the file exists at 0b75a84c (resolves); at tip, SCORECARD:18 cites `round-53-verifier-spotcheck.md` (resolves) and the round-52 token appears in zero backticked citations → the real row is a legitimate superseded disclosure.

## Residual risk / out-of-scope notes

- Ledger append-only is still unenforced (round-54-frozen behavior); the Finding-1 exploit needs row deletion as one ingredient — the delta's contribution is the second, unenforced ingredient.
- `externalized` has the same unenforced "unresolved at base" doc claim (pre-existing, frozen round-54 code, outside this delta).
- The `never` row's note cites "SCORECARD lines 1844, 1901" but only 1844 parses as a citation (line 1901's span contains spaces → BAD_CHARS); cosmetic, pre-existing.

## Files in this report dir
- `receipt-tip-9c60eae.txt`, `receipt-base-3a600d2f.txt`, `receipt-forge-570f2f4.txt` — counter runs on the shared clone (tip/base/forged; forged exits 0 = exploit).
- `experiments.txt` + `drive.py` — clause reachability matrix, None-path checks, laundering variants, fixture-clobber proof.
- `fix-superseded-base-resolved.diff`, `fix-fixture-superseded-hit.diff` — proposed fixes, both validated against synthetic and real-tree cases (frozen counter untouched).
