#!/usr/bin/env python3
"""Bounded CLI oracle for round-21 errata mutation probes; scratch-only fixtures."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--script", required=True, type=Path)
    ap.add_argument("--scratch", required=True, type=Path)
    args = ap.parse_args()
    script = args.script.resolve()
    scratch = args.scratch.resolve()
    script.relative_to(scratch)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(scratch))
    observations = []
    setup = []

    def command(argv, *, git_setup=False, extra_env=None):
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=30,
                              env=env if extra_env is None else {**env, **extra_env})
        record = {"argv": argv, "exit": proc.returncode,
                  "stdout": proc.stdout, "stderr": proc.stderr}
        if git_setup:
            setup.append(record)
            if proc.returncode != 0:
                raise RuntimeError(json.dumps(record))
        return record

    with tempfile.TemporaryDirectory(prefix="errata-oracle-", dir=scratch) as tmp:
        root = Path(tmp)
        lane, fleet = root / "lane", root / "fleet"
        for repo in (lane, fleet):
            repo.mkdir()
            command(["git", "-C", str(repo), "init", "-q", "-b", "master"],
                    git_setup=True)

        def commit(repo, subject, stamp):
            target = repo / "f"
            with target.open("a", encoding="utf-8") as stream:
                stream.write(subject + "\n")
            command(["git", "-C", str(repo), "add", "f"], git_setup=True)
            command(["git", "-C", str(repo), "-c", "user.name=kama-shokunin",
                     "-c", "user.email=kama@mutation.invalid", "-c",
                     "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                     "commit", "-q", "-m", subject], git_setup=True,
                    extra_env={"GIT_AUTHOR_DATE": f"@{stamp} +0000",
                               "GIT_COMMITTER_DATE": f"@{stamp} +0000"})
            return command(["git", "-C", str(repo), "rev-parse", "HEAD"],
                           git_setup=True)["stdout"].strip()

        a = commit(lane, "round-1: work", 1000)
        b = commit(lane, "round-1: measure", 1100)
        commit(fleet, "fixture fleet anchor", 1200)
        blob = command(["git", "-C", str(lane), "rev-parse", "HEAD:f"],
                       git_setup=True)["stdout"].strip()
        bogus = "f" * 40
        report = root / "report.md"
        report.write_text("## Work performed\n" + bogus + "\n## Landed changes\n"
                          + a + "\n" + b + "\n", encoding="utf-8")
        errata = root / "errata.tsv"
        common = ["python3", str(script), "--lane-repo", str(lane),
                  "--fleet-repo", str(fleet), "--branch", "HEAD", "--rounds", "1",
                  "--report", f"1={report}", "--json"]

        def row(rnd=1, kind="unresolved-full-hash", token=bogus, correction=a):
            return f"{rnd}\t{kind}\t{token}\t{correction}\tmutation oracle\n"

        def check(name, text, expected_exit, counts=None, *, raw=False, missing=False):
            if text is not None:
                errata.write_text(text, encoding="utf-8")
            argv = common + (["--no-errata"] if raw else ["--errata", str(errata)])
            if missing:
                argv = argv + ["--report", f"1={root / 'absent-report.md'}"]
            record = command(argv)
            actual = None
            if record["stdout"].strip():
                try:
                    summary = json.loads(record["stdout"])["summary"]
                    actual = {key: summary[key] for key in
                              ("uncorrected", "errata_unmatched", "errata_invalid",
                               "status")}
                except (ValueError, KeyError, TypeError):
                    pass
            expected = None if counts is None else dict(zip(
                ("uncorrected", "errata_unmatched", "errata_invalid", "status"), counts))
            ok = record["exit"] == expected_exit and (expected is None or actual == expected)
            if expected_exit == 2:
                ok = ok and "could-not-evaluate:" in record["stderr"]
            observations.append({"case": name, "ok": ok, "expected_exit": expected_exit,
                                 "expected_summary": expected, "actual_summary": actual,
                                 **record})

        check("exact-clean-exit0", row(), 0, (0, 0, 0, "clean"))
        check("round-must-equal", row(rnd=2), 1, (1, 1, 0, "failed"))
        check("kind-must-equal", row(kind="landed-omitted"), 1, (1, 1, 0, "failed"))
        check("token-must-equal-not-prefix", row(token=bogus[:7]), 1,
              (1, 1, 0, "failed"))
        check("unmatched-row-fails", row() + row(token="0" * 40), 1,
              (0, 1, 0, "failed"))
        check("nonexistent-correction-fails", row(correction="e" * 40), 1,
              (0, 0, 1, "failed"))
        check("blob-is-not-correction-commit", row(correction=blob), 1,
              (0, 0, 1, "failed"))
        check("malformed-field-count-exit2", "1\tunresolved-full-hash\tx\ty\n", 2)
        check("malformed-round-exit2", row(rnd="one"), 2)
        check("malformed-kind-exit2", row(kind="unknown"), 2)
        check("raw-defect-exit1", None, 1, (1, 0, 0, "failed"), raw=True)
        check("missing-report-exit2", None, 2, raw=True, missing=True)
    failed = [record["case"] for record in observations if not record["ok"]]
    print(json.dumps({"setup": setup, "cases": observations, "case_count": len(observations),
                      "failed": failed, "failed_count": len(failed)}, sort_keys=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
