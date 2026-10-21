#!/usr/bin/env python3
"""C2 back-compat regrade, pass 3: receipt objects nested below the root of
other committed .ufo/waves JSON documents (for example measure-reference.json
carrying a "receipt" object with schema kama-llamacpp-live/v3).

Walks every committed .ufo/waves JSON document mirrored by regrade.py under
scratch rx/, collects each non-root dict whose "schema" starts with
"kama-llamacpp-live/", writes it as a standalone file under scratch rx-nested/,
and runs both gates (7a6bc911 and a6617149) with no extra flags. Writes
nested-matrix.tsv into the out dir.
"""
import concurrent.futures as cf
import json
import os
import shutil
import subprocess
import sys

SCRATCH = "/tmp/kama-r21-C2BackCompatRegrade"
RX = os.path.join(SCRATCH, "rx")
NX = os.path.join(SCRATCH, "rx-nested")
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2BackCompatRegrade"
GATES = (
    ("7a6bc911", os.path.join(SCRATCH, "g7", "tests/llamacpp-live/check-receipt.py")),
    ("a6617149", os.path.join(SCRATCH, "lane", "tests/llamacpp-live/check-receipt.py")),
)
PREFIX = "kama-llamacpp-live/"


def walk(node, pointer, found):
    if isinstance(node, dict):
        if pointer and isinstance(node.get("schema"), str) and node["schema"].startswith(PREFIX):
            found.append((pointer, node))
        for key, value in node.items():
            walk(value, f"{pointer}/{key}", found)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            walk(value, f"{pointer}/{i}", found)


def run(gate, rel):
    p = subprocess.run([sys.executable, "-B", gate, rel], cwd=NX,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    return p.returncode, p.stdout, p.stderr


def first(s):
    ls = s.splitlines()
    return ls[0] if ls else "(no stdout)"


def main():
    shutil.rmtree(NX, ignore_errors=True)
    os.makedirs(NX)
    nested = []
    docs = 0
    for dirpath, _dirs, files in os.walk(RX):
        for name in sorted(files):
            if not name.endswith(".json"):
                continue
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, RX)
            try:
                with open(path, encoding="utf-8") as fh:
                    obj = json.load(fh)
            except (OSError, ValueError):
                continue
            docs += 1
            found = []
            walk(obj, "", found)
            for pointer, node in found:
                safe = rel.replace("/", "__")[:-5] + "__" + pointer.strip("/").replace("/", "_") + ".json"
                with open(os.path.join(NX, safe), "w", encoding="utf-8") as fh:
                    json.dump(node, fh, ensure_ascii=True, sort_keys=True)
                nested.append((rel, pointer, str(node.get("schema")), safe))

    results = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {}
        for label, gate in GATES:
            for rel, pointer, schema, safe in nested:
                futs[ex.submit(run, gate, safe)] = (label, safe)
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()

    cols = ["source_doc", "json_pointer", "schema", "nested_file", "g7_exit", "g7_line", "a6_exit", "a6_line", "changed"]
    lines = ["\t".join(cols)]
    changed = 0
    for rel, pointer, schema, safe in nested:
        rc7, out7, _ = results[("7a6bc911", safe)]
        rca, outa, _ = results[("a6617149", safe)]
        is_change = (rc7 != rca) or (out7 != outa)
        changed += is_change
        lines.append("\t".join(str(c).replace("\t", " ") for c in (
            rel, pointer, schema, safe, rc7, first(out7), rca, first(outa), is_change)))
    with open(os.path.join(OUT, "nested-matrix.tsv"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    print(f"json documents scanned: {docs}; nested kama-llamacpp-live receipt objects: {len(nested)}")
    for rel, pointer, schema, safe in nested:
        rc7, out7, _ = results[("7a6bc911", safe)]
        rca, outa, _ = results[("a6617149", safe)]
        print(f"{rel} {pointer} schema={schema} g7={rc7} [{first(out7)}] a6={rca} [{first(outa)}]")
    print(f"nested receipts with any exit or stdout change between gates: {changed}")


if __name__ == "__main__":
    main()
