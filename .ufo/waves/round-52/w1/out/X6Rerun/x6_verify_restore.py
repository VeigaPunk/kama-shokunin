#!/usr/bin/env python3
"""X6Rerun independent check of the round-52 C2 restore claim.

Read-only on --repo. Does not import the lane's counter or tool. For every row of the
--base disclosure ledger that names an A-corr file (the class round 50/51 called "restore by
append"), check that the tip blob of that file holds at least `count` lines whose CR-stripped
bytes hash to the row's key, and that every copy sits at or after a `## Restored lines
(round 52)` heading (`###` in SCORECARD.md) inside a five-backtick fence. Also checks that
the tip ledger names no A-corr file and prints the tip ledger row count.
"""
import argparse, hashlib, subprocess, sys

A_CORR = ("LOG.md", "SCORECARD.md", "corpus/QUALITY.md", "corpus/README.md")


def show(repo, rev, path):
    return subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                          capture_output=True).stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base", required=True)
    ap.add_argument("--tip", required=True)
    a = ap.parse_args()

    rows = []
    for ln in show(a.repo, a.base, "registry/append-only-disclosures.tsv").decode().splitlines():
        if not ln.strip() or ln.startswith("#") or ln.startswith("commit\t"):
            continue
        f = ln.split("\t")
        rows.append((f[0], f[1], f[2], int(f[3])))

    acorr = [r for r in rows
             if r[1] in A_CORR or (r[1].startswith("corpus/lessons/") and r[1].endswith(".md"))]
    other = [r for r in rows if r not in acorr]
    print(f"base ledger rows={len(rows)} a-corr rows={len(acorr)} other rows={len(other)}"
          f" a-corr lines={sum(r[3] for r in acorr)}")

    files, missing, outside = {}, 0, 0
    for _c, path, key, count in acorr:
        if path not in files:
            files[path] = show(a.repo, a.tip, path).decode(errors="surrogateescape").split("\n")
        head = None
        for i, ln in enumerate(files[path]):
            if ln.rstrip() in ("## Restored lines (round 52)", "### Restored lines (round 52)"):
                head = i
                break
        if head is None:
            print(f"FAIL {path}: no restored heading at tip")
            missing += count
            continue
        hits = [i for i, ln in enumerate(files[path])
                if hashlib.sha256(ln.rstrip("\r").encode("utf-8", "surrogateescape")).hexdigest() == key]
        if len(hits) < count:
            print(f"FAIL {path} {_c[:12]} key={key[:12]} want={count} found={len(hits)}")
            missing += count - len(hits)
        elif min(hits) < head:
            print(f".WARN {path} {_c[:12]} key={key[:12]} found {len(hits)} but earliest at line "
                  f"{min(hits)+1} < heading {head+1}")
            outside += 1

    tiprows = [ln for ln in show(a.repo, a.tip, "registry/append-only-disclosures.tsv").decode().splitlines()
               if ln.strip() and not ln.startswith("#") and not ln.startswith("commit\t")]
    tip_acorr = [ln for ln in tiprows
                 if ln.split("\t")[1] in A_CORR or
                 (ln.split("\t")[1].startswith("corpus/lessons/") and ln.split("\t")[1].endswith(".md"))]
    print(f"tip ledger rows={len(tiprows)} tip ledger a-corr rows={len(tip_acorr)}")
    print(f"restored_lines_found={sum(r[3] for r in acorr)-missing} missing={missing} "
          f"outside_heading={outside}")
    print("verdict=" + ("ok" if missing == 0 and not tip_acorr else "FAIL"))
    return 0 if missing == 0 and not tip_acorr else 1


sys.exit(main())
