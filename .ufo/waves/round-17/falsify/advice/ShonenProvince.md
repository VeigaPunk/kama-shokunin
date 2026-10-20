VERDICT: partial — round-17 pointers, 11/11×3 receipts, unchecked promotion boxes and shell-local PATH qualify correctly; the all-503 guarantee and fake-shape population wording overreach.

# ShonenProvince — scoped falsify advice

Reviewed commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`, against start `cff9e62f05aa7cfb9059444f62eb787100719713`. Attacked only the appended round-17 sentence in `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md:8` and note in `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:70-80`, following their concrete evidence into the producer, gate and controls. This is a recommendation to L1, not admission or promotion.

Review axes: **calibration** (numbers describe the actual population and the strength of the evidence), **operability** (paths resolve and the named checks execute), **freshness** (host-footprint/PATH qualifications), and **scope integrity** (author assertions do not become non-author marks or L0 authorization). No axis scores, route changes, or additional round claims are proposed.

## Findings — severity order

### P2 / medium — “every loading 503 graded” is false at the retention limit

- Claim: `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:74-75`, **“every loading 503 graded”**. The related `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md:8` description says **“every loading 503 exact”**. The latter is true of the three cited historical receipts, but does not establish the general guarantee in PROVINCE.
- Canonical implementation: `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:75` caps distinct loading bodies at 256. At `:560-567`, overflow bodies only increment `loading_bodies.dropped`; they are not added to the graded list. At `:1343-1355`, the pass predicate consumes only retained bodies, does not require zero drops, and computes `total_503_responses` from that retained list. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/check-receipt.py:922-935` also grades only that list; it does not reject overflow or compare the malformed body still present in transitions.
- Exercised counterexample, using the unchanged pinned tool, probe and gate in the private clone: the standard good fake was extended to send 256 distinct, valid JSON loading bodies (only trailing whitespace varied), followed by a 257th 503 with `message="Busy"` and string `code="503"`, then the usual ready surfaces. The real producer captured that malformed 503 in its transition evidence but dropped it from the capped grading list.

Observed result:

```text
tool_exit=0
gate_exit=0
four_pin_gate_exit=0 (VALID)
checks=11; passed_checks=11
captured_503_count=257
invalid_503_transitions=1
retained_bodies=256; loading_bodies_dropped=1
loading_envelope_graded.passed=true
loading_envelope_graded.observed.all_exact=true
loading_envelope_graded.observed.total_503_responses=256
teardown: returncode=0, sigterm_sent=true, sigkill_sent=false, port_refuses=true
```

The fake listened only on `127.0.0.1:44787`, a non-registered ephemeral port. Its child PID was 3690253. The four-pin rerun also returned `VALID`; its model/server pins identified this generated fixture, not the real b11755 installation. No real llama-server was launched by this seat.

**Impact:** the new summary promises exhaustive grading, but saturation can still turn an observed bad envelope into a successful, gate-valid 11/11 receipt. This is not evidence that the three committed b11755 receipts are wrong: all three have zero dropped bodies. It is an adversarial boundary failure in the claimed general contract.

**Recommendation:** grade each response before retention/deduplication, or fail/could-not-evaluate when any body is dropped. Keep the documentation's coverage statement consistent with that actual behavior. Merely printing the drop count does not make “every” true.

### P3 / low — “8 bad fake-server shapes” conflates seven bad server shapes with a harness-fault control

- Claim: `/home/vgpnk/Projects/shokunin/kama-shokunin/SHONEN.md:8`, **“8 bad fake-server shapes rejected, frozen pair accepted 6”**.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py:300-326` defines eight adverse controls, but K6 uses the **good K0 server shape**, with a wrapper monkeypatching the tool's teardown to raise `RuntimeError` (`:260-287`, `:319-321`). The seven distinct bad fake-server shapes are K1, K2, K3, K4, K5, K7 and K8. K6 is a harness-fault/receipt-obligation control, not an eighth bad server shape.
- The committed frozen result's six `accepted_bad` cases are five accepted-with-receipt cases (K1, K2, K4, K5, K8) plus **K6 escaping without a receipt**, tool exit 4 and no gate invocation. See `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/runs/controls-frozen.json:118-135`, especially **“\"receipt_written\": false”**. K3 is separately inconclusive, not a demonstrated frozen detection. The current result rejects K1–K8 with zero accepted-bad and zero inconclusive.

**Impact:** the integers are correct for the counter's expressly defined adverse-control metric, but the promotion pointer misnames the population and suggests six bad server receipts were accepted. That loses the distinction between server behavior, harness fault containment and receipt-gate acceptance.

**Recommendation:** use “8 adverse controls rejected (7 bad server shapes plus an injected teardown fault); frozen accepted-bad=6 (5 accepted bad receipts plus 1 receiptless escape), with 1 additional inconclusive.” No new test is needed to establish this distinction; it follows from the pinned definitions and recorded per-control outcomes.

## Confirmed facts

1. **New repository paths resolve at the round commit.** `git cat-file -e` returned 0 for each of:
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-1.json`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-2.json`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/live/receipt-3.json`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/llamacpp-live/controls.py`
   The brace notation in SHONEN is an understandable shorthand for those three existing receipt files, not a claimed literal filename.
2. **11/11×3 and four-pin VALID are reproducible offline.** Each cited receipt has schema `kama-llamacpp-live/v2`, 11 checks and 11 `passed: true` values. All three have one retained loading-body shape, zero drops, child ownership, live-at-teardown, delivered SIGTERM, no SIGKILL, returncode 0 and refused port after teardown. All three passed the pinned gate with independently checked model, server, probe and tool digests (exit 0 each). Recorded ports are 40089, 43091 and 38545, outside the registry's 8080/34113 ports. I did not contact these historical ports.
3. **No `[x]` was written.** The pinned SHONEN contains four `[~]` boxes and zero `[x]`; PROVINCE has zero `[x]`. Comparison to the starting revision shows box 2's old prose retained as a prefix and PROVINCE's old text preserved before the appended note. The new pointer still explicitly says “no non-author mark.” This seat made no promotion mark.
4. **The fixture identity really is unchanged in the recorded evidence.** The round-16 receipt and round-17 receipt-1 have identical server realpath, server digest, implementation-library digest, model path and model digest. The producer still passes `--host 127.0.0.1`; ownership-gated teardown predicates are implemented at `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:1311-1341`. The K6 fault wrapper and producer's finalization path support the scoped teardown-fault receipt claim; no guarantee about an unwritable output destination was inferred.
5. **The shell-local PATH correction is accurate, not an installation-wide guarantee.** In the observed login and non-login Bash descendants, `/home/vgpnk/.local/bin` precedes `/usr/bin`; both resolve `llama-server` to `/home/vgpnk/.local/bin/llama-server`. `readlink -f` resolves that link to `/home/vgpnk/.local/opt/llama-b11755/llama-server`. `/usr/bin/llama-server` was absent. The pinned `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/build/advice/ScribeInstallDisclosure.md:18-34` records the same absence and expressly limits its PATH observation to that shell. The appended qualifier does not claim every service or caller has that PATH.
6. **The archive path and abbreviated hash are correct.** `/home/vgpnk/.local/opt/llama-b11755-bin-ubuntu-x64.tar.gz` exists, size 22,240,468 bytes, sha256 `753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`. Thus `753bfa73…e226` matches. The host files named by the receipts still hash to:
   - model: `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
   - server: `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
   - server implementation: `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`
   - pinned probe: `36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3`
   - pinned tool: `0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac`
7. **The note does not silently ratify scope.** `/home/vgpnk/Projects/shokunin/kama-shokunin/PROVINCE.md:71-72` retains “pending L0 ratification”; the open fleet question is `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md:58`. The fleet file is outside the lane commit, so its present contents are corroboration, not round-pinned proof of every historical operator decision. The existing lane-relative L0 pointer from the earlier paragraph was not treated as a new round-17 path or authorization.

## Commands and observed exits

Every lane executable was run only from the private clone, with `PYTHONDONTWRITEBYTECODE=1`. No lane executable was run in the lane directory. Read-only Git and direct JSON/source inspection were also used. The Python evaluation cells parsed JSON and the `CONTROLS` AST; they did not execute the controls suite.

Clone/check out (tool completed successfully):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.ShonenProvince-clone && git -C /tmp/KamaR17.ShonenProvince-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3
```

Executed each of the following three commands. Captured subprocess return codes were **0, 0, 0**, with `VALID` and empty stderr for each. They were first invoked through the shell tool and repeated once through a subprocess capture to expose numerical return codes explicitly.

```sh
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.ShonenProvince-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.ShonenProvince-clone/.ufo/waves/round-17/live/receipt-1.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.ShonenProvince-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.ShonenProvince-clone/.ufo/waves/round-17/live/receipt-2.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.ShonenProvince-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.ShonenProvince-clone/.ufo/waves/round-17/live/receipt-3.json --expect-model-sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d --expect-server-sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
```

Adversary: `env PYTHONDONTWRITEBYTECODE=1 python3 /tmp/KamaR17.ShonenProvince-attack.py` — completed normally, tool exit **0**, ordinary gate exit **0**, four-pin gate exit **0**. Exact adversary source is retained below; its scratch-file sha256 was `90bcea75c4ca4822eb42c9763938738cc81619530021ead2fede57304a52241b`. The dynamically generated gate command was:

```sh
python3 /tmp/KamaR17.ShonenProvince-clone/tests/llamacpp-live/check-receipt.py /tmp/KamaR17.ShonenProvince-overflow-hu7tccly/k0/receipt.json --expect-model-sha256 630dcd2966c4336691125448bbb25b4ff412a49c732db2c8abc1b8581bd710dd --expect-server-sha256 94b3777ba7deda8ab4d8a2a1915a607e90aaf27beb258f57c60f2a2d4bdc7341 --expect-probe-sha256 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 --expect-tool-sha256 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac
```

It inherited `PYTHONDONTWRITEBYTECODE=1`. Its temporary receipt is deliberately removed; the observed output and complete reproduction source are in this report instead of pointing only at a deleted artifact.

Additional exact commands used for identity, host-state and cleanup evidence:

```sh
sha256sum /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf /home/vgpnk/.local/opt/llama-b11755/llama-server /home/vgpnk/.local/opt/llama-b11755/libllama-server-impl.so /tmp/KamaR17.ShonenProvince-clone/tools/kama-probe.sh /tmp/KamaR17.ShonenProvince-clone/tools/kama-llamacpp-live.py
readlink -f /home/vgpnk/.local/bin/llama-server
sha256sum /tmp/KamaR17.ShonenProvince-attack.py
ss -ltnp
ss -ltnp 'sport = :44787'
rm -rf /tmp/KamaR17.ShonenProvince-clone /tmp/KamaR17.ShonenProvince-attack.py && test ! -e /tmp/KamaR17.ShonenProvince-clone && test ! -e /tmp/KamaR17.ShonenProvince-attack.py && printf 'SCRATCH_REMOVAL_EXIT=0\n'
```

The cleanup printed `SCRATCH_REMOVAL_EXIT=0`. The adversary explicitly captured `ss` exit **0**, header only; the same owned-port check after cleanup was also header only. The final glob `/tmp/KamaR17.ShonenProvince-*` returned no files. Other pre-existing host listeners were not killed or contacted.

Read-only Git subprocesses with explicitly captured exit codes were:

```text
git -C /tmp/KamaR17.ShonenProvince-clone show cff9e62f05aa7cfb9059444f62eb787100719713:SHONEN.md                         exit 0
git -C /tmp/KamaR17.ShonenProvince-clone show cff9e62f05aa7cfb9059444f62eb787100719713:PROVINCE.md                       exit 0
git -C /tmp/KamaR17.ShonenProvince-clone cat-file -e 54a29268e2083caa2b1e0d54ee1e7d90961302f3:tests/llamacpp-live/controls.py  exit 0
git -C /tmp/KamaR17.ShonenProvince-clone cat-file -e 54a29268e2083caa2b1e0d54ee1e7d90961302f3:.ufo/waves/round-17/live/receipt-1.json  exit 0
git -C /tmp/KamaR17.ShonenProvince-clone cat-file -e 54a29268e2083caa2b1e0d54ee1e7d90961302f3:.ufo/waves/round-17/live/receipt-2.json  exit 0
git -C /tmp/KamaR17.ShonenProvince-clone cat-file -e 54a29268e2083caa2b1e0d54ee1e7d90961302f3:.ufo/waves/round-17/live/receipt-3.json  exit 0
```

Preparatory shell checks also inspected read-only Git log/stat/diff, the two documents, live/run artifact filenames, the archive size/hash, and only PATH metadata in Bash/systemd. Those initial composite shell calls did not expose numerical wrapper statuses; I do not turn that into an independently observed exit-code claim. The missing `/usr/bin/llama-server` subcommand printed `No such file or directory`; it was not a failed lane test. A lane-local read of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/l0-questions.md` returned not found; the explicit fleet-root record was used instead. No recursive text search was needed for these findings.

## Reproduction source (private scratch, now removed)

Save the following source as `/tmp/KamaR17.ShonenProvince-attack.py` after making the pinned private clone named above. It changes only the generated fake's response stream, not the producer, probe or receipt gate. The controls module stages its byte-identical tool in a private temporary mini-lane and performs ownership-checked fake cleanup.

```python
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

BASE = Path('/tmp/KamaR17.ShonenProvince-clone')
spec = importlib.util.spec_from_file_location('controls_under_review', BASE / 'tests/llamacpp-live/controls.py')
controls = importlib.util.module_from_spec(spec)
spec.loader.exec_module(controls)

changes = [
    ("LOADING = {'/v1/models': 3, '/health': 1}", "LOADING = {'/v1/models': 257, '/health': 0}"),
    ("body = json.dumps(obj, separators=(',', ':')).encode()", "body = (json.dumps(obj, separators=(',', ':')) + (' ' * STATE['models'] if code == 503 else '')).encode()"),
    ("return BAD_ENVELOPE if SHAPE == 'k2' else GOOD_ENVELOPE", "return BAD_ENVELOPE if (SHAPE == 'k2' or STATE['models'] == 256) else GOOD_ENVELOPE"),
]
for old, new in changes:
    assert controls.FAKE_TEMPLATE.count(old) == 1
    controls.FAKE_TEMPLATE = controls.FAKE_TEMPLATE.replace(old, new)

with tempfile.TemporaryDirectory(prefix='KamaR17.ShonenProvince-overflow-', dir='/tmp') as root:
    row = controls.run_control(root, 'k0', BASE / 'tools/kama-llamacpp-live.py', BASE / 'tests/llamacpp-live/check-receipt.py', BASE / 'tools/kama-probe.sh')
    receipt_path = Path(root) / 'k0/receipt.json'
    r = json.loads(receipt_path.read_text())
    bad_transitions = [t for t in r['transitions'] if t.get('status') == 503 and 'Busy' in (t.get('body') or '')]
    loading_check = next(c for c in r['checks'] if c['id'] == 'loading_envelope_graded')
    print(json.dumps({
        'tool_exit': row['tool_exit'],
        'gate_exit': row['gate_exit'],
        'control_accepted': row['accepted'],
        'schema': r['schema'],
        'port': r['port'],
        'child_pid': r['child_pid'],
        'checks': len(r['checks']),
        'passed_checks': sum(c['passed'] is True for c in r['checks']),
        'captured_503_count': sum(1 + t.get('repeats', 0) for t in r['transitions'] if t.get('status') == 503),
        'invalid_503_transitions': len(bad_transitions),
        'invalid_503_body': bad_transitions[0]['body'].strip() if bad_transitions else None,
        'retained_bodies': len(r['loading_503_bodies']),
        'dropped_bodies': r['loading_bodies_dropped'],
        'loading_check': loading_check,
        'teardown': {k: r['teardown'][k] for k in ('returncode', 'sigterm_sent', 'sigkill_sent', 'port_refuses')},
    }, indent=2, sort_keys=True))
    gate_cmd = ['python3', str(BASE / 'tests/llamacpp-live/check-receipt.py'), str(receipt_path)]
    for name in ('model', 'server', 'probe', 'tool'):
        gate_cmd += [f'--expect-{name}-sha256', r[name]['sha256']]
    gate = subprocess.run(gate_cmd, text=True, capture_output=True)
    print('FOUR_PIN_GATE_COMMAND', json.dumps(gate_cmd))
    print('FOUR_PIN_GATE_EXIT', gate.returncode)
    print(gate.stdout, end='')
    print(gate.stderr, end='')
    ports = subprocess.run(['ss', '-ltnp', f'sport = :{r["port"]}'], text=True, capture_output=True)
    print('OWN_PORT_SS_EXIT', ports.returncode)
    print(ports.stdout, end='')
```

## Residual risk and verification gaps

- **LSP unavailable:** reading `xd://lsp` returned `No such tool`; no mounted status/references/definition/diagnostics operation was available. There was therefore no cold server result to warm up or interpret as absence. Source conclusions above use explicit literal reads, AST/data inspection and the exercised producer/gate path, not grep presented as semantic proof.
- The committed current/frozen controls results were independently recounted and classified, but the entire original K0–K8 suite was not rerun by this seat. The new 257-body adversary was exercised end-to-end. Other C1, corpus/frontier and fleet-provenance claims were not this seat's assignment.
- No fresh real b11755 run was performed. The three recorded real receipts were re-gated with four pins. The saturation defect does not occur in their one-shape, zero-drop evidence.
- PATH and archive checks concern the observed host and the pinned build disclosure, not a guarantee about every shell, service environment, or future installation. Only PATH metadata was exposed by the preliminary environment checks; no credential/session store was read.
- The original F1 fake process is gone: its receipt proves port refusal, and `ss -ltnp` on its exact port was empty after execution and cleanup. No registered port was bound or contacted.
- No orchestration route or resume surface was changed or invoked; `resume_continuity_v1` is not part of either documentation hunk. No admission, integration or shipping action was taken.
- **Installs/updates: none.** Existing Python stdlib, Git, Bash, coreutils and `ss` sufficed; no pacman transaction or host-service restart occurred.
- **Writes:** only this assigned Report in the lane, plus private scratch under `/tmp/KamaR17.ShonenProvince-*`, all removed before completion. No lane source/test/document, MANIFEST, fleet file, `.ufo/state`, or sibling repo was edited; no `jj` or Git write was run in the lane. The temporary adversary's generated receipts/logs were removed by its `TemporaryDirectory` cleanup. Final scratch glob: no matches.
