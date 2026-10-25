#!/usr/bin/env python3
"""R41B07 adversarial check: naive `git ls-remote --tags | sort -V | tail -1`
vs pin-watch semantics on the lane's committed round-41 captures (read-only)."""
import re, subprocess

base = "/fast/scratch/kama-r41/clone/.ufo/waves/round-41/c2/"
files = {"sglang": "ls-remote-sglang.txt", "vllm": "ls-remote-vllm.txt",
         "llama.cpp": "ls-remote-llama.cpp.txt"}
pins = {"sglang": "v0.5.22", "vllm": "v0.32.0", "llama.cpp": "b11755"}
regexes = {"sglang": r"v(\d+)\.(\d+)\.(\d+)", "vllm": r"v(\d+)\.(\d+)\.(\d+)",
           "llama.cpp": r"b(\d+)"}

def tags_from(lines):
    tags = []
    for ln in lines:
        if "\t" not in ln:
            continue
        _, ref = ln.split("\t", 1)
        m = re.fullmatch(r"refs/tags/(.*)", ref.strip())
        if m and not m.group(1).endswith("^{}"):
            tags.append(m.group(1))
    return tags

for eng, fn in files.items():
    lines = open(base + fn).read().splitlines()
    tags = tags_from(lines)
    naive = subprocess.run(["sort", "-V"], input="\n".join(tags),
                           capture_output=True, text=True).stdout.splitlines()[-1]
    rx = re.compile(regexes[eng])
    keyed = {}
    for t in tags:
        m = rx.fullmatch(t)
        if m:
            keyed[t] = tuple(int(g) for g in m.groups())
    tool_max = max(keyed, key=lambda t: (keyed[t], t))
    if pins[eng] in keyed:
        newer = sum(1 for k in keyed.values() if k > keyed[pins[eng]])
        status = "current" if newer == 0 else "behind"
    else:
        newer, status = None, "missing"
    print(f"{eng}: naive_max={naive!r} tool_max={tool_max!r} pin={pins[eng]} "
          f"newer={newer} {status} | naive==tool_max: {naive==tool_max} "
          f"| naive_is_release: {naive in keyed}")
