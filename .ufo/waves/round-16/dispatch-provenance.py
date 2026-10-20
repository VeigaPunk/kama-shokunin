#!/usr/bin/env python3
"""dispatch-provenance.py — wave-dispatch provenance ledger (round-16 defect 4).

Round-15 routed defect 4 (corpus/lessons/round-15-verifier-spotcheck.md:168):
wave validation receipts must preserve the environment bindings and the
refused-attempt payload identity. This script is the receipt writer.

Mode 1 — wave run receipt:

    dispatch-provenance.py --spec PATH --out LEDGER.json [--timeout SECONDS]

Runs exactly:

    node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs \
        run --spec PATH

with exactly these three bindings added to the inherited environment:

    UFO_CONFIG_PATH=/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json
    UFO_FLEET_ALLOW_EXTERNAL_TOOLS=1
    UFO_PROJECT_ROOT=/home/vgpnk/Projects/shokunin/kama-shokunin

and appends a `wave_run` entry recording argv, cwd, ONLY those three
env bindings (never the rest of the environment), child exit code,
stdout/stderr sha256 + byte counts, spec sha256, the sha256 of the
canonical JSON of stdout's `taskCall`, dispatch counts, and started/ended
UTC. Exit status is the child's exit status.

Mode 2 — attempt receipt:

    dispatch-provenance.py --attempt-result PATH --label refused|spawned \
        --out LEDGER.json

Appends an `attempt` entry to the same ledger: {label, at UTC,
result_sha256, result_bytes, parseable, refused/spawned counts when the
result JSON is parseable} plus `bound_task_call_sha256` copied from the
most recent `wave_run` entry — so a refused task call is tied to the same
taskCall digest that produced it.

The ledger is a single JSON object {schema, entries:[...]} written
atomically (tempfile + os.replace). An existing file with a different
schema or unparseable JSON is refused, never clobbered.

Stdlib only. No other reads, no network, no environment capture.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

WAVE_SCRIPT = "/home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs"

# The complete set of bindings added to the inherited environment. The
# ledger records exactly these names and values — never any other entry
# of os.environ.
ENV_BINDINGS = {
    "UFO_CONFIG_PATH":
        "/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json",
    "UFO_FLEET_ALLOW_EXTERNAL_TOOLS": "1",
    "UFO_PROJECT_ROOT":
        "/home/vgpnk/Projects/shokunin/kama-shokunin",
}

LEDGER_SCHEMA = "dispatch-provenance-ledger-v1"
TOOL = "dispatch-provenance.py"

# Exit codes: the child's own exit status is propagated for a wave run;
# wrapper faults use 64 (usage) / 70 (internal/refused) / 74 (I/O).
EX_USAGE = 64
EX_SOFTWARE = 70
EX_IOERR = 74


def utc_now():
    """ISO-8601 UTC instant with Z suffix, microsecond precision."""
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z")


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value):
    """sha256 of canonical json.dumps(sort_keys, tight separators)."""
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    return sha256_bytes(blob)


def load_ledger(path):
    """Return ledger dict. Missing file -> fresh skeleton. Anything else
    unusable is refused loudly rather than rewritten."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        return {"schema": LEDGER_SCHEMA, "entries": []}
    except OSError as exc:
        sys.stderr.write("%s: cannot read ledger %s: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_IOERR)
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as exc:
        sys.stderr.write("%s: refusing to clobber unparseable ledger %s: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_SOFTWARE)
    if not isinstance(doc, dict) or doc.get("schema") != LEDGER_SCHEMA \
            or not isinstance(doc.get("entries"), list):
        sys.stderr.write("%s: refusing ledger %s: unknown schema\n"
                         % (TOOL, path))
        sys.exit(EX_SOFTWARE)
    return doc


def write_ledger(path, doc):
    """Atomic replace via tempfile + os.replace; fsync before rename."""
    directory = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".dispatch-provenance-",
                               dir=directory)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(json.dumps(doc, indent=2, sort_keys=True,
                                ensure_ascii=False).encode("utf-8"))
            fh.write(b"\n")
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except OSError as exc:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        sys.stderr.write("%s: cannot write ledger %s: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_IOERR)


def last_wave_run(entries):
    for entry in reversed(entries):
        if entry.get("kind") == "wave_run":
            return entry
    return None


# --- attempt-result count extraction -------------------------------------
# Counts are "refused/spawned ... if parseable": the result payload shape
# is not contractually fixed, so extraction is conservative and generic:
#   * any dict key literally "refused" or "spawned" carrying an int adds
#     to that tally;
#   * any "status"/"state" field whose string value is exactly "refused"
#     or "spawned" adds to that tally (per-member progress rows).
# Anything else contributes nothing; unparseable results record
# parseable:false and null counts.

def tally_counts(node, counts):
    if isinstance(node, dict):
        for key, value in node.items():
            if key in ("refused", "spawned") and isinstance(value, int) \
                    and not isinstance(value, bool):
                counts[key] += value
            elif key in ("status", "state") and isinstance(value, str) \
                    and value in ("refused", "spawned"):
                counts[value] += 1
            else:
                tally_counts(value, counts)
    elif isinstance(node, list):
        for item in node:
            tally_counts(item, counts)


def extract_counts(result_json):
    counts = {"refused": 0, "spawned": 0}
    tally_counts(result_json, counts)
    return counts


def cmd_run(args):
    spec = os.path.abspath(args.spec)
    if not os.path.isfile(spec):
        sys.stderr.write("%s: --spec not a file: %s\n" % (TOOL, spec))
        sys.exit(EX_USAGE)
    try:
        with open(spec, "rb") as fh:
            spec_sha256 = sha256_bytes(fh.read())
    except OSError as exc:
        sys.stderr.write("%s: cannot read spec %s: %s\n"
                         % (TOOL, spec, exc))
        sys.exit(EX_IOERR)

    argv = ["node", WAVE_SCRIPT, "run", "--spec", spec]
    env = dict(os.environ)
    env.update(ENV_BINDINGS)

    started = utc_now()
    spawn_error = None
    try:
        proc = subprocess.run(
            argv, env=env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, timeout=args.timeout,
            check=False)
        exit_code = proc.returncode
        stdout = proc.stdout
        stderr = proc.stderr
    except subprocess.TimeoutExpired as exc:
        exit_code = None
        spawn_error = "timeout after %ss" % args.timeout
        stdout = exc.stdout or b""
        stderr = exc.stderr or b""
    except OSError as exc:
        exit_code = None
        spawn_error = "spawn failed: %s" % exc
        stdout = b""
        stderr = b""
    ended = utc_now()

    # Parse the dispatch payload; a failure payload or truncated output
    # leaves stdout_parseable false and taskCall null.
    payload = None
    stdout_parseable = False
    try:
        candidate = json.loads(stdout.decode("utf-8"))
        if isinstance(candidate, dict):
            payload = candidate
            stdout_parseable = True
    except (ValueError, UnicodeDecodeError):
        pass

    task_call = payload.get("taskCall") if payload is not None else None
    counts = {
        "dispatch": payload.get("counts") if payload is not None else None,
        "tasks":
            len(task_call["tasks"])
            if isinstance(task_call, dict)
            and isinstance(task_call.get("tasks"), list) else None,
        "resume_sends":
            len(payload["resumeSends"])
            if payload is not None
            and isinstance(payload.get("resumeSends"), list) else None,
    }

    entry = {
        "kind": "wave_run",
        "argv": argv,
        "cwd": os.getcwd(),
        "env_bindings": dict(ENV_BINDINGS),
        "env_binding_names": sorted(ENV_BINDINGS),
        "spec": spec,
        "spec_sha256": spec_sha256,
        "started": started,
        "ended": ended,
        "exit": exit_code,
        "spawn_error": spawn_error,
        "stdout_sha256": sha256_bytes(stdout),
        "stdout_bytes": len(stdout),
        "stderr_sha256": sha256_bytes(stderr),
        "stderr_bytes": len(stderr),
        "stdout_parseable": stdout_parseable,
        # Canonical digest of stdout JSON taskCall (null when absent or
        # stdout unparseable — distinguish via stdout_parseable).
        "taskCall_sha256": canonical_sha256(task_call),
        "counts": counts,
    }

    ledger = load_ledger(args.out)
    ledger["entries"].append(entry)
    write_ledger(args.out, ledger)

    sys.stderr.write(
        "%s: wave_run recorded in %s (exit=%s taskCall=%s)\n"
        % (TOOL, args.out,
           "spawn-error" if spawn_error else exit_code,
           entry["taskCall_sha256"][:16]))
    if spawn_error is not None:
        sys.exit(EX_SOFTWARE)
    sys.exit(exit_code)


def cmd_attempt(args):
    try:
        with open(args.attempt_result, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        sys.stderr.write("%s: cannot read attempt result %s: %s\n"
                         % (TOOL, args.attempt_result, exc))
        sys.exit(EX_IOERR)

    parseable = False
    counts = None
    try:
        result_json = json.loads(raw.decode("utf-8"))
        parseable = True
        counts = extract_counts(result_json)
    except (ValueError, UnicodeDecodeError):
        pass

    ledger = load_ledger(args.out)
    bound = last_wave_run(ledger["entries"])

    entry = {
        "kind": "attempt",
        "label": args.label,
        "at": utc_now(),
        "attempt_result": os.path.abspath(args.attempt_result),
        "result_sha256": sha256_bytes(raw),
        "result_bytes": len(raw),
        "parseable": parseable,
        "refused": counts["refused"] if counts else None,
        "spawned": counts["spawned"] if counts else None,
        # Ties this attempt to the wave_run entry whose taskCall digest
        # minted the payload the operator tried to issue. Null when the
        # ledger has no prior run (recorded, not silently dropped).
        "bound_task_call_sha256":
            bound["taskCall_sha256"] if bound is not None else None,
        "bound_run_index":
            len(ledger["entries"]) - 1 - ledger["entries"][::-1].index(bound)
            if bound is not None else None,
    }
    ledger["entries"].append(entry)
    write_ledger(args.out, ledger)

    sys.stderr.write(
        "%s: attempt '%s' recorded in %s (result=%s bound=%s)\n"
        % (TOOL, args.label, args.out, entry["result_sha256"][:16],
           (entry["bound_task_call_sha256"] or "none")[:16]))
    sys.exit(0)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=TOOL,
        description="Wave-dispatch provenance ledger: record the exact "
                    "env bindings, argv, digests and counts of a "
                    "ufo-swarm-wave run, then bind refused/spawned task "
                    "attempts to the same taskCall digest.")
    parser.add_argument("--spec",
                        help="wave spec path for a wave run")
    parser.add_argument("--attempt-result",
                        help="JSON result file of a refused/spawned task "
                             "call to append to the ledger")
    parser.add_argument("--label", choices=["refused", "spawned"],
                        help="attempt outcome label (required with "
                             "--attempt-result)")
    parser.add_argument("--out", required=True,
                        help="ledger JSON path (created if absent)")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="child timeout seconds for a wave run "
                             "(default 300)")
    args = parser.parse_args(argv)

    if args.attempt_result is not None:
        if args.spec is not None:
            parser.error("--spec and --attempt-result are mutually "
                         "exclusive")
        if args.label is None:
            parser.error("--attempt-result requires --label "
                         "refused|spawned")
        cmd_attempt(args)
    else:
        if args.spec is None:
            parser.error("a wave run requires --spec PATH")
        if args.label is not None:
            parser.error("--label is only valid with --attempt-result")
        cmd_run(args)


if __name__ == "__main__":
    main()
