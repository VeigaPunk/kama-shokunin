#!/usr/bin/env python3
"""Fix proof: if cited() also reads the statement cell (cells[6], where the row
names the guard `server-context.cpp:6131-6133` / `6136-6138`), the existing
strong-line rule forces pin_lines to cover the guard, so the narrow row is
rejected and the guard-covering row is the only accepted one."""
import importlib.util, subprocess

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
PIN = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
REL = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"
PATH = "tools/server/server-context.cpp"
spec = importlib.util.spec_from_file_location("c1", LANE + "/tools/round46-release-recheck-audit.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
pin_txt = subprocess.run(["git","-C",UP,"show",f"{PIN}:{PATH}"],capture_output=True,text=True).stdout
rel_txt = subprocess.run(["git","-C",UP,"show",f"{REL}:{PATH}"],capture_output=True,text=True).stdout
pb = subprocess.run(["git","-C",UP,"rev-parse",f"{PIN}:{PATH}"],capture_output=True,text=True).stdout.strip()
rb = subprocess.run(["git","-C",UP,"rev-parse",f"{REL}:{PATH}"],capture_output=True,text=True).stdout.strip()
src = subprocess.run(["git","-C",LANE,"show","0163fea2dab3f282ebd70c71da9ab5de4cedf733:corpus/SOURCES.md"],capture_output=True,text=True).stdout
pop = m.population(src)
m.show = lambda repo, rev, path: pin_txt if rev == PIN else rel_txt
m.blob = lambda repo, rev, path: pb if rev == PIN else rb

orig_cited = m.cited
def cited_with_statement(c):
    s, w = orig_cited(c)
    s2, _ = orig_cited([None, c[6], None, None, None, "", None, None, None, None, None])
    return s | s2, w - s2
m.cited = cited_with_statement
for sid, narrow, wide in (("S118", "6132", "6131-6133"), ("S119", "6137", "6136-6138")):
    strong, weak = m.cited(pop[sid]["cells"])
    print(sid, "strong with c[6]:", sorted(strong))
    for spec_pl, spec_rl in ((narrow, str(int(narrow) + 604)), (wide, f"{int(narrow)+603}-{int(narrow)+605}")):
        lr = {"path": PATH, "pin_commit": PIN, "release": "b11906", "pin_blob": pb, "release_blob": rb,
              "changed": "1", "pin_lines": spec_pl, "release_lines": spec_rl,
              "witness_pin": "-", "witness_new": "-", "verdict": "holds", "note": "x"*40}
        print("   pin_lines", spec_pl, "->", m.check_row(pop[sid], lr, "stub"))
