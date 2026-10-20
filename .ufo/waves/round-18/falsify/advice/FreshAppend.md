VERDICT: partial — delivered selftests killed 1/4 fresh mutants; 3/4 survived although independent fixtures distinguished all four.

# FreshAppend — four preregistered mutation probes

This is scoped lane-owned falsification advice, not an outside non-author judgment or claim admission. L1 owns integration and admission. These four **fresh** mutants are a separate denominator from the named round-17 survivors. No opened-cell, blank-line termination, or refusal-prose mutant was used.

## Axes, isolation and bounds

Axes: **fresh detector sensitivity; independent fixture discrimination; byte-exact restoration and isolation**. All four defects were preregistered before the first detector run. Independent pristine detectors ran concurrently, and each phase ran its selftest and distinguishing fixture concurrently. Mutations of the same file were serialized, with byte-exact restoration between them.

Subject revision: `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`.

Executed setup (exit 0; stdout/stderr empty):

```sh
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-FreshAppend && git -C /tmp/kama-r18-falsify-FreshAppend switch -q -c seat/FreshAppend 1c325b2e58fcfdc6761f645b44cedfb1d65243e6
```

Every detector ran in `/tmp/kama-r18-falsify-FreshAppend`, using `/usr/bin/python3` (observed `Python 3.14.8`). Each child had a 15-second deadline, `TMPDIR=/tmp/kama-r18-falsify-FreshAppend/seat-tmp`, and `PYTHONDONTWRITEBYTECODE=1`. No timeout occurred. No daemon, server, model, wave dispatch, Node runtime, real policy read, registered port, or network fixture was invoked. The only production-source edits were in this private clone; the only live-lane write is this report. No installs or updates were performed.

The distinguishing detectors exercise the actual parser/comparator or entry-construction functions loaded with `runpy.run_path`, not a duplicate implementation. Their document builders and expected results do not use production selftest fixture constants. They are function-level probes, not end-to-end git-revision or dispatch executions.

## Context read and interpretation

- `corpus/lessons/round-18.md:20-29,116-145` limits C2 to named survivors and explicitly separates fresh mutants.
- `SCORECARD.md:753-760` likewise disclaims universal detector adequacy.
- `corpus/QUALITY.md:132-133` (KQ23/KQ24) was read; these parser/provenance experiments do not assess C1 control-path or live tri-state admission.
- Official `.ufo/waves/round-18/runs/append-only-selftest.stdout:1-43` reports 42/42; `provenance-selftest.stdout:1-31` reports 30/30. Their `commands.json` records exit 0 and stdout hashes matching the pristine outputs below.
- Official `runs/c2-survivors.exit:1` is `exit=2`. This seat did not rerun the official counter and does not launder its result into a pass.

## Preregistered sites and observed verdicts

All line references below are to the committed production paths at the stated revision; edits were applied only to their private-clone counterparts.

| ID | Small behavior-bearing mutation | Delivered selftest, pristine → mutant → restored | Independent fixture, pristine → mutant → restored | Verdict against delivered selftest |
|---|---|---|---|---|
| AP1 | `tools/sources-append-only.py:199`: remove `or len(cells) != len(header)` from the separator guard | **0 → 1 → 0**, 42/42 → 41/42 → 42/42 | **0 → 1 → 0**; malformed separator changes subject classification 2 → 0 → 2 | **KILLED**, targeted assertion; no crash |
| AP2 | `tools/sources-append-only.py:110`: `.strip()` of cell text → whitespace-collapsing `" ".join(...split())` | **0 → 0 → 0**, 42/42 throughout | **0 → 1 → 0**; `cold  start` → `cold start` edit loses its immutable `teaches` violation only under mutation | **SURVIVED**, non-equivalent; interior-whitespace coverage finding |
| PV1 | `.ufo/waves/round-18/dispatch-provenance.py:362`: iterate `entries` instead of `reversed(entries)` | **0 → 0 → 0**, 30/30 throughout | **0 → 1 → 0**; latest run digest/index `b×64 / 2` becomes earliest `a×64 / 0` | **SURVIVED**, non-equivalent; multiple-run binding coverage finding |
| PV2 | `.ufo/waves/round-18/dispatch-provenance.py:430`: `all(...)` → `any(...)` when recognizing member progress lists | **0 → 0 → 0**, 30/30 throughout | **0 → 1 → 0**; incomplete progress list yields spawned 2 rather than 0 | **SURVIVED**, non-equivalent; mixed-validity progress coverage finding |

**Fresh denominator:** delivered selftest killed **1**, survived **3**, inconclusive **0**, equivalent **0**, site_missing **0**, total **4**. Independent distinguishing fixtures rejected **4/4** mutants, but those are this seat's added probes, not delivered selftest kills. No production repair was made and no survivor was hidden or added to the named round-17 denominator.

### AP1 — separator-width rejection is fail-capable

Contract: `tools/sources-append-only.py:37-40,198-205` refuses a separator whose width differs from its header. The existing targeted case is at `:515-517`. The independent fixture supplies two identical 11-column registries with a two-column separator, so there is no unrelated immutable-cell delta.

Actual mutated selftest output, exit **1**, stderr empty:

```text
FAIL: separator narrower than the header (want exit 2 error ~'11-column `|---|...` separator', got exit 0)
41/42 selftest cases passed
```

Exactly one `FAIL` line was present. The distinguishing fixture's actual pristine/restored stdout (exit **0**, stderr empty):

```json
{"actual": {"error": "from:6: expected a 11-column `|---|...` separator after header", "subject_exit": 2}, "case": "AP1", "expected": {"error_contains": "expected a 11-column", "subject_exit": 2}, "ok": true}
```

Mutant stdout (exit **1**, stderr empty):

```json
{"actual": {"added": [], "subject_exit": 0, "violations": []}, "case": "AP1", "expected": {"error_contains": "expected a 11-column", "subject_exit": 2}, "ok": false}
```

This kill is attributable to the intentionally weakened separator-width predicate, not to a traceback or harness failure.

### AP2 — interior whitespace normalization escapes selftest

Contract: `tools/sources-append-only.py:43-47` promises verbatim cell contents after leading/trailing strip; `:262-266` compares the resulting immutable contents. The plausible cleanup at `:110` erases an actual immutable-cell edit. Delivered selftest cases at `:434-440` exercise literal pipe parsing with identical before/after documents, while `:470-473` changes each cell to a different token; neither witnesses this normalization defect.

Pristine/restored distinguishing stdout (exit **0**, stderr empty):

```json
{"actual": {"added": [], "subject_exit": 1, "violations": [{"details": [{"cell": "teaches", "from": "cold  start", "to": "cold start"}], "id": "S001", "kind": "cell-changed"}]}, "case": "AP2", "expected": {"added": [], "subject_exit": 1, "violations": [{"details": [{"cell": "teaches", "from": "cold  start", "to": "cold start"}], "id": "S001", "kind": "cell-changed"}]}, "ok": true}
```

Mutant stdout (exit **1**, stderr empty):

```json
{"actual": {"added": [], "subject_exit": 0, "violations": []}, "case": "AP2", "expected": {"added": [], "subject_exit": 1, "violations": [{"details": [{"cell": "teaches", "from": "cold  start", "to": "cold start"}], "id": "S001", "kind": "cell-changed"}]}, "ok": false}
```

Delivered selftest still reports `42/42 selftest cases passed`, exit **0**, with byte-identical stdout across all three phases. This is a detector-coverage finding; pristine behavior rejects the edit correctly.

### PV1 — latest-wave binding escapes singleton selftest

Contract: `.ufo/waves/round-18/dispatch-provenance.py:69-73,361-365,515-542` binds to the most recent wave run. The delivered binding fixture at `:892-897` supplies `[entry]`, so reversing traversal is observationally equivalent on that fixture. The independent fixture supplies two distinct wave runs, with attempts interspersed.

Pristine/restored distinguishing stdout (exit **0**, stderr empty):

```json
{"actual": {"bound_run_index": 2, "bound_task_call_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}, "case": "PV1", "expected": {"bound_run_index": 2, "bound_task_call_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}, "ok": true}
```

Mutant stdout (exit **1**, stderr empty):

```json
{"actual": {"bound_run_index": 0, "bound_task_call_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}, "case": "PV1", "expected": {"bound_run_index": 2, "bound_task_call_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}, "ok": false}
```

Delivered selftest remains `selftest: 30/30 checks passed`, exit **0**, byte-identical stdout in all phases. Pristine latest-wave behavior is correct; the missing witness is a multi-run ledger.

### PV2 — partial member-shape acceptance escapes homogeneous selftest

Contract: `.ufo/waves/round-18/dispatch-provenance.py:92-95,424-437` accepts progress lists only when every member carries `id` and `status`. The independent fixture has two dictionaries: one valid pending member, one missing `status`. Both are dictionaries, so the mutation cannot create an incidental `.get` AttributeError in `spawned_observations(:462-467)`.

Pristine/restored distinguishing stdout (exit **0**, stderr empty):

```json
{"actual": {"parseable": true, "refused": 0, "spawned": 0, "spawned_method": null, "spawned_methods": {}}, "case": "PV2", "expected": {"parseable": true, "refused": 0, "spawned": 0, "spawned_method": null, "spawned_methods": {}}, "ok": true}
```

Mutant stdout (exit **1**, stderr empty):

```json
{"actual": {"parseable": true, "refused": 0, "spawned": 2, "spawned_method": "omp_progress_members", "spawned_methods": {"omp_progress_members": 2, "omp_progress_pending": 1}}, "case": "PV2", "expected": {"parseable": true, "refused": 0, "spawned": 0, "spawned_method": null, "spawned_methods": {}}, "ok": false}
```

Delivered selftest remains `selftest: 30/30 checks passed`, exit **0**, with byte-identical stdout. Its `:816-817,847-852` member fixtures are uniformly valid. This finding is about missing mixed-validity coverage, not about the refusal parser.

## Commands, timing and output digests

The exact same two child argv arrays were used in all three phases of each case:

```text
AP1/AP2 selftest: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/tools/sources-append-only.py", "--selftest"]
PV1/PV2 selftest: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/.ufo/waves/round-18/dispatch-provenance.py", "--selftest"]
AP1 fixture: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py", "fixture", "AP1"]
AP2 fixture: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py", "fixture", "AP2"]
PV1 fixture: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py", "fixture", "PV1"]
PV2 fixture: ["/usr/bin/python3", "/tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py", "fixture", "PV2"]
```

Outer capture commands, each exit **0** (capture success, NOT a detector verdict), all with cwd `/tmp/kama-r18-falsify-FreshAppend`:

```sh
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP1 pristine
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP2 pristine
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV1 pristine
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV2 pristine
# Apply AP1 and PV1 independently, then:
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP1 mutated
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV1 mutated
# Restore AP1 and PV1 exactly, then:
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP1 restored
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV1 restored
# Apply AP2 and PV2 independently, then:
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP2 mutated
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV2 mutated
# Restore AP2 and PV2 exactly, then:
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase AP2 restored
/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py phase PV2 restored
```

Observed phase capture times UTC:

| Case | Pristine | Mutated | Restored |
|---|---|---|---|
| AP1 | 23:17:21.725231 | 23:17:45.132714 | 23:17:53.537311 |
| AP2 | 23:17:21.725953 | 23:18:05.557200 | 23:18:14.398277 |
| PV1 | 23:17:21.760474 | 23:17:45.170227 | 23:17:53.542636 |
| PV2 | 23:17:21.759698 | 23:18:05.562637 | 23:18:14.428267 |

All on 2026-10-20. All 24 child commands finished without timeout and with empty stderr (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`). No `own_fault` output or traceback occurred.

Stdout SHA-256 (pristine/restored are identical for every cell):

| Case/detector | Pristine and restored | Mutated |
|---|---|---|
| AP1 selftest | `e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770` | `7266f27522948ba2aaf0932530540455e19af5ece61442a3830b97791166850c` |
| AP2 selftest | `e74918130d839a79a0d620dda9bfdac5faaced6762e78fbfe415d270ad729770` | same |
| PV1 selftest | `99118cedaefe49a02646c0f1b0d6b41ddb53a3c15c23b9ef21367ea0a7a17a9a` | same |
| PV2 selftest | `99118cedaefe49a02646c0f1b0d6b41ddb53a3c15c23b9ef21367ea0a7a17a9a` | same |
| AP1 fixture | `c85d4dce3958796816547635a05a9adbbce4a9b4a177e7d7a1ed893e8f6bb3cc` | `dcc90c53b16f3a8e8aa7e519d5358cf2c38be1b42593bdf219d18f7c1074f0bc` |
| AP2 fixture | `8800bb872562b04343c9e4e07e234f4325f4268868d74bc875b93c0ea1b6ea55` | `bf0314eff8a28419d9402dac48aff304d0201ae2fe851e6878983255444e5311` |
| PV1 fixture | `3f4c8e80726d4c79a8786941ef757212998f9593fd29a7e02bd2c98c6ec0436f` | `e6992ddc804ddb9f1a23a6ee9d3e0a3994438edfb6a3987972032034dbc2ca68` |
| PV2 fixture | `c35b856fd97d8440e36239ce58d1b41b8c06ca7f4e215cee55168614eba0fec9` | `79a873c8ecc896cb4d12279657cf37e325ec722d33458e7bdf9b0d0d9b6d4f06` |

## Restoration and source hashes

SHA-256 was recorded before and after each phase's concurrent detector pair. Each of the twelve records had `stable_during_detectors: true`, with equal before/after phase hashes. Independent `sha256sum` calls before the mutations and after the final restoration yielded the same pristine target hashes.

| Case | Before / restored SHA-256 | Mutated SHA-256 |
|---|---|---|
| AP1 | `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` | `d4316fc2517ee48e792c1a67319a68fde0e01f072e3fb2bfb41dd2ec24592c06` |
| AP2 | `4d7868564226b6caa5957e9d7f4f8910a1c459ec26462a52d42e802be6079c2d` | `d0847205d2ab7999dab02a92abf41edf151434a3823a7642543ddc9aa2699748` |
| PV1 | `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f` | `b3ff167b00afac897277803f4152d9690af7a98c3e943e4e6f416131ff7df0aa` |
| PV2 | `93705f17a2b2dfeab1e80c886bcb53ae5a8e43b0c6e86e91b73a65ad5c1ea72f` | `b255ab311e7793fe8fe4092da05d37080fd9dd3ad854083d94ca89d5d62a049a` |

Preregistration hash, unchanged in every phase: `e6dd4515a6eb7588c583864d4d2862760030c642987f18af6037a51ec0923371`.

Exact experiment harness hash, unchanged in every phase: `592ccdd4babd22aefcd5e2f1b20f4c27995a1266e98adb1e153502c54af06f1e`.

A first edit-tool request refused an undisplayed private-clone anchor before applying it. The site was read and the request retried. No detector was run against an own-fault edit, and this tooling event was not counted as a mutation or kill.

## Safety evidence and limits

Executed `/usr/bin/python3 /tmp/kama-r18-falsify-FreshAppend/FreshAppend-safety.py` with cwd `/tmp`: exit **0**, stderr empty, stdout:

```json
{"ancestor_checker_processes_excluded": true, "seat_owned_processes": [], "seat_owned_tcp_listeners": [], "seat_process_groups": []}
```

No seat-owned process group remained to tear down, and no listener was created by these in-memory/tempdir detectors. The collector matches the unique scratch path in process argv/cwd and correlates any such PIDs with `ss -H -ltnp`; it excludes its own ancestor chain and is an instantaneous cleanup observation, not a global service-health claim. It reads no process environment. Its exact source is retained below (SHA-256 `091ca8fe131b5dcdf9e0350b2fa7c28ac51c76331839975bf33840f258f44c81`).

No model-quality, consumer-health, C1, general mutation-immunity or named-round17 closure conclusion follows. The three survivors support narrow missing-witness findings only. Four selected mutants are not a random sample or a full parser/provenance audit. The appended source and outputs make the experiments reproducible after removal of the scratch clone; no scratch path is offered as durable evidence.

## Exact preregistration source

Originally written at `/tmp/kama-r18-falsify-FreshAppend/FreshAppend-preregister.json` before the first detector:

```json
{
  "seat": "FreshAppend",
  "revision": "1c325b2e58fcfdc6761f645b44cedfb1d65243e6",
  "axes": ["fresh detector sensitivity", "independent fixture discrimination", "byte-exact restoration and isolation"],
  "scope": "Four fresh mutants, separate from the named round-17 set. No opened-cell, blank-line termination, or refusal-prose mutation.",
  "cases": [
    {
      "id": "AP1",
      "target": "/tmp/kama-r18-falsify-FreshAppend/tools/sources-append-only.py",
      "line": 199,
      "before": "            if not is_separator(cells) or len(cells) != len(header):",
      "after": "            if not is_separator(cells):",
      "defect": "Accept a syntactically valid separator with fewer columns than the header.",
      "selftest_prediction": "Killed by separator narrower than the header, expected subject exit 2 but mutant subject exit 0; no traceback expected.",
      "fixture": "Compare two identical 11-column one-row registries with a two-column separator; require subject parse error 2 containing expected a 11-column.",
      "fixture_prediction": "Pristine/restored detector exit 0, mutant detector exit 1 with subject exit 0."
    },
    {
      "id": "AP2",
      "target": "/tmp/kama-r18-falsify-FreshAppend/tools/sources-append-only.py",
      "line": 110,
      "before": "            cells.append(\"\".join(buf).strip())",
      "after": "            cells.append(\" \".join(\"\".join(buf).split()))",
      "defect": "Collapse interior cell whitespace rather than preserving verbatim contents after edge strip.",
      "selftest_prediction": "Survives; existing fixtures do not compare different interior whitespace.",
      "fixture": "Change only S001 teaches from cold  start to cold start in independently constructed valid registries; require the exact teaches violation.",
      "fixture_prediction": "Pristine/restored detector exit 0, mutant detector exit 1 with subject exit 0 and no violations."
    },
    {
      "id": "PV1",
      "target": "/tmp/kama-r18-falsify-FreshAppend/.ufo/waves/round-18/dispatch-provenance.py",
      "line": 362,
      "before": "    for entry in reversed(entries):",
      "after": "    for entry in entries:",
      "defect": "Bind attempts to the earliest rather than the latest wave_run in a mixed ledger.",
      "selftest_prediction": "Survives; existing binding fixture has only one wave_run.",
      "fixture": "Two wave_run entries with distinct digests separated/followed by attempts; require digest b*64 and bound_run_index 2.",
      "fixture_prediction": "Pristine/restored detector exit 0, mutant detector exit 1 with digest a*64 and bound_run_index 0."
    },
    {
      "id": "PV2",
      "target": "/tmp/kama-r18-falsify-FreshAppend/.ufo/waves/round-18/dispatch-provenance.py",
      "line": 430,
      "before": "                    and all(isinstance(e, dict) and \"id\" in e",
      "after": "                    and any(isinstance(e, dict) and \"id\" in e",
      "defect": "Treat a progress list as member evidence when any, not every, row carries id and status.",
      "selftest_prediction": "Survives; existing progress fixtures contain only well-formed members.",
      "fixture": "Parse result details.progress containing one pending member plus a dictionary missing status; require spawned 0, method null and no observed spawn methods.",
      "fixture_prediction": "Pristine/restored detector exit 0, mutant detector exit 1 with spawned 2, progress_members 2 and progress_pending 1; no non-dict rows, so no incidental AttributeError."
    }
  ],
  "execution": {
    "detectors": "For every case and phase, run the target --selftest and the independent fixture concurrently; same argv across pristine/mutated/restored.",
    "child_timeout_seconds": 15,
    "restoration": "Restore each changed line to exact pristine bytes before the next mutant for that target; record SHA-256 per phase.",
    "classification": "A target selftest kill requires green pristine/restored and red mutation with the intended assertion, not an exception. Timeout, own-fault, invalid baseline and missing site are inconclusive. Independent fixture kills are separate from delivered selftest coverage.",
    "network": "No runtime, listener, wave dispatch, real policy read, or external service is invoked. TMPDIR stays inside the isolated clone."
  }
}
```

## Exact detector/capture source

Originally `/tmp/kama-r18-falsify-FreshAppend/FreshAppend-probe.py`:

```python
#!/usr/bin/python3
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path('/tmp/kama-r18-falsify-FreshAppend')
TARGETS = {
    'AP1': ROOT / 'tools/sources-append-only.py',
    'AP2': ROOT / 'tools/sources-append-only.py',
    'PV1': ROOT / '.ufo/waves/round-18/dispatch-provenance.py',
    'PV2': ROOT / '.ufo/waves/round-18/dispatch-provenance.py',
}
COLUMNS = ['id', 'source', 'kind', 'tier', 'scope', 'anchor', 'teaches',
           'status', 'opened', 'recheck', 'used-by']


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def document(teaches='cold start', narrow=False):
    header = '| ' + ' | '.join(COLUMNS) + ' |\n'
    separator = '|---|---|\n' if narrow else '|'+ '---|' * 11 + '\n'
    row = '| ' + ' | '.join(['S001', 'https://example.invalid/source',
                            'docs', 'A', 'fixture', 'section-1', teaches,
                            'queued', '2026-10-20', '90d', 'none']) + ' |\n'
    return '# Sources\n\n## Registry\n\n' + header + separator + row + '\n## Paths\n'


def append_result(module, old, new):
    try:
        before, header = module['parse_registry'](old, 'from')
        after, unused = module['parse_registry'](new, 'to')
        violations, added = module['diff_registries'](before, after, header)
        return {'subject_exit': int(bool(violations)),
                'violations': violations, 'added': added}
    except module['ParseError'] as exc:
        return {'subject_exit': 2, 'error': str(exc)}


def fixture(case):
    module = runpy.run_path(str(TARGETS[case]), run_name='fresh_append_target')
    if case == 'AP1':
        actual = append_result(module, document(narrow=True), document(narrow=True))
        expected = {'subject_exit': 2, 'error_contains': 'expected a 11-column'}
        ok = actual.get('subject_exit') == 2 and expected['error_contains'] in actual.get('error', '')
    elif case == 'AP2':
        actual = append_result(module, document('cold  start'), document('cold start'))
        expected = {'subject_exit': 1, 'violations': [
            {'id': 'S001', 'kind': 'cell-changed', 'details': [
                {'cell': 'teaches', 'from': 'cold  start', 'to': 'cold start'}]}], 'added': []}
        ok = actual == expected
    elif case == 'PV1':
        entries = [{'kind': 'wave_run', 'taskCall_sha256': 'a' * 64},
                   {'kind': 'attempt'},
                   {'kind': 'wave_run', 'taskCall_sha256': 'b' * 64},
                   {'kind': 'attempt'}]
        entry = module['build_attempt_entry'](
            b'{"results": []}', 'spawned', str(ROOT / 'synthetic-result.json'),
            entries, {'path': str(ROOT / 'synthetic-policy.json')})
        actual = {key: entry[key] for key in ['bound_task_call_sha256', 'bound_run_index']}
        expected = {'bound_task_call_sha256': 'b' * 64, 'bound_run_index': 2}
        ok = actual == expected
    else:
        raw = json.dumps({'details': {'progress': [
            {'id': 'Member-0', 'status': 'pending'}, {'id': 'incomplete-row'}]}}).encode()
        parseable, detail = module['parse_attempt_result'](raw)
        actual = {'parseable': parseable, **detail}
        expected = {'parseable': True, 'refused': 0, 'spawned': 0,
                    'spawned_method': None, 'spawned_methods': {}}
        ok = actual == expected
    print(json.dumps({'case': case, 'ok': ok, 'actual': actual, 'expected': expected},
                     sort_keys=True, ensure_ascii=False))
    return 0 if ok else 1


def capture(argv):
    env = dict(os.environ)
    env['TMPDIR'] = str(ROOT / 'seat-tmp')
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    try:
        result = subprocess.run(argv, cwd=str(ROOT), env=env, capture_output=True, timeout=15)
        stdout, stderr = result.stdout, result.stderr
        return {'argv': argv, 'exit': result.returncode, 'timeout': False,
                'stdout': stdout.decode('utf-8', 'replace'),
                'stderr': stderr.decode('utf-8', 'replace'),
                'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)}
    except subprocess.TimeoutExpired as exc:
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        return {'argv': argv, 'exit': None, 'timeout': True,
                'stdout': stdout.decode('utf-8', 'replace'),
                'stderr': stderr.decode('utf-8', 'replace'),
                'stdout_sha256': sha(stdout), 'stderr_sha256': sha(stderr)}


def phase(case, label):
    (ROOT / 'seat-tmp').mkdir(exist_ok=True)
    target = TARGETS[case]
    before = target.read_bytes()
    commands = {'selftest': ['/usr/bin/python3', str(target), '--selftest'],
                'fixture': ['/usr/bin/python3', str(ROOT / 'FreshAppend-probe.py'), 'fixture', case]}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {kind: pool.submit(capture, argv) for kind, argv in commands.items()}
        results = {kind: future.result() for kind, future in futures.items()}
    after = target.read_bytes()
    record = {'case': case, 'phase': label, 'target': str(target),
              'at': datetime.now(timezone.utc).isoformat(),
              'target_sha256_before': sha(before), 'target_sha256_after': sha(after),
              'stable_during_detectors': before == after,
              'preregister_sha256': sha((ROOT / 'FreshAppend-preregister.json').read_bytes()),
              'experiment_source_sha256': sha((ROOT / 'FreshAppend-probe.py').read_bytes()),
              'results': results}
    path = ROOT / ('FreshAppend-' + case + '-' + label + '.json')
    path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    try:
        if sys.argv[1] == 'fixture':
            status = fixture(sys.argv[2])
        else:
            status = phase(sys.argv[2], sys.argv[3])
    except Exception as exc:
        print(json.dumps({'own_fault': type(exc).__name__, 'message': str(exc)}))
        status = 2
    raise SystemExit(status)
```

## Exact safety collector source

Originally `/tmp/kama-r18-falsify-FreshAppend/FreshAppend-safety.py`:

```python
#!/usr/bin/python3
import json
import os
from pathlib import Path
import subprocess

ROOT = '/tmp/kama-r18-falsify-FreshAppend'
raw = subprocess.run(['/usr/bin/ps', '-eo', 'pid=,ppid=,pgid=,args='],
                     capture_output=True, check=True, text=True).stdout
processes = {}
for line in raw.splitlines():
    fields = line.strip().split(None, 3)
    if len(fields) == 4:
        pid, ppid, pgid = map(int, fields[:3])
        processes[pid] = (ppid, pgid, fields[3])
ancestors = set()
pid = os.getpid()
while pid in processes and pid not in ancestors:
    ancestors.add(pid)
    pid = processes[pid][0]
seat = []
for pid, (ppid, pgid, args) in processes.items():
    if pid in ancestors:
        continue
    try:
        cwd = os.readlink('/proc/%d/cwd' % pid)
    except OSError:
        cwd = ''
    if ROOT in args or cwd == ROOT or cwd.startswith(ROOT + '/'):
        seat.append({'pid': pid, 'pgid': pgid})
ss = subprocess.run(['/usr/bin/ss', '-H', '-ltnp'], capture_output=True,
                    check=True, text=True)
listeners = [line for line in ss.stdout.splitlines()
             if any('pid=%d,' % member['pid'] in line for member in seat)]
print(json.dumps({'seat_owned_processes': seat,
                  'seat_process_groups': sorted({member['pgid'] for member in seat}),
                  'seat_owned_tcp_listeners': listeners,
                  'ancestor_checker_processes_excluded': True}, sort_keys=True))
raise SystemExit(0 if not seat and not listeners else 1)
```

## Scratch removal receipt

After the restored detector pairs, final target hashes, and empty seat-process/listener observation, executed with cwd `/tmp`:

```sh
/usr/bin/rm -rf -- /tmp/kama-r18-falsify-FreshAppend && /usr/bin/test ! -e /tmp/kama-r18-falsify-FreshAppend && /usr/bin/printf '%s\n' 'scratch_removed=true'
```

Exit **0**; stderr empty; stdout exactly:

```text
scratch_removed=true
```

The private clone and all temporary experiment artifacts are removed. Only this report, including exact experiment sources and scoped output evidence, was copied back.
