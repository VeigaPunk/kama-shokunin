#!/usr/bin/env python3
"""round73-province-host-drift.py - grade PROVINCE.md's recorded host identity against this host.

Round 65/67 recorded a Windows host in PROVINCE.md and only a hand-written round-71
re-derivation corrected it. ``tools/round71-province-host-claims.py`` re-probes each declared
surface against its marker, so it catches a host move only while a *marker* contradicts; a third
host move would leave every correction reading ``present``/``absent`` correctly while the province
file's recorded host stayed wrong. This counter grades the one thing no other instrument grades:
"the host this record describes is the host we are on".

Frozen predicate (plans/round-73-claims.md, C3):

    PREDICATE

Block grammar. A block is a paragraph whose first line matches
``Round-<N> host-identity block (YYYY-MM-DD)`` (leading ``**`` bold marks allowed) and whose text
carries the three triple tokens: ``uname -s``, ``uname -m`` and the ``ID`` field of
``/etc/os-release``, each followed by an arrow and a value (backticked or bare). The block count
is every parsed block; the graded block is the LAST one in file order, because PROVINCE.md is
append-only: a host move is answered by appending a later block, never by editing the old one. A
block whose triple cannot be parsed is a ``stale-host`` finding naming its line, never a skip.

Live triple: ``uname -s``, ``uname -m`` and the ``ID=`` value parsed (not sourced) from
``/etc/os-release``. A kernel-only update does not move the triple; a machine or OS change does.

Output:

    PROVINCE_HOST_DRIFT_FINDING <no-block|stale-host> <detail>     (one per finding)
    PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>

``recorded`` is the graded block's triple (``-`` per component when no block or the block's
triple is unparseable); ``stale`` is 0 iff the graded block's triple equals the live triple.

Exit: 0 clean; 1 findings; 2 could-not-evaluate (PROVINCE.md unreadable or not UTF-8, a live
probe failed, CLI misuse).

--file PATH is resolved against --repo (an absolute PATH replaces it). --selftest runs nine arms
over plain-directory fixtures under --work (a temporary work root is used and removed when
--work is omitted; a supplied root is left in place). The tool never edits PROVINCE.md.
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
PLAN_NAME = "plans/round-73-claims.md"
PROVINCE_NAME = "PROVINCE.md"
OS_RELEASE = "/etc/os-release"
PROBE_TIMEOUT = 30

PREDICATE = "`python3 tools/round73-province-host-drift.py --repo <lane>` prints one `PROVINCE_HOST_DRIFT blocks=<b> recorded=<s>/<m>/<id> live=<s>/<m>/<id> stale=<n>` line and exits 0 only when `PROVINCE.md` carries at least one `Round-<N> host-identity block (YYYY-MM-DD)` whose recorded triple (`uname -s`, `uname -m`, the `ID` field of `/etc/os-release`) equals the live triple, the newest block being the one graded; it exits 1 naming `PROVINCE_HOST_DRIFT_FINDING <no-block|stale-host> <detail>` when no block exists or the newest block's triple differs from the live one."

BLOCK_HEADER_RE = re.compile(
    r"^\s*\*{0,2}Round-(\d+)\s+host-identity\s+block\s+\((\d{4}-\d{2}-\d{2})\)")
ARROW_RE = re.compile(r"\s*(?:->|\u2192)\s*")
VALUE_REST_RE = re.compile(r"[^;]+")
SUMMARY_RE = re.compile(
    r"^PROVINCE_HOST_DRIFT blocks=(\d+) recorded=(\S+) live=(\S+) stale=(\d+)$", re.M)


class ProbeError(Exception):
    """The province file or the live host cannot be evaluated; the tool exits 2."""


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


def value_after(text, pos):
    """Read the value following an arrow at pos: backticked or bare up to ';'."""
    arrow = ARROW_RE.match(text, pos)
    if not arrow:
        return None
    index = arrow.end()
    if index < len(text) and text[index] == "`":
        closing = text.find("`", index + 1)
        if closing < 0:
            return None
        return text[index + 1:closing].strip() or None
    rest = VALUE_REST_RE.match(text, index)
    if not rest:
        return None
    return rest.group(0).strip().rstrip(".").strip() or None


def token_value(text, pattern):
    match = re.search(pattern, text)
    if not match:
        return None
    return value_after(text, match.end())


def parse_triple(paragraph):
    system = token_value(paragraph, r"`?uname -s`?")
    machine = token_value(paragraph, r"`?uname -m`?")
    ident = token_value(paragraph, r"`?/etc/os-release`?\s*`?ID`?")
    if ident is None:
        ident = token_value(paragraph, r"`?ID`?(?=\s*(?:->|\u2192))")
    if system is None or machine is None or ident is None:
        return None
    return (system, machine, ident)


def parse_blocks(text):
    """Return every host-identity block in file order."""
    blocks = []
    for line_no, lines in paragraphs(text):
        header = BLOCK_HEADER_RE.match(lines[0])
        if not header:
            continue
        paragraph = " ".join(line.strip() for line in lines)
        blocks.append({
            "line": line_no,
            "round": int(header.group(1)),
            "date": header.group(2),
            "triple": parse_triple(paragraph),
        })
    return blocks


def run_probe(argv, timeout=PROBE_TIMEOUT):
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ProbeError(f"{argv[0]}: {exc}") from exc
    return proc.returncode, proc.stdout


def os_release_id(path=OS_RELEASE):
    try:
        raw = Path(path).read_bytes().decode("utf-8", "replace")
    except OSError as exc:
        raise ProbeError(f"cannot read {path}: {exc}") from exc
    for line in raw.splitlines():
        if not line.startswith("ID="):
            continue
        value = line[3:].strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if value:
            return value
        break
    raise ProbeError(f"no ID= field in {path}")


def live_triple(os_release=OS_RELEASE):
    values = []
    for flag in ("-s", "-m"):
        rc, out = run_probe(["uname", flag])
        value = out.decode("utf-8", "replace").strip()
        if rc != 0 or not value:
            raise ProbeError(f"uname {flag} exit={rc} output={value or '<empty>'}")
        values.append(value)
    values.append(os_release_id(os_release))
    return tuple(values)


def triple_text(triple):
    return "/".join(triple) if triple else "-/-/-"


def evaluate(repo, filename):
    path = Path(repo) / filename
    blocks = parse_blocks(read_text(path))
    live = live_triple()
    graded = blocks[-1] if blocks else None
    findings = []
    if graded is None:
        findings.append(("no-block", f"no Round-<N> host-identity block in {path}"))
    elif graded["triple"] is None:
        findings.append(("stale-host",
                         f"line={graded['line']} round={graded['round']}: "
                         f"triple not parseable"))
    elif graded["triple"] != live:
        findings.append(("stale-host",
                         f"line={graded['line']} round={graded['round']}: "
                         f"recorded={triple_text(graded['triple'])} "
                         f"live={triple_text(live)}"))
    stale = 0 if graded is not None and graded["triple"] == live else 1
    return {"path": str(path), "blocks": blocks, "graded": graded, "live": live,
            "findings": findings, "stale": stale}


def summary_of(text):
    match = SUMMARY_RE.search(text)
    if not match:
        return None
    return {"blocks": int(match.group(1)), "recorded": match.group(2),
            "live": match.group(3), "stale": int(match.group(4))}


def last_line(text):
    lines = [line for line in text.strip().splitlines() if line.strip()]
    return lines[-1] if lines else "<no output>"


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Grade PROVINCE.md's newest host-identity block against the live host.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--file", default=PROVINCE_NAME)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--work")
    options = parser.parse_args(argv)

    created_work = options.work is None
    try:
        work = Path(tempfile.mkdtemp(prefix="r73-province-host-drift-")) if created_work \
            else Path(os.path.expanduser(options.work))
        work.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"PROVINCE_HOST_DRIFT could-not-evaluate: unusable --work root: {exc}",
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
                "tool": "province-host-drift/v1",
                "repo": str(repo),
                "file": result["path"],
                "blocks": len(result["blocks"]),
                "graded": result["graded"],
                "recorded": list(result["graded"]["triple"])
                if result["graded"] and result["graded"]["triple"] else None,
                "live": list(result["live"]),
                "stale": result["stale"],
                "findings": [{"kind": kind, "detail": detail}
                             for kind, detail in result["findings"]],
                "predicate": PREDICATE,
                "exit": exit_code,
            }
            print(json.dumps(payload, ensure_ascii=False))
            return exit_code
        for kind, detail in result["findings"]:
            print(f"PROVINCE_HOST_DRIFT_FINDING {kind} {detail}")
        print(f"PROVINCE_HOST_DRIFT blocks={len(result['blocks'])} "
              f"recorded={triple_text(result['graded']['triple'] if result['graded'] else None)} "
              f"live={triple_text(result['live'])} stale={result['stale']}")
        return exit_code
    except ProbeError as exc:
        print(f"PROVINCE_HOST_DRIFT could-not-evaluate: {exc}", file=sys.stderr)
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


def selftest(work):
    checks = []

    def check(name, ok, note):
        checks.append((name, ok, note))

    live = live_triple()
    windows = ("Windows", "AMD64", "win")

    def block(round_no, triple, date="2026-11-03"):
        system, machine, ident = triple
        return (f"Round-{round_no} host-identity block ({date}). Host triple: "
                f"`uname -s` -> `{system}`; `uname -m` -> `{machine}`; "
                f"`/etc/os-release` `ID` -> `{ident}`.")

    def fixture(name, text):
        path = work / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True)
        (path / PROVINCE_NAME).write_text(text, encoding="utf-8")
        return path

    # Arm 1: the live triple recorded in the newest (only) block -> exit 0.
    live_dir = fixture("f0-live", "# province fixture\n\n" + block(73, live) + "\n")
    rc, out = run_tool(["--repo", str(live_dir)])
    parsed = summary_of(out)
    check("live-match", rc == 0 and parsed is not None and parsed["blocks"] == 1
          and parsed["stale"] == 0,
          f"rc={rc} {last_line(out)}")

    # Arm 2: a Windows triple on this host -> exit 1 stale-host.
    stale_dir = fixture("f1-windows", "# province fixture\n\n" + block(73, windows) + "\n")
    rc, out = run_tool(["--repo", str(stale_dir)])
    parsed = summary_of(out)
    check("windows-stale", rc == 1 and parsed is not None and parsed["stale"] == 1
          and "PROVINCE_HOST_DRIFT_FINDING stale-host" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 3: no block at all -> exit 1 no-block.
    none_dir = fixture("f2-noblock",
                       "# province fixture\n\nA paragraph that is not a host-identity block.\n")
    rc, out = run_tool(["--repo", str(none_dir)])
    parsed = summary_of(out)
    check("no-block", rc == 1 and parsed is not None and parsed["blocks"] == 0
          and parsed["recorded"] == "-/-/-"
          and "PROVINCE_HOST_DRIFT_FINDING no-block" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 4: two blocks, the newest matches -> exit 0 (append-only, newest wins).
    two_dir = fixture("f3-two-newest-live",
                      "# province fixture\n\n" + block(72, windows)
                      + "\n\n" + block(73, live) + "\n")
    rc, out = run_tool(["--repo", str(two_dir)])
    parsed = summary_of(out)
    check("newest-matches", rc == 0 and parsed is not None and parsed["blocks"] == 2
          and parsed["stale"] == 0,
          f"rc={rc} {last_line(out)}")

    # Arm 5: an older block matches, the newest differs -> exit 1 stale-host.
    old_dir = fixture("f4-newest-stale",
                      "# province fixture\n\n" + block(72, live)
                      + "\n\n" + block(73, windows) + "\n")
    rc, out = run_tool(["--repo", str(old_dir)])
    parsed = summary_of(out)
    check("newest-differs", rc == 1 and parsed is not None and parsed["blocks"] == 2
          and parsed["stale"] == 1
          and "PROVINCE_HOST_DRIFT_FINDING stale-host" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 6: a block header whose triple tokens are missing -> exit 1, naming the line.
    bad_dir = fixture("f5-unparseable",
                      "# province fixture\n\n"
                      "Round-73 host-identity block (2026-11-03). "
                      "Host triple recorded without tokens.\n")
    rc, out = run_tool(["--repo", str(bad_dir)])
    parsed = summary_of(out)
    check("unparseable-triple", rc == 1 and parsed is not None and parsed["stale"] == 1
          and "PROVINCE_HOST_DRIFT_FINDING stale-host" in out and "line=3" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 7: no province file -> exit 2 (could not evaluate, never a finding).
    missing_dir = work / "f6-missing"
    missing_dir.mkdir(parents=True, exist_ok=True)
    rc, out = run_tool(["--repo", str(missing_dir)])
    check("missing-file", rc == 2 and "could-not-evaluate" in out,
          f"rc={rc} {last_line(out)}")

    # Arm 8: CLI misuse -> exit 2.
    rc, out = run_tool(["--no-such-flag"])
    check("cli-misuse", rc == 2, f"rc={rc} {last_line(out)}")

    # Arm 9: the constant is byte-equal to the frozen C3 blockquote, marks and breaks removed.
    planned = plan_predicate()
    check("predicate", planned is not None and planned == PREDICATE,
          f"plan_chars={len(planned) if planned is not None else 'absent'} "
          f"constant_chars={len(PREDICATE)}")

    failures = [item for item in checks if not item[1]]
    for name, ok, note in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {note}")
    print(f"PROVINCE_HOST_DRIFT_SELFTEST pass={len(checks) - len(failures)} "
          f"fail={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
