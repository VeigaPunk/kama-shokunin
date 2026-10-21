# SimplifyWrapper — centralized `git()` / `git_env()` hardening

## Godspeed axes

| Axis | Move |
|------|------|
| **Operability (C1)** | Repo-local encoding/replace/lazy-fetch faults become `EvalError` (exit 2) instead of traceback exit 1. |
| **Correctness** | Replace refs and promisor lazy-fetch cannot satisfy lookups or hide omissions. |
| **Simplicity** | One module-level `_GIT_PREFIX` + two function bodies; zero per-call-site flag edits. |
| **Parity** | Valid UTF-8 control paths unchanged; selftest 50/50 on patch (same as frozen base). |

## Proposal (smallest diff)

**Artifact:** `.ufo/waves/round-23/build/out/SimplifyWrapper/git-wrapper.patch` (+35/−8 lines in `tools/report-landing-audit.py` only).

1. **`_GIT_PREFIX`** — argv injected before `-C` on every `git()` call:
   - `--no-replace-objects`, `--no-lazy-fetch`
   - `-c i18n.logOutputEncoding=UTF-8`, `-c log.follow=false`

2. **`git_env()`** — adds `GIT_NO_REPLACE_OBJECTS=1`, `GIT_NO_LAZY_FETCH=1` (mirrors round-12 `fidelity.py:84–85`; belt-and-suspenders with argv flags per git(1)).

3. **`git()`** — drops `text=True`; encodes str `stdin` as UTF-8; decodes stdout with strict UTF-8 → `EvalError` on `UnicodeDecodeError`; stderr in failure messages uses `errors="replace"` only for the diagnostic string (never a verdict).

**Prior art in lane:** `.ufo/waves/round-12/fidelity.py:80–111` (`git_environment` + `--no-replace-objects` + bytes stdout).

## Call sites — different behaviour?

All **21** `git(...)` invocations in `report-landing-audit.py` use the wrapper; none opt out of replace/lazy-fetch/encoding overrides.

**Legitimate per-call `-c` (unchanged, compatible with prefix):**

| Location | Extra args | Why |
|----------|------------|-----|
| `_commit` L466 | `-c commit.gpgsign=false` | Selftest/fixture commits without GPG. |
| `selftest` L538 | `-c commit.gpgsign=false` | Fleet report rm/add fixture commits. |

These are **not** alternate git stacks; gpg override composes with `_GIT_PREFIX` (git applies multiple `-c` keys; distinct keys do not conflict).

**No call site** should bypass hardened `git()` for audit reads. Selftest `_commit` correctly keeps author/committer env via `git_env(...)` + hardened `git()`.

## Evidence

| Check | Command | Observed |
|-------|---------|----------|
| Patch size | `wc -l out/SimplifyWrapper/git-wrapper.patch` | 50 lines |
| Selftest (patched) | `python3 tools/report-landing-audit.py --selftest` in `/tmp/kama-r23/SimplifyWrapper` | `selftest cases=50 failed=0`, exit 0 |
| Selftest (frozen file) | same after `git stash` on unmodified tree | `selftest cases=50 failed=0`, exit 0 |
| Clone base | `git -C /tmp/kama-r23/SimplifyWrapper rev-parse HEAD` | `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` |
| Host git | `git --version` | `git version 2.56.0` |

## Not verified (this seat)

- L1 fault grid (a–e) re-run against patched script — DecodeFix/ReplaceFix seats own targeted selftest additions.
- Git &lt; 2.44 rejection of `--no-lazy-fetch` (OldGit seat).
- Whether env-only vs argv-only is sufficient alone (chose both for round-12 parity).
- Full fleet audit on real lane/fleet repos (contract: fixtures only in `/tmp`).

## Installs

None.

## Files written

- `.ufo/waves/round-23/build/advice/SimplifyWrapper.md` (this file)
- `.ufo/waves/round-23/build/out/SimplifyWrapper/git-wrapper.patch`
