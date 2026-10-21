#!/usr/bin/env python3
"""C1JsonFields (FALSIFY, round 21): independent recount of the JSON emitted by
tools/report-landing-audit.py --rounds 10-20 --no-errata --json at the measured
commit b76727f31e522763ce24e43d6ec86d21b507a11f.

Read-only: git log/show/cat-file/rev-parse/hash-object; no ref, index or lane/fleet
file writes. Exit 0 = zero mismatches, 1 = at least one, 2 = not evaluable.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
FLEET = Path("/home/vgpnk/Projects/shokunin")
MEAS = "b76727f31e522763ce24e43d6ec86d21b507a11f"
RAW = LANE / ".ufo/waves/round-21/runs/b76727f3/c1-audit-raw.stdout"
RAW_SHA256 = "af2707adf5c2424ebe64b30505d33d94b0c5ca08f2d843cf6a27a4aa10651e24"
ROUNDS = range(10, 21)
KINDS = ("unresolved-full-hash", "landed-unresolved", "landed-ambiguous",
         "landed-omitted", "landed-section-missing")
ABB = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])")
FULL = re.compile(r"(?<![0-9A-Za-z])[0-9a-f]{40}(?![0-9A-Za-z])")
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_OPTIONAL_LOCKS="0", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
FAILS = []


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, env=ENV)
    return p.returncode, p.stdout.decode("utf-8", "replace"), p.stderr.decode("utf-8", "replace")


def G(repo, *args):
    rc, out, err = git(repo, *args)
    if rc:
        raise SystemExit(f"could-not-evaluate: git {' '.join(args)} rc={rc}: {err.strip()}")
    return out


def check(label, ok, detail=""):
    print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f" | {detail}" if detail else ""))
    if not ok:
        FAILS.append(label)


def lcp(a, b):
    n = 0
    for x, y in zip(a, b):
        if x != y:
            break
        n += 1
    return n


def main():
    raw = RAW.read_bytes()
    check("raw stream sha256 == commands.json c1-audit-raw stdout_sha256",
          hashlib.sha256(raw).hexdigest() == RAW_SHA256)
    doc = json.loads(raw)
    results = {r["round"]: r for r in doc["results"]}

    tool_src = G(LANE, "show", f"{MEAS}:tools/report-landing-audit.py")
    with tempfile.TemporaryDirectory(prefix="c1-json-recount-") as tmp:
        tool = Path(tmp, "report-landing-audit.py")
        tool.write_text(tool_src, encoding="utf-8")
        p = subprocess.run([sys.executable, str(tool), "--lane-repo", str(LANE),
                            "--fleet-repo", str(FLEET), "--branch", MEAS,
                            "--rounds", "10-20", "--no-errata", "--json"],
                           capture_output=True, env=ENV)
    check("committed tool@MEAS reproduces measured stdout byte-for-byte (exit 1)",
          p.stdout == raw and p.returncode == 1, f"rc={p.returncode}")

    fmt = "%H%x1f%at%x1f%an%x1f%s"
    recs = [line.split("\x1f", 3) for line in G(LANE, "log", f"--format={fmt}", MEAS).splitlines() if line]
    print(f"measured-history commits={len(recs)}")

    kinds_count = {k: 0 for k in KINDS}
    total = sum_req = sum_post = 0
    for r in ROUNDS:
        rel = f".ufo/reports/round-{r}/kama.md"
        j = results[r]
        adds = [line.split(" ") for line in
                G(FLEET, "log", "--diff-filter=A", "--format=%H %at", "--", rel).splitlines() if line]
        check(f"r{r} exactly one add commit", len(adds) == 1, f"adds={len(adds)}")
        add_sha, cutoff = adds[-1][0], int(adds[-1][1])
        rows = [(sha, int(at), subj) for sha, at, an, subj in recs
                if an == "kama-shokunin" and re.match(rf"^(?:round-{r}:|checkpoint\(r{r}\))", subj)]
        req = [x for x in rows if x[1] <= cutoff]
        post = [x for x in rows if x[1] > cutoff]
        sum_req += len(req)
        sum_post += len(post)

        text = (FLEET / rel).read_text(encoding="utf-8")
        lines = text.split("\n")
        wt = G(FLEET, "hash-object", "--", rel).strip()
        head = git(FLEET, "rev-parse", "-q", "--verify", f"HEAD:{rel}")[1].strip()
        blob_add = G(FLEET, "rev-parse", f"{add_sha}:{rel}").strip()
        check(f"r{r} worktree == HEAD == first-add blob", wt == head == blob_add,
              f"wt={wt[:10]} head={head[:10]} add={blob_add[:10]}")

        start = next((i for i, l in enumerate(lines) if l.startswith("## Landed changes")), None)
        sec = None
        if start is not None:
            end = next((k for k in range(start + 1, len(lines)) if lines[k].startswith("## ")), len(lines))
            sec = "\n".join(lines[start + 1:end])
        cited_sec = set(ABB.findall(sec)) if sec is not None else set()
        cited_all = set(ABB.findall(text))

        exp = []  # (kind, token, cited_elsewhere as str)
        if sec is None:
            exp.append(("landed-section-missing", "-", "n/a"))
        for t in sorted(set(FULL.findall(text))):
            if git(LANE, "cat-file", "-e", t)[0] and git(FLEET, "cat-file", "-e", t)[0]:
                exp.append(("unresolved-full-hash", t, "n/a"))
                bp = max(recs, key=lambda c: lcp(t, c[0]))
                bs = max(recs, key=lambda c: lcp(t[::-1], c[0][::-1]))
                print(f"    unresolved {t}: prefix {lcp(t, bp[0])} chars match {bp[0][:12]}, "
                      f"suffix {lcp(t[::-1], bs[0][::-1])} chars match {bs[0][:12]}")
        for t in sorted(cited_sec):
            if not (len(t) == 40 or (re.search("[0-9]", t) and re.search("[a-f]", t))):
                continue
            st = []
            for repo in (LANE, FLEET):
                rc, _, err = git(repo, "cat-file", "-t", f"{t}^{{commit}}")
                st.append("found" if rc == 0 else ("ambiguous" if "ambiguous" in err else "missing"))
            if "found" not in st:
                exp.append(("landed-ambiguous" if "ambiguous" in st else "landed-unresolved", t, "n/a"))
        for x in req:
            if not any(x[0].startswith(t) for t in cited_sec):
                elsewhere = any(x[0].startswith(t) for t in cited_all)
                exp.append(("landed-omitted", x[0], str(elsewhere)))
                ev = [(i, m.group(0)) for i, l in enumerate(lines, 1)
                      for m in ABB.finditer(l) if x[0].startswith(m.group(0))]
                print(f"    omitted {x[0][:12]} ({x[2][:40]!r}) cited_elsewhere={elsewhere} evidence={ev[:3]}")
        total += len(exp)
        for kind, _, _ in exp:
            kinds_count[kind] += 1
        got = sorted((d["kind"], d["token"], str(d["cited_elsewhere"]) if "cited_elsewhere" in d else "n/a")
                     for d in j["defects"])
        check(f"r{r} cutoff == git add %at", j["cutoff"] == cutoff, f"json={j['cutoff']} git={cutoff}")
        check(f"r{r} required", j["required"] == len(req), f"json={j['required']} recount={len(req)}")
        check(f"r{r} round_commits", j["round_commits"] == len(rows),
              f"json={j['round_commits']} recount={len(rows)}")
        check(f"r{r} post_report SHAs in order", j["post_report"] == [x[0] for x in post],
              f"json={len(j['post_report'])} recount={len(post)}")
        check(f"r{r} report path", j["report"] == str((FLEET / rel).resolve()))
        check(f"r{r} report_committed", j["report_committed"] is True)
        check(f"r{r} defects (kind, token, cited_elsewhere)", got == sorted(exp),
              f"json={len(got)} recount={len(exp)}")
        print(f"  r{r}: cutoff={cutoff} add={add_sha[:10]} rows={len(rows)} req={len(req)} "
              f"post={len(post)} defects={len(exp)}")

    s = doc["summary"]
    check("summary.reports", s["reports"] == len(ROUNDS))
    check("summary.defects", s["defects"] == total, f"json={s['defects']} recount={total}")
    check("summary.by_kind", s["by_kind"] == kinds_count, f"json={s['by_kind']} recount={kinds_count}")
    check("summary.required_commits", s["required_commits"] == sum_req,
          f"json={s['required_commits']} recount={sum_req}")
    check("summary.post_report_commits", s["post_report_commits"] == sum_post,
          f"json={s['post_report_commits']} recount={sum_post}")
    check("summary.status/corrected/uncorrected (no errata)",
          s["status"] == "failed" and s["corrected"] == 0 and s["uncorrected"] == total)
    check("errata fields empty under --no-errata",
          s["errata_rows"] == 0 and s["errata_unmatched"] == 0 and s["errata_invalid"] == 0
          and doc["errata_unmatched"] == [] and doc["errata_invalid"] == [])
    check("every defect corrected_by == []",
          all(d["corrected_by"] == [] for r in doc["results"] for d in r["defects"]))
    print(f"MISMATCHES={len(FAILS)}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
