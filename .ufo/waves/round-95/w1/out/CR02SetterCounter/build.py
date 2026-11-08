#!/usr/bin/env python3
"""Build C2 setter-sweep forgeries from the M2 SKILL.md bytes."""
from pathlib import Path
import subprocess, sys

S = Path("/fast/scratch/hyaku/kama-r95/CR02SetterCounter")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-95/w1/out/CR02SetterCounter")
OUT.mkdir(parents=True, exist_ok=True)
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
HEAD95 = "## Listen port and slot-count setters (round 95 revision)"
HEAD94 = "## Listen port and slot-count setters (round 94 revision)"

m2 = (S / "skill-M2.md").read_text()
i95 = m2.index(HEAD95)
prefix, section = m2[:i95], m2[i95:]
assert section.count(HEAD95) == 1
base = subprocess.run(["git", "-C", LANE, "show", "2011161d:SKILL.md"],
                      capture_output=True, check=True).stdout.decode()

def rows(text):
    return text.split("\n")

def find_row(text, rid, occurrence=0):
    idxs = [i for i, l in enumerate(rows(text)) if l.startswith(f"| {rid} |")]
    assert len(idxs) > occurrence, (rid, occurrence, len(idxs))
    return idxs[occurrence]

def edit_row(text, rid, old, new, occurrence=0, expect=1):
    ls = rows(text)
    i = find_row(text, rid, occurrence)
    assert ls[i].count(old) == expect, (rid, old, ls[i].count(old))
    ls[i] = ls[i].replace(old, new)
    return "\n".join(ls)

def drop_row(text, rid, occurrence=0):
    ls = rows(text)
    i = find_row(text, rid, occurrence)
    before = sum(1 for l in ls if l.startswith(f"| {rid} |"))
    del ls[i]
    assert sum(1 for l in ls if l.startswith(f"| {rid} |")) == before - 1, rid
    return "\n".join(ls)

variants = {}
# V1: round-94 SKILL.md verbatim (no round-95 section at all)
variants["V1-round94-verbatim.md"] = base
# V1b: round-94 body retitled to the round-95 head (counter parses old population)
assert base.count(HEAD94) == 1
variants["V1b-round94-retitled.md"] = base.replace(HEAD94, HEAD95)
# V2: one new population row dropped (P96)
variants["V2-drop-newrow.md"] = prefix + drop_row(section, "P96")
# V2b: a setter row inside a decision set dropped (P87)
variants["V2b-drop-setter-row.md"] = prefix + drop_row(section, "P87")
# V3: fabricated line not in the archive (line 99999 of common/preset.cpp)
v3 = section + "\n| P107 | common/preset.cpp | 99999 | preset.name = \"fabricated\"; | - | shared | config.ini section scoping | invented row not in the archive | copies | - | S604 |\n"
variants["V3-fabricated-line.md"] = prefix + v3
# V4: wrong Entry cell on a new row (P100 cli -> server)
variants["V4-entry-newrow.md"] = prefix + edit_row(section, "P100", "| - | cli |", "| - | server |")
# V5: decision id set off by one (R20 cli gains P51, which is `copies`)
variants["V5-id-off-by-one.md"] = prefix + edit_row(section, "R20", "| P49, P50 |", "| P49, P50, P51 |", occurrence=1)
# V6: P91's `default` relabelled `realises`, value cell made consistent
v6sec = edit_row(section, "P91", "| default | 4 |", "| realises | - |")
variants["V6-default-to-realises.md"] = prefix + v6sec
# V6b: literal reading: a decision row whose Parameter cell is `realises`
variants["V6b-decision-param-realises.md"] = prefix + edit_row(section, "R21", "| n_parallel | server |", "| realises | server |")
# V6c: V6 + the decision id set edited to match (coherent reclassification)
v6c = edit_row(v6sec, "R21", "| P11, P13, P22, P30, P32, P91 |", "| P11, P13, P22, P30, P32 |")
variants["V6c-realises-coherent.md"] = prefix + v6c
# V7: a `realises` row with Parameter `-`
variants["V7-realises-dash-param.md"] = prefix + edit_row(section, "P102", "| n_parallel | server |", "| - | server |")
# V8: `[default]` removed from the shared port decision text
variants["V8-shared-default-token.md"] = prefix + edit_row(
    section, "R20", "only from the `[default]` or `[*]` section", "only from the `[*]` section", occurrence=3)
# V9: the whole shared port decision row deleted
variants["V9-shared-decision-deleted.md"] = prefix + drop_row(section, "R20", occurrence=3)
# V9b: the shared n_parallel decision row deleted
variants["V9b-shared-np-decision-deleted.md"] = prefix + drop_row(section, "R21", occurrence=2)

# --- round-94 survivor-class probes ---
# S1: non-literal value cell misstated (P50 free port -> 8080)
variants["S1-value-nonliteral.md"] = prefix + edit_row(section, "P50", "| the OS-chosen free port |", "| 8080 |")
# S2: default<->overrides swap on an integer-literal row (P38)
variants["S2-effect-swap.md"] = prefix + edit_row(section, "P38", "| default | 9931 |", "| overrides | 9931 |")
# S3: condition garbage on a config-route row (P93) -- round-94 L03/L04 class
v3s = rows(section); i = find_row(section, "P93")
cells = v3s[i].split("|")
# cells: ['', ' P93 ', ' common/arg.cpp ', ... ] condition is index 7
assert cells[8].strip().startswith("`presets.find(COMMON_PRESET_DEFAULT_NAME)`"), cells[8]
cells[8] = " x "
v3s[i] = "|".join(cells)
variants["S3-condition-garbage.md"] = prefix + "\n".join(v3s)
# S4: scope garbage on a new non-arg.cpp row (P101)
v4s = rows(section); i = find_row(section, "P101")
cells = v4s[i].split("|")
assert cells[7].strip() == "slot initialisation", cells[7]
cells[7] = " totally unrelated scope text "
v4s[i] = "|".join(cells)
variants["S4-scope-garbage.md"] = prefix + "\n".join(v4s)
# S5: decision text negated but still carrying the precedence tokens
v5s = rows(section); i = find_row(section, "R20", occurrence=3)
cells = v5s[i].split("|")
assert "config.ini" in cells[6], cells[6]
cells[6] = " No config.ini `[default]` or `[*]` section ever applies; the parsed `--port` alone decides. "
v5s[i] = "|".join(cells)
variants["S5-decision-negated.md"] = prefix + "\n".join(v5s)
# S6: P38 renamed P93 everywhere (duplicate row id accepted)
v6s = edit_row(section, "P38", "| P38 |", "| P93 |")
v6s = edit_row(v6s, "R20", "| P38 |", "| P93 |", occurrence=3)
variants["S6-duplicate-row-id.md"] = prefix + v6s
# S7: fabricated SOURCES row cited by a population row (separate sources file)
src = (S / "SOURCES-M2.md").read_text()
src += ("| S999 | llama.cpp common/preset.cpp at tag b12177 — "
        "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/common/preset.cpp | code | A | "
        "fabricated scope | fabricated anchor | fabricated teaches | mined | 2026-11-08 | on-release | SKILL.md |\n")
(OUT / "S7-fake-source-SOURCES.md").write_text(src)
variants["S7-fake-source-skill.md"] = prefix + edit_row(section, "P93", "| S596 |", "| S999 |")
# S8: entry relabel that changes the printed `entries=` metric (P85 router -> other)
variants["S8-entries-metric.md"] = prefix + edit_row(section, "P85", "| router |", "| other |")
# S9: decision-row Sources cell garbage (never graded)
v9s = rows(section); i = find_row(section, "R20", occurrence=3)
cells = v9s[i].split("|")
cells[7] = " S999, garbage "
v9s[i] = "|".join(cells)
variants["S9-decision-sources-garbage.md"] = prefix + "\n".join(v9s)

for name, text in variants.items():
    p = OUT / name
    p.write_text(text)
    print(f"wrote {name} lines={text.count(chr(10))}")
assert len({v for v in variants.values()}) == len(variants), "variants not distinct"
