#!/usr/bin/env python3
"""Audit-level replay (main() exit codes) of the lookup() findings.

Base (4fe9339f) and the current lane snapshot run against the same fresh temp
lane and fleets under /tmp/kama-r23/RevLookup/e2e. No lane or fleet repository
of the real checkout is read or written.
"""
import contextlib
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import zlib
from collections import defaultdict
from pathlib import Path

WORK = Path("/tmp/kama-r23/RevLookup")
ROOT = WORK / "e2e"
FAKE40 = "e4f1c2a9b7d30816f5e2a4b9c0d1e2f3a4b5c6d7"  # planted loose object
FAKE_C = "0123456789abcdef0123456789abcdef01234567"  # absent everywhere
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


def build_chunks(n):
    chunks = []
    mark = 0
    for i in range(n):
        mark += 1
        body = f"blob probe {i}\n".encode()
        chunks.append((mark, "blob",
                       f"blob\nmark :{mark}\ndata {len(body)}\n".encode() + body + b"\n"))
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
    marks = ROOT / f"marks-{repo.name}.txt"  # outside the worktree
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


def write_report(fleet, rnd, body):
    path = fleet / ".ufo" / "reports" / f"round-{rnd}" / "kama.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def commit_all(repo, msg):
    git(repo, "add", "-A")
    git(repo, "-c", "user.name=k", "-c", "user.email=k@example.invalid",
        "commit", "-q", "-m", msg)


def audit(mod, lane, fleet, rnd, errata=None):
    argv = ["--lane-repo", str(lane), "--fleet-repo", str(fleet), "--branch", "main",
            "--rounds", str(rnd), "--json"]
    argv += ["--errata", str(errata)] if errata else ["--no-errata"]
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = mod.main(argv)
    cell = {"rc": rc, "stderr": err.getvalue().strip()[:160]}
    if out.getvalue().strip():
        try:
            doc = json.loads(out.getvalue())
            cell["defects"] = sorted(f"{d['kind']}:{d['token']}"
                                     for r in doc["results"] for d in r["defects"])
        except (ValueError, KeyError) as exc:
            cell["defects"] = f"unparsed: {exc}; head={out.getvalue()[:120]!r}"
    return cell


def main():
    chunks = build_chunks(N_OBJ)
    kind = {mark: k for mark, k, _ in chunks}
    chunk_of = {mark: c for mark, _, c in chunks}
    lane = newrepo("lane")
    oids = import_chunks(lane, chunks)
    groups = defaultdict(lambda: {"commit": [], "blob": []})
    for mark, oid in oids.items():
        groups[oid[:7]][kind[mark]].append(mark)
    cb = next(p for p, g in groups.items() if has_digit_and_letter(p)
              and len(g["commit"]) == 1 and len(g["blob"]) == 1)
    cc = next(p for p, g in groups.items() if has_digit_and_letter(p)
              and len(g["commit"]) == 2 and not g["blob"])
    first, second = sorted(groups[cc]["commit"])
    any_commit = min(m for m, k, _ in chunks if k == "commit")
    git(lane, "update-ref", "refs/heads/main", oids[any_commit])
    planted = lane / ".git" / "objects" / FAKE40[:2]
    planted.mkdir(parents=True, exist_ok=True)
    (planted / FAKE40[2:]).write_bytes(zlib.compress(b"blob 3\x00abc"))

    fleet = newrepo("fleet_with_first")
    import_chunks(fleet, [(first, "commit", chunk_of[first])])
    write_report(fleet, 1, f"# Round 1\n## Work performed\nnone\n"
                           f"## Landed changes\n- {cb} round-1 work\n")
    write_report(fleet, 2, f"# Round 2\n## Work performed\nsee {FAKE40}\n"
                           f"## Landed changes\nnone\n")
    write_report(fleet, 3, f"# Round 3\n## Work performed\nsee {FAKE_C}\n"
                           f"## Landed changes\nnone\n")
    write_report(fleet, 4, f"# Round 4\n## Work performed\nnone\n"
                           f"## Landed changes\n- {cc} cross-repo probe\n")
    commit_all(fleet, "reports")

    fleet2 = newrepo("fleet_without_first")
    write_report(fleet2, 4, f"# Round 4\n## Work performed\nnone\n"
                            f"## Landed changes\n- {cc} cross-repo probe\n")
    commit_all(fleet2, "reports")

    errata = ROOT / "errata_head.tsv"
    errata.write_text(f"3\tunresolved-full-hash\t{FAKE_C}\tHEAD\tcontrol\n",
                      encoding="utf-8")
    errata_short = ROOT / "errata_short.tsv"
    errata_short.write_text(f"3\tunresolved-full-hash\t{FAKE_C}\t{cb}\tcontrol\n",
                            encoding="utf-8")

    cells = [
        ("R1 commit+blob share 7-hex; cited in Landed (lane only)", 1, lane, fleet, None),
        ("R2 40-hex cited in body; loose object planted in lane", 2, lane, fleet, None),
        ("R3 40-hex cited in body; absent everywhere (control)", 3, lane, fleet, None),
        ("R3 + errata correction=HEAD (symbolic, not a commit hash)", 3, lane, fleet, errata),
        ("R3 + errata correction=commit+blob 7-hex (ambiguous, not a commit)", 3, lane, fleet, errata_short),
        ("R4 commit+commit 7-hex; lane holds both, fleet holds the first", 4, lane, fleet, None),
        ("R4 control: same report, fleet lacks the first commit", 4, lane, fleet2, None),
    ]
    rows = []
    for name, rnd, lane_repo, fleet_repo, err in cells:
        rows.append({"case": name,
                     "base": audit(BASE, lane_repo, fleet_repo, rnd, err),
                     "cur": audit(CUR, lane_repo, fleet_repo, rnd, err)})
    (ROOT / "results.json").write_text(json.dumps(rows, indent=1))
    for r in rows:
        print(f"## {r['case']}")
        print(f"   base: rc={r['base']['rc']} defects={r['base'].get('defects')} "
              f"stderr={r['base']['stderr']!r}")
        print(f"   cur : rc={r['cur']['rc']} defects={r['cur'].get('defects')} "
              f"stderr={r['cur']['stderr']!r}")
    print(f"cb={cb} cc={cc} first={first} second={second} planted={FAKE40}")


if __name__ == "__main__":
    main()
