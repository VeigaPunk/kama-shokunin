#!/usr/bin/env python3
"""Reachability probe for mutant M17-ref-shadow.

Question: can any audit INPUT (report text, errata ledger, repository
state) reach the refusal at tools/report-landing-audit.py lookup()
(lines 260-280 at fa3b62a), the `if not peel and not
parts[0].startswith(token): raise EvalError(...)` site?

Three auditors are built from the pristine committed bytes:
  pristine  - unchanged
  mutant    - the registered M17 literal replaced by `pass`
  probe     - the same site instrumented to log every (token, oid, peel)
              triple it sees, so "the site was never reached" is a
              measured fact, not an argument.

Every fixture is run against all three; a verdict change between pristine
and mutant is the kill condition.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CLONE = Path("/fast/scratch/hyaku/kama-r25a2w2/MutationM17Reachability/clone")
WORK = Path("/fast/scratch/hyaku/kama-r25a2w2/MutationM17Reachability/work")
PRISTINE_PATH = CLONE / "tools/report-landing-audit.py"
REL = ".ufo/reports/round-1/kama.md"

# the registered M17 literal, taken from the instrument itself
sys.path.insert(0, str(CLONE / "tests/report-audit"))
import importlib.util as _u  # noqa: E402

_spec = _u.spec_from_file_location(
    "iso", CLONE / "tests/report-audit/isolation-mutants.py")
_iso = _u.module_from_spec(_spec)
_spec.loader.exec_module(_iso)
M17 = [m for m in _iso.MUTANTS if m[0] == "M17-ref-shadow"][0]
OLD, NEW = M17[1], M17[2]

PROBE_OLD = (
    'if not peel and not parts[0].startswith(token):\n'
    '                # git resolved a same-named ref before the object prefix\n'
    '                raise EvalError(f"{store.path}: citation {token} '
    'names a ref")')
PROBE_NEW = (
    'print(f"M17-SITE token={token} oid={parts[0]} peel={peel!r}",\n'
    '                 file=sys.stderr)\n'
    '            if not peel and not parts[0].startswith(token):\n'
    '                # git resolved a same-named ref before the object '
    'prefix\n'
    '                raise EvalError(f"{store.path}: citation {token} '
    'names a ref")')


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise RuntimeError(f"git {' '.join(map(str, args))}: "
                           f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surrogateescape").strip()


def init(path, fmt=None, ref_format=None):
    args = ["init", "-q", "-b", "master"]
    if fmt:
        args.append(f"--object-format={fmt}")
    if ref_format:
        args.append(f"--ref-format={ref_format}")
    g(path.parent, *args, str(path))
    return path


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(target, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        target.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_EMAIL="a@x",
      GIT_COMMITTER_NAME=author, GIT_AUTHOR_DATE=stamp,
      GIT_COMMITTER_DATE=stamp)
    return g(repo, "rev-parse", "HEAD")


def report(cites, extra=b""):
    lines = b"".join(b"- " + c.encode() + b"\n" for c in cites)
    return b"# kama round 1\n\n## Landed changes\n\n" + lines + extra


def publish(fleet, text, when=2000, path=REL):
    commit(fleet, "fleet", when, "round-1: report", path, text)


# --------------------------------------------------------------- auditors
def build_auditors():
    WORK.mkdir(parents=True, exist_ok=True)
    src = PRISTINE_PATH.read_text(encoding="utf-8")
    assert src.count(OLD) == 1, f"M17 literal occurs {src.count(OLD)} times"
    assert src.count(PROBE_OLD) == 1
    out = {}
    for name, old, new in (("pristine", OLD, OLD),
                           ("mutant", OLD, NEW),
                           ("probe", PROBE_OLD, PROBE_NEW)):
        path = WORK / f"report-landing-audit-{name}.py"
        path.write_text(src.replace(old, new), encoding="utf-8")
        out[name] = path
    # probe2: the same site, logging every entry to a file
    log_new = (
        'with open(os.environ.get("M17_PROBE_LOG", "/dev/null"), "a") as fh:\n'
        '                    fh.write(f"token={token} oid={parts[0]} '
        'peel={peel!r} store={store.path}\\n")\n'
        '            if not peel and not parts[0].startswith(token):\n'
        '                # git resolved a same-named ref before the object '
        'prefix\n'
        '                raise EvalError(f"{store.path}: citation {token} '
        'names a ref")')
    p2 = WORK / "report-landing-audit-probe2.py"
    p2.write_text(src.replace(PROBE_OLD, log_new), encoding="utf-8")
    out["probe2"] = p2
    return out


def run_auditor(auditor, lane, fleet, extra_argv=(), env_extra=None):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata", *extra_argv]
    p = subprocess.run(argv, capture_output=True, env=env(**(env_extra or {})),
                       cwd="/tmp")
    err = p.stderr.decode(errors="replace")
    site = [ln for ln in err.split("\n") if ln.startswith("M17-SITE")]
    tail = [ln for ln in err.split("\n") if ln.strip()][-3:]
    return {"exit": p.returncode,
            "stdout_sha256": hashlib.sha256(p.stdout).hexdigest()[:16],
            "stdout_bytes": len(p.stdout),
            "stderr_tail": tail,
            "m17_site_lines": site}


def compare(res):
    p, m = res["pristine"], res["mutant"]
    diff = (p["exit"] != m["exit"]
            or p["stdout_sha256"] != m["stdout_sha256"])
    return diff


# ---------------------------------------------------------------- fixtures
def fixture_base(tmp, lane_fmt=None, ref_format=None):
    lane = Path(tmp, "lane")
    fleet = Path(tmp, "fleet")
    init(lane, lane_fmt, ref_format)
    init(fleet)
    return lane, fleet


def attempt_a1(tmp):
    """40-hex citation; lane branch named exactly that 40-hex; the object
    does not exist anywhere."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "1" * 40
    g(lane, "branch", token)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a2(tmp):
    """40-hex citation that IS a real commit; lane branch with the same
    40-hex name pointing at a different commit."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    other = commit(lane, "kama-shokunin", 1100, "round-1: more")
    g(lane, "branch", lc, other)
    publish(fleet, report([lc]))
    return lane, fleet, {}


def attempt_a3(tmp):
    """40-hex citation; lane TAG with the same 40-hex name."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "2" * 40
    g(lane, "tag", token, lc)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a4(tmp):
    """40-hex citation; the same-named ref stored in packed-refs."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "3" * 40
    g(lane, "branch", token)
    g(lane, "pack-refs", "--all")
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a5(tmp):
    """40-hex citation; the same-named ref lives in the FLEET repo (the
    second store)."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "4" * 40
    publish(fleet, report([lc, token]))
    head = g(fleet, "rev-parse", "HEAD")
    g(fleet, "update-ref", f"refs/heads/{token}", head)
    return lane, fleet, {}


def attempt_a6(tmp):
    """F13 shape: short (8-hex) citation whose name is a TAG in the lane
    repo. This is the live site (bare_objects, mutant M33)."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    publish(fleet, report([lc, "deadbee1"]))
    g(lane, "tag", "deadbee1", lc)
    return lane, fleet, {}


def attempt_a7(tmp):
    """sha256 lane repo; 40-hex citation with a same-named tag."""
    lane, fleet = fixture_base(tmp, lane_fmt="sha256")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "5" * 40
    g(lane, "tag", token, lc)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a8(tmp):
    """errata ledger: a correction token that is a 40-hex naming a ref."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "6" * 40
    g(lane, "branch", token)
    publish(fleet, report([lc]))
    errata = Path(tmp, "errata.tsv")
    errata.write_text(
        f"1\tlanded-unresolved\tzzz\t{token}\tzzz\n", encoding="utf-8")
    return lane, fleet, {"--errata": str(errata)}


def attempt_a9(tmp):
    """40-hex citation; the same-named ref is a remote-tracking ref."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "7" * 40
    g(lane, "update-ref", f"refs/remotes/origin/{token}", lc)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a10(tmp):
    """reftable ref storage; 40-hex citation with a same-named branch."""
    lane, fleet = fixture_base(tmp, ref_format="reftable")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "8" * 40
    g(lane, "branch", token)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a11(tmp):
    """40-hex citation whose name is a ref in the lane repo AND the token
    is a real object in the fleet repo (cross-store)."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    fc = commit(fleet, "fleet", 900, "unrelated")
    g(lane, "branch", fc)
    publish(fleet, report([lc, fc]))
    return lane, fleet, {}


def attempt_a12(tmp):
    """Uppercase 40-hex citation with a same-named lower-case ref
    (git resolves hex case-insensitively; the auditor's FULL regex is
    lower-case only, so this is the closest legal spelling)."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "9" * 40
    g(lane, "branch", token)
    publish(fleet, report([lc, token.upper()]))
    return lane, fleet, {}


def attempt_a13(tmp):
    """BARE lane repo (clone --bare) with a 40-hex-named branch."""
    src = Path(tmp, "src")
    lane = Path(tmp, "lane")
    fleet = Path(tmp, "fleet")
    init(src)
    init(fleet)
    lc = commit(src, "kama-shokunin", 1000, "round-1: work")
    g(Path(tmp), "clone", "-q", "--bare", str(src), str(lane))
    token = "a" * 40
    g(lane, "branch", token)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


def attempt_a14(tmp):
    """40-hex-named branch in a lane repo with
    core.warnAmbiguousRefs=false (does the config change resolution?)."""
    lane, fleet = fixture_base(tmp)
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    token = "b" * 40
    g(lane, "config", "core.warnAmbiguousRefs", "false")
    g(lane, "branch", token)
    publish(fleet, report([lc, token]))
    return lane, fleet, {}


ATTEMPTS = [
    ("A1", "40-hex citation, same-named lane branch (object absent)",
     attempt_a1),
    ("A2", "40-hex citation of a real commit, same-named lane branch to "
     "another commit", attempt_a2),
    ("A3", "40-hex citation, same-named lane tag", attempt_a3),
    ("A4", "40-hex citation, same-named lane branch in packed-refs",
     attempt_a4),
    ("A5", "40-hex citation, same-named ref only in the fleet store",
     attempt_a5),
    ("A6", "8-hex citation with a same-named lane tag (F13 shape)",
     attempt_a6),
    ("A7", "sha256 lane repo, 40-hex citation with a same-named tag",
     attempt_a7),
    ("A8", "errata ledger correction that is a 40-hex naming a ref",
     attempt_a8),
    ("A9", "40-hex citation, same-named remote-tracking ref", attempt_a9),
    ("A10", "reftable ref storage, 40-hex citation, same-named branch",
     attempt_a10),
    ("A11", "40-hex citation of a fleet object, same-named lane branch",
     attempt_a11),
    ("A12", "uppercase 40-hex citation, same-named lower-case branch",
     attempt_a12),
    ("A13", "bare lane repo, 40-hex citation, same-named branch",
     attempt_a13),
    ("A14", "40-hex citation, same-named branch, "
     "core.warnAmbiguousRefs=false", attempt_a14),
]


def main():
    auditors = build_auditors()
    rows = []
    for name, desc, build in ATTEMPTS:
        with tempfile.TemporaryDirectory(prefix="m17-") as tmp:
            lane, fleet, extra = build(tmp)
            res = {k: run_auditor(v, lane, fleet,
                                  [x for pair in extra.items() for x in pair])
                   for k, v in auditors.items() if k != "probe2"}
            log = Path(tmp, "site.log")
            res["probe2"] = run_auditor(
                auditors["probe2"], lane, fleet,
                [x for pair in extra.items() for x in pair],
                env_extra={"M17_PROBE_LOG": str(log)})
            entries = [ln for ln in
                       (log.read_text().split("\n") if log.exists() else [])
                       if ln.strip()]
        row = {"attempt": name, "description": desc,
               "pristine": res["pristine"], "mutant": res["mutant"],
               "probe_site_lines": res["probe"]["m17_site_lines"],
               "probe_exit": res["probe"]["exit"],
               "probe_stderr_tail": res["probe"]["stderr_tail"],
               "probe2_site_entries": entries,
               "verdict_changed": compare(res)}
        rows.append(row)
        print(json.dumps(row, sort_keys=True))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if out:
        out.write_text(json.dumps(rows, indent=1, sort_keys=True),
                       encoding="utf-8")
    killed = [r["attempt"] for r in rows if r["verdict_changed"]]
    reached = [r["attempt"] for r in rows if r["probe_site_lines"]]
    print(f"\nattempts={len(rows)} verdict_changed={killed} "
          f"probe_site_reached={reached}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
