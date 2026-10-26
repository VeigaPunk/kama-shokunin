#!/usr/bin/env python3
"""Attack proof for K1R06: does the frozen C1 counter accept a `holds` row whose
anchored GUARD was edited, when the seat picks only the error-message line?

Pure simulation of check_row: show()/blob() are stubbed with the real pinned text
and a mutated release text; nothing is written outside this scratch dir.
"""
import importlib.util, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
UP = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
PIN = "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"
REL = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"
PATH = "tools/server/server-context.cpp"

spec = importlib.util.spec_from_file_location("c1", LANE + "/tools/round46-release-recheck-audit.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def git_show(rev):
    return subprocess.run(["git", "-C", UP, "show", f"{rev}:{PATH}"], capture_output=True, text=True).stdout

pin_txt = git_show(PIN)
rel_txt = git_show(REL)
pin_blob = subprocess.run(["git", "-C", UP, "rev-parse", f"{PIN}:{PATH}"], capture_output=True, text=True).stdout.strip()
rel_blob = subprocess.run(["git", "-C", UP, "rev-parse", f"{REL}:{PATH}"], capture_output=True, text=True).stdout.strip()

def mutate(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

def cells_for(sid):
    src = subprocess.run(["git", "-C", LANE, "show",
                          "0163fea2dab3f282ebd70c71da9ab5de4cedf733:corpus/SOURCES.md"],
                         capture_output=True, text=True).stdout
    return m.population(src)[sid]

def run(sid, pin_lines, rel_lines, release_text):
    ent = cells_for(sid)
    lr = {"path": PATH, "pin_commit": PIN, "release": "b11906", "pin_blob": pin_blob,
          "release_blob": rel_blob, "changed": "1", "pin_lines": pin_lines,
          "release_lines": rel_lines, "witness_pin": "-", "witness_new": "-",
          "verdict": "holds", "note": "x" * 40}
    m.show = lambda repo, rev, path: pin_txt if rev == PIN else release_text
    m.blob = lambda repo, rev, path: pin_blob if rev == PIN else rel_blob
    return m.check_row(ent, lr, "stub")

CASES = [
    ("S118", "6132", "6736", "6131-6133", "6735-6737",
     "if (!params.embedding) {", "if (!params.embedding && res_type == TASK_RESPONSE_TYPE_NONE) {"),
    ("S119", "6137", "6741", "6136-6138", "6740-6742",
     "if (res_type != TASK_RESPONSE_TYPE_NONE && meta->pooling_type == LLAMA_POOLING_TYPE_NONE) {",
     "if (meta->pooling_type == LLAMA_POOLING_TYPE_NONE) {"),
]
for sid, pl, rl, pl_wide, rl_wide, old, new in CASES:
    mutated = mutate(rel_txt, old, new)
    line_of_mutation = [i + 1 for i, x in enumerate(mutated.splitlines()) if new in x]
    narrow = run(sid, pl, rl, mutated)
    wide = run(sid, pl_wide, rl_wide, mutated)
    print(f"{sid}: mutated guard at b11906 line {line_of_mutation}")
    print(f"  narrow range (message line only) -> ok={narrow[0]} reason={narrow[1]!r}")
    print(f"  guard-covering range            -> ok={wide[0]} reason={wide[1]!r}")
