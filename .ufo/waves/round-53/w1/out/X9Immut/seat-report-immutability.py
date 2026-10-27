#!/usr/bin/env python3
"""seat-report-immutability.py -- committed seat reports keep their first-add bytes.

Round-53 seat X9Immut; routed from round-52 lesson R4 / Mistakes #8 (the proposed
`.ufo/waves/round-52/w1/out/W3Mistakes/seat-report-immutability.py`). The wave
context tells every seat "write your report once; never rewrite it after you have
finished"; no lane instrument graded that, and round 52 found ten committed seat
reports that no longer held their first-add bytes.

Contract
    Population: every path that is a seat report at ``--rev``:
    ``.ufo/waves/round-<N>/<wave>/out/**/*.md`` where ``<N>`` is selected by
    ``--rounds``, at any nesting depth below ``out/``. The round-52 remediation
    sibling ``<stem>.late-rewrite.md`` is the authorised home of divergent bytes,
    so it is not itself a seat report. Only tracked (tree) paths count; untracked
    worktree files are not committed reports.

    Baseline: the report's *most recent* add commit reachable from ``--rev`` and
    that commit's blob. A delete followed by a re-add restarts the baseline (the
    record-integrity question is "was a committed report edited", not "is the
    path's oldest incarnation still present"). A rename is read as delete + add
    (no rename detection), so a moved report restarts its baseline too.

    Violation: the blob at ``--rev`` differs from the baseline blob, i.e. the
    report was edited in place after it was committed and never restored. A
    restoration (tip blob equals the baseline blob) is not a violation; it is
    reported as ``RESTORED`` with the commits that carried the divergent bytes.
    The presence of a ``<stem>.late-rewrite.md`` sibling does not excuse a
    divergent tip: it is reported as ``sibling=matches``/``differs`` on the same
    line so a reader can see whether the divergent bytes were kept.

Output lines (stdout)
    REWRITTEN <path> first_add=<sha> first_blob=<sha> tip_blob=<sha>
             commits=<sha>[,...] later_blobs=<sha|->[,...] sibling=<absent|matches|differs>
        one line per violation; commits and later_blobs are oldest-first and
        name every commit newer than the add that touched the path (a deletion
        is the blob ``-``).
    RESTORED <path> first_add=<sha> first_blob=<sha> commits=... later_blobs=... sibling=...
        informational: divergent bytes were committed and then restored.
    UNBASED <path>
        no add commit reachable from --rev; the report cannot be graded.
    seat-report-immutability rev=<sha> rounds=<spec> reports=<n> rewritten=<n>
                             restored=<n> unbased=<n> met=<True|False>

Exit codes
    0  no violation
    1  at least one violation
    2  could not evaluate: not a git repository, unresolvable revision, git
       failure, empty population, or a report with no reachable add commit

Read-only: only ``git rev-parse``, ``git ls-tree``, ``git log`` and
``git cat-file`` are issued, and only against the repository named by --repo.
``--selftest`` writes git fixtures under ``$TMPDIR`` (honoured explicitly, never
a hardcoded /tmp) and removes them on exit.

Usage
    seat-report-immutability.py [--repo DIR] [--rev REV] [--rounds SPEC]
    seat-report-immutability.py --selftest

    --repo DIR     Repository to read (default: current directory).
    --rev REV      Commit/tree whose reports are graded (default: HEAD).
    --rounds SPEC  Rounds to grade: ``46-52``, ``46,48,50-52``, ``52``.
                   Default: every round directory present at --rev.
    --selftest     Build a scratch fixture with one untouched and one rewritten
                   seat report, show exit 0 and exit 1, and print
                   ``SEAT_REPORT_IMMUTABILITY_SELFTEST pass=N fail=M``.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

NAME = "seat-report-immutability"
LATE_SUFFIX = ".late-rewrite.md"


class EvalError(Exception):
    """Could not evaluate (exit 2)."""


def _git(repo, *args, check=True):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode:
        if not check:
            return None
        raise EvalError(
            "git %s failed (exit %d): %s"
            % (" ".join(args), p.returncode, p.stderr.decode("utf-8", "replace").strip()[:300])
        )
    return p.stdout


# ------------------------------------------------------------------ population


def parse_rounds(spec):
    """'46-52' / '46,48,50-52' -> {'46-52': {46, ..., 52}, ...} (list of sets)."""
    out = []
    for tok in spec.replace(" ", "").split(","):
        if not tok:
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", tok)
        if not m:
            raise EvalError("bad --rounds token %r (want N or N-M)" % tok)
        lo = int(m.group(1))
        hi = int(m.group(2)) if m.group(2) else lo
        if hi < lo:
            raise EvalError("bad --rounds range %r (hi < lo)" % tok)
        out.append(set(range(lo, hi + 1)))
    if not out:
        raise EvalError("empty --rounds")
    return out


def select_paths(paths, rounds_sets):
    """Filter tree paths to seat reports in the selected rounds."""
    sel = set().union(*rounds_sets)
    picked = []
    for p in paths:
        if not p or not p.endswith(".md") or p.endswith(LATE_SUFFIX):
            continue
        m = re.match(r"\.ufo/waves/round-(\d+)/", p)
        if not m or int(m.group(1)) not in sel:
            continue
        if "/out/" not in p:
            continue
        picked.append(p)
    return picked


def round_dirs(rounds_sets):
    sel = set().union(*rounds_sets)
    return [".ufo/waves/round-%d" % n for n in sorted(sel)]


# ------------------------------------------------------------------ git reads


def _walk_events(repo, rev, dirs):
    """One `git log` walk, newest first: path -> [(commit, status, path_after)]."""
    out = _git(
        repo,
        "log",
        rev,
        "--pretty=format:%x01%H",
        "--name-status",
        "-z",
        "--diff-filter=AMDR",
        "--",
        *dirs,
    )
    events = {}
    chunks = out.split(b"\x01")
    for chunk in chunks:
        if not chunk.strip(b"\x00\n"):
            continue
        # chunk is b"<sha>\nA\x00<path>\x00..." (git puts the first status on the
        # same NUL field as the header line)
        head, _, rest = chunk.partition(b"\n")
        commit = head.strip().decode()
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise EvalError("unexpected git log header %r" % head[:80])
        toks = [
            line.decode("utf-8", "surrogateescape")
            for line in rest.split(b"\x00")
            for line in line.split(b"\n")
            if line.strip()
        ]
        i = 0
        while i < len(toks):
            status = toks[i]
            i += 1
            if status[:1] in ("R", "C"):
                if i + 1 >= len(toks):
                    break
                old, new = toks[i], toks[i + 1]
                i += 2
                events.setdefault(old, []).append((commit, status[:1], new))
                events.setdefault(new, []).append((commit, status[:1], new))
            else:
                if i >= len(toks):
                    break
                path = toks[i]
                i += 1
                events.setdefault(path, []).append((commit, status[:1], path))
    return events


def _blobs(repo, specs):
    """Resolve many `<rev>:<path>` specs in one `git cat-file --batch-check`."""
    if not specs:
        return {}
    inp = "".join(s + "\n" for s in specs).encode("utf-8", "surrogateescape")
    p = subprocess.run(
        ["git", "-C", repo, "cat-file", "--batch-check"],
        input=inp,
        capture_output=True,
    )
    if p.returncode:
        raise EvalError("git cat-file --batch-check failed: %s" % p.stderr.decode()[:200])
    res = {}
    lines = [l for l in p.stdout.decode("utf-8", "surrogateescape").split("\n") if l]
    if len(lines) != len(specs):
        raise EvalError(
            "git cat-file --batch-check returned %d lines for %d specs"
            % (len(lines), len(specs))
        )
    for spec, line in zip(specs, lines):
        parts = line.split(" ")
        res[spec] = parts[0] if re.fullmatch(r"[0-9a-f]{40}", parts[0]) else None
    return res


# ------------------------------------------------------------------ evaluation


def evaluate(repo, rev, rounds_spec):
    """Grade every seat report in the selected rounds. Read-only on `repo`."""
    top = _git(repo, "rev-parse", "--show-toplevel", check=False)
    if top is None:
        raise EvalError("%s is not inside a git repository" % repo)
    # every tree path is repository-root relative, so read from the toplevel and
    # let --repo name any directory inside the worktree
    repo = top.decode("utf-8", "surrogateescape").strip()
    full = _git(repo, "rev-parse", "--verify", "%s^{commit}" % rev, check=False)
    if full is None:
        raise EvalError("cannot resolve --rev %r to a commit" % rev)
    full = full.decode().strip()

    if rounds_spec is None:
        tree = _git(repo, "ls-tree", "-r", "--name-only", full, "--", ".ufo/waves")
        rounds_seen = sorted(
            {
                int(m.group(1))
                for m in (
                    re.match(r"\.ufo/waves/round-(\d+)/", p)
                    for p in tree.decode("utf-8", "surrogateescape").split("\n")
                )
                if m
            }
        )
        if not rounds_seen:
            raise EvalError("no .ufo/waves/round-<N>/ directories at %s" % full[:12])
        spec = "%d-%d" % (rounds_seen[0], rounds_seen[-1])
        rounds_sets = [set(rounds_seen)]
    else:
        spec = rounds_spec
        rounds_sets = parse_rounds(rounds_spec)

    dirs = round_dirs(rounds_sets)
    existing = []
    for d in dirs:
        if _git(repo, "cat-file", "-e", "%s:%s" % (full, d), check=False) is not None:
            existing.append(d)
    if not existing:
        raise EvalError("no selected round directory exists at %s" % full[:12])

    tree = _git(repo, "ls-tree", "-r", "--name-only", full, "--", *existing)
    paths = select_paths(tree.decode("utf-8", "surrogateescape").split("\n"), rounds_sets)
    if not paths:
        raise EvalError("no seat reports in the selected rounds at %s" % full[:12])

    events = _walk_events(repo, full, existing)

    # baseline = most recent add event; everything newer is a later touch
    base_of = {}
    later_of = {}
    unbased = []
    for path in paths:
        base = None
        later = []
        for commit, status, after in events.get(path, []):
            if status == "A" and after == path:
                base = commit
                break
            later.append((commit, status, after))
        if base is None:
            unbased.append(path)
            continue
        base_of[path] = base
        later_of[path] = later

    specs = []
    for path in paths:
        if path in base_of:
            specs.append("%s:%s" % (base_of[path], path))
            specs.append("%s:%s" % (full, path))
        for commit, _status, _after in later_of.get(path, []):
            specs.append("%s:%s" % (commit, path))
        sibling = path[: -len(".md")] + LATE_SUFFIX
        specs.append("%s:%s" % (full, sibling))
    blobs = _blobs(repo, list(dict.fromkeys(specs)))

    m = re.compile(r"^\.ufo/waves/round-(\d+)/")
    violations = []
    restored = []
    for path in paths:
        if path in unbased:
            continue
        base = base_of[path]
        first_blob = blobs.get("%s:%s" % (base, path))
        tip_blob = blobs.get("%s:%s" % (full, path))
        if first_blob is None or tip_blob is None:
            raise EvalError("cannot resolve blob for %s" % path)
        sibling = path[: -len(".md")] + LATE_SUFFIX
        sibling_blob = blobs.get("%s:%s" % (full, sibling))

        commits = []
        seq = []
        for commit, _status, _after in reversed(later_of.get(path, [])):
            blob = blobs.get("%s:%s" % (commit, path))
            commits.append(commit)
            seq.append((commit, blob))
        if not commits:
            continue
        divergent = [b for _c, b in seq if b != first_blob]
        row = {
            "path": path,
            "round": int(m.match(path).group(1)),
            "first_add": base,
            "first_blob": first_blob,
            "tip_blob": tip_blob,
            "commits": commits,
            "later": seq,
            "sibling": (
                "absent"
                if sibling_blob is None
                else ("matches" if sibling_blob in divergent else "differs")
            ),
        }
        if tip_blob == first_blob:
            restored.append(row)
        else:
            violations.append(row)

    violations.sort(key=lambda r: r["path"])
    restored.sort(key=lambda r: r["path"])
    return {
        "status": "ok",
        "rev": full,
        "rounds": spec,
        "reports": len(paths),
        "violations": violations,
        "restored": restored,
        "unbased": unbased,
        "unbased_count": len(unbased),
    }


def exit_code(res):
    if res.get("status") != "ok":
        return 2
    if res["unbased"]:
        return 2  # a report that cannot be graded makes the evaluation incomplete
    return 1 if res["violations"] else 0


def _row_line(tag, row):
    later = ",".join(b if b else "-" for _c, b in row["later"])
    return (
        "%s %s first_add=%s first_blob=%s tip_blob=%s commits=%s later_blobs=%s sibling=%s"
        % (
            tag,
            row["path"],
            row["first_add"],
            row["first_blob"],
            row["tip_blob"],
            ",".join(row["commits"]),
            later,
            row["sibling"],
        )
    )


def report(res, stream=None):
    stream = stream or sys.stdout
    for row in res["violations"]:
        print(_row_line("REWRITTEN", row), file=stream)
    for row in res["restored"]:
        print(_row_line("RESTORED", row), file=stream)
    for path in res["unbased"]:
        print("UNBASED %s" % path, file=stream)
    print(
        "%s rev=%s rounds=%s reports=%d rewritten=%d restored=%d unbased=%d met=%s"
        % (
            NAME,
            res["rev"],
            res["rounds"],
            res["reports"],
            len(res["violations"]),
            len(res["restored"]),
            res["unbased_count"],
            "False" if (res["violations"] or res["unbased"]) else "True",
        ),
        file=stream,
    )


def main_report(repo, rev, rounds_spec):
    try:
        res = evaluate(repo, rev, rounds_spec)
    except EvalError as e:
        print("%s: could-not-evaluate: %s" % (NAME, e))
        return 2
    report(res)
    return exit_code(res)


# ------------------------------------------------------------------ selftest

GIT_ID = [
    "-c",
    "user.name=sri-selftest",
    "-c",
    "user.email=sri-selftest@invalid",
    "-c",
    "commit.gpgsign=false",
]


def _fixture_git(d, *args):
    # fixed timestamps keep the fixture commit ids stable between runs, so the
    # selftest output is a reproducible receipt rather than a fresh hash each time
    env = dict(
        os.environ,
        GIT_AUTHOR_DATE="2026-10-27T00:00:00+00:00",
        GIT_COMMITTER_DATE="2026-10-27T00:00:00+00:00",
        TZ="UTC",
    )
    p = subprocess.run(["git", "-C", d, *GIT_ID, *args], capture_output=True, env=env)
    if p.returncode:
        raise EvalError(
            "fixture git %s failed: %s" % (" ".join(args), p.stderr.decode()[:300])
        )
    return p.stdout


def _workdir():
    """mkdtemp under $TMPDIR (explicitly honoured) with the git fixture inside."""
    base = os.environ.get("TMPDIR") or tempfile.gettempdir()
    os.makedirs(base, exist_ok=True)
    return tempfile.mkdtemp(prefix="sri-", dir=base), base


def _write(d, rel, text):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def _commit(d, msg):
    _fixture_git(d, "add", "-A")
    _fixture_git(d, "commit", "-q", "-m", msg)
    return _fixture_git(d, "rev-parse", "HEAD").decode().strip()


def selftest():
    arms = []

    def arm(name, ok, detail):
        arms.append((name, bool(ok), detail))

    d, base = _workdir()
    try:
        _fixture_git(d, "init", "-q")
        top = _fixture_git(d, "rev-parse", "--show-toplevel").decode().strip()
        if os.path.realpath(top) != os.path.realpath(d):
            raise EvalError("fixture toplevel %s != %s" % (top, d))

        arm(
            "tmpdir-honoured",
            os.path.realpath(d).startswith(os.path.realpath(base) + os.sep),
            "fixture=%s TMPDIR=%s" % (d, base),
        )

        untouched = ".ufo/waves/round-52/w1/out/Untouched.md"
        rewritten = ".ufo/waves/round-52/w1/out/Rewritten.md"
        first_text = "# seat report\n\nverdict: ok\n"
        _write(d, untouched, first_text)
        _write(d, rewritten, first_text)
        _write(d, ".ufo/waves/round-52/w1/out/Rewritten.late-rewrite.md", "x\n")
        _write(d, ".ufo/waves/round-45/w1/out/Old.md", "old\n")
        add = _commit(d, "add seat reports")

        res = evaluate(d, "HEAD", "46-52")
        arm(
            "untouched-reported-once",
            res["reports"] == 2 and not res["violations"] and exit_code(res) == 0,
            "reports=%d violations=%d exit=%d"
            % (res["reports"], len(res["violations"]), exit_code(res)),
        )
        arm(
            "late-rewrite-sibling-not-a-report",
            all(not r["path"].endswith(LATE_SUFFIX) for r in res["violations"]),
            "paths=%d" % res["reports"],
        )

        # rewrite one report in place and commit it
        _write(d, rewritten, first_text + "\nextra: reworded after commit\n")
        edit = _commit(d, "rewrite Rewritten.md in place")
        res = evaluate(d, "HEAD", "46-52")
        v = {r["path"]: r for r in res["violations"]}
        ok = (
            list(v) == [rewritten]
            and res["reports"] == 2
            and exit_code(res) == 1
            and v[rewritten]["first_add"] == add
            and v[rewritten]["commits"] == [edit]
            and v[rewritten]["tip_blob"] != v[rewritten]["first_blob"]
            and v[rewritten]["sibling"] == "differs"
        )
        arm(
            "rewritten-in-place-exits-1",
            ok,
            "rewritten=%d exit=%d commits=%s"
            % (len(res["violations"]), exit_code(res), ",".join(v.get(rewritten, {}).get("commits", []))[:12]),
        )
        arm(
            "untouched-still-clean-in-same-tree",
            untouched not in v,
            "untouched_in_violations=%s" % (untouched in v),
        )

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cli_exit = main_report(d, "HEAD", "46-52")
        text = buf.getvalue()
        line = [l for l in text.splitlines() if l.startswith("REWRITTEN ")]
        ok = (
            cli_exit == 1
            and len(line) == 1
            and "first_add=" in line[0]
            and "first_blob=" in line[0]
            and "tip_blob=" in line[0]
            and ("commits=%s" % edit) in line[0]
            and ("later_blobs=%s" % v[rewritten]["tip_blob"]) in line[0]
            and text.splitlines()[-1].startswith("seat-report-immutability rev=")
        )
        arm("cli-prints-fields-and-exits-1", ok, "exit=%d lines=%d" % (cli_exit, len(line)))

        # keep the divergent bytes in the sibling: still a violation, now disclosed
        _write(
            d,
            ".ufo/waves/round-52/w1/out/Rewritten.late-rewrite.md",
            first_text + "\nextra: reworded after commit\n",
        )
        _commit(d, "file the divergent bytes as late-rewrite")
        res = evaluate(d, "HEAD", "46-52")
        arm(
            "sibling-matching-divergent-bytes",
            len(res["violations"]) == 1 and res["violations"][0]["sibling"] == "matches",
            "sibling=%s" % (res["violations"][0]["sibling"] if res["violations"] else "-"),
        )

        # restore the first bytes: no violation, RESTORED recorded
        _write(d, rewritten, first_text)
        restore = _commit(d, "restore first-add bytes")
        res = evaluate(d, "HEAD", "46-52")
        arm(
            "restoration-exits-0",
            not res["violations"]
            and len(res["restored"]) == 1
            and res["restored"][0]["path"] == rewritten
            and exit_code(res) == 0,
            "restored=%d violations=%d exit=%d"
            % (len(res["restored"]), len(res["violations"]), exit_code(res)),
        )
        arm(
            "restoration-names-both-commits",
            res["restored"] and res["restored"][0]["commits"] == [edit, restore],
            "commits=%s" % (",".join(res["restored"][0]["commits"])[:24] if res["restored"] else "-"),
        )

        # delete + re-add restarts the baseline
        _fixture_git(d, "rm", "-q", rewritten)
        _commit(d, "delete Rewritten.md")
        _write(d, rewritten, "completely new report\n")
        _commit(d, "re-add Rewritten.md")
        res = evaluate(d, "HEAD", "46-52")
        arm(
            "delete-re-add-restarts-baseline",
            not res["violations"] and exit_code(res) == 0,
            "violations=%d exit=%d" % (len(res["violations"]), exit_code(res)),
        )

        # rounds filter: a rewritten report outside the selected rounds is ignored
        _write(d, ".ufo/waves/round-99/w1/out/Future.md", "one\n")
        _commit(d, "add round-99 report")
        _write(d, ".ufo/waves/round-99/w1/out/Future.md", "one\ntwo\n")
        _commit(d, "rewrite round-99 report")
        res46 = evaluate(d, "HEAD", "46-52")
        res99 = evaluate(d, "HEAD", "99")
        arm(
            "rounds-filter",
            not res46["violations"]
            and exit_code(res46) == 0
            and len(res99["violations"]) == 1
            and exit_code(res99) == 1,
            "exit(46-52)=%d exit(99)=%d" % (exit_code(res46), exit_code(res99)),
        )

        # could-not-evaluate paths
        codes = []
        for spec, rev in (("46-52", "no-such-rev"), ("77-78", "HEAD"), ("4x", "HEAD")):
            try:
                bad = evaluate(d, rev, spec)
                codes.append(exit_code(bad))
            except EvalError:
                codes.append(2)
        arm("could-not-evaluate-exits-2", codes == [2, 2, 2], "codes=%s" % codes)

        # non-repository
        outside, _ = _workdir()
        try:
            try:
                evaluate(outside, "HEAD", "46-52")
                codes.append(0)
            except EvalError:
                codes.append(2)
            arm("non-repository-exits-2", codes[-1] == 2, "code=%d" % codes[-1])
        finally:
            shutil.rmtree(outside, ignore_errors=True)
    finally:
        shutil.rmtree(d, ignore_errors=True)

    failed = 0
    for name, ok, detail in arms:
        print("%s %-38s %s" % ("PASS" if ok else "FAIL", name, detail))
        failed += 0 if ok else 1
    print("SEAT_REPORT_IMMUTABILITY_SELFTEST pass=%d fail=%d" % (len(arms) - failed, failed))
    return 0 if failed == 0 else 1


# ------------------------------------------------------------------ main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Grade committed seat reports against their first-add bytes."
    )
    ap.add_argument("--repo", default=".", help="repository to read (default: .)")
    ap.add_argument("--rev", default="HEAD", help="revision to grade (default: HEAD)")
    ap.add_argument(
        "--rounds",
        default=None,
        help="rounds to grade: N, N-M or a comma list (default: every round present)",
    )
    ap.add_argument("--selftest", action="store_true", help="run the fixture matrix")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    return main_report(a.repo, a.rev, a.rounds)


if __name__ == "__main__":
    sys.exit(main())
