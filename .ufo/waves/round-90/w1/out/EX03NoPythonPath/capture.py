import json, os, sys
sys.path.insert(0, '.')
import runner as R

env = dict(os.environ, PATH=R.NOPY_BIN); env.pop("PYTHONPATH", None)
cases = {
 "H4raw-tab": {"/v1/models": {"body": R.doc_bytes_rawctrl(["good", "evil\tFORGED-ROW\tx\tMODEL_OK"])}},
 "H6raw-esc": {"/v1/models": {"body": R.doc_bytes_rawctrl(["good", "\x1b[31mRED"])}},
 "X-del-raw": {"/v1/models": {"body": R.doc_bytes_rawctrl(["good", "a\x7fb"])}},
 "X-u0085-raw": {"/v1/models": {"body": R.doc_bytes_rawctrl(["good", "a\u0085b"])}},
}
out = {}
for name, routes in cases.items():
    for rev in ("B", "M"):
        with R.Stub(routes) as st:
            rc, so, se = R.run(R.PROBE[rev], st.port, "good", False, env)
            rcj, soj, _ = R.run(R.PROBE[rev], st.port, "good", True, env)
        out[f"{name}/{rev}"] = {"rc": rc, "table_hex": so.hex(), "table_repr": repr(so)[:400],
                                "json_rc": rcj, "json_repr": repr(soj)[:300],
                                "has_del": b"\x7f" in so, "has_nel": b"\xc2\x85" in so,
                                "has_esc": b"\x1b" in so, "has_01": b"\x01" in so}
json.dump(out, open("capture.json", "w"), indent=1)
for k, v in out.items():
    print(k, "rc=", v["rc"], "esc=", v["has_esc"], "del=", v["has_del"], "nel=", v["has_nel"], "c0x01=", v["has_01"])
    print("   table:", v["table_repr"][:260])
