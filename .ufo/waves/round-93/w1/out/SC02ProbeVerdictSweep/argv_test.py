#!/usr/bin/env python3
"""SC02: ARG_MAX / argv-overflow candidate.

router_file_states "$body" "${cand[@]}" passes one index per candidate as an
argv word. If the number of router entries a listener sends exceeds what execve
accepts, the python never starts -> zero state lines -> nbad(0) < ncand(N) ->
router_refine's `unloaded=1` -> MODEL_OK / router-unloaded-autoload (false green).
"""
import os, subprocess, sys

CHILD = "import sys; sys.stdout.write('\\n'.join(sys.argv[1:]))"
print(f"# getconf ARG_MAX = {subprocess.run(['getconf','ARG_MAX'],capture_output=True,text=True).stdout.strip()}")
print(f"# getconf _POSIX_ARG_MAX = {subprocess.run(['getconf','_POSIX_ARG_MAX'],capture_output=True,text=True).stdout.strip()}")
for n in (1000, 2048, 4096, 8192, 16384, 32768, 65536, 131072):
    args = [str(i) for i in range(n)]
    p = subprocess.run([sys.executable, "-c", CHILD, *args], capture_output=True)
    ok = p.returncode == 0
    lines = p.stdout.decode().count("\n")
    err = p.stderr.decode().strip().split("\n")[-1] if p.stderr else ""
    print(f"ARGV n={n} rc={p.returncode} lines={lines} err={err!r}")
    if not ok:
        break
