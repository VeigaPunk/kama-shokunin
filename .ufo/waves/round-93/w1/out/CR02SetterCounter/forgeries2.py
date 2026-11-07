#!/usr/bin/env python3
"""forgeries2.py - second battery: structural placement and id/uniqueness probes with
*checkable-field-clean* misstatements (param/effect pairing preserved, value left valid), so
the structural question is isolated from the field gaps measured in forgeries.py.

Usage: forgeries2.py <counter.py> <archive.tar.gz> <SKILL-M2.md> <SOURCES-M2.md> <workdir> <repo>
"""
import re
import subprocess
import sys
from pathlib import Path

counter, archive, skill_m2, sources_m2, work = map(Path, sys.argv[1:6])
repo = str(Path(sys.argv[6]))
work.mkdir(parents=True, exist_ok=True)
base = skill_m2.read_text().split("\n")
src_base = sources_m2.read_text()
HEAD = "## Listen port and slot-count setters (round 93 revision)"


def split_cells(line):
    cells, cur, i, s = [], [], 0, line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|"); i += 2; continue
        if s[i] == "|":
            cells.append("".join(cur).strip()); cur = []
        else:
            cur.append(s[i])
        i += 1
    cells.append("".join(cur).strip())
    return cells


def join_cells(cells):
    return "| " + " | ".join(cells) + " |"


def find(lines, rid):
    rx = re.compile(r"^\| *" + re.escape(rid) + r" *\|")
    idx = [i for i, l in enumerate(lines) if rx.match(l)]
    assert len(idx) == 1, f"{rid}: {len(idx)}"
    return idx[0]


def set_cell(lines, rid, k, val):
    i = find(lines, rid)
    c = split_cells(lines[i]); c[k] = val; lines[i] = join_cells(c)


def drop_row(lines, rid):
    del lines[find(lines, rid)]


def heading_index(lines):
    i = [j for j, l in enumerate(lines) if l.rstrip() == HEAD]
    assert len(i) == 1, i
    return i[0]


PASS_FIELDS = dict(population=48, rows=48, bound=48, unbound=0, missing=0, duplicates=0,
                   fabricated=0, derived_disagree=0, decisions=2, decisions_bound=2)


def run(name, mutation, lines, srcs=src_base):
    d = work / name
    d.mkdir(exist_ok=True)
    sk, so = d / "SKILL.md", d / "SOURCES.md"
    sk.write_text("\n".join(lines)); so.write_text(srcs)
    p = subprocess.run([sys.executable, str(counter), "--repo", repo, "--rev", "HEAD",
                        "--work", str(d), "--archive", str(archive), "--skill-file", str(sk),
                        "--sources-file", str(so)], capture_output=True, text=True, cwd=str(d))
    summ = [l for l in p.stdout.split("\n") if l.startswith("SETTER_ROWS")]
    tail = summ[-1] if summ else p.stdout.strip().split("\n")[-1] + " | " + p.stderr.strip()[-200:]
    kv = dict(re.findall(r"(\w+)=([\w:-]+)", tail))
    ok = all(kv.get(k) == str(v) for k, v in PASS_FIELDS.items())
    print(f"\n== {name}: {mutation}")
    print(f"   exit={p.returncode} {'PASSES-COUNTER' if ok else 'CAUGHT'}")
    print(f"   {tail}")
    for l in [l for l in p.stdout.split("\n") if " unbound " in l][:6]:
        print(f"   {l}")
    return ok


def L():
    return list(base)


def bindrow(lines, rid, cond="the row's real condition", param="port", effect="copies", value="-"):
    """Rewrite a row so param/effect/value/scope pass every counter check while the condition
    text is a plain misstatement."""
    set_cell(lines, rid, 4, param)
    set_cell(lines, rid, 6, cond)
    set_cell(lines, rid, 7, effect)
    set_cell(lines, rid, 8, value)
    return lines[find(lines, rid)]


res = []

# 1 duplicate heading earlier in the document carrying the misstated row
x = L()
mis = bindrow(x, "P27", cond="MISSTATED: the client parser's default is the server listen port")
drop_row(x, "P27")
h = heading_index(x)
x[h - 2:h - 2] = [HEAD, "", "Superseded duplicate of the table, placed here.",
                  "", "| Id | File | Line | Text (pinned b12177 bytes) | Parameter | Scope | Condition | Effect | Value | Source |",
                  "|---|---|---|---|---|---|---|---|---|---|", mis, ""]
res.append(("dupe_heading_bind_P27", "second heading 1700 lines early carries a misstated P27", run("dupe_heading_bind_P27", "duplicate heading, split section", x)))

# 2 row after the declared Limit paragraph, in a ### block
x = L()
mis = bindrow(x, "P27", cond="MISSTATED: appended after the section's Limit paragraph")
drop_row(x, "P27")
x += ["", "### Rows moved below the limit paragraph", "",
      "|---|---|---|---|---|---|---|---|---|---|", mis, ""]
res.append(("trailing_subsection_bind_P27", "misstated P27 appended in a ### block at EOF", run("trailing_subsection_bind_P27", "row after the Limit paragraph", x)))

# 3 URL-parser default relabelled as the listen-port default (non-arg.cpp effect unchecked)
x = L()
set_cell(x, "P28", 4, "port"); set_cell(x, "P28", 7, "default"); set_cell(x, "P28", 8, "80")
set_cell(x, "P28", 6, "the listen port defaults to 80")
res.append(("effect_relabel_P28_default", "http.h URL default 80 relabelled as the listen-port default", run("effect_relabel_P28_default", "unrelated -> default", x)))

# 4 duplicate P-id across two rows with distinct keys
x = L()
id28 = split_cells(x[find(x, "P28")])
id28[0] = "P01"
x[find(x, "P28")] = join_cells(id28)
res.append(("duplicate_pid_P01", "P28 renamed to P01: two table rows share an Id", run("duplicate_pid_P01", "duplicate P-id", x)))

# 5 eleven-cell row
x = L()
c = split_cells(x[find(x, "P27")]); c.append("extra")
x[find(x, "P27")] = join_cells(c)
res.append(("eleven_cells_P27", "P27 gains a trailing 11th cell", run("eleven_cells_P27", "cell count 11", x)))

# 6 decision prose naming an id the row set does not contain
x = L()
c = split_cells(x[find(x, "R16")])
c[5] = c[5] + " P48 also sets the port to 4."
x[find(x, "R16")] = join_cells(c)
res.append(("decision_extra_prose_R16", "R16 decision adds a false clause about P48", run("decision_extra_prose_R16", "extra prose in decision", x)))

# 7 row with the section heading present twice, identical rows (identity ambiguity only)
x = L()
h = heading_index(x)
x[h:h] = [HEAD, "", "(duplicate heading, no rows here)", ""]
res.append(("dupe_heading_no_rows", "heading text repeated with no rows under the first copy", run("dupe_heading_no_rows", "duplicate heading, empty", x)))

print("\n== SUMMARY2")
for (n, d, ok) in res:
    print(f"{'PASSES-COUNTER' if ok else 'CAUGHT':16s} {n}: {d}")
print(f"passes={sum(1 for r in res if r[2])}/{len(res)}")
