# Round 23 — repo-local git state can flip or crash a report-landing verdict

DRAFT — scribe output under `build/out/ScribeLessonDraft/`. Not the corpus lesson; do not copy into `corpus/lessons/` without L1 integration.

Round start: branch master `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (git 2.56.0, Python 3.14.8).
Assigned axes: calibration7 (lowest assigned non-retired axis) and operability8. The L1 holds the canonical planner seat.

## Declared claim

**C1 — calibration7→7 (draft): `tools/report-landing-audit.py` fails closed under repository-local git state.**
The script's stated promise that errors are never verdicts, and its `git_env` docstring that audited repositories cannot be redirected, hold only for environment variables and user/system config. Repository-local configuration and refs still change or crash the verdict at frozen base `4fe9339f`:

- `i18n.logOutputEncoding` (non-UTF-8) plus a non-ASCII subject: uncaught `UnicodeDecodeError`.
- Invalid UTF-8 bytes in a committed report: uncaught `UnicodeDecodeError`.
- `refs/replace/*` hiding an omitted round commit, or resolving a fabricated full hash: clean verdict.
- Promisor remote with `core.sshCommand`: lazy fetch executes the configured command.

Measured form: a finite fault grid, frozen (`4fe9339f`) versus current. Each fault must become either a typed refusal (`could-not-evaluate`, exit 2) or the correct verdict. Control cases must be unchanged. The existing selftest (50/50) and the historical rounds 10–22 ledger (clean via errata) must remain unchanged.

This is narrow D4 frontier movement, not general untrusted-repository hardening. Alternates and `clone --shared` remain legitimate.

Counting command: to be fixed by the L1 before the measured run. No measured outcome is claimed here.

## Gate

_Placeholder: source rows (S-numbers, URL, located quote ≤25 words, access date) are to be opened and added by the L1 at Gate opening. This draft admits no source rows and quotes no source text._

Candidate source topics to be sought, not yet opened: git config and `--no-replace-objects` / `--no-lazy-fetch` semantics; `i18n.logOutputEncoding`; Python `subprocess.run(text=True)` decoding and `UnicodeDecodeError` being a `ValueError`, not an `OSError`.

## Mistakes

| ID | Class | Evidence | Captured-by | Fix / failure witness |
|---|---|---|---|---|
| M1 | Overclaimed trust boundary in docstring; non-`OSError` exception escapes the could-not-evaluate path | `tools/report-landing-audit.py:79-84`: `git_env` strips `GIT_*` and disables global/system config only; its docstring (`:80-81`) says audited repos cannot be redirected. `:87-97` `git()` converts only `OSError` to `EvalError`; `:835-843` `main()` catches only `EvalError` and `OSError`. Observed: `/tmp/kama-r23-probe/run.uCZq/f1-logenc.err` and `f2-report-bytes.err` (same in `run.xpxV`) end in `UnicodeDecodeError` from `subprocess.py` `_translate_newlines`; `.out` files empty, so no JSON verdict was emitted. Repo-local `i18n.logOutputEncoding=ISO-8859-1` in `f1/lane`; bytes `\377\376` committed in `f2/fleet/.ufo/reports/round-1/kama.md`. Exit code not captured; exit 1 is [INFERENCE] from an uncaught exception. | L1 probe `/tmp/kama-r23-probe/probe.sh` (faults F1, F2); artifacts `run.uCZq`, `run.xpxV` | Candidate, undecided: bytes-mode git with strict UTF-8 decode that raises `EvalError` (exit 2); `-c i18n.logOutputEncoding=UTF-8` on git calls. Witness: f1 and f2 must yield a typed refusal, never a traceback. The docstring must be corrected to name repo-local config as out of scope. |

## Integration and boundaries

- Scope is the fault grid only. Environment scrubbing does not suppress repository-local configuration; the docstring is corrected, not read as a hardening claim.
- Not claimed: untrusted-repository execution hardening, race freedom, or any fix to a production consumer. Lazy-fetch and `sshCommand` fixtures use `example.invalid` only and never touch real hosts. Fixtures run only in fresh temp repos under `/tmp` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1`.
- Other grid rows (not in M1; observed in probe artifacts, to be re-checked by the L1 before any claim):
  - F3 `git replace` of an omitted round commit: clean exit in `run.xpxV`; in `run.uCZq` the replace ref is absent and the audit flags `landed-omitted`. Not reproduced consistently.
  - F4 `refs/replace/<fabricated 40-hex>`: clean in both runs.
  - F5 promisor lazy fetch with `core.sshCommand="touch <marker>; false"`: marker file present in both runs, so the configured command executed.
- Not run by this draft: selftest 50/50, historical ledger check, frozen-vs-current measurement. These are L1 integration duties after the clean committed tree.
- Frozen base for the claim: `4fe9339f`. The lane checkout and corpus were not written.
