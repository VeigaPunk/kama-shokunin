#!/usr/bin/env python3
"""CR02: are the 14 landed C2 rows exact, or do they bind only through the counter's substring tests?

For each row at <rev>: pin must be a whole URL path segment, the value token must be a whole
numeric token in the literal, and a backticked name must occur as a whole identifier in the
literal. Also: each cited S### must occur exactly once in corpus/SOURCES.md (no shadowing).
"""
import re, subprocess, sys
rev = sys.argv[1]; repo = sys.argv[2]
HEAD = "## Serving timeout and limit thresholds"
def show(p): return subprocess.run(["git","-C",repo,"show",f"{rev}:{p}"],capture_output=True,check=True).stdout.decode()
skill, srcs = show("SKILL.md"), show("corpus/SOURCES.md")
rows, inside = [], False
in_c = False
for line in skill.split("\n"):
    if in_c:
        if "-->" in line: in_c = False
        continue
    while "<!--" in line:
        pre, rest = line.split("<!--",1)
        line = pre + (rest.split("-->",1)[1] if "-->" in rest else "")
        in_c = "-->" not in rest
    if line.startswith("## "):
        inside = line.rstrip() == HEAD; continue
    if inside and re.match(r"^\| *(T\d+) *\|", line):
        rows.append([c.strip() for c in line.strip().strip("|").split("|")])
src_count = {}
for line in srcs.split("\n"):
    m = re.match(r"^ {0,3}\| *(S\d{3,}) *\|", line)
    if m: src_count[m.group(1)] = src_count.get(m.group(1),0)+1
srcref = {}
for line in srcs.split("\n"):
    m = re.match(r"^ {0,3}\| *(S\d{3,}) *\|", line)
    if m and m.group(1) not in srcref:
        cells=[c.strip() for c in line.strip().strip("|").split("|")]
        srcref[m.group(1)] = cells
bad = 0
for cells in rows:
    rid, engine, name, value, sid, ln, literal, _ = cells
    pin = engine.split()[-1]; eng = engine.split()[0]
    url = re.search(r"https://\S+", srcref[sid][1]).group(0).rstrip(").,;")
    lit = literal.strip().strip("`")
    seg = pin in url.split("/")
    nums = re.findall(r"\d+(?:\.\d+)?", value)
    tok = None
    for n in nums:
        for m in re.finditer(re.escape(n), lit):
            a = lit[m.start()-1] if m.start() else " "
            b = lit[m.end()] if m.end() < len(lit) else " "
            if not (a.isdigit() or a == ".") and not (b.isdigit() or b == "."):
                tok = n; break
        if tok: break
    names = [t for t in re.findall(r"`([^`]+)`", name) if len(t) >= 3]
    idn = None
    for t in names:
        for m in re.finditer(re.escape(t), lit):
            a = lit[m.start()-1] if m.start() else " "
            b = lit[m.end()] if m.end() < len(lit) else " "
            if not (a.isalnum() or a == "_") and not (b.isalnum() or b == "_"):
                idn = t; break
        if idn: break
    flags = []
    if not seg: flags.append(f"PIN-SUBSTRING({pin})")
    if tok is None: flags.append(f"VALUE-SUBSTRING({value})")
    if idn is None: flags.append(f"NAME-SUBSTRING({names})")
    if src_count.get(sid,0) != 1: flags.append(f"SRC-COUNT={src_count.get(sid,0)}")
    bad += bool(flags)
    print(f"{rid} src={sid} pin_seg={seg} value_tok={tok} name_id={idn} "
          f"{' '.join(flags) if flags else 'exact'}")
print(f"AUDIT rows={len(rows)} non_exact={bad}")
