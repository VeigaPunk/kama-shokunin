#!/usr/bin/env python3
"""Fault probe: repo-local config and record-parsing channels for
round_commits() and report_cutoff() in tools/report-landing-audit.py.

Usage: harness.py SNAP_PATH   (cwd: the scratch clone; BASE = probe/base-4fe9339f.py)
Fixtures: fresh repos under probe/fx (under /tmp); GIT_* scrubbed and
GIT_CONFIG_GLOBAL=/dev/null, GIT_CONFIG_NOSYSTEM=1 for every git call.
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
FX = HERE / "fx"
VERS = {"base": HERE / "base-4fe9339f.py", "snap": Path(sys.argv[1]).resolve()}
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
REL = ".ufo/reports/round-23/kama.md"
FAKE = "1234567890abcdef1234567890abcdef12345678"
GPGSIG = (b"gpgsig -----BEGIN PGP SIGNATURE-----\n \n iQEzBAABCAAdFiEEfake\n"
          b" -----END PGP SIGNATURE-----\n")
UTF16_SUBJ = "round-23: second work\n".encode("utf-16-le")


def sh(args, input=None):
    p = subprocess.run(args, env=ENV, input=input, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"{args!r} rc={p.returncode}: "
                           f"{p.stderr.decode(errors='replace')}")
    return p.stdout


def git(repo, *args):
    return sh(["git", "-C", str(repo), *args]).decode("utf-8", "replace").strip()


def hash_obj(repo, data, commit=False):
    args = ["git", "-C", str(repo), "hash-object", "-w", "--stdin"]
    if commit:
        args += ["--literally", "-t", "commit"]
    return sh(args, input=data).decode().strip()


def make_tree(repo, files):
    idx = Path(repo, ".git", "fx-index")
    idx.unlink(missing_ok=True)
    env = dict(ENV, GIT_INDEX_FILE=str(idx))
    for path, data in files.items():
        blob = hash_obj(repo, data)
        p = subprocess.run(["git", "-C", str(repo), "update-index", "--add",
                            "--cacheinfo", f"100644,{blob},{path}"],
                           env=env, capture_output=True)
        if p.returncode:
            raise RuntimeError(p.stderr.decode())
    p = subprocess.run(["git", "-C", str(repo), "write-tree"], env=env,
                       capture_output=True)
    if p.returncode:
        raise RuntimeError(p.stderr.decode())
    idx.unlink(missing_ok=True)
    return p.stdout.decode().strip()


def mk_commit(repo, tree, parents, name, when, msg, extra=b""):
    """Raw commit object (hash-object --literally: no fsck), so header and
    message bytes are exactly as written."""
    ident = b" <x@example.invalid> " + str(when).encode() + b" +0000\n"
    hdr = b"tree " + tree.encode() + b"\n"
    for p in parents:
        hdr += b"parent " + p.encode() + b"\n"
    hdr += b"author " + name + ident + b"committer " + name + ident + extra
    return hash_obj(repo, hdr + b"\n" + msg, commit=True)


def new_repo(path):
    path.mkdir(parents=True, exist_ok=True)
    sh(["git", "init", "-q", "-b", "master", str(path)])
    return path


def build_chain(repo, specs):
    parents, shas = [], {}
    for s in specs:
        tree = make_tree(repo, s.get("files") or {"f": s["key"].encode()})
        sha = mk_commit(repo, tree, parents, s["name"], s["when"], s["msg"],
                        s.get("extra", b""))
        shas[s["key"]] = sha
        parents = [sha]
    git(repo, "update-ref", "refs/heads/master", parents[0])
    return shas


def lane_specs(L1msg=b"round-23: first work\n", L2name=b"kama-shokunin",
               L2msg=b"round-23: second work\n", L2extra=b"",
               L2when=1700000100, L3msg=b"docs: unrelated\n",
               extra_files=None):
    ef = dict(extra_files or {})
    return [
        {"key": "L1", "name": b"kama-shokunin", "when": 1700000000,
         "msg": L1msg, "files": {"f": b"1", **ef}},
        {"key": "L2", "name": L2name, "when": L2when, "msg": L2msg,
         "extra": L2extra, "files": {"f": b"2", **ef}},
        {"key": "L3", "name": b"other-dev", "when": 1700000150,
         "msg": L3msg, "files": {"f": b"3", **ef}},
    ]


def rep(cites, shas):
    body = "# Round 23 kama report\n\n## Landed changes\n"
    body += "".join(f"- {shas[c][:12]} landed\n" for c in cites)
    return (body + "\n").encode()


def fleet_build(F, kind, R, when):
    if kind == "single":
        build_chain(F, [{"key": "F1", "name": b"fleet-dev", "when": when,
                         "msg": b"round-23 report\n", "files": {REL: R}}])
    elif kind == "root-only":
        build_chain(F, [{"key": "F0", "name": b"fleet-dev", "when": 1700000050,
                         "msg": b"root\n", "files": {REL: R}}])
    elif kind == "draft-rename":
        build_chain(F, [
            {"key": "F0", "name": b"fleet-dev", "when": 1700000050,
             "msg": b"draft\n", "files": {".ufo/reports/round-23/draft.md": R}},
            {"key": "F1", "name": b"fleet-dev", "when": 1700000200,
             "msg": b"rename draft to kama.md\n", "files": {REL: R}},
        ])
    elif kind == "copy":
        build_chain(F, [
            {"key": "F0", "name": b"fleet-dev", "when": 1700000010,
             "msg": b"seed\n", "files": {"other.md": R}},
            {"key": "F1", "name": b"fleet-dev", "when": 1700000200,
             "msg": b"copy\n", "files": {"other.md": R, REL: R}},
        ])
    elif kind == "merge":
        t0 = make_tree(F, {"other.md": b"x"})
        c0 = mk_commit(F, t0, [], b"fleet-dev", 1700000010, b"root\n")
        t1 = make_tree(F, {"other.md": b"x", "other2.md": b"y"})
        c1 = mk_commit(F, t1, [c0], b"fleet-dev", 1700000020, b"side\n")
        t2 = make_tree(F, {"other.md": b"x", "other2.md": b"y", REL: R})
        c2 = mk_commit(F, t2, [c0, c1], b"fleet-dev", 1700000200,
                       b"merge that adds the report\n")
        git(F, "update-ref", "refs/heads/master", c2)
    else:
        raise ValueError(kind)


def post_grafts(L, shas):
    Path(L, ".git", "info").mkdir(parents=True, exist_ok=True)
    Path(L, ".git", "info", "grafts").write_text(shas["L2"] + "\n")


def post_shallow(L, shas):
    Path(L, ".git", "shallow").write_text(shas["L2"] + "\n")


def post_replace(L, shas):
    tree = git(L, "rev-parse", f"{shas['L1']}^{{tree}}")
    repl = mk_commit(L, tree, [], b"chore-bot", 1700000000,
                     b"chore: replaced\n")
    git(L, "update-ref", f"refs/replace/{shas['L1']}", repl)


def post_tag(L, shas):
    git(L, "tag", "master", shas["L1"])


def build_case(name, cites=("L1", "L2"), fleet="single", fleet_when=1700000200,
               lane_cfg=(), fleet_cfg=(), post=None, **lane_kw):
    d = FX / name
    d.mkdir(parents=True, exist_ok=True)
    L, F = new_repo(d / "lane"), new_repo(d / "fleet")
    shas = build_chain(L, lane_specs(**lane_kw))
    fleet_build(F, fleet, rep(cites, shas), fleet_when)
    for k, v in lane_cfg:
        git(L, "config", k, v)
    for k, v in fleet_cfg:
        git(F, "config", k, v)
    if post:
        post(L, shas)
    return L, F, shas


def cli(version, L, F):
    p = subprocess.run([sys.executable, str(VERS[version]), "--lane-repo",
                        str(L), "--fleet-repo", str(F), "--rounds", "23",
                        "--no-errata"], env=ENV, capture_output=True)
    out = p.stdout.decode(errors="replace").splitlines()
    err = p.stderr.decode(errors="replace").strip().splitlines()
    status = next((x.rsplit("status=", 1)[1] for x in reversed(out)
                   if x.startswith("summary ")), "-")
    defects = [x.strip() for x in out if x.startswith("  ")]
    tail = err[-1][:90] if err else ""
    return f"rc={p.returncode} status={status} defects={defects} err={tail!r}"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = {"base": load(VERS["base"], "base_audit"),
       "snap": load(VERS["snap"], "snap_audit")}


def rows(version, L, shas):
    branch = ("master" if version == "base"
              else git(L, "rev-parse", "refs/heads/master^{commit}"))
    names = {v: k for k, v in shas.items()}
    try:
        got = MOD[version].round_commits(L, branch, "kama", 23)
        return [(names.get(r["sha"], r["sha"][:8]), r["atime"]) for r in got]
    except Exception as exc:  # observed exception class, not a verdict
        return f"{type(exc).__name__}: {str(exc)[:60]}"


def cutoff(version, F):
    try:
        return MOD[version].report_cutoff(F, REL)
    except Exception as exc:
        return f"{type(exc).__name__}: {str(exc)[:60]}"


def script(d, fname, ran):
    p = d / fname
    p.write_text(f"#!/bin/sh\necho ran >> '{ran}'\nexit 1\n")
    p.chmod(0o755)
    return str(p)


def pre(name):
    d = FX / name
    d.mkdir(parents=True, exist_ok=True)
    return d


d5 = pre("S5-showSignature-exec")
g5 = script(d5, "gpg-marker.sh", d5 / "gpg-ran.txt")
d18 = pre("S18-fsmonitor-exec")
f18 = script(d18, "fsmon-marker.sh", d18 / "fsmon-ran.txt")
d19 = pre("S19-trace2-side-effect")
t19 = d19 / "trace2-event.json"
L1_UTF8_ACCENT = "round-23: caf\u00e9\n".encode()

CASES = [
    dict(name="S0-control-clean", kw={}, expect="0/0"),
    dict(name="S1-control-omit", kw=dict(cites=("L2",)), expect="1/1"),
    dict(name="S2-i18n-logOutputEncoding",
         kw=dict(L1msg=L1_UTF8_ACCENT,
                 lane_cfg=[("i18n.logOutputEncoding", "ISO-8859-1")]),
         expect="0 (base: traceback, L1 probe (a))"),
    dict(name="S3-log.follow-fleet",
         kw=dict(cites=("L1",), fleet="draft-rename",
                 fleet_cfg=[("log.follow", "true")]),
         expect="1 (L2 omitted); base-with-follow expected 0"),
    dict(name="S4-log.mailmap-lane",
         kw=dict(extra_files={".mailmap": b"renamed-person <x@example.invalid>"
                                          b" kama-shokunin <x@example.invalid>\n"},
                 lane_cfg=[("log.mailmap", "true")]),
         expect="0/0 (%an is raw; mailmap should not matter)"),
    dict(name="S5-showSignature-exec",
         kw=dict(L2extra=GPGSIG,
                 lane_cfg=[("log.showSignature", "true"), ("gpg.program", g5)]),
         expect="0 snap; base expected to run marker", markers=[d5 / "gpg-ran.txt"]),
    dict(name="S6-grafts-hide", kw=dict(cites=("L2",), post=post_grafts),
         expect="2 snap (refuse); base expected 0 (false)"),
    dict(name="S7-shallow-hide", kw=dict(cites=("L2",), post=post_shallow),
         expect="2 snap (refuse); base expected 0 (false)"),
    dict(name="S8-replace-omitted", kw=dict(cites=("L2",), post=post_replace),
         expect="1 (L1 omitted); base expected 0 (false)"),
    dict(name="S9-tag-shadows-branch", kw=dict(cites=("L1",), post=post_tag),
         expect="1 (L2 omitted); base expected 0 (false)"),
    dict(name="S10-author-field-injected-atime",
         kw=dict(cites=("L1",),
                 L2name=b"kama-shokunin\x1f4000000000\x1fround-23: x"),
         expect="1 (L2 omitted); both expected 0 (residual)"),
    dict(name="S11-subject-END-fake-record",
         kw=dict(L3msg=b"docs: unrelated\x1e" + FAKE.encode()
                 + b"\x1fkama-shokunin\x1f1700000000\x1fround-23: fake\n"),
         expect="0 (both cited); both expected 1 (false fail)"),
    dict(name="S12-5000-digit-atime",
         kw=dict(cites=("L1",),
                 L2name=b"kama-shokunin\x1f" + b"9" * 5000 + b"\x1fround-23: x"),
         expect="2 (refuse); both expected traceback exit 1"),
    dict(name="S13-utf16-subject-no-header",
         kw=dict(cites=("L1",), L2msg=UTF16_SUBJ),
         expect="1 (L2 omitted); both expected 0 (false)"),
    dict(name="S13b-utf16-unknown-encoding",
         kw=dict(cites=("L1",), L2msg=UTF16_SUBJ,
                 L2extra=b"encoding x-no-such-enc\n"),
         expect="1 (L2 omitted); both expected 0 (false)"),
    dict(name="S13c-utf16-known-encoding",
         kw=dict(cites=("L1",), L2msg=UTF16_SUBJ,
                 L2extra=b"encoding UTF-16LE\n"),
         expect="1 (control: git re-encodes)"),
    dict(name="S14-invalid-utf8-unrelated-subject",
         kw=dict(L3msg=b"docs: \xff\xfe bad\n"),
         expect="0 (both cited); base expected 2 refusal"),
    dict(name="S15-fleet-log.showRoot-false",
         kw=dict(cites=("L1",), fleet="root-only",
                 fleet_cfg=[("log.showRoot", "false")]),
         expect="0 (L1 only; L2 post-report); base expected 2"),
    dict(name="S16a-merge-adds-report-default", kw=dict(fleet="merge"),
         expect="2 (no merge diffs by default)"),
    dict(name="S16b-merge-adds-report-diffMerges",
         kw=dict(fleet="merge", fleet_cfg=[("log.diffMerges", "separate")]),
         expect="0 (config-dependent verdict; not in GIT_ISOLATION)"),
    dict(name="S17-copy-diff.renames-copies", kw=dict(fleet="copy",
         fleet_cfg=[("diff.renames", "copies")]),
         expect="0 (control)"),
    dict(name="S18-core.fsmonitor-exec",
         kw=dict(lane_cfg=[("core.fsmonitor", f18)]),
         expect="0; marker expected absent", markers=[d18 / "fsmon-ran.txt"]),
    dict(name="S19-trace2-eventTarget-side-effect",
         kw=dict(fleet_cfg=[("trace2.eventTarget", str(t19))]),
         expect="0; trace file side effect only", markers=[t19]),
    dict(name="S20-future-dated-author", kw=dict(cites=("L1",), L2when=4000000000),
         expect="0 (L2 treated post-report; design hole)"),
]


def main():
    lines = []
    for case in CASES:
        name = case["name"]
        L, F, shas = build_case(name, **case["kw"])
        markers = case.get("markers", [])
        res = {}
        for v in ("base", "snap"):
            for m in markers:
                m.unlink(missing_ok=True)
            res[v] = cli(v, L, F)
            if markers:
                res[v] += f" markers={[m.name for m in markers if m.exists()]}"
        lines.append(f"## {name}")
        lines.append(f"  expect: {case['expect']}")
        lines.append(f"  base: {res['base']}")
        lines.append(f"  snap: {res['snap']}")
        lines.append(f"  base rows: {rows('base', L, shas)}")
        lines.append(f"  snap rows: {rows('snap', L, shas)}")
        lines.append(f"  base cutoff: {cutoff('base', F)}  "
                     f"snap cutoff: {cutoff('snap', F)}")
    text = "\n".join(lines)
    (HERE / "results.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
