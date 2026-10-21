# ReadPartial — late streaming-read OSError design review

Scope: `late-read` cell of `install-io-grid.py` vs `install_tree`/`sha256_file`
in `tools/kama-llamacpp-live.py` (frozen `10271460` vs lane working tree).
Static review only; no verification runs this wave. Read-only fact checks:
`git show` of the frozen blob and sha256 of it — `FROZEN_SHA` pin in the grid
matches the real blob exactly (`cec67949…e023`).

## F1 — BLOCKER: reason-oracle format is three-way inconsistent; current arm goes falsely red

Three producers of the `install-tree-unpinnable` reason disagree:

- Working-tree producer emits **raw name, no suffix**:
  `install-tree-unpinnable:lstat:lib.so` (`tools/kama-llamacpp-live.py:188,194,200`)
- Grid oracle expects **repr(name) + `:` detail suffix** and startswith-matches:
  `expected_reason = 'install-tree-unpinnable:' + stage + ':' + repr(member)` then
  `reason.startswith(expected_reason + ':')` (`install-io-grid.py:148-152`)
- Selftest fixture emits `repr(name) + ':' + str(exc)` (`install-io-grid.py:230,234,237`)

Verified arithmetic: `'install-tree-unpinnable:read:lib.so'.startswith(
"install-tree-unpinnable:read:'lib.so':")` → **False**, and even the no-member
listdir case fails: `'install-tree-unpinnable:listdir'.startswith(
'install-tree-unpinnable:listdir:')` → **False**.

Consequence: the grid declares **18 fault rows** (3 listdir + 6 lstat + 8
immediate-read + 1 late-read); against the current working-tree producer,
each fails `good`, so the *fixed* arm reports `incomplete-install-identity` /
exit 1 while the selftest fixtures stay green — a green selftest masking a
broken oracle on real code.

Recommended resolution (lowest-diff, safest direction): **producer adopts the
grid/fixture format** — ApiFix changes the three raises to:

```python
raise SetupError(f'install-tree-unpinnable:listdir:{exc}') from exc
raise SetupError(f'install-tree-unpinnable:lstat:{name!r}:{exc}') from exc
raise SetupError(f'install-tree-unpinnable:read:{name!r}:{exc}') from exc
```

Rationale: `{name!r}` is control-character-safe (a `lib\nx.so` member cannot
smuggle a newline into `receipt['setup_error']`; precedent: `install_links`
already uses `{name!r}` at line 240), and the `:{exc}` suffix preserves errno
detail for operators. Grid oracle and selftest fixture then match reality with
zero grid changes. Alternative (grid relaxes to bare `{name}`/no-suffix) loses
both properties and is not recommended.

## F2 — MEDIUM: late-read cell models "fail on read #2 after an 8-byte file's only chunk", not a mid-stream failure

`LateReader.read` returns `stream.read(size)` once then raises
(`install-io-grid.py:90-107`). With `BODY['lib.so'] = b'library\xff'` (8 B)
read #1 consumes the whole file — the modelled fault is "error while probing
past end", not "media failure mid-payload". Both prove "a partial `h` state
exists and is never returned", but the assigned scenario — *late* OSError —
should prove at least one **full 1 MiB chunk** was consumed before failure.

Recommended:

```python
LATE_BODY = b'library\xff' + b'\x00' * ((1 << 20) - 8) + b'tail'
```

i.e. victim = 1 MiB + 4 B. Read #1 delivers exactly 1 MiB, read #2 raises.
Add to `LateReader`: `self.sizes = []` / `self.bytes = 0`; record `size` per
call and `len(data)` per success; surface `read_sizes`, `late_bytes` in
`result`. Assert `read_sizes == [1 << 20, 1 << 20]` (proves the streaming
contract — a producer regressed to `fh.read()` slurp fails the cell) and
`late_bytes == 1 << 20` (proves the abandoned `h` state was a true partial
hash, not an empty one). Keep `fail_on` fixed at 2; `fault == 1` guard then
still holds. Second `late-read-llama-server` cell: cheap symmetric addition,
optional.

Also polish: inject `OSError(errno.EIO, 'injected fixture failure')` instead
of bare `OSError('injected fixture failure')` so the `:{exc}` suffix and
`exc.errno` are realistic.

## F3 — INFO (honest claim boundary): frozen returns partial identity at the function boundary; the consumer has a secondary check

`observe()` records `paired_problems` (line 130-132) — `install_links` run
*after* the injected `install_tree` fault is removed. If the tree omitted a
member but the follow-up list/stat succeeds, `install_links` reports
`<name>:not-hashed`; main then maps that problem to `SetupError`
(`install-tree-unpinnable:…`, producer lines 1418-1420). Thus do **not** claim
that every frozen fault escapes the current end-to-end caller. The proved
defect is `install_tree`'s *own contract*: a transient `lstat`/member-read
OSError is silently skipped and it returns `(partial_tree, digest)`, where
the digest is **fully self-consistent** (sha over surviving `'name sha\\n'`
lines only; `check-receipt.py:412-415` recomputation passes on a partial map)
and therefore *comparable* to a complete install identity for a consumer
that doesn't perform the secondary completeness check. Listing failures
return `({}, None)` rather than a digest; current `install_links` and receipt
validation also reject incomplete state, but that does not make the
`install_tree` return contract complete. `paired_refusals` records secondary
gate observations for this fixture; it is not evidence about the primary
function's return value or persistent host errors.

## Streaming-allocation preservation — verified statically

- `sha256_file` is **byte-identical** frozen vs current (diff shows the only
  hunk is `install_tree`'s docstring + except arms). `iter(lambda:
  fh.read(1 << 20), b'')` unchanged → O(chunk) memory, no whole-file buffer.
- `install_tree` after-change adds no per-byte allocation: the only new object
  is the `SetupError` on the failure path; the success path allocates the same
  `tree` dict + one `str.join` for the combined digest as frozen.
- LateReader's `__exit__` returns `None` → propagates injected OSError while
  `stream.close()` still runs → no fd leak, matches producer `with` semantics.
- Module-scoped `patch.object(module, 'open', opened, create=True)` is the
  correct injection point: it binds only the producer module's namespace, so
  `install_links`/`install_tree`'s `os.open`, `tempfile`, and the harness's
  own I/O are unaffected. `os.listdir`/`os.lstat`/`sha256_file` patches are
  process-global during the `with` — acceptable (single-threaded harness);
  `install_links` deliberately runs *outside* the patch window.
- `same_exception`/`cause_is_fault is injected` (same object identity through
  `raise … from exc`) is a strong binding — confirms the *injected* fault is
  the reported cause, not a lookalike.

## Partial-hash-never-returned — proof shape

`sha256_file` has exactly one `return` (line 176), after the `with` block; any
OSError between open and EOF exits by exception — `h` is unreachable
post-raise. The cell's assertions (`status == 'refused'`,
`cause_is_fault is True`, `late_chunks == 1`, plus recommended `late_bytes ==
1 << 20`) close it dynamically. `partial_digests`/`null_results` counters
already separate "comparable digest returned" (the claim) from "null digest"
(legacy listdir shape).

## Minor findings

- **`evaluate()` line 146-147**: `result['fault'] != 1` → `RuntimeError` →
  exit 2 `could-not-evaluate`. A producer that re-reads after an OSError
  (retry) would fault >1 and be ungradeable instead of "violated". Acceptable
  for a strict gate; note it.
- **`main()` line 288**: a malformed `--current-source` raises `SyntaxError`
  from `compile` — uncaught → traceback, not exit 2. Add `SyntaxError` (or
  broaden to `Exception`) to the except tuple.
- **Sandbox caveat for Matrix**: `--current-source` defaults to `LANE /
  PRODUCER`; in Matrix's independent clone (cloned from base) that resolves to
  the *frozen* content → both arms red. For green-after runs it must point at
  ApiFix's clone file (or the integrated lane file post-L1). Document in the
  grid's header or a CLI comment.
- **CallerRepair/e2e note**: `sha256_file` OSError on `args.model`,
  `server_real`, `args.probe` (lines 1406/1413/1424) is *not* wrapped in
  SetupError → `except BaseException` → `internal_fault` + outcome
  `internal-error` exit 2, vs `setup-error` exit 2 for in-tree faults. e2e
  cells injecting at member files get `install-tree-unpinnable:*`; injecting
  at model/server/probe paths gets internal-fault. Both exit 2 but different
  `setup_error`/`internal_fault` fields — the e2e oracle must expect the right
  field per site. [INFERENCE: `_record_internal` naming assumed from
  `outcome`/`exit` mapping at lines 1607-1608, 1746-1750.]
- `unpinnable-e2e.py` diff in lane (working tree) shows `identity()` already
  handles `SetupError` → `{"setup_error": exc.code}` rows — consistent with
  the new contract; no action.

## Residual (mistake-mining, out of C1 scope)

Truncation *without* OSError: `fh.read` returning a short read then `b''`
produces a complete-looking digest of truncated bytes. Only `bytes_hashed ==
os.lstat().st_size` comparison closes it (with TOCTOU caveat: concurrent
truncation *should* refuse a pin). Flag for a future axis; today's OSError
claim need not cover silent-short-read.

## Owned paths

- This report: `.ufo/waves/round-22/build/advice/ReadPartial.md` (only file
  written by this seat)
- Reviewed (no writes): `tools/kama-llamacpp-live.py` (ApiFix),
  `tests/llamacpp-live/install-io-grid.py` (Matrix),
  `tests/llamacpp-live/check-receipt.py`,
  `tests/llamacpp-live/install-links-grid.py` (CallerRepair)

## Proposed checks for L1 post-integration

```bash
python3 tests/llamacpp-live/install-io-grid.py --arm both --json   # expect: frozen arm violations>0, current arm violations=0, exit 1 (frozen red) — or per-arm invocation: frozen→1, current→0
python3 tests/llamacpp-live/install-io-grid.py --selftest          # exit 0
python3 tools/kama-llamacpp-live.py --selftest                     # producer selftest incl. _install_identity_selftest
python3 tests/llamacpp-live/install-links-grid.py --selftest       # sibling grid still green
```

Tooling: none installed (no packages needed; stdlib only).
