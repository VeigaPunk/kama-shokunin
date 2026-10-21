#!/usr/bin/env python3
"""C1EnvSentinel probes (round 21 FALSIFY) for tools/report-landing-audit.py.

Question: does inherited or ambient environment (GIT_*, XDG_CONFIG_HOME, HOME,
TMPDIR), safe.directory, hooks, gpgsign, core.fsmonitor, repo discovery, or the
repo-local state of an audited repository redirect or break the audit or its
--selftest?

Every repository touched here is a throwaway fixture under --work. The lane and
fleet checkouts are never passed to the tool. The root-owned probe uses `sudo -n`
only to chown its throwaway fixture (restored afterwards); it is SKIPPED when
`sudo -n true` fails.

usage: repro.py [--tool PATH] [--work DIR] [--out FILE]
Prints one line per probe and writes the same lines to --out.
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
import tempfile

P = pathlib.Path
HERE = P(__file__).resolve().parent
SCRATCH = P("/tmp/kama-r21-C1EnvSentinel/exp")
TOOL_DEFAULT = "/tmp/kama-r21-C1EnvSentinel/lane/tools/report-landing-audit.py"
OLD_FILTER = 'env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}'
OLD_SET = 'env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1", **extra)'
OLD_OVERRIDE = '"-c", "commit.gpgsign=false", "commit"'
LOG = []


def say(pid, verdict, rc, text):
    line = f"{pid:<5} {verdict:<13} rc={str(rc):<4} {text}"
    LOG.append(line)
    print(line, flush=True)


def sh(argv, env=None, stdin=None, cwd=None, timeout=300):
    p = subprocess.run(argv, env=env, input=stdin, cwd=cwd, capture_output=True,
                       timeout=timeout)
    return (p.returncode, p.stdout.decode("utf-8", "backslashreplace"),
            p.stderr.decode("utf-8", "backslashreplace"))


def cne(err):
    """The could-not-evaluate / fatal line from stderr, else the first line."""
    lines = [ln.strip() for ln in err.splitlines() if ln.strip()]
    hits = [ln for ln in lines if "could-not-evaluate" in ln or "fatal" in ln]
    return (hits or lines or [""])[0][:170]


def env_with(**kw):
    env = dict(os.environ)
    for key, val in kw.items():
        if val is None:
            env.pop(key, None)
        else:
            env[key] = str(val)
    return env


def plain_env(home, xdg, **extra):
    """Ambient-like env: no GIT_* except what the caller adds."""
    env = {"PATH": os.environ["PATH"], "HOME": str(home), "LC_ALL": "C.UTF-8"}
    if xdg is not None:
        env["XDG_CONFIG_HOME"] = str(xdg)
    env.update({k: str(v) for k, v in extra.items()})
    return env


def ident(name, when):
    return {"GIT_AUTHOR_NAME": name, "GIT_COMMITTER_NAME": name,
            "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
            "GIT_AUTHOR_DATE": f"@{when} +0000", "GIT_COMMITTER_DATE": f"@{when} +0000"}


class Fx:
    """Fixture env: no ambient git config; GIT_CONFIG_GLOBAL pinned to devnull."""

    def __init__(self, work):
        self.work = work
        self.home = work / "fx-home"
        self.xdg = work / "fx-xdg"
        self.home.mkdir(parents=True, exist_ok=True)
        self.xdg.mkdir(parents=True, exist_ok=True)

    def env(self, **extra):
        env = plain_env(self.home, self.xdg, GIT_CONFIG_GLOBAL=os.devnull,
                        GIT_CONFIG_NOSYSTEM="1")
        env.update({k: str(v) for k, v in extra.items()})
        return env


def git(env, repo, *args, stdin=None):
    rc, out, err = sh(["git", "-C", str(repo), *args], env=env, stdin=stdin)
    if rc != 0:
        raise RuntimeError(f"git {' '.join(args)} in {repo}: rc={rc}: {err.strip()[:200]}")
    return out.strip()


def init(fx, repo):
    repo.mkdir(parents=True, exist_ok=True)
    git(fx.env(), repo, "init", "-q", "-b", "master")


def commit(fx, repo, msg, author, when, files=None):
    """Porcelain commit (git normalises the message to UTF-8)."""
    env = fx.env(**ident(author, when))
    if files is None:
        files = {"f": msg.split(b"\n", 1)[0] + b"\n"}
    for rel, data in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "ab") as fh:
            fh.write(data)
    git(env, repo, "add", "-A")
    git(env, repo, "-c", "commit.gpgsign=false", "commit", "-q", "--allow-empty",
        "-F", "-", stdin=msg + b"\n")
    return git(env, repo, "rev-parse", "HEAD")


def raw_commit(fx, repo, parent, msg, author, when):
    """Plumbing commit: stores msg bytes exactly (no UTF-8 normalisation)."""
    tree = git(fx.env(), repo, "rev-parse", parent + "^{tree}")
    body = (f"tree {tree}\nparent {parent}\nauthor {author} <a@x> {when} +0000\n"
            f"committer {author} <a@x> {when} +0000\n\n").encode() + msg + b"\n"
    sha = git(fx.env(), repo, "hash-object", "-t", "commit", "--literally", "-w",
              "--stdin", stdin=body)
    git(fx.env(), repo, "update-ref", "refs/heads/master", sha)
    return sha


def build_decoy(fx):
    """Bare repo holding one commit X that exists nowhere else."""
    bare = fx.work / "decoy.git"
    git(fx.env(), fx.work, "init", "-q", "--bare", str(bare))
    env = fx.env(**ident("decoy", 900))
    blob = git(env, bare, "hash-object", "-w", "--stdin", stdin=b"decoy only\n")
    tree = git(env, bare, "mktree", stdin=f"100644 blob {blob}\tdecoy.txt\n".encode())
    cm = git(env, bare, "commit-tree", tree, "-m", "decoy: only here")
    git(env, bare, "update-ref", "refs/heads/master", cm)
    return cm, bare


def build(fx, name, *, variant="base", shallow3=False, raw_c2=None, decoy_x=None):
    """Lane: round-1 work (1000) [+ round-1 measure (1100)] [+ docs tip (1150)].
    Fleet: round-1 kama report (1200) citing c1 (base) or c1+c2 (full)."""
    root = fx.work / name
    lane, fleet = root / "lane", root / "fleet"
    init(fx, lane)
    init(fx, fleet)
    shas = {"c1": commit(fx, lane, b"round-1: work", "kama-shokunin", 1000)}
    if raw_c2 is not None:
        shas["c2"] = raw_commit(fx, lane, shas["c1"], raw_c2, "kama-shokunin", 1100)
    else:
        shas["c2"] = commit(fx, lane, b"round-1: measure", "kama-shokunin", 1100)
    if shallow3:
        shas["c3"] = commit(fx, lane, b"docs: tidy", "kama-shokunin", 1150)
    landed = f"- `{shas['c1'][:9]}` work\n"
    if variant == "full":
        landed += f"- `{shas['c2'][:9]}` measure\n"
    body = "# r1\n## Work performed\nmeasured\n"
    if decoy_x:
        body += f"stray {decoy_x}\n"
    report = (body + "## Landed changes\n" + landed).encode()
    commit(fx, fleet, b"round-1: kama report", "kama-shokunin", 1200,
           files={".ufo/reports/round-1/kama.md": report})
    return lane, fleet, shas


def script(path, log, rc=0):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('#!/bin/sh\necho "$(basename "$0") $*" >> "%s"\nexit %d\n' % (log, rc),
                    encoding="utf-8")
    path.chmod(0o755)
    return path


def marks(log):
    return log.read_text(encoding="utf-8").strip().splitlines() if log.exists() else []


def evil_cfg(fx, tag):
    """Git config text whose every side effect appends a marker to one log."""
    log = fx.work / f"MARK-{tag}.log"
    tpl = fx.work / f"tpl-{tag}"
    script(tpl / "hooks" / "pre-commit", log, 0)
    fsm = script(fx.work / f"fsmonitor-{tag}.sh", log, 0)
    gpg = script(fx.work / f"gpg-{tag}.sh", log, 1)
    text = ("[commit]\n\tgpgsign = true\n"
            f"[gpg]\n\tprogram = {gpg}\n"
            f"[init]\n\ttemplateDir = {tpl}\n"
            f"[core]\n\tfsmonitor = {fsm}\n"
            "[log]\n\tshowSignature = true\n"
            "[safe]\n\tdirectory = *\n")
    return log, text


def write_xdg(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return root


def audit(tool, lane, fleet, env, *extra):
    argv = [sys.executable, str(tool), "--lane-repo", str(lane), "--fleet-repo", str(fleet),
            "--branch", "master", "--rounds", "1", "--no-errata", "--json", *extra]
    return sh(argv, env=env)


def norm(out):
    try:
        doc = json.loads(out)
    except ValueError:
        return out
    for res in doc["results"]:
        res.pop("report", None)
    return doc


def digest(rc, out):
    doc = norm(out)
    if isinstance(doc, dict):
        defects = [f"{d['kind']}:{d['token'][:10]}" for r in doc["results"] for d in r["defects"]]
        return f"rc={rc} status={doc['summary']['status']} defects={defects}"
    return f"rc={rc} stdout={doc[:40]!r}"


def selftest(tool, env):
    rc, out, err = sh([sys.executable, str(tool), "--selftest"], env=env)
    lines = [ln for ln in out.splitlines() if ln.strip()]
    last = lines[-1] if lines else ""
    fails = [ln for ln in lines if ln.startswith("FAIL")]
    return rc, last, fails, cne(err)


def st_ok(rc, last, fails):
    return rc == 0 and last.endswith("failed=0") and not fails


class Ctx:
    pass


def base_of(ctx, fixture):
    rc, out, _ = audit(ctx.tool, fixture[0], fixture[1], os.environ)
    return rc, out


def compare(ctx, pid, label, fixture, env, base=None):
    b_rc, b_out = base if base is not None else base_of(ctx, fixture)
    rc, out, err = audit(ctx.tool, fixture[0], fixture[1], env)
    same = rc == b_rc and norm(out) == norm(b_out)
    extra = "" if same else f" | base {digest(b_rc, b_out)}"
    err_s = f" | {cne(err)}" if err.strip() else ""
    say(pid, "ISOLATED" if same else "CHANGED", rc, f"{label} | {digest(rc, out)}{extra}{err_s}")
    return rc, out, err


def plain_probe(ctx, tag, home, xdg):
    """Positive control: plain git under the same ambient config."""
    repo = ctx.work / f"plain-{tag}"
    env = plain_env(home, xdg, **ident("plain", 1000))
    sh(["git", "init", "-q", "-b", "master", str(repo)], env=env)
    (repo / "f").write_text("x\n", encoding="utf-8")
    rc_add = sh(["git", "-C", str(repo), "add", "f"], env=env)[0]
    rc_commit = sh(["git", "-C", str(repo), "commit", "-q", "-m", "x"], env=env)[0]
    return rc_add, rc_commit


def group_a(ctx):
    d_obj = str(ctx.decoy / "objects")
    compare(ctx, "A1", "GIT_DIR=decoy.git", ctx.B, env_with(GIT_DIR=str(ctx.decoy)))
    compare(ctx, "A2", "GIT_INDEX_FILE=/nonexistent/idx", ctx.B,
            env_with(GIT_INDEX_FILE="/nonexistent/idx"))
    compare(ctx, "A3", "GIT_OBJECT_DIRECTORY=decoy/objects (X only there)", ctx.FULL,
            env_with(GIT_OBJECT_DIRECTORY=d_obj))
    compare(ctx, "A4", "GIT_ALTERNATE_OBJECT_DIRECTORIES=decoy/objects (X only there)",
            ctx.FULL, env_with(GIT_ALTERNATE_OBJECT_DIRECTORIES=d_obj))
    compare(ctx, "A5", "GIT_COMMON_DIR=decoy.git", ctx.B, env_with(GIT_COMMON_DIR=str(ctx.decoy)))
    compare(ctx, "A6", "GIT_WORK_TREE+GIT_NAMESPACE+GIT_CONFIG_COUNT(i18n UTF-16LE)", ctx.B,
            env_with(GIT_WORK_TREE="/nonexistent", GIT_NAMESPACE="decoy",
                     GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="i18n.logOutputEncoding",
                     GIT_CONFIG_VALUE_0="UTF-16LE"))
    gcfg = ctx.work / "evil-global.cfg"
    gcfg.write_text("[i18n]\n\tlogOutputEncoding = UTF-16LE\n[log]\n\tshowSignature = true\n",
                    encoding="utf-8")
    scfg = ctx.work / "evil-system.cfg"
    scfg.write_text("[core]\n\tfsmonitor = /nonexistent/fsm\n", encoding="utf-8")
    compare(ctx, "A7", "GIT_CONFIG_GLOBAL+GIT_CONFIG_SYSTEM evil files", ctx.B,
            env_with(GIT_CONFIG_GLOBAL=str(gcfg), GIT_CONFIG_SYSTEM=str(scfg)))


def group_b(ctx):
    rc, last, fails, tail = selftest(ctx.tool, os.environ)
    say("B1", "ISOLATED" if st_ok(rc, last, fails) else "BROKEN", rc,
        f"selftest, host env | {last} | {tail}")
    log_b2 = ctx.work / "MARK-B2.log"
    tpl2 = ctx.work / "tpl-B2"
    script(tpl2 / "hooks" / "pre-commit", log_b2, 1)
    g2 = ctx.work / "evil-B2-global.cfg"
    g2.write_text("[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /nonexistent/gpg\n",
                  encoding="utf-8")
    d_obj = str(ctx.decoy / "objects")
    env_b2 = env_with(
        GIT_DIR=str(ctx.decoy), GIT_INDEX_FILE="/nonexistent/idx",
        GIT_OBJECT_DIRECTORY=d_obj, GIT_ALTERNATE_OBJECT_DIRECTORIES=d_obj,
        GIT_COMMON_DIR=str(ctx.decoy), GIT_WORK_TREE="/nonexistent", GIT_NAMESPACE="decoy",
        GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="i18n.logOutputEncoding",
        GIT_CONFIG_VALUE_0="UTF-16LE", GIT_CONFIG_GLOBAL=str(g2), GIT_TEMPLATE_DIR=str(tpl2),
        GIT_NO_REPLACE_OBJECTS="1", GIT_CEILING_DIRECTORIES=str(ctx.work))
    rc, last, fails, tail = selftest(ctx.tool, env_b2)
    say("B2", "ISOLATED" if st_ok(rc, last, fails) and not marks(log_b2) else "BROKEN", rc,
        f"selftest, GIT_* decoys + GIT_TEMPLATE_DIR hook exit 1 | {last} | "
        f"hook_marks={len(marks(log_b2))} | {tail}")
    rc, last, fails, tail = selftest(ctx.tool, env_with(TMPDIR=str(ctx.B[1])))
    say("B3", "ISOLATED" if st_ok(rc, last, fails) else "BROKEN", rc,
        f"selftest with TMPDIR inside a git worktree | {last} | {tail}")


def group_c(ctx):
    # C1: XDG_CONFIG_HOME/git/config with side-effecting settings
    log1, txt1 = evil_cfg(ctx.fx, "xdg")
    xdg1 = write_xdg(ctx.work / "xdg-evil", "git/config", txt1)
    env_c1 = env_with(XDG_CONFIG_HOME=str(xdg1))
    compare(ctx, "C1a", "XDG git/config evil (gpgsign, templateDir hook, fsmonitor, showSignature)",
            ctx.B, env_c1)
    say("C1a'", "INFO", "-", f"marks after audit under XDG evil = {len(marks(log1))}")
    rc, last, fails, tail = selftest(ctx.tool, env_c1)
    say("C1b", "ISOLATED" if st_ok(rc, last, fails) and not marks(log1) else "BROKEN", rc,
        f"selftest under XDG evil | {last} | marks={len(marks(log1))} | {tail}")
    add_rc, commit_rc = plain_probe(ctx, "xdg", ctx.fx.home, xdg1)
    say("C1c", "CONTROL", commit_rc,
        f"plain git, same XDG config: add rc={add_rc} commit rc={commit_rc} "
        f"marks={sorted({m.split()[0] for m in marks(log1)})}")

    # C2: HOME/.gitconfig with the same content, XDG unset
    log2, txt2 = evil_cfg(ctx.fx, "home")
    home2 = write_xdg(ctx.work / "home-evil", ".gitconfig", txt2)
    env_c2 = env_with(HOME=str(home2), XDG_CONFIG_HOME=None)
    compare(ctx, "C2a", "HOME/.gitconfig evil (same content), XDG unset", ctx.B, env_c2)
    rc, last, fails, tail = selftest(ctx.tool, env_c2)
    say("C2b", "ISOLATED" if st_ok(rc, last, fails) and not marks(log2) else "BROKEN", rc,
        f"selftest under HOME evil | {last} | marks={len(marks(log2))} | {tail}")
    add_rc, commit_rc = plain_probe(ctx, "home", home2, None)
    say("C2c", "CONTROL", commit_rc,
        f"plain git, same HOME config: add rc={add_rc} commit rc={commit_rc} "
        f"marks={sorted({m.split()[0] for m in marks(log2)})}")

    # C3: XDG git/ignore (core.excludesFile default). GIT_CONFIG_GLOBAL does not cover it.
    ign = write_xdg(ctx.work / "xdg-ign", "git/ignore", "f\n")
    env_c3 = env_with(XDG_CONFIG_HOME=str(ign))
    compare(ctx, "C3a", "XDG git/ignore lists f: audit (no git add on audit path)", ctx.B, env_c3)
    rc, last, fails, tail = selftest(ctx.tool, env_c3)
    say("C3b", "BROKEN" if rc != 0 else "ISOLATED", rc, f"selftest under XDG git/ignore | {last} | {tail}")
    repo3 = ctx.work / "plain-ign"
    sh(["git", "init", "-q", "-b", "master", str(repo3)], env=plain_env(ctx.fx.home, ign))
    (repo3 / "f").write_text("x\n", encoding="utf-8")
    rc_ign, _, err_ign = sh(["git", "-C", str(repo3), "add", "f"],
                            env=plain_env(ctx.fx.home, ign))
    say("C3c", "CONTROL", rc_ign, f"plain git add f under same git/ignore | {cne(err_ign)}")

    # C4: XDG_CONFIG_DIRS -- does git read it at all?
    dirs = write_xdg(ctx.work / "xdg-dirs", "git/config", "[user]\n\tname = xdgdirs-evil\n")
    env_c4 = plain_env(ctx.fx.home, ctx.fx.xdg, XDG_CONFIG_DIRS=str(dirs))
    rc, out, _ = sh(["git", "config", "--get", "user.name"], env=env_c4, cwd=ctx.work)
    say("C4", "NOT-READ" if out.strip() == "" else "READ", rc,
        f"git config user.name with XDG_CONFIG_DIRS evil -> {out.strip()!r}")

    # C5: XDG git/attributes (core.attributesFile default). Not covered by GIT_CONFIG_GLOBAL.
    att = write_xdg(ctx.work / "xdg-attr", "git/attributes", "f working-tree-encoding=UTF-16LE\n")
    env_c5 = env_with(XDG_CONFIG_HOME=str(att))
    compare(ctx, "C5a", "XDG git/attributes: f working-tree-encoding=UTF-16LE, audit", ctx.B, env_c5)
    rc, last, fails, tail = selftest(ctx.tool, env_c5)
    say("C5b", "BROKEN" if rc != 0 else "ISOLATED", rc,
        f"selftest under XDG git/attributes | {last} | {tail}")
    repo5 = ctx.work / "plain-attr"
    env5 = plain_env(ctx.fx.home, att)
    sh(["git", "init", "-q", "-b", "master", str(repo5)], env=env5)
    (repo5 / "f").write_bytes(b"round-1: measure\n")
    rc_at, _, err_at = sh(["git", "-C", str(repo5), "add", "f"], env=env5)
    say("C5c", "CONTROL", rc_at, f"plain git add f (17 bytes) under same attributes | {cne(err_at)}")


def group_d(ctx):
    sudo_ok = sh(["sudo", "-n", "true"])[0] == 0
    if not sudo_ok:
        say("D0", "SKIPPED", "-", "sudo -n unavailable; root-owned safe.directory probe not run")
        return
    lane, fleet, _ = ctx.SAFE
    sh(["sudo", "-n", "chown", "-R", "root:root", str(lane)])
    try:
        rc, out, err = audit(ctx.tool, lane, fleet, os.environ)
        say("D1", "FAIL-CLOSED" if rc == 2 else "CHANGED", rc,
            f"root-owned lane, vgpnk audits | {cne(err)}")
        sdx = write_xdg(ctx.work / "xdg-safe", "git/config", f"[safe]\n\tdirectory = {lane}\n")
        prc = sh(["git", "-C", str(lane), "rev-parse", "--verify", "master^{commit}"],
                 env=plain_env(ctx.fx.home, sdx))[0]
        say("D2", "CONTROL", prc, "plain git with operator safe.directory for the lane")
        rc, out, err = audit(ctx.tool, lane, fleet, env_with(XDG_CONFIG_HOME=str(sdx)))
        say("D3", "FAIL-CLOSED" if rc == 2 else "CHANGED", rc,
            f"audit with operator safe.directory in XDG config | {cne(err)}")
    finally:
        sh(["sudo", "-n", "chown", "-R", f"{os.getuid()}:{os.getgid()}", str(lane)])


def group_e(ctx):
    lane, fleet, _ = ctx.DISC
    notlane = fleet / "not-a-lane"
    notlane.mkdir(parents=True, exist_ok=True)
    (notlane / "README").write_text("not a repository\n", encoding="utf-8")
    rc_n, out_n, _ = audit(ctx.tool, lane, fleet, os.environ)
    rc_1, out_1, _ = audit(ctx.tool, notlane, fleet, os.environ)
    same_1 = rc_1 == rc_n and norm(out_1) == norm(out_n)
    say("E1", "CHANGED" if not same_1 else "ISOLATED", rc_1,
        f"--lane-repo=non-repo dir inside fleet | {digest(rc_1, out_1)} | "
        f"normal {digest(rc_n, out_n)}")
    rc_2, out_2, _ = audit(ctx.tool, notlane, fleet, env_with(GIT_CEILING_DIRECTORIES=str(fleet)))
    same_2 = rc_2 == rc_1 and norm(out_2) == norm(out_1)
    say("E2", "CEILING-GONE" if same_2 else "CEILING-OK", rc_2,
        f"same with GIT_CEILING_DIRECTORIES=fleet (stripped) | {digest(rc_2, out_2)}")
    prc = sh(["git", "-C", str(notlane), "rev-parse", "--git-dir"],
             env=plain_env(ctx.fx.home, None, GIT_CEILING_DIRECTORIES=str(fleet)))[0]
    nrc = sh(["git", "-C", str(notlane), "rev-parse", "--git-dir"],
             env=plain_env(ctx.fx.home, None))[0]
    say("E3", "CONTROL", prc, f"plain git honors the ceiling: with ceiling rc={prc}; "
        f"without ceiling rc={nrc}")


def group_f(ctx):
    # F1: repo-local log.showSignature + gpg.program in the audited lane
    lane, fleet, shas = ctx.SIG
    tree = git(ctx.fx.env(), lane, "rev-parse", shas["c2"] + "^{tree}")
    body = (f"tree {tree}\nparent {shas['c2']}\nauthor kama-shokunin <a@x> 1300 +0000\n"
            "committer kama-shokunin <a@x> 1300 +0000\n"
            "gpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n\n"
            "round-1: signed tip\n").encode()
    sig = git(ctx.fx.env(), lane, "hash-object", "-t", "commit", "--literally", "-w",
              "--stdin", stdin=body)
    git(ctx.fx.env(), lane, "update-ref", "refs/heads/master", sig)
    log_f1 = ctx.work / "MARK-F1.log"
    gpg_f1 = script(ctx.work / "gpg-F1.sh", log_f1, 1)
    rc_a, out_a, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F1a", "INFO", rc_a, f"signed tip, no repo config | marks={len(marks(log_f1))} | "
        f"{digest(rc_a, out_a)}")
    git(ctx.fx.env(), lane, "config", "log.showSignature", "true")
    git(ctx.fx.env(), lane, "config", "gpg.program", str(gpg_f1))
    rc_b, out_b, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F1b", "EXEC" if marks(log_f1) else "NOT-EXEC", rc_b,
        f"audited repo's own config: showSignature+gpg.program | marks={marks(log_f1)[:1]} | "
        f"{digest(rc_b, out_b)}")

    # F3: refs/replace in the audited lane hides an omitted commit
    lane, fleet, shr = ctx.REPL
    base_rc, base_out = base_of(ctx, (lane, fleet, shr))
    tree1 = git(ctx.fx.env(), lane, "rev-parse", shr["c1"] + "^{tree}")
    repl = git(ctx.fx.env(**ident("someone", 1150)), lane, "commit-tree", tree1,
               "-p", shr["c1"], stdin=b"docs: tidy\n")
    git(ctx.fx.env(), lane, "replace", shr["c2"], repl)
    rc_r, out_r, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F3a", "FALSE-PASS" if rc_r == 0 and base_rc == 1 else "CHANGED", rc_r,
        f"refs/replace of omitted c2 | {digest(rc_r, out_r)} | base {digest(base_rc, base_out)}")
    rc_r2, out_r2, _ = audit(ctx.tool, lane, fleet, env_with(GIT_NO_REPLACE_OBJECTS="1"))
    say("F3b", "FALSE-PASS" if rc_r2 == 0 else "CHANGED", rc_r2,
        "operator GIT_NO_REPLACE_OBJECTS=1 is stripped; replacement still honored")
    raw = git(ctx.fx.env(), lane, "--no-replace-objects", "log", "--format=%s", "master")
    say("F3c", "CONTROL", 0, "git --no-replace-objects log shows: " + " | ".join(raw.splitlines()))

    # F4: repo-local objects/info/alternates widens the object lookup scope
    lane, fleet, _ = ctx.ALT
    base_rc, base_out = base_of(ctx, ctx.ALT)
    pre = sh(["git", "-C", str(fleet), "cat-file", "-t", ctx.decoy_x])[0]
    (fleet / ".git" / "objects" / "info" / "alternates").write_text(
        str(ctx.decoy / "objects") + "\n", encoding="utf-8")
    post = sh(["git", "-C", str(fleet), "cat-file", "-t", ctx.decoy_x])
    rc_f, out_f, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F4", "FALSE-PASS" if rc_f == 0 and base_rc == 1 else "CHANGED", rc_f,
        f"fleet alternates -> decoy objects | cat-file X before rc={pre} after rc={post[0]} "
        f"({post[1].strip()}) | {digest(rc_f, out_f)} | base {digest(base_rc, base_out)}")

    # F5: repo-local .git/shallow hides history below the tip
    lane, fleet, shs = ctx.SH3
    base_rc, base_out = base_of(ctx, ctx.SH3)
    count_before = git(ctx.fx.env(), lane, "rev-list", "--count", "master")
    (lane / ".git" / "shallow").write_text(shs["c3"] + "\n", encoding="utf-8")
    count_after = git(ctx.fx.env(), lane, "rev-list", "--count", "master")
    rc_s, out_s, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F5", "FALSE-PASS" if rc_s == 0 and base_rc == 1 else "CHANGED", rc_s,
        f"lane .git/shallow at tip | rev-list count {count_before}->{count_after} | "
        f"{digest(rc_s, out_s)} | base {digest(base_rc, base_out)}")

    # F5b: repo-local info/grafts re-parents the tip, hiding history below it
    lane, fleet, shg = build(ctx.fx, "graft", shallow3=True)
    base_rc, base_out = base_of(ctx, (lane, fleet, shg))
    (lane / ".git" / "info" / "grafts").write_text(f"{shg['c3']} {shg['c1']}\n", encoding="utf-8")
    rc_g, out_g, _ = audit(ctx.tool, lane, fleet, os.environ)
    count_g = git(ctx.fx.env(), lane, "rev-list", "--count", "master")
    say("F5b", "FALSE-PASS" if rc_g == 0 and base_rc == 1 else "CHANGED", rc_g,
        f"lane info/grafts re-parents tip onto c1 | rev-list count={count_g} | "
        f"{digest(rc_g, out_g)} | base {digest(base_rc, base_out)}")

    # F6: repo-local core.hooksPath in the audited lane is not executed by the audit
    lane, fleet, _ = ctx.HK
    log_f6 = ctx.work / "MARK-F6.log"
    hk = ctx.work / "hk-hooks"
    script(hk / "pre-commit", log_f6, 0)
    git(ctx.fx.env(), lane, "config", "core.hooksPath", str(hk))
    rc_h, _, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F6a", "NOT-RUN" if not marks(log_f6) else "EXEC", rc_h,
        f"audited repo core.hooksPath pre-commit during audit | marks={len(marks(log_f6))}")
    git(ctx.fx.env(**ident("plain", 1500)), lane, "commit", "-q", "--allow-empty", "-m", "t")
    say("F6b", "CONTROL", 0, f"same hook fires on a real commit | marks={len(marks(log_f6))}")

    # F7: repo-local core.fsmonitor in the audited lane is not run by the audit
    lane, fleet, _ = ctx.FSM
    log_f7 = ctx.work / "MARK-F7.log"
    fsm = script(ctx.work / "fsm-F7.sh", log_f7, 0)
    git(ctx.fx.env(), lane, "config", "core.fsmonitor", str(fsm))
    rc_m, _, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F7a", "NOT-RUN" if not marks(log_f7) else "EXEC", rc_m,
        f"audited repo core.fsmonitor during audit | marks={len(marks(log_f7))}")
    git(ctx.fx.env(), lane, "status", "--porcelain")
    say("F7b", "CONTROL", 0, f"git status on same repo runs it | marks={len(marks(log_f7))}")

    # F8: repo-local i18n.logOutputEncoding in the audited lane
    lane, fleet, _ = ctx.I18N
    git(ctx.fx.env(), lane, "config", "i18n.logOutputEncoding", "UTF-16LE")
    rc_i, out_i, err_i = audit(ctx.tool, lane, fleet, os.environ)
    say("F8", "CHANGED" if rc_i != 1 or out_i.strip() == "" else "ISOLATED", rc_i,
        f"audited repo i18n.logOutputEncoding=UTF-16LE | {cne(err_i)} | stdout={out_i[:30]!r}")

    # F9: repo-local log.showSignature + gpg.program in the audited FLEET repo
    lane, fleet, _ = build(ctx.fx, "fsig")
    fenv = ctx.fx.env()
    ftree = git(fenv, fleet, "rev-parse", "HEAD^{tree}")
    fbody = (f"tree {ftree}\nauthor kama-shokunin <a@x> 1200 +0000\n"
             "committer kama-shokunin <a@x> 1200 +0000\n"
             "gpgsig -----BEGIN PGP SIGNATURE-----\n \n AAAA\n -----END PGP SIGNATURE-----\n\n"
             "round-1: kama report\n").encode()
    fsig = git(fenv, fleet, "hash-object", "-t", "commit", "--literally", "-w", "--stdin",
               stdin=fbody)
    git(fenv, fleet, "update-ref", "refs/heads/master", fsig)
    log_f9 = ctx.work / "MARK-F9.log"
    gpg_f9 = script(ctx.work / "gpg-F9.sh", log_f9, 1)
    git(fenv, fleet, "config", "log.showSignature", "true")
    git(fenv, fleet, "config", "gpg.program", str(gpg_f9))
    rc_9, out_9, _ = audit(ctx.tool, lane, fleet, os.environ)
    say("F9", "EXEC" if marks(log_f9) else "NOT-EXEC", rc_9,
        f"audited FLEET repo's own config, signed root report commit | "
        f"marks={marks(log_f9)[:1]} | {digest(rc_9, out_9)}")


def group_u(ctx):
    lane, fleet, _ = ctx.UNI
    rc, out, err = audit(ctx.tool, lane, fleet, os.environ)
    crash = rc == 1 and "UnicodeDecodeError" in err
    say("U1", "EXIT1-VERDICT" if crash else "OTHER", rc,
        f"invalid-UTF-8 commit subject (raw object) | stdout={out[:12]!r} | "
        f"{[ln for ln in err.splitlines() if 'Error' in ln][-1:] or cne(err)}")
    prc, pout, _ = sh(["git", "-C", str(lane), "log", "--format=%s", "master"], env=ctx.fx.env())
    say("U1p", "CONTROL", prc, f"plain git log subject bytes: {pout.splitlines()[0][:60]!r}")


def make_mutant(ctx, name, old, new):
    assert ctx.src.count(old) == 1, (name, ctx.src.count(old))
    path = ctx.work / "mutants" / name / "tools" / "report-landing-audit.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(ctx.src.replace(old, new), encoding="utf-8")
    return path


def group_s(ctx):
    mut_a = make_mutant(ctx, "noStrip", OLD_FILTER, 'env = dict(os.environ)')
    rc, last, fails, tail = selftest(mut_a, os.environ)
    say("S-A", "CAUGHT" if not st_ok(rc, last, fails) else "MISSED", rc,
        f"mutant: no GIT_* stripping -> selftest | {last} | {tail}")

    mut_b = make_mutant(ctx, "stripGitDirOnly", OLD_FILTER,
                        'env = {k: v for k, v in os.environ.items() if k != "GIT_DIR"}')
    rc, last, fails, tail = selftest(mut_b, os.environ)
    say("S-B1", "MISSED" if st_ok(rc, last, fails) else "CAUGHT", rc,
        f"mutant: strip GIT_DIR only -> selftest | {last}")
    d_obj = str(ctx.decoy / "objects")
    rc, out, _ = audit(mut_b, ctx.FULL[0], ctx.FULL[1],
                       env_with(GIT_ALTERNATE_OBJECT_DIRECTORIES=d_obj))
    base_rc, base_out = base_of(ctx, ctx.FULL)
    changed = not (rc == base_rc and norm(out) == norm(base_out))
    say("S-B2", "CHANGED" if changed else "ISOLATED", rc,
        f"same mutant, CLI with GIT_ALTERNATE_OBJECT_DIRECTORIES | {digest(rc, out)}")

    mut_c = make_mutant(ctx, "noGlobalPin", OLD_SET, 'env.update(GIT_CONFIG_NOSYSTEM="1", **extra)')
    rc, last, fails, tail = selftest(mut_c, os.environ)
    say("S-C1", "MISSED" if st_ok(rc, last, fails) else "CAUGHT", rc,
        f"mutant: no GIT_CONFIG_GLOBAL pin -> selftest, host env | {last}")
    log_c, txt_c = evil_cfg(ctx.fx, "mutc")
    xdg_c = write_xdg(ctx.work / "xdg-mutc", "git/config", txt_c)
    rc, last, fails, tail = selftest(mut_c, env_with(XDG_CONFIG_HOME=str(xdg_c)))
    say("S-C2", "MISSED" if st_ok(rc, last, fails) and marks(log_c) else
        ("CAUGHT" if not st_ok(rc, last, fails) else "UNEXPECTED"), rc,
        f"mutant: no GIT_CONFIG_GLOBAL pin -> selftest under XDG evil | {last} | "
        f"leaked_marks={len(marks(log_c))}")

    mut_d = make_mutant(ctx, "noCommitOverride", OLD_OVERRIDE, '"commit"')
    log_d, txt_d = evil_cfg(ctx.fx, "mutd")
    xdg_d = write_xdg(ctx.work / "xdg-mutd", "git/config", txt_d)
    rc, last, fails, tail = selftest(mut_d, env_with(XDG_CONFIG_HOME=str(xdg_d)))
    say("S-D", "PIN-HOLDS" if st_ok(rc, last, fails) and not marks(log_d) else "LEAKS", rc,
        f"mutant: drop explicit commit.gpgsign=false override, XDG evil gpgsign | {last} | "
        f"marks={len(marks(log_d))}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", default=TOOL_DEFAULT)
    ap.add_argument("--work", default="")
    ap.add_argument("--out", default=str(HERE / "results.txt"))
    args = ap.parse_args()
    ctx = Ctx()
    ctx.tool = P(args.tool).resolve()
    ctx.src = ctx.tool.read_text(encoding="utf-8")
    if args.work:
        ctx.work = P(args.work)
    else:
        SCRATCH.mkdir(parents=True, exist_ok=True)
        ctx.work = P(tempfile.mkdtemp(prefix="c1env-", dir=SCRATCH))
    ctx.work.mkdir(parents=True, exist_ok=True)
    ctx.fx = Fx(ctx.work)
    git_v = sh(["git", "--version"])[1].strip()
    say("0", "INFO", 0, f"tool={ctx.tool} work={ctx.work} {git_v} python={sys.version.split()[0]}")
    ctx.decoy_x, ctx.decoy = build_decoy(ctx.fx)
    say("0b", "INFO", 0, f"decoy-only commit X={ctx.decoy_x} in {ctx.decoy}")
    ctx.B = build(ctx.fx, "base")
    ctx.FULL = build(ctx.fx, "full", variant="full", decoy_x=ctx.decoy_x)
    ctx.SH3 = build(ctx.fx, "shallow", shallow3=True)
    ctx.UNI = build(ctx.fx, "uni", raw_c2=b"round-1: measure \xff")
    ctx.SIG = build(ctx.fx, "signed")
    ctx.REPL = build(ctx.fx, "repl")
    ctx.ALT = build(ctx.fx, "alt", variant="full", decoy_x=ctx.decoy_x)
    ctx.HK = build(ctx.fx, "hooks")
    ctx.FSM = build(ctx.fx, "fsm")
    ctx.I18N = build(ctx.fx, "i18n")
    ctx.DISC = build(ctx.fx, "disc")
    ctx.SAFE = build(ctx.fx, "safe")
    rc, out = base_of(ctx, ctx.B)
    say("0c", "INFO", rc, f"baseline base fixture | {digest(rc, out)}")
    rc, out = base_of(ctx, ctx.FULL)
    say("0d", "INFO", rc, f"baseline full fixture | {digest(rc, out)}")
    groups = [("A", group_a), ("B", group_b), ("C", group_c), ("D", group_d),
              ("E", group_e), ("F", group_f), ("U", group_u), ("S", group_s)]
    for label, fn in groups:
        try:
            fn(ctx)
        except Exception as exc:  # record and keep going; never hide a probe
            say(f"{label}!", "ERROR", "-", f"{type(exc).__name__}: {str(exc)[:200]}")
    P(args.out).write_text("\n".join(LOG) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
