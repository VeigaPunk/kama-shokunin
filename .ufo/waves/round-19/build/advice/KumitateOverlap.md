VERDICT: partial - no install-tree pinning and no file or cited-line collision with the kama round-19 delta in kumitate-shokunin; citation-pin and origin-pin mechanisms overlap in concept and are live in kumitate round 36, but use different mechanisms and share no file.

# KumitateOverlap - kama round-19 advice (leaf seat, read-only)

Receipt: `/tmp/kama-r19-KumitateOverlap/out/KumitateOverlap-receipt.md` (commands, exits, hashes); rows: `out/collisions.tsv`. Kama copy HEAD `8bf99ca`; kumitate HEAD `eb4c106`. Axes touched: calibration (C1 coverage, C2 independence and blind spot). No axis moved by this scan.

## Baseline
- Assigned tip `1b85a24` is the parent of copy HEAD `8bf99ca` (`merge-base --is-ancestor`, exit 0). `8bf99ca` touches only `corpus/lessons/round-18-verifier-spotcheck.md` (+153, exit 0). Record the base as `8bf99ca`.
- Round-19 delta (`git status --porcelain`, exit 0): M `.ufo/waves/round-18/runs/run.py`, `SCORECARD.md`, `corpus/SOURCES.md`, `corpus/lessons/round-18.md`, `tests/llamacpp-live/check-receipt.py`; new `tools/citation-provenance.py`, `registry/required-citations.json`, `tests/llamacpp-live/install-tree-grid.py`, `corpus/lessons/round-19.md`, `.ufo/waves/round-18/residual/assignments.json`, `.ufo/waves/round-19/`.
- Registry revs `1c325b2e`, `eb78788b`, `1b85a24e` are commits; the repo is not shallow (exit 0 each).

## Kumitate negatives (whole tree, `.gitignore` off)
- `install_tree`, `install-tree`, `tree_sha256`, `expect-install`, `DT_NEEDED`, `S057`, `ld.so`: 0 matches.
- `cite(`, `required-citations`, `citation-provenance`, `revision-qualified`, `check-receipt`, `install-tree-grid`: 0 matches in kumitate content (hits only in `.ufo/interactive-sessions/` transcripts, roster text, not triaged exhaustively).
- Explicit kama path references: one, `.ufo/waves/round-35/falsify/SrcS026Reopen.md:41-42` (C-07).
- Kama mentions elsewhere are domain routing only (`PROVINCE.md:27`; `corpus/knowledge/kimi-*.md` endpoint notes).

## Collisions (file:line)
| id | kama (round-19 side) | kumitate | status |
|---|---|---|---|
| C-01 pin mechanism | `tools/citation-provenance.py:31-32` (explicit token), `:38-50` (immutable `rev:path` blob sha), `:81-82` (exact-token hit) | `scripts/cite-check.mjs:1116` (PIN_RE, gap `[\s\S]{0,32}?`), `:1127` (sha256 typed by marker or gap), `:1187` (hash of current file), `:1214-1219` (rev resolve), `:1522-1528` (nearest-owner binder) | concept overlap; live in round 36 (`.ufo/waves/round-36/baseline/cite-pin.txt:1-3`) |
| C-02 pin readers | `tests/llamacpp-live/check-receipt.py:27`, `:384-390` | `scripts/claims-check.mjs:57-69`, `:123-144`; `scripts/proxy-check.mjs:351-372` (copy); `scripts/surface-probe.mjs:171-179` (third reader), `:1725-1726` | concept overlap; kumitate's own 'five readers' defect (`.ufo/waves/round-36/build/CriticPinSemantics.md:30`, M10b) |
| C-03 digest over a file set | `tools/kama-llamacpp-live.py:178-202`; `check-receipt.py:165-170`; `install-tree-grid.py:32-34` | `scripts/surface-probe.mjs:724-728`, `:1117` (declared-input digest), `:1262-1265` (reorder mutant) | design contrast: kama walks a directory, kumitate digests a declared list |
| C-04 self-derived expected pin | `.ufo/waves/round-18/runs/run.py:57-60`, `:64` (expected digest from the producer's own `install_tree()`) | `.ufo/rounds/round-33/receipt-prerequisites.json:27` (no rehashing a dispatched digest) | analogy [INFERENCE] |
| C-05 fleet-index binding (latent) | round-19 files: `tools/citation-provenance.py`, `registry/required-citations.json`, `tests/llamacpp-live/*.py` | `scripts/cite-check.mjs:121`, `:290`, `:999`, `:1539` (fleet index = whole shokunin tree; only `node_modules`, `.git`, `target`, `.ufo` excluded); `cite-pin.txt:3` (`fleet=/home/vgpnk/Projects/shokunin`) | latent; no current kumitate citation of these basenames |
| C-06 same relative path | `corpus/lessons/round-19.md` (new), `round-18.md` (M), `corpus/SOURCES.md` (M), `SCORECARD.md` (M) | same paths exist in kumitate | name-only; no shared file |
| C-07 cross-lane anchor drift | `corpus/lessons/round-10.md:92` lists six IDs and says 're-derived'; the 'five unversioned anchors ... blocking' wording is at `:135` | `.ufo/waves/round-35/falsify/SrcS026Reopen.md:41-42` cites `:92` with the `:135` wording | pre-existing, kumitate-side; round 19 does not touch round-10.md |
| C-08 checked, no collision | `PROVINCE.md:11-23` (not in delta) | `.ufo/waves/round-35/build/ConnectorSiblingOverlap.md:20` | none; `scripts/local-helper.mjs:8` is under `$UFO_SRC`, absent from kama (`ls` exit 2) |

## Measured facts for C2 (install tree)
1. `llama-server` NEEDED: `libllama-server-impl.so` (regular file), `libstdc++.so.6`, `libgcc_s.so.1`, `libc.so.6`; RUNPATH `$ORIGIN` (`readelf -d`, exit 0; `out/llama-server-dynamic.txt`).
2. `libllama-server-impl.so` NEEDED: `libllama-common.so.0`, `libmtmd.so.0`, `libllama.so.0`, `libggml.so.0`, `libggml-base.so.0`, then system libs (exit 0; `out/libllama-server-impl-dynamic.txt`).
3. Those five SONAMEs are symlinks in the install dir (`find -printf`, exit 0; 10 `l` entries). The producer digests regular files only (`tools/kama-llamacpp-live.py:191-195`). The grid's `DEFAULT_MEMBERS` are the versioned regular targets (`install-tree-grid.py:28-29`), and it mutates only members (`:71`, `:86-89`).
4. So retargeting a SONAME link changes neither `install_tree_sha256` nor any grid row. The 3/3 result covers member-byte swaps only. Loader effect of a retarget: [INFERENCE], not executed.

## Other handoff-relevant points
- Digest formula is copied in three kama files (C-03); the pin is the producer's own output (C-04). A formula defect is invisible to all three.
- C1 coverage: `check()` requires presence of an exact token in the four `DEFAULT_DOCS` (`citation-provenance.py:33-34`, `:63-66`, `:81-82`) and blob equality (`:83-90`). It does not check that a token sits on the claim it supports, or that one sentence does not fuse two revisions (kumitate names that class at `.ufo/waves/round-35/falsify/CriticC2Final.md:34`).
- Clone dependence: rev resolution needs full history (`.ufo/waves/round-36/build/ScoutCiteProvenance.md:51-52`). Here the copy is not shallow, so the three rows resolve; a fresh shallow clone will report mismatch [INFERENCE].

HANDOFF: No kumitate file or line collision with round 19. Keep C1's explicit `cite()` and immutable blob pins, and do not import `cite-check.mjs:1116` or `:1187` pins. Fold the install_tree formula to one authority and add a SONAME-retarget case to the grid, since the five symlinks in measured fact 3 sit outside the pin. Record the base as `8bf99ca`, not `1b85a24`. The `SrcS026Reopen.md:41-42` anchor is a kumitate-side fix, not a round-19 change.

Verification: every command and exit is in `/tmp/kama-r19-KumitateOverlap/out/KumitateOverlap-receipt.md`. Nothing installed. No servers. No lane writes beyond this file. No kama gate, selftest, harness or test was run.
