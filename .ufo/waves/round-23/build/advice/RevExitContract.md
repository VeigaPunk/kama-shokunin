# RevExitContract: exit-contract review of tools/report-landing-audit.py

Findings only. No production edits, no commits, no writes to the lane or fleet repositories.

## Scope and pin

- Target: `tools/report-landing-audit.py`, working tree, uncommitted against HEAD `4fe9339`. `git status`: ` M tools/report-landing-audit.py`, `?? .ufo/waves/round-23/`, `?? tests/report-audit/`.
- The file changed twice during the review. First read: sha256 `79d9e124…` (921 lines). Re-test copy: sha256 `684764108872cea153284dfec89848d5efdf5b30dd37db026434dea2b623e210` (924 lines). The diff between them only rewords the docstring, drops `core.quotePath=true` from `GIT_ISOLATION`, and folds the errata hex check into `status.get`. Every case below was re-run on `684764…`; it is the version reported. Line numbers refer to `684764…`.
- Tools: git 2.56.0, Python 3.14.8 (`sys.get_int_max_str_digits()` = 4300). Nothing installed or upgraded.
- Fixtures: fresh trees under `/tmp/revexit/cases` and `/tmp/revexit/v2cases`, run with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 HOME=/tmp/revexit/home`. Only `file://` clones, no network hosts, nothing pointed at the real lane or fleet.
- No subagent dispatch (leaf member).

## Contract under test

Docstring lines 42–46: `Exit: 0 clean …; 1 failed …; 2 could-not-evaluate (missing/irregular report, unusable git or non-UTF-8 git output, shallow/grafted/non-sha1 repository, malformed ledger, empty round selection, output failure). Errors are never verdicts.`

| Contract item | Observed on `684764…` | Ref |
|---|---|---|
| missing report → 2 | holds | selftest `missing-report-is-error` |
| irregular report → 2 | **violated** for the committed report path (symlink, directory) | X2, F3 |
| unusable git → 2 | holds (symlink-loop lane path, bad lane path) | negatives |
| non-UTF-8 git output → 2 | **violated** for `git log` and `ls-tree` (decoded with `surrogateescape`) | X3 |
| shallow / grafted / partial → 2 | holds (shallow, `info/grafts`, promisor clone). non-sha1 not exercised | negatives |
| malformed ledger → 2 | **violated** for integer overflow in a ledger row | P1 |
| empty round selection → 2 | not exercised (code path in `run()`) | — |
| output failure → 2 | **violated**: non-`OSError` exceptions escape (P3); closed fd 1 exits with the verdict code and no output (F6). `/dev/full` and broken pipe do give 2 | P3, F6 |
| Errors are never verdicts | **violated** (F1–F5, X1–X3, P1–P3) | — |

Structural cause. `main()` (lines 908–920) maps only `EvalError` and `OSError` to 2. Any other exception escapes, and CPython exits 1, which is the "failed" code. Output is `print(..., flush=True)` (909–910), and a no-op print on closed fd 1 never raises. Parsing trusts field shapes (`split(SEP, 3)` at 190, `int()` at 196, 203, 359, 407, 412, 414, 423). `git()` (109–128) checks return codes only (120–121), so rc-0 stderr errors are dropped.

## Findings

Severity: **High** = exit 0 where evaluation was defective (silent false clean). **Medium** = exit 0 or 1 where the contract requires 2, or a documented rule that needs a decision. **Low** = coverage and dead code.

### High

**F1. A 0x1F byte in the author name silently drops a required round commit (exit 0, expected 1).**
- Repro: lane commit with `GIT_AUTHOR_NAME=$'kama-shokunin\x1f1700'`, subject `round-10: hidden`, `atime` before cutoff. Fleet report cites the two other round-10 commits. Git accepts the name. `git log -1 --format=%an|%at|%s` gives `kama-shokunin\x1f1700|1700000150|round-10: hidden`.
- Observed (`grid-part2-confirm.txt`, case A): rc=0, `round_commits=2 required=2 defects=0`. Same lane with a plain author (A2): rc=1, `round_commits=3 required=3 defects=1`.
- Mechanism: `round_commits` (181–197) splits on SEP with maxsplit 3 (190). The shape check (191–192) only tests `fields[0]` (40-hex) and `fields[2]` (digits). The injected `1700` satisfies `fields[2]`. The subject becomes `1150\x1fround-10: hidden`, `pat.match` (195) fails, and the commit is silently not required.
- Fix direction: NUL-delimited format (`-z` or `%x00`), or reject any record whose `%an`/`%s` contains SEP or END.

**F2. A 30-digit author timestamp is accepted as a far-future time, so the commit is classified post-report (exit 0).**
- Repro: `git hash-object -t commit -w --literally` (the default write refuses with `badDateOverflow`) of a commit by `kama-shokunin` with `author … 999…(30 digits) +0000`, round-10 subject, not cited.
- Observed (case B): rc=0, `round_commits=3 required=2 post_report=[<sha>]`. `git log --format=%at` prints the 30 nines.
- Mechanism: `int(atime)` (196) accepts any digit string. `post = [c … if c["atime"] > cutoff]` (322) excludes it silently.
- Fix direction: bound timestamps (digit count and plausible range) and raise EvalError.

**F3. A symlink at the committed report path is evaluated as report text (exit 0 when the target text is a clean report).**
- Repro: fleet commits `.ufo/reports/round-10/kama.md` as a symlink whose target string is a complete clean report, with newlines.
- Observed (case E / c06): `git show HEAD:.ufo/reports/round-10/kama.md` prints the target (151 chars). Audit rc=0, expected 2.
- Mechanism: `audit_round` (301) does `git show HEAD:{rel}` with no object-mode check. The S_ISREG guard (206–208) applies only to `--report` overrides. Selftest `irregular-report-is-error` (870) covers only that override.
- Fix direction: `git ls-tree HEAD -- <rel>` and require mode 100644 or 100755 and type blob, otherwise EvalError.

**F4. Per-repo ambiguity is masked by a found result in the other repo (exit 0, expected 1).**
- Repro: lane holds commit L (round-10, prefix P) and blob X (also prefix P). Fleet holds L only. Report cites P (7-hex, checkable).
- Observed (`ambiguous-prefix-masked`): rc=0, defects=0, `lane-cands=2 fleet-cands=1`. Expected `landed-ambiguous`, rc=1.
- Mechanism: `lookup` sets `ambiguous` from the bare pass (142), but the peeled pass sets `found` unconditionally (165) for any repo that resolves the commit. Ambiguity is never recomputed over the union.
- Fix direction: collect distinct full object ids per token across both repos. More than one means ambiguous. Keep per-repo ambiguity.
- Likelihood: accidental collision is rare (about N/2^28 per citation). A deliberate collision needs a birthday search of about 4k objects, which I ran.

**F5. An abbreviation naming two different commits in lane and fleet, with neither repo ambiguous, is clean (exit 0, expected 1).**
- Repro: lane commit L and fleet commit M, different objects, share 7-hex prefix P. Found by a birthday search.
- Observed (case G): `P=d8825ea lane-cands=[d8825eacbc…] fleet-cands=[d8825ea864…]`. rc=0, defects=[]. Expected rc=1.
- Mechanism: same as F4. The union is never checked for distinct ids. The `landed-omitted` check (336) accepts L via `startswith`, and P also satisfies it.
- Fix direction: as F4.

**F6. Closed fd 1 turns output failure into exit 0 with no output (contract: output failure → 2).**
- Repro: child started with fd 1 closed (`preexec_fn=os.close(1)`).
- Observed (case H): clean report → rc=0, stdout empty, stderr empty. Failing report (case b) → rc=1, stdout empty, so the summary line is lost. With fd 1 open the same failing report prints `summary … status=failed`.
- Mechanism: with `sys.stdout` None, `print(..., flush=True)` (909–910) silently does nothing. `except OSError` (915) never runs, and `return status` is used.
- Verdict is correct in both cases. The defect is the exit code and the silent loss of output. Severity is therefore Medium, though the contract violation is clear.
- Fix direction: check that stdout is usable (`sys.stdout is None` or fstat fd 1) and return 2 before computing. Or write through a handle whose write result is checked.

### Medium — exit 1 where the contract requires 2

**P1. A decimal integer over 4300 digits escapes `main()` as ValueError (exit 1), at four sites.**
- `--rounds 1000…(5000)` → rc=1, `ValueError: Exceeds the limit (4300 digits)` (parse_rounds 407; also 412, 414). Operator-supplied input.
- Errata row whose round field has 5001 digits → rc=1 (parse_errata 359). Contract: malformed ledger → 2.
- Lane commit with a 5000-digit author date → rc=1 (round_commits 196). Data-driven, reachable from repository content.
- Fleet report path `.ufo/reports/round-<5000 digits>/kama.md` under `--rounds 10-` → rc=1 (parse_rounds 423). Created with `update-index --cacheinfo`; the filesystem cannot hold it, but plumbing accepts it.
- Same class, not run: `report_cutoff` `int(out[-1])` (203) for a fleet report commit with an absurd author date [INFERENCE].

**P2. MemoryError escapes as exit 1 for an oversized round range (contract: 2).**
- `--rounds 1-30000000` under `RLIMIT_AS` = 1 GiB → rc=1, stderr `MemoryError`, from `rounds.update(range(lo, hi + 1))` (417). Without a limit the process may be OOM-killed (exit 137) [INFERENCE, not run].

**P3. UnicodeEncodeError escapes from `print(render(doc))` (exit 1, contract: output failure → 2).**
- Precondition: stdout encoding is ASCII (`PYTHONIOENCODING=ascii`) and an errata row carries non-ASCII text (`errata-invalid` correction `é`). Observed: rc=1, `UnicodeEncodeError: 'ascii' codec can't encode character '\xe9'`.
- Verdict was 1 here anyway (the invalid errata row), so the exit path is wrong, not the verdict. Stderr is safe: `could-not-evaluate` with a non-ASCII path, ASCII stderr → rc=2 (case c21). CPython uses backslashreplace on stderr.

**X1. A corrupt loose object is reported as missing with rc 0, so it becomes a defect (exit 1, expected 2).**
- Observed (case F): `git cat-file --batch-check` gives rc=0, stdout `b54632…834 missing`, stderr `error: inflate: data stream error (incorrect header check)`. Audit rc=1, `defects=[('unresolved-full-hash', …)]`.
- Mechanism: `git()` checks only the return code (120–121). `lookup` treats `missing` as absence (151).
- Corrupt packs take the same path [INFERENCE, not run].
- Fix direction: treat any `error:` or `fatal:` on stderr from `cat-file` as EvalError, or verify with `git cat-file -e` plus an fsck-style check.

**X2. A dangling symlink or a directory at the committed report path gives exit 1 (expected 2).**
- Symlink to `../round-9/kama.md`: rc=1, `defects=3`, `uncorrected=3`. Directory with `kama.md/index.txt`: rc=1, `defects=3`. These are the same mechanism as F3.

**X3. Non-UTF-8 bytes in `git log` output are accepted and produce a computed verdict (exit 1, contract: 2).**
- Repro: round-10 commit by `kama-shokunin` with raw subject bytes `round-10: caf\xe9 raw latin1`, written with `hash-object --literally`. `git log` returns the raw bytes.
- Observed (`grid-part5-raw-utf8.txt`): rc=1, `round_commits=3`, stderr empty. Expected 2.
- Mechanism: `round_commits` decodes with `errors="surrogateescape"` (line 183). `ls-tree` in `parse_rounds` (lines 420–421) does the same. The docstring says non-UTF-8 git output → 2.
- Note: `git commit -F` with latin-1 bytes stores the subject as UTF-8 (observed `caf\xc3\xa9`). Only raw objects reach this path.

### Design-level (exit 0 by a documented rule; decision needed)

**D1. An unverified 7-digit prefix satisfies `landed-omitted` (exit 0, expected 1 under "errors are never verdicts").**
- Control without the digit token: rc=1. With a digit-only 7-hex prefix of an omitted commit (case C): rc=0.
- Mechanism: `checkable_abbrev` (174–177) skips tokens with no a–f letter. `cited = set(ABBREV.findall(section))` (326) keeps them, and the `startswith` at 336 accepts them.
- The docstring says "not cited … by a >=7-hex prefix", so this follows the stated rule. It is a decision for the owner: verify every Landed token that could satisfy an omission, or treat an unverifiable sole candidate as could-not-evaluate.

### Low

**L1. Selftest coverage gap.** Selftest is 50/50 (`v2_selftest.out`, rc 0). Grep finds no case for shallow, grafts, promisor/partial, ref-named citations, symlink or directory at the HEAD report path, union ambiguity, integer overflow, closed stdout, or ASCII stdout. `irregular-report-is-error` (870) covers only the `--report` override.

**L2. Dead branch.** `lookup` treats `excluded` and `dangling` lines (157–158) as missing, which would make them exit-1 defects. Not reachable with the argv used (no `--filter`, no `--follow-symlinks`). [INFERENCE from git option semantics, not run.]

**L3. Selftest exceptions.** `return selftest()` (907) sits inside the same try. An unexpected exception there exits 1 [INFERENCE, not run].

## Confirmed correct (negative results)

- Shallow lane → 2 (case c14). Promisor clone → 2 (c15). `info/grafts` → 2 (c16). Lane path under another repository → 2 (c17). Branch named like a 7-hex prefix → 2 (c13). Symlink-loop lane path → 2 (k00). Non-ASCII stderr → 2 (c21). `/dev/full` stdout → 2 (I). Broken pipe → 2 (`bp_v2`).
- Textconv: `git show HEAD:path` (plain) does not run a configured `diff.<driver>.textconv` on git 2.56.0. `git show --textconv` does run it. The audit must not add that flag.
- Controls: baseline clean → 0; plain omitted round commit → 1; present blob cited → 0.

## Not verified

- Other repository-local channels: `log.diffMerges`, `diff.renames`, `core.fsmonitor`, hooks, `info/attributes`, alternates to partial repositories, LFS pointers. The docstring disclaims them.
- Corrupt packs (only loose objects tested). Non-sha1 repository. Empty round selection (code reading only). `report_cutoff` overflow. OOM kill (137).
- Other Python or git versions. The docstring floor `git >= 2.45` was not tested.
- Frozen-oracle comparison and the repository's own `tests/report-audit/` harness were not run.
- Race conditions (fleet HEAD moving between reads).
- Errata override semantics (any commit can correct any token of the same kind) were noted, not analysed.

## Fix directions (not applied)

1. `main()`: map every non-EvalError exception to 2, or narrow to ValueError, MemoryError, UnicodeError and RuntimeError. Check stdout is usable before computing.
2. Reject over-width integers before `int()`: rounds, errata round, author and committer timestamps, fleet path round.
3. `round_commits()`: NUL-delimited fields. Reject records whose name or subject contains SEP or END.
4. `audit_round()`: verify that the HEAD tree entry for the report is a regular blob.
5. `lookup()`: union of distinct full object ids per token across repositories. Ambiguous when more than one. Keep per-repository ambiguity. Treat any stderr `error:` from `cat-file` as EvalError.
6. Decide D1. Add one selftest per case above; each is a single fixture in this tree.

## Reproduction

Copy `out/CloseKama22.RevExitContract/report-landing-audit.v2-under-review.py` to `/tmp/revexit/rla_v2.py` and `drv_v2.py` to `/tmp/revexit/drv_v2.py`, then run `drv_v2.py`, `drv2_v2.py`, `drv3_v2.py`, `bp_v2.py` and `drv4_v2.py` (about 5 s total). Their captured outputs are in the same `out/` directory.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/advice/RevExitContract.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/build/out/CloseKama22.RevExitContract/`:
  - drivers: `drv_v2.py`, `drv2_v2.py`, `drv3_v2.py`, `drv4_v2.py`, `bp_v2.py`
  - outputs: `grid-part1-core.txt`, `grid-part2-confirm.txt`, `grid-part3-edge.txt`, `grid-part3-edge-say-lines.txt`, `grid-part4-brokenpipe.txt`, `grid-part5-raw-utf8.txt`, `grid-case-stdout-stderr.log`, `v2_selftest.out`
  - copy of the reviewed script: `report-landing-audit.v2-under-review.py` (sha256 `684764…`)
- Scratch only, not deliverables: `/tmp/revexit/` (`rla.py` sha `79d9…`, `rla_v2.py`, `drv*.py`, `bp*.py`, `cases/`, `v2cases/`, `home/`).
