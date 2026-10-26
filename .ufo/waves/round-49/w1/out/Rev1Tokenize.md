# Rev1Tokenize — /tokenize and /detokenize at llama.cpp caa8191d, and which C1 `observe()` assumptions hold

**Verdict.** The frozen tokenize surface is fully reconstructible from source and confirmed live on b11909:
`piece` is `common_token_to_piece()` with `lstrip=0, special=true` (BYTE → the raw byte, NORMAL → the vocab
text with U+2581 as a space, control/unknown → verbatim text), the leading space is the SPM
`add_space_prefix` prepend in `llama_vocab::impl::tokenize()` (not the UGM normalizer), and `/detokenize`
**does not strip it** because the route concatenates pieces instead of calling `llama_detokenize`.
C1's nonce check therefore holds — 200/200 fresh nonces round-trip as exactly `" " + nonce`, with 0 piece
disagreements against the model's own vocabulary and 0 byte-token uses (ids 261..491) — but of the five
claims inside that check only the *rendering rule* is true by construction; "piece is a JSON string",
"every nonce id maps to the file's token text", "no byte tokens", and "the bare-nonce branch can match"
are **empirical facts about stories260K**, and each of them is falsifiable by one out-of-vocab character
(demonstrated: `智` → 3 disagreements, `😀` → 4). C1 met=True on this model is honest; the docstring's
blanket "U+2581 read as a space" is not a general guarantee.

Commit: `caa8191df159f764fb0160e3d2fc6be008948aee`; the installed binary reports
`version: 0.7.0-dev (build 11909, commit caa8191df)` (`commands.txt` §2), model sha256
`270cba1b…bd256d` = counter `MODEL_SHA` (§3). All line numbers below are that commit's files
(`source-excerpts.md`).

---

## 1. How a `piece` is produced

Route → handler → helper chain:

| step | evidence |
|---|---|
| `POST /tokenize` / `POST /detokenize` registered | `tools/server/server.cpp:200-201` |
| handler body | `tools/server/server-context.cpp:6252-6290` (`post_tokenize`), `6293-6303` (`post_detokenize`) |
| tokenization | `tokenize_mixed()` → `common_tokenize(vocab, s, add_special, parse_special)` — `tools/server/server-common.cpp:988-1017`, `common/common.cpp` `common_tokenize` |
| piece | `common_token_to_piece(ctx_server.vocab, token)` — `server-context.cpp:6265`; default `special = true` (`common/common.h:1180-1189`); calls `llama_token_to_piece(..., lstrip = 0, special)` — `common/common.cpp:1881-1894` |
| rendering | `llama_vocab::impl::token_to_piece()` — `src/llama-vocab.cpp:4064-4191` |

The rendering switch for SPM (stories260K is `LLAMA_VOCAB_TYPE_SPM`: `tokenizer.ggml.model = "llama"`):

* control / unknown / user-defined → the vocab text **verbatim** (`llama-vocab.cpp:4108-4109`), because
  `special=true`; `special=false` would return 0 bytes (`4064-4068`).
* **NORMAL** → the vocab text with `llama_unescape_whitespace()` applied, i.e. every `U+2581` (E2 96 81)
  becomes `' '` (`4111-4114`; helper `3767-3773`).
* **BYTE** → the single raw byte `token_to_byte(token)`, which parses `"<0xNN>"` (`4116-4118`;
  `3565-3582`). This is the branch that can leave the response not-UTF-8.

Then the handler decides the JSON shape (`server-context.cpp:6266-6281`): `piece` is a **string** if
`is_valid_utf8(piece)` (`server-common.cpp:1815`), otherwise a **JSON array of byte values**. Documented in
`tools/server/README.md:686-700` ("The piece field is a string if the piece is valid unicode or a list of
bytes otherwise"). `with_pieces=false` returns bare ids (`6286-6288`).

Live confirmation (b11909, `probe-out.txt`, `probe2-out.txt`):

```
kama witness 771f62308fafbb2f ->
  ids     [409, 314, 412, 263, 275, 416, 406, 419, 410, 491, 491, 475, 431, 490, 479, 472, 477, 487, 431, 412, 431, 430, 430, 479, 431]
  pieces  [" k","am","a"," w","it","n","es","s"," ","7","7","1","f","6","2","3","0","8","f","a","f","b","b","2","f"]
  vocab   ["▁k","am","a","▁w","it","n","es","s","▁","7","7","1","f","6","2","3","0","8","f","a","f","b","b","2","f"]
智  -> ids [410, 233, 156, 189]  pieces [" ",[230],[153],[186]]  vocab ["▁","<0xE6>","<0x99>","<0xBA>"]
😀  -> ids [410, 243, 162, 155, 131] pieces [" ",[240],[159],[152],[128]]
café -> ids [280, 412, 431, 485] pieces [" c","a","f","é"]   (485 is a NORMAL token, not a byte token)
```

## 2. Where the leading space comes from, and who strips it

* **Tokenizer side.** SPM branch of `llama_vocab::impl::tokenize()`: `is_prev_special = true` seeds the
  loop, and the first raw fragment gets `text = ' '` when `add_space_prefix` (`llama-vocab.cpp:3811-3836`),
  then `llama_escape_whitespace()` turns it into `U+2581` (`3841`, helper `3767-3769`) before the SPM
  session tokenizes. `add_space_prefix` is forced `true` for SPM (`2760-2765`) and only overridden by
  `tokenizer.ggml.add_space_prefix` (`2789`); stories260K has no such key (`stories260K-vocab-facts.json`)
  → true. The UGM `normalize()` prepend at `1175-1211` is a *different* tokenizer family and not involved
  (that function belongs to `llm_tokenizer_ugm_session`, `1045`).
* **Piece side.** `U+2581` → `' '` for NORMAL tokens only (`4111-4114`), so the first piece is `" k"`.
* **Detokenize side.** `post_detokenize` calls `tokens_to_str(vocab, tokens)` (`server-context.cpp:6300`),
  which is `ret += common_token_to_piece(ctx, *begin)` over the ids (`server-common.cpp:1719-1734`), i.e.
  **piece concatenation with `special=true`, `lstrip=0`. No whitespace is stripped.** Live:
  `/detokenize` of the nonce ids returns `' kama witness 771f62308fafbb2f'` — exactly one leading space,
  never the bare nonce.
* The library detokenizer *would* strip it: `llama_vocab::impl::detokenize()` sets
  `bool remove_space = add_space_prefix;` ("remove the leading space", `llama-vocab.cpp:4210-4214`) and
  also runs a `clean_spaces` pass. The server route bypasses that entirely, so "detokenize strips the
  leading space" is **false for this endpoint** while being **true for `llama_detokenize`/`common_detokenize`**.
  This is also why `/detokenize` of `[3, 4, 65]` returns raw `'\x00\x01>'` (`probe2-out.txt`) instead of an
  unescaped string.

## 3. C1 `observe()` assumptions: by construction vs empirical

`observe()` = `tools/round49-replay-witness-audit.py:258-289`; the tokenize block is `276-289`.

| # | assumption in the counter | status | evidence |
|---|---|---|---|
| A1 | `{"content","with_pieces":true}` → `tokens[i] = {id, piece}` | **by construction** | `server-context.cpp:6252-6289`; README `686-700` |
| A2 | no BOS prepended (no `add_special` in the body) → ids are the bare tokenization | **by construction** | `add_special` default `false` (`server-context.cpp:6257`), README `692`; live: `add_special:true` prepends id 1 (`probe-out.txt`) |
| A3 | `vocab[id]` from the counter's own GGUF parse is the server's token text for that id | **by construction**, one caveat | ids are the array index: `id_to_token[i].text = gguf_get_arr_str(ctx, token_idx, i)` (`llama-vocab.cpp:2841-2856`); `-m` is hashed to `MODEL_SHA` so the file is identical. Caveat F3 below (empty entries are rewritten, `2846-2849`) — 0 empty tokens here |
| A4 | `piece` is a JSON **string** (`isinstance(t.get("piece"), str)`) | **empirical for this model** | by construction the server emits an int list when the piece is not valid UTF-8 (`6266-6280`); for the nonce that requires a BYTE token ≥ 0x80, and none occurs — 200/200 trials, `byte_token_uses = 0`, ids 261..491 |
| A5 | `vocab[id].replace("\u2581"," ") == piece` | **by construction for NORMAL**; **fails by construction for BYTE** | NORMAL: `4111-4114` + `lstrip=0` (`common/common.cpp:1884`). BYTE: piece is the raw byte (`4116-4118`) while `vocab[id]` is `"<0xNN>"` — the equality is impossible. Reachable only with out-of-vocab input: `智` → 3 disagreements, `😀` → 4 (`probe2-out.txt`, `probe4-out.txt`) |
| A6 | no BYTE token appears in `kama witness <16 hex>` | **empirical for stories260K** | 512-token vocab: 253 NORMAL, 256 BYTE (ids 3..258), 1 UNKNOWN, 2 CONTROL; every char of the nonce alphabet plus `U+2581` (id 410) exists as a NORMAL token (`stories260K-vocab-facts.json`); SPM byte fallback is only reached when no symbol merges to a token (`llama-vocab.cpp:176-196`) |
| A7 | `detokenize(ids) ∈ {nonce, " "+nonce}` | **the `" "` branch by construction; the bare branch is dead** | SPM `add_space_prefix` prepend (`3819, 3831-3834, 2764`); `/detokenize` = piece concat (`server-common.cpp:1719-1734` via `server-context.cpp:6300`), which never strips (`4213-4214` is not reached). Live: dt == `" " + nonce` in 200/200 trials, dt == nonce never |
| A8 | the nonce text contains no literal special-token string | **by construction** of the counter (`f"kama witness {secrets.token_hex(8)}"`, line 276) | `parse_special` defaults `true` (`6258`) but is inert on `[a-z0-9 ]`; even `<s>` round-trips because `special=true` renders it back to `"<s>"` (`probe-out.txt`) |
| A9 | concatenation is lossless, so A7 can hold at all | **by construction** (256 byte tokens make every byte representable; escape/unescape are inverse) | `llama-vocab.cpp:3767-3777`, `4116-4118`; `clean_spaces = false` for SPM (`2765`), and the route never runs `clean_spaces` anyway |

Empirical matrix (one live b11909 server, 200 random nonces, `probe3-out.txt`):

```
{"trials": 200, "fails": 0, "byte_token_uses": 0, "distinct_ids": 34,
 "id_range": [261, 491], "vocab_len": 512, "model_sha_ok": true}
```

## 4. Findings (lane counters are frozen — these are findings, not edits)

**F1 (latent, structural: C1 `observe()` piece predicate is model-dependent).**
`tools/round49-replay-witness-audit.py:280-281` assumes `piece` is a string and equals the vocab text with
`U+2581` replaced. That is only true for NORMAL (and special) tokens; a BYTE piece is the raw byte and is a
byte array when ≥ 0x80. Show it:

```
python3 probe2.py 18101 stories260K.gguf     # [cjk] counter_bad … n_bad 3 ; [emoji] n_bad 4
```

Consequence for C1 as frozen: none — the nonce alphabet is fully covered by NORMAL tokens on stories260K,
so witness legs are not at risk (0 failures in 200 trials). Consequence for reuse: a model whose vocab lacks
any of `[a-z0-9 ]` or the bare `▁` would make the witness leg report a false "pieces disagree" and C1 would
fail for a correct server. Fix (proposed, not applied): `counter-predicate-proposed.diff` — parse
`tokenizer.ggml.token_type` (int32 array) alongside `tokenizer.ggml.tokens`, and compare bytes:

```python
def expected_piece(token_id, text, ttype):
    if text == "":                      # loader rewrites empties (llama-vocab.cpp:2846-2849)
        text = f"[EMPTY_{token_id}]"
    if ttype == 6:                      # BYTE -> "<0xNN>" is the raw byte
        return bytes([int(text[3:5], 16)])
    if ttype == 1:                      # NORMAL -> U+2581 is a space
        return text.replace("\u2581", " ").encode()
    return text.encode()                # CONTROL/UNKNOWN/USER_DEFINED -> verbatim (special=true)
```

with `piece_bytes()` accepting both the str and the int-list form. Verified: the diff applies to the lane
file with `patch -p1` (exit 0), the result compiles (`py_compile`, exit 0) and runs (`--help`, exit 0), gives
0 false positives on `智`/`😀`/mixed, and still flags both forgery controls (a wrong `piece`, a wrong `id`)
— `probe4-out.txt`.

**F2 (latent: `▁` inside a *special* token's text is mis-normalized).** The counter applies
`.replace("\u2581"," ")` to every vocab entry, but `token_to_piece` only unescapes NORMAL tokens
(`llama-vocab.cpp:4108-4109` vs `4111-4114`). A model whose control tokens embed `U+2581` — e.g. CodeLlama's
`▁<PRE>` / `▁<SUF>` / `▁<MID>` specials (`3101, 3123, 3145`) — would make the counter report a mismatch for a
correct server. Not triggered here: stories260K's only specials are `<unk>`, `<s>`, `</s>`, and no
non-NORMAL token contains `U+2581` (`stories260K-vocab-facts.json: tokens_with_u2581_not_normal = []`). Same
fix as F1 (branch on token type).

**F3 (latent: empty vocab entries diverge).** llama.cpp rewrites an empty `tokenizer.ggml.tokens[i]` to
`"[EMPTY_i]"` (`llama-vocab.cpp:2843-2849`), which the counter's raw parse would not. 0 such tokens in
stories260K; covered by the F1 fix.

**F4 (scope note, not a defect: "/detokenize" is not detokenization).** The route concatenates pieces
(`server-context.cpp:6300` → `server-common.cpp:1719-1734`), so what C1 witnesses is *the piece table of the
running server*, not `llama_detokenize` (which would strip the leading space, `llama-vocab.cpp:4210-4214`, and
apply `clean_spaces`). The preregistration sentence "round-trips a fresh nonce through /tokenize and
/detokenize against the model's own vocabulary" is accurate as written, and the counter's `" " + nonce`
tolerance is *required*, not defensive padding — but the bare-`nonce` half of that test can never match on an
SPM model with `add_space_prefix` and should not be read as an independent check. [INFERENCE: the tolerance
was written for exactly this asymmetry; the counter's comment "one leading space allowed" (line 46-47) matches
the observed behaviour rather than a guess.]

**F5 (observation, operability):** `with_pieces` pieces are per-token and can be multi-character
(`"am"`, `"es"`), so any check that reconstructs the text must concatenate in order — the counter does
(`dt`), and the 200-trial matrix confirms byte-exact equality with `" " + nonce`.

## 5. Confidence

* Rendering rules, handler shapes, leading-space origin, detokenize semantics: **high** — four
  independent source files at the frozen commit plus 200 live round-trips on the exact build
  (`commit caa8191df` in `--version`).
* "By construction vs empirical" split for A4/A5/A6: **high** — each empirical item was falsified on purpose
  with `智`/`😀` and each construction item is a single cited branch.
* F2/F3 generality: **high** for the mechanism (source), unverified for other models by definition (no second
  model was run; out of scope for this seat).

## 6. Cleanup / tooling

* No installs, no upgrades: used the pre-existing `python3`, `curl`, `patch`, and the frozen
  `/home/vgpnk/.local/opt/llama-b11909` build.
* Five `llama-server` processes were started, each on a loopback port (18097-18099, 18101, 18102) and killed
  in the same command; `pgrep -af 'llama-server.*18(097|098|099)|llama-server.*1810[0-2]'` → no match. Other
  `llama-server` processes visible in `pgrep` belong to sibling seats (`X1Kill`, `X1Observe`, `S1Gate`,
  `V1Counter`) and were left alone.
* No write to the lane's tools, corpus or jj/git state, none to the fleet repo, none to `~/.local/bin`.
  The only lane-side writes are this report and the artifact directory beside it (the sanctioned out path).
  Scratch `/fast/scratch/hyaku/kama-r49/Rev1Tokenize` was removed after the artifacts below were copied.

## Artifacts

All under `.ufo/waves/round-49/w1/out/Rev1Tokenize/`: `commands.txt`, `source-excerpts.md` (every cited line,
with numbers, from the frozen commit), `stories260K-vocab-facts.json`, `probe.py`, `probe2.py`, `probe3.py`,
`probe4.py`, `probe-out.txt`, `probe2-out.txt`, `probe3-out.txt`, `probe4-out.txt`,
`counter-predicate-proposed.diff`, `gen-patch.py`, `server-version.txt`.
