#!/usr/bin/env python3
"""Distinguishing inputs: run M2 and a mutant probe on the same fixture and compare.

Reuses the frozen counter's loopback Stub/jbody helpers (imported, never modified) so the
fixture shape matches round92-linear-paths.py.
"""
from __future__ import annotations

import hashlib
import importlib.util
import re
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
SCRATCH = Path("/fast/scratch/hyaku/kama-r92/MT01ProbeMutants")
M2 = SCRATCH / "M2-probe.sh"
COUNTER = LANE / "tools/round92-linear-paths.py"

spec = importlib.util.spec_from_file_location("r92", COUNTER)
r92 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r92)


def run(probe: Path, args, work: Path, timeout=120):
    work.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMPDIR=str(work))
    try:
        p = subprocess.run(["bash", str(probe)] + list(args), capture_output=True, timeout=timeout,
                           env=env, cwd=work)
        return p.returncode, p.stdout
    except subprocess.TimeoutExpired:
        return None, b"<timeout>"


def check_json(probes, works, routes, expect):
    out = []
    with r92.Stub(routes) as s:
        for probe, work in zip(probes, works):
            out.append(run(probe, ["check", "--port", str(s.port), "--expect", expect, "--json",
                                   "--timeout", "5", "--connect-timeout", "2"], work))
    return out


def check_registry(probes, works, routes, expect, note: bytes):
    out = []
    with r92.Stub(routes) as s:
        for probe, work in zip(probes, works):
            pin = work / "pin.txt"
            pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
            reg = work / "registry.tsv"
            reg.write_bytes(
                b"id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                + b"cell\t" + str(pin).encode() + b"\tgrep:http://[^ ]+\t"
                + f"http://127.0.0.1:{s.port}/v1".encode() + b"\t" + expect.encode() + b"\t"
                + note + b"\n")
            out.append(run(probe, ["check", "--registry", str(reg), "--json",
                                   "--timeout", "5", "--connect-timeout", "2"], work))
    return out


def snapshot(probes, works, routes, expect):
    out = []
    with r92.Stub(routes) as s:
        for probe, work in zip(probes, works):
            pin = work / "pin.txt"
            pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
            reg = work / "registry.tsv"
            reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                           f"cell\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{s.port}/v1\t{expect}\tr92\n")
            hist = work / "history"
            rc, so = run(probe, ["snapshot", "--json", "--registry", str(reg), "--history", str(hist),
                                 "--timeout", "5", "--connect-timeout", "2"], work)
            latest = hist / "latest.tsv"
            tsv = latest.read_bytes() if latest.exists() else b"<no latest.tsv>"
            served = None
            for line in tsv.decode("utf-8", "replace").splitlines():
                f = line.split("\t")
                if f and f[0] == "cell" and len(f) >= 4:
                    served = f[3]
            out.append((rc, so, served, tsv))
    return out


CASES = {}


def case(name):
    def deco(fn):
        CASES[name] = fn
        return fn
    return deco


@case("trail_comma_id")
def trail_comma(probes, works):
    """An id ending in a comma: served value, then served_persist's trailing-comma rule."""
    return snapshot(probes, works, {"/v1/models": r92.jbody(r92.ids_doc(["abc,"]))}, "abc")


@case("ncand_one_good_one_bad")
def ncand_mixed(probes, works):
    """Two autoload candidates: one undecided (no -m) and one with a missing -m path."""
    doc = r92.router_doc([("good", "unloaded", None, None), ("good", "unloaded", None, None)])
    doc["data"][0]["status"]["args"] = ["/bin/sh"]
    doc["data"][1]["status"]["args"] = ["/bin/sh", "-m", "/nonexistent/r92/absent.gguf"]
    return check_json(probes, works, {"/v1/models": r92.jbody(doc),
                                      "/props": b'{"role":"router","models_autoload":true}'}, "good")


@case("registry_note_del")
def note_del(probes, works):
    return check_registry(probes, works, {"/v1/models": r92.jbody(r92.ids_doc(["good"]))}, "good",
                          b"NOTE-a\x7fb\x01c")


@case("registry_note_utf8")
def note_utf8(probes, works):
    return check_registry(probes, works, {"/v1/models": r92.jbody(r92.ids_doc(["good"]))}, "good",
                          "NOTE-\u00fc\u00f6-\u0436".encode())


@case("registry_note_invalid_utf8")
def note_invalid(probes, works):
    return check_registry(probes, works, {"/v1/models": r92.jbody(r92.ids_doc(["good"]))}, "good",
                          b"NOTE-a\xffb")


@case("expect_newline")
def expect_newline(probes, works):
    return check_json(probes, works, {"/v1/models": r92.jbody(r92.ids_doc(["good"]))}, "a\nb")


@case("cli_path_tab_del")
def cli_path_tab_del(probes, works):
    """The history path is jstr()d; an operator path carrying TAB and DEL reaches the escaping path."""
    out = []
    with r92.Stub({"/v1/models": r92.jbody(r92.ids_doc(["good"]))}) as s:
        for probe, work in zip(probes, works):
            pin = work / "pin.txt"
            pin.write_text(f"http://127.0.0.1:{s.port}/v1\n")
            reg = work / "registry.tsv"
            reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                           f"cell\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{s.port}/v1\tgood\tr92\n")
            hist = work / "hist\tx\x7fy"
            out.append(run(probe, ["snapshot", "--json", "--registry", str(reg), "--history", str(hist),
                                   "--timeout", "5", "--connect-timeout", "2"], work))
    return out


@case("served_ids_controls")
def served_controls(probes, works):
    return snapshot(probes, works,
                    {"/v1/models": r92.jbody(r92.ids_doc(["tab\there", "a\x01b", "c\rd", "d\x7fe"]))},
                    "a")


def norm(out: bytes, works=()) -> bytes:
    """Drop run-varying snapshot ids, the work-dir paths echo, and the default registry path echo."""
    out = b"\n".join(l for l in out.split(b"\n") if not l.startswith(b"#@snapshot_id"))
    for w in works:
        out = out.replace(str(w).encode(), b"<WORK>")
    out = re.sub(rb'"registry": "[^"]*"', b'"registry": "<REG>"', out)
    out = re.sub(rb"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", b"<TS>", out)
    return re.sub(rb"\d{8}T\d{6}Z", b"<TS>", out)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: distinguish.py <mutant-name> [<mutant-name> ...]", file=sys.stderr)
        return 2
    root = SCRATCH / "dist"
    root.mkdir(parents=True, exist_ok=True)
    report = {}
    for mn in sys.argv[1:]:
        probe = SCRATCH / "run" / "mutants" / f"{mn}.sh"
        if not probe.exists():
            print(f"missing mutant {probe}", file=sys.stderr)
            return 2
        rows = {}
        for cname, fn in CASES.items():
            w = root / f"{mn}-{cname}"
            if w.exists():
                shutil.rmtree(w)
            (w / "m2").mkdir(parents=True)
            (w / "mut").mkdir(parents=True)
            res = fn([M2, probe], [w / "m2", w / "mut"])
            bout, mout = res[0], res[1]
            (w / "m2.out").write_bytes(bout[1] if len(bout) < 4 else bout[3])
            (w / "mut.out").write_bytes(mout[1] if len(mout) < 4 else mout[3])
            if len(bout) == 4:
                bserved, mserved = bout[2], mout[2]
                same = (bout[0] == mout[0] and norm(bout[1], [w / "m2"]) == norm(mout[1], [w / "mut"])
                        and bserved == mserved
                        and norm(bout[3], [w / "m2"]) == norm(mout[3], [w / "mut"]))
                rows[cname] = dict(same=same, base_rc=bout[0], mut_rc=mout[0],
                                   base_served=bserved, mut_served=mserved)
            else:
                same = (bout[0] == mout[0]
                        and norm(bout[1], [w / "m2"]) == norm(mout[1], [w / "mut"]))
                rows[cname] = dict(same=same, base_rc=bout[0], mut_rc=mout[0],
                                   base_out_sha=hashlib.sha256(bout[1]).hexdigest()[:16],
                                   mut_out_sha=hashlib.sha256(mout[1]).hexdigest()[:16],
                                   base_out=norm(bout[1], [w / "m2"]).decode("utf-8", "replace")[:400],
                                   mut_out=norm(mout[1], [w / "mut"]).decode("utf-8", "replace")[:400])
            print(f"CASE {mn:<24} {cname:<26} same={int(rows[cname]['same'])} "
                  f"rc={rows[cname]['base_rc']}/{rows[cname]['mut_rc']}"
                  + (f" served={rows[cname].get('base_served')!r}/{rows[cname].get('mut_served')!r}"
                     if len(bout) == 4 else ""), flush=True)
        report[mn] = rows
    (root / "distinguish.json").write_text(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
