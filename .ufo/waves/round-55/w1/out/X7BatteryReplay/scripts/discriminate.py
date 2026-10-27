#!/usr/bin/env python3
"""X7 discrimination test: does the battery's m-text-flip mutant still kill a
counter whose OWN /proc/<pid>/mem vs archive-member byte comparison is disabled?

Procedure:
  1. rebuild the m-text-flip fixture commit in my clone (patch text taken from
     the L1 harness's MUTANTS table, byte-identical);
  2. run the FROZEN counter on it  -> expect met=False (the L1's result);
  3. run a COPY of the counter with the mem-compare branch disabled
     (the `got != want` -> probs.append line removed) -> if it STILL prints
     met=False, the battery's code-leg mutant does not discriminate that
     sub-leg.
The counter is never edited in place; the copy lives in my scratch.
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
TEXTFLIP = (
    "        import glob as _g\n"
    "        for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-rpc.so*')):\n"
    "            if os.path.getsize(_p) > 0x6000:\n"
    "                with open(_p, 'r+b') as fh:\n"
    "                    fh.seek(-0x3000, 2)\n"
    "                    _b = fh.read(1)\n"
    "                    fh.seek(-0x3000, 2)\n"
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


def counter_run(counter_path, tip, name):
    outp = os.path.join(OUT, f"{name}.out")
    scratch = os.path.join(S, f"run-{name}")
    shutil.rmtree(scratch, ignore_errors=True)
    os.makedirs(scratch)
    q = run([sys.executable, counter_path, "--repo", CLONE, "--tip", tip,
             "--scratch", scratch, "--out", outp], env=ENV)
    text = open(outp).read() if os.path.isfile(outp) else q.stdout
    lines = text.splitlines()
    return q.returncode, (lines[1] if len(lines) > 1 else ""), text


def main():
    os.makedirs(OUT, exist_ok=True)
    assert git("rev-parse", "--show-toplevel") == CLONE

    # 1. rebuild the m-text-flip fixture
    git("reset", "--hard", FREEZE)
    p = os.path.join(CLONE, LIVE)
    src = open(p).read()
    assert src.count(ENV_ANCHOR) == 1
    open(p, "w").write(src.replace(ENV_ANCHOR, TEXTFLIP))
    git("add", LIVE)
    r = run(["git", "-C", CLONE, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
             "commit", "-q", "-m", "X7 discrimination: m-text-flip fixture"], env=ENV)
    if r.returncode:
        print(r.stderr[:300]); return 2
    tip = git("rev-parse", "HEAD")
    print(f"m-text-flip fixture tip {tip}")

    # 2. frozen counter
    rc, verdict, text = counter_run(COUNTER, tip, "disc-frozen-m-text-flip")
    print(f"FROZEN counter  exit={rc}  {verdict}")
    frozen_mem_hits = [l for l in text.splitlines() if "mapped bytes" in l]
    print(f"  counter mem-compare hits: {len(frozen_mem_hits)}")

    # 3. counter copy with the mem-compare branch disabled
    src_c = open(COUNTER).read()
    target = ('                if got != want:\n'
              '                    probs.append(f"code: mapped bytes {f[0]} (offset {f[2]}) of {member} '
              'differ from the archive member")\n')
    if src_c.count(target) != 1:
        print(f"mem-compare anchor count = {src_c.count(target)} (expected 1)")
        return 2
    mutant = src_c.replace(target, "")
    cpath = os.path.join(S, "counter-no-memcompare.py")
    open(cpath, "w").write(mutant)
    rc2, verdict2, text2 = counter_run(cpath, tip, "disc-nomemcmp-m-text-flip")
    print(f"MUTATED counter (mem-compare disabled) exit={rc2}  {verdict2}")
    print(f"  verdict unchanged vs frozen? {verdict.split(' met=')[1] == verdict2.split(' met=')[1]}")
    print(f"  mutant counter sha256 {__import__('hashlib').sha256(mutant.encode()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
