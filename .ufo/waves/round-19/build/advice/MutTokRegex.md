VERDICT: partial - uppercase-hex TOKEN mutant survived the existing selftest; this is a detector-coverage finding, not a contract change.

Axes: calibration (lowest assigned axis) and operability.

Mutant: `/tmp/kama-r19-MutTokRegex/tools/citation-provenance.py:32`, widen both TOKEN hex classes from `[0-9a-f]` to `[0-9a-fA-F]`; no other source change. Expected detector: the existing `--selftest`; a kill requires pristine/restored success and mutant failure. No broader citation-acceptance claim is made.

Exact isolated-copy command (exit 0, empty stdout/stderr):
```sh
cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-MutTokRegex
```

Same bounded detector, run from `/tmp/kama-r19-MutTokRegex` on all three byte states:
```sh
env TMPDIR=/tmp/kama-r19-MutTokRegex/out PYTHONDONTWRITEBYTECODE=1 timeout 30s python3 /tmp/kama-r19-MutTokRegex/tools/citation-provenance.py --selftest
```

| Bytes | Exit | Actual stdout | Actual stderr |
|---|---:|---|---|
| Pristine | 0 | `selftest: ok (5 cases)` | empty |
| Mutated | 0 | `selftest: ok (5 cases)` | empty |
| Restored | 0 | `selftest: ok (5 cases)` | empty |

Verdict: **SURVIVED**, not inconclusive: pristine passed, the mutated detector still passed, and restored passed.

SHA-256 from `sha256sum /tmp/kama-r19-MutTokRegex/tools/citation-provenance.py` (exit 0 in each state):
- Pristine/restored: `edc9e06a2fc7925043c46d2ac32f6dd0f4c3e60b62e26c0e6fc47f5c5794236e`
- Mutated: `f494c889178a0fdc6fe910b7cf905a8b2bc6fa682eb99b809ce4e15774617532`

Exact restoration evidence (exit 0, empty stdout/stderr):
```sh
cmp --silent /tmp/kama-r19-MutTokRegex/out/citation-provenance.py.pristine /tmp/kama-r19-MutTokRegex/tools/citation-provenance.py
```
The source bytes were restored exactly. The saved pristine/mutant `diff -u` returned exit 1 (expected differences), showing only the one regex line changed.

Artifacts: `/tmp/kama-r19-MutTokRegex/out/receipt.json` records exact commands, exits, stdout/stderr and hashes; `mutation.diff` plus `citation-provenance.py.pristine` and `citation-provenance.py.mutant` retain the actual probe bytes in that directory.

Lane source/VCS untouched; only the required advice report is written there. No tools installed/updated; no servers started. Stopped after the assigned mutation probe.
