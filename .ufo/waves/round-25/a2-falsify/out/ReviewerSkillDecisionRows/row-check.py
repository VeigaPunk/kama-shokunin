#!/usr/bin/env python3
"""Read-only reproduction of the round-25 SKILL decision-row checks.

Seat: KamaR25a2.ReviewerSkillDecisionRows (wave 2, falsify).
Inputs: committed bytes at fa3b62ae (SKILL.md, corpus entry, receipt), raw bodies and
logs under final/raw, the fixture GGUF header read offline, and the round-20
nctx-crosscheck predict() function. No server is started. The script writes nothing.
Run: python3 -B row-check.py
"""
import hashlib
import importlib.util
import json
import pathlib
import re
import struct
import subprocess

LANE = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
PIN = "fa3b62ae6475d111eb466d79af616aeebb08bbb9"
MASTER = "46be41cf674301953837c8863cd2026e8a21fcb0"
SKILL = "SKILL.md"
ENTRY = "corpus/knowledge/context-capacity.md"
RECEIPT = ".ufo/waves/round-25/final/context-capacity-receipt.json"
RAW = LANE / ".ufo/waves/round-25/final/raw"
MODEL = pathlib.Path("/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf")
NCTX = LANE / ".ufo/waves/round-20/build/out/SrcServerNctx/nctx-crosscheck.py"


def git(*args):
    r = subprocess.run(["git", "-C", str(LANE), *args], capture_output=True)
    if r.returncode != 0:
        raise SystemExit("git " + " ".join(args) + " failed: " + r.stderr.decode("utf-8", "replace"))
    return r.stdout


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rd(name):
    p = RAW / name
    return p.read_bytes() if p.exists() else None


def flat(obj, prefix=""):
    out = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.update(flat(v, prefix + "." + k if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.update(flat(v, prefix + "[" + str(i) + "]"))
    else:
        out[prefix] = obj
    return out


def parse_gguf(b):
    scalar = {0: ("<B", 1), 1: ("<b", 1), 2: ("<H", 2), 3: ("<h", 2), 4: ("<I", 4), 5: ("<i", 4),
              6: ("<f", 4), 7: ("<?", 1), 10: ("<Q", 8), 11: ("<q", 8), 12: ("<d", 8)}

    def rstr(off):
        (n,) = struct.unpack_from("<Q", b, off)
        off += 8
        return b[off:off + n].decode("utf-8", "replace"), off + n

    def rval(t, off, keep):
        if t == 8:
            s, off = rstr(off)
            return (s if keep else None), off
        if t == 9:
            (et,) = struct.unpack_from("<I", b, off)
            off += 4
            (cnt,) = struct.unpack_from("<Q", b, off)
            off += 8
            first = []
            for i in range(cnt):
                k = keep and i < 4
                v, off = rval(et, off, k)
                if k:
                    first.append(v)
            return {"len": cnt, "first": first}, off
        fmt, size = scalar[t]
        (v,) = struct.unpack_from(fmt, b, off)
        return (v if keep else None), off + size

    if b[:4] != b"GGUF":
        raise SystemExit("not a GGUF file")
    (n_kv,) = struct.unpack_from("<Q", b, 16)
    off = 24
    kvs = {}
    for _ in range(n_kv):
        key, off = rstr(off)
        (t,) = struct.unpack_from("<I", b, off)
        off += 4
        kvs[key], off = rval(t, off, True)
    return kvs


def main():
    print("# Round-25 decision-row checks (read-only)")
    print("pin", PIN)
    print("master", git("rev-parse", MASTER).decode().strip())
    ancestor = subprocess.run(["git", "-C", str(LANE), "merge-base", "--is-ancestor", PIN, MASTER]).returncode == 0
    print("pin is an ancestor of master:", ancestor)
    for path in (SKILL, ENTRY, RECEIPT):
        pinned = git("show", PIN + ":" + path)
        worktree = (LANE / path).read_bytes()
        print("bytes", path, "| pin", sha(pinned)[:16], len(pinned), "| worktree", sha(worktree)[:16],
              len(worktree), "| same", pinned == worktree)

    print("\n## 1. Decision table at the pin (lines 675-690) and format")
    lines = git("show", PIN + ":" + SKILL).decode("utf-8").splitlines()
    for n in range(675, 691):
        line = lines[n - 1]
        pipes = line.replace("\\|", "").count("|") if line.startswith("|") else "-"
        print(n, "pipes", pipes, line[:100])
    print("header line 127 equals header line 684:", lines[126] == lines[683])
    print("separator line 128 equals separator line 685:", lines[127] == lines[684])

    print("\n## 2. Receipt cells against raw bodies (committed receipt)")
    rec = json.loads(git("show", PIN + ":" + RECEIPT))
    for c in rec["cells"]:
        cid = c["id"]
        props = rd(cid + ".props.body")
        slots = rd(cid + ".slots.body")
        models = rd(cid + ".models.body")
        health = rd(cid + ".health.body")
        log = rd(cid + ".server.log") or b""
        raw = c["raw"]
        hashes_ok = all([
            sha(props) == raw["raw_props"],
            sha(slots) == raw["raw_slots"],
            sha(models) == raw["raw_models"],
            sha(health) == raw["raw_health"],
            sha(log) == raw["server_log"],
        ])
        pj = json.loads(props)
        mj = json.loads(models)
        sj = json.loads(slots)
        meta = mj["data"][0]["meta"]
        text = log.decode("utf-8", "replace")
        pools = [int(x) for x in re.findall(r"llama_context: n_ctx\s*= (\d+)", text)]
        init = re.findall(r"load_model: initializing, n_slots = (\d+), n_ctx_slot = (\d+), kv_unified = '(\w+)'", text)
        served = pj["default_generation_settings"]["n_ctx"]
        slot_vals = [s["n_ctx"] for s in sj]
        last_pool = pools[-1] if pools else None
        agrees = (served == c["props_n_ctx"] and meta["n_ctx"] == served and set(slot_vals) == {served}
                  and pj["total_slots"] == c["total_slots"] and meta["n_ctx_train"] == c["models_n_ctx_train"]
                  and last_pool == c["kv_pool_n_ctx"])
        print(f"{cid:<3} {c['args']:<46} props={served:<5} slots={slot_vals} total={pj['total_slots']} "
              f"meta.n_ctx={meta['n_ctx']} meta.n_ctx_train={meta['n_ctx_train']} "
              f"pool(last log line)={last_pool} kv_unified={init[0][2] if init else None} "
              f"raw_hashes_ok={hashes_ok} receipt_fields_agree={agrees}")
    starts = sorted(c["started_utc"] for c in rec["cells"])
    stops = sorted(c["stopped_utc"] for c in rec["cells"])
    print("cell start range", starts[0], "to", starts[-1])
    print("cell stop range ", stops[0], "to", stops[-1])
    entry_pin = git("show", PIN + ":" + ENTRY).decode("utf-8")
    verified = next(line for line in entry_pin.splitlines() if line.startswith("verified-at:"))
    print("entry verified-at at the pin:", verified[:230])

    print("\n## 3. K1 versus X2 raw bodies; pool or layout keys")
    for kind in ("props", "slots", "models"):
        a = flat(json.loads(rd("K1." + kind + ".body")))
        b = flat(json.loads(rd("X2." + kind + ".body")))
        diffs = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        print(kind, "fields differing K1 vs X2:", diffs or "none")
    for kind in ("props", "models", "slots"):
        keys = [k for k in flat(json.loads(rd("K1." + kind + ".body")))
                if re.search(r"kv|unified|pool|layout", k, re.I)]
        print("K1", kind, "keys naming kv, unified, pool or layout:", keys or "none")

    print("\n## 4. Fixture GGUF header (offline read; no server)")
    model = MODEL.read_bytes()
    kvs = parse_gguf(model)
    print("bytes", len(model), "sha256", sha(model), "| receipt model_sha256",
          rec["cells"][0]["model_sha256"], "| same", sha(model) == rec["cells"][0]["model_sha256"])
    print("general.architecture", kvs.get("general.architecture"), "| llama.context_length", kvs.get("llama.context_length"))
    print("kv pairs", len(kvs), "| keys containing sliding:", [k for k in kvs if "sliding" in k] or "none")
    print("keys containing rope with scal or yarn:", [k for k in kvs if "rope" in k and ("scal" in k or "yarn" in k)] or "none")

    print("\n## 5. Round-20 nctx-crosscheck predict() against observed per-slot n_ctx")
    spec = importlib.util.spec_from_file_location("nctx_crosscheck", NCTX)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    results = {}
    for c in rec["cells"]:
        argv = c["argv"][1:]
        cleaned, fit_off, i = [], False, 0
        while i < len(argv):
            if argv[i] == "--fit" and i + 1 < len(argv):
                fit_off = argv[i + 1] == "off"
                i += 2
                continue
            if argv[i] == "-v":
                i += 1
                continue
            cleaned.append(argv[i])
            i += 1
        got = mod.launch_settings(["llama-server"] + cleaned, [])
        pred = mod.predict(got["ctx"], 2048, got["np"], got["kvu"], got["per_slot"])[0]
        served = json.loads(rd(c["id"] + ".props.body"))["default_generation_settings"]["n_ctx"]
        results[c["id"]] = pred == served
        print(c["id"], "fit_off" if fit_off else "fit_on ", "round20", pred, "observed", served,
              "agree" if pred == served else "DISAGREE")
    config = [k for k in results if k not in ("X1", "L1", "L2", "L3")]
    print("config cells (all except X1 and L1-L3) agreeing:", sum(results[k] for k in config), "of", len(config))
    print("\nDONE")


if __name__ == "__main__":
    main()
