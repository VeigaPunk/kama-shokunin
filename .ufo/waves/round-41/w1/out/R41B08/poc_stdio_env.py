#!/usr/bin/env python3
"""PoC: credential-prompt surface — stdin/env inheritance in pin-watch read_tags."""
import importlib.util, os, subprocess, sys

spec = importlib.util.spec_from_file_location(
    "pinwatch", "/fast/scratch/kama-r41/clone/tools/pin-watch.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

shim = "/tmp/R41B08-dev/shim"
os.makedirs(shim, exist_ok=True)
with open(os.path.join(shim, "git"), "w") as fh:
    fh.write("""#!/bin/sh
echo \"shim stdin-tty=$(test -t 0 && echo yes || echo no)\" >&2
echo \"shim stdin-closed=$(test -e /proc/self/fd/0 && echo no || echo yes)\" >&2
echo \"shim GIT_TERMINAL_PROMPT=$GIT_TERMINAL_PROMPT\" >&2
echo \"shim GIT_ASKPASS=$GIT_ASKPASS\" >&2
echo \"shim SSH_ASKPASS=$SSH_ASKPASS\" >&2
exec git \"$@\"
""")
os.chmod(os.path.join(shim, "git"), 0o755)

old_path = os.environ.get("PATH", "")
os.environ["PATH"] = shim + ":" + old_path
os.environ.setdefault("GIT_ASKPASS", "/fake/askpass")
os.environ.setdefault("SSH_ASKPASS", "/fake/ssh_askpass")

# network branch: subprocess.run without stdin=DEVNULL; capture stderr from shim
p = subprocess.run(["git", "ls-remote", "--tags",
                     "https://github.com/sgl-project/sglang.git"],
                    capture_output=True, text=True, timeout=60,
                    env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
print("rc:", p.returncode)
print("shim stderr:", p.stderr.strip().splitlines()[:6])
print("git stdout lines:", len(p.stdout.splitlines()))
