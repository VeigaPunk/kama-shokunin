#!/usr/bin/env python3
"""round-40 C2 operability audit (frozen before any data seat; kama round 40).

Freezes the r38-verifier-routed wave-evidence completeness correction. All
reads are git blobs at --tip. Exits 0 when met, 1 when not.

Frozen predicate (same sentence as preregistration.json C2):
  - .ufo/waves/round-38/w1/spec.json and run.json exist at tip;
  - sha256 of committed spec.json == 397f598009ad9dab0699cc73d165cff583d8f069b445f0dbaa0b79f6a4122cb7
    (authentic round-38 session file);
  - sha256 of committed run.json == d0666a36f483685bcadfdce997389ea4af7c6a80efe8b75c70e2e4c6d2039642
    (authentic round-38 session file);
  - run.json counts.total == 36 and len(spec.json items) == 36
    (the round-38 wave registry has 36 members at the committed
    out/swarm-registry.json).
"""
import argparse, hashlib, json, subprocess, sys

SPEC_SHA = "397f598009ad9dab0699cc73d165cff583d8f069b445f0dbaa0b79f6a4122cb7"
RUN_SHA = "d0666a36f483685bcadfdce997389ea4af7c6a80efe8b75c70e2e4c6d2039642"
SPEC_PATH = ".ufo/waves/round-38/w1/spec.json"
RUN_PATH = ".ufo/waves/round-38/w1/run.json"
MEMBERS = 36


def blob(repo, tip, path):
    p = subprocess.run(["git", "-C", repo, "show", f"{tip}:{path}"],
                       capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()

    spec = blob(a.repo, a.tip, SPEC_PATH)
    run = blob(a.repo, a.tip, RUN_PATH)
    spec_exists = 1 if spec is not None else 0
    run_exists = 1 if run is not None else 0
    spec_sha_ok = 1 if (spec is not None and hashlib.sha256(spec).hexdigest() == SPEC_SHA) else 0
    run_sha_ok = 1 if (run is not None and hashlib.sha256(run).hexdigest() == RUN_SHA) else 0

    counts_ok = 0
    if spec is not None and run is not None:
        try:
            sj = json.loads(spec)
            rj = json.loads(run)
            total = rj.get("counts", {}).get("total")
            if total == MEMBERS and len(sj.get("items", [])) == MEMBERS:
                counts_ok = 1
        except Exception:
            counts_ok = 0

    met = bool(spec_exists and run_exists and spec_sha_ok and run_sha_ok and counts_ok)
    line = (f"spec_exists={spec_exists} run_exists={run_exists} "
            f"spec_sha_ok={spec_sha_ok} run_sha_ok={run_sha_ok} "
            f"counts_ok={counts_ok} met={'True' if met else 'False'}")
    print(line)
    if a.out:
        with open(a.out, "w") as f:
            f.write(line + "\n")
    sys.exit(0 if met else 1)


if __name__ == "__main__":
    main()
