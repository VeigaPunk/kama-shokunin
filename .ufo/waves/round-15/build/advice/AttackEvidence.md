# AttackEvidence — does the copied baseline have true git blob correspondence?

Scope: compare `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py` and `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/manifest.json` against the git history of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/measure.py`. Review was read-only. This report is the only file written.

## Verdict

- **Blob correspondence: true.** The frozen bytes form git blob `783004569af9072afdeb32c6eeacc462868eb76b`. That is the same object as `.ufo/waves/round-14/measure.py` at the round-14 measured commit `e545ed99…`, at `06cc6dbe…`, and at the manifest's `6e348e28…`.
- **Nothing in round 15 pins or enforces that.** No round-15 artifact records the blob OID. The manifest only attests to itself. `check.py` reports `runner_sha256` but never compares it to anything (CE2).
- **Same blob does not mean same behaviour at the new path (CE1).** It also does not mean the same tree entry, because the file mode differs (CE3).

## Axes

| Axis | State |
|---|---|
| A1 frozen bytes = immutable git object | holds |
| A2 tree-entry identity (mode) | differs: source `100755`, copy `0644` |
| A3 execution equivalence at the copy's path | holds only with explicit `--tool` and `--cases` |
| A4 authority of the correspondence claim | observed, not pinned; the manifest only vouches for itself |
| A5 durability of correspondence claims | one sibling claim is already stale |

## Evidence

I ran these commands in `/home/vgpnk/Projects/shokunin/kama-shokunin`. All are read-only: no `-w`, no `git status`, no index refresh.

- **HEAD and ancestry.** `git log -n 12` shows HEAD `6e348e28943849aceb08d6954dee92be48ce9ba8`, committed 03:51:25-03:00. `git rev-list --parents -n 3 6e348e28…` gives the chain `6e348e28 → 06cc6dbe → e545ed99 → e1b3d746`.
- **History of the runner.** `git log -- .ufo/waves/round-14/measure.py` lists only `e545ed99aaa519196a2a7779b0a293b2ce4c765c`.
- **Blob at each commit.** `git --no-replace-objects rev-parse <c>:.ufo/waves/round-14/measure.py` for `e545ed99`, `6e348e28` and `06cc6dbe` returns `783004569af9…` each time.
- **Tree entry.** `git ls-tree 6e348e28 -- .ufo/waves/round-14/measure.py` returns `100755 blob 783004569af9…`.
- **Hash of the frozen and live files.**
  - `git hash-object --no-filters` on the frozen copy gives `783004569af9…`.
  - The live `.ufo/waves/round-14/measure.py` now gives `14e236efe9d5212f4bbf550d3f1ac2829e9ca0d9`.
- **Hash with attribute filters.** `git hash-object --path=<frozen> <frozen>` also gives `783004569af9…`, so `git add` will store the same object.
  - I found no `.gitattributes` in the lane.
  - The global `filter.lfs.*` does nothing without attributes.
- **Object store.**
  - `git replace -l` returns nothing.
  - These files do not exist: `.git/objects/info/alternates`, `.git/info/grafts`, `.git/shallow`.
- **Index.** `git ls-files -s` still shows `100755 783004569af9…` for the live runner, so the repair is unstaged. Both frozen files are absent from the index.
- **Config.** `core.filemode true` in the lane's `.git/config`.
- **Checksums.**
  - Frozen copy: `fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`, which matches `manifest.json:4`.
  - Live runner: `46c5866d73a4f875353ff59c6929615149a1f4f4acf69b0b07deeb99d5445257`.
- **File metadata (`stat`).**

  | File | Type / links | Inode | Mode | Bytes | mtime |
  |---|---|---|---|---|---|
  | Frozen copy | regular, nlink 1 | 43201523 | 0644 | 17134 | 05:01:37.312047080 |
  | `manifest.json` | — | — | — | — | 05:01:37.312105190 (58 µs later) |
  | Live runner | — | 43190131 | 0755 | 17214 | 05:09:13.962874723 |

- **Diff.** `diff -u <frozen> <live>` shows only `if len(declared) != unique: problems.append("duplicate case names")`, at live `:358-359`.
- **Parent repo.**
  - `git -C /home/vgpnk/Projects/shokunin cat-file -t 6e348e28…` fails with `could not get object info`.
  - `/home/vgpnk/Projects/shokunin/.gitignore:1` (`*-shokunin/`) ignores the runner path.
  - So `source_commit` only resolves inside the lane repo.

## Counterexamples

### CE1 — same blob, different verdict (A3)

- In `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py:55-58`, `LANE` is `Path(__file__).resolve().parent.parents[2]`. `DEFAULT_TOOL` and `DEFAULT_CASES` are built from `LANE`.
  - Under `.ufo/waves/round-14/`, `parents[2]` is the lane root.
  - Under `.ufo/waves/round-15/frozen/`, `parents[2]` is `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo`. A directory listing shows no `tools/` or `tests/` there.
- The falsifier is a committed receipt: the `final_corpus` record in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/acceptance.json:1831-1840`.
  - argv: `/usr/bin/python -I -B <runner>`, with no flags; cwd is the lane.
  - Result: exit 0, `tool` `…/kama-shokunin/tools/kama-ollama-evidence.py`, 51 of 51 passed.
- Now run the same argv with `<runner>` set to the frozen copy. From `:109-113`, `:426-455` and `:486-491`, I predict:
  - exit 1 and `records: []`;
  - `tool` `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/tools/kama-ollama-evidence.py`, `tool_present: false`;
  - `error` `cannot read cases /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/tests/ollama-evidence/cases.json: [Errno 2] …`.
- Variant: pass `--cases` but not `--tool`. Per `:370-391`, every record becomes `tool absent` / `unsupported`, for valid and duplicate corpora alike. The run exits 1, spawns zero children, and sets no `error`.
  - This is the same shape as the round-14 `capability_absent` control (`acceptance.json:6-17`).
  - So "exit 1 and zero children" cannot by itself attribute a rejection to the duplicate guard.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-corpus-guard/check.py` is not affected as read:
  - `:352-361` always passes `--tool <wrapper> --cases <temp cases>`.
  - The rejected predicate also requires `tool_present` true (`:538-542`).
- CE1 does apply to any 51-case "retain valid unique corpus" or before/after comparison that replays round-14 argv against the frozen path. ReceiptReview.md F1 already found the `parents[2]` shift. What is new here is that a committed receipt is the falsifier.

### CE2 — correspondence is asserted, not enforced (A4)

- **Missing fields.** `manifest.json:1-5` has only `source_commit`, `source_path` and `sha256`. It is missing:
  - the blob OID and byte count;
  - the snapshot path and the repo identity;
  - the copy method;
  - whether `sha256` hashes the snapshot or the source.
- **Convention regression.** It also drops the fields the round-14 frozen manifests carried: `artifact`, `source_kind`, `capture_time` and `limits` (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/frozen/precedence-before-manifest.json:2-7`).
- **Wrong commit named.** `source_commit` is the HEAD at freeze time (`6e348e28`), a verifier spot-check commit that does not touch the runner. Round 14 says it measured `e545ed99…` (`acceptance.json:2`, `measured_commit`). The bytes agree only because the blob did not change along the chain.
- **Self-attestation.** One writer produced the copy and the manifest 58 µs apart.
- **No enforcement in `check.py`.** It emits `runner_sha256` (`check.py:628-629`) but compares it to nothing. `--runner` accepts any existing file (`:694-696`).
- **Counterexample: coherent mutation.**
  1. Edit the frozen runner, for example by adding the two-line predicate.
  2. Rewrite `manifest.json` `sha256` to match.
  3. `sha256(frozen) == manifest.sha256` still holds, and `source_commit` / `source_path` still name real objects.
  4. `check.py --runner <frozen>` now grades the duplicate controls green, so there is no red-before.
  5. Nothing in round 15 fails closed until someone compares against the git object. The frozen files are not in the index, so git shows no diff either.
- **This failure has a precedent.** It is the round-11 D1 class. Round 12 closed it with code constants in `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-12/fidelity.py`:
  - `:45-49` define `SOURCE_REVISION`, `SOURCE_PATH`, `SOURCE_BLOB_OID`, `SOURCE_SHA256` and `SOURCE_BYTES`;
  - `:261-286` read the blob raw with `cat-file`.

### CE3 — blob equal, tree entry not (A2)

- The source tree entry is `100755`; the copy is `0644`.
- With `core.filemode true`, the copy will commit as `100644 blob 783004569af9…`.
- Running the copy directly (`./measure-before.py`) fails with EACCES, while the historical file runs.
- This does not affect `check.py`, which uses `runpy.run_path` under `sys.executable -I -B` (`check.py:257-273,352-356`).
- Do not `chmod` the copy. Nothing needs it, and it would change a frozen artifact.

### CE4 — stale correspondence claims (A5)

- **CaseAudit09.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/advice/CaseAudit09.md:15-17` says the frozen copy is "byte-identical to the current `.ufo/waves/round-14/measure.py`".
  - That has been false since 05:09:13: the live OID is now `14e236ef…`.
  - It holds only as a pre-edit observation. Identity with the live file must never be cited as blob correspondence.
- **GateDecisions.** `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/build/advice/GateDecisions.md:69` says four round-14 files "record hashes of `measure.py`": `sources-final-census.json`, `sources-final-validate.json`, `validation.json` and `integration-review.json`.
  - A grep of `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-14/*.json` for `fda61e001ca8|783004569af9|measure\.py` matches only `acceptance.json`, `dispatch.json`, `spawn-result.json` and `spec.json`.
  - No round-14 receipt pins the runner's bytes.

## Limitation on historical fidelity (not a counterexample)

Round-14 receipts identify the runner only by its path and by `measured_commit` `e545ed99`.

- `recorded_at` is `06:38:39.98Z` (`acceptance.json:3`). That is 27.98 s after `e545ed99`'s committer time (`03:38:12-03:00`). No dirty-tree flag is recorded.
- All four runner invocations (`acceptance.json:11,971,1836,3194`) used the default corpus of 51 unique names.
- On that corpus the frozen and repaired runners produce identical stdout, because the new predicate is false when `len(declared) == unique`. So the receipts cannot tell the runner versions apart.
- The claim "the measured runner had the R1 gap" therefore rests on `measured_commit` → blob `783004569af9…`. It assumes the tree was clean at measurement time. That is consistent with the evidence but cannot be proven from the receipts [INFERENCE].

## Smallest safe correction

None of this requires editing the frozen bytes, old receipts, or `check.py`.

1. **Keep `measure-before.py` byte-frozen.** Any path "fix" (for example `parents[2]` → `parents[3]`) or a re-copy would destroy the blob correspondence. The judge must reject such an edit.
2. **Pin the source in the round-15 record / R2 append.** Use constants, not values read from `manifest.json`:
   - `measured_commit e545ed99aaa519196a2a7779b0a293b2ce4c765c`
   - `source_path .ufo/waves/round-14/measure.py`
   - `source_blob_oid 783004569af9072afdeb32c6eeacc462868eb76b`
   - `sha256 fda61e001ca8c2533c99a1759bb4b82f3260a72fafccf72f863f3f4e3684b60d`
   - `bytes 17134`
   - source mode `100755`, snapshot mode `100644`

   Require the before-run `check.py` document's `runner_sha256` to equal that sha256. Treat any other value as could-not-evaluate, never as red.
3. **Valid unique-corpus retention.** Compare the repaired runner against the immutable `final_corpus` record in `acceptance.json`: exit 0, 51 of 51, `tool_sha256 38d1f5d2…`, `cases_sha256 4a4de0b8…`.
   - If the frozen runner is re-run, pass `--tool /home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-ollama-evidence.py --cases /home/vgpnk/Projects/shokunin/kama-shokunin/tests/ollama-evidence/cases.json`.
   - Never run it on its defaults.
4. **Red-before needs positive child evidence from the frozen run.** For every invalid control, cite from that run's record:
   - `observed.classifier_invocations == len(names)`
   - `observed.runner_popen_events == len(names)`
   - `observed.tool_present == true`

   `check.py`'s overall exit 1 is not enough, because any failure mode produces it.

## Falsifiers for L1 (run once, after edits)

```
git -C /home/vgpnk/Projects/shokunin/kama-shokunin --no-replace-objects cat-file blob e545ed99aaa519196a2a7779b0a293b2ce4c765c:.ufo/waves/round-14/measure.py | cmp - /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-15/frozen/measure-before.py
git -C /home/vgpnk/Projects/shokunin/kama-shokunin hash-object --no-filters .ufo/waves/round-15/frozen/measure-before.py   # expect 783004569af9072afdeb32c6eeacc462868eb76b
# after the round-15 commit:
git -C /home/vgpnk/Projects/shokunin/kama-shokunin ls-tree HEAD -- .ufo/waves/round-15/frozen/measure-before.py           # expect 100644 blob 783004569af9072afdeb32c6eeacc462868eb76b
```

CE1 is refuted if the frozen copy, run with the `final_corpus` argv from cwd `/home/vgpnk/Projects/shokunin/kama-shokunin`, exits 0 with 51 of 51. The prediction is exit 1 with the `.ufo/tests/…` read error.

## Limitations

- I used only read-only git plumbing, `sha256sum`, `stat`, `diff` and `ls`. I did not execute `measure-before.py`, `measure.py` or `check.py`. The runtime outcomes for CE1 and CE2 are derived from source.
- `measure.py` and `check.py` were being edited while I read them. Line numbers are as read: `check.py` had 720 lines, and the live runner's sha256 was `46c5866d…`.
- The copy method (from the git object or from the working tree) is not recorded.
  - Mode 0644 and the 58 µs gap suggest the bytes were written in-process rather than with `cp` [INFERENCE].
  - Either source gives the same bytes here: the index blob is unchanged, and CaseAudit09 saw `cmp` equality before the edit.
- No tools were installed or updated; no pacman, uv or npm actions were taken.

Report: .ufo/waves/round-15/build/advice/AttackEvidence.md
