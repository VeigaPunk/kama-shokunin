#!/usr/bin/env python3
"""HeldOut cells for C2: BASE vs M2 probes on unseen inputs.

Usage: python3 held_out.py --base base.sh --m2 m2.sh --out results.json [--kill 180]

Cells (2 = base run, M = M2 run):
 H1 models[] not data[], 200k ids
 H2 ids under `model` key
 H3 CRLF inside ids
 H4 100k duplicate ids
 H5 router entries failed:true, 60k
 H6 router autoload 80k unloaded, path missing -> router_file_states 80k args
 H7 table (non --json) output, 1.9MB backslash id
 H8 registry-mode check --registry with 3 rows
 H9 second snapshot run over 16000 ids (DELTA transitions)
 H10 served list mixing quotes/backslashes/controls at 1MB

Harm = base is right (rc+stdout fingerprint matches expected semantics) and M2 differs
from base (byte-equal stdout unless snapshot/timestamp nondeterminism). For H9 Delta/timestamps vary;
we compare rows and transitions rather than raw bytes.
"""
import argparse, hashlib, http.server, json, os, socket, subprocess, sys, tempfile, threading, time
from pathlib import Path

CAP = 4194304

class Stub:
    def __init__(ind, routes):
        ind.routes = routes
        stub = ind
        class H(http.server.BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.0"
            def log_message(self, *a): pass
            def do_GET(self):
                body = stub.routes.get(self.path.split("?")[0])
                code = 200
                if body is None:
                    body, code = b'{"error":"not found"}', 404
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                try: self.wfile.write(body)
                except OSError: pass
        ind.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        ind.srv.daemon_threads = True
        ind.port = ind.srv.server_address[1]
        ind.t = threading.Thread(target=ind.srv.serve_forever, daemon=True)
    def __enter__(ind):
        ind.t.start()
        dl = time.time() + 10
        while time.time() < dl:
            try:
                with socket.create_connection(("127.0.0.1", ind.port), timeout=1):
                    return ind
            except OSError:
                time.sleep(0.05)
        raise RuntimeError("stub never accepted")
    def __exit__(ind, *a):
        ind.srv.shutdown(); ind.srv.server_close()

def jbody(doc):
    b = json.dumps(doc, separators=(",", ":")).encode()
    if len(b) >= CAP: raise ValueError(f"body {len(b)} >= cap")
    return b

def run_one(probe, args, cwd, kill):
    t0 = time.monotonic()
    env = dict(os.environ, TMPDIR=str(cwd))
    try:
        p = subprocess.run(["bash", str(probe)] + args, capture_output=True, timeout=kill, env=env, cwd=cwd)
        return p.returncode, p.stdout, p.stderr, time.monotonic() - t0, False
    except subprocess.TimeoutExpired as e:
        return None, b"", b"", time.monotonic() - t0, True

def row_of(out):
    try:
        return json.loads(out.decode("utf-8"))["rows"][0]
    except Exception:
        return None

def stable(tsv):
    return b"\n".join(l for l in tsv.split(b"\n") if not l.startswith(b"#@snapshot_id"))

def snapshot_run(probe, port, expect, snapdir, kill):
    if snapdir.exists():
        import shutil; shutil.rmtree(snapdir)
    snapdir.mkdir(parents=True, exist_ok=True)
    pin = snapdir / "pin.txt"; pin.write_text(f"http://127.0.0.1:{port}/v1\n")
    reg = snapdir / "registry.tsv"
    reg.write_text("id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\n"
                   f"cell\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\t{expect}\tr92\n")
    hist = snapdir / "history"
    outdir = snapdir / "out"
    outdir.mkdir()
    rc, so, se, dt, killed = run_one(probe, ["snapshot", "--json", "--registry", str(reg), "--history", str(hist), "--timeout", "5", "--connect-timeout", "2"], outdir, kill)
    latest = hist / "latest.tsv"; tsv = latest.read_bytes() if latest.exists() else None
    delta = hist / "DELTA.md"; dtxt = delta.read_bytes().decode("utf-8", "replace") if delta.exists() else None
    return rc, so, se, dt, killed, tsv, dtxt

def registry_check(probe, port, kill, work):
    # 3 rows, all pointing to same stub via pin files
    work.mkdir(parents=True, exist_ok=True)
    reg = work / "reg.tsv"; lines = ["id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes"]
    for i, exp in enumerate(["good", "missing", "*"]):
        pin = work / f"pin{i}.txt"; pin.write_text(f"http://127.0.0.1:{port}/v1\n")
        lines.append(f"row{i}\t{pin}\tgrep:http://[^ ]+\thttp://127.0.0.1:{port}/v1\t{exp}\tr92")
    reg.write_text("\n".join(lines) + "\n")
    return run_one(probe, ["check", "--json", "--registry", str(reg), "--timeout", "5", "--connect-timeout", "2"], work, kill)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True); ap.add_argument("--m2", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--kill", type=int, default=180)
    a = ap.parse_args()

    def ids_doc(ids): return {"object": "list", "data": [{"id": i} for i in ids]}

    def router_doc(entries):
        data = []
        for i, st, failed, path in entries:
            s = {"value": st}
            if failed is not None: s["failed"] = failed
            e = {"id": i, "status": s}
            if path is not None: e["path"] = path
            data.append(e)
        return {"object": "list", "data": data}

    results = {}
    def record(cell, base, m2, note=""):
        # base/m2: dicts with rc, stdout_hash, seconds, verdict, reason, killed
        harm = (not base["killed"] and base["rc"] is not None and not m2["killed"] and m2["rc"] is not None
                and base["verdict"] is not None and (base["verdict"] != m2["verdict"] or base["reason"] != m2["reason"] or base["stdout_hash"] != m2["stdout_hash"]))
        # Also count harm if base completed but M2 differs in parseable output
        # byte-equal check uses stdout_hash for most cells; for snapshot we use special comparison
        results[cell] = {"base": base, "m2": m2, "harm": harm, "note": note}
        print(f"{cell} harm={int(harm)} base={base['verdict']}/{base['reason']} rc={base['rc']} sec={base['seconds']:.2f} kill={base['killed']}  m2={m2['verdict']}/{m2['reason']} rc={m2['rc']} sec={m2['seconds']:.2f} kill={m2['killed']} {note}", flush=True)

    def check_cell(cell, routes, expect, extra_args=None):
        with Stub(routes) as s:
            cwd = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            brc, bso, bse, bdt, bk = run_one(a.base, (["check", "--port", str(s.port), "--expect", expect, "--timeout", "5", "--connect-timeout", "2", "--json"] if extra_args is None else extra_args(s.port)), cwd, a.kill)
            mrc, mso, mse, mdt, mk = run_one(a.m2, (["check", "--port", str(s.port), "--expect", expect, "--timeout", "5", "--connect-timeout", "2", "--json"] if extra_args is None else extra_args(s.port)), cwd, a.kill)
            br, mr = row_of(bso), row_of(mso)
            base = dict(rc=brc, seconds=bdt, killed=bk, verdict=(br or {}).get("verdict"), reason=(br or {}).get("reason"),
                        stdout_len=len(bso), stdout_hash=hashlib.sha256(bso).hexdigest()[:16], served_len=(len((br or {}).get("served_model","")) if br else -1))
            m2d = dict(rc=mrc, seconds=mdt, killed=mk, verdict=(mr or {}).get("verdict"), reason=(mr or {}).get("reason"),
                       stdout_len=len(mso), stdout_hash=hashlib.sha256(mso).hexdigest()[:16], served_len=(len((mr or {}).get("served_model","")) if mr else -1))
            record(cell, base, m2d)

    # H1: models[] key instead of data[], 200k ids
    try:
        ids = [f"m{i:06d}" for i in range(200000)]
        # use models[] not data[]
        doc = {"object": "list", "models": [{"id": i} for i in ids]}
        check_cell("H1-models-200k", {"/v1/models": jbody(doc)}, "m000123")
    except Exception as e:
        print("H1 error", e, flush=True)

    # H2: ids under `model` key
    try:
        doc = {"object": "list", "data": [], "models": [{"model": f"mm{i}"} for i in range(5000)]}
        check_cell("H2-model-key", {"/v1/models": jbody(doc)}, "mm0001")
    except Exception as e:
        print("H2 error", e, flush=True)

    # H3: CRLF inside ids
    try:
        ids = ["good", "a\r\nb", "c\r\nd", "x\ry", "p\nq"]
        check_cell("H3-crlf-ids", {"/v1/models": jbody(ids_doc(ids))}, "good")
    except Exception as e:
        print("H3 error", e, flush=True)

    # H4: 100k duplicate ids of one value
    try:
        check_cell("H4-dup-100k", {"/v1/models": jbody(ids_doc(["good"]*100000))}, "good")
    except Exception as e:
        print("H4 error", e, flush=True)

    # H5: router entries failed:true (60k)
    try:
        doc = router_doc([("good", "unloaded", True, None)]*60000)
        check_cell("H5-router-failed-60k", {"/v1/models": jbody(doc)}, "good")
    except Exception as e:
        print("H5 error", e, flush=True)

    # H6: router autoload, 80k unloaded matching, path missing -> 80k args to router_file_states
    try:
        # 80k entries cannot carry per-entry paths under the 4 MiB cap (min ~55B x 80k = 4.4MB > cap),
        # so H6 uses path-missing form (no path field): file_state returns '-' (undecidable, stays
        # loadable) and the point is the 80k-argv pass to router_file_states plus the cand array.
        # This matches how the frozen counter's D9 router_doc path (top-level, not status.args)
        # is also undecidable. Body ~3.28MB fits.
        doc = router_doc([("good", "unloaded", None, None) for _ in range(80000)])
        routes = {"/v1/models": jbody(doc), "/props": b'{"role":"router","models_autoload":true}'}
        check_cell("H6-router-autoload-80k-missing", routes, "good")
    except Exception as e:
        print("H6 error", e, flush=True)

    # H7: table (non --json) output mode with 1.9MB backslash id
    try:
        # Use check --port without --json; build via custom runner
        with Stub({"/v1/models": jbody(ids_doc(["\\" * 1900000]))}) as s:
            cwd = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            brc, bso, _, bdt, bk = run_one(a.base, ["check", "--port", str(s.port), "--expect", "good", "--timeout", "5", "--connect-timeout", "2"], cwd, a.kill)
            mrc, mso, _, mdt, mk = run_one(a.m2, ["check", "--port", str(s.port), "--expect", "good", "--timeout", "5", "--connect-timeout", "2"], cwd, a.kill)
            base = dict(rc=brc, seconds=bdt, killed=bk, verdict=("MODEL_MISMATCH" if b"MISMATCH" in bso or b"MODEL_MISMATCH" in bso else None), reason=None, stdout_len=len(bso), stdout_hash=hashlib.sha256(bso).hexdigest()[:16], served_len=-1)
            m2d = dict(rc=mrc, seconds=mdt, killed=mk, verdict=("MODEL_MISMATCH" if b"MISMATCH" in mso or b"MODEL_MISMATCH" in mso else None), reason=None, stdout_len=len(mso), stdout_hash=hashlib.sha256(mso).hexdigest()[:16], served_len=-1)
            # For table mode, verdict inferred from text; also compare raw bytes directly
            eq = (bso == mso and brc == mrc)
            base["verdict"] = "MODEL_MISMATCH" if b"MODEL_MISMATCH" in bso else ("MODEL_OK" if b"MODEL_OK" in bso else None)
            m2d["verdict"] = "MODEL_MISMATCH" if b"MODEL_MISMATCH" in mso else ("MODEL_OK" if b"MODEL_OK" in mso else None)
            record("H7-table-backslash-1.9MB", base, m2d, note=f"bytes_equal={eq}")
    except Exception as e:
        print("H7 error", e, flush=True)

    # H8: registry-mode check --registry <file> with 3 rows
    try:
        with Stub({"/v1/models": jbody(ids_doc(["good"]))}) as s:
            cwd = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            brc, bso, _, bdt, bk = run_one(a.base, ["check", "--json", "--registry", "/nonexistent", "--timeout", "5", "--connect-timeout", "2"], cwd, a.kill)  # placeholder to warm
            # real: build registry pointing to this stub via pin files
            work = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            brc2, bso2, _, bdt2, bk2 = registry_check(a.base, s.port, a.kill, work)
            work2 = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            mrc2, mso2, _, mdt2, mk2 = registry_check(a.m2, s.port, a.kill, work2)
            try:
                brs = json.loads(bso2.decode())["rows"]; mrs = json.loads(mso2.decode())["rows"]
                bv = [(r["id"], r["verdict"]) for r in brs]; mv = [(r["id"], r["verdict"]) for r in mrs]
            except Exception:
                bv = []; mv = []
            base = dict(rc=brc2, seconds=bdt2, killed=bk2, verdict=str(bv), reason="", stdout_len=len(bso2), stdout_hash=hashlib.sha256(bso2).hexdigest()[:16], served_len=-1)
            m2d = dict(rc=mrc2, seconds=mdt2, killed=mk2, verdict=str(mv), reason="", stdout_len=len(mso2), stdout_hash=hashlib.sha256(mso2).hexdigest()[:16], served_len=-1)
            record("H8-registry-3rows", base, m2d, note=f"rows_equal={bv==mv}")
    except Exception as e:
        print("H8 error", e, flush=True)

    # H9: second snapshot run over 16000 ids so DELTA transitions are computed
    try:
        doc = ids_doc([f"/m/x{i:05d}.gguf" for i in range(16000)])
        with Stub({"/v1/models": jbody(doc)}) as s:
            cwd = Path(tempfile.mkdtemp(dir="/fast/scratch/hyaku/kama-r92/EX01HeldOutCells"))
            snapbase = cwd / "snap-base"
            rc1, _, _, dt1, k1, tsv1, d1 = snapshot_run(a.base, s.port, "x00000", snapbase, a.kill)
            rc2, _, _, dt2, k2, tsv2, d2 = snapshot_run(a.base, s.port, "x00000", snapbase, a.kill)
            # second run on same history computed transitions; now M2 with fresh history: first then second
            snapm2 = cwd / "snap-m2"
            mrc1, _, _, mdt1, mk1, mtsv1, md1 = snapshot_run(a.m2, s.port, "x00000", snapm2, a.kill)
            mrc2, _, _, mdt2, mk2, mtsv2, md2 = snapshot_run(a.m2, s.port, "x00000", snapm2, a.kill)
            b_eq = (tsv1 is not None and mtsv1 is not None and stable(tsv1) == stable(mtsv1))
            b2_eq = (tsv2 is not None and mtsv2 is not None and stable(tsv2) == stable(mtsv2))
            # delta text without timestamps: strip first 20 chars per line? Compare transition counts
            def trans_count(t): 
                if not t: return 0
                return sum(1 for l in t.splitlines() if "baseline" not in l and l.strip().startswith("- "))
            base = dict(rc=rc2, seconds=dt2, killed=k2, verdict=f"tsv_stable_b={b_eq} d_trans={trans_count(d2)}", reason="", stdout_len=len(tsv2 or b""), stdout_hash=hashlib.sha256(tsv2 or b"").hexdigest()[:16], served_len=-1)
            m2d = dict(rc=mrc2, seconds=mdt2, killed=mk2, verdict=f"tsv_stable_m={b2_eq} d_trans={trans_count(md2)}", reason="", stdout_len=len(mtsv2 or b""), stdout_hash=hashlib.sha256(mtsv2 or b"").hexdigest()[:16], served_len=-1)
            # harm for H9: base and M2 differ on second-run TSV (stable) or transition counts
            harm = (tsv2 is not None and mtsv2 is not None and stable(tsv2) != stable(mtsv2)) or (trans_count(d2) != trans_count(md2))
            results["H9-snapshot-second-16k"] = {"base": base, "m2": m2d, "harm": harm, "note": f"base_rc1={rc1} m2_rc1={mrc1} second_tsv_equal={b2_eq}"}
            print(f"H9-snapshot-second-16k harm={int(harm)} base rc={rc2} sec={dt2:.2f} m2 rc={mrc2} sec={mdt2:.2f} trans_b={trans_count(d2)} trans_m={trans_count(md2)} second_tsv_equal={b2_eq}", flush=True)
    except Exception as e:
        print("H9 error", e, flush=True)

    # H10: served list mixing quotes/backslashes/controls at 1MB
    try:
        # Build ~1MB of ids mixing specials: repeat pattern; total under cap
        # Use 30000 ids each ~33 chars = ~1MB
        unit = "q\"b\\s\t\u0001x/y.gguf"
        ids = [unit + str(i % 10) for i in range(30000)]
        check_cell("H10-mixed-1MB", {"/v1/models": jbody(ids_doc(ids))}, "good")
    except Exception as e:
        print("H10 error", e, flush=True)

    # Persist raw
    Path(a.out).write_text(json.dumps({"results": results, "kill": a.kill}, indent=2))
    harms = [k for k, v in results.items() if v["harm"]]
    print(f"HARMS {harms}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
