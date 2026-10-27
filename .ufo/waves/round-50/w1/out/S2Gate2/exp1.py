#!/usr/bin/env python3
"""Gate reject 1 experiment: /proc/<pid>/environ alone is not proof of interpreter
cleanliness.  Two independent failures:
  (i)  an interpreter can import a planted sitecustomize while carrying NO canary in
       its environment (environ clean, interpreter dirty) - only the marker file sees it;
  (ii) environ of another uid is unreadable, so an outside observer cannot sample it at
       all (the counter must fail closed, which it does: environ_keys -> None -> problem).
Uses the counter's own environ_keys().
"""
import importlib.util
import os
import subprocess
import sys

S = sys.argv[1]
TOOLS = sys.argv[2]
E = os.path.join(S, "exp", "e1")
site = os.path.join(E, "site")
os.makedirs(site, exist_ok=True)
marker = os.path.join(E, "marker")
if os.path.exists(marker):
    os.unlink(marker)
with open(os.path.join(site, "sitecustomize.py"), "w") as fh:
    fh.write("import os, sys\n"
             f"with open({marker!r}, 'a') as _f:\n"
             "    _f.write('%d %r\\n' % (os.getpid(), sys.argv[:2]))\n")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


counter = load("r50c1", os.path.join(TOOLS, "round50-replay-bind-audit.py"))

# (i) an interpreter whose environment carries no canary but which imports the plant.
env = {k: v for k, v in os.environ.items() if k != "KAMA_R50_CANARY"}
env["PYTHONPATH"] = site
code = ("import os, sys\n"
        "print('KAMA_R50_CANARY in os.environ:', 'KAMA_R50_CANARY' in os.environ)\n"
        "print('PYTHONPATH in os.environ:', 'PYTHONPATH' in os.environ)\n"
        "print('sitecustomize imported:', 'sitecustomize' in sys.modules)\n"
        "print('own environ keys containing CANARY:', "
        "[k for k in os.environ if 'CANARY' in k])")
r = subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True)
print("(i) hijacked interpreter (no -I, PYTHONPATH=plant):")
print(r.stdout.rstrip())
print("(i) exit:", r.returncode)
hits = open(marker).read().splitlines() if os.path.exists(marker) else []
print(f"(i) marker file lines: {len(hits)} -> {hits}")
print("(i) environ-only witness would call this interpreter CLEAN; the marker says DIRTY")

# (ii) environ of another uid is unreadable.
print("(ii) own pid environ readable:", counter.environ_keys(os.getpid()) is not None)
try:
    open("/proc/1/environ", "rb").read()
    print("(ii) /proc/1/environ readable (unexpected)")
except OSError as exc:
    print(f"(ii) /proc/1/environ: {type(exc).__name__}: {exc}")
print("(ii) counter.environ_keys(1) ->", counter.environ_keys(1),
      "| None is graded as a problem, not as clean")
print("(ii) /proc/1 owner uid:", os.stat("/proc/1").st_uid, "| own uid:", os.getuid())
