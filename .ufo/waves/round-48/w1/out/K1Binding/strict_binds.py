"""Proposed stricter declaration-binding rule for append-only-audit v3 / C1.

Replaces binds() in tools/append-only-audit.py and tools/round48-append-audit-v3-check.py.
Same signature. Differences from the shipped rule:
  1. phrase must be word-bounded: `append-only` / `append only` not embedded in a
     longer token;
  2. the four fixed negation substrings are kept, and any negation word within
     24 chars BEFORE the phrase also rejects (closes 'not an append-only',
     'isn't append-only', 'never been append-only', ...);
  3. the token must appear as a WHOLE WORD (not a substring), closing 'log' in
     'chronological'/'catalog', 'sources' in 'resources', 'quality' in 'equality';
  4. exact (wildcard-free) self-declaration is kept: a line inside the very file
     it declares still binds without naming the token;
  5. wildcard patterns need the family token as a whole word, closing the
     self-declaration loophole where any line inside any matched file bound the
     whole pattern (e.g. corpus/lessons/*.md bound by a local sentence).
Optional extension (not in the probe): accept 'appended only'/'appended-only'
as positive phrase forms (see KQ67: corpus/QUALITY.md:387).
"""
import fnmatch, re

NEG = ("not append-only", "not append only", "no longer append", "never append-only")
NEG_WORDS = r"\b(?:not|never|no longer|isn'?t|aren'?t|wasn'?t|weren'?t|hasn'?t|don'?t|doesn'?t)\b"

def row_token(pattern):
    parts = pattern.split("/")
    base = parts[-1]
    if any(ch in base for ch in "*?["):
        return parts[-2] if len(parts) > 1 else ""
    return base.rsplit(".", 1)[0] if "." in base else base

def binds(text, pattern, decl_path):
    if text is None:
        return False
    low = text.lower()
    m = re.search(r"(?<![a-z0-9])append[- ]only(?![a-z0-9])", low)
    if not m:
        return False
    if any(n in low for n in NEG):
        return False
    if re.search(NEG_WORDS, low[max(0, m.start() - 24):m.start()]):
        return False
    if not any(ch in pattern for ch in "*?[") and fnmatch.fnmatchcase(decl_path, pattern):
        return True
    tok = row_token(pattern).lower()
    if not tok:
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(tok) + r"(?![a-z0-9])", low) is not None
