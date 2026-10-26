#!/usr/bin/env python3
"""Verify the proposed patches in $S/patch/apply (patched copies of both tools).

Each line is one defect from the report, re-run against the patched tool; the
'before' value is in the report's evidence section.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import urllib.request

S = os.environ["S"]
P = os.path.join(S, "patch", "apply", "tools")
REPLAY = os.path.join(P, "kama-live-replay.py")
FAKE = os.path.join(S, "demo", "fake_live.py")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TIP = "3a09a1d93dcc16799cf6c4b48786e6440af134c4"


def spec(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def run(rp, work, extra=()):
    out = os.path.join(S, "fixtest", os.path.basename(work) + ".json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.run([sys.executable, REPLAY, "--receipt", rp, "--work", work,
                        "--out", out, "--live", FAKE, *extra],
                       capture_output=True, text=True)
    j = json.load(open(out)) if os.path.exists(out) else {}
    return p.returncode, j.get("refused")


def main():
    klr = spec("klr2", REPLAY)
    print("F1 file:// without --allow-file-urls ->",
          run(os.path.join(S, "e2", "c1", "r.json"), os.path.join(S, "fixtest", "w1")))
    print("F1 file:// with --allow-file-urls    ->",
          run(os.path.join(S, "e2", "c1", "r.json"), os.path.join(S, "fixtest", "w1b"),
              ("--allow-file-urls",)))
    marker = os.path.join(S, "e2", "c3", "EXECUTED")
    if os.path.exists(marker):
        os.unlink(marker)
    print("F2 receipt records server.sha256=000..., member differs ->",
          run(os.path.join(S, "e2", "c3", "r.json"), os.path.join(S, "fixtest", "w2"),
              ("--allow-file-urls",)), "marker_written=", os.path.exists(marker))
    print("F3 second run, archive without the member ->",
          run(os.path.join(S, "e2", "c5", "r2.json"), os.path.join(S, "fixtest", "w3"),
              ("--allow-file-urls",)))
    d = os.path.join(S, "fixtest", "cap")
    os.makedirs(d, exist_ok=True)
    big = os.path.join(d, "big.bin")
    open(big, "wb").write(b"z" * 4096)
    try:
        klr.fetch("file://" + big, os.path.join(d, "dest.bin"), allow_file=True, max_bytes=1024)
        print("F4 cap -> not enforced")
    except klr.Refused as exc:
        print("F4 cap ->", exc, "part_left=", os.path.exists(os.path.join(d, "dest.bin.part")))

    class Boom:
        def __init__(self):
            self.n = 0

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=-1):
            self.n += 1
            if self.n == 1:
                return b"x" * 100
            raise OSError("reset")

        def geturl(self):
            return "https://example.invalid/x"

    saved = urllib.request.urlopen
    urllib.request.urlopen = lambda *a, **k: Boom()
    try:
        klr.fetch("https://example.invalid/x", os.path.join(d, "dest2.bin"))
        err = None
    except OSError as exc:
        err = exc
    finally:
        urllib.request.urlopen = saved
    print("F5 aborted download ->", type(err).__name__,
          "part_left=", os.path.exists(os.path.join(d, "dest2.bin.part")))

    rec = json.load(open(os.path.join(LANE, ".ufo/waves/round-47/c2/live/receipt-1.json")))
    v = rec["provenance"]["model"]["sha256"]
    rec["provenance"]["model"]["sha256"] = ("0" if v[0] != "0" else "1") + v[1:]
    tp = os.path.join(S, "fixtest", "tamper.json")
    os.makedirs(os.path.dirname(tp), exist_ok=True)
    json.dump(rec, open(tp, "w"))
    work = os.path.join(S, "fixtest", "w6")
    out = os.path.join(work, "j.json")
    p = subprocess.run([sys.executable, REPLAY, "--receipt", tp, "--work", work, "--out", out],
                       capture_output=True, text=True)
    print("F6 --out inside not-yet-created --work -> exit", p.returncode,
          "out_written", os.path.exists(out), "traceback", "Traceback" in p.stderr)

    old = spec("old", os.path.join(LANE, "tools", "round47-live-replay-audit.py"))
    new = spec("new", os.path.join(P, "round47-live-replay-audit.py"))
    r1 = json.load(open(os.path.join(LANE, ".ufo/waves/round-47/c2/live/receipt-1.json")))
    alt = copy.deepcopy(r1)
    alt["provenance"]["model"]["url"] = "https://example.invalid/other.gguf"
    for name, mod in (("frozen", old), ("patched", new)):
        for label, r in (("receipt-1", r1), ("other-https-model", alt)):
            detail = []
            ok = mod.check_receipt(LANE, TIP, "x", r, detail)
            print(f"F7 {name:8s} {label:17s} passes={ok} detail={detail}")


if __name__ == "__main__":
    main()
