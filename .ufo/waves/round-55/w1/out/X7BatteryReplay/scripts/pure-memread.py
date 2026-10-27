#!/usr/bin/env python3
"""X7 test 2: a counter variant that keeps ONLY its own /proc/<pid>/mem read
as the code-leg evidence (drops the replay self-report cross-check and the
rehash leg).  Does the battery's m-text-flip mutant still kill it?

If it prints met=True, the battery's code-leg mutant is INVISIBLE to a counter
whose code evidence comes only from its own memory read - i.e. the battery does
not discriminate the counter's memory-read mechanism.
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
PROBE_FLIP = (
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


def build_fixture(patch, msg):
    git("reset", "--hard", FREEZE)
    p = os.path.join(CLONE, LIVE)
    src = open(p).read()
    assert src.count(ENV_ANCHOR) == 1
    open(p, "w").write(src.replace(ENV_ANCHOR, patch))
    git("add", LIVE)
    r = run(["git", "-C", CLONE, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
             "commit", "-q", "-m", msg], env=ENV)
    if r.returncode:
        print(r.stderr[:300]); raise SystemExit(2)
    return git("rev-parse", "HEAD")


def make_pure_memread_counter(path):
    """Keep ONLY the counter's own /proc/<pid>/mem comparison as code evidence.

    - code_observe: keep the mem read + the `got != want` comparison (and the
      anon / memfd / host-lib classification), DROP nothing there.
    - bind_one: drop the replay self-report cross-check block (the own_code /
      code_mappings digest comparison against the replay's report).
    - bind_one: drop the rehash leg (post-exit re-hash of the observed paths).
    """
    lines = open(COUNTER).read().splitlines(keepends=True)

    def find(sub, start=0):
        for i in range(start, len(lines)):
            if sub in lines[i]:
                return i
        return -1

    # (2) drop the rehash leg: from the 'if cobs is not None and arc is not None:'
    #     line up to and including the 'rehash_n = len(cobs["files"])' line
    r_start = find("if cobs is not None and arc is not None:")
    r_end = find('rehash_n = len(cobs["files"])', r_start)
    if r_start < 0 or r_end < 0:
        print(f"rehash block not found (start={r_start} end={r_end})")
        return None
    del lines[r_start:r_end + 1]

    # (1) drop the replay self-report cross-check: from the 'cm = rr.get("code_mappings")'
    #     line up to and including the 'own_code.members[...] != archive digest' line
    s_start = find('cm = rr.get("code_mappings")') - 1   # the 'if cobs is not None:' line above it
    s_end = find('!= archive digest")', s_start)
    if s_start < 0 or s_end < 0:
        print(f"self-report block not found (start={s_start} end={s_end})")
        return None
    if "if cobs is not None:" not in lines[s_start]:
        print(f"unexpected block start: {lines[s_start]!r}")
        return None
    del lines[s_start:s_end + 1]

    src = "".join(lines)
    open(path, "w").write(src)
    return src


def main():
    os.makedirs(OUT, exist_ok=True)
    assert git("rev-parse", "--show-toplevel") == CLONE
    cpath = os.path.join(S, "counter-pure-memread.py")
    src = make_pure_memread_counter(cpath)
    if src is None:
        return 2
    import hashlib
    print(f"pure-memread counter sha256 {hashlib.sha256(src.encode()).hexdigest()}")

    for label, patch, name in [("m-text-flip (battery, -0x3000)", TEXTFLIP, "pure-memread-m-text-flip"),
                               ("in-text probe (0x30000)", PROBE_FLIP, "pure-memread-in-text")]:
        tip = build_fixture(patch, f"X7 pure-memread fixture: {label}")
        rc, verdict, text = counter_run(cpath, tip, name)
        hits = [l for l in text.splitlines() if "mapped bytes" in l]
        print(f"{label}: exit={rc}  {verdict}")
        print(f"    mem-compare hits: {len(hits)}")

    # also: the frozen counter on the in-text fixture, for the record
    tip = build_fixture(PROBE_FLIP, "X7 frozen-counter fixture: in-text")
    rc, verdict, _ = counter_run(COUNTER, tip, "frozen-in-text")
    print(f"FROZEN counter on in-text fixture: exit={rc}  {verdict}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
