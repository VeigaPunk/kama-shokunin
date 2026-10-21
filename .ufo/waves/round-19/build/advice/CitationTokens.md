VERDICT: confirm - checker reports required=3 found=3 verified=3 missing=0 mismatch=0 (exit 0); independent git cat-file re-hash matches all three registry digests; 0 rows differ.

# CitationTokens: checker run and blob re-hash (round-19 build, leaf)

Scope: `tools/citation-provenance.py --json` plus `git cat-file` re-hash of the three registry blobs. Workspace: `/tmp/kama-r19-CitationTokens` (cp -a snapshot). Every command and exit: `out/RECEIPT.md`; artifact hashes: `out/SHA256SUMS`. Lane writes: this file only. Installs or updates: none.

## Result
- Checker, lane, final run (tool sha256 00998d52…, unchanged during the run): `required=3 found=3 verified=3 missing=0 mismatch=0`, exit 0. Four lane runs are byte-identical. The copy run (older tool) matches row for row.
- Re-hash (`git cat-file blob <rev>:<path> | sha256sum` in the copy; `git -C <repo> cat-file` plus hashlib in lane and copy): all three match the registry. Rows whose observed digest differs: none (0 of 3).
  - `s055-commands`, 1c325b2e…, `.ufo/waves/round-18/runs/commands.json`, 27279 B: ce7dc79c9523b92c33e0cbb141299db6196b2aa64b3c307779eee1842b51b84a
  - `gate-live-1`, eb78788b…, `.ufo/waves/round-18/runs/live-gate-1.stdout`, 90 B: b2043ba8a7b20b707367f03c13d25333ed045c4ec303b2ff3cc0df0dc5395c15
  - `c2-official-stdout`, 1b85a24e…, `.ufo/waves/round-18/runs/c2-survivors.stdout`, 249095 B: ea2e3e0258346410a04cef27a79c1ec0bbe1fd8ce8db13e683da327950cf272d
- Tokens in docs: 3, all in `corpus/lessons/round-18.md` (lines 417, 419, 421). None unregistered; none disagree with the registry.

## Findings
1. Checker changed under my run (observed). Snapshot copy sha edc9e06a… (mtime 03:13:24). A lane intermediate 03a4d167… was seen once; its content was not captured. Current lane 00998d52… (mtime 03:33:42, 8455 B) adds `corpus/lessons/round-19.md` to `DEFAULT_DOCS`, classifies a token whose digest disagrees with the registry as `mismatch` (the old code said `missing`), and runs a 12-case selftest (exit 0). This verdict covers 00998d52.
2. Exit-code contract defect (observed, both versions). Docstring lines 19-20 say exit 2 for "unusable registry/docs/git". Observed: unreadable doc gives exit 1 (missing=3); non-git lane gives exit 1 (mismatch=3, git error only in per-row `error`); unreadable registry gives exit 2. A CI wrapper cannot tell an unusable environment from a citation failure. Fix either the docstring or the exit paths. I did not change the lane.
3. Why revisions matter (observed). Tip-path files differ from the pinned digests: `commands.json` is b8dadf30c5c2ee99013917a08143de9978dd69e9c2e9d426fa7d391eaed62306 and `live-gate-1.stdout` is 1cb5a41bbfeb8f0f9306d9bf86df83d33cf9bc3aa46887c574e1dd07875574c7. `c2-survivors.stdout` matches its pin. Same in lane and copy.
4. Lane tip moved past the declared round-start (observed). HEAD and `master` are 8bf99cae (one `git log` entry after 1b85a24); `origin/master` is 8bf99cae. That commit adds only `corpus/lessons/round-18-verifier-spotcheck.md`. All three pinned revs are ancestors of HEAD (exit 0 each) and held by `refs/jj/keep/`.
5. Untracked checker inputs (observed, `git status` in copy). `registry/required-citations.json`, `tools/citation-provenance.py` and `corpus/lessons/round-19.md` show `??`. The cited blobs are committed.
6. `corpus/SOURCES.md` changed in the lane after my snapshot (copy 791e630e…3185; lane 932475538be7607acf0851172e307d2ccdc9a86b55eac35493745d98d14739a7). It has no cite tokens, and the counts are unchanged.
7. Minor (observed, V2 source line 160). `if not DEFAULT_DOCS or not all(d for d in DEFAULT_DOCS)` is a constant check and cannot fail.
8. Not mine (observed). Lane `tools/__pycache__/citation-provenance.cpython-314.pyc` has mtime 03:33:33. Direct script runs left no such file in my copy. Another process probably imported the module [INFERENCE]. I did not touch it.

## Negative controls (executed; exit codes)
- Fake digest in registry and doc token: exit 1, mismatch=1 (V2 and V0).
- Fake digest in doc token only: exit 1, mismatch=1 (V2); exit 1, missing=1 (V0).
- Nonexistent doc: exit 1, missing=3 (V2 and V0).
- Non-git lane: exit 1, mismatch=3 (V2 and V0).
- Nonexistent registry: exit 2 (V2 and V0).
- Real inputs, copy repo, V2: exit 0, 3/3/3/0/0.

## Commands cited (cwd `/tmp/kama-r19-CitationTokens`; exit)
- `python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/citation-provenance.py --json > out/checker-lane-final.json`: 0
- `python3 tools/citation-provenance.py --json > out/checker-copy.json`: 0
- `git cat-file blob <rev>:<path> | sha256sum`, three rows: 0 each
- lane `--selftest`: 0 (12 cases); copy `--selftest`: 0 (5 cases)
