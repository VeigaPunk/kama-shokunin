# E08DepsAudit — dependency audit: `tools/kama-completion-live.py` → `tools/kama-llamacpp-live.py`

Round 62 / kama / wave w1 — seat `E08DepsAudit` (advisory leaf; no claim verdict, no commit).
Frozen base `a959fd9022b1ac1f3cb4dc2475d9cded8b2b01c3`; lane tip at audit time
`65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master` == `HEAD`).
All readings are from the **tip blobs** (`git cat-file blob`), not from the worktree copy;
`git status --porcelain tools/kama-completion-live.py tools/kama-llamacpp-live.py` is empty,
so worktree == tip for both files.

Scope of this seat: the dependency edge only — which dep symbols the tool borrows, whether
each exists at master, how the import path resolves, and what happens when the dep blob is
absent or rotten. Nothing here asserts C1/C2 met or unmet.

---

## 1. Import mechanism (what the tool actually does)

`tools/kama-completion-live.py:57-62`

```python
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    'kama_llamacpp_live',
    os.path.join(REPO, 'tools', 'kama-llamacpp-live.py'))
_live = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_live)
```

Resolution chain, verified by execution (`contract-matrix.json` → `resolution.copied_tree`):

| Step | Value observed in a relocated copy | Consequence |
|---|---|---|
| `__file__` | `/…/tip/tools/kama-completion-live.py` | **not** `realpath`-resolved (see F6) |
| `REPO` | `/…/tip` (dir of the tool's dir) | location-relative, never cwd-relative |
| imported path | `<REPO>/tools/kama-llamacpp-live.py` | fixed single-file edge, no package |
| module name | `kama_llamacpp_live` | **not** inserted into `sys.modules` (`dep_in_sys_modules: false`) |
| dep `__file__` | `/…/tip/tools/kama-llamacpp-live.py` | dep resolves *its own* lane from its own path |
| dep `LANE` | `/…/tip` | so the dep's `REGISTRY` also lands inside the copy |
| dep `REGISTRY` | `/…/tip/registry/endpoint-consumers.tsv` | registry is read from the derived root, not from the lane |

Path-resolution claims, each executed:

1. **cwd-independent**: `cd / && python3 -I <copy>/tools/kama-completion-live.py --help` → rc 0,
   usage printed. `-I` also proves no `PYTHONPATH`/user-site contribution (the edge is an
   explicit `spec_from_file_location`, never `import`).
2. **Relocation-hermetic**: in the scratch copy the tool imported the *copy's* dep and the
   copy's registry — it did not reach back into the lane. This is exactly the tree shape
   `tools/round62-c1-counter.py:347-364` builds (`<work>/tip/tools/{tool,dep}` +
   `<work>/tip/registry/endpoint-consumers.tsv`), so the counter's extraction shape satisfies
   the tool's layout assumption, including the registry file it needs transitively.
3. **Symlink-fragile** (F6): `abspath`, not `realpath`, so invoking through a symlink resolves
   `REPO` to the *symlink's* directory (proved: `link/kama-completion-live.py` →
   `FileNotFoundError: /…/tools/kama-llamacpp-live.py`, i.e. `<symlink-dir>/tools/…`).
4. **No import side effects in the dep**: its imports are stdlib only
   (`argparse, http.client, hashlib, io, json, fcntl, os, re, shutil, signal, socket, stat,
   subprocess, sys, tempfile, time, urllib.error, urllib.request, datetime, pathlib`), and the
   only top-level executable statement besides constants is `if __name__ == '__main__'`. So
   loading the dep reads no file and spawns nothing.
5. Module-level import precedes `argparse`, so a missing/rotten dep also breaks `--help`
   (proved: rc 1, `FileNotFoundError`, before any usage text).

## 2. Imported symbols, existence at master, arity

Extracted by AST from the master blobs (`ast-symbols.json`); dep definition lines are in
`tools/kama-llamacpp-live.py` at master, reference lines in `tools/kama-completion-live.py`.

| # | symbol | kind in dep | dep def line | tool reference lines | guard at reference |
|---|---|---|---|---|---|
| 1 | `_utc_now` | function | 208 | 76 (wrapper) → invoked 157, 396 | 157 **unguarded** (receipt build, before the `try`), 396 guarded |
| 2 | `sha256_file` | function | 377 | 80 (wrapper) → invoked 189, 190 | **unguarded** (digest stage, before the `try`) |
| 3 | `http_get` | function | 907 | 143, 280, 286, 294 | 143 via `wait_ready` (reached under the `try`); 280/286/294 guarded |
| 4 | `refused_ports` | function | 517 | 204 | **unguarded** |
| 5 | `pick_port` | function | 546 | 205 | **unguarded** |
| 6 | `prepare_witness_dir` | function | 290 | 222 | narrow guard (`except _live.SetupError` only) |
| 7 | `SetupError` | class | 196 | 223 (except clause), raised by dep | — |
| 8 | `_FORKED_PPID` | module-level list | 676 | 240 (write `[0] = os.getpid()`) | guarded |
| 9 | `_preexec_pdeathsig` | function | 662 | 244 | guarded |
| 10 | `port_owned_by` | function | 641 | 263, 451 | 263 guarded; **451 unguarded** (teardown) |
| 11 | `hold_for_witness` | function | 327 | 400 | guarded |
| 12 | `_listen_inodes` | function | 619 | 457 | **unguarded** (teardown) |

**Existence at master: 12/12 — none missing, none renamed** (`ast-symbols.json: missing: []`;
runtime rebind in `contract-matrix.json` → 12/12 `hasattr`, kinds as tabled).
"Broad try" = `tools/kama-completion-live.py:232-423` (`except Exception` → `SETUP_ERROR`, rc 2).

Arity: every one of the **13 call expressions** is arity-compatible with the dep signature
(`arity=13/13`), including the keyword uses `http_get(..., timeout=1.0)` at 143 and the
4-positional `hold_for_witness(wdir, proc, port, timeout)` at 400.
`_FORKED_PPID` is the only **mutable** shared state; it is written by the tool (240) and read by
`_preexec_pdeathsig` (662-674) in the post-fork child — both refer to the same module instance,
so the pdeathsig guard is coherent. The dep is never entered in `sys.modules`, so the counter's
second instance (`kama_live_r62`, counter:256-260) and the tool's are separate and cannot
shadow each other.

Base↔master drift of the dep: **zero**. `git ls-tree` gives the same blob
`11b4b2ef9170c68cdeeecefa3a71f928e90a11b0` (file sha256 `98d2e6bb…36fbe9`) at
`a959fd90` and at master. The C1 fix therefore adds a *consumer* of a round-61 dependency and
modifies no dependency byte. The tool blob is `c8f35c37…` at master (file sha256 `71ac4f2c…3771f`)
and absent at the base.

## 3. Fall-over when the dep blob is absent or rotten — measured

Five fixtures, each running the **master tool blob** in an isolated tree
(`fallover-driver-output.txt`, `receipt-presence.txt`, `receipts/`):

| case | fixture shape | rc | receipt written | surfaced |
|---|---|---|---|---|
| dep absent | `tools/` has the tool only | **1** | **no** | `FileNotFoundError: …/tools/kama-llamacpp-live.py` (import line 62) |
| dep syntax-broken | dep with `def port_owned_by(pid, port)` (no colon) | **1** | **no** | `SyntaxError: expected ':'` (import line 62) |
| registry absent | both tools, no `registry/endpoint-consumers.tsv` | **1** | **no** | `kama_llamacpp_live.SetupError: registry-unreadable:…` from line 204 |
| invoked via symlink | `link/kama-completion-live.py` → real file | **1** | **no** | `FileNotFoundError: <symlink-dir>/tools/…` |
| one dep symbol removed | `port_owned_by` renamed | **2** | **yes**, `verdict=SETUP_ERROR`, `setup_error="AttributeError: module 'kama_llamacpp_live' has no attribute 'port_owned_by'"` | no stderr; child spawned then killed |

So the dep edge has **two** failure regimes:

* **whole-blob failure** (absent / unparsable): uncaught exception at import → interpreter rc **1**,
  no receipt, no work dir. Nothing is spawned or written; the traceback names the exact expected
  path. "Fails" = yes; "cleanly" = only in the sense of harmless — the rc collides with the
  tool's documented `1 = at least one evaluated check failed` (`kama-completion-live.py:33-35`).
* **symbol-level failure**: because access is attribute-lazy, a partially-rotten dep is caught by
  the broad `try` and reported as `SETUP_ERROR` rc 2 with a receipt naming the missing attribute —
  the better shape, provided the failing attribute is referenced inside the guarded region
  (F2 lists the 5 references that are not).

Positive control, run for real from a counter-shaped copy (`receipts/positive_copy.json`):
one hold-mode lifecycle, observer released the hold window, **rc 0, verdict `REQUEST_OK`, 17/17
checks evaluated and passed**, child reaped (`teardown.returncode 0`, `sigterm_sent true`,
`port_closed true`, `child_pre_dead false`), on loopback port 38749 (not in
`registry/endpoint-consumers.tsv`). Every one of the 12 dep symbols was exercised on that path.
No file outside my scratch was written by it.

## 4. Findings (severity = risk to operability/calibration, my judgement)

**F1 — [High] The graded counter crashes instead of refusing on a SETUP_ERROR receipt.**
`tools/round62-c1-counter.py:393-394` mutates `receipt['captures']['health']` unconditionally once
`receipt is not None`. The tool assigns `receipt['captures']` only at line 279, so *any* setup
failure before the first capture yields a receipt with no `captures`, and building the `log`
control family raises `KeyError: 'captures'`. Measured on the one-symbol-rotated fixture:
`rc=1`, **stdout empty — no tally line at all**, traceback only; the tool's own `setup_error`
text is never surfaced (`counter-rotated-dep.txt`). Any harness that parses the frozen
`tool_present=… met=…` line sees nothing. This is the exact class of tip a do-nothing / partial-fix
control produces, and the 16 frozen control families are all receipt-field mutations of a
*succeeding* receipt (`counter:388-436` for the mutation families,
`counter:445-470` for the two canned-server `fake` families: stale, log, tamper×8, predead,
sigterm, hold, outside, fake×2), so none reaches it. The frozen claim is unaffected at the measured tip (live leg succeeds,
`captures` present); the *refusal* path is what breaks.

**F2 — [Medium] `SetupError` raised by the dep escapes unguarded, so the documented rc=2 setup
contract is not honoured on five references.** `refused_ports` (204) raises
`SetupError('registry-unreadable:…')`; `pick_port` (205) raises
`SetupError('port-refused-registered:N' | 'port-in-use:N' | …)`. Both are outside the `try`
beginning at 232. Measured: no-registry tree → rc 1 + `SetupError` traceback + no receipt;
`--port 8080` and `--port 34113` (both in the dep's `HARD_REFUSED_PORTS`) → rc 1 +
`SetupError: port-refused-registered:8080` + no receipt (`receipts/port-refused-8080.stderr.txt`),
even though the refusal itself is correct behaviour. Line 222's `prepare_witness_dir` guard covers
`SetupError` only, so a *missing* symbol there would also escape. The in-repo precedent maps this
case to a named setup error instead: `tools/kama-context-capacity.py:174-184,725-727`
(`locate_live_module()` → `SetupError('kama-llamacpp-live.py-not-found')`), and it also discovers
the root by walking parents for the registry rather than assuming `../tools`.

**F3 — [Medium] Two graded C1 checks are dep-supplied and not recomputable by the verifier.**
`counter:159-162` and `:170` accept `listener_owned` and `teardown_port_closed` straight out of
the receipt's stored bools. Both were computed by `_live.port_owned_by` / `_live._listen_inodes`.
The counter's *witness* ownership flag is also produced by the tip's dep blob
(`counter:256-275`, `witness.get('listener_owned') is True` at `:204`), so the ownership gate is
attested by the same unpinned code on both sides. Mitigation present: the witness independently
binds a live answer to alias + fingerprint shape + nonce + the recorded pid/port, and C2's bound
row `live-llamacpp-lifecycle` (`registry/capability-claims-r62.tsv:4`) executes the dep itself and
grades `"outcome": "pass"`, so a grossly broken dep is caught downstream. But neither pin nor
control makes a *lying* ownership primitive detectable; a dep that returns `True` leaves both the
receipt and the witness consistent. Keep the overlap with `A03C1WitnessSpoof` in mind — this is
only the dependency-side half.

**F4 — [Medium] The dependency has no digest binding, and the receipt records none.** The counter
binds the tool by *copying the tip blob's bytes* (`counter:343-359`), not by a frozen sha256 —
there is no `TOOL_SHA`-style constant and, for the dep, only a presence test
(`if not dep: errors.append('tip lacks tools/kama-llamacpp-live.py')`). The receipt's provenance
field is the literal string `'tool': 'tools/kama-completion-live.py'` (tool:156) — no sha256 for
either file, unlike `model.sha256` / `server.sha256`. So a receipt re-derived later cannot say
which dependency semantics produced `listener_owned`/`teardown_port_closed`. One added field
(`dep.sha256`) plus one presence→digest check in the counter would close it; nothing in the frozen
predicate forbids recording it.

**F5 — [Low-Med] `_listen_inodes` fails open on unreadable procfs while `port_owned_by` fails
closed.** Measured (`contract-matrix.json` → `primitives`):

| situation | `_listen_inodes(port)` | `port_owned_by(me, port)` |
|---|---|---|
| my own listener | `['1434287645']` | `True` |
| no listener | `[]` | `None` |
| stranger's listener | `['1434310707']` | `False` |
| `/proc/net/tcp*` unreadable, listener present | **`[]`** | `None` |

The dep swallows `OSError` per proc file (`kama-llamacpp-live.py:629-637`) and returns an empty
set, which the tool reads as "no listener remains" at 457-462 → `td['port_closed'] = True`, i.e. a
graded check passes while the ownership state is actually unknown. The ownership *gate* at 263 is
the opposite (fails closed). Only reachable with an unreadable/hidden procfs, hence the low
severity, but it is a fail-open inside a graded check and worth a `procfs-unreadable` reason
string in the receipt.

**F6 — [Low] Symlink invocation breaks the edge; docstring understates what is borrowed.**
`REPO` uses `abspath`, not `realpath` (F6 row above), so any launcher that symlinks the tool into
another directory loses the dep. And the docstring (tool:36-37) says the dep is imported "for the
port refusal, ownership, digest and witness primitives" — it also supplies the **HTTP client used
to fetch every graded capture body** (`http_get`, whose `_OPENER` disables proxies and redirects),
the clock, and the pdeathsig pair. So the graded capture path itself is dep-owned, which matters
for anyone reasoning about what C1 actually measures.

**F7 — [Info] `SETUP_ERROR` receipts after a spawn carry no teardown block.** The `except` at
412-423 kills the child and returns before the teardown section (425-467), so
`missing_symbol.json` has `child_pid` and `port` but no `teardown`, and no proof the child was
reaped. I verified externally that it was: pid 1070280 absent from `ps`, port 43895 with no
listener (`ss -ltn` count 0). Harmless today; a receipt-level gap if a setup fault ever lands
after spawn in a graded run.

## 5. What is sound (so the report is not read as blanket rejection)

* 12/12 dep symbols exist at master; 13/13 call arities match; base↔master dep blob identical.
* The edge is explicit-file, cwd- and env-independent (`-I` from `/` works), and hermetic under
  relocation — the counter's `<work>/tip` shape satisfies it end-to-end (positive control
  `REQUEST_OK`, 17/17).
* The dep has no import-time side effects and stdlib-only imports, so the edge adds no third-party
  prerequisite.
* Symbol-level rot is reported as `SETUP_ERROR` rc 2 with a receipt naming the attribute — good
  behaviour wherever the reference sits inside the guarded region.
* Absent-dep is refused **cleanly at the graded-instrument level**: the counter emits its frozen
  tally (`tool_present=1 live_ok=0/1 … errors=2 met=False`) plus two named errors and exits 1
  (`counter-dep-absent.txt`). The defect in F1 is only the *present-but-rotten* shape.

## 6. Bounds, hygiene, tools

* Scratch root `/fast/scratch/hyaku/kama-r62/w/E08DepsAudit/` (created with `mkdir -p`, passed
  explicitly as `--work`/`--out`/`TMPDIR` everywhere, removed before yield; receipts copied to
  `.ufo/waves/round-62/w1/out/E08DepsAudit/` first).
* No git/jj mutation in the lane. Two throwaway fixture repos (`fx_no_dep`, `fx_renamed_dep`) were
  created under scratch; `git -C <fixture> rev-parse --show-toplevel` printed the fixture dir before
  every write, and commits used a fixture-local identity (`-c user.name=e08 -c user.email=e08@fixture.local`).
  Lane access was read-only (`rev-parse`, `ls-tree`, `cat-file`, `show`, `status`).
* Live runs: only the audited lane tool (byte-identical master blob, sha256 `71ac4f2c…`) on
  tool-chosen unregistered loopback ports (38749, 43895, 41289/43973/41895 for socket probes). No
  registered consumer port was contacted; I killed no process I did not spawn (the two foreign
  `llama-server` children visible during the run belong to sibling seats and were left alone).
* **No tool install or upgrade was performed** (no pacman — host-wide pause respected — no `uv`,
  no `npx`, no binary dropped in `PATH`); `python3` 3.14.8, `git`, `ss` were already present.
* Nothing was written outside `.ufo/waves/round-62/w1/out/E08DepsAudit/` and this file; no fleet
  file, sibling lane, lane jj state or Git index was touched; `/home/vgpnk/Projects/shokuknow` was
  not read or executed.

## 7. Tally (one line)

```
E08DepsAudit deps=12/12_present_at_master refs=16 arity=13/13_ok resolution=file_rel_abspath(cwd/env_independent, symlink_fragile, hermetic_in_copy) fallover={dep_absent:rc1_no_receipt, dep_syntax:rc1_no_receipt, registry_absent:rc1_no_receipt(SetupError_escape), symlink_invoke:rc1_no_receipt, symbol_removed:rc2_SETUP_ERROR_receipt} counter={dep_absent:CLEAN rc1 errors=2 tally_printed, dep_rotated:CRASH KeyError_captures no_tally rc1} positive=REQUEST_OK 17/17 checks port=38749
```

## 8. Evidence manifest

`.ufo/waves/round-62/w1/out/E08DepsAudit/`

| file | content |
|---|---|
| `ast-symbols.json` | AST symbol table: 12 deps, kinds, tool reference lines, `missing: []` |
| `contract-matrix.json` | import-resolution record (copied tree + isolated/cwd=`/`) and the 4-branch ownership/procfs primitive matrix |
| `fallover-driver-output.txt` | full driver output for all five fall-over fixtures |
| `receipt-presence.txt` | which fixtures reached the receipt writer (4 did not — that is the finding) |
| `receipts/missing_symbol.json` | SETUP_ERROR receipt from the one-symbol-rotated dep (rc 2 path) |
| `receipts/positive_copy.json` | full `kama-completion-live/v1` receipt, `REQUEST_OK`, 17 checks |
| `receipts/port-refused-8080.stderr.txt` | unguarded `SetupError` escape on the port-refusal path |
| `counter-dep-absent.txt` | counter vs dep-absent fixture: rc 1, tally line, `errors=2` |
| `counter-rotated-dep.txt` | counter vs rotated-dep fixture: rc 1, empty stdout, `KeyError: 'captures'` |
| `fixture-shas.txt` | sha256/git-oid receipts for both tool blobs, the dep at base and master, and both fixture repos |
| `scripts/` | `audit_deps.py`, `driver.py`, `contract_matrix.py`, `run_live_copy.py` (re-runnable probes) |
| `manifest.sha256` | sha256 of every artifact above |

Scratch root cited above is deleted at yield; every path inside these artifacts that points at
`/fast/scratch/hyaku/kama-r62/w/E08DepsAudit/…` refers to that now-removed tree.
