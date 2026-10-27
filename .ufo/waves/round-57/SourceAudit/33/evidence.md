# Distinct case 54 — independent test of S515 runtime env-pair claim

**Seat:** R57Item33SourceAudit (item `round57/SourceAudit/33`, executor). **Date:** 2026-10-27.
**Companion report:** `.ufo/waves/round-57/w1/out/R57Item33SourceAudit.md`.
**Rule under test (S515):** runtime Git configuration can be injected through the environment pairs `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`.

## Test design (derived from the opened paragraph, not the registry row)

The paragraph at `§ENVIRONMENT`, anchor `Documentation/git-config.txt-GITCONFIGCOUNT` (live lines 5846–5857), makes five falsifiable statements. Each was turned into a probe that could fail:

1. Positive `GIT_CONFIG_COUNT` adds indexed key/value pairs to the process's runtime configuration.
2. Pairs are zero-indexed.
3. Any missing key or value is an error.
4. An empty `GIT_CONFIG_COUNT` behaves as `GIT_CONFIG_COUNT=0` (no pairs processed).
5. Injected pairs override configuration files, but explicit `git -c` options override them.

Falsifiers looked for: the pair being ignored (statement 1 false), index 1 accepted at count 1 (statement 2 false), silent tolerance of a missing pair (statement 3 false), pairs applied under an empty count (statement 4 false), `-c` losing to the environment (statement 5 false).

## Evidence (git version 2.56.0; fresh throwaway repo)

Fixture guard: `git init` in scratch, then `git rev-parse --show-toplevel` printed the fixture directory and the `test` assertion printed `GUARD_OK` before any config write. `GIT_CONFIG_NOSYSTEM=1` throughout.

| Probe | Observed | Meaning |
|---|---|---|
| no pairs: `git config --get probe.key` | exit 1, no output | baseline absent |
| `COUNT=1 KEY_0=probe.key VALUE_0=env-value` | `env-value`, exit 0 | statement 1 holds |
| file `probe.key=file-value`; same env pair | `env-value`, exit 0 | statement 5 (env over file) holds |
| same env pair + `git -c probe.key=cli-value` | `cli-value`, exit 0 | statement 5 (explicit `-c` wins) holds |
| `COUNT=2`, only index 0 given | `error: missing config key GIT_CONFIG_KEY_1` + `fatal: unable to parse command-line config`, exit 128 | statement 3 holds |
| empty `COUNT` with file value present | `file-value`, exit 0 | statement 4 holds (no pairs) |
| `COUNT=2`, pairs at 0 and 1 | `v0`, `v1`, exit 0 | indexed pairs all apply |
| outside any repository, env pair | `env-value`, exit 0 | injection is process-level, not repo-local |
| `KEY_0=core.hooksPath VALUE_0=/attacker/hooks` | `/attacker/hooks`, exit 0 | motivating example reproduces |
| `KEY_0`/`VALUE_0` set, `COUNT` unset | exit 1, no output | pairs need the count |
| `COUNT=1`, only index 1 given | `error: missing config key GIT_CONFIG_KEY_0`, exit 128 | statement 2 holds (zero-indexed) |
| `COUNT=0` with a pair given | exit 1, no output | statement 4 holds |

Raw transcripts: `.ufo/waves/round-57/SourceAudit/33/receipts/runtime-repo.out` and `runtime-edge.out`; versions in `versions.out`.

## Independent source re-check

Live fetch this round: `HTTP/2 200`, 830605 bytes, exit 0; sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`, identical (`cmp`) to both the round-57 and round-56 snapshots. Quote verifies at 18 words after entity decoding, with U+2019 in `process’s`; the registry/lesson ASCII apostrophe is a normalization, not a verbatim substring. Revision selector says `git-config last updated in 2.56.0`.

## Result

All five statements survive the probes; no falsifier fired. The S515 claim is **confirmed** for git 2.56.0 at the 2026-10-27 revision, with the single punctuation-fidelity caveat. No shared files were edited; the scratch fixture was deleted after `receipts/` were copied to the wave path.
