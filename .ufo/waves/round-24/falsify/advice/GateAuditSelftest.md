# GateAuditSelftest — round-24 falsification (fresh), commit 2e254a1763a9c08aa07fc53081287f506c447d84

Role: leaf member, single bounded check, read-only production.
Target: `python3 tools/report-landing-audit.py --selftest` in a pinned clone.
Expected (as assigned): 62 cases, 0 failed; actual CLI exit must be verified.

## Verdict

**HOLDS.** The pinned selftest expectation reproduces exactly: `selftest cases=62 failed=0`, CLI exit **0**.
No falsification of the selftest contract was found. Nothing here upgrades, weakens, or relabels the
withdrawn unknown-from-metadata expectation (that stays withdrawn/not-achieved, per
`oracle-amendment-1.json`); this check only covers the tool's own self-test harness at this revision.

## Snapshot / provenance

| item | value | how observed |
|---|---|---|
| pinned revision | `2e254a1763a9c08aa07fc53081287f506c447d84` | `git rev-parse HEAD` in scratch clone, detached |
| subject | `round-24: land completed 64-seat build evidence and explicitly carry residual closure debt` | `git checkout --detach` output |
| scratch clone | `/fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/repo` | `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin repo` |
| tool blob sha256 | `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220` | `git show <rev>:tools/report-landing-audit.py \| sha256sum` — matches the round-24 contract's "source tool ea51bc35…" |
| worktree copy sha256 | identical to the above | `sha256sum tools/report-landing-audit.py` (scratch worktree == pinned blob, no drift) |
| host python | 3.14.8 | `python3 --version` |
| host git | 2.56.0 | `git --version` (satisfies the tool's documented `git >= 2.45`, tool header line 55) |
| TMPDIR | `/fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/tmp` | exported per subprocess; verified honored (see below) |

No installs, upgrades, or configuration mutations were performed; no pacman/uv/cargo/npm transaction
occurred, so there is no tool/channel/reason row to record. Python 3.14.8 and git 2.56.0 were
pre-existing host interpreters.

## Exact commands and exits

All commands ran with `cwd` inside the scratch clone and `TMPDIR` exported to the lane's own scratch.
No other suite, no network, no transport/execution payload.

1. Primary run (module form, as assigned):

```
cd /fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/repo
export TMPDIR=/fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/tmp
python3 tools/report-landing-audit.py --selftest
```

- exit **0**
- last line: `selftest cases=62 failed=0`
- 62 `ok <name>` lines, 0 `FAIL` lines.

2. Executable form (the actual CLI entrypoint, shebang `#!/usr/bin/env python3`):

```
./tools/report-landing-audit.py --selftest
```

- exit **0**, last line `selftest cases=62 failed=0`.

3. Determinism repeat (run2) and re-run (run3):

```
python3 tools/report-landing-audit.py --selftest > run3.txt 2>&1   # exit 0
diff run2.txt run3.txt   # -> IDENTICAL_OUTPUT ; 63 lines each (62 ok + 1 summary)
```

Byte-identical stdout across two independent runs (62 case lines + summary line).

4. Negative control — proves the exit code is genuinely coupled to selftest failures and is not a
   hardcoded 0. Performed on a **scratch copy only**
   (`/fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/mutated-audit.py`), never on production:

```
cp repo/tools/report-landing-audit.py mutated-audit.py
# edit mutated-audit.py only: inside check(), append one always-false case
python3 mutated-audit.py --selftest
```

- exit **1**
- last line: `selftest cases=124 failed=62`, 62 `FAIL` lines (one forced per original case).

This is the falsification-critical step: a pristine run's exit 0 is therefore meaningful, not an
artifact of an unconditional success path.

## Finding / token pairs (case names, pinned revision)

All 62 case names observed `ok`. The subset that carries the amended local-object contract (from
`oracle-amendment-1.json` prospective expectations) and its observed pairing:

| case name | observed |
|---|---|
| `promisor-metadata-keeps-the-local-verdict` | ok |
| `promisor-remote-is-never-contacted` | ok |
| `unrelated-missing-object-does-not-block` | ok |
| `citation-of-a-missing-object-is-unknown` | ok |
| `errata-cannot-rescue-unavailable-content` | ok |
| `errata-corrects-an-ordinary-absent-citation` | ok |
| `known-tag-with-unavailable-target-is-unknown` | ok |
| `wrongtype-citation-is-a-failed-finding` | ok |
| `blob-hole-is-not-an-opaque-hole` | ok |
| `missing-tree-is-an-opaque-hole` | ok |
| `unused-tree-hole-does-not-block-resolved-citations` | ok |
| `opaque-hole-makes-an-unresolved-token-unknown` | ok |
| `inherited-GIT_DIR-untouched` | ok |

Full list (62/62 `ok`), in tool emission order:

```
raw-fails, mashup-detected, checkpoint-without-colon-omission-detected, bad-abbrev-detected,
exact-defect-set, subject-without-space-required, boundary-commit-required-not-post,
first-add-cutoff-not-readd, author-exact-other-round-and-prefix-ignored,
author-time-cutoff-survives-rebase, post-report-excluded, token-bounds, heading-anchor,
hex-words-not-citations, absent-source-registry-is-no-exemption,
curated-full-source-url-accepted, census-normalized-source-url-accepted,
bare-copy-of-curated-hash-remains-unresolved, unregistered-source-url-remains-unresolved,
malformed-source-row-is-not-an-exemption, leads-url-is-not-a-registry-exemption,
census-url-left-boundary, census-url-right-boundary,
scheme-stripped-url-not-matched-inside-http,
full-source-url-not-matched-inside-another-url, worktree-source-row-does-not-authorize,
landed-source-url-keeps-both-hash-checks,
landed-heading-source-url-keeps-full-hash-check, ambiguous-prefix-is-ambiguous,
errata-clean, unmatched-errata-fails, unselected-round-row-ignored, round-must-equal,
kind-must-equal, token-must-equal, invalid-correction-fails, blob-is-not-a-correction,
omitted-correction-must-be-the-commit, malformed-errata-is-error, draft-uses-fleet-cutoff,
missing-section-fails, uncommitted-draft-uses-now, missing-report-is-error,
committed-report-bytes-not-worktree, reversed-range-is-error, empty-report-path-is-error,
irregular-report-is-error, unusable-git-is-error, open-range-finds-reports,
wrongtype-citation-is-a-failed-finding, promisor-metadata-keeps-the-local-verdict,
promisor-remote-is-never-contacted, unrelated-missing-object-does-not-block,
citation-of-a-missing-object-is-unknown, errata-cannot-rescue-unavailable-content,
errata-corrects-an-ordinary-absent-citation, known-tag-with-unavailable-target-is-unknown,
blob-hole-is-not-an-opaque-hole, missing-tree-is-an-opaque-hole,
unused-tree-hole-does-not-block-resolved-citations,
opaque-hole-makes-an-unresolved-token-unknown, inherited-GIT_DIR-untouched
```

Count independently re-derived from the case-name list above: **62**, matching the tool's own
`cases=62` counter and the assigned expectation of 62.

## Observed vs inferred

Observed (directly measured):
- 62 cases / 0 failed / exit 0, on three separate invocations (module form ×2 identical, shebang ×1).
- Exit 1 / `failed=62` on the forced-negative-control copy → exit code is coupled to failures.
- Scratch clone is a detached checkout of the pinned revision; the tool file's worktree bytes equal
  the pinned blob bytes (`ea51bc35…`), so the measured code is the committed code.
- `TMPDIR` is honored by the tool's storage mechanism: the tool uses
  `tempfile.TemporaryDirectory(prefix="report-landing-selftest-")`; with `TMPDIR` exported, an
  equivalent probe created `/fast/scratch/.../tmp/report-landing-selftest-pwqa4_4y` and reported
  `under TMPDIR: True`. After each run the TMPDIR was empty (no leftover fixtures).
- No network/transport surface in the tool: the only `http(s)://` occurrences are string literals
  inside test fixtures (`github.com/ggml-org/llama.cpp/...`, `other.example/...`); no `urlopen`,
  `socket`, `curl`, `wget`.
- Production tree unmodified: `git diff --stat HEAD` in production is empty; `git status --porcelain`
  shows only the pre-existing untracked wave workspace `?? .ufo/waves/round-24/falsify/`.
- Production `lane production/.jj` untouched: `.jj/repo/index` mtime `2026-10-20 11:16:57 -0300`,
  `.jj/repo/op_store` `2026-10-20 11:16:57 -0300` — both predate this session's runs
  (2026-10-21 16:46–16:48 -0300). The scratch clone was created with `--no-hardlinks`, so it shares
  no object storage with production.
- The selftest builds every repository it touches under its own `TemporaryDirectory`; the only
  `kama-shokunin` occurrences in the tool are author-name strings in fixtures — no production path,
  fleet path, sibling lane, operator config, routing or service reference exists in the code path.

Inferred (not directly measured here):
- That the `cases=62` set is *semantically* the one the round-24 amendment intends. The mapping
  table above shows the 13 amended-contract cases are present and green, but semantic adequacy of
  each assertion was not re-derived from the oracle; that is L1's/source-census ownership.
- That the inherited `git >= 2.45` prerequisite (tool header line 55) holds on every target host.
  Verified only on this host (git 2.56.0). The prerequisite remains open at L0 and is **not**
  closed by this report.
- That no other entry point of the tool (non-`--selftest` modes, `--json`, `--rounds`) is affected
  by the same code path. Out of scope for this assigned check; no other suite was run.

## Unverified / out-of-scope

- The preregistered grid `python3 tests/report-audit/promisor-grid.py --arm both --json`
  (preregistration.json `measurement`) was **not** run — it is a different measurement, outside this
  lane's single bounded check.
- Historical r23 parity and mutation sensitivity were **not** run.
- Original (un-amended) unknown-from-metadata expectation remains **withdrawn/not-achieved**; this
  report does not count it as passed and makes no claim about it.
- No source bug found; no production edit proposed or made. The only edit performed anywhere was to a
  disposable scratch copy (`mutated-audit.py`) used for the negative control.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/advice/GateAuditSelftest.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateAuditSelftest/selftest-run3.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateAuditSelftest/negative-control.txt`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-24/falsify/out/GateAuditSelftest/mutated-audit.py.scratch-copy`

Scratch (not under the repo): `/fast/scratch/hyaku/kama-r24/falsify/GateAuditSelftest/` —
clone `repo/`, `tmp/` (TMPDIR), `run2.txt`, `run3.txt`, `negctl.txt`, `mutated-audit.py`.

## Addendum — lazy-fetch fixture hazard (cross-check with KamaR23-2.CaseFleetBlobless)

A sibling lane reported that a blobless clone whose `remote.origin.url` still points at a reachable
local `file://` origin can be silently re-hydrated by any git probe issued **without**
`--no-lazy-fetch`, turning the intended premise into a false "clean" exit 0 instead of exit 2.
This lane's measurement was checked against that hazard and is immune; evidence:

- The tool itself cannot lazy-fetch, at this revision: `tools/report-landing-audit.py` has exactly
  one git subprocess site (line 162, `subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args], ...)`)
  and `GIT_ISOLATION` (line 138) always includes `--no-lazy-fetch` and `--no-replace-objects`.
  Every git call — including `lookup()`'s `cat-file --batch-check` — passes through that site, so the
  isolation is unconditional. The green selftest case `promisor-remote-is-never-contacted` covers this.
- My scratch clone has the hazardous *shape* (reachable local origin) but is complete, so there was
  nothing to materialise:
  - `remote.origin.url = /home/vgpnk/Projects/shokunin/kama-shokunin` (reachable local origin)
  - `git config --get-regexp 'promisor|partialclone'` → no output (no promisor/partialclone config)
  - `git --no-lazy-fetch rev-list --objects --all --missing=print | grep -c '?'` → **0** (zero missing objects)
  - `.git/objects/info/alternates` → absent (`--no-hardlinks`, no shared object store with production)
  - no `.promisor` packs
- The one manual object probe I ran used `--no-lazy-fetch`.

Consequence for this report: the 62/0 selftest result cannot have been produced by a re-hydrated
fixture, because the measured clone had no missing objects and the tool's own probes are
unconditionally `--no-lazy-fetch`. No source defect was found in response to the hazard; nothing was
edited (the scratch `mutated-audit.py` copy remains the only edit made anywhere).

Note relayed to the sibling lane (their A/B, not this lane's scope): a "blob materialised by one
stray probe" control is only valid if the materialisation is itself recorded (object present in the
clone afterwards) — a stray fetch against a reachable origin may leave the clone no longer
blobless, so the two arms must be provably distinct repositories.

## Report trailer

Report: .ufo/waves/round-24/falsify/advice/GateAuditSelftest.md
