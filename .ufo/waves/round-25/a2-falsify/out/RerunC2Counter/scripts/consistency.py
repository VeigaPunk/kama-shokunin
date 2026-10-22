import json
import re
import sys

path = sys.argv[1]
d = json.load(open(path))
cells = d["cells"]
srv = d["server"]
PORT_RANGE = d["port_range"]
REFUSED = set(d["port_refusal_set"])
POOL = re.compile(r"llama_context: n_ctx\s*=\s*(\d+)\s*$")
NSLOT = re.compile(r"n_slots = (\d+), n_ctx_slot = (\d+), kv_unified = '(true|false)'")
fails = []
rows = []


def fail(cid, msg):
    fails.append(f"{cid}: {msg}")


for c in cells:
    cid = c["id"]
    args = c["args"]
    argv = c.get("argv") or []
    t = c.get("teardown") or {}
    log = c.get("log_lines") or []
    pools = [int(m.group(1)) for m in map(POOL.search, log) if m]
    nslots = [m.groups() for m in map(NSLOT.search, log) if m]
    reqs = c.get("requests") or []
    rows.append(
        f"{cid:3} obs={c.get('observed')!s:5} err={c.get('error')!s:6} "
        f"rc={t.get('child_returncode')!s:4} portclosed={t.get('port_closed')!s:5} "
        f"port={c.get('port')} tot={c.get('total_slots')} props={c.get('props_n_ctx')} "
        f"slots={c.get('slots_n_ctx')} pool={c.get('kv_pool_n_ctx')} cand={c.get('kv_pool_candidates')} "
        f"train={c.get('models_n_ctx_train')} mode={c.get('request_mode')} "
        f"logpools={pools} nslot={nslots} "
        f"reqs={[(q.get('status'), q.get('t_start'), q.get('t_end')) for q in reqs]} "
        f"delta={c.get('concurrency_delta_s')}"
    )
    # tool verdict fields the counter never reads
    if c.get("observed") is not True:
        fail(cid, f"tool observed flag is {c.get('observed')!r}")
    if c.get("error") is not None:
        fail(cid, f"tool error is {c.get('error')!r}")
    if t.get("port_closed") is not True:
        fail(cid, "port_closed not True")
    if t.get("child_returncode") is None:
        fail(cid, "child_returncode None")
    if t.get("ss_listen_lines_after"):
        fail(cid, f"ss_listen_lines_after non-empty {t.get('ss_listen_lines_after')}")
    # binding fields per cell
    if c.get("server_sha256") != srv["sha256"]:
        fail(cid, "cell server_sha256 differs from top-level server sha")
    if c.get("model_sha256") != d["model_sha256"]:
        fail(cid, "cell model_sha256 differs from top-level")
    # port scope and argv
    if not (PORT_RANGE[0] <= c.get("port", -1) <= PORT_RANGE[1]) or c.get("port") in REFUSED:
        fail(cid, f"port {c.get('port')} outside range or refused")
    if "--port" not in argv or argv[argv.index("--port") + 1] != str(c.get("port")):
        fail(cid, "argv --port does not match cell port")
    if "-m" not in argv or argv[argv.index("-m") + 1] != d["model"]["realpath"]:
        fail(cid, "argv -m does not match model realpath")
    if argv[:1] != [srv["realpath"]]:
        fail(cid, f"argv[0] {argv[:1]} differs from server realpath")
    if argv[-len(args.split()):] != args.split():
        fail(cid, "argv does not end with args")
    # props / slots / pool internal consistency
    slots = c.get("slots_n_ctx") or []
    if c.get("total_slots") != len(slots):
        fail(cid, "total_slots != len(slots_n_ctx)")
    if slots and any(s != c.get("props_n_ctx") for s in slots):
        fail(cid, "props_n_ctx differs from per-slot n_ctx")
    if pools and c.get("kv_pool_n_ctx") != pools[-1]:
        fail(cid, "kv_pool_n_ctx != last log pool line")
    if c.get("kv_pool_candidates") and c["kv_pool_candidates"][-1] != c.get("kv_pool_n_ctx"):
        fail(cid, "kv_pool_candidates[-1] != kv_pool_n_ctx")
    if not nslots:
        fail(cid, "no n_slots line")
    else:
        ns, nc, ku = nslots[-1]
        if int(ns) != c.get("total_slots"):
            fail(cid, f"log n_slots {ns} != total_slots")
        if any(int(nc) != s for s in slots):
            fail(cid, f"log n_ctx_slot {nc} != slots_n_ctx {slots}")
    if c.get("models_n_ctx_train") != 2048:
        fail(cid, f"models_n_ctx_train {c.get('models_n_ctx_train')} (expected training context 2048)")
    # load cells
    if cid.startswith("L"):
        want = "sequential" if cid == "L3" else "concurrent"
        if c.get("request_mode") != want:
            fail(cid, f"request_mode {c.get('request_mode')} != {want}")
        if len(reqs) != 2:
            fail(cid, f"{len(reqs)} requests")
        if any(q.get("prompt_tokens") != 1000 or q.get("n_predict") != 600 for q in reqs):
            fail(cid, "request prompt_tokens/n_predict not 1000/600")
        if len(reqs) == 2:
            ov = max(q["t_start"] for q in reqs) < min(q["t_end"] for q in reqs)
            if ov != (want == "concurrent"):
                fail(cid, f"overlap {ov} does not match mode {want}")
            if want == "concurrent" and c.get("concurrency_delta_s") is None:
                fail(cid, "concurrency_delta_s missing")
    else:
        if c.get("requests") or c.get("request_mode") is not None:
            fail(cid, "config cell carries request data")

# child windows must not overlap (one child at a time)
order = sorted(cells, key=lambda c: c.get("started_utc") or "")
for a, b in zip(order, order[1:]):
    if (a.get("stopped_utc") or "") > (b.get("started_utc") or ""):
        fail(b["id"], f"starts {b.get('started_utc')} before {a['id']} stopped {a.get('stopped_utc')}")
ports = [c.get("port") for c in cells]
if len(set(ports)) != len(ports):
    fail("ALL", "a port was reused across cells")

print("== per-cell rows ==")
for r in rows:
    print(r)
print()
print("== consistency failures ==", len(fails))
for f in fails:
    print(" ", f)
print("cell order:", [c["id"] for c in order])
