#!/usr/bin/env python3
"""forgeries.py - attack tools/round93-setter-rows.py beyond disclosed limit L1.

Each mutation rewrites the C2 section table of SKILL.md at M2 (and/or a SOURCES.md copy) and
runs the frozen counter through its real CLI (--skill-file/--sources-file), then asks whether
the printed SETTER_ROWS line satisfies the predicated field set (exit 0 is impossible with the
override flags, so the summary line is the verdict).

Usage: forgeries.py <counter.py> <archive.tar.gz> <SKILL-M2.md> <SOURCES-M2.md> <workdir>
Output: one block per forgery: name, mutation, summary line, PASSES/CAUGHT.
"""
import re
import subprocess
import sys
from pathlib import Path

counter, archive, skill_m2, sources_m2, work = map(Path, sys.argv[1:6])
work.mkdir(parents=True, exist_ok=True)
base = skill_m2.read_text().split("\n")
src_base = sources_m2.read_text()


def split_cells(line):
    cells, cur, i, s = [], [], 0, line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|") and not s.endswith("\\|"):
        s = s[:-1]
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s) and s[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if s[i] == "|":
            cells.append("".join(cur).strip())
            cur = []
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
    assert len(idx) == 1, f"{rid}: {len(idx)} lines"
    return idx[0]


def set_cell(lines, rid, k, val):
    i = find(lines, rid)
    c = split_cells(lines[i])
    c[k] = val
    lines[i] = join_cells(c)


def drop_row(lines, rid):
    del lines[find(lines, rid)]


def heading_index(lines):
    i = [j for j, l in enumerate(lines) if l.rstrip() == "## Listen port and slot-count setters (round 93 revision)"]
    assert len(i) == 1, i
    return i[0]


PASS_FIELDS = dict(population=48, rows=48, bound=48, unbound=0, missing=0, duplicates=0,
                   fabricated=0, derived_disagree=0, decisions=2, decisions_bound=2)


def run(name, mutation, lines, srcs=src_base):
    d = work / name
    d.mkdir(exist_ok=True)
    sk = d / "SKILL.md"
    so = d / "SOURCES.md"
    sk.write_text("\n".join(lines))
    so.write_text(srcs)
    p = subprocess.run([sys.executable, str(counter), "--repo", str(work.parent / "wt"), "--rev", "HEAD",
                        "--work", str(d), "--archive", str(archive),
                        "--skill-file", str(sk), "--sources-file", str(so)],
                       capture_output=True, text=True, cwd=str(d))
    summ = [l for l in p.stdout.split("\n") if l.startswith("SETTER_ROWS")]
    tail = summ[-1] if summ else p.stdout.strip().split("\n")[-1] + " | " + p.stderr.strip()[-200:]
    kv = dict(re.findall(r"(\w+)=([\w:-]+)", tail))
    ok = all(kv.get(k) == str(v) for k, v in PASS_FIELDS.items())
    print(f"\n== {name}: {mutation}")
    print(f"   exit={p.returncode} {'PASSES-COUNTER' if ok else 'CAUGHT'}")
    print(f"   {tail}")
    bad = [f"{k}={kv.get(k)}!={v}" for k, v in PASS_FIELDS.items() if kv.get(k) != str(v)]
    if bad:
        print(f"   fields-off: {bad}")
    unbound = [l for l in p.stdout.split("\n") if " unbound " in l]
    for l in unbound[:8]:
        print(f"   {l}")
    return ok


def L():
    return list(base)


results = []

# 1-4 structural hiding
x = L()
i = find(x, "P37")
x.insert(i, "<!--")
x.insert(i + 2, "-->")
results.append(("comment_hide_P37", "P37 row wrapped in an HTML comment", run("comment_hide_P37", "row inside <!-- -->", x)))

x = L()
i = find(x, "P37")
x.insert(i, "```")
x.insert(i + 2, "```")
results.append(("fence_hide_P37", "P37 row inside a code fence", run("fence_hide_P37", "row inside a fence", x)))

x = L()
i = find(x, "P34")
c = split_cells(x[i])
c[8] = c[8] + " <!-- x -->"
x[i] = join_cells(c)
results.append(("comment_inside_cell_P34", "comment marker inside the value cell", run("comment_inside_cell_P34", "inline comment in a cell", x)))

x = L()
i = find(x, "P27")
x.insert(i, "<!--")
c = split_cells(x[i + 1])
c[7] = "overrides"
c[8] = "8011"
x[i + 1] = join_cells(c)
x.insert(i + 2, "-->")
results.append(("comment_misstate_P27", "P27 misstated inside a comment, real row removed", run("comment_misstate_P27", "misstated row only in a comment", x)))

# 5 duplicate heading, section split across the document
x = L()
set_cell(x, "P27", 7, "overrides")
set_cell(x, "P27", 8, "8080")
mis = x[find(x, "P27")]
drop_row(x, "P27")
h = heading_index(x)
x[h - 2:h - 2] = ["## Listen port and slot-count setters (round 93 revision)", "", "Superseded duplicate placed here.",
                  "", "| Id | File | Line | Text (pinned b12177 bytes) | Parameter | Scope | Condition | Effect | Value | Source |",
                  "|---|---|---|---|---|---|---|---|---|---|", mis, ""]
results.append(("dupe_heading_early_P27", "second heading 1700 lines earlier carries a misstated P27", run("dupe_heading_early_P27", "duplicate heading + split section", x)))

# 6 row moved into a trailing ### subsection after the declared Limit paragraph
x = L()
set_cell(x, "P27", 7, "overrides")
set_cell(x, "P27", 8, "8080")
mis = x[find(x, "P27")]
drop_row(x, "P27")
x += ["", "### Superseded rows (not part of the table above)", "", "|---|---|---|---|---|---|---|---|---|---|", mis, ""]
results.append(("trailing_subsection_P27", "misstated P27 in a ### block after the Limit paragraph", run("trailing_subsection_P27", "row after the declared section end", x)))

# 7-8 effect relabel (overrides -> copies) where no derived check applies
x = L()
set_cell(x, "P11", 7, "copies"); set_cell(x, "P11", 8, "-")
set_cell(x, "R16", 4, ", ".join(c for c in split_cells(x[find(x, "R16")])[4].split(", ") if c != "P11"))
results.append(("effect_relabel_arg_P11", "P11 (arg.cpp preset override 8011) relabelled copies", run("effect_relabel_arg_P11", "arg.cpp effect overrides->copies", x)))

x = L()
set_cell(x, "P41", 7, "copies"); set_cell(x, "P41", 8, "-")
set_cell(x, "R16", 4, ", ".join(c for c in split_cells(x[find(x, "R16")])[4].split(", ") if c != "P41"))
results.append(("effect_relabel_nonarg_P41", "P41 (router child LLAMA_ARG_PORT override) relabelled copies", run("effect_relabel_nonarg_P41", "non-arg.cpp effect overrides->copies", x)))

# 9-10 trace string relabelled
x = L()
set_cell(x, "P34", 4, "port"); set_cell(x, "P34", 7, "copies")
results.append(("trace_as_copies_P34", "SRV_TRC trace text relabelled parameter=port effect=copies", run("trace_as_copies_P34", "trace text -> copies", x)))

x = L()
set_cell(x, "P34", 4, "port"); set_cell(x, "P34", 7, "overrides"); set_cell(x, "P34", 8, "9931")
set_cell(x, "R16", 4, split_cells(x[find(x, "R16")])[4] + ", P34")
set_cell(x, "R16", 5, split_cells(x[find(x, "R16")])[5] + " (P34)")
results.append(("trace_as_override_P34", "SRV_TRC trace text relabelled overrides and added to R16 (L1 exemplar)", run("trace_as_override_P34", "trace text -> overrides + R16", x)))

# 11-14 value cell with a symbolic right-hand side
x = L(); set_cell(x, "P37", 8, "8080 (the AIP default)")
results.append(("value_symbolic_wrong_P37", "P37 value misstated (OS-chosen port -> 8080)", run("value_symbolic_wrong_P37", "symbolic value wrong", x)))
x = L(); set_cell(x, "P36", 8, "AIP_HTTP_PORT, else 8000")
results.append(("value_symbolic_wrong_P36", "P36 value misstated (else 8080 -> 8000)", run("value_symbolic_wrong_P36", "symbolic value wrong", x)))
x = L(); set_cell(x, "P03", 8, "the parsed N (0 kept; -1 refused)")
results.append(("value_symbolic_wrong_P03", "P03 value misstates the refusal rule", run("value_symbolic_wrong_P03", "symbolic value wrong", x)))
x = L(); set_cell(x, "P48", 8, "3")
results.append(("value_int_wrong_P48", "P48 integer default 4 -> 3", run("value_int_wrong_P48", "integer value wrong", x)))

# 15-16 decision wording
x = L()
c = split_cells(x[find(x, "R17")])
c[5] = ("No population row overrides n_parallel: P03, P12, P20 and P22 are each explicitly not applied "
        "by llama-server; the count stays auto and resolves no number.")
x[find(x, "R17")] = join_cells(c)
results.append(("decision_negation_R17", "R17 decision names its overriding ids only in a negation", run("decision_negation_R17", "R17 ids only negated", x)))

x = L()
c = split_cells(x[find(x, "R17")])
c[5] = c[5].replace("P12 `--embd-gemma-default` 32", "P12 `--embd-gemma-default` 4")
x[find(x, "R17")] = join_cells(c)
results.append(("decision_wrong_count_R17", "R17 decision states P12 as 4 slots (row P12 says 32)", run("decision_wrong_count_R17", "R17 wrong count for a named row", x)))

# 17-19 arg.cpp condition/scope
x = L(); set_cell(x, "P11", 6, "`--embd-gemma-default` is never parsed; the 8011 arrives only through `--port`")
results.append(("cond_negation_arg_P11", "P11 condition negates its own block but still names the option", run("cond_negation_arg_P11", "arg.cpp condition reversed", x)))
x = L(); set_cell(x, "P11", 5, "LLAMA_EXAMPLE_SERVER, LLAMA_EXAMPLE_EMBEDDING")
results.append(("scope_order_P11", "P11 scope cells permuted", run("scope_order_P11", "scope order", x)))
x = L(); set_cell(x, "P13", 5, "LLAMA_EXAMPLE_SERVER, LLAMA_EXAMPLE_CLI")
results.append(("scope_extra_P13", "P13 scope gains LLAMA_EXAMPLE_CLI", run("scope_extra_P13", "scope extra", x)))

# 20-22 basic integrity
x = L()
c = split_cells(x[find(x, "P27")]); c[3] = c[3].replace("std::stoi(port_str)", "std::stoi(port_str2)")
x[find(x, "P27")] = join_cells(c)
results.append(("text_change_P27", "P27 text cell altered", run("text_change_P27", "text altered", x)))
x = L(); set_cell(x, "P27", 1, "common/http.cpp")
results.append(("fabricated_P27", "P27 file not in the archive", run("fabricated_P27", "fabricated key", x)))
x = L()
row = x[find(x, "P27")]
drop_row(x, "P28")
x.append(row)
results.append(("dupe_row_P27", "P27 duplicated, P28 dropped", run("dupe_row_P27", "duplicate row", x)))

# 23-25 decision cell arithmetic
x = L(); set_cell(x, "R16", 3, "8011")
results.append(("decision_value_R16", "R16 value 9931 -> 8011", run("decision_value_R16", "R16 value wrong", x)))
x = L()
set_cell(x, "R16", 4, ", ".join(c for c in split_cells(x[find(x, "R16")])[4].split(", ") if c != "P37"))
results.append(("decision_drop_P37", "P37 dropped from R16 overriding rows", run("decision_drop_P37", "overriding set short", x)))
x = L()
c = split_cells(x[find(x, "R16")]); c[4] = c[4].replace("P09,", "P09, P09,")
x[find(x, "R16")] = join_cells(c)
results.append(("decision_dupe_id_P09", "P09 repeated in R16 overriding rows", run("decision_dupe_id_P09", "id repeated in set cell", x)))

# 26-27 source provenance
x = L(); set_cell(x, "P27", 9, "S598")
results.append(("source_swap_P27", "P27 (common/http.h) cites S598 (server-http.cpp)", run("source_swap_P27", "wrong S-id", x)))
x = L()
stale = "| S600 | `common/http.h` | not opened this round | stale duplicate placed first |"
results.append(("source_dup_first", "stale duplicate S600 row placed first in SOURCES.md", run("source_dup_first", "duplicate S-id first-wins", x, stale + "\n" + src_base)))

# 28-31 labels and placement
x = L()
a, b = find(x, "P27"), find(x, "P28")
ca, cb = split_cells(x[a]), split_cells(x[b])
ca[0], cb[0] = "P28", "P27"
x[a], x[b] = join_cells(ca), join_cells(cb)
results.append(("pid_swap_P27_P28", "P-ids swapped between two rows (labels unchecked)", run("pid_swap_P27_P28", "ids swapped", x)))
x = L(); set_cell(x, "P46", 4, "-"); set_cell(x, "P46", 7, "unrelated"); set_cell(x, "P46", 8, "-")
results.append(("effect_relabel_default_P46", "P46 (router meta port default 0) relabelled -/unrelated", run("effect_relabel_default_P46", "default relabelled unrelated", x)))
x = L()
row = x[find(x, "P27")]
drop_row(x, "P27")
h = heading_index(x)
x.insert(h, row)
x.insert(h + 1, "")
results.append(("row_before_heading_P27", "P27 placed immediately before the section heading", run("row_before_heading_P27", "row outside the section", x)))
x = L()
h = heading_index(x)
x[h] = x[h] + "."
results.append(("heading_variant", "heading gains a trailing period", run("heading_variant", "heading text differs", x)))

print("\n== SUMMARY")
for (name, desc, ok) in results:
    print(f"{'PASSES-COUNTER' if ok else 'CAUGHT':16s} {name}: {desc}")
print(f"passes={sum(1 for r in results if r[2])}/{len(results)}")
