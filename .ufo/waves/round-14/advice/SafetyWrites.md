# SafetyWrites — round 14 write boundary / history preservation (sentinel, read-only)

Axes: (1) new tool is read-only, (2) selftest/harness writes only to temp, (3) no writes to the live host or repo, (4) historical files preserved. Method: static source read plus `git status`/`git diff`/`sha256sum` on the lane. I ran no tool, selftest, measure.py, test or build. Baseline is start_commit `e1b3d746dbfd2100b61c67b6389217252592460f` (tree `e5a250c5…`).

Snapshot this report reviewed: `tools/kama-ollama-evidence.py` sha256 `cb713873…7752`, `.ufo/waves/round-14/measure.py` `0c736880…46d4`, `tests/ollama-evidence/cases.json` `827e22c6…b7c2` (38 cases). These files were still changing while I reviewed. If they change again, the conclusions below need a fresh read.

## Verdict
No HIGH or MEDIUM write-boundary defect was found. There are two LOW items (W1, W2) and one cosmetic item (W3). There is also one gap in how L1's check must be done (H1).

## Evidence (observed)
- **Classifier is read-only.** It opens inputs with `os.open(path, O_RDONLY|O_NONBLOCK)` and rejects anything that is not a regular file using `fstat`/`S_ISREG`. Reads are capped at 4 MiB. The only output is `emit()` → `sys.stdout.write`. The classification path has no write, rename, chmod, network or subprocess call. There are no `urllib`/`http`/`socket` imports, and no imports outside the stdlib.
- **Selftest stays in temp.** It uses `tempfile.TemporaryDirectory(prefix='kama-ollama-evidence-')` as a context manager. Case directories are named only by index (`case-{index:03d}`), never by the fixture `name`, so a name cannot be used for path traversal. The child runs as `[sys.executable, '-I', SCRIPT, …]` with no shell, `cwd=case_dir` and a 30 s timeout. A missing-ps case passes a path inside the temp dir that does not exist; it never passes a host path. `cases.json` is opened read-only and resolved from `Path(__file__).resolve()`, not from the working directory.
- **measure.py stays in temp.** It uses `TemporaryDirectory(prefix='kama-r14-measure-')` with index-only subdirectories `f"{index:02d}"`; the owner adopted this change after I recommended it. The child runs as `-I -B` with `shell=False`, `stdin=DEVNULL` and a minimal environment (`HOME`/`TMPDIR` set to the case dir). An absent tool is detected with `is_file()` only and gives an `unsupported` failure; there is no fallback classifier. It does not invoke `kama-probe.sh`, and output goes to stdout only.
- **Fixtures.** All 38 names match `[a-z0-9_-]+`. The only URL is `https://remote.invalid` (a reserved TLD). There is no userinfo, token or secret-like key.
- **History is preserved at the time of review.**
  - `registry/history/*` hashes match the baseline I took before the files landed: `0f2c166d…`, `a119b806…`, `e9e57b9a…`, `f9f8f3b5…`. Modification times are still Oct 14.
  - `git diff --name-only HEAD` shows only LOG.md, SKILL.md, corpus/{QUALITY,README,SOURCES}.md.
  - Removed lines per file: LOG 0, QUALITY 0, README 0. SKILL has 1, which is the same last line re-added (an end-of-file newline artifact; the text is identical). SOURCES has 2.
  - The two SOURCES.md removals are the S012/S031 rows. A cell-by-cell check showed columns 1–10 are byte-equal and the new `used-by` value keeps the old one as a prefix.
  - New files are not historical: `corpus/lessons/round-14.md`, the knowledge entry, the tool, the fixtures, and round-14 wave files.
  - No lesson, receipt, verifier or older-round `.ufo` file is modified.
- **SKILL registry `Write scope` cell** says "Classification writes stdout only; selftest writes removed temporary fixtures only". This matches the source.

## Findings
- **H1 (process; must apply to the final check).** The dated snapshots `registry/history/2026…Z.json` and `.lock` are **gitignored** (`git status --ignored`). `git diff` cannot detect a rewrite of them. **Remediation:** L1 should compare by hash, for example `sha256sum registry/history/*`, against the four hashes listed above, in addition to running `git diff --name-only e1b3d74 -- corpus/lessons registry tools/kama-probe.sh tools/test-snapshot.sh .ufo/round-* .ufo/waves/round-1[0-3]`. That diff should show nothing except new untracked round-14 files.
- **W1 LOW — opening a device before checking its type.** `read_json_file` calls `os.open` *before* the `S_ISREG` check. If a caller passes a character-device path (for example a tape or watchdog node the user can open), the driver's open/close side effects can happen before the file is rejected. A FIFO is safe because of `O_NONBLOCK`.
  - Exploit path: only a path the caller supplies themselves. There is no remote trigger. Most such devices are root-only.
  - **Smallest fix (Classifier):** before opening, call `os.stat` and reject non-regular files. After opening, compare `fstat` `st_dev`/`st_ino` with the earlier stat. I sent this to SafetyInputs' area only by mentioning it here; I did not message them.
- **W2 LOW — documentation claim.** `ollama-evidence-replay.md:206-207` says the tool "never reads … environment variables". That is too broad for `--selftest`, because `tempfile` reads TMPDIR/TEMP/TMP and the top-level interpreter is not run with `-I`.
  - Side effect: if TMPDIR points inside the repo, temp fixtures are briefly written there and then removed.
  - Sent to ReplayKnowledge with replacement wording.
- **W3 cosmetic — RESOLVED.** The extra blank line before the round-14 search note in SOURCES.md has been removed. Re-read: the Search log bullets are contiguous at lines 56–62, and the SOURCES diff still removes only the 2 row lines.
- **Parity note (not safety).** For missing inputs, measure.py *omits* the flag, so the reason is `missing_required_argument`. Selftest instead passes a temp path that does not exist, so the reason is `ps_input_unavailable`. Both produce `invalid_input`/exit 2 and both fail closed. Only the reasons differ, and reasons are not graded.

## Limits
- This is static review only. I executed nothing, so temp-only writes are inferred from the source, not observed while a selftest ran.
- QUALITY/README/LOG/SKILL appends were checked for removed lines, not for content.
- I did not check fleet/sibling files, the environment or config, per the contract.
- No tools were installed or updated.

## Owner messages sent
Classifier, Harness and Fixtures: temp/index naming, no shell, read-only cases, no probe invocation, reserved hosts (adopted). ReplayKnowledge: W2. Sources: W3.
