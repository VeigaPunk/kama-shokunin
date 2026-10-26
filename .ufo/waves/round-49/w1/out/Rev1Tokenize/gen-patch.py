"""Regenerate the proposed counter patch: orig = lane tool, new = fixed predicate."""
import difflib, pathlib
src = pathlib.Path("patched/tools/orig.py").read_text().splitlines(keepends=True)

def sub(old, new, count=1):
    global src
    text = "".join(src)
    assert text.count(old) == count, (text.count(old), old[:60])
    src = text.replace(old, new).splitlines(keepends=True)

sub('''def gguf_tokens(path):
    """tokenizer.ggml.tokens of a GGUF v2/v3 file, decoded by this counter."""''',
'''def gguf_vocab(path):
    """(tokenizer.ggml.tokens, tokenizer.ggml.token_type) of a GGUF v2/v3 file.

    token_type is llama_token_type (1 NORMAL, 2 UNKNOWN, 3 CONTROL,
    4 USER_DEFINED, 6 BYTE); absent means every token is NORMAL, which is how
    llama.cpp reads it (src/llama-vocab.cpp:2858-2862 at the frozen commit).
    """''')

sub('''    for _ in range(nkv):
        key, off = rstr(off)
        t = struct.unpack_from("<I", data, off)[0]
        off += 4
        if key == "tokenizer.ggml.tokens" and t == 9:
            et, n = struct.unpack_from("<IQ", data, off)
            off += 12
            if et != 8:
                raise EvalError("tokens array is not strings")
            out = []
            for _ in range(n):
                s, off = rstr(off)
                out.append(s)
            return out
        off = skip(t, off)
    raise EvalError("tokenizer.ggml.tokens absent")''',
'''    tokens = types = None
    for _ in range(nkv):
        key, off = rstr(off)
        t = struct.unpack_from("<I", data, off)[0]
        off += 4
        if key == "tokenizer.ggml.tokens" and t == 9:
            et, n = struct.unpack_from("<IQ", data, off)
            off += 12
            if et != 8:
                raise EvalError("tokens array is not strings")
            tokens = []
            for _ in range(n):
                s, off = rstr(off)
                tokens.append(s)
            continue
        if key == "tokenizer.ggml.token_type" and t == 9:
            et, n = struct.unpack_from("<IQ", data, off)
            off += 12
            if et not in (4, 5):        # GGUF stores token_type as int32
                raise EvalError("token_type array is not int32")
            types = list(struct.unpack_from(f"<{n}{'I' if et == 4 else 'i'}", data, off))
            off += 4 * n
            continue
        off = skip(t, off)
    if tokens is None:
        raise EvalError("tokenizer.ggml.tokens absent")
    if types is None or len(types) != len(tokens):
        types = [1] * len(tokens)
    return tokens, types''')

sub('''def observe(pid, port, vocab, probs):''',
'''def piece_bytes(piece):
    """A /tokenize piece as bytes; the server sends a list of byte values when the
    piece is not valid UTF-8 (tools/server/server-context.cpp:6266-6280)."""
    if isinstance(piece, str):
        return piece.encode()
    if isinstance(piece, list) and piece and all(isinstance(b, int) and 0 <= b < 256 for b in piece):
        return bytes(piece)
    return None


def expected_piece(token_id, text, ttype):
    """The piece the server must return for this token.

    common_token_to_piece() renders with lstrip 0 and special true
    (common/common.cpp:1881-1894); llama_vocab::token_to_piece() then emits the raw
    byte for BYTE (src/llama-vocab.cpp:4116-4118), the text with U+2581 as a space
    for NORMAL (4111-4114), and the text verbatim for special/user-defined tokens
    (4108-4109).  The loader rewrites empty vocab entries (2846-2849).
    """
    if text == "":
        text = f"[EMPTY_{token_id}]"
    if ttype == 6:
        try:
            return bytes([int(text[3:5], 16)])
        except ValueError:
            return None
    if ttype == 1:
        return text.replace("\\u2581", " ").encode()
    return text.encode()


def observe(pid, port, vocab, types, probs):''')

sub('''        bad = [t for t in tk if not (isinstance(t.get("piece"), str) and 0 <= t["id"] < len(vocab)
                                     and vocab[t["id"]].replace("\\u2581", " ") == t["piece"])]''',
'''        bad = [t for t in tk if not (isinstance(t.get("id"), int) and 0 <= t["id"] < len(vocab)
                                     and piece_bytes(t.get("piece")) is not None
                                     and piece_bytes(t.get("piece")) == expected_piece(
                                         t["id"], vocab[t["id"]], types[t["id"]]))]''')

sub('''def witness_one(tree, rpath, S, tag, env, vocab, detail):''',
'''def witness_one(tree, rpath, S, tag, env, vocab, types, detail):''')
sub('''            nonce = observe(pid, port, vocab, probs)''',
'''            nonce = observe(pid, port, vocab, types, probs)''')
sub('''        vocab = None
        try:''', '''        vocab = types = None
        try:''')
sub('''                vocab = gguf_tokens(model)''', '''                vocab, types = gguf_vocab(model)''')
sub('''                witnessed += witness_one(tree, os.path.join(tree, path), S, f"w{n}", env, vocab, detail)''',
'''                witnessed += witness_one(tree, os.path.join(tree, path), S, f"w{n}", env, vocab, types, detail)''')

new = "".join(src)
pathlib.Path("patched/tools/new.py").write_text(new)
pathlib.Path("counter-predicate-proposed.diff").write_text("".join(difflib.unified_diff(
    pathlib.Path("patched/tools/orig.py").read_text().splitlines(keepends=True),
    new.splitlines(keepends=True),
    fromfile="a/tools/round49-replay-witness-audit.py",
    tofile="b/tools/round49-replay-witness-audit.py", n=3)))
print("wrote counter-predicate-proposed.diff")
