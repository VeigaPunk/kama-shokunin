#!/usr/bin/env python3
"""Bounded offline probe #4: definitive classification matrix.

Ground truth: in a promisor-backed repository git tries to lazily fetch a
missing object from a promisor remote.  With GIT_NO_LAZY_FETCH=1 the fetch is
suppressed and git prints

    warning: lazy fetching disabled; some objects may not be available
    fatal: could not fetch <oid> from promisor remote

(promisor-remote.c fetch_objects / promisor_remote_get_direct).  The probe
command is `git log -p --all` on a synthetic partial clone that is missing one
blob.  No transport is invoked: the warning is emitted before start_command().

Each case rewrites the clone's .git/config with one candidate spelling and
re-probes.  The matrix is the classification contract the audit must
implement for round-24.
"""
import os
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
CLONE = BASE / "fixtures" / "clone" / "c2"
OUT = BASE / "out"
BLOB = "c2532a76d98b3de3ef230a5c37888aa5e951ae5c"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
           GIT_NO_LAZY_FETCH="1")

ORIGIN = '[remote "origin"]\n\turl = file:///nowhere\n\tfetch = +refs/heads/*:refs/remotes/origin/*\n'

CASES = [
    ("git-generated partial clone",
     '[core]\n\trepositoryformatversion = 1\n[remote "origin"]\n\turl = file:///nowhere\n'
     '\tpromisor = true\n\tpartialclonefilter = blob:none\n'),
    ("promisor = true", ORIGIN + '\tpromisor = true\n'),
    ("promisor = TRUE", ORIGIN + '\tpromisor = TRUE\n'),
    ("promisor = True", ORIGIN + '\tpromisor = True\n'),
    ("promisor = yes", ORIGIN + '\tpromisor = yes\n'),
    ("promisor = on", ORIGIN + '\tpromisor = on\n'),
    ("promisor = 1", ORIGIN + '\tpromisor = 1\n'),
    ("promisor = false", ORIGIN + '\tpromisor = false\n'),
    ("promisor = FALSE", ORIGIN + '\tpromisor = FALSE\n'),
    ("promisor = no", ORIGIN + '\tpromisor = no\n'),
    ("promisor = off", ORIGIN + '\tpromisor = off\n'),
    ("promisor = 0", ORIGIN + '\tpromisor = 0\n'),
    ("promisor = 00", ORIGIN + '\tpromisor = 00\n'),
    ("promisor = -1", ORIGIN + '\tpromisor = -1\n'),
    ("promisor = (empty value)", ORIGIN + '\tpromisor =\n'),
    ("promisor (valueless key)", ORIGIN + '\tpromisor\n'),
    ("promisor = \"true\"", ORIGIN + '\tpromisor = "true"\n'),
    ("promisor = \"TRUE\"", ORIGIN + '\tpromisor = "TRUE"\n'),
    ("promisor = \"false\"", ORIGIN + '\tpromisor = "false"\n'),
    ("promisor = 'true' (single quotes)", ORIGIN + "\tpromisor = 'true'\n"),
    ("promisor = \" true \" (quoted spaces)", ORIGIN + '\tpromisor = " true "\n'),
    ("promisor = maybe (invalid)", ORIGIN + '\tpromisor = maybe\n'),
    ("promisor = 1abc (invalid int)", ORIGIN + '\tpromisor = 1abc\n'),
    ("promisor = true, then promisor = false",
     ORIGIN + '\tpromisor = true\n\tpromisor = false\n'),
    ("promisor = false, then promisor = true",
     ORIGIN + '\tpromisor = false\n\tpromisor = true\n'),
    ("partialclonefilter only (no promisor key)",
     ORIGIN + '\tpartialclonefilter = blob:none\n'),
    ("partialclonefilter + promisor = false",
     ORIGIN + '\tpartialclonefilter = blob:none\n\tpromisor = false\n'),
    ("partialclonefilter + promisor = true",
     ORIGIN + '\tpartialclonefilter = blob:none\n\tpromisor = true\n'),
    ("extensions.partialclone = origin (remote has no promisor key)",
     ORIGIN + '[extensions]\n\tpartialclone = origin\n'),
    ("extensions.partialclone = origin + promisor = false",
     ORIGIN + '\tpromisor = false\n[extensions]\n\tpartialclone = origin\n'),
    ("extensions.partialclone (valueless)",
     '[extensions]\n\tpartialclone\n'),
    ("no promisor config at all (plain clone shape)", ORIGIN),
]


def probe():
    p = subprocess.run(["git", "-C", str(CLONE), "log", "-p", "--all"],
                       capture_output=True, env=ENV, timeout=60)
    err = p.stderr.decode("utf-8", "replace")
    lazy = "lazy fetching disabled" in err
    unusable = ("bad boolean config value" in err
                or "bad config line" in err
                or "missing value for" in err
                or "fatal: not a git repository" in err
                or "error: could not read" in err)
    return lazy, unusable, err.strip().replace("\n", " | ")


rows = []
for label, cfg in CASES:
    (CLONE / ".git" / "config").write_text(cfg)
    lazy, unusable, err = probe()
    rows.append((label, lazy, unusable, err))

width = max(len(r[0]) for r in rows)
print(f"{'config state'.ljust(width)}  promisor  unusable  detail")
for label, lazy, unusable, err in rows:
    print(f"{label.ljust(width)}  {str(lazy).ljust(8)}  {str(unusable).ljust(9)}  {err[:90]}")

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "promisor-classification-matrix.tsv").open("w") as fh:
    fh.write("config_state\tgit_promisor_backed\tgit_unusable_repo\tobserved\n")
    for label, lazy, unusable, err in rows:
        fh.write(f"{label}\t{lazy}\t{unusable}\t{err}\n")
print("\nwrote", OUT / "promisor-classification-matrix.tsv")
