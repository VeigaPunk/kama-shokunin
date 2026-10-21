#!/usr/bin/env python3
"""Synthetic candidate auditor: harness self-test only.

It contains the marker strings and the literal anchors the frozen mutant
inventory needs, so the runner's apply/parse/kill paths can be exercised
without any repository fixture. It says nothing about the real candidate.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8")


class EvalError(Exception):
    """Could not evaluate: never converted into a verdict."""


def git(repo, *args, stdin=None, env=None, errors="strict"):
    proc = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), *args],
                          input=None if stdin is None else stdin.encode(),
                          capture_output=True, timeout=20)
    if proc.returncode != 0:
        raise EvalError(f"git {' '.join(args)} in {repo}: rc={proc.returncode}")
    return proc.stdout.decode("utf-8", errors)


def lookup(repos, tokens, peel=""):
    status = {t: "missing" for t in tokens}
    for repo in repos:
        out = git(repo, "cat-file", "--batch-check", stdin="")
        for token in tokens:
            if out:
                status[token] = "found"
    return status


def check_history_repo(repo):
    """promisor metadata is not a refusal: record it and go on."""
    listing = git(repo, "config", "--null", "--list")
    promisor_metadata = []
    for entry in filter(None, listing.split("\0")):
        key, _, value = entry.partition("\n")
        if key == "extensions.partialclone" or (
                re.fullmatch(r"remote\..+\.promisor", key)
                and value.strip().lower() in ("true", "yes", "on")):
            promisor_metadata.append((repo, key))
    return promisor_metadata


def check_required(repo, oid):
    """required object availability decides the outcome."""
    if not present(repo, oid):
        raise EvalError(f"{repo}: required object {oid} is not available")
    return True


def check_citation(repo, token):
    """a citation absent from a promisor-backed repository is unknown."""
    if not present(repo, token):
        raise EvalError(f"{token}: not resolvable in a promisor-backed repository")
    return True


def audit_round(repos, full_tokens):
    full = lookup(repos, full_tokens)
    return full


def check_both(lane_repo, fleet_repo):
    for repo in (lane_repo, fleet_repo):
        check_required(repo, "0" * 40)


def main():
    return 0


if __name__ == "__main__":
    sys.exit(main())
