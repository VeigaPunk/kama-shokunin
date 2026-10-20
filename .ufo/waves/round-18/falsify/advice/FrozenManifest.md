VERDICT: confirm — all 10 frozen sources are byte-identical to `e75cf680b53484a61709ee1b2787d8dbc6419f74` blobs (SHA-256 and git blob OID), the manifest path mapping and SHA256SUMS are complete/unique/self-consistent, `prior_exposure` explicitly declares the set non-heldout, and no pycache/temp file exists on disk or in history.

## Scope and method

Read-only static reads against the live lane, plus an independent re-verification in a fresh clone
(`git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r18-falsify-FrozenManifest`,
`git switch -c seat/FrozenManifest 1c325b2e58fcfdc6761f645b44cedfb1d65243e6`, clone removed after the
check). No production edits, no official counting command, no installs, no listeners.

## 1. Every frozen byte equals the e75cf680 blob

`cd .ufo/waves/round-18/frozen && sha256sum -c SHA256SUMS` → exit 0, 10 × `OK`.
Independent cross-check in the clone: for each manifest entry, `git cat-file blob <rev>:<lane path>`
vs the frozen file bytes, `git hash-object <frozen file>` vs `git rev-parse <rev>:<lane path>`, and the
SHA256SUMS digest — `ALL_BYTES_SHA_OID_OK= True`.

| frozen file | lane path at e75cf680 | sha256 | blob OID | bytes |
|---|---|---|---|---|
| tools_kama-llamacpp-live.py | tools/kama-llamacpp-live.py | 0efd1723b02ef748d720a6036d3ac481b1d5fe9755110999d7c9acaf486c46ac | 07c3b61f4721 | 57556 |
| tests_llamacpp-live_check-receipt.py | tests/llamacpp-live/check-receipt.py | ad6801791f2ada896a7ee188609391aac86185c47320dbf415331869ca9cd2a5 | 886670df76b1 | 60756 |
| tests_llamacpp-live_controls.py | tests/llamacpp-live/controls.py | aad8b1c758fe9616ecd7ad78538dbfd82227c7e99df3b051d2bf82d34d6e3a06 | be751c0713d5 | 26791 |
| tests_probe-verdicts_check.py | tests/probe-verdicts/check.py | ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099 | d5ebf264ef6d | 27947 |
| tests_probe-verdicts_fault-controls.py | tests/probe-verdicts/fault-controls.py | d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312 | 46e600977148 | 33332 |
| tools_sources-append-only.py | tools/sources-append-only.py | c477a172cd5ae1512a9f75456da216a7df8cfde1df7c28fd09e60b76054b1e05 | b4116bb021bf | 14899 |
| tools_kama-probe.sh | tools/kama-probe.sh | 36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3 | ce45ea8e53ee | 49744 |
| round-17_c1_mutants.py | .ufo/waves/round-17/c1/mutants.py | 498d1f7fa7f248d7c794db95ac6208a59c13297305226774e6aa4dc6ff88ac1e | 539d81c701b0 | 54928 |
| round-17_dispatch-provenance.py | .ufo/waves/round-17/dispatch-provenance.py | 11ebb2c02f4c9160a4f20fba8d107b14be648ce6a3b1722dbbd112961b8d96df | 5716a7a5bdb2 | 37928 |
| round-17_count-verdicts.py | .ufo/waves/round-17/count-verdicts.py | 1ffa75604728f9d6993fdb7f7173ba8915de7f0ff1d8f8d75487641773fa905a | 3436dbfa45a0 | 10916 |

`git cat-file -t e75cf680b5…` → `commit`; `git merge-base --is-ancestor e75cf680… HEAD` → exit 0;
`git rev-parse master` → `1c325b2e58fcfdc6761f645b44cedfb1d65243e6`. The frozen bytes are the round-17
delivered production: `git diff --stat 54a2926 e75cf680 -- tools tests` is empty.

## 2. Manifest mapping and SHA256SUMS

- `manifest.json:3` revision is the full 40-hex `e75cf680…`; `:5` capture is
  `git show e75cf680…:<path>; SHA256SUMS contains the byte digests`; `:7-18` map all 10 names.
- Mapping is explicit, 10/10 unique lane paths, all relative, no absolute path and no `..` component;
  every path resolves at the pinned revision (`git cat-file`/`rev-parse` exit 0 for all).
- `SHA256SUMS` has exactly the same 10 names as `manifest.json.files` (set equality), unique names,
  lowercase 64-hex digests, LF only, no CRLF. No duplicate JSON keys (strict `object_pairs_hook`).
- Frozen directory contains exactly 12 entries: the 10 sources + `manifest.json` + `SHA256SUMS`;
  no subdirectories, no symlinks, no hardlinks (all link counts 1, distinct inodes from production).
- `SHA256SUMS` sha256 = `696211fb8005743e66c61286c028465eec199c5f5815ce868e0edd57ea32ba8c`, equal to
  `runs/c2-survivors.json` `inputs["frozen/SHA256SUMS"].sha256`. `manifest.json` sha256 =
  `d48de26866567525d052a63d37a64e0e4a06167bc19305913e80076fe7de8e7b`, identical in working tree and
  `HEAD` blob.

## 3. prior_exposure and not-heldout

- `manifest.json:6` states verbatim: “The author and seats had access to these lane sources and
  round-17 survivor findings before this capture. These are frozen historical comparators, not a
  held-out evaluation set.”
- Case-insensitive `held.?out|heldout` over `.ufo/waves/round-18`, `corpus/lessons/round-18.md`,
  `SCORECARD.md`, `corpus/QUALITY.md` hits only `frozen/manifest.json:6` and the falsify assignment
  prompt itself. No lesson, scorecard, advice file or counting artifact treats the frozen set (or the
  round-17 survivor list) as held out or as an outside non-author evaluation.
- Consistent hedging: `corpus/lessons/round-18.md:22-24` “bounded named-survivor repair, not evidence
  that an unseen mutant cannot survive”; `SCORECARD.md:744-760` “not a claim of universal detector
  adequacy”; `runs/c2-survivors.json` `fresh_wave2 = {included:false, mutants:0, reason:"fresh wave-2
  mutants are a separate denominator"}`. `round-18.md:8` “Outside round 17” refers to the round-17
  non-author verifier, not to the frozen comparator.

## 4. No pycache/temp in the frozen set

- `find .ufo/waves/round-18/frozen -mindepth 1 \( -name '__pycache__' -o -name '*.py[co]' -o -name '*.tmp'
  -o -name '*~' -o -name '*.swp' -o -type l \)` → empty.
- `git ls-tree -r HEAD .ufo/waves/round-18 | grep -Ei '__pycache__|\.py[co]$|\.tmp$|~$|\.swp$|\.orig$|\.rej$'`
  → no output, grep exit 1.
- `git rev-list --all --objects | grep round-18 | grep -Ei '__pycache__|\.pyc$|\.tmp$'` → no output.
- Repo-wide committed count of `.pyc/.pyo/__pycache__` under `HEAD` = 0.

## 5. Consumers pin the verified bytes

- `c1/measure.py:118` `FROZEN_REV = 'e75cf680b53484a61709ee1b2787d8dbc6419f74'`; `:119-120`
  `FROZEN_GIT_PATHS`; `:189-225` `git_blob` via `git show` and `frozen_pin` compare frozen bytes,
  sha256 and length against the blob.
- `runs/c1-measure.json` and `runs/c1-self-mutants.json`: `frozen_tool`/`frozen_gate` have
  `verified:true`, `git_rev:e75cf680…`, blob sha256 `0efd1723…`/`ad680179…`, bytes 57556/60756 —
  identical to this verification.
- `c2/survivors.py:145-160` `FROZEN_DIR`/`FROZEN_TOOLS`; `:477-494` SHA256SUMS parse; `:737-742`
  every frozen input must have a sums entry and is snapshotted before execution.
  `runs/c2-survivors.json` records `pinned_ok:true` with the same digests for all four frozen tools and
  `inconclusive_reasons.frozen_witness_mismatches: []`.
- Probe + nine matrix JSON unchanged: `runs/run.py:66` compares each worktree file to
  `git show e75cf680:<path>` and `runs/probe-matrix-identity.json` shows `same:true` for all 10; my
  independent `git rev-parse e75cf680:<path> HEAD:<path>` is identical for all 10.
- Pins are not stale relative to delivery: `git diff --stat c6dc46f..HEAD -- tools tests` is empty, so
  measured revision `c6dc46f` and delivered `1c325b2` have identical production bytes.

## Limits and residuals (none block the verdict)

- The manifest names the source commit and paths but no per-file digest/blob OID; digests live only in
  the sibling `SHA256SUMS` (the capture field points there). QUALITY KQ16 (`corpus/QUALITY.md:61`)
  describes an OID pin and a `git cat-file blob` comparison; C1's counter uses `git show` and checks
  sha256/bytes without an OID, and C2 performs no git read at all (same-commit SHA256SUMS only). The
  e75cf680 correspondence is therefore reproducible by an external verifier (this report) but is not
  reproduced by the committed C2 counting command; the C2 integrity anchor is same-commit trust.
- `manifest.json`'s own sha256 (`d48de268…`) is not pinned by any run artifact; only `SHA256SUMS`
  (`696211fb…`) is recorded (`runs/c2-survivors.json`).
- Frozen `round-17_c1_mutants.py` and `round-17_count-verdicts.py` are not read by either official
  counter; they are stored comparators whose mapping is accurate (no dangling reference).
- Adjacent, outside this seat's question: `SCORECARD.md:767` still says measured results “are appended
  after execution”, but the Round-18 measured block is absent from `SCORECARD.md` (numbers are in
  `corpus/lessons/round-18.md:154+`). Flagged for the docs/L1 seats.

## Hygiene

No production/fleet/lane edits from this seat; concurrent working-tree changes seen during the check
(`corpus/SOURCES.md`, untracked `runs/corrected.py`, etc.) are sibling seats' work. The /tmp clone was
removed; `ps -eo pid,args | grep FrozenManifest` empty and this seat started no listener. No tools
installed or upgraded.
