# CallSnapshot — historical/frozen `install_tree` consumers under `.ufo/waves`

Seat: KamaR22.CallSnapshot (scout, read-only). Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`, base `master` = `10271460cc575fc2280aa831e442726385fc2319`.
Method: `rg` text search (no LSP server answers these scratch/history scripts; findings are literal, not semantic), plus `git show 10271460:tools/kama-llamacpp-live.py` and targeted reads. No verification runs, no installs.

## Verdict

**No file under `.ufo/waves/round-{16..21}` requires migration.** Every hit is one of: a frozen producer copy, a probe pinned to a past revision (git show / `/tmp` clone), a probe parameterised by `--lane`/argv, recorded output, or a historical recipe/runner. They are do-not-migrate history. Several recorded outputs are direct red-before evidence for C1 and should be cited, not edited.

Owned path written: `.ufo/waves/round-22/build/advice/CallSnapshot.md` (this file only).

## Base behaviour being replaced (observed)

At `10271460:tools/kama-llamacpp-live.py:178-203`, `install_tree` does three things on error. A `listdir` failure returns `(tree, None)` (lines 185-187). An `lstat` failure silently `continue`s (lines 190-193). A `sha256_file` `OSError` silently `continue`s (lines 197-200). The `S_ISREG` skip at lines 194-195 is the intentional symlink/nonregular skip and must stay.

## A. Frozen producer copies (identical silent-skip body; do-not-migrate)

| path | `def install_tree` | `return tree, None` / lstat `continue` / read `continue` |
|---|---|---|
| `.ufo/waves/round-17/frozen/tools_kama-llamacpp-live.py` | 146 | 155 / 161 / 167 |
| `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py` | 178 | 187 / 193 / 199 |
| `.ufo/waves/round-18/build/out/KamaR18.C1LiveTool-2/kama-llamacpp-live.py` (+ `.diff`) | 178 | 187 / 193 / 199 |
| `.ufo/waves/round-21/build/out/LinksPolicyCritic/frozen-producer.py` | 178 | 187 / 193 / 199 |

These are snapshot evidence of earlier rounds. Editing them would falsify history. Matrix's "frozen arm" SHOULD load `git show 10271460:tools/kama-llamacpp-live.py`, not any of these copies, because they are older revisions.

## B. Scripts that call `install_tree()` on a loaded producer

The question is whether a script resolves to the live lane working-tree producer. Only one does, by a hard-coded path.

- `.ufo/waves/round-18/runs/run.py:56-60`. It loads `L/'tools/kama-llamacpp-live.py'` (L = lane root, line 5) and calls `install_tree(server.resolve())` on the real llama-b11755 install. It already treats a missing or None digest as fatal (`SystemExit('install-tree digest unavailable')`, lines 59-60). On a healthy tree the success tuple is unchanged. On a fault it would now raise `SetupError` with a traceback instead of the `SystemExit`. Its exit is still nonzero, so this is a fail-closed change. This is a round-18 runner and is **do-not-migrate**.
- Pinned to a past revision, so immune to the change:
  - `round-21/falsify/out/ConnectorKQ/probe.py:13-14,29,43,57-64` uses git show at `a6617149`.
  - `round-21/falsify/out/C2ClaimCritic/composition-probe.py:26-33,47,55` uses git show at `a6617149`/`7a6bc911`.
  - `round-21/build/out/RevengeInstallTreeIntent/intent_check.py:36-68` uses git show and only hashes the function body.
  - `round-21/build/out/KamaR21.LinksGridReview-6/ast_and_realpath.py:11-18,43-45` uses git show inside a `/tmp` clone.
  - `round-21/build/out/LinksRealReceipt/links-real-receipt.py:34-35,76,84` uses `LANE_REV a29bb84`.
- Load from `/tmp` scratch clones at old revisions, so they do not resolve to the lane:
  - `round-21/falsify/out/C2DigestSentinel/attacks/common.py:15,31`, which `a_producer_names.py:53,69,92,115`, `b_loader.py:67,98`, `d_producer_main.py:80`, `e_extra.py:61`, `f_hwcaps.py:59` and `run_all.sh:19` share.
  - `round-21/falsify/out/C2ProducerReview/probe_links.py:16,101-113,136,209,230` and `landlock_demo.py:15,56,80`.
  - `round-21/build/out/LinksPolicyCritic/probe.py:19,31,51,96-97,212,226,231` and `probe2.py:19,29,44`.
  - `round-21/build/out/LinksDigestEncoding/{probe.py:25,48,72,265; minimal_witness.py:14,28,30; needed_check.py:24,27; proposal.py:28,174}`.
  - `round-21/build/out/LinksGateReview/synthetic_link_checks.py:34,74,98` (`{S}/head`).
- Parameterised by `--lane`/argv/env, so they only reach the live producer if L1 points them there:
  - `round-21/falsify/out/KnowledgeAccuracy/probe.py:28-31,155,170,178,233,240`
  - `round-21/build/out/LinksTreeDeterminism/probe.py:30,42,98,125,301`
  - `round-21/build/out/KamaR21.LinksProducerReview-6/probe.py:17,21,93,115,143-184` (env `LANE`)
  - `round-21/build/out/LinksLoaderProof/digests.py:14-18`
  - `round-21/build/out/LinksProducerSelftestCase/probe_calls.py:15-16`
  - `round-21/falsify/out/KamaR21.C2GateReview/{attack_gate.py:22,48,342,379; probe_extra.py:19,30}`
- [INFERENCE] If someone reran these against the post-C1 producer, the fault-injection sections that expect a partial or empty return would now raise an uncaught `SetupError`. The affected sections are `KnowledgeAccuracy/probe.py:168-180`, `LinksPolicyCritic/probe.py:231`, `LinksProducerReview-6/probe.py:115` (E2b), `C2ProducerReview/probe_links.py:229-231`, `C2DigestSentinel/d_producer_main.py:90-104` and `landlock_demo.py:80`. That crash is the intended new contract. It is not a regression to repair, because these are one-shot round-21 probes with recorded outputs.
- Calls `install_tree()` on a self-defined or reimplemented digest only: `round-20/build/out/FreshnessS039/freshness_check.py:52-55,104-116,178-182`. This one is **already fail-closed**: its own `installed_members` lets `OSError` propagate into `c.error(...)`. It is not a silent-skip instance.
- Mention `install_tree` only as receipt JSON keys or mutate receipts, with no producer call. All are no-op for C1:
  - `round-20/build/out/{GridKillFix/install-tree-grid.py, MutGridRedBefore/*.py, ConnectTameshi/xlane-cells.py, SrcPySubprocess-2/probe-signal-returncode.py, CensusHarness/error-verdict-census.py}`
  - `round-18/build/out/C1Gate-2/check-receipt.py`
  - `round-17,18/frozen/tests_llamacpp-live_check-receipt.py`
  - `round-18/{build/out/C1Controls-2,frozen}/…controls.py` (docstring only)
  - `round-21/falsify/out/C2SetupErrorGrading/build_fixtures.py:63-64,168`

## C. Recorded red-before evidence (cite in mistake mining; do not edit)

These outputs show the base silently returning a comparable partial or null identity:
- `round-21/falsify/out/ConnectorKQ/results.json:3-11`: at `a6617149`, a read fault on `aux.so` gives `partial_members ["llama-server"]` and `partial_digest_present: true`, while `install_links` reports no problem.
- `round-21/falsify/out/KnowledgeAccuracy/probe-output.txt:28`: injected EIO on `libllama.so.0.7.1` drops the member and the tree sha changes, while `install_links problems []`. A partial digest therefore escapes even through the round-21 links guard.
- `round-21/falsify/out/C2ProducerReview/probe-user.json:~110-150` (`c_silent_drop_eio`, `c_silent_drop_unlink_race`, plus the probe-root twin): `recorded_tree_names ["llama-server"]` against `full_tree_names ["libextra.so","llama-server"]`, with the same 64-hex digest `391ceef5…` and links problems `[]`.
- `round-21/falsify/out/C2DigestSentinel/results/d_producer_main.txt:6-15`: in D1 (EIO on an unlinked member), `main()` proceeds to launch with a two-member tree. The gate without a pin accepts it (`exit=0`) and only an honest tree pin catches it (`exit=1`). D2 is the lstat→open TOCTOU variant with the same result.
- `round-21/build/out/KamaR21.LinksProducerReview-6/probe-transcript.txt:14` (`E2b install_tree -> ({}, None)`) and `round-21/build/out/LinksPolicyCritic/probe-output.txt:66` (`install_tree missing dir: ({}, None)`) show the `listdir` null-digest path.

## D. Recipes and runners (history; the new round-22 recipe is Recipe's)

- `round-20/run.py:25` and `round-21/run.py:25` already pin `refs/heads/master` and refuse a dirty tree (line 26). Recipe can reuse this as is.
- `round-21/recipe.json` and `round-21/recipe-final.json` (lines 126/136, 166, 249-252, 369-372) invoke the live `tools/kama-llamacpp-live.py --selftest`, the live receipt, `install-links-grid.py`, `install-tree-grid.py --selftest` and `unpinnable-e2e.py`. These are recorded expectations for round-21 and are **do-not-migrate**. Any expected-exit change belongs in the new `round-22/recipe.json`.
- `round-21/recipe.json:171-210` grades the legacy receipts `.ufo/waves/round-18/live-recovery/receipt-{1,2,3}.json` with the gate. These receipts are frozen data. [INFERENCE] They cannot record whether their `install_tree` was complete: the base skipped errors silently, so the receipt carries no completeness marker. C1 cannot retroactively refuse them, and the gate's legacy semantics for them should be preserved (CallerRepair's scope).

## Cross-surface notes (outside `.ufo`, for L1)

- Current consumers that read `.ufo/waves` files: `tools/error-verdict-census.py:32` (round-18 `survivors.py`, unrelated to `install_tree`) and `tests/ollama-corpus-guard/check.py:64`. Nothing under `tests/llamacpp-live/` references `.ufo` paths (`rg '\.ufo' tests tools`).
- **Contract observation.** My first `git status --short` showed only `?? .ufo/waves/round-22/`. A later `git status --porcelain -- tools tests` showed ` M tools/kama-llamacpp-live.py` and ` M tests/llamacpp-live/install-links-grid.py` in the lane checkout itself, with HEAD still `10271460`. The working-tree `install_tree` (lines 178-203) now raises `SetupError('install-tree-unpinnable:{listdir|lstat:<name>|read:<name>}')`. Seats are forbidden to mutate the lane checkout, so L1 should check who wrote these edits before integrating. Base-relative statements above use the `git show 10271460` blob, not the working tree.

## Proposed no-harm checks (L1, post-integration; not run)

- `git -C <lane> diff --stat 10271460 -- .ufo/waves/round-1[6-9] .ufo/waves/round-2[01]` should be empty. This proves no history was migrated.
- `rg -n 'tools/kama-llamacpp-live' <lane>/.ufo/waves/round-22/recipe.json` should show that the round-22 recipe, not the round-21 recipes, carries any new expected exits.

Tool installs: none.
