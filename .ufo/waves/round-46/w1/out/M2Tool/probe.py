#!/usr/bin/env python3
"""Demonstrate pristine-vs-mutant divergence for each surviving mutant (M2Tool C2)."""
import json
import os
import subprocess
import sys
import tempfile

S = "/fast/scratch/hyaku/kama-r46/M2Tool"
PRISTINE = os.path.join(S, "pristine.py")
IDENT = ["-c", "user.name=aoa-probe", "-c", "user.email=aoa-probe@invalid", "-c", "commit.gpgsign=false"]


def git(d, *args, env_extra=None, inp=None):
    e = dict(os.environ)
    if env_extra:
        e.update(env_extra)
    p = subprocess.run(["git", "-C", d, *args], capture_output=True, text=True, env=e, input=inp)
    assert p.returncode == 0, f"git {args}: {p.stderr}"
    return p.stdout.strip()


def repo(root):
    d = tempfile.mkdtemp(prefix="probe-", dir=root)
    git(d, "init", "-q")
    assert os.path.realpath(git(d, "rev-parse", "--show-toplevel")) == os.path.realpath(d)
    return d


def commit(d, files, date=None, msg="c"):
    for name, body in files.items():
        path = os.path.join(d, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            fh.write("".join(x + "\n" for x in body))
    env = {"GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date} if date else None
    git(d, "add", "-A")
    git(d, *IDENT, "commit", "-q", "-m", msg, env_extra=env)
    return git(d, "rev-parse", "HEAD")


def lines(tag, n, salt=""):
    return [f"{tag} {salt} line {i} {os.urandom(6).hex()}" for i in range(n)]


def run_tool(mut, args):
    p = subprocess.run([sys.executable, mut, *args], capture_output=True, text=True,
                       env=dict(os.environ, TMPDIR=os.path.join(S, "probe")))
    return p.returncode, p.stdout, p.stderr


def brief(rc, out, err):
    try:
        j = json.loads(out)
        ev = [(e["commit"][:6], e["file"], e["deleted"], e["restored_at_tip"], e["status"],
               (e["restored_by"] or "-")[:6]) for e in j["events"]]
        return f"rc={rc} events={ev} summary={j.get('summary')} err={err.strip()[:60]!r}"
    except Exception:
        return f"rc={rc} out={out.strip()[:120]!r} err={err.strip()[:120]!r}"


def case(fn):
    root = tempfile.mkdtemp(prefix="proberoot-", dir=os.path.join(S, "probe"))
    d = repo(root)
    sha = fn(d)
    return sha


# ---------------------------------------------------------------- fixtures
def fx_cli20(d):
    a = lines("a", 40)
    commit(d, {"LOG.md": a}, msg="c1")
    return commit(d, {"LOG.md": a[:20]}, msg="c2-20del")


def fx_thresh0(d):
    a = lines("a", 40)
    commit(d, {"LOG.md": a}, msg="c1")
    return commit(d, {"LOG.md": a[:20]}, msg="c2")


def fx_merge_add(d):
    a = lines("a", 40) + lines("x", 0)
    extra = lines("extra", 30)
    commit(d, {"LOG.md": a}, msg="c1-base")
    base = git(d, "rev-parse", "HEAD")
    git(d, "checkout", "-q", "-b", "side")
    commit(d, {"LOG.md": a + extra}, msg="cs-side-add-only")
    git(d, "checkout", "-q", "-")
    commit(d, {"LOG.md": a + ["main tail"]}, msg="cm-main")
    git(d, *IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
    return git(d, "rev-parse", "HEAD")


def fx_dup_selfrestore(d):
    uniq = lines("u", 40)
    dup = uniq[:20]
    commit(d, {"LOG.md": uniq + dup}, msg="c1-60lines")
    c2 = commit(d, {"LOG.md": uniq}, msg="c2-del-dup-block")
    commit(d, {"LOG.md": uniq + ["tail"]}, msg="c3-next")
    return c2


def fx_unrestored(d):
    a = lines("a", 40)
    commit(d, {"LOG.md": a}, msg="c1")
    return commit(d, {"LOG.md": a[:10]}, msg="c2-30del-unrestored")


def fx_rename_real(d):
    # LOG.md (50 lines) is deleted while SCORECARD.md (previously ABSENT) appears
    # with exactly that content -> pure rename R100, target is a declared file.
    a = lines("a", 50)
    commit(d, {"LOG.md": a}, msg="c1")
    os.remove(os.path.join(d, "LOG.md"))
    with open(os.path.join(d, "SCORECARD.md"), "w") as fh:
        fh.write("".join(x + "\n" for x in a))
    git(d, "add", "-A")
    git(d, *IDENT, "commit", "-q", "-m", "c2-rename-log-into-new-scorecard")
    print("    name-status full:", git(d, "diff", "--name-status", "HEAD~1", "HEAD"))
    print("    name-status 5-file pathspec:",
          git(d, "diff", "--name-status", "HEAD~1", "HEAD", "--",
              "SCORECARD.md", "LOG.md", "corpus/QUALITY.md", "corpus/README.md", "corpus/SOURCES.md"))
    print("    -M -U0 single-path LOG.md:",
          repr(git(d, "diff", "-M", "--no-color", "-U0", "HEAD~1", "HEAD", "--", "LOG.md"))[:200])
    return git(d, "rev-parse", "HEAD")


def fx_merge_conflict(d):
    # merge tree differs from BOTH parents: prefilter fires, first-parent -U0 has
    # 5 deletions, second parent adds 15 more -> union crosses the threshold.
    base = lines("b", 40)
    extra = lines("e", 15)
    commit(d, {"LOG.md": base}, msg="c0-base")
    git(d, "checkout", "-q", "-b", "side")
    commit(d, {"LOG.md": base[:30]}, msg="side-10del")
    git(d, "checkout", "-q", "-")
    commit(d, {"LOG.md": base[:10] + extra}, msg="main-30del-plus-extra")
    git(d, "checkout", "-q", "side")
    p = subprocess.run(["git", "-C", d, *IDENT, "merge", "--no-edit", "-"], capture_output=True, text=True)
    assert p.returncode != 0, "expected a merge conflict"
    with open(os.path.join(d, "LOG.md"), "w") as fh:
        fh.write("".join(x + "\n" for x in base[:25]))
    git(d, "add", "LOG.md")
    git(d, *IDENT, "commit", "-q", "-m", "merge-resolved-25")
    return git(d, "rev-parse", "HEAD")


def fx_topo_date(d):
    a = lines("a", 40)
    commit(d, {"LOG.md": a}, msg="c0-base")
    # main: E deletes 20 (date T5); R restores (child of E, bogus EARLY date T1)
    e = commit(d, {"LOG.md": a[:20]}, date="2026-01-05T00:00:00", msg="E-delete20")
    git(d, "checkout", "-q", "-b", "side", e)
    cs = commit(d, {"LOG.md": a + ["side extra"]}, date="2026-01-03T00:00:00", msg="cs-side-holds")
    git(d, "checkout", "-q", "-")
    r = commit(d, {"LOG.md": a + ["restored"]}, date="2026-01-01T00:00:00", msg="R-restore")
    git(d, *IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
    m = git(d, "rev-parse", "HEAD")
    print(f"    fixture: E={e[:6]} R={r[:6]} cs={cs[:6]} M={m[:6]} "
          f"topo={' '.join(x[:4] for x in git(d, 'rev-list', '--topo-order', '--reverse', m).split())} "
          f"date={' '.join(x[:4] for x in git(d, 'rev-list', '--reverse', m).split())}")
    return m


def fx_merge_add_real(d):
    a = lines("a", 40)
    extra = lines("extra", 30)
    commit(d, {"LOG.md": a}, msg="c1-base")
    git(d, "checkout", "-q", "-b", "side")
    commit(d, {"LOG.md": a + extra}, msg="cs-side-add30")
    git(d, "checkout", "-q", "-")
    commit(d, {"LOG.md": a + ["main tail"]}, msg="cm-main")
    git(d, *IDENT, "merge", "-q", "-s", "ours", "--no-edit", "side")
    return git(d, "rev-parse", "HEAD")


CASES = [
    ("M03", "cli-default-threshold-20-vs-21", fx_cli20, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M04", "threshold-0-validation-removed", fx_thresh0, ["--repo", "@D@", "--to", "@T@", "--json", "--threshold", "0"]),
    ("M08", "merge-last-parent-side-adds30", fx_merge_add_real, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M10", "merge-all-parents-conflict-merge", fx_merge_conflict, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M14", "dup-lines-restored-by-includes-self", fx_dup_selfrestore, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M23", "summary-partial-counts-unrestored", fx_unrestored, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M28", "renames-allowed-log-renamed-away", fx_rename_real, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M29", "renames-prefilter-log-renamed-away", fx_rename_real, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M30", "renames-udiff-log-renamed-away", fx_rename_real, ["--repo", "@D@", "--to", "@T@", "--json"]),
    ("M37", "topo-vs-date-restored-by", fx_topo_date, ["--repo", "@D@", "--to", "@T@", "--json"]),
]


def main():
    outdir = os.path.join(S, "probe-out")
    os.makedirs(outdir, exist_ok=True)
    for mid, label, fx, args in CASES:
        root = tempfile.mkdtemp(prefix="probe-", dir=os.path.join(S, "probe"))
        d = repo(root)
        print(f"== {mid} {label}")
        if mid == "M03":
            # drive through main() CLI: subprocess without --threshold
            pass
        tip = fx(d)
        real_args = [x.replace("@D@", d).replace("@T@", tip) for x in args]
        rc0, o0, e0 = run_tool(PRISTINE, real_args)
        mutp = os.path.join(S, "mut", f"{mid}.py")
        rc1, o1, e1 = run_tool(mutp, real_args)
        print(f"    pristine: {brief(rc0, o0, e0)}")
        print(f"    mutant  : {brief(rc1, o1, e1)}")
        same = (rc0, o0) == (rc1, o1)
        print(f"    DIVERGES: {not same}")
        with open(os.path.join(outdir, f"{mid}.txt"), "w") as fh:
            fh.write(f"case: {label}\nargs: {real_args}\n\n"
                     f"pristine rc={rc0}\n{o0}\nstderr: {e0}\n\n"
                     f"mutant rc={rc1}\n{o1}\nstderr: {e1}\n\ndiverges: {(rc0, o0) != (rc1, o1)}\n")


if __name__ == "__main__":
    main()
