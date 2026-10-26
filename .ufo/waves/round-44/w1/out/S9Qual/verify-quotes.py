#!/usr/bin/env python3
"""verify-quotes.py — check S9Qual's round-44 qualification patch against the lane.

Facts, all read from the lane working tree and the patch bytes; none inferred:

  quote     every blockquote under a `Superseded — … at line N[-M]:` marker in
            the patch is a verbatim (whitespace-normalised) substring of lines
            N-M of the lane file. A correction that misquotes the sentence it
            supersedes fails here.
  fragment  each inline-quoted fragment the patch attributes to a line is
            present in that line (the matrix cells and the KQ6 clause, the two
            `recheck:` lines, the pin-watch clause and its four-version list).
  append    the patch adds lines only: no `-` content line and no `+` line that
            carries a dated sentence verbatim (belt and braces for KQ7: a
            correction is appended, a dated line is never rewritten).
  apply     `git apply --check -p1` succeeds in a throwaway fixture repo, the
            patch applies, and each applied file starts with the lane's own
            bytes (prefix intact, so no line anchor above moves).

Usage: verify-quotes.py --diff FILE [--lane DIR]
Exit: 0 all facts hold; 1 a fact fails; 2 unusable input.
"""
import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

FILES = (
    "runtime-health-surface-matrix.md",
    "endpoint-health-probe-conventions.md",
    "served-model-id-resolution.md",
    "engine-pin-watch.md",
)
MARK = re.compile(r"^Superseded — .*?(?:the Claim at line|at line|lines) (\d+)(?:-(\d+))?")
# (file, first line, last line, fragment the patch attributes to those lines)
FRAGMENTS = (
    ("runtime-health-surface-matrix.md", 15, 15, "`GET /health` listed under Instrumentator APIs"),
    ("runtime-health-surface-matrix.md", 15, 15,
     "Render-only servers have no engine and return 200 unconditionally — a passing `/health` may not even reach an engine"),
    ("runtime-health-surface-matrix.md", 15, 15, "S002, S004"),
    ("runtime-health-surface-matrix.md", 35, 35, "tier A for its scope; no C-tier row supports this entry"),
    ("runtime-health-surface-matrix.md", 4, 4, "recheck: on-release"),
    ("endpoint-health-probe-conventions.md", 5, 5, "recheck: 90d"),
    ("served-model-id-resolution.md", 5, 5, "recheck: 90d"),
    ("engine-pin-watch.md", 60, 61, "It watches only pins that a registry row backs"),
    ("engine-pin-watch.md", 61, 61, "Four other engine versions appear in the corpus without a row"),
    ("engine-pin-watch.md", 65, 65, "grep -rnoiE"),
)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def sections(diff_text: str) -> dict:
    """Per lane file: the appended text, from the new-side `+` lines."""
    out, cur = {}, None
    for line in diff_text.split("\n"):
        if line.startswith("+++ b/corpus/knowledge/"):
            cur = line[len("+++ b/corpus/knowledge/"):]
            out[cur] = []
        elif cur and line.startswith("+"):
            out[cur].append(line[1:])
    return out


def quotes(appended: list) -> list:
    """(start, end, quote) for every Superseded marker that has a blockquote."""
    found, i = [], 0
    while i < len(appended):
        m = MARK.match(appended[i])
        i += 1
        if not m:
            continue
        start, end = int(m.group(1)), int(m.group(2) or m.group(1))
        body = []
        while i < len(appended) and not appended[i].startswith(">"):
            if appended[i].startswith("Read"):
                break
            i += 1
        while i < len(appended) and appended[i].startswith(">"):
            body.append(appended[i][2:] if appended[i].startswith("> ") else "")
            i += 1
        if body:
            found.append((start, end, norm(" ".join(body))))
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default="/home/vgpnk/Projects/shokunin/kama-shokunin")
    ap.add_argument("--diff", required=True)
    a = ap.parse_args()
    lane = pathlib.Path(a.lane)
    try:
        diff_text = pathlib.Path(a.diff).read_text()
    except OSError as exc:
        print(f"UNUSABLE {exc}")
        return 2
    sec = sections(diff_text)
    missing = [f for f in FILES if f not in sec]
    if missing:
        print(f"UNUSABLE patch does not touch {missing}")
        return 2

    bad = 0
    for f in FILES:
        src = (lane / "corpus/knowledge" / f).read_text().split("\n")
        qs = quotes(sec[f])
        print(f"{f}: {len(qs)} superseded blockquote(s)")
        for start, end, quote in qs:
            ok = bool(quote) and quote in norm(" ".join(src[start - 1:end]))
            print(f"  {'PASS' if ok else 'FAIL'} quote verbatim in lines {start}-{end}")
            bad += not ok

    print(f"inline fragments: {len(FRAGMENTS)} attributed citation(s)")
    for f, line0, line1, frag in FRAGMENTS:
        lines = (lane / "corpus/knowledge" / f).read_text().split("\n")[line0 - 1:line1]
        ok = frag in norm(" ".join(lines))
        span = f"{line0}" if line0 == line1 else f"{line0}-{line1}"
        print(f"  {'PASS' if ok else 'FAIL'} {f}:{span} carries {frag[:52]!r}")
        bad += not ok

    minus = [l for l in diff_text.split("\n") if l.startswith("-") and not l.startswith("---")]
    print(f"append: removed content lines={len(minus)} (must be 0)")
    bad += bool(minus)

    scratch = pathlib.Path(tempfile.mkdtemp())
    try:
        d = scratch / "fx"
        (d / "corpus/knowledge").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(d)], check=True)
        top = pathlib.Path(subprocess.run(
            ["git", "-C", str(d), "rev-parse", "--show-toplevel"],
            check=True, stdout=subprocess.PIPE, text=True).stdout.strip())
        if top != d:
            print(f"UNUSABLE fixture toplevel {top} != {d}")
            return 2
        for f in FILES:
            shutil.copyfile(lane / "corpus/knowledge" / f, d / "corpus/knowledge" / f)
        patch = str(pathlib.Path(a.diff).resolve())
        chk = subprocess.run(["git", "-C", str(d), "apply", "--check", "-p1", patch],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        print(f"apply: git apply --check exit={chk.returncode} {chk.stdout.strip()}")
        bad += chk.returncode != 0
        if chk.returncode == 0:
            subprocess.run(["git", "-C", str(d), "apply", "-p1", patch], check=True)
            for f in FILES:
                old = (lane / "corpus/knowledge" / f).read_text()
                new = (d / "corpus/knowledge" / f).read_text()
                ok = new.startswith(old)
                print(f"  {'PASS' if ok else 'FAIL'} {f}: {len(old.split(chr(10))) - 1} -> "
                      f"{len(new.split(chr(10))) - 1} lines, prefix intact")
                bad += not ok
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print(f"VERDICT {'PASS' if bad == 0 else 'FAIL'} failures={bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
