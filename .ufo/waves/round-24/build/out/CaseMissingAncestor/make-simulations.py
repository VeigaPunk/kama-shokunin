#!/usr/bin/env python3
"""Build two scratch simulations of tools/report-landing-audit.py from the
round-24 base blob (0df800e).

sim-repaired.py   the base with the two promisor *metadata* refusals
                  removed (the .promisor pack check and the config check).
                  Everything else is untouched: --no-lazy-fetch,
                  --no-replace-objects, the log/signature suppression, the
                  per-call timeout, the strict UTF-8 decode.  It exists to
                  show that the preregistered expectations of case CA-1 are
                  jointly achievable, not to be a candidate.

sim-tolerant.py   sim-repaired plus a tolerant history enumeration
                  (`rev-list --missing=print`, missing commits skipped).
                  It exists to show the discriminating power of the CA-1b
                  arm: the same repair, with the truncation hazard left in.
"""
import subprocess
import sys
from pathlib import Path

BASE = "0df800e896f6bce285a81e794ad4ae1d1e6c3a71"
AUDIT = "tools/report-landing-audit.py"
LANE = Path("/fast/scratch/hyaku/kama-r24/CaseMissingAncestor")
OUT = LANE / "build"

PACK_CHECK = '''        if rel == "objects/pack" and path.is_dir() and any(
                p.suffix == ".promisor" and p.with_suffix(".pack").exists()
                for p in path.iterdir()):
            raise EvalError(f"{repo}: partial clone (promisor pack)")
'''
CONFIG_CHECK = '''    listing = git(repo, "config", "--null", "--list",
                  errors="surrogateescape")
    for entry in filter(None, listing.split("\\0")):
        key, _, value = entry.partition("\\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\\..+\\.promisor", key)
                and git_bool(value)):
            raise EvalError(f"{repo}: partial clone ({key})")
'''
LOG_CALL = r'''    out = git(lane_repo, "log", "-z", "--format=%H%x00%an%x00%at%x00%s",
              branch, errors="surrogateescape")
    fields = out.split("\0")
'''
TOLERANT_CALL = '''    listed = git(lane_repo, "rev-list", "--missing=print", branch,
                 errors="surrogateescape")
    fields = []
    for sha in listed.split("\\n"):
        sha = sha.strip()
        if not sha or sha.startswith("?"):
            continue
        rec = git(lane_repo, "show", "-s", "-z",
                  "--format=%H%x00%an%x00%at%x00%s", sha,
                  errors="surrogateescape")
        fields.extend(rec.split("\\0")[:4])
'''
NOWALK_CALL = '''    listed = git(lane_repo, "rev-list", "--missing=print", branch,
                 errors="surrogateescape")
    fields = []
    for sha in listed.split("\\n"):
        sha = sha.strip()
        if not sha or sha.startswith("?"):
            continue
        rec = git(lane_repo, "log", "--no-walk", "-z",
                  "--format=%H%x00%an%x00%at%x00%s", sha,
                  errors="surrogateescape")
        fields.extend(rec.split("\\0")[:4])
'''


def blob():
    p = subprocess.run(["git", "-C", str(LANE), "cat-file", "blob",
                        f"{BASE}:{AUDIT}"], capture_output=True)
    if p.returncode:
        sys.exit(f"cannot read {BASE}:{AUDIT}: {p.stderr.decode()}")
    return p.stdout.decode()


def main():
    text = blob()
    for name in (PACK_CHECK, CONFIG_CHECK, LOG_CALL):
        if name not in text:
            sys.exit(f"anchor not found:\n{name}")
    repaired = text.replace(PACK_CHECK, "").replace(CONFIG_CHECK, "")
    (OUT / "sim-repaired.py").write_text(repaired)
    tolerant = repaired.replace(LOG_CALL, TOLERANT_CALL)
    (OUT / "sim-tolerant.py").write_text(tolerant)
    nowalk = repaired.replace(LOG_CALL, NOWALK_CALL)
    (OUT / "sim-nowalk.py").write_text(nowalk)
    print("wrote", OUT / "sim-repaired.py", OUT / "sim-tolerant.py",
          OUT / "sim-nowalk.py")


main()
