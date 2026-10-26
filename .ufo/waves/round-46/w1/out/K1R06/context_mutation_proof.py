#!/usr/bin/env python3
"""Residual limit: `holds` proves the quoted range is text-preserved, not the row's
statement. Two mutations OUTSIDE any plausible range keep a guard-covering `holds`
row VALID: (a) the OAI caller passes a different res_type, (b) json::parse is moved
ahead of the guard. Both invalidate S118/S119's statement text while the guard and
message lines stay byte-identical."""
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

def check(sid, pin_lines, rel_lines, release_text):
    m.show = lambda repo, rev, path: pin_txt if rev == PIN else release_text
    m.blob = lambda repo, rev, path: pb if rev == PIN else rb
    lr = {"path": PATH, "pin_commit": PIN, "release": "b11906", "pin_blob": pb, "release_blob": rb,
          "changed": "1", "pin_lines": pin_lines, "release_lines": rel_lines,
          "witness_pin": "-", "witness_new": "-", "verdict": "holds", "note": "x"*40}
    return m.check_row(pop[sid], lr, "stub")

lines = rel_txt.splitlines(keepends=True)
# (a) caller mutation: /v1/embeddings no longer asks for the OAI response type
a = list(lines)
i = next(i for i,x in enumerate(a) if "handle_embeddings_impl(req, TASK_RESPONSE_TYPE_OAI_EMBD)" in x)
a[i] = a[i].replace("TASK_RESPONSE_TYPE_OAI_EMBD", "TASK_RESPONSE_TYPE_NONE")
# (b) order mutation: json::parse moved ahead of both guards
b = list(lines)
j = next(i for i,x in enumerate(b) if "const json body = json::parse(req.body);" in x)
guard = next(i for i,x in enumerate(b) if "if (!params.embedding) {" in x)
parse_line = b.pop(j)
b.insert(guard - 1, "    " + parse_line.strip() + "\n")
print("caller mutation at b11906 line", i+1)
print("  S119 wide guard-covering holds ->", check("S119", "6136-6138", "6740-6742", "".join(a)))
print("order mutation: parse now before guard at b11906 line", guard)
print("  S118 wide guard-covering holds ->", check("S118", "6131-6133", "6735-6737", "".join(b)))
