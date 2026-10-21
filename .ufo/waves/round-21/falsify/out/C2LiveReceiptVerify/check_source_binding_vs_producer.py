#!/usr/bin/env python3
"""Compare a receipt's source_binding with the COMMITTED producer's source_bindings().

Only these committed producer nodes are compiled and executed, selected by ast from
`git show <commit>:tools/kama-llamacpp-live.py`: the constants LLAMA_COMMIT, _LLAMA_RAW,
SERVER_CONTEXT_SHA, SERVER_HTTP_SHA, SERVER_SHA_CPP and the functions _binding and
source_bindings. These are literal data plus hashlib. No other producer statement runs;
there is no subprocess, network access, or llama-server launch.
"""
import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys

WANT_ASSIGN = {"LLAMA_COMMIT", "_LLAMA_RAW", "SERVER_CONTEXT_SHA", "SERVER_HTTP_SHA",
               "SERVER_SHA_CPP"}
WANT_DEF = {"_binding", "source_bindings"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", required=True)
    ap.add_argument("--commit", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    src = subprocess.run(
        ["git", "-C", args.lane, "show", f"{args.commit}:tools/kama-llamacpp-live.py"],
        capture_output=True, check=True).stdout.decode("utf-8")
    tree = ast.parse(src)
    keep, extracted = [], []
    for node in tree.body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            names = {t.id for t in node.targets}
            if names & WANT_ASSIGN:
                keep.append(node)
                extracted += sorted(names & WANT_ASSIGN)
        elif isinstance(node, ast.FunctionDef) and node.name in WANT_DEF:
            keep.append(node)
            extracted.append(node.name)
    missing = sorted((WANT_ASSIGN | WANT_DEF) - set(extracted))
    if missing:
        raise SystemExit(f"committed producer lacks {missing}")

    module = ast.Module(body=keep, type_ignores=[])
    ast.fix_missing_locations(module)
    ns = {"hashlib": hashlib}
    exec(compile(module, "<committed-producer-extract>", "exec"), ns)
    emitted = ns["source_bindings"]()

    with open(args.receipt, "r", encoding="utf-8") as fh:
        received = json.load(fh)["source_binding"]

    equal = emitted == received
    result = {"commit": args.commit, "extracted": extracted,
              "producer_entries": len(emitted), "receipt_entries": len(received),
              "equal": equal, "rows": [e["row"] for e in emitted]}
    if not equal:
        result["entry_diffs"] = [
            {"index": i, "keys_differ": sorted(k for k in set(e) | set(r)
                                                if e.get(k) != r.get(k))}
            for i, (e, r) in enumerate(zip(emitted, received))]
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "source-binding-vs-producer.json"), "w",
              encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=True)
        fh.write("\n")
    print(("EQUAL" if equal else "DIFFER") +
          f" receipt.source_binding vs producer.source_bindings() @ {args.commit}"
          f" entries={len(received)} rows={result['rows']}")
    return 0 if equal else 1


if __name__ == "__main__":
    sys.exit(main())
