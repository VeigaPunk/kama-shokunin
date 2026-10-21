#!/usr/bin/env python3
"""RevengeGitfile: round-23 O02 gitfile / linked-worktree probes (findings only).

Fixtures live under /tmp/gitfile-r23-run/fx (fresh; GIT_CONFIG_GLOBAL=/dev/null;
explicit identity). The auditor under test is the lane clone at 245a37f. The only
contact with the real lane and fleet is read-only `git rev-parse` in the classifier
section and one read-only auditor run on the production pair.
"""
import json
import os
import re
import shutil
import signal
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path("/tmp/gitfile-r23-run/fx")
AUDIT = Path("/tmp/kama-r23w2/RevengeGitfile/tools/report-landing-audit.py")
PROD_LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
PROD_FLEET = Path("/home/vgpnk/Projects/shokunin")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
           GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
           GIT_OPTIONAL_LOCKS="0")


class Refuse(Exception):
    """Proposed-check refusal; the message is the reason."""


def run(argv, timeout=60, env=None):
    proc = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=env or ENV, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        return 124, "", "TIMEOUT"
    return proc.returncode, out.decode(errors="replace"), err.decode(errors="replace")


def git(path, *args, env=None):
    """Fixture-building git: a failed premise stops the probe, never passes silently."""
    rc, out, err = run(["git", "-C", str(path), *args], env=env)
    if rc:
        raise SystemExit(f"PREMISE: git {' '.join(args)} in {path}: rc={rc} {err.strip()}")
    return out.strip()


def lstype(path):
    try:
        mode = os.lstat(path).st_mode
    except FileNotFoundError:
        return "missing"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISDIR(mode):
        return "dir"
    if stat.S_ISREG(mode):
        return "file"
    if stat.S_ISFIFO(mode):
        return "fifo"
    return "other"


def init(path):
    path.mkdir(parents=True, exist_ok=True)
    git(path, "init", "-q", "-b", "master")
    return path


def commit(repo, when, msg, author="kama-shokunin", rel="f", content=None):
    p = Path(repo, rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(p, "ab") as fh:
            fh.write((msg + "\n").encode())
    else:
        p.write_text(content, encoding="utf-8")
    git(repo, "add", "--", rel)
    stamp = f"@{when} +0000"
    env = dict(ENV, GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
               GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg, env=env)
    return git(repo, "rev-parse", "HEAD")


def gitfile(d, target):
    d.mkdir(parents=True, exist_ok=True)
    (d / ".git").write_text(f"gitdir: {target}\n", encoding="utf-8")
    return d


def hostile(root):
    """Repo-local config that would run programs if git executed the keys."""
    def mark(name):
        return f"sh -c 'touch {root}/MARK-{name}'"
    return (f"[core]\n\tfsmonitor = {mark('fsmonitor')}\n"
            f"\tpager = {mark('pager-core')}\n"
            f"[pager]\n\tlog = {mark('pager-log')}\n"
            f"[diff]\n\texternal = {mark('diff-external')}\n"
            f"[gpg]\n\tprogram = {mark('gpg')}\n"
            f"[log]\n\tshowSignature = true\n"
            f"[filter \"x\"]\n\tprocess = {mark('filter')}\n"
            f"[alias]\n\tlg = !{mark('alias')}\n"
            f"[include]\n\tpath = {root}/inc.cfg\n")


def build():
    if ROOT.exists():
        shutil.rmtree(ROOT)
    (ROOT / "out").mkdir(parents=True)
    P = {}
    main = P["main"] = init(ROOT / "main")
    A = P["A"] = commit(main, 1000, "round-1: work")
    B = P["B"] = commit(main, 1100, "round-1: measure")
    P["wt"] = ROOT / "wt"
    git(main, "worktree", "add", "-q", str(P["wt"]), "-b", "wtb")
    P["wtrel"] = ROOT / "wtrel"
    git(main, "-c", "worktree.useRelativePaths=true", "worktree", "add", "-q",
        str(P["wtrel"]), "-b", "wtrel")
    P["sepwt"] = ROOT / "sepwt"
    P["sep.git"] = ROOT / "sep.git"
    git(ROOT, "clone", "-q", "--separate-git-dir", str(P["sep.git"]), str(main), str(P["sepwt"]))
    P["clone_same"] = ROOT / "clone_same"
    git(ROOT, "clone", "-q", "--no-hardlinks", str(main), str(P["clone_same"]))
    decoy = P["decoy"] = ROOT / "decoy"
    git(ROOT, "clone", "-q", "--no-hardlinks", str(main), str(decoy))
    E = P["E"] = commit(decoy, 1150, "round-1: extra")
    decoy2 = P["decoy2"] = init(ROOT / "decoy2")
    if commit(decoy2, 1000, "round-1: work") != A:
        raise SystemExit("PREMISE: decoy2 commit A is not byte-identical to lane commit A")

    def fleet(name, cites):
        repo = init(ROOT / name)
        body = ("# kama round 1\n\n## Work performed\n- measured\n\n"
                "## Landed changes\n"
                + "".join(f"- `{sha[:12]}` {label}\n" for sha, label in cites))
        commit(repo, 1200, "round-1: kama report",
               rel=".ufo/reports/round-1/kama.md", content=body)
        return repo

    P["fleet_ok"] = fleet("fleet_ok", [(A, "work"), (B, "measure")])
    P["fleet_e"] = fleet("fleet_e", [(A, "work"), (B, "measure"), (E, "extra")])

    P["front"] = gitfile(ROOT / "front", decoy / ".git")
    P["front2"] = gitfile(ROOT / "front2", decoy2 / ".git")
    P["relfront"] = ROOT / "relfront"
    P["relfront"].mkdir()
    (P["relfront"] / ".git").write_text("gitdir: ../decoy/.git\n", encoding="utf-8")
    P["front_same"] = gitfile(ROOT / "front_same", P["clone_same"] / ".git")
    P["wt_copy"] = ROOT / "wt-copy"
    shutil.copytree(P["wt"], P["wt_copy"], symlinks=True)
    P["atk"] = init(ROOT / "atk")
    adm = P["atk_admin"] = ROOT / "atk" / ".git" / "worktrees" / "x"
    adm.mkdir(parents=True)
    (adm / "commondir").write_text(os.path.relpath(main / ".git", adm) + "\n", encoding="utf-8")
    (adm / "gitdir").write_text(str(ROOT / "atk-wt" / ".git") + "\n", encoding="utf-8")
    (adm / "HEAD").write_text("ref: refs/heads/master\n", encoding="utf-8")
    P["atk_wt"] = gitfile(ROOT / "atk-wt", adm)
    P["symrepo"] = ROOT / "symrepo"
    P["symrepo"].mkdir()
    os.symlink(decoy / ".git", P["symrepo"] / ".git")
    P["dangle"] = gitfile(ROOT / "dangle", ROOT / "nonexistent" / ".git")
    P["fifo"] = ROOT / "fifo"
    P["fifo"].mkdir()
    os.mkfifo(P["fifo"] / ".git")
    sup = P["super"] = init(ROOT / "super")
    git(sup, "-c", "protocol.file.allow=always", "submodule", "add", "-q", str(main), "sub")
    P["super_sub"] = ROOT / "super" / "sub"
    decoy_g = P["decoy_g"] = ROOT / "decoy_g"
    git(ROOT, "clone", "-q", "--no-hardlinks", str(main), str(decoy_g))
    (decoy_g / ".git" / "info").mkdir(exist_ok=True)
    (decoy_g / ".git" / "info" / "grafts").write_text(f"{B} {A}\n", encoding="utf-8")
    P["front_g"] = gitfile(ROOT / "front_g", decoy_g / ".git")
    decoy_h = P["decoy_h"] = ROOT / "decoy_h"
    git(ROOT, "clone", "-q", "--no-hardlinks", str(main), str(decoy_h))
    (ROOT / "inc.cfg").write_text(f"[core]\n\tfsmonitor = sh -c 'touch {ROOT}/MARK-include-fsmonitor'\n",
                                  encoding="utf-8")
    with open(decoy_h / ".git" / "config", "a", encoding="utf-8") as fh:
        fh.write(hostile(ROOT))
    P["front_h"] = gitfile(ROOT / "front_h", decoy_h / ".git")
    return P


def gitp(path, *args, gitdir=None):
    argv = ["git", "--git-dir", str(gitdir)] if gitdir else ["git", "-C", str(path)]
    rc, out, err = run([*argv, *args], timeout=20)
    if rc:
        raise Refuse(f"git {' '.join(args)} failed rc={rc}: {err.strip()[:100]}")
    return out.strip()


def gitdir_target(dotgit):
    first = Path(dotgit).read_text(encoding="utf-8").split("\n", 1)[0]
    if not first.startswith("gitdir: "):
        raise Refuse("gitfile lacks a 'gitdir: ' line")
    target = first[len("gitdir: "):].strip()
    if not os.path.isabs(target):
        target = os.path.join(os.path.dirname(dotgit), target)
    target = os.path.realpath(target)
    if not os.path.isdir(target):
        raise Refuse(f"gitfile target {target} is missing")
    return target


def classify(lane):
    """PROPOSED check (not applied to the auditor). Type of .git is read BEFORE any git
    call, because git itself blocks on a FIFO .git."""
    lane = os.path.abspath(str(lane))
    dotgit = os.path.join(lane, ".git")
    kind = lstype(dotgit)
    try:
        if kind in ("missing", "symlink", "fifo", "other"):
            raise Refuse(f".git is {kind}")
        target = gitdir_target(dotgit) if kind == "file" else None
        top = os.path.realpath(gitp(lane, "rev-parse", "--show-toplevel"))
        if top != os.path.realpath(lane):
            raise Refuse("not a worktree root")
        gd = os.path.realpath(gitp(lane, "rev-parse", "--path-format=absolute", "--git-dir"))
        cd = os.path.realpath(gitp(lane, "rev-parse", "--path-format=absolute",
                                   "--git-common-dir"))
        if kind == "dir":
            if gd == cd == os.path.realpath(dotgit):
                return "PLAIN: .git directory is both git-dir and common-dir"
            raise Refuse("directory .git whose git-dir and common-dir differ")
        if target != gd:
            raise Refuse("gitfile target differs from the git-dir git resolved")
        if gd == cd:
            try:
                wt = gitp(None, "config", "--get", "core.worktree", gitdir=gd)
            except Refuse:
                raise Refuse("gitfile -> standalone repository, no core.worktree back-link")
            if os.path.realpath(os.path.join(gd, wt)) != os.path.realpath(lane):
                raise Refuse("core.worktree names another path")
            return "GITFILE-STANDALONE: core.worktree back-link verified"
        if os.path.realpath(os.path.dirname(gd)) != os.path.realpath(os.path.join(cd, "worktrees")):
            raise Refuse("admin dir is not a direct child of common worktrees/")
        with open(os.path.join(gd, "gitdir"), encoding="utf-8") as fh:
            back = fh.readline().strip()
        back = os.path.realpath(back if os.path.isabs(back) else os.path.join(gd, back))
        if back != os.path.realpath(dotgit):
            raise Refuse(f"admin back-link names {back}")
        listed = {os.path.realpath(line[len("worktree "):])
                  for line in gitp(None, "worktree", "list", "--porcelain",
                                   gitdir=cd).splitlines()
                  if line.startswith("worktree ")}
        if os.path.realpath(lane) not in listed:
            raise Refuse("common repository does not list this worktree")
        return f"LINKED: worktree of {cd}"
    except Refuse as exc:
        return f"REFUSE: {exc}"


def dump(label, path):
    kind = lstype(Path(path, ".git"))
    print(f"\n[{label}] {path}  .git={kind}")
    if kind == "file":
        print(f"   gitfile line: {Path(path, '.git').read_text().splitlines()[0]!r}")
    if kind in ("missing", "fifo"):
        print("   (git not invoked: missing or FIFO)")
        return
    for args in (["--show-toplevel"], ["--git-dir"], ["--git-common-dir"],
                 ["--path-format=absolute", "--git-dir"],
                 ["--path-format=absolute", "--git-common-dir"],
                 ["--show-prefix"], ["--git-path", "info/grafts"]):
        rc, out, err = run(["git", "-C", str(path), "rev-parse", *args])
        val = out.strip() if rc == 0 else f"rc={rc} {err.strip()[:90]}"
        print(f"   rev-parse {' '.join(args)}: {val}")


def audit(lane, fleet, timeout=30):
    rc, out, err = run([sys.executable, str(AUDIT), "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1",
                        "--no-errata", "--json"], timeout=timeout)
    if rc == 124:
        return {"rc": "TIMEOUT(hang)"}
    if rc in (0, 1):
        doc = json.loads(out)
        res = doc["results"][0]
        return {"rc": rc, "status": doc["summary"]["status"],
                "required": res["required"], "round_commits": res["round_commits"],
                "defects": [f'{d["kind"]}:{d["token"][:12]}' for d in res["defects"]],
                "json": out}
    last = err.strip().splitlines()[-1] if err.strip() else ""
    return {"rc": rc, "stderr": last[:160]}


def marks():
    return sorted(p.name for p in ROOT.glob("MARK-*"))


def clear_marks():
    for p in ROOT.glob("MARK-*"):
        p.unlink()


def traced(lane, fleet):
    trace = ROOT / "out" / f"strace-{Path(lane).name}.txt"
    rc, _, _ = run(["strace", "-f", "-e", "trace=execve", "-o", str(trace),
                    sys.executable, str(AUDIT), "--lane-repo", str(lane),
                    "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata", "--json"],
                   timeout=90)
    progs, subs = {}, {}
    for line in trace.read_text().splitlines() if trace.exists() else []:
        m = re.search(r'execve\("([^"]+)"', line)
        if m and line.rstrip().endswith("= 0"):
            progs[m.group(1)] = progs.get(m.group(1), 0) + 1
            for sub in re.findall(r'"(rev-parse|log|cat-file|ls-tree|show|config|worktree|'
                                  r'hash-object|status|commit|add|rm|init|update-index|'
                                  r'fetch|clone|submodule)"', line):
                subs[sub] = subs.get(sub, 0) + 1
    return rc, progs, subs


def main():
    print(f"python {sys.version.split()[0]}; git: {run(['git', '--version'])[1].strip()}")
    P = build()
    print("\n## T1 git's own view of each fixture (no auditor)")
    for label, key in [("plain main", "main"), ("linked wt (absolute gitfile)", "wt"),
                       ("linked wtrel (relative gitfile)", "wtrel"),
                       ("separate-git-dir sepwt", "sepwt"),
                       ("submodule super/sub", "super_sub"),
                       ("gitfile front -> standalone decoy", "front"),
                       ("relative gitfile relfront", "relfront"),
                       ("gitfile front_same -> identical clone", "front_same"),
                       ("copied linked worktree wt-copy", "wt_copy"),
                       ("forged admin atk-wt -> main", "atk_wt"),
                       ("symlinked .git symrepo", "symrepo"),
                       ("dangling gitfile", "dangle"),
                       ("FIFO .git", "fifo")]:
        dump(label, P[key])
    print("\n## T1b admin back-links and config")
    for label, adm in [("wt admin", P["main"] / ".git/worktrees/wt"),
                       ("wtrel admin", P["main"] / ".git/worktrees/wtrel"),
                       ("forged atk admin", P["atk_admin"])]:
        for name in ("commondir", "gitdir"):
            f = adm / name
            print(f"  {label} {name}: {f.read_text().strip() if f.exists() else '(absent)'}")
    print(f"  main worktree list: "
          f"{gitp(None, 'worktree', 'list', '--porcelain', gitdir=P['main'] / '.git')!r}")
    print(f"  sep.git core.worktree: "
          f"{run(['git', '--git-dir', str(P['sep.git']), 'config', '--get', 'core.worktree'])[1:]}")
    print(f"  submodule module core.worktree: "
          f"{run(['git', '--git-dir', str(P['super'] / '.git/modules/sub'), 'config', '--get', 'core.worktree'])[1:]}")

    print("\n## T2 auditor verdicts (--rounds 1 --no-errata --json; expectation in brackets)")
    cases = [
        ("M plain + fleet_ok [clean]", "main", "fleet_ok"),
        ("M plain + fleet_e [landed-unresolved E]", "main", "fleet_e"),
        ("wt linked + fleet_ok [clean]", "wt", "fleet_ok"),
        ("wtrel relative linked + fleet_ok [clean]", "wtrel", "fleet_ok"),
        ("sepwt separate-git-dir + fleet_ok [clean]", "sepwt", "fleet_ok"),
        ("submodule super/sub + fleet_ok [clean]", "super_sub", "fleet_ok"),
        ("front -> decoy superset + fleet_e [FLIP?]", "front", "fleet_e"),
        ("relfront -> decoy superset + fleet_e [FLIP?]", "relfront", "fleet_e"),
        ("symrepo -> decoy superset + fleet_e [FLIP?]", "symrepo", "fleet_e"),
        ("front2 -> decoy subset (no B) + fleet_ok [fail]", "front2", "fleet_ok"),
        ("front_same -> identical clone + fleet_ok [clean]", "front_same", "fleet_ok"),
        ("wt-copy copied worktree + fleet_ok [clean?]", "wt_copy", "fleet_ok"),
        ("atk-wt forged admin -> main + fleet_ok [clean?]", "atk_wt", "fleet_ok"),
        ("front_g -> grafted decoy + fleet_ok [rc2 rewrites]", "front_g", "fleet_ok"),
        ("dangle + fleet_ok [rc2]", "dangle", "fleet_ok"),
        ("front_h -> hostile config + fleet_ok [clean, no marks]", "front_h", "fleet_ok"),
    ]
    for label, key, fkey in cases:
        clear_marks()
        res = audit(P[key], P[fkey])
        body = {k: v for k, v in res.items() if k != "json"}
        print(f"  {label:<56} {body} marks={marks()}")
    clear_marks()
    res = audit(P["fifo"], P["fleet_ok"], timeout=15)
    print(f"  {'FIFO .git + fleet_ok [hang expected]':<56} "
          f"{ {k: v for k, v in res.items() if k != 'json'} } marks={marks()}")
    print("  leftover git processes on fifo:",
          run(["pgrep", "-fc", str(P['fifo'] / '.git')])[1].strip() or "0")

    print("\n## T3 proposed identity check (classify); production pair read-only")
    for label, key in [("plain main", "main"), ("linked wt", "wt"), ("linked wtrel", "wtrel"),
                       ("separate-git-dir sepwt", "sepwt"), ("submodule super/sub", "super_sub"),
                       ("gitfile front (decoy)", "front"), ("relfront", "relfront"),
                       ("gitfile front_same", "front_same"), ("wt-copy", "wt_copy"),
                       ("forged atk-wt", "atk_wt"), ("symrepo", "symrepo"),
                       ("dangle", "dangle"), ("FIFO", "fifo"), ("gitfile front_g", "front_g"),
                       ("gitfile front_h", "front_h")]:
        print(f"  {label:<26} {classify(P[key])}")
    print(f"  {'PRODUCTION lane kama-shokunin':<26} {classify(PROD_LANE)}")
    print(f"  {'PRODUCTION fleet root':<26} {classify(PROD_FLEET)}")

    print("\n## T4 exec trace (strace -f -e execve); positive controls first")
    clear_marks()
    run(["git", "-C", str(P["front_h"]), "status", "--porcelain"])
    print("  positive control, status through gitfile front_h:", marks())
    clear_marks()
    run(["git", "-C", str(P["front_h"]), "log", "-p", "-1", "--format=%H"])
    print("  positive control, log -p through gitfile front_h:", marks())
    clear_marks()
    rc, progs, subs = traced(P["front_h"], P["fleet_ok"])
    print(f"  auditor via front_h: strace rc={rc} marks={marks()}")
    print(f"    programs executed: {progs}")
    print(f"    git subcommands seen in execve argv: {subs}")
    clear_marks()
    rc2, progs2, subs2 = traced(P["main"], P["fleet_ok"])
    print(f"  auditor via plain main (baseline): strace rc={rc2} programs={progs2} subs={subs2}")

    print("\n## T5 identity-blindness of the verdict record")
    a = audit(P["main"], P["fleet_ok"])
    b = audit(P["front_same"], P["fleet_ok"])
    print(f"  plain main JSON == gitfile-to-identical-clone JSON: {a.get('json') == b.get('json')}")
    if a.get("json"):
        d = json.loads(a["json"])
        print(f"  top-level JSON keys: {sorted(d)}")
        print(f"  result keys: {sorted(d['results'][0])}")

    print("\n## T6 production run (read-only; default --rounds 10-)")
    rc, out, err = run([sys.executable, str(AUDIT), "--lane-repo", str(PROD_LANE),
                        "--fleet-repo", str(PROD_FLEET), "--json"], timeout=120)
    if rc in (0, 1):
        s = json.loads(out)["summary"]
        print(f"  rc={rc} status={s['status']} reports={s['reports']} defects={s['defects']} "
              f"uncorrected={s['uncorrected']} required_commits={s['required_commits']}")
    else:
        print(f"  rc={rc} stderr={err.strip()[-200:]}")


if __name__ == "__main__":
    main()
