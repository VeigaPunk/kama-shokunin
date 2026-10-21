# UnicodeNames — round 22 C1 non-ASCII / surrogateescape boundary

Seat `KamaR22.UnicodeNames`, reviewer (read-only). Owned path: this file only.
Analysis pinned to `tools/kama-llamacpp-live.py` snapshot `#AF80` (the file drifted
`#E133` → `#AF80` mid-investigation; the lane checkout shows `M` on producer and
three test files plus untracked `install-io-grid.py` — active seat/L1 mutation
observed, not mine). Line numbers below are `#AF80`.

## The exact encode boundary

`install_tree`, producer lines 200–202:

```python
combined = hashlib.sha256(
    ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()
```

`.encode()` = UTF-8 **strict**. On POSIX, `os.listdir(str)` returns names decoded
with the filesystem encoding + `surrogateescape`, so an undecodable basename byte
(e.g. raw `b'\x80'`) becomes a lone surrogate (`'\udc80'`). Everything upstream of
the encode line survives surrogate names: `os.path.join`, `os.lstat`, and
`sha256_file`'s `open(full,'rb')` all re-encode via `os.fsencode` and work. The
single failure point is this digest-encode line, which raises
`UnicodeEncodeError` — **not** an `OSError`, so it escapes every fail-closed arm:

- Frozen 10271460 (returns `(tree, None)` / `continue`s on OSError): same line,
  `UnicodeEncodeError` propagates uncaught → crash, no output.
- Current `#AF80` (raises `SetupError` on listdir/lstat/read OSError):
  `UnicodeEncodeError` propagates between `sha256_file` success and the `return`,
  bypassing `except SetupError` at line 1603 → traceback, nonzero exit, **zero
  receipt rows** (no `setup_error` field emitted).

**Status vs the C1 claim:** a surrogate-named directory already fails *loudly* —
no digest is returned, nothing comparable escapes. Technically the declared claim
(incomplete identity must not silently return a comparable digest) holds either
way. The defect is a *channel* inconsistency: one refusal class arrives as an
unhandled crash instead of a `SetupError` receipt, and io-grid can only classify
it as generic `raised`.

## Asymmetry worth naming

`install_links`/`links_digest` (lines 206–211) **can** represent surrogate names:
`json.dumps(ensure_ascii=True)` escapes them as `\udcXX`, deterministic and
injective. The control-char gate (line 237, `ord(ch) < 0x20`) does not fire —
surrogates are U+D800–DFFF. So today: surrogate-named *symlink* → fully
pinnable; surrogate-named *regular file* → hard crash in `install_tree`. The gap
lives purely in the `'name sha\n'` text-line digest format. `_emit`
(lines 1307–1325) is also json-escaped end-to-end, so `SetupError` codes and
`problems` strings embedding raw surrogate names serialize safely.

## Preserve vs expand — recommendation

**Preserve (adopt):** wrap the combined computation so `UnicodeEncodeError`
becomes first-class refusal, e.g.

```python
try:
    combined = hashlib.sha256(
        ''.join(...).encode()).hexdigest()
except UnicodeEncodeError as exc:
    raise SetupError('install-tree-unpinnable:name-encoding') from exc
```

Zero change to every currently-encodable input (digest bytes identical — a
no-harm move); converts crash → `setup_error` receipt. Observable delta to flag:
the run now *emits* a receipt where it previously emitted nothing; any e2e that
asserts receipt-absence on crash paths would see a difference (none observed —
`unpinnable-e2e.py` only scans pre-launch `problems`).

**Expand (rejected):** hashing `os.fsencode(name)` or
`name.encode('utf-8','surrogateescape')` is byte-wise lossless and injective —
surrogateescape output can't collide with well-formed UTF-8 — but it *enlarges
the pinnable set*, beyond the declared C1 scope, and breaks the recompute
contract: `tests/llamacpp-live/check-receipt.py:165-170` and
`install-tree-grid.py:40-41` recompute `install_tree_sha` with strict
`.encode()` and would raise on such receipts (gate crash, not a clean verdict).
Every comparator would need retesting. Do not expand this round.

**Forbidden middle ground (flag if ApiFix touches the line):** any lossy
errors-mode — `replace`, `ignore`, `namereplace`, `xmlcharrefreplace` — makes the
map non-injective: `b'\x80x.so'` and literal `?x.so` converge to one line. That
is a *new* silent-comparability hole of exactly the class C1 removes. Strict
encode + catch, or nothing.

## Normalization check — clean

No `unicodedata`, `normalize`, `casefold`, or `normcase` anywhere in producer or
`tests/llamacpp-live/` (grep verified). `sorted()` is code-point order, locale
independent; `os.listdir` returns raw bytes verbatim — NFC `libé.so` (C3 A9) and
NFD `libé.so` (65 CC 81) are distinct names, distinct lines, distinct digests.
No accidental normalization risk in the current shape; keep it that way — any
future `fsnormalize`/`casefold` on names would collapse the NFC/NFD pair.

Non-surrogate Unicode (RTL, U+2028, U+200B) encodes verbatim → injective. The
only ambiguous names for the text-line format are control chars (`\n`), already
refused by `install_links` before the receipt records identity.

## Advice for `install-io-grid.py` (Matrix)

- Grid already covers `raised` non-OSError classification (`value-error`,
  `keyboard-interrupt` controls) and a `'unicode'` positive control (`libé.so`,
  NFC). Add a fault cell `name-encoding`: mock `os.listdir` → `['llama-server',
  '\udcff.so']`, `os.lstat` → regular, `sha256_file` → `'a'*64` — pure mock, no
  host-fs dependency, reaches the encode line deterministically. Expected after
  the wrap: `refused` + `install-tree-unpinnable:name-encoding`; frozen arm:
  `raised/UnicodeEncodeError` (recorded, already non-silent). If ApiFix does not
  wrap, pin `raised` and note the claim still holds — do not let the cell go
  unpinned.
- Optional cheap control: NFC+NFD pair fixture asserting *both* keys present with
  distinct digests — catches future normalization. `reversed-order` already
  guards sort nondeterminism.

## Checks proposed for L1 (not run this wave)

- `python3 -c "os.fsdecode(b'\\x80').encode()"` → confirms `UnicodeEncodeError`
  class on host Python 3.14.
- `tests/llamacpp-live/install-io-grid.py --arm both --json` post-integration:
  expect frozen red on OSError cells, current green, `name-encoding` cell per
  the pinned expectation above.
- Smoke: tempfile dir, `os.mkdir`+`open` a `os.fsdecode(b'bad\\x80.so')` member,
  invoke producer → expect `setup_error` receipt (wrapped) or clean crash
  (unwrapped), never a digest.

## Installs

None (pacman paused host-wide; none needed).
