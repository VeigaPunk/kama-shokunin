#!/usr/bin/env python3
"""CR01RepeatCounter - round-93 C1 counter forgery sweep.

Seat spec: build probe variants (copies of `git show <M1>:tools/kama-probe.sh`) that are WRONG
yet score `mismatches=0 positive_mismatches=0` under the frozen counter, and list which the
counter catches.  Every variant is run exactly as the frozen controls do:
    python3 tools/round93-router-repeat.py --repo <lane> --rev <M1> --work <scratch>/<name> \
        --probe-file <out>/<name>.sh
so it prints probe=override and can never meet the frozen predicate itself; a 10/10 score here
means the 10 cells cannot distinguish the variant from M1 (counter gap), not that the predicate
is met.

Run with TMPDIR under the seat scratch.  Reads lane files read-only, writes only its own out dir
and --work.
"""
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
OUT = LANE / ".ufo/waves/round-93/w1/out/CR01RepeatCounter"
SCR = Path("/fast/scratch/hyaku/kama-r93/CR01RepeatCounter")
M1 = "fe5f031cb1b9d33e1160360d892149b8ac3c7771"
M1_SHA = "159c80688c5d903ea776e3e548a980f64e6ddedf43b8d7a35ab4724acab48dbb"
COUNTER = LANE / "tools/round93-router-repeat.py"

M1_TEXT = subprocess.run(["git", "-C", str(LANE), "show", f"{M1}:tools/kama-probe.sh"],
                         capture_output=True, check=True).stdout
assert hashlib.sha256(M1_TEXT).hexdigest() == M1_SHA, "M1 probe bytes moved"
TEXT = M1_TEXT.decode()

OLD_STATE = '''def gguf_state(path):
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return gguf_parse(path)
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    if key not in SEEN:
        SEEN[key] = gguf_parse(path)
    return SEEN[key]
'''
OLD_STATES = '    states = [gguf_state(p) for p in paths if os.path.isabs(p)]\n'


def sub(text, old, new):
    assert text.count(old) == 1, f"anchor not unique: {old.splitlines()[0]!r} x{text.count(old)}"
    return text.replace(old, new)


def state_fn(body):
    return sub(TEXT, OLD_STATE, body)


def states_post(new):
    return sub(TEXT, OLD_STATES, OLD_STATES + new)


VARIANTS = {}

VARIANTS["m1-control"] = TEXT  # positive control: the measured probe itself

VARIANTS["key-basename"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = os.path.basename(path)\n")

VARIANTS["key-size"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = st.st_size\n")

VARIANTS["key-size-mtime"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = (st.st_size, st.st_mtime_ns)\n")

VARIANTS["key-name-size"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = (os.path.basename(path), st.st_size)\n")

VARIANTS["key-devino"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = (st.st_dev, st.st_ino)\n")

VARIANTS["key-realpath"] = sub(
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = os.path.realpath(path)\n")

VARIANTS["key-path"] = sub(  # control F2 equivalent, expected caught by R05
    TEXT, "    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)\n",
    "    key = path\n")

# second sighting of any path string -> "invalid" (memo that never re-parses, wrong default)
VARIANTS["repeat-invalid"] = state_fn('''def gguf_state(path):
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return gguf_parse(path)
    if path in SEEN:
        return "invalid"
    SEEN[path] = gguf_parse(path)
    return SEEN[path]
''')

# fail-closed cap: candidates past CAP are never parsed and are graded bad
VARIANTS["cap64-bad"] = states_post('''    if len(states) > 64:
        states = states[:64] + ["invalid"] * (len(states) - 64)
''')
VARIANTS["cap1024-bad"] = states_post('''    if len(states) > 1024:
        states = states[:1024] + ["invalid"] * (len(states) - 1024)
''')
# conservative cap: past CAP -> undecided (expected caught by R04)
VARIANTS["cap64-unknown"] = states_post('''    if len(states) > 64:
        states = states[:64] + ["-"] * (len(states) - 64)
''')

# second sighting of the same IDENTITY -> "invalid" (the assignment's repeat->invalid rule,
# keyed so the repeat is seen through whatever path string names the file); MT01 m07 covers
# "memoize only bad results", this is the opposite default on a repeat.
VARIANTS["identity-repeat-invalid"] = state_fn('''def gguf_state(path):
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    if not stat.S_ISREG(st.st_mode) or os.path.realpath(path).startswith(NO_OPEN):
        return gguf_parse(path)
    key = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    if key in SEEN:
        return "invalid"
    SEEN[key] = gguf_parse(path)
    return SEEN[key]
''')

# fail-closed cap in the bash caller: candidates past N are never parsed and are graded bad
# (the per-entry file_state cap above is inert: every cell entry has one path flag)
BASH_NBAD = '    if [ "$nbad" -lt "$ncand" ]; then unloaded=1; fi\n'
for _n in (64, 1024):
    _tail = ('    if [ "$ncand" -gt %d ]; then nbad=$((nbad + ncand - %d)); '
             '[ -n "$unloadable" ] || unloadable="router-model-invalid"; fi\n' % (_n, _n))
    VARIANTS[f"cap{_n}-bash-bad"] = sub(sub(TEXT, BASH_NBAD, _tail + BASH_NBAD),
                                        '"${cand[@]}")', '"${cand[@]:0:%d}")' % _n)

# first candidate's path state broadcast within one entry
VARIANTS["first-path-broadcast"] = states_post('''    if states:
        states = [states[0]] * len(states)
''')

# cross-call on-disk cache keyed by path string (TMPDIR is set per runner to probe-cwd)
VARIANTS["disk-cache-path"] = state_fn('''def gguf_state(path):
    CACHE = os.path.join(os.environ.get("TMPDIR", "."), ".kama-gguf-cache.json")
    try:
        with open(CACHE) as fh:
            cache = json.load(fh)
    except Exception:
        cache = {}
    if path in cache:
        return cache[path]
    state = gguf_parse(path)
    cache[path] = state
    try:
        with open(CACHE, "w") as fh:
            json.dump(cache, fh)
    except Exception:
        pass
    return state
''')
# cross-call cache keyed by the identity tuple (stale only if size+mtime unchanged)
VARIANTS["disk-cache-identity"] = state_fn('''def gguf_state(path):
    CACHE = os.path.join(os.environ.get("TMPDIR", "."), ".kama-gguf-idcache.json")
    try:
        with open(CACHE) as fh:
            cache = json.load(fh)
    except Exception:
        cache = {}
    try:
        st = os.stat(path)
    except OSError:
        return gguf_parse(path)
    key = "%d:%d:%d:%d" % (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns)
    if key in cache:
        return cache[key]
    state = gguf_parse(path)
    cache[key] = state
    try:
        with open(CACHE, "w") as fh:
            json.dump(cache, fh)
    except Exception:
        pass
    return state
''')

# a decided positive parse is never required: "ok" is reported as undecided
VARIANTS["ok-as-unknown"] = sub(TEXT, '            return "ok"\n', '            return "-"\n')

# pure fixture overfit: no parse at all, only the fixture basenames/sizes
VARIANTS["overfit-names"] = state_fn('''def gguf_state(path):
    try:
        os.stat(path)
    except OSError:
        return "missing"
    if "slow" in os.path.basename(path):
        return "invalid"
    return "-"
''')


def run(name, text):
    outdir = OUT / "forgeries"
    outdir.mkdir(parents=True, exist_ok=True)
    pf = outdir / f"{name}.sh"
    pf.write_text(text)
    work = SCR / "work" / name
    p = subprocess.run([sys.executable, str(COUNTER), "--repo", str(LANE), "--rev", M1,
                        "--work", str(work), "--probe-file", str(pf)],
                       capture_output=True, text=True, timeout=1200)
    lines = p.stdout.splitlines()
    summary = next((l for l in lines if l.startswith("ROUTER_REPEAT ")), "(no summary)")
    bad = [l.split()[1] for l in lines if l.startswith("ROUTER_REPEAT_CELL") and " ok=0 " in l]
    rec = {
        "name": name,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "rc": p.returncode,
        "summary": summary,
        "failed_cells": [b[len("ROUTER_REPEAT_CELL "):] if b.startswith("ROUTER_REPEAT_CELL ") else b
                         for b in bad],
        "stderr": p.stderr.strip()[-400:],
    }
    print(f"FORGERY {name} rc={p.returncode} failed={' '.join(rec['failed_cells']) or 'NONE'} "
          f"| {summary}", flush=True)
    return rec


if __name__ == "__main__":
    only = sys.argv[1:]
    recs = []
    for name, text in VARIANTS.items():
        if only and name not in only:
            continue
        recs.append(run(name, text))
    out_json = OUT / "forgery-sweep.json"
    prior = json.loads(out_json.read_text()) if out_json.exists() else []
    by = {r["name"]: r for r in prior}
    for r in recs:
        by[r["name"]] = r
    out_json.write_text(json.dumps([by[k] for k in sorted(by)], indent=1) + "\n")
    passing = [r["name"] for r in recs if r["rc"] == 0 and "mismatches=0 positive_mismatches=0" in r["summary"]]
    caught = [r["name"] for r in recs if r not in [x for x in recs if x["name"] in passing]]
    print(f"FORGERY_SWEEP total={len(recs)} pass10of10={len(passing)} caught={len(recs) - len(passing)}")
    print("FORGERY_PASS " + " ".join(passing))
    print("FORGERY_CAUGHT " + " ".join(r["name"] for r in recs if r["name"] not in passing))
