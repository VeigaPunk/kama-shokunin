import os, re, subprocess, sys
S = os.environ["TMPDIR"]
SRC = open(os.path.join(S, "work/before.py")).read()
M = [
 ("m01 threshold <=", "            if ns[f] < threshold:\n                continue", "            if ns[f] <= threshold:\n                continue"),
 ("m02 zero-guard", "            if ns[f] < threshold:\n                continue", "            if 0 < ns[f] < threshold:\n                continue"),
 ("m03 deleted=graded", '"deleted": len(dl), "graded": ng', '"deleted": ng, "graded": ng'),
 ("m04 restored off-by-one", 'status = "restored" if best == ng', 'status = "restored" if best == ng - 1'),
 ("m05 restored_by ungraded", "                if by is None and ng and h == ng:", "                if by is None and h == ng:"),
 ("m06 no ungraded status", '            if ng == 0:\n                status = "ungraded"', '            if ng == 0:\n                status = "restored"'),
 ("m07 eligible >", "                        >= pcount[t]}", "                        > pcount[t]}"),
 ("m08 titles not eligible", "                if s in eligible:\n                    continue", "                if s in titles:\n                    continue"),
 ("m09 only contains", 'if prefixes and not any(s is not None and s.startswith(q) for q in prefixes):', 'if prefixes and not any(s is not None and q in s for q in prefixes):'),
 ("m10 section ## -> #", '        if line.startswith(b"## "):', '        if line.startswith(b"# "):'),
 ("m11 section no rstrip", 'title = line.rstrip(b"\\r").decode("utf-8", "replace").rstrip()', 'title = line.decode("utf-8", "replace")'),
 ("m12 split keeps final", '    if segs and segs[-1] == b"":\n        segs.pop()', '    if False:\n        segs.pop()'),
 ("m13 K no subtraction", "            K = r.lines(pb) - D", "            K = r.lines(pb)"),
 ("m14 no clamp", "max(0, M[l] - K[l])", "(M[l] - K[l])"),
 ("m15 set not multiset", "sum(min(n, max(0, M[l] - K[l])) for l, n in G.items())", "sum(max(0, M[l] - K[l]) for l in G)"),
 ("m16 short window", "            window = commits[i:]", "            window = commits[i:i + 2]"),
 ("m17 skip hunk check", "            if len(dl) != ns[f]:", "            if False:"),
 ("m18 vanished all", "return sorted(t for t in seen if t not in present and", "return sorted(t for t in seen if"),
 ("m19 binary as zero", "            if ns[f] is None:", "            if ns[f] == 0:"),
 ("m20 binds no negation", "    if not (\"append-only\" in low or \"append only\" in low) or any(n in low for n in NEGATIONS):", "    if not (\"append-only\" in low or \"append only\" in low):"),
 ("m21 binds no token", "    return fnmatch.fnmatchcase(decl_path, pattern) or (bool(tok) and tok in low)", "    return True"),
 ("m22 exempt no re-derived", '        if text is None or "re-derived" not in low or', '        if text is None or'),
 ("m23 exit no regressed", '                 or s["bad_declarations"]) else 0', '                 ) else 0'),
 ("m24 exit no declarations", '    return 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"]\n                 or s["bad_declarations"]) else 0', '    return 1 if (s["partial"] or s["unrestored"] or s["regressed"] or s["vanished"]) else 0'),
 ("m25 position +1", "                out.append((start + gd, ln[1:]))", "                out.append((start + gd + 1, ln[1:]))"),
 ("m26 contract cells<5", "        if len(cells) != 5:", "        if len(cells) < 5:"),
 ("m27 region whole file", '    if region[0] == "*":', '    if True:'),
 ("m28 CRLF contract ok", '    if "\\r" in text:', '    if False:'),
 ("m29 no unmatched", "    nomatch = unmatched(repo_path, to_full, patterns)", "    nomatch = []"),
 ("m31 hardcoded threshold", "            if ns[f] < threshold:\n                continue", "            if ns[f] < 5:\n                continue"),
 ("m32 numstat no pathspec", 'parent, commit, "--", *files)', 'parent, commit)'),
 ("m30 no vanished", "        gone = vanished(repo_path, to_full, patterns, set(files))", "        gone = []"),
]
cases = None
kills = {}
crashed = []
for label, old, new in M:
    if SRC.count(old) != 1:
        crashed.append((label, f"anchor count {SRC.count(old)}")); continue
    p = os.path.join(S, "work", "mut.py")
    open(p, "w").write(SRC.replace(old, new))
    r = subprocess.run([sys.executable, p, "--selftest", "--scratch", os.path.join(S, "st-mut")],
                       capture_output=True, text=True, timeout=600)
    got = re.findall(r"^(pass|FAIL) (\S+?):?(?: |$)", r.stdout, re.M)
    names = [n for _, n in got]
    if cases is None: cases = names
    if names != cases:
        crashed.append((label, f"case list differs ({len(names)} vs {len(cases)})")) 
    for st, n in got:
        if st == "FAIL":
            kills.setdefault(n, []).append(label)
print("cases:", len(cases or []), "mutants run:", len(M) - len(crashed))
for c in cases or []:
    k = kills.get(c, [])
    print(f"{len(k):2d} {c:28s} {', '.join(x.split()[0] for x in k)}")
for label, why in crashed: print("SKIPPED", label, why)
