#!/usr/bin/env python3
"""dispatch-provenance.py — wave-dispatch provenance ledger (round-18 correction).

Round-17 residual fixed here: per-task "Background job limit reached" messages
were previously missed by the refused counter.

Round-16 routed defect 1 (corpus/lessons/round-16-verifier-spotcheck.md:182):
(a) every wave's validation must record the policy version and every
    ledger entry the policy identity; falsify needs a validation.json
    with a policy block;
(b) taskCall digests need ONE canonicalization — the round-16 build
    receipt reproduced only with ensure_ascii=True while the falsify
    producer used False;
(c) the attempt ledger must count async `pending` spawns — round 16
    recorded spawned:0 for 79 members because the OMP task result holds
    members as pending progress rows plus a human-readable spawn list,
    not a `spawned` count key;
(d) a per-wave validation.json must be writable from the ledger alone.

Canonicalization — the ONLY definition of taskCall_sha256, recorded
verbatim in every entry as `canonicalization` so a verifier never has to
guess which dump produced a digest:

    json.dumps(taskCall, sort_keys=True, separators=(',',':'),
               ensure_ascii=False).encode('utf-8')

Policy identity — every ledger entry carries `policy`:

    {path, sha256, version, policy_version, band}

where `path` is ENV_BINDINGS["UFO_CONFIG_PATH"], `sha256` is the digest
of the policy file bytes read at record time, `version` is parsed from
the policy note carrying "hyaku campaign policy vN" — the note at
sighting.dispatch.swarm.note first, then the first matching `note`
string anywhere in the document — and `band` is {waveMinLanes,
waveMaxLanes, maxLanes} from sighting.dispatch.swarm. `policy_version`
is the same value under the defect-1a field name. When the file is
unreadable or unparseable the affected fields are null; sha256 is still
recorded whenever the bytes could be read.

Mode 1 — wave run receipt:

    dispatch-provenance.py --spec PATH --out LEDGER.json \\
        [--timeout SECONDS] [--write-validation VALIDATION.json]

Runs exactly:

    node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs \\
        run --spec PATH

with exactly these three bindings added to the inherited environment:

    UFO_CONFIG_PATH=/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json
    UFO_FLEET_ALLOW_EXTERNAL_TOOLS=1
    UFO_PROJECT_ROOT=/home/vgpnk/Projects/shokunin/kama-shokunin

and appends a `wave_run` entry recording argv, cwd, ONLY those three
env bindings (never the rest of the environment), child exit code,
stdout/stderr sha256 + byte counts, spec sha256, the canonical
taskCall_sha256, dispatch counts, the policy block, and started/ended
UTC. Exit status is the child's exit status. --write-validation also
writes this run's validation.json (mode 3 shape).

Mode 2 — attempt receipt:

    dispatch-provenance.py --attempt-result PATH --label refused|spawned \\
        --out LEDGER.json

Appends an `attempt` entry: {label, at UTC, result_sha256, result_bytes,
parseable, policy, canonicalization, refused, spawned, spawned_method,
spawned_methods} plus `bound_task_call_sha256` copied from the most
recent `wave_run` entry — so an attempt is tied to the same taskCall
digest that produced it.

`refused` retains the round-16 legacy tally (keys literally "refused" or
"spawned" carrying ints, and "status"/"state" fields with those exact
string values). If a result text contains task-specific `Background job
limit reached (N)` messages, `refused` instead counts distinct task labels
in those messages; this text observation takes precedence to avoid adding
the same refusals twice when both representations occur. Otherwise the
legacy tally is used.

`spawned` is resolved for OMP async task results, whose members are
`pending` progress rows rather than a count key. Methods, in precedence
order; the first observed wins and is named in `spawned_method`, while
every observed per-method value is kept in `spawned_methods`:

    1. omp_text_spawned_header — "Spawned N background agents" in any
       "text" string of the result JSON;
    2. omp_text_member_bullets — "- `Name` (job ...)" member bullet
       lines in the same texts;
    3. omp_progress_members — rows of a "progress" list whose elements
       all carry "id" and "status";
    4. omp_progress_pending — the subset of those rows with status
       "pending";
    5. key_status_tally — the legacy tally, only when positive.

A non-JSON result file is still scanned as raw text for refusal messages,
the spawn header and bullet patterns (round-16 results were stored as the
JSON wrapper {"at", "result": {"text", "details": {"progress": [...]}}};
a bare text dump is scanned too). A parseable result with no observations
yields refused 0 and spawned 0 / spawned_method null; an undecodable one
yields null for counts without observations.

Mode 3 — emit a per-wave validation.json:

    dispatch-provenance.py --write-validation VALIDATION.json \\
        --out LEDGER.json

Writes, from the ledger's most recent wave_run entry plus a freshly
read policy block:

    {argv, cwd, env_bindings, exit, stdout_sha256, taskCall_sha256,
     canonicalization, counts, policy{path, sha256, version, band},
     recorded_at}

The file is created exclusively — an existing path is refused, never
clobbered.

Mode 4 — --selftest: in-memory + tempdir fixtures covering (a)-(d);
runs no wave and reads no real spec or policy. Exit 0 when every check
passes, 1 otherwise.

The ledger is a single JSON object {schema, entries:[...]} written
atomically (tempfile + os.replace). Schema is
dispatch-provenance-ledger-v2; v1 ledgers are accepted for appending
and keep their v1 tag on write so round-16 ledgers remain usable (e.g.
backfilling the falsify validation.json). An existing file with any
other schema or unparseable JSON is refused, never clobbered.

Stdlib only. No other reads, no network, no environment capture beyond
ENV_BINDINGS.
"""

import argparse
import hashlib
import json
import os
import re
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
    "UFO_PROJECT_ROOT": "/home/vgpnk/Projects/shokunin/kama-shokunin",
}

POLICY_PATH = ENV_BINDINGS["UFO_CONFIG_PATH"]

LEDGER_SCHEMA = "dispatch-provenance-ledger-v2"
# v1 ledgers stay appendable: a round-16 ledger can still receive the
# backfilled falsify validation via mode 3.
LEDGER_SCHEMAS = {LEDGER_SCHEMA, "dispatch-provenance-ledger-v1"}
TOOL = "dispatch-provenance.py"

# The single taskCall canonicalization (routed defect 1b). Recorded
# verbatim in entries and validation files; the build wave's L1-recorded
# validation.json uses this same literal.
CANONICALIZATION = (
    "json.dumps(taskCall, sort_keys=True, separators=(',',':'), "
    "ensure_ascii=False).encode('utf-8')")

# Policy note location and version phrase (defect 1a).
POLICY_VERSION_RE = re.compile(r"hyaku campaign policy (v\d+)")
# OMP async task-result spawn markers (defect 1c).
SPAWN_HEADER_RE = re.compile(r"Spawned (\d+) background agents")
SPAWN_BULLET_RE = re.compile(r"^\s*-\s*`[^`]+`\s*\(job\b", re.M)

REFUSED_TASK_RE = re.compile(
    r"(?:^|[;:]\s*)([^;:\n]+):\s*Background job limit reached \(\d+\)")
SPAWN_METHODS = (
    "omp_text_spawned_header",
    "omp_text_member_bullets",
    "omp_progress_members",
    "omp_progress_pending",
    "key_status_tally",
)

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
    """sha256 of the ONE canonicalization in CANONICALIZATION."""
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")
    return sha256_bytes(blob)


# --- policy identity (defect 1a) ------------------------------------------

def _note_version(node):
    """First 'hyaku campaign policy vN' in any dict's 'note' string,
    depth-first in document order. None when absent."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "note" and isinstance(value, str):
                match = POLICY_VERSION_RE.search(value)
                if match:
                    return match.group(1)
            found = _note_version(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = _note_version(item)
            if found is not None:
                return found
    return None


def _dig(node, *keys):
    for key in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(key)
    return node


def parse_policy(raw):
    """Return {sha256, version, band} for policy file bytes. Never
    raises: unparseable bytes yield null version and band."""
    block = {"sha256": sha256_bytes(raw), "version": None, "band": None}
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return block
    swarm = _dig(doc, "sighting", "dispatch", "swarm")
    if not isinstance(swarm, dict):
        swarm = {}
    block["band"] = {
        "waveMinLanes": swarm.get("waveMinLanes"),
        "waveMaxLanes": swarm.get("waveMaxLanes"),
        "maxLanes": swarm.get("maxLanes"),
    }
    note = swarm.get("note")
    if isinstance(note, str):
        match = POLICY_VERSION_RE.search(note)
        if match:
            block["version"] = match.group(1)
    if block["version"] is None:
        # Fallback: first matching note anywhere in the document.
        block["version"] = _note_version(doc)
    return block


def load_policy(path=POLICY_PATH):
    """Read the policy file and return the entry block:
    {path, sha256, version, policy_version, band}. Nulls on failure."""
    block = {"path": path, "sha256": None, "version": None,
             "policy_version": None, "band": None}
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError:
        return block
    parsed = parse_policy(raw)
    block["sha256"] = parsed["sha256"]
    block["version"] = parsed["version"]
    block["policy_version"] = parsed["version"]
    block["band"] = parsed["band"]
    return block


def load_ledger(path):
    """Return ledger dict. Missing file -> fresh v2 skeleton. Existing
    v1/v2 accepted (tag preserved); anything else is refused."""
    if not os.path.exists(path):
        return {"schema": LEDGER_SCHEMA, "entries": []}
    try:
        with open(path, "rb") as fh:
            doc = json.loads(fh.read().decode("utf-8"))
    except (OSError, ValueError, UnicodeDecodeError) as exc:
        sys.stderr.write("%s: ledger %s unreadable/unparseable: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_USAGE)
    if not isinstance(doc, dict) \
            or doc.get("schema") not in LEDGER_SCHEMAS \
            or not isinstance(doc.get("entries"), list):
        sys.stderr.write(
            "%s: ledger %s has unexpected schema %r (accepted: %s); "
            "refusing to clobber\n"
            % (TOOL, path, doc.get("schema") if isinstance(doc, dict)
               else type(doc).__name__,
               ", ".join(sorted(LEDGER_SCHEMAS))))
        sys.exit(EX_USAGE)
    return doc


def write_ledger(path, doc):
    """Atomic replace via tempfile + os.replace; fsync before rename."""
    blob = (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    directory = os.path.dirname(os.path.abspath(path))
    try:
        fd, tmp = tempfile.mkstemp(dir=directory, prefix=".ledger-", suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(blob)
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp, path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    except OSError as exc:
        sys.stderr.write("%s: cannot write ledger %s: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_IOERR)


def write_validation_file(path, doc):
    """Exclusive-create write for a validation receipt. An existing
    path raises FileExistsError — receipts are never clobbered."""
    blob = (json.dumps(doc, indent=1, ensure_ascii=False) + "\n").encode("utf-8")
    directory = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".validation-",
                               suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(blob)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            raise
        os.unlink(tmp)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def last_wave_run(entries):
    for entry in reversed(entries):
        if isinstance(entry, dict) and entry.get("kind") == "wave_run":
            return entry
    return None


# Task-specific "Background job limit reached (N)" text overrides the
# legacy refused tally and counts distinct labels. Without that observation,
# refused keeps the round-16 tally: integer "refused"/"spawned" fields plus
# exact "status"/"state" values. `spawned` is resolved separately for OMP
# async task results (defect 1c): members arrive as `pending` progress rows
# plus a "Spawned N background agents" text, not a `spawned` count key — the
# round-16 tally therefore recorded 0 for 79 spawned seats.

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


def _iter_texts(node):
    """Yield every string value stored under a 'text' key."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "text" and isinstance(value, str):
                yield value
            else:
                yield from _iter_texts(value)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_texts(item)


def refused_observations(result_json, raw_text):
    """Return distinct task labels with a background-job-limit refusal."""
    texts = list(_iter_texts(result_json)) if result_json is not None else []
    if not texts and raw_text is not None:
        texts = [raw_text]
    return {
        match.group(1).strip()
        for text in texts
        for match in REFUSED_TASK_RE.finditer(text)
        if match.group(1).strip()
    }


def _progress_lists(node, out):
    """Collect 'progress' lists whose elements are all dicts carrying
    'id' and 'status' — the OMP per-member progress shape."""
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "progress" and isinstance(value, list) and value \
                    and all(isinstance(e, dict) and "id" in e
                            and "status" in e for e in value):
                out.append(value)
            else:
                _progress_lists(value, out)
    elif isinstance(node, list):
        for item in node:
            _progress_lists(item, out)


def spawned_observations(result_json, raw_text):
    """Return {method: count} for each spawn evidence found. result_json
    is the parsed result (or None); raw_text a UTF-8 fallback scan."""
    obs = {}
    texts = list(_iter_texts(result_json)) if result_json is not None else []
    if not texts and raw_text is not None:
        texts = [raw_text]
    header = None
    bullets = 0
    for text in texts:
        match = SPAWN_HEADER_RE.search(text)
        if match:
            header = max(header or 0, int(match.group(1)))
        bullets = max(bullets, len(SPAWN_BULLET_RE.findall(text)))
    if header is not None:
        obs["omp_text_spawned_header"] = header
    if bullets:
        obs["omp_text_member_bullets"] = bullets
    if result_json is not None:
        lists = []
        _progress_lists(result_json, lists)
        if lists:
            obs["omp_progress_members"] = max(len(rows) for rows in lists)
            pending = max(
                sum(1 for e in rows if e.get("status") == "pending")
                for rows in lists)
            if pending:
                obs["omp_progress_pending"] = pending
    return obs


def resolve_spawned(obs, tally_spawned):
    """Pick the spawned total by method precedence. tally_spawned is the
    legacy tally (None when the result was unparseable)."""
    for method in SPAWN_METHODS[:-1]:
        if method in obs:
            return obs[method], method
    if tally_spawned:
        return tally_spawned, "key_status_tally"
    if tally_spawned is not None:
        return 0, None
    return None, None


def parse_attempt_result(raw):
    """Return (parseable, detail) for attempt-result bytes. detail
    carries refused/spawned/spawned_method/spawned_methods."""
    result_json = None
    raw_text = None
    parseable = False
    try:
        result_json = json.loads(raw.decode("utf-8"))
        parseable = True
    except (ValueError, UnicodeDecodeError):
        pass
    if not parseable:
        try:
            raw_text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raw_text = None
    tally = extract_counts(result_json) if parseable \
        else {"refused": None, "spawned": None}
    refused_tasks = refused_observations(result_json, raw_text)
    refused = len(refused_tasks) if refused_tasks else tally["refused"]
    obs = spawned_observations(result_json, raw_text)
    spawned, method = resolve_spawned(obs, tally["spawned"])
    detail = {
        "refused": refused,
        "spawned": spawned,
        "spawned_method": method,
        "spawned_methods": obs,
    }
    return parseable, detail


def build_attempt_entry(raw, label, path, entries, policy):
    """Pure entry construction for an attempt (selftest-covered)."""
    parseable, detail = parse_attempt_result(raw)
    bound = last_wave_run(entries)
    bound_index = None
    if bound is not None:
        bound_index = len(entries) - 1 - entries[::-1].index(bound)
    return {
        "kind": "attempt",
        "label": label,
        "at": utc_now(),
        "attempt_result": os.path.abspath(path),
        "result_sha256": sha256_bytes(raw),
        "result_bytes": len(raw),
        "parseable": parseable,
        "canonicalization": CANONICALIZATION,
        "policy": policy,
        "refused": detail["refused"],
        "spawned": detail["spawned"],
        "spawned_method": detail["spawned_method"],
        "spawned_methods": detail["spawned_methods"],
        # Ties this attempt to the wave_run entry whose taskCall digest
        # minted the payload the operator tried to issue. Null when the
        # ledger has no prior run (recorded, not silently dropped).
        "bound_task_call_sha256":
            bound["taskCall_sha256"] if bound is not None else None,
        "bound_run_index": bound_index,
    }


def build_run_entry(argv, spec, spec_sha256, started, ended, exit_code,
                    spawn_error, stdout, stderr, policy):
    """Pure entry construction for a wave run (selftest-covered)."""
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

    return {
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
        # Canonical digest of stdout JSON taskCall under the ONE
        # canonicalization (null when absent or stdout unparseable —
        # distinguish via stdout_parseable).
        "taskCall_sha256": canonical_sha256(task_call),
        "canonicalization": CANONICALIZATION,
        "policy": policy,
        "counts": counts,
    }


def build_validation(entry, policy):
    """Per-wave validation.json object (defect 1d): exactly the required
    key set; policy restricted to {path, sha256, version, band}."""
    return {
        "argv": list(entry["argv"]),
        "cwd": entry["cwd"],
        "env_bindings": dict(entry["env_bindings"]),
        "exit": entry["exit"],
        "stdout_sha256": entry["stdout_sha256"],
        "taskCall_sha256": entry["taskCall_sha256"],
        "canonicalization": CANONICALIZATION,
        "counts": entry["counts"],
        "policy": {key: policy.get(key)
                   for key in ("path", "sha256", "version", "band")},
        "recorded_at": utc_now(),
    }


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

    # Read the policy the child will bind before dispatch so the digest
    # names the configuration actually in force.
    policy = load_policy()
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

    entry = build_run_entry(argv, spec, spec_sha256, started, ended,
                            exit_code, spawn_error, stdout, stderr,
                            policy)
    ledger = load_ledger(args.out)
    ledger["entries"].append(entry)
    write_ledger(args.out, ledger)

    if args.write_validation:
        _write_validation(args.write_validation,
                          build_validation(entry, policy))

    sys.stderr.write(
        "%s: wave_run recorded in %s (exit=%s taskCall=%s)\n"
        % (TOOL, args.out,
           "spawn-error" if spawn_error else exit_code,
           entry["taskCall_sha256"][:16]))
    if spawn_error is not None:
        sys.exit(EX_SOFTWARE)
    sys.exit(exit_code)


def _write_validation(path, validation):
    try:
        write_validation_file(path, validation)
    except FileExistsError:
        sys.stderr.write("%s: validation %s exists; refusing to "
                         "clobber\n" % (TOOL, path))
        sys.exit(EX_USAGE)
    except OSError as exc:
        sys.stderr.write("%s: cannot write validation %s: %s\n"
                         % (TOOL, path, exc))
        sys.exit(EX_IOERR)
    sys.stderr.write("%s: validation written to %s\n" % (TOOL, path))


def cmd_attempt(args):
    try:
        with open(args.attempt_result, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        sys.stderr.write("%s: cannot read attempt result %s: %s\n"
                         % (TOOL, args.attempt_result, exc))
        sys.exit(EX_IOERR)

    policy = load_policy()
    ledger = load_ledger(args.out)
    entry = build_attempt_entry(raw, args.label, args.attempt_result,
                                ledger["entries"], policy)
    ledger["entries"].append(entry)
    write_ledger(args.out, ledger)

    sys.stderr.write(
        "%s: attempt '%s' recorded in %s (result=%s spawned=%s via %s "
        "bound=%s)\n"
        % (TOOL, args.label, args.out, entry["result_sha256"][:16],
           entry["spawned"], entry["spawned_method"],
           (entry["bound_task_call_sha256"] or "none")[:16]))
    sys.exit(0)


def cmd_emit_validation(args):
    ledger = load_ledger(args.out)
    run = last_wave_run(ledger["entries"])
    if run is None:
        sys.stderr.write("%s: ledger %s has no wave_run entry\n"
                         % (TOOL, args.out))
        sys.exit(EX_USAGE)
    _write_validation(args.write_validation,
                      build_validation(run, load_policy()))
    sys.exit(0)


# --- selftest (defect 1a-1d, in-memory + tempdir fixtures) ----------------

def _selftest():
    checks = []

    def check(name, cond, detail=""):
        checks.append((name, bool(cond), detail))

    # (b) canonicalization — the literal formula, pinned.
    obj = {"b": 1, "a": "é", "c": [3, {"z": None, "y": 2}]}
    expect = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=False).encode("utf-8")).hexdigest()
    check("canonical_sha256 matches documented formula",
          canonical_sha256(obj) == expect)
    ascii_digest = hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":"),
                   ensure_ascii=True).encode("utf-8")).hexdigest()
    check("canonicalization is ensure_ascii=False",
          canonical_sha256(obj) != ascii_digest)

    # (a) policy parsing — version, band, sha256; null paths.
    policy_raw = json.dumps({
        "sighting": {"dispatch": {"swarm": {
            "maxLanes": 9,
            "note": "hyaku campaign policy v9 (fixture)",
            "waveMinLanes": 4,
            "waveMaxLanes": 7}}}}).encode("utf-8")
    parsed = parse_policy(policy_raw)
    check("policy version parsed from swarm note",
          parsed["version"] == "v9")
    check("policy band extracted",
          parsed["band"] == {"waveMinLanes": 4, "waveMaxLanes": 7,
                             "maxLanes": 9})
    check("policy sha256 recorded",
          parsed["sha256"] == sha256_bytes(policy_raw))
    no_version = parse_policy(json.dumps(
        {"sighting": {"dispatch": {"swarm": {"maxLanes": 1,
                                            "note": "no phrase here"}}}}
    ).encode("utf-8"))
    check("policy version null when phrase absent",
          no_version["version"] is None)
    fallback = parse_policy(json.dumps(
        {"other": {"note": "hyaku campaign policy v3 elsewhere"}}
    ).encode("utf-8"))
    check("policy version fallback finds any note",
          fallback["version"] == "v3")
    bad = parse_policy(b"not json")
    check("unparseable policy keeps sha256, nulls rest",
          bad["sha256"] == sha256_bytes(b"not json")
          and bad["version"] is None and bad["band"] is None)

    with tempfile.TemporaryDirectory(prefix="dispatch-prov-selftest-") \
            as tmp:
        policy_file = os.path.join(tmp, "policy.json")
        with open(policy_file, "wb") as fh:
            fh.write(policy_raw)
        block = load_policy(policy_file)
        check("load_policy records path+version+policy_version",
              block["path"] == policy_file
              and block["version"] == "v9"
              and block["policy_version"] == "v9")
        missing = load_policy(os.path.join(tmp, "absent.json"))
        check("load_policy missing file -> null identity",
              missing["sha256"] is None and missing["version"] is None)

    # Refused task-call text; duplicate labels count once.
    refusal_text = (
        "Failed to start background task jobs: Seat-0: Background job "
        "limit reached (100). Wait for running jobs to finish or cancel "
        "one.; Seat-1: Background job limit reached (100). Wait for "
        "running jobs to finish or cancel one.; Seat-0: Background job "
        "limit reached (100). Wait for running jobs to finish or cancel one.")
    refusal_only = json.dumps(
        {"result": {"text": refusal_text}}).encode("utf-8")
    parseable, detail = parse_attempt_result(refusal_only)
    check("refused text counts distinct task labels",
          parseable and detail["refused"] == 2 and detail["spawned"] == 0)

    mixed_text = refusal_text + "\nSpawned 3 background agents using executor."
    mixed = json.dumps({"result": {"text": mixed_text}}).encode("utf-8")
    parseable, detail = parse_attempt_result(mixed)
    check("mixed refused and spawned observations",
          parseable and detail["refused"] == 2 and detail["spawned"] == 3)

    # (c) spawned counting — OMP async result shapes.
    member_rows = [{"id": "Seat-%d" % i, "status": "pending"}
                   for i in range(3)]
    spawn_text = ("Spawned 3 background agents using executor.\n"
                  "- `Seat-0` (job `Seat-0`)\n"
                  "- `Seat-1` (job `Seat-1`)\n"
                  "- `Seat-2` (job `Seat-2`)\n\n"
                  "Coordinate: 3 siblings are running together.")
    wrapped = json.dumps({
        "at": "2026-10-20T00:00:00Z",
        "result": {"text": spawn_text,
                   "details": {"progress": member_rows,
                               "async": {"state": "running"}}},
    }).encode("utf-8")
    parseable, detail = parse_attempt_result(wrapped)
    check("wrapped async result parseable", parseable)
    check("spawned total from header",
          detail["spawned"] == 3
          and detail["spawned_method"] == "omp_text_spawned_header")
    check("all methods observed",
          detail["spawned_methods"].get("omp_text_member_bullets") == 3
          and detail["spawned_methods"].get("omp_progress_members") == 3
          and detail["spawned_methods"].get("omp_progress_pending") == 3)

    bullets_only = json.dumps({"result": {"text": (
        "Dispatched.\n- `A-1` (job `A-1`)\n- `B-1` (job `B-1`)")}}) \
        .encode("utf-8")
    _, detail = parse_attempt_result(bullets_only)
    check("spawned falls back to bullets",
          detail["spawned"] == 2
          and detail["spawned_method"] == "omp_text_member_bullets")

    progress_only = json.dumps({"details": {"progress": member_rows}}) \
        .encode("utf-8")
    _, detail = parse_attempt_result(progress_only)
    check("spawned falls back to progress members",
          detail["spawned"] == 3
          and detail["spawned_method"] == "omp_progress_members")

    _, detail = parse_attempt_result(spawn_text.encode("utf-8"))
    check("raw-text result scanned, parseable false",
          detail["spawned"] == 3
          and detail["spawned_method"] == "omp_text_spawned_header")

    _, detail = parse_attempt_result(b'{"spawned": 4, "refused": 1}')
    check("legacy tally still resolves",
          detail["spawned"] == 4
          and detail["spawned_method"] == "key_status_tally"
          and detail["refused"] == 1)

    _, detail = parse_attempt_result(b'{"results": []}')
    check("parseable-empty result -> refused/spawned 0",
          detail["refused"] == 0 and detail["spawned"] == 0
          and detail["spawned_method"] is None)

    # (a,b) run-entry construction — policy + canonicalization in entry.
    fixture_policy = {"path": "/x/policy.json", "sha256": "0" * 64,
                      "version": "v9", "policy_version": "v9",
                      "band": {"waveMinLanes": 4, "waveMaxLanes": 7,
                               "maxLanes": 9}}
    stdout = json.dumps({
        "taskCall": {"tasks": [{"a": 1}], "mode": "spawn"},
        "counts": {"spawn": 1}, "resumeSends": []}).encode("utf-8")
    entry = build_run_entry(
        ["node", "w.js", "run", "--spec", "/x/spec.json"],
        "/x/spec.json", "1" * 64, "t0", "t1", 0, None, stdout, b"",
        fixture_policy)
    task_call = {"tasks": [{"a": 1}], "mode": "spawn"}
    check("wave_run taskCall_sha256 uses single canonicalization",
          entry["taskCall_sha256"] == canonical_sha256(task_call)
          and entry["canonicalization"] == CANONICALIZATION)
    check("wave_run entry carries policy identity",
          entry["policy"]["version"] == "v9"
          and entry["policy"]["band"]["waveMinLanes"] == 4
          and entry["policy"]["sha256"] == "0" * 64)
    check("wave_run counts tasks", entry["counts"]["tasks"] == 1)

    # attempt entry binds the last wave_run and carries policy.
    attempt = build_attempt_entry(wrapped, "spawned", "/x/r.json",
                                  [entry], fixture_policy)
    check("attempt entry binds wave_run taskCall digest",
          attempt["bound_task_call_sha256"] == entry["taskCall_sha256"]
          and attempt["bound_run_index"] == 0)
    check("attempt entry carries policy + spawned detail",
          attempt["policy"]["version"] == "v9"
          and attempt["spawned"] == 3
          and attempt["spawned_method"] == "omp_text_spawned_header")

    # (d) validation emission — exact key set, policy subset.
    validation = build_validation(entry, fixture_policy)
    check("validation key set exact",
          set(validation) == {"argv", "cwd", "env_bindings", "exit",
                              "stdout_sha256", "taskCall_sha256",
                              "canonicalization", "counts", "policy",
                              "recorded_at"})
    check("validation policy key set exact",
          set(validation["policy"]) == {"path", "sha256", "version",
                                        "band"})

    with tempfile.TemporaryDirectory(prefix="dispatch-prov-selftest-") \
            as tmp:
        ledger_path = os.path.join(tmp, "ledger.json")
        write_ledger(ledger_path,
                     {"schema": LEDGER_SCHEMA, "entries": [entry]})
        # v1 ledger stays loadable.
        v1_path = os.path.join(tmp, "ledger-v1.json")
        write_ledger(v1_path,
                     {"schema": "dispatch-provenance-ledger-v1",
                      "entries": [entry]})
        doc = load_ledger(v1_path)
        check("v1 ledger accepted, tag preserved",
              doc["schema"] == "dispatch-provenance-ledger-v1")
        out = os.path.join(tmp, "validation.json")
        # Exclusive create succeeds then refuses.
        write_validation_file(out, validation)
        check("validation file written",
              os.path.isfile(out))
        refused = False
        try:
            write_validation_file(out, validation)
        except FileExistsError:
            refused = True
        check("existing validation refused, not clobbered", refused)

    failures = [c for c in checks if not c[1]]
    for name, ok, detail in checks:
        sys.stdout.write("%s %s%s\n" % ("ok" if ok else "FAIL", name,
                                        (" — " + detail) if detail
                                        else ""))
    sys.stdout.write("selftest: %d/%d checks passed\n"
                     % (len(checks) - len(failures), len(checks)))
    sys.exit(0 if not failures else 1)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog=TOOL,
        description="Wave-dispatch provenance ledger: record the exact "
                    "env bindings, argv, digests, policy identity and "
                    "counts of a ufo-swarm-wave run, bind refused/"
                    "spawned task attempts to the same taskCall digest "
                    "(one canonicalization), and emit a per-wave "
                    "validation.json.")
    parser.add_argument("--spec",
                        help="wave spec path for a wave run")
    parser.add_argument("--attempt-result",
                        help="JSON or text result file of a refused/"
                             "spawned task call to append to the ledger")
    parser.add_argument("--label", choices=["refused", "spawned"],
                        help="attempt outcome label (required with "
                             "--attempt-result)")
    parser.add_argument("--out",
                        help="ledger JSON path (created if absent; "
                             "required unless --selftest)")
    parser.add_argument("--timeout", type=float, default=300.0,
                        help="child timeout seconds for a wave run "
                             "(default 300)")
    parser.add_argument("--write-validation",
                        help="write a per-wave validation.json (with "
                             "--spec: this run; alone: from the "
                             "ledger's latest wave_run entry)")
    parser.add_argument("--selftest", action="store_true",
                        help="run in-memory fixture checks and exit")
    args = parser.parse_args(argv)

    if args.selftest:
        _selftest()

    def _need_out():
        if args.out is None:
            parser.error("--out LEDGER.json is required for this mode")

    if args.attempt_result is not None:
        if args.spec is not None:
            parser.error("--spec and --attempt-result are mutually "
                         "exclusive")
        if args.write_validation is not None:
            parser.error("--write-validation is only valid for wave "
                         "runs or ledger re-emission")
        if args.label is None:
            parser.error("--attempt-result requires --label "
                         "refused|spawned")
        _need_out()
        cmd_attempt(args)
    elif args.spec is not None:
        if args.label is not None:
            parser.error("--label is only valid with --attempt-result")
        _need_out()
        cmd_run(args)
    elif args.write_validation is not None:
        if args.label is not None:
            parser.error("--label is only valid with --attempt-result")
        _need_out()
        cmd_emit_validation(args)
    else:
        parser.error("one of --spec, --attempt-result, "
                     "--write-validation or --selftest is required")


if __name__ == "__main__":
    main()
