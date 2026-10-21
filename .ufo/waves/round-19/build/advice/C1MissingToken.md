VERDICT: confirm - deleting any one of the three round-18 `cite()` tokens in a /tmp copy makes `tools/citation-provenance.py` exit 1 and print `missing: <row-id> <rev>:<path>` for that row; restoring gives a byte-identical file and exit 0. All three rows were checked on the snapshot checker (sha edc9e06a); the S055 row was rechecked on the live checker (sha 00998d52).

Receipts: `/tmp/kama-r19-C1MissingToken/out/` (index with every command and exit in `RECEIPT.md`).

Executed (exit codes observed):
- Snapshot baseline: default exit 0, `required=3 found=3 verified=3 missing=0 mismatch=0`; selftest exit 0 (5 cases).
- Deleted round-18.md:417 (S055) in the copy: exit 1, `missing: s055-commands 1c325b2e…:.ufo/waves/round-18/runs/commands.json`; the other two rows stay `ok`. Restored: sha256 9e65b316… equals the lane file, `cmp` exit 0, default exit 0.
- Same for :419 gate-live-1 (exit 1, named) and :421 c2-official-stdout (exit 1, named). Each was restored byte-identically.
- Live checker 00998d52 (copy refreshed to it): baseline exit 0 (3/3); selftest exit 0 (12 cases); deleting :417 gives exit 1 and names s055-commands; final state exit 0.

Findings:
1. [low, diagnostic] A token that is present with a wrong digest (:419, last hex 5→6) is labelled `missing` by the snapshot checker and `mismatch` by the live one; both exit 1. Both lines print `expected=b2043ba8a7b2 observed=b2043ba8a7b2`, the git-blob digest, so the line reads as self-contradictory. The live JSON leaves `documents` empty for that row and gives no stale-token reason. Suggest printing the document-side digest or `token=absent|stale`. Receipts: `out/mut4-digest-typo.stdout`, `out/v2-mut4-digest-typo.stdout`.
2. [low, doc drift] `SCORECARD.md:824` says `selftest 5 cases`; the live checker prints `selftest: ok (12 cases)`.
3. [info, lane drift] The lane moved after my copy. Checker sha changed edc9e06a → 00998d52 (mtime 03:33:42 -0300). `round-19.md`, `SOURCES.md`, C2 test scripts, `.jj` and `.git` refs, peer advice files and `tools/__pycache__` also changed, and `.git/HEAD` went from 8bf99cae to 7229fa95 (raw SHA). Round-18.md and the registry are unchanged (9e65b316, 5307d855). I ran no git or jj command in the lane and wrote nothing to it except this report.
4. [info] No token-shaped `cite(` text exists in the live round-19.md, SOURCES.md, SCORECARD.md or LOG.md, so no other default doc can mask a deleted round-18 token.

Not exercised: rows 2–3 under the live checker (same branch as row 1 [INFERENCE]); the v1 `mismatch` branch, which needs a consistent wrong digest in both registry and doc [INFERENCE from `check()`]; an unreadable default doc, where `scan()` only writes to stderr [INFERENCE from `scan()`].

Installs and updates: none. Servers started: none.
