# K2Selftest — v5 rule → selftest coverage matrix (round 48)

Coverage base: `tools/kama-live-replay.py` `_selftest` (21 cases) and `tools/kama-llamacpp-live.py`
`_provenance_selftest()`. "New case" verdicts are from the runs in `evidence/`:
`replay-asis.out` (current tool + new cases only), `replay-proposed.out` (full proposal),
`live-current-driver.out` (current live module, per-check driver), `live-proposed.out`
(patched live selftest).

## Replay tool (`kama-live-replay.py`)

| # | Rule (refusal token / compare source) | Covered by 21? | New case | Current tool verdict |
|---|---|---|---|---|
| R1 | schema not v4/v5 (`not-a-v4-or-v5-receipt`) | yes (v3-receipt) | — | — |
| R2 | provenance fields missing (`provenance-missing`) | partial (missing-url only; other 4 fields same code path) | — | — |
| R3 | non-64-hex digest (`provenance-bad-digest`) | **no** | `asset-digest-bad-hex`, `model-digest-bad-hex` | PASS (enforced) |
| R4 | prov model sha != receipt model sha | yes | — | — |
| R5 | unsafe member | yes | — | — |
| R6 | commit not 40 hex (`provenance-bad-commit`) | yes (non-hex "abc") | `v5-commit-uppercase-accepted` (valid hex, uppercase) | **FAIL — refused (exit 2, provenance-bad-commit); over-strict for valid uppercase hex** |
| R7 | commit not in `/resolve/<commit>/` path segment | yes (URL layout commit) | `v5-url-commit-query-string` (commit only in query string) | PASS (enforced) |
| R8 | verified block `at != "record"` | partial (None only) | `v5-verified-at-wrong-value`, `v5-verified-empty-block` | PASS (enforced) |
| R9 | URL scheme | yes | — | — |
| R10 | acquire digest mismatch | yes (both assets) | — | — |
| R11 | member-absent after extract | yes | — | — |
| R12 | member digest mismatch | yes | — | — |
| R13 | compare: outcome differs | **no** | `compare-outcome-mismatch` | PASS (enforced) |
| R14 | compare: server.sha256 differs | **no** | `compare-server-sha256-mismatch` | PASS (enforced) |
| R15 | compare: model.sha256 differs | **no** (same code as R14) | (R14 covers the branch) | PASS |
| R16 | compare: original evaluated check missing from rerun (`not-evaluated`) | **no** | `compare-check-not-evaluated-in-rerun` | PASS (enforced) |
| R17 | original has no evaluated check | yes | — | — |
| R18 | projection mismatch | partial (slots via projection-differs, props via compare-stable-differs) | `projection-full-captures-vs-none`, `projection-models-body-unparseable` | PASS (enforced) |
| R19 | v5 rerun itself carries commit+verified | **no — not enforced anywhere** | `v5-rerun-provenance-shape` | **FAIL under current tool (proceeds to compare, exit 1, not refused); PASS with proposed enforcement + stub fix** |
| R20 | live tool exits without writing rerun (`no-rerun-receipt`) | **no** | `live-no-rerun-receipt` | PASS (enforced) |
| R21 | `--compare` CLI: unreadable / malformed JSON / non-object | **no** (selftest calls `compare()` directly) | `compare-cli-unreadable`, `compare-cli-malformed-json`, `compare-cli-non-object` | PASS (enforced) |

## Live tool (`kama-llamacpp-live.py`)

| # | Rule | Covered by `_provenance_selftest()`? | New case/check | Current tool verdict |
|---|---|---|---|---|
| L1 | verify_archive_member: archive digest mismatch | yes | — | — |
| L2 | member absent | yes | — | — |
| L3 | member not a file (dir) | yes | — | — |
| L4 | member digest mismatch | yes | — | — |
| L5 | archive unreadable (missing / corrupt tar) | **no** | missing + corrupt tar checks | PASS (enforced) |
| L6 | PINNED_MODEL_URL: pinned lowercase 40-hex | yes | — | — |
| L7 | PINNED_MODEL_URL: unpinned (main / 7-hex) | yes | — | — |
| L8 | PINNED_MODEL_URL: uppercase 40-hex | **no** | uppercase / mixed-case asserts | **FAIL — regex is `[0-9a-f]{40}` (lowercase-only); valid uppercase hex commit refused** |
| L9 | PINNED_MODEL_URL: trailing query on pinned URL | **no** | `?x=1` assert | PASS (enforced) |
| L10 | commit only in query string | **no** | `main/m.gguf?revision=<commit>` assert | PASS (recognized as unpinned) |
| L11 | parser: four v4 flags together | **no** | 1-of-4 / 3-of-4 | PASS (enforced) |
| L12 | parser: asset/model URL https | **no** | http asset, file:// model | PASS (enforced) |
| L13 | parser: member relative, no `..` | **no** | absolute member, `bin/../` | PASS (enforced) |
| L14 | parser: v5 pinned URL required | **no** | unpinned, query-string commit | PASS (enforced) |
| L15 | parser: 64-hex digest accept+normalize | **no** | uppercase `AB`*32/`EF`*32 | PASS (normalized to lowercase; observed in emitted setup-error receipt) |
| L16 | record-time emit: commit extraction + verified.at=record + archive/member/model hashes | **no** | stub-server emit (evidence/ `live-recordtime-emit-receipt.json`) | PASS (schema v5, commit `c`*40, verified.at=record, all hashes equal) |

## Findings summary

- **F1 (R6/L8, defect candidate):** commit hex is validated lowercase-only in both tools
  (replay `HEX40` at `kama-live-replay.py:65`, live `PINNED_MODEL_URL` at
  `kama-llamacpp-live.py:71`), while the contract says "40-hex". The live tool itself accepts
  uppercase hex for sha256 args and normalizes them (L15), so the commit restriction is an
  asymmetry. A receipt whose model URL/commit uses uppercase hex is refused
  (`provenance-bad-commit` / `must be pinned`).
- **F2 (R19, defect):** replay validates only the ORIGINAL receipt's provenance; a v5 rerun
  missing `provenance.model.commit`/`provenance.verified` is accepted (compare proceeds). The
  selftest's own v5 stub also omits those fields, so no case could catch a live-tool regression
  that drops them. Proposed fix: enforce v5 rerun shape in `replay()` (token
  `v5-rerun-provenance-incomplete`) and make the stub emit complete v5 provenance; with both,
  the full suite passes 36/37 and the new shape case passes.
- **F3 (coverage only):** all other identified rules are enforced correctly by current code;
  the listed new cases pass unchanged. They pin behavior that nothing exercised before.
