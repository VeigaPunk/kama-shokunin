import re
import subprocess
import sys

p = subprocess.run(["git", "-C", sys.argv[1], "config", "--list", "--name-only"],
                   capture_output=True)
hits = [line for line in p.stdout.decode("utf-8", "replace").split("\n")
        if line == "extensions.partialclone"
        or re.fullmatch(r"remote\..+\.promisor", line)]
print("YES: " + repr(hits) if hits else "NO")
