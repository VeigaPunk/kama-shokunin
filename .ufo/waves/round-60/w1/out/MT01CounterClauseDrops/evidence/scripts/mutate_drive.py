#!/usr/bin/env python3
"""MT01CounterClauseDrops: clause-drop mutation test of round60-c1-counter.py verify().

Makes scratch mutants (one clause dropped each), runs baseline + mutants against the
frozen tip, records outputs. Lane tree is never written; lane file hash before/after
is recorded as restoration evidence.
"""
import concurrent.futures
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SRC = LANE / "tools/round60-c1-counter.py"
TIP = "e0b5b1ead9adb7a5a4744caca8837ec6496e1ca1"
S = pathlib.Path("/fast/scratch/hyaku/kama-r60/MT01CounterClauseDrops")
MUT = S / "mutants"
RES = S / "results"
WORK = S / "work"
REQUIRED = ["binary-digest", "model-digest", "port-unregistered", "ready", "version",
            "running-exe-digest", "listener-owned", "tags-empty-before-create", "create",
            "tags-lists-model", "v1-models-lists-model", "evidence-before-load", "generate",
            "ps-lists-loaded", "evidence-after-load", "teardown"]

MUTANTS = [
    ("nonce",        [('bad.append("nonce")', "pass")], 1),
    ("verdict",      [('bad.append("verdict")', "pass")], 1),
    ("binary-sha",   [('bad.append("binary-sha")', "pass")], 1),
    ("port",         [('bad.append("port")', "pass")], 1),
    ("capture-sha",  [('bad.append("capture-sha:" + name)', "pass")], 1),
    ("tags-entry",   [('bad.append("tags-entry")', "pass")], 1),
    ("ps-digest",    [('bad.append("ps-digest")', "pass")], 1),
    ("version",      [('bad.append("version")', "pass")], 1),
    ("teardown",     [('bad.append("teardown")', "pass")], 1),
    ("log-listening",[('bad.append("log-listening")', "pass")], 1),
    ("log-generate", [('bad.append("log-generate")', "pass")], 1),
    ("manifest",     [('bad.append("manifest")', "pass")], 1),
    ("manifest-layer",[('bad.append("manifest-layer")', "pass")], 2),
    ("blob-sha",     [('bad.append("blob-sha")', "pass")], 1),
    ("req-all",      [('bad.append("check:" + cid)', "pass")], 1),
] + [
    (f"req-{cid}",
     [('for cid in REQUIRED:', f'for cid in [x for x in REQUIRED if x != "{cid}"]:')], 1)
    for cid in REQUIRED
]


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def make_mutants():
    src = SRC.read_text()
    MUT.mkdir(parents=True, exist_ok=True)
    index = []
    for name, reps, expect in MUTANTS:
        txt = src
        for old, new in reps:
            n = txt.count(old)
            assert n == expect, f"{name}: {old!r} found {n}x, expected {expect}"
            txt = txt.replace(old, new)
        (MUT / f"{name}.py").write_text(txt)
        index.append((name, sha(MUT / f"{name}.py")))
    return index


def run_one(tag, path):
    out = RES / f"{tag}.txt"
    env = dict(os.environ)
    env["TMPDIR"] = str(S / "tmp")
    wdir = WORK / tag
    wdir.mkdir(parents=True, exist_ok=True)
    p = subprocess.run([sys.executable, str(path), "--repo", str(LANE), "--tip", TIP,
                        "--work", str(wdir)],
                       capture_output=True, text=True, env=env, timeout=900)
    body = f"exit={p.returncode}\nstdout: {p.stdout.strip()}\nstderr: {p.stderr.strip()[-400:]}"
    out.write_text(body)
    return tag, p.returncode, p.stdout.strip()


def main():
    (S / "tmp").mkdir(parents=True, exist_ok=True)
    RES.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    before = sha(SRC)
    (S / "lane-counter-before.sha256").write_text(before + "\n")
    shutil.copyfile(SRC, S / "pristine.py")
    index = make_mutants()
    (S / "mutant-hashes.txt").write_text(
        "".join(f"{h}  {n}.py\n" for n, h in index))
    jobs = [("pristine", S / "pristine.py")] + [(n, MUT / f"{n}.py") for n, _ in index]
    # baseline gate first
    tag, rc, so = run_one(*jobs[0])
    print(f"BASELINE {tag}: exit={rc} :: {so}", flush=True)
    if "met=True" not in so:
        print("BASELINE FAILED -> mutants inconclusive; stopping", flush=True)
        return 2
    rest = jobs[1:]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(run_one, t, p) for t, p in rest]
        for f in concurrent.futures.as_completed(futs):
            tag, rc, so = f.result()
            print(f"MUTANT {tag}: exit={rc} :: {so}", flush=True)
    after = sha(SRC)
    (S / "lane-counter-after.sha256").write_text(after + "\n")
    print(f"RESTORATION lane-before={before}\nRESTORATION lane-after={after}\n"
          f"RESTORATION identical={before == after}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
