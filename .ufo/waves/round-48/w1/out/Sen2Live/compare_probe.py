#!/usr/bin/env python3
"""Crafted-input harness for `kama-live-replay.py --compare A B`."""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPLAY = os.path.join(HERE, "kama-live-replay.py")
OUT = os.path.join(HERE, "cmp")
os.makedirs(OUT, exist_ok=True)


def base(schema="kama-llamacpp-live/v5"):
    return {
        "schema": schema, "outcome": "pass",
        "server": {"sha256": "a" * 64}, "model": {"sha256": "b" * 64},
        "checks": [{"id": "health", "passed": True, "evaluated": True}],
        "captures": {"props": {"fields": {"n": 1}}, "slots": {"element_count": 0, "body_sha256": "c" * 64},
                     "health": {"status": 200, "body_sha256": "d" * 64},
                     "models": {"body": json.dumps({"data": [{"id": "m", "owned_by": "x"}]})},
                     "metrics": {"status": 200}},
        "loading_envelope_exact": True, "loading_503": {"body_sha256": "e" * 64},
        "teardown": {"returncode": 0, "sigterm_sent": True, "sigkill_sent": False, "port_refuses": True},
        "port_listener_ownership": "proven",
    }


def write(name, obj=None, raw=None):
    p = os.path.join(OUT, name)
    with open(p, "w") as fh:
        fh.write(raw if raw is not None else json.dumps(obj))
    return p


def run(label, a, b, timeout=120):
    t0 = time.monotonic()
    try:
        p = subprocess.run([sys.executable, REPLAY, "--compare", a, b],
                           capture_output=True, text=True, timeout=timeout)
        out = {"rc": p.returncode, "stdout": p.stdout.strip()[:400],
               "stderr_tail": p.stderr.strip().splitlines()[-1][:300] if p.stderr.strip() else ""}
    except subprocess.TimeoutExpired:
        out = {"rc": "TIMEOUT"}
    out.update(label=label, seconds=round(time.monotonic() - t0, 2))
    print(json.dumps(out), flush=True)


if __name__ == "__main__":
    case = sys.argv[1]
    good = write("good.json", base())
    if case == "deep":
        deep = "[" * 200000 + "]" * 200000
        p = write("deep.json", raw=deep)
        run("deep-nesting-200k", p, good)
    elif case == "shape":
        b = base()
        b["captures"]["models"]["body"] = {"data": []}          # body not a string
        run("models-body-is-object", write("s1.json", b), good)
        b = base()
        b["captures"]["models"]["body"] = json.dumps({"data": 5})
        run("models-data-is-int", write("s2.json", b), good)
        b = base()
        b["captures"]["models"]["body"] = json.dumps({"data": {"id": "m"}})
        run("models-data-is-object", write("s3.json", b), good)
        b = base()
        b["captures"]["models"]["body"] = json.dumps({"data": [5]})
        run("models-element-is-int", write("s4.json", b), good)
        b = base()
        b["checks"] = {"health": True}
        run("checks-is-object", write("s5.json", b), good)
        b = base()
        b["captures"] = "nope"
        run("captures-is-string", write("s6.json", b), good)
    elif case == "bytes":
        raw = b'{"schema": "kama-llamacpp-live/v5", "x": "\xff\xfe"}'
        p = os.path.join(OUT, "bad-utf8.json")
        open(p, "wb").write(raw)
        run("invalid-utf8", p, good)
        p = os.path.join(OUT, "empty.json")
        open(p, "w").close()
        run("empty-file", p, good)
        run("missing-file", os.path.join(OUT, "nope.json"), good)
    elif case == "big":
        b = base()
        b["pad"] = "x" * (400 << 20)
        p = write("big.json", b)
        print(json.dumps({"size_mb": os.path.getsize(p) // (1 << 20)}))
        run("400MB-receipt", p, good, timeout=300)
    elif case == "vacuous":
        # two receipts whose models body carries a dict-valued "data": different content,
        # same projection -> the models surface silently disappears
        def modelish(data):
            r = base()
            r["captures"]["models"]["body"] = json.dumps({"data": data})
            return r
        run("dict-data-A-vs-B", write("v1.json", modelish({"real-model-1": {"owned_by": "team-a"}})),
            write("v2.json", modelish({"totally": {"different": "content"}})))
        run("dict-data-A-vs-A", write("v3.json", modelish({"real-model-1": {"owned_by": "team-a"}})),
            write("v4.json", modelish({"real-model-1": {"owned_by": "team-a"}})))
    elif case == "twins":
        run("v5-vs-identical", good, write("good2.json", base()))
        run("v5-vs-v4-schema", good, write("v4.json", base("kama-llamacpp-live/v4")))
