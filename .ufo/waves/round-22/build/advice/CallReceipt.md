# CallReceipt — receipt gate as a standalone-JSON consumer of install identity (round 22, C1)

Seat: KamaR22.CallReceipt (scout, read-only). Base `10271460cc575fc2280aa831e442726385fc2319` (lane `HEAD` observed equal). No edits outside this file; no builds/tests/gate runs this wave. Semantic tracing: no `lsp` device available to this seat; all call-site claims below are `rg` text matches over the lane (excluding `.ufo/`) plus direct reads, so absence claims are bounded to that literal search.

## Verdict

The receipt gate `tests/llamacpp-live/check-receipt.py` never calls `install_tree()`. It consumes the receipt JSON only, so the ApiFix change to `tools/kama-llamacpp-live.py:178-202` needs **no gate code migration**. The gate cannot detect a member that a historical producer silently omitted. It MUST NOT be described as doing so. One adjacent gap is optional to tighten, but no seat owns the file (G2 below).

## Observed facts

1. **Producer → receipt.** `install_tree()` (`tools/kama-llamacpp-live.py:178-202`) skips members whose `lstat` or `sha256_file` fails (`:190-199`). On `listdir` failure it returns `({}, None)` (`:184-187`). `main` writes `tree`/`tree_sha` into `receipt['server']` at `:1414`, `:1431-1432`. The initial receipt literal carries `install_tree: {}` and `install_tree_sha256: None` (`:1350`). Only a setup-error receipt keeps those values, and the gate rejects it at `check-receipt.py:307-310`.
2. **Gate tree checks** (`check-receipt.py:386-422`, `validate()`; blame: `b8e485c`/`f1790e2`/`726f737`, unchanged since round 19):
   - the map must be a non-empty dict (`:387-392`);
   - every value must be hex64 (`:394-397`);
   - the map must contain the `realpath` basename (`:399-403`), whose value must equal `server.sha256` (`:404-406`);
   - the digest may be null (`allow_none=True`, `:410-411`). The comment at `:407-408` says it is "null only when the producer could not list the directory";
   - when the digest is hex, it must recompute over the stored map (`:412-415`);
   - the optional pin `--expect-install-tree-sha256` (`:416-422`, CLI `:2351-2352`, wired `:2387`).
3. **What the gate can see of an omission.** It compares the receipt against itself plus caller pins. A receipt whose map lacks member X, with the digest recomputed over the smaller map, passes `:386-415` unchanged. It is caught only in these cases:
   - X is the server basename (`:401-403`);
   - a recorded `install_links` chain ends at X (`link_chain_problem`, `:181-198`, applied `:473-477`). This only works for receipts that carry `install_links`, which earlier receipts lack (`:442`);
   - the caller passes an `--expect-install-tree-sha256` computed independently over the complete directory. A pin copied from the partial receipt itself confirms the partial identity.
4. **Impl-library omission is also invisible.** If `libllama-server-impl.so` is absent from the map, the field↔tree cross-check at `:427-431` is skipped, because it requires the name to be in the tree. `--expect-server-impl-sha256` (`:432-441`) binds `server_impl_sha256`, which the producer hashes separately (`tools/kama-llamacpp-live.py:1420-1423`), not tree membership.
5. **Gate selftest has no omission cell.** The tree mutations are:
   - `install-tree-sha-tampered` (`:1960`);
   - `tree-sha-mismatch-expect` (`:1968`);
   - `tree-empty-map-with-pin` (`:1971`);
   - `tree-sha-absent-expect` (`:1975`, pinned only);
   - `tree-sha-malformed-expect` (`:1978`);
   - `tree-consistent-member-swap` (`:1981`, which adds a member under the pin);
   - `impl-field-tree-mismatch` (`:1987`).

   None removes a member, and none uses a null digest without a pin.
6. **Prior recorded evidence (not rerun).** `.ufo/waves/round-21/falsify/out/C2SetupErrorGrading/gate-runs.txt` records `VALID … complete-null-tree-digest.json exit=0`. That fixture has 51 tree members, `install_tree_sha256: null` and `setup_error: null`, so it is a complete receipt with a null tree digest that the gate accepts unpinned. [INFERENCE] The same lines `:386-415` were in force then (blame above). The gate copy used there is not re-hashed here.
7. **Stored real receipts are all non-null.** Read-only scan of the stored `.ufo/waves/round-{16,17,18,21}` live receipts (13 files: round-16 ×2, round-17 ×3, round-18 ×6, round-21 `runs/{7054dba1,b76727f3}/live-receipt.json`): each has 51 members, a hex `install_tree_sha256` and `setup_error: null`. No round-19 or round-20 live receipt matched the scan globs; that is a scan-scope limit, not a claim that none exist.

## Consumer callsites of install-tree identity (lane, excluding `.ufo/`)

| Callsite | Consumes | Migration for the fail-closed `install_tree` |
|---|---|---|
| `tools/kama-llamacpp-live.py:1414-1419` (`main`) | `install_tree()` return tuple, then `install_links(server_real, tree)` | ApiFix owns it. The existing `except SetupError` path covers the new raise. Keep `install_links` problems for symlinks and non-regular entries (`:213-262`). |
| `tools/kama-llamacpp-live.py:1135-1162` (producer `--selftest`) | `install_tree(server)` on a temporary tree, plus a retarget-invariance check | ApiFix (same file). Check whether the unreadable-member cell near `:1194` hits the new raise before `install_links`. |
| `tests/llamacpp-live/install-links-grid.py:178-183` | `module.install_tree(str(server))` for the frozen and current arms | CallerRepair owns it. Required: the current arm must catch `SetupError('install-tree-unpinnable…')` as a refusal. |
| `tests/llamacpp-live/unpinnable-e2e.py:73` | `producer.install_tree(pristine/llama-server)` on a pristine copy | CallerRepair. On pristine input it is unchanged by construction; a fault there would now raise, not under-hash. |
| `tests/llamacpp-live/check-receipt.py:386-422` | receipt JSON only | No migration required (G1); optional tightening (G2). |
| `tests/llamacpp-live/install-tree-grid.py:124-147` | receipt JSON; swaps digest values on the named `DEFAULT_MEMBERS` (`:35-36`) and recomputes the digest | None. It reports a named member absent from the receipt as `absent` (exit 1, `:141-142`). That is the only lane detector of omission in stored JSON, and it only covers 3 named members. |
| `tools/error-verdict-census.py:228-229` | synthetic receipt `{"server":{"install_tree":{…}}}` passed to the grid | None (fixture only). |
| `tests/llamacpp-live/controls.py:129` | producer run against a staged `srv/` holding only `fake_server.py`; the pid file is created after hashing | None [INFERENCE: no control injects lstat/read faults into `srv/`; `rg` found no `chmod` of `srv` contents except the 0o755 at `:839`]. |

## Gaps and recommendations (findings only)

- **G1 — no claim of historical omission detection.** Round-22 reports, SKILL/SCORECARD rows and lessons MUST NOT say the gate, the tree pin or the grid detects members that earlier producers silently dropped. Correct wording: the producer refuses incomplete identity from now on; stored receipts are trusted only to the extent of an independently computed tree pin. Existing doc rows (`SKILL.md:647`, `:653-654`, `:684`; `corpus/knowledge/llamacpp-loading-lifecycle.md:316-327`, `:343-348`) make no such claim (`rg` for partial/omitted/complete wording returned only the gate comments `:408`, `:456`). `SCORECARD.md:1032` lists "an unreadable-member fail-closed rule for `install_tree` consumers outside the live producer" as frontier. That maps to the CallerRepair callsites, not the gate.
- **G2 — optional gate tightening (no owner assigned; L1 decision).** After the fix, no complete receipt can carry a null `install_tree_sha256`. All 13 stored real receipts are hex (fact 7), and a null digest with an empty map is already rejected (`:390-392`). Changing `:410-411` to `allow_none=False` would turn `complete-null-tree-digest.json` (fact 6) from VALID to INVALID without breaking any scanned historical receipt. The stale comment `:407-408` would be rewritten, and an unpinned `tree-sha-null` mutation added next to `:1975`. This is a gate-side change in a file outside ApiFix, Matrix, CallerRepair and Recipe. Also, `SKILL.md:654` quotes a selftest mutation count, and adding a mutation changes the count.
- **G3 — not closable by the gate.** Omission of a non-basename, non-link-target member (including the impl library, fact 4) is undetectable from the JSON alone. Do not add a heuristic: any expected-member list would be a host-specific pin, which `--expect-install-tree-sha256` already provides.

## Proposed no-harm checks for L1 (not run)

- `python3 tests/llamacpp-live/check-receipt.py --selftest` (exit 0; mutation count unchanged unless G2 lands).
- `python3 tests/llamacpp-live/check-receipt.py .ufo/waves/round-21/runs/7054dba1/live-receipt.json --require-schema v3` with the round-21 recipe pins, including `--expect-install-tree-sha256` (expect `VALID`, exit 0).
- `python3 tests/llamacpp-live/install-tree-grid.py --selftest` (exit 0).

## Owned paths

- Written: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/CallReceipt.md` (this file only).
- Installs: none.
