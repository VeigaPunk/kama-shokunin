#!/usr/bin/env python3
"""round-55 C1 kill battery (kama): named mutants of the live tool must each fail the
frozen round-55 C1 counter with their named leg, and the unmutated positive control
must pass. Run: python3 .ufo/waves/round-55/c1/battery/run-battery.py
Receipts land in .ufo/waves/round-55/c1/battery/ beside this file. Everything else
lives under /fast/scratch/hyaku/kama-r55/c1/battery and is removed on exit.
"""
import os
import re
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
COUNTER = os.path.join(LANE, "tools/round54-replay-code-audit.py")
OUT = os.path.join(LANE, ".ufo/waves/round-55/c1/battery")
SCRATCH = "/fast/scratch/hyaku/kama-r55/c1/battery"
LIVE = "tools/kama-llamacpp-live.py"

ENV_ANCHOR = "        receipt['child_env_keys'] = sorted(child_env)\n"
FLIP_ANCHOR = "            receipt['code_mappings'] = code_mappings(proc.pid)\n"

MUTANTS = {
    # envnames leg: a frozen-set root-owned preloaded library - mapping is admissible,
    # the LD_PRELOAD name itself is the failure
    "m-ldpreload": (
        "envnames",
        "kill",
        ENV_ANCHOR,
        "        child_env['LD_PRELOAD'] = '/usr/lib/libzstd.so.1.5.7'\n" + ENV_ANCHOR,
    ),
    # code leg: flip one byte INSIDE libggml-rpc's mapped executable segment before
    # the server starts (post-extract, pre-Popen), so the counter's own
    # /proc/<pid>/mem vs archive-member compare fails. Round-55 X7: the previous
    # offset (size-0x3000) landed in .strtab, outside every LOAD segment, so the
    # flipped byte was never mapped and the counter's mem compare never fired (the
    # kill came from the replay's self-report and the rehash leg instead). 0x30000
    # is inside .text (exec LOAD file extent 0x12000..0x31469); the server still
    # starts clean (X7 probe: sealed 3/3, twopass 3/3).
    "m-text-flip": (
        "code",
        "kill",
        ENV_ANCHOR,
        "        import glob as _g\n"
        "        for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-rpc.so*')):\n"
        "            if os.path.getsize(_p) > 0x40000:\n"
        "                with open(_p, 'r+b') as fh:\n"
        "                    fh.seek(0x30000)\n"
        "                    _b = fh.read(1)\n"
        "                    fh.seek(0x30000)\n"
        "                    fh.write(bytes([_b[0] ^ 1]))\n"
        "                break\n" + ENV_ANCHOR,
    ),
    # hostlibs leg: not reproducible as a non-root mutant - any same-uid mapping fails
    # the code/archive classification first (the leg guards root-actor plants, the
    # K1Cheat class), and the LD_AUDIT vector for loading a root-owned foreign lib is
    # empirically void on this glibc (receipt m-ldaudit-foreign below). Recorded as a
    # vector analysis, not a live kill.
    "m-ldaudit-foreign": (
        "hostlibs",
        "vector",  # expect met=True: the LD_AUDIT vector is void on this glibc; the
                   # receipt is the evidence that the live hostlibs kill is root-gated
        ENV_ANCHOR,
        "        child_env['LD_AUDIT'] = '/usr/lib/libexpat.so.1'\n" + ENV_ANCHOR,
    ),
    # rehash leg: after the server mapped its cpu backend, flip one byte near the end
    # of EVERY libggml-cpu variant (this host loads zen4; flipping only the first glob
    # hit missed it) - mapped pages unchanged, the observed path's file digest changes.
    # Synchronous: the counter can observe and release inside 300 ms, so a delayed
    # threaded flip races the re-hash (the first battery run showed met=True for it).
    "m-member-flip": (
        "rehash",
        "kill",
        FLIP_ANCHOR,
        FLIP_ANCHOR +
        "            import glob as _g\n"
        "            for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-cpu-*.so*')):\n"
        "                try:\n"
        "                    with open(_p, 'r+b') as fh:\n"
        "                        fh.seek(-32, 2)\n"
        "                        _b = fh.read(1)\n"
        "                        fh.seek(-32, 2)\n"
        "                        fh.write(bytes([_b[0] ^ 1]))\n"
        "                except OSError:\n"
        "                    pass\n",
    ),
}


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


GREEN = {"bind": lambda v: v == "1", "sealed": lambda v: v == "1",
         "code": lambda v: v == "1", "teardown": lambda v: v == "1",
         "newrow": lambda v: v == "1", "rehash": lambda v: v == "0"}


def leg_failed(text, leg):
    """True when the receipt's OWN summary line says the named leg did not pass.

    run-battery.py's previous check grepped every `detail:` line for "<leg> ",
    which the PASSING detail lines satisfy too ("detail: code b1: 8 archive files
    ... byte-equal"), so it could never distinguish a killed leg from a green one
    (round-55 seat X7).  The summary line at index 1 carries the per-leg verdict,
    so read it there.
    """
    lines = text.splitlines()
    if len(lines) < 2:
        return False
    summary = lines[1]
    m = re.search(rf"(?<![A-Za-z]){re.escape(leg)}=(\d+)(?:/(\d+))?", summary)
    if not m:
        return False
    if leg in GREEN:
        return not GREEN[leg](m.group(1))
    if m.group(2) is not None:
        return m.group(1) != m.group(2)          # n/3 style: killed unless n == 3
    return m.group(1) != "0"                     # a bare counter: killed unless 0


def main():
    os.makedirs(OUT, exist_ok=True)
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(SCRATCH)
    clone = os.path.join(SCRATCH, "lane")
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = run(["git", "clone", "--shared", LANE, clone], env=env)
    if r.returncode:
        print(f"battery: clone failed: {r.stderr[:300]}")
        return 2
    live_path = os.path.join(clone, LIVE)
    original = open(live_path).read()
    summary = []

    def counter(tip, name):
        outp = os.path.join(OUT, f"{name}.out")
        p = run([sys.executable, COUNTER, "--repo", clone, "--tip", tip,
                 "--scratch", os.path.join(SCRATCH, f"run-{name}"), "--out", outp], env=env)
        text = open(outp).read() if os.path.isfile(outp) else p.stdout
        met = "met=True" in text.splitlines()[1] if len(text.splitlines()) > 1 else False
        return p.returncode, met, text

    # positive control: the unmutated freeze tip passes
    rc, met, _ = counter(FREEZE, "control")
    summary.append(("control", "all legs", "kill", rc, met, rc == 0 and met))

    for name, (leg, kind, old, new) in MUTANTS.items():
        # reset the clone to the freeze tip and apply exactly one mutant
        run(["git", "-C", clone, "reset", "--hard", FREEZE], env=env)
        src = open(live_path).read()
        if src != original:
            print(f"battery: {name}: clone not clean after reset")
            return 2
        if src.count(old) != 1:
            print(f"battery: {name}: anchor not unique ({src.count(old)})")
            return 2
        open(live_path, "w").write(src.replace(old, new))
        run(["git", "-C", clone, "add", LIVE], env=env)
        r = run(["git", "-C", clone, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
                 "commit", "-q", "-m", f"battery mutant {name}"], env=env)
        if r.returncode:
            print(f"battery: {name}: fixture commit failed: {r.stderr[:300]}")
            return 2
        tip = run(["git", "-C", clone, "rev-parse", "HEAD"], env=env).stdout.strip()
        rc, met, text = counter(tip, name)
        if kind == "vector":
            ok = rc == 0 and met  # the vector is void: the mutant passes, which is the finding
        else:
            ok = rc == 1 and not met and leg_failed(text, leg)
        summary.append((name, leg, kind, rc, met, ok))

    for name, leg, kind, rc, met, ok in summary:
        print(f"battery {name}: leg={leg} kind={kind} exit={rc} met={met} -> {'ok' if ok else 'BATTERY-FAIL'}")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if all(s[5] for s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
