#!/usr/bin/env python3
"""C2 back-compat regrade, pass 2: arm matrix and digest root-cause check.

Re-runs the same committed .ufo/waves JSON bytes (mirrored by regrade.py under
scratch rx/, the 66 targets listed in regrade-matrix.tsv) through four gate
revisions and locates where each verdict flips. Gate blobs:
  7a6bc911   e90be78d...  (round start)
  a29bb84    8a6b5dd2...  (round-21 draft: install_links digest = 'name -> text' lines)
  1471344    8d83fe7f...  (integration: install_links digest = canonical JSON)
  a6617149   8d83fe7f...  (attack commit; same gate blob as 1471344)
Read-only on the lane. Writes arms-matrix.tsv, digest-check.tsv and
arms-stderr-diff.txt into the out dir.
"""
import collections
import concurrent.futures as cf
import difflib
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

SCRATCH = "/tmp/kama-r21-C2BackCompatRegrade"
RX = os.path.join(SCRATCH, "rx")
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C2BackCompatRegrade"
GATE = "tests/llamacpp-live/check-receipt.py"
ARMS = (
    ("7a6bc911", os.path.join(SCRATCH, "g7", GATE)),
    ("a29bb84", os.path.join(SCRATCH, "arm-a29bb84", GATE)),
    ("1471344", os.path.join(SCRATCH, "arm-1471344", GATE)),
    ("a6617149", os.path.join(SCRATCH, "lane", GATE)),
)


def run(gate, rel):
    p = subprocess.run([sys.executable, "-B", gate, rel], cwd=RX,
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=300)
    return p.returncode, p.stdout, p.stderr


def first(s):
    ls = s.splitlines()
    return ls[0] if ls else "(no stdout)"


def last(s):
    ls = s.strip().splitlines()
    return ls[-1] if ls else ""


def cell(v):
    return str(v).replace("\t", " ").replace("\n", " ").replace("\r", " ")


def line_digest(links):
    return hashlib.sha256(''.join(f'{n} -> {links[n]}\n' for n in sorted(links))
                          .encode()).hexdigest()


def canon_digest(links):
    return hashlib.sha256(json.dumps(links, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True).encode('ascii')).hexdigest()


def load_gate(name, path):
    spec = importlib.util.spec_from_file_location(f"gate_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_targets():
    with open(os.path.join(OUT, "regrade-matrix.tsv"), encoding="utf-8") as fh:
        next(fh)
        return [tuple(ln.rstrip("\n").split("\t")[:2]) for ln in fh if ln.strip()]


def main():
    targets = load_targets()
    names = [n for n, _ in ARMS]
    results = {}
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(run, gate, path): (name, path)
                for name, gate in ARMS for path, _kind in targets}
        for fut in cf.as_completed(futs):
            results[futs[fut]] = fut.result()

    kinds = {path: kind for path, kind in targets}
    cols = (["path", "kind", "links_keys", "transitions"]
            + [f"exit_{n}" for n in names]
            + [f"line_{n}" for n in names]
            + ["stderr_last_7a6bc911", "stderr_last_a6617149"])
    rows = []
    stderr_diffs = []
    trans_counter = collections.Counter()
    legacy_changed = []
    arm_mismatch_1471344_vs_a6 = []
    for path, kind in targets:
        exits = [results[(n, path)][0] for n in names]
        outs = [results[(n, path)][1] for n in names]
        errs = [results[(n, path)][2] for n in names]
        trans = []
        for i in range(1, len(names)):
            if exits[i] != exits[i - 1]:
                trans.append(f"{names[i]}:{exits[i - 1]}>{exits[i]}")
        trans_s = ";".join(trans) if trans else "-"
        trans_counter[trans_s] += 1
        links_keys = ""
        try:
            with open(os.path.join(RX, path), encoding="utf-8") as fh:
                obj = json.load(fh)
            server = obj.get("server") if isinstance(obj, dict) else None
            if isinstance(server, dict):
                links_keys = ";".join(sorted(k for k in server if k.startswith("install_links")))
        except (OSError, ValueError):
            pass
        rows.append([path, kind, links_keys, trans_s] + exits
                    + [first(o) for o in outs]
                    + [last(errs[0]), last(errs[3])])
        if outs[2] != outs[3] or exits[2] != exits[3] or errs[2] != errs[3]:
            arm_mismatch_1471344_vs_a6.append(path)
        if kind == "receipt" and not links_keys and trans:
            legacy_changed.append((path, trans_s))
        if errs[0] != errs[3]:
            diff = difflib.unified_diff(errs[0].splitlines(), errs[3].splitlines(),
                                        "7a6bc911 stderr", "a6617149 stderr",
                                        lineterm="", n=2)
            stderr_diffs.append(f"== {path}\n" + "\n".join(diff) + "\n")

    with open(os.path.join(OUT, "arms-matrix.tsv"), "w", encoding="utf-8") as fh:
        fh.write("\t".join(cols) + "\n")
        for r in rows:
            fh.write("\t".join(cell(c) for c in r) + "\n")
    with open(os.path.join(OUT, "arms-stderr-diff.txt"), "w", encoding="utf-8") as fh:
        fh.write("".join(stderr_diffs) if stderr_diffs else "no stderr differences\n")

    # Digest root cause: which encoding do the stored install_links_sha256 values match?
    mod29 = load_gate("a29bb84", ARMS[1][1])
    mod_a6 = load_gate("a6617149", ARMS[3][1])
    print("sanity: a29bb84 install_links_sha is line-format:",
          hasattr(mod29, "install_links_sha"))
    print("sanity: a6617149 install_links_sha is canonical-JSON:",
          hasattr(mod_a6, "install_links_sha"))
    digest_rows = []
    for path, kind in targets:
        if kind != "receipt":
            continue
        try:
            with open(os.path.join(RX, path), encoding="utf-8") as fh:
                obj = json.load(fh)
        except (OSError, ValueError):
            continue
        server = obj.get("server") if isinstance(obj, dict) else None
        if not isinstance(server, dict) or "install_links" not in server:
            continue
        links = server.get("install_links")
        stored = server.get("install_links_sha256")
        if not isinstance(links, dict):
            digest_rows.append([path, stored, "n/a", "n/a", "n/a", "n/a", "links not a dict"])
            continue
        try:
            ln = line_digest(links)
            cn = canon_digest(links)
        except UnicodeEncodeError as exc:
            digest_rows.append([path, stored, "ERR", "ERR", "ERR", "ERR",
                                f"{type(exc).__name__}"])
            continue
        g29 = mod29.install_links_sha(links)
        g6 = mod_a6.install_links_sha(links)
        digest_rows.append([path, stored, ln, cn, g29, g6,
                            f"stored==line:{stored == ln} stored==canon:{stored == cn} "
                            f"gate29==line:{g29 == ln} gate6==canon:{g6 == cn}"])
    with open(os.path.join(OUT, "digest-check.tsv"), "w", encoding="utf-8") as fh:
        fh.write("path\tstored\tline_format_sha\tcanonical_sha\tgate_a29bb84_sha\t"
                 "gate_a6617149_sha\tcomparison\n")
        for r in digest_rows:
            fh.write("\t".join(cell(c) for c in r) + "\n")

    print("targets:", len(targets), "arms:", names)
    for i, n in enumerate(names):
        print(f"exit distribution {n}:", dict(collections.Counter(r[4 + i] for r in rows)))
    print("transition patterns:", dict(trans_counter))
    print("legacy receipts (no install_links keys) with any exit change across arms:",
          legacy_changed if legacy_changed else "none")
    print("1471344 vs a6617149 disagreements (exit/stdout/stderr):",
          arm_mismatch_1471344_vs_a6 if arm_mismatch_1471344_vs_a6 else "none")
    print("7a6bc911 vs a6617149 stderr differences:",
          [p for p, _ in targets
           if results[("7a6bc911", p)][2] != results[("a6617149", p)][2]])
    n_line = sum(1 for r in digest_rows if r[2] == r[1])
    n_canon = sum(1 for r in digest_rows if r[3] == r[1])
    print(f"link-bearing receipts: {len(digest_rows)}; stored digest == line-format: {n_line};"
          f" stored digest == canonical-JSON: {n_canon}")
    print("digest comparisons with gate function sanity:",
          sum(1 for r in digest_rows if "gate29==line:True" in r[6] and "gate6==canon:True" in r[6]),
          "of", len(digest_rows), "rows where both gate functions equal the formulas")


if __name__ == "__main__":
    main()
