# BadNameControl — C1 discriminating case design: control-character basename stays `install_links` policy

Scope: design only, no edits/runs. Owned path: this file. Lane root `/home/vgpnk/Projects/shokunin/kama-shokunin`; frozen blob `10271460cc575fc2280aa831e442726385fc2319`. Lane checkout is dirty and `tools/kama-llamacpp-live.py` drifted between my two reads (raise sites gained `:{exc}` suffixes); line refs marked WT are working-tree at observation time.

## The case

`control:name-tab` — a **real** regular member `lib\tx.so` (TAB, one byte < 0x20) in an otherwise pristine fixture, **zero patches**. The row asserts a *preserved policy boundary*, not a fault: the control-name gate lives in `install_links`, and C1's fail-closed `install_tree` must neither adopt it nor silently drop the member.

- `install_tree` returns `(tree, tree_sha)` with `lib\tx.so` **in** `tree` and the digest matching the oracle that includes it — identical on frozen and current (both hash control-named regulars: frozen skips only on OSError, no name check anywhere in `install_tree`, frozen 178–202; WT 183–203 likewise has no name predicate).
- `install_links(server, tree)` problems is **exactly** `["'lib\\tx.so':control-character-in-name"]` — the ord-check at WT 238–240 / frozen 237–240 fires before `lstat` (WT 246), before `glibc-hwcaps` is irrelevant here, and before the `not-hashed` check (WT 259–260), so the token is stable whether or not the member is in `tree`.
- Consumer consequence (unchanged in both arms): `install_links(server_real, tree)` reports the problem → `SetupError('install-tree-unpinnable:' + joined problems)` at WT 1418–1420 / frozen 1417–1419 → exit 2, no receipt. Policy location and reason token preserved.

### Expected class (per arm)

**Green on BOTH arms — a policy-preservation control, not a red-before row.** Frozen has no name predicate in `install_tree`, so frozen *returns*; expecting `refused` on frozen would be a false violation (FP-1). The row discriminates *wrong fixes*, not frozen-vs-current:

- **Mutant A** — `install_tree` refuses/skips-with-error on `ord < 0x20` (over-broad fail-closed, policy location moved): `status != 'returned'` → caught by map/digest assertion alone. Consumer still exits 2 but with a different reason token (`install-tree-unpinnable:lstat|read:…` vs `…:'lib\tx.so':control-character-in-name`) — indistinguishable at exit-code level, so function-level observation is mandatory (FP-2).
- **Mutant B** — `install_tree` silently `continue`s on control names: member absent from `tree`, digest is a *comparable partial digest* — the exact C1 harm relocated from fault axis to name axis, and the links token still reads `control-character-in-name` (ord-check precedes `not-hashed`). Caught **only** by asserting member-presence + oracle digest, never by the links token alone (FP-3).
- **Mutant D** — ord-check deleted or narrowed (e.g. to `\n` only): `install_links` reports no problem → consumer ships a receipt whose `install_tree_sha256` preimage is ambiguous (`'name sha\n'` lines; frozen comment at 238–239 states this; `links_digest` exists precisely because JSON is injective — WT 206–211). `check-receipt.py` validates `install_links` keys for control chars (462–468) but has **no** plain-basename rule for `install_tree` keys (386–431) — the gate would accept the receipt. Caught **only** by exact `problems` list equality (FP-4).

### Smallest injection target

**A fixture file, not a mock.** The smallest injection is `Path(folder, 'lib\tx.so').write_bytes(b'…')` — no `unittest.mock` at all. Fault injection must be `None`/absent for this row: injecting a read/lstat fault on the control member shifts the refusal reason from `control-character-in-name` to `install-tree-unpinnable:{site}:…` (legitimate fail-closed precedence, but the row then tests the fault axis, not the name axis). Conversely, mocking `listdir` to *return* a phantom `lib\tx.so` never created on disk makes `os.lstat` raise ENOENT → current arm refuses as `lstat` fault → tests lstat coverage, not name policy (FP-5).

Why `\t`: producer selftest already pins `lib\nx.so` at `install_links` level only (WT 1164–1167, frozen 1165–1168) and `check-receipt.py` bad-key mutants use `lib\nx.so` (2012–2015). TAB is the smallest *unpinned* member of the `ord < 0x20` family — it catches a mutant special-casing `\n` literally; repr is deterministic ASCII (`"'lib\\tx.so'"`). `\x01`/`\r` are equivalent alternates.

### Positive control

The row carries its own positive control — it *is* the clean-tree control for the name axis: assert `status == 'returned'`, `result == (oracle_tree, oracle_digest)`, and exact problems list, on both arms. In the lane-draft grid the existing `regular` control (CONTROLS, lane #172E:39) is the sibling complete-map control; in the sandbox draft `control:complete-map-digest` (#6CCA:62) is it. Additionally, the links-side digest stays meaningful: `links` map unaffected (member is regular, not a symlink), `links_sha` equals the no-control-member fixture's value if fixture otherwise identical — optional secondary pin.

### Oracle construction (two integration shapes)

- **Lane draft (`tests/llamacpp-live/install-io-grid.py` #172E, 281 lines — the newer copy at lane root):** add e.g. `'control-name'` to `CONTROLS` (39–40); in the controls branch (157–190) write `body['lib\tx.so'] = b'…'` before fixture creation — `expected_tree(body)` (55–58) then derives both map and digest oracles automatically, including correct sort position (`'\t'`(0x09) < `'l'` → sorts first). Extend `good` (186–188) with `result.get('paired_problems') == ["'lib\\tx.so':control-character-in-name"]` — `observe()` already calls `install_links` when status is `returned` (130–132). ~5 lines.
- **Sandbox draft (`build/sandboxes/Matrix/tests/llamacpp-live/install-io-grid.py` #6CCA, 318 lines — authoritative per StatGone):** `_observe` (132–140) never calls `install_links`; `_control_row` (208–225) asserts only `result == (EXPECTED_TREE, EXPECTED_TREE_SHA256)` via `complete` (217). Integration needs: (a) a new CONTROL_ID e.g. `control:control-name-policy`; (b) per-control expected-map pins — extend `MEMBER_BYTES`-style literals with a second pinned pair `EXPECTED_TREE_CTRL`/`EXPECTED_TREE_CTRL_SHA256` (author computes literals once, pins them; `lib\tx.so` sorts first: compare position 3 `'\t'` vs `'l'`/`'a'`); (c) a guarded paired call — `_load_module` only requires `install_tree`+`SetupError` (104–106), so call `module.install_links(server, tree)` under `callable(getattr(module, 'install_links', None))` or hard-require it (both real arms define it; a minimal selftest fixture producer may not → guard, record `links_token_observed: false`, do not crash into exit-2 territory). (d) keep the row OUT of `fault_counts`/`incomplete_identity_escapes` (232–241) — frozen cannot refuse names, so a fault-class row would break `baseline_red` (246) or inflate `property_pass` (245).

### False-positive risks

- **FP-1 (expected-class):** asserting `refused`/`SetupError` for this row is wrong on *both* arms — no I/O fault exists, so `install_tree` must return. A refused-expecting row goes red on the honest current producer for the wrong axis and would *pass* Mutant A. Class = control, expected = `returned`.
- **FP-2 (observation level):** consumer-level/e2e assertion alone cannot discriminate Mutant A — exit 2 with `install-tree-unpinnable:…` either way; only the reason *string* differs. Assert at `install_tree` return + `install_links` problems.
- **FP-3 (token-only assertion):** `problems == [control-character-in-name]` alone misses Mutant B — the ord-check precedes `not-hashed` (WT 238 vs 259–260), so the token survives a silent member-drop. Assert `lib\tx.so in tree` AND digest equality.
- **FP-4 (map-only assertion):** map/digest equality alone misses Mutant D — the receipt validator never checks `install_tree` key plainness (check-receipt 386–431 vs 462–468), so a producer that drops the ord-check ships ambiguous-preimage receipts cleanly. Exact problems-list equality is mandatory; use `==`, not `in`/contains (a mutant that *over*-flags ordinary members appends extra problems — `in` would mask it).
- **FP-5 (mock substitution):** never mock `listdir` to fabricate the name (→ ENOENT lstat, tests fault axis); never inject a fault on the member (→ refusal token changes legitimately). Real file, zero patches.
- **FP-6 (character selection):** `'\x00'` uncreatable (POSIX); `' '` 0x20, `'\x7f'` DEL, C1 U+0080–U+009F are all *outside* `ord < 0x20` — asserting control-char policy on them asserts a non-policy (real false positive). Surrogateescape names belong to UnicodeNames' encode-boundary row (`.encode()` at WT 201–202 / frozen 200–202), do not conflate. `'/'` impossible in a basename.
- **FP-7 (oracle semantics):** assert digest **equality** to the oracle, never distinctness/injectivity — the `'name sha\n'` preimage is *intentionally* ambiguous for control names; that ambiguity is the reason `install_links` refuses them. Asserting `digest != other_digest` marks the honest producer red.
- **FP-8 (repr pinning):** pin the literal `"'lib\\tx.so':control-character-in-name"`; single control member keeps the problems list single-element so sort order is irrelevant. Multiple control names would make ordering load-bearing — don't.
- **FP-9 (row accounting):** row must not enter `refused`/`escaped`/`error` fault counters (sandbox 232–234, 245–246; lane `kind='fault'` branch 155–156) — frozen-arm refused-count semantics and `baseline_red` break otherwise.
- **FP-10 (module gate):** sandbox `_load_module` (104–106) doesn't require `install_links`; guard the paired call or extend the gate, else selftest fixture producers lacking it produce `error` rows misclassified as violations (cross-ref StatGone FP-1 for the sandbox draft's exact-`error_code` match issue at #6CCA:137 — WT codes are `install-tree-unpinnable:{site}[:{name}]:{exc}`, prefixed, not bare).

## Source line references

- **Frozen blob `10271460`**: `install_tree` 178–202 (listdir→`({},None)` 184–187; lstat skip 190–193; read skip 196–199; ambiguous preimage 200–202). `install_links` 213–262 (own listdir 231–234; **ord-check 237–240**; lstat 245; `not-hashed` 258–259). Consumer 1414–1419. Selftest `lib\nx.so` pin 1164–1168.
- **Current WT** (`#AF80`, drifted): `install_tree` 178–203 — raises `install-tree-unpinnable:listdir|lstat|read…` at 188/194/200; **no name predicate** (verified). `install_links` 214–263 — **ord-check 238–240**, `glibc-hwcaps` 242–244, lstat 246, `not-hashed` 259–260. `links_digest` JSON-injective 206–211. Consumer: `install_links(server_real, tree)` 1416–1417, `SetupError` on problems 1418–1420; `server` receipt fields 1432–1437. `SetupError` 154–159; selftest control pin WT 1164–1167 (`install_links`-only, does NOT cover `install_tree` inclusion — my row fills that gap).
- **Consumers**: `install-links-grid.py` `identity()` ~177–186 (WT, SetupError-adapted by CallerRepair); `unpinnable-e2e.py` pristine `install_tree` call ~73–76 (WT); `check-receipt.py` links-key plainness 462–468, **no tree-key plainness rule** 386–431.
- **Grids**: sandbox #6CCA `FAULT_CASES` 42–59, `CONTROL_IDS` 61–65, `_make_fixture` 110–119, `_observe` 132–140, `_control_row`+`complete` 208–225, counters/`property_pass`/`baseline_red` 232–246, pins 29–37. Lane #172E `FAULTS` 28–35, `CONTROLS` 39–40, `expected_tree` 55–58, `observe`+`paired_problems` 61–133 (paired at 130–132), controls branch 157–190.

## Complementary coverage (not this row's job, noted for CallerRepair/L1)

`unpinnable-e2e.py` could carry an end-to-end fixture row asserting the consumer `SetupError` reason contains `control-character-in-name` — the receipt-level proof the reason path is preserved. Not a substitute for the function-level row (FP-2).

## Owned paths

- This report only: `.ufo/waves/round-22/build/advice/BadNameControl.md` (absolute: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-22/build/advice/BadNameControl.md`). No production/test files edited; no commands run.
