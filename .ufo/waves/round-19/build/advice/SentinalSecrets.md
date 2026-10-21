VERDICT: partial - the citation registry is clean and subprocesses are shell-free, but default Git lazy-fetch and the copied runner's hard-coded lane path violate the no-network/no-mutation boundary.

Axes reviewed: provenance/calibration; operability; secrets and path privacy; network, shell construction, and host mutation.

### HIGH — round-18 runner ignores its /tmp copy

**Exploit path [INFERENCE]:** executing `.ufo/waves/round-18/runs/run.py` from the required `/tmp` copy still uses the absolute canonical lane root at line 5. `L`, `W`, and `R` therefore point back at the original lane. The runner writes stdout/stderr/exit files and `commands.json` (lines 21–28), creates live receipt paths, and invokes the producer three times (lines 62–68); the producer launches a child bound to `127.0.0.1` and requests `--offline` (tools/kama-llamacpp-live.py:1292–1341). I did not execute it.

**Evidence:** `git -C /tmp/kama-r19-SentinalSecrets diff -U3 1b85a24eca4d1fe81ef8d9ddf513fda1aad93e0e -- .ufo/waves/round-18/runs/run.py` exited 0 and shows the round-19 digest/pin/grid additions. Read-only inspection of `run.py:5,21–28,62–68` shows the hard-coded root and writes/process calls; producer lines 1292–1341 show the loopback launch. The runner's host-cache path at line 52 is outside the install tree and was unchanged by this diff.

**Impact:** running the copied script can write into the original lane and start a local server; it is not copy-isolated. **Smallest remediation:** derive `L` from `__file__` (or require an explicit lane argument) and refuse any resolved root other than the intended copy.

### MEDIUM — citation verification can fetch and mutate a partial clone

**Exploit path:** run the checker against a repository with a promisor remote and a missing blob (the default lane is also subject to this if it is a partial clone). `git_blob()` calls `git cat-file` via an argv list but inherits the environment and does not disable Git lazy-fetch (`tools/citation-provenance.py:38–44`).

**Evidence:** in an isolated local `file://` partial-clone fixture, `remote.origin.promisor=true`, filter `blob:none`, and the evidence blob was absent before validation. The validator exited 0 with `required=1 found=1 verified=1 missing=0 mismatch=0`; `GIT_TRACE2_EVENT` recorded `git fetch origin ...`, and the pack count rose from 1 to 2. This used only a local file transport; no external network was contacted. A fresh fixture with `GIT_NO_LAZY_FETCH=1` exited 1 (`mismatch=1`, missing blob) and retained one pack with zero fetch child-start events.

**Impact:** on an actual network-backed promisor remote, a routine check may contact that configured remote and add fetched objects to the local object store [INFERENCE]. **Smallest remediation:** pass `GIT_NO_LAZY_FETCH=1` in the `git cat-file` subprocess environment and fail closed when the blob is unavailable.

### LOW — emitted provenance contains host paths

The registry itself contains only revision IDs, repository-relative paths, and SHA-256 digests; the credential/path search over `registry/required-citations.json` found no matches. However, `--json` defaults `docs` to absolute paths (citation-provenance.py:164–173) and `scan()` returns `str(doc)` (58–65), so the `documents` output leaks the caller's workspace path. The modified runner also records raw argv/cwd in `commands.json`; the pre-existing cache path outside the install tree at `run.py:52` is included in its producer argv at line 63.

**Impact:** sharing JSON or retained run artifacts can disclose local filesystem layout; no credential value was found. **Smallest remediation:** emit document paths relative to `lane` and redact/private-scope host-local argv paths in exported run evidence.

### Safe observations and executed checks

- `python3 /tmp/kama-r19-SentinalSecrets/tools/citation-provenance.py --selftest` — exit 0; `selftest: ok (5 cases)`.
- `python3 /tmp/kama-r19-SentinalSecrets/tests/llamacpp-live/check-receipt.py --selftest` — exit 0; 6 VALID and 1 NOT-EVALUATED accepted; 74 mutations plus unreadable case rejected.
- `GIT_NO_LAZY_FETCH=1 python3 /tmp/kama-r19-SentinalSecrets/tools/citation-provenance.py --json` — exit 0; 3 required, 3 found, 3 verified, 0 missing/mismatch; its `documents` values were absolute.
- `install-tree-grid.py:48–52` and `citation-provenance.py:41–44` use argv arrays, not shell strings. The gate pins `127.0.0.1` and requires the `--no-webui --offline` argv tail (`check-receipt.py:511–528`); its upstream URL is source metadata, not a fetch call (`:90–93`).

No code or test files were edited. The canonical runner and any external/network-backed fetch were not run; those effects are marked [INFERENCE]. Supporting command/trace receipts are in `/tmp/kama-r19-SentinalSecrets/out/`.