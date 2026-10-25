#!/usr/bin/env python3
"""R41A14 — C1 `## Axes` table mutation probe.

Fixture: /tmp/R41A14-vrlPZz/repo — clone of /fast/scratch/kama-r41/clone at tip
24aa1d3485c107f88b8b838892d43ea7587befcf. For each mutant: reset fixture to
pristine tip, apply exactly one single-substring mutation inside the one
`## Axes` table row that carries the targeted fact, commit, run the C1 counter
(tools/round41-scorecard-reconcile.py) at the mutant commit, record verdict.
Restores pristine bytes at the end and re-runs the counter on the restored tip.
"""
import hashlib
import json
import os
import subprocess

REPO = "/tmp/R41A14-vrlPZz/repo"
TIP = "24aa1d3485c107f88b8b838892d43ea7587befcf"
COUNTER = os.path.join(REPO, "tools", "round41-scorecard-reconcile.py")
SC = "SCORECARD.md"
LOG = "/tmp/R41A14-mutlog.txt"

# (id, class, axis, old, new, note)
MUTANTS = [
    ("H1", "hash", "operability", "`36b64978", "`46b64978",
     "cited sha256 of tools/kama-probe.sh, first hex char 3->4"),
    ("H2", "hash", "freshness", "`236c23c1", "`336c23c1",
     "cited sha256 of tools/test-snapshot.sh, first hex char 2->3"),
    ("H3", "hash", "depth", "`151023b9", "`251023b9",
     "cited sha256 of SKILL.md, first hex char 1->2"),
    ("H4", "hash", "depth", "`0100ac6d", "`1100ac6d",
     "cited sha256 of corpus/knowledge/endpoint-identity.md, first hex char 0->1"),
    ("H5", "hash", "coverage", "`dbb5f4f7", "`ebb5f4f7",
     "cited sha256 of PROVINCE.md, first hex char d->e"),
    ("H6", "hash", "adjacency", "`1801cb7f", "`2801cb7f",
     "cited sha256 of corpus/knowledge/cross-lane-scope.md, first hex char 1->2"),
    ("L1", "lines", "operability", "(1138 lines)", "(1139 lines)",
     "tools/kama-probe.sh line count +1"),
    ("L2", "lines", "freshness", "(194 lines)", "(195 lines)",
     "tools/test-snapshot.sh line count +1"),
    ("L3", "lines", "depth", "(1375 lines)", "(1376 lines)",
     "SKILL.md line count +1"),
    ("L4", "lines", "depth", "(218 lines)", "(219 lines)",
     "corpus/knowledge/endpoint-identity.md line count +1"),
    ("L5", "lines", "coverage", "(169 lines)", "(170 lines)",
     "PROVINCE.md line count +1"),
    ("L6", "lines", "adjacency", "(87 lines)", "(88 lines)",
     "corpus/knowledge/cross-lane-scope.md line count +1"),
    ("R1", "run", "operability", "`RESULT pass=30 fail=0`", "`RESULT pass=30 fail=1`",
     "expected stdout line of run `bash tools/test-snapshot.sh`"),
    ("R2", "run", "operability", "`selftest cases=79 failed=0`", "`selftest cases=79 failed=1`",
     "expected stdout line of run `python3 tools/report-landing-audit.py --selftest`"),
    ("R3", "run", "operability", "`42/42 selftest cases passed`", "`41/42 selftest cases passed`",
     "expected stdout line of run `python3 tools/sources-append-only.py --selftest`"),
    ("R4", "run", "freshness", "`selftest: ok (24 cases)`", "`selftest: ok (25 cases)`",
     "expected stdout line of run `python3 tools/citation-provenance.py --selftest`"),
    ("R5", "run", "calibration", "`CAP_SELFTEST pass=2 fail=0`", "`CAP_SELFTEST pass=2 fail=1`",
     "expected stdout line of run `python3 tools/capability-repertoire-audit.py --selftest`"),
    ("R6", "run", "calibration", "`IA_SELFTEST pass=4 fail=0`", "`IA_SELFTEST pass=4 fail=1`",
     "expected stdout line of run `python3 tools/instrument-agreement.py --selftest`"),
    ("P1", "path", "coverage", "endpoint-health-probe-conventions.md",
     "xndpoint-health-probe-conventions.md",
     "dead-checked held-ground path, first basename char -> x"),
    ("P2", "path", "coverage", "kv-cache-reclamation-models.md",
     "xv-cache-reclamation-models.md", "dead-checked held-ground path"),
    ("P3", "path", "coverage", "serving-alias-contract.md",
     "xerving-alias-contract.md", "dead-checked held-ground path"),
    ("P4", "path", "calibration", "round41-scorecard-reconcile.py",
     "xound41-scorecard-reconcile.py", "dead-checked counter path"),
    ("P5", "path", "calibration", "round-40-verifier-spotcheck.md",
     "xound-40-verifier-spotcheck.md", "dead-checked lesson path"),
    ("P6", "path", "adjacency", "PROVINCE.md", "XROVINCE.md",
     "dead-checked PROVINCE.md token in adjacency row"),
    ("S1", "score", "operability", "| **operability** | **8** |", "| **operability** | **9** |",
     "score 8 -> 9 (counter expects 8)"),
    ("S2", "score", "freshness", "| **freshness** | **8** |", "| **freshness** | **9** |",
     "score 8 -> 9 (counter expects 8)"),
    ("S3", "score", "depth", "| depth | **7** |", "| depth | **8** |",
     "score 7 -> 8 (counter expects 7)"),
    ("S4", "score", "coverage", "| coverage | **9** |", "| coverage | **10** |",
     "score 9 -> 10 (counter expects 9)"),
    ("S5", "score", "calibration", "| calibration | **7** |", "| calibration | **8** |",
     "score 7 -> 8 (counter expects 7)"),
    ("S6", "score", "adjacency", "| adjacency | **7** |", "| adjacency | **8** |",
     "score 7 -> 8 (counter expects 7)"),
]


def sh(*args):
    return subprocess.run(list(args), capture_output=True, text=True)


def git(*args):
    p = sh("git", "-C", REPO, *args)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout.strip()


def rows_of(text):
    """Mirror the counter's axes_table(): {axis: (lineno0, line)} for the new table."""
    lines = text.split("\n")
    start = lines.index("## Axes")
    out = {}
    in_table = False
    for i in range(start + 1, len(lines)):
        ln = lines[i]
        if ln.startswith("## "):
            break
        if ln.startswith("|"):
            in_table = True
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if cells[0] == "Axis" or cells[0].startswith("---"):
                continue
            axis = cells[0].replace("*", "").strip().split(" ")[0].lower()
            out.setdefault(axis, (i, ln))
        elif in_table:
            break
    return out, lines


def main():
    sc_path = os.path.join(REPO, SC)
    pristine = open(sc_path, "rb").read()
    pristine_sha = hashlib.sha256(pristine).hexdigest()
    rows0, _ = rows_of(pristine.decode("utf-8"))
    expected_axes = {"operability", "freshness", "depth", "coverage",
                     "calibration", "adjacency"}
    assert set(rows0) == expected_axes, sorted(rows0)

    log = []
    results = []
    for mid, cls, axis, old, new, note in MUTANTS:
        git("reset", "-q", "--hard", TIP)
        text = open(sc_path, "rb").read().decode("utf-8")
        rows, lines = rows_of(text)
        lineno, rowline = rows[axis]
        n = rowline.count(old)
        assert n == 1, f"{mid}: old substring occurs {n}x in {axis} row, expected 1"
        newline = rowline.replace(old, new)
        assert newline != rowline
        before_lines = text.split("\n")
        lines[lineno] = newline
        mutated = "\n".join(lines).encode("utf-8")
        changed = [i for i, (a, b) in enumerate(zip(before_lines, lines)) if a != b]
        assert changed == [lineno], f"{mid}: changed lines {changed}, expected [{lineno}]"
        open(sc_path, "wb").write(mutated)
        git("add", SC)
        git("-c", "user.name=R41A14 mutation probe", "-c", "user.email=r41a14@probe.invalid",
            "commit", "-q", "-m", f"mutant {mid} ({cls}/{axis}): {note}")
        commit = git("rev-parse", "HEAD")
        p = sh("python3", COUNTER, "--repo", REPO, "--tip", commit)
        summary = next((l for l in p.stdout.splitlines() if l.startswith("axes=")), "")
        details = [l for l in p.stdout.splitlines() if l.startswith("detail:")]
        if p.returncode == 0 and "met=True" in summary:
            verdict = "SURVIVOR"
        elif p.returncode == 1 and "met=False" in summary:
            verdict = "killed"
        else:
            verdict = "INCONCLUSIVE"
        results.append(dict(id=mid, cls=cls, axis=axis, old=old, new=new, note=note,
                            commit=commit, rc=p.returncode, summary=summary,
                            details=details, verdict=verdict, row_line=lineno + 1))
        log.append(f"=== mutant {mid} ({cls}/{axis}) commit {commit} rc={p.returncode} verdict={verdict}")
        log.append(f"    row: SCORECARD.md:{lineno + 1}")
        log.append(f"    old: {old}")
        log.append(f"    new: {new}")
        log.append("    counter stdout:")
        log.extend("      " + l for l in p.stdout.splitlines())
        if p.stderr.strip():
            log.append("    counter stderr:")
            log.extend("      " + l for l in p.stderr.splitlines())
        log.append("")

    # restore pristine bytes and re-run the detector
    git("reset", "-q", "--hard", TIP)
    restored = open(sc_path, "rb").read()
    restored_sha = hashlib.sha256(restored).hexdigest()
    p = sh("python3", COUNTER, "--repo", REPO, "--tip", TIP)
    restored_summary = next((l for l in p.stdout.splitlines() if l.startswith("axes=")), "")
    status = git("status", "--porcelain")

    log.append("=== restoration ===")
    log.append(f"    pristine SCORECARD.md sha256: {pristine_sha}")
    log.append(f"    restored SCORECARD.md sha256: {restored_sha}")
    log.append(f"    byte-identical: {pristine == restored}")
    log.append(f"    restored counter run rc={p.returncode}: {restored_summary}")
    log.append(f"    git status --porcelain after restore: {'' if status == '' else status!r}")

    with open(LOG, "w") as f:
        f.write("\n".join(log) + "\n")

    survivors = [r for r in results if r["verdict"] == "SURVIVOR"]
    inconclusive = [r for r in results if r["verdict"] == "INCONCLUSIVE"]
    print(json.dumps(dict(
        mutants=len(results),
        killed=sum(1 for r in results if r["verdict"] == "killed"),
        survivors=[r["id"] for r in survivors],
        inconclusive=[r["id"] for r in inconclusive],
        pristine_sha256=pristine_sha,
        restored_sha256=restored_sha,
        restored_byte_identical=pristine == restored,
        restored_counter=restored_summary,
        restored_rc=p.returncode,
        porcelain=status,
    ), indent=2))
    print("\nper-mutant:")
    for r in results:
        print(f"{r['id']} {r['cls']:<5} {r['axis']:<12} SCORECARD.md:{r['row_line']:<3} "
              f"rc={r['rc']} {r['verdict']:<12} {r['summary']}")
        for d in r["details"]:
            print(f"    {d}")


if __name__ == "__main__":
    main()
