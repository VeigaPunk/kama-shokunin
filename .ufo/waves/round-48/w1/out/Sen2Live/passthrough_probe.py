#!/usr/bin/env python3
"""End-to-end pass-through probe: what replay hands the live tool, and the
file:// backstop. Uses a fake live tool (argv dump) and then the real one."""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT = "499bc8821c6b12b4e53c5bffcb21ec206f212d81"
BIN = b"#!/bin/sh\necho bin\n"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build():
    src = os.path.join(HERE, "pass")
    shutil.rmtree(src, ignore_errors=True)
    rev = os.path.join(src, "resolve", COMMIT)
    os.makedirs(rev)
    arc = os.path.join(src, "llama.tgz")
    with tarfile.open(arc, "w:gz") as tf:
        ti = tarfile.TarInfo("rel/llama-server")
        ti.size = len(BIN)
        ti.mode = 0o755
        tf.addfile(ti, io.BytesIO(BIN))
    model = os.path.join(rev, "m.gguf")
    open(model, "wb").write(b"GGUF" * 16)
    return src, arc, model


def receipt(schema, arc, model):
    r = {"schema": schema, "outcome": "pass",
         "server": {"sha256": sha(arc) and hashlib.sha256(BIN).hexdigest()},
         "model": {"sha256": sha(model)},
         "checks": [{"id": "health", "passed": True, "evaluated": True}],
         "captures": {"models": {"body": json.dumps({"data": []})}},
         "provenance": {"server": {"asset_url": "file://" + arc, "asset_sha256": sha(arc),
                                   "member": "rel/llama-server"},
                        "model": {"url": "file://" + model, "sha256": sha(model)}},
         "teardown": {"returncode": 0, "sigterm_sent": True, "sigkill_sent": False,
                      "port_refuses": True},
         "port_listener_ownership": "proven", "loading_envelope_exact": True}
    if schema.endswith("v5"):
        r["provenance"]["model"]["commit"] = COMMIT
        r["provenance"]["verified"] = {"at": "record", "archive_sha256": sha(arc),
                                       "member_sha256": hashlib.sha256(BIN).hexdigest(),
                                       "model_sha256": sha(model)}
    return r


def main():
    src, arc, model = build()
    for tag, schema in (("v5", "kama-llamacpp-live/v5"), ("v4", "kama-llamacpp-live/v4")):
        rp = os.path.join(src, f"r-{tag}.json")
        json.dump(receipt(schema, arc, model), open(rp, "w"))
        work = os.path.join(HERE, "work-" + tag)
        shutil.rmtree(work, ignore_errors=True)
        env = dict(os.environ, FAKE_ORIG=rp, FAKE_ARGV=os.path.join(src, f"argv-{tag}.json"))
        p = subprocess.run([sys.executable, "kama-live-replay.py", "--receipt", rp, "--work", work,
                            "--out", os.path.join(src, f"res-{tag}.json"), "--live", "fake_live.py"],
                           capture_output=True, text=True, env=env)
        print(f"[fake-live {tag}] replay rc={p.returncode} {p.stdout.strip()}")
        argv = json.load(open(env["FAKE_ARGV"]))
        print(f"  --server-archive occurrences={argv.count('--server-archive')} "
              f"value={[argv[i+1] for i, a in enumerate(argv) if a == '--server-archive']}")
        print(f"  --server value={[argv[i+1] for i, a in enumerate(argv) if a == '--server']}")
        print(f"  tail={argv[-2:]}")
        res = json.load(open(os.path.join(src, f"res-{tag}.json")))
        print(f"  inputs={json.dumps(res['inputs'])}")
    # real live tool on the v5 file:// receipt: the https gate is the backstop
    work = os.path.join(HERE, "work-real")
    shutil.rmtree(work, ignore_errors=True)
    p = subprocess.run([sys.executable, "kama-live-replay.py", "--receipt",
                        os.path.join(src, "r-v5.json"), "--work", work,
                        "--out", os.path.join(HERE, "res-real.json")],
                       capture_output=True, text=True)
    res = json.load(open(os.path.join(HERE, "res-real.json")))
    print(f"[real-live file://] replay rc={p.returncode} refused={res['refused'].splitlines()[-1][:110]}")
    print(f"  live_exit={res.get('live_exit')} extracted={os.path.exists(os.path.join(work, 'server', 'rel', 'llama-server'))}")


if __name__ == "__main__":
    main()
