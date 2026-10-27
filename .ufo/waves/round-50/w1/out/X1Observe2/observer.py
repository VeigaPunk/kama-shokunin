#!/usr/bin/env python3
"""observer.py - X1Observe2 independent outside observer for kama round-50 C1.

Written WITHOUT reading tools/round50-replay-bind-audit.py. For each of the three
round-48 v5 receipts it drives one witnessed replay of tools/kama-live-replay.py
(round-50 build) at the measured tip and checks, from outside the replay, while the
server is held by the witness handshake (tools/kama-llamacpp-live.py writes
<wdir>/ready.json {port,pid} and waits for <wdir>/release):

  exe      /proc/<pid>/exe hashes to the receipt's server.sha256
  listen   the listening socket for the announced port is owned by <pid> (/proc/net/tcp{,6}
           inode -> /proc/<pid>/fd scan), and no other process owns a listener on it
  tree     the <pid> ppid chain reaches the replay pid we started (server descends from replay)
  mapped   the model file mapped in /proc/<pid>/maps (dev+inode re-stat'd, path reopened
           O_NOFOLLOW, hashed) hashes to the receipt's model.sha256
  env      /proc/<pid>/environ has no KAMA_R50_CANARY (planted in the replay's own env;
           also a PYTHONPATH sitecustomize canary that stamps a marker file)
  nonce    a fresh nonce 'observer nonce <16 hex>': the server tokenizes/detokenizes it
           exactly, its ids lie in the model's own vocabulary (GGUF header count, joined
           with /props n_vocab), and a greedy completion of the nonce answers with token
           ids inside that vocabulary whose detokenization equals the returned content and
           which repeats identically on a second identical request

Supplementary joins (not part of the six, recorded for comparison with the counter):
  child_pid  ready.json pid == the rerun receipt's child_pid
  mapping    the replay's recorded model_mapping dev/inode/sha256 == what I observed

Usage: observer.py --repo CLONE --tip COMMIT --receipts R1 R2 R3 --scratch DIR --out JSON
Exit 0 when all six legs hold for all three replays, 1 otherwise, 2 on setup failure.
"""
from __future__ import annotations

import binascii
import hashlib
import http.client
import json
import os
import re
import secrets
import shutil
import socket
import struct
import subprocess
import sys
import time

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REPLAY_KEYS = ("PATH", "HOME", "LANG", "LC_ALL")


# ---------------------------------------------------------------- small utilities
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError:
        return None


def proc_status(pid):
    raw = read_text(f"/proc/{pid}/status")
    if raw is None:
        return None
    out = {}
    for line in raw.decode("utf-8", "replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def ppid_of(pid):
    st = proc_status(pid)
    if not st:
        return None
    try:
        return int(st.get("PPid", "").split()[0])
    except (IndexError, ValueError):
        return None


def ancestry(pid):
    """[pid, parent, grandparent, ...] up to 1; stops on a vanished pid."""
    chain, seen, cur = [], set(), pid
    while cur and cur > 1 and cur not in seen:
        seen.add(cur)
        chain.append(cur)
        cur = ppid_of(cur)
    if cur == 1:
        chain.append(1)
    return chain


def environ_of(pid):
    raw = read_text(f"/proc/{pid}/environ")
    if raw is None:
        return None
    return [e.split(b"=", 1)[0].decode("utf-8", "replace")
            for e in raw.split(b"\0") if e]


# ---------------------------------------------------------------- listener ownership
def listening_inodes(port):
    """{inode: local_addr} for LISTEN sockets on `port`, from /proc/net/tcp{,6}."""
    found = {}
    for table in ("/proc/net/tcp", "/proc/net/tcp6"):
        raw = read_text(table)
        if raw is None:
            continue
        for line in raw.decode("ascii", "replace").splitlines()[1:]:
            parts = line.split()
            if len(parts) < 10:
                continue
            local, state, inode = parts[1], parts[3], parts[9]
            if state != "0A":
                continue
            try:
                p = int(local.rsplit(":", 1)[1], 16)
            except ValueError:
                continue
            if p == port:
                found[inode] = local
    return found


def socket_owners():
    """{socket inode: [pid, ...]} by scanning /proc/<pid>/fd."""
    owners = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        fd_dir = f"/proc/{name}/fd"
        try:
            entries = os.listdir(fd_dir)
        except OSError:
            continue
        for fd in entries:
            try:
                target = os.readlink(f"{fd_dir}/{fd}")
            except OSError:
                continue
            if target.startswith("socket:["):
                ino = target[8:-1]
                owners.setdefault(ino, []).append(int(name))
    return owners


# ---------------------------------------------------------------- maps / vocab
def maps_entries(pid):
    raw = read_text(f"/proc/{pid}/maps")
    if raw is None:
        return []
    out = []
    for line in raw.decode("utf-8", "surrogateescape").splitlines():
        parts = line.split(None, 5)
        if len(parts) < 6:
            continue
        addr, perms, offset, dev, inode, path = parts
        out.append({"addr": addr, "perms": perms, "offset": offset, "dev": dev,
                    "inode": inode, "path": path, "deleted": path.endswith(" (deleted)")})
    return out


def model_maps(pid, sha_want):
    """Maps lines whose pathname is the .gguf model, verified by dev+inode and hash."""
    hits, notes = [], []
    for e in maps_entries(pid):
        path = e["path"][:-10] if e["deleted"] else e["path"]
        if not path.startswith("/") or not path.endswith(".gguf"):
            continue
        real = os.path.realpath(path)
        try:
            st = os.stat(real)
            fd = os.open(real, os.O_RDONLY | os.O_NOFOLLOW)
        except OSError as exc:
            notes.append(f"model-maps-open-failed:{path}:{exc.strerror}")
            continue
        try:
            dev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
            ino = str(st.st_ino)
            got = sha256_file(real)
        finally:
            os.close(fd)
        hit = {"path": path, "dev": e["dev"], "inode": e["inode"], "stat_dev": dev,
               "stat_inode": ino, "sha256": got, "deleted": e["deleted"]}
        hits.append(hit)
        if e["dev"] != dev or e["inode"] != ino:
            notes.append(f"maps-stat-mismatch:{path}:maps={e['dev']}:{e['inode']}:stat={dev}:{ino}")
    ok = bool(hits) and all(h["sha256"] == sha_want and h["dev"] == h["stat_dev"]
                            and h["inode"] == h["stat_inode"] and not h["deleted"] for h in hits)
    return ok, hits, notes


def gguf_tokens(path, key_want="tokenizer.ggml.tokens"):
    """The model's own vocabulary: the GGUF metadata string array at `key_want`, read
    from the file header alone (no llama.cpp code, no server involvement).
    Returns {'count': N, 'tokens': [bytes, ...]} or None."""
    try:
        fh = open(path, "rb")
    except OSError:
        return None
    with fh:
        try:
            if fh.read(4) != b"GGUF":
                return None
            version = struct.unpack("<I", fh.read(4))[0]
            if version not in (2, 3):
                return None
            struct.unpack("<Q", fh.read(8))  # tensor count
            n_kv = struct.unpack("<Q", fh.read(8))[0]
            sizes = {0: 1, 1: 1, 2: 2, 3: 2, 4: 4, 5: 4, 6: 4, 7: 1, 10: 4, 11: 8, 12: 8}

            def rstr():
                n = struct.unpack("<Q", fh.read(8))[0]
                return fh.read(n)

            def skip(t):
                if t == 8:
                    return rstr()
                if t == 9:
                    et = struct.unpack("<I", fh.read(4))[0]
                    cnt = struct.unpack("<Q", fh.read(8))[0]
                    for _ in range(cnt):
                        skip(et)
                    return None
                n = sizes.get(t)
                if n is None:
                    raise ValueError("gguf-bad-type")
                return fh.read(n)

            for _ in range(n_kv):
                key = rstr().decode("utf-8", "replace")
                vtype = struct.unpack("<I", fh.read(4))[0]
                if vtype == 9:
                    et = struct.unpack("<I", fh.read(4))[0]
                    cnt = struct.unpack("<Q", fh.read(8))[0]
                    if key == key_want:
                        if et != 8:
                            return None
                        return {"count": cnt, "tokens": [rstr() for _ in range(cnt)]}
                    for _ in range(cnt):
                        skip(et)
                else:
                    skip(vtype)
        except (ValueError, struct.error, OSError):
            return None
    return None


def decode_ids(tokens, ids):
    """Decode ids through the model's own vocabulary with llama.cpp's sentencepiece
    convention: concatenate pieces, then turn U+2581 ('▁') into a space. The leading
    space the tokenizer puts on a word-initial piece is kept (llama-server's own
    /detokenize keeps it too), so callers compare against ' ' + text."""
    try:
        raw = b"".join(tokens[i] for i in ids)
    except (IndexError, TypeError):
        return None
    return raw.replace("\u2581".encode(), b" ").decode("utf-8", "surrogateescape")


# ---------------------------------------------------------------- HTTP
def http_json(port, method, path, body=None, timeout=20):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=timeout)
    try:
        payload = None if body is None else json.dumps(body).encode()
        headers = {"Content-Type": "application/json"} if payload else {}
        conn.request(method, path, body=payload, headers=headers)
        resp = conn.getresponse()
        raw = resp.read()
        try:
            data = json.loads(raw.decode("utf-8", "replace"))
        except ValueError:
            data = {"raw": raw[:400].decode("utf-8", "replace")}
        return resp.status, data
    finally:
        conn.close()


def nonce_roundtrip(port, nonce, vocab):
    """Fresh-nonce round trip against the model's own vocabulary.

    `vocab` is {'count', 'tokens'} parsed from the gguf file the server maps (checked by
    the caller against the frozen model digest). The server tokenizes the nonce; those ids
    are decoded here with the model's own vocabulary and must give back the nonce (modulo
    the sentencepiece leading space llama.cpp always puts on a word-initial piece). The
    server then answers a greedy completion of the nonce: the answer's content must be
    non-empty, its re-tokenization must stay inside the vocabulary, its own-vocabulary
    decode must reproduce the content, and the same request must repeat identically.
    """
    checks, notes = {}, []
    status, props = http_json(port, "GET", "/props")
    checks["props_ok"] = status == 200
    text = None
    if isinstance(props, dict):
        text = props.get("model_alias")
    checks["props_model_alias"] = text
    n = vocab.get("count") if isinstance(vocab, dict) else None
    toks = vocab.get("tokens") if isinstance(vocab, dict) else None
    checks["vocab_count"] = n
    # 1. nonce -> ids -> nonce through the model's own vocabulary
    st, tok = http_json(port, "POST", "/tokenize", {"content": nonce})
    ids = tok.get("tokens") if isinstance(tok, dict) else None
    checks["tokenize_ok"] = st == 200 and isinstance(ids, list) and bool(ids)
    if checks["tokenize_ok"]:
        checks["nonce_ids_in_vocab"] = (n is not None
                                        and all(isinstance(i, int) and 0 <= i < n for i in ids))
        decoded = decode_ids(toks, ids) if toks and checks["nonce_ids_in_vocab"] else None
        checks["nonce_decoded"] = decoded
        checks["nonce_roundtrip_exact"] = decoded is not None and decoded == " " + nonce
        if not checks["nonce_roundtrip_exact"]:
            notes.append(f"nonce-decode:{decoded!r}")
        # freshness: a second, different nonce tokenizes differently inside the vocabulary
        other = nonce[:-2] + ("00" if not nonce.endswith("00") else "01")
        st_o, tok_o = http_json(port, "POST", "/tokenize", {"content": other})
        ids_o = tok_o.get("tokens") if isinstance(tok_o, dict) else None
        checks["nonce_fresh"] = (st_o == 200 and isinstance(ids_o, list) and ids_o != ids)
    else:
        checks["nonce_ids_in_vocab"] = checks["nonce_roundtrip_exact"] = checks["nonce_fresh"] = False
    # 2. the server answers a generation request built from the nonce
    req = {"prompt": nonce, "n_predict": 16, "temperature": 0.0, "top_k": 1,
           "seed": 424242, "cache_prompt": False, "stream": False}
    st3, comp = http_json(port, "POST", "/completion", req)
    content = comp.get("content") if isinstance(comp, dict) else None
    predicted = comp.get("tokens_predicted") if isinstance(comp, dict) else None
    checks["completion_ok"] = st3 == 200 and isinstance(comp, dict)
    checks["completion_predicted"] = predicted
    checks["completion_content"] = content
    if checks["completion_ok"] and isinstance(content, str) and content:
        st4, ctok = http_json(port, "POST", "/tokenize", {"content": content})
        cids = ctok.get("tokens") if isinstance(ctok, dict) else None
        checks["completion_ids_in_vocab"] = (st4 == 200 and isinstance(cids, list) and bool(cids)
                                             and n is not None
                                             and all(isinstance(i, int) and 0 <= i < n for i in cids))
        cdec = decode_ids(toks, cids) if checks["completion_ids_in_vocab"] else None
        checks["completion_decoded"] = cdec
        checks["completion_decode_matches"] = (cdec is not None and cdec == " " + content)
        st5, comp2 = http_json(port, "POST", "/completion", req)
        checks["completion_repeats"] = (st5 == 200 and isinstance(comp2, dict)
                                        and comp2.get("content") == content)
    else:
        checks["completion_ids_in_vocab"] = checks["completion_decode_matches"] = False
        checks["completion_repeats"] = False
        notes.append(f"completion-empty:{content!r}")
    checks["nonce"] = nonce
    checks["passed"] = all(checks.get(k) for k in (
        "props_ok", "tokenize_ok", "nonce_ids_in_vocab", "nonce_roundtrip_exact",
        "nonce_fresh", "completion_ok", "completion_ids_in_vocab",
        "completion_decode_matches", "completion_repeats"))
    return checks, notes


# ---------------------------------------------------------------- one witnessed replay
def observe_one(repo, receipt_path, idx, scratch, canary_dir):
    wd = os.path.join(scratch, f"witness-{idx}")
    work = os.path.join(scratch, f"work-{idx}")
    out_json = os.path.join(scratch, f"replay-{idx}.json")
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    os.makedirs(work, exist_ok=True)
    os.makedirs(canary_dir, exist_ok=True)
    marker = os.path.join(canary_dir, "marker")
    if os.path.exists(marker):
        os.unlink(marker)
    rec = json.load(open(receipt_path))
    want_exe = (rec.get("server") or {}).get("sha256")
    want_model = (rec.get("model") or {}).get("sha256")
    result = {"receipt": receipt_path, "want_exe": want_exe, "want_model": want_model,
              "legs": {}, "notes": [], "supplementary": {}}
    token = secrets.token_hex(8)
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "LC_ALL") if k in os.environ}
    env["TMPDIR"] = os.environ.get("TMPDIR", scratch)
    env["KAMA_R50_CANARY"] = "observer-" + token          # planted canary value
    env["PYTHONPATH"] = canary_dir                         # sitecustomize canary vector
    replay = os.path.join(repo, "tools", "kama-live-replay.py")
    argv = [sys.executable, "-I", replay, "--receipt", receipt_path, "--work", work,
            "--out", out_json, "--witness-dir", wd, "--witness-timeout", "120"]
    result["argv"] = argv
    p = subprocess.Popen(argv, cwd=repo, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    result["replay_pid"] = p.pid
    ready = os.path.join(wd, "ready.json")
    deadline = time.monotonic() + 240
    info = None
    while time.monotonic() < deadline:
        if os.path.exists(ready):
            try:
                info = json.load(open(ready))
            except ValueError:
                info = None
            if info:
                break
        if p.poll() is not None:
            break
        time.sleep(0.05)
    if not info:
        err = p.communicate(timeout=30)[1] if p.poll() is not None else ""
        result["notes"].append(f"no-witness-ready:exit={p.poll()}:stderr={err[-600:]}")
        for leg in ("exe", "listen", "tree", "mapped", "env", "nonce"):
            result["legs"][leg] = {"passed": False, "detail": "no-ready.json"}
        try:
            p.kill()
        except OSError:
            pass
        result["replay_exit"] = p.wait()
        return result
    result["ready"] = info
    pid, port = info.get("pid"), info.get("port")
    result["witness"] = {"pid": pid, "port": port}
    # the replay's own environ (sanity: canary planted where the live child's parent sits)
    replay_env = environ_of(p.pid) or []
    result["supplementary"]["canary_in_replay_env"] = "KAMA_R50_CANARY" in replay_env
    time.sleep(0.1)
    # 1. exe
    try:
        exe = os.readlink(f"/proc/{pid}/exe")
        exe_hash = sha256_file(exe)
        result["legs"]["exe"] = {"passed": exe_hash == want_exe, "exe": exe, "sha256": exe_hash}
    except OSError as exc:
        result["legs"]["exe"] = {"passed": False, "detail": f"readlink:{exc.strerror}"}
    # 2. listener ownership
    inodes = listening_inodes(port)
    owners = socket_owners()
    owner_pids = sorted({pid_ for ino in inodes for pid_ in owners.get(ino, [])})
    all_inode_owners = {ino: sorted(owners.get(ino, [])) for ino in inodes}
    result["legs"]["listen"] = {
        "passed": bool(inodes) and bool(set(owner_pids)) and owner_pids == [pid],
        "port": port, "listen_inodes": sorted(inodes), "inode_owners": all_inode_owners,
        "owner_pids": owner_pids}
    # 3. descent from the replay
    chain = ancestry(pid)
    result["legs"]["tree"] = {
        "passed": p.pid in chain and chain and chain[0] == pid,
        "chain": chain, "replay_pid": p.pid}
    parent = ppid_of(pid)
    result["supplementary"]["direct_parent"] = parent
    result["supplementary"]["parent_cmdline"] = (read_text(f"/proc/{parent}/cmdline") or b"").replace(b"\0", b" ").decode("utf-8", "replace")[:300]
    result["supplementary"]["replay_cmdline"] = (read_text(f"/proc/{p.pid}/cmdline") or b"").replace(b"\0", b" ").decode("utf-8", "replace")[:300]
    # 4. mapped model
    gguf = None
    for root, _dirs, files in os.walk(work):
        for f in files:
            if f.endswith(".gguf"):
                gguf = os.path.join(root, f)
                break
        if gguf:
            break
    mapped_ok, hits, mnotes = model_maps(pid, want_model)
    result["legs"]["mapped"] = {"passed": mapped_ok, "hits": hits, "work_model": gguf}
    result["notes"].extend(mnotes)
    vocab = None
    if gguf:
        vocab = gguf_tokens(gguf, "tokenizer.ggml.tokens")
        result["supplementary"]["gguf_sha256"] = sha256_file(gguf)
        result["supplementary"]["gguf_vocab_count"] = vocab.get("count") if vocab else None
        result["supplementary"]["gguf_vocab_from_mapped_file"] = (
            result["supplementary"]["gguf_sha256"] == want_model)
    # 5. env canary (assigned surface: the server's own /proc/<pid>/environ)
    envkeys = environ_of(pid)
    if envkeys is None:
        result["legs"]["env"] = {"passed": False, "detail": "environ-unreadable"}
    else:
        bad = [k for k in envkeys if k == "KAMA_R50_CANARY"]
        bad_path = [k for k in envkeys if k == "PYTHONPATH"]
        result["legs"]["env"] = {"passed": not bad, "canary_keys": bad,
                                 "pythonpath_keys": bad_path,
                                 "env_key_count": len(envkeys),
                                 "env_keys": sorted(envkeys)}
    # 5b. the same canary in the server's parent (the live tool) - the surface where the
    # pre-build leak shows (base 26ecba64 passes the assigned server-environ check)
    penv = environ_of(parent) if parent else None
    if penv is None:
        result["supplementary"]["parent_env"] = "unreadable"
    else:
        result["supplementary"]["parent_env"] = {
            "canary_keys": [k for k in penv if k == "KAMA_R50_CANARY"],
            "pythonpath_keys": [k for k in penv if k == "PYTHONPATH"],
            "env_keys": sorted(penv)}
        result["supplementary"]["parent_env_canary_free"] = "KAMA_R50_CANARY" not in penv
        result["supplementary"]["parent_env_pythonpath_free"] = "PYTHONPATH" not in penv
    # 6. nonce round trip
    try:
        nchecks, nnotes = nonce_roundtrip(port, "observer nonce " + token, vocab)
        result["legs"]["nonce"] = {"passed": nchecks["passed"], "checks": nchecks}
        result["notes"].extend(nnotes)
    except (OSError, http.client.HTTPException) as exc:
        result["legs"]["nonce"] = {"passed": False, "detail": f"http:{type(exc).__name__}:{exc}"}
    # release the witness hold and let the replay finish its own checks
    open(os.path.join(wd, "release"), "w").close()
    try:
        out, err = p.communicate(timeout=240)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        result["notes"].append("replay-timeout-after-release")
    result["replay_exit"] = p.returncode
    result["replay_stdout_tail"] = (out or "")[-800:]
    result["replay_stderr_tail"] = (err or "")[-1500:]
    # supplementary joins: rerun receipt child_pid + recorded model_mapping
    rerun = None
    if os.path.exists(out_json):
        try:
            rj = json.load(open(out_json))
        except ValueError:
            rj = {}
        result["replay_out"] = {k: rj.get(k) for k in
                                ("schema", "match", "refused", "mismatches", "live_child", "witness_dir")}
        rerun = rj.get("rerun_receipt")
    rr = {}
    if rerun and os.path.exists(rerun):
        rr = json.load(open(rerun))
        result["rerun_receipt"] = rerun
    result["supplementary"]["child_pid_join"] = rr.get("child_pid") == pid
    result["supplementary"]["rerun_child_pid"] = rr.get("child_pid")
    mm = rr.get("model_mapping") if isinstance(rr.get("model_mapping"), dict) else {}
    result["supplementary"]["recorded_model_mapping"] = mm
    observed = hits[0] if hits else {}
    result["supplementary"]["mapping_join"] = (
        mm.get("mapped") is True and observed.get("sha256") == mm.get("sha256")
        and str(observed.get("inode")) == str(mm.get("inode"))
        and str(observed.get("dev")) == str(mm.get("dev")))
    result["supplementary"]["canary_marker_file"] = os.path.exists(marker)
    result["legs_passed"] = sum(1 for leg in result["legs"].values() if leg.get("passed"))
    result["passed"] = result["legs_passed"] == 6
    # extended verdict: the six assigned legs plus the canary surfaces that actually move
    # between the base and the build (live tool environ, sitecustomize marker)
    result["extended_passed"] = bool(result["passed"]
                                    and result["supplementary"].get("parent_env_canary_free")
                                    and result["supplementary"].get("parent_env_pythonpath_free")
                                    and not result["supplementary"].get("canary_marker_file"))
    return result


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--tip", required=True)
    ap.add_argument("--receipts", nargs="+", required=True)
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    os.makedirs(a.scratch, exist_ok=True)
    canary_dir = os.path.join(a.scratch, "canary")
    os.makedirs(canary_dir, exist_ok=True)
    with open(os.path.join(canary_dir, "sitecustomize.py"), "w") as fh:
        fh.write(
            "import os\n"
            "try:\n"
            "    open(os.path.join(os.path.dirname(__file__), 'marker'), 'a').write(str(os.getpid()) + '\\n')\n"
            "except Exception:\n"
            "    pass\n")
    results = []
    head = subprocess.run(["git", "-C", a.repo, "rev-parse", "HEAD"], capture_output=True, text=True)
    head_sha = head.stdout.strip()
    for idx, receipt in enumerate(a.receipts, 1):
        print(f"[observer] replay {idx}: {receipt}", flush=True)
        try:
            r = observe_one(os.path.abspath(a.repo), os.path.abspath(receipt), idx,
                            os.path.abspath(a.scratch), canary_dir)
        except Exception as exc:  # keep the other replays running
            r = {"receipt": receipt, "legs": {}, "notes": [f"observer-exception:{type(exc).__name__}:{exc}"],
                 "passed": False}
        results.append(r)
        legs = {k: v.get("passed") for k, v in (r.get("legs") or {}).items()}
        print(f"[observer] {idx}: legs={legs} passed={r.get('passed')}", flush=True)
    doc = {"schema": "x1observe2-observer/v1", "tip": a.tip, "clone_head": head_sha,
           "receipts": [os.path.abspath(p) for p in a.receipts], "replays": results,
           "met": all(r.get("passed") for r in results) and len(results) == len(a.receipts)}
    with open(a.out, "w") as fh:
        json.dump(doc, fh, indent=1, sort_keys=True)
    print(f"[observer] met={doc['met']}")
    return 0 if doc["met"] else 1


if __name__ == "__main__":
    sys.exit(main())
