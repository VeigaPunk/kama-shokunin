#!/usr/bin/env python3
"""Generate kama-live-replay.py attack variants (K2Urlswap, round 48).

Each variant is a full-file replacement of tools/kama-live-replay.py built from
the lane's committed file at the round-48 build commit, with only the
acquisition path changed. The counter (round48-live-replay-v5-audit.py) is
FROZEN; we never modify it. This script only writes into the seat scratch.
"""
import hashlib
import os
import sys

S = os.environ.get("S", "/fast/scratch/hyaku/kama-r48/K2Urlswap")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
BASE = open(os.path.join(LANE, "tools/kama-live-replay.py")).read()

OUT = os.path.join(S, "variants")
os.makedirs(OUT, exist_ok=True)

# --- frozen constants (from the C2 counter docstring) ---
ASSET_URL = "https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz"
ASSET_SHA = "bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b"
MODEL_URL = ("https://huggingface.co/ggml-org/models-moved/resolve/"
             "499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf")
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
MODEL_SIZE = 1185376  # x-linked-size opened 2026-10-26T22:09:23Z (hf-revision-499bc882.txt)

# genuine asset size from whichever local copy exists (host cache or prior install)
asset_candidates = [
    os.path.join(S, "hostcache", "llama-b11909-bin-ubuntu-x64.tar.gz"),
    "/home/vgpnk/.local/opt/llama-b11909-bin-ubuntu-x64.tar.gz",
]
ASSET_SIZE = None
for c in asset_candidates:
    if os.path.isfile(c) and os.path.getsize(c) > 0:
        ASSET_SIZE = os.path.getsize(c)
        break
if ASSET_SIZE is None:
    sys.exit("no genuine asset available yet to size ASSET_SIZE")
if not os.path.isfile(os.path.join(S, "hostcache", "stories260K.gguf")):
    sys.exit("host-cache model missing; wait for the download job")

HEADER = f'''# --- K2Urlswap attack variant (round 48): frozen-pair refusal + host cache ---
ASSET_URL = {ASSET_URL!r}
ASSET_SHA = {ASSET_SHA!r}
MODEL_URL = {MODEL_URL!r}
MODEL_SHA = {MODEL_SHA!r}
MODEL_SIZE = {MODEL_SIZE}
ASSET_SIZE = {ASSET_SIZE}
HOST_CACHE = os.environ.get("KAMA_HOSTCACHE") or {os.path.join(S, 'hostcache')!r}
'''

ANCHOR = "CHUNK = 1 << 20\n"


def with_header(text, extra=""):
    assert ANCHOR in text
    return text.replace(ANCHOR, ANCHOR + HEADER + extra, 1)


# ---------- acquire() bodies ----------
ACQ_V1 = '''def acquire(url, sha, dest):
    # V1: refuse any URL/digest that is not the frozen round-48 pair, and serve
    # the frozen pair from a host cache (no body download at all).
    if url == ASSET_URL and sha == ASSET_SHA:
        src = os.path.join(HOST_CACHE, "llama-b11909-bin-ubuntu-x64.tar.gz")
    elif url == MODEL_URL and sha == MODEL_SHA:
        src = os.path.join(HOST_CACHE, "stories260K.gguf")
    else:
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:not-frozen")
    if not os.path.isfile(src):
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:host-cache-missing")
    shutil.copyfile(src, dest)
    got = sha256_file(dest)
    if got != sha:
        os.unlink(dest)
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:want={sha}:got={got}")
    return got
'''

ACQ_V2 = '''def _num(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _head_headers(url):
    acc = {}

    class _Rec(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            for k, v in headers.items():
                acc[str(k).lower()] = str(v)   # last hop wins (302s may carry Content-Length: 0)
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    opener = urllib.request.build_opener(_Rec)
    req = urllib.request.Request(url, method="HEAD",
                                 headers={"User-Agent": "kama-live-replay/1"})
    with opener.open(req, timeout=120) as r:
        for k, v in r.headers.items():
            acc[str(k).lower()] = str(v)
    return acc


def acquire(url, sha, dest):
    # V2: verify provenance with HEAD requests only (no body transfer); serve the
    # frozen pair from a host cache.
    try:
        hs = _head_headers(url)
    except Exception as exc:  # noqa: BLE001 - any network failure is refused
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:head-failed:{type(exc).__name__}") from exc
    etag = (hs.get("x-linked-etag") or "").strip('\\"')
    size = _num(hs.get("x-linked-size") or hs.get("content-length"))
    if url == MODEL_URL:
        if etag != MODEL_SHA or size != MODEL_SIZE:
            raise Refused(f"digest-mismatch:{os.path.basename(dest)}:head-model etag={etag[:16]!r} size={size}")
        src = os.path.join(HOST_CACHE, "stories260K.gguf")
    elif url == ASSET_URL:
        if size != ASSET_SIZE:
            raise Refused(f"digest-mismatch:{os.path.basename(dest)}:head-asset size={size}")
        src = os.path.join(HOST_CACHE, "llama-b11909-bin-ubuntu-x64.tar.gz")
    else:
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:not-frozen")
    if not os.path.isfile(src):
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:host-cache-missing")
    shutil.copyfile(src, dest)
    got = sha256_file(dest)
    if got != sha:
        os.unlink(dest)
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:want={sha}:got={got}")
    return got
'''

ACQ_V4 = '''def acquire(url, sha, dest):
    # V4: blind host-cache copy, no URL/digest gate (the naive round-47 D1 cheat).
    if url.startswith("https://github.com/"):
        src = os.path.join(HOST_CACHE, "llama-b11909-bin-ubuntu-x64.tar.gz")
    elif url.startswith("https://huggingface.co/"):
        src = os.path.join(HOST_CACHE, "stories260K.gguf")
    else:
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:not-frozen")
    if not os.path.isfile(src):
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:host-cache-missing")
    shutil.copyfile(src, dest)
    got = sha256_file(dest)
    if got != sha:
        os.unlink(dest)
        raise Refused(f"digest-mismatch:{os.path.basename(dest)}:want={sha}:got={got}")
    return got
'''


def replace_acquire(text, body):
    start = text.index("def acquire(url, sha, dest):")
    end = text.index("def extract(", start)
    return text[:start] + body + text[end:]


# ---------- V3: zero-execution tail of replay() ----------
V3_TAIL = '''        # ---- V3 (K2Urlswap): no live execution; synthesize the rerun receipt ----
        rr = json.loads(json.dumps(rec))
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        rr["started_utc"], rr["ended_utc"] = now, now
        rr["port"] = (rec.get("port") or 0) + 1
        rr["child_pid"] = (rec.get("child_pid") or 0) + 7
        rr["server"]["realpath"] = server
        rr["model"]["path"] = model
        with open(rerun, "w") as fh:
            json.dump(rr, fh)
        res["rerun_receipt"] = rerun
        res["mismatches"] = compare(rec, rr)
        res["match"] = not res["mismatches"]
        return res, (0 if res["match"] else 1)
'''

SUB_TARGET = '''        p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=timeout)
        res["live_exit"] = p.returncode
        if not os.path.isfile(rerun):
            raise Refused(f"no-rerun-receipt:exit={p.returncode}:{p.stderr[-300:]}")
        res["rerun_receipt"] = rerun
        with open(rerun) as fh:
            rr = json.load(fh)
        res["mismatches"] = compare(rec, rr)
        if p.returncode != 0:
            res["mismatches"].append(f"live-exit:{p.returncode}")
        # instance differences that do not fail a replay but are worth reading
        res["notes"] = [f"{k}.sha256:{(rec.get(k) or {}).get('sha256')}->{(rr.get(k) or {}).get('sha256')}"
                        for k in ("tool", "probe")
                        if (rec.get(k) or {}).get("sha256") != (rr.get(k) or {}).get("sha256")]
        res["match"] = not res["mismatches"]
        return res, (0 if res["match"] else 1)
'''

V3_IMPORTS = "from datetime import datetime, timezone\n"

specs = {
    "replay-v1": (ACQ_V1, None),
    "replay-v2": (ACQ_V2, None),
    "replay-v3": (ACQ_V1, V3_TAIL),
    "replay-v4": (ACQ_V4, None),
}
# v0 = pristine
with open(os.path.join(OUT, "replay-v0.py"), "w") as fh:
    fh.write(BASE)

for name, (acq, tail) in specs.items():
    text = with_header(BASE, V3_IMPORTS if tail else "")
    text = replace_acquire(text, acq)
    if tail:
        assert SUB_TARGET in text, "subprocess tail anchor missing"
        text = text.replace(SUB_TARGET, tail)
    out = os.path.join(OUT, name + ".py")
    with open(out, "w") as fh:
        fh.write(text)
    print(name, len(text), "bytes, sha256", hashlib.sha256(text.encode()).hexdigest())

print("ASSET_SIZE", ASSET_SIZE)
print("done")
