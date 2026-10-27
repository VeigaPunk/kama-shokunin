#!/usr/bin/env python3
"""J12Hide ablation driver: build C2 hiding variants in the seat's own clone.

Usage: ablate.py <clone> <variant a|b|c> <scope all|skill> <base-commit>
Edits SCORECARD.md / SKILL.md in the clone working tree, removes the ledger
(whole file for scope=all; only the SKILL.md rows for scope=skill), leaves the
change uncommitted; the caller commits with a fixture identity.
"""
import importlib.util
import os
import subprocess
import sys

COUNTER = "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round53-cited-path-check.py"
LEDGER = "registry/cited-path-corrections.tsv"


def load_counter():
    spec = importlib.util.spec_from_file_location("c2", COUNTER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    clone, variant, scope, base = sys.argv[1:5]
    top = subprocess.run(["git", "-C", clone, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True).stdout.strip()
    assert os.path.realpath(top) == os.path.realpath(clone), (top, clone)
    m = load_counter()
    lane = m.Repo(clone, base)
    fleet = m.Repo("/home/vgpnk/Projects/shokunin", "ee9f7341bd98de0fcd85f6c01f689301589b27e9")
    _cited, unres = m.survey(lane, fleet)

    targets = {}
    for surf in m.SURFACES:
        if scope == "skill" and surf == "SCORECARD.md":
            continue
        text = m.show(lane.path, lane.rev, surf)
        lines = {}
        for n, tok, core, lo, hi in m.citations(text):
            if tok in unres[surf]:
                lines.setdefault(n, []).append(tok)
        if lines:
            targets[surf] = lines

    for surf, lines in targets.items():
        path = os.path.join(clone, surf)
        src = open(path).read().split("\n")
        if variant == "a":
            for n in sorted(lines, reverse=True):
                src[n - 1:n] = ["```", src[n - 1], "```"]
        else:
            for n in sorted(lines, reverse=True):
                line = src[n - 1]
                for tok in lines[n]:
                    span = "`" + tok + "`"
                    assert span in line, (surf, n, tok, line[:120])
                    rep = '"' + tok + '"' if variant == "b" else "`./x/" + tok + "`"
                    line = line.replace(span, rep)
                src[n - 1] = line
        open(path, "w").write("\n".join(src))
        print(f"{surf}: hid {sorted(lines)} variant={variant}")

    lpath = os.path.join(clone, LEDGER)
    text = open(lpath).read().split("\n")
    kept, dropped = [], 0
    for line in text:
        if line.startswith("#") or not line.strip() or line.split("\t")[0] == "surface":
            kept.append(line)
            continue
        f = line.split("\t")
        if scope == "skill" and f[0] == "SKILL.md" and f[2] != "fixed":
            dropped += 1
            continue
        if scope == "all":
            dropped += 1
            continue
        kept.append(line)
    open(lpath, "w").write("\n".join(kept))
    print(f"ledger rows removed: {dropped}")


if __name__ == "__main__":
    main()
