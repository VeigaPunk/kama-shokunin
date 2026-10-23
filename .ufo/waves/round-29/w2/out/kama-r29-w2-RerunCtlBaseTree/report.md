# RerunCtlBaseTree — re-execution of pre-data control CtlBaseTree (C1 calibration)

Seat `kama-r29-w2-RerunCtlBaseTree`, kama lane round 29 wave 2, 2026-10-23.
Claim served: **C1 (calibration) — pre-data controls**.
Item: re-run CtlBaseTree (check each base statement against the **base tree**
`2aa46e24`, never against its writing revision `W`), score with the frozen
counter, compare with `.ufo/waves/round-29/controls/CtlBaseTree/counter.out`.
Lane repo `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch `master`, HEAD
`513eba3ba51a142c9936553e3a85918345eb5c4c`, read-only for this seat).

## Result

**Reproduced exactly; expected outcome confirmed. No defect found.**

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip 93efe2d45da5
exit=0
```

| artifact | recorded | mine | verdict |
|---|---|---|---|
| `counter.out` (140 B) | sha256 `89c459b0206c10e6178d4fb53ac994250bc791af06ca4a08270dac9512519db1` | same | **byte-identical** |
| `receipt.json` (3979 B) | sha256 `fd9662f4106ca9bfd032319f684407ea580537f99bd502d962b894e646fbe96d` | same | **byte-identical** |
| `change.diff` (1935 B) | sha256 `ac2fccb96e0a62178f36922c03ecb80cbe17a5ff7b9053f05d53a818542b5783` | same | **byte-identical** |
| `base_rows.txt` (617 B) | sha256 `7d52c27ad86616452868391180e507147c2aa9ec88fb3329cbfae646dd626703` | same | **byte-identical** |
| policy commit | `93efe2d45da5ed1f72455f16a97107ee6a151592`, tree `be55ce978a804b5752e599b0a7869ed4cf1442d9`, parent `827d136546b85059a984b34970f5b493d9a71290` | same | **identical** |
| tip `SCORECARD.md` blob | `e98c13c70bcd5a63a7f00b140618761a8b8284d0` (106 061 B = base `24882de8…` 104 553 B + 1508 B append) | same | **identical** |

Frozen counter `.ufo/waves/round-29/count-c1.py` sha256
`fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` verified
**before** the first run and **after** all arms — never modified, never copied
into the scored tree.

## What was executed

1. Fresh clone of the lane (read-only source) to
   `/tmp/kama-r29-w2-RerunCtlBaseTree/repo`; branch `ctl` at freeze commit
   `827d136546b85059a984b34970f5b493d9a71290` (tree `efe74520…`).
2. Copied the recorded policy implementation
   `controls/CtlBaseTree/base_tree_check.py` into `/tmp/.../policy/` — it takes
   the repo path as `argv[1]` and contains no hard-coded clone path — and ran it
   against the fresh clone. It emitted:
   `statements 69 by_class {'H': 2, 'N': 2, 'Q': 25, 'T': 3, 'P': 10, 'C': 27}`,
   `failing_at_base 10`, and 10 `ROW` lines. The output is byte-identical to the
   recorded `base_rows.txt`; its 10 rows are field-for-field identical to the
   recorded `base_failures.jsonl` (every `sid`, `file`, `line`, `class`, `token`,
   `args`, and `observed_at_base` recomputed independently, see below).
3. Composed the `SCORECARD.md` append under the frozen heading from those 10
   rows and the control's own published format. The resulting blob hashes to the
   recorded tip blob `e98c13c7…` — the recorded append is exactly the 10 rows,
   nothing else.
4. Committed in the clone with the recorded metadata (`ctl <ctl@local>`,
   `1792753296 -0300`, message `round-29 C1 control CtlBaseTree: check
   statements against base tree 2aa46e24 and record base-observed values`). The
   commit hash reproduced as `93efe2d45da5ed1f72455f16a97107ee6a151592` —
   identical to the scored tip.
5. Ran the **lane copy** of the frozen counter, unchanged, exactly as the control
   procedure prescribes:
   `/usr/bin/python3 <lane>/.ufo/waves/round-29/count-c1.py --repo <clone> --tip ctl --out <evidence>/receipt.json`.
   Exit 0; counter line and receipt byte-identical to the recorded artifacts.

## Independent recompute at BASE `2aa46e24`

Every base-observed value was recomputed without the policy code, with
`git cat-file blob 2aa46e24:<path>`, `hashlib`, and `git grep` against the base
tree with the counter's exclusions (`SCORECARD.md`, `SHONEN.md`, `LOG.md`,
`corpus/**`):

| base failure | independent base value | row's observed |
|---|---|---|
| `tools/kama-probe.sh` md5 | `e8bfdcac8e0b66d76c1f0173383d0c80` | `md5=e8bfdcac8e0b66d76c1f0173383d0c80` |
| `tools/kama-probe.sh` newlines | 1138 `\n`, last byte `0x22` (unterminated) | `newlines=1138 unterminated=true` |
| `tools/test-snapshot.sh` md5 | `3116d4594d5d5fe259d8815485ea85dc` | `md5=3116d4594d5d5fe259d8815485ea85dc` |
| `SKILL.md` newlines | 1230 `\n`, last byte `0x0a` (terminated) | `newlines=1230 unterminated=false` |
| `MISSION.md` at base | absent | `p:absent` |
| `round-17-verifier-spotcheck.md` at base | absent | `p:absent` |
| `.ufo/reports/round-25/kama.md` at base | absent | `p:absent` |
| `count-c1.py` at base | absent (added at freeze `827d1365`) | `p:absent` |
| `snapshot=20261014T124232Z … exit=2` in base tree | absent (exists only in freeze-added round-29 files) | `q:no-artifact` |
| `baseline=VALID rejected=3/3` in base tree | absent | `q:no-artifact` |

All 10 values match. Also confirmed absent/present exactly as reported for the
five `Q` spans the policy missed: `RESULT pass=24 fail=0`,
`rows=50 resolved=48 terminal=2 unresolved=0`,
`required=3 found=0 verified=0 missing=3`,
`required=3 found=3 verified=3 missing=0 mismatch=0`,
`baseline=VALID members=3 rejected=0/3` are all **present in the base tree**.

## Why the control fails (arithmetic, verified against the receipt)

* Counter mismatches at writing revisions `W`: **11**.
* Base-tree failures written as rows: **10**.
* Intersection: **6** — `P:980355388a`, `P:312b3e69b1`, `P:1c6c1f3e4c`,
  `P:17a7db7c81`, `Q:f4c42debcc:0`, `Q:a7e98b1030` — the `P` paths are absent at
  both base and `W`, and the two `Q` spans are absent at both. Accepted as valid.
* Base-only: **4** — `H:cda32b698f`, `N:cda32b698f`, `H:f4c42debcc`,
  `N:54da210e98`. Each **holds at `W`** (`holds_at_W=True`; the counter records
  all four as `false_corrections` with `why: not-a-mismatch`). The digests/counts
  written in the statements describe the `W` state (`1f81e859…`/1092 newlines,
  `860f26ac…`, 323 newlines), not the base state — so the rows are false
  correction rows.
* `W`-only: **5** — `Q:0ccd533544`, `Q:4c5d902830`, `Q:4f8083e30a`,
  `Q:f1021c03db`, `Q:f4c42debcc:2` — no artifact at `W`, but the span exists in
  the base tree, so a base-tree grep passes them; never flagged.
* `unresolved = 5 + 4 = 9`; target needs `unresolved == 0`, hence
  **`met False`**. `append_only True` (base bytes preserved, verified via the
  blob identity above).

## Verdict

The recorded CtlBaseTree control is **faithful and reproducible end-to-end from a
fresh clone**: the scored commit, the counter line, the receipt, the diff, and
the pre-scoring rows all reproduce byte-for-byte, and every base-observed value
was independently confirmed at `2aa46e24`. The policy **fails the target as
designed**: checking the base tree instead of the writing revision turns 4
holding statements into false rows and misses the 5 statements false only at
`W`. The `6` "valid" corrections are coincidental (constant `p:absent` /
`q:no-artifact` strings for statements that fail at both trees), not evidence of
partial correctness.

Additional arm — parent at the literal base commit: a second clone branched
`ctl` from `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` with the same policy tree
scored tip `c86e624e2d5120af4569d2d7274342fcc382e208`. Receipt fields are
identical to the recorded receipt except `tip`; the counter line is
`statements 69 mismatched_at_base 11 append_only True valid_corrections 6 false_corrections 4 unresolved 9 met False tip c86e624e2d51`.
So the measured counts are invariant to whether the scored commit is parented on
the freeze commit or on the base commit. (Minor wording point for the L1: the
recorded run parented the scored commit on freeze `827d1365`, while all checks
are pinned to base `2aa46e24`; the item's "base tree" refers to the check tree,
not the clone point.)

## Limits

* The control's `REPORT.md` claim "the counter was not run before scoring" is
  process testimony that cannot be re-derived from artifacts. What *is* verified:
  the policy script contains no counter invocation, its 10 rows are derivable
  from the base tree alone, and the recorded pre-scoring rows reproduce exactly
  from a fresh clone without consulting the receipt.
* The check-column prose in the appended table is policy-authored text; I
  reproduced it from the recorded `change.diff`. The statement selection and
  every observed value were regenerated and independently recomputed.

## Restoration and bounds

* Lane untouched: HEAD still `513eba3ba51a142c9936553e3a85918345eb5c4c`; `git
  status --porcelain` identical to session start (the six modified narrative
  files plus the untracked round-29 paths that pre-existed); counter and control
  artifact hashes unchanged.
* All writes confined to this output directory and
  `/tmp/kama-r29-w2-RerunCtlBaseTree/`. Scratch clones retained with the scored
  commits (`repo` = `93efe2d4…`, `repo-base` = `c86e624e…`); nothing deleted.
* No pacman; no tools installed or updated (only `/usr/bin/git`,
  `/usr/bin/python3` stdlib, `sha256sum`, `md5sum`, `diff`, `timeout`).

## Evidence paths

Under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-RerunCtlBaseTree/`:

* `report.md` (this file), `evidence-manifest.txt`
* `evidence/counter.out` (sha256 `89c459b0…`), `evidence/receipt.json` (`fd9662f4…`)
* `evidence/counter-base-parent.out` (`92766379…`; identical counts, only the
  `tip` token differs), `evidence/receipt-base-parent.json` (`3db48f44…`)
* `evidence/pre_rows.txt` (= recorded `base_rows.txt`, `7d52c27a…`), `evidence/pre_rows.err` (empty)
* `evidence/change.diff` (`ac2fccb9…`), `evidence/commit-meta.txt`
* `evidence/my_scorcard_tip.md` (106 061 B, blob `e98c13c7…`)
* `evidence/policy-script-copy.py` (recorded policy, used unmodified)

Recorded counterparts:
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlBaseTree/`.
