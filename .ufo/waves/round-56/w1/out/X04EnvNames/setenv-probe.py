"""Edge: a child that sets LD_AUDIT in its own environment AFTER exec (setenv, no exec).

/proc/<pid>/environ exposes the exec-time environment block only; the child's own
os.environ view is written by the child itself so both sides of the divergence are
in the receipt. The round-56 env_leg reads the /proc side, by design.
"""
import importlib.util
import os
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
spec = importlib.util.spec_from_file_location("r56", f"{LANE}/tools/round56-replay-code-audit.py")
r56 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r56)

view = os.path.abspath("child-environ-view.txt")
code = (
    "import os,time\n"
    "os.environ['LD_AUDIT']='/usr/lib/libexpat.so.1'\n"
    f"open({view!r},'w').write('\\n'.join(sorted(os.environ))+'\\n')\n"
    "time.sleep(20)\n"
)
p = subprocess.Popen([sys.executable, "-c", code])
try:
    for _ in range(200):
        if os.path.exists(view):
            break
        time.sleep(0.01)
    raw = open(f"/proc/{p.pid}/environ", "rb").read()
    own = open(view).read().split()
    probs = []
    keys = r56.env_leg(p.pid, probs)
    print(f"child pid={p.pid}")
    print(f"child's own os.environ names={len(own)} has_LD_AUDIT={'LD_AUDIT' in own}")
    print(f"/proc/<pid>/environ bytes={len(raw)} has_LD_AUDIT={b'LD_AUDIT' in raw}")
    print(f"r56 env_leg keys={len(keys)} has_LD_AUDIT={'LD_AUDIT' in keys} problems={probs}")
finally:
    p.terminate()
    p.wait()
