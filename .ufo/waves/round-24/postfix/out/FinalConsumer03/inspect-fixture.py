#!/usr/bin/env python3
"""Independent reconstruction of the replay-v3 `fleet-only-tag` fixture.

Mirrors proof-driver-replay-v3.py scenario('fleet-only-tag') but KEEPS the
fixture on disk so the actual Git object types/presence can be inspected, and
so the after/before tools can be run directly on it (raw JSON, not the
driver's summarised row).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ENV = {"GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "kama-shokunin", "GIT_COMMITTER_NAME": "kama-shokunin",
       "GIT_AUTHOR_EMAIL": "a@x", "GIT_COMMITTER_EMAIL": "a@x",
       "PATH": "/usr/bin:/bin"}


def git(repo, *args, stdin=None):
    out = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                          "-C", str(repo), *args],
                         input=None if stdin is None else stdin.encode(),
                         capture_output=True, env=ENV, timeout=30)
    if out.returncode != 0:
        raise SystemExit(f"git {args} in {repo}: {out.stderr.decode()}")
    return out.stdout.decode("utf-8", "replace")


def build(root):
    lane, fleet = Path(root, "lane"), Path(root, "fleet")
    for repo in (lane, fleet):
        repo.mkdir(parents=True)
        git(repo, "init", "-q", "-b", "master")
    Path(lane, "f").write_text("work\n", encoding="utf-8")
    git(lane, "add", "f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work")
    a = git(lane, "rev-parse", "HEAD").strip()
    report = fleet / ".ufo/reports/round-1/kama.md"
    report.parent.mkdir(parents=True)
    report.write_text("## Landed changes\n", encoding="utf-8")
    git(fleet, "add", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: kama report")
    # fleet-only TAG object (the consumer under test)
    target = git(fleet, "hash-object", "-w", "--stdin",
                 stdin="fleet tag target\n").strip()
    tag = git(fleet, "mktag", stdin=f"object {target}\ntype blob\ntag t\n"
                                    f"tagger k <a@x> 1000 +0000\n\ntag\n").strip()
    draft = Path(root, "draft.md")
    draft.write_text("## Landed changes\n- `" + a + "` work\n- `" + tag
                     + "` under test\n", encoding="utf-8")
    return lane, fleet, draft, a, target, tag


def probe(repo, oid):
    """Actual object type / presence / content for one OID in one repo."""
    t = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                        str(repo), "cat-file", "-t", oid],
                       capture_output=True, env=ENV, timeout=30)
    if t.returncode != 0:
        return {"present": False,
                "cat_file_stderr": t.stderr.decode().strip()[:200]}
    kind = t.stdout.decode().strip()
    body = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch", "-C",
                           str(repo), "cat-file", kind, oid],
                          capture_output=True, env=ENV, timeout=30)
    return {"present": True, "type": kind,
            "body_sha256": hashlib.sha256(body.stdout).hexdigest(),
            "body": body.stdout.decode("utf-8", "replace")[:400]}


def main():
    root = Path(sys.argv[1]).resolve()
    lane, fleet, draft, a, target, tag = build(root)
    out = {"root": str(root), "lane": str(lane), "fleet": str(fleet),
           "draft_path": str(draft), "draft_text": draft.read_text(),
           "lane_valid_commit": a, "tag_target_blob": target, "tag_oid": tag,
           "objects": {}}
    for label, repo in (("lane", lane), ("fleet", fleet)):
        out["objects"][label] = {
            "valid_commit": probe(repo, a),
            "tag_oid": probe(repo, tag),
            "tag_target_blob": probe(repo, target),
        }
        # is the tag reachable from any ref in this repo?
        reach = subprocess.run(["git", "--no-replace-objects", "--no-lazy-fetch",
                                "-C", str(repo), "rev-list", "--objects", "--all"],
                               capture_output=True, env=ENV, timeout=30)
        out["objects"][label]["rev_list_objects"] = sorted(
            reach.stdout.decode().split())
        out["objects"][label]["refs"] = sorted(
            git(repo, "for-each-ref", "--format=%(refname) %(objectname)").splitlines())
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
