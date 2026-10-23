#!/usr/bin/env python3
"""Round-31 C1 counter (depth): llama-server b11755 /v1/chat/completions parameter outcomes.

Frozen predicate (the same sentence as preregistration.json C1.predicate and the summary label
`counted`):

  Claim met iff counted >= 12.

A registry row of registry/chat-param-outcomes-r31.json (`rows`) is COUNTED iff all of:
(a) its `id` is unique in the registry; `param` is a nonempty string; `sent` is any JSON value
    (null allowed only when `also` carries the payload); `outcome.kind` is one of
    reject|slot|ignored|response;
(b) SKILL.md at the tip contains a section whose heading starts with
    "## Round-31 chat-completions parameter outcomes", and the first table of that section has the
    header exactly `| id | param | sent | outcome | meaning | source |`, and one of its rows has
    exactly these six cells with: the cell `id` equal to the registry id; `param` equal to the
    registry param; `sent` equal to the canonical JSON of the registry `sent`; `outcome` equal to
    the counter's rendering of the registry outcome (see RENDER below); a `meaning` cell of at
    least eight whitespace-separated words; `source` equal to the registry source row id.
(c) the source row exists in corpus/SOURCES.md at the tip, does not exist at the base commit,
    contains the pinned file name, "L<line>" or "line <line>", and the string 704366d; and the
    sha256-pinned snapshot of that file at that line contains the row's `source.contains`
    substring verbatim.
(d) live: the counter starts its own pinned server (binary, library and model sha256 checked;
    default argv `-m <model> --host 127.0.0.1 --port <port>`), issues the base request, then the
    row request (base body, then {param: sent}, then `also` merged), and observes:
      reject   -> HTTP status equals outcome.status; the error object's key set is exactly
                  {code,message,type}; error.code equals the status; error.type equals
                  outcome.type; error.message equals outcome.message byte for byte.
      slot     -> HTTP 200; every key of outcome.set is present in the newest slot's `params`
                  and equals its value (float32 tolerance for numbers).
      response -> HTTP 200 and the named check holds: n_choices (len(choices)), has_logprobs
                  (choices[0].logprobs is not null), sse (the body holds >=1 `data: ` line, a
                  `data: [DONE]` line and at least one non-DONE JSON frame), sse_usage (some
                  non-DONE frame carries a non-empty `usage` object).
      ignored  -> HTTP 200; the newest slot's full `params` object equals the base request's
                  (float32 tolerance, same key set); and the normalized response equals the
                  base's, where normalized = {top_keys, n_choices, choice_keys, has_logprobs,
                  usage_keys, prompt_tokens}.
(e) discrimination (KQ38; a row predictable from the native schema's declared bounds or type
    rules is not counted):
      reject rows count only when outcome.message occurs verbatim in the pinned
      server-common.cpp snapshot (an adapter-authored message, not the schema's bounds text);
      slot rows only when at least one key of outcome.set differs from `param` (a mapping the
      schema does not declare for that name); response rows only for the four checks above
      (response-contract facts absent from the schema); ignored rows only when `param` occurs in
      no `field_*(` / `add_alias(` declaration of the pinned server-schema.cpp snapshot and
      appears in the counter's frozen OAI_STANDARD list.

RENDER (the `outcome` cell text the SKILL table must carry):
  reject   -> "reject <status> <type>: <message>"
  slot     -> "200, " + ", ".join("<key> = <json.dumps(value)>" for key in sorted(set))
  ignored  -> "200, no slot-parameter or response change"
  response -> "200, <check> = <json.dumps(value)>"

Not checked (reviewed per row, never counted): whether the meaning prose is correct beyond its
word count; whether the client consequence is the best advice.

Usage: count-c1.py [--lane DIR] [--repo GITDIR] [--tip REV] [--out FILE] [--explain ID]
Exit: 0 ran (whatever the count), 2 could not evaluate (pins, process identity, unsafe port,
base request failed).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
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

HOST = "127.0.0.1"
SERVER = Path.home() / ".local/opt/llama-b11755/llama-server"
IMPL = Path.home() / ".local/opt/llama-b11755/libllama-server-impl.so"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
BASE_COMMIT = "07794a4d30a54a60ebdff50ac76d12c6df40a0f1"
TARGET = 12
SKILL_HEADING = "## Round-31 chat-completions parameter outcomes"
TABLE_HEADER = ["id", "param", "sent", "outcome", "meaning", "source"]
SNAPSHOT_PINS = ".ufo/waves/round-31/sources/SNAPSHOT.json"
REGISTRY = "registry/chat-param-outcomes-r31.json"
GIT = "/usr/bin/git"
OAI_STANDARD = {
    "user", "parallel_tool_calls", "tools", "tool_choice", "response_format", "logprobs",
    "top_logprobs", "n", "stream", "stream_options", "stop", "max_tokens",
    "max_completion_tokens", "seed", "presence_penalty", "frequency_penalty", "logit_bias",
    "temperature", "top_p", "messages", "metadata", "store", "service_tier",
}
RESPONSE_CHECKS = ("n_choices", "has_logprobs", "sse", "sse_usage")


class CannotEvaluate(Exception):
    pass


def git(repo, *args, check=True):
    env = {k: v for k, v in os.environ.items()
           if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_OBJECT_DIRECTORY",
                        "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_REPLACE_REF_BASE")}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    p = subprocess.run([GIT, "--no-replace-objects", "-C", repo, *args],
                       capture_output=True, env=env)
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {p.stderr.decode(errors='replace').strip()}")
    return p


def blob(repo, rev, path):
    p = git(repo, "cat-file", "blob", f"{rev}:{path}", check=False)
    return p.stdout if p.returncode == 0 else None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((HOST, port)) != 0


def pick_port() -> int:
    ports = list(range(47900, 47999))
    random.shuffle(ports)
    for p in ports[:64]:
        if port_free(p):
            return p
    raise CannotEvaluate("no free port in 47900-47999")


def http(port: int, method: str, path: str, body, timeout=120):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(f"http://{HOST}:{port}{path}", data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)


def clean_env():
    drop = ("PYTHONPATH", "PYTHONSTARTUP", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH")
    env = {k: v for k, v in os.environ.items() if k not in drop}
    env["LD_LIBRARY_PATH"] = str(SERVER.parent)
    return env


class Server:
    def __init__(self):
        missing = [str(p) for p in (SERVER, MODEL, IMPL) if not p.exists()]
        if missing:
            raise CannotEvaluate(f"pinned path missing: {missing}")
        self.port = pick_port()
        self.tmp = tempfile.TemporaryDirectory(prefix="kama-r31c1-")
        self.log = Path(self.tmp.name) / f"srv-{self.port}.log"
        argv = [str(SERVER), "-m", str(MODEL), "--host", HOST, "--port", str(self.port)]
        self.fh = open(self.log, "wb")
        self.proc = subprocess.Popen(argv, stdout=self.fh, stderr=subprocess.STDOUT,
                                     env=clean_env(), start_new_session=True)
        self._wait_ready()

    def _wait_ready(self):
        deadline = time.time() + 90
        while time.time() < deadline:
            if self.proc.poll() is not None:
                raise CannotEvaluate(f"server exited early (see {self.log})")
            try:
                st, _, _ = http(self.port, "GET", "/health", None, timeout=2)
                if st == 200:
                    break
            except Exception:
                pass
            time.sleep(0.15)
        else:
            raise CannotEvaluate("server did not become ready in 90s")
        st, body, _ = http(self.port, "GET", "/props", None)
        mp = json.loads(body.decode()).get("model_path")
        if mp is None or Path(mp).resolve() != MODEL.resolve():
            raise CannotEvaluate(f"/props model_path {mp!r} is not the pinned model")

    def slots(self):
        st, body, _ = http(self.port, "GET", "/slots", None)
        if st != 200:
            raise CannotEvaluate(f"/slots status {st}")
        return json.loads(body.decode())

    def newest(self):
        slots = self.slots()
        return max(slots, key=lambda s: s.get("id_task", -1))

    def close(self):
        try:
            self.proc.send_signal(signal.SIGTERM)
            self.proc.wait(timeout=15)
        except Exception:
            try:
                self.proc.kill()
            except Exception:
                pass
        self.fh.close()
        deadline = time.time() + 10
        while time.time() < deadline and not port_free(self.port):
            time.sleep(0.1)
        self.tmp.cleanup()


def f32_eq(a, b) -> bool:
    if isinstance(a, bool) or isinstance(b, bool):
        return a == b
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        try:
            return abs(float(a) - float(b)) <= 1e-6 * max(1.0, abs(float(a)), abs(float(b)))
        except OverflowError:
            return False
    return a == b


def normalize_response(body: bytes) -> dict:
    try:
        d = json.loads(body.decode())
    except Exception:
        return {"raw_prefix": body[:40].decode(errors="replace")}
    choices = d.get("choices") or []
    return {
        "top_keys": sorted(d.keys()),
        "n_choices": len(choices),
        "choice_keys": [sorted(c.keys()) for c in choices if isinstance(c, dict)],
        "has_logprobs": bool(choices) and isinstance(choices[0], dict)
                        and choices[0].get("logprobs") is not None,
        "usage_keys": sorted((d.get("usage") or {}).keys()),
        "prompt_tokens": (d.get("usage") or {}).get("prompt_tokens"),
    }


def render(row: dict) -> str:
    o = row["outcome"]
    k = o["kind"]
    if k == "reject":
        return f"reject {o['status']} {o['type']}: {o['message']}"
    if k == "slot":
        return "200, " + ", ".join(f"{key} = {json.dumps(o['set'][key], sort_keys=True)}"
                                   for key in sorted(o["set"]))
    if k == "ignored":
        return "200, no slot-parameter or response change"
    if k == "response":
        return f"200, {o['check']} = {json.dumps(o['value'])}"
    raise ValueError(f"bad kind {k!r}")


def canonical_json(v) -> str:
    return json.dumps(v, sort_keys=True, separators=(",", ":"))


def schema_declares(snapshot: str, name: str) -> bool:
    if re.search(r'field_[a-z0-9_]+\("' + re.escape(name) + r'"', snapshot):
        return True
    if re.search(r'add_alias\("' + re.escape(name) + r'"\)', snapshot):
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lane", default=".")
    ap.add_argument("--repo", default=None)
    ap.add_argument("--tip", default=None)
    ap.add_argument("--out")
    ap.add_argument("--explain")
    a = ap.parse_args()

    repo = a.repo or a.lane
    tip = a.tip
    if tip is None:
        p = git(repo, "rev-parse", "--verify", "--quiet", "refs/heads/master", check=False)
        if p.returncode != 0:
            raise CannotEvaluate("no --tip and no refs/heads/master")
        tip = p.stdout.decode().strip()
    tip = git(repo, "rev-parse", "--verify", "--quiet", f"{tip}^{{commit}}", check=False) \
        .stdout.decode().strip()
    if not tip:
        raise CannotEvaluate("tip does not resolve")

    pins_raw = blob(repo, tip, SNAPSHOT_PINS)
    if pins_raw is None:
        raise CannotEvaluate(f"{SNAPSHOT_PINS} missing at tip")
    pins = json.loads(pins_raw)
    reg_raw = blob(repo, tip, REGISTRY)
    if reg_raw is None:
        raise CannotEvaluate(f"{REGISTRY} missing at tip")
    reg = json.loads(reg_raw)
    rows = reg.get("rows") or []
    base_body = reg.get("base_body") or {}

    if a.explain:
        for row in rows:
            if row.get("id") == a.explain:
                print(render(row))
                return 0
        print(f"no row {a.explain}", file=sys.stderr)
        return 2

    # Pins: local binary/library/model vs the registry's declared digests.
    build = reg.get("build") or {}
    for label, path, key in (("server", SERVER, "server_sha256"),
                             ("library", IMPL, "library_sha256"),
                             ("model", MODEL, "model_sha256")):
        want = build.get(key)
        if not want:
            raise CannotEvaluate(f"registry build.{key} missing")
        got = sha256_file(path)
        if got != want:
            raise CannotEvaluate(f"{label} pin mismatch: {got} != {want}")

    snapshots = {}
    for name, meta in (pins.get("files") or {}).items():
        data = (Path(a.lane) / ".ufo/waves/round-31/sources/llama.cpp-704366d" / name)
        if not data.exists():
            raise CannotEvaluate(f"snapshot {name} missing on disk")
        got = sha256_file(data)
        if got != meta["sha256"]:
            raise CannotEvaluate(f"snapshot {name} sha256 {got} != {meta['sha256']}")
        snapshots[name] = data.read_text(errors="replace")
    schema_snap = snapshots.get("server-schema.cpp")
    common_snap = snapshots.get("server-common.cpp")
    if schema_snap is None or common_snap is None:
        raise CannotEvaluate("server-schema.cpp / server-common.cpp snapshots required")

    skill_raw = blob(repo, tip, "SKILL.md")
    sources_raw = blob(repo, tip, "corpus/SOURCES.md")
    if skill_raw is None or sources_raw is None:
        raise CannotEvaluate("SKILL.md or corpus/SOURCES.md missing at tip")
    skill = skill_raw.decode("utf-8", errors="replace").split("\n")
    sources = sources_raw.decode("utf-8", errors="replace")
    base_sources = blob(repo, BASE_COMMIT, "corpus/SOURCES.md")
    if base_sources is None:
        raise CannotEvaluate("base SOURCES.md missing")
    base_sources = base_sources.decode("utf-8", errors="replace")

    # SKILL table locate.
    table = None
    for i, ln in enumerate(skill):
        if ln.startswith(SKILL_HEADING):
            j = i + 1
            while j < len(skill) and not skill[j].startswith("|"):
                if skill[j].startswith("## "):
                    break
                j += 1
            if j < len(skill) and [c.strip() for c in skill[j].strip().strip("|").split("|")] \
                    == TABLE_HEADER:
                k = j + 1
                if k < len(skill) and set(skill[k].replace("|", "").replace(" ", "")) <= set("-:"):
                    k += 1
                cells = []
                while k < len(skill) and skill[k].startswith("|"):
                    cells.append((k + 1, [c.strip() for c in
                                          skill[k].strip().strip("|").split("|")]))
                    k += 1
                table = cells
            break
    if table is None:
        print(f"cannot evaluate: no `{SKILL_HEADING}` table with the frozen header", file=sys.stderr)
        return 2

    results = []
    seen_ids = set()
    counted = 0
    dup_ids = set()
    for row in rows:
        rid = str(row.get("id", ""))
        if rid in seen_ids:
            dup_ids.add(rid)
        seen_ids.add(rid)

    server = Server()
    try:
        st, body, _ = http(server.port, "POST", "/v1/chat/completions", base_body)
        if st != 200:
            raise CannotEvaluate(f"base request status {st}: {body[:200]!r}")
        base_slot = server.newest()
        base_params = base_slot["params"]
        base_norm = normalize_response(body)
        base_task = base_slot.get("id_task", -1)

        for row in rows:
            rid = str(row.get("id", ""))
            reasons = []
            out = row.get("outcome") or {}
            param = row.get("param")
            sent = row.get("sent")
            src = row.get("source") or {}
            if rid in dup_ids:
                reasons.append("duplicate-id")
            if not isinstance(param, str) or not param:
                reasons.append("no-param")
            if out.get("kind") not in ("reject", "slot", "ignored", "response"):
                reasons.append("bad-kind")
            # (b) SKILL table row
            want = None
            try:
                want = render(row)
            except Exception:
                reasons.append("unrenderable-outcome")
            match = None
            for line_no, cells in table:
                if len(cells) == 6 and cells[0] == rid:
                    match = (line_no, cells)
                    break
            if match is None:
                reasons.append("no-skill-row")
            else:
                line_no, cells = match
                if cells[1] != param:
                    reasons.append(f"skill-param:{cells[1]!r}")
                if cells[2] != canonical_json(sent):
                    reasons.append(f"skill-sent:{cells[2]!r}")
                if want is not None and cells[3] != want:
                    reasons.append(f"skill-outcome:{cells[3]!r}")
                if len(cells[4].split()) < 8:
                    reasons.append(f"skill-meaning-words:{len(cells[4].split())}")
                if cells[5] != str(src.get("row", "")):
                    reasons.append(f"skill-source:{cells[5]!r}")
            # (c) SOURCES row + snapshot binding
            srow = str(src.get("row", ""))
            m = re.search(r"^\|\s*" + re.escape(srow) + r"\s*\|(.*)$", sources, re.M)
            if not m:
                reasons.append(f"no-source-row:{srow}")
            else:
                text = m.group(1)
                fname = str(src.get("file", ""))
                line_no = src.get("line")
                if fname and fname not in text:
                    reasons.append(f"source-file:{fname}")
                if line_no is not None and f"L{line_no}" not in text and f"line {line_no}" not in text:
                    reasons.append(f"source-line:{line_no}")
                if "704366d" not in text:
                    reasons.append("source-commit")
                if re.search(r"^\|\s*" + re.escape(srow) + r"\s*\|", base_sources, re.M):
                    reasons.append("source-existed-at-base")
                snap = snapshots.get(fname)
                needle = src.get("contains")
                if snap is None:
                    reasons.append(f"source-file-unpinned:{fname}")
                elif line_no is None or not isinstance(line_no, int) \
                        or not (1 <= line_no <= len(snap.split("\n"))):
                    reasons.append("source-line-range")
                elif str(needle or "") not in snap.split("\n")[line_no - 1]:
                    reasons.append("source-line-content")
            # (e) discrimination rules that do not need the live run
            kind = out.get("kind")
            if kind == "reject" and str(out.get("message", "")) not in common_snap:
                reasons.append("reject-message-not-adapter")
            if kind == "slot" and not any(k != param for k in (out.get("set") or {})):
                reasons.append("slot-not-a-mapping")
            if kind == "response" and out.get("check") not in RESPONSE_CHECKS:
                reasons.append("response-check-not-allowed")
            if kind == "ignored":
                if param not in OAI_STANDARD:
                    reasons.append("ignored-not-oai-standard")
                if schema_declares(schema_snap, str(param)):
                    reasons.append("ignored-declared-in-schema")
            # (d) live
            live = {}
            if not reasons:
                req = dict(base_body)
                req[param] = sent
                for k2, v2 in (row.get("also") or {}).items():
                    req[k2] = v2
                try:
                    st, body, headers = http(server.port, "POST", "/v1/chat/completions", req)
                except Exception as e:  # noqa: BLE001
                    reasons.append(f"live-error:{type(e).__name__}")
                    st, body, headers = 0, b"", {}
                live["status"] = st
                if kind == "reject":
                    try:
                        doc = json.loads(body.decode())
                        err = doc.get("error") or {}
                        live["error_keys"] = sorted(err.keys())
                        live["message"] = err.get("message")
                        live["type"] = err.get("type")
                        live["code"] = err.get("code")
                        if st != out.get("status"):
                            reasons.append(f"reject-status:{st}")
                        if sorted(err.keys()) != ["code", "message", "type"]:
                            reasons.append(f"reject-envelope:{sorted(err.keys())}")
                        if err.get("code") != out.get("status"):
                            reasons.append(f"reject-code:{err.get('code')}")
                        if err.get("type") != out.get("type"):
                            reasons.append(f"reject-type:{err.get('type')}")
                        if err.get("message") != out.get("message"):
                            reasons.append("reject-message")
                    except Exception:
                        reasons.append("reject-body-not-json")
                elif kind == "slot":
                    if st != 200:
                        reasons.append(f"slot-status:{st}")
                    else:
                        newest = server.newest()
                        live["slot_task"] = newest.get("id_task")
                        params = newest.get("params") or {}
                        for key, val in (out.get("set") or {}).items():
                            if key not in params:
                                reasons.append(f"slot-key-absent:{key}")
                            elif not f32_eq(params[key], val):
                                reasons.append(f"slot-value:{key}={params[key]!r}")
                elif kind == "ignored":
                    if st != 200:
                        reasons.append(f"ignored-status:{st}")
                    else:
                        newest = server.newest()
                        params = newest.get("params") or {}
                        if set(params.keys()) != set(base_params.keys()):
                            reasons.append("ignored-key-set")
                        else:
                            diff = [k for k in params if not f32_eq(params[k], base_params[k])]
                            if diff:
                                reasons.append(f"ignored-delta:{sorted(diff)}")
                        norm = normalize_response(body)
                        if norm != base_norm:
                            reasons.append("ignored-response")
                        live["normalized"] = norm
                elif kind == "response":
                    if st != 200:
                        reasons.append(f"response-status:{st}")
                    else:
                        check = out.get("check")
                        text = body.decode(errors="replace")
                        if check == "n_choices":
                            got = len(json.loads(text).get("choices") or [])
                        elif check == "has_logprobs":
                            ch = json.loads(text).get("choices") or [{}]
                            got = ch[0].get("logprobs") is not None
                        elif check in ("sse", "sse_usage"):
                            frames = [ln[len("data: "):] for ln in text.split("\n")
                                      if ln.startswith("data: ")]
                            parsed = []
                            for fr in frames:
                                if fr.strip() == "[DONE]":
                                    continue
                                try:
                                    parsed.append(json.loads(fr))
                                except Exception:
                                    pass
                            if check == "sse":
                                got = bool(parsed) and any(fr.strip() == "[DONE]" for fr in frames)
                            else:
                                got = any(isinstance(p, dict) and p.get("usage")
                                          for p in parsed)
                        else:
                            got = None
                        live["observed"] = got
                        if got != out.get("value"):
                            reasons.append(f"response-value:{got!r}")
            ok = not reasons
            counted += 1 if ok else 0
            results.append({"id": rid, "counted": ok, "reasons": reasons, "live": live})

        # Base request repeatability: the base params must not drift across the run.
        final = server.newest()
        drift = [k for k in base_params
                 if k in (final.get("params") or {})
                 and not f32_eq(base_params[k], final.get("params")[k])]
    finally:
        server.close()

    not_counted = [r["id"] for r in results if not r["counted"]]
    summary = (f"registered {len(rows)} counted {counted} target {TARGET} met {counted >= TARGET} "
               f"not-counted {not_counted}")
    print(summary)
    if a.out:
        with open(a.out, "w") as fh:
            json.dump({"summary": summary, "tip": tip, "base": BASE_COMMIT,
                       "registered": len(rows), "counted": counted, "target": TARGET,
                       "met": counted >= TARGET, "not_counted": not_counted,
                       "rows": results}, fh, indent=1)
            fh.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CannotEvaluate as e:
        print(f"cannot evaluate: {e}", file=sys.stderr)
        sys.exit(2)
