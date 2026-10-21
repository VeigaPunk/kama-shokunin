#!/usr/bin/env python3
"""Hand-built C06-channel variants; independent of repo-state-grid.py.
Each variant builds fresh /tmp repos and runs both auditors."""
import json, os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/tmp/kama-r23w2/c06/var")
FROZEN = "/tmp/frozen-audit-C06.py"
CURRENT = "/tmp/kama-r23w2/RowC06ErrataCorrects-2/tools/report-landing-audit.py"
FAKE = "1234567890abcdef1234567890abcdef12345678"

def env(extra=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture")
    if extra: e.update(extra)
    return e

def g(repo, *args, **kw):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       env=env(kw.get("extra")), input=kw.get("data"))
    if p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode(errors='replace')}")
    return p.stdout.decode().strip()

def init(path):
    path.mkdir(parents=True)
    g(path, "init", "-q", "-b", "master")
    return path

def commit(repo, author, when, msg, path="f", content=None):
    t = Path(repo, path); t.parent.mkdir(parents=True, exist_ok=True)
    if content is None:
        with open(t, "ab") as fh: fh.write((msg + "\n").encode())
    else:
        t.write_bytes(content)
    g(repo, "add", "--", path)
    stamp = f"@{when} +0000"
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      extra={"GIT_AUTHOR_NAME": author, "GIT_COMMITTER_NAME": author,
             "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
    return g(repo, "rev-parse", "HEAD")

def base(root, lane_extra=None):
    lane, fleet = init(root / "lane"), init(root / "fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    rel = ".ufo/reports/round-1/kama.md"
    commit(fleet, "fleet", 2000, "round-1: report", rel,
           f"# kama round 1\n\n## Landed changes\n\n- {lc}\n".encode())
    x = commit(lane, "kama-shokunin", 1500, "round-1: more")
    return lane, fleet, lc, x

def errata(lane, rows, author="fixture", subject="errata", when=1600,
           crlf=False, raw=None):
    text = raw if raw is not None else "".join(
        "\t".join(r) + "\n" for r in rows)
    if crlf:
        text = text.replace("\n", "\r\n")
    commit(lane, author, when, subject, "registry/report-landing-errata.tsv",
           text.encode())
    return text

def run(auditor, root, extra=()):
    p = subprocess.run([sys.executable, auditor, "--lane-repo", str(root / "lane"),
                        "--fleet-repo", str(root / "fleet"), "--json",
                        "--rounds", "1", *extra],
                       capture_output=True, env=env(), cwd=root)
    doc = None
    if p.stdout:
        try: doc = json.loads(p.stdout)
        except ValueError: doc = None
    kinds = None
    if doc:
        kinds = sorted({d["kind"] for r in doc["results"] for d in r["defects"]})
    return {"exit": p.returncode, "kinds": kinds,
            "corrected": doc and doc["summary"]["corrected"],
            "uncorrected": doc and doc["summary"]["uncorrected"],
            "unmatched": doc and doc["summary"]["errata_unmatched"],
            "invalid": doc and doc["summary"]["errata_invalid"],
            "status": doc and doc["summary"]["status"],
            "stderr": p.stderr.decode(errors="replace").strip()[-160:]}

VARIANTS = {}

def variant(name):
    def deco(fn):
        VARIANTS[name] = fn
        return fn
    return deco

@variant("01-baseline-control")
def v01(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, x, "ev"]])

def fake_report(root, token=FAKE):
    lane, fleet, lc, x = base(root)
    # commit the report with token outside Landed changes
    commit(fleet, "fleet", 2100, "extend report",
           ".ufo/reports/round-1/kama.md",
           f"# kama round 1\n\n## Landed changes\n\n- {lc}\n\n## Notes\n\nsee {token}\n".encode())
    return lane, lc, x

@variant("02-unresolved-correction-unrelated-real-commit")
def v02(root):
    lane, lc, x = fake_report(root)
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"],
                  ["1", "unresolved-full-hash", FAKE, lc, "unrelated real commit"]])

@variant("03-unresolved-correction-uppercase-real-commit")
def v03(root):
    lane, lc, x = fake_report(root)
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"],
                  ["1", "unresolved-full-hash", FAKE, lc.upper(), "uppercase"]])

@variant("04-unresolved-correction-head")
def v04(root):
    lane, lc, x = fake_report(root)
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"],
                  ["1", "unresolved-full-hash", FAKE, "HEAD", "revision expr"]])

@variant("05-omitted-token-uppercase")
def v05(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x.upper(), x.upper(), "uppercase"]])

@variant("06-omitted-token-prefix")
def v06(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x[:7], x, "prefix token"]])

@variant("07-section-missing-free-text-correction")
def v07(root):
    lane, fleet = init(root / "lane"), init(root / "fleet")
    commit(lane, "someone", 1000, "not a round commit")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", b"# kama round 1\n\nno section\n")
    errata(lane, [["1", "landed-section-missing", "-",
                   "canonical text restated elsewhere", "prose"]])

@variant("08-crlf-ledger")
def v08(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, x, "ev"]], crlf=True)

@variant("09-duplicate-correct-rows")
def v09(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, x, "a"],
                  ["1", "landed-omitted", x, x, "b"]])

@variant("10-empty-evidence")
def v10(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, x, ""]])

@variant("11-stale-row-after-report-cites")
def v11(root):
    lane, fleet = init(root / "lane"), init(root / "fleet")
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work")
    x = commit(lane, "kama-shokunin", 1500, "round-1: more")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md",
           f"# kama round 1\n\n## Landed changes\n\n- {lc}\n- {x}\n".encode())
    errata(lane, [["1", "landed-omitted", x, x, "stale"]])

@variant("12-ledger-commit-is-round-commit")
def v12(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, x, "ev"]],
           author="kama-shokunin", subject="round-1: ledger")

@variant("13-omitted-correction-different-real-commit")
def v13(root):
    lane, fleet, lc, x = base(root)
    errata(lane, [["1", "landed-omitted", x, lc, "wrong commit"]])

@variant("14-unresolved-correction-zero-hash")
def v14(root):
    lane, fleet, lc, x = base(root)
    commit(fleet, "fleet", 2100, "notes", ".ufo/reports/round-1/notes.md",
           ("## Notes\n\nsee " + FAKE + "\n").encode())
    errata(lane, [["1", "unresolved-full-hash", FAKE, "0" * 40, "zero"]])

@variant("15-uppercase-citation-ignored")
def v15(root):
    lane, lc, x = fake_report(root, FAKE.upper())
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"]])

@variant("16-section-missing-missing-object-correction")
def v16(root):
    lane, fleet = init(root / "lane"), init(root / "fleet")
    commit(lane, "someone", 1000, "not a round commit")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", b"# kama round 1\n\nno section\n")
    errata(lane, [["1", "landed-section-missing", "-", "f" * 40, "bogus sha"]])

@variant("17-unresolved-correction-repeats-token")
def v17(root):
    lane, lc, x = fake_report(root)
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"],
                  ["1", "unresolved-full-hash", FAKE, FAKE, "token repeated"]])

@variant("18-unresolved-correction-uppercase-7-prefix")
def v18(root):
    lane, lc, x = fake_report(root)
    errata(lane, [["1", "landed-omitted", x, x, "clear omission"],
                  ["1", "unresolved-full-hash", FAKE, lc[:7].upper(), "upper prefix"]])

def main():
    if ROOT.exists(): shutil.rmtree(ROOT)
    out = {}
    for name, fn in VARIANTS.items():
        root = ROOT / name
        root.mkdir(parents=True)
        fn(root)
        out[name] = {arm: run(a, root) for arm, a in
                     (("frozen", FROZEN), ("current", CURRENT))}
    print(json.dumps(out, indent=1, sort_keys=True))

if __name__ == "__main__":
    main()
