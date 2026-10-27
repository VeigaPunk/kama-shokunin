# R57Item33SourceAudit — S515 live re-open and runtime env-pair verification

**Item:** `round57/SourceAudit/33` (executor; distinct case 54). **Axes:** calibration, operability. **Run date:** 2026-10-27.
**Scope:** read-only source audit plus scratch-runtime tests. No lane source files, shared files, registry rows, or fleet files edited. Tooling rules read (`/home/vgpnk/.omp/agent/RULES.md`); pacman transactions remain paused.

## S515 source reopen (this round)

```
$ curl -sSL --fail --show-error --max-time 45 -D live.headers -o live.html \
    -w 'http_code=%{http_code} url_effective=%{url_effective} size_download=%{size_download}\n' \
    https://git-scm.com/docs/git-config
http_code=200 url_effective=https://git-scm.com/docs/git-config size_download=830605
curl_exit=0
```

Response headers (receipt `receipts/live.headers`): `HTTP/2 200`, `last-modified: Mon, 26 Oct 2026 14:52:03 GMT`,
`etag: W/"6adf6913-cac8d"`, `date: Tue, 27 Oct 2026 18:10:22 GMT`.

- **Access date:** 2026-10-27 (live re-open this round).
- **URL:** https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT — the anchor id `Documentation/git-config.txt-GITCONFIGCOUNT` is present (live line 5846), so the fragment target resolves.
- **Snapshot identity:** live body sha256 `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`, 830605 B; `cmp` **IDENTICAL** to both `.ufo/waves/round-57/sources/git-config-live-2026-10-27.html` and the round-56 snapshot `.ufo/waves/round-56/sources/git-docs-git-config.html`. No drift since the round-56 snapshot; the S515 snapshot-path claim holds.
- **Location:** `§ENVIRONMENT` (nearest preceding `<h2>` is `ENVIRONMENT`; next is `EXAMPLES`), under the task-oriented headings `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>`, in the paragraph at live lines 5850–5857 following the anchor at 5846.
- **Located quote — 18 words (≤25):** “all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to that number will be added to the process’s runtime configuration”.
- **Revision marker:** page selector text `git-config last updated in 2.56.0` is present; local `git version 2.56.0`. This matches the row's “git 2.56.0 (page last updated in 2.56.0)”.

**Quote-fidelity note (minor, non-blocking):** after HTML-entity decoding and whitespace collapse the quote is present verbatim with a typographic apostrophe (`process’s`, U+2019); the ASCII-apostrophe form recorded in `corpus/SOURCES.md:268` and `corpus/lessons/round-56.md:18` is **not** a byte substring of the source (`quote_present_U2019=True`, `quote_present_ASCII_apostrophe=False`). Word count is unchanged at 18; this is punctuation normalization in the registry/lesson, not a wrong quote.

## Runtime claim verified on git 2.56.0

The claim under audit is runtime configuration injection through the `GIT_CONFIG_COUNT` / `GIT_CONFIG_KEY_<n>` / `GIT_CONFIG_VALUE_<n>` environment pairs. Beyond the source text, the claim was exercised against the installed `git version 2.56.0` in a throwaway repo. Guard: `git init` in scratch, then `git rev-parse --show-toplevel` printed the fixture dir and the assertion printed `GUARD_OK` before any config mutation.

| Probe | Result | Exit |
|---|---|---|
| fresh repo, no pairs, `git config --get probe.key` | (no output) | 1 |
| `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=probe.key GIT_CONFIG_VALUE_0=env-value` | `env-value` | 0 |
| file `probe.key=file-value`; then same env pair | `env-value` (env overrides file) | 0 |
| same env pair + `git -c probe.key=cli-value` | `cli-value` (explicit `-c` overrides env) | 0 |
| `COUNT=2` with only index 0 supplied | `error: missing config key GIT_CONFIG_KEY_1` / `fatal: unable to parse command-line config` | 128 |
| `GIT_CONFIG_COUNT=` (empty) with file value present | `file-value` (empty treated as 0, no pairs) | 0 |
| `COUNT=2`, pairs at indexes 0 and 1 | `v0`, `v1` | 0 |
| outside any repository, env pair | `env-value` | 0 |
| `GIT_CONFIG_KEY_0=core.hooksPath GIT_CONFIG_VALUE_0=/attacker/hooks` | `/attacker/hooks` | 0 |
| `KEY_0`/`VALUE_0` set with `COUNT` unset | (no output) | 1 |
| `COUNT=1` with only index 1 supplied | `error: missing config key GIT_CONFIG_KEY_0` | 128 |
| `COUNT=0` with a pair supplied | (no output) | 1 |

Every observed behavior matches the opened paragraph: positive count adds indexed pairs to the process's runtime configuration; pairs are zero-indexed; a missing key or value is an error; empty/count-zero processes no pairs; env pairs override config files but are overridden by explicit `-c`. The motivating example (injected `core.hooksPath`) resolves through `git config` with no config file.

## Verdict

S515's claim — a corrected revision anchor for **runtime Git config injection through environment pairs** — is **supported**: live source, anchor, quote (18 words), revision marker, and byte-identical snapshot all verify, and the documented semantics reproduce on git 2.56.0. No source defect found; only the ASCII-vs-U+2019 apostrophe fidelity note above. The row does not overreach: it claims runtime injection, and neither row nor lesson claims injected pairs beat explicit `-c` or that malformed pairs are ignored.

## Advisory non-author spot-check (advise only — lane-author seat, no judgment)

Spot-checked one admit/reject decision, S515 itself: **ADMIT, tier B, mined** (`corpus/SOURCES.md:268`). Quote ≤25 words (18), location and revision recorded, snapshot exists and is byte-identical to the live page, and the row correctly presents itself as superseding S511's omitted revision marker without rewriting S511. The only observation is the apostrophe normalization. Census flags `S515 duplicate url git-scm.com/docs/git-config across scopes` (`.ufo/waves/round-57/census/start.out:101`, `start.exit=0`) — a W04 warning expected for a correction row that reuses the base page with a distinct fragment, not an error. This is advice to the L1; no admit/reject status was changed.

## Distinct case 54

Independent test and its evidence are filed separately at `.ufo/waves/round-57/SourceAudit/33/evidence.md`; it re-derives the claim from the source paragraph and falsification probes rather than restating the registry row.

## Receipts

All under `.ufo/waves/round-57/SourceAudit/33/receipts/`:
`fetch.status`, `fetch.err` (empty), `live.headers`, `hashes.out`, `quote-check.out`, `runtime-repo.out`, `runtime-edge.out`, `versions.out`.
Scratch `/fast/scratch/hyaku/kama-r57/R57Item33SourceAudit` was copied out first and then removed; the command carried an `EXIT` trap but the harness shell did not fire it, so removal was completed with an explicit `rm -rf` and verified (`test ! -e`). Nothing was written to `/tmp`.

## Tooling

No installs or updates. Used pre-existing `git 2.56.0`, `curl 8.23.0`, `Python 3.14.8` (`receipts/versions.out`). Pacman transactions untouched.

Report: .ufo/waves/round-57/w1/out/R57Item33SourceAudit.md
