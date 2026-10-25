#!/usr/bin/env python3
r"""pin-watch.py - report whether a newer upstream release exists for each
serving-engine version the kama corpus is pinned to.

Pins file (TSV, `registry/engine-pins.tsv`), header then one row per pin:
    engine  repo  tag_regex  pin  source
  engine     unique name matching [A-Za-z0-9][A-Za-z0-9_.-]*; also the
             offline tag-list file name (<engine>.txt)
  repo       git URL listed with `git ls-remote --tags <repo>`; a cell that
             starts with '-' is refused (git would parse it as an option)
  tag_regex  Python regex that a release tag must fullmatch; its capturing
             groups are ASCII digit runs and form the version key (compared
             as integers, so v0.10.0 > v0.9.9 and b11887 > b9999); a
             quantified group such as (\d+)+ is refused; tag names longer
             than 128 characters are skipped
  pin        the release tag the corpus is pinned to
  source     SOURCES.md row id(s) that cite the pinned release

Release style is whatever tag_regex admits. With v(\d+)\.(\d+)\.(\d+),
`.postN`, four-part (v0.9.0.1) and rc tags are not releases, so a final
`v0.5.22.post1` would leave a v0.5.22 pin `current`.

Tag list: `git ls-remote --tags` output (`<oid> TAB <ref>`). Only
`refs/tags/<name>` refs count; the peeled `<ref>^{}` line git prints for an
annotated tag names the tagged object, not another tag, and is skipped.

Per pin:
  newest  the release tag with the greatest version key
  newer   how many release tags have a greater key than the pin
  status  current (newer 0) | behind (newer > 0) |
          missing (the pin is not a release tag upstream) |
          error   (the tag list could not be read)

Output: `engine=<e> pin=<p> newest=<n|-> newer=<k|-> status=<s>` per row in
file order, then `pins=N current=a behind=b missing=m error=x`.
Exit: 2 if any missing/error (could not evaluate a pin), else 1 if any
behind (a newer release exists: recheck the rows in `source`), else 0.
A `behind` result is a recheck trigger, not proof that pinned knowledge is
wrong: the pinned docs still describe the pinned release.

Usage:
    pin-watch.py check --pins registry/engine-pins.tsv [--tags-dir DIR]
    pin-watch.py selftest
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile

HEADER = ["engine", "repo", "tag_regex", "pin", "source"]
# Pins cells are data, never options or paths: an engine name is used as a
# file name under --tags-dir, and a repo cell reaches git's argv.
ENGINE_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*")
# A quantified group such as (\d+)+ backtracks catastrophically on long names.
QUANTIFIED_GROUP_RE = re.compile(r"\)[+*?{]")
ASCII_DIGITS_RE = re.compile(r"[0-9]+")
MAX_TAG_LEN = 128


class PinsError(Exception):
    pass


def load_pins(path: str) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        lines = [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
    if not lines or lines[0].split("\t")[:5] != HEADER:
        raise PinsError(f"{path}: header must be {' '.join(HEADER)} (tab-separated)")
    pins, seen = [], set()
    for n, line in enumerate(lines[1:], start=2):
        cells = line.split("\t")
        if len(cells) < 5:
            raise PinsError(f"{path}:{n}: expected 5 tab-separated cells")
        engine, repo, regex, pin, source = (c.strip() for c in cells[:5])
        if not ENGINE_RE.fullmatch(engine):
            raise PinsError(f"{path}:{n}: engine must match {ENGINE_RE.pattern}: {engine!r}")
        if engine in seen:
            raise PinsError(f"{path}:{n}: duplicate engine {engine}")
        seen.add(engine)
        if repo.startswith("-") or not repo:
            raise PinsError(f"{path}:{n}: repo must be a URL, not an option: {repo!r}")
        try:
            rx = re.compile(regex)
        except re.error as e:
            raise PinsError(f"{path}:{n}: bad tag_regex: {e}")
        if rx.groups < 1:
            raise PinsError(f"{path}:{n}: tag_regex needs a capturing group")
        if QUANTIFIED_GROUP_RE.search(regex):
            raise PinsError(f"{path}:{n}: tag_regex must not quantify a group (backtracking risk)")
        pins.append(dict(engine=engine, repo=repo, rx=rx, pin=pin, source=source))
    return pins


def release_tags(lsremote: str, rx: re.Pattern) -> dict[str, tuple[int, ...]]:
    tags: dict[str, tuple[int, ...]] = {}
    for line in lsremote.splitlines():
        oid, sep, ref = line.partition("\t")
        ref = ref.strip()
        if not sep or not ref.startswith("refs/tags/") or ref.endswith("^{}"):
            continue
        name = ref[len("refs/tags/"):]
        if len(name) > MAX_TAG_LEN:
            continue
        m = rx.fullmatch(name)
        if m and all(g is not None and ASCII_DIGITS_RE.fullmatch(g) for g in m.groups()):
            tags[name] = tuple(int(g) for g in m.groups())
    return tags


def read_tags(pin: dict, tags_dir: str | None) -> str | None:
    if tags_dir is not None:
        path = os.path.join(tags_dir, f"{pin['engine']}.txt")
        try:
            with open(path, encoding="utf-8") as fh:
                return fh.read()
        except OSError:
            return None
    try:
        p = subprocess.run(["git", "ls-remote", "--tags", pin["repo"]],
                           capture_output=True, text=True, timeout=120,
                           stdin=subprocess.DEVNULL,
                           env={**os.environ, "GIT_TERMINAL_PROMPT": "0"})
    except (OSError, subprocess.TimeoutExpired):
        return None
    return p.stdout if p.returncode == 0 else None


def check(pins: list[dict], tags_dir: str | None) -> tuple[list[str], int]:
    out: list[str] = []
    n = dict(current=0, behind=0, missing=0, error=0)
    for pin in pins:
        head = f"engine={pin['engine']} pin={pin['pin']}"
        text = read_tags(pin, tags_dir)
        if text is None:
            n["error"] += 1
            out.append(f"{head} newest=- newer=- status=error")
            continue
        tags = release_tags(text, pin["rx"])
        newest = max(tags, key=lambda t: (tags[t], t)) if tags else "-"
        if pin["pin"] not in tags:
            n["missing"] += 1
            out.append(f"{head} newest={newest} newer=- status=missing")
            continue
        key = tags[pin["pin"]]
        newer = sum(1 for k in tags.values() if k > key)
        status = "current" if newer == 0 else "behind"
        n[status] += 1
        out.append(f"{head} newest={newest} newer={newer} status={status}")
    out.append(f"pins={len(pins)} current={n['current']} behind={n['behind']} "
               f"missing={n['missing']} error={n['error']}")
    code = 2 if n["missing"] or n["error"] else (1 if n["behind"] else 0)
    return out, code


# ------------------------------------------------------------------ selftest

def _case(tmp: str, name: str, rows: list[tuple[str, str, str]], tags: dict[str, str]):
    d = os.path.join(tmp, name)
    os.makedirs(os.path.join(d, "tags"))
    with open(os.path.join(d, "pins.tsv"), "w") as fh:
        fh.write("\t".join(HEADER) + "\n")
        for engine, regex, pin in rows:
            fh.write(f"{engine}\thttps://example.invalid/{engine}.git\t{regex}\t{pin}\tS000\n")
    for engine, text in tags.items():
        with open(os.path.join(d, "tags", f"{engine}.txt"), "w") as fh:
            fh.write(text)
    return check(load_pins(os.path.join(d, "pins.tsv")), os.path.join(d, "tags"))


def selftest() -> int:
    sem = r"v(\d+)\.(\d+)\.(\d+)"
    o = "0" * 40
    cases = [
        # numeric, not lexicographic, ordering; rc and peeled lines ignored
        ("numeric-order", [("e", sem, "v1.2.3")],
         {"e": f"{o}\trefs/tags/v1.2.3\n{o}\trefs/tags/v1.2.3^{{}}\n{o}\trefs/tags/v1.2.10\n"
               f"{o}\trefs/tags/v1.10.0\n{o}\trefs/tags/v1.11.0rc1\n{o}\trefs/heads/v9.9.9\n"},
         ["engine=e pin=v1.2.3 newest=v1.10.0 newer=2 status=behind"], 1),
        ("current", [("e", sem, "v0.5.22")],
         {"e": f"{o}\trefs/tags/v0.5.9\n{o}\trefs/tags/v0.5.22\n{o}\trefs/tags/v0.5.22^{{}}\n"},
         ["engine=e pin=v0.5.22 newest=v0.5.22 newer=0 status=current"], 0),
        ("build-numbers", [("e", r"b(\d+)", "b9999")],
         {"e": f"{o}\trefs/tags/b9999\n{o}\trefs/tags/b11755\n{o}\trefs/tags/b11887\n"
               f"{o}\trefs/tags/b11887-hotfix\n"},
         ["engine=e pin=b9999 newest=b11887 newer=2 status=behind"], 1),
        ("missing-pin", [("e", sem, "v2.0.0")],
         {"e": f"{o}\trefs/tags/v1.0.0\n"},
         ["engine=e pin=v2.0.0 newest=v1.0.0 newer=- status=missing"], 2),
        ("unreadable", [("e", sem, "v1.0.0")], {},
         ["engine=e pin=v1.0.0 newest=- newer=- status=error"], 2),
    ]
    passed = failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, rows, tags, want_lines, want_code in cases:
            got, code = _case(tmp, name, rows, tags)
            ok = got[:-1] == want_lines and code == want_code
            passed += ok
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'} {name}: exit {code} {got}")
        # a malformed pins file is refused, never read as zero pins
        bad = os.path.join(tmp, "bad.tsv")
        with open(bad, "w") as fh:
            fh.write("engine\trepo\n")
        try:
            load_pins(bad)
            ok = False
        except PinsError:
            ok = True
        passed += ok
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'} bad-header refused")
        # hostile cells are refused at load, before git or the filesystem sees them
        hostile = [
            ("option-repo", "e\t--upload-pack=/bin/true\tv(\\d+)\tv1\tS000"),
            ("traversal-engine", "../e\thttps://example.invalid/e.git\tv(\\d+)\tv1\tS000"),
            ("quantified-group", "e\thttps://example.invalid/e.git\tv(\\d+)+\tv1\tS000"),
        ]
        for name, row in hostile:
            path = os.path.join(tmp, f"{name}.tsv")
            with open(path, "w") as fh:
                fh.write("\t".join(HEADER) + "\n" + row + "\n")
            try:
                load_pins(path)
                ok = False
            except PinsError:
                ok = True
            passed += ok
            failed += not ok
            print(f"{'PASS' if ok else 'FAIL'} {name} refused")
    print(f"selftest pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--pins", required=True)
    c.add_argument("--tags-dir")
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "selftest":
        return selftest()
    try:
        pins = load_pins(a.pins)
    except (OSError, PinsError) as e:
        print(f"pin-watch: {e}", file=sys.stderr)
        return 2
    out, code = check(pins, a.tags_dir)
    print("\n".join(out))
    return code


if __name__ == "__main__":
    sys.exit(main())
