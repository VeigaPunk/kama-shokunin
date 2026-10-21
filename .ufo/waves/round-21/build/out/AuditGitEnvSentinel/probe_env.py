#!/usr/bin/env python3
"""AuditGitEnvSentinel probe for tools/report-landing-audit.py (kama round 21).

Throwaway fixtures only: every repo is created under SCRATCH/exp-LABEL.
Refuses any path under the real fleet root (which contains the real lane).
The real round-20 report is read, never written.

usage: probe_env.py TOOL.py SCRATCH LABEL
  SCRATCH/lane must be a throwaway clone of the lane (created by the caller).
Prints one JSON object on stdout and writes SCRATCH/exp-LABEL/results.json.
"""
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

FLEET = pathlib.Path("/home/vgpnk/Projects/shokunin").resolve()
TOOL = pathlib.Path(sys.argv[1]).resolve()
SCRATCH = pathlib.Path(sys.argv[2]).resolve()
LABEL = sys.argv[3]
for _p in (TOOL, SCRATCH):
    if _p == FLEET or FLEET in _p.parents:
        sys.exit(f"refusing non-throwaway path: {_p}")

PY = sys.executable
LANE = SCRATCH / "lane"
EXP = SCRATCH / f"exp-{LABEL}"
shutil.rmtree(EXP, ignore_errors=True)
EXP.mkdir(parents=True)
OMIT = "33a6777866d0f63d894ef21bc863486bcb35b56c"  # landed-omitted in the real r20 report
PWN = EXP / "PWN"
REAL_TEXT = (FLEET / ".ufo/reports/round-20/kama.md").read_text(encoding="utf-8")
REAL_GLOBAL = (pathlib.Path.home() / ".config/git/config").read_text(encoding="utf-8")
HERM = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
HERM.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
BASE = dict(os.environ)
RESULTS, AUDITS = {}, {}
PROSE = ["- `deadbee1` (ref-name shadow probe)", "- defaced cache note"]
PAYLOAD = [f"- `$(touch {PWN}_bt)` ; touch {PWN}_semi && echo $(touch {PWN}_sub)",
           f"- $(echo {OMIT})"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "<absent>"


def gd_out(gd, *args):
    p = subprocess.run(["git", f"--git-dir={gd}", *args], env=HERM,
                       capture_output=True, text=True, timeout=120)
    return p.stdout.strip() if p.returncode == 0 else f"<rc{p.returncode}>"


def snap(repo):
    gd = repo / ".git"
    worktree = sorted(str(p.relative_to(repo)) for p in repo.rglob("*")
                      if p.is_file() and ".git" not in p.relative_to(repo).parts)
    return {"HEAD": gd_out(gd, "rev-parse", "HEAD"),
            "refs": gd_out(gd, "for-each-ref", "--format=%(refname) %(objectname)"),
            "log": gd_out(gd, "log", "--all", "--format=%h %an %s"),
            "index_sha256": sha(gd / "index"),
            "config_sha256": sha(gd / "config"),
            "loose_objects": len(list((gd / "objects").glob("??/*"))),
            "worktree": worktree}


def diff(before, after):
    keys = [k for k in after if after[k] != before[k]]
    out = {"changed": keys}
    if "log" in keys:
        old = set(before["log"].splitlines())
        out["new_commits"] = [x for x in after["log"].splitlines() if x not in old]
    if "refs" in keys:
        out["refs_after"] = after["refs"]
    if "loose_objects" in keys:
        out["loose_objects_delta"] = after["loose_objects"] - before["loose_objects"]
    if "worktree" in keys:
        out["worktree_added"] = sorted(set(after["worktree"]) - set(before["worktree"]))
    return out


def make_repo(path, commits):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "master", str(path)], env=HERM, check=True)
    for rel, text, msg, author in commits:
        target = path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(text + "\n")
        subprocess.run(["git", "-C", str(path), "add", rel], env=HERM, check=True)
        subprocess.run(["git", "-C", str(path), "-c", f"user.name={author}",
                        "-c", f"user.email={author}@x", "commit", "-q", "-m", msg],
                       env=HERM, check=True)
    return path


def make_victim(tag):
    return make_repo(EXP / f"victim-{tag}", [
        ("README", "victim base", "victim base", "victim-owner"),
        ("README", "victim second", "victim second", "victim-owner")])


def make_fleet(tag, text):
    path = EXP / f"fleet-{tag}"
    report = path / ".ufo/reports/round-20/kama.md"
    report.parent.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "master", str(path)], env=HERM, check=True)
    report.write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(path), "add", ".ufo/reports/round-20/kama.md"], env=HERM, check=True)
    subprocess.run(["git", "-C", str(path), "-c", "user.name=kama-shokunin", "-c", "user.email=k@x",
                    "commit", "-q", "-m", "round-20: kama report"], env=HERM, check=True)
    return path


def insert_after_landed(text, lines):
    out, done = [], False
    for line in text.splitlines(keepends=True):
        out.append(line)
        if not done and line.startswith("## Landed changes"):
            out.extend(item + "\n" for item in lines)
            done = True
    if not done:
        sys.exit("real report has no Landed section")
    return "".join(out)


def errata_file(tag, rows):
    path = EXP / f"errata-{tag}.tsv"
    path.write_text("".join("\t".join(row) + "\n" for row in rows), encoding="utf-8")
    return path


def selftest(env, cwd, argv=None):
    argv = argv or [PY, str(TOOL), "--selftest"]
    p = subprocess.run(argv, env=env, cwd=cwd, capture_output=True, text=True, timeout=900)
    text = p.stdout + p.stderr
    lines = text.strip().splitlines()
    return {"rc": p.returncode,
            "summary": next((l for l in lines if l.startswith("selftest cases=")), None),
            "FAIL": [l for l in lines if l.startswith("FAIL ")],
            "traceback_last": lines[-1] if ("Traceback (most recent call last)" in text and lines) else None,
            "tail": lines[-2:]}


def env_delta(env):
    return {k: v for k, v in sorted(env.items()) if BASE.get(k) != v}


def selftest_case(name, desc, env, repo=None, argv=None, cwd=None, marker=None):
    cwd = cwd or EXP / f"cwd-{name}"
    cwd.mkdir(parents=True, exist_ok=True)
    before = snap(repo) if repo else None
    rec = {"desc": desc, "env_delta": env_delta(env), **selftest(env, cwd, argv)}
    if argv:
        rec["argv"] = argv
    if repo:
        rec["victim"] = diff(before, snap(repo))
    if marker:
        rec["marker_lines"] = len(marker.read_text().splitlines()) if marker.exists() else 0
    RESULTS[name] = rec


def audit(env, args, cwd):
    p = subprocess.run([PY, str(TOOL), *args], env=env, cwd=cwd, capture_output=True,
                       text=True, timeout=900)
    rec = {"args": args, "rc": p.returncode, "stderr_last": p.stderr.strip().splitlines()[-1:],
           "stdout_has_ESC": "\x1b" in p.stdout}
    try:
        doc = json.loads(p.stdout)
    except ValueError:
        rec["stdout_tail"] = p.stdout.strip().splitlines()[-12:]
        rec["unmatched_lines_repr"] = [repr(l) for l in p.stdout.splitlines()
                                       if l.startswith("errata-unmatched")]
        return rec
    rec["summary"] = doc["summary"]
    rec["results"] = [{"round": r["round"], "required": r["required"],
                       "round_commits": r["round_commits"],
                       "defects": [[d["kind"], d["token"], bool(d["corrected_by"])] for d in r["defects"]]}
                      for r in doc["results"]]
    rec["errata_unmatched"] = [e["token"] for e in doc["errata_unmatched"]]
    rec["errata_invalid"] = [e["correction"] for e in doc["errata_invalid"]]
    return rec


def main():
    cfg = EXP / "cfg"
    cfg.mkdir()
    hooks = EXP / "hooks-core"
    hooks.mkdir()
    marker_hook = EXP / "marker-E5.txt"
    (hooks / "post-commit").write_text(f"#!/bin/sh\necho ran >> {marker_hook}\n", encoding="utf-8")
    (hooks / "post-commit").chmod(0o755)
    cfg_hooks = cfg / "core-hookspath.gitconfig"
    cfg_hooks.write_text(REAL_GLOBAL + f"\n[core]\n\thooksPath = {hooks}\n", encoding="utf-8")
    tpl = EXP / "tpl"
    (tpl / "hooks").mkdir(parents=True)
    (tpl / "hooks" / "pre-commit").write_text("#!/bin/sh\necho blocked-by-template >&2\nexit 1\n",
                                              encoding="utf-8")
    (tpl / "hooks" / "pre-commit").chmod(0o755)
    cfg_tpl = cfg / "init-templatedir.gitconfig"
    cfg_tpl.write_text(REAL_GLOBAL + f"\n[init]\n\ttemplateDir = {tpl}\n", encoding="utf-8")
    cfg_gpg = cfg / "commit-gpgsign.gitconfig"
    cfg_gpg.write_text(REAL_GLOBAL + "\n[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /bin/false\n",
                       encoding="utf-8")

    tags = ["E0", "E1", "E1b", "E2", "E2b", "E3", "E3b", "E4", "E5", "E5b", "E6", "E6b",
            "E7", "E8", "E9", "E10", "A1"]
    V = {t: make_victim(t) for t in tags}

    selftest_case("E0_control_clean_env", "no injection; victim is control", dict(BASE), V["E0"])
    selftest_case("E1_GIT_DIR", "GIT_DIR=victim/.git",
                  {**BASE, "GIT_DIR": str(V["E1"] / ".git")}, V["E1"])
    selftest_case("E1b_GIT_DIR_plus_GIT_WORK_TREE", "GIT_DIR=victim/.git GIT_WORK_TREE=victim",
                  {**BASE, "GIT_DIR": str(V["E1b"] / ".git"), "GIT_WORK_TREE": str(V["E1b"])}, V["E1b"])
    selftest_case("E2_GIT_INDEX_FILE_absolute", "GIT_INDEX_FILE=victim/.git/index",
                  {**BASE, "GIT_INDEX_FILE": str(V["E2"] / ".git" / "index")}, V["E2"])
    selftest_case("E2b_GIT_INDEX_FILE_relative_hook_style",
                  "GIT_INDEX_FILE=.git/index with cwd=victim (form git exports to hooks)",
                  {**BASE, "GIT_INDEX_FILE": ".git/index"}, V["E2b"], cwd=V["E2b"])
    selftest_case("E3_GIT_OBJECT_DIRECTORY", "GIT_OBJECT_DIRECTORY=victim/.git/objects",
                  {**BASE, "GIT_OBJECT_DIRECTORY": str(V["E3"] / ".git" / "objects")}, V["E3"])
    selftest_case("E3b_GIT_COMMON_DIR", "GIT_COMMON_DIR=victim/.git",
                  {**BASE, "GIT_COMMON_DIR": str(V["E3b"] / ".git")}, V["E3b"])
    selftest_case("E4_GIT_WORK_TREE_only", "GIT_WORK_TREE=victim (no GIT_DIR)",
                  {**BASE, "GIT_WORK_TREE": str(V["E4"])}, V["E4"])
    selftest_case("E5_global_core_hooksPath",
                  "copy of real global config + core.hooksPath with post-commit marker",
                  {**BASE, "GIT_CONFIG_GLOBAL": str(cfg_hooks)}, V["E5"], marker=marker_hook)
    selftest_case("E5b_global_init_templateDir",
                  "copy of real global config + init.templateDir with pre-commit exit 1",
                  {**BASE, "GIT_CONFIG_GLOBAL": str(cfg_tpl)}, V["E5b"])
    selftest_case("E6_global_commit_gpgsign",
                  "copy of real global config + commit.gpgsign=true, gpg.program=/bin/false",
                  {**BASE, "GIT_CONFIG_GLOBAL": str(cfg_gpg)}, V["E6"])
    selftest_case("E6b_env_GIT_CONFIG_COUNT_gpgsign", "same two pins via GIT_CONFIG_COUNT env",
                  {**BASE, "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "commit.gpgsign",
                   "GIT_CONFIG_VALUE_0": "true", "GIT_CONFIG_KEY_1": "gpg.program",
                   "GIT_CONFIG_VALUE_1": "/bin/false"}, V["E6b"])
    selftest_case("E7_env_GIT_TEMPLATE_DIR", "GIT_TEMPLATE_DIR with pre-commit exit 1",
                  {**BASE, "GIT_TEMPLATE_DIR": str(tpl)}, V["E7"])
    selftest_case("E8_outer_git_c_then_alias",
                  "outer: git -c commit.gpgsign=true -c gpg.program=/bin/false -c alias.sentinel=!tool --selftest",
                  dict(BASE), V["E8"],
                  argv=["git", "-c", "commit.gpgsign=true", "-c", "gpg.program=/bin/false",
                        "-c", f"alias.sentinel=!{PY} {TOOL} --selftest", "sentinel"])
    selftest_case("E9_GIT_DEFAULT_HASH_sha256", "GIT_DEFAULT_HASH=sha256 (selftest assumes 40-hex)",
                  {**BASE, "GIT_DEFAULT_HASH": "sha256"}, V["E9"])
    selftest_case("E10_PATH_without_git", "PATH=/nonexistent", {**BASE, "PATH": "/nonexistent"}, V["E10"])

    fleet_plain = make_fleet("plain", REAL_TEXT)
    fleet_prose = make_fleet("prose", insert_after_landed(REAL_TEXT, PROSE))
    fleet_pay = make_fleet("payload", insert_after_landed(REAL_TEXT, PAYLOAD))
    lane_shadow = EXP / "lane-shadow"
    shutil.copytree(LANE, lane_shadow, symlinks=True)
    subprocess.run(["git", "-C", str(lane_shadow), "branch", "deadbee1", "HEAD"], env=HERM, check=True)

    cwd_a = EXP / "cwd-audit"
    cwd_a.mkdir()
    base = ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_plain), "--rounds", "20",
            "--no-errata", "--json"]
    AUDITS["A0_clean_baseline"] = audit(dict(BASE), base, cwd_a)
    AUDITS["A1_GIT_DIR_victim"] = audit({**BASE, "GIT_DIR": str(V["A1"] / ".git")}, base, cwd_a)
    AUDITS["A2_prose_lane_clean"] = audit(
        dict(BASE), ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_prose), "--rounds", "20",
                     "--no-errata", "--json"], cwd_a)
    AUDITS["A3_prose_lane_with_branch_deadbee1"] = audit(
        dict(BASE), ["--lane-repo", str(lane_shadow), "--fleet-repo", str(fleet_prose), "--rounds", "20",
                     "--no-errata", "--json"], cwd_a)
    AUDITS["A4_PATH_without_git_audit"] = audit({**BASE, "PATH": "/nonexistent"}, base, cwd_a)
    esc = errata_file("esc", [["20", "landed-omitted", "\x1b[31mESC", OMIT, "ev"]])
    AUDITS["A5_errata_ESC_in_token_text_mode"] = audit(
        dict(BASE), ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_plain), "--rounds", "20",
                     "--errata", str(esc)], cwd_a)
    pwn_err = EXP / "PWN_errata"
    esc_pay = errata_file("payload", [["20", "landed-omitted", OMIT, f"$(touch {pwn_err})", "ev"]])
    AUDITS["A6_errata_correction_shell_payload"] = audit(
        dict(BASE), ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_plain), "--rounds", "20",
                     "--errata", str(esc_pay), "--json"], cwd_a)
    esc_rev = errata_file("mutable", [["20", "landed-omitted", OMIT, "HEAD~1", "ev"]])
    AUDITS["A7_errata_correction_HEAD_minus_1"] = audit(
        dict(BASE), ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_plain), "--rounds", "20",
                     "--errata", str(esc_rev), "--json"], cwd_a)
    AUDITS["A8_report_shell_payload"] = audit(
        dict(BASE), ["--lane-repo", str(LANE), "--fleet-repo", str(fleet_pay), "--rounds", "20",
                     "--no-errata", "--json"], cwd_a)

    before = {"lane": snap(LANE), "fleet_plain": snap(fleet_plain)}
    selftest_case("A9_clean_selftest_repeat", "clean env again; checks repos are not written", dict(BASE))
    AUDITS["A10_clean_audit_repeat"] = audit(dict(BASE), base, cwd_a)
    after = {"lane": snap(LANE), "fleet_plain": snap(fleet_plain)}
    no_mutation = {k: diff(before[k], after[k]) for k in before}

    out = {"label": LABEL, "tool": str(TOOL), "tool_sha256": sha(TOOL),
           "git_version": subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip(),
           "harness_GIT_env_keys": sorted(k for k in BASE if k.startswith("GIT_")),
           "selftests": RESULTS, "audits": AUDITS,
           "PWN_files_created": sorted(p.name for p in EXP.glob("PWN*")),
           "no_mutation_clean_runs": no_mutation}
    text = json.dumps(out, indent=1, sort_keys=True)
    (EXP / "results.json").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
