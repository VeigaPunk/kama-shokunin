#!/usr/bin/env python3
"""Re-derive six sealed round-76 facts; accept only appended value-bound corrections.

Records and evidence are committed blobs, never worktree Markdown. --rev selects
where appended corrections are read; RECORD_REV fixes the original declarations.
Selftest fixtures are restricted to the caller's explicit --work directory.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import date
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
_SPEC = importlib.util.spec_from_file_location(
    "round76_selfrecord", Path(__file__).with_name("round76-selfrecord-facts.py"))
_PREVIOUS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREVIOUS)
CouldNotEvaluate = _PREVIOUS.CouldNotEvaluate
git, blob, text = _PREVIOUS.git, _PREVIOUS.blob, _PREVIOUS.text
match, section = _PREVIOUS.match, _PREVIOUS.section

RECORD_REV = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
FREEZE = "1a85a991fce5b76b60f88a5cab3df98d253b1a4a"
TALLY = "PRE_REPORT_SELFTEST pass=21 fail=0"
PREDICATE = """`python3 tools/round77-selfrecord-round76.py --repo <lane>` prints one `SELFRECORD_R76
claims=6 mismatches=0 corrected=2 unbacked=0` line and exits 0 only when each of the six
declared round-76 self-record facts — the work tip, the gate-selftest tally's backing receipt,
the capability count against the round-76 canonical table, the filtered knowledge-entry count
at the revision the record names, the `corpus/SOURCES.md` registry row count at that revision,
and the `## Axes` calibration row's newest-closure pointer — either re-derives from the blob at
the revision it names or is superseded by an appended dated correction block that names the
superseded bytes and states a corrected value which itself re-derives; it exits 1 naming each
`SELFRECORD_R76_FACT <id> filed=<v> derived=<v>` mismatch and each `SELFRECORD_R76_CORRECTION
<id> unbacked|wrong-value`, and 2 on could-not-evaluate (a missing self-record, an unreadable
blob, CLI misuse)."""


def record_path(path):
    return _PREVIOUS.record_path(path) or path.startswith(".ufo/waves/round-76/")


def worktip(repo, rev, freeze):
    closure = "corpus/lessons/round-76-verifier-spotcheck.md"
    introductions = git(repo, "log", "--format=%H", "--diff-filter=A", rev,
                        "--", closure).decode().splitlines()
    if not introductions:
        raise CouldNotEvaluate("missing round-76 sealing closure introduction")
    for commit in git(repo, "rev-list", "--first-parent",
                      f"{freeze}..{introductions[-1]}").decode().splitlines():
        paths = git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only",
                    "-r", commit).decode().splitlines()
        if any(not record_path(path) for path in paths):
            return commit
    raise CouldNotEvaluate("no non-record work commit after round-76 freeze")


def tally_backed(repo, rev):
    paths = git(repo, "ls-tree", "-r", "--name-only", rev, "--",
                ".ufo/waves/round-76/").decode().splitlines()
    return any(Path(path).suffix in {".out", ".txt", ".stdout", ".log"}
               and TALLY in text(repo, rev, path).splitlines() for path in paths)


def facts(repo, record_rev=RECORD_REV, freeze=FREEZE):
    records = {path: text(repo, record_rev, path) for path in ("SCORECARD.md", "LOG.md")}
    score, log = records["SCORECARD.md"], records["LOG.md"]
    score76, score_offset = section(score, r"^## Round 76[^\n]*")
    log76, log_offset = section(log, r"^## Round 76[^\n]*")
    population = match(r"Population at `rev=([0-9a-f]{8})`:(.*?)(?:\n\n|\Z)", score76)
    measured = git(repo, "rev-parse", "--verify", population.group(1) + "^{commit}").decode().strip()
    result = []

    def add(identity, filed, derived, path, position, revision=record_rev):
        result.append(dict(id=identity, filed=str(filed), derived=str(derived), path=path,
                           pos=position, line=records[path].count("\n", 0, position) + 1,
                           revision=revision))

    tip = match(r"work tip `([0-9a-f]{40})`", log76)
    add("work-tip", tip.group(1), worktip(repo, record_rev, freeze), "LOG.md", log_offset + tip.start())
    tally = match(re.escape(TALLY), log76)
    add("gate-tally", TALLY, TALLY if tally_backed(repo, record_rev) else "unbacked",
        "LOG.md", log_offset + tally.start())
    retired, retired_offset = section(score, r"^## Retired\s*$")
    capability = match(r"6 axes and (\d+) capabilities remain active", retired)
    canonical = match(r"^\*\*Capabilities — canonical list as of round 76\*\*\s*$", score76)
    table = score76[canonical.end():].lstrip().split("\n\n", 1)[0]
    rows = [row for row in table.splitlines() if row.startswith("|")]
    if len(rows) < 3:
        raise CouldNotEvaluate("empty round-76 canonical capability table")
    add("capability-count", capability.group(1), len(rows) - 2, "SCORECARD.md",
        retired_offset + capability.start())
    names = git(repo, "ls-tree", "--name-only", f"{measured}:corpus/knowledge").decode().splitlines()
    entries = sum(name.endswith(".md") and "engine-sides" not in name and "processes" not in name
                  for name in names)
    position = score_offset + population.start()
    add("knowledge-entries", match(r"filtered knowledge entries (\d+)", population.group()).group(1),
        entries, "SCORECARD.md", position, measured)
    rows = sum(bool(re.match(rb"^ {0,3}\|\s*S[0-9]{3,}", row))
               for row in blob(repo, measured, "corpus/SOURCES.md").splitlines())
    add("sources-rows", match(r"sources census (\d+) rows", population.group()).group(1),
        rows, "SCORECARD.md", position, measured)
    module = _PREVIOUS.closure_module(repo, record_rev)
    try:
        population = module._closure_population(str(repo), record_rev, 63)
        newest = max((module._closure_date(str(repo), record_rev, name)[0], number, name)
                     for name, number in population)[2]
        filed = module._calibration_row(str(repo), record_rev)
    except module.CouldNotEvaluate as exc:
        raise CouldNotEvaluate(str(exc)) from exc
    axes, offset = section(score, r"^## Axes\s*$")
    row = match(r"^\|\s*\*{0,2}calibration\*{0,2}\s*\|[^\n]*", axes)
    add("closure-pointer", filed, "corpus/lessons/" + newest, "SCORECARD.md", offset + row.start())
    return result, records


def correction_blocks(source, identity):
    pattern = r"^### Correction \(([^\n]+)\) — " + re.escape(identity) + r"[ \t]*$"
    for heading in re.finditer(pattern, source, re.M):
        rest = source[heading.end():]
        end = re.search(r"^#{1,3} ", rest, re.M)
        body = rest[:end.start()] if end else rest
        yield heading, body


def apply_correction(repo, rev, fact, source, sealed):
    # Historical corrections already in the sealed record belong to round 75,
    # even where their ids coincide with this round's declared fact population.
    old = {(h.group(), b.strip()) for h, b in correction_blocks(sealed, fact["id"])}
    found = list(correction_blocks(source, fact["id"]))
    for heading, body in reversed(found):
        if (heading.group(), body.strip()) in old:
            continue
        try:
            date.fromisoformat(heading.group(1))
        except ValueError:
            return "wrong-value"
        fields = dict(re.findall(r"^(Supersedes|Revision|Corrected):[ \t]*([^\n]+)", body, re.M))
        fields = {key: value.strip() for key, value in fields.items()}
        locator = f'{fact["path"]}:{fact["line"]}'
        # Locate the superseded bytes in the read record, not a shifted line number.
        # A head section the contract re-derives in place (`## Axes`) no longer holds the
        # sealed bytes, so its sealed position is the stable "after the superseded text"
        # anchor there; every append-only section is still located by its surviving bytes.
        original_line = sealed.splitlines()[fact["line"] - 1]
        position = source.find(original_line)
        if position < 0:
            position = fact["pos"]
        if (heading.start() <= position
                or fields.get("Supersedes") not in {locator, fact["filed"]}):
            return "wrong-value"
        revision = fields.get("Revision", "")
        if not re.fullmatch(r"[0-9a-f]{40}", revision):
            return "wrong-value"
        ancestry = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                                   revision, rev], capture_output=True)
        if ancestry.returncode:
            return "wrong-value"
        if fact["id"] in {"knowledge-entries", "sources-rows"} and revision != fact["revision"]:
            return "wrong-value"
        if fact["id"] == "gate-tally" and not tally_backed(repo, revision):
            return "unbacked"
        return "corrected" if fields.get("Corrected") == fact["derived"] else "wrong-value"
    return None


def audit(repo, rev, record_rev=RECORD_REV, freeze=FREEZE):
    checks, sealed = facts(repo, record_rev, freeze)
    records = {path: text(repo, rev, path) for path in sealed}
    mismatches = corrected = unbacked = 0
    findings = []
    for fact in checks:
        correction = apply_correction(repo, rev, fact, records[fact["path"]], sealed[fact["path"]])
        if correction == "corrected":
            corrected += 1
            continue
        if correction:
            findings.append(f'SELFRECORD_R76_CORRECTION {fact["id"]} {correction}')
        if fact["filed"] != fact["derived"] or correction:
            mismatches += 1
            findings.append(f'SELFRECORD_R76_FACT {fact["id"]} filed={fact["filed"]} derived={fact["derived"]}')
        if fact["id"] == "gate-tally" and fact["derived"] == "unbacked":
            unbacked += 1
            if not correction:
                findings.append("SELFRECORD_R76_CORRECTION gate-tally unbacked")
    print(f"SELFRECORD_R76 claims=6 mismatches={mismatches} corrected={corrected} unbacked={unbacked}")
    for line in findings:
        print(line)
    return int(bool(mismatches))


def run_selftest(repo, work):
    root = Path(work).resolve() / "selfrecord-r76-fixture"
    if root.exists():
        raise CouldNotEvaluate(f"fixture directory already exists: {root}")
    root.mkdir(parents=True)
    passed = failed = 0

    def check(name, condition):
        nonlocal passed, failed
        passed += bool(condition)
        failed += not condition
        print(f"SELFRECORD_R76_SELFTEST {name} {'PASS' if condition else 'FAIL'}")

    try:
        subprocess.run(["git", "-C", str(root), "init", "-q"], check=True, capture_output=True)
        if git(root, "rev-parse", "--show-toplevel").decode().strip() != str(root):
            raise CouldNotEvaluate("fixture repository root mismatch")
        fixture = _PREVIOUS.Fixture.__new__(_PREVIOUS.Fixture)
        fixture.root, fixture.files, fixture.head = root, {}, None
        freeze = fixture.commit()
        checks, records = facts(repo)
        measured = next(f["revision"] for f in checks if f["id"] == "knowledge-entries")
        paths = git(repo, "ls-tree", "-r", "--name-only", measured, "--",
                    "corpus/knowledge/").decode().splitlines() + ["corpus/SOURCES.md"]
        for path in paths:
            fixture.files[path] = blob(repo, measured, path)
        population_rev = fixture.commit()
        fixture.files[_PREVIOUS.CLOSURE_TOOL] = blob(repo, RECORD_REV, _PREVIOUS.CLOSURE_TOOL)
        fixture.files["tools/work.py"] = b"print('work')\n"
        work_tip = fixture.commit()
        for path in git(repo, "ls-tree", "-r", "--name-only", RECORD_REV, "--",
                        "corpus/lessons/").decode().splitlines():
            if re.fullmatch(r"corpus/lessons/round-(?:6[3-9]|7[0-6])-verifier-spotcheck\.md", path):
                fixture.files[path] = blob(repo, RECORD_REV, path)
        fixture.files[".ufo/waves/round-76/tally.out"] = (TALLY + "\n").encode()
        original_tip = next(f["filed"] for f in checks if f["id"] == "work-tip")
        fixture.files["SCORECARD.md"] = records["SCORECARD.md"].replace(measured[:8], population_rev[:8]).encode()
        fixture.files["LOG.md"] = records["LOG.md"].replace(original_tip, work_tip).encode()
        red = fixture.commit()

        def probe(rev):
            stream = io.StringIO()
            with redirect_stdout(stream):
                try:
                    code = audit(root, rev, red, freeze)
                except CouldNotEvaluate as exc:
                    print(f"SELFRECORD_R76 CouldNotEvaluate: {exc}")
                    code = 2
            return code, stream.getvalue()

        def stale(code, output):
            return code == 1 and set(re.findall(r"^SELFRECORD_R76_FACT (\S+)", output, re.M)) == {
                "knowledge-entries", "closure-pointer"}

        code, output = probe(red)
        check("stale-uncorrected", stale(code, output))
        fixture_checks, _ = facts(root, red, freeze)
        fact = next(f for f in fixture_checks if f["id"] == "knowledge-entries")
        original = fixture.files["SCORECARD.md"]
        fixture.files["SCORECARD.md"] = original + ("\n" + _PREVIOUS.correction_block(fact, fact["filed"])).encode()
        wrong = fixture.commit()
        code, output = probe(wrong)
        check("correction-wrong-value", stale(code, output) and
              "SELFRECORD_R76_CORRECTION knowledge-entries wrong-value" in output)
        fixture.files.pop("SCORECARD.md")
        missing = fixture.commit()
        code, output = probe(missing)
        check("missing-record", code == 2 and "CouldNotEvaluate" in output)
        cheat = root / "cheat.py"
        cheat.write_text('print("SELFRECORD_R76 claims=6 mismatches=0 corrected=2 unbacked=0")\n')
        result = subprocess.run([sys.executable, str(cheat), "--repo", str(root)],
                                capture_output=True, text=True)
        check("cheat-constant", not stale(result.returncode, result.stdout))
    finally:
        shutil.rmtree(root)
    print(f"SELFRECORD_R76_SELFTEST pass={passed} fail={failed}")
    return int(bool(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="master")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--work")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    try:
        repo = Path(args.repo).resolve()
        if args.selftest:
            # Scratch discipline (round-77 §7): honour TMPDIR; --work is optional.
            owned = None
            if not args.work:
                owned = tempfile.mkdtemp(prefix="selfrecord-r76-root-",
                                         dir=os.environ.get("TMPDIR") or tempfile.gettempdir())
            try:
                return run_selftest(repo, args.work or owned)
            finally:
                if owned:
                    shutil.rmtree(owned, ignore_errors=True)
        rev = git(repo, "rev-parse", "--verify", args.rev + "^{commit}").decode().strip()
        return audit(repo, rev)
    except (CouldNotEvaluate, OSError, UnicodeError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"SELFRECORD_R76 CouldNotEvaluate: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
