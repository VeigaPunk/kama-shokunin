# S1Rel — SOURCES row S482 for release b11889

**Verdict: PASS for the row itself — schema-clean under the frozen census (NF=13, 11 cells, zero new validator finding); one integration condition stands: the row's `used-by` target `registry/release-recheck-b11889.tsv` does not exist in the lane yet, so the frozen counter emits `E11` for S482 until the C1 ledger lands. Tag identity and publication time are confirmed from two independent surfaces.**

Axis: freshness. Object: which commit release b11889 names and when it was published.

## 1. Release object fetched (one GitHub API request)

```
$ gh api repos/ggml-org/llama.cpp/releases/tags/b11889 > .../out/S1Rel/release-b11889.json
gh_exit=0 ; wc -c = 69393
sha256 = 7443531d00d3edb9cb05ef0fd51a30bfb3994d743a724a0f5450559774939c15
```

Fields read from the saved JSON (`jq`):

| field | value |
|---|---|
| `name` / `tag_name` | b11889 / b11889 |
| `target_commitish` | d854d98bae598388ecea1ed84396587e5edc326d |
| `published_at` | 2026-10-25T23:44:54Z |
| `created_at` | 2026-10-25T23:08:22Z |
| `prerelease` / `draft` | true / false |
| `id` | 423733270 |
| `assets` | 36 entries |

## 2. Tag resolves to the same commit (second surface)

```
$ git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11889 refs/tags/b11889^{}
d854d98bae598388ecea1ed84396587e5edc326d	refs/tags/b11889
exit=0
```

One line only, no `^{}` peeled ref. The shared clone confirms the object is a commit:

```
$ git -C /fast/scratch/hyaku/kama-r44/shared/llama.cpp cat-file -t d854d98bae598388ecea1ed84396587e5edc326d
commit        (exit 0)
$ git -C ... rev-parse d854d98b...
d854d98bae598388ecea1ed84396587e5edc326d
```

So `target_commitish` in the release object and the tag ref are the same commit id; the two surfaces agree.

## 3. Row S482 (draft, full text in `row.md`)

11 cells, no `|` inside any cell, inserted after S481 (`corpus/SOURCES.md:234`, last registry row; `## Registry` opens at `:9`):

| S482 | llama.cpp release b11889 — https://github.com/ggml-org/llama.cpp/releases/tag/b11889 | docs | A | which commit release b11889 names and when it was published | `tag_name` b11889, `target_commitish` d854d98bae598388ecea1ed84396587e5edc326d, `published_at` 2026-10-25T23:44:54Z, `prerelease` true; release JSON fetched 2026-10-26 with `gh api repos/ggml-org/llama.cpp/releases/tags/b11889`, 69393 bytes, SHA-256 7443531d00d3edb9cb05ef0fd51a30bfb3994d743a724a0f5450559774939c15, copy `.ufo/waves/round-44/w1/out/S1Rel/release-b11889.json`; `git ls-remote --tags https://github.com/ggml-org/llama.cpp.git refs/tags/b11889` printed d854d98bae598388ecea1ed84396587e5edc326d refs/tags/b11889 | Release b11889's `target_commitish` names commit d854d98bae598388ecea1ed84396587e5edc326d, the same id that tag ref `b11889` resolves to, and the release was published at 2026-10-25T23:44:54Z as a prerelease | mined | 2026-10-26 | on-release | registry/release-recheck-b11889.tsv |

Gate line (lesson text, also in `row.md`): URL, accessed 2026-10-26, quote located in field `target_commitish` — "d854d98bae598388ecea1ed84396587e5edc326d" (1 word) — and quote located in field `published_at` — "2026-10-25T23:44:54Z" (1 word). Both are exact substrings of the saved JSON.

Id space: `grep -n 'S482' corpus/SOURCES.md` → exit 1 (free); highest registry id is S481; `grep -n b11889 corpus/SOURCES.md` → exit 1 (no prior row for this release).

## 4. Validation (frozen counter)

Scratch mirror: `val/` is a directory of symlinks to every lane top-level entry, with `val/corpus/` a real directory of symlinks to lane `corpus/*` plus a modified `SOURCES.md` (row inserted at line 235). `--file` resolves used-by against the parent of `corpus/`, so the mirror reproduces the lane's real path graph without writing the lane.

```
$ scripts/sources-census.sh validate --file $S/val/corpus/SOURCES.md --today 2026-10-26
file  W04  S031 duplicate url docs.ollama.com/api/tags across scopes
... 92 W04 lines + 1 W01 (S481, pre-existing) ...
file  E11  S482 missing used-by registry/release-recheck-b11889.tsv
EXIT_row_noledger=1
```

```
$ scripts/sources-census.sh validate --file $S/val-reg/corpus/SOURCES.md --today 2026-10-26
(same 94 lines, no S482 line)
file  ok  .../val-reg/corpus/SOURCES.md
EXIT_row_ledger_present=0
```

`val-reg/registry/` is a real directory mirroring lane `registry/*` plus a header-only placeholder at the used-by path; the diff between the two outputs is exactly the S482 `E11` line and the `ok` line. No `E01`–`E10`, no `E12`, no new `W` code: the row parses and is admitted.

Counts (census mode): `rows 223` vs baseline `222`, `tier.A 212` vs `211`, `status.mined 204` vs `203`, `tier.invalid 0`, `status.invalid 0`; exit 0 both.

## 5. Findings

**F1 — S482's used-by path does not exist yet (integration condition, not a row defect).**
`corpus/SOURCES.md` has no `registry/release-recheck-b11889.tsv` (`ls` → exit 2; `registry/` listing has 13 entries, none of them that ledger). The frozen counter's used-by leg (`scripts/sources-census.sh:538` `usedby_findings`, called at `:721` in validate mode; semantics `:29`) reports `E11 S482 missing used-by registry/release-recheck-b11889.tsv` and exits 1. Reproduce: `scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md --today 2026-10-26`. Proposed fix (L1, not done here): land the C1 ledger at `registry/release-recheck-b11889.tsv` in the same commit as S482 — the `val-reg` run above shows the row then validates `ok` with exit 0. Ordering matters: drafting the row before the ledger can never validate clean.

**F2 — self-disclosed stray write, already reverted.** My first mirror variant symlinked `registry/` into the lane, and writing the placeholder through that symlink created `/home/vgpnk/Projects/shokunin/kama-shokunin/registry/release-recheck-b11889.tsv` (94 bytes, header only, mtime 04:56). Detected immediately; `rm -f` → exit 0, re-`ls` → exit 2. The lane file is absent again and no other lane path was written; the only lane-tree change is that create-then-delete. The mirror was rebuilt with a real `registry/` directory afterwards.

## 6. Limits

- One `gh api` request only; no release-page HTML fetch, no tag-object API call. The claim tested is "the ref id is the commit the release names", not annotated-vs-lightweight tag type (the absence of a `^{}` line in `ls-remote` is consistent with a lightweight tag, `[INFERENCE]`).
- `published_at` is asserted only for the fetched bytes; no stability claim across later fetches.
- `--today 2026-10-26` equals the host date, so the default would behave identically.
- The mirror validation tests the frozen counter's row parsing and used-by leg; it does not exercise the fleet roster path.
- No tools installed or upgraded; no pacman; scratch removed after receipts were copied.

## 7. Touched surfaces

- Wrote only: `.ufo/waves/round-44/w1/out/S1Rel/` (this report, `row.md`, `release-b11889.json`, two validate outputs, `scratch-SOURCES-with-S482.md`).
- Lane tree: no edits. `corpus/SOURCES.md` unchanged (`S482` absent from the lane file, grep exit 1).
- Scratch `/fast/scratch/hyaku/kama-r44/S1Rel/` removed at the end.
