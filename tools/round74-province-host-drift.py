#!/usr/bin/env python3
"""round74-province-host-drift.py - grade PROVINCE.md's host identity with base-revision preservation.

Round-74 C3 instrument (freshness). It composes the byte-frozen round-73 counter as
its base leg and adds the preservation leg the round-73 closure item 5 asked for:
a host-identity block carrying a `recorded at <40-hex>` token must be byte-identical
at the recorded revision and at the worktree tip, so a block edited into matching
the live triple is a finding the base leg cannot see.

Resolution rule: the recorded bytes are the ordinal-matched block's compared text
in the token rev's tree (`git show <rev>:PROVINCE.md`). When the block is absent
there - the round-74 control fixtures and the lane's own record commit gain the
token naming a base rev that predates the block's appearance - the resolution
walks forward (`git rev-list --reverse <rev>..HEAD -- <file>`) to the first commit
that carries the block: the recording commit proper. A rev that does not resolve
at all is could-not-evaluate. A block never committed through the tip is a finding.

Token semantics (fixed by the round-74 record): the token sentence - from the
`recorded at <rev>` match to the end of the paragraph - is the pointer, not the
payload. It is stripped from both sides before the byte comparison, because the
lane's own newest block gains the token in the round-74 record commit after the
revision the token names; gaining the pointer is the honest flow and must not
self-fail. Every byte before the token (header date, triple, notes) is compared.

Exit map: 0 clean (base leg green, edited=0), 1 findings (no-block / stale-host /
edited-block), 2 could-not-evaluate (PROVINCE.md unreadable, a `recorded at` rev
unresolvable, the base leg could-not-evaluate, CLI misuse). Nothing on the host is
written; git is only read (rev-parse / show / rev-list).

Selftest: --selftest builds git fixture repos under --work (or a TMPDIR temp dir),
including replays of the committed c3_edited / c3_clean kill and clean fixture
shapes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve()
LANE = TOOL.parent.parent
BASE_TOOL = TOOL.parent / "round73-province-host-drift.py"
PLAN_NAME = "plans/round-74-claims.md"
PROVINCE_NAME = "PROVINCE.md"
PROBE_TIMEOUT = 30

PREDICATE = "`python3 tools/round74-province-host-drift.py --repo <lane>` prints one `PROVINCE_HOST_DRIFT_V2 blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n> edited=<e>` line and exits 0 only when the byte-frozen `tools/round73-province-host-drift.py` verdict for `<lane>` is green and every host-identity block carrying a `recorded at <rev>` token has byte-identical block text at `<rev>` and at the worktree tip, so that a block whose recorded triple, date or any other byte changed after its recorded revision is a finding even when the edited block matches the live triple; it exits 1 naming `PROVINCE_HOST_DRIFT_V2_FINDING <no-block|stale-host|edited-block> <detail>` and 2 on could-not-evaluate (PROVINCE.md unreadable, a `recorded at` rev unresolvable, CLI misuse)."

BLOCK_HEADER_RE = re.compile(
    r"^\s*\*{0,2}Round-(\d+)\s+host-identity\s+block\s+\((\d{4}-\d{2}-\d{2})\)")
RECORDED_AT_RE = re.compile(r"recorded\s+at\s+([0-9a-fA-F]{40})")
SUMMARY_RE = re.compile(
    r"^PROVINCE_HOST_DRIFT_V2 blocks=(\d+) recorded=(\S+) live=(\S+) "
    r"stale=(\d+) edited=(\d+)$", re.M)

GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
         "-c", "commit.gpgsign=false"]


class ProbeError(Exception):
    """The province file, the live host, or a recorded revision cannot be evaluated."""


def read_text(path):
    try:
        return Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise ProbeError(f"cannot read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ProbeError(f"{path} is not UTF-8: {exc}") from exc


def paragraphs(text):
    """Return (first line number, lines) for every blank-line-separated paragraph."""
    out = []
    lines = []
    start = 0
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip():
            if not lines:
                start = number
            lines.append(line)
        elif lines:
            out.append((start, lines))
            lines = []
    if lines:
        out.append((start, lines))
    return out


def parse_blocks(text):
    """Return every host-identity block in file order, with its compared text."""
    blocks = []
    for line_no, lines in paragraphs(text):
        header = BLOCK_HEADER_RE.match(lines[0])
        if not header:
            continue
        paragraph = " ".join(line.strip() for line in lines)
        token = RECORDED_AT_RE.search(paragraph)
        blocks.append({
            "line": line_no,
            "round": int(header.group(1)),
            "date": header.group(2),
            "text": paragraph,
            "recorded_at": token.group(1) if token else None,
        })
    return blocks


def compared_text(block_text):
    """The block text with the `recorded at <rev>` token sentence stripped.

    The token sentence runs from the `recorded at` match to the end of the
    paragraph: it is the pointer at the recorded revision, not the recorded
    payload, and gaining it after the recorded revision is the honest flow.
    """
    match = RECORDED_AT_RE.search(block_text)
    if not match:
        return block_text
    return block_text[:match.start()].rstrip()


def run_git(repo, args, timeout=PROBE_TIMEOUT):
    try:
        proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                              text=True, timeout=timeout)
    except OSError as exc:
        raise ProbeError(f"git: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProbeError(f"git {' '.join(args)}: timed out") from exc
    return proc


def block_text_at(repo, commit, filename, ordinal):
    """Compared text of the ordinal-th host block at commit, or None if absent."""
    shown = run_git(repo, ["show", f"{commit}:{filename}"])
    if shown.returncode != 0:
        return None
    blocks = parse_blocks(shown.stdout.replace("\r\n", "\n"))
    if ordinal >= len(blocks):
        return None
    return compared_text(blocks[ordinal]["text"])


def resolve_recorded_text(repo, rev, filename, ordinal):
    """Resolve the recorded bytes of a token-carrying block.

    Returns (status, resolved_commit, text): status "rev" when the block exists
    in the token rev's tree, "forward" when the resolution walked to the first
    commit carrying the block (the recording commit), "absent" when no commit
    from the token rev through the tip carries it. An unresolvable rev raises
    ProbeError (could-not-evaluate).
    """
    verified = run_git(repo, ["rev-parse", "--verify", f"{rev}^{{commit}}"])
    if verified.returncode != 0:
        detail = (verified.stderr or verified.stdout).strip()
        raise ProbeError(f"recorded at rev unresolvable: {rev} ({detail})")
    text = block_text_at(repo, rev, filename, ordinal)
    if text is not None:
        return "rev", rev, text
    history = run_git(repo, ["rev-list", "--reverse", f"{rev}..HEAD", "--",
                             filename])
    if history.returncode != 0:
        detail = (history.stderr or history.stdout).strip()
        raise ProbeError(f"git rev-list {rev}..HEAD -- {filename}: {detail}")
    for commit in history.stdout.split():
        text = block_text_at(repo, commit, filename, ordinal)
        if text is not None:
            return "forward", commit, text
    return "absent", None, None


def run_probe(argv, timeout=PROBE_TIMEOUT):
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except OSError as exc:
        raise ProbeError(f"{argv[0]}: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProbeError(f"{' '.join(argv)}: timed out") from exc
    return proc.returncode, proc.stdout


def os_release_id(path="/etc/os-release"):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ProbeError(f"cannot read {path}: {exc}") from exc
    for line in text.splitlines():
        if line.startswith("ID="):
            return line[3:].strip().strip('"')
    raise ProbeError(f"no ID= field in {path}")


def live_triple():
    values = []
    for flag in ("-s", "-m"):
        rc, out = run_probe(["uname", flag])
        if rc != 0:
            raise ProbeError(f"uname {flag} failed: {out.strip()}")
        values.append(out.strip())
    values.append(os_release_id())
    return tuple(values)


def triple_text(triple):
    return "/".join(triple) if triple else "-/-/-"


def base_leg(repo, filename):
    """Run the byte-frozen r73 counter with --json; return its payload."""
    if not BASE_TOOL.exists():
        raise ProbeError(f"base leg tool absent: {BASE_TOOL}")
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run([sys.executable, str(BASE_TOOL), "--repo", str(repo),
                               "--file", filename, "--json"],
                              capture_output=True, text=True, env=env,
                              timeout=PROBE_TIMEOUT)
    except OSError as exc:
        raise ProbeError(f"base leg: {exc}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ProbeError("base leg: timed out") from exc
    if proc.returncode == 2:
        detail = (proc.stderr or proc.stdout).strip()
        raise ProbeError(f"base leg could-not-evaluate: {detail}")
    line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    try:
        payload = json.loads(line)
    except (ValueError, IndexError) as exc:
        raise ProbeError(f"base leg output unparseable: {proc.stdout!r}") from exc
    if proc.returncode not in (0, 1) or payload.get("exit") not in (0, 1):
        raise ProbeError(f"base leg unexpected verdict: rc={proc.returncode} {line}")
    return payload


def preservation_leg(repo, filename, blocks):
    """Grade every token-carrying block: byte-identity at rev vs the worktree tip."""
    edited = []
    for ordinal, block in enumerate(blocks):
        if not block["recorded_at"]:
            continue
        rev = block["recorded_at"]
        status, resolved, at_rev = resolve_recorded_text(repo, rev, filename,
                                                         ordinal)
        at_tip = compared_text(block["text"])
        if status == "absent":
            edited.append((block, rev,
                           f"block absent at recorded revision {rev} through the tip"))
        elif at_rev != at_tip:
            where = f"rev={rev}" if status == "rev" \
                else f"rev={rev} resolved-at={resolved}"
            edited.append((block, rev,
                           f"{where}: at-recorded={at_rev!r} at-tip={at_tip!r}"))
    return edited


def evaluate(repo, filename):
    repo = Path(repo).resolve()
    path = repo / filename
    text = read_text(path)
    blocks = parse_blocks(text)
    live = live_triple()
    base = base_leg(repo, filename)
    findings = [(f["kind"], f["detail"]) for f in base.get("findings", [])]
    edited = preservation_leg(repo, filename, blocks)
    for block, rev, detail in edited:
        findings.append(("edited-block",
                         f"line={block['line']} round={block['round']} "
                         f"recorded-at={rev}: {detail}"))
    return {"path": str(path), "blocks": len(blocks), "live": live,
            "recorded": base.get("recorded"), "stale": base.get("stale", 1),
            "edited": len(edited), "findings": findings}


def summary_of(text):
    match = SUMMARY_RE.search(text)
    if not match:
        return None
    return {"blocks": int(match.group(1)), "recorded": match.group(2),
            "live": match.group(3), "stale": int(match.group(4)),
            "edited": int(match.group(5))}


def last_line(text):
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else "<no output>"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Grade PROVINCE.md's host identity with base-revision "
                    "preservation (runs the byte-frozen r73 counter as its "
                    "base leg).")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--file", default=PROVINCE_NAME)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--work")
    options = parser.parse_args(argv)

    created_work = options.work is None
    try:
        work = Path(tempfile.mkdtemp(prefix="r74-province-host-drift-")) if created_work \
            else Path(os.path.expanduser(options.work))
        work.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"PROVINCE_HOST_DRIFT_V2 could-not-evaluate: unusable --work root: {exc}",
              file=sys.stderr)
        return 2
    try:
        if options.selftest:
            return selftest(work)
        repo = Path(os.path.expanduser(options.repo)).resolve()
        result = evaluate(repo, options.file)
        exit_code = 0 if not result["findings"] else 1
        if options.json:
            payload = {
                "tool": "province-host-drift/v2",
                "repo": str(repo),
                "file": result["path"],
                "blocks": result["blocks"],
                "recorded": result["recorded"],
                "live": list(result["live"]),
                "stale": result["stale"],
                "edited": result["edited"],
                "findings": [{"kind": kind, "detail": detail}
                             for kind, detail in result["findings"]],
                "predicate": PREDICATE,
                "exit": exit_code,
            }
            print(json.dumps(payload, ensure_ascii=False))
            return exit_code
        for kind, detail in result["findings"]:
            print(f"PROVINCE_HOST_DRIFT_V2_FINDING {kind} {detail}")
        print(f"PROVINCE_HOST_DRIFT_V2 blocks={result['blocks']} "
              f"recorded={triple_text(result['recorded'])} "
              f"live={triple_text(result['live'])} "
              f"stale={result['stale']} edited={result['edited']}")
        return exit_code
    except ProbeError as exc:
        print(f"PROVINCE_HOST_DRIFT_V2 could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    finally:
        if created_work:
            shutil.rmtree(work, ignore_errors=True)


def run_tool(argv):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    try:
        proc = subprocess.run([sys.executable, str(TOOL), *argv], capture_output=True,
                              text=True, env=env)
    except OSError as exc:
        return 127, str(exc)
    return proc.returncode, proc.stdout + proc.stderr


def run_tool_base(repo):
    """Run the byte-frozen r73 counter directly over a fixture repo."""
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run([sys.executable, str(BASE_TOOL), "--repo", str(repo)],
                          capture_output=True, text=True, env=env)
    return proc.returncode, proc.stdout + proc.stderr


def plan_predicate():
    """Re-derive the C3 blockquote from the frozen plan: marks and line breaks removed."""
    try:
        text = (LANE / PLAN_NAME).read_text(encoding="utf-8")
    except OSError:
        return None
    start = text.find("## C3")
    if start < 0:
        return None
    end = text.find("\n## ", start + 5)
    section = text[start:end if end >= 0 else len(text)]
    quoted = []
    for line in section.splitlines():
        if line.startswith(">"):
            quoted.append(line[1:].lstrip())
        elif quoted:
            break
    return " ".join(quoted).strip() if quoted else None


# ---------------------------------------------------------------------- selftest

def git(d, *args, check=True):
    proc = subprocess.run(["git", "-C", str(d), *GITID, *args],
                          capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f"git -C {d} {' '.join(args)} -> {proc.returncode}\n"
                           f"{proc.stdout}\n{proc.stderr}")
    return proc


def fixture_repo(work, name):
    d = work / name
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    git(d, "init", "-q", "-b", "master")
    top = Path(git(d, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert top == d.resolve(), f"toplevel {top} != fixture {d.resolve()}"
    return d


def commit_all(d, msg):
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg)
    return git(d, "rev-parse", "HEAD").stdout.strip()


def selftest(work):
    checks = []

    def check(name, ok, note):
        checks.append((name, ok, note))

    live = live_triple()
    windows = ("Windows", "AMD64", "win")

    def block(round_no, triple, date="2026-11-03", token=None):
        system, machine, ident = triple
        text = (f"Round-{round_no} host-identity block ({date}). Host triple: "
                f"`uname -s` -> `{system}`; `uname -m` -> `{machine}`; "
                f"`/etc/os-release` `ID` -> `{ident}`.")
        if token:
            text = text + f" recorded at {token}."
        return "# province fixture\n\n" + text + "\n"

    def plain(name, text):
        d = work / name
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        (d / PROVINCE_NAME).write_text(text, encoding="utf-8")
        return d

    # Arm 1 (c3_clean replay, committed-builder shape): seed rev A names a tree
    # without PROVINCE.md; the block with `recorded at A` lands in the next
    # commit and is never edited -> exit 0, edited=0.
    clean = fixture_repo(work, "f0-clean")
    (clean / "LOG.md").write_text("# kama fixture LOG\n")
    rev_a = commit_all(clean, "seed")
    (clean / PROVINCE_NAME).write_text(block(73, live, token=rev_a),
                                       encoding="utf-8")
    commit_all(clean, "host block recorded at A")
    (clean / "LOG.md").write_text("# kama fixture LOG\nunrelated later commit\n")
    commit_all(clean, "unrelated edit")
    rc_base, _ = run_tool_base(clean)
    rc, out = run_tool(["--repo", str(clean)])
    parsed = summary_of(out)
    check("clean-token", rc_base == 0 and rc == 0 and parsed is not None
          and parsed["edited"] == 0 and parsed["stale"] == 0,
          f"base_rc={rc_base} rc={rc} {last_line(out)}")

    # Arm 2 (c3_edited replay, committed-builder shape): same, but a later
    # commit edits the block's date byte -> base leg stays green, v2 exits 1
    # naming edited-block.
    edited = fixture_repo(work, "f1-edited")
    (edited / "LOG.md").write_text("# kama fixture LOG\n")
    rev_a = commit_all(edited, "seed")
    (edited / PROVINCE_NAME).write_text(block(73, live, token=rev_a),
                                        encoding="utf-8")
    commit_all(edited, "host block recorded at A")
    (edited / PROVINCE_NAME).write_text(block(73, live, date="2026-11-04",
                                              token=rev_a), encoding="utf-8")
    commit_all(edited, "edit the recorded date byte")
    rc_base, out_base = run_tool_base(edited)
    rc, out = run_tool(["--repo", str(edited)])
    parsed = summary_of(out)
    check("edited-date", rc_base == 0 and rc == 1 and parsed is not None
          and parsed["edited"] == 1
          and "PROVINCE_HOST_DRIFT_V2_FINDING edited-block" in out,
          f"base_rc={rc_base} {last_line(out_base)} | rc={rc} {last_line(out)}")

    # Arm 3: no block at all -> exit 1 no-block.
    none_dir = plain("f2-noblock",
                     "# province fixture\n\nA paragraph that is not a host block.\n")
    rc, out = run_tool(["--repo", str(none_dir)])
    parsed = summary_of(out)
    check("no-block", rc == 1 and parsed is not None and parsed["blocks"] == 0
          and "PROVINCE_HOST_DRIFT_V2_FINDING no-block" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 4: stale triple, no token -> exit 1 stale-host (base-leg passthrough).
    stale_dir = plain("f3-windows", block(73, windows))
    rc, out = run_tool(["--repo", str(stale_dir)])
    parsed = summary_of(out)
    check("stale-host", rc == 1 and parsed is not None and parsed["stale"] == 1
          and "PROVINCE_HOST_DRIFT_V2_FINDING stale-host" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 5: a token naming an unresolvable rev -> exit 2, naming the rev.
    badrev = fixture_repo(work, "f4-badrev")
    (badrev / "LOG.md").write_text("# kama fixture LOG\n")
    commit_all(badrev, "seed")
    ghost = "0123456789abcdef0123456789abcdef01234567"
    (badrev / PROVINCE_NAME).write_text(block(73, live, token=ghost),
                                        encoding="utf-8")
    commit_all(badrev, "host block recorded at a rev that does not exist")
    rc, out = run_tool(["--repo", str(badrev)])
    check("unresolvable-rev", rc == 2 and "could-not-evaluate" in out
          and ghost in out,
          f"rc={rc} {last_line(out)}")

    # Arm 6: an older token-carrying block edited while the newest stays live ->
    # base leg green, v2 names the older block's round.
    older = fixture_repo(work, "f5-older-edited")
    (older / "LOG.md").write_text("# kama fixture LOG\n")
    commit_all(older, "seed")
    (older / PROVINCE_NAME).write_text(block(72, windows), encoding="utf-8")
    rev_a = commit_all(older, "old block, no token")
    (older / PROVINCE_NAME).write_text(block(72, windows, token=rev_a),
                                       encoding="utf-8")
    commit_all(older, "old block recorded at A")
    (older / PROVINCE_NAME).write_text(block(72, windows, date="2026-11-04",
                                             token=rev_a) + "\n\n"
                                       + block(73, live), encoding="utf-8")
    commit_all(older, "edit old date, append live block")
    rc_base, _ = run_tool_base(older)
    rc, out = run_tool(["--repo", str(older)])
    parsed = summary_of(out)
    check("older-block-edited", rc_base == 0 and rc == 1 and parsed is not None
          and parsed["edited"] == 1 and "edited-block" in out
          and "round=72" in out,
          f"base_rc={rc_base} rc={rc} {last_line(out)}")

    # Arm 7: no province file -> exit 2.
    missing = work / "f6-missing"
    missing.mkdir(parents=True, exist_ok=True)
    rc, out = run_tool(["--repo", str(missing)])
    check("missing-file", rc == 2 and "could-not-evaluate" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 8: CLI misuse -> exit 2.
    rc, out = run_tool(["--no-such-flag"])
    check("cli-misuse", rc == 2, f"rc={rc} {last_line(out)}")

    # Arm 9: the constant is byte-equal to the frozen C3 blockquote.
    planned = plan_predicate()
    check("predicate", planned is not None and planned == PREDICATE,
          f"plan_chars={len(planned) if planned is not None else 'absent'} "
          f"constant_chars={len(PREDICATE)}")

    # Arm 10: the live-lane record shape - the block exists at the token rev
    # without the token; the token sentence is gained later naming that rev ->
    # exit 0 (the honest gain is not a finding; plain rev resolution path).
    gained = fixture_repo(work, "f7-token-gained")
    (gained / "LOG.md").write_text("# kama fixture LOG\n")
    commit_all(gained, "seed")
    (gained / PROVINCE_NAME).write_text(block(73, live), encoding="utf-8")
    rev_a = commit_all(gained, "host block, no token")
    text = block(73, live).rstrip("\n")
    (gained / PROVINCE_NAME).write_text(
        text + f" recorded at {rev_a} (round-74 record; the v2 leg strips this "
        f"token sentence).\n", encoding="utf-8")
    commit_all(gained, "gain the recorded-at token naming A")
    rc, out = run_tool(["--repo", str(gained)])
    parsed = summary_of(out)
    check("token-gained-honest", rc == 0 and parsed is not None
          and parsed["edited"] == 0,
          f"rc={rc} {last_line(out)}")

    failures = [item for item in checks if not item[1]]
    for name, ok, note in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {note}")
    print(f"PROVINCE_HOST_DRIFT_V2_SELFTEST pass={len(checks) - len(failures)} "
          f"fail={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
