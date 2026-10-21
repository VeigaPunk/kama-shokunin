VERDICT: partial - `--json` shape matches its documented counts exactly and empty/malformed registry is a guarded exit 2 (no false 0); but the documented "unusable docs → exit 2" is not implemented — unreadable/nonexistent docs are silently skipped and exit 0 is reachable while a supplied doc was unreadable (stderr-only signal).

All commands executed in my copy `/tmp/kama-r19-C1JsonSemantics` (cp -a of the round-19 tree, exit 0); full transcript + digests: `/tmp/kama-r19-C1JsonSemantics/out/receipt-transcript.md`.

1. Shape (executed, exit 0): `python3 tools/citation-provenance.py --json` prints `{"counts":{required,found,verified,missing,mismatch},"results":[{id,rev,path,sha256,documents,observed_sha256,error,status}...]}`. The five `counts` keys and values are identical to the documented plaintext line `required=3 found=3 verified=3 missing=0 mismatch=0` (SCORECARD.md:822-824, corpus/lessons/round-19.md:10-12). Only gap: the JSON key names themselves are undocumented anywhere (docstring documents exits only) — cosmetic, not a mismatch. `--selftest` exit 0 (5 cases).

2. Empty registry — no false 0 (all executed, exit 2): `[]` → `registry must be a non-empty JSON array`; `{}` → same; invalid JSON → 2; absent registry file → 2 (main catches OSError/ValueError → 2). A row with an unknown/short rev and no token → `missing=1`, exit 1.

3. Unreadable doc — cannot forge a verified row (blob check is `git cat-file`-based, doc-independent), but the documented exit-2 contract for docs is dead code: `scan()` swallows OSError with a stderr line and `continue` (tools/citation-provenance.py:57-62).
   - Default docs: `chmod 000 corpus/lessons/round-18.md` → `missing=3` exit 1; all four docs 000 → exit 1. Fails closed today only because all three tokens live solely in `corpus/lessons/round-18.md:417-421` — incidental, not structural.
   - Fabricated (executed): one readable doc carrying the 3 registry tokens + one `chmod 000` supplied doc → `required=3 found=3 verified=3 missing=0 mismatch=0`, **exit 0**, warning only on stderr. Same exit 0 with a nonexistent `--docs` path. Under the docstring contract ("2 unusable registry/docs/git") that run is a false 0: pass reported while a supplied document was silently dropped from the scanned set.

Minimal repair: make `scan()`'s OSError fatal (propagate → main returns 2, matching its own docstring), or count skipped docs (e.g. `docs_unreadable` in counts) and fail when > 0.
