#!/usr/bin/env python3
"""Build table.md from runs/<name>-<label>.out produced by measure-x2.sh.

One row per measure.sh instrument: base line, build line, exit codes, verdict.
Verdict is derived mechanically from the two lines; the report argues each one.
"""
import os
import re
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(OUT, "runs")
LABELS = ("base", "build")

# name -> (extractor, "better is" direction note)
ORDER = ["c1", "c2", "gate", "cap", "r41", "r42", "r43", "pointer", "digest", "hexrun",
         "sao", "aoa", "aoa-selftest", "klr-selftest", "live-selftest", "cr-selftest",
         "tally", "r48c2", "r49c1", "r49c2", "r50c1", "r50c2", "census"]


def read(name, label):
    p = os.path.join(RUNS, f"{name}-{label}.out")
    if not os.path.exists(p):
        return None
    return open(p, errors="replace").read()


def exit_code(text):
    m = re.findall(r"^exit=(\d+)$", text, re.M)
    return m[-1] if m else "?"


def first(text, pat):
    m = re.search(pat, text, re.M)
    return m.group(0).strip() if m else ""


def passfail(text):
    return f"pass={len(re.findall(r'^pass ', text, re.M))} fail={len(re.findall(r'^FAIL|fail:', text, re.M))}"


def summary(name, text):
    if name == "c1":
        return first(text, r"^bind=\S.*$")
    if name == "c2":
        return first(text, r"^fixture=\S.*$")
    if name == "gate":
        return first(text, r"^registered .*$")
    if name == "cap":
        return first(text, r"^listed .*$")
    if name == "r41":
        return first(text, r"^axes=.*$")
    if name == "r42":
        return first(text, r"^r41=.*$")
    if name == "r43":
        return first(text, r"^unreg=.*$")
    if name == "pointer":
        return "met=" + (first(text, r"^met=\S+$")[4:] or "?")
    if name in ("digest", "hexrun"):
        return first(text, r"^tokens=.*$")
    if name == "sao":
        lines = [l for l in text.splitlines() if re.match(r"^(added S\d+ \(allowed\)|no append-only violations)$", l)]
        return " / ".join(lines)
    if name == "aoa":
        return first(text, r"^summary .*$")
    if name in ("aoa-selftest", "klr-selftest"):
        return passfail(text)
    if name in ("live-selftest", "cr-selftest"):
        return first(text, r"^selftest: .*$")
    if name == "tally":
        blocks = re.findall(r"^(\d\d) ", text, re.M)
        sts = re.findall(r"^\d\d .*\s(\S+)\s*$", text, re.M)
        uniq = list(dict.fromkeys(sts))
        return (f"rounds={blocks[0]}-{blocks[-1]} rows={len(blocks)} "
                f"status={','.join(uniq)}" if blocks else "no rows")
    if name in ("r48c2", "r49c2", "r50c2"):
        return first(text, r"^fixture=\S.*$") if name != "r48c2" else first(text, r"^receipts=\S.*$")
    if name == "r49c1":
        return first(text, r"^witness=\S.*$")
    if name == "r50c1":
        return first(text, r"^bind=\S.*$")
    if name == "census":
        e = re.findall(r"^\S+\t(E\d\d)\t.*$", text, re.M)
        w = re.findall(r"^\S+\t(W\d\d)\t.*$", text, re.M)
        lastE = first(text, r"^\S+\tE\d\d\t.*$")
        return f"E={len(e)} W={len(w)}" + (f" | {lastE}" if lastE else "")
    return text.strip().splitlines()[-1][:160] if text.strip() else ""


def main():
    rows = []
    for name in ORDER:
        cells = []
        for label in LABELS:
            t = read(name, label)
            if t is None:
                cells.append(("-", "?"))
            else:
                cells.append((summary(name, t), exit_code(t)))
        rows.append((name, cells[0], cells[1]))
    w = max(len(r[0]) for r in rows) + 2
    print("| instrument".ljust(w) + "| base 57a2e25 (line / exit) | build 138af25 (line / exit) | verdict |")
    print("|" + "-" * w + "|---|---|---|")
    for name, b, d in rows:
        print("| " + name.ljust(w - 2) + f"| {b[0]} / {b[1]} | {d[0]} / {d[1]} | |")


if __name__ == "__main__":
    main()
