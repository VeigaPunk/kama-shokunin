#!/usr/bin/env python3
"""Bounded offline probe #6: exact boolean spelling rules.

For each candidate spelling of remote.origin.promisor, compare
  * git's own answer: `git config --bool --get remote.origin.promisor`
  * the base audit helper: tools/report-landing-audit.py:git_bool()
  * a git-faithful re-implementation (git_parse_maybe_bool_text +
    git_parse_int with strtoimax base 0)
"""
import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/RevBoolean")
FIX = BASE / "fixtures" / "spell"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

spec = importlib.util.spec_from_file_location(
    "audit", "/fast/scratch/hyaku/kama-r24/RevBoolean/tools/report-landing-audit.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

SPELLINGS = [
    "true", "TRUE", "True", "TrUe", "tRuE",
    "yes", "YES", "on", "ON",
    "false", "FALSE", "no", "off",
    "1", "0", "-1", "00", "010", "0x1", "0X1", "08", "+1", " 1", "1 ", "\t1",
    "1abc", "abc", "", " true ", "true ", " true", "maybe",
    "true#comment", "true ; comment", "-0", "9999999999999999999999",
]


def run(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=ENV, timeout=20)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def faithful(value):
    """git_parse_maybe_bool_text + git_parse_int(strtoimax, base 0)."""
    if value is None:
        return True
    if value == "":
        return False
    low = value.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    # git_parse_int: strtoimax(value, &end, 0); valid iff end consumed all
    s = value.lstrip(" \t\n\v\f\r")
    if not s:
        return None
    body = s[1:] if s[0] in "+-" else s
    digits = body[2:] if body[:2].lower() in ("0x", "0b", "0o") else body
    if not digits or not all(c.isdigit() for c in digits):
        return None
    try:
        return int(s, 0) != 0
    except ValueError:
        return None


rows = []
for spelling in SPELLINGS:
    repo = FIX / "sp"
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    run(repo, "init", "-q")
    # write the raw value into the config file, quoting only if needed
    literal = spelling.replace("\\", "\\\\").replace('"', '\\"')
    (repo / ".git" / "config").write_text(
        f'[remote "origin"]\n\tpromisor = "{literal}"\n')
    rc, out, err = run(repo, "config", "--bool", "--get", "remote.origin.promisor")
    git_answer = {"true": True, "false": False}.get(out.strip(),
                                                     f"rc={rc} {err.strip()[:40]}")
    rc2, listing, _ = run(repo, "config", "--null", "--list")
    seen = None
    for entry in listing.split("\0"):
        if entry.startswith("remote.origin.promisor"):
            key, sep, val = entry.partition("\n")
            seen = val if sep else None
    base_answer = audit.git_bool(seen) if seen is not None else None
    rows.append((spelling, seen, git_answer, base_answer, faithful(seen)))

w = max(len(repr(r[0])) for r in rows)
print(f"{'spelling'.ljust(w)}  {'git --bool'.ljust(12)}  {'base()'.ljust(7)}  {'faithful'.ljust(9)}  base==git")
for spelling, seen, ga, ba, fa in rows:
    agree = (ba == ga) if isinstance(ga, bool) else None
    print(f"{repr(spelling).ljust(w)}  {str(ga).ljust(12)}  {str(ba).ljust(7)}  "
          f"{str(fa).ljust(9)}  {agree}")

out = BASE / "out" / "boolean-spellings.tsv"
out.parent.mkdir(parents=True, exist_ok=True)
with out.open("w") as fh:
    fh.write("spelling\tvalue_seen\tgit_config_bool\tbase_git_bool\tfaithful\n")
    for spelling, seen, ga, ba, fa in rows:
        fh.write(f"{spelling!r}\t{seen!r}\t{ga}\t{ba}\t{fa}\n")
print("\nwrote", out)
