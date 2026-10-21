# SrcHashlib — round 22 C1 source scout (Python `hashlib`, 3.14)

Seat `KamaR22.SrcHashlib`, read-only. Owned path: this file only. SOURCES not edited; ID reserved for L1 (next free = S075; current registry tops at S074).

## Source opened

- URL: https://docs.python.org/3.14/library/hashlib.html
- Version: page title "hashlib — Secure hashes and message digests — Python 3.14.8 documentation"; footer "Last updated on Oct 21, 2026 (10:01 UTC)". Host interpreter `python3 --version` = Python 3.14.8 (matches).
- Access: 2026-10-21 ~13:00 UTC, HTTP/2 200, `last-modified: Wed, 21 Oct 2026 10:03:03 GMT`, etag `"6ad88dd7-1d853"`, 120915 bytes, fetched HTML sha256 `0273eec6a65fb821ef4036100d5c9bb47f294bf2e1906818483f46e56de5376a` (copy was at /tmp, not retained in lane; L1 re-fetches if a pinned copy is wanted).

## Located quotes (each ≤25 words)

1. §Hash Objects, `hash.update(data)` (anchor `#hashlib.hash.update`):
   > "Repeated calls are equivalent to a single call with the concatenation of all the arguments: m.update(a); m.update(b) is equivalent to m.update(a+b)."
2. §Hash Objects, `hash.digest()` (anchor `#hashlib.hash.digest`):
   > "Return the digest of the data passed to the update() method so far."
3. §File hashing, `hashlib.file_digest` (anchor `#hashlib.file_digest`), supporting only:
   > "The function may bypass Python's I/O and use the file descriptor from fileno() directly."

## Findings for C1 (observed vs inference)

Observed in the code at base 10271460 (`tools/kama-llamacpp-live.py`): `sha256_file` lines 171–176 streams 1 MiB `fh.read` chunks into `h.update`, then calls `hexdigest()`. `install_tree` lines 178–202 returns `(tree, None)` when `listdir` fails (186–187). It `continue`s on an `lstat` OSError (190–193) and on a `sha256_file` OSError (196–199). Then it computes `combined` over whatever `tree` holds (200–201).

- Quote 1 (streaming equivalence). Chunked streaming gives the same digest as hashing the whole file in one call. So the success path's per-file digests do not depend on the chunk size or the number of reads, and the fail-closed fix keeps them byte-identical as long as it does not change which bytes are fed. **Use:** the positive digest control in `install-io-grid.py` MAY compare against a one-shot `hashlib.sha256(bytes).hexdigest()`, and that comparison is justified by the docs.
- Quote 2 (digest meaning). A digest is a function of "the data passed … so far". It carries no record of whether that data was complete. **[INFERENCE]** The `combined` value built from a `tree` that has lost members is a well-formed, comparable sha256 of the *partial* name/sha lines, and nothing in the value marks it as partial. Completeness has to be enforced by the caller, so refusing with `SetupError('install-tree-unpinnable')` is the only way to make that incompleteness visible. This is the docs-backed half of the C1 claim. The skip behaviour itself is code-observed (lines 186–199), not something the docs say.
- Quote 2 also covers a mid-read failure. If `fh.read` raises partway through a file, `sha256_file` never reaches `hexdigest()` (the exception propagates out of line 175). At base the member is then dropped silently (line 198), so it is not hashed as a prefix. The danger is omission, not a truncated digest.
- Quote 3 (fault-injection design caveat). `file_digest` "may bypass Python's I/O" and read via `fileno()`. **Advice for ApiFix and Matrix:** do not refactor `sha256_file` onto `hashlib.file_digest` this round. If that happened, mocks that patch `open` or `read` might never intercept the reads, and the red-before/green-after matrix would go silently vacuous. Inject at `os.listdir`, `os.lstat`, `builtins.open`, or the module's `sha256_file`, all of which the current code calls directly.
- Gap: the page says nothing about I/O error handling, partial files, or directory identity. It cannot support any claim about listdir/lstat semantics. That belongs to the Python `os` docs, which the round-21 re-open already used and which have no hashlib overlap.

## Redundancy check

`corpus/SOURCES.md` at base has no row citing `hashlib` or `docs.python.org/3.14/library/hashlib.html`. The Python rows are S044/S064 (subprocess returncode), S051 (exceptions), and S061/S065 (sys.exit), none of which overlap. S066 teaches that a regular-file digest cannot see symlink state, and S068/S069 cover tree-hash prior art. None of them defines what a digest *means* or the streaming equivalence. Not redundant.

## Proposed row (ID reserved for L1 → S075)

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S075 *(L1 allocates)* | Python `hashlib` hash objects (Python 3.14) — https://docs.python.org/3.14/library/hashlib.html#hashlib.hash.update | docs | A | streaming-update equivalence and what `digest()` denotes for CPython 3.14.8 hash objects; not file/dir completeness, not I/O error semantics | §Hash Objects `hash.update(data)` and `hash.digest()`; page titled Python 3.14.8 documentation, last updated 2026-10-21 10:01 UTC; opened 2026-10-21 | `m.update(a); m.update(b)` equals `m.update(a+b)`, and a digest covers only the data fed so far, so a digest over a partial member map is valid yet carries no completeness signal; refusal must come from the caller. | mined | 2026-10-21 | on-release | corpus/lessons/round-22.md *(L1 confirms the consumer)* |

Tier A is justified because this is the official CPython documentation, version-pinned to the host interpreter, and the claim is the API contract itself. The completeness consequence is kama's inference and SHOULD be tagged so in the lesson, the same way S066's digest consequence was.

Flip conditions: the 3.14 docs change the `update` equivalence or the `digest()` wording, or the host moves off 3.14 (re-open at the new version). Reject conditions: none met. The source is primary and on-topic, so it is not rejected.

## Remaining unknowns

- Which consumer file (lesson or knowledge note) L1 lists in `used-by`.
- Whether L1 wants a lane-pinned raw copy and sha256 under `.ufo/waves/round-22/sources/`. This seat did not write one, per its read-only bounds.

## Installs

None.

## Checks proposed for L1 (not run)

- `curl -sSL https://docs.python.org/3.14/library/hashlib.html | sha256sum` to re-pin. Expect a drift from `0273eec6…` if the docs get rebuilt; the quotes are what matter.
- `python3 -c "import hashlib;a=hashlib.sha256();a.update(b'x');a.update(b'y');assert a.hexdigest()==hashlib.sha256(b'xy').hexdigest()"` as a no-harm sanity check of quote 1 on the host interpreter.
