#!/usr/bin/env python3
"""Round 25 C2 counting command (registered by preregistration amendment 2,
made stricter by amendments 3 and 4).

Amendment 4 registers the stricter counter proposed by wave-1 critic seat
CriticC2SizingA2 (.ufo/waves/round-25/a2-build/out/CriticC2SizingA2/): the
5388b7c bytes with only stricter checks (each change shrinks the accepted
set): positive integers; one /slots entry per slot; the recorded argv ends
with the registered args and carries the launch flags including -v; the pool
equals the last `llama_context: n_ctx = N` line; an `n_slots ... kv_unified`
startup line; load cells have exactly two requests with HTTP status 100-599,
integer token counts, start and end times, and overlap if and only if the
mode is concurrent; exact build and commit binding.

Counts the registered context-capacity cells that the committed receipt
observed. A cell counts only when its id and args equal the registered cell,
its id occurs once in the receipt, and every required field is present with
the required type. Truthy strings, duplicate ids and extra cells never count.
The receipt-level binding (llama-server build 11755, fixture sha256) is
printed separately and must be True for the claim value to stand.

Round-26 repair (routed defect 5): binding also requires every cell's `raw`
to be a non-empty object whose values each equal the sha256 of the file the
receipt schema assigns it under .ufo/waves/round-25/final/raw/
(`<id>.health.body`, `<id>.models.body`, `<id>.props.body`, `<id>.slots.body`
and `<id>.server.log`, per tools/kama-context-capacity.py). A missing file,
a hash that matches no such file, a hash that matches a different cell's
file, a missing or empty `raw`, or a non-string value never binds. An
unregistered `raw` key binds only when its value equals some file's sha256.

Round-28 repair (routed defect 1 of the round-27 verifier spot-check; open
since round-25 defect 5 and round-26 defect 8): every per-cell value this
counter reports -- props n_ctx, total slots, per-slot n_ctx, model
n_ctx_train, the KV pool and its candidate lines, the kept log lines and the
load-request outcomes (prompt tokens, HTTP outcome, error text, truncation,
concurrency) -- is recomputed from the raw bytes the cell's `raw` hashes
bind, never read from the receipt's cell fields. The derivations mirror
tools/kama-context-capacity.py: /props default_generation_settings.n_ctx and
total_slots; every /slots entry n_ctx; /v1/models data[0].meta.n_ctx_train;
the last `llama_context: n_ctx = N` line of the server log; the log lines
matching the claim-named set; and for load cells the `new prompt` task lines
(task.n_tokens, start order), `srv send_error: task id = N` (HTTP 500 with
that message) and `slot release: ... stop processing: n_tokens = M,
truncated = F` (HTTP 200, truncated flag), with concurrent mode iff the
second request starts before the first ends. A cell whose receipt values
disagree with its raw bytes, or whose raw bytes are missing or do not match
the bound sha256, is not observed and the receipt does not bind. Absolute
request timestamps and the launch argv are not recoverable from the
committed bytes; the timestamps stay a receipt-internal consistency check
and both requests' overlap must equal the raw-derived mode. `n_predict` is
the registered request constant. A forgery that rewrites a raw file, its
receipt hash and the matching cell fields together is indistinguishable
from genuine data without an external anchor; the counter binds receipt to
raw, not raw to the server.

Usage: python3 .ufo/waves/round-25/count-c2.py [receipt.json]
Prints: registered N observed M bound B
Exit 0 always when the receipt parses; exit 2 when it cannot be read.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

RECEIPT = ".ufo/waves/round-25/final/context-capacity-receipt.json"
RAW_DIR = Path(__file__).resolve().parent / "final" / "raw"
RAW_FILES = {"raw_health": "health.body", "raw_models": "models.body",
             "raw_props": "props.body", "raw_slots": "slots.body",
             "server_log": "server.log"}
MODEL_SHA = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
LOAD_REQUEST = {"prompt_tokens": 1000, "n_predict": 600}
CELLS = {
    "K1": ("-c 0", "config"),
    "K2": ("-c 2048 -np 2 --no-kv-unified", "config"),
    "K3": ("-c 2048 -np 2 --kv-unified", "config"),
    "K4": ("-c 1024 -np 1", "config"),
    "K5": ("-c 4096 -np 1", "config"),
    "K6": ("-c 1000 -np 3 --no-kv-unified", "config"),
    "K7": ("-np 2 --kv-unified-per-slot 512", "config"),
    "K8": ("-c 4096 -np 4 --kv-unified --kv-unified-per-slot 512", "config"),
    "X1": ("-np 4 --no-kv-unified", "config"),
    "X2": ("-c 8192 -np 4 --no-kv-unified", "config"),
    "X3": ("-np 4 --no-kv-unified --fit off", "config"),
    "L1": ("-c 0", "load-concurrent"),
    "L2": ("-c 8192 -np 4 --no-kv-unified", "load-concurrent"),
    "L3": ("-c 0", "load-sequential"),
}


BUILD = re.compile(r"\(build 11755, commit 704366d76\)")
POOL = re.compile(r"\bllama_context: n_ctx +=  ?(\d+)\s*$")
SLOT = re.compile(r"n_slots = \d+, n_ctx_slot = \d+, kv_unified = '(true|false)'")
LAUNCH = ["--host", "127.0.0.1", "--no-webui", "--offline", "-v"]

# Raw derivations, byte-for-byte the extraction rules of
# tools/kama-context-capacity.py (extract_log_lines, extract_kv_pool) plus
# the load-request lifecycle lines the tool records in `requests`.
LOG_KEEP = re.compile(
    r"n_ctx|kv_unified|n_seq|capping|rounding|KV pool|llama_kv_cache: size",
    re.IGNORECASE)
KV_POOL_RE = re.compile(r"llama_context: n_ctx\s*=\s*(\d+)")
NEW_PROMPT = re.compile(
    r"slot\s+operator\(\): id\s+\d+ \| task (\d+) \| new prompt, "
    r"n_ctx_slot = \d+, n_keep = \d+, task\.n_tokens = (\d+)")
RELEASE = re.compile(
    r"slot\s+release: id\s+\d+ \| task (\d+) \| stop processing: "
    r"n_tokens = (\d+), truncated = (\d+)")
SEND_ERROR = re.compile(r"srv\s+send_error: task id = (\d+), error: (.*)")

RAW_KEYS = ("props_n_ctx", "total_slots", "slots_n_ctx",
            "models_n_ctx_train", "kv_pool_candidates", "kv_pool_n_ctx",
            "log_lines")


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def pos(v):
    return is_int(v) and v > 0


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def raw_hashes():
    """sha256 of every regular file under RAW_DIR, by file name."""
    files = {}
    if not RAW_DIR.is_dir():
        return files
    try:
        for p in RAW_DIR.iterdir():
            if p.is_file():
                files[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    except OSError:
        return {}
    return files


def cell_raw_bound(c, files):
    """True iff this cell's `raw` sha256 values match files in RAW_DIR.

    Each known raw key must equal the sha256 of its own file
    (`<id>.<suffix>`); any other key must equal some file's sha256.
    """
    raw = c.get("raw")
    if not isinstance(raw, dict) or not raw:
        return False
    by_hash = set(files.values())
    for key, val in raw.items():
        if not isinstance(val, str):
            return False
        suffix = RAW_FILES.get(key)
        if suffix is not None:
            if val != files.get(f"{c.get('id')}.{suffix}"):
                return False
        elif val not in by_hash:
            return False
    return True


def raw_bound(cells, files=None):
    """True iff every cell's raw sha256 values match files in RAW_DIR."""
    files = raw_hashes() if files is None else files
    if not files:
        return False
    for c in cells:
        if not isinstance(c, dict):
            continue
        if not cell_raw_bound(c, files):
            return False
    return True


def _tuple(o):
    return (o.get("prompt_tokens"), o.get("status"), o.get("error"),
            o.get("truncated"))


def request_outcomes(text):
    """Recompute the two load requests from the server log.

    Each request is a `slot operator(): ... new prompt ... task.n_tokens = N`
    line. Its outcome is the `srv send_error: task id = N` line (HTTP 500
    with that message) or the `slot release: ... stop processing: n_tokens =
    M, truncated = F` line (HTTP 200, truncated flag); no terminal line
    leaves the outcome unknown. The mode is concurrent iff the second
    request starts before the first ends. Returns (outcomes, mode); mode is
    None unless exactly two distinct tasks start and both reach a terminal
    line.
    """
    starts = []
    ends = {}
    errors = {}
    for m in NEW_PROMPT.finditer(text):
        starts.append((m.start(), int(m.group(1)), int(m.group(2))))
    for m in RELEASE.finditer(text):
        ends.setdefault(int(m.group(1)),
                        (m.start(), int(m.group(2)), int(m.group(3))))
    for m in SEND_ERROR.finditer(text):
        errors.setdefault(int(m.group(1)), (m.start(), m.group(2).strip()))
    starts.sort()
    tasks = [task for _, task, _ in starts]
    if len(tasks) != 2 or len(set(tasks)) != 2:
        return [], None
    outcomes = []
    for _, task, tokens in starts:
        end = ends.get(task)
        err = errors.get(task)
        if err is not None:
            outcomes.append({"prompt_tokens": tokens, "status": 500,
                             "error": err[1], "truncated": None})
        elif end is not None:
            outcomes.append({"prompt_tokens": tokens, "status": 200,
                             "error": None, "truncated": bool(end[2])})
        else:
            return [], None
    terminal = [p for p in (errors.get(starts[0][1], (None,))[0],
                            ends.get(starts[0][1], (None,))[0]) if p is not None]
    mode = None
    if terminal:
        mode = "concurrent" if starts[1][0] < min(terminal) else "sequential"
    return outcomes, mode


def derive_cell(cid):
    """Recompute every value the committed raw bytes determine for cid.

    Returns a dict of raw-derived values, or None when a required raw file
    is missing, unreadable, or not the shape the receipt schema claims. The
    caller compares every key with the receipt cell, so a raw file with a
    different value than the receipt makes that cell unobserved.
    """
    if not isinstance(cid, str) or not cid or "/" in cid or cid in (".", ".."):
        return None
    try:
        props_b = (RAW_DIR / f"{cid}.props.body").read_bytes()
        slots_b = (RAW_DIR / f"{cid}.slots.body").read_bytes()
        models_b = (RAW_DIR / f"{cid}.models.body").read_bytes()
        log_b = (RAW_DIR / f"{cid}.server.log").read_bytes()
    except OSError:
        return None
    if not log_b:
        return None
    try:
        props = json.loads(props_b.decode("utf-8"))
        slots = json.loads(slots_b.decode("utf-8"))
        models = json.loads(models_b.decode("utf-8"))
    except (UnicodeDecodeError, ValueError):
        return None
    props_n_ctx = None
    total_slots = None
    if isinstance(props, dict):
        dgs = props.get("default_generation_settings")
        if isinstance(dgs, dict):
            props_n_ctx = dgs.get("n_ctx")
        total_slots = props.get("total_slots")
    slots_n_ctx = None
    if isinstance(slots, list):
        slots_n_ctx = [e.get("n_ctx") for e in slots
                       if isinstance(e, dict) and is_int(e.get("n_ctx"))]
    models_n_ctx_train = None
    if isinstance(models, dict):
        data = models.get("data")
        if isinstance(data, list) and data and isinstance(data[0], dict):
            meta = data[0].get("meta")
            if isinstance(meta, dict):
                models_n_ctx_train = meta.get("n_ctx_train")
    text = log_b.decode("utf-8", errors="replace")
    pools = [int(m.group(1)) for m in KV_POOL_RE.finditer(text)]
    derived = {
        "props_n_ctx": props_n_ctx,
        "total_slots": total_slots,
        "slots_n_ctx": slots_n_ctx,
        "models_n_ctx_train": models_n_ctx_train,
        "kv_pool_candidates": pools,
        "kv_pool_n_ctx": pools[-1] if pools else None,
        "log_lines": [ln for ln in text.splitlines() if LOG_KEEP.search(ln)],
    }
    derived["requests"], derived["request_mode"] = request_outcomes(text)
    return derived


def cell_matches_raw(c, derived):
    """True iff every raw-derived value equals the receipt cell's value."""
    if derived is None:
        return False
    for key in RAW_KEYS:
        if c.get(key) != derived[key]:
            return False
    if c.get("request_mode") != derived.get("request_mode"):
        return False
    requests = c.get("requests")
    if not isinstance(requests, list):
        return False
    got = [_tuple(q) if isinstance(q, dict) else None for q in requests]
    want = [_tuple(q) for q in derived.get("requests") or []]
    if any(x is None for x in got):
        return False
    return sorted(got, key=repr) == sorted(want, key=repr)


def cell_ok(c, kind):
    if not (pos(c.get("props_n_ctx")) and pos(c.get("total_slots"))
            and pos(c.get("models_n_ctx_train"))
            and pos(c.get("kv_pool_n_ctx"))):
        return False
    s = c.get("slots_n_ctx")
    if not (isinstance(s, list) and len(s) == c["total_slots"]
            and all(pos(x) for x in s)):
        return False
    argv = c.get("argv")
    if not (isinstance(argv, list) and all(isinstance(x, str) for x in argv)
            and argv[-len(c["args"].split()):] == c["args"].split()
            and all(x in argv for x in LAUNCH)):
        return False
    lines = c.get("log_lines")
    if not (isinstance(lines, list) and lines
            and all(isinstance(x, str) and x for x in lines)):
        return False
    pools = [int(m.group(1)) for m in map(POOL.search, lines) if m]
    if not (pools and pools[-1] == c["kv_pool_n_ctx"]):
        return False
    if not any(SLOT.search(x) for x in lines):
        return False
    if kind.startswith("load"):
        want = "sequential" if kind == "load-sequential" else "concurrent"
        if c.get("request_mode") != want:
            return False
        r = c.get("requests")
        if not (isinstance(r, list) and len(r) == 2):
            return False
        for q in r:
            if not (isinstance(q, dict) and is_int(q.get("status"))
                    and 100 <= q["status"] <= 599
                    and is_int(q.get("prompt_tokens"))
                    and q["prompt_tokens"] == LOAD_REQUEST["prompt_tokens"]
                    and is_int(q.get("n_predict"))
                    and q["n_predict"] == LOAD_REQUEST["n_predict"]
                    and is_num(q.get("t_start")) and is_num(q.get("t_end"))
                    and q["t_start"] < q["t_end"]):
                return False
        overlap = max(q["t_start"] for q in r) < min(q["t_end"] for q in r)
        if overlap != (want == "concurrent"):
            return False
    return True


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else RECEIPT
    try:
        d = json.load(open(path))
    except (OSError, ValueError) as exc:
        print(f"cannot read receipt: {exc}", file=sys.stderr)
        return 2
    cells = d.get("cells") if isinstance(d, dict) else None
    cells = cells if isinstance(cells, list) else []
    ids = [c.get("id") for c in cells if isinstance(c, dict)]
    files = raw_hashes()
    derived = [(c, derive_cell(c.get("id")))
               for c in cells if isinstance(c, dict)]
    observed = []
    for c, raw in derived:
        cid = c.get("id")
        if not isinstance(cid, str) or cid not in CELLS or ids.count(cid) != 1:
            continue
        args, kind = CELLS[cid]
        if (c.get("args") == args and cell_raw_bound(c, files)
                and cell_matches_raw(c, raw) and cell_ok(c, kind)):
            observed.append(cid)
    ver = d.get("server_version") if isinstance(d, dict) else None
    sha = d.get("model_sha256") if isinstance(d, dict) else None
    bound = (isinstance(ver, str) and bool(BUILD.search(ver)) and sha == MODEL_SHA
             and all(c.get(k, v) == v for c in cells if isinstance(c, dict)
                     for k, v in (("server_version", ver),
                                  ("model_sha256", sha)))
             and raw_bound(cells, files)
             and bool(derived)
             and all(cell_matches_raw(c, raw) for c, raw in derived))
    missing = [k for k in CELLS if k not in observed]
    print("registered", len(CELLS), "observed", len(observed), "bound", bound,
          "missing", missing)
    return 0


if __name__ == "__main__":
    sys.exit(main())
