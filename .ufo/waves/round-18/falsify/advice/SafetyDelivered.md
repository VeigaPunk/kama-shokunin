VERDICT: partial — the intended controls work, but registry exclusion and fallback cleanup identity have bounded safety gaps.

# SafetyDelivered — scoped delivered-safety review

Advisory only; L1 owns admission. Reviewed pushed revision `1c325b2e58fcfdc6761f645b44cedfb1d65243e6` in the required separate clone. No production remediation, integration, ship judgment, other-runtime invocation, or source-mutant counting was performed.

## Axes and boundary

Axes: **loopback/port isolation; signal-target identity; descendant cleanup; registry fail-closed behavior; environment and argv data/control separation; receipt/evidence fidelity**. C1 operability is the principal affected claim; this is not a new C2 calibration denominator or an outside non-author judgment.

Read the assignment lesson, SCORECARD Round 18, QUALITY KQ23/KQ24 and relevant official raw runs. The official `runs/commands.json` records measured commit `c6dc46fabc51eb1dd0e91647f2e5e6b2b8ae4d6d`; the delivered tool/control/gate hashes below match its input pins. I did not rerun official counting commands. The original c1 counting result remains **exit 2 / could-not-evaluate**, with stderr `c1-measure: fault: before: misclassified=1 but 0 row(s) classified misclassified`; the fresh selected controls below do not turn that official fault into a successful full count.

## Findings

### SD1 — MEDIUM: the tool detects a surviving listener but leaves its helper for the controls runner to kill

- **Path/evidence:** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:798-831` sends SIGTERM to the child group and waits/reaps the leader; escalation occurs only on a leader wait timeout. Its final fallback at `:1433-1450` likewise runs only while `_child_running(proc)` is true. The retained counterexample is `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:408-420,623-628`: a same-group helper inherits the listening socket and ignores SIGTERM while the leader exits 0.
- **Executed observation:** k0 was green (tool/gate `0/0`). Selected k15 then produced tool/gate `1/1`, `outcome=fail`, `teardown_graceful=true`, `teardown_port_closed=false`, `sigterm_sent=true`, `sigkill_sent=false`, leader returncode 0. The listener at **127.0.0.1:33735** still accepted connections **after the tool exited and before controls cleanup**. The existing controls cleanup subsequently closed it. Receipt SHA-256: `91c5b4328b3816f092f7d39589b63bc71232a2e50af2a0336573d061c9f47668`.
- **Failure path / impact:** a caller-selected server that leaves a same-group listener descendant is correctly rejected, but a direct invocation of the production tool lacks the control runner's extra cleanup. [INFERENCE] Repeated failed invocations of that shape can retain local listeners/processes; this is a cleanup limitation, not a false-pass or remote-exposure result. The test helper was loopback-only and was killed immediately by the trusted retained cleanup.
- **Smallest remediation:** finish owned same-group cleanup even when the leader exits first, while maintaining a verifiable identity for that group. Do **not** merely add an unconditional `killpg` after reaping the leader. Preserve the existing failed teardown grade; the detector itself worked.

### SD2 — LOW: fallback cleanup's “exact fake” identity check is a substring check over an untrusted PID record

- **Path/evidence:** `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:777-813` reads the PID list, takes its first entry as the group leader, decodes the entire NUL-delimited cmdline, and accepts `if fake not in cmdline` as the identity guard (`:801`). Its docstring promises an exact fake-script identity, but `.unrelated` suffixes satisfy the same check.
- **Executed observation (all OS signals mocked):** synthetic PID 424242 with an exact fake-script argument caused a recorded SIGKILL group call, as expected. The same cmdline with **only `<fake_server.py>.unrelated`** also caused the identical recorded group call `[424242,9]`; a wholly unrelated cmdline caused no signal. No real process was named or signalled in this identity probe. The exact experiment source and stdout are embedded below.
- **Failure path / impact:** a stale/corrupted PID file plus a same-UID process whose command merely contains that path substring can pass the fallback guard. [INFERENCE] Cleanup could kill an unrelated process/group in that situation. This is local accidental/destructive-target risk, **not** a privilege escalation or a sandbox boundary against arbitrary caller-selected tool code.
- **Smallest remediation:** split `/proc/<pid>/cmdline` on NUL and require the exact script in the expected interpreter/script slot, not substring membership. Bind group signalling to captured process start/session identity rather than treating the PID file alone as ownership. Retain the current checks against signalling this runner's own process group.

### SD3 — MEDIUM, latent with current registry: readable registry bytes are not sufficient to preserve all exclusions

- **Path/evidence:** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:246-271` fails on read errors but extracts ports by regex over arbitrary text. The IPv4 regex does not match an address followed by `]`, and the IPv6 regex handles `::1` but not IPv4-mapped loopback. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:828-835` correctly refuses a missing/unreadable registry, but copies a readable malformed/empty one. The declared registry format is six TSV columns at `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:3-8,27-29`.
- **Executed observation (data only, no binds):** a complete six-column row declaring `http://127.0.0.1:45677/v1` added 45677; a row declaring `http://[::1]:45679/v1` added 45679. An otherwise identical row declaring **`http://[::ffff:127.0.0.1]:45678/v1` did not add 45678**, returning only `[8080,34113]`. Empty and malformed readable files also returned only the hard pins instead of rejecting. Missing files correctly raised `registry-unreadable` in the tool and `registry unavailable` in controls.
- **Failure path / impact:** [INFERENCE] adding a loadable mapped-loopback consumer on a non-hard-pinned port would not reserve that port against this tool; a free explicit request or default allocation could use it. A corrupt readable registry can similarly erase extra exclusions. An already-active service may still be stopped by the separate port-in-use check. **The committed registry currently names only the two hard-pinned ports, both remain protected, and this experiment did not bind 45677/45678/45679 or any consumer port.**
- **Smallest remediation:** validate the TSV envelope and parse the declared URL's numeric port with a URL parser (including bracketed IPv6), while retaining the documented explicit port-token forms needed elsewhere in the registry. Reject malformed/corrupt registry data rather than treating it as an empty dynamic exclusion set. Add retained readable-malformed and mapped-loopback registry controls.

## Confirmed invariants and limits

| Surface | Observed evidence | Scope / limit |
|---|---|---|
| Hard refused ports | Explicit 8080 and 34113 both raised `port-refused-registered` before **zero connection attempts**; 0 and 65536 raised range errors | No refused port was bound or contacted |
| Child environment | Launch interception received exactly `HOME,LANG,LC_ALL,PATH,TMPDIR`, `start_new_session=true`, one `--host 127.0.0.1`; nonallowlisted synthetic canary/proxy/loader/host keys did not survive, and canary absent from receipt | Interception deliberately raised OSError before execution, yielding setup exit 2. This is kwargs evidence, not a successful live environment run; no real environment values were printed |
| Producer kill identity | Mock dead leader produced no killpg; mock live leader produced only `[424242,15]` | Confirms the existing dead-leader guard, not atomic identity guarantees for all descendants |
| IPv6 ownership | Real retained k17 mapped-loopback control accepted, tool/gate 0/0; parser accepted `::1` and mapped 127/8, rejected `::`, `::2`, mapped 128/8 and `fe80::1` | Native `::1` here was data-only; official raw tool selftest separately records real closed `::1:39071` and mapped `:41601` listeners. No wildcard/nonloopback socket was opened |
| Forged argv remains data | k22 duplicate wildcard-host **receipt data** rejected on exact argv, gate exit 1, targeted=true | Only executed command for this forgery was `/usr/bin/python3 /tmp/kama-r18-falsify-SafetyDelivered/tests/llamacpp-live/check-receipt.py /tmp/kama-r18-falsify-SafetyDelivered/safety-work/k22/gate-input.json`. No forged argv was launched |
| BaseException receipt | Selected k18 had fired injection, `internal:KeyboardInterrupt`, tool/gate 2/1, returncode -9, closed port | Correct controlled failure, not a passing subject |
| Receipt publication / permissions | Producer uses `mkstemp` then `os.replace` at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1110-1126`; controls use a private temporary workspace and explicit argv, not a shell command built from receipt content | Static inspection; no output-path race or file-permission attack was performed |

The tool/probe/server are caller-selected execution authorities; this is not a sandbox for hostile executables or a claim that a self-consistent receipt authenticates a live run. Exact launch argv and procfs loopback eligibility do not prove that an arbitrary child opened no additional sockets. `run_probe` at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:737-753` uses a subprocess timeout without separate probe-group ownership; descendant behavior on that timeout was **not exercised** here and is not credited as a reproduced failure. No registered-consumer health, real model-serving quality, all-host portability, or general mutant immunity follows.

No `resume_continuity_v1` occurrence exists in the three assigned tool/control/gate files (exact targeted search: no matches). Therefore that rejection/mutation surface is **not applicable to this assignment**, and no zero-mutation certification of a different runtime is made.

## Experiment commands, outcomes, cleanup and counting

Clone commands, both exit 0 (no stdout/stderr):

```text
/usr/bin/git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-SafetyDelivered
/usr/bin/git -C /tmp/kama-r18-falsify-SafetyDelivered switch -q -c seat/SafetyDelivered 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

Exact bounded experiment command, exit **0**, stderr **empty**, stdout reproduced verbatim in Appendix B:

```text
/usr/bin/env TMPDIR=/tmp/kama-r18-falsify-SafetyDelivered /usr/bin/python3 -B /tmp/kama-r18-falsify-SafetyDelivered/safety_experiment.py
```

Four selected fake runs executed **sequentially**, never more than one server at a time:

| Selected control | Tool / gate exits | Classification | Cleanup |
|---|---|---|---|
| k0 pristine good | 0 / 0 | accepted | 45369 closed before extra cleanup |
| k17 mapped loopback good | 0 / 0 | accepted | 40843 closed before extra cleanup |
| k15 inherited listener | 1 / 1 | rejected-targeted (`teardown_port_closed`) | 33735 open before, closed after controls cleanup |
| k18 injected KeyboardInterrupt | 2 / 1 | rejected-targeted | 34467 closed before extra cleanup |
| k22 receipt-only forgery | no tool / 1 | rejected-targeted (`argv`) | no server for this arm |

All four final port-refusal checks were true. Final procfs listener-inode scan over tracked fake PIDs `1913886,1913996,1914197,1914198,1914516` reported **`remaining_seat_listener_fds: []`**. This scan included k15's helper and all listener address families. The clone and all seat scratch were removed after copying this report's attachments; no seat-owned listener remained before removal.

Fresh source mutants: **0**; killed 0, survived 0, equivalent 0, site_missing 0; mutation-denominator assessment **not performed**. The weak-identity and registry witnesses are safety counterexamples, not claimed source-mutant kills. The official invalid counter baseline remains could-not-evaluate. No production bytes were edited; before/after byte hashes were identical, so no restoration was needed. Only this report is copied into the lane.

**Installs / upgrades:** none. Used existing `/usr/bin/python3` **3.14.8**, stdlib, git and the delivered fake-control/probe dependencies. No pacman transaction, host-service/configuration change, installed binary/model write, sibling state change, forbidden store read, or environment-value dump.

## Hash manifest

SHA-256 (all paths under the lane below are read-only evidence):

| File | SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py` (clone bytes) | `dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py` (clone bytes) | `106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py` (clone bytes) | `c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh` (clone bytes) | `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv` (clone bytes) | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/run.py` | `e3c957ca01caf891815ecd8ed9fdcd15fd66c640fc3a10d133023e058ee55be4` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/commands.json` | `ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/c1-measure.json` | `3ad738fc1a5035fd678dd4207b381f7491fb74887a894234a4d60274dfc098a4` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/tool-selftest.stdout` | `4ec682e1b6a7790e59da608a15527640c018dd70b2a08cf634e0986a00d3d9d6` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-18/runs/controls-selftest.stdout` | `a0e4ab83ba65a834de99f0145f343fac4829c06bc58d7acd58c939cb3c0809e6` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety_experiment.py` (Appendix A) | `0a12ed7a5030e3b0d0a0611a5c783f4dc57f64ca94da60e097da6098be103e4b` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/result.json` (Appendix B; exact stdout bytes) | `d6731de610fa328b4329e672ccb02dfdd809df78bda3d350d08534ab18058974` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k0/receipt.json` | `967e0fd86e7a106ef31c59452229506f98cb09efbf5251a1f4a95a110b301d09` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k17/receipt.json` | `a18400304cf699793cd112dedae69f3ba9b0f46b5b4d8e021807883937388f3a` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k15/receipt.json` | `91c5b4328b3816f092f7d39589b63bc71232a2e50af2a0336573d061c9f47668` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k18/receipt.json` | `b55cd90f30c0bd75217d259267fe9e8a11ef6fba33e7883dea669c3f9cdcc711` |
| `/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k22/gate-input.json` | `87a03818512bb617330801b01811d7ba0dd93742998b4da1cdb7f415ebe57e72` |

The forgery's canonical-content digest printed by controls (`74e55336e435457c115ebf2e18d034297af0ddec528bdbf96830ed6780c93c5e`) is intentionally distinct from its indented file-byte digest above. The scratch receipt files are not retained separately; their digests and bounded observations are retained here. Exact experiment source follows, so the experiment can be repeated only in a newly isolated clone under the assignment's same loopback/port bounds.

## Appendix A — exact experiment source

```python
#!/usr/bin/python3
"""Seat-owned safety observations; destructive identity probes use mocks only."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time
from unittest.mock import Mock, mock_open, patch

ROOT = Path('/tmp/kama-r18-falsify-SafetyDelivered')
WORK = ROOT / 'safety-work'
WORK.mkdir(mode=0o700, exist_ok=True)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

live = load('seat_live', ROOT / 'tools/kama-llamacpp-live.py')
c = load('seat_controls', ROOT / 'tests/llamacpp-live/controls.py')
TOOL = ROOT / 'tools/kama-llamacpp-live.py'
GATE = ROOT / 'tests/llamacpp-live/check-receipt.py'
PROBE = ROOT / 'tools/kama-probe.sh'
SURFACES = (TOOL, GATE, ROOT / 'tests/llamacpp-live/controls.py', PROBE,
            ROOT / 'registry/endpoint-consumers.tsv')
def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in SURFACES}

result = {'python': sys.version.split()[0], 'before_sha256': hashes()}
actual_refused = live.refused_ports()
result['actual_refused'] = sorted(actual_refused)
refusals = {}
for port in (0, 8080, 34113, 65536):
    with patch.object(live.socket, 'create_connection') as connect:
        try:
            live.pick_port(actual_refused, port)
            refusals[str(port)] = {'accepted': True}
        except live.SetupError as exc:
            refusals[str(port)] = {'error': exc.code,
                                   'connection_calls': connect.call_count}
result['explicit_refusals'] = refusals

registry_cases = {
    'ipv4': 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\nx\t/local/data\tgrep:x\thttp://127.0.0.1:45677/v1\tmodel\tnote\n',
    'mapped_loopback': 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\nx\t/local/data\tgrep:x\thttp://[::ffff:127.0.0.1]:45678/v1\tmodel\tnote\n',
    'native_loopback': 'id\tconsumer_path\tjson_pointer_or_grep\tdeclared_baseurl\texpected_model_id\tnotes\nx\t/local/data\tgrep:x\thttp://[::1]:45679/v1\tmodel\tnote\n',
    'empty': '',
    'malformed': 'not a six-column registry\n',
}
registry_results = {}
for name, text in registry_cases.items():
    path = WORK / (name + '.tsv')
    path.write_text(text)
    with patch.object(live, 'REGISTRY', path):
        try:
            registry_results[name] = {'refused': sorted(live.refused_ports())}
        except live.SetupError as exc:
            registry_results[name] = {'error': exc.code}
with patch.object(live, 'REGISTRY', WORK / 'missing.tsv'):
    try:
        live.refused_ports()
        registry_results['missing'] = {'accepted': True}
    except live.SetupError as exc:
        registry_results['missing'] = {'error_prefix': exc.code.split(':', 1)[0]}
with patch.object(c, 'REGISTRY_SRC', WORK / 'missing.tsv'):
    try:
        c._stage_control(WORK, 'registry-missing-control', 'k0', TOOL)
        registry_results['controls_missing'] = {'accepted': True}
    except c.ControlsFault as exc:
        registry_results['controls_missing'] = {'error_prefix': str(exc).split(':', 1)[0]}
result['registry_cases_no_bind'] = registry_results

v6 = {}
for address in ('::1', '::2', '::', '::ffff:127.0.0.1',
                '::ffff:127.7.8.9', '::ffff:128.0.0.1', 'fe80::1'):
    raw = socket.inet_pton(socket.AF_INET6, address)
    proc_hex = b''.join(raw[i:i+4][::-1] for i in range(0, 16, 4)).hex()
    v6[address] = live._tcp6_is_loopback(proc_hex)
result['tcp6_data_only'] = v6

# Signal-delivery identity probes never name or signal a real process.
signal_cases = {}
for name, running in (('dead_leader', False), ('live_leader', True)):
    proc = Mock(pid=424242, returncode=0)
    proc.poll.return_value = None if running else 0
    proc.wait.return_value = 0
    log = WORK / (name + '.log')
    log.write_bytes(b'')
    with patch.object(live.os, 'killpg') as killpg, \
         patch.object(live, '_port_refuses', return_value=True):
        td = live.teardown(proc, 45670, log)
        signal_cases[name] = {'calls': [[a.args[0], int(a.args[1])]
                                       for a in killpg.call_args_list],
                              'alive': td['alive_at_teardown_start']}

srv = WORK / 'mock-cleanup'
srv.mkdir()
(srv / 'fake.pid').write_text('424242\n')
fake = str(srv / 'fake_server.py')
identity = {}
for name, cmdline in (
        ('exact_token', b'/usr/bin/python3\0' + os.fsencode(fake) + b'\0'),
        ('substring_only', b'/usr/bin/python3\0' + os.fsencode(fake) + b'.unrelated\0'),
        ('unrelated', b'/usr/bin/python3\0/unrelated/script.py\0')):
    with patch('builtins.open', mock_open(read_data=cmdline)), \
         patch.object(c.os, 'getpgid', return_value=424242), \
         patch.object(c.os, 'getpgrp', return_value=777777), \
         patch.object(c.os, 'killpg') as killpg, \
         patch.object(c.os, 'kill') as kill:
        c._kill_fake(srv)
        identity[name] = {'group_calls': [[a.args[0], int(a.args[1])]
                                          for a in killpg.call_args_list],
                          'pid_calls': [[a.args[0], int(a.args[1])]
                                        for a in kill.call_args_list]}
result['signal_delivery_mock_only'] = signal_cases
result['cleanup_identity_mock_only'] = identity

# Intercept launch before execution; all environment values are synthetic and
# only key names / booleans are emitted.
st = c._stage_control(WORK, 'env-only', 'k0', TOOL)
launch = {}
emitted = []
def intercept(argv, **kwargs):
    launch['keys'] = sorted(kwargs['env'])
    launch['new_session'] = kwargs['start_new_session']
    launch['argv_has_one_loopback_host'] = (
        argv.count('--host') == 1 and argv[argv.index('--host') + 1] == '127.0.0.1')
    raise OSError('seat-intercept-before-exec')
synthetic_env = {k: 'synthetic-not-a-secret' for k in live.CHILD_ENV_KEYS}
synthetic_env['TMPDIR'] = str(st['wd'])
synthetic_env.update(KAMA_SAFETY_CANARY='synthetic-canary-no-record',
                     HTTP_PROXY='synthetic-proxy', LLAMA_ARG_HOST='synthetic-host',
                     LD_PRELOAD='synthetic-loader')
with patch.dict(os.environ, synthetic_env, clear=True), \
     patch.object(live, 'REGISTRY', st['wd'] / 'lane/registry/endpoint-consumers.tsv'), \
     patch.object(live, 'pick_port', return_value=45670), \
     patch.object(live.subprocess, 'Popen', side_effect=intercept), \
     patch.object(live, '_port_refuses', return_value=True), \
     patch.object(live, '_emit', side_effect=lambda doc, out: emitted.append(copy.deepcopy(doc))):
    rc = live.main(['--server', str(st['fake']), '--model', str(st['model']),
                    '--model-sha256', st['model_sha'], '--probe', str(PROBE),
                    '--out', str(st['receipt'])])
launch['exit'] = rc
launch['canary_absent_from_receipt'] = 'synthetic-canary-no-record' not in json.dumps(emitted)
result['environment_intercept_no_exec'] = launch

# Four selected real controls, strictly sequential; all bind only loopback.
# Observe k15's residual listener before the existing trusted cleanup runs.
cleanup = []
tracked = set()
used_ports = []
original_cleanup = c._kill_fake

def audited_cleanup(srvdir):
    srvdir = Path(srvdir)
    pidfile = srvdir / 'fake.pid'
    if pidfile.is_file():
        tracked.update(int(x) for x in pidfile.read_text().split())
    receipt_path = srvdir.parent / 'receipt.json'
    doc = json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
    port = doc.get('port')
    row = {'control': srvdir.parent.name, 'port': port}
    if isinstance(port, int):
        assert port not in actual_refused
        used_ports.append(port)
        row['closed_before_controls_cleanup'] = live._port_refuses(port)
    original_cleanup(srvdir)
    if isinstance(port, int):
        deadline = time.monotonic() + 3
        while not live._port_refuses(port) and time.monotonic() < deadline:
            time.sleep(0.02)
        row['closed_after_controls_cleanup'] = live._port_refuses(port)
        assert row['closed_after_controls_cleanup']
    cleanup.append(row)

rows = []
base = None
gate = c.SubprocessGate(GATE)
with patch.object(c, '_kill_fake', side_effect=audited_cleanup):
    for cid in ('k0', 'k17', 'k15', 'k18'):
        try:
            row, doc = c.run_tool_control(WORK, c.CONTROLS[cid], TOOL, PROBE, gate)
        except BaseException:
            audited_cleanup(WORK / cid / 'srv')
            raise
        rows.append({k: row.get(k) for k in (
            'id', 'classification', 'bucket', 'tool_exit', 'gate_exit',
            'failed_checks', 'targeted_hit', 'inject_fired', 'receipt_sha256',
            'tool_stderr_tail')})
        rows[-1]['outcome'] = doc.get('outcome') if doc else None
        rows[-1]['internal_fault'] = doc.get('internal_fault') if doc else None
        rows[-1]['teardown'] = {k: (doc.get('teardown') or {}).get(k) for k in (
            'sigterm_sent', 'sigkill_sent', 'alive_at_teardown_start',
            'returncode', 'port_refuses')}
        if cid == 'k0':
            base = {'doc': doc, 'gate_exit': row['gate_exit'], 'source': 'seat-k0'}

forgery_commands = []
original_popen = subprocess.Popen

def record_gate_command(argv, *args, **kwargs):
    forgery_commands.append(list(argv))
    return original_popen(argv, *args, **kwargs)

with patch.object(c.subprocess, 'Popen', side_effect=record_gate_command):
    forged = c.grade_forgery_row(c.CONTROLS['k22'], c._forgery_stage(WORK, 'k22'), gate, base)
result['selected_controls'] = rows
result['forged_argv_data_only'] = {k: forged.get(k) for k in (
    'id', 'classification', 'bucket', 'gate_exit', 'targeted_hit',
    'gate_problems', 'forged_sha256')}
result['forged_argv_data_only']['executed_commands'] = forgery_commands
result['cleanup_observations'] = cleanup
result['final_ports_closed'] = {str(p): live._port_refuses(p) for p in used_ports}

# Prove no tracked fake owns any LISTEN socket; zombies have no open fds.
listen_inodes = set()
for net in ('/proc/net/tcp', '/proc/net/tcp6'):
    for line in Path(net).read_text().splitlines()[1:]:
        fields = line.split()
        if len(fields) >= 10 and fields[3] == '0A':
            listen_inodes.add('socket:[' + fields[9] + ']')
remaining = []
for pid in sorted(tracked):
    fd_dir = Path('/proc') / str(pid) / 'fd'
    if not fd_dir.exists():
        continue
    for fd in fd_dir.iterdir():
        try:
            target = os.readlink(fd)
        except OSError:
            continue
        if target in listen_inodes:
            remaining.append({'pid': pid, 'fd': fd.name})
result['tracked_fake_pids'] = sorted(tracked)
result['remaining_seat_listener_fds'] = remaining
result['after_sha256'] = hashes()
result['production_bytes_unchanged'] = result['before_sha256'] == result['after_sha256']
result['selected_controls_conform'] = all(r['bucket'] == 'ok' for r in rows) and forged['bucket'] == 'ok'
assert not remaining
assert all(result['final_ports_closed'].values())
assert result['production_bytes_unchanged']
output = json.dumps(result, indent=2, sort_keys=True) + '\n'
(WORK / 'result.json').write_text(output)
print(output, end='')
```

## Appendix B — exact experiment stdout

```json
{
  "actual_refused": [
    8080,
    34113
  ],
  "after_sha256": {
    "registry/endpoint-consumers.tsv": "bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c",
    "tests/llamacpp-live/check-receipt.py": "c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335",
    "tests/llamacpp-live/controls.py": "106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8",
    "tools/kama-llamacpp-live.py": "dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b",
    "tools/kama-probe.sh": "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3"
  },
  "before_sha256": {
    "registry/endpoint-consumers.tsv": "bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c",
    "tests/llamacpp-live/check-receipt.py": "c5715641f34fb9bffaf33ca3e0391dd5485a0a914462bf6540e519b566c78335",
    "tests/llamacpp-live/controls.py": "106dd98b60e066a190ee8fea609e5be99c6b2065b9c5a404e14394ce59b6ffc8",
    "tools/kama-llamacpp-live.py": "dc036d7dcfe2933827c07f8bc0dedba68a24f7b099309871f6cb25ccb811a04b",
    "tools/kama-probe.sh": "36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3"
  },
  "cleanup_identity_mock_only": {
    "exact_token": {
      "group_calls": [
        [
          424242,
          9
        ]
      ],
      "pid_calls": []
    },
    "substring_only": {
      "group_calls": [
        [
          424242,
          9
        ]
      ],
      "pid_calls": []
    },
    "unrelated": {
      "group_calls": [],
      "pid_calls": []
    }
  },
  "cleanup_observations": [
    {
      "closed_after_controls_cleanup": true,
      "closed_before_controls_cleanup": true,
      "control": "k0",
      "port": 45369
    },
    {
      "closed_after_controls_cleanup": true,
      "closed_before_controls_cleanup": true,
      "control": "k17",
      "port": 40843
    },
    {
      "closed_after_controls_cleanup": true,
      "closed_before_controls_cleanup": false,
      "control": "k15",
      "port": 33735
    },
    {
      "closed_after_controls_cleanup": true,
      "closed_before_controls_cleanup": true,
      "control": "k18",
      "port": 34467
    }
  ],
  "environment_intercept_no_exec": {
    "argv_has_one_loopback_host": true,
    "canary_absent_from_receipt": true,
    "exit": 2,
    "keys": [
      "HOME",
      "LANG",
      "LC_ALL",
      "PATH",
      "TMPDIR"
    ],
    "new_session": true
  },
  "explicit_refusals": {
    "0": {
      "connection_calls": 0,
      "error": "explicit-port-out-of-range"
    },
    "34113": {
      "connection_calls": 0,
      "error": "port-refused-registered:34113"
    },
    "65536": {
      "connection_calls": 0,
      "error": "explicit-port-out-of-range"
    },
    "8080": {
      "connection_calls": 0,
      "error": "port-refused-registered:8080"
    }
  },
  "final_ports_closed": {
    "33735": true,
    "34467": true,
    "40843": true,
    "45369": true
  },
  "forged_argv_data_only": {
    "bucket": "ok",
    "classification": "rejected-targeted",
    "executed_commands": [
      [
        "/usr/bin/python3",
        "/tmp/kama-r18-falsify-SafetyDelivered/tests/llamacpp-live/check-receipt.py",
        "/tmp/kama-r18-falsify-SafetyDelivered/safety-work/k22/gate-input.json"
      ]
    ],
    "forged_sha256": "74e55336e435457c115ebf2e18d034297af0ddec528bdbf96830ed6780c93c5e",
    "gate_exit": 1,
    "gate_problems": [
      "invalid <receipt>: 1 problem(s)",
      "- argv does not exactly match the producer's server.realpath/model.arg/alias/host/port/ctx/threads command"
    ],
    "id": "k22",
    "targeted_hit": true
  },
  "production_bytes_unchanged": true,
  "python": "3.14.8",
  "registry_cases_no_bind": {
    "controls_missing": {
      "error_prefix": "registry unavailable"
    },
    "empty": {
      "refused": [
        8080,
        34113
      ]
    },
    "ipv4": {
      "refused": [
        8080,
        34113,
        45677
      ]
    },
    "malformed": {
      "refused": [
        8080,
        34113
      ]
    },
    "mapped_loopback": {
      "refused": [
        8080,
        34113
      ]
    },
    "missing": {
      "error_prefix": "registry-unreadable"
    },
    "native_loopback": {
      "refused": [
        8080,
        34113,
        45679
      ]
    }
  },
  "remaining_seat_listener_fds": [],
  "selected_controls": [
    {
      "bucket": "ok",
      "classification": "accepted",
      "failed_checks": [],
      "gate_exit": 0,
      "id": "k0",
      "inject_fired": null,
      "internal_fault": null,
      "outcome": "pass",
      "receipt_sha256": "967e0fd86e7a106ef31c59452229506f98cb09efbf5251a1f4a95a110b301d09",
      "targeted_hit": null,
      "teardown": {
        "alive_at_teardown_start": true,
        "port_refuses": true,
        "returncode": 0,
        "sigkill_sent": false,
        "sigterm_sent": true
      },
      "tool_exit": 0,
      "tool_stderr_tail": null
    },
    {
      "bucket": "ok",
      "classification": "accepted",
      "failed_checks": [],
      "gate_exit": 0,
      "id": "k17",
      "inject_fired": null,
      "internal_fault": null,
      "outcome": "pass",
      "receipt_sha256": "a18400304cf699793cd112dedae69f3ba9b0f46b5b4d8e021807883937388f3a",
      "targeted_hit": false,
      "teardown": {
        "alive_at_teardown_start": true,
        "port_refuses": true,
        "returncode": 0,
        "sigkill_sent": false,
        "sigterm_sent": true
      },
      "tool_exit": 0,
      "tool_stderr_tail": null
    },
    {
      "bucket": "ok",
      "classification": "rejected-targeted",
      "failed_checks": [
        "teardown_port_closed"
      ],
      "gate_exit": 1,
      "id": "k15",
      "inject_fired": null,
      "internal_fault": null,
      "outcome": "fail",
      "receipt_sha256": "91c5b4328b3816f092f7d39589b63bc71232a2e50af2a0336573d061c9f47668",
      "targeted_hit": true,
      "teardown": {
        "alive_at_teardown_start": true,
        "port_refuses": false,
        "returncode": 0,
        "sigkill_sent": false,
        "sigterm_sent": true
      },
      "tool_exit": 1,
      "tool_stderr_tail": null
    },
    {
      "bucket": "ok",
      "classification": "rejected-targeted",
      "failed_checks": [
        "teardown_graceful"
      ],
      "gate_exit": 1,
      "id": "k18",
      "inject_fired": true,
      "internal_fault": "internal:KeyboardInterrupt",
      "outcome": "setup-error",
      "receipt_sha256": "b55cd90f30c0bd75217d259267fe9e8a11ef6fba33e7883dea669c3f9cdcc711",
      "targeted_hit": true,
      "teardown": {
        "alive_at_teardown_start": null,
        "port_refuses": true,
        "returncode": -9,
        "sigkill_sent": true,
        "sigterm_sent": false
      },
      "tool_exit": 2,
      "tool_stderr_tail": null
    }
  ],
  "selected_controls_conform": true,
  "signal_delivery_mock_only": {
    "dead_leader": {
      "alive": false,
      "calls": []
    },
    "live_leader": {
      "alive": true,
      "calls": [
        [
          424242,
          15
        ]
      ]
    }
  },
  "tcp6_data_only": {
    "::": false,
    "::1": true,
    "::2": false,
    "::ffff:127.0.0.1": true,
    "::ffff:127.7.8.9": true,
    "::ffff:128.0.0.1": false,
    "fe80::1": false
  },
  "tracked_fake_pids": [
    1913886,
    1913996,
    1914197,
    1914198,
    1914516
  ]
}
```

## Final teardown and scratch removal receipt

After Appendix A/B publication, executed:

```text
/usr/bin/ps -p 1913886,1913996,1914197,1914198,1914516 -o pid=,ppid=,pgid=,sid=,stat=,args=
```

Exit **1**, stdout/stderr **empty**: none of the tracked fake processes remained (not even zombies). The earlier listener-inode scan was empty and all four used ports refused connections.

```text
/usr/bin/rm -rf -- /tmp/kama-r18-falsify-SafetyDelivered && /usr/bin/test ! -e /tmp/kama-r18-falsify-SafetyDelivered && /usr/bin/printf 'seat scratch removed; tracked process query was empty\n'
```

Exit **0**, stderr empty, stdout exactly:

```text
seat scratch removed; tracked process query was empty
```
