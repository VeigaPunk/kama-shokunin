#!/usr/bin/env python3
"""Round-27 C1 counter (depth): live request-validation error signatures in SKILL.md.

Frozen predicate, amendments A1, A2 and A3 (the same sentence as preregistration.json
C1.predicate and the label `counted` in the receipt):

  A registry row is COUNTED iff
  (a) the first table of the SKILL.md section whose heading starts with
      "## Round-27 request-validation signatures" has the header
      `| id | signature | trigger | meaning | next action | source |`, and one
      of its rows has exactly these six cells with: id = the registry id; the
      signature cell holding the registry signature verbatim; the trigger cell
      holding the request path verbatim; meaning and next-action cells of at
      least six words each; the source cell holding the registry S### token;
  (b) the signature is at least 20 UTF-8 bytes, holds no "|" and no newline, and
      it is new to the lane: neither it nor its JSON-escaped form occurs,
      case-folded, verbatim or with all whitespace removed, in ANY tracked file
      of the lane at base a720399e except the pinned source snapshots (paths
      holding "/sources/") -- so knowledge already in SKILL.md, corpus/, the
      registry or any earlier round's wave evidence never counts;
  (c) its S### row exists in corpus/SOURCES.md of the measured tree, does not
      exist at base, and names the registry source file, the registry line
      (as "L<line>" or "line <line>") and commit 704366d;
  (d) the cited file is in the sha256-pinned 704366d snapshot, the signature is
      a substring of a C string literal on the cited line (escapes decoded; one
      literal or the line's literals joined), the cited line or one of the
      three lines above it holds an error-raising token (ERROR_TOKENS), and the
      signature is a substring of no string literal on any other line of any
      pinned snapshot file (it names its source line uniquely);
  (e) the row's profile is one of PROFILES (the counter owns every argv; rows
      set none), its request is GET or POST to a plain path with a JSON body or
      none and no headers, and the counter's own run returns status >= 400
      whose JSON-decoded error message contains the signature. The run is the
      pinned llama-server process the counter launched: its /proc exe is the
      sha256-pinned binary, the pinned libllama-server-impl.so is mapped, and
      /props reports the pinned fixture model path; the counter re-executes
      itself as /usr/bin/python3 -I -S with the fixed environment
      {PATH, HOME, LANG} before reading anything, and refuses to evaluate
      (exit 2) when the interpreter or git is not the sha256-pinned host
      binary, /etc/ld.so.preload is non-empty, its own process or the server
      maps a file outside /usr/ and /etc/ld.so.cache (server: also the pinned install and model),
      the server's environment is not the fixed one, or any base object it
      reads (commit, every tree, every blob) fails its git hash;
  (f) the signature does not occur (case-insensitive, verbatim or with all
      whitespace removed) in the request path, in any JSON-decoded string key
      or value of the request body, in either JSON serialisation of the body,
      in the counter's healthy baseline (responses and server log) or in
      `llama-server --help` / `--version`;
  (g) the row's own control request (same profile, method and path) returns
      2xx and its body does not contain the signature;
  (h) one fault, one row: its (file, line) differs from every earlier counted
      row, the signature is neither a substring nor a superstring of an earlier
      counted signature, no earlier counted signature occurs in its error
      message and it occurs in no earlier counted row's error message, its
      request differs from every earlier counted request, its next-action
      cell (case and whitespace folded) differs from every earlier counted
      row's next-action cell, its S### differs from every earlier counted
      row's S###, and its error message with the signature cut out
      (case-folded), when not blank, differs from every earlier counted row's
      message with that row's signature cut out (one message frame, one row).

Not checked by this counter (reviewed per row, never counted): whether the
trigger, meaning and next-action prose is correct (KamaR27CtlContentFree).

Claim met iff counted >= 15 (preregistration.json C1.target).

Usage: count-c1.py [--lane DIR] [--repo GITDIR] [--out FILE]
Exit: 0 ran (whatever the count), 2 could not evaluate (pins, process
identity, unsafe port, baseline failed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "a720399e627b23026143646cb8de470b266346b5"
TARGET = 15
MIN_BYTES = 20
OPT = Path.home() / ".local/opt/llama-b11755"
SERVER = OPT / "llama-server"
PINS = {
    SERVER: "b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804",
    OPT / "libllama-server-impl.so": "e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed",
}
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_SHA256 = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
COMMIT = "704366d"
PYTHON = Path("/usr/bin/python3")
GIT = "/usr/bin/git"
HOST_PINS = {
    "/usr/bin/python3.14": "375532f83be620283ab780c14ca6bcc5907dc379d2b621de0c5d0a112cf5458b",
    "/usr/bin/git": "2912a2a32f408c9b8122e476251b32f4b35f4c3f0c15961686ae87ca456d384c",
}
SOURCE_DIR = ".ufo/waves/round-27/sources/llama.cpp-704366d"
SOURCE_SHA256 = {
    "arg.cpp": "bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d",
    "chat-peg-parser.cpp": "895755d892a759fdf96c9c5b67202f2201228d286ddfe1b7b699d07f063cebec",
    "chat.cpp": "3793510ff80015d575777f01f9edcf8a58d859188d4f988190a02c50763bab49",
    "common.cpp": "d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4",
    "json-schema-to-grammar.cpp": "d5a82fff5d611abd1198ff27c328b20376ffe9f110b4771d579c8bd20c70541f",
    "llama-context.cpp": "2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5",
    "llama-grammar.cpp": "97d76071a2ed1b0c4ce827f002f554b12a25593776adb525dde33ac4cb1eb1e9",
    "llama-vocab.cpp": "75b8bcb686b9df653d9f3d69d8030da7da3db33a58bee127382cfc7ac05453a7",
    "sampling.cpp": "e88c45dfdc58ef2e86b5519aac68c83ced333952ade7d4bd8fca5f1ce5bbea02",
    "server-common.cpp": "b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442",
    "server-context.cpp": "dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329",
    "server-http.cpp": "24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb",
    "server-models.cpp": "9c5a6f2cc7997a3a409482c53119a2462e8c409ddf001cc568a9a8740e708b4a",
    "server-queue.cpp": "168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba",
    "server-task.cpp": "4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495",
    "server.cpp": "2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4",
}
REGISTRY = "registry/error-signatures-r27.json"
HEADING = "## Round-27 request-validation signatures"
COLUMNS = ["id", "signature", "trigger", "meaning", "next action", "source"]
ID_RE = re.compile(r"^E27-\d{2}$")
PATH_RE = re.compile(r"^/[A-Za-z0-9/_.-]*$")
ERROR_TOKENS = re.compile(
    r"throw\b|format_error_response|ERROR_TYPE_|invalid_argument|runtime_error|"
    r"->error\(|send_error|LOG_ERR|SRV_ERR|SLT_ERR|GGML_ABORT")
LITERAL_RE = re.compile(r'(?<![A-Za-z0-9_])"((?:[^"\\\n]|\\.)*)"')
PROFILES = {
    "default": [],
    "no-jinja": ["--no-jinja"],
    "embeddings": ["--embeddings"],
    "embeddings-pooling-none": ["--embeddings", "--pooling", "none"],
}
HOST = "127.0.0.1"
PORTS = range(47600, 47620)
READY_WAIT = 60.0
REQUEST_TIMEOUT = 30.0
BASELINE_REQUESTS = [
    ("GET", "/health", None),
    ("GET", "/v1/models", None),
    ("GET", "/props", None),
    ("GET", "/slots", None),
    ("POST", "/completion", {"prompt": "Once upon a time", "n_predict": 8}),
    ("POST", "/v1/chat/completions",
     {"messages": [{"role": "user", "content": "Hi"}], "max_tokens": 8}),
    ("POST", "/tokenize", {"content": "Once upon a time"}),
]
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}))


class CannotEvaluate(Exception):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def clean_env() -> dict:
    return {"PATH": "/usr/bin:/bin", "HOME": str(Path.home()), "LANG": "C.UTF-8"}


def git(repo: str, *args: str, **kw) -> subprocess.CompletedProcess:
    env = clean_env() | {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
    return subprocess.run([GIT, "--no-replace-objects", "-C", repo, *args],
                          capture_output=True, env=env, **kw)


def read_objects(repo: str, oids: list[bytes]) -> dict[bytes, tuple[bytes, bytes]]:
    """Raw objects by id; every object must hash to its id (no forged object store)."""
    p = git(repo, "cat-file", "--batch", input=b"\n".join(oids) + b"\n", timeout=600)
    if p.returncode != 0:
        raise CannotEvaluate("git cat-file at base failed")
    out, i, objs = p.stdout, 0, {}
    for oid in oids:
        nl = out.find(b"\n", i)
        head = out[i:nl].split() if nl >= 0 else []
        if len(head) != 3 or head[0] != oid:
            raise CannotEvaluate(f"base object {oid.decode()} missing")
        typ, size = head[1], int(head[2])
        body = out[nl + 1:nl + 1 + size]
        if hashlib.sha1(typ + b" %d\0" % size + body).hexdigest().encode() != oid:
            raise CannotEvaluate(f"base object {oid.decode()} fails its hash")
        objs[oid] = (typ, body)
        i = nl + 1 + size + 1
    return objs


_BASE_FILES: dict[str, dict[str, bytes]] = {}
_BASE_TEXT: dict[str, tuple[str, str]] = {}


def base_files(repo: str) -> dict[str, bytes]:
    """Every tracked blob at BASE except pinned source snapshots (paths holding
    '/sources/'), read from hash-verified commit, tree and blob objects."""
    if repo not in _BASE_FILES:
        typ, body = read_objects(repo, [BASE.encode()])[BASE.encode()]
        first = body.split(b"\n", 1)[0]
        if typ != b"commit" or not first.startswith(b"tree "):
            raise CannotEvaluate("base commit unreadable")
        r = git(repo, "ls-tree", "-r", "-t", "-z", BASE, timeout=120)
        if r.returncode != 0:
            raise CannotEvaluate("git ls-tree at base failed")
        trees, blobs = [first[5:]], []
        for rec in r.stdout.split(b"\0"):
            if not rec:
                continue
            meta, name = rec.split(b"\t", 1)
            _mode, otyp, oid = meta.split()
            if otyp == b"tree":
                trees.append(oid)
            elif otyp == b"blob" and b"/sources/" not in name:
                blobs.append((name.decode("utf-8", "replace"), oid))
        objs = read_objects(repo, trees + [oid for _, oid in blobs])
        _BASE_FILES[repo] = {name: objs[oid][1] for name, oid in blobs}
    return _BASE_FILES[repo]


def base_file(repo: str, path: str) -> str | None:
    data = base_files(repo).get(path)
    return data.decode("utf-8", "replace") if data is not None else None


def base_text(repo: str) -> tuple[str, str]:
    """Every tracked file at BASE except pinned source snapshots, concatenated:
    (lowercased text, whitespace-removed lowercased text)."""
    if repo not in _BASE_TEXT:
        text = "\n".join(d.decode("utf-8", "replace") for d in base_files(repo).values()).lower()
        _BASE_TEXT[repo] = (text, re.sub(r"\s+", "", text))
    return _BASE_TEXT[repo]


def mapped_files(pid: str) -> set[str]:
    out = set()
    for ln in Path(f"/proc/{pid}/maps").read_text("utf-8", "replace").splitlines():
        parts = ln.split(None, 5)
        if len(parts) == 6 and parts[5].startswith("/"):
            out.add(parts[5].removesuffix(" (deleted)"))
    return out


def host_integrity() -> None:
    for p, want in HOST_PINS.items():
        if not os.path.isfile(p) or sha256_file(Path(p)) != want:
            raise CannotEvaluate(f"host pin mismatch {p}")
    if os.path.realpath(sys.executable) != os.path.realpath(PYTHON) or \
            os.path.realpath(PYTHON) not in HOST_PINS or os.path.realpath(GIT) not in HOST_PINS:
        raise CannotEvaluate("interpreter or git is not the pinned host binary")
    pre = Path("/etc/ld.so.preload")
    if pre.exists() and pre.read_text("utf-8", "replace").strip():
        raise CannotEvaluate("/etc/ld.so.preload is not empty")
    stray = sorted(f for f in mapped_files("self")
                   if not f.startswith("/usr/") and f != "/etc/ld.so.cache")
    if stray:
        raise CannotEvaluate(f"counter maps files outside /usr/: {stray}")


def held_at_base(repo: str, sig: str) -> bool:
    text, folded = base_text(repo)
    forms = {sig.lower(), json.dumps(sig)[1:-1].lower(),
             json.dumps(sig, ensure_ascii=False)[1:-1].lower()}
    return any(f in text for f in forms) or any(squash(f) in folded for f in forms)


_LITERALS: dict[str, list[tuple[str, int, list[str]]]] = {}


def literal_elsewhere(lane: Path, sig: str, fname: str, line: int) -> str | None:
    """First other (file:line) of the pinned snapshot whose string literals contain sig."""
    key = str(lane)
    if key not in _LITERALS:
        idx = []
        for f in sorted(SOURCE_SHA256):
            text = (lane / SOURCE_DIR / f).read_text("utf-8", "replace").splitlines()
            for n, l in enumerate(text, 1):
                if '"' in l:
                    lits = literal_texts(l)
                    if lits:
                        idx.append((f, n, lits))
        _LITERALS[key] = idx
    for f, n, lits in _LITERALS[key]:
        if (f, n) != (fname, line) and any(sig in t for t in lits):
            return f"{f}:{n}"
    return None


def sources_rows(text: str) -> dict[str, str]:
    rows = {}
    for line in text.splitlines():
        m = re.match(r"^\|\s*(S\d{3,})\s*\|", line)
        if m:
            rows[m.group(1)] = line
    return rows


def skill_rows(text: str) -> list[str]:
    """Data rows of the first table under HEADING whose header row is exactly COLUMNS."""
    rows, inside, header_ok = [], False, None
    for line in text.splitlines():
        if line.startswith("#"):
            inside = line.startswith(HEADING)
            continue
        if not inside or not line.startswith("|"):
            continue
        cells = [" ".join(c.split()).lower() for c in line.strip().strip("|").split("|")]
        if header_ok is None:
            header_ok = cells == COLUMNS
            continue
        if header_ok and not all(set(c) <= set("-: ") for c in cells):
            rows.append(line)
    return rows


def decode_c(lit: str) -> str:
    simple = {"n": "\n", "t": "\t", "\\": "\\", '"': '"', "'": "'", "r": "\r", "0": "\0"}
    out, i = [], 0
    while i < len(lit):
        c = lit[i]
        if c == "\\" and i + 1 < len(lit):
            out.append(simple.get(lit[i + 1], "\\" + lit[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def literal_texts(line: str) -> list[str]:
    lits = [decode_c(m.group(1)) for m in LITERAL_RE.finditer(line)]
    return lits + (["".join(lits)] if len(lits) > 1 else [])


def squash(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def occurs(sig: str, text: str) -> bool:
    return sig.lower() in text.lower() or squash(sig) in squash(text)


def json_strings(value) -> list[str]:
    out = []
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        for k, v in value.items():
            out.append(str(k))
            out.extend(json_strings(v))
    elif isinstance(value, list):
        for v in value:
            out.extend(json_strings(v))
    return out


def request_surfaces(req: dict) -> list[str]:
    body = req.get("body")
    surf = [req["path"]]
    if body is not None:
        surf += json_strings(body)
        surf.append(json.dumps(body))
        surf.append(json.dumps(body, ensure_ascii=False))
    return surf


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((HOST, port)) != 0


def pick_port() -> int:
    for p in PORTS:
        if port_free(p):
            return p
    raise CannotEvaluate("no free port in 47600-47619")


def http(port: int, method: str, path: str, body) -> tuple[int, bytes]:
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}{path}", data=data, method=method)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with OPENER.open(req, timeout=REQUEST_TIMEOUT) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        return -1, repr(e).encode()


class Server:
    def __init__(self, profile: str, tmp: Path, tag: str):
        self.port = pick_port()
        self.log = tmp / f"{tag}-{profile}-{self.port}.log"
        argv = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(self.port)]
        argv += PROFILES[profile]
        self.fh = open(self.log, "wb")
        self.proc = subprocess.Popen(argv, stdout=self.fh, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True,
                                     env=clean_env())

    def ready(self) -> bool:
        end = time.time() + READY_WAIT
        while time.time() < end:
            if self.proc.poll() is not None:
                return False
            status, _ = http(self.port, "GET", "/health", None)
            if status == 200:
                try:
                    self.check_identity()
                except CannotEvaluate:
                    self.stop()
                    raise
                return True
            time.sleep(0.25)
        return False

    def check_identity(self) -> None:
        """The process answering is the one we launched, running the pinned files."""
        exe = os.path.realpath(f"/proc/{self.proc.pid}/exe")
        if exe != os.path.realpath(SERVER) or sha256_file(Path(exe)) != PINS[SERVER]:
            raise CannotEvaluate(f"launched process exe {exe} is not the pinned server")
        impl = os.path.realpath(OPT / "libllama-server-impl.so")
        maps = mapped_files(str(self.proc.pid))
        if impl not in maps:
            raise CannotEvaluate("pinned libllama-server-impl.so is not mapped")
        allowed = (os.path.realpath(OPT) + "/", "/usr/")
        stray = sorted(f for f in maps if not f.startswith(allowed)
                       and f not in (os.path.realpath(MODEL), "/etc/ld.so.cache"))
        if stray:
            raise CannotEvaluate(f"server maps files outside the pinned install: {stray}")
        raw = Path(f"/proc/{self.proc.pid}/environ").read_bytes()
        env = dict(kv.split("=", 1) for kv in raw.decode("utf-8", "replace").split("\0") if "=" in kv)
        if env != clean_env():
            raise CannotEvaluate("server environment is not the fixed environment")
        status, data = http(self.port, "GET", "/props", None)
        try:
            mp = json.loads(data.decode("utf-8")).get("model_path")
        except (UnicodeDecodeError, json.JSONDecodeError, AttributeError):
            mp = None
        if status != 200 or mp != str(MODEL):
            raise CannotEvaluate(f"/props model_path {mp!r} is not the pinned model")

    def alive(self) -> bool:
        return self.proc.poll() is None

    def stop(self) -> bool:
        if self.proc.poll() is None:
            try:
                os.killpg(self.proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(self.proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                self.proc.wait(timeout=10)
        self.fh.close()
        for _ in range(40):
            if port_free(self.port):
                return True
            time.sleep(0.25)
        return False


def run_baseline(tmp: Path) -> str:
    srv = Server("default", tmp, "baseline")
    parts = []
    try:
        if not srv.ready():
            raise CannotEvaluate("baseline server never became healthy")
        for method, path, body in BASELINE_REQUESTS:
            status, data = http(srv.port, method, path, body)
            if status != 200:
                raise CannotEvaluate(f"baseline {method} {path} -> {status}")
            parts.append(data.decode("utf-8", "replace"))
    finally:
        closed = srv.stop()
    if not closed:
        raise CannotEvaluate("baseline port did not close")
    parts.append(srv.log.read_text("utf-8", "replace"))
    for flag in ("--help", "--version"):
        r = subprocess.run([str(SERVER), flag], capture_output=True, timeout=30,
                           stdin=subprocess.DEVNULL, env=clean_env())
        text = (r.stdout + r.stderr).decode("utf-8", "replace")
        if r.returncode != 0 or not text.strip():
            raise CannotEvaluate(f"informational baseline {flag} exit {r.returncode}")
        parts.append(text)
    return "\n".join(parts)


def error_message(data: bytes) -> str | None:
    try:
        doc = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(doc, dict):
        return None
    err = doc.get("error")
    if isinstance(err, dict) and isinstance(err.get("message"), str):
        return err["message"]
    if isinstance(err, str):
        return err
    return None


def static_checks(e: dict, lane: Path, repo: str, skill: list[str],
                  src_now: dict, src_base: dict, base_seen: dict) -> list[str]:
    why = []
    rid, sig = e.get("id", ""), e.get("signature")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        why.append("bad id")
    if not isinstance(sig, str) or not sig:
        return why + ["no signature"]
    if len(sig.encode()) < MIN_BYTES or "|" in sig or "\n" in sig:
        why.append("b:short-or-bad-char")
    elif sig not in base_seen:
        base_seen[sig] = held_at_base(repo, sig)
    if base_seen.get(sig):
        why.append("b:held-at-base")
    src = e.get("source") or {}
    row, fname, line = src.get("row"), src.get("file"), src.get("line")
    req0 = e.get("request") if isinstance(e.get("request"), dict) else {}
    match = None
    for r in skill:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) != len(COLUMNS) or cells[0] != rid:
            continue
        if (sig in cells[1] and isinstance(row, str)
                and re.search(rf"\b{re.escape(row)}\b", cells[5])
                and isinstance(req0.get("path"), str) and req0["path"] in cells[2]
                and len(cells[3].split()) >= 6 and len(cells[4].split()) >= 6):
            match = cells
            break
    if match is None:
        why.append("a:no-skill-row")
    else:
        e["_next"] = " ".join(match[4].lower().split())
    srow = src_now.get(row) if isinstance(row, str) else None
    if (srow is None or row in src_base or not isinstance(fname, str)
            or fname not in srow or COMMIT not in srow or not isinstance(line, int)
            or not re.search(rf"(#L{line}\b|\bL{line}\b|line {line}\b)", srow)):
        why.append("c:no-new-sources-row")
    if fname not in SOURCE_SHA256 or not isinstance(line, int) or line < 1:
        why.append("d:unpinned-file")
    else:
        lines = (lane / SOURCE_DIR / fname).read_text("utf-8", "replace").splitlines()
        if line > len(lines):
            why.append("d:line-out-of-range")
        else:
            if not any(sig in t for t in literal_texts(lines[line - 1])):
                why.append("d:not-a-literal-on-line")
            if not any(ERROR_TOKENS.search(lines[i]) for i in range(max(0, line - 4), line)):
                why.append("d:no-error-token")
            elsewhere = literal_elsewhere(lane, sig, fname, line)
            if elsewhere:
                why.append(f"d:literal-not-unique:{elsewhere}")
    prof, req = e.get("profile"), e.get("request")
    ctl = e.get("control")
    if prof not in PROFILES:
        why.append("e:unknown-profile")
    for name, r in (("request", req), ("control", ctl)):
        if (not isinstance(r, dict) or set(r) - {"method", "path", "body"}
                or r.get("method") not in ("GET", "POST")
                or not isinstance(r.get("path"), str) or not PATH_RE.match(r["path"])
                or not (r.get("body") is None or isinstance(r.get("body"), (dict, list)))):
            why.append(f"e:bad-{name}")
    if isinstance(req, dict) and isinstance(ctl, dict) and (
            req.get("method"), req.get("path")) != (ctl.get("method"), ctl.get("path")):
        why.append("g:control-not-same-endpoint")
    if isinstance(req, dict) and isinstance(req.get("path"), str):
        if any(occurs(sig, s) for s in request_surfaces(req)):
            why.append("f:in-request")
    return why


def main() -> int:
    clean = (sys.flags.isolated and sys.flags.no_site
             and os.path.realpath(sys.executable) == os.path.realpath(PYTHON))
    if not clean:
        # run only on the pinned interpreter's own stdlib in the fixed environment:
        # no PYTHONPATH, user site, sitecustomize, LD_PRELOAD or PATH decoys
        os.execve(str(PYTHON), [str(PYTHON), "-I", "-S", os.path.abspath(__file__)]
                  + sys.argv[1:], clean_env())
    here = Path(__file__).resolve()
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=str(here.parents[3]))
    ap.add_argument("--repo", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    lane = Path(a.lane).resolve()
    repo = a.repo or str(lane)
    receipt: dict = {"schema": "kama-r27-c1-receipt/v1", "counter_sha256": sha256_file(here),
                     "lane": str(lane), "base": BASE, "target": TARGET}
    try:
        if dict(os.environ) != clean_env():
            raise CannotEvaluate("environment is not the fixed environment after re-exec")
        host_integrity()
        for p, want in PINS.items():
            if not p.is_file() or sha256_file(p) != want:
                raise CannotEvaluate(f"pin mismatch {p}")
        if not MODEL.is_file() or sha256_file(MODEL) != MODEL_SHA256:
            raise CannotEvaluate("model pin mismatch")
        for f, want in SOURCE_SHA256.items():
            p = lane / SOURCE_DIR / f
            if not p.is_file() or sha256_file(p) != want:
                raise CannotEvaluate(f"source pin mismatch {f}")
        if base_file(repo, "SKILL.md") is None:
            raise CannotEvaluate("base revision not readable")
        reg_path = lane / REGISTRY
        entries = []
        if reg_path.is_file():
            doc = json.loads(reg_path.read_text("utf-8"))
            entries = doc.get("signatures", []) if isinstance(doc, dict) else []
            if not isinstance(entries, list):
                raise CannotEvaluate("registry signatures is not a list")
        receipt["registered"] = len(entries)
        if not entries:
            receipt.update(counted=0, met=False, rows=[], not_counted=[])
            print(f"registered 0 counted 0 target {TARGET} met False not-counted []")
            return finish(receipt, a.out)
        skill_p = lane / "SKILL.md"
        skill = skill_rows(skill_p.read_text("utf-8")) if skill_p.is_file() else []
        src_p = lane / "corpus/SOURCES.md"
        src_now = sources_rows(src_p.read_text("utf-8")) if src_p.is_file() else {}
        src_base = sources_rows(base_file(repo, "corpus/SOURCES.md") or "")
        base_seen: dict = {}
        rows = []
        for e in entries:
            if not isinstance(e, dict):
                rows.append({"id": None, "why": ["not an object"]})
                continue
            rows.append({"id": e.get("id"), "entry": e,
                         "why": static_checks(e, lane, repo, skill, src_now, src_base,
                                              base_seen)})
        with tempfile.TemporaryDirectory(prefix="kama-r27-c1-") as td:
            tmp = Path(td)
            baseline = run_baseline(tmp)
            for r in rows:
                sig = (r.get("entry") or {}).get("signature")
                if isinstance(sig, str) and sig and occurs(sig, baseline):
                    r["why"].append("f:in-baseline-or-help")
            live = [r for r in rows if r.get("entry") and not any(
                w.startswith(("e:", "g:control")) or w in ("bad id", "no signature")
                for w in r["why"])]
            for prof in PROFILES:
                todo = [r for r in live if r["entry"]["profile"] == prof]
                srv = None
                for r in todo:
                    e = r["entry"]
                    if srv is None or not srv.alive():
                        if srv is not None:
                            r.setdefault("notes", []).append("server restarted")
                            srv.stop()
                        srv = Server(prof, tmp, "rows")
                        if not srv.ready():
                            r["why"].append("e:profile-not-ready")
                            srv.stop()
                            srv = None
                            continue
                    c = e["control"]
                    cs, cb = http(srv.port, c["method"], c["path"], c.get("body"))
                    q = e["request"]
                    qs, qb = http(srv.port, q["method"], q["path"], q.get("body"))
                    msg = error_message(qb)
                    r["live"] = {"profile": prof, "control_status": cs,
                                 "control_sha256": hashlib.sha256(cb).hexdigest(),
                                 "status": qs, "message": msg,
                                 "body_sha256": hashlib.sha256(qb).hexdigest()}
                    if not (200 <= cs < 300) or occurs(e["signature"], cb.decode("utf-8", "replace")):
                        r["why"].append("g:control-failed")
                    if qs < 400 or msg is None or e["signature"] not in msg:
                        r["why"].append("e:not-shown")
                if srv is not None:
                    if not srv.stop():
                        raise CannotEvaluate(f"port {srv.port} did not close")
        counted, seen = [], []
        for r in rows:
            if r["why"]:
                continue
            e, msg = r["entry"], r["live"]["message"]
            key = (e["source"]["file"], e["source"]["line"])
            canon = json.dumps(e["request"], sort_keys=True)
            clash = None
            for o in seen:
                oe, om = o["entry"], o["live"]["message"]
                if key == (oe["source"]["file"], oe["source"]["line"]):
                    clash = "h:same-source-line"
                elif e["signature"] in oe["signature"] or oe["signature"] in e["signature"]:
                    clash = "h:sub-or-superstring"
                elif oe["signature"] in msg or e["signature"] in om:
                    clash = "h:shared-message"
                elif (fr := msg.replace(e["signature"], "\0").lower()).strip("\0 ") and \
                        fr == om.replace(oe["signature"], "\0").lower():
                    clash = "h:same-message-frame"
                elif canon == json.dumps(oe["request"], sort_keys=True):
                    clash = "h:same-request"
                elif e["_next"] == oe["_next"]:
                    clash = "h:same-next-action"
                elif e["source"]["row"] == oe["source"]["row"]:
                    clash = "h:same-sources-row"
                if clash:
                    break
            if clash:
                r["why"].append(clash)
            else:
                seen.append(r)
                counted.append(r["id"])
        not_counted = [r["id"] for r in rows if r["why"]]
        receipt.update(counted=len(counted), met=len(counted) >= TARGET,
                       counted_ids=counted, not_counted=not_counted,
                       rows=[{k: v for k, v in r.items() if k != "entry"} | {
                           "signature": (r.get("entry") or {}).get("signature")} for r in rows])
        print(f"registered {len(entries)} counted {len(counted)} target {TARGET} "
              f"met {len(counted) >= TARGET} not-counted {not_counted}")
        return finish(receipt, a.out)
    except CannotEvaluate as ex:
        receipt["could_not_evaluate"] = str(ex)
        print(f"could-not-evaluate: {ex}", file=sys.stderr)
        finish(receipt, a.out)
        return 2


def finish(receipt: dict, out: str | None) -> int:
    if out:
        Path(out).write_text(json.dumps(receipt, indent=1, sort_keys=True) + "\n", "utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
