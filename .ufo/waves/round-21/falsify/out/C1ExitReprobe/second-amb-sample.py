#!/usr/bin/env python3
"""Second sample: do several ambiguous 7-hex prefixes all collapse to
'missing' under ^{commit} peel, and does the tool emit landed-unresolved
(never landed-ambiguous) for each? Read-only on lane/fleet."""
import collections, json, pathlib, subprocess, sys, tempfile

W = pathlib.Path(tempfile.mkdtemp(prefix="c1-amb2."))
ROOT = W / "amb"; ROOT.mkdir()
LANE = "/tmp/kama-r21-C1ExitReprobe/lane"
FLEET = "/home/vgpnk/Projects/shokunin"
AUD = f"{LANE}/tools/report-landing-audit.py"
FIF = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-21/falsify/out/C1ExitReprobe/second-amb-sample-output.txt")
out = []
def log(s):
    out.append(s)

subprocess.run(["git", "init", "-q", "-b", "master", str(ROOT)], check=True)
parts = []
for i in range(60000):
    msg = f"c{i}\n".encode()
    parts.append(f"commit refs/heads/master\nmark :{i+1}\ncommitter Amb <a@x> {1700000000+i} +0000\ndata {len(msg)}\n".encode())
    parts.append(msg)
    if i:
        parts.append(f"from :{i}\n".encode())
    parts.append(b"\n")
subprocess.run(["git", "-C", str(ROOT), "fast-import", "--quiet"], input=b"".join(parts), check=True, capture_output=True)
shas = subprocess.run(["git", "-C", str(ROOT), "rev-list", "master"], capture_output=True, text=True, check=True).stdout.split()
by = collections.defaultdict(list)
for s in shas:
    by[s[:7]].append(s)
ambigs = [v[0][:7] for v in by.values() if len(v) > 1][:3]
log(f"ambiguous prefixes sampled: {ambigs}")

for n, amb in enumerate(ambigs):
    draft = W / f"d{n}.md"
    draft.write_text(f"## Landed changes\n- `{amb}` x\n## End\n", encoding="utf-8")
    nop = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch-check"],
                         input=f"{amb}\n", capture_output=True, text=True)
    peel = subprocess.run(["git", "-C", str(ROOT), "cat-file", "--batch-check"],
                          input=f"{amb}^{{commit}}\n", capture_output=True, text=True)
    log(f"prefix={amb} no-peel-> {nop.stdout.strip()!r} (rc={nop.returncode})")
    log(f"prefix={amb} peel   -> {peel.stdout.strip()!r} (rc={peel.returncode})")
    r = subprocess.run([sys.executable, AUD, "--lane-repo", str(ROOT),
                        "--fleet-repo", FLEET, "--rounds", "1",
                        f"--report=1={draft}", "--no-errata", "--json"],
                       capture_output=True, text=True)
    kinds = [d["kind"] for d in json.loads(r.stdout)["results"][0]["defects"]]
    log(f"prefix={amb} tool exit={r.returncode} kinds={kinds} "
        f"landed-ambiguous_emitted={'landed-ambiguous' in kinds}")

import shutil
shutil.rmtree(W)
FIF.write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
