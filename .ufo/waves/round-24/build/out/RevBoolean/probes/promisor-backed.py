#!/usr/bin/env python3
"""Bounded offline probe #2: does git treat a repository as promisor-backed?

Ground truth probe: in a promisor-backed repository git would try to lazy
fetch a missing object; with GIT_NO_LAZY_FETCH=1 the fetch is suppressed and
git prints "lazy fetching disabled; some objects may not be available"
(promisor-remote.c fetch_objects()). No transport is ever invoked (the
warning is emitted before start_command()).

Also records the exact byte form of `git config --null --list` entries so the
audit's "key\\nvalue\\0" parsing can be checked against git's own output.
"""
import os
import shutil
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
FIX = BASE / "fixtures" / "promisor"
OUT = BASE / "out"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def run(repo, *args, extra_env=None):
    env = dict(ENV)
    if extra_env:
        env.update(extra_env)
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env, timeout=20)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def make_repo(name, config_text):
    repo = FIX / name
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    run(repo, "init", "-q")
    run(repo, "-c", "user.name=t", "-c", "user.email=t@example.invalid",
        "commit", "-q", "--allow-empty", "-m", "synthetic")
    (repo / ".git" / "config").write_text(config_text)
    return repo


CASES = [
    ("plain", "[core]\n\trepositoryformatversion = 0\n"),
    ("promisor_true", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = true\n'),
    ("promisor_false", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = false\n'),
    ("promisor_empty_value", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor =\n'),
    ("promisor_valueless", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor\n'),
    ("promisor_upper_TRUE", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = TRUE\n'),
    ("promisor_quoted_true", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = "true"\n'),
    ("promisor_squoted_true", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = \'true\'\n'),
    ("promisor_junk", '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = maybe\n'),
    ("filter_only", '[remote "origin"]\n\turl = ./nowhere\n\tpartialclonefilter = blob:none\n'),
    ("filter_only_plus_false", '[remote "origin"]\n\turl = ./nowhere\n\tpartialclonefilter = blob:none\n\tpromisor = false\n'),
    ("filter_only_plus_true", '[remote "origin"]\n\turl = ./nowhere\n\tpartialclonefilter = blob:none\n\tpromisor = true\n'),
    ("extensions_partialclone", '[remote "origin"]\n\turl = ./nowhere\n[extensions]\n\tpartialclone = origin\n'),
    ("extensions_partialclone_remote_false",
     '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = false\n[extensions]\n\tpartialclone = origin\n'),
    ("extensions_partialclone_valueless", '[extensions]\n\tpartialclone\n'),
    ("extensions_partialclone_unknown_remote",
     '[remote "origin"]\n\turl = ./nowhere\n[extensions]\n\tpartialclone = elsewhere\n'),
    ("multivalue_true_then_false",
     '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = true\n\tpromisor = false\n'),
    ("multivalue_false_then_true",
     '[remote "origin"]\n\turl = ./nowhere\n\tpromisor = false\n\tpromisor = true\n'),
]

MISSING = "0123456789abcdef0123456789abcdef01234567"

rows = []
for label, cfg in CASES:
    repo = make_repo(label, cfg)
    rc, out, err = run(repo, "cat-file", "--batch-check",
                       extra_env={"GIT_NO_LAZY_FETCH": "1"})
    # feed the missing oid through stdin instead
    p = subprocess.run(["git", "-C", str(repo), "cat-file", "-p", MISSING],
                       capture_output=True,
                       env={**ENV, "GIT_NO_LAZY_FETCH": "1"}, timeout=20)
    stderr = p.stderr.decode("utf-8", "replace")
    stdout = p.stdout.decode("utf-8", "replace")
    lazy = "lazy fetching disabled" in stderr
    # raw config listing form
    rc2, raw, _ = run(repo, "config", "--null", "--list")
    raw_repr = repr(raw)
    # last-value view used by `git config --bool --get`
    rc3, last, err3 = run(repo, "config", "--bool", "--get", "remote.origin.promisor")
    rows.append({
        "case": label,
        "promisor_backed": lazy,
        "catfile_stderr": stderr.strip().replace("\n", " | "),
        "catfile_stdout": stdout.strip(),
        "list_null_raw": raw_repr,
        "bool_get_rc": rc3,
        "bool_get_out": last.strip(),
        "bool_get_err": err3.strip().splitlines()[-1] if err3.strip() else "",
    })

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "promisor-backed.tsv").open("w") as fh:
    fh.write("case\tpromisor_backed\tbool_get_rc\tbool_get_out\tbool_get_err\t"
             "catfile_stderr\n")
    for r in rows:
        fh.write("\t".join([r["case"], str(r["promisor_backed"]),
                            str(r["bool_get_rc"]), r["bool_get_out"],
                            r["bool_get_err"], r["catfile_stderr"]]) + "\n")

w = max(len(r["case"]) for r in rows)
print(f"{'case'.ljust(w)}  promisor  --bool-get(rc,out)      stderr")
for r in rows:
    print(f"{r['case'].ljust(w)}  {str(r['promisor_backed']).ljust(8)}  "
          f"({r['bool_get_rc']},{r['bool_get_out'] or r['bool_get_err'][:40]})  "
          f"{r['catfile_stderr'][:70]}")
print("\nraw --null --list samples:")
for r in rows:
    if r["case"] in ("promisor_valueless", "promisor_empty_value",
                     "multivalue_true_then_false", "filter_only"):
        print(f"  {r['case']}: {r['list_null_raw']}")
