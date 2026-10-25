#!/usr/bin/env python3
"""round41-pinwatch-audit.py - kama round-41 C2 (operability, capability) counter.

Question: at a revision, does the lane hold a working engine version-pin watch
- a tool that reads the lane's pinned serving-engine releases, lists the
upstream release tags, and reports per engine whether a newer release exists?

Frozen tool contract (tools/pin-watch.py):
  pins file: TSV, header line `engine	repo	tag_regex	pin	source`; tag_regex is
    a Python regex with >=1 capturing group of digits; a tag's version key is
    tuple(int(g) for g in fullmatch.groups()).
  tag list: `git ls-remote --tags <repo>` lines `<sha>\t<ref>`; only refs
    `refs/tags/<name>` count, `^{}` peeled refs are ignored, and only names that
    fullmatch tag_regex are release tags.  `--tags-dir DIR` reads the same
    format from DIR/<engine>.txt instead of the network.
  newest = matching tag with the greatest key (ties: greatest name);
  newer  = number of distinct matching tags whose key > key(pin);
  status = missing (pin not a matching tag) | current (newer == 0) |
           behind (newer > 0) | error (tag list unreadable).
  output: one line per pins row, in file order:
    engine=<e> pin=<p> newest=<n or -> newer=<k or -> status=<s>
  then `pins=N current=a behind=b missing=m error=x`.
  exit: 2 if missing+error > 0, else 1 if behind > 0, else 0.
  command: python3 tools/pin-watch.py check --pins FILE [--tags-dir DIR]

Legs (each 0/1):
  tool      tools/pin-watch.py exists at --tip.
  contract  every one of CASES randomized offline fixture cases (seeded; the
            seed is printed) gives byte-equal engine lines, summary line and
            exit code to this file's reference implementation.
  live      `check --pins registry/engine-pins.tsv` (network) equals the
            reference computed from this counter's own `git ls-remote --tags`
            per repo, and the pins file holds >= 3 engines.
  sourced   every pins row's `source` cell names >= 1 S-id that is a
            registry row of corpus/SOURCES.md with status `mined`; and
            corpus/knowledge/engine-pin-watch.md exists and its `source:` line
            names an S-id whose registry row has opened == 2026-10-25.
  capability the highest-numbered "Capabilities — canonical list as of round N"
            table in SCORECARD.md has a row whose first cell is `pin-watch` and
            whose evidence cell contains `tools/pin-watch.py`.
met = all five legs 1.

Output: `tool=T contract=C live=L sourced=S capability=K met=True|False seed=N`
plus `detail:` lines.  Exit 0 met, 1 not met, 2 could not evaluate.
Read-only on --repo (git rev-parse / archive / show).
"""
from __future__ import annotations

import argparse
import os
import random
import re
import subprocess
import sys
import tempfile

CASES = 6
ROUND_DATE = "2026-10-25"


class EvalError(Exception):
    pass


def git(repo, *args, binary=False):
    p = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if p.returncode != 0:
        raise EvalError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout if binary else p.stdout.decode()


# ---------------------------------------------------------------- reference

def parse_pins(text):
    rows = []
    lines = [l for l in text.splitlines() if l.strip() and not l.startswith("#")]
    if not lines or lines[0].split("\t")[:5] != ["engine", "repo", "tag_regex", "pin", "source"]:
        raise ValueError("bad pins header")
    for l in lines[1:]:
        c = l.split("\t")
        if len(c) < 5:
            raise ValueError(f"bad pins row: {l!r}")
        rows.append(dict(engine=c[0], repo=c[1], regex=c[2], pin=c[3], source=c[4]))
    return rows


def tag_names(lsremote_text):
    names = set()
    for l in lsremote_text.splitlines():
        parts = l.split("\t")
        if len(parts) != 2:
            continue
        ref = parts[1].strip()
        if not ref.startswith("refs/tags/") or ref.endswith("^{}"):
            continue
        names.add(ref[len("refs/tags/"):])
    return names


def reference(rows, tag_text_by_engine):
    out, cnt = [], dict(current=0, behind=0, missing=0, error=0)
    for r in rows:
        text = tag_text_by_engine.get(r["engine"])
        if text is None:
            out.append(f"engine={r['engine']} pin={r['pin']} newest=- newer=- status=error")
            cnt["error"] += 1
            continue
        rx = re.compile(r["regex"])
        keyed = {}
        for n in tag_names(text):
            m = rx.fullmatch(n)
            if m:
                keyed[n] = tuple(int(g) for g in m.groups())
        newest = max(keyed, key=lambda n: (keyed[n], n)) if keyed else "-"
        if r["pin"] not in keyed:
            out.append(f"engine={r['engine']} pin={r['pin']} newest={newest} newer=- status=missing")
            cnt["missing"] += 1
            continue
        k = keyed[r["pin"]]
        newer = len({n for n in keyed if keyed[n] > k})
        st = "current" if newer == 0 else "behind"
        cnt[st] += 1
        out.append(f"engine={r['engine']} pin={r['pin']} newest={newest} newer={newer} status={st}")
    out.append(f"pins={len(rows)} current={cnt['current']} behind={cnt['behind']} "
               f"missing={cnt['missing']} error={cnt['error']}")
    code = 2 if cnt["missing"] + cnt["error"] else (1 if cnt["behind"] else 0)
    return out, code


# ---------------------------------------------------------------- fixtures

def fake_sha(rng):
    return "".join(rng.choice("0123456789abcdef") for _ in range(40))


def make_case(rng, idx):
    rows, texts = [], {}
    for e in range(rng.randint(2, 4)):
        name = f"fx{idx}e{e}"
        semver = rng.random() < 0.6
        if semver:
            regex = r"v(\d+)\.(\d+)\.(\d+)"
            vers = set()
            while len(vers) < rng.randint(3, 9):
                vers.add((rng.randint(0, 2), rng.randint(0, 12), rng.randint(0, 25)))
            tags = [f"v{a}.{b}.{c}" for a, b, c in vers]
            decoys = [f"{rng.choice(tags)}rc{rng.randint(1, 3)}", "nightly", f"v{rng.randint(0, 3)}.x"]
        else:
            regex = r"b(\d+)"
            vers = set()
            while len(vers) < rng.randint(3, 9):
                vers.add(rng.choice([rng.randint(900, 999), rng.randint(1000, 12000)]))
            tags = [f"b{v}" for v in vers]
            decoys = ["latest", f"gguf-v{rng.randint(1, 9)}.0", f"b{rng.randint(1, 99)}-hotfix"]
        mode = rng.choice(["current", "behind", "behind", "missing"])
        keyed = sorted(tags, key=lambda t: tuple(int(x) for x in re.findall(r"\d+", t)))
        if mode == "current":
            pin = keyed[-1]
        elif mode == "behind":
            pin = rng.choice(keyed[:-1])
        else:
            pin = "v9.99.99" if semver else "b99999"
        lines = []
        for t in tags + decoys:
            sha = fake_sha(rng)
            lines.append(f"{sha}\trefs/tags/{t}")
            if rng.random() < 0.5:
                lines.append(f"{fake_sha(rng)}\trefs/tags/{t}^{{}}")
        lines.append(f"{fake_sha(rng)}\trefs/heads/main")
        rng.shuffle(lines)
        rows.append(dict(engine=name, repo=f"https://example.invalid/{name}.git",
                         regex=regex, pin=pin, source="S000"))
        texts[name] = "\n".join(lines) + "\n"
    if rng.random() < 0.3:  # an engine whose tag list is unreadable
        rows.append(dict(engine=f"fx{idx}gone", repo="https://example.invalid/gone.git",
                         regex=r"v(\d+)", pin="v1", source="S000"))
    return rows, texts


def pins_text(rows):
    hdr = "engine\trepo\ttag_regex\tpin\tsource"
    return "\n".join([hdr] + ["\t".join([r["engine"], r["repo"], r["regex"], r["pin"], r["source"]])
                              for r in rows]) + "\n"


def run_tool(export, args, timeout=600):
    p = subprocess.run([sys.executable, "tools/pin-watch.py", *args], cwd=export,
                       capture_output=True, text=True, timeout=timeout)
    return [l.rstrip() for l in p.stdout.splitlines() if l.strip()], p.returncode, p.stderr


# ---------------------------------------------------------------- legs

def registry_rows(text):
    rows = {}
    for l in text.splitlines():
        if re.match(r"^ {0,3}\|\s*S\d{3,}\s*\|", l):
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if len(c) == 11:  # id source kind tier scope anchor teaches status opened recheck used-by
                rows[c[0]] = dict(status=c[7], opened=c[8])
    return rows


def evaluate(repo, tip, seed):
    tip = git(repo, "rev-parse", "--verify", f"{tip}^{{commit}}").strip()
    details = []
    legs = dict(tool=0, contract=0, live=0, sourced=0, capability=0)
    export = tempfile.mkdtemp(prefix="r41c2-")
    subprocess.run(["tar", "-x", "-C", export], input=git(repo, "archive", "--format=tar", tip, binary=True),
                   check=True)
    if os.path.isfile(os.path.join(export, "tools/pin-watch.py")):
        legs["tool"] = 1
    else:
        details.append("detail: tools/pin-watch.py absent")

    if legs["tool"]:
        rng = random.Random(seed)
        ok = True
        for i in range(CASES):
            rows, texts = make_case(rng, i)
            d = tempfile.mkdtemp(prefix=f"case{i}-", dir=export)
            with open(os.path.join(d, "pins.tsv"), "w") as f:
                f.write(pins_text(rows))
            os.makedirs(os.path.join(d, "tags"))
            for eng, t in texts.items():
                with open(os.path.join(d, "tags", f"{eng}.txt"), "w") as f:
                    f.write(t)
            want, wcode = reference(rows, texts)
            try:
                got, gcode, err = run_tool(export, ["check", "--pins", os.path.join(d, "pins.tsv"),
                                                    "--tags-dir", os.path.join(d, "tags")], timeout=60)
            except subprocess.TimeoutExpired:
                got, gcode, err = [], None, "timeout"
            if got != want or gcode != wcode:
                ok = False
                details.append(f"detail: contract case {i} mismatch: want exit {wcode} {want} got exit {gcode} {got} {err.strip()[:200]}")
        legs["contract"] = int(ok)

    pins_path = os.path.join(export, "registry/engine-pins.tsv")
    rows = None
    if os.path.isfile(pins_path):
        try:
            rows = parse_pins(open(pins_path).read())
        except ValueError as e:
            details.append(f"detail: registry/engine-pins.tsv unparsable: {e}")
    else:
        details.append("detail: registry/engine-pins.tsv absent")

    if legs["tool"] and rows is not None:
        texts = {}
        for r in rows:
            p = subprocess.run(["git", "ls-remote", "--tags", r["repo"]], capture_output=True, text=True,
                               timeout=120)
            if p.returncode == 0:
                texts[r["engine"]] = p.stdout
        want, wcode = reference(rows, texts)
        try:
            got, gcode, err = run_tool(export, ["check", "--pins", "registry/engine-pins.tsv"])
        except subprocess.TimeoutExpired:
            got, gcode, err = [], None, "timeout"
        if len(rows) >= 3 and got == want and gcode == wcode:
            legs["live"] = 1
        else:
            details.append(f"detail: live mismatch or <3 engines: want exit {wcode} {want} got exit {gcode} {got}")
        details.append("live-reference: " + " | ".join(want) + f" exit={wcode}")

    src = os.path.join(export, "corpus/SOURCES.md")
    reg = registry_rows(open(src).read()) if os.path.isfile(src) else {}
    if rows is not None:
        s_ok = len(rows) > 0
        for r in rows:
            ids = re.findall(r"S\d{3,}", r["source"])
            if not any(reg.get(i, {}).get("status") == "mined" for i in ids):
                s_ok = False
                details.append(f"detail: pins row {r['engine']} cites no mined registry row: {r['source']!r}")
        ke = os.path.join(export, "corpus/knowledge/engine-pin-watch.md")
        if os.path.isfile(ke):
            sl = [l for l in open(ke).read().splitlines() if re.match(r"^[-* ]*source\s*:", l)]
            ids = re.findall(r"S\d{3,}", sl[0]) if sl else []
            if not any(reg.get(i, {}).get("opened") == ROUND_DATE for i in ids):
                s_ok = False
                details.append("detail: engine-pin-watch.md source: line names no row opened " + ROUND_DATE)
        else:
            s_ok = False
            details.append("detail: corpus/knowledge/engine-pin-watch.md absent")
        legs["sourced"] = int(s_ok)

    scp = os.path.join(export, "SCORECARD.md")
    if os.path.isfile(scp):
        lines = open(scp).read().splitlines()
        best, at = -1, None
        for i, l in enumerate(lines):
            m = re.search(r"Capabilities\s+[—-]+\s+canonical list as of round (\d+)", l)
            if m and int(m.group(1)) > best:
                best, at = int(m.group(1)), i
        if at is not None:
            tbl, started = [], False
            for l in lines[at + 1:]:
                if l.startswith("|"):
                    started = True
                    tbl.append([c.strip() for c in l.strip().strip("|").split("|")])
                elif started:
                    break
            for c in tbl[2:]:
                if c and c[0].strip("`") == "pin-watch" and len(c) >= 3 and "tools/pin-watch.py" in c[2]:
                    legs["capability"] = 1
        if not legs["capability"]:
            details.append(f"detail: no pin-watch row in canonical capability list (round {best})")
    met = all(legs.values())
    return tip, legs, met, details


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--tip", default="HEAD")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out")
    a = ap.parse_args()
    seed = a.seed if a.seed is not None else random.SystemRandom().randrange(1, 2**31)
    try:
        tip, legs, met, details = evaluate(a.repo, a.tip, seed)
    except EvalError as e:
        print(f"could-not-evaluate: {e}", file=sys.stderr)
        return 2
    line = " ".join(f"{k}={v}" for k, v in legs.items()) + f" met={met} seed={seed}"
    out = "\n".join([f"tip={tip}", line, *details]) + "\n"
    sys.stdout.write(out)
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        with open(a.out, "w") as f:
            f.write(out)
    return 0 if met else 1


if __name__ == "__main__":
    sys.exit(main())
