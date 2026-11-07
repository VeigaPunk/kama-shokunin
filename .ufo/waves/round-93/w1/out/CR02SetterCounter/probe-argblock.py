#!/usr/bin/env python3
"""probe-argblock.py - instrument round93-setter-rows.py's arg_block() on every arg.cpp
population line and on every P-row, and compare with an independent reading of the
enclosing add_opt(common_arg( block (first long option, set_examples list).

Usage: probe-argblock.py <counter.py> <archive.tar.gz> <skill.md>
"""
import importlib.util
import sys
from pathlib import Path

counter_path, archive, skill_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
spec = importlib.util.spec_from_file_location("c93", counter_path)
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)

files, digest = c.load_archive(Path("/tmp") / "unused-probe-work", archive)
pop = c.population(files)
lines = files["common/arg.cpp"]


def own_block(lines, ln):
    """Independent reading: scan backwards to the nearest 'add_opt(common_arg(' that is not
    already closed, i.e. track paren depth from ln backwards is unreliable; instead find the
    nearest preceding start whose terminating '));' is at/after ln."""
    starts = [i for i, t in enumerate(lines) if "add_opt(common_arg(" in t]
    ends = {}  # start -> end index
    for s in starts:
        depth = 0
        for j in range(s, len(lines)):
            depth += lines[j].count("(") - lines[j].count(")")
            if depth <= 0:
                ends[s] = j
                break
    best = None
    for s in starts:
        if s <= ln - 1 <= ends.get(s, -1):
            best = s if best is None else max(best, s)  # innermost/last enclosing
    if best is None:
        return None, None, None
    end = ends[best]
    opts = []
    for t in lines[best:min(best + 4, end + 1)]:
        import re
        opts += re.findall(r'"(--[A-Za-z0-9][\w.-]*)"', t)
    ex = None
    import re
    block = "\n".join(lines[best:end + 1])
    m = re.search(r"\.set_examples\(\{([^}]*)\}\)", block)
    if m:
        ex = sorted(x.strip() for x in m.group(1).split(",") if x.strip())
    return (best + 1, end + 1), (opts[0] if opts else None), ex


skill = skill_path.read_text()
prow, drow = c.section_rows(skill)
by_key = {}
for cells in prow:
    if len(cells) == 10 and cells[2].isdigit():
        by_key[(cells[1], int(cells[2]))] = cells

print(f"# archive {digest[:16]} population={len(pop)}")
print("## every common/arg.cpp population line")
for (f, ln) in sorted(k for k in pop if k[0] == "common/arg.cpp"):
    cb = c.arg_block(lines, ln)
    ob = own_block(lines, ln)
    cells = by_key.get((f, ln))
    cond = cells[6] if cells else "<no row>"
    scope = cells[5] if cells else "<no row>"
    flag = "" if (cb and ob[1] and cb[0] == ob[1] and cb[1] == (ob[2] or ["LLAMA_EXAMPLE_COMMON"])) else "  <<<DIFF"
    print(f"{ln:5d} counter_block={ob[0] and cb} own={(ob[0], ob[1], ob[2])}{flag}")
    print(f"      cond_cell={cond!r}")
    print(f"      scope_cell={scope!r}")

print("## per-row derived checks (arg.cpp rows from P-table)")
for cells in prow:
    if len(cells) != 10:
        continue
    ok, why, chk, dis, key = c.grade_p(list(cells), pop, files, c.sources(Path("/dev/null").read_text()), set())
    if cells[1] == "common/arg.cpp":
        print(f"{cells[0]:4s} line={cells[2]} derived_checked={chk} why={why}")
