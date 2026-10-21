#!/usr/bin/env python3
"""Probe of a fail-closed round_commits candidate and two extra fixtures.

Usage: proto.py SNAP_PATH   (same argument as harness.py)
Reuses fixtures and CLI runner from harness.py; nothing here touches the lane.
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import harness as H  # noqa: E402  (module-level setup only; main() not run)

S = H.MOD["snap"]
ISO = S.GIT_ISOLATION
CASES = {c["name"]: c for c in H.CASES}


def fail(msg):
    return S.EvalError(msg)


def git_bytes(repo, args, stdin=None):
    p = subprocess.run(["git", *ISO, "-C", str(repo), *args], env=S.git_env(),
                       input=stdin, capture_output=True)
    if p.returncode:
        raise fail(f"git {args[0]} rc={p.returncode}")
    return p.stdout


def raw_commits_ok(repo, shas):
    """Every reachable commit object: no NUL byte (fsck nulInCommit) and an
    encoding header, if any, that names UTF-8."""
    data = git_bytes(repo, ["cat-file", "--batch"],
                     stdin=("\n".join(shas) + "\n").encode())
    pos = 0
    for _ in shas:
        nl = data.index(b"\n", pos)
        head = data[pos:nl].split(b" ")
        if len(head) != 3 or head[1] != b"commit":
            raise fail(f"unexpected object header {head!r}")
        size = int(head[2])
        body = data[nl + 1:nl + 1 + size]
        pos = nl + 2 + size
        if b"\x00" in body:
            raise fail(f"NUL byte in commit {head[0].decode()}")
        headers = body.split(b"\n\n", 1)[0]
        enc = re.search(rb"^encoding (.*)$", headers, re.M)
        if enc and enc.group(1).strip().lower() not in (b"utf-8", b"utf8"):
            raise fail(f"non-UTF-8 encoding in {head[0].decode()}")


def round_commits_candidate(lane_repo, branch, lane, rnd):
    shas = git_bytes(lane_repo, ["rev-list", branch]).decode().split()
    raw_commits_ok(lane_repo, shas)
    out = git_bytes(lane_repo, ["log", "-z", "--format=%H%x00%an%x00%at%x00%s",
                                branch]).decode("utf-8", "surrogateescape")
    parts = out.split("\x00")
    if parts and parts[-1] == "":
        parts.pop()
    if len(parts) % 4:
        raise fail("record arity")
    pat = re.compile(rf"^(?:round-{rnd}:|checkpoint\(r{rnd}\))")
    rows = []
    for i in range(0, len(parts), 4):
        sha, author, atime, subject = parts[i:i + 4]
        if not re.fullmatch(r"[0-9a-f]{40}", sha) or not re.fullmatch(
                r"[0-9]{1,18}", atime):
            raise fail(f"malformed record {sha[:20]!r}")
        if re.search(r"[\x00-\x08\x0a-\x1f\x7f]", author + subject):
            raise fail(f"control byte in record {sha}")
        if author == f"{lane}-shokunin" and pat.match(subject):
            rows.append({"sha": sha, "atime": int(atime)})
    return rows


def show(label, fn):
    try:
        return fn()
    except Exception as exc:  # observed class only
        return f"{type(exc).__name__}: {str(exc)[:70]}"


def candidate_rows(L, shas):
    names = {v: k for k, v in shas.items()}
    head = H.git(L, "rev-parse", "refs/heads/master^{commit}")
    got = round_commits_candidate(L, head, "kama", 23)
    return [(names.get(r["sha"], r["sha"][:8]), r["atime"]) for r in got]


def main():
    names = ["S0-control-clean", "S1-control-omit", "S10-author-field-injected-atime",
             "S11-subject-END-fake-record", "S12-5000-digit-atime",
             "S13-utf16-subject-no-header", "S13b-utf16-unknown-encoding",
             "S13c-utf16-known-encoding", "S14-invalid-utf8-unrelated-subject",
             "S20-future-dated-author"]
    lines = []
    for name in names:
        L, F, shas = H.build_case("P-" + name, **CASES[name]["kw"])
        lines.append(f"## candidate {name}")
        lines.append(f"  rows: {show('rows', lambda: candidate_rows(L, shas))}")
        lines.append(f"  snap-cli: {H.cli('snap', L, F)}")
    # fleet-side replace of the add commit: base honors refs/replace on the
    # fleet walk; snap pins --no-replace-objects.
    L, F, shas = H.build_case("P-S21-fleet-replace-add", cites=("L1",))
    f1 = H.git(F, "rev-parse", "master")
    tree = H.git(F, "rev-parse", "master^{tree}")
    repl = H.mk_commit(F, tree, [], b"fleet-dev", 1700000010, b"round-23 report\n")
    H.git(F, "update-ref", f"refs/replace/{f1}", repl)
    lines.append("## S21-fleet-replace-add (cites L1 only; correct verdict 1)")
    lines.append(f"  base: {H.cli('base', L, F)}")
    lines.append(f"  snap: {H.cli('snap', L, F)}")
    lines.append(f"  base cutoff: {H.cutoff('base', F)}  snap cutoff: {H.cutoff('snap', F)}")
    text = "\n".join(lines)
    (HERE / "proto-results.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
