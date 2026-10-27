#!/usr/bin/env python3
"""X7 extra probe: flip a byte INSIDE libggml-rpc.so's mapped executable range
(offset 0x30000, inside .text 0x13ff0..0x3145a) instead of the battery's
-0x3000 (offset 0x4b120, inside .strtab - never mapped).  Question: does the
counter's OWN /proc/<pid>/mem vs archive-member byte comparison fire
("code: mapped bytes ... differ from the archive member")?

Runs the frozen counter on a fixture commit in my own clone.  Writes into my
out dir only.
"""
import os
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
COUNTER = os.path.join(LANE, "tools/round54-replay-code-audit.py")
LIVE = "tools/kama-llamacpp-live.py"
S = "/fast/scratch/hyaku/kama-r55/w1/X7BatteryReplay"
OUT = os.path.join(LANE, ".ufo/waves/round-55/w1/out/X7BatteryReplay")
CLONE = os.path.join(S, "lane")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}

ENV_ANCHOR = "        receipt['child_env_keys'] = sorted(child_env)\n"
# flip at a fixed absolute file offset inside .text (0x30000), not -0x3000
PATCH = (
    "        import glob as _g\n"
    "        for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-rpc.so*')):\n"
    "            if os.path.getsize(_p) > 0x6000:\n"
    "                with open(_p, 'r+b') as fh:\n"
    "                    fh.seek(0x30000)\n"
    "                    _b = fh.read(1)\n"
    "                    fh.seek(0x30000)\n"
    "                    fh.write(bytes([_b[0] ^ 1]))\n"
    "                break\n" + ENV_ANCHOR
)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def git(*args):
    r = run(["git", "-C", CLONE, *args], env=ENV)
    if r.returncode:
        raise SystemExit(f"git {args}: {r.stderr[:400]}")
    return r.stdout.strip()


def main():
    os.makedirs(OUT, exist_ok=True)
    assert git("rev-parse", "--show-toplevel") == CLONE
    git("reset", "--hard", FREEZE)
    p = os.path.join(CLONE, LIVE)
    src = open(p).read()
    assert src.count(ENV_ANCHOR) == 1, src.count(ENV_ANCHOR)
    open(p, "w").write(src.replace(ENV_ANCHOR, PATCH))
    git("add", LIVE)
    r = run(["git", "-C", CLONE, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
             "commit", "-q", "-m", "X7 probe: flip byte inside rpc .text"], env=ENV)
    if r.returncode:
        print(r.stderr[:300]); return 2
    tip = git("rev-parse", "HEAD")
    outp = os.path.join(OUT, "probe-in-text.out")
    scratch = os.path.join(S, "run-probe-in-text")
    shutil.rmtree(scratch, ignore_errors=True); os.makedirs(scratch)
    q = run([sys.executable, COUNTER, "--repo", CLONE, "--tip", tip,
             "--scratch", scratch, "--out", outp], env=ENV)
    text = open(outp).read() if os.path.isfile(outp) else q.stdout
    lines = text.splitlines()
    print("exit", q.returncode)
    print(lines[0])
    print(lines[1] if len(lines) > 1 else "")
    hits = [ln for ln in lines if "mapped bytes" in ln]
    print(f"counter mem-compare hits ('code: mapped bytes ... differ'): {len(hits)}")
    for h in hits[:6]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
