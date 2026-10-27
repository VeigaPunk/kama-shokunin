#!/usr/bin/env python3
"""Mirror of the round-58 harness prof/fake_run closures, plus an event grammar log."""
import sys, threading, gc, json

SRC = "battery.py"
WATCHED = ("run", "assert_mutant_breaks_detection")
frames, stack = [], []
EVENTS = []

def prof(frame, event, arg):
    if frame.f_code.co_filename != SRC or frame.f_code.co_name not in WATCHED:
        return
    EVENTS.append((frame.f_code.co_name, event, format(id(frame), 'x')[-5:]))
    if event == "call":
        first = frame.f_code.co_varnames[0] if frame.f_code.co_argcount else None
        label = frame.f_locals.get(first) if first else None
        rec = {"fn": frame.f_code.co_name, "label": label if isinstance(label, str) else None,
               "sub": [], "frame": id(frame)}
        stack.append(rec); frames.append(rec)
    elif event == "return" and stack and stack[-1]["frame"] == id(frame):
        stack.pop()

def fake_run(cmd):
    argv = [str(c) for c in cmd]
    if stack:
        stack[-1]["sub"].append(argv)
    else:
        EVENTS.append(("<unattributed>", argv[-1], "-"))

SRC_CODE = '''
KEEP = []
def run(label, n=0):
    yield label          # generator body: issues nothing itself
'''
ns = {}
exec(compile(SRC_CODE, SRC, "exec"), ns)

sys.setprofile(prof)
print("== A: generator call/yield/resume/exhaust ==")
g = ns["run"]("control-clean"); frames.clear(); stack.clear(); EVENTS.clear()
ns["KEEP"].append(g); next(g)           # first next: 'call' fires? 'return' at yield?
print("after first next: stack_depth=%d events=%s" % (len(stack), EVENTS))
EVENTS.clear(); fake_run(["python3", "--counter", "while-suspended"])
print("subprocess while suspended: top_rec_sub=%d" % (len(stack[-1]["sub"]) if stack else -1))
EVENTS.clear(); next(g, None)           # resume to exhaustion
print("after exhaust: stack_depth=%d events=%s" % (len(stack), EVENTS))

print("== B: abandoned suspended generator (kept alive) ==")
frames.clear(); stack.clear(); EVENTS.clear()
g2 = ns["run"]("base-old-counter"); ns["KEEP"].append(g2); next(g2)
print("after first next: stack_depth=%d events=%s" % (len(stack), EVENTS))
fake_run(["python3", "--counter", "ghost-after-abandon"])
rec = stack[-1] if stack else {"label": None, "sub": []}
print("fake_run after abandon -> attributed to label=%r sub=%d" % (rec["label"], len(rec["sub"])))
print("frames rows (harness result.json shape):",
      json.dumps([{"fn": f["fn"], "label": f["label"], "sub": len(f["sub"]),
                   "counter": sum(1 for s in f["sub"] if "--counter" in s)} for f in frames]))
sys.setprofile(None)
