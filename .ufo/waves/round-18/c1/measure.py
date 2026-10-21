#!/usr/bin/env python3
"""measure.py — kama round-18 C1 counting command (L1 runs it; seats never).

Counts the four numbers the round-18 C1 operability claim declares —
``accepted_bad``, ``good_rejected``, ``misclassified`` and
``uncontrolled_checks`` — on the FROZEN tool+gate (before) and on the
CURRENT tool+gate (after). ONE controls.py grades both sides, so the graded
pair is the only difference between the two runs.

    measure.py --controls PATH --frozen-tool PATH --frozen-gate PATH \\
               --tool PATH --gate PATH [--probe PATH] [--json] [--out PATH]
    measure.py --self-mutants --controls PATH --tool PATH --gate PATH \\
               [--frozen-tool PATH --frozen-gate PATH] [--probe PATH] \\
               [--mutant NAME ...] [--baseline-runs N] [--json] [--out PATH]
    measure.py --selftest

Measurement mode
----------------
1. Every input (this script, controls, both tools, both gates, probe and the
   resolved controls registry/endpoint-consumers.tsv) is SHA-256 hashed.
   Each frozen input MUST match the exact bytes at
   ``git -C LANE show e75cf680b53484a61709ee1b2787d8dbc6419f74:<path>``;
   unverifiable or mismatching frozen bytes exit 2 before controls run.
   Byte-identical frozen/current pairs are flagged (before == after).
2. ``python3 CONTROLS --tool T --gate G --probe P --json`` runs once per
   side, serially (one fake server at a time): before = frozen pair, after
   = current pair. Each run gets its own session, PYTHONDONTWRITEBYTECODE=1,
   stdin /dev/null and TMPDIR = a fresh scratch dir; on timeout its process
   group is SIGKILLed. Afterwards every process whose /proc/<pid>/cmdline
   names that scratch dir is SIGKILLed (its group when it leads one) and
   listed in ``leaked_processes``.
3. Each run records argv, exit, duration, the raw-stdout sha256, the
   canonical-JSON sha256 (sort_keys, separators (',', ':'), UTF-8) and the
   parsed doc. The probe default is the controls' own default,
   <controls>.parents[2]/tools/kama-probe.sh; the same probe serves both
   sides.
4. Normalization (``summarize``). Shape ``reported`` (any of
   ``misclassified``/``good_rejected``/``uncontrolled_checks`` at top level
   or ``classification`` in a row — the round-18 controls contract) takes
   every count as reported; a missing count is ``null`` (not reported),
   never derived. Shape ``v1-derived`` (schema kama-live-controls/v1, the
   frozen controls) derives only what v1 states exactly: good_rejected =
   0/1 from ``good_ok`` (k0 is v1's only good control) and a per-row
   classification from accepted/inconclusive/attributed. For reported v2,
   ``misclassified`` is cross-checked against row ``bucket`` (not
   ``classification``); rows from an older reported schema without bucket
   use classification as the compatibility fallback. ``accepted_bad`` and
   ``good_rejected`` are cross-checked the same way and may not under-report
   rows (a partial projection reporting fewer bad buckets is legal and only
   noted). ``uncontrolled_checks`` stay ``null`` for v1 (no classification
   and failed checks only). An ``uncontrolled_checks`` id is removed into
   ``uncontrolled_excluded`` only when the document itself declares it in
   ``input_integrity_checks``; an undeclared label stays uncontrolled here.
   ``gate_flip_arms`` is read from the controls JSON when present, otherwise
   derived from rows whose ``gate_flip`` is an object (the arm ran); a
   reported value below the row count is a fault, above it only a note.
5. Report: before -> after for the four counts plus good_ok, gate_flip_bad,
   gate_flip_arms, inconclusive; per-control classification and bucket diffs;
   controls-JSON digests.

Self-mutants mode
-----------------
Applies each named single-site edit to a COPY of controls.py (located by
exact source-string match; the first listed alternative occurring exactly
once is applied; none -> ``site_missing``; only >1 -> ``site_ambiguous``;
non-compiling -> ``invalid_mutation``; never skipped, never counted as
survived). Baseline and mutant are staged in identical layouts that mirror
<controls>.parents[2] (every regular file beside controls.py plus
registry/endpoint-consumers.tsv when the original resolves one), so path
resolution matches between them. Detectors:
* selftest — ``--selftest`` of the copy; usable only when the unmutated
  copy exits 0; a mutant exiting nonzero is killed.
* numbers — the copy's ``--json`` run per pair (current; frozen too when
  given). The unmutated copy runs --baseline-runs times (default 2) per
  pair; a pair whose baseline runs disagree is ``unstable`` and its diffs
  are reported but never credited. Killed when the signature (controls
  exit, the four counts, good_ok, gate_flip_bad, gate_flip_arms,
  inconclusive, per-control classifications) differs or the mutant run
  faults. ``killed_by`` names the detector and every differing key, so a
  kill by measure's own gate_flip_arms coverage count is visible as such.
The original controls file is re-hashed at the end (must be unchanged).

Exit codes
----------
measurement:  0 iff the current side has accepted_bad == 0,
              good_rejected == 0, misclassified == 0 and
              uncontrolled_checks == [] (after removing model_unchanged).
              A count the controls did not report is not clean. 1 otherwise.
self-mutants: 0 iff every selected mutant is killed; 1 otherwise.
selftest:     0 pass, 1 fail.
2 (all modes): own fault — usage, missing input, frozen git-blob mismatch
              or unverifiable revision, a controls run that timed out /
              exited outside 0|1 / emitted non-JSON or malformed counts /
              exited 0 against its own counts / reported a tool_sha256 or
              gate_sha256 different from the file passed, --out onto an
              input, no usable mutant detector, an interrupt. The JSON
              report is still emitted with ``faults``.

Cannot detect: a controls.py that misreports consistently (its counts and
exit agree but are wrong); behaviour that depends on lane files other than
the registry when a mutant copy is staged; leaked processes whose cmdline
does not name the scratch dir (e.g. a daemon that re-execs elsewhere).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

SCHEMA = 'kama-c1-measure/v1'
HERE = Path(__file__).resolve()
# .ufo/waves/round-18/c1/measure.py -> lane root
DEFAULT_LANE = HERE.parents[4] if len(HERE.parents) > 4 else HERE.parent
FROZEN_REV = 'e75cf680b53484a61709ee1b2787d8dbc6419f74'   # round-18 start
FROZEN_GIT_PATHS = {'frozen_tool': 'tools/kama-llamacpp-live.py',
                    'frozen_gate': 'tests/llamacpp-live/check-receipt.py'}
V1_SCHEMA = 'kama-live-controls/v1'
EXCLUDED_UNCONTROLLED = frozenset({'model_unchanged'})
CLASSIFICATIONS = frozenset({'accepted', 'rejected-targeted',
                             'rejected-untargeted', 'not-evaluated',
                             'misclassified'})
BUCKETS = frozenset({'ok', 'accepted_bad', 'good_rejected', 'misclassified'})
CONTROLS_TIMEOUT = 3600.0   # one full controls.py run (each control <=240s)
SELFTEST_TIMEOUT = 600.0
STDERR_TAIL = 2000
MUTANT_TAG = '# c1-measure mutant'
EXIT_CLEAN, EXIT_NOT_CLEAN, EXIT_FAULT = 0, 1, 2
COUNT_KEYS = ('accepted_bad', 'good_rejected', 'misclassified',
              'uncontrolled_checks')
EXTRA_KEYS = ('good_ok', 'gate_flip_bad', 'gate_flip_arms', 'inconclusive')

# name -> (intent, alternatives). Each alternative is an exact (old, new)
# source-string pair, tried in order.
MUTANTS = {
    'drop-gate-flip-arm': (
        'the gate-flip arm never runs; every row keeps gate_flip null '
        '(round-17 MutControlsSelf (c))',
        (('gate_flip = _gate_flip(st, gate, receipt_doc, failed)',
          'gate_flip = None  ' + MUTANT_TAG),)),
    'loosen-k0-exit': (
        "K0's tool-exit predicate also accepts -15 "
        '(round-17 MutControlsSelf (d))',
        (('accepted = (tool_exit == 0 and gate_exit == 0',
          'accepted = (tool_exit in (0, -15) and gate_exit == 0'),)),
    'k6-any-nonzero': (
        'K6 (exit spec (2,)) accepts any nonzero tool exit, the frozen K6 '
        'rule; the site is the shared exit predicate, so every control '
        'with an exit spec is loosened alike',
        (('exit_ok = tool_exit in spec.exits',
          'exit_ok = tool_exit not in (0, None)'),)),
}


class MeasureFault(Exception):
    """measure.py could not take the measurement (exit 2, never a verdict)."""


# ------------------------------------------------------------ hashing / io

def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(doc):
    return sha256_bytes(json.dumps(doc, sort_keys=True, separators=(',', ':'),
                                   ensure_ascii=False).encode('utf-8'))


def utc_now():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


def file_record(label, path):
    p = Path(path)
    if not p.is_file():
        raise MeasureFault(f'{label} not found or not a regular file: {path}')
    try:
        data = p.read_bytes()
    except OSError as exc:
        raise MeasureFault(f'{label} unreadable: {path}: {exc}') from exc
    return {'path': str(p.resolve()), 'sha256': sha256_bytes(data),
            'bytes': len(data)}


def git_blob(lane, rev, path):
    """Raw bytes of rev:path in the repository at `lane`, from git show."""
    cmd = ['git', '-C', str(lane), 'show', f'{rev}:{path}']
    try:
        cp = subprocess.run(cmd, stdin=subprocess.DEVNULL,
                            capture_output=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise MeasureFault(f"{' '.join(cmd)}: {type(exc).__name__}: "
                           f'{exc}') from exc
    if cp.returncode != 0:
        err = cp.stderr.decode('utf-8', 'replace').strip()[-200:]
        raise MeasureFault(f"{' '.join(cmd)} exited {cp.returncode}: {err}")
    return cp.stdout


def frozen_pin(label, rec, lane, rev):
    """(pin, faults): a frozen input must equal git rev:<its lane path>
    byte-for-byte; an unverifiable pin is a fault too (refusal)."""
    gpath = FROZEN_GIT_PATHS[label]
    pin = {'git_lane': str(lane), 'git_rev': rev, 'git_path': gpath,
           'git_blob_sha256': None, 'git_blob_bytes': None,
           'verified': None}
    try:
        blob = git_blob(lane, rev, gpath)
        local = Path(rec['path']).read_bytes()
    except (MeasureFault, OSError) as exc:
        return pin, [f'{label}: cannot verify exact frozen bytes: {exc}']
    pin.update(git_blob_sha256=sha256_bytes(blob), git_blob_bytes=len(blob))
    pin['verified'] = (local == blob and sha256_bytes(local) == rec['sha256']
                       and len(local) == rec['bytes'])
    if pin['verified']:
        return pin, []
    return pin, [f"{label} {rec['path']} sha256 {sha256_bytes(local)} != git "
                 f"{rev}:{gpath} sha256 {pin['git_blob_sha256']}"]


def write_atomic(path, text):
    out = Path(path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=out.name + '.', dir=str(out.parent))
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            fh.write(text)
        os.replace(tmp, out)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ------------------------------------------------------------- processes

def _killpg(pgid):
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def reap_scratch(root):
    """SIGKILL every process whose argv names `root` (or a path under it).

    Called only after the run that owned `root` has been waited on, so any
    match outlived its run. A process leading its own group (the tool's
    start_new_session child) is killed by group. Returns [{pid, argv0,
    killed}] — argv0 basename only, never the full command line."""
    root_b = os.fsencode(str(root))
    me, my_pgrp = os.getpid(), os.getpgrp()
    found = []
    try:
        pids = [int(n) for n in os.listdir('/proc') if n.isdigit()]
    except OSError:
        return found
    for pid in pids:
        if pid == me:
            continue
        try:
            with open(f'/proc/{pid}/cmdline', 'rb') as fh:
                raw = fh.read()
        except OSError:
            continue
        args = raw.split(b'\0')
        if not any(a == root_b or a.startswith(root_b + b'/')
                   or (root_b + b'/') in a for a in args):
            continue
        entry = {'pid': pid,
                 'argv0': os.path.basename(os.fsdecode(args[0])),
                 'killed': False}
        try:
            pgid = os.getpgid(pid)
            if pgid == pid and pgid != my_pgrp:
                os.killpg(pgid, signal.SIGKILL)
            else:
                os.kill(pid, signal.SIGKILL)
            entry['killed'] = True
        except ProcessLookupError:
            continue      # exited between the scan and the kill
        except OSError as exc:
            entry['error'] = type(exc).__name__
        found.append(entry)
    deadline = time.monotonic() + 3.0
    for entry in found:
        while time.monotonic() < deadline and _alive(entry['pid']):
            time.sleep(0.05)
        entry['gone'] = not _alive(entry['pid'])
    return found


def _alive(pid):
    """False for gone or zombie pids."""
    try:
        with open(f'/proc/{pid}/stat', 'rb') as fh:
            stat = fh.read()
    except OSError:
        return False
    try:
        return stat[stat.rindex(b')') + 2:][:1] != b'Z'
    except ValueError:
        return False


def run_child(cmd, cwd, env, timeout):
    """Run cmd in its own session; SIGKILL its group on timeout or on an
    interrupt of this process. Never raises for child misbehaviour."""
    obs = {'argv': [str(c) for c in cmd], 'exit': None, 'timed_out': False,
           'spawn_error': None, 'stdout': b'', 'stderr': b''}
    start = time.monotonic()
    try:
        proc = subprocess.Popen(cmd, cwd=cwd, env=env,
                                stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                start_new_session=True)
    except OSError as exc:
        obs['spawn_error'] = f'{type(exc).__name__}: {exc}'
        obs['duration_s'] = round(time.monotonic() - start, 3)
        return obs
    try:
        out, err = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        obs['timed_out'] = True
        _killpg(proc.pid)
        try:
            out, err = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()   # a pipe holder outside the group; reap_scratch
            out, err = b'', b''
    except BaseException:
        _killpg(proc.pid)
        proc.wait()
        raise
    obs['stdout'], obs['stderr'] = out or b'', err or b''
    obs['exit'] = proc.returncode
    obs['duration_s'] = round(time.monotonic() - start, 3)
    return obs


def child_env(tmpdir):
    env = dict(os.environ)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env['TMPDIR'] = str(tmpdir)
    return env


def run_controls(controls, tool, gate, probe, scratch, label, timeout):
    """One `controls.py --json` run; returns the run record (never raises
    for a misbehaving controls)."""
    rundir = Path(tempfile.mkdtemp(prefix=f'{label}-', dir=str(scratch)))
    cmd = [sys.executable, str(controls), '--tool', str(tool),
           '--gate', str(gate), '--probe', str(probe), '--json']
    try:
        obs = run_child(cmd, cwd=str(rundir), env=child_env(rundir),
                        timeout=timeout)
    finally:
        leaked = reap_scratch(rundir)
    rec = {'label': label, 'argv': obs['argv'], 'exit': obs['exit'],
           'timed_out': obs['timed_out'], 'spawn_error': obs['spawn_error'],
           'duration_s': obs['duration_s'],
           'stdout_sha256': sha256_bytes(obs['stdout']),
           'stdout_bytes': len(obs['stdout']),
           'stderr_tail': obs['stderr'][-STDERR_TAIL:].decode(
               'utf-8', 'replace'),
           'leaked_processes': leaked, 'doc': None,
           'doc_canonical_sha256': None, 'parse_error': None}
    try:
        doc = json.loads(obs['stdout'].decode('utf-8'))
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        rec['parse_error'] = f'{type(exc).__name__}: {exc}'[:300]
    else:
        rec['doc'] = doc
        rec['doc_canonical_sha256'] = canonical_sha256(doc)
    shutil.rmtree(rundir, ignore_errors=True)
    return rec


def run_selftest_of(controls, scratch, label, timeout):
    rundir = Path(tempfile.mkdtemp(prefix=f'{label}-', dir=str(scratch)))
    try:
        obs = run_child([sys.executable, str(controls), '--selftest'],
                        cwd=str(rundir), env=child_env(rundir),
                        timeout=timeout)
    finally:
        leaked = reap_scratch(rundir)
    shutil.rmtree(rundir, ignore_errors=True)
    return {'argv': obs['argv'], 'exit': obs['exit'],
            'timed_out': obs['timed_out'], 'spawn_error': obs['spawn_error'],
            'duration_s': obs['duration_s'],
            'stdout_tail': obs['stdout'][-600:].decode('utf-8', 'replace'),
            'stderr_tail': obs['stderr'][-600:].decode('utf-8', 'replace'),
            'leaked_processes': leaked}


def run_faults(rec):
    """Reasons a controls run cannot be graded (exit 2 material)."""
    faults = []
    if rec['spawn_error']:
        faults.append(f"spawn failed: {rec['spawn_error']}")
    if rec['timed_out']:
        faults.append('timed out; process group killed')
    elif rec['exit'] not in (0, 1):
        faults.append(f"controls exit {rec['exit']} (0|1 expected; 2 is its "
                      'own fault)')
    if rec['doc'] is None:
        faults.append(f"stdout is not JSON ({rec['parse_error']})")
    elif not isinstance(rec['doc'], dict):
        faults.append('stdout JSON is not an object')
    return faults


# ---------------------------------------------------------- normalization

def _v1_classification(row):
    if row.get('id') == 'k0':
        return 'accepted' if row.get('accepted') is True else 'rejected'
    if row.get('accepted') is True:
        return 'accepted'
    if row.get('inconclusive') is True:
        return 'rejected-untargeted'
    if row.get('attributed') is True:
        return 'rejected-targeted'
    return 'rejected'       # rejected, no attribution expected (v1 K7)


def _count(doc, key, faults):
    if key not in doc:
        return None
    val = doc[key]
    if isinstance(val, bool) or not isinstance(val, int) or val < 0:
        faults.append(f'{key} is not a non-negative integer: {val!r}')
        return None
    return val


def summarize(doc, controls_exit):
    """(summary, faults, notes) for one parsed controls doc."""
    faults, notes = [], []
    rows_in = doc.get('controls')
    if not isinstance(rows_in, list) \
            or not all(isinstance(r, dict) for r in rows_in):
        faults.append("'controls' is not a list of objects")
        rows_in = []
    if any(k in doc for k in ('misclassified', 'good_rejected',
                              'uncontrolled_checks')) \
            or any('classification' in r for r in rows_in):
        shape = 'reported'
    elif doc.get('schema') == V1_SCHEMA:
        shape = 'v1-derived'
    else:
        shape = None
        faults.append(f"unknown controls output shape: schema "
                      f"{doc.get('schema')!r} and no classification keys")

    rows, order, flip_seen, flip_arms = {}, [], False, 0
    for r in rows_in:
        cid = r.get('id')
        if not isinstance(cid, str) or not cid:
            faults.append(f'row without a string id: {cid!r}')
            continue
        if cid in rows:
            faults.append(f'duplicate control id {cid}')
            continue
        if shape == 'v1-derived':
            cls, src = _v1_classification(r), 'derived-v1'
            targeted = r.get('expected_failed')
            bucket = None
            bucket_source = 'v1-unavailable'
        else:
            cls = r.get('classification')
            if cls not in CLASSIFICATIONS:
                faults.append(f'{cid}: invalid or missing classification '
                              f'{cls!r}')
                cls = None
                src = None
            else:
                src = 'reported'
            targeted = r.get('targeted')
            if not isinstance(targeted, list) \
                    or not all(isinstance(x, str) for x in targeted):
                faults.append(f'{cid}: targeted is not a list of strings')
            targeted_hit = r.get('targeted_hit')
            if not (isinstance(targeted_hit, bool) or targeted_hit is None):
                faults.append(f'{cid}: targeted_hit is not boolean/null')
            if 'bucket' in r:
                bucket = r['bucket']
                if bucket not in BUCKETS:
                    faults.append(f'{cid}: invalid bucket {bucket!r}')
                    bucket = None
                    bucket_source = 'invalid'
                else:
                    bucket_source = 'reported'
            else:
                bucket = None
                bucket_source = 'classification-fallback'
        failed = r.get('failed_checks')
        if not isinstance(failed, list) \
                or not all(isinstance(x, str) for x in failed):
            faults.append(f'{cid}: failed_checks is not a list of strings')
            failed_checks = None
        else:
            failed_checks = failed
        ran = None
        if 'gate_flip' in r:
            flip_seen = True
            ran = isinstance(r['gate_flip'], dict)
            flip_arms += int(ran)
        rows[cid] = {
            'classification': cls, 'classification_source': src,
            'bucket': bucket,
            'bucket_source': bucket_source,
            'expected': r.get('expected'), 'targeted': targeted,
            'targeted_hit': r.get('targeted_hit') if shape == 'reported'
            else None,
            'failed_checks': failed_checks,
            'tool_exit': r.get('tool_exit'), 'gate_exit': r.get('gate_exit'),
            'gate_flip_ran': ran,
            'gate_flip_accepted': (r['gate_flip'].get('accepted')
                                   if isinstance(r.get('gate_flip'), dict)
                                   else None)}
        order.append(cid)

    good_ok = doc.get('good_ok')
    if not (isinstance(good_ok, bool) or good_ok is None):
        faults.append(f'good_ok is not a boolean: {good_ok!r}')
        good_ok = None
    accepted_bad = _count(doc, 'accepted_bad', faults)
    gate_flip_bad = _count(doc, 'gate_flip_bad', faults)
    inconclusive = _count(doc, 'inconclusive', faults)
    gate_flip_arms = _count(doc, 'gate_flip_arms', faults)
    if gate_flip_arms is not None:
        arms_source = 'reported'
        if gate_flip_arms < flip_arms:
            faults.append(f'gate_flip_arms={gate_flip_arms} but {flip_arms} '
                          'row(s) carry a gate_flip object')
        elif gate_flip_arms > flip_arms:
            notes.append(f'gate_flip_arms={gate_flip_arms} exceeds '
                         f'{flip_arms} row(s) with a gate_flip object')
    elif flip_seen:
        gate_flip_arms, arms_source = flip_arms, 'derived:rows'
    else:
        arms_source = None
    uncontrolled, excluded = None, []
    if shape == 'v1-derived':
        good_rejected = {True: 0, False: 1}.get(good_ok)
        gr_source = 'derived:good_ok' if good_rejected is not None else None
        misclassified = None
        notes.append('misclassified: not reported by kama-live-controls/v1 '
                     '(no classification); its inconclusive count is listed '
                     'separately')
        notes.append('uncontrolled_checks: not derivable from '
                     'kama-live-controls/v1 (rows list failed checks only)')
        notes.append('good_rejected derived from good_ok (k0 is the only '
                     'v1 good control)')
    else:
        good_rejected = _count(doc, 'good_rejected', faults)
        gr_source = 'reported' if good_rejected is not None else None
        misclassified = _count(doc, 'misclassified', faults)
        raw = doc.get('uncontrolled_checks')
        if raw is not None:
            if not isinstance(raw, list) \
                    or not all(isinstance(c, str) for c in raw):
                faults.append(f'uncontrolled_checks is not a list of '
                              f'strings: {raw!r}')
            else:
                if len(raw) != len(set(raw)):
                    faults.append('uncontrolled_checks contains duplicates')
                declared = doc.get('input_integrity_checks')
                if declared is None:
                    declared = []
                elif not isinstance(declared, list) \
                        or not all(isinstance(c, str) for c in declared):
                    faults.append('input_integrity_checks is not a list of '
                                  f'strings: {declared!r}')
                    declared = []
                excluded = sorted({c for c in raw
                                   if c in EXCLUDED_UNCONTROLLED
                                   and c in declared})
                keep = set(excluded)
                undeclared = sorted({c for c in raw
                                     if c in EXCLUDED_UNCONTROLLED
                                     and c not in declared})
                if undeclared:
                    notes.append(
                        'exclusion label(s) ' + ','.join(undeclared)
                        + ' not declared in input_integrity_checks; '
                        'counted as uncontrolled')
                uncontrolled = sorted({c for c in raw if c not in keep})
        if misclassified is not None and rows:
            n, counted = 0, 0
            for row in rows.values():
                if row['bucket_source'] == 'reported':
                    counted += 1
                    n += row['bucket'] == 'misclassified'
                elif row['bucket_source'] == 'classification-fallback':
                    counted += 1
                    n += row['classification'] == 'misclassified'
            if counted == len(rows) and n != misclassified:
                faults.append(f'misclassified={misclassified} but {n} row(s) '
                              'have a misclassified outcome bucket')
        # accepted_bad and good_rejected are certified only when the child's
        # rows do not record MORE bad outcomes than it reports: a consistent
        # under-report is otherwise CLEAN. Counting is restricted to rows that
        # carry a reported bucket, so one bucket-less sibling cannot disable
        # the check; fewer rows than the certified count is legal and noted.
        bucket_rows = [row for row in rows.values()
                       if row['bucket_source'] == 'reported']
        if bucket_rows:
            n_ab = sum(1 for row in bucket_rows
                       if row['bucket'] == 'accepted_bad')
            n_flip = sum(1 for row in rows.values()
                         if row['gate_flip_accepted'] is True)
            if accepted_bad is not None and accepted_bad < n_ab + n_flip:
                faults.append(f'accepted_bad={accepted_bad} but {n_ab} '
                              f'accepted_bad bucket row(s) + {n_flip} '
                              'accepted gate-flip row(s)')
            if accepted_bad is not None and accepted_bad > n_ab + n_flip:
                notes.append(f'accepted_bad={accepted_bad} exceeds {n_ab} '
                             f'bucket + {n_flip} flip row(s)')
            n_gr = sum(1 for row in bucket_rows
                       if row['bucket'] == 'good_rejected')
            if good_rejected is not None and good_rejected < n_gr:
                faults.append(f'good_rejected={good_rejected} but {n_gr} '
                              'row(s) have a good_rejected outcome bucket')
            if good_rejected is not None and good_rejected > n_gr:
                notes.append(f'good_rejected={good_rejected} exceeds '
                             f'{n_gr} bucket row(s)')
        if good_ok is False and good_rejected == 0:
            faults.append('good_ok is false but good_rejected is 0')

    summary = {
        'shape': shape, 'schema': doc.get('schema'),
        'accepted_bad': accepted_bad, 'good_rejected': good_rejected,
        'good_rejected_source': gr_source, 'misclassified': misclassified,
        'uncontrolled_checks': uncontrolled,
        'uncontrolled_excluded': excluded,
        'good_ok': good_ok, 'gate_flip_bad': gate_flip_bad,
        'gate_flip_arms': gate_flip_arms,
        'gate_flip_arms_source': arms_source,
        'input_integrity_checks': doc.get('input_integrity_checks'),
        'inconclusive': inconclusive, 'controls_exit': controls_exit,
        'not_reported': [k for k, v in (
            ('accepted_bad', accepted_bad), ('good_rejected', good_rejected),
            ('misclassified', misclassified),
            ('uncontrolled_checks', uncontrolled)) if v is None],
        'order': order, 'rows': rows}

    if controls_exit == 0:
        dirty = [f'{k}={v}' for k, v in (
            ('accepted_bad', accepted_bad), ('misclassified', misclassified),
            ('good_rejected', good_rejected if gr_source == 'reported'
             else None)) if v]
        if shape == 'v1-derived':
            dirty += [f'{k}={v}' for k, v in (
                ('gate_flip_bad', gate_flip_bad),
                ('inconclusive', inconclusive)) if v]
        if good_ok is False:
            dirty.append('good_ok=false')
        if dirty:
            faults.append('controls exited 0 against its own counts: '
                          + ', '.join(dirty))
    return summary, faults, notes


def clean_reasons(summary):
    """Why the AFTER side fails the four requested count criteria."""
    reasons = []
    for key in ('accepted_bad', 'good_rejected', 'misclassified'):
        val = summary[key]
        if val is None:
            reasons.append(f'{key} not reported by the controls output')
        elif val != 0:
            reasons.append(f'{key}={val}')
    unc = summary['uncontrolled_checks']
    if unc is None:
        reasons.append('uncontrolled_checks not reported by the controls '
                       'output')
    elif unc:
        reasons.append('uncontrolled_checks=' + ','.join(unc))
    return reasons


def count_value(summary, key):
    val = summary.get(key)
    if key == 'uncontrolled_checks' and val is not None:
        return len(val)
    return val


def counts_table(before, after):
    table = {}
    for key in COUNT_KEYS + EXTRA_KEYS:
        b, a = count_value(before, key), count_value(after, key)
        both_int = all(isinstance(v, int) and not isinstance(v, bool)
                       for v in (b, a))
        table[key] = {'before': b, 'after': a,
                      'delta': a - b if both_int else None}
    table['uncontrolled_checks']['before_list'] = \
        before['uncontrolled_checks']
    table['uncontrolled_checks']['after_list'] = after['uncontrolled_checks']
    return table


def control_diffs(before, after):
    ids = list(before['order']) + [i for i in after['order']
                                   if i not in before['rows']]
    out = []
    for cid in ids:
        b, a = before['rows'].get(cid), after['rows'].get(cid)
        bc = b['classification'] if b else None
        ac = a['classification'] if a else None
        bb = b['bucket'] if b else None
        ab = a['bucket'] if a else None
        out.append({
            'id': cid,
            'present': 'both' if b and a else ('before' if b else 'after'),
            'before': bc, 'after': ac,
            'before_bucket': bb, 'after_bucket': ab,
            'changed': (bc != ac or bb != ab
                        or (b is None) != (a is None)),
            'before_failed_checks': b['failed_checks'] if b else None,
            'after_failed_checks': a['failed_checks'] if a else None,
            'targeted': (a or b)['targeted']})
    return out


def signature(summary):
    sig = {'controls_exit': summary['controls_exit']}
    for key in COUNT_KEYS + EXTRA_KEYS:
        sig[key] = summary[key]
    sig['classifications'] = {cid: row['classification']
                              for cid, row in summary['rows'].items()}
    sig['buckets'] = {cid: row['bucket']
                      for cid, row in summary['rows'].items()}
    return sig


def signature_diff(base, other):
    diffs = []
    for key in base:
        if key in ('classifications', 'buckets'):
            b, o = base[key], other[key]
            field = ('classification' if key == 'classifications'
                     else 'bucket')
            for cid in sorted(set(b) | set(o)):
                if b.get(cid) != o.get(cid):
                    diffs.append(f'{field}[{cid}]: {b.get(cid)!r} -> '
                                 f'{o.get(cid)!r}')
        elif base[key] != other[key]:
            diffs.append(f'{key}: {base[key]!r} -> {other[key]!r}')
    return diffs


# ----------------------------------------------------------- measurement

def _collect_inputs(pairs, doc):
    for label, path in pairs:
        try:
            doc['inputs'][label] = file_record(label, path)
        except MeasureFault as exc:
            doc['faults'].append(str(exc))


def _default_probe(controls):
    return Path(controls).resolve().parents[2] / 'tools' / 'kama-probe.sh'


def _registry_note(controls, doc):
    reg = Path(controls).resolve().parents[2] / 'registry' / \
        'endpoint-consumers.tsv'
    if reg.is_file():
        doc['inputs']['registry'] = file_record('registry', reg)
    else:
        doc['inputs']['registry'] = {'path': str(reg), 'sha256': None,
                                     'bytes': None, 'absent': True}
        doc['warnings'].append(
            f'{reg} is absent: controls stages an EMPTY registry, so the '
            'tool refuses only its built-in ports')


def _pin_frozen(args, doc):
    for label in ('frozen_tool', 'frozen_gate'):
        pin, faults = frozen_pin(label, doc['inputs'][label], args.lane,
                                 args.frozen_rev)
        doc['frozen_pins'][label] = pin
        doc['faults'] += faults


def _check_out(args, doc):
    if args.out:
        out = str(Path(args.out).resolve())
        if any(rec['path'] == out for rec in doc['inputs'].values()):
            doc['faults'].append(f'--out {out} would overwrite an input')


def _graded(rec, side, doc, tool_label, gate_label):
    """Attach summary/faults to one run record."""
    faults = run_faults(rec)
    rec['summary'] = None
    rec['notes'] = []
    if isinstance(rec['doc'], dict):
        summary, sfaults, notes = summarize(rec['doc'], rec['exit'])
        rec['summary'], rec['notes'] = summary, notes
        faults += sfaults
        for key, label in (('tool_sha256', tool_label),
                           ('gate_sha256', gate_label)):
            val = rec['doc'].get(key)
            want = doc['inputs'][label]['sha256']
            if val is None:
                doc['warnings'].append(f'{side}: controls output does not '
                                       f'report {key}')
            elif val != want:
                faults.append(f'controls reports {key} {val} but {label} is '
                              f'{want}')
    rec['faults'] = faults
    doc['faults'] += [f'{side}: {f}' for f in faults]
    return rec


def run_measure(args):
    """(report doc, exit code) for measurement mode."""
    doc = {'schema': SCHEMA, 'mode': 'measure', 'started_utc': utc_now(),
           'python': sys.version.split()[0], 'argv': list(sys.argv),
           'inputs': {}, 'frozen_pins': {}, 'identical_pairs': None,
           'runs': {}, 'controls_json_sha256': {}, 'counts': None,
           'controls': [], 'current_clean': None, 'reasons': [],
           'faults': [], 'warnings': [], 'exit': None}
    probe = args.probe or (_default_probe(args.controls)
                           if Path(args.controls).is_file() else None)
    _collect_inputs([('measure', HERE), ('controls', args.controls),
                     ('frozen_tool', args.frozen_tool),
                     ('frozen_gate', args.frozen_gate),
                     ('tool', args.tool), ('gate', args.gate),
                     ('probe', probe or '<unresolved>')], doc)
    if not doc['faults']:
        _registry_note(args.controls, doc)
        _pin_frozen(args, doc)
        ins = doc['inputs']
        doc['identical_pairs'] = (
            ins['frozen_tool']['sha256'] == ins['tool']['sha256']
            and ins['frozen_gate']['sha256'] == ins['gate']['sha256'])
        if doc['identical_pairs']:
            doc['warnings'].append('frozen and current tool+gate are '
                                   'byte-identical: before and after grade '
                                   'the same pair')
        _check_out(args, doc)
    if doc['faults']:
        doc['exit'] = EXIT_FAULT
        doc['finished_utc'] = utc_now()
        return doc, EXIT_FAULT

    scratch = Path(tempfile.mkdtemp(prefix='kama-c1-measure-'))
    try:
        for side, tool_l, gate_l in (('before', 'frozen_tool', 'frozen_gate'),
                                     ('after', 'tool', 'gate')):
            rec = run_controls(doc['inputs']['controls']['path'],
                               doc['inputs'][tool_l]['path'],
                               doc['inputs'][gate_l]['path'],
                               doc['inputs']['probe']['path'], scratch, side,
                               args.timeout)
            doc['runs'][side] = _graded(rec, side, doc, tool_l, gate_l)
            doc['controls_json_sha256'][side] = {
                'stdout': rec['stdout_sha256'],
                'canonical': rec['doc_canonical_sha256']}
            if rec['leaked_processes']:
                doc['warnings'].append(
                    f"{side}: {len(rec['leaked_processes'])} process(es) "
                    'outlived the controls run (reaped)')
    finally:
        late = reap_scratch(scratch)
        shutil.rmtree(scratch, ignore_errors=True)
    if late:
        doc['warnings'].append(f'{len(late)} late process(es) reaped')

    b, a = doc['runs']['before'], doc['runs']['after']
    if b['summary'] and a['summary']:
        doc['counts'] = counts_table(b['summary'], a['summary'])
        doc['controls'] = control_diffs(b['summary'], a['summary'])
    if doc['faults']:
        code = EXIT_FAULT
    else:
        doc['reasons'] = clean_reasons(a['summary'])
        doc['current_clean'] = not doc['reasons']
        code = EXIT_CLEAN if doc['current_clean'] else EXIT_NOT_CLEAN
    doc['exit'] = code
    doc['finished_utc'] = utc_now()
    return doc, code


# ---------------------------------------------------------- self-mutants

def apply_mutant(src, alternatives):
    tried = []
    for idx, (old, new) in enumerate(alternatives):
        n = src.count(old)
        tried.append({'old': old, 'occurrences': n})
        if n == 1:
            pos = src.index(old)
            return {'status': 'applied', 'alternative': idx, 'old': old,
                    'new': new, 'line': src.count('\n', 0, pos) + 1,
                    'tried': tried, 'source': src.replace(old, new, 1)}
    status = ('site_ambiguous' if any(t['occurrences'] > 1 for t in tried)
              else 'site_missing')
    return {'status': status, 'tried': tried, 'source': None}


def stage_controls(dest, controls, source):
    """Copy the controls' directory (regular files) into dest mirroring
    controls.parents[2], plus registry/endpoint-consumers.tsv when the
    original resolves one; write `source` as the controls file."""
    orig = Path(controls).resolve()
    if len(orig.parents) < 3:
        raise MeasureFault(f'{orig} has no parents[2] to mirror')
    base = orig.parents[2]
    staged = dest / orig.relative_to(base)
    staged.parent.mkdir(parents=True, exist_ok=True)
    for f in sorted(orig.parent.iterdir()):
        if f.is_file() and not f.is_symlink() and f.name != orig.name:
            shutil.copyfile(f, staged.parent / f.name)
    reg = base / 'registry' / 'endpoint-consumers.tsv'
    if reg.is_file():
        (dest / 'registry').mkdir(parents=True, exist_ok=True)
        shutil.copyfile(reg, dest / 'registry' / 'endpoint-consumers.tsv')
    staged.write_text(source, encoding='utf-8')
    os.chmod(staged, 0o755)
    return staged


def _compact(rec):
    keep = ('exit', 'timed_out', 'duration_s', 'stdout_sha256',
            'doc_canonical_sha256', 'faults', 'leaked_processes')
    out = {k: rec.get(k) for k in keep}
    out['signature'] = signature(rec['summary']) if rec.get('summary') \
        else None
    return out


def run_self_mutants(args, mutants=MUTANTS):
    doc = {'schema': SCHEMA, 'mode': 'self-mutants',
           'started_utc': utc_now(), 'python': sys.version.split()[0],
           'argv': list(sys.argv), 'inputs': {}, 'pairs': [],
           'baseline': {}, 'mutants': [], 'frozen_pins': {}, 'faults': [],
           'warnings': [], 'exit': None}
    if (args.frozen_tool is None) != (args.frozen_gate is None):
        doc['faults'].append('--frozen-tool and --frozen-gate go together')
    names = args.mutant or list(mutants)
    unknown = [n for n in names if n not in mutants]
    if unknown:
        doc['faults'].append(f'unknown mutant(s): {", ".join(unknown)}')
    probe = args.probe or (_default_probe(args.controls)
                           if Path(args.controls).is_file() else None)
    labels = [('measure', HERE), ('controls', args.controls),
              ('tool', args.tool), ('gate', args.gate),
              ('probe', probe or '<unresolved>')]
    if args.frozen_tool and args.frozen_gate:
        labels += [('frozen_tool', args.frozen_tool),
                   ('frozen_gate', args.frozen_gate)]
    _collect_inputs(labels, doc)
    src = None
    if not doc['faults']:
        _registry_note(args.controls, doc)
        if 'frozen_tool' in doc['inputs']:
            _pin_frozen(args, doc)
        _check_out(args, doc)
        try:
            src = Path(args.controls).read_bytes().decode('utf-8')
        except (OSError, UnicodeDecodeError) as exc:
            doc['faults'].append(f'controls source unreadable: {exc}')
    if doc['faults']:
        doc['exit'] = EXIT_FAULT
        doc['finished_utc'] = utc_now()
        return doc, EXIT_FAULT

    ins = doc['inputs']
    pairs = [('current', ins['tool']['path'], ins['gate']['path'])]
    if 'frozen_tool' in ins:
        pairs.append(('frozen', ins['frozen_tool']['path'],
                      ins['frozen_gate']['path']))
    doc['pairs'] = [p[0] for p in pairs]
    controls = ins['controls']['path']
    probe_path = ins['probe']['path']
    scratch = Path(tempfile.mkdtemp(prefix='kama-c1-measure-mut-'))
    try:
        base = stage_controls(scratch / 'base', controls, src)
        bsel = run_selftest_of(base, scratch, 'selftest-base',
                               args.selftest_timeout)
        bsel['available'] = (bsel['exit'] == 0 and not bsel['timed_out'])
        doc['baseline']['selftest'] = bsel
        base_sig = {}
        for pname, tool, gate in pairs:
            runs, sigs, usable = [], [], True
            for i in range(args.baseline_runs):
                rec = run_controls(base, tool, gate, probe_path, scratch,
                                   f'base-{pname}-{i}', args.timeout)
                _attach(rec)
                runs.append(_compact(rec))
                if rec['faults']:
                    usable = False
                else:
                    sigs.append(signature(rec['summary']))
            stable = usable and all(s == sigs[0] for s in sigs)
            doc['baseline'][pname] = {'runs': runs, 'usable': usable,
                                      'stable': stable}
            if usable and not stable:
                doc['warnings'].append(
                    f'{pname}: baseline runs disagree; numeric diffs on this '
                    'pair are reported, never credited: '
                    + '; '.join(signature_diff(sigs[0], sigs[-1])))
            base_sig[pname] = sigs[0] if stable else None
        if not bsel['available'] and not any(base_sig.values()):
            doc['faults'].append('no usable detector: baseline --selftest '
                                 f"exit {bsel['exit']} and no stable "
                                 'baseline pair')

        for name in ([] if doc['faults'] else names):
            intent, alternatives = mutants[name]
            entry = {'name': name, 'intent': intent, 'status': None,
                     'killed_by': [], 'selftest': None, 'numbers': {}}
            doc['mutants'].append(entry)
            app = apply_mutant(src, alternatives)
            entry['site'] = {k: v for k, v in app.items() if k != 'source'}
            if app['status'] != 'applied':
                entry['status'] = app['status']
                continue
            mdir = scratch / f'mut-{name}'
            try:
                compile(app['source'], str(Path(controls).name), 'exec')
            except (SyntaxError, ValueError) as exc:
                entry['status'] = 'invalid_mutation'
                entry['site']['compile_error'] = f'{type(exc).__name__}: {exc}'
                continue
            if app['source'] == src:
                entry['status'] = 'invalid_mutation'
                entry['site']['compile_error'] = 'edit is a no-op'
                continue
            mut = stage_controls(mdir, controls, app['source'])
            entry['mutant_sha256'] = sha256_bytes(
                app['source'].encode('utf-8'))
            if bsel['available']:
                msel = run_selftest_of(mut, scratch, f'selftest-{name}',
                                       args.selftest_timeout)
                entry['selftest'] = msel
                if msel['exit'] != 0:
                    entry['killed_by'].append(
                        f"selftest (exit {msel['exit']})")
            for pname, tool, gate in pairs:
                if not doc['baseline'][pname]['usable']:
                    entry['numbers'][pname] = {'status': 'baseline-unusable'}
                    continue
                rec = run_controls(mut, tool, gate, probe_path, scratch,
                                   f'mut-{name}-{pname}', args.timeout)
                _attach(rec)
                if rec['faults']:
                    diff = ['run-fault: ' + '; '.join(rec['faults'])]
                else:
                    ref = base_sig[pname] or signature(
                        _first_summary(doc['baseline'][pname]))
                    diff = signature_diff(ref, signature(rec['summary']))
                credited = base_sig[pname] is not None
                entry['numbers'][pname] = {'differs': bool(diff),
                                           'diff': diff,
                                           'credited': credited,
                                           'run': _compact(rec)}
                if diff and credited:
                    entry['killed_by'].append(
                        f'numbers:{pname} (' + '; '.join(diff) + ')')
            entry['status'] = 'killed' if entry['killed_by'] else 'survived'
    finally:
        late = reap_scratch(scratch)
        shutil.rmtree(scratch, ignore_errors=True)
    if late:
        doc['warnings'].append(f'{len(late)} late process(es) reaped')
    try:
        after = file_record('controls', controls)['sha256']
    except MeasureFault as exc:
        after = str(exc)
    if after != ins['controls']['sha256']:
        doc['faults'].append(f'original controls changed during the run '
                             f'({ins["controls"]["sha256"]} -> {after})')
    if doc['faults']:
        code = EXIT_FAULT
    else:
        code = EXIT_CLEAN if doc['mutants'] and all(
            m['status'] == 'killed' for m in doc['mutants']) \
            else EXIT_NOT_CLEAN
    doc['summary'] = {m['name']: m['status'] for m in doc['mutants']}
    doc['exit'] = code
    doc['finished_utc'] = utc_now()
    return doc, code


def _attach(rec):
    rec['faults'] = run_faults(rec)
    rec['summary'] = None
    if isinstance(rec['doc'], dict):
        summary, sfaults, _notes = summarize(rec['doc'], rec['exit'])
        rec['summary'] = summary
        rec['faults'] += sfaults
    return rec


def _first_summary(base):
    """Signature source for an unstable pair: its first baseline run (the
    diff is then reported but never credited)."""
    sig = base['runs'][0]['signature']
    return {'controls_exit': sig['controls_exit'],
            **{k: sig[k] for k in COUNT_KEYS + EXTRA_KEYS},
            'rows': {cid: {'classification': c,
                           'bucket': sig['buckets'].get(cid)}
                     for cid, c in sig['classifications'].items()}}


# ---------------------------------------------------------------- output

def _fmt(val):
    return '-' if val is None else str(val)


def print_measure(doc):
    ins = doc['inputs']
    if 'controls' in ins:
        print(f"c1-measure: controls {ins['controls']['path']} "
              f"sha256 {ins['controls']['sha256']}")
    for label in ('frozen_tool', 'frozen_gate', 'tool', 'gate', 'probe'):
        if label in ins:
            pin = doc['frozen_pins'].get(label)
            tag = '' if pin is None else f" pinned={pin['verified']}"
            print(f"  {label:<11} {ins[label]['sha256'][:16]} "
                  f"{ins[label]['path']}{tag}")
    if doc['counts']:
        print(f"  {'count':<20} {'before':>7} {'after':>7} {'delta':>6}")
        for key, row in doc['counts'].items():
            print(f"  {key:<20} {_fmt(row['before']):>7} "
                  f"{_fmt(row['after']):>7} {_fmt(row['delta']):>6}")
        unc = doc['counts']['uncontrolled_checks']
        print(f"  uncontrolled before: {unc['before_list']}")
        print(f"  uncontrolled after:  {unc['after_list']}")
        for row in doc['controls']:
            mark = 'CHANGED' if row['changed'] else ''
            print(f"  {row['id']:<6} {_fmt(row['before']):<22} -> "
                  f"{_fmt(row['after']):<22} {mark}")
    for side in ('before', 'after'):
        run = doc['runs'].get(side)
        if run:
            print(f"  run {side}: exit {run['exit']} "
                  f"{run['duration_s']}s stdout sha256 "
                  f"{run['stdout_sha256'][:16]}")
            for note in run.get('notes') or ():
                print(f'    note: {note}')
    for warn in doc['warnings']:
        print(f'  warning: {warn}')
    if doc['exit'] == EXIT_FAULT:
        print('verdict: FAULT (exit 2): ' + ' | '.join(doc['faults']))
    elif doc['exit'] == EXIT_CLEAN:
        print('verdict: CLEAN (exit 0)')
    else:
        print('verdict: NOT CLEAN (exit 1): ' + ' | '.join(doc['reasons']))


def print_self_mutants(doc):
    ins = doc['inputs']
    if 'controls' in ins:
        print(f"c1-measure self-mutants: controls {ins['controls']['path']} "
              f"sha256 {ins['controls']['sha256']}")
    bsel = doc['baseline'].get('selftest')
    if bsel:
        print(f"  selftest detector: "
              f"{'available' if bsel['available'] else 'unavailable'} "
              f"(baseline exit {bsel['exit']})")
    for pname in doc['pairs']:
        base = doc['baseline'].get(pname)
        if base:
            print(f"  numbers detector {pname}: usable={base['usable']} "
                  f"stable={base['stable']} runs={len(base['runs'])}")
    for m in doc['mutants']:
        site = m['site']
        where = (f"line {site['line']}" if site.get('line') else
                 'occurrences ' + ','.join(str(t['occurrences'])
                                           for t in site['tried']))
        print(f"  {m['name']:<20} {m['status']:<17} {where}")
        for k in m['killed_by']:
            print(f'      killed_by {k}')
    for warn in doc['warnings']:
        print(f'  warning: {warn}')
    if doc['exit'] == EXIT_FAULT:
        print('verdict: FAULT (exit 2): ' + ' | '.join(doc['faults']))
    else:
        print(f"verdict: exit {doc['exit']} "
              f"({'all killed' if doc['exit'] == 0 else 'not all killed'})")


# -------------------------------------------------------------- selftest

FAKE_CONTROLS = r'''#!/usr/bin/env python3
"""Synthetic controls.py for measure.py --selftest (never serves)."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

MODE = '%%MODE%%'
COUNTER = '%%COUNTER%%'


def _sha(path):
    with open(path, 'rb') as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _gate_flip(st, gate, receipt_doc, failed):
    return {'exit': 1, 'rejected': True, 'accepted': False, 'flipped': 1}


def k0_accepted(tool_exit, gate_exit):
    accepted = (tool_exit == 0 and gate_exit == 0
                and True)
    return accepted


class K6Spec:
    exits = (2,)


def k6_rejected(receipt_written, tool_exit, spec=K6Spec):
    exit_ok = tool_exit in spec.exits
    return receipt_written and exit_ok


def selftest():
    ok = (k0_accepted(0, 0) and not k0_accepted(-15, 0)
          and k6_rejected(True, 2) and not k6_rejected(True, 1))
    print('fake selftest', 'ok' if ok else 'FAILED')
    return 0 if ok else 1


def row(cid, cls, failed, targeted, st=None, gate=None, receipt_doc=None):
    gate_flip = None
    if cid != 'k0':
        gate_flip = _gate_flip(st, gate, receipt_doc, failed)
    targets = [targeted] if isinstance(targeted, str) else []
    bucket = ('misclassified' if cls == 'misclassified'
              else 'accepted_bad' if cid != 'k0' and cls == 'accepted'
              else 'ok')
    return {'id': cid, 'classification': cls, 'failed_checks': failed,
            'targeted': targets, 'targeted_hit': cls == 'rejected-targeted',
            'bucket': bucket, 'gate_flip': gate_flip}


def main():
    ap = argparse.ArgumentParser()
    for flag in ('--tool', '--gate', '--probe'):
        ap.add_argument(flag)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        if MODE == 'noselftest':
            return 2
        return selftest()
    before = '/frozen/' in a.tool
    if MODE == 'crash':
        print('fake: own fault', file=sys.stderr)
        return 2
    if MODE == 'garbage':
        print('this is not json')
        return 0
    if MODE == 'hang':
        time.sleep(60)
    if MODE == 'leak' and not before:
        subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)',
                          os.path.join(os.environ['TMPDIR'], 'leak-marker')],
                         start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    tool_sha = _sha(a.tool)
    if MODE == 'wrongsha' and not before:
        tool_sha = '0' * 64
    if MODE == 'v1':
        flip = None if before else {'exit': 1, 'accepted': False}
        doc = {'schema': 'kama-live-controls/v1', 'tool_sha256': tool_sha,
               'gate_sha256': _sha(a.gate),
               'accepted_bad': 1 if before else 0, 'gate_flip_bad': 0,
               'inconclusive': 0, 'good_ok': True, 'controls': [
                   {'id': 'k0', 'accepted': True, 'inconclusive': False,
                    'attributed': None, 'failed_checks': [],
                    'expected_failed': [], 'gate_flip': None},
                   {'id': 'k1', 'accepted': before, 'inconclusive': False,
                    'attributed': None if before else True,
                    'failed_checks': [] if before else ['health_ready'],
                    'expected_failed': ['health'], 'gate_flip': flip}]}
        print(json.dumps(doc))
        return 1 if before else 0
    rows = [row('k0', 'accepted', [], None)]
    if before:
        rows.append(row('k1', 'accepted', [], 'health_ready'))
        rows.append(row('k9', 'misclassified', ['teardown_graceful'],
                        'props_alias'))
        k17 = row('k17', 'rejected-targeted', ['ownership'], 'ownership')
        k17['bucket'] = 'good_rejected'
        rows.append(k17)
        doc = {'accepted_bad': 1, 'good_rejected': 1, 'misclassified': 1,
               'uncontrolled_checks': ['props_alias', 'model_unchanged'],
               'input_integrity_checks': ['model_unchanged'],
               'good_ok': False}
        rc = 1
    else:
        rows.append(row('k1', 'rejected-targeted', ['health_ready'],
                        'health_ready'))
        rows.append(row('k9', 'rejected-targeted', ['props_alias'],
                        'props_alias'))
        unc = {'dirty': ['props_alias'],
               'model-only': ['model_unchanged'],
               'model-only-undeclared': ['model_unchanged']}.get(MODE, [])
        doc = {'accepted_bad': 1 if MODE == 'inconsistent' else 0,
               'good_rejected': 0, 'misclassified': 0,
               'uncontrolled_checks': unc, 'good_ok': True}
        if MODE == 'model-only':
            doc['input_integrity_checks'] = ['model_unchanged']
        rc = {'exit1clean': 1, 'exit2json': 2}.get(MODE, 0)
    doc.update(schema='kama-live-controls/v2', tool_sha256=tool_sha,
               gate_sha256=_sha(a.gate), controls=rows)
    if MODE == 'flaky':
        try:
            with open(COUNTER, encoding='ascii') as fh:
                n = int(fh.read() or 0)
        except OSError:
            n = 0
        with open(COUNTER, 'w', encoding='ascii') as fh:
            fh.write(str(n + 1))
        doc['inconclusive'] = n % 2
    print(json.dumps(doc, indent=2, sort_keys=True))
    return rc


if __name__ == '__main__':
    sys.exit(main())
'''


def _fake_source(lane, mode):
    return (FAKE_CONTROLS.replace('%%MODE%%', mode)
            .replace('%%COUNTER%%', str(lane / 'counter')))


def _selftest_git(root):
    """Create one isolated repository with the expected immutable blobs."""
    repo = root / 'frozen-git'
    repo.mkdir()
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM='1',
               GIT_CONFIG_GLOBAL=os.devnull)

    def git(*argv):
        cp = subprocess.run(['git', *argv], cwd=repo, env=env,
                            stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            text=True, timeout=60)
        if cp.returncode:
            raise RuntimeError(f'git {argv!r}: exit {cp.returncode}: '
                               f'{cp.stderr[-400:]}')
        return cp.stdout.strip()

    git('init', '-q', '--template=')
    for rel, content in (
            (FROZEN_GIT_PATHS['frozen_tool'], '# frozen_tool\n'),
            (FROZEN_GIT_PATHS['frozen_gate'], '# frozen_gate\n')):
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    git('-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
        '-c', 'user.name=C1Measure selftest',
        '-c', 'user.email=c1measure-selftest@example.invalid',
        'add', '--', '.')
    git('-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgsign=false',
        '-c', 'user.name=C1Measure selftest',
        '-c', 'user.email=c1measure-selftest@example.invalid',
        'commit', '-q', '-m', 'measure selftest frozen input')
    return repo, git('rev-parse', 'HEAD')


def _selftest_tree(root, mode, gitroot, rev):
    """lane-like tree: lane/tests/llamacpp-live/controls.py + tools."""
    lane = root / f'lane-{mode}'
    ctl = lane / 'tests' / 'llamacpp-live' / 'controls.py'
    ctl.parent.mkdir(parents=True)
    ctl.write_text(_fake_source(lane, mode), encoding='utf-8')
    (lane / 'tools').mkdir()
    (lane / 'registry').mkdir()
    (lane / 'registry' / 'endpoint-consumers.tsv').write_text(
        '# selftest registry\n', encoding='utf-8')
    paths = {'controls': ctl, 'probe': lane / 'tools' / 'kama-probe.sh',
             'lane': gitroot, 'rev': rev}
    paths['probe'].write_text('#!/bin/sh\n', encoding='utf-8')
    frozen = lane / 'frozen'
    frozen.mkdir()
    for label, where, name in (('frozen_tool', frozen, 'frozen-tool.py'),
                               ('frozen_gate', frozen, 'frozen-gate.py'),
                               ('tool', lane / 'tools', 'tool.py'),
                               ('gate', lane / 'tools', 'gate.py')):
        path = where / name
        path.write_text(f'# {label}\n', encoding='utf-8')
        paths[label] = path
    return paths


def _args(paths, *extra):
    argv = ['--controls', str(paths['controls']),
            '--frozen-tool', str(paths['frozen_tool']),
            '--frozen-gate', str(paths['frozen_gate']),
            '--tool', str(paths['tool']), '--gate', str(paths['gate']),
            '--probe', str(paths['probe']),
            '--lane', str(paths['lane']), '--frozen-rev', paths['rev']]
    return build_parser().parse_args(argv + list(extra))


def selftest():
    fails = []
    n = [0]

    def expect(cond, what):
        n[0] += 1
        if not cond:
            fails.append(what)

    # unit: apply_mutant
    src = 'a = 1\nb = 2\nb = 2\n'
    r = apply_mutant(src, (('a = 1', 'a = 3'),))
    expect(r['status'] == 'applied' and r['line'] == 1
           and r['source'] == 'a = 3\nb = 2\nb = 2\n', 'apply: unique')
    expect(apply_mutant(src, (('zz', 'y'),))['status'] == 'site_missing',
           'apply: missing')
    expect(apply_mutant(src, (('b = 2', 'b = 5'),))['status']
           == 'site_ambiguous', 'apply: ambiguous')
    r = apply_mutant(src, (('zz', 'y'), ('b = 2', 'x'), ('a = 1', 'c = 1')))
    expect(r['status'] == 'applied' and r['alternative'] == 2,
           'apply: falls through missing and ambiguous alternatives')

    # unit: summarize / clean_reasons
    clean_doc = {'schema': 'x/v2', 'accepted_bad': 0, 'good_rejected': 0,
                 'misclassified': 0, 'good_ok': True,
                 'uncontrolled_checks': ['model_unchanged'],
                 'input_integrity_checks': ['model_unchanged'],
                 'controls': [{'id': 'k0', 'classification': 'accepted',
                               'bucket': 'ok', 'targeted': [],
                               'targeted_hit': None, 'failed_checks': [],
                               'gate_flip': None}]}
    s, f, _ = summarize(clean_doc, 0)
    expect(not f and s['uncontrolled_checks'] == []
           and s['uncontrolled_excluded'] == ['model_unchanged']
           and clean_reasons(s) == [], 'summarize: clean + excluded')
    undeclared = dict(clean_doc)
    undeclared.pop('input_integrity_checks')
    s, f, _ = summarize(undeclared, 0)
    expect(not f and s['uncontrolled_checks'] == ['model_unchanged']
           and s['uncontrolled_excluded'] == [],
           'summarize: undeclared exclusion label stays uncontrolled')
    launder = dict(clean_doc, controls=clean_doc['controls'] + [{
        'id': 'k1', 'classification': 'accepted', 'bucket': 'accepted_bad',
        'targeted': [], 'targeted_hit': None, 'failed_checks': [],
        'gate_flip': None}])
    _, f, _ = summarize(launder, 0)
    expect(any('accepted_bad=0 but 1' in x for x in f),
           'summarize: accepted_bad row/count divergence is a fault')
    gap = dict(clean_doc, controls=clean_doc['controls'] + [
        {'id': 'k2', 'classification': 'rejected-targeted',
         'targeted': [], 'targeted_hit': None, 'failed_checks': [],
         'gate_flip': None},
        {'id': 'k1', 'classification': 'accepted', 'bucket': 'accepted_bad',
         'targeted': [], 'targeted_hit': None, 'failed_checks': [],
         'gate_flip': None}])
    _, f, _ = summarize(gap, 0)
    expect(any('accepted_bad=0 but 1' in x for x in f),
           'summarize: bucket-less sibling cannot disable the cross-check')
    _, f, _ = summarize(dict(clean_doc, good_ok=False), 0)
    expect(any('good_ok is false' in x for x in f),
           'summarize: good_ok false with zero good_rejected is a fault')
    flips = dict(clean_doc, gate_flip_arms=0, controls=[
        dict(clean_doc['controls'][0],
             gate_flip={'accepted': False, 'exit': 1})])
    _, f, _ = summarize(flips, 0)
    expect(any('gate_flip_arms=0' in x for x in f),
           'summarize: under-reported gate_flip_arms is a fault')
    _, f, _ = summarize(dict(clean_doc, gate_flip_arms=99), 0)
    expect(not f, 'summarize: over-reported gate_flip_arms is a note')
    bad = dict(clean_doc, accepted_bad=True)
    expect(summarize(bad, 1)[1], 'summarize: bool count is a fault')
    s, f, _ = summarize(dict(clean_doc, misclassified=2), 0)
    expect(any('exited 0 against' in x for x in f),
           'summarize: exit 0 contradicting counts is a fault')

    # Exact k16/top-level regression projection from round-18
    # runs/c1-measure.json runs.before.doc. The observed classification is
    # rejected-targeted; expected-outcome bucket is misclassified.
    rawbefore_k16 = {
        'schema': 'kama-live-controls/v2',
        'accepted_bad': 5, 'good_rejected': 1, 'misclassified': 1,
        'uncontrolled_checks': [], 'good_ok': True,
        'gate_flip_bad': 0, 'gate_flip_arms': 16, 'inconclusive': 0,
        'controls': [{
            'id': 'k16', 'classification': 'rejected-targeted',
            'bucket': 'misclassified', 'expected': 'not-evaluated',
            'targeted': ['loading_envelope_graded'], 'targeted_hit': True,
            'failed_checks': ['loading_envelope_graded'],
            'tool_exit': 1, 'gate_exit': 1,
            'gate_flip': {'accepted': False, 'cleared': [], 'exit': 1,
                          'flipped': ['loading_envelope_graded'],
                          'rejected': True, 'targeted': True},
        }],
    }
    s, f, _ = summarize(rawbefore_k16, 1)
    expect(not f and s['misclassified'] == 1
           and s['rows']['k16']['classification'] == 'rejected-targeted'
           and s['rows']['k16']['bucket'] == 'misclassified',
           'rawbefore k16: count bucket without relabeling classification')

    # Older reported-schema rows without bucket retain classification-based
    # consistency checking for compatibility.
    no_bucket = {
        'schema': 'kama-live-controls/v2', 'accepted_bad': 0,
        'good_rejected': 0, 'misclassified': 1, 'uncontrolled_checks': [],
        'good_ok': True,
        'controls': [{'id': 'legacy', 'classification': 'misclassified',
                      'targeted': [], 'targeted_hit': None,
                      'failed_checks': []}],
    }
    s, f, _ = summarize(no_bucket, 1)
    expect(not f and s['rows']['legacy']['bucket_source']
           == 'classification-fallback',
           'reported schema without bucket uses legacy classification')
    s, f, _ = summarize({k: v for k, v in clean_doc.items()
                         if k != 'good_rejected'}, 1)
    expect(not f and s['good_rejected'] is None and any(
        'good_rejected not reported' in x for x in clean_reasons(s)),
        'summarize: missing count is not reported, never clean')
    s, f, _ = summarize({'schema': 'nope', 'controls': []}, 1)
    expect(f, 'summarize: unknown shape is a fault')
    s, f, _ = summarize(dict(clean_doc, good_ok=None), 1)
    expect(not f and clean_reasons(s) == [],
           'clean predicate follows exactly the four declared counts')
    s, f, _ = summarize(dict(clean_doc, good_ok=0), 1)
    expect(any('good_ok is not a boolean' in x for x in f),
           'summarize: good_ok type validation')

    root = Path(tempfile.mkdtemp(prefix='kama-c1-measure-selftest-'))
    try:
        gitroot, test_rev = _selftest_git(root)
        def measure_mode(mode, *extra, mutate=None):
            paths = _selftest_tree(root, mode, gitroot, test_rev)
            if mutate:
                mutate(paths)
            args = _args(paths, *extra)
            return run_measure(args)

        doc, code = measure_mode('normal')
        c = doc['counts'] or {}
        ch = {r['id']: (r['before'], r['after']) for r in doc['controls']}
        expect(code == 0 and doc['current_clean'] is True,
               f'normal: exit {code} {doc["faults"]} {doc["reasons"]}')
        expect(c.get('accepted_bad', {}).get('delta') == -1
               and c['good_rejected']['before'] == 1
               and c['misclassified']['before'] == 1
               and c['uncontrolled_checks']['before'] == 1
               and c['uncontrolled_checks']['after'] == 0
               and c['gate_flip_arms']['after'] == 2,
               f'normal: counts {c}')
        expect(ch.get('k1') == ('accepted', 'rejected-targeted')
               and ch.get('k0') == ('accepted', 'accepted'),
               f'normal: per-control diff {ch}')
        expect(all(doc['frozen_pins'][k]['verified'] is True
                   for k in ('frozen_tool', 'frozen_gate')),
               'normal: frozen pins verified')
        expect(all(len(doc['controls_json_sha256'][s]['stdout']) == 64
                   for s in ('before', 'after')), 'normal: JSON digests')

        doc, code = measure_mode('v1')
        expect(code == 1 and any('misclassified not reported' in x
                                 for x in doc['reasons'])
               and any('uncontrolled_checks not reported' in x
                       for x in doc['reasons'])
               and doc['counts']['good_rejected']['after'] == 0,
               f'v1: exit {code} {doc["reasons"]} {doc["faults"]}')
        doc, code = measure_mode('dirty')
        expect(code == 1 and 'uncontrolled_checks=props_alias'
               in doc['reasons'], f'dirty: exit {code} {doc["reasons"]}')
        doc, code = measure_mode('model-only')
        expect(code == 0, f'model-only: exit {code} {doc["reasons"]}')
        doc, code = measure_mode('model-only-undeclared')
        expect(code == 1 and 'uncontrolled_checks=model_unchanged'
               in doc['reasons'],
               f'model-only-undeclared: exit {code} {doc["reasons"]}')
        doc, code = measure_mode('exit1clean')
        expect(code == 0 and doc['reasons'] == [],
               f'exit1clean: exit {code} {doc["reasons"]}')
        for mode in ('inconsistent', 'garbage', 'crash', 'wrongsha',
                     'exit2json'):
            doc, code = measure_mode(mode)
            expect(code == 2 and doc['faults'],
                   f'{mode}: exit {code} {doc["faults"]}')
        t0 = time.monotonic()
        doc, code = measure_mode('hang', '--timeout', '2')
        expect(code == 2 and doc['runs']['before']['timed_out']
               and time.monotonic() - t0 < 40, f'hang: exit {code}')
        doc, code = measure_mode('leak')
        leaked = doc['runs']['after']['leaked_processes']
        expect(code == 0 and len(leaked) == 1 and leaked[0]['gone']
               and any('outlived' in w for w in doc['warnings']),
               f'leak: exit {code} {leaked} {doc["warnings"]}')

        def corrupt(paths):
            paths['frozen_tool'].write_text('# drifted\n', encoding='utf-8')
        doc, code = measure_mode('pin', mutate=corrupt)
        expect(code == 2 and not doc['runs']
               and any('!= git' in e for e in doc['faults']),
               f'git pin mismatch: exit {code} {doc["faults"]}')

        def unlink(paths):
            paths['gate'].unlink()
        doc, code = measure_mode('missing', mutate=unlink)
        expect(code == 2 and not doc['runs'], f'missing input: exit {code}')
        paths = _selftest_tree(root, 'outclash', gitroot, test_rev)
        doc, code = run_measure(_args(paths, '--out', str(paths['gate'])))
        expect(code == 2 and not doc['runs'], f'--out onto input: {code}')

        # self-mutants: real table against the synthetic controls
        paths = _selftest_tree(root, 'mut', gitroot, test_rev)
        args = _args(paths, '--self-mutants')
        doc, code = run_self_mutants(args)
        st = doc.get('summary', {})
        kb = {m['name']: ' '.join(m['killed_by']) for m in doc['mutants']}
        expect(code == 0 and set(st.values()) == {'killed'},
               f'self-mutants: exit {code} {st} {doc["faults"]}')
        expect('numbers:current' in kb.get('drop-gate-flip-arm', '')
               and 'numbers:frozen' in kb['drop-gate-flip-arm']
               and 'gate_flip_arms' in kb['drop-gate-flip-arm']
               and kb.get('loosen-k0-exit', '').startswith('selftest')
               and kb.get('k6-any-nonzero', '').startswith('selftest'),
               f'self-mutants: killed_by {kb}')
        synthetic = {
            'noop': ('observably equivalent edit',
                     (("print('fake selftest', 'ok'",
                       "print('fake selftest:', 'ok'"),)),
            'missing': ('absent site', (('no such source text', 'x'),)),
            'ambiguous': ('repeated site', (('import ', 'import  '),)),
            'invalid': ('non-compiling edit',
                        (('def selftest():', 'def selftest(:'),)),
        }
        doc, code = run_self_mutants(_args(paths, '--self-mutants',
                                           '--baseline-runs', '1'),
                                     mutants=synthetic)
        expect(code == 1 and doc['summary'] == {
            'noop': 'survived', 'missing': 'site_missing',
            'ambiguous': 'site_ambiguous', 'invalid': 'invalid_mutation'},
            f'self-mutants synthetic: exit {code} {doc.get("summary")}')
        paths = _selftest_tree(root, 'noselftest', gitroot, test_rev)
        doc, code = run_self_mutants(_args(paths, '--self-mutants',
                                           '--mutant', 'loosen-k0-exit'))
        expect(code == 1 and doc['summary'] == {'loosen-k0-exit': 'survived'}
               and doc['baseline']['selftest']['available'] is False,
               f'self-mutants without selftest: exit {code} '
               f'{doc.get("summary")}')
        expect(sha256_bytes(paths['controls'].read_bytes()) == sha256_bytes(
            _fake_source(paths['controls'].parents[2], 'noselftest')
            .encode()), 'self-mutants: original controls untouched')
        paths = _selftest_tree(root, 'flaky', gitroot, test_rev)
        doc, code = run_self_mutants(_args(paths, '--self-mutants',
                                           '--mutant', 'drop-gate-flip-arm'))
        num = (doc['mutants'] or [{}])[0].get('numbers', {}).get('current',
                                                                 {})
        expect(code == 1
               and doc['summary'] == {'drop-gate-flip-arm': 'survived'}
               and doc['baseline']['current']['stable'] is False
               and num.get('differs') is True
               and num.get('credited') is False,
               f'self-mutants unstable baseline: exit {code} '
               f'{doc.get("summary")} {num}')
    finally:
        reap_scratch(root)
        shutil.rmtree(root, ignore_errors=True)

    for f in fails:
        print(f'SELFTEST FAIL {f}', file=sys.stderr)
    print(f'selftest: {n[0] - len(fails)}/{n[0]} cases passed')
    return 0 if not fails else 1


# ------------------------------------------------------------------- cli

def build_parser():
    ap = argparse.ArgumentParser(
        description='kama round-18 C1 counting command: controls.py on '
                    'frozen vs current tool+gate, or controls self-mutants.')
    ap.add_argument('--controls', help='controls.py to run (one for both '
                                       'sides)')
    ap.add_argument('--frozen-tool', help='frozen kama-llamacpp-live.py')
    ap.add_argument('--frozen-gate', help='frozen check-receipt.py')
    ap.add_argument('--tool', help='current kama-llamacpp-live.py')
    ap.add_argument('--gate', help='current check-receipt.py')
    ap.add_argument('--probe', help='kama-probe.sh (default: the controls\' '
                                    'own default, <controls>.parents[2]/'
                                    'tools/kama-probe.sh)')
    ap.add_argument('--json', action='store_true',
                    help='print the JSON report instead of the summary')
    ap.add_argument('--out', help='also write the JSON report here '
                                  '(atomic)')
    ap.add_argument('--timeout', type=float, default=CONTROLS_TIMEOUT,
                    help='seconds per controls.py run (default %(default)s)')
    ap.add_argument('--self-mutants', action='store_true',
                    help='mutate a copy of controls.py and report '
                         'killed/survived')
    ap.add_argument('--mutant', action='append', choices=sorted(MUTANTS),
                    help='self-mutants to run (default: all)')
    ap.add_argument('--baseline-runs', type=int, default=2,
                    choices=range(1, 6), metavar='N',
                    help='unmutated runs per pair (1-5, default 2)')
    ap.add_argument('--selftest-timeout', type=float,
                    default=SELFTEST_TIMEOUT,
                    help='seconds per controls --selftest run')
    ap.add_argument('--lane', default=str(DEFAULT_LANE),
                    help='lane Git repository for exact frozen-blob checks')
    ap.add_argument('--frozen-rev', default=FROZEN_REV,
                    help='revision holding the immutable frozen bytes')
    ap.add_argument('--selftest', action='store_true',
                    help="run measure.py's own selftest (no servers)")
    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    need = ['controls', 'tool', 'gate'] + (
        [] if args.self_mutants else ['frozen_tool', 'frozen_gate'])
    missing = ['--' + k.replace('_', '-') for k in need
               if getattr(args, k) is None]
    if missing:
        ap.error('required: ' + ', '.join(missing))
    runner = run_self_mutants if args.self_mutants else run_measure
    printer = print_self_mutants if args.self_mutants else print_measure
    try:
        doc, code = runner(args)
    except KeyboardInterrupt:
        print('c1-measure: interrupted (children killed, scratch removed)',
              file=sys.stderr)
        return EXIT_FAULT
    except (MeasureFault, OSError) as exc:
        print(f'c1-measure: own fault: {type(exc).__name__}: {exc}',
              file=sys.stderr)
        return EXIT_FAULT
    text = json.dumps(doc, indent=2, sort_keys=True) + '\n'
    if args.out:
        try:
            write_atomic(args.out, text)
        except (OSError, ValueError) as exc:
            message = f'cannot write --out {args.out}: {exc}'
            doc['faults'].append(message)
            doc['exit'] = EXIT_FAULT
            code = EXIT_FAULT
            print(f'c1-measure: own fault: {message}', file=sys.stderr)
            text = json.dumps(doc, indent=2, sort_keys=True) + '\n'
    if args.json:
        sys.stdout.write(text)
    else:
        printer(doc)
    for fault in doc['faults']:
        print(f'c1-measure: fault: {fault}', file=sys.stderr)
    return code


if __name__ == '__main__':
    sys.exit(main())
