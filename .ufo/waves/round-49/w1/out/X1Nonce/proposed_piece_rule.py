def piece_want(tok):
    """Expected `piece` for one GGUF vocabulary entry: a byte-fallback entry
    <0xXX> is rendered by the server as that single byte; any other entry is
    its text with U+2581 read as a space."""
    if len(tok) == 6 and tok.startswith("<0x") and tok.endswith(">"):
        try:
            return bytes([int(tok[3:5], 16)])
        except ValueError:
            return None
    return tok.replace("\u2581", " ")


def piece_matches(t, vocab):
    tid = t.get("id")
    if not isinstance(tid, int) or not 0 <= tid < len(vocab):
        return False
    want = piece_want(vocab[tid])
    if want is None:
        return False
    piece = t.get("piece")
    if isinstance(want, bytes):
        got = bytes(piece) if isinstance(piece, list) else (
            piece.encode("utf-8", "surrogateescape") if isinstance(piece, str) else None)
    else:
        got = piece if isinstance(piece, str) else None
    return got == want
