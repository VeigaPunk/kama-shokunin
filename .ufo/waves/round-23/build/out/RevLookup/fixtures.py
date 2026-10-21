#!/usr/bin/env python3
"""RevLookup fault matrix for lookup() in tools/report-landing-audit.py.

Compares the frozen base blob (4fe9339f) with a snapshot of the lane working
tree. Every repository is a fresh temp repo under /tmp/kama-r23/RevLookup/fx.
No lane or fleet repository is read or written.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import zlib
from collections import defaultdict
from pathlib import Path

WORK = Path("/tmp/kama-r23/RevLookup")
ROOT = WORK / "fx"
FAKE40 = "e4f1c2a9b7d30816f5e2a4b9c0d1e2f3a4b5c6d7"
N_OBJ = 90000

shutil.rmtree(ROOT, ignore_errors=True)
ROOT.mkdir(parents=True)
HOME = ROOT / "_home"
HOME.mkdir()
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(HOME=str(HOME), GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


BASE = load("base_audit", WORK / "base_audit.py")
CUR = load("cur_audit", os.environ.get("CUR_PY", str(WORK / "cur_audit_v2.py")))
RESULTS = []


def git(repo, *args, inp=None):
    proc = subprocess.run(["git", "-C", str(repo), *args], input=inp,
                          capture_output=True, env=ENV)
    if proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={proc.returncode}: "
                           f"{proc.stderr.decode(errors='replace').strip()}")
    return proc.stdout.decode("utf-8", errors="replace").strip()


def newrepo(name):
    path = ROOT / name
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    return path


def mkcommit(repo, msg):
    tree = git(repo, "mktree", inp=b"")
    return git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
               "commit-tree", tree, "-m", msg)


def lk(mod, repos, tokens, peel=""):
    try:
        return dict(sorted(mod.lookup(tuple(repos), list(tokens), peel).items()))
    except Exception as exc:  # recorded, never hidden
        return f"{type(exc).__name__}: {exc}"[:220]


def record(case, probe, peel, base, cur, note=""):
    RESULTS.append({"case": case, "probe": probe, "peel": peel or "-",
                    "base": base, "cur": cur, "note": note})


def case_replace_fabricated():
    repo = newrepo("replace_fabricated")
    blob = git(repo, "hash-object", "-w", "--stdin", inp=b"hello\n")
    git(repo, "update-ref", f"refs/replace/{FAKE40}", blob)
    record("refs/replace names a fabricated 40-hex oid -> existing blob",
           FAKE40, "", lk(BASE, [repo], [FAKE40]), lk(CUR, [repo], [FAKE40]))
    record("control: real blob with the same replace ref present", blob, "",
           lk(BASE, [repo], [blob]), lk(CUR, [repo], [blob]))


def case_replace_type():
    repo = newrepo("replace_type")
    commit = mkcommit(repo, "real commit")
    blob = git(repo, "hash-object", "-w", "--stdin", inp=b"not a commit\n")
    git(repo, "update-ref", f"refs/replace/{commit}", blob)
    record("refs/replace: real commit replaced by a blob", commit, "^{commit}",
           lk(BASE, [repo], [commit], "^{commit}"),
           lk(CUR, [repo], [commit], "^{commit}"))
    record("refs/replace: real commit replaced by a blob", commit, "",
           lk(BASE, [repo], [commit]), lk(CUR, [repo], [commit]))


def case_promisor_exec():
    src = newrepo("promisor_exec_src")
    obj = mkcommit(src, "object absent locally")
    fake_ssh = ROOT / "fake_ssh.sh"
    cells = {}
    for label, mod in (("base", BASE), ("cur", CUR)):
        repo = newrepo(f"promisor_exec_{label}")
        sentinel = repo / "SENTINEL"
        fake_ssh.write_text(f"#!/bin/sh\necho ran >> {sentinel}\nexit 1\n")
        fake_ssh.chmod(0o755)
        git(repo, "config", "extensions.partialclone", "origin")
        git(repo, "config", "remote.origin.promisor", "true")
        git(repo, "config", "remote.origin.url", "ssh://example.invalid/none.git")
        git(repo, "config", "core.sshCommand", str(fake_ssh))
        value = lk(mod, [repo], [obj])
        cells[label] = f"{value} | sshCommand ran={sentinel.exists()}"
    record("promisor remote, object absent locally, core.sshCommand planted",
           obj, "", cells["base"], cells["cur"])


def case_promisor_available():
    src = newrepo("promisor_avail_src")
    obj = mkcommit(src, "object served by file remote")
    git(src, "config", "uploadpack.allowAnySHA1InWant", "true")
    cells = {}
    for label, mod in (("base", BASE), ("cur", CUR)):
        repo = newrepo(f"promisor_avail_{label}")
        git(repo, "config", "extensions.partialclone", "origin")
        git(repo, "config", "remote.origin.promisor", "true")
        git(repo, "config", "remote.origin.url", f"file://{src}")
        cells[label] = lk(mod, [repo], [obj])
    record("promisor remote serves the object (file://), absent locally",
           obj, "", cells["base"], cells["cur"])
    check = newrepo("promisor_avail_check")
    git(check, "config", "extensions.partialclone", "origin")
    try:
        CUR.check_history_repo(check)
        refusal = "accepted"
    except CUR.EvalError as exc:
        refusal = f"EvalError: {exc}"
    record("cur run-level gate on the same promisor config", "-", "-",
           "no gate in base", refusal)


def case_ref_shadow():
    repo = newrepo("ref_shadow")
    commit = mkcommit(repo, "shadow target")
    short = "a1b2c3d"
    assert not commit.startswith(short)
    git(repo, "update-ref", f"refs/heads/{short}", commit)
    record("branch named as a fabricated 7-hex citation", short, "",
           lk(BASE, [repo], [short]), lk(CUR, [repo], [short]))
    record("branch named as a fabricated 7-hex citation", short, "^{commit}",
           lk(BASE, [repo], [short], "^{commit}"),
           lk(CUR, [repo], [short], "^{commit}"))
    tag = "b2c3d4e"
    assert not commit.startswith(tag)
    git(repo, "update-ref", f"refs/tags/{tag}", commit)
    record("tag named as a fabricated 7-hex citation", tag, "^{commit}",
           lk(BASE, [repo], [tag], "^{commit}"),
           lk(CUR, [repo], [tag], "^{commit}"))
    real = commit[:7]
    record("control: real 7-hex prefix of the same commit", real, "^{commit}",
           lk(BASE, [repo], [real], "^{commit}"),
           lk(CUR, [repo], [real], "^{commit}"))
    git(repo, "update-ref", f"refs/heads/{FAKE40}", commit)
    record("control: branch named as a fabricated 40-hex", FAKE40, "",
           lk(BASE, [repo], [FAKE40]), lk(CUR, [repo], [FAKE40]))
    record("control: branch named as a fabricated 40-hex", FAKE40, "^{commit}",
           lk(BASE, [repo], [FAKE40], "^{commit}"),
           lk(CUR, [repo], [FAKE40], "^{commit}"))


def case_planted_object():
    repo = newrepo("planted_object")
    objdir = repo / ".git" / "objects" / FAKE40[:2]
    objdir.mkdir(parents=True, exist_ok=True)
    (objdir / FAKE40[2:]).write_bytes(zlib.compress(b"blob 3\x00abc"))
    try:
        kind = git(repo, "cat-file", "-t", FAKE40)
    except RuntimeError as exc:
        kind = f"cat-file -t failed: {exc}"
    record(f"loose object at a fabricated name whose bytes do not hash to it "
           f"(git cat-file -t: {kind})", FAKE40, "",
           lk(BASE, [repo], [FAKE40]), lk(CUR, [repo], [FAKE40]))
    record("same planted loose object, peel", FAKE40, "^{commit}",
           lk(BASE, [repo], [FAKE40], "^{commit}"),
           lk(CUR, [repo], [FAKE40], "^{commit}"))


def case_annotated_tag():
    repo = newrepo("annotated_tag")
    commit = mkcommit(repo, "tagged commit")
    git(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
        "tag", "-a", "-m", "t", "v1", commit)
    tag_obj = git(repo, "rev-parse", "refs/tags/v1")
    prefix = tag_obj[:7]
    record("annotated tag OBJECT 7-hex prefix (its target is a commit)", prefix,
           "", lk(BASE, [repo], [prefix]), lk(CUR, [repo], [prefix]))
    record("annotated tag OBJECT 7-hex prefix (its target is a commit)", prefix,
           "^{commit}", lk(BASE, [repo], [prefix], "^{commit}"),
           lk(CUR, [repo], [prefix], "^{commit}"))


def case_alternates():
    src = newrepo("alternates_src")
    obj = mkcommit(src, "only in alternate")
    repo = newrepo("alternates_dst")
    info = repo / ".git" / "objects" / "info"
    info.mkdir(parents=True, exist_ok=True)
    (info / "alternates").write_text(str(src / ".git" / "objects") + "\n")
    record("objects/info/alternates: object only in the alternate", obj, "",
           lk(BASE, [repo], [obj]), lk(CUR, [repo], [obj]))


def build_chunks(n):
    chunks = []
    mark = 0
    for i in range(n):
        mark += 1
        body = f"blob probe {i}\n".encode()
        chunks.append((mark, "blob",
                       f"blob\nmark :{mark}\ndata {len(body)}\n".encode()
                       + body + b"\n"))
    for j in range(n):
        mark += 1
        msg = f"collision probe {j}\n".encode()
        ts = 1600000000 + j
        head = (f"reset refs/heads/x\ncommit refs/heads/x\nmark :{mark}\n"
                f"author T <t@example.invalid> {ts} +0000\n"
                f"committer T <t@example.invalid> {ts} +0000\n"
                f"data {len(msg)}\n").encode()
        chunks.append((mark, "commit", head + msg + b"\n"))
    return chunks


def import_chunks(repo, chunks):
    marks = repo / "marks.txt"
    stream = b"".join(chunk for _, _, chunk in chunks)
    proc = subprocess.run(["git", "-C", str(repo), "fast-import", "--quiet",
                           f"--export-marks={marks}"], input=stream,
                          capture_output=True, env=ENV)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.decode(errors="replace"))
    oids = {}
    for line in marks.read_text().splitlines():
        mark_text, oid = line.split(" ")
        oids[int(mark_text[1:])] = oid
    return oids


def has_digit_and_letter(text):
    return re.search("[0-9]", text) is not None and re.search("[a-f]", text) is not None


def case_collisions():
    chunks = build_chunks(N_OBJ)
    kind = {mark: k for mark, k, _ in chunks}
    chunk_of = {mark: c for mark, _, c in chunks}
    lane = newrepo("collide_lane")
    oids = import_chunks(lane, chunks)
    groups = defaultdict(lambda: {"commit": [], "blob": []})
    for mark, oid in oids.items():
        groups[oid[:7]][kind[mark]].append(mark)
    cb = next((p for p, g in groups.items() if has_digit_and_letter(p)
               and len(g["commit"]) == 1 and len(g["blob"]) == 1), None)
    cc = next((p for p, g in groups.items() if has_digit_and_letter(p)
               and len(g["commit"]) == 2 and not g["blob"]), None)
    assert cb and cc, "no collision found; raise N_OBJ"
    record("commit + blob share a 7-hex prefix (same repo)", cb, "",
           lk(BASE, [lane], [cb]), lk(CUR, [lane], [cb]))
    record("commit + blob share a 7-hex prefix (same repo)", cb, "^{commit}",
           lk(BASE, [lane], [cb], "^{commit}"), lk(CUR, [lane], [cb], "^{commit}"))
    record("two commits share a 7-hex prefix (same repo)", cc, "",
           lk(BASE, [lane], [cc]), lk(CUR, [lane], [cc]))
    record("two commits share a 7-hex prefix (same repo)", cc, "^{commit}",
           lk(BASE, [lane], [cc], "^{commit}"), lk(CUR, [lane], [cc], "^{commit}"))
    first, second = sorted(groups[cc]["commit"])
    fleet = newrepo("collide_fleet")
    fleet_oids = import_chunks(fleet, [(first, "commit", chunk_of[first])])
    assert fleet_oids[first] == oids[first]
    assert fleet_oids[first] != oids[second]
    for peel in ("", "^{commit}"):
        record("cross-repo: lane holds both commits, fleet holds only the first",
               cc, peel, lk(BASE, [lane, fleet], [cc], peel),
               lk(CUR, [lane, fleet], [cc], peel))
    for value in ("none", "blob", "tree", "commit", "committish", "tag"):
        git(lane, "config", "core.disambiguate", value)
        record(f"repo-local core.disambiguate={value}, commit + blob collision",
               cb, "bare / ^{commit}",
               f"{lk(BASE, [lane], [cb])} / {lk(BASE, [lane], [cb], '^{commit}')}",
               f"{lk(CUR, [lane], [cb])} / {lk(CUR, [lane], [cb], '^{commit}')}")
    git(lane, "config", "--unset", "core.disambiguate")


def run_case(fn):
    try:
        fn()
    except Exception as exc:
        RESULTS.append({"case": fn.__name__, "probe": "-", "peel": "-",
                        "base": "-", "cur": f"FIXTURE ERROR {type(exc).__name__}: {exc}"[:300],
                        "note": ""})


def main():
    for fn in (case_replace_fabricated, case_replace_type, case_promisor_exec,
               case_promisor_available, case_ref_shadow, case_planted_object,
               case_annotated_tag, case_alternates, case_collisions):
        run_case(fn)
    (ROOT / "results.json").write_text(json.dumps(RESULTS, indent=1))
    for r in RESULTS:
        print(f"## {r['case']}\n   probe={r['probe']} peel={r['peel']}\n"
              f"   base: {r['base']}\n   cur : {r['cur']}\n   note: {r['note']}")


if __name__ == "__main__":
    main()
