VERDICT: partial — the recorded hard-pin controls discriminate removal of 34113, but not loss of registry parsing or fail-open registry reads.

# Attack and axes

Seat: KamaR16.MutateLiveRefusal. Attacked only `refused_ports()` in isolated copies of `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py`.

Axes: **operability** (refuse before networking/launch), **coverage** (registry-only ports and unreadable registry), **calibration** (separate existing-control survivors from mutants killed by added detectors). These are probe dimensions, not round admission or score judgments.

Three independent one-line mutants; the same seven-case bounded detector ran on pristine, mutated, and exactly restored bytes for each. The three subjects ran concurrently within each phase. No subagents, server starts, HTTP probes, or successful socket operations. The only persistent write is this report; all scratch was removed.

## Mutants

All line references below are to `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py` before mutation. Only the corresponding scratch subject was edited.

| Subject | Mutation inside `refused_ports()` | Intended defect |
|---|---|---|
| DropRegistryParsing | line 209: `for pat in patterns:` → `for pat in ():` | Preserve the registry read/error gate but never add parsed ports. |
| Drop34113 | line 217: `return refused` → `return refused - {34113}` | Remove 34113 from the final refusal set, including its registry-derived entry. |
| FailOpenRegistry | line 200: `raise SetupError(f'registry-unreadable:{REGISTRY}')` → `return refused` | On an unreadable registry, return only hardcoded pins rather than fail closed. |

Removing 34113 only from the initial hardcoded set would let the real registry add it back. The selected mutation removes it at the behavior-bearing return point instead.

# Safety boundary and digest ordering

The executable was **not invoked**: its path was supplied for the tool's existing prelaunch identity checks. Every tool invocation used a Python audit barrier that raises a `BaseException` on **every `socket.*` audit event** and on child-process launch events. An intercepted event exits the wrapper with **97**, explicitly a detector sentinel, not a native tool exit. Imports and the real scratch `main(argv)` were executed; refusal and digest computations were not mocked.

The three weakened-refusal paths stopped at `socket.getaddrinfo`, before name resolution, socket construction, connection, bind, or launch. There were **three such intercepted attempts** across all 63 invocations and **zero intercepted launch events**. All other invocations returned natively before the barrier was needed. In particular, neither 8080 nor 34113 was actually connected to or bound.

Ordering is both source-grounded and exercised:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:710-716`: model hash comparison returns 3 on mismatch.
- Same file, lines 726-727: `refused_ports()` and `pick_port()` occur afterward.
- Same file, line 824: child `subprocess.Popen` occurs later still.
- Server executable/model/probe existence checks precede the digest comparison; “digest first” here means **before registry, port selection, and launch**, not before every setup check.

In **all 18 wrong-digest runs**, including unreadable-registry runs and all three mutant states, the trace was exactly:

```text
main:call
model_digest:call
model_digest:return
main:return:3
```

No `refused_ports`/`pick_port` call or blocked audit event occurred. Actual stderr was:

```text
kama-llamacpp-live: model digest mismatch
  expected: 0000000000000000000000000000000000000000000000000000000000000000
  actual:   270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d
  refusing to launch
```

**Consequence:** a wrong hash safely prevents launch but also prevents testing the refusal logic. Exit 3 in such a run is not evidence that a registered port was refused.

# Exactly what ran

Working directory for driver commands: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Python was already installed: `python3 --version` → `Python 3.14.8`, exit 0; `id -u` → `1000`, exit 0. The executable identity check `stat -c '%n %s %a' /home/vgpnk/.local/opt/llama-b11755/llama-server` returned `/home/vgpnk/.local/opt/llama-b11755/llama-server 17864 755`, exit 0.

Setup command, exit 0:

```sh
python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py setup
```

Driver invocations and observed outer exits:

| Exact command | Exit | Assertions passed |
|---|---:|---:|
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name DropRegistryParsing --phase pristine` | 0 | 7/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name Drop34113 --phase pristine` | 0 | 7/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name FailOpenRegistry --phase pristine` | 0 | 7/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name DropRegistryParsing --phase mutated` | 1 | 6/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name Drop34113 --phase mutated` | 1 | 6/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name FailOpenRegistry --phase mutated` | 1 | 5/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name DropRegistryParsing --phase restored` | 0 | 7/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name Drop34113 --phase restored` | 0 | 7/7 |
| `python3 -B /tmp/kama-r16-MutateLiveRefusal/detect.py detect --name FailOpenRegistry --phase restored` | 0 | 7/7 |

Each driver invocation ran these seven tool commands, bounded at 60 seconds each, in its own subject directory. No timeout occurred. The exact argument-vector template was:

```text
/usr/bin/python3 -B /tmp/kama-r16-MutateLiveRefusal/guarded.py
  /tmp/kama-r16-MutateLiveRefusal/<Subject>/tools/kama-llamacpp-live.py
  --server /home/vgpnk/.local/opt/llama-b11755/llama-server
  --model /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
  --model-sha256 <Hash>
  --probe /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh
  --port <Port>
```

`<Subject>` is exactly the table's subject name. `GOOD` below expands to `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; `BAD` is exactly 64 zeroes.

There is **no registry CLI option** in `build_parser()` (same source, lines 634-663). Registry selection was exercised through the tool's existing `LANE = SCRIPT.parent.parent` / `REGISTRY = LANE / 'registry' / 'endpoint-consumers.tsv'` calculation, not a source override. The unreadable fixture was that scratch registry file at mode **000**, running as uid 1000. It was not a synthetic exception. The sentinel fixture appended this one row only in scratch (tabs shown as `\t`):

```text
mutation-only\t/tmp/absent-consumer\tgrep:host:60001\thttp://127.0.0.1:60001/v1\t-\tisolated registry-only port
```

The original scratch registry bytes and mode were restored in `finally` after every seven-case detector invocation.

## All per-command outcomes

`P/R` is the observed pristine **and** restored result for each of the three subjects. All 42 P/R cases passed. `97` means the audit barrier stopped an attempted preflight network operation; it is not a native exit or proof a server launched. All tool stdout was empty.

| Case | Registry fixture | Port | Hash | Expected exit / stderr token | P/R | DropRegistryParsing mutated | Drop34113 mutated | FailOpenRegistry mutated |
|---|---|---:|---|---|---:|---:|---:|---:|
| actual-34113-bad-digest | Actual registry | 34113 | BAD | 3 / `model digest mismatch` | 3 | 3 | 3 | 3 |
| actual-34113 | Actual registry | 34113 | GOOD | 2 / `port-refused-registered:34113` | 2 | 2 | **97** | 2 |
| actual-8080 | Actual registry | 8080 | GOOD | 2 / `port-refused-registered:8080` | 2 | 2 | 2 | 2 |
| registry-only-60001 | Actual + sentinel row | 60001 | GOOD | 2 / `port-refused-registered:60001` | 2 | **97** | 2 | 2 |
| unreadable-34113-bad-digest | Mode 000 | 34113 | BAD | 3 / `model digest mismatch` | 3 | 3 | 3 | 3 |
| unreadable-34113 | Mode 000 | 34113 | GOOD | 2 / `registry-unreadable:` | 2 | 2 | 2 | **2, wrong reason** |
| unreadable-60001 | Mode 000 | 60001 | GOOD | 2 / `registry-unreadable:` | 2 | 2 | 2 | **97** |

Actual differing stderr excerpts:

```text
DropRegistryParsing / registry-only-60001:
  SAFETY_STOP:socket.getaddrinfo
  exit=97; blocked=["socket.getaddrinfo"]

Drop34113 / actual-34113:
  SAFETY_STOP:socket.getaddrinfo
  exit=97; blocked=["socket.getaddrinfo"]

FailOpenRegistry / unreadable-34113:
  kama-llamacpp-live: port-refused-registered:34113
  exit=2; blocked=[]

FailOpenRegistry / unreadable-60001:
  SAFETY_STOP:socket.getaddrinfo
  exit=97; blocked=["socket.getaddrinfo"]
```

For the corresponding pristine/restored unreadable case the actual reason was `kama-llamacpp-live: registry-unreadable:/tmp/kama-r16-MutateLiveRefusal/<Subject>/registry/endpoint-consumers.tsv` and exit 2. For ordinary refused ports, stderr was exactly `kama-llamacpp-live: port-refused-registered:<Port>` and exit 2.

# Which existing controls discriminate these mutants?

The historical receipt inspected was `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/controls.txt:4-14`. Its recorded negative cases are digest mismatch (3), 34113 refusal (2), 8080 refusal (2), and listening port 631 (2). It does **not** contain a registry-only-port or unreadable-registry control. The actual registry at `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv:35-37` names 8080 and 34113, which are also hardcoded pins.

| Mutant | Recorded digest + hard-pin control replay | Seven-case bounded detector verdict | Coverage interpretation |
|---|---|---|---|
| DropRegistryParsing | **SURVIVED**: same digest exit 3 and both expected hard-pin refusals, exit 2. | **KILLED** by the added registry-only 60001 case (native refusal → guarded network attempt). | [INFERENCE] The historical control set would miss the defect: it has no consumer port outside the hardcoded set. |
| Drop34113 | **KILLED at the 34113 refusal boundary**: expected refusal token/exit 2 became audit-stop exit 97. Digest-only control still survives. | **KILLED** by `actual-34113`. | [INFERENCE] A control asserting the recorded `port-refused-registered:34113` token would catch this defect. The unguarded final tool exit was deliberately not measured. |
| FailOpenRegistry | **SURVIVED** with the readable actual registry: digest and both hard-pin outputs unchanged. | **KILLED** by the added unreadable cases: wrong reason at 34113, audit-stop at 60001. | [INFERENCE] The historical control set would miss the defect because its registry read succeeds. Even a new unreadable-34113 control checking only exit 2 would miss it. |

An exit-only check can confuse `port-in-use`, `registry-unreadable`, and registered-port refusal, since all are setup exit 2. The observed unreadable-34113 mutant is a concrete example: **same exit, wrong refusal cause**. The recorded token is therefore important when saying a control “catches” a defect.

No baseline failed, so none of these seven-case mutation verdicts is inconclusive. Existing-control survivors are **coverage findings**, not permission to weaken the contract or a finding that pristine refusal logic is broken. This seat did not integrate changes, admit C2, or change scores.

# Hashes, exact restoration, and cleanup

Initial command, exit 0:

```sh
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py /home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf
```

| Input | Initial and final SHA-256 |
|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py` | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv` | `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c` |
| `/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf` | `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |

| Scratch subject | Pristine SHA-256 | Mutated SHA-256 | Restored SHA-256 |
|---|---|---|---|
| DropRegistryParsing | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` | `9c4ca180668b84cc3695e096dd8a82cf2050b66c9e7acf27fcc6df6713b32bf3` | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` |
| Drop34113 | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` | `3a41332536e7aeb89cf8b8894350b5d95486e991108fbff31b49bb97dbc3bae3` | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` |
| FailOpenRegistry | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` | `aa6eff906c188519922d41e49084fd4b6a6f96bcc208b24e55ad66df1e6c7972` | `cf95f382032d9c510c5e59124c3fda3a50915c0800fdbcd27ddbd145a9ef39ea` |

Every detector receipt also recorded the restored registry digest `bf343625188d9f486a6f6d13c60c946e23c21d05ee1bef881204dfa14c62bc6c`. Each source edit was individually reversed before the restored run.

Final hashing command, exit 0, confirmed all three restored copies equalled the unchanged original, and registry/model hashes still matched:

```sh
sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py /tmp/kama-r16-MutateLiveRefusal/DropRegistryParsing/tools/kama-llamacpp-live.py /tmp/kama-r16-MutateLiveRefusal/Drop34113/tools/kama-llamacpp-live.py /tmp/kama-r16-MutateLiveRefusal/FailOpenRegistry/tools/kama-llamacpp-live.py /home/vgpnk/Projects/shokunin/kama-shokunin/registry/endpoint-consumers.tsv /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf /tmp/kama-r16-MutateLiveRefusal/detect.py /tmp/kama-r16-MutateLiveRefusal/guarded.py
```

Detector SHA-256: `80aa6ec262b9fa9836c4a1c04820084ab9f7b0ce0e57d3e312b4e0987addf0ce`. Guard SHA-256: `b0d56ababc8b8d7bdc2cc849c1c95caf239eb3d41cfdd571d4d9b45697028cc2`.

Before and after the experiment, `pgrep -x llama-server` returned **exit 1, no output**. No server was started by this seat. Cleanup command returned exit 0:

```sh
rm -r -- /tmp/kama-r16-MutateLiveRefusal && test ! -e /tmp/kama-r16-MutateLiveRefusal
```

## Limitations

- These are bounded, no-network refusal tests, not lifecycle runs. Exit 97 is explicitly harness-generated; no claim is made about a mutant's eventual unguarded native exit or port availability.
- The historical 631 listener control and positive live receipt gates were not rerun: this assignment forbids server startup and did not require listener probing. Statements about the complete historical control set are marked [INFERENCE].
- Permission-denied behavior was exercised at mode 000 as uid 1000. Other OSError subclasses were not separately enumerated.
- No alternative registry CLI flag exists; the unreadable fixture used the existing script-relative registry path in scratch.
- The initial/final source hash identifies the bytes attacked; no git operation was used to independently establish a commit association.
- `pgrep` is point-in-time process evidence, not a claim about other seats between observations. The audit barrier provides the stronger seat-local no-launch boundary.

## Installs

None. Used the existing Python 3.14.8 standard library and existing core utilities; no package transaction, tool upgrade, service restart, or runtime invocation.

# Reproduction appendix: exact scratch harnesses

The two files below were the executed detector and guard. They are embedded because scratch was required to be removed. Recreate them at their named absolute scratch paths, run `setup`, then the phase commands above while applying/reversing only the one-line mutations listed above. The detector itself is unchanged across all phases. Do not omit the audit guard when reproducing a mutated case.

## `/tmp/kama-r16-MutateLiveRefusal/guarded.py`

```python
#!/usr/bin/env python3
"""Execute the real scratch main while refusing every socket and child process."""
import json
from pathlib import Path
import runpy
import sys

subject = Path(sys.argv[1]).resolve()
argv = sys.argv[2:]
model = argv[argv.index('--model') + 1]
events = []
blocked = []


class SafetyStop(BaseException):
    pass


def audit(event, args):
    if event.startswith('socket.') or event in {
        'subprocess.Popen', 'os.system', 'os.fork', 'os.forkpty', 'os.exec', 'os.posix_spawn'
    }:
        blocked.append(event)
        raise SafetyStop(event)


def profile(frame, event, value):
    if frame.f_code.co_filename != str(subject):
        return
    name = frame.f_code.co_name
    if name == 'sha256_file' and str(frame.f_locals.get('path')) == model:
        label = 'model_digest'
    elif name in {'main', 'refused_ports', 'pick_port'}:
        label = name
    else:
        return
    if event == 'call':
        events.append(f'{label}:call')
    elif event == 'return':
        if name == 'main':
            events.append(f'{label}:return:{value}')
        else:
            events.append(f'{label}:return')


sys.addaudithook(audit)
code = 98
try:
    namespace = runpy.run_path(str(subject), run_name='isolated_refusal_subject')
    sys.setprofile(profile)
    code = namespace['main'](argv)
except SafetyStop as exc:
    print(f'SAFETY_STOP:{exc}', file=sys.stderr)
    code = 97
finally:
    sys.setprofile(None)
    print('GUARD_TRACE=' + json.dumps({'events': events, 'blocked': blocked}, sort_keys=True),
          file=sys.stderr)
sys.exit(code)
```

## `/tmp/kama-r16-MutateLiveRefusal/detect.py`

```python
#!/usr/bin/env python3
"""Bounded scratch-only refusal detector; never permits sockets or children."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path('/tmp/kama-r16-MutateLiveRefusal')
LANE = Path('/home/vgpnk/Projects/shokunin/kama-shokunin')
SOURCE = LANE / 'tools/kama-llamacpp-live.py'
REGISTRY = LANE / 'registry/endpoint-consumers.tsv'
SERVER = Path('/home/vgpnk/.local/opt/llama-b11755/llama-server')
MODEL = Path('/home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf')
MODEL_SHA = '270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d'
GUARD = ROOT / 'guarded.py'
NAMES = ('DropRegistryParsing', 'Drop34113', 'FailOpenRegistry')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def setup():
    for name in NAMES:
        base = ROOT / name
        (base / 'tools').mkdir(parents=True, exist_ok=False)
        (base / 'registry').mkdir()
        shutil.copy2(SOURCE, base / 'tools/kama-llamacpp-live.py')
        shutil.copy2(REGISTRY, base / 'registry/endpoint-consumers.tsv')
    print(json.dumps({'source_sha256': digest(SOURCE),
                      'registry_sha256': digest(REGISTRY),
                      'scratch_sha256': {n: digest(ROOT / n / 'tools/kama-llamacpp-live.py')
                                         for n in NAMES}}, sort_keys=True))


def detect(name, phase):
    base = ROOT / name
    subject = base / 'tools/kama-llamacpp-live.py'
    registry = base / 'registry/endpoint-consumers.tsv'
    original_registry = registry.read_bytes()
    original_mode = registry.stat().st_mode & 0o777
    tests = (
        ('actual-34113-bad-digest', 'actual', 34113, '0' * 64, 3, 'model digest mismatch'),
        ('actual-34113', 'actual', 34113, MODEL_SHA, 2, 'port-refused-registered:34113'),
        ('actual-8080', 'actual', 8080, MODEL_SHA, 2, 'port-refused-registered:8080'),
        ('registry-only-60001', 'sentinel', 60001, MODEL_SHA, 2, 'port-refused-registered:60001'),
        ('unreadable-34113-bad-digest', 'unreadable', 34113, '0' * 64, 3, 'model digest mismatch'),
        ('unreadable-34113', 'unreadable', 34113, MODEL_SHA, 2, 'registry-unreadable:'),
        ('unreadable-60001', 'unreadable', 60001, MODEL_SHA, 2, 'registry-unreadable:'),
    )
    rows = []
    try:
        for test, fixture, port, sha, expected_exit, expected_reason in tests:
            registry.chmod(original_mode)
            content = original_registry
            if fixture == 'sentinel':
                content += (b'\nmutation-only\t/tmp/absent-consumer\tgrep:host:60001\t'
                            b'http://127.0.0.1:60001/v1\t-\tisolated registry-only port\n')
            registry.write_bytes(content)
            if fixture == 'unreadable':
                registry.chmod(0)
            command = [sys.executable, '-B', str(GUARD), str(subject),
                       '--server', str(SERVER), '--model', str(MODEL),
                       '--model-sha256', sha, '--probe', str(LANE / 'tools/kama-probe.sh'),
                       '--port', str(port)]
            result = subprocess.run(command, capture_output=True, text=True,
                                    timeout=60, cwd=str(base))
            trace = None
            output_lines = []
            for line in result.stderr.splitlines():
                if line.startswith('GUARD_TRACE='):
                    trace = json.loads(line.split('=', 1)[1])
                else:
                    output_lines.append(line)
            stderr = '\n'.join(output_lines)
            passed = (result.returncode == expected_exit and expected_reason in stderr
                      and trace is not None and not trace['blocked'])
            rows.append({'test': test, 'fixture': fixture, 'argv': command,
                         'exit': result.returncode, 'stdout': result.stdout,
                         'stderr': stderr, 'trace': trace,
                         'expected_exit': expected_exit, 'expected_reason': expected_reason,
                         'passed': passed})
    finally:
        registry.chmod(original_mode)
        registry.write_bytes(original_registry)
    report = {'mutant': name, 'phase': phase,
              'source_sha256': digest(subject),
              'registry_restored_sha256': digest(registry),
              'passed': sum(row['passed'] for row in rows),
              'total': len(rows), 'rows': rows}
    out = ROOT / f'{name}-{phase}.json'
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, sort_keys=True))
    return 0 if report['passed'] == report['total'] else 1


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('action', choices=('setup', 'detect'))
    p.add_argument('--name', choices=NAMES)
    p.add_argument('--phase', choices=('pristine', 'mutated', 'restored'))
    args = p.parse_args()
    if args.action == 'setup':
        setup()
    else:
        sys.exit(detect(args.name, args.phase))
```
