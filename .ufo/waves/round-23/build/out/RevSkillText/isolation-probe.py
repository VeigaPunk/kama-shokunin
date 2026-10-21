#!/usr/bin/env python3
"""RevSkillText probe set for tools/report-landing-audit.py (round 23, review seat).

Runs each repository-local channel against a candidate copy and the frozen base
blob (default 4fe9339f...), plus the end-to-end verdicts and CLI exit codes that
the SKILL/QUALITY drafts cite. Every fixture lives under one fresh temporary
directory that is removed on exit. Fixtures run with GIT_CONFIG_GLOBAL=/dev/null
and GIT_CONFIG_NOSYSTEM=1 and never touch the lane or fleet repositories; the
base blob is read with a read-only `git show`. The sshCommand fixture points at
a local marker script and its remote is ssh://example.invalid/; nothing connects.

Usage: python3 -B isolation-probe.py --candidate PATH [--lane-repo PATH]
                                     [--base-rev REV] [--out PATH]
Writes JSON (stdout when --out is absent). It records observations and grades
nothing; a reader compares base against candidate.
"""
import argparse
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import traceback

BASE_REV = "4fe9339f8fc3a4a4a479d9c938a850da12f1124d"
FIX_ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
FIX_ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
GPGSIG = ("gpgsig -----BEGIN PGP SIGNATURE-----\n \n fake-signature-line\n"
          " -----END PGP SIGNATURE-----\n")
REPORT_HASH = ("# kama round 10\n\n## Landed changes\n- none\n\n"
               "stray 0123456789abcdef0123456789abcdef01234567\n")
FAB = "abcdef0123456789abcdef0123456789abcdef01"


def sha256(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def script(path, body):
    path.write_text("#!/bin/sh\n" + body + "\n", encoding="utf-8")
    path.chmod(0o755)
    return str(path)


def try_call(fn, *args, **kwargs):
    try:
        return {"ok": True, "value": repr(fn(*args, **kwargs))[:300]}
    except Exception as exc:  # the exception class is the observation
        return {"ok": False, "exc": type(exc).__name__, "msg": str(exc)[:240]}


def authored(name, when):
    mail = f"{name}@example.invalid"
    return {"GIT_AUTHOR_NAME": name, "GIT_COMMITTER_NAME": name,
            "GIT_AUTHOR_EMAIL": mail, "GIT_COMMITTER_EMAIL": mail,
            "GIT_AUTHOR_DATE": f"@{when} +0000",
            "GIT_COMMITTER_DATE": f"@{when} +0000"}


class Ctx:
    def __init__(self, cand, base, root):
        self.cand, self.base, self.root = cand, base, root

    def git(self, repo, *args, iso=False, inp=None, extra_env=None):
        """iso=True: the candidate's own argv (GIT_ISOLATION + git_env)."""
        env = dict(self.cand.git_env()) if iso else dict(FIX_ENV)
        if extra_env:
            env.update(extra_env)
        isolation = list(self.cand.GIT_ISOLATION) if iso else []
        proc = subprocess.run(["git", *isolation, "-C", str(repo), *args],
                              input=inp, capture_output=True, env=env, timeout=120)
        return proc.returncode, proc.stdout, proc.stderr.decode("utf-8", "replace")


class Fixtures:
    def __init__(self, ctx):
        self.ctx = ctx

    def repo(self, name):
        path = self.ctx.root / name
        path.mkdir(parents=True)
        self.ctx.git(path, "init", "-q", "-b", "master")
        return path

    def commit(self, repo, msg, name="t", when=1700000000, files=None):
        for rel, content in (files or {}).items():
            target = repo / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")
        self.ctx.git(repo, "add", "-A")
        rc, _, err = self.ctx.git(repo, "-c", "commit.gpgsign=false", "commit", "-q",
                                  "--allow-empty", "-m", msg, extra_env=authored(name, when))
        assert rc == 0, err
        return self.ctx.git(repo, "rev-parse", "HEAD")[1].decode().strip()

    def raw_commit(self, repo, parent, msg_bytes, when, name="kama-shokunin", extra_headers=""):
        tree = self.ctx.git(repo, "rev-parse", "HEAD^{tree}")[1].decode().strip()
        head = (f"tree {tree}\n" + (f"parent {parent}\n" if parent else "")
                + f"author {name} <{name}@example.invalid> {when} +0000\n"
                + f"committer {name} <{name}@example.invalid> {when} +0000\n"
                + extra_headers + "\n")
        rc, out, err = self.ctx.git(repo, "hash-object", "-t", "commit", "-w", "--literally",
                                    "--stdin", inp=head.encode() + msg_bytes)
        assert rc == 0, err
        return out.decode().strip()

    def build_lane(self, name, msgs):
        lane = self.repo(name)
        shas = [self.commit(lane, msg, name="kama-shokunin", when=when,
                            files={"lane.txt": msg + "\n"}) for msg, when in msgs]
        return lane, shas

    def build_fleet(self, name, report, attrs=None, when=1700000200):
        fleet = self.repo(name)
        files = {".ufo/reports/round-10/kama.md": report}
        if attrs:
            files[".gitattributes"] = attrs
        self.commit(fleet, "fleet: round-10 report", name="fleet", when=when, files=files)
        return fleet


def e2e(mod, lane, fleet):
    args = argparse.Namespace(lane_repo=str(lane), fleet_repo=str(fleet), branch="master",
                              lane="kama", rounds="10", report=None, errata=None,
                              no_errata=True, json=True)
    try:
        status, doc = mod.run(args)
    except Exception as exc:
        return {"exc": type(exc).__name__, "msg": str(exc)[:200]}
    return {"status": status, "required": doc["summary"]["required_commits"],
            "defects": [[d["kind"], d["token"]] for res in doc["results"]
                        for d in res["defects"]]}


def cli(script_path, lane, fleet):
    proc = subprocess.run([sys.executable, "-B", str(script_path), "--lane-repo", str(lane),
                           "--fleet-repo", str(fleet), "--rounds", "10", "--no-errata"],
                          capture_output=True, text=True, timeout=300, env=FIX_ENV)
    return {"rc": proc.returncode,
            "stdout_last": proc.stdout.strip().splitlines()[-1:],
            "stderr_last": proc.stderr.strip().splitlines()[-1:]}


def channels(fx, ctx):
    out, root, cand, base = {}, ctx.root, ctx.cand, ctx.base

    # signature display: log.showSignature runs gpg.program
    r = fx.repo("ch-gpg")
    c1 = fx.commit(r, "round-10: first", name="kama-shokunin", when=1700000000, files={"a.txt": "a\n"})
    sig = fx.raw_commit(r, c1, b"round-10: signed fixture\n", 1700000100, extra_headers=GPGSIG)
    ctx.git(r, "update-ref", "refs/heads/signed", sig)
    marker = root / "gpg.marker"
    ctx.git(r, "config", "gpg.program", script(
        root / "gpg.sh", f'echo GPG_EXECUTED >> "{marker}"\necho "[GNUPG:] BADSIG fixture" >&2\nexit 1'))
    ctx.git(r, "config", "log.showSignature", "true")
    out["gpg"] = {}
    for label, iso in (("candidate", True), ("plain", False)):
        marker.unlink(missing_ok=True)
        rc, o, _ = ctx.git(r, "log", "--format=%H%x1f%an%x1f%at%x1f%s%x1e", "signed", iso=iso)
        out["gpg"][label] = {"rc": rc, "marker": marker.exists(),
                             "stdout_head": o[:90].decode("utf-8", "replace")}

    # refs/replace: a fabricated name resolves only through the replace ref
    r = fx.repo("ch-replace")
    c1 = fx.commit(r, "round-10: real", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    ctx.git(r, "update-ref", f"refs/replace/{FAB}", c1)
    out["replace"] = {"candidate_lookup": try_call(cand.lookup, (r,), [FAB]),
                      "base_lookup": try_call(base.lookup, (r,), [FAB]),
                      "plain_cat_file_t": ctx.git(r, "cat-file", "-t", FAB)[1].decode().strip()}

    # promisor remote: lazy fetch runs core.sshCommand on a missing object
    r = fx.repo("ch-lazy")
    fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    marker = root / "ssh.marker"
    ssh = script(root / "ssh.sh", f'echo SSH_EXECUTED >> "{marker}"\nexit 1')
    for key, value in (("core.repositoryformatversion", "1"), ("extensions.partialclone", "origin"),
                       ("remote.origin.url", "ssh://example.invalid/none.git"),
                       ("remote.origin.promisor", "true"),
                       ("remote.origin.partialclonefilter", "blob:none"),
                       ("core.sshCommand", ssh)):
        ctx.git(r, "config", key, value)
    marker.unlink(missing_ok=True)
    out["lazy"] = {"candidate_lookup": try_call(cand.lookup, (r,), [FAB]),
                   "candidate_marker": marker.exists()}
    marker.unlink(missing_ok=True)
    rc, o, _ = ctx.git(r, "cat-file", "--batch-check", inp=(FAB + "\n").encode())
    out["lazy"].update({"plain_batch_check_out": o.decode()[:60], "plain_marker": marker.exists()})

    # info/grafts and shallow: visible to log under the candidate argv too
    r = fx.repo("ch-history")
    c1 = fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "1\n"})
    c2 = fx.commit(r, "round-10: two", name="kama-shokunin", when=1700000100, files={"f": "2\n"})
    fx.commit(r, "round-10: three", name="kama-shokunin", when=1700000200, files={"f": "3\n"})

    def revs(iso):
        return ctx.git(r, "log", "--format=%H", "master", iso=iso)[1].decode().split()

    out["history"] = {"candidate_log": revs(True)}
    (r / ".git/info/grafts").write_text(c2 + "\n", encoding="utf-8")
    out["history"]["grafts_candidate_log"] = revs(True)
    out["history"]["grafts_plain_log"] = revs(False)
    out["history"]["grafts_candidate_refusal"] = try_call(cand.check_history_repo, r)
    (r / ".git/info/grafts").unlink()
    (r / ".git/shallow").write_text(c2 + "\n", encoding="utf-8")
    out["history"]["shallow_candidate_log"] = revs(True)
    out["history"]["shallow_candidate_refusal"] = try_call(cand.check_history_repo, r)
    (r / ".git/shallow").unlink()

    # objects/info/alternates: borrowed objects resolve (documented open limit O01)
    store = fx.repo("ch-alt-store")
    x = fx.commit(store, "round-99: only in store", name="kama-shokunin", when=1700000500,
                  files={"s": "s\n"})
    victim = fx.repo("ch-alt-victim")
    (victim / ".git/objects/info/alternates").write_text(
        str(store / ".git/objects") + "\n", encoding="utf-8")
    out["alternates"] = {"store_object": x,
                         "candidate_lookup": try_call(cand.lookup, (victim,), [x]),
                         "plain_cat_file_t": ctx.git(victim, "cat-file", "-t", x)[1].decode().strip(),
                         "candidate_check_history_repo": try_call(cand.check_history_repo, victim)}

    # gitfile redirect: a .git file pointing at another gitdir (open limit O02)
    real = fx.repo("ch-gitfile-real")
    gx = fx.commit(real, "round-99: gitfile target", name="kama-shokunin", when=1700000600,
                   files={"g": "g\n"})
    link = root / "ch-gitfile-link"
    link.mkdir()
    (link / ".git").write_text(f"gitdir: {real / '.git'}\n", encoding="utf-8")
    out["gitfile"] = {"candidate_lookup": try_call(cand.lookup, (link,), [gx]),
                      "candidate_check_history_repo": try_call(cand.check_history_repo, link)}

    # ref named like a citation token: git resolves the ref, the guard refuses
    r = fx.repo("ch-ref-named")
    c1 = fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    token = "abcdef12"
    ctx.git(r, "update-ref", f"refs/heads/{token}", c1)
    out["ref_named_citation"] = {"candidate_lookup": try_call(cand.lookup, (r,), [token]),
                                 "base_lookup": try_call(base.lookup, (r,), [token])}

    # .mailmap FIFO in the worktree: a plain log blocks reading it; log.mailmap=false does not
    r = fx.repo("ch-mailmap-fifo")
    fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    fifo = r / ".mailmap"
    os.mkfifo(fifo)
    out["mailmap_fifo"] = {}
    for label, iso in (("candidate", True), ("plain", False)):
        argv = ["git", *(list(cand.GIT_ISOLATION) if iso else []), "-C", str(r),
                "log", "--format=%H", "master"]
        env = dict(cand.git_env()) if iso else dict(FIX_ENV)
        try:
            proc = subprocess.run(argv, capture_output=True, env=env, timeout=5)
            out["mailmap_fifo"][label] = {"timed_out": False, "rc": proc.returncode}
        except subprocess.TimeoutExpired:
            out["mailmap_fifo"][label] = {"timed_out": True}
    fifo.unlink()

    # %an is the raw author name under both settings (mailmap does not rewrite it)
    r = fx.repo("ch-mailmap-an")
    fx.commit(r, "round-10: one", name="raw-name", when=1700000000,
              files={".mailmap": "Mapped Name <raw-name@example.invalid>\n", "f": "x\n"})
    out["mailmap_an"] = {
        "candidate_an_aN": ctx.git(r, "log", "--format=%an|%aN", "master", iso=True)[1].decode().strip(),
        "plain_log_mailmap_true": ctx.git(r, "-c", "log.mailmap=true", "log",
                                          "--format=%an|%aN", "master")[1].decode().strip()}

    # textconv: git show default vs --textconv (attribute and driver positive control)
    r = fx.repo("ch-textconv")
    fx.commit(r, "round-10: base", name="t", files={".gitattributes": "*.md diff=pwn\n",
                                                     "report.md": "# r\n"})
    marker = root / "tc.marker"
    ctx.git(r, "config", "diff.pwn.textconv", script(
        root / "tc.sh", f'echo EXECUTED >> "{marker}"\nprintf "CONVERTED\\n"'))
    out["textconv"] = {"check_attr": ctx.git(r, "check-attr", "diff", "--", "report.md")[1].decode().strip()}
    for label, args in (("default_show", ("show", "HEAD:report.md")),
                        ("show_textconv_flag", ("show", "--textconv", "HEAD:report.md"))):
        marker.unlink(missing_ok=True)
        rc, o, _ = ctx.git(r, *args, iso=True)
        out["textconv"][label] = {"marker": marker.exists(), "out": o.decode()[:30]}

    # core.fsmonitor: read commands used by the audit; status is the positive control
    r = fx.repo("ch-fsmonitor")
    c1 = fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    marker = root / "fsm.marker"
    ctx.git(r, "config", "core.fsmonitor", script(root / "fsm.sh",
                                                 f'echo FSM_EXECUTED >> "{marker}"\nexit 1'))
    probes = {
        "log": lambda: ctx.git(r, "log", "--format=%H", "master", iso=True),
        "show": lambda: ctx.git(r, "show", "HEAD:f", iso=True),
        "ls_tree": lambda: ctx.git(r, "ls-tree", "-r", "--name-only", "HEAD", iso=True),
        "rev_parse": lambda: ctx.git(r, "rev-parse", "--verify", "master^{commit}", iso=True),
        "cat_file_batch": lambda: ctx.git(r, "cat-file", "--batch-check", iso=True,
                                          inp=(c1 + "\n").encode()),
        "candidate_lookup": lambda: cand.lookup((r,), [c1]),
        "plain_status_positive_control": lambda: ctx.git(r, "status", "--porcelain"),
    }
    out["fsmonitor"] = {}
    for name, call in probes.items():
        marker.unlink(missing_ok=True)
        call()
        out["fsmonitor"][name] = marker.exists()

    # smudge filter: show/cat-file default; checkout is the positive control
    r = fx.repo("ch-filter")
    fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000,
              files={".gitattributes": "*.txt filter=smud\n", "a.txt": "clean\n"})
    marker = root / "smudge.marker"
    ctx.git(r, "config", "filter.smud.smudge", script(root / "smudge.sh",
                                                     f'echo SMUDGE_EXECUTED >> "{marker}"\ncat'))
    ctx.git(r, "config", "filter.smud.required", "false")
    out["filter"] = {}
    marker.unlink(missing_ok=True)
    ctx.git(r, "show", "HEAD:a.txt", iso=True)
    out["filter"]["candidate_show"] = marker.exists()
    marker.unlink(missing_ok=True)
    ctx.git(r, "cat-file", "blob", "HEAD:a.txt", iso=True)
    out["filter"]["candidate_cat_file"] = marker.exists()
    (r / "a.txt").unlink()
    marker.unlink(missing_ok=True)
    ctx.git(r, "checkout", "--", "a.txt")
    out["filter"]["plain_checkout_positive_control"] = marker.exists()

    # i18n.logOutputEncoding and an invalid UTF-8 subject
    r = fx.repo("ch-i18n")
    fx.commit(r, "round-10: caf\u00e9", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    ctx.git(r, "config", "i18n.logOutputEncoding", "ISO-8859-1")
    out["i18n"] = {"plain_subject_bytes": repr(ctx.git(r, "log", "--format=%s", "master")[1]),
                   "candidate_subject_bytes": repr(ctx.git(r, "log", "--format=%s", "master", iso=True)[1]),
                   "candidate_round_commits": try_call(cand.round_commits, r, "master", "kama", 10),
                   "base_round_commits": try_call(base.round_commits, r, "master", "kama", 10)}
    r = fx.repo("ch-utf8-subject")
    c1 = fx.commit(r, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    bad = fx.raw_commit(r, c1, b"round-10: caf\xe9 latin1 subject\n", 1700000300)
    ctx.git(r, "update-ref", "refs/heads/master", bad)
    out["invalid_utf8_subject"] = {
        "candidate_round_commits": try_call(cand.round_commits, r, "master", "kama", 10),
        "candidate_strict_git_log": try_call(cand.git, r, "log", "--format=%s", "master"),
        "base_round_commits": try_call(base.round_commits, r, "master", "kama", 10)}
    return out


def refusals(fx, ctx):
    out, root, cand = {}, ctx.root, ctx.cand
    sha = root / "refusal-sha256"
    subprocess.run(["git", "init", "-q", "--object-format=sha256", str(sha)],
                   env=FIX_ENV, check=True, capture_output=True)
    out["sha256_repo"] = try_call(cand.check_history_repo, sha)
    promisor = fx.repo("refusal-promisor-config")
    ctx.git(promisor, "config", "extensions.partialclone", "origin")
    out["promisor_config_repo"] = try_call(cand.check_history_repo, promisor)
    pack = fx.repo("refusal-promisor-pack")
    fx.commit(pack, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    (pack / ".git/objects/pack").mkdir(parents=True, exist_ok=True)
    (pack / ".git/objects/pack/pack-fixture.promisor").write_text("", encoding="utf-8")
    out["promisor_pack_file"] = try_call(cand.check_history_repo, pack)
    sub = fx.repo("refusal-subdir")
    fx.commit(sub, "round-10: one", name="kama-shokunin", when=1700000000, files={"f": "x\n"})
    (sub / "sub").mkdir()
    out["subdirectory_argument"] = try_call(cand.check_history_repo, sub / "sub")
    out["toplevel_argument"] = try_call(cand.check_history_repo, sub)
    return out


def scenarios(fx, ctx, cand_path, base_path):
    out, root, cand, base = {}, ctx.root, ctx.cand, ctx.base

    # S1: textconv driver on the fleet report read by the default `git show`
    lane, _ = fx.build_lane("s1-lane", [("round-10: lane one", 1700000000)])
    plain = fx.build_fleet("s1-plain", REPORT_HASH)
    driven = fx.build_fleet("s1-driven", REPORT_HASH, attrs="*.md diff=pwn\n")
    marker = root / "s1.marker"
    ctx.git(driven, "config", "diff.pwn.textconv", script(
        root / "s1.sh", f'echo EXECUTED >> "{marker}"\nprintf "## Landed changes\\n- none\\n"'))
    out["S1_textconv"] = {"base_plain": e2e(base, lane, plain),
                          "candidate_plain": e2e(cand, lane, plain)}
    marker.unlink(missing_ok=True)
    out["S1_textconv"]["base_driven"] = e2e(base, lane, driven)
    out["S1_textconv"]["base_marker"] = marker.exists()
    marker.unlink(missing_ok=True)
    out["S1_textconv"]["candidate_driven"] = e2e(cand, lane, driven)
    out["S1_textconv"]["candidate_marker"] = marker.exists()

    # S2: grafts / shallow hide an omitted round commit
    lane, (c1, c2) = fx.build_lane("s2-lane", [("round-10: first", 1700000000),
                                               ("round-10: second", 1700000100)])
    fleet = fx.build_fleet("s2-fleet", "## Landed changes\n- `%s` round-10: second\n" % c2[:9])
    out["S2_history"] = {"baseline": {"base": e2e(base, lane, fleet),
                                      "candidate": e2e(cand, lane, fleet)}}
    (lane / ".git/info/grafts").write_text(c2 + "\n", encoding="utf-8")
    out["S2_history"]["grafts"] = {"base": e2e(base, lane, fleet),
                                   "candidate": e2e(cand, lane, fleet),
                                   "base_cli": cli(base_path, lane, fleet),
                                   "candidate_cli": cli(cand_path, lane, fleet)}
    (lane / ".git/info/grafts").unlink()
    (lane / ".git/shallow").write_text(c2 + "\n", encoding="utf-8")
    out["S2_history"]["shallow"] = {"base": e2e(base, lane, fleet),
                                    "candidate": e2e(cand, lane, fleet)}
    (lane / ".git/shallow").unlink()

    # S3: signed round commit on the lane with a repo-local gpg.program
    lane, (c1,) = fx.build_lane("s3-lane", [("round-10: first", 1700000000)])
    sig = fx.raw_commit(lane, c1, b"round-10: signed\n", 1700000100, extra_headers=GPGSIG)
    ctx.git(lane, "update-ref", "refs/heads/master", sig)
    fleet = fx.build_fleet("s3-fleet", "## Landed changes\n- none\n")
    marker = root / "s3.marker"
    ctx.git(lane, "config", "gpg.program", script(
        root / "s3.sh", f'echo GPG_EXECUTED >> "{marker}"\necho "[GNUPG:] BADSIG fixture" >&2\nexit 1'))
    ctx.git(lane, "config", "log.showSignature", "true")
    marker.unlink(missing_ok=True)
    out["S3_signature"] = {"base": e2e(base, lane, fleet), "base_marker": marker.exists()}
    marker.unlink(missing_ok=True)
    out["S3_signature"]["candidate"] = e2e(cand, lane, fleet)
    out["S3_signature"]["candidate_marker"] = marker.exists()

    # S4: repo-local log.showRoot=false hides a root-commit report add
    lane, (c1,) = fx.build_lane("s4-lane", [("round-10: first", 1700000000)])
    fleet = fx.build_fleet("s4-fleet", "## Landed changes\n- `%s` round-10: first\n" % c1[:9])
    ctx.git(fleet, "config", "log.showRoot", "false")
    out["S4_showRoot"] = {"base": e2e(base, lane, fleet), "candidate": e2e(cand, lane, fleet),
                          "base_cli": cli(base_path, lane, fleet),
                          "candidate_cli": cli(cand_path, lane, fleet)}

    # S5: rename of the report into kama.md; repo-local log.follow=true
    lane, _ = fx.build_lane("s5-lane", [("round-10: mid", 1700000150)])
    fleet = fx.repo("s5-fleet")
    fx.commit(fleet, "fleet: old path", name="fleet", when=1700000100,
              files={".ufo/reports/round-10/old.md": "## Landed changes\n- none\n"})
    ctx.git(fleet, "mv", ".ufo/reports/round-10/old.md", ".ufo/reports/round-10/kama.md")
    fx.commit(fleet, "fleet: rename to kama.md", name="fleet", when=1700000200, files={})
    out["S5_follow"] = {"no_config": {"base": e2e(base, lane, fleet),
                                      "candidate": e2e(cand, lane, fleet)}}
    ctx.git(fleet, "config", "log.follow", "true")
    out["S5_follow"]["log_follow_true"] = {"base": e2e(base, lane, fleet),
                                           "candidate": e2e(cand, lane, fleet)}

    # S6: include.path supplies log.showRoot=false; a pinned -c must win
    lane, (c1,) = fx.build_lane("s6-lane", [("round-10: first", 1700000000)])
    fleet = fx.build_fleet("s6-fleet", "## Landed changes\n- `%s` round-10: first\n" % c1[:9])
    inc = root / "s6-include.cfg"
    inc.write_text("[log]\n\tshowRoot = false\n", encoding="utf-8")
    ctx.git(fleet, "config", "include.path", str(inc))
    out["S6_include"] = {"base": e2e(base, lane, fleet), "candidate": e2e(cand, lane, fleet)}

    # S7: undecodable bytes in the committed fleet report
    lane, (c1,) = fx.build_lane("s7-lane", [("round-10: first", 1700000000)])
    fleet = fx.build_fleet("s7-fleet", b"## Landed changes\n- `" + c1[:9].encode()
                           + b"` round-10: first \xff\n")
    out["S7_undecodable_report"] = {"base": e2e(base, lane, fleet),
                                    "candidate": e2e(cand, lane, fleet),
                                    "base_cli": cli(base_path, lane, fleet),
                                    "candidate_cli": cli(cand_path, lane, fleet)}

    # S8: a tag named like the branch; plain `--branch master` must mean refs/heads/master
    lane, (a,) = fx.build_lane("s8-lane", [("round-10: real", 1700000000)])
    b = fx.commit(lane, "round-10: tag-target", name="kama-shokunin", when=1700000050,
                  files={"lane.txt": "other\n"})
    ctx.git(lane, "reset", "-q", "--hard", a)
    ctx.git(lane, "update-ref", "refs/tags/master", b)
    fleet = fx.build_fleet("s8-fleet", "## Landed changes\n- `%s` round-10: real\n" % a[:9])
    out["S8_tag_named_master"] = {"base": e2e(base, lane, fleet),
                                  "candidate": e2e(cand, lane, fleet),
                                  "candidate_resolve_branch": try_call(cand.resolve_branch, lane, "master")}
    return out


def selftest(script_path, cwd):
    proc = subprocess.run([sys.executable, "-B", str(script_path), "--selftest"],
                          capture_output=True, text=True, timeout=900, cwd=str(cwd))
    lines = proc.stdout.strip().splitlines()
    return {"rc": proc.returncode,
            "ok_lines": sum(1 for line in lines if line.startswith("ok ")),
            "fail_lines": [line for line in lines if line.startswith("FAIL")][:20],
            "summary": [line for line in lines if line.startswith("selftest")]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--lane-repo", default=str(pathlib.Path(__file__).resolve().parents[6]))
    ap.add_argument("--base-rev", default=BASE_REV)
    ap.add_argument("--out")
    args = ap.parse_args(argv)
    root = pathlib.Path(tempfile.mkdtemp(prefix="revskilltext-probe-"))
    try:
        cand_path = root / "candidate-report-landing-audit.py"
        shutil.copyfile(args.candidate, cand_path)
        base_path = root / "base-report-landing-audit.py"
        with open(base_path, "wb") as fh:
            subprocess.run(["git", "--no-optional-locks", "-C", args.lane_repo, "show",
                            f"{args.base_rev}:tools/report-landing-audit.py"], stdout=fh, check=True)
        sys.dont_write_bytecode = True
        cand = load("rla_candidate", cand_path)
        base = load("rla_base", base_path)
        ctx = Ctx(cand, base, root)
        fx = Fixtures(ctx)
        result = {
            "candidate": {"source": args.candidate, "sha256": sha256(cand_path)},
            "base": {"rev": args.base_rev, "sha256": sha256(base_path)},
            "git": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(),
            "git_isolation": list(cand.GIT_ISOLATION),
        }
        for name, fn in (("channels", lambda: channels(fx, ctx)),
                         ("refusals", lambda: refusals(fx, ctx)),
                         ("scenarios", lambda: scenarios(fx, ctx, cand_path, base_path))):
            try:
                result[name] = fn()
            except Exception as exc:
                result[name] = {"probe_exception": f"{type(exc).__name__}: {exc}",
                                "tb": traceback.format_exc()[-600:]}
        result["selftest_candidate"] = selftest(cand_path, root)
        result["selftest_base"] = selftest(base_path, root)
        text = json.dumps(result, indent=1, sort_keys=True)
        if args.out:
            pathlib.Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(text)
        return 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
