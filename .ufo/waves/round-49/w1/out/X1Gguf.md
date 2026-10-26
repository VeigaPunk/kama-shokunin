# X1Gguf — C1 counter's GGUF vocabulary decoder, independently checked

**Verdict:** `gguf_tokens()` of `tools/round49-replay-witness-audit.py` reproduces the pinned model's vocabulary exactly — all 512 entries byte-for-byte, identical digest — against a second implementation (PyPI `gguf` 0.19.0); of the four required malformed classes only tail truncation inside the last token body is accepted silently (returns 512 entries with the last one patched), and three crafted files raise exception classes that this counter's own handler does not catch (`OverflowError`, `RecursionError`) — but the counter hashes the model before decoding (`tools/round49-replay-witness-audit.py:442`) and only ever decodes the digest-matched file, so **no defect reaches C1's claim**.

## 1. Setup and pins

- Model: the counter's own pin, `MODEL_URL`/`MODEL_SHA` at `tools/round49-replay-witness-audit.py:99-101`
  (`499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf`).
  Downloaded once to scratch, 1 185 376 B,
  `sha256 = 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` = `MODEL_SHA`. Match.
- Second implementation: `gguf` **0.19.0**, PyPI channel via `uv run --with gguf` (installed into the uv
  cache only; nothing added to any PATH directory, no pacman — host guard respected).
  Chosen over `tools/gguf-identity.py`, which **cannot** supply entries: its reader keeps only
  `ArraySummary(element_type, length)` (`tools/gguf-identity.py:91`, returned at `:204`), so it can
  confirm the array is `STRING` with `length 512` and nothing more (recorded in
  `out/X1Gguf/gguf-identity-model.json`).
- The counter was imported by path with `importlib` (never copied into the lane, never executed as a
  script), so `gguf_tokens()` is the exact frozen source.

## 2. Result A — the 512 entries agree

```
$ uv run --with gguf python out/X1Gguf/compare_gguf_tokens.py stories260K.gguf \
      kama-shokunin/tools/round49-replay-witness-audit.py        # exit 0
counter_len 512 / package_len 512 / mismatches 0 / all_512_equal true
counter_vocab_sha256 = fda96b6ed6f364937824db6c0ee91a58319721f001fc9b6005eb13bf0cd9cf03
package_vocab_sha256 = fda96b6ed6f364937824db6c0ee91a58319721f001fc9b6005eb13bf0cd9cf03
raw_byte_count 512 / invalid_utf8_count 0 / package_tokenizer_model "llama"
first3 ["<unk>", "<s>", "</s>"]   last3 ["]", "~", "\u200a"]
```

- Comparison is **index-aligned**, which is exactly what the witness consumes:
  `vocab[t["id"]].replace("\u2581", " ") == t["piece"]` at `tools/round49-replay-witness-audit.py:281`.
- Every entry was also checked for byte-level agreement: the raw token bytes re-decoded strictly
  yield 512/512 valid UTF-8, so the counter's `decode("utf-8","replace")` (`:159`) cannot be hiding a
  replacement character on this file. `out/X1Gguf/tokens-512-both.tsv` has all 512 rows
  (`idx, counter_repr, package_repr, equal`), all `equal=1`; index 0/1/2/509/510/511 are
  `'<unk>' '<s>' '</s>' ']' '~' '\u200a'` in both.
- Parser-offset agreement beyond this file: `skip()`'s fixed-width table (`:155`) was exercised with one
  KV of each scalar type 0–12 plus a string, a nested array and an ARRAY<UINT32> placed *before* the
  tokens key; the decode returned exactly the 5 planted tokens (case `skip-coverage-types-0-12`).
  On a deliberately invalid nested-array fixture **both** decoders stop at the same byte with the same
  bogus element type (`out/X1Gguf/invalid-agreement.txt`: counter `EvalError: GGUF value type 21`,
  gguf-py `ValueError: np.uint32(21) is not a valid GGUFValueType`, `agree_on_rejection=True`).

## 3. Result B — malformed inputs (26 cases, no hang)

`out/X1Gguf/malformed-cases.jsonl`, produced by `malformed_gguf_tokens.py` (each case in a subprocess,
60 s cap that was never approached; whole harness wall ~1 s, exit 0):

| required class | fixture(s) | behaviour | seconds |
|---|---|---|---|
| truncated file | prefix cuts at 6470/6469/6468/6467/6466/6459/6450/4000/100/69 B (tokens array is bytes 69–6470; token 511 `e2 80 8a` body at 6467–6470) | **6469, 6468 → returns 512 tokens with last = `'\ufffd'`; 6467 → returns 512 with last = `''` (silent patch).** 6466, 6459, 6450, 4000, 100, 69 → `struct.error` ("unpack_from requires a buffer of at least N bytes … actual buffer size is M"). 6470 → 512 correct | 0.0 |
| GGUF v1 header | version 1 (and version 0) | `EvalError: GGUF v1 unsupported` (`:152`) | 0.0 |
| tokens array not strings | `ARRAY<UINT32>` | `EvalError: tokens array is not strings` (`:182`) | 0.0 |
| tokens as a scalar STRING | key present, type 8 | `EvalError: tokenizer.ggml.tokens absent` (the `t == 9` test at `:178` skips it) | 0.0 |
| 1 MiB random file | `os.urandom(1<<20)` | `EvalError: model is not GGUF` (`:149`) | 0.0 |

Extra cases beyond the four, run to answer "hang?" and to find handler escapes:

| case | behaviour | seconds |
|---|---|---|
| random 1 MiB **with `b"GGUF"` forced** | `OverflowError: Python int too large to convert to C ssize_t` — **uncaught** | 0.008 |
| 1 MiB random claiming `nkv = 2**62` | `OverflowError` — **uncaught** | 0.008 |
| 2000-deep nested array before tokens | `RecursionError: maximum recursion depth exceeded` — **uncaught** | 0.002 |
| 1 000 000 zero-length tokens (8 MB) | returns 1 000 000 entries, no cap | 0.165 |
| v2 minimal / v3 minimal | both return the 3 planted tokens (version 2 accepted as the docstring promises) | 0.0 |

No case hung; the slowest decode is 0.165 s (1e6 tokens), and cost is linear in file size, since the
whole file is read at `:147` and every token needs an 8-byte prefix.

## 4. Findings

All four are decoder robustness. **None weakens C1**: the decode only runs after
`if sha_file(model) != MODEL_SHA` (`tools/round49-replay-witness-audit.py:442`), so in a real counter run
`gguf_tokens()` sees either exactly the pinned bytes or is not called at all. They matter only if the
function is reused on an attacker- or network-controlled path without the digest gate.

- **F1 (low, silent corruption).** A prefix-truncated file whose cut lands inside the *last* token body
  returns a complete-looking 512-entry list with the last entry patched (`'\ufffd'` or `''`) instead of
  raising. Cause: `rstr()` slices `data[o+8:o+8+n]` without checking the declared length against the
  remaining bytes (`:157-159`), and the loop ends after the last iteration, so nothing detects the
  overrun. Evidence: `real-prefix-6469B/6468B/6467B` in `malformed-cases.jsonl`
  (`silently_differs_from_true_vocab=true`). Impact if it did reach the witness: the mismatch would show
  up as a piece disagreement at id 511 (fail-closed), not as a pass.
- **F2 (low, uncaught crash).** A file that passes the magic check but has a bogus version / KV count
  makes `rstr()` advance `off` to a value larger than `sys.maxsize`, and the next
  `struct.unpack_from("<I", data, off)` at `:176` raises `OverflowError`. The counter's handler catches
  only `(OSError, EvalError, struct.error)` (`:447`), so the exception leaves `main()`: traceback,
  exit 1 — the same exit code as a legitimate `met=False`. Evidence: `out/X1Gguf/escape-probe.jsonl`
  (`escapes_handler` = the two random cases) and `out/X1Gguf/exitcode-sim.txt` (`exitcode_sim.py` runs the
  counter's exact `try/except` on `random-magic.gguf` and `nested.gguf` in child processes: rc=1, empty
  stdout — no "counter model unavailable" line — and stderr ending `OverflowError: …` / `RecursionError: …`).
  Contributing cause: the version guard is `if ver < 2` (`:151`), so any version ≥ 2 — including
  `0x9138f1ee` — is parsed with the v3 layout.
- **F3 (low, uncaught crash).** `skip()` recurses per nesting level with no depth limit (`:161-172`,
  recursion at `:170`); 2000 levels give `RecursionError`, also outside `:447`. Compare
  `tools/gguf-identity.py:39` (`MAX_ARRAY_DEPTH = 32`), which bounds this.
- **F4 (informational).** No bound on `nkv` (`:153`), array length (`:167`, `:179`) or token count
  (`:184`); the file is read whole (`:147`). Bounded in practice by file size (1e6 tokens in 0.165 s,
  8 MB resident) and, today, by the digest gate before the call.
- **F5 (observation, not a defect).** `tools/gguf-identity.py` cannot serve as the entry-level second
  implementation: `Reader.value()` discards STRING array elements and returns only
  `ArraySummary(type, length)` (`:204`). It confirms `tokenizer.ggml.tokens` = `STRING`, `length 512`.

### Proposed fix (frozen files: proposal only, **not applied**)

`out/X1Gguf/proposed-fix.diff` (unified diff against `tools/round49-replay-witness-audit.py`):
reject versions other than 2/3, refuse a header shorter than 24 B, bound every string length and array
count by the bytes actually left, and cap nesting depth at 64 — i.e. make every malformed input an
`EvalError`, which the counter already handles.

Verified on a scratch copy (`$S/counter-patched.py`, never in the lane): 512/512 tokens still equal
(same digest `fda96b6e…`), all 26 malformed cases either raise `EvalError` or keep the cuts that already give `struct.error`
(which the counter catches),
the silent-patch cases become `EvalError: truncated string: 3 bytes declared, 2 left`, the two
`OverflowError`s become `EvalError: GGUF v2436472238 unsupported` / `… truncated string: …`, the nesting
case becomes `EvalError: GGUF nesting too deep`, and `escape_probe.py` reports `escapes_handler: []`
(`out/X1Gguf/malformed-cases-patched.jsonl`, exit 0).

## 5. Residual risks / not tested

- Decoder level only: I did not run the C1 counter end-to-end (other seats own that), and I started no
  server; `pgrep -af llama-server` shows only another seat's `V1Counter` fixture processes, none of mine.
- `sha_file(model)` (`:442`) and `gguf_tokens(model)` open the file twice — a same-user swap between the
  two calls would decode bytes other than the hashed ones. `mkdtemp` is 0700, so this is theoretical.
- One real model was available (the pinned tiny model). Parser coverage beyond it comes from the
  synthetic v2/v3 fixtures (all scalar types, nested arrays) rather than a second real GGUF.
- The random-byte fixtures are non-deterministic; the harness reconstructs them on each run.

## 6. Reproduce

```bash
S=/fast/scratch/hyaku/kama-r49/X1Gguf; mkdir -p "$S"; export TMPDIR="$S"
O=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Gguf
curl -sSL -o "$S/stories260K.gguf" \
  "https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf"
sha256sum "$S/stories260K.gguf"        # 270cba1b…256d
C=/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round49-replay-witness-audit.py
cd "$S"
uv run --with gguf python "$O/compare_gguf_tokens.py" stories260K.gguf "$C"          # exit 0
python3 "$O/malformed_gguf_tokens.py" "$C" "$S/cases" "$S/stories260K.gguf" \
        "$O/malformed-cases.jsonl"                                                    # exit 0, 26 cases
python3 "$O/escape_probe.py" "$C" "$S/cases"                                          # exit 1: 3 escapes
python3 "$O/exitcode_sim.py" "$C" "$S/cases"                                          # both rc=1, traceback
uv run --with gguf python "$O/invalid_agreement.py" "$C" "$O/invalid-agreement.txt"   # exit 0, agree
```

## 7. Tooling record

- `gguf` 0.19.0, PyPI channel, `uv run --with gguf` (uv 0.13.0; cache-only install) — reason: independent
  GGUF metadata decoder for the 512-entry comparison. No pacman (host-wide pause respected); nothing
  installed into `~/.local/bin` or any other PATH directory.
- Scratch `/fast/scratch/hyaku/kama-r49/X1Gguf` held the model, fixtures and the patched copy; both were
  removed after the artifacts below were copied out.
- Footprint: importing the frozen counter from a script makes CPython write ignored bytecode caches
  (`kama-shokunin/tools/__pycache__/round49-replay-witness-audit.cpython-31{3,4}.pyc`, covered by
  `.gitignore:3`); no tracked lane file was touched (`git status --porcelain tools/` shows only the
  build's own `M tools/append-only-audit.py`). No server was started by this seat; `pgrep -af llama-server`
  shows only another seat's `V1Counter` fixtures.

## 8. Files written

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Gguf/`
(this report: `…/w1/out/X1Gguf.md`) — see `MANIFEST.sha256` for sizes and hashes.
