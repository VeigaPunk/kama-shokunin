#!/usr/bin/env python3
"""case29_derive.py - independent re-derivation of the SCORECARD `## Axes` evidence table.

Does NOT import or reuse tools/round41-scorecard-reconcile.py or
tools/round42-selfdesc-reconcile.py. Reads SCORECARD.md (or a `git show` of a
revision), extracts every `run `CMD` -> `OUT`` and `PATH` sha256 `HEX` (N lines)
fact from the six axis rows, re-executes/recomputes each at the lane, and
additionally checks the *stated scope* of the freshness count (S001-S477) against
the live registry bound -- the check the self-description counter does not make.

Usage: case29_derive.py [--rev REV]  (default: working tree)
Exit 0 iff every fact and scope check agrees.
"""
import argparse, hashlib, os, re, shlex, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
RUN_RE = re.compile(r"run `([^`]+)` → `([^`]*)`")
HASH_RE = re.compile(r"`([^`]+)` (sha256|md5) `([0-9a-f]{32,64})`(?: \((\d+) lines?\))?")


def scorecard_text(rev):
    if rev:
        return subprocess.run(["git", "-C", LANE, "show", f"{rev}:SCORECARD.md"],
                              capture_output=True, text=True).stdout
    return open(os.path.join(LANE, "SCORECARD.md")).read()


def axes_rows(text):
    lines = text.split("\n")
    try:
        start = lines.index("## Axes")
    except ValueError:
        raise SystemExit("no ## Axes")
    rows = []
    AX = {"operability", "freshness", "depth", "coverage", "calibration", "adjacency"}
    for l in lines[start + 1:]:
        if l.startswith("#"):
            break
        if not l.startswith("|"):
            continue
        cells = [c.strip() for c in l.strip().strip("|").split("|")]
        if len(cells) != 4:
            continue
        name = cells[0].strip("* ").split(" ")[0].lower()
        if name in AX and name not in [r[0] for r in rows]:
            rows.append((name, cells[2]))
    return rows


def run(cmd):
    p = subprocess.run(["bash", "-c", cmd], cwd=LANE, capture_output=True, text=True, timeout=600)
    return p.returncode, p.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rev")
    a = ap.parse_args()
    text = scorecard_text(a.rev)
    rows = axes_rows(text)
    bad = 0
    print(f"source={'HEAD:'+a.rev if a.rev else 'worktree'} axes={len(rows)}")
    for axis, ev in rows:
        print(f"[{axis}]")
        if a.rev:
            print("  (rev mode: RUN/HASH legs are worktree-bound and skipped)")
            m = re.search(r"verifier-spotcheck\.md'\)\)\)` → `(\d+)`", ev)
            if m:
                print(f"  COUNT asserted={m.group(1)} (rev-mode glob is not rev-bound; see worktree leg)")
            continue
        for cmd, want in RUN_RE.findall(ev):
            rc, out = run(cmd)
            got = [x.strip() for x in out.split("\n") if x.strip()]
            ok = want in got
            bad += 0 if ok else 1
            print(f"  RUN  {'OK ' if ok else 'BAD'} cmd={cmd!r}")
            print(f"       want={want!r} got={got[:3] if not ok else 'match'!r} exit={rc}")
            if axis == "freshness" and "recheck" in cmd:
                m = re.search(r"<=(\d+)", cmd)
                bound = int(m.group(1)) if m else None
                src = open(os.path.join(LANE, "corpus/SOURCES.md")).read()
                ids = [int(x) for x in re.findall(r"^\|\s*S(\d+)\s*\|", src, re.M)]
                have = sum(1 for l in src.split("\n") if l.startswith("| S") and l.split("|")[10].strip())
                over = [i for i in ids if bound and i > bound]
                print(f"       SCOPE stated<=S{bound} registry_max=S{max(ids)} rows={len(ids)} "
                      f"excluded_rows={len(over)} recheck_all={have} recheck_in_window={got[0] if got else '?'}")
                if over:
                    bad += 1
        for path, algo, want, lines in (HASH_RE.findall(ev) if not a.rev else []):
            p = os.path.join(LANE, path)
            if not os.path.exists(p):
                print(f"  PATH BAD missing {path}"); bad += 1; continue
            data = open(p, "rb").read()
            got = (hashlib.sha256(data) if algo == "sha256" else hashlib.md5(data)).hexdigest()
            n = data.count(b"\n")
            ok = got == want and (not lines or int(lines) == n)
            bad += 0 if ok else 1
            print(f"  HASH {'OK ' if ok else 'BAD'} {path} {algo} lines={n} want_lines={lines or '-'}")
            if not ok:
                print(f"       want={want} got={got}")
    if a.rev:
        src = open(os.path.join(LANE, "corpus/SOURCES.md")).read()
        ids = [int(x) for x in re.findall(r"^\|\s*S(\d+)\s*\|", src, re.M)]
        print(f"  (rev mode: registry snapshot is worktree: max=S{max(ids)} rows={len(ids)})")
    if not a.rev:
        # calibration row scope claim: the glob count sentence
        m = re.search(r"verifier-spotcheck\.md'\)\)\)` → `(\d+)`", text)
        if m:
            import glob
            got = len(glob.glob(os.path.join(LANE, "corpus/lessons/*verifier-spotcheck.md")))
            ok = int(m.group(1)) == got
            bad += 0 if ok else 1
            print(f"  COUNT {'OK ' if ok else 'BAD'} verifier-spotcheck asserted={m.group(1)} observed={got}")
    print(f"FAILURES={bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
