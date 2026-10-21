#!/usr/bin/env python3
"""AuditReport10 probe driver (read-only with respect to the lane and the fleet).

Runs tools/report-landing-audit.py on:
  1. the real round-10 report, no errata (official count);
  2. the same with the default errata ledger, round 10 only;
  3. six scratch drafts (`--report 10=PATH`, cutoff = now) that isolate the
     tool's blind spots and controls;
  4. a scratch fleet repo whose round-10 report is committed at the real bytes
     and then edited in the working tree only.
Scratch lives under /tmp/kama-r21-AuditReport10-6 and is removed at the end.
"""
import json
import os
import pathlib
import shutil
import subprocess

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = pathlib.Path("/home/vgpnk/Projects/shokunin")
TOOL = LANE / "tools/report-landing-audit.py"
OUT = LANE / ".ufo/waves/round-21/build/out/AuditReport10-6"
SCR = pathlib.Path("/tmp/kama-r21-AuditReport10-6")
REL = ".ufo/reports/round-10/kama.md"

PROBES = {
    "A-blob-fullhash.md": """# probe A: 40-hex token that resolves to a blob, outside Landed

## Work performed

Probe token (blob of LOG.md at 1e41928): 4d3823ac97db3987d613b1d700279bb670105094

## Landed changes

- `1e41928` and `4066035`.
""",
    "B-control-fake-fullhash.md": """# probe B: 40-hex token that resolves to no object (control)

## Work performed

Probe token: 0123456789abcdef0123456789abcdef01234567

## Landed changes

- `1e41928` and `4066035`.
""",
    "C-otherround-in-landed.md": """# probe C: Landed cites a round-9 commit as landed

## Landed changes

- `1e41928`, `4066035`, and `35e9175` (round-9 base, listed as landed).
""",
    "D-control-only-otherround.md": """# probe D: Landed cites only the round-9 commit (control)

## Landed changes

- `35e9175` (round-9 base, listed as landed).
""",
    "E-7hex-nonobject-outside-landed.md": """# probe E: 7-hex token that is no object, outside Landed

## Work performed

Lane commit: `1e41929` (one digit off 1e41928).

## Landed changes

- `1e41928` and `4066035`.
""",
    "F-control-7hex-nonobject-in-landed.md": """# probe F: 7-hex token that is no object, inside Landed (control)

## Landed changes

- `1e41929`, `1e41928` and `4066035`.
""",
}


def run(cmd, env=None):
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout, proc.stderr


def audit(extra, out_name):
    rc, out, err = run(["python3", str(TOOL), "--rounds", "10", "--no-errata",
                        "--json", *extra])
    (OUT / out_name).write_text(out, encoding="utf-8")
    if rc not in (0, 1):
        return rc, f"could-not-evaluate: {err.strip()}"
    doc = json.loads(out)
    return rc, [(d["kind"], d["token"]) for r in doc["results"]
                for d in r["defects"]]


def main():
    shutil.rmtree(SCR, ignore_errors=True)
    probe_dir = SCR / "probes"
    probe_dir.mkdir(parents=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "probes").mkdir(exist_ok=True)
    for name, text in PROBES.items():
        (probe_dir / name).write_text(text, encoding="utf-8")
        (OUT / "probes" / name).write_text(text, encoding="utf-8")

    print("== official: lane + committed fleet report, --rounds 10 --no-errata")
    print("exit, defects:", audit([], "official-rounds10-no-errata.json"))

    rc, out, _ = run(["python3", str(TOOL), "--rounds", "10"])
    (OUT / "official-rounds10-with-errata.txt").write_text(out, encoding="utf-8")
    print("== default errata ledger, --rounds 10: exit", rc)
    print(out.strip().splitlines()[-1])

    print("== probes: --report 10=<draft> (cutoff = now)")
    for name in PROBES:
        print(name, "->", audit(["--report", f"10={probe_dir / name}"],
                                f"probe-{name}.json"))

    print("== scratch fleet repo: report committed at real bytes, then edited in worktree")
    mini = SCR / "fleet-mini"
    mini.mkdir()
    src = (FLEET / REL).read_bytes()
    (mini / REL).parent.mkdir(parents=True)
    (mini / REL).write_bytes(src)
    env = dict(os.environ, GIT_AUTHOR_NAME="probe",
               GIT_AUTHOR_EMAIL="probe@example.invalid",
               GIT_COMMITTER_NAME="probe",
               GIT_COMMITTER_EMAIL="probe@example.invalid",
               GIT_AUTHOR_DATE="1792450135 +0000",
               GIT_COMMITTER_DATE="1792450135 +0000")
    for args in (["init", "-q"], ["add", "."],
                 ["commit", "-q", "-m", "scratch: round-10 report at committed bytes"]):
        rc, _, err = run(["git", "-C", str(mini), *args], env=env)
        assert rc == 0, (args, err)
    old = "All changes are in lane commit `1e41928`"
    text = src.decode("utf-8")
    assert text.count(old) == 1
    (mini / REL).write_bytes(text.replace(
        old, "All changes are in lane commits `1e41928` and `4066035`", 1
    ).encode("utf-8"))
    _, status, _ = run(["git", "-C", str(mini), "status", "--short"])
    print("worktree status:", repr(status.strip()))
    print("dirty worktree audit ->", audit(["--fleet-repo", str(mini)],
                                           "mini-dirty-worktree.json"))
    _, committed, _ = run(["git", "-C", str(mini), "show", f"HEAD:{REL}"])
    print("HEAD copy still has the omission (no 4066035 in Landed):",
          "lane commits `1e41928` and `4066035`" not in committed)
    (mini / REL).write_bytes(src)
    print("clean worktree audit ->", audit(["--fleet-repo", str(mini)],
                                           "mini-clean-worktree.json"))

    shutil.rmtree(SCR)
    print("scratch removed:", not SCR.exists())


if __name__ == "__main__":
    main()
