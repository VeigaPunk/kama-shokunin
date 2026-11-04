# SC01Lesson — round-82 lesson scribe report

Seat: `SC01Lesson` (scribe). Deliverable: a full draft of `corpus/lessons/round-82.md` at the seat path
for the L1 to file. No production file was edited; the lane is read-only from this seat.

## Behavior

Drafted `round-82.md` with the four assigned sections in order:

1. `## Gate` — one row per source candidate, all five URLs opened by this seat on 2026-11-04:
   (a) llama.cpp `tools/server/README.md` at `b12103` (HTTP 200, 136429 bytes, sha256 `eafc1b53…a137`),
   (b) the same file at the lane pin `b11755` (200, 119661, `714c067b…6a37`), (c) SGLang
   `docs/docs/basic_usage/native_api.mdx` at `v0.5.23` (200, 18295, `3ed17118…7a3c`), (d) the llama.cpp
   `b12103` release page as the required reject (200, 174444, `bf125a51…c3e2`), and (e) the already-filed
   SGLang `README.md` reject `S565` re-opened for byte agreement (200, 9472, `a7654a48…303c`). Each row
   carries access date, status, bytes, full sha256, line-located ≤25-word quote, verdict, reason and flip.
   The section states that the llama.cpp anchored sentence survived byte-identically and moved one line
   (481 → 482) across the release gap (15 hunks, 2402 → 2620 lines), and that the SGLang gap is two hunks
   (`/ready` and `/ping` added at lines 111-112; `/get_model_info` unchanged; `/model_info` still absent).
   Five locators that answered HTTP 404 are recorded and refused rather than written as rows.
2. `## Corrections` — the five `corrected F<n> …` lines byte-identical to `plans/round-82-claims.md`
   (verified by script, see below), one prose paragraph per fact naming record location, declared value
   and receipt value, and the F6 paragraph stating it holds and is not corrected.
3. `## Mistakes` — one row, class `register-introduction-conflated`, evidence the red-before receipt plus
   the round-81 plan §C2 / sealed module docstring promise, captured-by `none`, fix the row-level
   `git blame` resolution plus three selftest arms; two short paragraphs record the promise verbatim and
   the red-capability check.
4. `## Freeze divergences` — the three named items only: the unbound `--late` path, the retained
   `registry/append-only-late-r82.tsv`, and the `pending` convention.

The draft is at:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/round-82.md`
sha256 `5f2f82bce2b9bb30d53a850f939ee86699741aa02d011302d55957baafbf5f4e`, 14916 bytes.

## Gates measured on the draft

The C1 counter was run over the draft bytes in a scratch clone of the lane (the only way to feed the
counter tip bytes, since it reads `corpus/lessons/round-82.md` with `git show <tip>:<path>`):

- command: `python3 tools/round82-selfrecord-round81.py --repo . --tip master`
- repo: `/fast/scratch/hyaku/kama-r82/SC01Lesson/clone`, lane tip `384ef1d5bcbf737183571398ecb0955ea5074609`,
  draft committed as `4fb438b1732dc4d3c797b831340a0e64cc4a1d50`
- output: `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`, **EXIT=0**
- receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/c1-draft-check.txt`

Correction-block byte equality with the frozen plan was checked separately:
`byte-identical block: True` (5 lines), extracted from `plans/round-82-claims.md` and the draft.

The lane's C2 receipts were read, not rerun: leg 1
`.ufo/waves/round-82/measured/after/c2-late-delta.out` prints `LATE_DELTA round=82 base=aaf974dbd3b6
population=103 carried=88 new=15 bad=0` EXIT=0; leg 2 `.ufo/waves/round-82/measured/after/c2-debt.out`
prints `APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=2 unaccepted=0
bad_rows=0 bad_declarations=0 out_of_population=0` EXIT=0.

## Touch surfaces

Wrote only inside `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/`:

| file | bytes | sha256 |
|---|---|---|
| `round-82.md` | 14916 | `5f2f82bce2b9bb30d53a850f939ee86699741aa02d011302d55957baafbf5f4e` |
| `fetch-receipts.txt` | 1883 | `56d77da2f0dc5938a6f97ab1048b20c0b1f6fd773ad95f057529d39afdc8faa5` |
| `no-corr-rerun.out` | 809 | (control rerun, see finding 1) |
| `oldres-selftest.out` | 1445 | `bdf7c1d48f148db98e088bbc2325e494d5c5d04079c5ccf06c181337db727555` |
| `c1-draft-check.txt` | 809 | (draft validation, see Gates) |

No tracked lane file was modified by this seat (`git -C /home/vgpnk/Projects/shokunin/kama-shokunin
status --porcelain` shows only `?? .ufo/waves/round-82/w1/SC01Lesson/` for this seat; the tracked
`D .ufo/waves/round-82/w1.ready.partial` and the other untracked `w1/*` seat dirs predate this seat's
first write at 10:11 and are not mine). Scratch `$S=/fast/scratch/hyaku/kama-r82/SC01Lesson` was deleted
after the receipts were copied into the seat dir; only the clone's git objects existed there.

The draft was written to the seat path only. The lane already carries a filed
`corpus/lessons/round-82.md` (commits `962bd251`, `a251cbab`) from the L1's earlier composition; this
seat did not touch it. The L1 decides whether to replace or reconcile it with this draft.

## Findings

1. **The no-corrections control receipt records the wrong exit code.** Stored
   `.ufo/waves/round-82/measured/control/c1-no-corrections.out` ends:

   ```
   SELFRECORD_R81 claims=6 mismatches=5 corrected=0 unbacked=0
   EXIT=0
   ```

   The plan's control 2 requires exit 1, and the counter at the receipt's own revision
   (`a251cbab`, `main()` tail: `return 0 if mismatches == 0 else 1`) returns 1 for `mismatches=5`.
   Re-running the command against the lane at tip `384ef1d5` prints the same counter line and
   `EXIT=1` (receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/no-corr-rerun.out`,
   command `python3 tools/round82-selfrecord-round81.py --repo . --no-corrections`). The stored receipt's
   `EXIT` line is a capture artifact (likely `$?` after a pipe), not the tool's exit; the receipt should be
   regenerated so the control is red in the evidence, not only in behaviour.

2. **Red-capability of `row-intro-later` is demonstrated, not just asserted.** On a scratch copy of
   `tools/round81-append-debt.py` the selftest harness call was changed to `row_intro=None` (the old
   register-level resolution, which uses the fixture's single register introduction `9…9` for every row).
   `python3 append-debt-oldres.py --selftest` prints
   `APPEND_DEBT_SELFTEST_FAIL row-intro-later exit=1 want=0 … row-introduction commit 9999… is not a
   strict descendant of event commit bbbb…` and `APPEND_DEBT_SELFTEST pass=23 fail=2` (EXIT=1). The second
   failing arm is `row-intro-unbound` (the old resolution never reports an unresolvable row); the
   load-bearing arm named in the lesson is `row-intro-later`. Receipt:
   `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/oldres-selftest.out`,
   command `python3 ./append-debt-oldres.py --selftest`, EXIT=1. The repaired module's own green receipt
   is `.ufo/waves/round-82/measured/after/c2-debt-selftest.out` → `APPEND_DEBT_SELFTEST pass=25 fail=0`,
   EXIT=0.

3. **SGLang knowledge delta at the newest tag.** `docs/docs/basic_usage/native_api.mdx` at `v0.5.23`
   still lists `/get_model_info` (line 9) and never names `/model_info`, so `S328`'s deprecation claim
   holds across `v0.5.22 → v0.5.23`; but the health surface moved — `/ready` and `/ping` are added at
   lines 111-112 with pause-sensitive semantics. If the L1 files Gate row (c), the held health-surface
   knowledge (S006: "`/health` and one-token `/health_generate` are separate checks") is now a four-route
   surface and should be stated as such rather than left at two routes.

4. **Source ids for rows (c) and (d) are not assigned.** `corpus/SOURCES.md` had `S565` as its highest id
   at every read this seat made (`S563`/`S564` are the llama.cpp rows, `S565` the SGLang README reject);
   rows (c) (SGLang native API at `v0.5.23`) and (d) (llama.cpp `b12103` release page) need ids at filing.
   The draft labels them `new` deliberately.

5. **F2's witness is base-bound in the draft.** `LOG.md` §Round 81 says 301; the base `aaf974db` holds 302
   rows; the tip holds 305 after the round's three admitted rows. The draft's F2 paragraph states all three
   and keeps `new=302`, matching the counter's base reading. This is the same divergence the round-82
   freeze records; it is prose in my draft, not a new correction.

6. **Lane tip moved during the seat.** Observed `bacae072` at dispatch read, `4beb4f2b` at the last
   pre-draft read, `384ef1d5` at clone time and at the final read. All receipts name the revision they were
   taken at; nothing in this seat writes to the lane.

## Out of scope (not done)

- `tools/pre-report-gate.py` was not run (the L1 runs it in scored mode).
- No `corpus/SOURCES.md`, `SCORECARD.md`, `LOG.md`, `SKILL.md`, `plans/` or `tools/` edit was made.
- The C2 legs were not rerun; their committed receipts were read. The C1 counter was rerun only for the
  control-receipt finding (finding 1) and to validate the draft in a scratch clone (Gates).
- No tool install or upgrade was needed.

## Receipts (absolute path · command · exit)

Lane receipts read (status as recorded in the file):

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c1-green.out` ·
  `python3 tools/round82-selfrecord-round81.py --repo .` · EXIT=0 · `SELFRECORD_R81 claims=6
  mismatches=0 corrected=5 unbacked=0` (rev `a251cbab`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c1-selftest.out` ·
  `python3 tools/round82-selfrecord-round81.py --selftest` · EXIT=0 · `pass=19 fail=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c2-late-delta.out` ·
  `python3 tools/round82-late-delta.py --repo . --round 82` · EXIT=0 · `population=103 carried=88 new=15
  bad=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c2-debt.out` ·
  `python3 tools/round81-append-debt.py --repo . --round 82` · EXIT=0 · `pending=2 unaccepted=0 bad_rows=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/after/c2-debt-selftest.out` ·
  `python3 tools/round81-append-debt.py --selftest` · EXIT=0 · `pass=25 fail=0` (rev `5fe3c58`)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/before/c1-enum.out` ·
  `python3 tools/round82-selfrecord-round81.py --repo . --enumerate` · EXIT=1 · `claims=6 stale=5
  corrected=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/control/c1-no-corrections.out` ·
  `python3 tools/round82-selfrecord-round81.py --repo . --no-corrections` · recorded EXIT=0, actual EXIT=1
  (finding 1)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/measured/defects/c2-debt-register-level-before.out` ·
  `python3 tools/round81-append-debt.py --repo . --round 82` · EXIT=1 · `unaccepted=5 bad_rows=15` (rev
  `b0064016`)

This seat's receipts:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/c1-draft-check.txt` ·
  `python3 tools/round82-selfrecord-round81.py --repo . --tip master` (scratch clone, tip `384ef1d5`) ·
  EXIT=0 · `SELFRECORD_R81 claims=6 mismatches=0 corrected=5 unbacked=0`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/no-corr-rerun.out` ·
  `python3 tools/round82-selfrecord-round81.py --repo . --no-corrections` (lane, tip `384ef1d5`) ·
  EXIT=1
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/oldres-selftest.out` ·
  `python3 ./append-debt-oldres.py --selftest` (scratch copy, old register-level resolution) · EXIT=1 ·
  `pass=23 fail=2`, `row-intro-later` failed
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC01Lesson/fetch-receipts.txt` ·
  `curl -sS -w '%{http_code} %{size_download}' -o <file> <URL>` per candidate, access date 2026-11-04 ·
  status/bytes/sha256 as tabled
