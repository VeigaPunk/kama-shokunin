VERDICT: partial - Row drafts for both new instruments delivered; neither tool exists at lane HEAD, so every command/exit in the rows is a proposed [INFERENCE] contract; oracle pins and red-cell citations verified.

# RegNewTools — round-20 registry row drafts

Row text: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-20/build/out/RegNewTools/rows.md` (Row A census, Row B GGUF identity). Not written to `SKILL.md` (L1 integrates).

## Executed checks (command → exit)
- `git rev-parse HEAD` → `37bd4c5b…5715856`; `git status --short` → only `?? .ufo/waves/round-20/`.
- `git cat-file -e 37bd4c5:tools/error-verdict-census.py` → 128 (absent); same for `tools/gguf-identity.py` → 128. **Both tools are absent; no command for them was run.**
- `sha256sum` on stories260K.gguf → `270cba1b…d256d`, 1185376 bytes (`stat`, exit 0). Header `GGUF` (od), and raw `struct` read → version 3, tensor_count 48, kv_count 22 (exit 0).
- `uv run --quiet --with gguf python` (gguf-py **0.19.0**, uv 0.13.0; channel `uv`, reason: strict oracle for the header; ephemeral uv cache, nothing installed into the lane) → exit 0; decoded fields listed in rows.md.
- Oracle reports `general.file_type` and `general.alignment` **absent** in this file → tool must report absence (rows.md Row B).
- Receipt `.ufo/waves/round-18/live-recovery/receipt-1.json` (exit 0 read): schema `kama-llamacpp-live/v3`; `model_sha256_post` = file sha; `captures.props.fields["default_generation_settings.n_ctx"]` = 256 vs GGUF `llama.context_length` = 2048.
- `git show 37bd4c5:tests/llamacpp-live/install-tree-grid.py | sed -n 110p` → line 110 `status = ("rejected" if code == 1 else` (confirms red cell).
- `grep -n 'INVALID {args.receipt}' tests/llamacpp-live/check-receipt.py` → line 2233 (confirms gate verdict line).
- `.ufo/waves/round-18/c2/survivors.py` exists at frozen rev (`git cat-file -e` exit 0).
- `python3 tools/citation-provenance.py --lane /nonexistent/…` → exit 2 ("lane is not a git repository"); `--docs /nonexistent/…` → exit 2. **The cited red cell "exits 1 on unusable git/docs" was NOT reproduced for these inputs** (the tool header documents exit 2 for unusable registry/docs/git). Any other failing input is untested.
- `corpus/QualityCriteria.md` does not exist; the cited `QualityCriteria.md:31` is not located (only a wave spec name matches). Corpus criteria file is `corpus/QUALITY.md`. [unverified reference]
- Scratch `/tmp/kama-r20-RegNewTools` removed (`ls /tmp | grep` → exit 1, nothing left).

## Findings for L1
1. The two tools must exist and be run before rows can carry measured values; all `<L1 fills>` placeholders are unmeasured.
2. Row B needs an explicit policy for the declared-vs-served context difference (2048 vs 256). [INFERENCE: it is a present difference, not yet classified.]
3. Row B's fail-closed behaviour must not invent `general.alignment` (spec default) or `general.file_type` when absent.
4. Row A's "known red cells" list should drop the citation-provenance entry until L1 reproduces it on a concrete input; the two verified cells are install-tree-grid.py:110 and the round-18 survivors arm.
5. Row A's frozen-arm bytes come from `git show 37bd4c5…`; the census must read them from git, not the working tree.

## Out of scope / not done
- No registry row for install-tree-grid or citation-provenance (other scribes).
- No tallies, no fixtures, no tool code written (no code deliverable was requested).

## Tooling record
- gguf-py 0.19.0 via `uv run --with gguf` (uv 0.13.0), ephemeral. No pacman, no system install, no lane edits.

Report artifacts: this file; `.ufo/waves/round-20/build/out/RegNewTools/rows.md`.
