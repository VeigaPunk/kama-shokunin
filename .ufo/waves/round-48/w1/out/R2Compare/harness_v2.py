#!/usr/bin/env python3
"""R2Compare harness v2: version-pinned diff of the two projection() definitions.

KLR_TOOL must point at a pinned copy of tools/kama-live-replay.py.
The counter is the frozen tools/round48-live-replay-v5-audit.py.

Sections:
  A1  structure of both projections on a healthy receipt
  A2  absent-capture treatment, per field
  A3  grid over captures.models shapes -> verdict-state classification
      (EQ vs FAIL, FAIL = mismatch or crash) + disagreement pairs
  B   real tool --compare runs on the constructed disagreement pairs
"""
import hashlib, importlib.util, json, os, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
TOOL_PATH = os.environ["KLR_TOOL"]
CNT_PATH = os.environ.get("CNT_TOOL", LANE + "/tools/round48-live-replay-v5-audit.py")
OUT = LANE + "/.ufo/waves/round-48/w1/out/R2Compare"


def load_mod(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


tool = load_mod("klr_tool", TOOL_PATH)
cnt = load_mod("r48_counter", CNT_PATH)
print(f"tool={os.path.basename(TOOL_PATH)} sha256={hashlib.sha256(open(TOOL_PATH,'rb').read()).hexdigest()[:16]} "
      f"lines={sum(1 for _ in open(TOOL_PATH))}")
print(f"counter sha256={hashlib.sha256(open(CNT_PATH,'rb').read()).hexdigest()[:16]} "
      f"lines={sum(1 for _ in open(CNT_PATH))}")

BASE = {"schema": "kama-llamacpp-live/v5", "outcome": "pass",
        "checks": [{"id": "c1", "passed": True, "evaluated": True}],
        "server": {"sha256": "d" * 64}, "model": {"sha256": "c" * 64},
        "provenance": {"server": {"asset_url": "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz",
                                  "asset_sha256": "a" * 64, "member": "llama-b11909/llama-server"},
                       "model": {"url": "https://huggingface.co/ggml-org/models-moved/resolve/" + "b" * 40 + "/tinyllamas/stories260K.gguf",
                                 "commit": "b" * 40, "sha256": "c" * 64},
                       "verified": {"at": "record", "archive_sha256": "a" * 64,
                                    "member_sha256": "d" * 64, "model_sha256": "c" * 64}}}
REAL_DOC = json.dumps({"data": [{"id": "x", "owned_by": "llamacpp", "created": 1}],
                       "models": [{"name": "n"}]})
sha = lambda s: hashlib.sha256(s.encode()).hexdigest()


def V(body, bsha=None):
    return {"body": body} if bsha is None else {"body": body, "body_sha256": bsha}


VARIANTS = {
    "absent-models": None,
    "no-body-key": {},
    "captures-nondict": "NOCAP",
    "null": V("null"), "empty-str": V(""), "zero-str": V("0"), "false": V("false"),
    "empty-arr": V("[]"), "num5": V("5"), "arr12": V("[1,2]"), "str-abc": V('"abc"'),
    "str-unparseable": V('"unparseable"'),
    "bad-json": V("{bad"),
    "bad-json-sha1": V("{bad", sha("{bad")),
    "bad-json-sha2": V("{bad2", sha("{bad2")),
    "real-doc": V(REAL_DOC),
    "real-doc-changed-id": V(json.dumps({"data": [{"id": "y", "owned_by": "llamacpp"}],
                                         "models": [{"name": "n"}]})),
    "doc-data-str": V(json.dumps({"data": "s"})),
    "doc-data-num": V(json.dumps({"data": 5})),
    "doc-nonstring": {"body": {"parsed": "object"}},
}


def receipt(v):
    r = json.loads(json.dumps(BASE))
    if v == "NOCAP":
        r["captures"] = "not-a-dict"
    elif v is None:
        r["captures"] = {}
    elif isinstance(v, dict):
        r["captures"] = {"models": json.loads(json.dumps(v))}
    return r


def proj_state(fn, r):
    """EQ/FAIL state of one definition on one receipt (crash = FAIL)."""
    try:
        fn(r)
        return "ok"
    except Exception as exc:
        return f"CRASH:{type(exc).__name__}"


FIELDS = ("props", "slots", "health", "models", "metrics", "loading", "teardown", "ownership")

print("\n== A1. structure on a healthy receipt (real-doc) ==")
r = receipt(VARIANTS["real-doc"])
pt, pc = tool.projection(r), cnt.projection(r)
for k in FIELDS:
    print(f"  {k:10} tool={type(pt[k]).__name__:5} {json.dumps(pt[k])[:66]:66} "
          f"counter={type(pc[k]).__name__:5} {json.dumps(pc[k])[:50]}")

print("\n== A2. absent-capture treatment, per field (both definitions) ==")
for name in ("absent-models", "no-body-key", "captures-nondict"):
    ra, rb = receipt(VARIANTS[name]), receipt(VARIANTS["real-doc"])
    t = {k: tool.projection(ra)[k] == tool.projection(rb)[k] for k in FIELDS}
    c = {k: cnt.projection(ra)[k] == cnt.projection(rb)[k] for k in FIELDS}
    pt = tool.projection(ra)
    print(f"  {name:18} agree={all(t[k] == c[k] for k in FIELDS)} props={pt['props']} "
          f"slots={pt['slots']} teardown={pt['teardown']} "
          f"models tool={pt['models']!r} counter={cnt.projection(ra)['models']!r}")
r = receipt(VARIANTS["real-doc"])
r["teardown"] = {"returncode": 0, "sigterm_sent": True, "sigkill_sent": False, "port_refuses": True}
r2 = json.loads(json.dumps(r))
del r2["teardown"]
t = {k: tool.projection(r)[k] == tool.projection(r2)[k] for k in FIELDS}
c = {k: cnt.projection(r)[k] == cnt.projection(r2)[k] for k in FIELDS}
print(f"  teardown-absent    agree={all(t[k] == c[k] for k in FIELDS)} "
      f"tool={tool.projection(r2)['teardown']} counter={cnt.projection(r2)['teardown']}")

print("\n== A3. grid: verdict states (EQ vs FAIL; FAIL = mismatch or crash) ==")
keys = list(VARIANTS)
cls = {}
disagree = []
for a in keys:
    for b in keys:
        ra, rb = receipt(VARIANTS[a]), receipt(VARIANTS[b])
        ta, tb = proj_state(tool.projection, ra), proj_state(tool.projection, rb)
        ca, cb = proj_state(cnt.projection, ra), proj_state(cnt.projection, rb)
        t_eq = ta == tb == "ok" and tool.projection(ra) == tool.projection(rb)
        c_eq = ca == cb == "ok" and cnt.projection(ra) == cnt.projection(rb)
        t_state, c_state = ("EQ" if t_eq else "FAIL"), ("EQ" if c_eq else "FAIL")
        cls[(t_state, c_state)] = cls.get((t_state, c_state), 0) + 1
        if t_state != c_state:
            disagree.append((a, b, f"tool={t_state} counter={c_state}"))
print(f"  pairs={len(keys) ** 2}  " + "  ".join(f"tool={a}/counter={b}: {n}" for (a, b), n in sorted(cls.items())))
seen = set()
for a, b, w in disagree:
    sig = frozenset((a, b))
    if sig in seen:
        continue
    seen.add(sig)
    print(f"  DISAGREE {a!r:18} vs {b!r:18} -> {w}")

print("\n== B. real tool --compare on constructed pairs ==")
os.makedirs(OUT, exist_ok=True)
tag = os.path.basename(TOOL_PATH).replace(".py", "").replace("tool-", "")


def pair(name, va, vb):
    pa = os.path.join(OUT, f"pair-{tag}-{name}-A.json")
    pb = os.path.join(OUT, f"pair-{tag}-{name}-B.json")
    json.dump(receipt(va), open(pa, "w"))
    json.dump(receipt(vb), open(pb, "w"))
    p = subprocess.run([sys.executable, TOOL_PATH, "--compare", pa, pb], capture_output=True, text=True)
    first = p.stdout.strip().split("\n")[0] if p.stdout.strip() else p.stderr.strip()[:80]
    print(f"  {name:16} exit={p.returncode}  {first}")
    return p.returncode


cases = [
    ("collision", "str-unparseable", "bad-json"),
    ("collision-sha", "str-unparseable", "bad-json-sha1"),
    ("two-unparseable", "bad-json-sha1", "bad-json-sha2"),
    ("nonstring-vs-bad", "doc-nonstring", "bad-json"),
    ("lenient-null-5", "null", "num5"),
    ("lenient-5-arr", "num5", "arr12"),
    ("ctrl-real", "real-doc", "real-doc"),
    ("ctrl-id", "real-doc", "real-doc-changed-id"),
]
codes = {n: pair(n, VARIANTS[a], VARIANTS[b]) for n, a, b in cases}
print("  exits:", codes)
