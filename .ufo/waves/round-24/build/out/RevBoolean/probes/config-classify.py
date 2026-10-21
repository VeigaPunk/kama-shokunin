#!/usr/bin/env python3
"""Bounded offline probe: how git 2.56 reads promisor-relevant config, and
how the base audit tool's git_bool() classifies the same spellings.

Fixtures are synthetic local repos under this scratch tree. No network.
"""
import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
FIX = BASE / "fixtures" / "cfg"
OUT = BASE / "out"

spec = importlib.util.spec_from_file_location(
    "audit", "/fast/scratch/hyaku/kama-r24/RevBoolean/tools/report-landing-audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def run(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=ENV, timeout=20)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def make_repo(name, config_text):
    repo = FIX / name
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    run(repo, "init", "-q")
    (repo / ".git" / "config").write_text(config_text)
    return repo


CASES = [
    # (label, config body after [remote "origin"] section header)
    ("promisor_true", '[remote "origin"]\n\tpromisor = true\n'),
    ("promisor_upper_TRUE", '[remote "origin"]\n\tpromisor = TRUE\n'),
    ("promisor_mixed_True", '[remote "origin"]\n\tpromisor = True\n'),
    ("promisor_yes", '[remote "origin"]\n\tpromisor = yes\n'),
    ("promisor_ON", '[remote "origin"]\n\tpromisor = ON\n'),
    ("promisor_one", '[remote "origin"]\n\tpromisor = 1\n'),
    ("promisor_false", '[remote "origin"]\n\tpromisor = false\n'),
    ("promisor_upper_FALSE", '[remote "origin"]\n\tpromisor = FALSE\n'),
    ("promisor_no", '[remote "origin"]\n\tpromisor = no\n'),
    ("promisor_off", '[remote "origin"]\n\tpromisor = off\n'),
    ("promisor_zero", '[remote "origin"]\n\tpromisor = 0\n'),
    ("promisor_empty_value", '[remote "origin"]\n\tpromisor =\n'),
    ("promisor_valueless", '[remote "origin"]\n\tpromisor\n'),
    ("promisor_quoted_true", '[remote "origin"]\n\tpromisor = "true"\n'),
    ("promisor_quoted_TRUE", '[remote "origin"]\n\tpromisor = "TRUE"\n'),
    ("promisor_quoted_false", '[remote "origin"]\n\tpromisor = "false"\n'),
    ("promisor_squoted_true", "[remote \"origin\"]\n\tpromisor = 'true'\n"),
    ("promisor_quoted_space_true", '[remote "origin"]\n\tpromisor = " true "\n'),
    ("promisor_bare_uppercase_word", '[remote "origin"]\n\tpromisor = TrUe\n'),
    ("promisor_junk", '[remote "origin"]\n\tpromisor = maybe\n'),
    ("promisor_negative_one", '[remote "origin"]\n\tpromisor = -1\n'),
    ("promisor_zero_padded", '[remote "origin"]\n\tpromisor = 00\n'),
    ("filter_only", '[remote "origin"]\n\tpartialclonefilter = blob:none\n'),
    ("filter_only_plus_false_promisor",
     '[remote "origin"]\n\tpartialclonefilter = blob:none\n\tpromisor = false\n'),
    ("filter_only_plus_true_promisor",
     '[remote "origin"]\n\tpartialclonefilter = blob:none\n\tpromisor = true\n'),
    ("extensions_partialclone", '[remote "origin"]\n\turl = /nonexistent\n[extensions]\n\tpartialclone = origin\n'),
    ("extensions_partialclone_empty", '[extensions]\n\tpartialclone\n'),
    ("extensions_partialclone_named_but_remote_false",
     '[remote "origin"]\n\tpromisor = false\n[extensions]\n\tpartialclone = origin\n'),
]


def observed_value(repo, key):
    """What the audit tool sees: `git config --null --list` entry for key."""
    rc, out, err = run(repo, "config", "--null", "--list")
    if rc != 0:
        return None, f"rc={rc} {err.strip()}"
    for entry in out.split("\0"):
        if not entry:
            continue
        k, _, v = entry.partition("\n")
        if k == key:
            return v, None
    return None, "absent"


def git_bool_spelling(repo, key):
    rc, out, err = run(repo, "config", "--bool", "--get", key)
    if rc != 0:
        return f"rc={rc}", err.strip().splitlines()[-1] if err.strip() else ""
    return out.strip(), ""


rows = []
for label, body in CASES:
    repo = make_repo(label, body)
    raw = (repo / ".git" / "config").read_text()
    key = "extensions.partialclone"
    if "promisor" in body and "extensions" not in body.split("[remote")[0]:
        key = "remote.origin.promisor"
    obs, err = observed_value(repo, key)
    truth, terr = git_bool_spelling(repo, key)
    base_bool = audit.git_bool(obs) if obs is not None else None
    rows.append({
        "case": label,
        "config": raw.replace("\n", "\\n"),
        "key": key,
        "audit_sees_value": obs,
        "audit_sees_err": err,
        "git_config_bool": truth,
        "git_bool_err": terr,
        "base_git_bool": base_bool,
        "base_matches_git": (base_bool is True and truth == "true")
        or (base_bool is False and truth == "false"),
    })

OUT.mkdir(parents=True, exist_ok=True)
with (OUT / "config-classification.tsv").open("w") as fh:
    fh.write("case\tkey\tvalue_seen_by_audit\tgit_config_bool\tbase_git_bool\t"
             "base_matches_git\n")
    for r in rows:
        fh.write("\t".join([
            r["case"], r["key"], repr(r["audit_sees_value"]),
            r["git_config_bool"], repr(r["base_git_bool"]),
            str(r["base_matches_git"])]) + "\n")

width = max(len(r["case"]) for r in rows)
print(f"{'case'.ljust(width)}  {'value'.rjust(14)}  {'git --bool'.rjust(9)}  "
      f"{'base()'.rjust(7)}  match")
for r in rows:
    print(f"{r['case'].ljust(width)}  {repr(r['audit_sees_value']).rjust(14)}  "
          f"{r['git_config_bool'].rjust(9)}  {repr(r['base_git_bool']).rjust(7)}  "
          f"{'OK' if r['base_matches_git'] else 'DIVERGE'}")
print("\nwrote", OUT / "config-classification.tsv")
