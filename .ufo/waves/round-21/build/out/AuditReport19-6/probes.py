#!/usr/bin/env python3
"""AuditReport19-6 evidence script (kama round 19, landing audit).

Read-only for the lane and the fleet. Three parts:
  1. derive: git-only derivation of round-19 landing facts (no tool use);
  2. tool: the audit tool's invocations on the real repos;
  3. probe: the committed report copied into scratch fleet repos under /tmp,
     mutated one property at a time, audited with the tool (--lane-repo is the
     real lane; scratch repos carry the committed first-add timestamp).
Usage: python3 probes.py [RESULTS_FILE]
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
TOOL = f"{LANE}/tools/report-landing-audit.py"
REL = ".ufo/reports/round-19/kama.md"
REPORT_ADD = "ac9859f4e74753ae2c14447c81b371760ea5b2b7"
SCRATCH = pathlib.Path("/tmp/kama-r21-AuditReport19-6")
LOG = []


def say(line=""):
    LOG.append(line)
    print(line)


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def tool(*args):
    p = subprocess.run(["python3", "-B", TOOL, *args], capture_output=True, text=True, cwd=LANE)
    return p.returncode, p.stdout, p.stderr


def describe(doc):
    r = next(x for x in doc["results"] if x["round"] == 19)
    s = doc["summary"]
    defects = [(d["kind"], d["token"][:40]) for d in r["defects"]]
    return (f"status={s['status']} errata_unmatched={s['errata_unmatched']} "
            f"committed={r['report_committed']} cutoff={r['cutoff']} required={r['required']} "
            f"post_report={len(r['post_report'])} round_commits={r['round_commits']} defects={defects}")


def derive():
    say("== 1. derive (git only) ==")
    rc, out, _ = git(FLEET, "log", "--diff-filter=A", "--format=%H %ct", "--", REL)
    add_sha, add_ct = out.split()
    say(f"fleet first-add of {REL}: {add_sha} ct={add_ct} (git rc={rc})")
    rc, out, _ = git(LANE, "log", "--format=%H%x09%an%x09%ct%x09%s", "master")
    mine = []
    for row in out.splitlines():
        h, an, ct, s = row.split("\t", 3)
        if an == "kama-shokunin" and re.match(r"(round-19:|checkpoint\(r19\))", s):
            mine.append((h, int(ct), s))
    rc, text, _ = git(FLEET, "show", f"{add_sha}:{REL}")
    lines = text.split("\n")
    a = next(i for i, l in enumerate(lines) if l.startswith("## Landed changes"))
    b = next(i for i, l in enumerate(lines) if i > a and l.startswith("## "))
    landed = "\n".join(lines[a + 1:b])
    say(f"lane master round-19 kama commits: {len(mine)}; Landed body = report lines {a + 2}-{b}")
    for h, ct, s in mine:
        side = "PRE " if ct <= int(add_ct) else "POST"
        say(f"  {side} {h[:12]} ct={ct} cited_in_landed(7-hex)={h[:7] in landed} | {s[:60]}")
    for tok in ("7229fa95eb122310e9e5334ad799ee3006293ebd", "24adc8ed372e85d4739ae290e5fde5a6a7ebc2e9",
                "5b108c1a", "84cf2f76", "f1790e25", "028235e6", "05f0f6c7", "30ed3783", "24adc8ed",
                "7229fa9", "7229fa95", "6c216313", "8bf99cae"):
        _, lane_hit, _ = git(LANE, "rev-parse", "--verify", "-q", tok + "^{commit}")
        _, fleet_hit, _ = git(FLEET, "rev-parse", "--verify", "-q", tok + "^{commit}")
        say(f"  token {tok:42s} lane={(lane_hit.strip() or '-')[:12]} fleet={(fleet_hit.strip() or '-')[:12]}")
    return add_sha, int(add_ct)


def tool_runs():
    say("== 2. tool on the real repos (read-only) ==")
    cases = [
        ["--rounds", "19", "--no-errata", "--json"],
        ["--rounds", "19", "--no-errata"],
        ["--rounds", "19", "--json"],
        ["--rounds", "19", "--no-errata", "--report", f"19={FLEET}/{REL}", "--json"],
        ["--no-errata"],
        [],
    ]
    for args in cases:
        rc, out, err = tool(*args)
        say(f"$ tools/report-landing-audit.py {' '.join(args)} -> exit={rc}")
        if "--json" in args:
            say("   " + describe(json.loads(out)))
        elif out.strip():
            for line in out.strip().split("\n"):
                say("   " + line)
        if err.strip():
            say("   stderr: " + err.strip()[:200])


def probes(add_ct):
    say("== 3. controlled probes (scratch fleets under /tmp; lane read-only) ==")
    rc, orig, err = git(FLEET, "show", f"{REPORT_ADD}:{REL}")
    assert rc == 0, err
    rc, tree, _ = git(LANE, "rev-parse", "master^{tree}")
    tree = tree.strip()

    def sub(text, old, new):
        assert text.count(old) == 1, (old, text.count(old))
        return text.replace(old, new)

    def fleet_repo(name, text):
        d = SCRATCH / name / "fleet"
        (d / REL).parent.mkdir(parents=True, exist_ok=True)
        (d / REL).write_text(text, encoding="utf-8")
        env = dict(os.environ, GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
                   GIT_AUTHOR_EMAIL="probe@local", GIT_COMMITTER_EMAIL="probe@local",
                   GIT_AUTHOR_DATE=f"@{add_ct} +0000", GIT_COMMITTER_DATE=f"@{add_ct} +0000")
        subprocess.run(["git", "-C", str(d), "init", "-q"], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(d), "add", REL], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(d), "commit", "-q", "-m", "round-19: kama report"],
                       check=True, capture_output=True, env=env)
        return str(d)

    def probe(name, text):
        rc, out, err = tool("--lane-repo", LANE, "--fleet-repo", fleet_repo(name, text),
                            "--rounds", "19", "--no-errata", "--json")
        say(f"[{name}] exit={rc}")
        say("   " + (describe(json.loads(out)) if out.strip() else "stderr: " + err.strip()[:200]))

    probe("P0_control_committed_text", orig)
    probe("P1_landed_heading_renamed", sub(orig, "## Landed changes", "## Landed"))
    probe("P2_landed_prefix_uppercase", sub(orig, "`5b108c1a…`", "`5B108C1A…`"))
    probe("P3_landed_decimal_token",
          sub(orig, "receipts and the wave advice.", "receipts and the wave advice 1792565257."))
    probe("P4_landed_cites_round18_commit",
          sub(orig, "receipts and the wave advice.",
              "receipts and the wave advice; 8bf99cae7de2517fd4ebe209f3b940aeabb6b687."))
    probe("P5_lane_tree_object_as_full_hash", orig + f"\nProbe tree object: {tree}\n")
    probe("P6_absent_lowercase_full_hash",
          orig + "\nProbe absent: 0123456789abcdef0123456789abcdef01234567\n")
    probe("P7_absent_uppercase_full_hash",
          orig + "\nProbe absent upper: ABCDEF0123456789ABCDEF0123456789ABCDEF01\n")
    probe("P8_landed_cites_post_report_commit",
          sub(orig, "receipts and the wave advice.",
              "receipts and the wave advice; 8d9191f53ca30bf3b92cf6b6120fd53322f33444."))
    probe("P9_landed_drops_028235e6",
          sub(sub(orig, "`028235e6…`, `05f0f6c7…`", "`05f0f6c7…`"),
              "commit for both claim commands: `028235e6…`", "commit for both claim commands: `05f0f6c7…`"))
    shutil.rmtree(SCRATCH, ignore_errors=True)
    say(f"[cleanup] scratch removed: {not SCRATCH.exists()}")


def main():
    add_sha, add_ct = derive()
    tool_runs()
    probes(add_ct)
    if len(sys.argv) > 1:
        pathlib.Path(sys.argv[1]).write_text("\n".join(LOG) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
