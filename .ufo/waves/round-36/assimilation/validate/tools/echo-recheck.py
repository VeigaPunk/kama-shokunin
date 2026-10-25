#!/usr/bin/env python3
r"""echo-recheck -- runnable recheck of the round-27 live echo probe (S137).

Replaces the `recheck:` cadence of corpus/knowledge/echo-discriminating-counters.md
with a procedure that never overwrites the committed receipts:

  start   ~/.local/opt/llama-b11755/llama-server
          -m ~/.cache/kama-shokunin/models/stories260K.gguf
          --host 127.0.0.1 --port P            (P in 48231-48233 or --port)
  probe   the six POST bodies of
          .ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/probe.py, byte for
          byte, to POST /v1/chat/completions
  record  HTTP status and response sha256 per request in --out (JSON)
  compare against the committed receipt at
          .ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/receipt.json
  verdict echo-recheck same N/N   -> exit 0
          echo-recheck drift IDS  -> exit 1
          echo-recheck cannot-evaluate REASON -> exit 2
  stop    SIGTERM to the server's process group, then `ss -ltnp` and a
          connect attempt prove the port closed

--out is required and refused when it already exists (also its derived
.server.log), so a run can never write over an earlier receipt. Only the two
files below --out's directory are written.

Comparison basis (recorded per request):
  * committed status >= 300: byte equality of the response body. These are
    the S137 validation responses; their bytes are the evidence and repeat
    exactly on an unchanged build.
  * committed status < 300: the success body carries a per-run `id`, a
    wall-clock `created`, `timings`, one sampled token, and a prefix-cache
    counter (`usage.prompt_tokens_details`) that follows the server's context
    flags (measured: `cached_tokens` 41 under the round-27 probe argv
    `-c 256 -t 2`, 0 under the round-28 argv pinned here), so raw bytes cannot
    repeat. Compare a canonical projection that drops exactly `id`, `created`,
    `timings`, each `choices[].message.content` and `usage.prompt_tokens_details`;
    the raw response sha256 is still recorded.

The binary, libllama-server-impl.so and model are sha256-pinned to the values
in .ufo/waves/round-27/count-c1.py PINS; a mismatch, a missing baseline
request, a fixture sha mismatch, a server that cannot start, or a port that
cannot be proven closed is a cannot-evaluate (exit 2), never a silent pass.
"""
import argparse
import copy
import hashlib
import http.client
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path

HOME = Path.home()
OPT = HOME / ".local/opt/llama-b11755"
SERVER = OPT / "llama-server"
IMPL = OPT / "libllama-server-impl.so"
MODEL = HOME / ".cache/kama-shokunin/models/stories260K.gguf"
PINS = {
    SERVER: "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804",
    IMPL: "e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed",
    MODEL: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d",
}

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
DEFAULT_RECEIPT = (
    LANE / ".ufo/waves/round-27/w1a3/out/ExecLiveEchoProbe/receipt.json")

PORT_CANDIDATES = (48231, 48232, 48233)
READY_TIMEOUT = 120.0

SIGA = b"echo_sig_9f3a"
SIGB = b"alt_sig_4b7e"
MSG = b'{"messages":[{"role":"user","content":"hi"}],"max_tokens":1'


def esc(s):
    return b"".join(b"\\u%04x" % c for c in s)


# Exact bytes of probe.py (round-27 live probe), verified against the committed
# receipt request_sha256 values before the server starts.
REQ = {
    "req4-control": MSG + b"}",
    "req1-plain": MSG + b',"response_format":{"type":"echo_sig_9f3a"}}',
    "req2-firstesc": MSG + b',"response_format":{"type":"\\u0065cho_sig_9f3a"}}',
    "req3-fullesc": MSG + b',"response_format":{"type":"' + esc(SIGA) + b'"}}',
    "req5-altsig-plain": MSG + b',"response_format":{"type":"alt_sig_4b7e"}}',
    "req6-altsig-full": MSG + b',"response_format":{"type":"' + esc(SIGB) + b'"}}',
}
ORDER = ["req4-control", "req1-plain", "req2-firstesc", "req3-fullesc",
         "req5-altsig-plain", "req6-altsig-full"]

DROP_TOP = ("id", "created", "timings")
DROP_MESSAGE = ("content",)
DROP_USAGE = ("prompt_tokens_details",)


class CannotEvaluate(Exception):
    pass


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode()


def project_obj(payload):
    """Deterministic part of a 2xx /v1/chat/completions body."""
    if not isinstance(payload, dict):
        raise CannotEvaluate("response is not a JSON object")
    j = copy.deepcopy(payload)
    j = {k: v for k, v in j.items() if k not in DROP_TOP}
    choices = j.get("choices")
    if isinstance(choices, list):
        for c in choices:
            if isinstance(c, dict) and isinstance(c.get("message"), dict):
                c["message"] = {k: v for k, v in c["message"].items()
                                if k not in DROP_MESSAGE}
    usage = j.get("usage")
    if isinstance(usage, dict):
        j["usage"] = {k: v for k, v in usage.items() if k not in DROP_USAGE}
    return j


def projection(body):
    try:
        j = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CannotEvaluate(f"response is not JSON: {exc}") from exc
    return canonical(project_obj(j))


def port_is_free(port):
    """True when nothing listens on 127.0.0.1:port and we can bind it."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(("127.0.0.1", port))
        except OSError:
            return False
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.settimeout(0.3)
        return c.connect_ex(("127.0.0.1", port)) != 0


def http_request(port, method, path, body=None, timeout=30):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        headers = {"Content-Type": "application/json"} if body is not None else {}
        conn.request(method, path, body=body, headers=headers)
        r = conn.getresponse()
        return r.status, dict(r.getheaders()), r.read()
    finally:
        conn.close()


def log_tail(path, limit=4096):
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            f.seek(max(0, f.tell() - limit))
            return f.read().decode("utf-8", "replace")
    except OSError:
        return ""


def start_server(port, log_path):
    argv = [str(SERVER), "-m", str(MODEL), "--host", "127.0.0.1",
            "--port", str(port)]
    with open(log_path, "xb") as log:
        proc = subprocess.Popen(argv, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
    return argv, proc, os.getpgid(proc.pid)


def wait_ready(port, proc, log_path):
    deadline = time.monotonic() + READY_TIMEOUT
    last = None
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            raise CannotEvaluate(
                f"server exited {proc.returncode} before ready; "
                f"log tail: {log_tail(log_path)[-600:]!r}")
        try:
            st, _, data = http_request(port, "GET", "/health", timeout=2)
            last = (st, data[:120])
            if st == 200:
                try:
                    if json.loads(data) == {"status": "ok"}:
                        return {"status": st, "body": data.decode("utf-8", "replace")}
                except (UnicodeDecodeError, json.JSONDecodeError):
                    pass
        except (OSError, http.client.HTTPException):
            pass
        time.sleep(0.1)
    raise CannotEvaluate(
        f"server not ready on 127.0.0.1:{port} within {READY_TIMEOUT:.0f}s; "
        f"last health {last}; log tail: {log_tail(log_path)[-600:]!r}")


def terminate(proc, pgid, timeout=20.0):
    if proc.poll() is None:
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                return False
    return proc.poll() is not None


def listener_lines(port):
    try:
        res = subprocess.run(["ss", "-H", "-ltnp"], capture_output=True,
                             text=True, timeout=15)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CannotEvaluate(f"ss -ltnp failed: {exc}") from exc
    if res.returncode != 0:
        raise CannotEvaluate(f"ss -ltnp exit {res.returncode}: {res.stderr.strip()}")
    pat = re.compile(r":%d\b" % port)
    return [ln for ln in res.stdout.splitlines() if pat.search(ln)]


def port_closed_proof(port):
    lines = listener_lines(port)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as c:
        c.settimeout(0.5)
        rc = c.connect_ex(("127.0.0.1", port))
    return {"ss_ltnp_listeners": lines, "connect_exit": rc,
            "closed": not lines and rc != 0}


def load_baseline(path):
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CannotEvaluate(f"baseline unreadable: {exc}") from exc
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CannotEvaluate(f"baseline not JSON: {exc}") from exc
    reqs = doc.get("requests")
    if not isinstance(reqs, dict):
        raise CannotEvaluate("baseline has no requests object")
    for name in ORDER:
        entry = reqs.get(name)
        if not isinstance(entry, dict) or "status" not in entry \
                or "response_sha256" not in entry:
            raise CannotEvaluate(f"baseline missing status/sha for {name}")
    return raw, doc


def check_pins():
    doc = {}
    for path, want in PINS.items():
        if not path.is_file():
            raise CannotEvaluate(f"missing pinned file {path}")
        got = sha256_file(path)
        if got != want:
            raise CannotEvaluate(f"pin mismatch {path}: {got} != {want}")
        doc[str(path)] = got
    return doc


def compare_one(name, status, body, committed):
    c_status = committed["status"]
    record = {
        "status": status,
        "response_bytes": len(body),
        "response_sha256": sha256_bytes(body),
        "response_body": body.decode("utf-8", "backslashreplace")
                         if len(body) <= 65536 else None,
        "committed_status": c_status,
        "committed_response_sha256": committed["response_sha256"],
    }
    if c_status >= 300:
        record["compare_basis"] = "body-sha256"
        record["compare_sha256"] = sha256_bytes(body)
        record["committed_compare_sha256"] = committed["response_sha256"]
        record["equal"] = (status == c_status
                           and record["compare_sha256"]
                           == record["committed_compare_sha256"])
    else:
        record["compare_basis"] = "stable-json"
        record["excluded_fields"] = ["id", "created", "timings",
                                     "choices[].message.content",
                                     "usage.prompt_tokens_details"]
        try:
            cur = projection(body)
            record["compare_sha256"] = sha256_bytes(cur)
        except CannotEvaluate as exc:
            record["compare_sha256"] = None
            record["compare_error"] = str(exc)
        cj = committed.get("response_json")
        if isinstance(cj, dict):
            record["committed_compare_sha256"] = sha256_bytes(
                canonical(project_obj(cj)))
        else:
            record["committed_compare_sha256"] = None
        record["equal"] = (status == c_status
                           and record["committed_compare_sha256"] is not None
                           and record["compare_sha256"]
                           == record["committed_compare_sha256"])
    return record


def evaluate(args, out, doc):
    out.parent.mkdir(parents=True, exist_ok=True)
    log_path = Path(str(out) + ".server.log")
    if os.path.lexists(log_path):
        raise CannotEvaluate(f"server log exists: {log_path}")

    doc["observed_at_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    try:
        doc["tool_sha256"] = sha256_file(Path(__file__).resolve())
    except OSError:
        doc["tool_sha256"] = None

    baseline_path = Path(args.receipt)
    raw, baseline = load_baseline(baseline_path)
    doc["baseline"] = {"path": str(baseline_path),
                       "sha256": sha256_bytes(raw)}

    for name in ORDER:
        want = baseline["requests"][name]["request_sha256"]
        got = sha256_bytes(REQ[name])
        if got != want:
            raise CannotEvaluate(
                f"fixture sha mismatch {name}: {got} != {want}")
    doc["fixtures"] = {n: sha256_bytes(REQ[n]) for n in ORDER}

    doc["pins"] = check_pins()

    if args.port is not None:
        if not 1 <= args.port <= 65535:
            raise CannotEvaluate(f"--port out of range: {args.port}")
        if not port_is_free(args.port):
            raise CannotEvaluate(f"--port {args.port} is not free")
        port = args.port
        selection = "explicit"
    else:
        port = None
        for candidate in PORT_CANDIDATES:
            if port_is_free(candidate):
                port = candidate
                break
        if port is None:
            raise CannotEvaluate(
                "no free port in " + "-".join(map(str, (PORT_CANDIDATES[0],
                                                        PORT_CANDIDATES[-1]))))
        selection = "auto"

    doc["port"] = port
    doc["port_selection"] = selection

    argv, proc, pgid = start_server(port, log_path)
    doc["server"] = {"argv": argv, "pid": proc.pid, "pgid": pgid,
                     "log": str(log_path)}
    pending = None
    try:
        doc["health"] = wait_ready(port, proc, log_path)
        doc["requests"] = {}
        for name in ORDER:
            try:
                status, hdrs, body = http_request(
                    port, "POST", "/v1/chat/completions", REQ[name],
                    timeout=120)
            except (OSError, http.client.HTTPException) as exc:
                raise CannotEvaluate(
                    f"request {name} failed: {type(exc).__name__}: {exc}"
                ) from exc
            rec = compare_one(name, status, body, baseline["requests"][name])
            rec["content_type"] = hdrs.get("Content-Type")
            doc["requests"][name] = rec
    except BaseException as exc:  # noqa: BLE001 -- cleanup below must run
        pending = exc

    stopped = terminate(proc, pgid)
    proof = port_closed_proof(port)
    doc["shutdown"] = {
        "signal": "SIGTERM (process group)",
        "exited": stopped,
        "returncode": proc.poll(),
        "port": port,
        "port_closed": proof,
    }
    if not stopped:
        raise CannotEvaluate(f"server pid {proc.pid} did not exit")
    if not proof["closed"]:
        raise CannotEvaluate(f"port {port} still has a listener after shutdown")
    if pending is not None:
        raise pending

    differing = [n for n in ORDER if not doc["requests"][n]["equal"]]
    doc["same"] = len(ORDER) - len(differing)
    doc["total"] = len(ORDER)
    doc["differing"] = differing


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="echo-recheck",
        description="Re-run the round-27 live echo probe against the pinned "
                    "llama-server and compare with its committed receipt.")
    ap.add_argument("--out", required=True,
                    help="receipt JSON path; must not exist")
    ap.add_argument("--receipt", default=str(DEFAULT_RECEIPT),
                    help="committed probe receipt to compare against "
                         "(default: %(default)s)")
    ap.add_argument("--port", type=int, default=None,
                    help="explicit port (default: first free of 48231-48233)")
    args = ap.parse_args(argv)

    out = Path(args.out)
    if os.path.lexists(out):
        print(f"echo-recheck cannot-evaluate --out exists: {out}")
        return 2

    doc = {"schema": "kama-echo-recheck/v1",
           "tool": "tools/echo-recheck.py",
           "out": str(out),
           "requests": {}}
    code = 2
    try:
        evaluate(args, out, doc)
        code = 0 if not doc["differing"] else 1
    except CannotEvaluate as exc:
        doc["error"] = str(exc)
        code = 2
    except Exception as exc:  # noqa: BLE001 -- never fail open
        doc["error"] = f"unexpected {type(exc).__name__}: {exc}"
        code = 2

    doc["exit"] = code
    try:
        with open(out, "x") as f:
            json.dump(doc, f, indent=1, sort_keys=True)
            f.write("\n")
    except FileExistsError:
        print(f"echo-recheck cannot-evaluate --out exists: {out}")
        return 2
    except OSError as exc:
        print(f"echo-recheck cannot-evaluate cannot write {out}: {exc}")
        return 2

    if code == 0:
        print(f"echo-recheck same {doc['same']}/{doc['total']}")
    elif code == 1:
        print("echo-recheck drift " + " ".join(doc["differing"]))
    else:
        print(f"echo-recheck cannot-evaluate {doc.get('error')}")
    return code


if __name__ == "__main__":
    sys.exit(main())
