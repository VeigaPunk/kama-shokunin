#!/usr/bin/env python3
"""MT01Forgeries: end-to-end detector with SELF-BUILT near-boundary fixtures.

Runs each probe (pristine + six own mutants) through the same bash check path
the counter uses (the counter's Runner + Stub, imported read-only), against
fixtures I wrote that the 19 counter cells do not contain. Every verdict is
recorded; the expected isolating flips are asserted.
"""
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-98/w1/out/"
           "MT01Forgeries")
SCRATCH = Path("/fast/scratch/hyaku/kama-r98/MT01Forgeries")
REPO = SCRATCH / "repo"
MUTANTS = OUT / "mutants"


def load_counter():
    spec = importlib.util.spec_from_file_location(
        "rb98", REPO / "tools/round98-router-budget.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = load_counter()


def gguf_no_data(n_tensors: int, nd: int, name_len: int = 8) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", n_tensors, 0)]
    for i in range(n_tensors):
        name = (b"t%0*d" % (name_len - 1, i))
        dims = struct.pack("<" + "Q" * nd, 1, *([1] * (nd - 1)))
        out.append(struct.pack("<Q", len(name)) + name + struct.pack("<I", nd) + dims
                   + struct.pack("<IQ", 0, 1 << 40))
    return b"".join(out)


def gguf_kvstrarr(n: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<IIQ", 9, 8, n))
    out.append((struct.pack("<Q", 1) + b"x") * n)
    name = b"t0"
    out.append(struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    return b"".join(out)


def gguf_maxmeta(payload_len: int) -> bytes:
    out = [b"GGUF", struct.pack("<I", 3), struct.pack("<QQ", 1, 1)]
    out.append(struct.pack("<Q", 1) + b"k")
    out.append(struct.pack("<I", 8))
    out.append(struct.pack("<Q", payload_len))
    out.append(b"\0" * 64)
    name = b"t0"
    tail = (struct.pack("<Q", len(name)) + name + struct.pack("<IQIQ", 1, 1, 0, 1 << 40))
    return b"".join(out) + b"\0" * (payload_len - 64) + tail


def build_fixtures(fx: Path):
    fx.mkdir(parents=True, exist_ok=True)
    ok = fx / "ok.gguf"
    ok.write_bytes(MOD.gguf(1, 32, True))
    fxmap = {"ok": str(ok)}
    specs = [
        ("kvarr_2p6m", lambda p: p.write_bytes(gguf_kvstrarr(2_600_000))),
        ("nd4_650k", lambda p: p.write_bytes(gguf_no_data(650_000, 4))),
        ("nd1_950k", lambda p: p.write_bytes(gguf_no_data(950_000, 1))),
        ("nd1_720k", lambda p: p.write_bytes(gguf_no_data(720_000, 1))),
        ("nd1_630k", lambda p: p.write_bytes(gguf_no_data(630_000, 5))),  # nd=5 -> invalid; unused
    ]
    for name, fn in specs:
        if name == "nd1_630k":
            continue
        p = fx / f"{name}.gguf"
        fn(p)
        fxmap[name] = str(p)
    mm = fx / "maxmeta110.gguf"
    mm.write_bytes(gguf_maxmeta(110 * 1024 ** 2))
    fxmap["maxmeta110"] = str(mm)
    return fxmap


def check(mod, probe_bytes: bytes, work: Path, exe: str, model: str):
    work.mkdir(parents=True)
    R = mod.Runner(work)
    R.install(probe_bytes)
    routes = {"/v1/models": mod.router_body([[exe, "-m", model]]), "/props": mod.PROPS}
    with mod.Stub(routes) as st:
        return R.check(st.port)


def main() -> int:
    import shutil
    shutil.rmtree(SCRATCH / "selfwork", ignore_errors=True)
    shutil.rmtree(SCRATCH / "selfcheck", ignore_errors=True)
    fx = SCRATCH / "selfcheck"
    fxmap = build_fixtures(fx)
    # designed classes, from the probe's own accounting rule on the bytes I wrote
    print("SELFCHECK designed: " + " ".join(
        f"{k}={v}" for k, v in {
            "kvarr_2p6m": "invalid(4+3+2+2.6M+6 <= 5M)",
            "nd4_650k": "-(4+650k*9=5,850,004)",
            "nd1_950k": "-(4+950k*6=5,700,004)",
            "nd1_720k": "invalid(4+720k*6=4,320,004)",
            "maxmeta110": "invalid(pos 110MiB < 512MiB)",
        }.items()), flush=True)
    probes = {"pristine": REPO / "tools/kama-probe.sh"}
    for p in sorted(MUTANTS.glob("*.sh")):
        probes[p.stem] = p
    rows = {}
    for name, path in probes.items():
        pb = path.read_bytes()
        rows[name] = {"sha256": hashlib.sha256(pb).hexdigest(), "cases": {}}
        for ci, case in enumerate(["kvarr_2p6m", "nd4_650k", "nd1_950k", "nd1_720k",
                                   "maxmeta110"]):
            w = SCRATCH / f"selfwork/{name}/{case}"
            rc, v, r, dt = check(MOD, pb, w, fxmap["ok"], fxmap[case])
            rows[name]["cases"][case] = {"rc": rc, "verdict": v, "reason": r,
                                         "seconds": round(dt, 2)}
            print(f"SELFCHECK {name} {case} -> rc={rc} {v}/{r} {dt:.2f}s", flush=True)
    (OUT / "selfcheck.json").write_text(json.dumps(rows, indent=2) + "\n")

    # isolating expectations
    fails = []
    expect = {
        "kvarr_2p6m": {"pristine": "invalid", "A_kv2x": "-"},
        "nd4_650k": {"pristine": "-", "B_flat6": "invalid"},
        "nd1_950k": {"pristine": "-", "D_minus1": "invalid"},
        "nd1_720k": {"pristine": "invalid", "E_plus1": "-"},
        "maxmeta110": {"pristine": "invalid", "C_maxmeta100": "-"},
    }
    def vd(name, case):
        d = rows[name]["cases"][case]
        if d["verdict"] == "MODEL_OK":
            return "-"
        if d["verdict"] == "MODEL_UNLOADED":
            return "invalid" if d["reason"] == "router-model-invalid" else d["reason"]
        return d["verdict"]
    for case, exp in expect.items():
        for name, want in exp.items():
            got = vd(name, case)
            if got != want:
                fails.append(f"{case}: {name} -> {got!r} (want {want!r})")
    # isolation: the other mutants must match pristine on each case
    for case in expect:
        base = vd("pristine", case)
        for name in rows:
            if name == "pristine" or name in expect[case]:
                continue
            got = vd(name, case)
            if got != base:
                print(f"SELFCHECK_NOTE {case}: {name} also flips pristine {base!r} -> {got!r}",
                      flush=True)
    if fails:
        for f in fails:
            print(f"SELFCHECK_FAIL {f}")
        return 1
    print("SELFCHECK_OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
