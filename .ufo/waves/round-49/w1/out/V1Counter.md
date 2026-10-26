# V1Counter — round-49 C1 code review (frozen counter: `kama-shokunin/tools/round49-replay-witness-audit.py`)

Verdict: **No in-scope defect defeats the frozen C1 measurement; review found 2 medium severity latent false-negative risks (listen_inodes() v4-mapped loopback; observe() byte-list pieces), 2 low-severity robustness/control-strength notes, and confirmed every remaining scoped behavior (GGUF spec parse, zombie handling, leading-space rule, release ordering, cap timeout, newrow parse) as correct on minimal fixtures.**

Reviewed file: `tools/round49-replay-witness-audit.py` (475 lines). Verified identical to the frozen preregistration revision: `git -C $S/lane show 36d5ed2681111b68c180f8ab1646d8dc9beaedee:tools/round49-replay-witness-audit.py`differs the clone copy → `IDENTICAL to frozen`.

All fixtures ran in `S=/fast/scratch/hyaku/kama-r49/V1Counter` (TMPDIR=$S). Driver scripts and outputs are copied to `.ufo/waves/round-49/w1/out/V1Counter/`.

---

## Findings (by severity)

### F1 — MEDIUM (latent false negative): `listen_inodes()` rejects IPv4-mapped loopback, diverging from the harness's own listener helper
- **File:line** `tools/round49-replay-witness-audit.py:208-209` (address whitelist `("0100007F", "00000000000000000000000001000000")`).
- **Evidence** `drv_listen.py` (out/listen.txt): four real listeners inspected against both C1's `listen_inodes()` and the live tool's `_listen_inodes()` (kama-llamacpp-live.py:508-564):
  - `tcp4 127.0.0.1`: st=0A addr=0100007F → C1 `['620977903']` ✓ (accepted)
  - `tcp6 ::1 V6ONLY=1`: st=0A addr=00000000000000000000000001000000 → C1 `['620977904']` ✓
  - `tcp6 :: dual-stack V6ONLY=0`: addr=00000000000000000000000000000000 (wildcard) → C1 `[]`, live `[]` (both fail-closed — okay)
  - `tcp6 ::ffff:127.0.0.1` (v4-mapped loopback): addr=00000000000000FFFF00000100007F → **C1 `[]`**, live `['620977906']`.
- **Interpretation** The counter's whitelist does not recognize IPv4-mapped loopback, while the lane's own harness helper (`_tcp6_is_loopback`, kama-llamacpp-live.py:508-522) does. In the frozen flow this cannot fire: the live tool hardcodes `--host 127.0.0.1` (kama-llamacpp-live.py:1707), which produces an AF_INET socket visible in `/proc/net/tcp` (accepted). It becomes a false negative only if the server ever binds on an AF_INET6 socket on the mapped address or `::1` isn't the sole loopback form. Risk is latent, not currently triggered.
- **Proposed fix** align C1 with the harness semantics: accept `::ffff:127/8` (`address[:12] == b'\0'*10 + b'\xff\xff' and address[12] == 127`) and any 127/8 for tcp4 (`addr[-2:].upper() == '7F'`), while still rejecting wildcard `::`/`0.0.0.0` (fail-closed). Suggested replacement for lines 208-209:
  ```python
  if len(addr) == 8:
      ok = addr[-2:].upper() == "7F"          # any 127/8, little-endian
  else:
      raw = bytes.fromhex(addr) if len(addr) == 32 else b""
      # reverse each 32-bit word -> network order
      words = [raw[i:i+4][::-1] for i in range(0, 16, 4)]
      net = b"".join(words)
      ok = (net == b"\0"*15 + b"\1") or (net[:12] == b"\0"*10 + b"\xff\xff" and net[12] == 127)
  ```

### F2 — MEDIUM (latent false negative): `observe()` expects `piece` to be a `str`; the cited README documents byte-list pieces for non-unicode text
- **File:line** `tools/round49-replay-witness-audit.py:280-281` (`isinstance(t.get("piece"), str)` gate).
- **Evidence** the sourced README (llama.cpp tools/server/README.md @ caa8191d) line 700: *"The piece field is a string if the piece is valid unicode or a list of bytes otherwise"*, with the concrete example for input `á` (lines 721-728): `{"id":198,"piece":[195]}, {"id":164,"piece":[161]}`. Verified against the real frozen server (drv_observe_real.py, out/observe_real.txt): ASCII nonce `kama witness a0f13eee7bced799` → 23 tokens, every `piece` a string, counter `bad` list empty; `á` → `{'id':198,'piece':[195]}`, `{'id':164,'piece':[161]}` — `isinstance(..., str)` False.
- **Interpretation** the nonce is ASCII-only (`f"kama witness {secrets.token_hex(8)}"`, line 276), so all pieces ARE strings and the leg is unaffected today. But the comparison is not robust to the *documented* API shape: any non-ASCII byte in the nonce would turn pieces into byte-lists and the counter would record a false "tokenize pieces disagree" failure; Unicode normalization differences (NFC/NFD) would likewise false-negative. The seat's suspicion is confirmed: **a nonce with non-ASCII would fail**.
- **Proposed fix** keep the ASCII hex nonce (already the case) and either (a) drop byte-list pieces into `bytes(piece).decode("utf-8","replace")` before comparing, or (b) add a comment + guard that the nonce must remain ASCII so the `str`-piece assumption is enforced by construction.

### F3 — LOW: `gguf_tokens()` has no read-bound checks; oversized declared string lengths silently truncate
- **File:line** `tools/round49-replay-witness-audit.py:157-159` (`rstr` slices `data[o+8:o+8+n]`; slicing clamps, no error).
- **Evidence** drv_gguf.py: an array entry declaring a 999999-byte string with only `ab` present parses successfully to `['ab']` (out/gguf.txt `trunc: parsed without error -> ['ab']`). Header/type/version handling all correct: v2 & v3 parse, v1 rejected (`GGUF v1 unsupported`), non-GGUF rejected, missing `tokenizer.ggml.tokens` rejected, wrong array element type rejected, unknown GGUF value type 13 rejected.
- **Interpretation** only reachable with a corrupt/forged model. The model download is SHA-256 gated (lines 442-446) before parsing, so this is not externally exploitable in the frozen flow; still a robustness gap — a truncated download would silently parse garbage instead of failing the leg with a clear error.
- **Proposed fix** in `rstr`, raise `EvalError("GGUF truncated")` when `o + 8 + n > len(data)`.

### F4 — LOW (control-strength): `cap_leg()`'s positive control passes even when the stub server is executed but the live tool then fails
- **File:line** `tools/round49-replay-witness-audit.py:386-387` — `good_case = executed and not (isinstance(err, str) and err.startswith("provenance-"))`.
- **Evidence** drv_cap.py (out/cap.txt), fake LIVE stub:
  - `good-fail` mode (executes the stub server, then exits 1 with `setup_error: internal:boom`): control reports **ok** (`executed=True`).
  - `bomb` mode with `setup_error: provenanceance-member-sparse`, exit 2, not executed → `ok` (refusal correctly graded).
  - `slow` mode (sleeps 45 s): `subprocess.run(..., timeout=30)` → `code=None` → both cases FAIL (exit None, executed=False, seconds=30.0; total 60.1 s for the two runs) — **timeout handling works as intended**.
- **Interpretation** the control matches the documented intent ("the stub is executed, its marker written", docstring lines 58-60), but it does not require the live tool to succeed overall; any non-`provenance-` error after execution still counts as a pass. Not a correctness bug in the frozen counter, but a weaker positive control than "verification passes and the tool completes". Note the real LIVE tool's own checks (outcome/checks) are what the replay leg grades; this only affects the cap leg's control strictness.
- **Proposed fix (optional)** require `code == 0` and `err is None` for the positive control.

### F5 — INFO: `witness_one()` release ordering — release is always written, leg still fails correctly
- **File:line** `tools/round49-replay-witness-audit.py:312-313` (unconditional release write), 306-311; post-checks 327-332.
- **Evidence** drv_witness_order.py (out/witness_order.txt) with a stub replay:
  - `no-ready` (replay exits 0, never writes ready.json): detail `no ready.json (replay exit 0)`, leg returns False; **release file exists** afterward in `wd-no-ready/`.
  - `bad-ready` (ready.json points at a sleeping dummy pid on a closed port): observe() records `exe sha256 ... is not the frozen server`, `no LISTEN socket ... owned by pid`, `cmdline unreadable: list.index(x)`, `nonce round-trip failed: Connection refused`, plus `server still alive or port still accepting after the replay exited`; leg returns False; release exists in `wd-bad-ready/`.
- **Interpretation** writing `release` even when the witness failed is safe: the failure is retained in `probs`, flows into `detail`, and makes `witness_one` return False, so `met` stays False. The release only tells the replay to tear down (matching the live tool's hold loop, kama-llamacpp-live.py:280-300). One note: the post-exit aliveness check uses `pid_alive(ready["pid"])` only; there is no lineage check that `ready["pid"]` belongs to the replay's process tree — but the exe/listen/model/nonce gates are the decision, so this is not an integrity hole. No defect found.

### F6 — INFO: `newrow_leg()` row parser superset/superset behavior
- **File:line** `tools/round49-replay-witness-audit.py:395-400` (`ln.lstrip(" ")[:3] == "| S"` and `[3:4].isdigit()`).
- **Evidence** drv_newrow.py (out/newrow.txt): synthetic lines matched with 0/1/2/3 and even 4 leading spaces (`lstrip` strips all; superset of the stated 0-3); tab-indented rows (`\t| S499`) and `|S`-with-no-space rows are **not** matched; `| S12a` matched (digit check only on the first id char). Real repo run on the lane clone: `newrow: 2 rows new since base; 1 name the README at caa8191df159 and /tokenize: ['| S494 |']` → `hit=True` (S494 row present, as expected; S495 is the `proc_pid_exe(5)` row without `/tokenize`).
- **Interpretation** the parser matches the actual SOURCES.md format (columns like `| S494 | …`). No defect in scope.

### F7 — INFO: `pid_alive()` zombie handling and `observe()` leading-space rule verified
- **File:line** `tools/round49-replay-witness-audit.py:229-235` (`state not in ("Z","X")`) and 284-286 (`dt not in (nonce, " " + nonce)`).
- **Evidence** drv_pid.py: normal sleeping child → True; zombie (state Z) → False; after reap → False; comm containing `)` (`comm='a)b'`) parses via `rsplit(")",1)` → True. drv_observe_real.py against the real b11909 server + frozen model: `/tokenize` returns 23 tokens, all pieces strings and all equal to `vocab[id].replace("▁"," ")`; `/detokenize` content is `' kama witness a0f13eee7bced799'` = `" " + nonce` → exactly **one** leading space is produced and accepted. The single-leading-space rule matches real server behavior.

---

## Positive verification (no defect found)

- **GGUF spec conformance** (`gguf_tokens`, lines 144-189): magic+version+n_tensors+n_kv offsets (24-byte header) correct; value-type sizes match the GGUF enum (0-12: 1,1,2,2,4,4,4,1,string,array,8,8,8); array header `u32 et + u64 n`; nested array skip recurses; v2/v3 parse, v1 rejected. KV alignment correctly not applied (GGUF has none).
- **`listen_inodes()` parsing**: state `0A`, local-address/port split, inode field index 9 all correct for tcp and tcp6; wildcard `::`/`0.0.0.0` consistently fail-closed in both the counter and the harness.
- **`cap_leg()` timeout**: 30s `subprocess.run` timeout path turns into `code=None` → FAIL (verified with the slow stub).
- **`observe()` exception handling**: `OSError/ValueError/KeyError/TypeError` cover JSON decode (`JSONDecodeError` ⊂ ValueError), missing keys, and connection failures; `nonce` is always bound before the detail line that prints it (no `UnboundLocalError`).

## Residual risks / verification gaps

- The full C1 end-to-end measurement (3 replays, ~75 MB each) was not re-run by this seat; L1's dry run already reported `witness=1 cap=1 newrow=1 witnessed=3/3 met=True`. This review validates each code path individually on fixtures and against the real server.
- `cap_leg` was exercised with a stub LIVE tool (counter-side code under test), not the shipped live tool; the timeout and control logic is what was being verified.
- F1/F2 are latent: they require a change in how the server binds or a non-ASCII nonce — neither occurs in the frozen flow.

## Evidence files (copied to `.ufo/waves/round-49/w1/out/V1Counter/`)
`gguf.txt`, `listen.txt`, `pid.txt`, `observe_real.txt`, `witness_order.txt`, `cap.txt`, `newrow.txt`, driver scripts `drv_*.py`, `readme_tokenize_lines686-729.txt` (sourced README excerpt).
