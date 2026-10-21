# CallLinks — install_links callers and tree-membership expectation (round 22, C1)

Seat: KamaR22.CallLinks (scout, read-only). Lane `/home/vgpnk/Projects/shokunin/kama-shokunin`,
HEAD = master = `10271460cc575fc2280aa831e442726385fc2319` (observed `git rev-parse HEAD master`).
Search: `git grep -n -E '\binstall_links\b|\binstall_tree\b|install_tree\(|install_links\('
HEAD -- . ':!.ufo'` (tracked source, all hits read), plus `rg` over `.ufo/**/*.py` for historical
callers. Text search only (Python; no LSP server queried) — callsites below are literal
call expressions, each read in context. No installs, no runs, no edits outside this file.

## Contract under change (observed)

- `install_tree` `tools/kama-llamacpp-live.py:178-202`: `listdir` OSError → `return {}, None`
  (:185-187); `lstat` OSError → `continue` (:190-193); `sha256_file` OSError → `continue`
  (:196-199). Success: `(tree, combined)` with `combined = sha256(''.join(f'{n} {tree[n]}\n'))`.
- `install_links(server_real, tree=None)` :213-262 independently re-lists the directory.
  With `tree` given, a regular member missing from `tree` → `'{name}:not-hashed'` (:258-259);
  unreadable via `os.access` → `'{name}:unreadable'` (:256-257, checked first);
  listdir failure → `['listdir:<strerror>']` (:233-234).
- `SetupError(code)` :154-158; caught once in `main` :1603 → `receipt['setup_error'] = exc.code`,
  exit 2.

So at base, the **only** thing keeping a partial `install_tree` out of a receipt is the
producer's second scan via `install_links(server_real, tree)`. Any caller of `install_tree`
that does not pass its map to `install_links` and refuse on problems gets a silently partial
digest.

## Callsites (code that calls the functions)

| # | Path:line | Calls | Passes `tree` to install_links? | Migration |
|---|---|---|---|---|
| P1 | `tools/kama-llamacpp-live.py:1414-1419` (`main`) | `install_tree(server_real)` then `install_links(server_real, tree)`; problems → `SetupError('install-tree-unpinnable:' + ';'.join(problems[:8]))` | yes | **No structural migration**: both calls sit inside the `try` at :1391, so a `SetupError` from `install_tree` reaches :1603 the same way. Reason text changes for the failures `install_tree` now catches first (see R1). |
| P2 | `tools/kama-llamacpp-live.py:1135`, `:1157` (`_install_identity_selftest`) | `install_tree(server)` on clean stub dirs | no (`:1136` calls `install_links(server)`) | No: every `install_tree` call is on a fully readable tree. |
| P3 | same selftest, `:1165`, `:1169`, `:1175`, `:1180`, `:1184`, `:1189`, `:1194` | `install_links(server)` / `install_links(server, partial)` alone | `:1189` passes a synthetic `partial` map | No: `install_tree` is never called on these mutated dirs. `:1191-1198` (chmod 0 → `:unreadable`) is where ApiFix should **add** an assertion that `install_tree(server)` raises `SetupError` (guarded by the same `os.access` check, so root/ACL hosts don't become flaky). |
| G1 | `tests/llamacpp-live/install-links-grid.py:177-184` (`identity`), used at `:215`, `:227`, `:232` | `module.install_tree(str(server))` then (current arm) `module.install_links(str(server), tree)` | yes (current arm) | **REQUIRED** (owner CallerRepair). Cell `regular-unreadable` `:169-170` (`os.chmod(d / regular[-1], 0)`) makes the current arm's `install_tree` raise. `identity` doesn't catch it, `run` doesn't, and `selftest` only catches `EvalError` (`:312-317`). `main`'s `except Exception` (:389-395) then returns **2** for `--arm current`, `--arm both` and `--selftest` (the synthetic selftest tree uses the same `build_cells`, so `regular[-1]` = `llama-server` is chmod 0). This applies to a non-root runner; as root `open` succeeds, nothing raises, and the old path stays. |
| G2 | `tests/llamacpp-live/unpinnable-e2e.py:73-75` (pristine scan) | `producer.install_tree(...)` then `producer.install_links(..., tree)[2]` | yes | **REQUIRED, small** (owner CallerRepair). If the pristine copy can't be read, the new `SetupError` isn't in the caught tuple `(OSError, RuntimeError, ValueError, subprocess.TimeoutExpired)` (:106). The resulting uncaught traceback exits **1**, which is this script's "case not refused" verdict code, so a could-not-evaluate gets mislabelled as a verdict. Catch `producer.SetupError` and return 2. Subprocess cases `:60-100` are unaffected: hwcaps dir/symlink and the dangling soname all `lstat` cleanly, so `install_tree` doesn't raise there. They keep reaching `install_links`, and the producer still emits `install-tree-unpinnable:...`. |

Gate / fixtures that consume the **receipt field**, not the function:

| # | Path:line | Use | Migration |
|---|---|---|---|
| R-gate | `tests/llamacpp-live/check-receipt.py:181-198` `link_chain_problem` | chain must end at a key of `install_tree` | No. This is the membership expectation, and a complete tree satisfies it by construction. |
| R-gate | `check-receipt.py:386-415` | rejects missing/empty tree (:388-392), recomputes digest when hex (:412-415); `install_tree_sha256` `allow_none=True` (:410-411) | **Comment stale; optional tightening** (no seat owns the gate this round, so L1 decides). The comment at :407-408 ("null only when the producer could not list the directory") stops being true: after the fix the producer never writes a null digest next to a recorded tree, and the only null is the initial setup-error receipt (:1350). [INFERENCE] With a non-empty tree, a null `install_tree_sha256` still passes the gate (the :412 recompute is skipped). Requiring hex whenever the tree is non-empty would close that, but it's a receipt-forgery axis, not the C1 producer claim. |
| R-gate | `check-receipt.py:442-477` install_links block (`name in tree` shadow :469-471, chain :473-477) | membership | No. |
| R-grid | `tests/llamacpp-live/install-tree-grid.py:124-147` | reads/mutates receipt `install_tree`; no producer call | No. |
| R-fixture | `tools/error-verdict-census.py:228-229` | literal receipt `{"server":{"install_tree":{...}}}` | No. |
| comment | `tests/llamacpp-live/controls.py:129` | prose ("pid file is created after the tool's install_tree hash") | No. The fake `srv/` holds one readable `fake_server.py`. |

Historical `.ufo` callers (frozen evidence; append-only; **no migration**):
`.ufo/waves/round-18/runs/run.py:58`, round-17/18 frozen copies, and round-21 probes
(`build/out/LinksRealReceipt/links-real-receipt.py:84-85`, `LinksGateReview/synthetic_link_checks.py:74-75,98-99`,
`LinksLoaderProof/digests.py:18-19`, `KamaR21.LinksGridReview-6/ast_and_realpath.py:43-45`,
`KamaR21.SrcReproducibleBuildsArchive-6/symlink_encoding_probe.py:26,34`).
`.ufo/waves/round-21/recipe.json:54,64,76,88` runs `install-links-grid.py` (frozen, current,
both, selftest). The round-22 Recipe should expect the G1 migration to keep current=0, both=1
(because frozen=1), selftest=0, frozen=1 unchanged.

## Required semantics for the migrations (to keep legacy expectations)

- **G1 `identity`**: catch the *loaded module's* class, `module.SetupError`. Each `load_source`
  `exec` creates a distinct class object, so `except SetupError` imported from elsewhere won't
  match. Return an identity that differs from `real_ids[arm]` and has a non-empty `problems`
  (e.g. `{"install_tree_sha256": None, "install_links_sha256": None, "problems": [exc.code],
  "unpinned": []}`, `tree={}`, `links={}`). Then `changed=True` and `refused=True` still hold for
  `regular-unreadable`. The selftest check `controls-both-arms` (`:339-342`, current
  `regular.changed == 3`) and the class summary stay unchanged. The frozen arm (FROZEN_REV
  `7a6bc911`, :49) never raises, so leave its behaviour alone. The real-tree path `:215-219`
  should still turn a raise into `EvalError` ("real tree is not pinnable"), not a verdict.
- **G2**: `except producer.SetupError` → `could-not-evaluate`, return 2.
- **R1 (ApiFix)**: keep the one-prefix contract `install-tree-unpinnable:<detail>` *with the
  colon*. `unpinnable-e2e.py:92` tests `setup.startswith("install-tree-unpinnable:")`, and the
  knowledge entry documents `install-tree-unpinnable:…`. A bare
  `SetupError('install-tree-unpinnable')` breaks that prefix for any future unreadable/listdir
  e2e case. Suggested details, mirroring `install_links`: `listdir:<strerror>`,
  `<name>:<strerror>` for lstat, `<name>:unreadable`/`<name>:<strerror>` for reads. A subtype
  isn't needed: `main` reads only `exc.code`.
- **Interaction with `install_links(..., tree)`**: once `install_tree` is fail-closed, the
  `not-hashed` branch (:258-259) can't be reached from P1/G1/G2, because any regular member it
  failed to hash has already raised. Keep the branch: P3 `:1189` still exercises it with a
  caller-supplied partial map. The docstring at :224-225 should describe it as defence for
  caller-supplied maps. `listdir` failure now raises in `install_tree` first, so the
  `listdir:` problem at :233-234 also becomes unreachable from P1. Keep it too: `install_links`
  is still callable standalone.
- Success path: tuple shape `(dict, hex)` must stay identical. P1, G1, G2 and every historical
  probe unpack exactly two values.

## Docs that mention the changed behaviour (owner: scribes / L1)

- `corpus/knowledge/llamacpp-loading-lifecycle.md:343-348` ("Fail closed, never smaller"): add
  that `install_tree` itself refuses on listdir/lstat/read failure.
- `SCORECARD.md:1032` and `corpus/lessons/round-21.md:136`: the round-21 frontier item
  "unreadable-member fail-closed rule for `install_tree` consumers outside the live producer"
  is what this round pays off. Cite G1/G2 as those consumers.

## Owned paths

Written: `.ufo/waves/round-22/build/advice/CallLinks.md` (this file only). Read-only otherwise.
Tools installed: none.

## Checks for L1 after integration (not run here)

`python3 tools/kama-llamacpp-live.py --selftest`;
`python3 tests/llamacpp-live/install-links-grid.py --selftest` (expect 0),
`--arm current --json` (0), `--arm both --json` (1), `--arm frozen --json` (1);
`python3 tests/llamacpp-live/unpinnable-e2e.py` (0);
`python3 tests/llamacpp-live/check-receipt.py --selftest`. Run them as a non-root user:
the chmod-0 cell is a no-op for root.

## Remaining unknowns

- I haven't seen ApiFix's exact reason string, so the R1 colon-prefix compatibility is a
  recommendation, not an observation.
- I didn't check whether a CallerRepair draft exists yet: no `.ufo/waves/round-22/build/sandboxes/`
  directory existed when I looked.
