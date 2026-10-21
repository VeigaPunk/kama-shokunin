# NullDigest — do callers accept `({}, None)` after listdir failure as comparable identity?

Scope: C1 axis7 assessment. Frozen = `install_tree` in `tools/kama-llamacpp-live.py` at
`10271460cc575fc2280aa831e442726385fc2319` (HEAD; blob also = io-grid's `FROZEN`,
sha `cec67949…`). Worktree currently carries the integrated fix + caller repairs;
all line refs below are HEAD unless marked `w/`.

## Verdict

`({}, None)` is **accepted as a comparable identity by the bare-helper callers**
(`install-links-grid` identity digests, `unpinnable-e2e` pristine scan) and
**tolerated on receipts by the gate's `allow_none`**, but it **never reaches a
receipt** through `main()` at HEAD: `install_links` re-lists the directory, hits
the same `listdir` OSError, and `main()` raises
`SetupError('install-tree-unpinnable:listdir:…')` first. The silently-escaping
form is the **partial map + valid digest** after member `lstat`/read failure,
which escapes only through a TOCTOU window between the two scans or through
callers of the bare helper.

## Before witness (frozen blob executed in /tmp, fault-injected real dirs)

`git show HEAD:tools/…` exec'd, `install_tree(<dir>/llama-server)`:

| dir state | return |
|---|---|
| `llama-server`+`libx.so`, all readable | `({both}, 'b0bff174…')` complete |
| dir `chmod 000` (listdir EACCES) | **`({}, None)`** — no exception |
| `libx.so` `chmod 000` (read EACCES) | **`({'llama-server':…}, 'f07b2567…')` — partial map, valid comparable digest** |

`lstat` failure behaves like the read row (`continue` → member dropped).

## Caller-by-caller (all `install_tree` consumers)

| Caller | HEAD behavior on `({}, None)` | On partial map+digest | Migration (w/) |
|---|---|---|---|
| `kama-llamacpp-live.py` `main()` :1414-18 | unreachable — paired `install_links` listdir fails → same-token `SetupError` exit 2; receipt keeps defaults `{}`/`None` | refused via `:unreadable`/`:not-hashed`; **escape = member vanishes between the two scans** | `install_tree` raises first; same `except SetupError` → `setup_error`, exit 2, nothing launched, gate still sees `({},None)`+`setup_error` → rejected |
| `install-links-grid.py` `identity()` (HEAD :177-186) | **accepted**: `{"install_tree_sha256": None}`; `None == None` feeds `changed`, `real_ids`, `back_compat_install_tree_sha256_equal` → two unpinnable dirs "equal" | silently recorded as the arm's identity; `changed` verdicts conflate "identity moved" with "identity incomplete" | w/ `try/except module.SetupError` → `{"setup_error": code, "problems":[code], "unpinned":[]}` → `refused=True`, `changed` via dict inequality ✓ |
| `unpinnable-e2e.py` :74 (HEAD) | `tree, _ =` discards digest; `({}, None)` → `install_links` reports all members `:not-hashed` → exit 1 (indirect catch) | same indirect catch | w/ `except producer.SetupError → RuntimeError → exit 2` (could-not-evaluate), honest ✓ |
| `check-receipt.py` gate :386-421 | `install_tree={}` → rejected `server.install_tree is empty`; null `install_tree_sha256` passes `check_digest(allow_none=True)` | recomputes sha over stored map, `tree[basename]==server.sha256`, `--expect` compare | unchanged — receipt consumer, not function caller ✓ |
| `install-tree-grid.py` :124-127 | baseline receipt w/ empty/missing `install_tree` → exit 2 (could-not-evaluate) | mutates map + recomputes sha through gate | unchanged ✓ |
| `tools/error-verdict-census.py` :228, `tests/controls.py` :129 | synthetic `{member: "a"*64}` fixture / staged pinnable trees | n/a | unaffected ✓ |
| `_install_identity_selftest` (HEAD :1135-1191) | calls `install_tree` only on pinnable synthetic tree; `chmod 0` happens **after** last `install_tree` call, then only `install_links` | n/a | no change needed — verified sequence compatible |

## Exact migration behavior

- New tokens: `install-tree-unpinnable:listdir:<detail>`,
  `…:lstat:<name!r>:<detail>`, `…:read:<name!r>:<detail>` (`<detail>` =
  `exc.strerror or type(exc).__name__`). Old producer token was
  `install-tree-unpinnable:listdir:Permission denied` (via `install_links`
  `listdir:{exc.strerror}`) → **identical shape**; `unpinnable-e2e`'s
  `startswith("install-tree-unpinnable:")` and corpus grammar
  `<stage>:<member?>:<detail>` (`llamacpp-loading-lifecycle.md:387`) both hold.
- `install_tree` now raises before the combined digest is computed — the
  `({}, None)` and partial-map returns are unreachable; success path byte-exact.
- Gate unchanged; it already refused every receipt a refusing producer emits.

## Findings

1. **[Medium] Gate accepts `{non-empty install_tree, install_tree_sha256: null}`
   without `--expect`.** `check-receipt.py:410` `allow_none=True` + `:412` skips
   recomputation when sha isn't hex — legacy tolerance for pre-`install_tree`
   receipts (`:407-408` comment). No producer emits it, so reachability is
   forgery-only, but C1's "all consumers must refuse incomplete identity" reads
   tighter than this slack. Optional hardening: `bad()` when `tree` non-empty
   and `tree_sha is None`. Selftest `tree-sha-absent-expect` pins refusal only
   with `--expect` (`:1976`), so tightening needs a paired selftest row.
2. **[Info] Grid `changed` semantics.** Under HEAD both arms recorded
   "changed=True" for silent partial results (frozen: digest moved; current:
   `problems` appears). The w/ repair keeps `changed` derived from dict
   inequality while `refused` comes from `problems` — verdict stays correct;
   the `{"setup_error":…}` synthetic dict just can't equal `real_ids`.
3. **[Info] `except module.SetupError` in w/ `identity()`.** Evaluated only on
   raise; frozen arm never raises (`with_links=False` re-raises anyway), and
   both frozen blobs (7a6bc91, 1027146) define `SetupError` — no AttributeError
   risk.
4. **[Note on claim framing]** At HEAD the producer pipeline already refused
   these faults via the `install_links` backstop; the genuinely reachable
   pre-fix escape was (a) the TOCTOU gap between the two scans, (b) every
   bare-helper consumer comparing `install_tree` tuples directly. C1 is a
   helper-contract hardening — matches the round-22 corpus supplement wording
   ("not a newly discovered producer-level escape"). Honest claim text should
   keep that scope.

## Residual risk / gaps

- `install_links` still returns `({}, None, [problems], [])` (listdir fail) —
  acceptable: it reports problems, never a clean identity; its callers fail
  closed on `problems`. Out of C1's stated scope but the same axis.
- TOCTOU between `install_tree` and `install_links` remains for the *added*
  member case (a member created between scans is hashed by the second's own
  `os.access`/`tree` checks only if it appears in `tree` — new members not in
  `tree` → `:not-hashed` → refused ✓; removed members now refuse at the new
  `lstat`/`read` raise ✓). Same-scan consistency now enforced by construction.
- Owned path: this report only. No production/test edits by this seat. Witness
  run was `/tmp`-only execution of the frozen blob; no build-wave verification
  of the new code was performed.
- Tooling: no installs this run.
