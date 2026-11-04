#!/usr/bin/env python3
"""Round-76 C2: committed, value-bound round-75 self-record facts.

Correction wire format (the frozen plan declares semantic, not lexical shape)::

    ### Correction (2026-11-04) — province-digest
    Supersedes: SCORECARD.md:4065
    Revision: <revision of the originally measured blob>
    Corrected: <derived value>

For log-tally, additionally supply Receipt: .ufo/waves/<committed receipt>;
its Revision identifies the receipt commit. No worktree content is evidence.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import date
import hashlib
import io
from pathlib import Path
import re
import shutil
import subprocess
import sys
import types
import zlib

BASE = "b06cc612711560c53eef3ec21484c6963601262f"
PREDICATE = """`python3 tools/round76-selfrecord-facts.py --repo <lane>` prints one `SELFRECORD_FACTS
claims=8 mismatches=0 corrected=5 unbacked=0` line and exits 0 only when each of the eight
declared round-75 self-record facts — the `SKILL.md` sha256 and line count, the `PROVINCE.md`
sha256 and line count, the `corpus/SOURCES.md` registry row count, the filtered
`corpus/knowledge/*.md` entry count, the LOG work tip, the LOG mistake-class count, the LOG
gate-selftest tally's backing receipt and the `## Axes` calibration row's newest-closure
pointer — either re-derives from the blob at the revision it names or is superseded by an
appended dated correction block that names the superseded bytes and states a corrected value
which itself re-derives; it exits 1 naming each `SELFRECORD_FACT <id> filed=<v> derived=<v>`
mismatch and each `SELFRECORD_CORRECTION <id> unbacked|wrong-value` finding, and 2 on
could-not-evaluate (a missing self-record, an unreadable blob, CLI misuse)."""
TALLY = "PRE_REPORT_SELFTEST pass=18 fail=0"
CLOSURE_TOOL = "tools/round69-newest-closure-counter.py"


class CouldNotEvaluate(Exception):
    """Maps incomplete evidence to exit 2, never clean."""


def git(repo, *args):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True)
    if result.returncode:
        raise CouldNotEvaluate(result.stderr.decode(errors="replace").strip())
    return result.stdout


def blob(repo, rev, path):
    return git(repo, "show", f"{rev}:{path}")


def text(repo, rev, path):
    return blob(repo, rev, path).decode("utf-8")


def match(pattern, value):
    found = re.search(pattern, value, re.M | re.S)
    if not found:
        raise CouldNotEvaluate(f"missing declared fact: {pattern}")
    return found


def section(value, heading):
    found = match(heading, value)
    end = re.search(r"^## ", value[found.end():], re.M)
    stop = found.end() + end.start() if end else len(value)
    return value[found.start():stop], found.start()


def record_path(path):
    # The inherited round-72 record set; PROVINCE.md remains work, not record.
    return path in {"LOG.md", "SCORECARD.md", "corpus/README.md"} or path.startswith((
        "corpus/lessons/", ".ufo/waves/round-75/"))


def worktip(repo, rev, freeze):
    # Seal the round at its outside closure, not at an asserted work-tip token.
    closure = "corpus/lessons/round-75-verifier-spotcheck.md"
    introductions = git(repo, "log", "--format=%H", "--diff-filter=A", rev, "--", closure).decode().splitlines()
    boundary = introductions[-1] if introductions else rev
    for commit in git(repo, "rev-list", "--first-parent", f"{freeze}..{boundary}").decode().splitlines():
        paths = git(repo, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit).decode().splitlines()
        if any(not record_path(path) for path in paths):
            return commit
    raise CouldNotEvaluate("no non-record work commit after LOG freeze")


def closure_module(repo, rev):
    module = types.ModuleType("round69_closure")
    exec(compile(blob(repo, rev, CLOSURE_TOOL), CLOSURE_TOOL, "exec"), module.__dict__)
    return module


def tally_backed(repo, rev, path=None, tally=TALLY):
    paths = [path] if path else git(repo, "ls-tree", "-r", "--name-only", rev, "--", ".ufo/waves/round-75/").decode().splitlines()
    for name in paths:
        if not name.startswith(".ufo/waves/") or ".." in Path(name).parts:
            continue
        # Markdown records and executable source are not backing run receipts.
        if Path(name).suffix not in {".out", ".txt", ".stdout", ".log"}:
            continue
        if name.endswith("correction-template.txt"):
            continue
        if tally.encode() in blob(repo, rev, name):
            return True
    return False


def facts(repo, rev):
    score = text(repo, rev, "SCORECARD.md")
    log = text(repo, rev, "LOG.md")
    score75, score_offset = section(score, r"^## Round 75[^\n]*")
    log75, log_offset = section(log, r"^## Round 75[^\n]*")
    population = match(r"^Axis harm check:[^\n]*", score75)
    line = population.group()
    measured = match(r"Population at `rev=([0-9a-f]{40})`", line).group(1)
    freeze = match(r"freeze `([0-9a-f]{40})`", log75).group(1)
    result = []

    def add(identity, filed, derived, path, position, revision):
        source = score if path == "SCORECARD.md" else log
        result.append(dict(id=identity, filed=str(filed), derived=str(derived), path=path,
                           line=source.count("\n", 0, position) + 1, pos=position,
                           revision=revision))

    pos = score_offset + population.start()
    for path, prefix in [("SKILL.md", "skill"), ("PROVINCE.md", "province")]:
        declaration = match(re.escape(f"`{path}`") + r" (\d+) lines sha256 `([0-9a-f]{64})`", line)
        data = blob(repo, measured, path)
        add(prefix + "-digest", declaration.group(2), hashlib.sha256(data).hexdigest(), "SCORECARD.md", pos, measured)
        add(prefix + "-lines", declaration.group(1), data.count(b"\n"), "SCORECARD.md", pos, measured)
    rows = sum(bool(re.match(rb"^ {0,3}\|\s*S[0-9]{3,}", row)) for row in blob(repo, measured, "corpus/SOURCES.md").splitlines())
    add("sources-rows", match(r"sources census exit 0 over (\d+) rows", line).group(1), rows, "SCORECARD.md", pos, measured)
    names = git(repo, "ls-tree", "--name-only", f"{measured}:corpus/knowledge").decode().splitlines()
    entries = sum(name.endswith(".md") and "engine-sides" not in name and "processes" not in name for name in names)
    add("knowledge-entries", match(r"filtered knowledge entries (\d+)", line).group(1), entries, "SCORECARD.md", pos, measured)
    tip = match(r"work tip `([0-9a-f]{40})`", log75)
    add("log-worktip", tip.group(1), worktip(repo, rev, freeze), "LOG.md", log_offset + tip.start(), measured)
    mistakes = match(r"\((\w+) mistake classes,", log75)
    numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    raw = mistakes.group(1)
    count = numbers[raw] if raw in numbers else int(raw)
    lesson = text(repo, rev, "corpus/lessons/round-75.md")
    derived = len(re.findall(r"^[0-9]+\. \*\*`", lesson, re.M))
    add("log-mistakes", count, derived, "LOG.md", log_offset + mistakes.start(), rev)
    tally = match(re.escape(TALLY), log75)
    add("log-tally", TALLY, TALLY if tally_backed(repo, rev) else "unbacked", "LOG.md", log_offset + tally.start(), rev)
    module = closure_module(repo, rev)
    try:
        population = module._closure_population(str(repo), rev, 63)
        newest = max((module._closure_date(str(repo), rev, name)[0], rnd, name) for name, rnd in population)[2]
        filed = module._calibration_row(str(repo), rev)
    except module.CouldNotEvaluate as exc:
        raise CouldNotEvaluate(str(exc)) from exc
    row = match(r"^\|\s*\*{0,2}calibration\*{0,2}\s*\|[^\n]*", score)
    add("closure-pointer", filed, f"corpus/lessons/{newest}", "SCORECARD.md", row.start(), rev)
    return result, {"SCORECARD.md": score, "LOG.md": log}


def apply_correction(repo, rev, fact, source):
    pattern = r"^### Correction \((\d{4}-\d{2}-\d{2})\) [—-] " + re.escape(fact["id"]) + r"\s*$"
    blocks = list(re.finditer(pattern, source, re.M))
    for heading in reversed(blocks):
        if heading.start() <= fact["pos"]:
            continue
        try:
            date.fromisoformat(heading.group(1))
        except ValueError:
            continue
        rest = source[heading.end():]
        end = re.search(r"^#{1,3} ", rest, re.M)
        block = rest[:end.start()] if end else rest
        fields = dict(re.findall(r"^(Supersedes|Revision|Corrected|Receipt):[ \t]*(.+?)\s*$", block, re.M))
        locator = f'{fact["path"]}:{fact["line"]}'
        if fields.get("Supersedes") not in {locator, fact["filed"]}:
            continue
        value = fields.get("Corrected")
        expected = fact["derived"]
        correction_rev = fields.get("Revision", "")
        if not re.fullmatch(r"[0-9a-f]{40}", correction_rev):
            return "wrong-value"
        git(repo, "merge-base", "--is-ancestor", correction_rev, rev)
        if fact["id"] == "log-tally":
            if value == "unbacked":
                return "unbacked"
            tally = value.removeprefix("historical-unbacked; ") if value else ""
            if not re.fullmatch(r"PRE_REPORT_SELFTEST pass=[0-9]+ fail=0", tally):
                return "wrong-value"
            if not fields.get("Receipt") or not tally_backed(repo, correction_rev, fields["Receipt"], tally):
                return "unbacked"
            if tally != TALLY and not value.startswith("historical-unbacked; "):
                return "wrong-value"
            return "corrected"
        if fact["id"] in {"skill-digest", "skill-lines", "province-digest", "province-lines", "sources-rows", "knowledge-entries", "log-worktip"}:
            if correction_rev != fact["revision"]:
                return "wrong-value"
        else:
            if correction_rev != rev:
                # Revision must name the same immutable evidence, not merely an ancestor.
                evidence_path = "corpus/lessons/round-75.md" if fact["id"] == "log-mistakes" else fact["derived"]
                if blob(repo, correction_rev, evidence_path) != blob(repo, rev, evidence_path):
                    return "wrong-value"
        if value != expected:
            return "wrong-value"
        return "corrected"
    return None


def audit(repo, rev):
    checks, records = facts(repo, rev)
    mismatches = corrected = unbacked = 0
    lines = []
    for fact in checks:
        correction = apply_correction(repo, rev, fact, records[fact["path"]])
        if correction == "corrected":
            corrected += 1
            continue
        if correction:
            lines.append(f'SELFRECORD_CORRECTION {fact["id"]} {correction}')
        if fact["filed"] != fact["derived"] or correction:
            mismatches += 1
            unbacked += fact["id"] == "log-tally" and fact["derived"] == "unbacked"
            lines.append(f'SELFRECORD_FACT {fact["id"]} filed={fact["filed"]} derived={fact["derived"]}')
            if fact["id"] == "log-tally" and not correction:
                lines.append("SELFRECORD_CORRECTION log-tally unbacked")
    print(f"SELFRECORD_FACTS claims=8 mismatches={mismatches} corrected={corrected} unbacked={unbacked}")
    print("\n".join(lines), end="\n" if lines else "")
    return int(bool(mismatches))


def probe(program, repo, rev):
    result = subprocess.run([sys.executable, str(program), "--repo", str(repo), "--rev", rev], capture_output=True, text=True)
    return result.returncode, result.stdout


class Fixture:
    """Small real Git object store, without running any Git mutation command."""
    def __init__(self, root):
        self.root = root
        (root / ".git/objects").mkdir(parents=True)
        (root / ".git/refs/heads").mkdir(parents=True)
        (root / ".git/HEAD").write_text("ref: refs/heads/main\n")
        (root / ".git/config").write_text("[core]\nrepositoryformatversion = 0\nbare = false\n")
        self.files = {}
        self.head = None

    def obj(self, kind, data):
        raw = kind.encode() + b" " + str(len(data)).encode() + b"\0" + data
        oid = hashlib.sha1(raw).hexdigest()
        target = self.root / ".git/objects" / oid[:2] / oid[2:]
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(zlib.compress(raw))
        return oid

    def commit(self):
        def tree(files):
            children = {}
            for path, data in files.items():
                first, sep, rest = path.partition("/")
                if sep:
                    children.setdefault(first, {})[rest] = data
                else:
                    children[first] = data
            entries = []
            for name, data in sorted(children.items(), key=lambda item: item[0] + ("/" if isinstance(item[1], dict) else "")):
                directory = isinstance(data, dict)
                oid = tree(data) if directory else self.obj("blob", data)
                entries.append((b"40000" if directory else b"100644") + b" " + name.encode() + b"\0" + bytes.fromhex(oid))
            return self.obj("tree", b"".join(entries))
        content = f"tree {tree(self.files)}\n"
        if self.head:
            content += f"parent {self.head}\n"
        content += "author Fixture <fixture@example.invalid> 1793750400 +0000\ncommitter Fixture <fixture@example.invalid> 1793750400 +0000\n\nfixture\n"
        self.head = self.obj("commit", content.encode())
        (self.root / ".git/refs/heads/main").write_text(self.head + "\n")
        return self.head


def correction_block(fact, value, revision=None, receipt=None):
    out = (f'### Correction (2026-11-04) — {fact["id"]}\n'
           f'Supersedes: {fact["path"]}:{fact["line"]}\n'
           f'Revision: {revision or fact["revision"]}\nCorrected: {value}\n')
    return out + (f"Receipt: {receipt}\n" if receipt else "") + "\n"


def run_selftest(repo, work):
    root = Path(work).resolve() / "selfrecord-fixtures"
    if root.exists():
        raise CouldNotEvaluate(f"fixture directory already exists: {root}")
    fixture = Fixture(root)
    passed = failed = 0

    def check(name, condition):
        nonlocal passed, failed
        passed += bool(condition)
        failed += not condition
        print(f"SELFRECORD_FACTS_ARM {name} {'PASS' if condition else 'FAIL'}")

    try:
        # Preserve the real base record bytes and measured data, replacing only
        # revision identities so all derivations run against this fixture graph.
        score = text(repo, BASE, "SCORECARD.md")
        log = text(repo, BASE, "LOG.md")
        measured = match(r"Population at `rev=([0-9a-f]{40})`", section(score, r"^## Round 75[^\n]*")[0]).group(1)
        freeze_original = match(r"freeze `([0-9a-f]{40})`", section(log, r"^## Round 75[^\n]*")[0]).group(1)
        fixture.files[CLOSURE_TOOL] = blob(repo, BASE, CLOSURE_TOOL)
        freeze = fixture.commit()
        paths = ["SKILL.md", "PROVINCE.md", "corpus/SOURCES.md"]
        paths += git(repo, "ls-tree", "-r", "--name-only", measured, "--", "corpus/knowledge/").decode().splitlines()
        for path in paths:
            fixture.files[path] = blob(repo, measured, path)
        measured_fixture = fixture.commit()
        fixture.files["SCORECARD.md"] = score.replace(measured, measured_fixture).encode()
        fixture.files["LOG.md"] = log.replace(freeze_original, freeze).encode()
        fixture.files["corpus/lessons/round-75.md"] = blob(repo, BASE, "corpus/lessons/round-75.md")
        for path in git(repo, "ls-tree", "-r", "--name-only", BASE, "--", "corpus/lessons/").decode().splitlines():
            if re.fullmatch(r"corpus/lessons/round-(?:6[3-9]|7[0-5])-verifier-spotcheck\.md", path):
                fixture.files[path] = blob(repo, BASE, path)
        red = fixture.commit()
        program = Path(__file__).resolve()
        rc, output = probe(program, root, red)
        expected_ids = {"province-digest", "log-worktip", "log-mistakes", "log-tally", "closure-pointer"}
        observed = set(re.findall(r"^SELFRECORD_FACT (\S+)", output, re.M))
        check("red-at-base", rc == 1 and observed == expected_ids and "mismatches=5 corrected=0 unbacked=1" in output)
        checks, _ = facts(root, red)
        province = next(f for f in checks if f["id"] == "province-digest")
        original = fixture.files["SCORECARD.md"]
        fixture.files["SCORECARD.md"] = original + ("\n" + correction_block(province, province["filed"])).encode()
        wrong = fixture.commit()
        rc, output = probe(program, root, wrong)
        check("correction-wrong-value", rc == 1 and "SELFRECORD_CORRECTION province-digest wrong-value" in output and "mismatches=5" in output)
        fixture.files["SCORECARD.md"] = original + ("\n" + correction_block(province, province["derived"])).encode()
        good = fixture.commit()
        rc, output = probe(program, root, good)
        check("correction-value-bound", rc == 1 and "mismatches=4 corrected=1 unbacked=1" in output and "SELFRECORD_FACT province-digest" not in output)
        # Remove the sealing closure, add real work, then publish a new closure.
        # Fork before the first closure: later work must precede publication.
        fixture.head = measured_fixture
        closure = fixture.files.pop("corpus/lessons/round-75-verifier-spotcheck.md")
        fixture.commit()
        fixture.files["tools/later-work.py"] = b"print('later work')\n"
        later = fixture.commit()
        fixture.files["corpus/lessons/round-75-verifier-spotcheck.md"] = closure
        flipped = fixture.commit()
        check("worktip-graph", worktip(root, flipped, freeze) == later and later != measured_fixture)
        cheat = root / "cheat.py"
        cheat.write_text('print("SELFRECORD_FACTS claims=8 mismatches=0 unbacked=0 corrected=0")\n')
        rc, output = probe(cheat, root, red)
        check("cheat-zeros", not (rc == 1 and set(re.findall(r"^SELFRECORD_FACT (\S+)", output, re.M)) == expected_ids))
    finally:
        shutil.rmtree(root)
    print(f"SELFRECORD_FACTS_SELFTEST pass={passed} fail={failed}")
    return int(bool(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--rev", default="HEAD")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--work")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            if not args.work:
                raise CouldNotEvaluate("--selftest requires --work")
            return run_selftest(Path(args.repo).resolve(), args.work)
        rev = git(args.repo, "rev-parse", "--verify", args.rev + "^{commit}").decode().strip()
        return audit(args.repo, rev)
    except (CouldNotEvaluate, OSError, UnicodeError, ValueError) as exc:
        print(f"SELFRECORD_FACTS CouldNotEvaluate: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
