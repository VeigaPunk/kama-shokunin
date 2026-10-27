#!/usr/bin/env python3
"""M1C1Mut round-55 C1 counter mutation test (kama lane).

15 single mutants of the frozen counter tools/round54-replay-code-audit.py at
9c60eae6f7ed84f7da93d219a406aadc30958c6c (sha256 c81fe971...), each run against
the case that exercises its leg. 3 battery-style attack trees (m-ldpreload,
m-text-flip, m-member-flip) built once in the scratch clone from the battery
driver's exact anchors. 17 counter runs total (budget <= 25).
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "9c60eae6f7ed84f7da93d219a406aadc30958c6c"
BASETIP = "3a600d2f729828419aaea34cc402c8b0d20fb720"
S = "/fast/scratch/hyaku/kama-r55/w1/M1C1Mut"
CLONE = os.path.join(S, "lane")
COUNTER_SRC = os.path.join(LANE, "tools/round54-replay-code-audit.py")
MUTDIR = os.path.join(S, "mutants")
RUNSCR = os.path.join(S, "runs")
LOGDIR = os.path.join(S, "logs")
OUT = os.path.join(LANE, ".ufo/waves/round-55/w1/out/M1C1Mut")
LIVE = "tools/kama-llamacpp-live.py"
ENV_ANCHOR = "        receipt['child_env_keys'] = sorted(child_env)\n"
FLIP_ANCHOR = "            receipt['code_mappings'] = code_mappings(proc.pid)\n"
PRISTINE_SHA = "c81fe971a0d224622d0cc8bf03a4b61af70ddaca370a873fa8ca65e5110579af"

TREES = {
    "t-ldpreload": (
        ENV_ANCHOR,
        ENV_ANCHOR + "        child_env['LD_PRELOAD'] = '/usr/lib/libzstd.so.1.5.7'\n",
    ),
    "t-text-flip": (
        ENV_ANCHOR,
        ENV_ANCHOR
        + "        import glob as _g\n"
        + "        for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-rpc.so*')):\n"
        + "            if os.path.getsize(_p) > 0x6000:\n"
        + "                with open(_p, 'r+b') as fh:\n"
        + "                    fh.seek(-0x3000, 2)\n"
        + "                    _b = fh.read(1)\n"
        + "                    fh.seek(-0x3000, 2)\n"
        + "                    fh.write(bytes([_b[0] ^ 1]))\n"
        + "                break\n",
    ),
    "t-member-flip": (
        FLIP_ANCHOR,
        FLIP_ANCHOR
        + "            import glob as _g\n"
        + "            for _p in _g.glob(os.path.join(os.path.dirname(server_real), 'libggml-cpu-*.so*')):\n"
        + "                try:\n"
        + "                    with open(_p, 'r+b') as fh:\n"
        + "                        fh.seek(-32, 2)\n"
        + "                        _b = fh.read(1)\n"
        + "                        fh.seek(-32, 2)\n"
        + "                        fh.write(bytes([_b[0] ^ 1]))\n"
        + "                except OSError:\n"
        + "                    pass\n",
    ),
}

MUTANTS = {
    # --- code_observe classification ---
    "A1-drop-mem-compare": (
        "code",
        "t-text-flip",
        '                if got != want:\n'
        '                    probs.append(f"code: mapped bytes {f[0]} (offset {f[2]}) of {member} differ from the archive member")\n',
        "",
    ),
    "A2-first-page-only": (
        "code",
        "t-text-flip",
        "                length = hi - lo\n",
        "                length = hi - lo\n                length = min(length, 4096)\n",
    ),
    "A3-accept-any-uid": (
        "code",
        "clean",
        "                if st.st_uid != 0 or str(st.st_ino) != ino or os.access(path, os.W_OK):\n",
        "                if str(st.st_ino) != ino or os.access(path, os.W_OK):\n",
    ),
    "A4-drop-writable-test": (
        "code",
        "clean",
        "                if st.st_uid != 0 or str(st.st_ino) != ino or os.access(path, os.W_OK):\n",
        "                if st.st_uid != 0 or str(st.st_ino) != ino:\n",
    ),
    "A5-skip-hostlibs-basename": (
        "code",
        "clean",
        '                if os.path.basename(path) not in HOST_LIBS:\n'
        '                    probs.append(f"code: root-owned host library {path} is not in the frozen host set")\n'
        "                    continue\n",
        "",
    ),
    "A6-drop-REQUIRED": (
        "code",
        "clean",
        '    for pat in REQUIRED:\n'
        '        if not any(fnmatch.fnmatchcase(n, pat) for n in names):\n'
        '            probs.append(f"code: no mapped archive member matches {pat} (mapped: {sorted(names)})")\n',
        "",
    ),
    "A7-memfd-by-name-only": (
        "code",
        "clean",
        "                if own is None or (dev_f := f[3], ino_f := f[4]) != (own[0], own[1]):\n",
        "                if own is None:\n",
    ),
    "A8-skip-KERNEL_MAPS": (
        "code",
        "clean",
        "                if name in KERNEL_MAPS:\n                    continue\n",
        "",
    ),
    # --- env_leg ---
    "B1-drop-BAD_ENV-check": (
        "envnames",
        "t-ldpreload",
        '    for bad in BAD_ENV:\n'
        '        if bad in keys:\n'
        '            probs.append(f"env: server environment carries {bad}")\n'
        "    return sorted(keys)\n",
        "    return sorted(keys)\n",
    ),
    "B2-read-env-values": (
        "envnames",
        "t-ldpreload",
        '            probs.append(f"env: server environment carries {bad}")\n    return sorted(keys)\n',
        '            probs.append(f"env: server environment carries {bad}")\n'
        '    with open(f"/proc/{pid}/environ", "rb") as _fh:\n'
        '        _vals = {e.split(b"=", 1)[0]: e.split(b"=", 1)[1] for e in _fh.read().split(b"\\0") if b"=" in e}\n'
        '    return sorted(f"{k}={_vals[k.encode()].decode(\'utf-8\', \'replace\')}" for k in keys)\n',
    ),
    # --- bind_one descendant gate ---
    "C1-drop-descendant-gate": (
        "bind",
        "clean",
        "            if rp is None or not descends_from(pid, rp):\n",
        "            if False:\n",
    ),
    # --- twopass snapshot compare ---
    "D1-drop-twopass-compare": (
        "twopass",
        "clean",
        '                            if first["snaps"] != second["snaps"]:\n'
        '                                cprobs.append("code: executable bytes differ between the two observation passes")\n',
        "",
    ),
    # --- rehash leg ---
    "E1-drop-rehash": (
        "rehash",
        "t-member-flip",
        '            if cobs is not None and arc is not None:\n'
        '                # J7Late facet 1: a library rewritten after the observation and left\n'
        '                # rewritten fails here - the tree outlives the server\n'
        '                for path, (dev, ino, member) in sorted(cobs["files"].items()):\n'
        '                    want = hashlib.sha256(arc.member(member)).hexdigest()\n'
        '                    try:\n'
        '                        st, digest = os.stat(path), sha_file(path)\n'
        '                    except OSError as exc:\n'
        '                        rprobs.append(f"{path} not re-readable after the replay: {exc.strerror}")\n'
        '                        continue\n'
        '                    if str(st.st_ino) != ino or digest != want:\n'
        '                        rprobs.append(f"{path} changed after the observation: inode "\n'
        '                                      f"{st.st_ino} != {ino} or digest {digest} != {want}")\n'
        '                rehash_n = len(cobs["files"])\n',
        "            if cobs is not None and arc is not None:\n                rehash_n = 0\n",
    ),
    # --- newrow leg ---
    "F1-newrow-always-true": (
        "newrow",
        "base",
        "    return bool(hit)\n",
        "    return True\n",
    ),
    # --- clean_env ---
    "G1-strip-only-GIT_DIR": (
        "clean_env",
        "hostile",
        '    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}\n',
        '    env = {k: v for k, v in os.environ.items() if k != "GIT_DIR"}\n',
    ),
}

RUNS = [
    ("R0-pristine-clean", None, "clean"),
    ("A1-drop-mem-compare", "A1-drop-mem-compare", "t-text-flip"),
    ("A2-first-page-only", "A2-first-page-only", "t-text-flip"),
    ("A3-accept-any-uid", "A3-accept-any-uid", "clean"),
    ("A4-drop-writable-test", "A4-drop-writable-test", "clean"),
    ("A5-skip-hostlibs-basename", "A5-skip-hostlibs-basename", "clean"),
    ("A6-drop-REQUIRED", "A6-drop-REQUIRED", "clean"),
    ("A7-memfd-by-name-only", "A7-memfd-by-name-only", "clean"),
    ("A8-skip-KERNEL_MAPS", "A8-skip-KERNEL_MAPS", "clean"),
    ("B1-drop-BAD_ENV-check", "B1-drop-BAD_ENV-check", "t-ldpreload"),
    ("B2-read-env-values", "B2-read-env-values", "t-ldpreload"),
    ("C1-drop-descendant-gate", "C1-drop-descendant-gate", "clean"),
    ("D1-drop-twopass-compare", "D1-drop-twopass-compare", "clean"),
    ("E1-drop-rehash", "E1-drop-rehash", "t-member-flip"),
    ("F1-newrow-always-true", "F1-newrow-always-true", "base"),
    ("G1-strip-only-GIT_DIR", "G1-strip-only-GIT_DIR", "hostile"),
    ("G0-pristine-hostile", None, "hostile"),
]


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def base_env():
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def sh(cmd):
    r = run(cmd, env=base_env())
    if r.returncode != 0:
        raise SystemExit(f"driver: {cmd}: rc={r.returncode} {r.stderr[:300]}")
    return r.stdout.strip()


def build_trees():
    live_path = os.path.join(CLONE, LIVE)
    toplevel = sh(["git", "-C", CLONE, "rev-parse", "--show-toplevel"])
    assert toplevel == CLONE, f"toplevel {toplevel} != {CLONE}"
    sh(["git", "-C", CLONE, "reset", "--hard", FREEZE])
    original = open(live_path).read()
    tips = {}
    for name, (old, new) in TREES.items():
        sh(["git", "-C", CLONE, "reset", "--hard", FREEZE])
        src = open(live_path).read()
        assert src == original, f"{name}: clone not at freeze content"
        assert src.count(old) == 1, f"{name}: live anchor count {src.count(old)}"
        open(live_path, "w").write(src.replace(old, new))
        sh(["git", "-C", CLONE, "add", LIVE])
        sh(["git", "-C", CLONE, "-c", "user.name=fx", "-c", "user.email=fx@invalid",
            "commit", "-q", "-m", f"M1C1Mut attack tree {name} (battery-style)"])
        tips[name] = sh(["git", "-C", CLONE, "rev-parse", "HEAD"])
    sh(["git", "-C", CLONE, "reset", "--hard", FREEZE])
    return tips


def make_mutants():
    src = open(COUNTER_SRC).read()
    got = hashlib.sha256(src.encode()).hexdigest()
    assert got == PRISTINE_SHA, f"lane counter sha {got} != frozen {PRISTINE_SHA}"
    shutil.copy2(COUNTER_SRC, os.path.join(MUTDIR, "pristine.py"))
    shas = {"pristine": got}
    for name, (_leg, _case, old, new) in MUTANTS.items():
        assert src.count(old) == 1, f"{name}: counter anchor count {src.count(old)}"
        patched = src.replace(old, new)
        p = os.path.join(MUTDIR, f"{name}.py")
        open(p, "w").write(patched)
        shas[name] = hashlib.sha256(patched.encode()).hexdigest()
        with open(os.path.join(MUTDIR, f"{name}.diff"), "w") as fh:
            r = run(["diff", "-u", os.path.join(MUTDIR, "pristine.py"), p])
            fh.write(r.stdout)
    return shas


def one_run(item):
    run_name, mut_name, case = item
    tips = TIPS
    if case == "clean":
        tip, extra = FREEZE, {}
    elif case == "base":
        tip, extra = BASETIP, {}
    elif case == "hostile":
        tip, extra = FREEZE, {"GIT_OBJECT_DIRECTORY": os.path.join(S, "empty-objects")}
    else:
        tip, extra = tips[case], {}
    counter = os.path.join(MUTDIR, f"{mut_name}.py") if mut_name else os.path.join(MUTDIR, "pristine.py")
    env = base_env()
    env["TMPDIR"] = os.path.join(S, "tmp")
    env.update(extra)
    rscratch = os.path.join(RUNSCR, run_name)
    os.makedirs(rscratch, exist_ok=True)
    outp = os.path.join(OUT, f"{run_name}.out")
    t0 = time.monotonic()
    try:
        p = run([sys.executable, counter, "--repo", CLONE, "--tip", tip,
                 "--scratch", rscratch, "--out", outp], env=env, timeout=700)
        rc, err = p.returncode, p.stderr[-400:]
    except subprocess.TimeoutExpired:
        rc, err = -9, "TIMEOUT 700s"
    dt = time.monotonic() - t0
    text = open(outp).read() if os.path.isfile(outp) else ""
    lines = text.splitlines()
    legs = lines[1] if len(lines) > 1 else "(no receipt)"
    met = "met=True" in legs
    with open(os.path.join(LOGDIR, f"{run_name}.log"), "w") as fh:
        fh.write(f"cmd rc={rc}\nstderr tail:\n{err}\n--- stdout/receipt ---\n{text}\n")
    return {"run": run_name, "mutant": mut_name or "pristine", "case": case, "tip": tip,
            "exit": rc, "met": met, "legs": legs, "seconds": round(dt, 1),
            "mutant_sha256": SHAS.get(mut_name or "pristine"), "env_extra": sorted(extra)}


def main():
    global TIPS, SHAS
    for d in (MUTDIR, RUNSCR, LOGDIR, OUT, os.path.join(S, "tmp"), os.path.join(S, "empty-objects")):
        os.makedirs(d, exist_ok=True)
    SHAS = make_mutants()
    TIPS = build_trees()
    print("tree tips:", json.dumps(TIPS, indent=1), flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for res in pool.map(one_run, RUNS):
            results.append(res)
            print(f"done {res['run']}: exit={res['exit']} met={res['met']} ({res['seconds']}s)", flush=True)
    with open(os.path.join(S, "results.json"), "w") as fh:
        json.dump({"trees": TIPS, "mutant_sha256": SHAS, "results": results}, fh, indent=1)
    shutil.copy(os.path.join(S, "results.json"), os.path.join(OUT, "results.json"))
    print("\n==== SUMMARY ====")
    for r in results:
        print(f"{r['run']:28s} case={r['case']:13s} exit={r['exit']:3d} met={str(r['met']):5s} | {r['legs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
