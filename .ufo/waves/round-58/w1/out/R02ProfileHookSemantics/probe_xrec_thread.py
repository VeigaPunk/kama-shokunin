#!/usr/bin/env python3
"""Exception unwind, recursion, and cross-thread attribution under the harness prof."""
import sys, threading, json

SRC = "battery.py"
WATCHED = ("run", "assert_mutant_breaks_detection")
frames, stack = [], []
EVENTS = []
unattributed = []

def prof(frame, event, arg):
    if frame.f_code.co_filename != SRC or frame.f_code.co_name not in WATCHED:
        return
    EVENTS.append((frame.f_code.co_name, event))
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
        unattributed.append(argv)

SRC_CODE = '''
import threading
READY = threading.Event()
FIRE = threading.Event()

def run(label, n=0):
    if label == "raise":
        raise RuntimeError("battery leg crashed")
    if label == "rec":
        run("rec-inner")
    if label == "threaded":
        t = threading.Thread(target=_ghost, daemon=True)
        t.start(); t.join()
    return label

def _ghost():
    FIRE.set()
    READY.wait(2)
    FIRE.set()
'''
ns = {}
exec(compile(SRC_CODE, SRC, "exec"), ns)
# ghost thread: issue a counter subprocess from an unwatched thread, synchronized
# to the window while a watched frame is on the main-thread stack.
ghost_log = []
def ghost_loop():
    while True:
        ns["FIRE"].wait(2)
        if ns["FIRE"].is_set() and threading.main_thread().is_alive():
            fake_run(["python3", "--counter", "ghost-from-thread"])
            ghost_log.append("fired")
            ns["FIRE"].clear()

sys.setprofile(prof)

print("== C: exception unwinding out of a watched frame ==")
try:
    ns["run"]("raise")
except RuntimeError:
    pass
print("events=%s stack_depth=%d" % (EVENTS, len(stack)))

print("== D: recursion (nested watched calls) ==")
EVENTS.clear()
ns["run"]("rec")
print("events=%s stack_depth=%d rows=%s" % (EVENTS, len(stack),
      [(f["label"], len(f["sub"])) for f in frames]))

print("== E: ghost thread fires while run('threaded') frame is up ==")
EVENTS.clear(); frames.clear(); stack.clear()
t = threading.Thread(target=ghost_loop, daemon=True); t.start()
ns["run"]("threaded")
import time; time.sleep(0.1)
print("ghost fired=%d stack_depth=%d rows=%s" % (len(ghost_log), len(stack),
      [(f["label"], len(f["sub"]), sum(1 for s in f["sub"] if "--counter" in s)) for f in frames]))

print("== F: watched fn executed inside a fresh thread (hook is thread-local) ==")
EVENTS.clear(); frames.clear(); stack.clear(); unattributed.clear()
def in_thread():
    ns["run"]("in-thread-leg")
    fake_run(["python3", "--counter", "thread-own-call"])
tt = threading.Thread(target=in_thread); tt.start(); tt.join()
print("events(main-hook)=%s stack_depth=%d unattributed=%d" % (EVENTS, len(stack), len(unattributed)))
sys.setprofile(None)
