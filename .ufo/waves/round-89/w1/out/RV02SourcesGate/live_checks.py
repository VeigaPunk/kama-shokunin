#!/usr/bin/env python3
"""RV02SourcesGate live checks (lane-owned children only; killpg on every exit path).

A: b12177 router, autoload, plain-text .gguf listed -> after a failed completion the entry
   reads unloaded + failed:true + exit_code:1 (knowledge/SKILL sentence, receipt-less).
B: b11755 router, --models-dir, GET /v1/models only -> status.args carries the child argv
   including --model <abs path> (knowledge sentence 3, b11755 half).
C: b12177 single-model server on a version=2 copy of stories260K -> loads (/health 200)
   (S586 reject reason 1: the b12177 loader loads v2).
D: b12177 single-model server on a copy with a gap in tensor offsets -> exits 1 with the
   S584 exact-contiguity error (S586 reject reason 2).
"""
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

SCRATCH = Path("/fast/scratch/hyaku/kama-r89/RV02SourcesGate/live")
OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-89/w1/out/RV02SourcesGate")
B12177 = Path("/home/vgpnk/.local/opt/llama-b12177/llama-server")
B11755 = Path("/home/vgpnk/.local/opt/llama-b11755/llama-server")
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
procs = []


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def stop_all():
    for p in procs:
        try:
            os.killpg(os.getpgid(p.pid), 15)
        except Exception:
            pass
    time.sleep(0.7)
    for p in procs:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            pass


def wait_health(port, timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=2) as r:
                return r.status, r.read().decode()
        except urllib.error.HTTPError as e:
            if e.code in (200, 503):
                body = e.read().decode()
                if e.code == 200:
                    return 200, body
            time.sleep(0.4)
        except Exception:
            time.sleep(0.4)
    return None, "timeout"


def get_json(port, path):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}", timeout=5) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def post_json(port, path, obj, timeout=60):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=json.dumps(obj).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def parse_gguf(path):
    """Return (n_tensors, alignment, infos[(name_len_pos,...)]) enough to patch the last offset."""
    b = Path(path).read_bytes()
    off = 0
    magic = b[0:4]; off = 4
    assert magic == b"GGUF"
    version = struct.unpack_from("<I", b, off)[0]; off += 4
    n_tensors, n_kv = struct.unpack_from("<QQ", b, off); off += 16
    align = 32
    SC = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 8, 11: 8, 12: 8}
    for _ in range(n_kv):
        klen = struct.unpack_from("<Q", b, off)[0]; off += 8
        key = b[off:off + klen]; off += klen
        t = struct.unpack_from("<I", b, off)[0]; off += 4
        if t == 8:
            slen = struct.unpack_from("<Q", b, off)[0]; off += 8 + slen
        elif t == 9:
            et, n = struct.unpack_from("<IQ", b, off); off += 12
            for _ in range(n):
                if et == 8:
                    slen = struct.unpack_from("<Q", b, off)[0]; off += 8 + slen
                elif et in SC:
                    off += SC[et]
                else:
                    raise SystemExit(f"array etype {et} unsupported")
        elif t in SC:
            if key == b"general.alignment":
                align = struct.unpack_from("<I", b, off)[0]
            off += SC[t]
        else:
            raise SystemExit(f"kv type {t} unsupported")
    infos = []
    for _ in range(n_tensors):
        nlen = struct.unpack_from("<Q", b, off)[0]; off += 8
        name = b[off:off + nlen]; off += nlen
        nd = struct.unpack_from("<I", b, off)[0]; off += 4
        off += 8 * nd
        tt = struct.unpack_from("<I", b, off)[0]; off += 4
        off_pos = off
        o = struct.unpack_from("<Q", b, off)[0]; off += 8
        infos.append((name.decode(), tt, o, off_pos))
    kv_end = off
    return version, n_tensors, align, infos, kv_end


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    report = []

    def say(s):
        print(s)
        report.append(s)

    # ---- Test A: failed:true capture on b12177 router child
    workA = SCRATCH / "A"; workA.mkdir()
    (workA / "badhdr.gguf").write_bytes(b"this is not a gguf file, just text\n" * 8)
    port = free_port()
    logA = SCRATCH / "A.log"
    with open(logA, "w") as lf:
        p = subprocess.Popen([str(B12177), "--port", str(port), "--models-dir", str(workA),
                              "--models-max", "1", "--host", "127.0.0.1"],
                             stdout=lf, stderr=subprocess.STDOUT, start_new_session=True, cwd=str(workA))
        procs.append(p)
        try:
            st, _ = wait_health(port)
            s1, b1 = get_json(port, "/v1/models")
            before = json.dumps(b1)[:400] if isinstance(b1, (list, dict)) else str(b1)[:400]
            c_code, c_body = post_json(port, "/v1/chat/completions",
                                       {"model": "badhdr", "max_tokens": 2,
                                        "messages": [{"role": "user", "content": "hi"}]})
            time.sleep(1.5)
            s2, b2 = get_json(port, "/v1/models")
            say(f"A: health={st} completion=HTTP {c_code} body={c_body[:160]}")
            say(f"A: /v1/models BEFORE completion: {before}")
            say(f"A: /v1/models AFTER completion: {json.dumps(b2) if isinstance(b2, dict) else str(b2)[:800]}")
        finally:
            try:
                os.killpg(os.getpgid(p.pid), 15)
            except Exception:
                pass
    procs.clear()

    # ---- Test B: b11755 router lists status.args (GET only)
    workB = SCRATCH / "B"; workB.mkdir()
    shutil.copy(MODEL, workB / "stories260K.gguf")
    port = free_port()
    logB = SCRATCH / "B.log"
    with open(logB, "w") as lf:
        p = subprocess.Popen([str(B11755), "--port", str(port), "--models-dir", str(workB),
                              "--host", "127.0.0.1"],
                             stdout=lf, stderr=subprocess.STDOUT, start_new_session=True, cwd=str(workB))
        procs.append(p)
        try:
            st, _ = wait_health(port)
            s, b = get_json(port, "/v1/models")
            say(f"B: b11755 GET /v1/models HTTP {s}")
            if isinstance(b, dict):
                for m in b.get("models", []):
                    st_obj = m.get("status", {})
                    say(f"B: id={m.get('id')} status.value={st_obj.get('value')} args={st_obj.get('args')}")
        finally:
            try:
                os.killpg(os.getpgid(p.pid), 15)
            except Exception:
                pass
    procs.clear()

    # ---- Test C: version-2 file loads on b12177
    workC = SCRATCH / "C"; workC.mkdir()
    v2 = workC / "stories-v2.gguf"
    data = bytearray(MODEL.read_bytes())
    assert data[0:4] == b"GGUF"
    ver = struct.unpack_from("<I", data, 4)[0]
    struct.pack_into("<I", data, 4, 2)
    v2.write_bytes(bytes(data))
    say(f"C: source version={ver} patched to 2 -> {v2}")
    port = free_port()
    logC = SCRATCH / "C.log"
    with open(logC, "w") as lf:
        p = subprocess.Popen([str(B12177), "-m", str(v2), "--port", str(port), "--host", "127.0.0.1"],
                             stdout=lf, stderr=subprocess.STDOUT, start_new_session=True, cwd=str(workC))
        procs.append(p)
        try:
            st, body = wait_health(port, timeout=40)
            say(f"C: v2 file /health -> HTTP {st} body={body[:160]}")
        finally:
            try:
                os.killpg(os.getpgid(p.pid), 15)
            except Exception:
                pass
    procs.clear()
    tail = logC.read_text(errors="replace")[-400:]
    say(f"C: log tail: {tail!r}")

    # ---- Test D: offset gap rejected by b12177
    workD = SCRATCH / "D"; workD.mkdir()
    version, n_tensors, align, infos, kv_end = parse_gguf(MODEL)
    say(f"D: stories260K version={version} n_tensors={n_tensors} align={align} infos={infos}")
    gap = workD / "stories-gap.gguf"
    data = bytearray(MODEL.read_bytes())
    name, tt, o, off_pos = infos[-1]
    struct.pack_into("<Q", data, off_pos, o + 2 * align)
    gap.write_bytes(bytes(data))
    port = free_port()
    logD = SCRATCH / "D.log"
    with open(logD, "w") as lf:
        p = subprocess.Popen([str(B12177), "-m", str(gap), "--port", str(port), "--host", "127.0.0.1"],
                             stdout=lf, stderr=subprocess.STDOUT, start_new_session=True, cwd=str(workD))
        procs.append(p)
        time.sleep(6)
        rc = p.poll()
        say(f"D: gap file (tensor '{name}' offset {o} -> {o + 2 * align}) server rc={rc}")
        try:
            st, body = wait_health(port, timeout=3)
            say(f"D: /health after wait -> HTTP {st} body={body[:120]}")
        except Exception as e:
            say(f"D: /health raised: {e}")
    try:
        os.killpg(os.getpgid(p.pid), 9)
    except Exception:
        pass
    procs.clear()
    tail = logD.read_text(errors="replace")
    hits = [ln for ln in tail.splitlines() if "offset" in ln or "expected" in ln or "GGUF" in ln]
    say("D: log lines mentioning offset/expected/GGUF:")
    for ln in hits[:6]:
        say(f"   {ln.strip()[:220]}")

    (OUT / "live-checks.out").write_text("\n".join(report) + "\n")
    print("WROTE", OUT / "live-checks.out")


if __name__ == "__main__":
    try:
        main()
    finally:
        stop_all()
