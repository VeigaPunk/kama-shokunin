#!/usr/bin/env python3
"""own_exe(): os.open of /proc/<pid>/exe is guarded, but fstat/dup/fdopen/read are
not. Under fd exhaustion the open succeeds (one freed slot) and os.dup raises
EMFILE -> OSError escapes own_exe. bind_one has no except (only finally), so the
counter dies with a traceback and exit 1 - the 'not met' exit - without the
met= line; the contract's exit 2 'could not evaluate' is unreachable here.
Runs in a subprocess because we deliberately exhaust fds."""
import importlib.util, os, resource, sys

C1 = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round51-replay-exe-audit.py"
spec = importlib.util.spec_from_file_location("c1", C1)
c1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c1)

soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
print("rlimit:", soft, hard)
fds = []
while True:
    try:
        fds.append(os.open("/dev/null", os.O_RDONLY))
    except OSError as e:
        print(f"fd table full at {len(fds)} opens: {e.strerror}")
        break
# free exactly one slot so own_exe's os.open succeeds but os.dup fails
os.close(fds.pop())

probs = []
try:
    got = c1.own_exe(os.getpid(), "/dev/null", probs)
    print("no exception; got", got, "probs", probs)
except OSError as e:
    print(f"UNGUARDED: {type(e).__name__}: {e.strerror} escaped own_exe (probs={probs})")
finally:
    for fd in fds:
        os.close(fd)
