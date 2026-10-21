# ScribeLessonDraft — round-23 lesson skeleton report

Role: leaf scribe. No subagent dispatch. No corpus, lane, fleet, or config writes. No installs. No probe re-execution.

## Behavior
Drafted the round-23 lesson skeleton with sections Declared claim, Gate (placeholder), Mistakes (one row, M1), and Integration and boundaries. Corpus untouched.

## Gates
- Gate section: placeholder only. No source rows admitted or quoted.
- No pass/fail gate was run.

## Touched surfaces
- Written: `.ufo/waves/round-23/build/out/ScribeLessonDraft/round-23-draft.md`
- Written: `.ufo/waves/round-23/build/advice/ScribeLessonDraft.md` (this file)
- Read only: `tools/report-landing-audit.py` (lines 79-97, 813-843); `/tmp/kama-r23-probe/probe.sh`; `/tmp/kama-r23-probe/run.uCZq/`, `run.xpxV/` (artifacts, read-only); `corpus/lessons/round-22.md` (format reference); `.ufo/waves/round-23/build/` listing.

## Findings (exact evidence)
1. **Docstring overclaim.** `tools/report-landing-audit.py:80-81` says audited repos cannot be redirected. `git_env` (`:82-84`) removes `GIT_*` variables and disables global/system config only. Repo-local config still applies, confirmed by `run.uCZq/f1/lane` and `run.xpxV/f1/lane` having `i18n.logOutputEncoding=ISO-8859-1`.
2. **Errors escape the EvalError path.** `git()` (`:87-97`) converts only `OSError`. `main()` (`:835-843`) catches `EvalError` and `OSError`. `UnicodeDecodeError` is a `ValueError` and escapes.
   - `run.uCZq/f1-logenc.err` and `f2-report-bytes.err`, and the same files in `run.xpxV`: `UnicodeDecodeError` traceback; `.out` files are empty, no JSON verdict.
   - **Discrepancy with the L1 brief:** it said the f1 error "became a `failed` verdict". The retained artifacts show no verdict; the outcome is an uncaught exception. Exit code was not captured; exit 1 is [INFERENCE] from uncaught-exception behavior.
3. **F3 (replace-omit) is not reproducible across the two runs.**
   - `run.xpxV/f3-replace-omit.out`: `status: clean`, `round_commits: 1`, with `refs/replace/4312b0…` → `573413f…` present and `git log` showing the replacement message "unrelated". Matches the L1's "false clean exit0".
   - `run.uCZq/f3`: no `refs/replace` ref; `status: failed`, defect `landed-omitted` for `4312b0…`. The fault did not activate in this run; the probe script has no `set -e`, so the silent `git replace` failure is the likely cause [INFERENCE].
   - The lesson must not count F3 as stable until the L1 re-establishes it with a checked replace-ref precondition.
4. **F4 (fabricated full hash) reproduces.** `run.uCZq/f4` and `run.xpxV/f4`: `refs/replace/1234567890abcdef…` present; `defects: []`, `status: clean`. The fabricated citation in the report resolves.
5. **F5 (lazy fetch executes repo command) reproduces.** `run.uCZq/f5/marker` and `run.xpxV/f5/marker` exist (0 bytes, created by `core.sshCommand="touch …; false"`); repo has `remote.origin.promisor=true`. Verdict `failed` with `unresolved-full-hash` / `landed-unresolved` on `abcdef…`, not `could-not-evaluate`.
6. **F6 (log.follow) control:** `status: clean` in `run.uCZq`. Not part of M1.
7. **Run directory `run.f3eZO`** contains only partial `fleet` and `lane` directories. Not used as evidence.

## Out of scope (not drafted)
- Trust-boundary extension to untrusted repos; race or authentication hardening; alternates or `clone --shared`.
- Selftest 50/50 run, historical ledger check, frozen-vs-current measurement. These are L1 integration duties.
- Source-row Gate content; not opened by the scribe.

## Not verified
- Exit codes for any probe case (not captured in artifacts).
- Reproducibility of F3, and the root cause of its missing replace ref.
- The L1's stated fix direction. The draft records it as undecided.
- Frozen-base (`4fe9339f`) behavior for these cases. The audit revision the probe invoked (the `AUDIT` env var) is not recorded in the artifacts, so which script revision produced each outcome is unverified.

## Tools installed or updated
None.
