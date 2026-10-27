# S2Anchor — round 53, item: re-open S509 (ggml-backend-reg.cpp anchors)

Verdict: **PASS — no defect found in scope.** S509's four anchors are all correct at tag b11909 (fresh fetch today, byte-equal to the lane's committed copy), the line-491 comment has exactly 7 words as S509 claims, S509 conforms to CORPUS.md SOURCES.md rule 2 (`teaches` opens `supersedes S505 —`, new appended row, S505 not rewritten in place), and S505 is unchanged between base 4229ea1b and build c22602bd.

## Evidence

### 1. Re-open of S509's URL

```
curl -sSL -o $S/ggml-backend-reg.cpp \
  https://raw.githubusercontent.com/ggml-org/llama.cpp/b11909/ggml/src/ggml-backend-reg.cpp
# exit 0; 18091 bytes; 598 lines
sha256sum $S/ggml-backend-reg.cpp \
  /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909
# both: 1436b46bd1e8355345d454baa4b40069be73e9cb09a3a188d32426ea1e1037fe
```

The lane's committed copy is the same bytes:
- `git -C kama-shokunin ls-tree c22602bd8d83ab26349d1087e916ca537ee4f9d1 -- .ufo/waves/round-53/c1/` → blob `4e9681c9` for `ggml-backend-reg.cpp.b11909` (alongside `proc_pid_map_files.5.txt`, `proc_pid_mem.5.txt`, `ptrace.2.txt`).
- `git -C kama-shokunin cat-file blob c22602bd:…ggml-backend-reg.cpp.b11909 | sha256sum` → `1436b46b…` (identical).
- `git -C kama-shokunin diff c22602bd -- corpus/SOURCES.md .ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` → empty (working tree = build commit for both cited files).

So the anchor's "(copy `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909`)" is real, committed at the build, and byte-equal to what upstream serves at the tag today. A refetched copy is archived at `.ufo/waves/round-53/w1/out/S2Anchor/ggml-backend-reg.cpp.b11909.refetch`.

### 2. The four anchors, in the fetched file (line numbers via `grep -n` / ranged reads)

| S509 anchor claim | Fetched file at b11909 | OK |
|---|---|---|
| `get_executable_path()` from line 401 | line 401: `static fs::path get_executable_path() {` (the call site is 492; "from" = definition) | yes |
| `ggml_backend_load_best` from line 480 | line 480: `static ggml_backend_reg_t ggml_backend_load_best(const char * name, bool silent, const char * user_search_path) {` (call sites 578–592) | yes |
| `GGML_BACKEND_DIR` lines 488–489 | 488: `#ifdef GGML_BACKEND_DIR`; 489: `search_paths.push_back(fs::u8path(GGML_BACKEND_DIR));` | yes |
| the quoted comment line 491 | 491: `        // default search paths: executable directory, current directory` | yes |

Word count of line 491's comment (stripping `//`): `default`(1) `search`(2) `paths:`(3) `executable`(4) `directory,`(5) `current`(6) `directory`(7) — **7 words**, exactly as S509's `teaches` says ("7 words, not 21"). The round-52 lesson's "line 431" and S505's "lines 422–439" locate nothing (422–439 in this file is mid–`get_executable_path`/registry code, not the quote), confirming round-52 closure R1 (`.ufo/waves/round-52/w1/out/…` → `corpus/lessons/round-52-verifier-spotcheck.md:116,134` names precisely 401/480/491 and 7 words — consistent with what I measured).

### 3. Rule 2 conformance (`/home/vgpnk/Projects/shokunin/CORPUS.md:116-118`)

> **Append-only.** Only `status`, `recheck` and `used-by` change in place … A correction is a new row whose `teaches` opens `supersedes S0NN —`.

- `corpus/SOURCES.md:262` (S509) `teaches` cell opens verbatim: `` supersedes S505 — REJECTED: its anchor "lines 422–439" and the round-52 lesson's "line 431" are wrong (the outside closure, R1); … `` — opener matches the required form.
- It is a **new** row: the base→build diff (`git diff 4229ea1b… c22602bd… -- corpus/SOURCES.md`) is a single hunk `@@ -256,6 +256,10 @@` adding exactly S506–S509 after S505; S505 is a context line, i.e. not rewritten in place (its `status`/`recheck`/`used-by` also unchanged — see 4).
- Rejected-row shape (`REJECTED: … ; flip: …`) present; `flip: as S505` inherits S505's flip by reference. Rule 2 mandates only the opener, so this is within the contract's letter — noted as an observation, not a defect.
- Row hygiene: 11 cells (matches the registry header `id|source|kind|tier|scope|anchor|teaches|status|opened|recheck|used-by`), `opened` 2026-10-27, `recheck` on-release (same as S505, sensible for a pinned-tag URL), `used-by` = `corpus/lessons/round-53.md` (exists; its Gate row for S509 at `corpus/lessons/round-53.md:21` carries URL, access stamp 2026-10-27T06:03:07Z, copy path, the 7-word quote at line 491 — rule-1 grounding consistent with the row).

### 4. S505 unchanged at c22602bd

Command (as assigned): `git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff 4229ea1b9a789148dded1f159c20967d9a01373f c22602bd8d83ab26349d1087e916ca537ee4f9d1 -- corpus/SOURCES.md` → only the one additive hunk above; S503/S504/S505 appear as context lines. The full raw S505 row (`corpus/SOURCES.md:258`) still reads anchor `` `ggml_backend_load_best`, lines 422–439 at tag b11909; opened 2026-10-27 by seat S5Ggml … `` with `rejected | 2026-10-27 | on-release | corpus/lessons/round-52.md` — i.e. the stale anchor is preserved as history and superseded, not edited, exactly what rule 2 requires.

## Findings

None in scope. No defect to fix; no proposed diff.

## Residual risk / verification gaps

- Anchors verified against a fresh fetch of the tag URL; a tag could in principle be re-pointed upstream, but the lane's committed hash-equal copy pins the anchors independently of upstream.
- I did not run the C1/C2 counters — out of this seat's scope (S509 is a sources-calibration item); the counters' behavior is covered by other seats.
- No tools installed or upgraded (nothing needed; pacman untouched).

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S2Anchor.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-53/w1/out/S2Anchor/ggml-backend-reg.cpp.b11909.refetch` (evidence copy of the refetched b11909 source, sha256 `1436b46b…`)
