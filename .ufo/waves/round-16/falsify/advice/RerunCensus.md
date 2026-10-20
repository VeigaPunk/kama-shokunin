VERDICT: confirm — the SOURCES conformance claim (41 rows, tier A 38 / tier C 3, status mined 31 / queued 5 / rejected 5, sole warning W04 S031, validate exit 0) reproduces exactly; the stated delta is exactly 7 new mined tier-A rows S035–S041 plus one used-by cell on S017.

## Commands run (all exit codes literal)

1. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → **exit 0**
   ```
   kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
   kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
   ```
2. `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh --root /home/vgpnk/Projects/shokunin kama` → **exit 0**
   ```
   kama	rows	41
   kama	tier.A	38
   kama	tier.C	3
   kama	status.mined	31
   kama	status.queued	5
   kama	status.rejected	5
   FLEET	rows	41 … FLEET.missing 0
   ```
3. Same two commands a second time into fresh files → validate and census outputs **byte-identical** to run 1 (`RERUN=identical`), exits 0/0. Deterministic.
4. HEAD~1 reproduction: `git show HEAD~1:corpus/SOURCES.md` fed through `--file` in a `/tmp` mirror whose `corpus/knowledge` and `corpus/lessons` are symlinks to the lane's real dirs → census **exit 0**, validate **exit 0**, output identical to `sources-before-*.txt` content (modulo the capture's appended `exit=0` line).

## Before → after

| metric | sources-before-*.txt | now | delta |
|---|---|---|---|
| rows / FLEET.rows | 34 | 41 | +7 |
| tier.A / FLEET.tier.A | 31 | 38 | +7 |
| tier.B | 0 | 0 | 0 |
| tier.C | 3 | 3 | 0 |
| status.mined / FLEET | 24 | 31 | +7 |
| status.queued | 5 | 5 | 0 |
| status.rejected | 5 | 5 | 0 |
| FLEET.invalid, FLEET.missing | 0, 0 | 0, 0 | 0 |

Warnings: validate output is **byte-identical** before vs now; the only W-code is the pre-existing `W04 S031 duplicate url docs.ollama.com/api/tags across scopes`. **No warning other than the known W04 S031 appeared**; no E-codes; exit 0 in both modes, before and after.

Line-level proof the before receipt is honest, not just asserted: pre-append `SOURCES.md` (HEAD~1, 93 lines) through the same unchanged script yields exactly 34 rows / 31 A / 3 C / 24 mined / 5 queued / 5 rejected, matching `sources-before-census.txt` cell-for-cell. Mirror-validate of HEAD~1 yields only the same W04 S031. Script identity unchanged across the wave: `sha256 3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`, mtime 2026-10-19 21:22:45 (both before-receipt files were written 2026-10-20).

## Field-level conformance of the append

Parsed both revisions as table cells (11 columns, id/…/used-by):
- added: `S035 S036 S037 S038 S039 S040 S041`; removed: none; rows 34 → 41, ids contiguous S001–S041.
- changed: only `S017`, exactly the `used-by` cell: `corpus/knowledge/runtime-health-surface-matrix.md` → same plus `corpus/knowledge/llamacpp-loading-lifecycle.md`. Status/tier/teaches untouched.
- S035–S041 all `tier=A`, `status=mined`; every listed used-by path exists on disk (`E11` clean and spot-checked: `llamacpp-loading-lifecycle.md`, `endpoint-identity.md`, `served-identity-crosswalk.md`, `runtime-health-surface-matrix.md`, `lessons/round-16.md`).
- Independent count (awk over the registry) reproduces the census exactly: tier.A=38, tier.C=3, mined=31, queued=5, rejected=5; total 41. So census's numbers are not a script artifact.
- Pinned-copy digests agree with the row text: S036 `server-http.cpp` sha256 `24ede172…` and S035 `README.md` sha256 `714c067…` and S037 `server.cpp` sha256 `214396…` all match `.ufo/waves/round-16/sources/llama.cpp-704366d/` files.
- Validate's E12 (row-shaped source outside `## Registry`) stays clean despite the 27-line round-16 prose supplement appended at file end: the supplement contains no `|`-row lines.

## Limitations [INFERENCE where marked]

- Attribution of the delta to `corpus/SOURCES.md` alone is direct: the only tracked change to that file is commit b8e485c (`+35 −1`: 7 rows, S017 line, 30-line prose block), working tree clean (`git status --porcelain -- corpus/SOURCES.md` empty), script unchanged since before both receipts.
- S038 release-asset digest, S039 Hugging Face LFS sha256, and S040's supersede/404 claim were **not** network-re-verified here — out of this item's scope; only the local pinned files were digested.
- S041 (own-work) has no http URL, so E04's duplicate-URL check cannot see it; same shape as existing S030/S034, so not a regression. No finding.
- Method note for future reviewers: `validate --file <copy>` on a relocated `SOURCES.md` emits phantom `E11` (34 of them) because used-by is resolved relative to the file's tree; reproduce in-place or mirror `corpus/` with symlinks. This mirrors nothing about the lane's state.
- Both `sources-before-*.txt` receipts carry a trailing `exit=0` line that the tool does not emit; treating it as a capture trailer, content matches exactly.

## Installs

None. No packages installed or upgraded; nothing was started or bound; `/tmp/kama-r16-RerunCensus` removed after use.
