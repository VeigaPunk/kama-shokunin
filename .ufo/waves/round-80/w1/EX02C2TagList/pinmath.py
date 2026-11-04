#!/usr/bin/env python3
"""EX02 pinmath.py — re-derive pin-freshness arithmetic from the committed tag lists.

Reads engine pins from ``registry/engine-pins.tsv`` and raw ``git ls-remote
--tags`` output from ``.ufo/waves/round-80/measured/after/c2-tags/<engine>.txt``
(the committed tag lists — the same offline leg ``tools/pin-watch.py
--tags-dir`` uses; release-tag parsing is reused from pin-watch itself so the
rules cannot drift). For each requested ref it computes:

  newest      the engine's newest release tag (max by (numeric key, name),
              the pin-watch ``check`` rule)
  newer       count of release tags with a strictly greater version key; for a
              commit anchor, greater than the key of the release tag whose
              peeled oid equals the anchor
  peeled      a tag ref: the tag's peeled commit oid (the ``^{}`` line's oid
              when the tag is annotated, else the tag ref's own oid — a
              lightweight tag peels to itself); a commit anchor: the anchor
              oid itself (a commit peels to itself)
  is_tag_tip  a tag ref: yes iff the ref IS the engine's newest release tag;
              a commit anchor: yes iff it equals some release tag's peeled oid

Writes EX02.tsv (engine, ref, kind, newest, newer, peeled, is_tag_tip) next to
this script and prints one summary line per ref. Exit 0 unless a ref cannot be
derived (then the line carries the failure and exit is 1).

Usage:
    pinmath.py --repo <lane-root>
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys

# engine, ref, kind — the five refs this seat was assigned, in item order.
REFS = [
    ("llama.cpp", "b11755", "tag"),
    ("llama.cpp", "39febd2adb947b70da35e95f9351b3bf58ad170a", "commit"),
    ("llama.cpp", "b7200", "tag"),
    ("sglang", "v0.5.22", "tag"),
    ("vllm", "v0.32.0", "tag"),
]
HEADER = ["engine", "ref", "kind", "newest", "newer", "peeled", "is_tag_tip"]


def load_pin_watch(lane: str):
    path = os.path.join(lane, "tools", "pin-watch.py")
    spec = importlib.util.spec_from_file_location("pin_watch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def peeled_map(raw: str) -> tuple[dict[str, str], dict[str, str]]:
    """Return ({tag: peeled commit oid}, {tag: ref oid}) from ls-remote output."""
    peeled: dict[str, str] = {}
    refoid: dict[str, str] = {}
    for line in raw.splitlines():
        oid, sep, ref = line.partition("\t")
        ref = ref.strip()
        if not sep or not ref.startswith("refs/tags/"):
            continue
        name = ref[len("refs/tags/"):]
        if name.endswith("^{}"):
            peeled[name[:-3]] = oid
        else:
            refoid[name] = oid
    return peeled, refoid


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True, help="lane root")
    args = ap.parse_args()
    lane = os.path.abspath(args.repo)

    pw = load_pin_watch(lane)
    pins = {p["engine"]: p for p in pw.load_pins(os.path.join(lane, "registry", "engine-pins.tsv"))}

    raws: dict[str, str] = {}
    for engine in pins:
        path = os.path.join(lane, ".ufo", "waves", "round-80", "measured", "after", "c2-tags", f"{engine}.txt")
        with open(path, encoding="utf-8") as fh:
            raws[engine] = fh.read()

    state: dict[str, dict] = {}
    for engine, pin in pins.items():
        tags = pw.release_tags(raws[engine], pin["rx"])
        peeled, refoid = peeled_map(raws[engine])
        # A release tag's peeled commit oid: the ^{} oid when present, else the
        # tag ref's own oid (lightweight tag peels to itself).
        for name in tags:
            peeled.setdefault(name, refoid.get(name, ""))
        newest = max(tags, key=lambda t: (tags[t], t)) if tags else "-"
        state[engine] = dict(tags=tags, peeled=peeled, newest=newest)

    rows: list[dict] = []
    failed = False
    for engine, ref, kind in REFS:
        st = state[engine]
        row = dict(engine=engine, ref=ref, kind=kind, newest=st["newest"], newer="-",
                   peeled="-", is_tag_tip="no", note="")
        if kind == "tag":
            if ref not in st["tags"]:
                row["note"] = "tag not a release tag upstream"
                failed = True
            else:
                key = st["tags"][ref]
                row["newer"] = sum(1 for k in st["tags"].values() if k > key)
                row["peeled"] = st["peeled"].get(ref, "")
                row["is_tag_tip"] = "yes" if ref == st["newest"] else "no"
        else:
            hits = sorted((n for n, oid in st["peeled"].items()
                           if oid == ref and n in st["tags"]),
                          key=lambda n: st["tags"][n])
            if not hits:
                row["note"] = "anchor matches no release tag's peeled oid"
            else:
                # One tag normally peels here; with aliases, judge from the greatest key.
                loc = hits[-1]
                key = st["tags"][loc]
                row["newer"] = sum(1 for k in st["tags"].values() if k > key)
                row["peeled"] = ref  # a commit peels to itself
                row["is_tag_tip"] = "yes"
                if len(hits) > 1:
                    row["note"] = "anchor peels to tags: " + ",".join(hits)
        rows.append(row)
        print(f"{engine}\t{ref}\t{kind}\tnewest={row['newest']}\tnewer={row['newer']}\t"
              f"peeled={row['peeled']}\tis_tag_tip={row['is_tag_tip']}"
              + (f"\t{row['note']}" if row["note"] else ""))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "EX02.tsv")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\t".join(HEADER) + "\n")
        for row in rows:
            fh.write("\t".join(str(row[c]) for c in HEADER) + "\n")
    print(f"wrote {out}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
