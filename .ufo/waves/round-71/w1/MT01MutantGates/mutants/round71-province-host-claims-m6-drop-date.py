#!/usr/bin/env python3
"""round71-province-host-claims.py - re-derive every PROVINCE.md host-surface claim.

Round 65 re-hosted the lane and recorded each former-host artifact as an
``absent-on-this-host (DATE)`` marker in PROVINCE.md; round 67 added three more.
Markers rot: the lane is back on the original Linux box, so ten of the twelve
marked surfaces and all four prose claims no longer hold. The frozen predicate
(plans/round-71-claims.md, C3): every province host-surface claim is re-derived
on this host and stale ones carry a dated, verdict-checked correction.

    PROVINCE_HOST_CLAIMS markers=<m> tags=<t> extra=<e> contradicted=<c> uncovered=<u> exit=<x>

Marker grammar. A marker paragraph opens with ``- absent-on-this-host (YYYY-MM-DD)``
and continues over indented wrap lines until a blank line. Every
``province-host:TAG`` occurrence inside that paragraph declares TAG absent (a
wrap naming two tags declares two claims). One marker line naming two tags is
the round-67 ``llama-b11755-install`` / ``llama-server-link`` wrap.

Declared SURFACES (path existence unless the kind says otherwise):
  omp-binary                 ~/.local/bin/omp
  llama-b11755-install       ~/.local/opt/llama-b11755
  llama-server-link          ~/.local/bin/llama-server
  kama-cache-gguf            ~/.cache/kama-shokunin
  llama-b11755-archive       ~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz
  qwen-coder-unit            ~/.config/systemd/user/qwen-coder.service
  opencode-json              ~/.config/opencode/opencode.json
  janitor-md                 ~/.config/opencode/agents/janitor.md
  ollama-v04011-install      ~/.local/opt/ollama-v0.40.11
  fixture-gguf-model         ~/.cache/kama-shokunin/models/stories260K.gguf
  ufo-src                    a ufo-fsd checkout resolves, in the declared search
                             order $UFO_SRC then ~/Projects/ufo-fsd-alpha (a
                             checkout = that directory carries .git)
  python3-interpreter        `python3 -c "import sys"` exits 0 (a real run, not a
                             PATH hit; the round-65 Store alias passes `command -v`)

Declared EXTRA prose claims (4), each a claim of the surface subject's presence:
  host-identity   the lane host is Windows 10.0.26200    probe: `uname -s`
  python3-alias   python3 is the Microsoft Store alias   probe: a real run
  ntfs-path       a tracked `|` path cannot be checked   probe: a scratch repo
                  out under NTFS                         commit + checkout of
                                                         `pipe|name.txt`
  ss-flock        `ss` and `flock` are absent            probe: `command -v ss flock`
The extra claim date is the round-65 note date, 2026-10-31. A claim is
contradicted when its declared verdict differs from the live probe verdict.

Corrections. A line
    - correction-on-host (YYYY-MM-DD) `province-host:TAG` — present|absent: <evidence>
covers TAG only when its date is later than the claim date, TAG is declared,
and its verdict equals the live probe verdict. A wrong tag or a flipped
verdict covers nothing (the do-nothing shortcut this round's control names).

--base REV additionally reads PROVINCE.md at REV (git show) and requires every
base marker tag to still occur in a tip marker paragraph; a missing tag prints
``PROVINCE_HOST_CLAIMS_REWRITTEN <tag>`` and exits 1 (the append-only rule:
marker lines are never deleted or reworded). When --corrections names another
file inside the repo, its repo-relative path is read at REV first and
PROVINCE.md at REV is the fallback (an untracked copy of the province file).

--draft PATH writes the generated correction block for every contradicted and
uncovered claim (one line per tag, probe command and live output carried in the
evidence field). The tool never edits PROVINCE.md.

Exit: 0 uncovered == 0; 1 uncovered > 0 or a base marker tag rewritten;
2 could-not-evaluate (unreadable --corrections, --base git failure, a marker
tag with no declared probe, an NTFS probe setup failure). Read-only on the
repository: it stats host paths, spawns the declared probes once, creates its
NTFS probe repo under the scratch root and removes it, and reads PROVINCE.md.

    --repo PATH        repository/worktree holding PROVINCE.md (default ".")
    --base REV         rewrite check against PROVINCE.md at REV
    --corrections PATH province file to grade (default <repo>/PROVINCE.md)
    --json             one JSON object instead of per-claim lines
    --draft PATH       write the generated correction block to PATH
    --scratch DIR      scratch root for the NTFS probe and selftest fixtures
    --selftest         fixture arms; prints PROVINCE_HOST_CLAIMS_SELFTEST pass=N fail=M
    --keep             keep the selftest fixture tree
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOL = Path(__file__).resolve()
LANE = TOOL.parent.parent
PROVINCE_NAME = "PROVINCE.md"
BASE_REV = "f3ee44f4"
MARKER_DATE = "2026-10-31"
PROBE_TIMEOUT = 30
GIT_TIMEOUT = 60

MARKER_OPEN_RE = re.compile(r"^- absent-on-this-host \((\d{4}-\d{2}-\d{2})\)")
TAG_RE = re.compile(r"province-host:([A-Za-z0-9._-]+)")
CORRECTION_RE = re.compile(
    r"^\s*-\s*correction-on-host\s+\((\d{4}-\d{2}-\d{2})\)\s+"
    r"`province-host:([A-Za-z0-9._-]+)`\s*(?:\u2014|--)\s*"
    r"(present|absent)\s*:\s*(\S.*)$"
)

# (tag, kind, target) - the round-65/67 host surfaces, one live probe each.
SURFACES = [
    ("omp-binary", "file", "~/.local/bin/omp"),
    ("llama-b11755-install", "dir", "~/.local/opt/llama-b11755"),
    ("llama-server-link", "file", "~/.local/bin/llama-server"),
    ("kama-cache-gguf", "dir", "~/.cache/kama-shokunin"),
    ("llama-b11755-archive", "file", "~/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz"),
    ("qwen-coder-unit", "file", "~/.config/systemd/user/qwen-coder.service"),
    ("opencode-json", "file", "~/.config/opencode/opencode.json"),
    ("janitor-md", "file", "~/.config/opencode/agents/janitor.md"),
    ("ufo-src", "checkout", "UFO_SRC|~/Projects/ufo-fsd-alpha"),
    ("ollama-v04011-install", "dir", "~/.local/opt/ollama-v0.40.11"),
    ("fixture-gguf-model", "file", "~/.cache/kama-shokunin/models/stories260K.gguf"),
    ("python3-interpreter", "spawn", "python3"),
]
SURFACE_MAP = {tag: (kind, target) for tag, kind, target in SURFACES}


class ProbeError(Exception):
    """A live probe could not be evaluated; the tool fails closed (exit 2)."""


def _run(cmd, timeout, cwd=None):
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout, cwd=cwd)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, b"", str(exc).encode("utf-8", "replace")
    return proc.returncode, proc.stdout, proc.stderr


def _text(raw):
    return raw.decode("utf-8", "replace").strip()


def git(root, *args):
    rc, out, err = _run(["git", "-C", str(root), *args], GIT_TIMEOUT)
    return rc, _text(out), _text(err)


def read_text(path):
    try:
        return Path(path).read_bytes().decode("utf-8").replace("\r\n", "\n")
    except OSError as exc:
        raise ProbeError(f"cannot read {path}: {exc}") from exc
    except UnicodeDecodeError as exc:
        raise ProbeError(f"{path} is not UTF-8: {exc}") from exc


def parse_markers(text):
    """Return (marker paragraphs, {tag: first paragraph date})."""
    lines = text.splitlines()
    markers = 0
    tags = {}
    i = 0
    while i < len(lines):
        match = MARKER_OPEN_RE.match(lines[i])
        if not match:
            i += 1
            continue
        markers += 1
        date = match.group(1)
        block = [lines[i]]
        j = i + 1
        while j < len(lines) and lines[j].strip() and lines[j][0] in " \t":
            block.append(lines[j])
            j += 1
        for tag in TAG_RE.findall("\n".join(block)):
            tags.setdefault(tag, date)
        i = j
    return markers, tags


def parse_corrections(text):
    found = []
    for line in text.splitlines():
        match = CORRECTION_RE.match(line)
        if not match:
            continue
        found.append({"date": match.group(1), "tag": match.group(2),
                      "verdict": match.group(3), "evidence": match.group(4).strip()})
    return found


def probe_path(kind, target):
    path = Path(os.path.expanduser(target))
    try:
        hit = path.is_dir() if kind == "dir" else path.is_file()
    except OSError:
        hit = False
    command = f"test {'-d' if kind == 'dir' else '-e'} {path}"
    if hit:
        evidence = f"{path} exists ({'directory' if kind == 'dir' else 'file'})"
    else:
        evidence = f"{path} does not exist"
    return ("present" if hit else "absent"), command, evidence


def probe_checkout(_target):
    order = []
    env = os.environ.get("UFO_SRC", "")
    if env:
        order.append(os.path.expanduser(env))
    order.append(os.path.expanduser("~/Projects/ufo-fsd-alpha"))
    for candidate in order:
        root = Path(candidate)
        try:
            if (root / ".git").exists():
                command = f"test -e {root}/.git (search order: $UFO_SRC, ~/Projects/ufo-fsd-alpha)"
                return "present", command, f"ufo-fsd checkout resolves at {root}"
        except OSError:
            continue
    command = "test -e $UFO_SRC/.git || test -e ~/Projects/ufo-fsd-alpha/.git"
    tried = ", ".join(order) if order else "<none>"
    return "absent", command, f"no ufo-fsd checkout (tried {tried})"


def probe_spawn(target):
    rc, out, err = _run([target, "-c", "import sys; print(sys.version.split()[0])"],
                        PROBE_TIMEOUT)
    command = f'{target} -c "import sys"'
    if rc == 0:
        return "present", command, f"exit=0, Python {_text(out) or 'unknown'}"
    detail = _text(err) or _text(out) or "no output"
    return "absent", command, f"exit={rc}: {detail.splitlines()[0][:200]}"


def probe_windows():
    rc, out, err = _run(["uname", "-s"], PROBE_TIMEOUT)
    name = _text(out) if rc == 0 and out.strip() else platform.system()
    lowered = name.lower()
    windows = lowered.startswith(("mingw", "msys", "cygwin")) or lowered == "windows"
    return ("present" if windows else "absent"), "uname -s", f"{name or _text(err) or 'unknown'}"


def probe_python3_alias():
    rc, out, err = _run(["python3", "-c", "import sys; print(sys.version.split()[0])"],
                        PROBE_TIMEOUT)
    command = 'python3 -c "import sys"'
    if rc == 0:
        return "absent", command, f"exit=0, Python {_text(out)}; python3 is a real interpreter, not the Store alias"
    detail = _text(err) or _text(out) or "no output"
    return "present", command, f"exit={rc}: {detail.splitlines()[0][:200]}"


def probe_ss_flock():
    ss = shutil.which("ss")
    flock = shutil.which("flock")
    both_absent = ss is None and flock is None
    evidence = f"ss={ss or 'not found'}, flock={flock or 'not found'}"
    return ("present" if both_absent else "absent"), "command -v ss flock", evidence


def _git_fixture(root, *args):
    if not any(arg in ("init", "rev-parse") for arg in args):
        rc, out, err = git(root, "rev-parse", "--show-toplevel")
        if rc != 0 or os.path.realpath(out) != os.path.realpath(str(root)):
            raise ProbeError(f"fixture toplevel assertion failed for {root}: {out or err}")
    return git(root, *args)


def probe_ntfs_path(scratch_root):
    repo = Path(tempfile.mkdtemp(prefix="ntfs-path-probe-", dir=str(scratch_root)))
    command = "git init; git add 'pipe|name.txt'; git commit; git checkout -- ."
    payload = "probe\n"
    try:
        rc, _out, err = _git_fixture(repo, "init", "-q")
        if rc != 0:
            raise ProbeError(f"ntfs probe: git init failed: {err[:200]}")
        rc, out, err = _git_fixture(repo, "rev-parse", "--show-toplevel")
        if rc != 0 or os.path.realpath(out) != os.path.realpath(str(repo)):
            raise ProbeError(f"ntfs probe: toplevel assertion failed: {out or err}")
        target = repo / "pipe|name.txt"
        try:
            target.write_text(payload, encoding="utf-8")
        except OSError as exc:
            return "present", command, f"cannot create the '|' path under {repo}: {exc}"
        rc, _out, err = _git_fixture(repo, "add", "--", "pipe|name.txt")
        if rc != 0:
            raise ProbeError(f"ntfs probe: git add of the '|' path failed: {err[:200]}")
        rc, _out, err = _git_fixture(
            repo, "-c", "user.name=kama-r71", "-c", "user.email=kama-r71@example.invalid",
            "commit", "-q", "-m", "pipe-path probe")
        if rc != 0:
            raise ProbeError(f"ntfs probe: git commit failed: {err[:200]}")
        target.unlink()
        rc, _out, err = _git_fixture(repo, "checkout", "--", ".")
        if rc != 0:
            return "present", command, f"git checkout exit={rc}: {err[:200]}"
        return "absent", command, f"git checkout exit=0; the '|' path round-tripped under {repo}"
    finally:
        shutil.rmtree(repo, ignore_errors=True)


# (tag, claim verdict, prose claim, probe) - probe None means probe_ntfs_path.
EXTRAS = [
    ("host-identity", "present", "the lane host is Windows 10.0.26200", probe_windows),
    ("python3-alias", "present", "python3 on PATH is the Microsoft Store alias stub", probe_python3_alias),
    ("ntfs-path", "present", "a tracked '|' path cannot be checked out under NTFS", None),
    ("ss-flock", "present", "ss and flock are absent", probe_ss_flock),
]


def probe_surface(tag):
    kind, target = SURFACE_MAP[tag]
    if kind in ("file", "dir"):
        return probe_path(kind, target)
    if kind == "checkout":
        return probe_checkout(target)
    if kind == "spawn":
        return probe_spawn(target)
    raise ProbeError(f"unknown probe kind {kind!r} for {tag}")


def covering_correction(claim, corrections):
    for correction in corrections:
        if correction["tag"] != claim["tag"]:
            continue
        if correction["verdict"] != claim["live"]:
            continue
        return correction
    return None


def evaluate(corrections_path, scratch_root):
    text = read_text(corrections_path)
    markers, marker_tags = parse_markers(text)
    corrections = parse_corrections(text)
    claims = []
    for tag, date in marker_tags.items():
        if tag not in SURFACE_MAP:
            raise ProbeError(
                f"marker tag province-host:{tag} has no declared probe (add it to SURFACES)")
        verdict, command, evidence = probe_surface(tag)
        claims.append({"tag": tag, "kind": "marker", "date": date, "claim": "absent",
                       "live": verdict, "command": command, "evidence": evidence})
    for tag, verdict, prose, probe in EXTRAS:
        if probe is None:
            live, command, evidence = probe_ntfs_path(scratch_root)
        else:
            live, command, evidence = probe()
        claims.append({"tag": tag, "kind": "extra", "date": MARKER_DATE,
                       "claim": verdict, "prose": prose,
                       "live": live, "command": command, "evidence": evidence})
    for claim in claims:
        claim["contradicted"] = claim["claim"] != claim["live"]
        correction = covering_correction(claim, corrections)
        claim["covered"] = correction is not None
        claim["correction"] = correction
    contradicted = sum(1 for claim in claims if claim["contradicted"])
    uncovered = sum(1 for claim in claims if claim["contradicted"] and not claim["covered"])
    return {"markers": markers, "tags": len(marker_tags), "extra": len(EXTRAS),
            "contradicted": contradicted, "uncovered": uncovered,
            "claims": claims, "corrections": len(corrections)}


def relative_to_repo(corrections, repo):
    try:
        return Path(os.path.realpath(corrections)).relative_to(
            Path(os.path.realpath(repo))).as_posix()
    except ValueError:
        return PROVINCE_NAME


def base_province(repo, rev, corrections):
    rel = relative_to_repo(corrections, repo)
    candidates = [rel] if rel == PROVINCE_NAME else [rel, PROVINCE_NAME]
    errors = []
    for candidate in candidates:
        rc, out, err = git(repo, "show", f"{rev}:{candidate}")
        if rc == 0:
            return out
        errors.append(f"{rev}:{candidate}: {err[:120] or 'no such object/path'}")
    raise ProbeError("git show failed for " + "; ".join(errors))


def draft_date(claims):
    today = _dt.date.today()
    latest = max((_dt.date.fromisoformat(claim["date"]) for claim in claims),
                 default=_dt.date(1970, 1, 1))
    chosen = today if today > latest else latest + _dt.timedelta(days=1)
    return chosen.isoformat()


def write_draft(path, claims, date):
    target = Path(os.path.expanduser(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "<!-- generated by tools/round71-province-host-claims.py --draft.",
        "     One correction line per contradicted claim; each carries the live probe command",
        "     and its output in the evidence field. Append verbatim to PROVINCE.md. -->",
        "",
    ]
    written = 0
    for claim in claims:
        if not claim["contradicted"] or claim["covered"]:
            continue
        written += 1
        lines.append(
            f'- correction-on-host ({date}) `province-host:{claim["tag"]}` '
            f'\u2014 {claim["live"]}: {claim["command"]} \u2192 {claim["evidence"]}')
    lines.append("")
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"PROVINCE_HOST_CLAIMS_DRAFT path={target} lines={written}", file=sys.stderr)
    return written


def summary_of(stdout):
    match = re.search(
        r"^PROVINCE_HOST_CLAIMS markers=(\d+) tags=(\d+) extra=(\d+) "
        r"contradicted=(\d+) uncovered=(\d+) exit=(\d+)$", stdout, re.M)
    if not match:
        return None
    keys = ("markers", "tags", "extra", "contradicted", "uncovered", "exit")
    return {key: int(value) for key, value in zip(keys, match.groups())}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Re-derive every PROVINCE.md host-surface claim on this host.")
    parser.add_argument("--repo", default=".")
    parser.add_argument("--base")
    parser.add_argument("--corrections")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--draft")
    parser.add_argument("--scratch")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--keep", action="store_true")
    options = parser.parse_args(argv)

    created_scratch = options.scratch is None
    scratch_root = Path(os.path.expanduser(options.scratch)) if options.scratch \
        else Path(tempfile.mkdtemp(prefix="r71-province-claims-"))
    scratch_root.mkdir(parents=True, exist_ok=True)
    try:
        if options.selftest:
            return selftest(scratch_root, options.keep)
        repo = Path(os.path.expanduser(options.repo)).resolve()
        corrections = Path(os.path.expanduser(options.corrections)).resolve() \
            if options.corrections else repo / PROVINCE_NAME
        if not corrections.is_file():
            print(f"PROVINCE_HOST_CLAIMS could-not-evaluate: cannot read {corrections}",
                  file=sys.stderr)
            return 2
        result = evaluate(str(corrections), str(scratch_root))
        rewritten = []
        if options.base:
            base_text = base_province(str(repo), options.base, str(corrections))
            _base_markers, base_tags = parse_markers(base_text)
            tip_tags = {claim["tag"] for claim in result["claims"]
                        if claim["kind"] == "marker"}
            rewritten = [tag for tag in base_tags if tag not in tip_tags]
        exit_code = 0 if result["uncovered"] == 0 and not rewritten else 1
        if options.draft:
            write_draft(options.draft, result["claims"], draft_date(result["claims"]))
        if options.json:
            payload = {
                "tool": "province-host-claims/v1",
                "repo": str(repo),
                "corrections": str(corrections),
                "base": options.base,
                "markers": result["markers"],
                "tags": result["tags"],
                "extra": result["extra"],
                "contradicted": result["contradicted"],
                "uncovered": result["uncovered"],
                "corrections_parsed": result["corrections"],
                "rewritten": rewritten,
                "exit": exit_code,
                "claims": result["claims"],
            }
            print(json.dumps(payload, ensure_ascii=False))
            return exit_code
        for claim in result["claims"]:
            covered = "yes" if claim["covered"] else (
                "n/a" if not claim["contradicted"] else "no")
            print(f'claim {claim["tag"]} kind={claim["kind"]} date={claim["date"]} '
                  f'claim={claim["claim"]} live={claim["live"]} '
                  f'contradicted={"yes" if claim["contradicted"] else "no"} '
                  f'covered={covered} evidence="{claim["command"]} -> {claim["evidence"]}"')
        for tag in rewritten:
            print(f"PROVINCE_HOST_CLAIMS_REWRITTEN {tag}")
        print(f'PROVINCE_HOST_CLAIMS markers={result["markers"]} tags={result["tags"]} '
              f'extra={result["extra"]} contradicted={result["contradicted"]} '
              f'uncovered={result["uncovered"]} exit={exit_code}')
        return exit_code
    except ProbeError as exc:
        print(f"PROVINCE_HOST_CLAIMS could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    finally:
        if created_scratch:
            shutil.rmtree(scratch_root, ignore_errors=True)


def drop_marker_block(text, tag):
    lines = text.splitlines(keepends=True)
    out = []
    i = 0
    removed = False
    while i < len(lines):
        line = lines[i]
        match = MARKER_OPEN_RE.match(line.rstrip("\n"))
        if match and not removed:
            j = i + 1
            while j < len(lines) and lines[j].strip() and lines[j][0] in " \t":
                j += 1
            block = "".join(lines[i:j])
            if tag in block:
                i = j
                removed = True
                continue
        out.append(line)
        i += 1
    if not removed:
        raise ProbeError(f"fixture: no marker block names {tag}")
    return "".join(out)


def selftest(scratch_root, keep):
    checks = []

    def check(name, ok, note):
        checks.append((name, bool(ok), note))

    try:
        base_text = base_province(str(LANE), BASE_REV, str(LANE / PROVINCE_NAME))
    except ProbeError as exc:
        print(f"[FAIL] base-fixture: {exc}")
        print("PROVINCE_HOST_CLAIMS_SELFTEST pass=0 fail=1")
        return 1

    root = scratch_root / "selftest"
    shutil.rmtree(root, ignore_errors=True)
    root.mkdir(parents=True, exist_ok=True)

    def run_tool(args):
        proc = subprocess.run([sys.executable, str(TOOL), *args],
                              capture_output=True, text=True, timeout=300)
        return proc.returncode, proc.stdout, proc.stderr

    def fixture(name, text):
        directory = root / name
        directory.mkdir()
        (directory / PROVINCE_NAME).write_text(text, encoding="utf-8")
        return directory

    def correction_lines(claims, date, flip=None, flip_all=False):
        lines = []
        for claim in claims:
            if not claim["contradicted"]:
                continue
            verdict = claim["live"]
            if flip_all or (flip and claim["tag"] == flip):
                verdict = "absent" if verdict == "present" else "present"
            lines.append(
                f'- correction-on-host ({date}) `province-host:{claim["tag"]}` '
                f'\u2014 {verdict}: {claim["command"]} \u2192 {claim["evidence"]}')
        return "\n".join(lines)

    # Arm 1: the frozen base text - contradicted claims exist and none is covered.
    base_dir = fixture("f0-base", base_text)
    rc, out, err = run_tool(["--repo", str(base_dir)])
    parsed = summary_of(out)
    check("base-uncovered",
          rc == 1 and parsed is not None and parsed["markers"] == 11
          and parsed["tags"] == 12 and parsed["extra"] == 4
          and parsed["contradicted"] == parsed["uncovered"] and parsed["uncovered"] > 0,
          f"rc={rc} summary={out.strip().splitlines()[-1] if out.strip() else err[:120]}")

    # The live claims (with probe verdicts) drive the generated corrections.
    rc_json, json_out, json_err = run_tool(["--repo", str(base_dir), "--json"])
    data = json.loads(json_out)
    date = draft_date(data["claims"])

    # Arm 2: verdict-equal corrections for every contradicted claim -> uncovered 0.
    corrected_dir = fixture("f1-corrected", base_text + "\n\n"
                            + correction_lines(data["claims"], date) + "\n")
    rc, out, _err = run_tool(["--repo", str(corrected_dir)])
    parsed = summary_of(out)
    check("corrected-covers",
          rc == 0 and parsed is not None and parsed["uncovered"] == 0
          and parsed["contradicted"] > 0,
          f"rc={rc} contradicted={parsed and parsed['contradicted']} "
          f"uncovered={parsed and parsed['uncovered']}")

    # Arm 3: one flipped verdict leaves exactly that claim uncovered.
    flipped_tag = next((claim["tag"] for claim in data["claims"]
                        if claim["contradicted"] and claim["kind"] == "marker"),
                       next(claim["tag"] for claim in data["claims"] if claim["contradicted"]))
    flipped_dir = fixture("f2-flipped", base_text + "\n\n"
                          + correction_lines(data["claims"], date, flip=flipped_tag) + "\n")
    rc, out, _err = run_tool(["--repo", str(flipped_dir)])
    parsed = summary_of(out)
    check("flipped-verdict",
          rc == 1 and parsed is not None and parsed["uncovered"] == 1,
          f"rc={rc} tag={flipped_tag} uncovered={parsed and parsed['uncovered']}")

    # Arm 4: the do-nothing shortcut - every correction tag-correct, every verdict
    # flipped (appended without probing the host) - covers nothing.
    shortcut_dir = fixture("f2b-shortcut", base_text + "\n\n"
                           + correction_lines(data["claims"], date, flip_all=True) + "\n")
    rc, out, _err = run_tool(["--repo", str(shortcut_dir)])
    parsed = summary_of(out)
    check("shortcut-all-flipped",
          rc == 1 and parsed is not None
          and parsed["uncovered"] == parsed["contradicted"] and parsed["uncovered"] > 0,
          f"rc={rc} contradicted={parsed and parsed['contradicted']} "
          f"uncovered={parsed and parsed['uncovered']}")

    # Arm 5: a wrong tag covers nothing.
    wrong_dir = fixture("f3-wrongtag", base_text + f"\n\n"
                        f"- correction-on-host ({date}) `province-host:not-a-declared-surface` "
                        f"\u2014 absent: fixture\n")
    rc, out, _err = run_tool(["--repo", str(wrong_dir)])
    parsed = summary_of(out)
    check("wrong-tag",
          rc == 1 and parsed is not None and parsed["uncovered"] == parsed["contradicted"]
          and parsed["uncovered"] > 0,
          f"rc={rc} contradicted={parsed and parsed['contradicted']} "
          f"uncovered={parsed and parsed['uncovered']}")

    # Arm 6: deleting a base marker line trips the rewrite check.
    rewrite_repo = root / "f4-rewritten"
    rewrite_repo.mkdir()
    (rewrite_repo / PROVINCE_NAME).write_text(base_text, encoding="utf-8")
    rc, _out, err = git(rewrite_repo, "init", "-q")
    if rc != 0:
        check("rewritten-marker", False, f"git init failed: {err[:120]}")
    else:
        rc, top, err = git(rewrite_repo, "rev-parse", "--show-toplevel")
        if rc != 0 or os.path.realpath(top) != os.path.realpath(str(rewrite_repo)):
            check("rewritten-marker", False, f"toplevel assertion failed: {top or err}")
        else:
            rc, _out, err = git(rewrite_repo, "add", PROVINCE_NAME)
            rc2, _out2, err2 = git(rewrite_repo, "-c", "user.name=kama-r71",
                                   "-c", "user.email=kama-r71@example.invalid",
                                   "commit", "-q", "-m", "fixture base")
            rev = git(rewrite_repo, "rev-parse", "HEAD")[1]
            if rc != 0 or rc2 != 0 or not rev:
                check("rewritten-marker", False, f"fixture commit failed: {err or err2}")
            else:
                (rewrite_repo / PROVINCE_NAME).write_text(
                    drop_marker_block(base_text, "qwen-coder-unit"), encoding="utf-8")
                rc, out, err = run_tool(
                    ["--repo", str(rewrite_repo), "--base", rev])
                check("rewritten-marker",
                      rc == 1 and "PROVINCE_HOST_CLAIMS_REWRITTEN qwen-coder-unit" in out,
                      f"rc={rc} rewritten_line="
                      f"{'yes' if 'PROVINCE_HOST_CLAIMS_REWRITTEN qwen-coder-unit' in out else 'no'}")

    # Arm 7: no contradicted marker and every extra covered -> exit 0.
    clean_dir = fixture("f5-clean",
                        "# province fixture\n\n"
                        "- absent-on-this-host (2026-10-31) "
                        "`province-host:qwen-coder-unit` \u2014 fixture paragraph "
                        "naming no other surface.\n")
    rc, out, err = run_tool(["--repo", str(clean_dir), "--json"])
    clean_data = json.loads(out)
    clean_text = (clean_dir / PROVINCE_NAME).read_text(encoding="utf-8")
    clean_text += "\n" + correction_lines(clean_data["claims"], date) + "\n"
    (clean_dir / PROVINCE_NAME).write_text(clean_text, encoding="utf-8")
    rc, out, _err = run_tool(["--repo", str(clean_dir)])
    parsed = summary_of(out)
    check("no-contradiction",
          rc == 0 and parsed is not None and parsed["uncovered"] == 0
          and parsed["extra"] == 4,
          f"rc={rc} uncovered={parsed and parsed['uncovered']} "
          f"contradicted={parsed and parsed['contradicted']}")

    if not keep:
        shutil.rmtree(root, ignore_errors=True)
    failures = [item for item in checks if not item[1]]
    for name, ok, note in checks:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {note}")
    print(f"PROVINCE_HOST_CLAIMS_SELFTEST pass={len(checks) - len(failures)} "
          f"fail={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
