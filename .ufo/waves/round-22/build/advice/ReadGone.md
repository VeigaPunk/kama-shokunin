# ReadGone — discriminating C1 case: member `sha256_file` FileNotFoundError

Scope: design only, no code edits, no runs. Line numbers cite the frozen blob
`10271460cc575fc2280aa831e442726385fc2319:tools/kama-llamacpp-live.py` (sha256
`cec679495591cf2410334dfe08c648e310f23825181dcbae7d13b911c980e023`, verified
identical to Matrix's `FROZEN_SHA` pin) unless marked [wt] = current lane
working tree (dirty, uncommitted, still moving — see Verification gaps).

## The ONE case

**`member-read-gone:libllama.so.0.7.0`** — a regular library member passes
`os.lstat` as `S_ISREG`, then `sha256_file` raises `FileNotFoundError` (ENOENT)
at the `open()` inside it. Models the TOCTOU hole: present and regular at
enumeration, gone at read — concurrent relayout, package-manager replace, or AV
quarantine of the install directory. This is the member-read failure leg;
listdir/lstat legs belong to sibling reviewers (ListMissing, StatIO et al).

### Why FileNotFoundError is the sharpest member-read error

- It is an `OSError` subclass, so the same `except` clause is exercised as
  `PermissionError` (sibling ReadLibPerm's case) — but FNF leaves **zero
  on-disk trace**: the member still exists, is still regular, still
  `os.access(R_OK)`-readable. Unlike permission faults, it can never be
  explained as a pre-existing filesystem condition; it is irreducibly a race
  against the pin. That makes it the purest "incomplete identity that must not
  become a digest" specimen.
- Only `FileNotFoundError` (and sibling `IsADirectoryError`) cannot be produced
  by host permissions at all — `chmod 000` yields EACCES, deleting the file
  would trip the *lstat* leg instead. Mock injection is the only way to
  isolate this leg, which is why the contract's `unittest.mock` mandate is
  load-bearing here.
- It cannot be produced by real fixture mutation without a racing thread;
  injection at the function boundary is deterministic — no threads, no perms,
  no host-state dependency ("No real host permissions dependency", contract).

### Why the victim must be `libllama.so.0.7.0` (a non-server library member)

- `llama-server` is the wrong victim: frozen hashes it independently at
  frozen:1413 (`server_sha = sha256_file(server_real)`) *before* `install_tree`
  — a server-read fault conflates with a separate, earlier refusal and is not
  attributable to the install-tree leg.
- `libllama.so.0.7.0` is identified *only* by the `install_tree` map/combined
  digest; its silent omission is invisible to every other producer check.
- In sort order `libllama.so.0.7.0` precedes `llama-server` in any realistic
  mix, and in the grid's 2-member `BODY` `lib.so` sorts first — the surviving
  partial was built by *continuing past the hole*, proving the fault did not
  truncate iteration but silently dropped a member mid-map.

### Fixture (temporary tree)

| name | kind | role |
|---|---|---|
| `llama-server` | regular file | `server_real` arg; surviving member |
| `libggml-base.so.0.27.0` | regular file | second survivor |
| `libllama.so.0.7.0` | regular file | **fault target** |
| `libllama.so` | symlink → `libllama.so.0.7.0` | symlink-semantics sentinel |

Two surviving regular members are deliberate: a 2-of-3 partial `{llama-server,
libggml-base.so.0.27.0}` is indistinguishable from the identity a genuinely
smaller release directory would pin — the vivid "comparable partial digest".
The symlink sentinel proves intentional symlink skipping is preserved (skipped,
not refused) on the after arm. (Matrix's current 2-member `BODY` already
exercises the leg minimally; 3 members + sentinel is the recommended shape —
consistent with sibling ReadLibPerm.)

## Smallest injection target

```python
real = mod.sha256_file
def guarded(path, *a, **k):
    if os.fspath(path) == os.fspath(folder / 'libllama.so.0.7.0'):
        raise FileNotFoundError(errno.ENOENT,
                                os.strerror(errno.ENOENT), str(path))
    return real(path, *a, **k)

with patch.object(mod, 'sha256_file', guarded):
    tree, digest = mod.install_tree(str(folder / 'llama-server'))
```

- Patch `mod.sha256_file` — `install_tree` resolves it through module globals
  at call time (frozen:197). `mod` is the per-arm exec'd module object from
  `load_source`; `mock.patch('tools.kama-llamacpp-live.sha256_file')` is a
  no-op (module never enters `sys.modules`) and would yield vacuous green.
- The guard matches by full-path `os.fspath` equality and delegates every
  non-victim to the real `sha256_file`; an unguarded `side_effect` would also
  kill survivors' reads (fault count ≠ 1 → could-not-evaluate catches it).
- Raise a real-shaped `FileNotFoundError(errno, strerror, filename)` — not a
  bare instance: [wt]'s detail suffix is `(exc.strerror or type(exc).__name__)`,
  and the real shape exercises the `strerror` arm, matching what `open()`
  actually raises.
- Do **not** patch `builtins.open` (overbroad, hits harness internals) or
  `os.lstat`/`os.listdir` (sibling legs), do not wrap `open` with a chunk
  reader (that is the separate late-read case), do not `os.unlink` the file
  (moves the fault to the lstat leg).

## Expected classes

- **frozen arm — RED (`returned` + comparable partial).** frozen:197→199
  (`tree[name] = sha256_file(full)` / `except OSError:` / `continue`) swallows
  the FNF; loop continues, hashes survivors, returns
  `({'llama-server': …, 'libggml-base.so.0.27.0': …}, <self-consistent
  sha256>)`. Non-`None` digest that compares equal to a different real layout —
  exactly the C1 claim. Expected observation:
  `{'status':'returned', 'tree': <2-member map>, 'digest': <hex>,
  'paired_problems': ['libllama.so.0.7.0:not-hashed']}`.
- **current arm — GREEN (`refused`).** [wt] ~199-202 raises
  `SetupError(f'install-tree-unpinnable:read:{name!r}:' + (exc.strerror or
  type(exc).__name__)) from exc` →
  `{'status':'refused', 'reason':"install-tree-unpinnable:read:'libllama.so.0.7.0':No such file or directory",
  'cause_is_fault':True, 'fault':1}`.
- Existing consumers need no repair for this leg: [wt] `main()` calls
  `install_tree(server_real)` at [wt]:1415 inside the `SetupError`-catching
  block ([wt]:1603 → exit 2 + `setup_error` receipt token). The producer catch
  already handles it.

### Pinned digest values (grid `BODY` 2-member fixture, computed offline)

- members: `llama-server` `5a20fe58f9668764eeec736f9b07a96a857699565af9c98f926430c176ae7dd0`, `lib.so` `7f4b61ed12752d3e8aeb7a52536f9f4fd35c6706912a19a53501df20ad25262e`
- complete combined (positive-control pin): `3f0edaa087d7358666f1477997d43ad2133e4ad5d8152327e5c07d055f3b12a7`
- partial minus `lib.so` (the exact comparable value frozen must be caught returning): `3c1f2af51a68eaad77f36169f0ee9205ea31009f0ff6ee6b4b10802895df804e`
- partial minus `llama-server`: `c82c1b1cea20a1a06d72916d676e5f378af229a48b148889c2430174c969267d`

Pinning these (not merely "digest is not None") proves the escaped identity is
self-consistent and comparable — a garbage hex digest would be a different
finding class. For the 3-member fixture the survivor set is two entries.

## Positive control

Unpatched `observe()` on the pristine fixture: both arms must return
`{'status':'returned', 'tree': == expected_tree(body), 'digest': == complete
pin, 'fault': 0}` — identical map and digest across arms (byte-exact
success-path preservation, same property the links-grid's
`back_compat_install_tree_sha256_equal` enforces). Symlink sentinel: on
current, skipped without refusal and without `problems`; on frozen, same skip
(frozen already skipped non-regulars — preserved semantics, no behavior
change). Negative/selftest controls already exist in the draft grid:
`read-refusal-deleted` fixture → exit 1; `always-refuse`/`always-empty` →
exit 2; module-load/git-show failure → exit 2 (`could-not-evaluate`).

## False-positive risks

1. **Scoring above the unit boundary — the dominant risk.** Frozen `main()`
  *still refuses* this fault end-to-end: `install_links` (frozen:1415-1416)
  re-lstats the still-present member, finds it absent from the partial tree,
  and emits `libllama.so.0.7.0:not-hashed` (frozen:258-259) → `SetupError` at
  frozen:1417-1419. The same masking holds for the listdir leg (frozen's own
  `install_links` listdir fails → `listdir:` problem) and lstat leg. So at
  producer-CLI granularity **frozen is green for every I/O fault leg** — the
  entire C1 delta lives at `install_tree`'s return/raise boundary. Any scoring
  of `main()` exit code or `install_links` outcome produces false-green on
  frozen. Score `status`/`digest`/`reason` at the `install_tree` call only;
  record `paired_problems` as evidence that the backstop exists, never as the
  verdict. (The draft grid's `observe()` does exactly this — keep it.)
2. **Token-shape over-pinning.** Match `reason` by prefix
  `install-tree-unpinnable:read:` + member `repr`, never exact equality — the
  [wt] token evolved mid-wave (plain `{name}` → `{name!r}` + strerror detail);
  an exact-string oracle red-flags a correct producer and pins one transient
  format as contract. Also accept the prefix only — a frozen-arm "refusal"
  carrying a foreign token (e.g. `lstat:`) means the fault landed on the wrong
  leg.
3. **`install_links` paired call must stay outside the patch scope** — inside,
  the injected lstat/read wrappers corrupt `install_links`'s own stat/readlink
  and fabricate `problems` evidence. Draft keeps it outside `ExitStack`; keep.
4. **`cause_is_fault` provenance.** Require `exc.__cause__ is injected` (wt
  uses `raise … from exc`). A refusal with a foreign cause — or `fault != 1`
  — is could-not-evaluate (exit 2), not a pass; never count a refusal on the
  wrong exception as satisfying the property.
5. **Frozen-pin integrity.** `frozen_source()` pins the blob sha256
  (`cec67949…` — verified above) and refuses tamper via exit 2, not a verdict;
  `install-links-grid.py`'s `FROZEN_REV = 7a6bc911…` is the *previous* round's
  pin and must not be copied into the io grid (draft correctly uses 10271460).
6. **Mid-write torn reads of [wt].** The lane checkout is dirty and was edited
  during this review; `--current-source` reads whatever bytes are present. A
  torn write execs as SyntaxError → `raised` status → counted violation →
  false red on current. The doc's `source_sha256` fields make runs
  attributable; L1 should run after integration settles.
7. **`late-read` leg is a different case** (FNF/OSError mid-stream after first
  chunk); do not fold it into this row — it needs the `LateReader` open-wrap,
  a different injection site (`module.open`, `create=True`).
8. **Don't assert `install_links` for the refused arm** — current raises inside
  `install_tree`, links never runs; `paired_problems` exists only on
  `returned`.

## Exact line references

Frozen `10271460:tools/kama-llamacpp-live.py`:
- 178-202 `install_tree`; 184-187 listdir leg (`except OSError` → `return
  tree, None` — null-digest escape); 190-193 lstat leg (`continue`);
  **196-199 member-read leg (`tree[name] = sha256_file(full)` 197,
  `except OSError:` 198, `continue` 199) ← this case**; 200-202 combined
  digest + return.
- 171-176 `sha256_file` (the `open(path,'rb')` site the injected FNF models).
- 1414-1419 consumer: `install_tree` 1414, `install_links(server_real, tree)`
  1415-1416, `link_problems` → `SetupError('install-tree-unpinnable:' +
  ';'.join(...))` 1417-1419; backstop `not-hashed` 258-259.
- 1413 `server_sha = sha256_file(server_real)` (why the server binary is the
  wrong victim).

[wt] `tools/kama-llamacpp-live.py` (dirty, may shift):
- ~185-202 `install_tree`: `listdir` raise ~187-189, `lstat:{name!r}` raise
  ~193-195, **`read:{name!r}` raise ~199-202**; docstring 179-182 already
  states the fail-closed contract.
- 1415-1419 `install_tree`→`install_links`→`link_problems` refusal; 1603
  `except SetupError` → exit 2.

`tests/llamacpp-live/install-io-grid.py` (untracked draft in wt):
- 25-26 `ERRORS` (`'missing': FileNotFoundError`); 32-34 `read-*` FAULT rows
  (`read-llama-server-missing`, `read-lib.so-missing` — this case, both
  members); 82-86 `hashed` wrapper (the exact `patch.object(mod,
  'sha256_file')` site); 121-128 `status`/`reason`/`cause_is_fault`
  observation; 130-132 `paired_problems` outside patch scope; 148-155 oracle
  (`install-tree-unpinnable:read:{member!r}:` prefix + cause + fault==1);
  193-198 `partial_digests`/`null_results` counters — extend these to pin the
  recomputed partial digest values above, not just non-None.

## Owned paths

- Report: `.ufo/waves/round-22/build/advice/ReadGone.md` (this file — sole
  owned artifact; design-only seat, no production/test edits).

## Verification gaps

- [wt] producer is uncommitted and changed during this read (token format
  moved to `{name!r}` + detail between snapshot AF80 and the latest `git
  diff`); all [wt] line numbers must be re-anchored at L1 integration.
- `install-io-grid.py` exists only as an untracked wt draft; behavior
  described here is from source reading, not execution — no runs this wave
  per contract.
- Frozen digest pins above are arithmetic over the grid's `BODY` fixture, not
  from any run.
- Proposed runnable check for L1: `python tests/llamacpp-live/install-io-grid.py
  --arm both --json` → frozen arm `violations ≥ 1` red (incl. both
  `read-*-missing` rows), current arm `violations 0`; `--selftest` → 0.
