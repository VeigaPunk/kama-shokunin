#!/usr/bin/env python3
"""M3Tool mutant generator: apply one anchored edit each to pristine.py."""
import hashlib
import os
import sys

S = "/fast/scratch/hyaku/kama-r50/M3Tool"
PRISTINE = os.path.join(S, "pristine.py")
OUT = os.path.join(S, "mutants")

# (id, category, old, new, one-line rationale)
MUTS = [
    # ---- fence_open: indentation, run length, char class, info-string ----
    ("M01", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ {0,4}(`{3,}|~{3,})(.*)$", ln)',
     "4-space indent opens a fence (spec: 0-3)"),
    ("M02", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ *(`{3,}|~{3,})(.*)$", ln)',
     "any indentation opens a fence"),
    ("M03", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ {0,3}(`{2,}|~{2,})(.*)$", ln)',
     "2-char run opens a fence (spec: >=3)"),
    ("M04", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ {0,3}(`{4,}|~{4,})(.*)$", ln)',
     "4+ chars required to open (3-char fences no longer open)"),
    ("M05", "fence_open",
     'if run[:1] == b"`" and b"`" in m.group(2):',
     'if run[:1] == b"`" and b"~" in m.group(2):',
     "backtick fence with backtick in info string opens (spec: may not)"),
    ("M06", "fence_open",
     'if run[:1] == b"`" and b"`" in m.group(2):',
     'if run[:1] == b"`" and b"`" not in m.group(2):',
     "polarity flipped: backtick fence opens only with a backtick in info"),
    ("M07", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ {0,3}(`{3,})(.*)$", ln)',
     "tilde fences never open"),
    ("M49", "fence_open",
     're.match(rb"^ {0,3}(`{3,}|~{3,})(.*)$", ln)',
     're.match(rb"^ {0,3}(~{3,}|`{3,})(.*)$", ln)',
     "alternation order swapped (expected equivalent)"),
    # ---- fence_close: length, indent, char, trailing ----
    ("M08", "fence_close",
     "if len(ln) - len(s) > 3:",
     "if len(ln) - len(s) > 2:",
     "3-space-indented line cannot close (spec: up to three)"),
    ("M09", "fence_close",
     "if len(ln) - len(s) > 3:",
     "if len(ln) - len(s) > 99:",
     "any indentation closes a fence"),
    ("M10", "fence_close",
     "return k >= n and s[k:].strip(b\" \\t\") == b\"\"",
     "return k > n and s[k:].strip(b\" \\t\") == b\"\"",
     "equal-length closer fails (spec: at least as many)"),
    ("M11", "fence_close",
     "return k >= n and s[k:].strip(b\" \\t\") == b\"\"",
     "return k == n and s[k:].strip(b\" \\t\") == b\"\"",
     "longer closer fails (spec: at least as many)"),
    ("M12", "fence_close",
     "k = len(s) - len(s.lstrip(ch))",
     "k = len(s) - len(s.lstrip(b\"`~\"))",
     "either char closes either fence (spec: same char)"),
    ("M13", "fence_close",
     "return k >= n and s[k:].strip(b\" \\t\") == b\"\"",
     "return k >= n",
     "trailing junk after closing run still closes"),
    ("M14", "fence_close",
     "return k >= n and s[k:].strip(b\" \\t\") == b\"\"",
     "return k >= n and s[k:].strip(b\" \") == b\"\"",
     "tab after closer is not allowed (spec allows space or tab)"),
    ("M50", "fence_close",
     "if len(ln) - len(s) > 3:",
     "if len(ln) - len(s) > 4:",
     "4-space-indented line still closes (spec: up to three)"),
    # ---- sections(): fence state machine, heading tests ----
    ("M15", "sections",
     """        if fence is not None:
            if fence_close(b, fence):
                fence = None
        else:""",
     """        if fence is not None:
            if fence_close(b, fence):
                fence = None
            elif b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()
        else:""",
     "F4 reintroduced: ## inside a fence re-titles following lines"),
    ("M16", "sections",
     '            elif b.startswith(b"## "):',
     '            if b.startswith(b"## "):',
     "elif -> if inside else-branch (expected equivalent)"),
    ("M17", "sections",
     """            fo = fence_open(b)
            if fo is not None:
                fence = fo
            elif b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()""",
     """            if b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()
            else:
                fo = fence_open(b)
                if fo is not None:
                    fence = fo""",
     "heading tested before fence-open (expected equivalent: ## cannot open)"),
    ("M18", "sections",
     '        b = line.rstrip(b"\\r")',
     '        b = line',
     "CR not stripped before fence/heading tests: CRLF fences never close"),
    ("M19", "sections",
     'elif b.startswith(b"## "):',
     'elif b.startswith(b"##"):',
     "##x and ### lines also become titles"),
    ("M20", "sections",
     'elif b.startswith(b"## "):',
     'elif b.lstrip(b" ").startswith(b"## "):',
     "indented ## lines become titles"),
    ("M21", "sections",
     """            elif b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()
        out.append(title)""",
     """            elif b.startswith(b"## "):
                title = b.decode("utf-8", "replace").rstrip()
            out.append(title)""",
     "fence lines get no sections entry: title list misaligns with body"),
    ("M22", "sections",
     'title = b.decode("utf-8", "replace").rstrip()\n        out.append(title)',
     'title = b.decode("utf-8", "replace")\n        out.append(title)',
     "title keeps trailing blanks/tabs (spec strips)"),
    # ---- key(): CRLF normalization ----
    ("M23", "key",
     'return ln[:-1] if ln.endswith(b"\\r") else ln',
     'return ln',
     "F5 reintroduced: raw bytes as origin key"),
    ("M24", "key",
     'return ln[:-1] if ln.endswith(b"\\r") else ln',
     'return ln.rstrip(b"\\r")',
     "all trailing CRs removed (spec: exactly one)"),
    ("M25", "key",
     'return ln[:-1] if ln.endswith(b"\\r") else ln',
     'return ln.rstrip(b" \\t\\r")',
     "trailing blanks folded into the key as well"),
    ("M26", "key",
     'return ln[:-1] if ln.endswith(b"\\r") else ln',
     'return ln[:64]',
     "key truncated to 64 bytes (collision-prone)"),
    # ---- origins(): births, parents, pkeys, skips ----
    ("M27", "origins",
     "orig[k].add(t)",
     "orig[k] = {t}",
     "F3 reintroduced: last rev-list birth wins instead of union"),
    ("M28", "origins",
     "if k not in pkeys:",
     "if k in pkeys:",
     "birth polarity inverted: only keys a parent already holds are births"),
    ("M29", "origins",
     'for q in (parents[x] or "").split():',
     'for q in []:',
     "parents ignored: every blob is a birth of all its keys"),
    ("M30", "origins",
     "if pkeys is keys:",
     "if pkeys == keys:",
     "identity skip weakened to equality (expected equivalent)"),
    ("M31", "origins",
     "            if pkeys is keys:\n                continue\n",
     "",
     "unchanged-blob skip removed (expected equivalent: per-key test)"),
    ("M32", "origins",
     "                    pkeys = keys\n                    break\n",
     "                    pkeys = keys\n",
     "early break on identical parent blob removed (expected equivalent)"),
    ("M33", "origins",
     "            if b is None:\n                continue\n",
     "",
     "absent-blob skip removed (expected equivalent: empty body)"),
    ("M34", "origins",
     "        for x in commits:\n            b = bl[f\"{x}:{f}\"]",
     "        for x in reversed(commits):\n            b = bl[f\"{x}:{f}\"]",
     "birth scan order reversed (equivalent under union; contrast M27)"),
    ("M35", "origins",
     "for ln, t in zip(body, sections(body)):",
     "for ln, t in zip(body[1:], sections(body)):",
     "section titles shifted one line earlier in origin birth scan"),
    ("M36", "origins",
     "for ln, t in zip(body, sections(body)):",
     "for ln, t in zip(sections(body), body):",
     "zip operands swapped (str/bytes type confusion)"),
    ("M37", "origins",
     'for q in (parents[x] or "").split():',
     'for q in _text(repo_path, "show", "-s", "--pretty=%P", x).split():',
     "REPAIR-MUTANT: union ALL parents (line 470 keeps only parts[1]); "
     "predicted equivalent on counter fixtures = latent defect unpinned"),
    # ---- body_of cache ----
    ("M38", "body_of",
     "keyset_cache[b] = (body, {key(x) for x in body})",
     "keyset_cache[b] = (body, set(body))",
     "keyset holds raw lines, not keys (CRLF parent lines -> phantom births)"),
    ("M39", "body_of",
     "keyset_cache[b] = (body, {key(x) for x in body})",
     "keyset_cache[b] = (body, set())",
     "keyset always empty: every blob is a birth of all its keys"),
    ("M40", "body_of",
     "keyset_cache[b] = (body, {key(x) for x in body})",
     "keyset_cache[b] = ({key(x) for x in body}, body)",
     "cache tuple swapped (crash on key(str))"),
    # ---- ungraded eligibility test ----
    ("M41", "ungraded",
     "if s in eligible and org.get(key(text), frozenset()) & titles:",
     "if s in eligible:",
     "origin clause dropped: v3 carve-out (selftest pins it)"),
    ("M42", "ungraded",
     "if s in eligible and org.get(key(text), frozenset()) & titles:",
     "if s is not None and org.get(key(text), frozenset()) & titles:",
     "parent-section eligibility dropped: exempt origin ungrades anywhere"),
    ("M43", "ungraded",
     "org.get(key(text), frozenset()) & titles:",
     "org.get(key(text), frozenset()) & eligible:",
     "origin must intersect eligible titles, not all exempt titles"),
    ("M44", "ungraded",
     ">= pcount[t]}",
     "> pcount[t]}",
     "eligibility requires strict growth (spec: >= parent count)"),
    ("M45", "ungraded",
     "s = psec[pos - 1]",
     "s = psec[pos]",
     "deleted line attributed to next line's section (off-by-one)"),
    ("M51", "ungraded",
     "if s in eligible and org.get(key(text), frozenset()) & titles:",
     "if s in eligible and not (org.get(key(text), frozenset()) & titles):",
     "origin clause negated: only non-exempt-born lines ungraded"),
    # ---- definition string ----
    ("M46", "definition",
     '"schema": SCHEMA, "definition": "v5"',
     '"schema": SCHEMA, "definition": "v4"',
     "receipt claims v4 semantics (predicted survivor: nothing pins it)"),
    # ---- selftest registration ----
    ("M47", "selftest",
     '("launder-through-head", t_launder_through_head)',
     '("launder-through-head", t_dated_rewritten)',
     "v4 launder case swapped for a weaker case; registration unpinned"),
    ("M48", "selftest",
     '("origin-multi-title", t_origin_multi_title),',
     "",
     "v4 origin case de-registered; case count unpinned"),
]


def main():
    src = open(PRISTINE).read()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for mid, cat, old, new, why in MUTS:
        n = src.count(old)
        if n != 1:
            print(f"ANCHOR-FAIL {mid}: anchor occurs {n}x", file=sys.stderr)
            return 1
        body = src.replace(old, new)
        path = os.path.join(OUT, f"{mid}_{cat}.py")
        with open(path, "w") as fh:
            fh.write(body)
        h = hashlib.sha256(body.encode()).hexdigest()
        rows.append(f"{mid}\t{cat}\t{h}\t{why}")
        compile(body, path, "exec")  # syntax check
    with open(os.path.join(S, "mutants.tsv"), "w") as fh:
        fh.write("id\tcategory\tsha256\tchange\n" + "\n".join(rows) + "\n")
    print(f"{len(rows)} mutants written to {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
