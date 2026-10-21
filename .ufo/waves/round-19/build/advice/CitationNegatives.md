VERDICT: confirm - C1 checker (tools/citation-provenance.py) fails closed on every required-citation mutation class and names the failing row in each; 20/20 negative cases nonzero exit, no fail-open found.

Campaign: /tmp/kama-r19-CitationNegatives (cp -a of round-19 tree; lane untouched). All commands executed there; receipts at /tmp/kama-r19-CitationNegatives/out/ (summary.md, negatives.tsv, negatives-text.tsv, logs/, negatives.py, negatives-text.py).

Executed: `python3 tools/citation-provenance.py` → 0 (`required=3 found=3 verified=3`); `--selftest` → 0 (5 cases); `python3 out/negatives.py` → 0 (`cases=20 exit0=0`, post-restore rc=0); `python3 out/negatives-text.py` → 0 (15 text-mode cases, post-restore rc=0).

Matrix (rows s055-commands, gate-live-1, c2-official-stdout):
- wrong rev (swapped to a sibling row's rev; and bogus f*40), wrong sha, absent path: 3×4=12 cases, each exit 1, line `missing: <id> <rev>:<path> expected=… observed=…|absent (fatal: …)` names the row id.
- doc+registry co-drift sha: 3 cases, exit 1, `mismatch: <id> … expected=… observed=…` with observed equal to the true blob digest — the observed-vs-expected branch works.
- registry-level fail-closed: `[]` exit 2 (`registry must be a non-empty JSON array`); malformed JSON exit 2; row missing `sha256` exit 2 and non-string `sha256: 123` exit 2, both printing `invalid registry row: {...}` with the row dict.
- `--docs <absent>`: exit 1, all rows `missing`. Post-restore baseline: exit 0.

Calibration notes (improvements, none fail-open; L1 may fold into C1 polish):
1. Registry-only wrong-sha surfaces as `missing` (token triple rev,path,sha must match), never `mismatch`; the `mismatch` branch is reachable only when doc token and registry drift to the same wrong digest. Selftest's 5 cases do not cover `mismatch`; a 6th co-drift case would.
2. `missing` conflates token-absent with pointer drift: with docs absent, expected==observed (blob verifies) yet status is `missing` — correct semantics, noisy line.
3. wrongrev-swap prints `observed=` from the swapped rev's blob on a `missing` line — accurate, slightly confusing.

Operability: untouched; checker is read-only (git cat-file), no listeners, no installs.
