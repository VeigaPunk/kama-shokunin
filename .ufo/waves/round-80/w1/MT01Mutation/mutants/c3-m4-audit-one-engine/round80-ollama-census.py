#!/usr/bin/env python3
"""round80-ollama-census.py - round-80 C3 (operability): the registered class on a second engine.

PREDICATE (frozen: plans/round-80-claims.md section C3):

    `python3 tools/round80-ollama-census.py --repo <lane>` prints one `OLLAMA_CENSUS port=<p>
    engine=ollama unregistered=1 governed=1 class_missing=0` line and exits 0 only when the
    lane-owned pinned Ollama child (v0.40.11, scratch HOME and model store, one model created
    from the lane fixture GGUF) serving on a free loopback port is reported by
    `bash tools/kama-probe.sh listeners` as `registered=no` under a registry that does not
    declare that port and as `registered=yes` under one that does, the summary's
    `unregistered`/`governed` counts move with the class, and the run writes the engine's
    receipt into the class-engine register; `--audit` then prints `CLASS_ENGINES engines=2
    verified=2 stale=0` only when every register row's receipt exists, carries
    `class_missing=0` and names the same engine.

What it does: starts `~/.local/opt/ollama-v0.40.11/bin/ollama serve` with `OLLAMA_HOST` on a
free loopback port that is neither a registry-declared consumer port nor listening, creates one
model from `~/.cache/kama-shokunin/models/stories260K.gguf` under a scratch HOME and model
store, checks the server identifies as 0.40.11 and the model is listed, then runs the probe's
`listeners --json --port` against two scratch registries (one declaring the port, one not) and
grades the class both ways. The child is torn down in the same run and the port closure is
checked. It is a lane-owned child under the round-16/60/61 fixture boundary: nothing under
`~/.config`, `~/.omp` or systemd is written, no registered consumer is contacted, no consumer
row is admitted, and the live-host leg is informational (it gates nothing).

Class-engine register (`registry/unregistered-class-engines.tsv`, tab-separated):

    engine  counter  receipt  verified_at

`--audit` re-derives each row: the counter path exists, the receipt exists at the tip (or in the
worktree), carries `class_missing=0`, and names the row's engine. It requires at least two
distinct engines: one engine's receipt is a class, two engines' receipts are an engine-agnostic
class.

Usage: round80-ollama-census.py --repo DIR [--work DIR] [--out FILE] [--probe PATH]
       [--keep] [--audit] [--register FILE] [--tip REV] [--json] | --selftest

Exit: 0 the two fixture legs classify as the predicate requires (or the register audits green
with two engines); 1 a leg disagrees / a register row is stale; 2 could-not-evaluate
(prerequisite absent, child not ready, probe error) -- never silently 0.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SERVER = Path.home() / ".local/opt/ollama-v0.40.11/bin/ollama"
MODEL = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"
MODEL_ID = "stories260K"
PIN_VERSION = "0.40.11"
REGISTER = "registry/unregistered-class-engines.tsv"
REGISTER_HEADER = "engine\tcounter\treceipt\tverified_at"


class CouldNotEvaluate(Exception):
    pass


def opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def fetch(port: int, path: str, timeout: float = 5.0) -> tuple[int, bytes]:
    try:
        with opener().open(f"http://127.0.0.1:{port}{path}", timeout=timeout) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:  # type: ignore[attr-defined]
        return exc.code, exc.read()
    except OSError as exc:
        raise CouldNotEvaluate(f"GET {path} failed: {exc}")


def registered_ports(repo: Path) -> set[int]:
    path = repo / "registry/endpoint-consumers.tsv"
    ports: set[int] = set()
    if not path.is_file():
        return ports
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        cells = line.split("\t")
        if len(cells) < 4 or cells[0].strip() == "id":
            continue
        host = cells[3].strip().split("://")[-1].split("/")[0]
        if ":" in host and host.rsplit(":", 1)[1].isdigit():
            ports.add(int(host.rsplit(":", 1)[1]))
    return ports


def listening(port: int) -> bool:
    with socket.socket() as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def free_port(repo: Path) -> int:
    taken = registered_ports(repo)
    for _ in range(200):
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        if port not in taken and not listening(port):
            return port
    raise CouldNotEvaluate("no free loopback port outside the registry")


def write_registry(path: Path, port: int | None) -> None:
    rows = ["# round-80 scratch registry (census legs; not a consumer admission)"]
    if port is None:
        rows.append("fixture\t-\tgrep::\thttp://127.0.0.1:9\t-\tscratch")
    else:
        rows.append(f"fixture\t-\tgrep::\thttp://127.0.0.1:{port}\t{MODEL_ID}\tscratch")
    path.write_text("\n".join(rows) + "\n")


def probe_json(probe: Path, repo: Path, registry: Path, port: int) -> tuple[dict, int]:
    argv = ([sys.executable] if probe.suffix == ".py" else ["bash"]) + [
        str(probe), "listeners", "--json", "--registry", str(registry), "--port", str(port)]
    proc = subprocess.run(argv, cwd=repo, capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        return {"__error__": proc.stderr.strip()[:300] or f"exit {proc.returncode}"}, proc.returncode
    try:
        return json.loads(proc.stdout), proc.returncode
    except json.JSONDecodeError as exc:
        return {"__error__": f"unparsable probe JSON: {exc}"}, proc.returncode


def classify(doc: dict, port: int) -> tuple[str | None, dict]:
    rows = doc.get("listeners")
    if not isinstance(rows, list):
        return None, doc.get("summary") or {}
    for row in rows:
        if row.get("port") == port:
            return row.get("registered"), row
    return None, doc.get("summary") or {}


def grade(doc_yes: dict, doc_no: dict, port: int) -> dict:
    findings = []
    yes_class, yes_row = classify(doc_yes, port)
    no_class, no_row = classify(doc_no, port)
    missing = False
    if yes_class is None or no_class is None:
        missing = True
        findings.append("OLLAMA_CENSUS_FINDING class-missing")
    else:
        if no_class != "no":
            findings.append(f"OLLAMA_CENSUS_FINDING unregistered-leg={no_class}")
        if yes_class != "yes":
            findings.append(f"OLLAMA_CENSUS_FINDING governed-leg={yes_class}")
        if no_class == yes_class:
            findings.append("OLLAMA_CENSUS_FINDING legs-agree")
        for name, row, summary in (("no", no_row, doc_no.get("summary") or {}),
                                   ("yes", yes_row, doc_yes.get("summary") or {})):
            if row.get("owner") and "ollama" not in str(row.get("owner")):
                findings.append(f"OLLAMA_CENSUS_FINDING owner-not-ollama leg={name} "
                                f"owner={row.get('owner')}")
            if row.get("verdict") != "MODEL_OK":
                findings.append(f"OLLAMA_CENSUS_FINDING verdict leg={name} "
                                f"verdict={row.get('verdict')}")
            if summary.get("governed") != (1 if name == "yes" else 0):
                findings.append(f"OLLAMA_CENSUS_FINDING governed-count leg={name} "
                                f"governed={summary.get('governed')}")
            if summary.get("unregistered") != (1 if name == "no" else 0):
                findings.append(f"OLLAMA_CENSUS_FINDING unregistered-count leg={name} "
                                f"unregistered={summary.get('unregistered')}")
    summary = {"port": port, "engine": "ollama", "unregistered": 1 if not findings else 0,
               "governed": 1 if not findings else 0, "class_missing": 1 if missing else 0}
    return {"summary": summary, "findings": findings}


def run_fixture(repo: Path, work: Path, probe: Path | None, out: Path, keep: bool) -> dict:
    server = SERVER
    if not server.is_file() or not os.access(server, os.X_OK):
        raise CouldNotEvaluate(f"pinned ollama binary absent: {server}")
    if not MODEL.is_file():
        raise CouldNotEvaluate(f"fixture GGUF absent: {MODEL}")
    probe = probe or repo / "tools/kama-probe.sh"
    if not probe.is_file():
        raise CouldNotEvaluate(f"probe absent: {probe}")
    work.mkdir(parents=True, exist_ok=True)
    home, models = work / "home", work / "models"
    home.mkdir(exist_ok=True)
    models.mkdir(exist_ok=True)
    port = free_port(repo)
    nonce = f"kama-r80-{port}"
    env = {**os.environ, "HOME": str(home), "OLLAMA_MODELS": str(models),
           "OLLAMA_HOST": f"127.0.0.1:{port}"}
    log = work / "serve.log"
    handle = log.open("wb")
    child = subprocess.Popen([str(server), "serve"], env=env, stdout=handle, stderr=subprocess.STDOUT,
                             start_new_session=True)
    receipt: dict = {"schema": "kama-ollama-census/v1", "port": port, "nonce": nonce,
                     "server": str(server), "probe": str(probe), "model": str(MODEL)}
    try:
        deadline = time.monotonic() + 120
        version = None
        while time.monotonic() < deadline:
            if child.poll() is not None:
                raise CouldNotEvaluate(f"ollama exited early: {log.read_text()[-400:]}")
            try:
                status, body = fetch(port, "/api/version", timeout=1)
            except CouldNotEvaluate:
                time.sleep(0.2)
                continue
            if status == 200:
                version = json.loads(body).get("version")
                break
            time.sleep(0.2)
        if version != PIN_VERSION:
            raise CouldNotEvaluate(f"server version {version!r} != pinned {PIN_VERSION}")
        receipt["version"] = version
        modelfile = work / "Modelfile"
        modelfile.write_text(f"FROM {MODEL}\n")
        created = subprocess.run([str(server), "create", nonce, "-f", str(modelfile)], env=env,
                                 capture_output=True, text=True, timeout=300)
        if created.returncode != 0:
            raise CouldNotEvaluate(f"ollama create exit={created.returncode}: "
                                   f"{created.stderr.strip()[:300]}")
        status, body = fetch(port, "/api/tags")
        tags = json.loads(body) if status == 200 else {}
        names = [m.get("name", "") for m in tags.get("models", [])]
        if not any(n.startswith(nonce) for n in names):
            raise CouldNotEvaluate(f"created model not listed: {names}")
        receipt["api_tags_names"] = names
        status, body = fetch(port, "/v1/models")
        receipt["v1_models"] = {"status": status, "body": json.loads(body) if status == 200 else None}
        status, body = fetch(port, "/api/ps")
        receipt["api_ps"] = {"status": status, "body": json.loads(body) if status == 200 else None}
        yes_reg, no_reg = work / "registry-yes.tsv", work / "registry-no.tsv"
        write_registry(yes_reg, port)
        write_registry(no_reg, None)
        doc_yes, exit_yes = probe_json(probe, repo, yes_reg, port)
        doc_no, exit_no = probe_json(probe, repo, no_reg, port)
        if "__error__" in doc_yes or "__error__" in doc_no:
            raise CouldNotEvaluate(f"probe error: {doc_yes.get('__error__') or doc_no.get('__error__')}")
        result = grade(doc_yes, doc_no, port)
        receipt.update({"exit_yes": exit_yes, "exit_no": exit_no, "doc_yes": doc_yes,
                        "doc_no": doc_no, "grade": result})
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n")
        s = result["summary"]
        line = (f"OLLAMA_CENSUS port={s['port']} engine=ollama unregistered={s['unregistered']} "
                f"governed={s['governed']} class_missing={s['class_missing']}")
        print(line)
        for finding in result["findings"]:
            print(finding)
        return {"result": result, "receipt": receipt, "exit": 1 if result["findings"] else 0}
    finally:
        if not keep:
            child.terminate()
            try:
                child.wait(timeout=20)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait(timeout=20)
        handle.close()
        receipt["teardown"] = {"returncode": child.returncode, "port_closed": not listening(port)}
        if not listening(port):
            pass
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, indent=2) + "\n")


def audit(repo: Path, register: str, tip: str) -> dict:
    path = repo / register
    if not path.is_file():
        return {"summary": {"engines": 0, "verified": 0, "stale": 0},
                "findings": ["CLASS_ENGINES_FINDING register-absent"], "exit": 2}
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    findings: list[str] = []
    if not lines or lines[0].rstrip("\r") != REGISTER_HEADER:
        raise CouldNotEvaluate(f"{register}: header is not {REGISTER_HEADER!r}")
    engines, verified = set(), 0
    for number, line in enumerate(lines[1:], 2):
        cells = line.split("\t")
        if len(cells) != 4:
            findings.append(f"CLASS_ENGINES_FINDING bad-row line {number}")
            continue
        engine, counter, receipt, dated = (c.strip() for c in cells)
        engines.add(engine)
        if not (repo / counter).is_file():
            findings.append(f"CLASS_ENGINES_FINDING missing-counter {engine} {counter}")
            continue
        text = None
        for spec in (f"{tip}:{receipt}", None):
            if spec is None:
                if (repo / receipt).is_file():
                    text = (repo / receipt).read_text()
                break
            proc = subprocess.run(["git", "-C", str(repo), "show", spec], capture_output=True, text=True)
            if proc.returncode == 0:
                text = proc.stdout
                break
        if text is None:
            findings.append(f"CLASS_ENGINES_FINDING missing-receipt {engine} {receipt}")
            continue
        if "class_missing=0" not in text:
            findings.append(f"CLASS_ENGINES_FINDING receipt-red {engine} {receipt}")
            continue
        if engine not in text:
            findings.append(f"CLASS_ENGINES_FINDING receipt-names-other-engine {engine} {receipt}")
            continue
        verified += 1
    summary = {"engines": len(engines), "verified": verified, "stale": len(findings)}
    return {"summary": summary, "findings": findings, "exit": 1 if findings else 0}


def selftest() -> int:
    port = 45001
    cases = []

    def doc(registered, summary, owner="ollama(pid=1)", verdict="MODEL_OK"):
        return {"listeners": [{"port": port, "registered": registered, "owner": owner,
                               "verdict": verdict}], "summary": summary}

    def case(name, yes, no, want):
        result = grade(yes, no, port)
        got = 1 if result["findings"] else 0
        cases.append((name, got == want, got, want, result["findings"][:2]))

    green_yes = doc("yes", {"governed": 1, "unregistered": 0})
    green_no = doc("no", {"governed": 0, "unregistered": 1})
    case("both-legs", green_yes, green_no, 0)
    case("class-missing", doc("yes", {"governed": 1}), doc(None, {"unregistered": 1}), 1)
    case("legs-agree", green_yes, doc("yes", {"governed": 1}), 1)
    case("owner-not-ollama", green_yes, doc("no", {"unregistered": 1}, owner="python3(pid=2)"), 1)
    case("verdict-not-model-ok", green_yes, doc("no", {"unregistered": 1}, verdict="FOREIGN_SERVICE"), 1)
    case("counts-do-not-move", green_yes, doc("no", {"governed": 1, "unregistered": 0}), 1)
    failed = 0
    for name, ok, got, want, findings in cases:
        failed += not ok
        print(f"OLLAMA_CENSUS_SELFTEST {name} {'PASS' if ok else 'FAIL'} exit={got} expected={want}")
        if not ok:
            print("  findings", findings)
    print(f"OLLAMA_CENSUS_SELFTEST pass={len(cases) - failed} fail={failed}")
    return int(bool(failed))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work")
    parser.add_argument("--out", default=".ufo/waves/round-80/measured/after/c3-ollama-census.json")
    parser.add_argument("--probe")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--register", default=REGISTER)
    parser.add_argument("--tip", default="master")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    if args.audit:
        try:
            result = audit(repo, args.register, args.tip)
        except (CouldNotEvaluate, OSError) as exc:
            print(f"could-not-evaluate: {exc}", file=sys.stderr)
            return 2
        s = result["summary"]
        print(f"CLASS_ENGINES engines={s['engines']} verified={s['verified']} stale={s['stale']}")
        for finding in result["findings"]:
            print(finding)
        return result["exit"]
    provider = Path(args.work) if args.work else Path(tempfile.mkdtemp(prefix="kama-r80-ollama-"))
    owned = not args.work and not args.keep
    try:
        outcome = run_fixture(repo, provider, Path(args.probe).resolve() if args.probe else None,
                              repo / args.out, args.keep)
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    finally:
        if owned:
            shutil.rmtree(provider, ignore_errors=True)
    return outcome["exit"]


if __name__ == "__main__":
    sys.exit(main())
