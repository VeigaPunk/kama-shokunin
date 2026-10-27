#!/usr/bin/env python3
"""kama-llamacpp-live.py — ephemeral lane-owned llama.cpp server lifecycle harness.

Domain: local model serving & endpoint health (kama-shokunin). Capability
acquisition tool: it launches a caller-selected ``llama-server`` against a
digest-pinned GGUF on a free loopback port that is never a registered consumer
port, captures the documented HTTP lifecycle surfaces (loading -> ready),
runs ``tools/kama-probe.sh`` against it twice (matching and mismatched
``--expect``), then tears the server down and proves the teardown.

It is deliberately lane-owned and ephemeral: no ~/.config, ~/.omp, systemd or
service writes; the only filesystem artifacts are a temp stdout/stderr log
(deleted after the interesting lines are copied into the receipt) and the
optional ``--out`` receipt file.

Exit codes:
    0  outcome pass: every evaluated check passed
    1  outcome fail: at least one evaluated check failed
    2  outcome not-evaluated or setup-error (including internal faults)
Receipt schema: ``kama-llamacpp-live/v4`` (round 47): v3 plus a ``provenance``
block (where the server archive and the model came from, recorded from
``--server-asset-url``/``--server-asset-sha256``/``--server-member``/``--model-url``;
``tools/kama-live-replay.py`` re-acquires and verifies them) and
``teardown.log_path`` null, because the temp log is always deleted (its kept
lines are inlined in ``teardown.log_lines``). Checks record both ``passed``
(true/false/null) and ``evaluated``. A missing loading-503 observation is
not-evaluated, never a server failure. The exact child argv is recorded;
environment values are never recorded.

Receipt schema ``kama-llamacpp-live/v5`` (round 48) is v4 with provenance
verified when it is recorded (round-47 closure D3, D6). The four v4 flags
(``--server-asset-url``, ``--server-asset-sha256``, ``--server-member``,
``--model-url``) must now come together, with https URLs and a member path
without a leading ``/`` or ``..`` (argument errors: exit 2, no receipt).
``--server-archive`` (the local copy of the release archive) selects v5: it
also needs the model URL pinned to a 40-hex ``/resolve/<commit>/`` revision,
and before the server is started the tool hashes the archive (must equal the
asset sha256) and the archive member's bytes (must equal the server binary's
sha256), exiting 2 with a setup-error receipt otherwise. A v5 receipt adds
``provenance.model.commit`` and ``provenance.verified`` {``at``: ``record``,
``archive_sha256``, ``member_sha256``, ``model_sha256``}. Without
``--server-archive`` the receipt stays v4, so round-47 replays of v4 receipts
run as before.

Round 49 (schema unchanged): ``--server-archive`` verification is bounded - the
archive must be a regular file of at most 1 GiB with at most 4096 index entries,
and the member a regular, non-sparse file whose declared size equals the
``--server`` file's size, all checked before a byte of the member is hashed
(round-48 seat Sen2Live F1: a ~104-byte sparse archive made record time hash
~10^15 bytes); new tokens ``provenance-archive-not-regular``,
``-archive-too-large``, ``-archive-too-many-members``, ``-member-sparse``,
``-member-size-mismatch``. ``--witness-dir D`` (an existing directory) makes the
tool, once the server is ready and its checks ran, write ``D/ready.json``
{schema ``kama-live-witness/v1``, port, pid of the llama-server child} and keep
the server up until ``D/release`` exists (``--witness-timeout``, default 120 s),
so an outside observer can check the running binary, its listening socket and
its answers; the receipt gains ``witness`` {released, waited_ms, port, pid, dir}.
A witness dir is one run's handshake: before the server starts the tool removes an
earlier run's ``ready.json``/``release`` (and refuses a dir it cannot make empty or
write to), and when the hold ends it removes ``ready.json``, so an observer never
reads a dead pid or a release from another run.

Deps: python3 stdlib only, plus whatever the probed server and
``bash tools/kama-probe.sh`` (curl, ss) need.
"""
from __future__ import annotations

import argparse
import http.client
import hashlib
import io
import json
import fcntl
import os
import re
import shutil
import signal
import socket
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = 'kama-llamacpp-live/v4'
SCHEMA_V5 = 'kama-llamacpp-live/v5'
PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')
SCRIPT = Path(__file__).resolve()
LANE = SCRIPT.parent.parent
REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'
DEFAULT_PROBE = LANE / 'tools' / 'kama-probe.sh'

# Pinned upstream evidence for the sourced predicates (b11755).
LLAMA_COMMIT = '704366d76f8748cf9ad3df62a464bfcc8d1ae6ad'
_LLAMA_RAW = ('https://raw.githubusercontent.com/ggml-org/llama.cpp/'
              + LLAMA_COMMIT + '/tools/server/')
POPEN_RETURNCODE_DOC = (
    'https://docs.python.org/3.14/library/subprocess.html'
    '#subprocess.Popen.returncode')
# The exact JSON document a ready /health must answer (object equality;
# a 200 with {"status":"degraded"} is not ready).
HEALTH_READY_BODY = {'status': 'ok'}

# Ports that must never be served even if the OS offers them: the two known
# consumer pins plus anything the registry TSV names (parsed at runtime).
HARD_REFUSED_PORTS = {8080, 34113}
PORT_PICK_ATTEMPTS = 64

POLL_TIMEOUT = 0.5          # per-request readiness poll timeout, seconds
PROBE_TIMEOUT = 60          # seconds per kama-probe.sh invocation
TERM_GRACE = 10.0           # SIGTERM grace before SIGKILL
TRANSITION_BODY_CAP = 4096  # verbatim body kept on lifecycle transitions
LOADING_BODY_MAX = 256      # distinct loading-503 bodies kept verbatim
CAPTURE_BODY_CAP = 65536    # verbatim body kept on ready captures (= read cap)
LOG_KEEP = re.compile(r'build|model loaded|listening|loading', re.IGNORECASE)
HTTP_BODY_CAP = 65536       # max bytes read per response (R3)
LOG_TAIL_CAP = 65536        # only the last bytes of the temp log are kept
LOG_KEEP_MAX = 200          # copied log lines before truncation flag
MISMATCH_EXPECT = 'kama-not-this-model'
# Child process environment allowlist: the server sees only these names when
# present in the harness env — names are recorded, values never are.
CHILD_ENV_KEYS = ('PATH', 'HOME', 'LANG', 'LC_ALL', 'TMPDIR')


# Documentation anchors for the checks array (llama.cpp b11755).
DOC = {
    'health_ready': (
        'llama.cpp ' + _LLAMA_RAW + 'server-context.cpp L5288-5299: '
        'get_health answers res->ok({{"status","ok"}}); a 200 with any '
        'other body (e.g. {"status":"degraded"}) is not ready'
    ),
    'models_alias_id': (
        'llama.cpp tools/server README @ b11755 GET /v1/models: '
        'OpenAI-compatible list whose data[].id is the --alias value'
    ),
    'models_owned_by_llamacpp': (
        'llama.cpp server b11755 /v1/models emits owned_by "llamacpp" '
        '(observed by L1 smoke 2026-10-20: data[0].owned_by == "llamacpp")'
    ),
    'metrics_not_enabled': (
        'llama.cpp tools/server README @ b11755: GET /metrics requires the '
        '--metrics flag; without it the endpoint answers exactly 501'
    ),
    'props_alias': (
        'llama.cpp server /props returns model_alias equal to the --alias '
        'value (server_params -> props endpoint, b11755)'
    ),
    'probe_model_ok': (
        'tools/kama-probe.sh classify() contract: matching served id -> '
        'MODEL_OK reason "matched", exit 0'
    ),
    'probe_mismatch': (
        'tools/kama-probe.sh classify() contract: non-matching served id -> '
        'MODEL_MISMATCH reason "served-id-mismatch", exit 2'
    ),
    'teardown_graceful': (
        'llama.cpp ' + _LLAMA_RAW + 'server.cpp L529-534 installs '
        'signal_handler for SIGTERM, L519-523 shutdown_handler calls '
        'ctx_server.terminate(), L575-590 start_loop() unblocks and '
        'llama_server returns 0 — the documented graceful exit status; '
        'per ' + POPEN_RETURNCODE_DOC + ' a negative returncode means '
        'the child was terminated by that signal and fails; the "0" '
        'grounds on this shutdown code path plus the round-16 observed '
        'receipt (returncode 0, 3 ms), not on the Python row alone. '
        'Also requires port_listener_ownership == "child" proven before '
        'teardown, i.e. harness-initiated on our own child'
    ),
    'teardown_port_closed': (
        'lane ownership: passes only when the port was proven owned by '
        'our child earlier in this run (port_listener_ownership '
        '"child") AND refuses connections after teardown; vacuous '
        'otherwise -> fail'
    ),
    'loading_envelope_graded': (
        'llama.cpp ' + _LLAMA_RAW + 'server-http.cpp L314-325: while '
        'is_ready is false every non-frontend path answers 503 '
        '{"error":{"message":"Loading model","type":"unavailable_error"'
        ',"code":503}}. Grades EVERY distinct /v1/models 503 body; no '
        '/v1/models 503 observed -> not evaluated with '
        '{"loading_observed": false}. Bodies are deduped by sha256 '
        'and capped at LOADING_BODY_MAX, so identical repeats are '
        'graded once'
    ),
    'model_unchanged': (
        'lane input integrity, not subject behaviour: the GGUF must '
        'hash identically after teardown; only external mutation can '
        'flip it'
    ),
}


class SetupError(Exception):
    """Fatal pre-check failure; mapped to exit 2 with a stable reason token."""

    def __init__(self, code):
        super().__init__(code)
        self.code = code


class Terminated(Exception):
    """SIGINT/SIGTERM/SIGHUP delivered mid-run; teardown still runs."""


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace(
        '+00:00', 'Z')


ARCHIVE_MAX_BYTES = 1 << 30      # release assets are ~70 MB; 1 GiB is generous
MEMBER_MAX_COUNT = 4096          # archive index entries; the b11909 asset has ~60


def verify_archive_member(archive, asset_sha256, member, server_sha256, server_size=None):
    """Record-time provenance (v5): the archive must hash to asset_sha256 and its member
    to the server binary's sha256. Returns (archive_sha256, member_sha256); raises
    SetupError with a stable token otherwise. Reads the archive only; extracts nothing.

    Host-safety bounds (round 49; round-48 seat Sen2Live F1-F3, closure R1): the archive
    must be a regular file of at most ARCHIVE_MAX_BYTES (a FIFO or device path would block
    or stream forever) and is opened once, that descriptor hashed and parsed; the index is
    walked streaming with a MEMBER_MAX_COUNT cap (getmember() materialises it all); the
    member must be a regular, non-sparse file whose declared size equals server_size (the
    --server file's size) - tarfile synthesises a sparse member's declared size, so a
    ~104-byte archive could otherwise make this loop hash ~10^15 bytes. The size checks run
    before a byte of the member is read. The last occurrence of a duplicated member name
    wins, as extraction does."""
    import tarfile
    # one descriptor for the checks and the reads (round-49 seat V1Live F1: a path stat'ed
    # then re-opened could be swapped for a FIFO, which blocks open(), or a larger file);
    # O_NONBLOCK keeps open() from blocking on a FIFO and is inert for a regular file
    try:
        fd = os.open(archive, os.O_RDONLY | os.O_NONBLOCK)
    except OSError:
        raise SetupError('provenance-archive-unreadable')
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise SetupError('provenance-archive-not-regular')
        if st.st_size > ARCHIVE_MAX_BYTES:
            raise SetupError('provenance-archive-too-large')
        arc = os.fdopen(fd, 'rb')
    except BaseException:
        os.close(fd)
        raise
    with arc:
        h_arc = hashlib.sha256()
        for chunk in iter(lambda: arc.read(1 << 20), b''):
            h_arc.update(chunk)
        archive_sha = h_arc.hexdigest()
        if archive_sha != asset_sha256:
            raise SetupError('provenance-archive-digest-mismatch')
        arc.seek(0)
        try:
            with tarfile.open(fileobj=arc, mode='r:*') as tf:
                found, count = None, 0
                for info in tf:
                    count += 1
                    if count > MEMBER_MAX_COUNT:
                        raise SetupError('provenance-archive-too-many-members')
                    if info.name == member:
                        found = info
                if found is None:
                    raise SetupError('provenance-member-absent')
                if not found.isfile():
                    raise SetupError('provenance-member-not-a-file')
                if found.sparse is not None:
                    raise SetupError('provenance-member-sparse')
                if server_size is not None and found.size != server_size:
                    raise SetupError('provenance-member-size-mismatch')
                h = hashlib.sha256()
                fh = tf.extractfile(found)
                for chunk in iter(lambda: fh.read(1 << 20), b''):
                    h.update(chunk)
        except SetupError:
            raise
        except (OSError, EOFError, tarfile.TarError):
            raise SetupError('provenance-archive-unreadable')
    if h.hexdigest() != server_sha256:
        raise SetupError('provenance-member-digest-mismatch')
    return archive_sha, h.hexdigest()


WITNESS_SCHEMA = 'kama-live-witness/v1'


def prepare_witness_dir(wdir):
    """Round 49 (seat X1Offline): a witness dir carries ONE run's handshake.

    ready.json is only written once the server is ready, so an observer polling from
    the start of the run reads whatever an earlier run left behind (a dead pid, or a
    still-live server of another run) and a leftover release ends this run's hold at
    once with no observation window. Remove both before the server starts and prove
    the directory is writable, so a bad directory is a fast token instead of an
    internal fault after a server start."""
    for name in sorted(os.listdir(wdir)):
        if (name == 'ready.json' or name == 'release'
                or name.startswith('ready.json.tmp')
                or name.startswith('.witness-write-probe')):
            path = os.path.join(wdir, name)
            try:
                os.unlink(path)
            except IsADirectoryError as exc:
                raise SetupError('witness-dir-unusable:not-a-file:' + name) from exc
            except OSError as exc:
                raise SetupError('witness-dir-unusable:'
                                 + (exc.strerror or type(exc).__name__)) from exc
    probe = os.path.join(wdir, '.witness-write-probe.%d' % os.getpid())
    try:
        with open(probe, 'w') as fh:
            fh.write('')
    except OSError as exc:
        raise SetupError('witness-dir-unwritable:'
                         + (exc.strerror or type(exc).__name__)) from exc
    try:
        os.unlink(probe)
    except FileNotFoundError:
        pass  # the write proved the directory writable; the probe is already gone
    except OSError as exc:
        raise SetupError('witness-dir-unwritable:'
                         + (exc.strerror or type(exc).__name__)) from exc


def hold_for_witness(wdir, proc, port, timeout):
    """Round 49 (closure R5: a replay that never ran a server met the round-48 counter):
    announce the ready server - ready.json {schema, port, pid} written atomically in wdir,
    pid being the llama-server child itself - and keep it up until wdir/release exists,
    the child exits or `timeout` seconds pass. An outside observer can then read
    /proc/<pid>/exe, the listening socket and the server's own answers; this tool records
    only that it waited, never what the observer saw."""
    ready = {'schema': WITNESS_SCHEMA, 'port': port, 'pid': proc.pid,
             'written_utc': _utc_now()}
    ready_path = os.path.join(wdir, 'ready.json')
    # per-run temp name: a fixed ready.json.tmp is opened by every run using the
    # directory, and a second run's os.replace() then fails ENOENT (X1Offline)
    tmp = os.path.join(wdir, 'ready.json.tmp.%d' % proc.pid)
    # announce only a child that is still running (round-49 seat V1Live F2)
    if not _child_running(proc):
        raise SetupError('witness-child-exited-before-announce')
    parent = os.getppid()
    # O_EXCL|O_NOFOLLOW: a symlink planted at the temp name is never followed for the
    # write (round-49 seat Sen1Witness F1); an existing entry is a setup error
    try:
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
    except OSError as exc:
        raise SetupError('witness-dir-unusable:' + (exc.strerror or type(exc).__name__))
    with os.fdopen(fd, 'w') as fh:
        json.dump(ready, fh)
    os.replace(tmp, ready_path)
    release = os.path.join(wdir, 'release')
    t0 = time.monotonic()
    try:
        # the hold also ends when this tool's parent dies (round-49 seat X1Kill: a killed
        # replay left the server listening for the whole witness timeout, because
        # pdeathsig covers only live tool -> server); teardown then runs as usual
        while (not os.path.exists(release) and time.monotonic() - t0 < timeout
               and _child_running(proc) and os.getppid() == parent):
            time.sleep(0.05)
        waited = int((time.monotonic() - t0) * 1000)
        released = os.path.exists(release)
        orphaned = os.getppid() != parent
    finally:
        # the handshake names this run's child only while it is up: a ready.json left
        # behind is a dead pid a later observer in the same directory would read
        for path in (ready_path, tmp):
            try:
                os.unlink(path)
            except OSError:
                pass
    return {'schema': WITNESS_SCHEMA, 'dir': os.path.abspath(wdir), 'port': port,
            'pid': proc.pid, 'released': released, 'waited_ms': waited, 'orphaned': orphaned}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def install_tree(server_real):
    """Complete regular-file map and digest for dirname(server_real).
    Symlinks/nonregular entries are intentionally skipped; install_links()
    handles their policy. Any listing/stat/read OSError refuses the identity
    with SetupError rather than returning a partial comparable digest."""
    tree = {}
    directory = os.path.dirname(server_real)
    try:
        entries = sorted(os.listdir(directory))
    except OSError as exc:
        raise SetupError('install-tree-unpinnable:listdir:'
                         + (exc.strerror or type(exc).__name__)) from exc
    for name in entries:
        full = os.path.join(directory, name)
        try:
            st = os.lstat(full)
        except OSError as exc:
            raise SetupError(f'install-tree-unpinnable:lstat:{name!r}:'
                             + (exc.strerror or type(exc).__name__)) from exc
        if not stat.S_ISREG(st.st_mode):
            continue
        try:
            tree[name] = sha256_file(full)
        except OSError as exc:
            raise SetupError(f'install-tree-unpinnable:read:{name!r}:'
                             + (exc.strerror or type(exc).__name__)) from exc
    combined = hashlib.sha256(
        ''.join(f'{n} {tree[n]}\n' for n in sorted(tree)).encode()).hexdigest()
    return tree, combined


def links_digest(links):
    """sha256 over canonical JSON (sorted keys, ASCII escapes): injective for
    any {str: str} map, including names with newlines or ' -> '."""
    return hashlib.sha256(json.dumps(
        links, sort_keys=True, separators=(',', ':'),
        ensure_ascii=True).encode('ascii')).hexdigest()


def install_links(server_real, tree=None):
    """({basename: link text}, digest, problems, unpinned) for
    dirname(server_real).
    install_tree() skips symlinks, so a retargeted soname link
    (libllama.so.0 -> ...) would otherwise leave every pin unchanged. Link
    text is recorded unresolved; the gate checks that each chain ends at a
    pinned regular member. `problems` names entries that make the directory
    unpinnable: unreadable members, failed lstat/readlink, a `glibc-hwcaps`
    entry of any type except absent (the loader searches it before the
    directory itself), special files (FIFO, socket, device), symlinks whose
    target does not resolve to a regular file in the same directory, and,
    when `tree` is given, regular members absent from that map (a caller's
    partial map or files appearing between scans). install_tree itself now
    raises on I/O failure. The caller refuses any problem instead of recording
    a partial identity. `unpinned` names other subdirectories (for example a
    licensing folder in OpenVINO release archives): recorded by name, their
    contents outside this pin, never silently dropped."""
    links, problems, unpinned = {}, [], []
    directory = os.path.dirname(server_real)
    try:
        entries = sorted(os.listdir(directory))
    except OSError as exc:
        return links, None, [f'listdir:{exc.strerror}'], unpinned
    for name in entries:
        full = os.path.join(directory, name)
        if any(ord(ch) < 0x20 for ch in name):
            # install_tree's 'name sha\n' lines are ambiguous for such names
            problems.append(f'{name!r}:control-character-in-name')
            continue
        if name == 'glibc-hwcaps':
            problems.append(f'{name}:loader-searched-subdirectory')
            continue
        try:
            mode = os.lstat(full).st_mode
            if stat.S_ISLNK(mode):
                links[name] = os.readlink(full)
                real = os.path.realpath(full)
                if not (os.path.isfile(real) and os.path.dirname(real)
                        == os.path.realpath(directory)):
                    problems.append(f'{name}:link-not-to-member')
            elif stat.S_ISDIR(mode):
                unpinned.append(name)
            elif not stat.S_ISREG(mode):
                problems.append(f'{name}:not-regular-or-symlink')
            elif not os.access(full, os.R_OK):
                problems.append(f'{name}:unreadable')
            elif tree is not None and name not in tree:
                problems.append(f'{name}:not-hashed')
        except OSError as exc:
            problems.append(f'{name}:{exc.strerror}')
    return links, links_digest(links), problems, unpinned


def _envelope_ok(body_text):
    """True iff one loading-503 body parses to the documented envelope:
    error.message=="Loading model", error.type=="unavailable_error",
    error.code is int and ==503."""
    try:
        doc = json.loads(body_text or '')
    except (ValueError, TypeError):
        return False
    err = doc.get('error') if isinstance(doc, dict) else None
    if not isinstance(err, dict):
        return False
    code = err.get('code')
    return (err.get('message') == 'Loading model'
            and err.get('type') == 'unavailable_error'
            and type(code) is int and code == 503)


def loading_envelope_exact(loading_503):
    """Envelope grade of the first captured 503 body (receipt field
    loading_envelope_exact): True/False, or None when no 503 was seen.
    Not a check."""
    if loading_503 is None:
        return None
    return _envelope_ok(loading_503.get('body'))


def loading_envelopes_all(bodies):
    """True iff every distinct captured 503 body is the exact envelope;
    None when no body was captured. Grounds loading_envelope_graded."""
    if not bodies:
        return None
    return all(_envelope_ok(b.get('body')) for b in bodies)


class _BodyLog(list):
    """Distinct loading-503 bodies, plus the count dropped past
    LOADING_BODY_MAX so coverage limits are recorded, never hidden.
    Serializes as a plain JSON array."""
    dropped = 0


def refused_ports():
    """Ports we must never serve: hardcoded pins + every port token the
    registry TSV expresses (host:port, --port N, port=N markers; a bare digit
    run like 'Qwen3-Coder-30B' is never a port)."""
    refused = set(HARD_REFUSED_PORTS)
    try:
        text = REGISTRY.read_text(encoding='utf-8', errors='replace')
    except OSError:
        raise SetupError(f'registry-unreadable:{REGISTRY}')
    patterns = (
        r'(?:\d{1,3}\.){3}\d{1,3}:(\d{1,5})',
        r'localhost:(\d{1,5})',
        r'\[?::1\]?:?(\d{1,5})\b',  # only inside a URL-ish context; still guarded by range check
        r'--port[ =](\d{1,5})',
        r'\bport=(\d{1,5})',
        r'\bhost:(\d{1,5})',
    )
    for pat in patterns:
        for m in re.finditer(pat, text):
            try:
                n = int(m.group(1))
            except ValueError:
                continue
            if 1 <= n <= 65535:
                refused.add(n)
    return refused



def pick_port(refused, requested=None):
    """Select the serve port.

    Explicit --port: must clear the refused set AND refuse connections now
    (a live listener means the port is already in use). This is the only
    path that can exercise a refusal of a sub-ephemeral port like 8080 —
    the kernel's bind(:0) range is 32768-60999, so 34113 CAN be offered
    while 8080 cannot (port-gate advice, round 16).

    Default: bind 127.0.0.1:0, take the offered port, release; retry when
    refused. The release/rebind race is documented in the receipt.
    Never pass 0 through to llama-server: it would bind before any refusal
    check could reject a kernel-chosen registered port."""
    if requested is not None:
        if not (1 <= requested <= 65535):
            raise SetupError('explicit-port-out-of-range')
        if requested in refused:
            raise SetupError(f'port-refused-registered:{requested}')
        try:
            socket.create_connection(('127.0.0.1', requested),
                                     timeout=1.0).close()
        except ConnectionRefusedError:
            return requested
        except OSError:
            return requested  # timeout/reset: no proven listener; try anyway
        raise SetupError(f'port-in-use:{requested}')
    for _ in range(PORT_PICK_ATTEMPTS):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('127.0.0.1', 0))
            port = s.getsockname()[1]
        if port not in refused:
            return port
    raise SetupError('no-free-unregistered-port')


def _tcp6_is_loopback(addr_hex):
    """Recognize procfs tcp6 addresses after reversing each host-endian word."""
    if len(addr_hex) != 32:
        return False
    try:
        raw = bytes.fromhex(addr_hex)
    except ValueError:
        return False
    address = bytearray(16)
    for start in range(0, 16, 4):
        address[start:start + 4] = raw[start:start + 4][::-1]
    address = bytes(address)
    return (address == b'\0' * 15 + b'\1'
            or (address[:12] == b'\0' * 10 + b'\xff\xff'
                and address[12] == 127))


def _proc_listener_inode(proc_net, line, port):
    """Return an eligible loopback LISTEN inode from one procfs row."""
    parts = line.split()
    if len(parts) < 10 or parts[3] != '0A':
        return None
    try:
        addr_hex, port_hex = parts[1].rsplit(':', 1)
        if int(port_hex, 16) != port:
            return None
        if proc_net.endswith('tcp6'):
            if not _tcp6_is_loopback(addr_hex):
                return None
        elif (len(addr_hex) != 8
              or addr_hex[-2:].upper() != '7F'):
            return None
        return parts[9]
    except (ValueError, IndexError):
        return None


def _listen_inodes(port):
    """Socket inodes LISTENing on `port` AND bound to loopback in procfs.

    IPv4 addresses use little-endian byte order. Each 32-bit word in tcp6's
    address column is also little-endian; reversing each word yields the
    network-order IPv6 address. Native ::1 and IPv4-mapped 127/8 are loopback.
    Wildcard addresses are deliberately not counted — fail-closed.
    """
    inodes = set()
    for proc_net in ('/proc/net/tcp', '/proc/net/tcp6'):
        try:
            with open(proc_net, encoding='ascii') as fh:
                next(fh, None)
                for line in fh:
                    inode = _proc_listener_inode(proc_net, line, port)
                    if inode is not None:
                        inodes.add(inode)
        except (OSError, ValueError, IndexError):
            continue
    return inodes


def port_owned_by(pid, port):
    """True: a LISTEN socket on `port` is an fd of `pid` (our child owns it).
    False: listener exists but none of its inodes is in the child's fd table
    (a stranger can satisfy /health before the child's bind failure lands).
    None: no listener yet, or /proc unreadable (ownership unknown)."""
    try:
        inodes = _listen_inodes(port)
        if not inodes:
            return None
        wanted = {f'socket:[{i}]' for i in inodes}
        for fd in os.listdir(f'/proc/{pid}/fd'):
            try:
                if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
                    return True
            except OSError:
                continue
        return False
    except OSError:
        return None


def _preexec_pdeathsig():
    """Child-side: die with SIGKILL if the harness parent dies (Linux).
    Outcome is not observable post-close_fds, so the receipt records
    prctl_ok 'unknown' honestly rather than a guessed boolean (F2)."""
    try:
        import ctypes
        libc = ctypes.CDLL(None, use_errno=True)
        libc.prctl(1, signal.SIGKILL, 0, 0, 0)  # PR_SET_PDEATHSIG
        if os.getppid() != _FORKED_PPID[0]:
            os._exit(1)  # parent already gone before prctl landed
    except Exception:  # pragma: no cover - best effort hardening
        pass


_FORKED_PPID = [0]


def model_mapping(pid, model_path):
    """Round 50 (round-49 closure R1, seats K1Design, R0Controls: the model bytes the server
    loaded were not bound): the file-backed mapping of the server child whose pathname is
    the --model file, read from /proc/<pid>/maps (proc_pid_maps(5): `dev` major:minor,
    `inode`, `pathname`), and the sha256 of that same file - opened by its pathname with
    O_NOFOLLOW, accepted only when fstat() shows the dev and inode the maps line shows,
    a regular file no larger than when it was mapped - so the receipt records the bytes
    the running server maps, not a path the tool was handed. Linux only; any other
    outcome is recorded as `mapped: False` with its reason, never guessed."""
    want = os.path.realpath(model_path)
    try:
        with open(f'/proc/{pid}/maps') as fh:
            rows = fh.read().splitlines()
    except OSError as exc:
        return {'mapped': False, 'reason': 'maps-unreadable:' + (exc.strerror or type(exc).__name__)}
    hits = []
    for row in rows:
        f = row.split(None, 5)
        if len(f) == 6 and f[4] != '0' and f[5] == want and (f[3], f[4]) not in hits:
            hits.append((f[3], f[4]))
    if not hits:
        return {'mapped': False, 'reason': 'model-path-not-in-maps', 'path': want}
    if len(hits) != 1:
        return {'mapped': False, 'reason': 'model-path-maps-several-files', 'path': want}
    dev, ino = hits[0]
    try:
        fd = os.open(want, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except OSError as exc:
        return {'mapped': False, 'reason': 'model-open-failed:' + (exc.strerror or type(exc).__name__),
                'path': want, 'dev': dev, 'inode': ino}
    try:
        st = os.fstat(fd)
        sdev = '%02x:%02x' % (os.major(st.st_dev), os.minor(st.st_dev))
        if not stat.S_ISREG(st.st_mode) or sdev != dev or str(st.st_ino) != ino:
            return {'mapped': False, 'reason': 'mapped-file-is-not-the-model-path', 'path': want,
                    'dev': dev, 'inode': ino, 'path_dev': sdev, 'path_inode': str(st.st_ino)}
        h, left = hashlib.sha256(), st.st_size
        while left > 0:
            chunk = os.read(fd, min(1 << 20, left))
            if not chunk:
                break
            h.update(chunk)
            left -= len(chunk)
        if left != 0:
            return {'mapped': False, 'reason': 'model-shrank-while-hashed', 'path': want,
                    'dev': dev, 'inode': ino}
    finally:
        os.close(fd)
    return {'mapped': True, 'path': want, 'dev': dev, 'inode': ino, 'size': st.st_size,
            'sha256': h.hexdigest()}


def server_exe(pid):
    """Round 51 (round-50 closure R6, seat J4Decoy: a decoy replay that exec'd the host's own
    b11909 install met the round-50 counter): the executable the server child is running,
    opened through /proc/<pid>/exe - proc_pid_exe(5): "attempting to open it will open the
    executable" - so the dev and inode fstat() shows and the sha256 of the bytes read are
    the running image itself, not a path the tool was handed and not whatever sits at that
    path now. `path` is the readlink(2) text (it ends in " (deleted)" when the file was
    unlinked). Linux only; any other outcome is `opened: False` with its reason."""
    link = f'/proc/{pid}/exe'
    try:
        path = os.readlink(link)
        fd = os.open(link, os.O_RDONLY)
    except OSError as exc:
        return {'opened': False, 'reason': 'exe-unreadable:' + (exc.strerror or type(exc).__name__)}
    try:
        st = os.fstat(fd)
        seals = file_seals(fd)
        if not stat.S_ISREG(st.st_mode):
            return {'opened': False, 'reason': 'exe-not-a-regular-file', 'path': path}
        h, left = hashlib.sha256(), st.st_size
        while left > 0:
            chunk = os.read(fd, min(1 << 20, left))
            if not chunk:
                break
            h.update(chunk)
            left -= len(chunk)
        if left != 0:
            return {'opened': False, 'reason': 'exe-shrank-while-hashed', 'path': path}
    except OSError as exc:
        # round-51 seat V2Review: a read error is recorded, never raised past the docstring
        return {'opened': False, 'reason': 'exe-read-failed:' + (exc.strerror or type(exc).__name__),
                'path': path}
    finally:
        os.close(fd)
    # round 52: `seals` is fcntl(F_GET_SEALS) on the opened image (None for a file that
    # does not support sealing) and `nlink` its link count - a sealed memfd (memfd_create(2))
    # has no directory entry, so no copy, hardlink or rename-over at a path can be it
    return {'opened': True, 'path': path,
            'dev': '%02x:%02x' % (os.major(st.st_dev), os.minor(st.st_dev)),
            'inode': str(st.st_ino), 'size': st.st_size, 'sha256': h.hexdigest(),
            'nlink': st.st_nlink, 'seals': seals}


def code_mappings(pid):
    """Round 53 (round-52 closure R2, seat K2Design: the launcher's code lives in
    libllama-server-impl.so and libggml*, which load by path): every executable file
    mapping of the server child (/proc/<pid>/maps, proc_pid_maps(5): an `x` in `perms`, a
    pathname starting with `/`; the anonymous `/memfd:` image is server_exe's), each
    opened by its pathname with O_NOFOLLOW and hashed only when fstat() shows the inode the
    maps line shows (and its dev, except for root-owned files: this host's btrfs/overlay
    root reports another st_dev than maps does), so the receipt records the bytes behind
    each mapping, its owner, and never a path the tool was handed. A mapping that cannot
    be matched is recorded with `opened: False` and its reason, never guessed. Linux only."""
    try:
        with open(f'/proc/{pid}/maps') as fh:
            rows = fh.read().splitlines()
    except OSError as exc:
        return {'read': False, 'reason': 'maps-unreadable:' + (exc.strerror or type(exc).__name__)}
    seen, out = set(), []
    for row in rows:
        f = row.split(None, 5)
        if (len(f) < 6 or 'x' not in f[1]
                or f[5].startswith('/memfd:') or (f[5], f[3], f[4]) in seen):
            continue
        seen.add((f[5], f[3], f[4]))
        path, dev, ino = f[5], f[3], f[4]
        ent = {'path': path, 'dev': dev, 'inode': ino}
        if path.endswith(' (deleted)'):
            # the mapped file has no directory entry any more (rename-over or unlink): the
            # name is not opened, so a file that happens to carry that name is never hashed
            out.append({**ent, 'opened': False, 'reason': 'mapped-file-deleted'})
            continue
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        except OSError as exc:
            out.append({**ent, 'opened': False,
                        'reason': 'open-failed:' + (exc.strerror or type(exc).__name__)})
            continue
        try:
            st = os.fstat(fd)
            sdev = '%02x:%02x' % (os.major(st.st_dev), os.minor(st.st_dev))
            if (not stat.S_ISREG(st.st_mode) or str(st.st_ino) != ino
                    or (sdev != dev and st.st_uid != 0)):
                out.append({**ent, 'opened': False, 'reason': 'path-is-not-the-mapped-file',
                            'path_dev': sdev, 'path_inode': str(st.st_ino)})
                continue
            h, left = hashlib.sha256(), st.st_size
            while left > 0:
                chunk = os.read(fd, min(1 << 20, left))
                if not chunk:
                    break
                h.update(chunk)
                left -= len(chunk)
            if left != 0:
                out.append({**ent, 'opened': False, 'reason': 'file-shrank-while-hashed'})
                continue
            out.append({**ent, 'opened': True, 'size': st.st_size, 'uid': st.st_uid,
                        'sha256': h.hexdigest()})
        except OSError as exc:
            out.append({**ent, 'opened': False,
                        'reason': 'read-failed:' + (exc.strerror or type(exc).__name__)})
        finally:
            os.close(fd)
    return {'read': True, 'mappings': out}


F_GET_SEALS = 1034          # F_LINUX_SPECIFIC_BASE + 10 (fcntl(2))
SEALS_ALL = 15              # F_SEAL_SEAL | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_WRITE
F_SEAL_EXEC = 32            # fcntl(2): the execute bits are frozen


def memfd_noexec():
    """Round 52 (seat Sen1Exec): vm.memfd_noexec as this pid namespace reports it (kernel
    mfd_noexec documentation, S502: at 1 a memfd_create() without MFD_EXEC acts as
    MFD_NOEXEC_SEAL, at 2 it is refused), named in the refusal below."""
    try:
        with open('/proc/sys/vm/memfd_noexec', encoding='ascii') as fh:
            return fh.read().strip() or 'empty'
    except OSError as exc:
        return 'unreadable:' + (exc.strerror or type(exc).__name__)


def file_seals(fd):
    """fcntl(F_GET_SEALS) on fd; None when the file does not support sealing (EINVAL)."""
    try:
        return fcntl.fcntl(fd, F_GET_SEALS)
    except OSError:
        return None


def sealed_fd(fd, want_sha, want_size):
    """Round 52: the inherited --server-fd must be a sealed memfd holding exactly the bytes
    of --server (memfd_create(2): an anonymous file; seals write/shrink/grow/seal), read
    with pread from offset 0 so the descriptor's own offset does not matter. Returns its
    identity; raises SetupError otherwise."""
    try:
        st = os.fstat(fd)
    except OSError as exc:
        raise SetupError(f'server-fd-unusable:{exc.strerror}') from exc
    seals = file_seals(fd)
    if not stat.S_ISREG(st.st_mode) or seals is None or seals & SEALS_ALL != SEALS_ALL:
        raise SetupError(f'server-fd-not-sealed:{seals}')
    if seals & F_SEAL_EXEC:
        # F_SEAL_EXEC freezes the exec bits off (a memfd made without MFD_EXEC on a host
        # with vm.memfd_noexec >= 1): the exec below would fail EACCES, so say why now
        raise SetupError('server-fd-not-executable:F_SEAL_EXEC:memfd_noexec='
                         + memfd_noexec())
    if st.st_size != want_size:
        raise SetupError(f'server-fd-size:{st.st_size}!={want_size}')
    h, off = hashlib.sha256(), 0
    while off < st.st_size:
        chunk = os.pread(fd, min(1 << 20, st.st_size - off), off)
        if not chunk:
            break
        h.update(chunk)
        off += len(chunk)
    if h.hexdigest() != want_sha:
        raise SetupError('server-fd-digest-differs-from-server')
    return {'dev': '%02x:%02x' % (os.major(st.st_dev), os.minor(st.st_dev)),
            'inode': str(st.st_ino), 'nlink': st.st_nlink, 'seals': seals,
            'sha256': h.hexdigest()}


def _header_subset(headers):
    return {
        'server': headers.get('Server'),
        'content-type': headers.get('Content-Type'),
    }


def http_get(port, path, timeout=POLL_TIMEOUT):
    """One loopback GET. Returns dict(status|None, error|None, headers,
    body, body_truncated). At most HTTP_BODY_CAP+1 bytes are read; the flag
    marks a truncated read. HTTPError is a normal response (status set);
    URLError/socket errors give status=None and an error class name."""
    url = f'http://127.0.0.1:{port}{path}'
    req = urllib.request.Request(url, method='GET')

    def _result(status, headers, raw):
        return {
            'status': status,
            'error': None,
            'headers': dict(headers),
            'body': raw[:HTTP_BODY_CAP],
            'body_truncated': len(raw) > HTTP_BODY_CAP,
        }

    try:
        with _OPENER.open(req, timeout=timeout) as resp:
            return _result(resp.status, resp.headers.items(),
                           resp.read(HTTP_BODY_CAP + 1))
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read(HTTP_BODY_CAP + 1)
        except OSError:
            raw = b''
        return _result(exc.code,
                       exc.headers.items() if exc.headers else {}, raw)
    except urllib.error.URLError as exc:
        reason = getattr(exc, 'reason', exc)
        return {'status': None, 'error': type(reason).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}
    except (OSError, socket.timeout, TimeoutError) as exc:
        return {'status': None, 'error': type(exc).__name__,
                'headers': {}, 'body': b'', 'body_truncated': False}


def _decode_body(body, cap):
    """Return (text_or_None, truncated_bool); None when body exceeds cap."""
    if len(body) > cap:
        return None, True
    return body.decode('utf-8', errors='replace'), False


def _transition_row(t0, path, result):
    body_text, truncated = _decode_body(result['body'], TRANSITION_BODY_CAP)
    return {
        't_ms': round((time.monotonic() - t0) * 1000),
        'path': path,
        'status': result['status'],
        'error': result['error'],
        'body_sha256': hashlib.sha256(result['body']).hexdigest(),
        'body': body_text,
        'body_read_truncated': result.get('body_truncated', False),
        'body_over_cap': truncated,
        'headers': _header_subset(result['headers']),
        'repeats': 0,
    }


def _sig(row):
    return (row['status'], row['error'], row['body_sha256'])


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """F3: refuse redirects — a 30x must surface as its own status, never
    be followed to a foreign document."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                      _NoRedirect)


class _KeepAlive:
    """Reused http.client connection for the tight readiness polls.
    Recycled once on transport errors so a server-side close is retried."""

    def __init__(self, port, timeout=POLL_TIMEOUT):
        self.port = port
        self.timeout = timeout
        self.conn = None

    def get(self, path):
        for attempt in range(2):
            try:
                if self.conn is None:
                    self.conn = http.client.HTTPConnection(
                        '127.0.0.1', self.port, timeout=self.timeout)
                self.conn.request('GET', path)
                resp = self.conn.getresponse()
                raw = resp.read(HTTP_BODY_CAP + 1)
                return {'status': resp.status, 'error': None,
                        'headers': dict(resp.getheaders()),
                        'body': raw[:HTTP_BODY_CAP],
                        'body_truncated': len(raw) > HTTP_BODY_CAP}
            except (OSError, http.client.HTTPException) as exc:
                self._close()
                if attempt == 1:
                    return {'status': None, 'error': type(exc).__name__,
                            'headers': {}, 'body': b'',
                            'body_truncated': False}

    def _close(self):
        try:
            if self.conn is not None:
                self.conn.close()
        finally:
            self.conn = None


def readiness_loop(proc, port, ready_timeout):
    """Two-phase lifecycle capture (ExecLoadingWindowCapture design):

    Phase 'models': GET /v1/models on a reused keep-alive connection, NO
    sleep, 0.5 s per-request timeout, until the first non-503 answer — the
    ~5-6 ms loading window needs an unbroken request cadence. The first 503
    is kept verbatim in loading_503, and every distinct 503 body is kept
    in loading_bodies (status, Server/Content-Type, body <=4096, sha256).

    Phase 'health': GET /health the same way until 200.

    D1: the FIRST successful HTTP response (any status) immediately triggers
    port_owned_by(child, port); foreign or unproven ownership discards every
    recorded body and is a setup error — a stranger's loading body can never
    reach loading_503.
    Returns (transitions, loading_503, loading_bodies, ready,
    failure_code, ownership). loading_bodies lists every DISTINCT 503
    body (deduped by sha256, repeats counted, capped) so the graded
    check covers all observed envelopes, not just the first."""
    t0 = time.monotonic()
    deadline = t0 + ready_timeout
    transitions = []
    loading_503 = None
    loading_bodies = _BodyLog()   # every distinct 503 body, {path,
                                  # body_sha256, body, repeats}
    _seen_503 = {}                # body_sha256 -> index into loading_bodies
    ownership = None
    proven = False
    conn = _KeepAlive(port)

    def _observe(phase, path, result):
        nonlocal loading_503, ownership, proven
        row = _transition_row(t0, path, result)
        row['phase'] = phase
        sig = _sig(row)
        if transitions and _sig(transitions[-1]) == sig \
                and transitions[-1]['path'] == path:
            transitions[-1]['repeats'] += 1
            transitions[-1]['t_ms'] = row['t_ms']
        else:
            transitions.append(row)
        if result['status'] is not None and not proven:
            # D1: prove the child owns the listener on first contact
            owned = port_owned_by(proc.pid, port)
            ownership = owned
            if owned is not True:
                return ('port-listener-not-our-child' if owned is False
                        else 'port-listener-ownership-unproven')
            proven = True
        if (result['status'] == 503 and path == '/v1/models'
                and proven):
            body_text = result['body'][:TRANSITION_BODY_CAP].decode(
                'utf-8', errors='replace')
            sha = row['body_sha256']
            if sha in _seen_503:
                loading_bodies[_seen_503[sha]]['repeats'] += 1
            elif len(loading_bodies) < LOADING_BODY_MAX:
                _seen_503[sha] = len(loading_bodies)
                loading_bodies.append({'path': path,
                                       'body_sha256': sha,
                                       'body': body_text,
                                       'repeats': 0})
            else:
                loading_bodies.dropped += 1
            if loading_503 is None:
                loading_503 = {
                    't_ms': row['t_ms'],
                    'path': path,
                    'status': 503,
                    'headers': _header_subset(result['headers']),
                    'body_sha256': sha,
                    'body': body_text,
                }
        return None

    try:
        while time.monotonic() < deadline:
            rc = proc.poll()
            if rc is not None:
                return (transitions, loading_503, loading_bodies, False,
                        f'server-exited-early-rc{rc}', ownership)
            err = _observe('models', '/v1/models', conn.get('/v1/models'))
            if err:
                _discard_bodies(transitions, loading_503, loading_bodies)
                return transitions, None, [], False, err, ownership
            if transitions[-1]['status'] not in (None, 503):
                break
        else:
            return (transitions, loading_503, loading_bodies, False,
                    'ready-timeout', ownership)
        while time.monotonic() < deadline:
            rc = proc.poll()
            if rc is not None:
                return (transitions, loading_503, loading_bodies, False,
                        f'server-exited-early-rc{rc}', ownership)
            err = _observe('health', '/health', conn.get('/health'))
            if err:
                _discard_bodies(transitions, loading_503, loading_bodies)
                return transitions, None, [], False, err, ownership
            if transitions[-1]['status'] == 200 \
                    and transitions[-1]['path'] == '/health':
                return (transitions, loading_503, loading_bodies, True,
                        None, ownership)
        return (transitions, loading_503, loading_bodies, False,
                'ready-timeout', ownership)
    finally:
        conn._close()


def _discard_bodies(transitions, loading_503, loading_bodies=()):
    """D1: on an ownership failure, no recorded body may survive — a
    stranger's response must never reach the receipt."""
    for row in transitions:
        row['body'] = None
        row['body_sha256'] = None
    if loading_503 is not None:
        loading_503['body'] = None
        loading_503['body_sha256'] = None
    for b in loading_bodies:
        b['body'] = None
        b['body_sha256'] = None


def verify_live(proc, port, label):
    """R1 liveness gate: child must be running AND provably own the LISTEN
    socket. Returns (error_code|None, ownership) — 'child'/'foreign'/
    'unproven'. Callers: before ready_captures, before each probe, after
    probes."""
    if proc.poll() is not None:
        return f'{label}:child-exited-rc{proc.returncode}', 'unproven'
    owned = port_owned_by(proc.pid, port)
    if owned is not True:
        code = ('port-listener-not-our-child' if owned is False
                else 'port-listener-ownership-unproven')
        return f'{label}:{code}', 'foreign' if owned is False else 'unproven'
    return None, 'child'


def _capture(port, path, keep_body):
    result = http_get(port, path, timeout=10.0)
    cap = {
        'path': path,
        'status': result['status'],
        'error': result['error'],
        'headers': dict(result['headers']),
        'body_sha256': hashlib.sha256(result['body']).hexdigest(),
        'body_read_truncated': result.get('body_truncated', False),
    }
    if keep_body:
        text, truncated = _decode_body(result['body'], CAPTURE_BODY_CAP)
        cap['body'] = text
        cap['body_truncated'] = truncated
    return cap, result


def ready_captures(port):
    """Documented lifecycle surfaces once /health is 200."""
    captures = {}
    health, health_res = _capture(port, '/health', keep_body=True)
    captures['health'] = health

    models, models_res = _capture(port, '/v1/models', keep_body=True)
    captures['models'] = models
    models_doc = None
    try:
        models_doc = json.loads(models_res['body'])
    except (ValueError, TypeError):
        pass
    captures['_models_doc'] = models_doc  # stripped before emit

    props, props_res = _capture(port, '/props', keep_body=False)
    props_fields = None
    try:
        doc = json.loads(props_res['body'])
        if isinstance(doc, dict):
            dgs = doc.get('default_generation_settings')
            props_fields = {
                'model_alias': doc.get('model_alias'),
                'total_slots': doc.get('total_slots'),
                'is_sleeping': doc.get('is_sleeping'),
                'build_info': doc.get('build_info'),
                'default_generation_settings.n_ctx':
                    dgs.get('n_ctx') if isinstance(dgs, dict) else None,
            }
    except (ValueError, TypeError):
        pass
    props['fields'] = props_fields
    captures['props'] = props

    slots, slots_res = _capture(port, '/slots', keep_body=False)
    slots_count = None
    try:
        doc = json.loads(slots_res['body'])
        if isinstance(doc, list):
            slots_count = len(doc)
    except (ValueError, TypeError):
        pass
    slots['element_count'] = slots_count
    captures['slots'] = slots

    metrics, _ = _capture(port, '/metrics', keep_body=False)
    captures['metrics'] = {'path': '/metrics', 'status': metrics['status'],
                           'error': metrics['error']}
    return captures


def run_probe(probe, port, expect, child_env):
    """bash PROBE check --port P --expect E --json --timeout 2
    --connect-timeout 1. Returns parsed JSON + exit. Runs under the same
    allowlisted env as the server child (no proxy vars can redirect it);
    subprocess-level timeout is 60 s."""
    argv = ['bash', str(probe), 'check', '--port', str(port),
            '--expect', expect, '--json',
            '--timeout', '2', '--connect-timeout', '1']
    rec = {'expect': expect, 'argv': argv, 'exit': None,
           'result': None, 'stderr_tail': None}
    try:
        cp = subprocess.run(argv, capture_output=True, text=True,
                            timeout=PROBE_TIMEOUT, env=child_env)
    except subprocess.TimeoutExpired:
        rec['exit'] = None
        rec['stderr_tail'] = f'timeout after {PROBE_TIMEOUT}s'
        return rec
    rec['exit'] = cp.returncode
    if cp.stderr:
        rec['stderr_tail'] = cp.stderr[-2000:]
    try:
        rec['result'] = json.loads(cp.stdout)
    except (ValueError, TypeError):
        rec['result'] = None
        rec['stdout_tail'] = (cp.stdout or '')[-2000:]
    return rec


def probe_row(rec):
    """First rows[] element of a parsed kama-probe check payload, or None."""
    doc = rec.get('result')
    if not isinstance(doc, dict):
        return None
    rows = doc.get('rows')
    if isinstance(rows, list) and rows and isinstance(rows[0], dict):
        return rows[0]
    return None


def _child_running(proc):
    """Fresh aliveness: poll() reaps a self-exited child. False when the
    process is gone or the state cannot be proven — killpg stays off a
    dead child so its pgid can never hit a reincarnated process."""
    try:
        return proc is not None and proc.poll() is None
    except Exception:
        return False


def _port_refuses(port):
    """True iff a loopback connect to `port` is refused; False for any
    other outcome (a live listener, timeout, or reset)."""
    try:
        socket.create_connection(('127.0.0.1', port), timeout=1.0).close()
        return False
    except ConnectionRefusedError:
        return True
    except OSError:
        return False


def teardown(proc, port, log_path):
    """SIGTERM the process group, SIGKILL after TERM_GRACE, then prove the
    port refuses connections and reduce the temp log to kept lines.
    alive_at_teardown_start records whether the child was still running
    when teardown began — a self-exited child was never signalled."""
    out = {'returncode': None, 'sigterm_sent': False, 'sigkill_sent': False,
           'alive_at_teardown_start': _child_running(proc),
           'term_wait_ms': None, 'port_refuses': None, 'log_lines': [],
           'log_lines_truncated': False, 'log_path': None}
    if out['alive_at_teardown_start']:  # F5: killpg only on a live child
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            out['sigterm_sent'] = True  # recorded only on delivery
        except (ProcessLookupError, PermissionError, OSError):
            pass
    if proc is not None:
        t0 = time.monotonic()
        try:
            proc.wait(timeout=TERM_GRACE)
        except subprocess.TimeoutExpired:
            if _child_running(proc):  # re-check: it may have exited just now
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    out['sigkill_sent'] = True
                except (ProcessLookupError, PermissionError, OSError):
                    pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
        out['term_wait_ms'] = round((time.monotonic() - t0) * 1000)
        out['returncode'] = proc.returncode
    # prove the port is closed
    out['port_refuses'] = _port_refuses(port)
    # reduce the log to kept lines; the temp file is unlinked even when
    # reduction raises, so an internal fault never leaves it behind
    try:
        try:
            with open(log_path, 'rb') as fh:  # keep only the last LOG_TAIL_CAP bytes (R3)
                fh.seek(0, os.SEEK_END)
                size = fh.tell()
                fh.seek(max(0, size - LOG_TAIL_CAP))
                tail = fh.read()
            text = tail.decode('utf-8', errors='replace')
            out['log_tail_truncated'] = size > LOG_TAIL_CAP
        except OSError:
            text = ''
            out['log_tail_truncated'] = None
        kept = [ln for ln in text.splitlines() if LOG_KEEP.search(ln)]
        out['log_lines_truncated'] = len(kept) > LOG_KEEP_MAX
        out['log_lines'] = kept[:LOG_KEEP_MAX]
    finally:
        try:
            os.unlink(log_path)
        except OSError:
            pass
    return out


def _check(check_id, passed, observed, not_evaluated_reason=None):
    if passed is None:
        if not_evaluated_reason is None:
            raise ValueError('a null check needs a not-evaluated reason')
        observed = dict(observed) if isinstance(observed, dict) else {
            'value': observed}
        observed['not_evaluated_reason'] = not_evaluated_reason
        evaluated = False
    else:
        passed = bool(passed)
        evaluated = True
    return {'id': check_id, 'documented_by': DOC[check_id],
            'passed': passed, 'evaluated': evaluated,
            'observed': observed}


def _outcome_exit(checks, setup_error):
    """Return the v3 outcome and process exit code from check state."""
    if setup_error is not None:
        return 'setup-error', 2
    states = [check.get('passed') for check in checks
              if isinstance(check, dict)]
    if any(state is False for state in states):
        return 'fail', 1
    if any(state is None for state in states):
        return 'not-evaluated', 2
    if states and all(state is True for state in states):
        return 'pass', 0
    return 'setup-error', 2


def _record_internal(receipt, exc):
    token = f'internal:{type(exc).__name__}'
    receipt['internal_fault'] = token
    receipt['setup_error'] = token


def _restore_signal_handlers(old_handlers, receipt, saved=False):
    """Ignore or restore the pre-harness signal dispositions.

    Never raises: a fault while materialising or walking the mapping is
    recorded on the receipt and must not abort the finalizer (teardown,
    safety-net kill and receipt emission still run). Returns True when a
    restore fault was recorded. `saved=False` sets SIG_IGN (finalizer);
    `saved=True` restores each saved handler (outer epilogue).
    """
    try:
        items = tuple(old_handlers.items())
    except BaseException as exc:
        _record_internal(receipt, exc)
        return True
    fault = False
    for sig, handler in items:
        try:
            signal.signal(sig, handler if saved else signal.SIG_IGN)
        except BaseException as exc:
            _record_internal(receipt, exc)
            fault = True
    return fault


# Byte-contiguous spans of the pinned llama.cpp commit that ground the v3
# sourced predicates. Each binding is {check, row, commit, path, url,
# lines:[a,b], file_sha256, span_text, span_sha256}. `row` is the SOURCES
# registry id when a landed row already covers the proposition; null means
# this round still owes a row (the span is still cited and re-derivable).
# The span text is literal here so the gate can re-derive span_sha256
# without network access; file_sha256 is the raw digest of the whole file
# at the pinned commit (S036/S037 record the same digests).
def _binding(check, row, path, first, last, file_sha256, span_text):
    return {
        'check': check,
        'row': row,
        'commit': LLAMA_COMMIT,
        'path': 'tools/server/' + path,
        'url': _LLAMA_RAW + path,
        'lines': [first, last],
        'file_sha256': file_sha256,
        'span_text': span_text,
        'span_sha256': hashlib.sha256(
            span_text.encode('utf-8')).hexdigest(),
    }


SERVER_CONTEXT_SHA = (
    'dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329')
SERVER_HTTP_SHA = (
    '24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb')
SERVER_SHA_CPP = (
    '2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4')


def source_bindings():
    """Producer half of the source-binding contract (one entry per sourced
    predicate span). Plain data; never executed, never network-read."""
    return [
        _binding(
            'health_ready', None, 'server-context.cpp', 5288, 5299,
            SERVER_CONTEXT_SHA,
            '    this->get_health = [this](const server_http_req &) {\n'
            '        // error and loading states are handled by middleware\n'
            '        auto res = create_response(true);\n'
            '\n'
            '        // this endpoint can be accessed during sleeping\n'
            '        // the next LOC is to avoid someone accidentally use '
            'ctx_server\n'
            '        bool ctx_server; // do NOT delete this line\n'
            '        GGML_UNUSED(ctx_server);\n'
            '\n'
            '        res->ok({{"status", "ok"}});\n'
            '        return res;\n'
            '    };\n'),
        _binding(
            'loading_envelope_graded', 'S036', 'server-http.cpp',
            314, 325, SERVER_HTTP_SHA,
            '            res.status = 503;\n'
            '            res.set_content(\n'
            '                safe_json_to_str(json {\n'
            '                    {"error", {\n'
            '                        {"message", "Loading model"},\n'
            '                        {"type", "unavailable_error"},\n'
            '                        {"code", 503}\n'
            '                    }}\n'
            '                }),\n'
            '                "application/json; charset=utf-8"\n'
            '            );\n'
            '            return false;\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 529, 534,
            SERVER_SHA_CPP,
            '        struct sigaction sigint_action;\n'
            '        sigint_action.sa_handler = signal_handler;\n'
            '        sigemptyset (&sigint_action.sa_mask);\n'
            '        sigint_action.sa_flags = 0;\n'
            '        sigaction(SIGINT, &sigint_action, NULL);\n'
            '        sigaction(SIGTERM, &sigint_action, NULL);\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 519, 523,
            SERVER_SHA_CPP,
            '        shutdown_handler = [&](int) {\n'
            '            mcp_mgr.shutdown();\n'
            '            // this will unblock start_loop()\n'
            '            ctx_server.terminate();\n'
            '        };\n'),
        _binding(
            'teardown_graceful', None, 'server.cpp', 575, 590,
            SERVER_SHA_CPP,
            '        // this call blocks the main thread until '
            'queue_tasks.terminate() is called\n'
            '        ctx_server.start_loop();\n'
            '\n'
            '        clean_up();\n'
            '        ctx_http.join();\n'
            '        if (monitor_thread.joinable()) {\n'
            '            monitor_thread.join();\n'
            '        }\n'
            '\n'
            '        auto * ll_ctx = ctx_server.get_llama_context();\n'
            '        if (ll_ctx != nullptr) {\n'
            '            common_memory_breakdown_print(ll_ctx);\n'
            '        }\n'
            '    }\n'
            '\n'
            '    return 0;\n'),
    ]


def build_parser():
    p = argparse.ArgumentParser(
        prog='kama-llamacpp-live.py',
        description='Launch an ephemeral llama-server on a free unregistered '
                    'loopback port, capture its lifecycle, probe it with '
                    'kama-probe.sh, tear it down, and emit a '
                    'kama-llamacpp-live/v4 receipt (v5 with --server-archive).',
    )
    p.add_argument('--server', default=None,
                   help='llama-server binary (default: shutil.which'
                        '("llama-server")); realpath+sha256 recorded')
    p.add_argument('--model', default=None, help='GGUF path')
    p.add_argument('--model-sha256', default=None,
                   help='expected hex sha256 of --model; mismatch -> exit 2')
    p.add_argument('--alias', default='kama-live-probe',
                   help='--alias passed to llama-server')
    p.add_argument('--probe', default=str(DEFAULT_PROBE),
                   help='kama-probe.sh path')
    p.add_argument('--ctx', type=int, default=256, help='-c ctx size')
    p.add_argument('--threads', type=int, default=1, help='-t threads')
    p.add_argument('--ready-timeout', type=float, default=60.0,
                   help='seconds to wait for /health == 200')
    p.add_argument('--out', default=None,
                   help='receipt path (default: stdout)')
    p.add_argument('--port', type=int, default=None,
                   help='explicit port instead of bind(:0); still refused '
                        'when it is a registered consumer port (8080, 34113, '
                        'any port in registry/endpoint-consumers.tsv) or '
                        'already listening')
    p.add_argument('--server-asset-url', default=None,
                   help='provenance: https URL of the release archive the '
                        'server binary was extracted from')
    p.add_argument('--server-asset-sha256', default=None,
                   help='provenance: sha256 of that archive (64 hex)')
    p.add_argument('--server-member', default=None,
                   help='provenance: path of llama-server inside the archive')
    p.add_argument('--model-url', default=None,
                   help='provenance: https URL the --model file was fetched '
                        'from, pinned to a 40-hex /resolve/<commit>/ revision')
    p.add_argument('--server-archive', default=None,
                   help='provenance (v5): local copy of the release archive; '
                        'hashed against --server-asset-sha256 and its member '
                        'against --server before the server starts')
    p.add_argument('--witness-dir', default=None,
                   help='existing directory, one run at a time: an earlier run\'s '
                        'ready.json/release is removed before the server starts and '
                        'the handshake is removed when the hold ends; once the '
                        'server is ready and its checks ran, write ready.json '
                        '{port, pid} there and keep the server up until a file named '
                        'release appears (round 49)')
    p.add_argument('--witness-timeout', type=float, default=120.0,
                   help='seconds to wait for the release file (default 120)')
    p.add_argument('--server-fd', type=int, default=None,
                   help='round 52: an inherited descriptor of a sealed memfd '
                        '(memfd_create(2); F_SEAL_WRITE|SHRINK|GROW|SEAL) holding '
                        'the bytes of --server; the server is exec\'d from it '
                        '(/proc/<this pid>/fd/<n>), so its running image is that '
                        'anonymous file, and LD_LIBRARY_PATH names --server\'s '
                        'directory because $ORIGIN no longer does')
    p.add_argument('--selftest', action='store_true',
                   help='run parser and outcome self-tests without a server')
    return p


def _install_identity_selftest():
    """Stub install: regular server and libs plus a soname chain. The chain
    is recorded only by install_links(); a retarget moves only
    install_links_sha256; a subdirectory or unreadable member is a problem
    (fail closed), never a silently smaller identity."""
    members = {'llama-server': b'server-stub\n',
               'libllama.so.0.7.0': b'lib-0.7.0\n',
               'libllama.so.0.7.1': b'lib-0.7.1\n'}
    with tempfile.TemporaryDirectory(
            prefix='kama-install-selftest-') as directory:
        for name, body in members.items():
            with open(os.path.join(directory, name), 'wb') as fh:
                fh.write(body)
        server = os.path.join(directory, 'llama-server')
        soname = os.path.join(directory, 'libllama.so.0')
        os.symlink('libllama.so.0.7.0', soname)
        os.symlink('libllama.so.0', os.path.join(directory, 'libllama.so'))
        tree, tree_sha = install_tree(server)
        links, links_sha, problems, unpinned = install_links(server)
        if tree != {n: hashlib.sha256(b).hexdigest()
                    for n, b in members.items()}:
            raise AssertionError(f'install_tree members mismatch: {tree!r}')
        if links != {'libllama.so': 'libllama.so.0',
                     'libllama.so.0': 'libllama.so.0.7.0'} or problems \
                or unpinned:
            raise AssertionError(f'install_links mismatch: {links!r} '
                                 f'{problems!r}')
        if links_sha != hashlib.sha256(
                b'{"libllama.so":"libllama.so.0",'
                b'"libllama.so.0":"libllama.so.0.7.0"}').hexdigest():
            raise AssertionError('install_links_sha256 digest mismatch')
        if links_digest({'b': 'x', 'a': 'y'}) != hashlib.sha256(
                b'{"a":"y","b":"x"}').hexdigest():
            raise AssertionError('install_links digest is not key-sorted')
        if links_digest({'a': 'b\nc -> d'}) == links_digest(
                {'a': 'b', 'c': 'd'}):
            raise AssertionError('install_links digest is not injective')
        os.unlink(soname)
        os.symlink('libllama.so.0.7.1', soname)
        moved = install_tree(server), install_links(server)
        if moved[1][0].get('libllama.so.0') != 'libllama.so.0.7.1' \
                or moved[1][1] == links_sha:
            raise AssertionError('retarget not recorded by install_links')
        if moved[0] != (tree, tree_sha):
            raise AssertionError('retarget moved install_tree identity')
        with open(os.path.join(directory, 'lib\nx.so'), 'wb'):
            pass
        if install_links(server)[2] != ["'lib\\nx.so':control-character-in-name"]:
            raise AssertionError('newline member name not a problem')
        os.unlink(os.path.join(directory, 'lib\nx.so'))
        os.makedirs(os.path.join(directory, 'glibc-hwcaps', 'x86-64-v3'))
        if install_links(server)[2] != [
                'glibc-hwcaps:loader-searched-subdirectory']:
            raise AssertionError('glibc-hwcaps not reported as a problem')
        os.rmdir(os.path.join(directory, 'glibc-hwcaps', 'x86-64-v3'))
        os.rmdir(os.path.join(directory, 'glibc-hwcaps'))
        os.symlink(tempfile.gettempdir(), os.path.join(directory, 'glibc-hwcaps'))
        if install_links(server)[2] != [
                'glibc-hwcaps:loader-searched-subdirectory']:
            raise AssertionError('symlinked glibc-hwcaps not reported')
        os.unlink(os.path.join(directory, 'glibc-hwcaps'))
        os.symlink(tempfile.gettempdir(), os.path.join(directory, 'libx.so'))
        if install_links(server)[2] != ['libx.so:link-not-to-member']:
            raise AssertionError('link to a directory not reported')
        os.unlink(os.path.join(directory, 'libx.so'))
        os.mkdir(os.path.join(directory, 'openvino-licensing'))
        found = install_links(server)
        if found[2] or found[3] != ['openvino-licensing']:
            raise AssertionError('other subdirectory not recorded unpinned')
        os.rmdir(os.path.join(directory, 'openvino-licensing'))
        partial = {k: v for k, v in tree.items() if k != 'libllama.so.0.7.1'}
        if install_links(server, partial)[2] != ['libllama.so.0.7.1:not-hashed']:
            raise AssertionError('member missing from install_tree not reported')
        lib = os.path.join(directory, 'libllama.so.0.7.0')
        os.chmod(lib, 0)
        try:
            if not os.access(lib, os.R_OK) and install_links(server)[2] \
                    != ['libllama.so.0.7.0:unreadable']:
                raise AssertionError('unreadable member not a problem')
        finally:
            os.chmod(lib, 0o644)


def _provenance_selftest():
    """v5 record-time verification on a stub archive: the right archive and member
    pass; a wrong archive digest, an absent member, a directory member and a member
    whose bytes are not the server each raise their own SetupError token."""
    import tarfile
    with tempfile.TemporaryDirectory(prefix='kama-live-prov-') as d:
        rel = os.path.join(d, 'rel')
        os.makedirs(rel)
        srv = os.path.join(rel, 'llama-server')
        with open(srv, 'wb') as fh:
            fh.write(b'server-stub\n')
        arc = os.path.join(d, 'a.tar.gz')
        with tarfile.open(arc, 'w:gz') as tf:
            tf.add(rel, arcname='rel')
        asha, ssha = sha256_file(arc), sha256_file(srv)
        got = verify_archive_member(arc, asha, 'rel/llama-server', ssha, os.path.getsize(srv))
        # a PAX GNU-sparse member declaring 10**15 bytes in a ~200-byte archive (round-48
        # seat Sen2Live F1): refused before a byte of it is hashed
        sparse = os.path.join(d, 'sparse.tar.gz')
        with tarfile.open(sparse, 'w:gz', format=tarfile.PAX_FORMAT) as tf:
            ti = tarfile.TarInfo('rel/llama-server')
            ti.size = 1
            ti.pax_headers = {'GNU.sparse.map': '0,1', 'GNU.sparse.major': '1',
                              'GNU.sparse.minor': '0',
                              'GNU.sparse.realsize': str(10 ** 15)}
            tf.addfile(ti, io.BytesIO(b'A'))
        # round 49 (X1Selftest): the streaming index cap, one member past MEMBER_MAX_COUNT
        # (the only archive-level round-49 token no selftest or counter exercised)
        many = os.path.join(d, 'many.tar')
        with tarfile.open(many, 'w') as tf:
            for i in range(MEMBER_MAX_COUNT + 1):
                tf.addfile(tarfile.TarInfo(f'f{i}'))
        if got != (asha, ssha):
            raise AssertionError('right archive and member not verified')
        for args, token in (((arc, '0' * 64, 'rel/llama-server', ssha), 'provenance-archive-digest-mismatch'),
                            ((arc, asha, 'rel/nope', ssha), 'provenance-member-absent'),
                            ((arc, asha, 'rel', ssha), 'provenance-member-not-a-file'),
                            ((arc, asha, 'rel/llama-server', '1' * 64), 'provenance-member-digest-mismatch'),
                            ((arc, asha, 'rel/llama-server', ssha, 1), 'provenance-member-size-mismatch'),
                            ((sparse, sha256_file(sparse), 'rel/llama-server', ssha), 'provenance-member-sparse'),
                            ((many, sha256_file(many), 'rel/llama-server', ssha), 'provenance-archive-too-many-members'),
                            ((d, asha, 'rel/llama-server', ssha), 'provenance-archive-not-regular')):
            try:
                verify_archive_member(*args)
            except SetupError as exc:
                if exc.code != token:
                    raise AssertionError(f'{token}: got {exc.code}')
            else:
                raise AssertionError(f'{token}: not raised')
    for url, pinned in (('https://huggingface.co/o/r/resolve/' + 'a' * 40 + '/m.gguf', True),
                        ('https://huggingface.co/o/r/resolve/main/m.gguf', False),
                        ('https://huggingface.co/o/r/resolve/' + 'a' * 7 + '/m.gguf', False)):
        if bool(PINNED_MODEL_URL.match(url)) != pinned:
            raise AssertionError(f'pinned-url rule wrong for {url}')


F_ADD_SEALS = 1033          # F_LINUX_SPECIFIC_BASE + 9 (fcntl(2)); round 52


def _server_fd_selftest():
    """Round 52 (X5Selftest): sealed_fd() accepts exactly one shape - a sealed memfd whose
    bytes and length are the --server file's - and refuses an unsealed memfd, a file that
    cannot be sealed at all, a partly sealed memfd, a length mismatch and a digest
    mismatch. No case called sealed_fd before this one, so deleting the seal test or the
    digest comparison from it left the selftest green."""
    def a_memfd(payload, seals):
        fd = os.memfd_create('server-fd-selftest',
                             os.MFD_CLOEXEC | os.MFD_ALLOW_SEALING)
        if payload:
            os.write(fd, payload)
        if seals:
            fcntl.fcntl(fd, F_ADD_SEALS, seals)
        return fd

    def refused(fd, want_sha, want_size, token):
        try:
            sealed_fd(fd, want_sha, want_size)
        except SetupError as exc:
            if not str(exc).startswith(token):
                raise AssertionError(
                    f'server-fd refusal {exc} != {token}') from None
            return
        raise AssertionError(f'server-fd accepted, expected {token}')

    payload = b'\x7fELF server-fd selftest'
    want = hashlib.sha256(payload).hexdigest()
    fd = a_memfd(payload, SEALS_ALL)
    try:
        try:
            ident = sealed_fd(fd, want, len(payload))
        except SetupError as exc:
            raise AssertionError(
                f'server-fd refused a sealed memfd: {exc}') from None
    finally:
        os.close(fd)
    if (ident['sha256'] != want or ident['nlink'] != 0
            or ident['seals'] & SEALS_ALL != SEALS_ALL):
        raise AssertionError(f'server-fd identity not a sealed memfd: {ident}')
    fd = a_memfd(payload, 0)                  # memfd, never sealed
    try:
        refused(fd, want, len(payload), 'server-fd-not-sealed:0')
    finally:
        os.close(fd)
    with tempfile.TemporaryDirectory(prefix='kama-server-fd-selftest-') as directory:
        path = os.path.join(directory, 'server')
        with open(path, 'wb') as fh:         # a directory file cannot be sealed
            fh.write(payload)
        fd = os.open(path, os.O_RDONLY)
        try:
            refused(fd, want, len(payload), 'server-fd-not-sealed:None')
        finally:
            os.close(fd)
    fd = a_memfd(payload, 3)                  # F_SEAL_SEAL|F_SEAL_SHRINK only
    try:
        refused(fd, want, len(payload), 'server-fd-not-sealed:3')
    finally:
        os.close(fd)
    fd = a_memfd(payload, SEALS_ALL)
    try:
        refused(fd, want, len(payload) + 1, 'server-fd-size:')
    finally:
        os.close(fd)
    fd = a_memfd(payload, SEALS_ALL)
    try:
        refused(fd, '0' * 64, len(payload), 'server-fd-digest-differs-from-server')
    finally:
        os.close(fd)


def _code_mappings_selftest():
    """Round 53: code_mappings() records a user-owned executable mapping with the bytes of
    the file at its path only while that path is the mapped inode; after a rename-over the
    entry is `opened: False` (mapped-file-deleted), never the newcomer's digest."""
    src = shutil.which('sleep') or '/usr/bin/sleep'
    with tempfile.TemporaryDirectory(prefix='kama-code-map-selftest-') as directory:
        exe = os.path.join(directory, 'sleeper')
        shutil.copyfile(src, exe)
        os.chmod(exe, 0o700)
        want = sha256_file(exe)
        proc = subprocess.Popen([exe, '30'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 5
            ent = None
            while time.monotonic() < deadline and ent is None:
                got = code_mappings(proc.pid)
                ent = next((e for e in got.get('mappings') or [] if e.get('path') == exe), None)
                if ent is None:
                    time.sleep(0.05)
            if not (got.get('read') is True and ent and ent.get('opened') is True
                    and ent.get('sha256') == want and ent.get('uid') == os.getuid()):
                raise AssertionError(f'code_mappings missed the user-owned mapping: {ent}')
            decoy = os.path.join(directory, 'decoy')
            with open(decoy, 'wb') as fh:
                fh.write(b'not the mapped file')
            os.replace(decoy, exe)
            got = code_mappings(proc.pid)
            ent = next((e for e in got.get('mappings') or [] if e.get('path') == exe + ' (deleted)'), None)
            if not (ent and ent.get('opened') is False
                    and ent.get('reason') == 'mapped-file-deleted' and 'sha256' not in ent):
                raise AssertionError(f'code_mappings hashed a renamed-over path: {ent}')
        finally:
            proc.kill()
            proc.wait()
    if code_mappings(2 ** 22 + 7).get('read') is not False:
        raise AssertionError('code_mappings read maps of a pid that does not exist')


def _selftest():
    """Exercise procfs parsing, live tcp6 ownership rows, v3 verdicts, install
    identity and v5 record-time provenance."""
    _server_fd_selftest()
    _code_mappings_selftest()
    _install_identity_selftest()
    _provenance_selftest()
    port = 0x1234
    tcp6_rows = (
        ('00000000000000000000000001000000', True),
        ('0000000000000000FFFF00000100007F', True),
        ('00000000000000000000000002000000', False),
        ('00000000000000000000000000000000', False),
    )
    for addr_hex, expected in tcp6_rows:
        row = (f'0: {addr_hex}:{port:04X} '
               '00000000000000000000000000000000:0000 0A '
               '00000000:00000000 00:00000000 00000000 1000 0 43210')
        if _proc_listener_inode('/proc/net/tcp6', row, port) != (
                '43210' if expected else None):
            raise AssertionError(f'tcp6 proc-row parse failed: {addr_hex}')

    refused = refused_ports()
    tested_ports = []
    for address in ('::1', '::ffff:127.0.0.1'):
        listener_port = pick_port(refused)
        tested_ports.append(f'{address}:{listener_port}')
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as listener:
            listener.setsockopt(socket.IPPROTO_IPV6,
                                socket.IPV6_V6ONLY, 0)
            listener.bind((address, listener_port))
            listener.listen(1)
            inode_match = re.fullmatch(
                r'socket:\[(\d+)\]',
                os.readlink(f'/proc/self/fd/{listener.fileno()}'))
            if inode_match is None:
                raise AssertionError('listener fd has no procfs socket inode')
            inode = inode_match.group(1)
            if inode not in _listen_inodes(listener_port):
                raise AssertionError(
                    f'live tcp6 listener not recognized: {address}')
            with open('/proc/net/tcp6', encoding='ascii') as fh:
                rows = fh.readlines()[1:]
            live_row = next(
                (row for row in rows
                 if len(row.split()) >= 10
                 and row.split()[9] == inode),
                None)
            if live_row is None:
                raise AssertionError('live listener absent from /proc/net/tcp6')
            local_hex = live_row.split()[1].rsplit(':', 1)[0]
            if not _tcp6_is_loopback(local_hex):
                raise AssertionError(
                    f'live tcp6 loopback parser failed: {address}')

    good = [_check('health_ready', True, {})]
    bad = [_check('health_ready', False, {})]
    unknown = [_check(
        'loading_envelope_graded', None, {'loading_observed': False},
        'no-loading-503-observed')]
    if _outcome_exit(good, None) != ('pass', 0):
        raise AssertionError('pass outcome/exit mapping failed')
    if _outcome_exit(bad, None) != ('fail', 1):
        raise AssertionError('fail outcome/exit mapping failed')
    if _outcome_exit(unknown, None) != ('not-evaluated', 2):
        raise AssertionError('not-evaluated outcome/exit mapping failed')
    if _outcome_exit([], 'internal:KeyboardInterrupt') != (
            'setup-error', 2):
        raise AssertionError('setup-error outcome/exit mapping failed')

    if _outcome_exit(bad, 'internal:KeyboardInterrupt') != (
            'setup-error', 2):
        raise AssertionError('setup-error must take precedence over false')
    if good[0]['evaluated'] is not True or unknown[0]['evaluated'] is not False:
        raise AssertionError('tri-state evaluated field mapping failed')
    with tempfile.TemporaryDirectory(prefix='kama-emit-selftest-') as directory:
        original_replace = os.replace
        def interrupted_replace(_source, _destination):
            raise KeyboardInterrupt('atomic-publish-selftest')
        os.replace = interrupted_replace
        try:
            try:
                _emit({'schema': SCHEMA}, str(Path(directory) / 'receipt.json'))
            except KeyboardInterrupt:
                pass
            else:
                raise AssertionError('atomic publish interruption did not propagate')
        finally:
            os.replace = original_replace
        if list(Path(directory).iterdir()):
            raise AssertionError('atomic publish interruption leaked a sibling temp')

    class _HostileHandlers(dict):
        def items(self):
            raise RuntimeError('selftest-hostile-handlers')

    selftest_receipt = {'internal_fault': None, 'setup_error': None}
    if _restore_signal_handlers(
            _HostileHandlers({signal.SIGTERM: None}),
            selftest_receipt) is not True or selftest_receipt.get(
                'internal_fault') != 'internal:RuntimeError':
        raise AssertionError('finalizer handler restore fault escaped')
    print('selftest: ok; closed tcp6 listeners ' + ', '.join(tested_ports))
    return 0




def _emit(receipt, out_path):
    text = json.dumps(receipt, ensure_ascii=True, allow_nan=False,
                      indent=2, sort_keys=True) + '\n'
    if out_path:
        # atomic publish: sibling temp file + os.replace
        fd, tmp = tempfile.mkstemp(prefix='.kama-live-',
                                   dir=str(Path(out_path).parent))
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                fh.write(text)
            os.replace(tmp, out_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise
    else:
        sys.stdout.write(text)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        try:
            return _selftest()
        except BaseException as exc:
            try:
                print(f'kama-llamacpp-live selftest: {type(exc).__name__}',
                      file=sys.stderr)
            except BaseException:
                pass
            return 1
    if args.model is None or args.model_sha256 is None:
        parser.error('--model and --model-sha256 are required unless '
                     '--selftest is used')
    for name in ('model_sha256', 'server_asset_sha256'):
        value = getattr(args, name)
        if value is not None:
            if not re.fullmatch(r'[0-9a-fA-F]{64}', value):
                parser.error(f'--{name.replace("_", "-")} must be 64 hex digits')
            setattr(args, name, value.lower())
    # provenance shape (round 48, closure D3): the four v4 flags come together with
    # https URLs and a safe member; --server-archive selects v5, which also needs a
    # model URL pinned to a /resolve/<40-hex commit>/ revision (closure D6)
    v4_flags = (args.server_asset_url, args.server_asset_sha256,
                args.server_member, args.model_url)
    model_commit = None
    if args.server_archive is not None or any(v is not None for v in v4_flags):
        if any(v is None for v in v4_flags):
            parser.error('provenance flags --server-asset-url, '
                         '--server-asset-sha256, --server-member and '
                         '--model-url must be given together')
        for flag, url in (('--server-asset-url', args.server_asset_url),
                          ('--model-url', args.model_url)):
            if not url.startswith('https://'):
                parser.error(f'{flag} must be an https:// URL')
        member = args.server_member
        if not member or member.startswith('/') or '..' in member.split('/'):
            parser.error('--server-member must be a relative path without ..')
        if args.server_archive is not None:
            m = PINNED_MODEL_URL.match(args.model_url)
            if not m:
                parser.error('--model-url must be pinned to a 40-hex '
                             '/resolve/<commit>/ revision (v5)')
            model_commit = m.group(1)
    if args.witness_dir is not None:
        if not os.path.isdir(args.witness_dir):
            parser.error('--witness-dir must be an existing directory')
        try:
            prepare_witness_dir(args.witness_dir)
        except SetupError as exc:
            parser.error(f'--witness-dir unusable ({exc.code})')
    # finite and bounded (round-49 seat Sen1Witness F4: `inf` was accepted and the replay
    # then died with OverflowError after spawning this tool)
    if not 0 < args.witness_timeout <= 3600:
        parser.error('--witness-timeout must be > 0 and <= 3600 seconds')

    receipt = {
        'schema': SCHEMA,
        'started_utc': None,
        'ended_utc': None,
        'server': {
            'arg': args.server, 'realpath': None, 'sha256': None,
            'install_tree': {}, 'install_tree_sha256': None,
            'install_links': {}, 'install_links_sha256': None,
            'server_impl_sha256': None,
        },
        'model': {'arg': args.model, 'path': None, 'sha256': None},
        'model_sha256_post': None,
        'provenance': {
            'server': {'asset_url': args.server_asset_url,
                       'asset_sha256': args.server_asset_sha256,
                       'member': args.server_member},
            'model': {'url': args.model_url, 'sha256': args.model_sha256},
        },
        'probe': {'path': str(args.probe), 'sha256': None},
        'alias': args.alias,
        'ctx': args.ctx,
        'threads': args.threads,
        'port': None,
        'port_refusal_set': [],
        'child_env_keys': [],
        'argv': None,
        'transitions': [],
        'loading_503': None,
        'loading_503_bodies': [],
        'loading_bodies_dropped': 0,
        'loading_observed': False,
        'loading_envelope_exact': None,
        'captures': {},
        'probes': [],
        'teardown': None,
        'checks': [],
        'setup_error': None,
        'internal_fault': None,
        'child_pid': None,
        'model_mapping': None,
        'server_exe': None,
        'port_listener_ownership': 'unproven',
        'source_binding': [],
        'tool': {'path': str(SCRIPT), 'sha256': None},
        'outcome': 'setup-error',
    }
    proc = None
    log_path = None
    port = None
    model_sha = None
    child_env = {}
    old_handlers = {}
    emitted = False
    exit_code = 2

    try:
        receipt['started_utc'] = _utc_now()

        server_arg = args.server or shutil.which('llama-server')
        if not server_arg:
            raise SetupError('no-llama-server')
        server_real = os.path.realpath(server_arg)
        if not (os.path.isfile(server_real) and os.access(server_real, os.X_OK)):
            raise SetupError(f'server-not-executable:{server_real}')
        if not os.path.isfile(args.model):
            raise SetupError(f'model-not-found:{args.model}')
        if not os.path.isfile(args.probe):
            raise SetupError(f'probe-not-found:{args.probe}')

        model_sha = sha256_file(args.model)
        receipt['model'].update({
            'path': os.path.realpath(args.model),
            'sha256': model_sha,
        })
        if model_sha.lower() != args.model_sha256.lower():
            raise SetupError('model-digest-mismatch')

        server_sha = sha256_file(server_real)
        if args.server_archive is not None:
            # v5: verify provenance now, before anything is started
            archive_sha, member_sha = verify_archive_member(
                args.server_archive, args.server_asset_sha256,
                args.server_member, server_sha, os.path.getsize(server_real))
            receipt['schema'] = SCHEMA_V5
            receipt['provenance']['model']['commit'] = model_commit
            receipt['provenance']['verified'] = {
                'at': 'record', 'archive_sha256': archive_sha,
                'member_sha256': member_sha, 'model_sha256': model_sha}
        tree, tree_sha = install_tree(server_real)
        links, links_sha, link_problems, unpinned = install_links(
            server_real, tree)
        if link_problems:
            raise SetupError('install-tree-unpinnable:'
                             + ';'.join(link_problems[:8]))
        impl_path = os.path.join(os.path.dirname(server_real),
                                 'libllama-server-impl.so')
        impl_sha = (sha256_file(impl_path)
                    if os.path.isfile(impl_path) else None)
        probe_sha = sha256_file(args.probe)
        refused = refused_ports()
        port = pick_port(refused, args.port)
        receipt['server'].update({
            'arg': server_arg,
            'realpath': server_real,
            'sha256': server_sha,
            'install_tree': tree,
            'install_tree_sha256': tree_sha,
            'install_links': links,
            'install_links_sha256': links_sha,
            'install_unpinned': unpinned,
            'server_impl_sha256': impl_sha,
        })
        receipt['probe']['sha256'] = probe_sha
        receipt['port'] = port
        receipt['port_refusal_set'] = sorted(refused)
        receipt['source_binding'] = source_bindings()
        receipt['port_pick_note'] = (
            'port released after bind(:0) and re-bound by the server; '
            'a sub-second collision race is possible')

        server_argv = [
            server_real, '-m', args.model,
            '--alias', args.alias,
            '--host', '127.0.0.1',
            '--port', str(port),
            '-c', str(args.ctx),
            '-t', str(args.threads),
            '--no-webui',
            '--offline',
        ]
        receipt['argv'] = server_argv
        try:
            receipt['tool']['sha256'] = sha256_file(SCRIPT)
        except OSError:
            pass
        child_env = {key: os.environ[key] for key in CHILD_ENV_KEYS
                     if key in os.environ}
        if args.server_fd is not None:
            # round 52: the server runs from the sealed memfd, whose /proc link is
            # "/memfd:..." - $ORIGIN cannot find the install tree's libraries any more
            receipt['server']['fd'] = sealed_fd(
                args.server_fd, server_sha, os.path.getsize(server_real))
            child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)
            # ggml finds its CPU backend in the executable's directory or the current
            # one; the memfd has no directory, so the server starts in the install tree
            # and gets an absolute model path
            server_argv[2] = os.path.abspath(args.model)
        receipt['child_env_keys'] = sorted(child_env)

        def _term_handler(signum, _frame):
            raise Terminated(f'signal {signum}')

        for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGHUP):
            old_handlers[sig] = signal.signal(sig, _term_handler)

        try:
            log_fd, log_path = tempfile.mkstemp(
                prefix='kama-llamacpp-live-', suffix='.log')
        except OSError as exc:
            raise SetupError(f'log-mkstemp-failed:{exc}') from exc
        try:
            log_file = os.fdopen(log_fd, 'wb')
        except BaseException:
            try:
                os.close(log_fd)
            except OSError:
                pass
            raise
        try:
            _FORKED_PPID[0] = os.getpid()
            popen_kwargs = dict(
                stdin=subprocess.DEVNULL,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                preexec_fn=_preexec_pdeathsig,
                env=child_env,
            )
            if args.server_fd is not None:
                # argv[0] stays the --server path; the image is the memfd itself
                popen_kwargs['executable'] = (
                    f'/proc/{os.getpid()}/fd/{args.server_fd}')
                popen_kwargs['cwd'] = os.path.dirname(server_real)
            try:
                proc = subprocess.Popen(server_argv, **popen_kwargs)
            except OSError as exc:
                raise SetupError(
                    f'launch-failed:{type(exc).__name__}:{exc.errno}:'
                    f'{exc.strerror or exc}') from exc
            receipt['child_pid'] = proc.pid
        finally:
            log_file.close()
        receipt['pdeathsig'] = {'requested': True, 'prctl_ok': 'unknown'}

        (transitions, loading_503, loading_bodies, ready, fail,
         ownership) = readiness_loop(proc, port, args.ready_timeout)
        receipt['port_listener_ownership'] = {
            True: 'child', False: 'foreign', None: 'unproven',
        }[ownership]
        receipt['transitions'] = transitions
        receipt['loading_503'] = loading_503
        receipt['loading_503_bodies'] = loading_bodies
        receipt['loading_bodies_dropped'] = getattr(
            loading_bodies, 'dropped', 0)
        receipt['loading_observed'] = loading_503 is not None
        receipt['loading_envelope_exact'] = loading_envelope_exact(loading_503)
        if not ready:
            raise SetupError(fail)

        err, owned_state = verify_live(proc, port, 'pre-captures')
        receipt['port_listener_ownership'] = owned_state
        if err:
            raise SetupError(err)

        captures = ready_captures(port)
        models_doc = captures.pop('_models_doc')
        receipt['captures'] = captures
        checks = receipt['checks']

        health_status = captures['health']['status']
        health_body = None
        try:
            health_body = json.loads(captures['health'].get('body') or '')
        except (ValueError, TypeError):
            pass
        checks.append(_check(
            'health_ready',
            health_status == 200 and health_body == HEALTH_READY_BODY,
            {'status': health_status, 'body': health_body,
             'expected_body': HEALTH_READY_BODY}))

        data = models_doc.get('data') if isinstance(models_doc, dict) else None
        ids = [entry.get('id') for entry in data if isinstance(entry, dict)] \
            if isinstance(data, list) else []
        owners = [entry.get('owned_by') for entry in data
                  if isinstance(entry, dict)] \
            if isinstance(data, list) else []
        models_status = captures['models'].get('status')
        checks.append(_check(
            'models_alias_id',
            models_status == 200 and bool(ids)
            and all(value == args.alias for value in ids),
            {'data_ids': ids, 'expected_alias': args.alias,
             'status': models_status}))
        checks.append(_check(
            'models_owned_by_llamacpp',
            models_status == 200 and bool(owners)
            and all(value == 'llamacpp' for value in owners),
            {'owned_by': owners, 'status': models_status}))
        checks.append(_check(
            'metrics_not_enabled',
            captures['metrics']['status'] is not None
            and captures['metrics']['status'] == 501,
            {'status': captures['metrics']['status']}))

        props_fields = captures['props']['fields']
        checks.append(_check(
            'props_alias',
            isinstance(props_fields, dict)
            and props_fields.get('model_alias') == args.alias,
            {'fields': props_fields}))

        for index, expect in enumerate((args.alias, MISMATCH_EXPECT)):
            err, owned_state = verify_live(
                proc, port, f'pre-probe-{index + 1}')
            receipt['port_listener_ownership'] = owned_state
            if err:
                raise SetupError(err)
            receipt['probes'].append(
                run_probe(args.probe, port, expect, child_env))
        err, owned_state = verify_live(proc, port, 'post-probes')
        receipt['port_listener_ownership'] = owned_state
        if err:
            raise SetupError(err)

        ok_probe, bad_probe = receipt['probes']
        ok_row = probe_row(ok_probe) or {}
        bad_row = probe_row(bad_probe) or {}
        checks.append(_check(
            'probe_model_ok',
            ok_probe['exit'] == 0
            and ok_row.get('verdict') == 'MODEL_OK'
            and ok_row.get('reason') == 'matched',
            {'exit': ok_probe['exit'], 'verdict': ok_row.get('verdict'),
             'reason': ok_row.get('reason')}))
        checks.append(_check(
            'probe_mismatch',
            bad_probe['exit'] == 2
            and bad_row.get('verdict') == 'MODEL_MISMATCH'
            and bad_row.get('reason') == 'served-id-mismatch',
            {'exit': bad_probe['exit'], 'verdict': bad_row.get('verdict'),
             'reason': bad_row.get('reason')}))
        # round 50 (closure R1): the model file the running server maps, read from its
        # /proc/<pid>/maps and hashed through that same file (recorded, never a check id:
        # v1-v5 check lists stay as they were)
        # round 51 (round-50 closure R6): the executable the running server child is,
        # opened through /proc/<pid>/exe (recorded the same way, never a check id)
        if _child_running(proc):
            receipt['model_mapping'] = model_mapping(proc.pid, args.model)
            receipt['server_exe'] = server_exe(proc.pid)
            # round 53 (round-52 closure R2): every executable file mapping, by its bytes
            receipt['code_mappings'] = code_mappings(proc.pid)
        else:
            receipt['model_mapping'] = {'mapped': False, 'reason': 'server-not-running'}
            receipt['server_exe'] = {'opened': False, 'reason': 'server-not-running'}
            receipt['code_mappings'] = {'read': False, 'reason': 'server-not-running'}
        if args.witness_dir is not None:
            # round 49 (closure R5): hold the ready server up for an outside observer
            receipt['witness'] = hold_for_witness(
                args.witness_dir, proc, port, args.witness_timeout)
            err, owned_state = verify_live(proc, port, 'post-witness')
            receipt['port_listener_ownership'] = owned_state
            if err:
                raise SetupError(err)
    except SetupError as exc:
        receipt['setup_error'] = exc.code
    except Terminated as exc:
        receipt['setup_error'] = f'terminated:{exc}'
    except BaseException as exc:
        _record_internal(receipt, exc)
    finally:
        _restore_signal_handlers(old_handlers, receipt)

        td = None
        if proc is not None or log_path is not None:
            try:
                td = teardown(proc, port, log_path)
            except BaseException as exc:
                _record_internal(receipt, exc)
                returncode = None
                if proc is not None:
                    try:
                        returncode = proc.returncode
                    except BaseException as read_exc:
                        _record_internal(receipt, read_exc)
                td = {
                    'error': f'internal:{type(exc).__name__}',
                    'returncode': returncode,
                    'sigterm_sent': False,
                    'sigkill_sent': False,
                    'alive_at_teardown_start': None,
                    'port_refuses': None,
                    'term_wait_ms': None,
                    'log_lines': [],
                }

        try:
            if _child_running(proc):
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                    if isinstance(td, dict):
                        td['sigkill_sent'] = True
                except (ProcessLookupError, PermissionError, OSError):
                    pass
                except BaseException as exc:
                    _record_internal(receipt, exc)
                try:
                    proc.wait(timeout=5)
                    if isinstance(td, dict):
                        td['returncode'] = proc.returncode
                except subprocess.TimeoutExpired:
                    pass
                except BaseException as exc:
                    _record_internal(receipt, exc)
        except BaseException as exc:
            _record_internal(receipt, exc)

        if isinstance(td, dict) and td.get('port_refuses') is None \
                and port is not None:
            try:
                td['port_refuses'] = _port_refuses(port)
            except BaseException as exc:
                _record_internal(receipt, exc)
        receipt['teardown'] = td

        if port is not None:
            checks = receipt['checks']
            try:
                graceful = (
                    isinstance(td, dict)
                    and td.get('sigterm_sent') is True
                    and td.get('sigkill_sent') is False
                    and td.get('alive_at_teardown_start') is True
                    and td.get('returncode') == 0
                    and receipt.get('port_listener_ownership') == 'child')
                checks.append(_check(
                    'teardown_graceful', graceful,
                    {'sigterm_sent': td.get('sigterm_sent')
                     if isinstance(td, dict) else None,
                     'sigkill_sent': td.get('sigkill_sent')
                     if isinstance(td, dict) else None,
                     'alive_at_teardown_start':
                         td.get('alive_at_teardown_start')
                         if isinstance(td, dict) else None,
                     'returncode': td.get('returncode')
                     if isinstance(td, dict) else None,
                     'port_listener_ownership':
                         receipt.get('port_listener_ownership'),
                     'error': td.get('error')
                     if isinstance(td, dict) else None}))
                checks.append(_check(
                    'teardown_port_closed',
                    isinstance(td, dict)
                    and td.get('port_refuses') is True
                    and receipt.get('port_listener_ownership') == 'child',
                    {'port_refuses': td.get('port_refuses')
                     if isinstance(td, dict) else None,
                     'port_listener_ownership':
                         receipt.get('port_listener_ownership')}))
                bodies = receipt.get('loading_503_bodies') or []
                total_503 = sum(
                    1 + (body.get('repeats') or 0)
                    for body in bodies if isinstance(body, dict))
                all_exact = loading_envelopes_all(bodies)
                loading_observed = receipt.get('loading_observed') is True
                checks.append(_check(
                    'loading_envelope_graded',
                    (all_exact is True) if loading_observed else None,
                    {'loading_observed': receipt.get('loading_observed'),
                     'distinct_bodies': len(bodies),
                     'bodies_dropped':
                         receipt.get('loading_bodies_dropped', 0),
                     'total_503_responses': total_503,
                     'all_exact': all_exact,
                     'exact': all_exact},
                    None if loading_observed
                    else 'no-loading-503-observed'))
                if model_sha is not None:
                    try:
                        receipt['model_sha256_post'] = sha256_file(args.model)
                    except OSError as exc:
                        receipt['model_sha256_post'] = f'rehash-error:{exc}'
                    checks.append(_check(
                        'model_unchanged',
                        receipt['model_sha256_post'] == model_sha,
                        {'pre': model_sha,
                         'post': receipt['model_sha256_post']}))
            except BaseException as exc:
                _record_internal(receipt, exc)

        if log_path is not None:
            for attempt in range(2):
                try:
                    os.unlink(log_path)
                    break
                except FileNotFoundError:
                    break
                except BaseException as exc:
                    _record_internal(receipt, exc)
                    if attempt == 1:
                        break

        try:
            receipt['ended_utc'] = _utc_now()
        except BaseException as exc:
            _record_internal(receipt, exc)
        try:
            receipt['outcome'], exit_code = _outcome_exit(
                receipt['checks'], receipt['setup_error'])
        except BaseException as exc:
            _record_internal(receipt, exc)
            receipt['outcome'], exit_code = 'setup-error', 2

        needs_reemit = False
        try:
            _emit(receipt, args.out)
            emitted = True
        except Terminated as exc:
            receipt['setup_error'] = (
                receipt.get('internal_fault') or f'terminated:{exc}')
            receipt['outcome'], exit_code = 'setup-error', 2
            needs_reemit = True
        except BaseException as exc:
            _record_internal(receipt, exc)
            receipt['outcome'], exit_code = 'setup-error', 2
            needs_reemit = True

        restore_fault = _restore_signal_handlers(
            old_handlers, receipt, saved=True)

        if needs_reemit or restore_fault:
            try:
                receipt['outcome'], exit_code = _outcome_exit(
                    receipt['checks'], receipt['setup_error'])
            except BaseException as exc:
                _record_internal(receipt, exc)
                receipt['outcome'], exit_code = 'setup-error', 2
            try:
                _emit(receipt, args.out)
                emitted = True
            except Terminated as exc:
                receipt['setup_error'] = (
                    receipt.get('internal_fault') or f'terminated:{exc}')
                receipt['outcome'], exit_code = 'setup-error', 2
            except BaseException as exc:
                _record_internal(receipt, exc)
                receipt['outcome'], exit_code = 'setup-error', 2

    return exit_code if emitted else 2


if __name__ == '__main__':
    sys.exit(main())
