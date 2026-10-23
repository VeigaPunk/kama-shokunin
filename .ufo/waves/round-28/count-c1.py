#!/usr/bin/env python3
"""Round-28 C1 counter (depth): llama-server b11755 request-field outcomes in SKILL.md.

Frozen predicate, amendment A1 (the same sentence as preregistration.json C1.predicate and the
label `counted` in the receipt):

  A registry row is COUNTED iff
  (a) the first table of the SKILL.md section whose heading starts with
      "## Round-28 request-field outcomes" has the header
      `| id | field | value | outcome | meaning | source |`, and one of its rows
      has exactly these six cells with: id = the registry id; the field cell
      holding the registry field verbatim; the value cell holding the canonical
      JSON of the registry value verbatim; the outcome cell holding the row's
      canonical outcome text verbatim; a meaning cell of at least six words; the
      source cell holding the registry S### token;
  (b) the registry `set` object has exactly one key, equal to the field; the
      cited line of the sha256-pinned 704366d `server-schema.cpp` snapshot
      declares that field (`new field_` and one string literal equal to the
      field), and no other registry row cites the same line or the same field
      (a duplicated line or field voids every row that shares it);
  (c) its S### row exists in corpus/SOURCES.md of the measured tree, does not
      exist at base 4179301f, and names `server-schema.cpp`, the cited line (as
      "L<line>" or "line <line>") and commit 704366d;
  (d) the counter's own run of the pinned llama-server (default argv, pinned
      binary, library and model, fixed environment, same process identity
      checks as round 27) answers POST /completion with body
      {"prompt": "Once upon a time", "n_predict": 1} updated with `set` as
      the row's outcome says: kind `reject` -> status 400 and an error message
      matching `Field '<field>': Value must be between A <= value <= B, but got`
      with A and B numerically equal (float32 tolerance) to the row's bounds;
      kind `effective` -> status 200 and `generation_settings[<key>]` equal
      (float32 tolerance for numbers, exact otherwise) to the row's value;
  (e) source-blind outcomes are not counted: for an `effective` row the live
      value differs from the requested value, from the live value of the
      same key when the field is omitted (the counter's own base request),
      and from every generic conversion of the requested value (amendment
      A1): float32 rounding, float32 saturation to +-3.4028234663852886e38 or
      +-infinity, truncation toward zero, wrap modulo 2^32 or 2^64 (signed or
      unsigned) and truthiness.

Claim met iff counted >= 18 (preregistration.json C1.target).

Not checked by this counter (reviewed per row, never counted): whether the
meaning prose is correct beyond its word count.

Usage: count-c1.py [--lane DIR] [--repo GITDIR] [--out FILE]
Exit: 0 ran (whatever the count), 2 could not evaluate (pins, process
identity, unsafe port, base request failed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "4179301f7516ad667509d54b5ebfe0a70a002d5b"
TARGET = 18
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
SOURCE_DIR = ".ufo/waves/round-28/sources/llama.cpp-704366d"
SCHEMA_FILE = "server-schema.cpp"
SOURCE_SHA256 = {
    "server-schema.cpp": "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050",
}
REGISTRY = "registry/request-field-outcomes-r28.json"
HEADING = "## Round-28 request-field outcomes"
COLUMNS = ["id", "field", "value", "outcome", "meaning", "source"]
ID_RE = re.compile(r"^F28-\d{2}$")
LITERAL_RE = re.compile(r'(?<![A-Za-z0-9_])"((?:[^"\\\n]|\\.)*)"')
REJECT_RE = re.compile(
    r"Field '([^']*)': Value must be between (\S+) <= value <= (\S+), but got")
HOST = "127.0.0.1"
PORTS = range(47600, 47620)
READY_WAIT = 60.0
REQUEST_TIMEOUT = 30.0
BASE_PATH = "/completion"
BASE_BODY = {"prompt": "Once upon a time", "n_predict": 1}
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


def base_sources(repo: str) -> tuple[str, list[str]]:
    """(corpus/SOURCES.md at BASE, every tracked path at BASE), from hash-verified objects."""
    typ, body = read_objects(repo, [BASE.encode()])[BASE.encode()]
    first = body.split(b"\n", 1)[0]
    if typ != b"commit" or not first.startswith(b"tree "):
        raise CannotEvaluate("base commit unreadable")
    r = git(repo, "ls-tree", "-r", "-t", "-z", BASE, timeout=120)
    if r.returncode != 0:
        raise CannotEvaluate("git ls-tree at base failed")
    trees, paths, src_oid = [first[5:]], [], None
    for rec in r.stdout.split(b"\0"):
        if not rec:
            continue
        meta, name = rec.split(b"\t", 1)
        _mode, otyp, oid = meta.split()
        if otyp == b"tree":
            trees.append(oid)
        elif otyp == b"blob":
            paths.append(name.decode("utf-8", "replace"))
            if name == b"corpus/SOURCES.md":
                src_oid = oid
    objs = read_objects(repo, trees + ([src_oid] if src_oid else []))
    text = objs[src_oid][1].decode("utf-8", "replace") if src_oid else ""
    return text, paths


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


def literals(line: str) -> list[str]:
    return [decode_c(m.group(1)) for m in LITERAL_RE.finditer(line)]


def canon(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def is_num(v) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def same(a, b) -> bool:
    """Numbers: float32 tolerance; everything else: exact JSON equality."""
    if is_num(a) and is_num(b):
        if math.isinf(a) or math.isinf(b) or math.isnan(a) or math.isnan(b):
            return a == b
        return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))
    return canon(a) == canon(b)


def outcome_text(o) -> str | None:
    """Canonical outcome cell text, or None when the outcome object is malformed."""
    if not isinstance(o, dict):
        return None
    if o.get("kind") == "reject":
        b = o.get("bounds")
        if (isinstance(b, list) and len(b) == 2 and all(is_num(x) for x in b)
                and set(o) == {"kind", "bounds"}):
            return f"reject 400, bounds {canon(b[0])} to {canon(b[1])}"
        return None
    if o.get("kind") == "effective":
        k = o.get("key")
        if isinstance(k, str) and k and "value" in o and set(o) == {"kind", "key", "value"}:
            return f"200, {k} = {canon(o['value'])}"
        return None
    return None


FLT_MAX = 3.4028234663852886e38


def conversions(sent) -> list:
    """Generic conversions a typed field applies to any value (A1): never field knowledge."""
    if isinstance(sent, bool) or not is_num(sent):
        return []
    out = [bool(sent)]
    if math.isnan(sent):
        return out
    if math.isinf(sent) or abs(sent) > FLT_MAX:
        out += [math.copysign(FLT_MAX, sent), math.copysign(math.inf, sent)]
    if math.isinf(sent):
        return out
    try:
        out.append(struct.unpack("f", struct.pack("f", sent))[0])
    except (OverflowError, struct.error):
        pass
    t = int(sent)
    out.append(t)
    for bits in (32, 64):
        m = 1 << bits
        out += [t % m, (t + (m >> 1)) % m - (m >> 1)]
    return out


def lookup(gs, key: str):
    """generation_settings[key]: the flat key, else a dotted path."""
    if not isinstance(gs, dict):
        return False, None
    if key in gs:
        return True, gs[key]
    cur = gs
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


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
    def __init__(self, tmp: Path, tag: str):
        self.port = pick_port()
        self.log = tmp / f"{tag}-{self.port}.log"
        cwd = tmp / "cwd"
        cwd.mkdir(exist_ok=True)
        argv = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(self.port)]
        self.fh = open(self.log, "wb")
        self.proc = subprocess.Popen(argv, stdout=self.fh, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, start_new_session=True,
                                     env=clean_env(), cwd=str(cwd))

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


def parse_json(data: bytes):
    try:
        return json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None


def error_message(doc) -> str | None:
    if not isinstance(doc, dict):
        return None
    err = doc.get("error")
    if isinstance(err, dict) and isinstance(err.get("message"), str):
        return err["message"]
    if isinstance(err, str):
        return err
    return None


def static_checks(e: dict, lane: Path, skill: list[str], src_now: dict,
                  src_base: dict) -> list[str]:
    why = []
    rid, field = e.get("id", ""), e.get("field")
    if not isinstance(rid, str) or not ID_RE.match(rid):
        why.append("bad id")
    if not isinstance(field, str) or not field or "|" in field:
        return why + ["b:no-field"]
    st = e.get("set")
    if not (isinstance(st, dict) and list(st) == [field]):
        why.append("b:set-not-one-key-equal-to-field")
        value_text = None
    else:
        value_text = canon(st[field])
    otext = outcome_text(e.get("outcome"))
    if otext is None:
        why.append("d:bad-outcome")
    src = e.get("source") or {}
    row, fname, line = src.get("row"), src.get("file"), src.get("line")
    match = None
    for r in skill:
        cells = [c.strip() for c in r.strip().strip("|").split("|")]
        if len(cells) != len(COLUMNS) or cells[0] != rid:
            continue
        if (field in cells[1] and value_text is not None and value_text in cells[2]
                and otext is not None and otext in cells[3]
                and len(cells[4].split()) >= 6 and isinstance(row, str)
                and re.search(rf"\b{re.escape(row)}\b", cells[5])):
            match = cells
            break
    if match is None:
        why.append("a:no-skill-row")
    srow = src_now.get(row) if isinstance(row, str) else None
    if (srow is None or row in src_base or fname != SCHEMA_FILE or SCHEMA_FILE not in srow
            or COMMIT not in srow or not isinstance(line, int)
            or not re.search(rf"(#L{line}\b|\bL{line}\b|line {line}\b)", srow)):
        why.append("c:no-new-sources-row")
    if fname != SCHEMA_FILE or not isinstance(line, int) or line < 1:
        why.append("b:not-schema-file")
    else:
        lines = (lane / SOURCE_DIR / SCHEMA_FILE).read_text("utf-8", "replace").splitlines()
        if line > len(lines):
            why.append("b:line-out-of-range")
        else:
            text = lines[line - 1]
            if "new field_" not in text or field not in literals(text):
                why.append("b:line-does-not-declare-field")
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
    receipt: dict = {"schema": "kama-r28-c1-receipt/v1-A1", "counter_sha256": sha256_file(here),
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
        base_src_text, base_paths = base_sources(repo)
        receipt["schema_file_at_base"] = sorted(p for p in base_paths
                                                if p.endswith("/" + SCHEMA_FILE) or p == SCHEMA_FILE)
        reg_path = lane / REGISTRY
        entries = []
        if reg_path.is_file():
            doc = json.loads(reg_path.read_text("utf-8"))
            entries = doc.get("rows", []) if isinstance(doc, dict) else []
            if not isinstance(entries, list):
                raise CannotEvaluate("registry rows is not a list")
        receipt["registered"] = len(entries)
        if not entries:
            receipt.update(counted=0, met=False, rows=[], not_counted=[])
            print(f"registered 0 counted 0 target {TARGET} met False not-counted []")
            return finish(receipt, a.out)
        skill_p = lane / "SKILL.md"
        skill = skill_rows(skill_p.read_text("utf-8")) if skill_p.is_file() else []
        src_p = lane / "corpus/SOURCES.md"
        src_now = sources_rows(src_p.read_text("utf-8")) if src_p.is_file() else {}
        src_base = sources_rows(base_src_text)
        rows = []
        for e in entries:
            if not isinstance(e, dict):
                rows.append({"id": None, "why": ["not an object"]})
                continue
            rows.append({"id": e.get("id"), "entry": e,
                         "why": static_checks(e, lane, skill, src_now, src_base)})
        # (b) one registered row per cited line and per field
        by_line: dict = {}
        by_field: dict = {}
        for r in rows:
            e = r.get("entry")
            if not e:
                continue
            s = e.get("source") or {}
            by_line.setdefault((s.get("file"), s.get("line")), []).append(r)
            by_field.setdefault(e.get("field"), []).append(r)
        for group in list(by_line.values()) + list(by_field.values()):
            if len(group) > 1:
                for r in group:
                    if "b:duplicate-line-or-field" not in r["why"]:
                        r["why"].append("b:duplicate-line-or-field")
        live = [r for r in rows if r.get("entry") and not any(
            w in ("bad id", "b:no-field", "b:set-not-one-key-equal-to-field", "d:bad-outcome")
            for w in r["why"])]
        with tempfile.TemporaryDirectory(prefix="kama-r28-c1-") as td:
            tmp = Path(td)
            srv = None
            base_gs = None
            try:
                for r in live:
                    e = r["entry"]
                    if srv is None or not srv.alive():
                        if srv is not None:
                            r.setdefault("notes", []).append("server restarted")
                            srv.stop()
                        srv = Server(tmp, "rows")
                        if not srv.ready():
                            raise CannotEvaluate("server never became healthy")
                        bs, bb = http(srv.port, "POST", BASE_PATH, BASE_BODY)
                        bdoc = parse_json(bb)
                        if bs != 200 or not isinstance(bdoc, dict) or \
                                not isinstance(bdoc.get("generation_settings"), dict):
                            raise CannotEvaluate(f"base request -> {bs}")
                        if base_gs is None:
                            base_gs = bdoc["generation_settings"]
                            receipt["base_request_sha256"] = hashlib.sha256(bb).hexdigest()
                    body = dict(BASE_BODY)
                    body.update(e["set"])
                    qs, qb = http(srv.port, "POST", BASE_PATH, body)
                    doc = parse_json(qb)
                    o = e["outcome"]
                    lv = {"status": qs, "body_sha256": hashlib.sha256(qb).hexdigest()}
                    if o["kind"] == "reject":
                        msg = error_message(doc)
                        lv["message"] = msg
                        m = REJECT_RE.search(msg or "")
                        ok = False
                        if qs == 400 and m and m.group(1) == e["field"]:
                            try:
                                lo, hi = float(m.group(2)), float(m.group(3))
                                ok = same(lo, o["bounds"][0]) and same(hi, o["bounds"][1])
                            except ValueError:
                                ok = False
                        if not ok:
                            r["why"].append("d:not-shown")
                    else:
                        gs = doc.get("generation_settings") if isinstance(doc, dict) else None
                        found, val = lookup(gs, o["key"])
                        lv["effective"] = val if found else None
                        if qs != 200 or not found or not same(val, o["value"]):
                            r["why"].append("d:not-shown")
                        else:
                            bfound, bval = lookup(base_gs, o["key"])
                            lv["base_effective"] = bval if bfound else None
                            sent = e["set"][e["field"]]
                            if same(val, sent):
                                r["why"].append("e:identity")
                            elif any(same(val, c) for c in conversions(sent)):
                                r["why"].append("e:generic-conversion")
                            if bfound and same(val, bval):
                                r["why"].append("e:default")
                    r["live"] = lv
            finally:
                if srv is not None and not srv.stop():
                    raise CannotEvaluate(f"port {srv.port} did not close")
        counted = [r["id"] for r in rows if not r["why"]]
        not_counted = [r["id"] for r in rows if r["why"]]
        receipt.update(counted=len(counted), met=len(counted) >= TARGET,
                       counted_ids=counted, not_counted=not_counted,
                       rows=[{k: v for k, v in r.items() if k != "entry"} for r in rows])
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
