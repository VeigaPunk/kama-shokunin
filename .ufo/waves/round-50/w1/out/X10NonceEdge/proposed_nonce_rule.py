"""Proposed hardening of the C1 counter's nonce rule - NOT applied (the counter is frozen).

Evaluated offline against the 80 stored nonce rows of seats X10NonceEdge's two witnessed
replays; see vocab-analysis.json `proposed_rule_eval`. The diff in the report replaces
tools/round50-replay-bind-audit.py:362-370 (observe()).
"""
import re

BYTE_TOKEN = re.compile(r"^<0x([0-9A-Fa-f]{2})>$")
SENTINEL = "\u2581"


def piece_bytes(piece):
    """Wire bytes of one with_pieces token: JSON string, or byte-fallback int array."""
    if isinstance(piece, list):
        if piece and all(isinstance(b, int) and 0 <= b < 256 for b in piece):
            return bytes(piece)
        raise ValueError(f"piece array is not bytes: {piece!r}")
    if isinstance(piece, str):
        return piece.encode("utf-8")
    raise ValueError(f"piece is neither a string nor a byte array: {piece!r}")


def piece_ok(t, vocab):
    """True when the wire bytes are the model's own piece for pin id.

    Text tokens: the GGUF string with U+2581 standing for a space (the server sends
    either form). Byte/control tokens: the GGUF stores '<0xNN>' while the server sends
    the raw byte, as a JSON string (control) or an int array (byte fallback).
    """
    tid, piece = t.get("id"), t.get("piece")
    if not isinstance(tid, int) or not 0 <= tid < len(vocab):
        return False
    wire = piece_bytes(piece)
    packed = vocab[tid]
    m = BYTE_TOKEN.match(packed)
    if m:
        return wire == bytes([int(m.group(1), 16)])
    return wire in (packed.replace(SENTINEL, " ").encode("utf-8"), packed.encode("utf-8"))


def nonce_ok(tokens, vocab, nonce):
    """The full rule: every piece is the model's piece for its id, and the pieces
    concatenate to the nonce (server prepends one space). Order-sensitive."""
    if not tokens or not all(piece_ok(t, vocab) for t in tokens):
        return False
    try:
        joined = b"".join(piece_bytes(t.get("piece")) for t in tokens)
    except ValueError:
        return False
    return joined in (nonce.encode("utf-8"), b" " + nonce.encode("utf-8"))
