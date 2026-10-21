#!/usr/bin/env python3
"""RevengerLiveBinding probe for the round-21 live v3 receipt (FALSIFY seat).

Reconstructs how live-receipt.json binds to code and tests each binding claim.
Read-only against the lane: git rev-list/cat-file/show/log, file reads, one TCP
connect attempt to 127.0.0.1:45311 and one pgrep. Gate mutants are written to a
private temp dir that is removed on exit. Exit 0 iff every observation equals the
value recorded in RevengerLiveBinding.md; 1 otherwise; 2 if an input is unreadable.

  binding_probe.py [--lane DIR] [--receipt PATH] [--upstream-dir DIR] [--report PATH]

--upstream-dir holds server-context.cpp, server-http.cpp and server.cpp fetched from
raw.githubusercontent.com at llama.cpp 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad
(path tools/server/<name>). Omit it to skip the upstream byte check.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
from pathlib import Path

MEASURED = "b76727f31e522763ce24e43d6ec86d21b507a11f"
ATTACKED = "a6617149722c73d90e142fbdc8154d6967055f7e"
TOOL = "tools/kama-llamacpp-live.py"
PROBE = "tools/kama-probe.sh"
GATE = "tests/llamacpp-live/check-receipt.py"
RECIPE = ".ufo/waves/round-21/recipe.json"
MANIFEST = ".ufo/waves/round-21/runs/b76727f3/commands.json"
SOURCES = "corpus/SOURCES.md"
REL_RECEIPT = ".ufo/waves/round-21/runs/b76727f3/live-receipt.json"
PORT = 45311
TEARDOWN_LOG = "/tmp/kama-llamacpp-live-0eeenn7_.log"
UPSTREAM = {"tools/server/server-context.cpp": "server-context.cpp",
            "tools/server/server-http.cpp": "server-http.cpp",
            "tools/server/server.cpp": "server.cpp"}
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV["GIT_OPTIONAL_LOCKS"] = "0"
OUT = []
FAILS = []


def say(text):
    OUT.append(text)
    print(text)


def check(name, observed, expected):
    ok = observed == expected
    say(f"{'OK  ' if ok else 'FAIL'} {name}: observed={observed!r} expected={expected!r}")
    if not ok:
        FAILS.append(name)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def ts(text):
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def git(lane, *args):
    p = subprocess.run(["git", "-C", str(lane), *args], capture_output=True, env=ENV)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode(errors='replace').strip()}")
    return p.stdout


def content_window(lane, path, want):
    """Commits reachable from ATTACKED (newest first) whose blob at path hashes to want."""
    revs = git(lane, "rev-list", ATTACKED).decode().split()
    batch = "".join(f"{c}:{path}\n" for c in revs).encode()
    info = subprocess.run(["git", "-C", str(lane), "cat-file", "--batch-check"], input=batch,
                          capture_output=True, env=ENV).stdout.decode().splitlines()
    oid = {}
    for commit, line in zip(revs, info):
        fields = line.split()
        oid[commit] = fields[0] if len(fields) == 3 and fields[1] == "blob" else None
    digest = {o: sha256(git(lane, "cat-file", "blob", o)) for o in set(oid.values()) if o}
    hits = [c for c in revs if oid[c] and digest[oid[c]] == want]
    return revs, hits


def contiguous(revs, hits):
    idx = sorted(revs.index(c) for c in hits)
    return bool(idx) and idx == list(range(idx[0], idx[0] + len(idx)))


def run_gate(gate, receipt, flags):
    p = subprocess.run([sys.executable, str(gate), str(receipt), *flags],
                       capture_output=True, text=True)
    out = p.stdout.splitlines()
    return p.returncode, (out[0].split()[0] if out else ""), p.stderr.strip()


def main():
    ap = argparse.ArgumentParser(description="RevengerLiveBinding probe")
    ap.add_argument("--lane", type=Path, default=Path("/home/vgpnk/Projects/shokunin/kama-shokunin"))
    ap.add_argument("--receipt", type=Path, default=None)
    ap.add_argument("--upstream-dir", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=None)
    a = ap.parse_args()
    lane = a.lane
    receipt_path = a.receipt or lane / REL_RECEIPT
    try:
        rec_bytes = receipt_path.read_bytes()
        rec = json.loads(rec_bytes)
    except (OSError, ValueError) as exc:
        print(f"cannot read receipt: {exc}")
        return 2

    say("## A receipt identity")
    check("working-tree receipt == committed blob at ATTACKED",
          sha256(rec_bytes), sha256(git(lane, "show", f"{ATTACKED}:{REL_RECEIPT}")))
    absent = subprocess.run(["git", "-C", str(lane), "cat-file", "-e", f"{MEASURED}:{REL_RECEIPT}"],
                            capture_output=True, env=ENV).returncode
    check("receipt absent from MEASURED tree (cat-file -e rc != 0)", absent != 0, True)
    check("receipt schema", rec["schema"], "kama-llamacpp-live/v3")
    check("receipt tool.path is the lane tool file", rec["tool"]["path"], str(lane / TOOL))
    check("receipt probe.path is the lane probe file", rec["probe"]["path"], str(lane / PROBE))

    say("## B key paths that could name a revision")
    keys = []

    def walk(node, path):
        if isinstance(node, dict):
            for k, v in node.items():
                p = f"{path}.{k}" if path else k
                keys.append(p)
                walk(v, p)
        elif isinstance(node, list):
            for v in node:
                walk(v, f"{path}[]")

    walk(rec, "")
    revish = sorted({k for k in keys if re.search(r"(?i)commit|revision|\brev\b|git|lane|build", k)})
    check("revision-like key paths", revish,
          ["captures.props.fields.build_info", "checks[].observed.fields.build_info",
           "source_binding[].commit"])
    check("'measured_commit' string appears in receipt", "measured_commit" in json.dumps(rec), False)

    say("## C tool and probe identity")
    tool_blob = git(lane, "show", f"{MEASURED}:{TOOL}")
    probe_blob = git(lane, "show", f"{MEASURED}:{PROBE}")
    check("receipt tool.sha256 == sha256(tool@MEASURED)", rec["tool"]["sha256"], sha256(tool_blob))
    check("receipt probe.sha256 == sha256(probe@MEASURED)", rec["probe"]["sha256"], sha256(probe_blob))
    tool_revs, tool_hits = content_window(lane, TOOL, rec["tool"]["sha256"])
    check("tool sha window: commits (newest first) carrying the receipt's tool content",
          [c[:12] for c in tool_hits],
          ["a6617149722c", "b76727f31e52", "4e75d9e85ba4", "1471344b4c8b"])
    probe_revs, probe_hits = content_window(lane, PROBE, rec["probe"]["sha256"])
    check("probe sha window size (commits carrying the receipt's probe content)", len(probe_hits), 41)
    check("probe sha window oldest commit", probe_hits[-1][:12], "726f737a942f")
    check("both windows contiguous in history", contiguous(tool_revs, tool_hits) and contiguous(probe_revs, probe_hits), True)
    check("MEASURED inside both windows", MEASURED in tool_hits and MEASURED in probe_hits, True)

    say("## D source_binding")
    for sb in rec["source_binding"]:
        check(f"span_sha256 re-derives from span_text: {sb['check']} {sb['lines']}",
              sha256(sb["span_text"].encode()), sb["span_sha256"])
    if a.upstream_dir:
        for sb in rec["source_binding"]:
            data = (a.upstream_dir / UPSTREAM[sb["path"]]).read_bytes()
            lo, hi = sb["lines"]
            span = b"\n".join(data.split(b"\n")[lo - 1:hi]) + b"\n"
            check(f"upstream file sha256 {sb['path']}", sha256(data), sb["file_sha256"])
            check(f"upstream bytes at lines {lo}-{hi} equal span_text", span.decode("utf-8") == sb["span_text"], True)
    else:
        say("  upstream byte check: not executed (no --upstream-dir)")
    registry = git(lane, "show", f"{MEASURED}:{SOURCES}").decode()
    for sb in rec["source_binding"]:
        rows = sorted({m.group(1) for m in re.finditer(r"^\| (S\d{3}) \|.*$", registry, re.M)
                       if sb["file_sha256"][:16] in m.group(0)})
        say(f"  row {sb['check']} {sb['lines']}: receipt.row={sb['row']!r} SOURCES rows quoting this file digest={rows}")

    say("## E gate behaviour: recorded official flags, receipt mutants")
    gate_src = git(lane, "show", f"{MEASURED}:{GATE}")
    recipe = json.loads(git(lane, "show", f"{MEASURED}:{RECIPE}"))
    item = next(i for i in recipe if i["name"] == "c2-live-gate-pinned")
    check("recipe gate argv receipt placeholder", item["argv"][2], "{out}/live-receipt.json")
    flags = item["argv"][3:]
    tool_pin = sha256(tool_blob)
    probe_pin = sha256(probe_blob)
    cases = [
        ("official flags, receipt as written", lambda m: None, flags, 0),
        ("official flags, tool.sha256 = 7*64", lambda m: m["tool"].update(sha256="7" * 64), flags, 0),
        ("official flags, tool block deleted", lambda m: m.pop("tool"), flags, 0),
        ("official flags, tool.path nonexistent",
         lambda m: m["tool"].update(path="/nonexistent/kama-llamacpp-live.py"), flags, 0),
        ("official flags, probe.sha256 = 7*64", lambda m: m["probe"].update(sha256="7" * 64), flags, 0),
        ("official flags, install_links and digest removed",
         lambda m: (m["server"].pop("install_links"), m["server"].pop("install_links_sha256")), flags, 1),
        ("official flags, source_binding[0].row = S042",
         lambda m: m["source_binding"][0].update(row="S042"), flags, 1),
        ("official flags, source_binding[2].file_sha256 = 7*64",
         lambda m: m["source_binding"][2].update(file_sha256="7" * 64), flags, 1),
        ("official flags + tool pin from git, tool.sha256 = 7*64",
         lambda m: m["tool"].update(sha256="7" * 64), flags + ["--expect-tool-sha256", tool_pin], 1),
        ("official flags + tool and probe pins from git, receipt as written",
         lambda m: None, flags + ["--expect-tool-sha256", tool_pin, "--expect-probe-sha256", probe_pin], 0),
    ]
    tmp = Path(tempfile.mkdtemp(prefix="kama-r21-RevengerLiveBinding-"))
    try:
        gate = tmp / "check-receipt.py"
        gate.write_bytes(gate_src)
        for i, (name, mutate, fl, want) in enumerate(cases):
            m = json.loads(rec_bytes)
            mutate(m)
            path = tmp / f"mutant-{i}.json"
            path.write_text(json.dumps(m))
            rc, verdict, err = run_gate(gate, path, fl)
            check(f"gate rc: {name}", rc, want)
            say(f"      verdict={verdict} stderr={err[:80]!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    say("## F run manifest, timeline, server binary")
    man = json.loads(git(lane, "show", f"{ATTACKED}:{MANIFEST}"))
    check("manifest measured_commit", man["measured_commit"], MEASURED)
    check("manifest recipe_sha256 == sha256(recipe@MEASURED)",
          man["recipe_sha256"], sha256(git(lane, "show", f"{MEASURED}:{RECIPE}")))
    c2 = next(c for c in man["commands"] if c["name"] == "c2-live-receipt")
    check("manifest c2-live-receipt exit", c2["exit"], 0)
    check("manifest start within 1 s of receipt started_utc",
          abs((ts(c2["started_utc"]) - ts(rec["started_utc"])).total_seconds()) < 1.0, True)
    t_m = git(lane, "log", "-1", "--format=%aI", MEASURED).decode().strip()
    t_a = git(lane, "log", "-1", "--format=%aI", ATTACKED).decode().strip()
    say(f"  author times: MEASURED={t_m} ATTACKED={t_a}; receipt started={rec['started_utc']} ended={rec['ended_utc']}")
    check("receipt run lies strictly between the two commit times",
          ts(t_m) < ts(rec["started_utc"]) and ts(rec["ended_utc"]) < ts(t_a), True)
    check("sha256(realpath llama-server) == receipt server.sha256",
          sha256(Path(rec["server"]["realpath"]).read_bytes()), rec["server"]["sha256"])

    say("## G processes, port, /tmp logs")
    pg = subprocess.run(["pgrep", "-af", "llama-server"], capture_output=True, text=True)
    check("pgrep -af llama-server rc (1 = no match)", pg.returncode, 1)
    try:
        socket.create_connection(("127.0.0.1", PORT), timeout=1).close()
        listening = True
    except ConnectionRefusedError:
        listening = False
    check(f"127.0.0.1:{PORT} accepts connections", listening, False)
    check("teardown log named in receipt is absent", os.path.exists(TEARDOWN_LOG), False)
    run_start = ts(rec["started_utc"]).timestamp()
    residual = sorted(Path("/tmp").glob("kama-llamacpp-live-*.log"))
    for p in residual:
        st = p.stat()
        text = p.read_bytes().decode("utf-8", "replace")
        local = dt.datetime.fromtimestamp(st.st_mtime).astimezone().isoformat(timespec="seconds")
        say(f"  residual {p.name}: size={st.st_size} mtime={local} "
            f"before_run={st.st_mtime < run_start} names_port_or_log={str(PORT) in text or '0eeenn7' in text}")
    check("every residual /tmp log predates the run and names neither port nor log",
          all(p.stat().st_mtime < run_start and str(PORT) not in p.read_bytes().decode("utf-8", "replace")
              and "0eeenn7" not in p.read_bytes().decode("utf-8", "replace") for p in residual), True)

    say(f"RESULT: {len(FAILS)} expectation(s) failed" + (": " + "; ".join(FAILS) if FAILS else ""))
    if a.report:
        a.report.parent.mkdir(parents=True, exist_ok=True)
        a.report.write_text("\n".join(OUT) + "\n")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
