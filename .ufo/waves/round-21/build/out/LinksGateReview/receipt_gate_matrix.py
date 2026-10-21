#!/usr/bin/env python3
"""Run the three committed round-18 receipts through the C2 gate at base
(7a6bc911f9eb7dbea9e3b81f5f2449ecda10096d) and head (a29bb84abbb8b4d328f5970a89e448330a3a42ac).

Requires read-only git-archive snapshots (created by the reviewer):
  git -C LANE archive <rev> | tar -x -C /tmp/kama-r21-LinksGateReview/{base,head}
Writes only gate-receipts-transcript.txt into the out directory.
"""
import json
import os
import subprocess
import sys

S = "/tmp/kama-r21-LinksGateReview"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
OUT = f"{LANE}/.ufo/waves/round-21/build/out/LinksGateReview"
REC = [f"{LANE}/.ufo/waves/round-18/live-recovery/receipt-{i}.json" for i in (1, 2, 3)]


def gate_path(rev):
    return f"{S}/{rev}/tests/llamacpp-live/check-receipt.py"


def run_gate(rev, args):
    p = subprocess.run([sys.executable, gate_path(rev), *args],
                       capture_output=True, text=True, timeout=120)
    return p.returncode, p.stdout, p.stderr


def main():
    os.makedirs(OUT, exist_ok=True)
    rows, transcript = [], []
    for rp in REC:
        d = json.load(open(rp, encoding="utf-8"))
        srv = d.get("server", {})
        pins = {
            "tree": srv.get("install_tree_sha256"),
            "server": srv.get("sha256"),
            "impl": srv.get("server_impl_sha256"),
            "model": (d.get("model") or {}).get("sha256"),
            "probe": (d.get("probe") or {}).get("sha256"),
            "tool": (d.get("tool") or {}).get("sha256"),
        }
        argsets = [
            ("bare", []),
            ("require-schema-v3", ["--require-schema", "v3"]),
            ("own-tree-pin", ["--expect-install-tree-sha256", str(pins["tree"])]),
            ("own-server-pin", ["--expect-server-sha256", str(pins["server"])]),
            ("own-impl-pin", ["--expect-server-impl-sha256", str(pins["impl"])]),
            ("own-model-pin", ["--expect-model-sha256", str(pins["model"])]),
            ("own-probe-pin", ["--expect-probe-sha256", str(pins["probe"])]),
            ("own-tool-pin", ["--expect-tool-sha256", str(pins["tool"])]),
            ("links-pin-zeros", ["--expect-install-links-sha256", "0" * 64]),
            ("links-pin-malformed", ["--expect-install-links-sha256", "zz"]),
        ]
        for label, args in argsets:
            b = run_gate("base", [rp, *args])
            h = run_gate("head", [rp, *args])
            same = b == h
            rows.append((os.path.basename(rp), label, b[0], h[0],
                         "SAME" if same else "DIFF"))
            transcript.append(
                f"## {os.path.basename(rp)} :: {label}\n"
                f"# base exit={b[0]}\n{b[1]}{b[2]}# head exit={h[0]}\n{h[1]}{h[2]}\n")
    with open(f"{OUT}/gate-receipts-transcript.txt", "w", encoding="utf-8") as fh:
        fh.write("\n".join(transcript))
    print("receipt  argset  base_exit  head_exit  verdict-change")
    for r in rows:
        print(f"{r[0]}  {r[1]}  {r[2]}  {r[3]}  {r[4]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
