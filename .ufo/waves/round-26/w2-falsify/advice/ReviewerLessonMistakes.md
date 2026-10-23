ATTACK lesson round-26 §Mistakes and §Routed defects: partial

Seat: KamaR26.ReviewerLessonMistakes (reviewer, wave 2 FALSIFY). Repo: lane
`master` at f4066979096e3452ae731c0e09e50155c6d8258a (`git rev-parse HEAD`
printed it; `git status --short` printed only `?? .ufo/waves/round-26/w2-falsify/`).
Every git run was in a scratch clone (`/fast/scratch/hyaku/kama-r26w2/ReviewerLessonMistakes/clone`)
or a `git archive f4066979` extract, or was a read-only `git show`/`git diff`/`git ls-tree`
in the lane, with GIT_DIR, GIT_WORK_TREE and GIT_INDEX_FILE unset. I started no
llama-server, and I did not run the frozen C1 counter: it binds ports 47560-47579
(`count-c1.py:77`) and this item has no port block. At the end, `pgrep -af llama-server`
printed nothing (exit 1). No tools were installed or updated.

## Per-row verdicts

| Lesson item | Evidence resolves | Captured-by accurate | Fix shown able to fail | Verdict |
|---|---|---|---|---|
| §Mistakes row 1: false timestamp | yes, except the `round-25.md` row number | yes | yes on the cited revisions; misses 8 of 9 alternate spellings; no gate runs it | **partial** |
| §Mistakes row 2: control met the counter | yes | yes (prompt `kama-round-26.md:352-356`) | yes (A0 12/14, then 0/14 under A1 with identical patch bytes) | **holds** |
| §Mistakes row 3: counter weaknesses after data | yes | yes (`preregistration.json` control_wave) | n/a (not fixed); the defect list is incomplete and "no file argument" is literally false | **partial** |
| §Mistakes row 4: late-seat writes, early release | spot-check lines resolve; "the round report" does not exist at the tip | yes | "42 paths committed at a4a159c3" is incomplete; the release timing is unverifiable | **partial** |
| Routed defect 1: 42 paths committed | yes | — | one path was missed at a4a159c3 and landed at 7e5ff9b5 | **partial** |
| Routed defect 2: KQ36 qualification and round-25 erratum | yes (`corpus/QUALITY.md:205-213`; `round-25.md` erratum) | — | the erratum's claims about M17 re-check true at a23c0e04 | **holds** |
| Routed defect 3: S131-S135 | yes; each teaches cell starts `supersedes S1NN —`; no old row changed | — | five fetched sources are byte-identical to the snapshot | **holds** |
| Routed defect 4: context-capacity errata | yes (appended at the end; lines 55-56 and 137 quoted correctly) | — | — | **holds** |
| Routed defect 5: count-c2 raw binding | yes; the tip prints the claimed line | — | rejects the 5 registered mutants; accepts 4 new ones, including changed receipt values | **partial** |
| Routed defect 6: SCORECARD trend correction | yes (`SCORECARD.md`, round-26 section) | — | — | **holds** |
| Routed defect 7: release after the wave settles | not resolvable (see row 4) | — | — | **unverified** |
| Routed defect 8: work the lowest axis | yes: SCORECARD gives depth 7, and calibration and adjacency are also 7 | — | — | **holds** |

## Findings by severity

### F-A MEDIUM: count-c2's raw binding does not bind receipt values to the raw files (routed defect 5)

The lesson says `.ufo/waves/round-25/count-c2.py` "now binds every receipt raw
sha256 to its own file in `final/raw/`". `raw_bound` (count-c2.py:84-114) checks
only the hash keys that are present. It does not require all five keys. It also
accepts any unregistered key whose value is the hash of any file. Separately,
`cell_ok` reads `log_lines`, `kv_pool_n_ctx` and the other values from the
receipt, never from the hashed raw files. So the receipt's values can be
changed while `bound` stays True.

Command (extract of f4066979 at `/fast/scratch/hyaku/kama-r26w2/ReviewerLessonMistakes/tip`; harness `c2mut.py`):
`python3 c2mut.py /fast/scratch/hyaku/kama-r26w2/ReviewerLessonMistakes`, exit 0. Every counter run exited 0:

```
control-unmutated             registered 14 observed 14 bound True  missing []
raw-bytes                     registered 14 observed 14 bound False missing []
raw-sha                       registered 14 observed 14 bound False missing []
raw-deleted                   registered 14 observed 14 bound False missing []
raw-empty                     registered 14 observed 14 bound False missing []
raw-cross-cell                registered 14 observed 14 bound False missing []
N1-drop-4-of-5-raw-keys       registered 14 observed 14 bound True  missing []
N2-K1-unregistered-key-K2hash registered 14 observed 14 bound True  missing []
N3-K5-pool-x2-fields-only     registered 14 observed 14 bound True  missing []
N5-K2-kv_unified-flipped      registered 14 observed 14 bound True  missing []
```

- N3 changes K5's `kv_pool_n_ctx` and `props_n_ctx` from 4096 to 8192, and its pool line in `log_lines`. The bound raw `K5.server.log` still says `llama_context: n_ctx = 4096`.
- N5 flips K2's `kv_unified = 'false'` to `'true'` in `log_lines`. The raw `K2.server.log` says `'false'`.
- The harness also ran an `N4-L2-status-200-fields` case. It was a no-op (L2's statuses were already 200), so it is excluded.

The five registered MutationC2Receipts cases do fail, so the fix can fail.
But it covers only the raw-hash axis, not the property the spot-check cares
about (that the receipt is the run's evidence).

Smallest correction: in `raw_bound`, require every key in `RAW_FILES` for
every cell and reject unregistered keys. In `cell_ok`, derive `log_lines`
from the hashed `<id>.server.log` (each receipt line must occur in that file),
and derive `props_n_ctx`, `total_slots` and the slots list from the hashed
`.props.body` and `.slots.body`. Otherwise, register this limit in the lesson
§Routed defects item 5. The spot-check offered "or register the limit".

### F-B MEDIUM: the §Mistakes row 3 defect list omits a HIGH counter finding (F7) and four MEDIUM ones

The lesson row and SCORECARD round 26 ("Known counter limits found after
data (warning lines, decoded echoes, file-content echoes, the 19-row port
limit)") list only F1-F4. The cited `ReviewerCounterCode/findings.md` also has:

- **F7 HIGH (integrity):** the server pin hashes only the launcher. I re-checked it:
  - `sha256sum $(readlink -f ~/.local/bin/llama-server)` printed `b6a31a8e…0cd804`, and the file is 17,864 bytes.
  - `readelf -d` shows `RUNPATH [$ORIGIN]` and `NEEDED libllama-server-impl.so` (7,671,544 bytes, not pinned).
  - So the C1 statement's "sha256 b6a31a8e...cd804" pin does not cover the code that prints the signatures.
- **F5, F6, F8, F9 MEDIUM:** F8 (environment-dependent results) and F9 (order-dependent clause g) bear on reproducibility of the 17/17 receipt.

`grep -n 'F7\|launcher\|RUNPATH' corpus/lessons/round-26.md LOG.md` found no match.

Smallest correction: add F7 (and one clause naming F5, F6, F8 and F9) to
§Mistakes row 3 and the SCORECARD "known counter limits" sentence. Add "pin
every library in `~/.local/opt/llama-b11755/` and clear `LD_*`" to the
round-27 counter plan.

### F-C MEDIUM: prereg-time-check is fallible only on the exact spelling it was built from, and no gate runs it (§Mistakes row 1)

Cited runs re-done in the scratch clone, using tool sha256 `3d508f77…58c1`, which equals the lane `tools/prereg-time-check.py`. Outputs are in `runs-r26.txt`:

| revision | default mode | `--strict` |
|---|---|---|
| a4a159c3 | exit 1 (line 6, `03:45Z`, +1569 s) | exit 1 |
| a12850c5 | exit 1 (lines 6 and 29, +1517 s and +2117 s) | exit 1 |
| f071209a | exit 0 | exit 0 |
| a23c0e04 | exit 0 | exit 1 (the 429 `2026-10-25T14:27:28Z`) |
| f4066979 | exit 0 | exit 1 (same) |

The round-25 runs (`runs-r25.txt`) gave:

- preregistration at efe58e96: exit 1 (+76 s)
- amendment 1 at efe58e96: exit 1 (+16 s and +76 s)
- amendment 2 at 5388b7cf: exit 1
- amendment 3 at c808ba07: exit 1
- amendment 4 at 46fb04bd: exit 0

These match the lesson and `final/prereg-time-check.out`.

Mutants: the same 03:45Z guess committed at 00:18:51-03:00 in a scratch repo (`ptc-mutants.out`):

```
default=1 strict=1  "2026-10-23T03:45Z"            (control)
default=0 strict=0  "2026-10-23T03:45:00+00:00"
default=0 strict=0  "2026-10-23T00:45:00-03:00"
default=0 strict=0  "2026-10-23T03:45:00.000Z"
default=0 strict=0  "2026-10-23 03:45Z"
default=0 strict=0  "2026-10-23t03:45z"
default=0 strict=0  "2026-10-23 03:45 UTC"
default=0 strict=0  1792727100 (epoch; `date -u -d @1792727100` = 03:45:00 UTC)
default=0 strict=1  "2026-10-24T03:45Z" (date guessed a day off; beyond the 24 h horizon)
```

`TIME_RE` (prereg-time-check.py:39) needs a literal uppercase `Z` and no
fractional seconds. The tool is mentioned only in `LOG.md:1709` and the
lesson (`git grep -n prereg-time-check f4066979`). No gate, script or
QUALITY criterion runs it, so the class stays "captured by: none mechanical".

There is also an undisclosed false positive. Amendment 1 line 10 quotes the
false value it corrects (`"preregistration.json says written_utc 2026-10-22T08:31:00Z ..."`),
and the tool flags it (+76 s). An erratum that quotes the bad time fails the tool.

Smallest correction:

- Widen `TIME_RE` to `\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2}| UTC)` with re.I, and normalise offsets.
- Wire the tool into the round-landing checklist (a KQ row or the landed-tip receipts) for every `.ufo/waves/round-N/*.json`.
- State the boundary in row 1: Z-suffix only, the 24 h horizon, and quoted values flagged.

### F-D LOW: wrong row pointer into round-25.md (§Mistakes row 1, twice)

Row 1 says "same class as `round-25.md` §Mistakes row 7" and "which
`round-25.md` row 7 said amendment 1 had corrected". Numbering the
`round-25.md` §Mistakes table at f4066979 (and at 7f84cd0e) gives:

- row 6 = `| false timestamp repeated | amendment 2 written_utc 09:30Z ...` (`corpus/lessons/round-25.md:53`)
- row 7 = `| axis misfiled: drift declared as a calibration claim |` (`:54`)

Smallest correction: "row 7" → "row 6" in both places.

### F-E LOW: routed defect 1 and §Mistakes row 4 say "committed at a4a159c3"; one path landed later, because jj skips files over 1 MiB

- `diff <(git ls-tree -r --name-only a4a159c3 .ufo/waves/round-25/a2-falsify) <(git ls-tree -r --name-only f4066979 ...)` prints `> .../ReplicateReceipt/replication-run3/raw/L3.server.log`.
- That file is 1,446,775 bytes, with mtime 2026-10-22 07:31:37 -03:00 (a round-25 late write).
- `git check-ignore` returns 1 (not ignored).
- `jj --ignore-working-copy config get snapshot.max-new-file-size` prints `1MiB`.
- The file was committed at 7e5ff9b5 ("commit the late round-25 L3 replication log skipped by the directory commit (routed defect 1)").
- The lesson (§Routed defects 1, §Mistakes row 4) and `LOG.md` ("42 late paths committed (a4a159c3)") do not name 7e5ff9b5. "42 paths" is the spot-check's porcelain entry count. a4a159c3 changed 223 file paths under `a2-falsify/` (220 A, 2 M, 1 D).

Smallest correction: "committed at a4a159c3 and 7e5ff9b5 (one 1.4 MB log that
jj's 1 MiB snapshot limit skipped)". Also add a landing check: `git status
--porcelain` must be empty except the next wave's directory.

### F-F LOW: "the release lines are in the round report" does not resolve at the tip (§Mistakes row 4, routed defect 7)

- `/home/vgpnk/Projects/shokunin/.ufo/reports/round-26/` holds no `kama.md` (`ls -la` shows 11 other lanes' files).
- The lane tree has no round-26 report.
- `~/.local/state/shokunin-hyaku/events.log` has no round-26 kama slot event. Its last kama line is 728/729, the round-26 launch.
- `wave-slots` now holds only `1792727810 34 kama kama-r26-w2-falsify`; no wave-1 row remains, and no release time is recorded.

Wave-1 seat ExecRequestParams wrote its last files at 00:55:48 -03:00
(`advice/ExecRequestParams.md`). That is after the integration commit
7f84cd0e (00:50:35) and the landed-tip receipts (3550523, 00:51:34); they
landed at f4066979 (00:56:41). The lesson itself says ExecChatFormat
"returned after integration". Integrating before the wave settled is a milder
recurrence of the late-seat class. Whether the wave-1 slot was released
before 00:55:48 cannot be checked from committed or state bytes.

[INFERENCE] The w2 reservation (03:56:50Z = 00:56:50 -03:00) follows
f4066979 by 9 s, which fits release after the last wave-1 return. That is
not proof.

Smallest correction: commit each wave's slot acquire and release lines (time
and seat count) in the round's wave directory, and cite that path instead of
a report that does not exist yet.

### F-G INFO

- Row 1 says the L1 self-review "found it two minutes later". a4a159c3 (00:18:51) → f071209a (00:20:14) is 83 s.
- The S132 Gate quote `params.n_ctx == 0 ? hparams.n_ctx_train : params.n_ctx;` collapses the source's alignment spaces. The fetched line 219 is `cparams.n_ctx            = params.n_ctx           == 0    ? hparams.n_ctx_train           : params.n_ctx;`. The words match; the bytes do not.
- The committed A1 re-score receipt (`controls/A1-rescore/invalid-flag-usage-A1.json`) records no counter or tree hash. Its binding to the A0 patch rests on the scratch tree `/fast/scratch/hyaku/kama-r26/ctl/A1/inv`. I verified that tree:
  - SKILL.md `938d635c…`, SOURCES `bbac5e6e…` and registry `941d6d1c…` equal `KamaR26CtlAllFalse/invalid-flag-usage-hashes.json`.
  - Its counter is `6501737c…` (A1), against A0's `f800865d…`.
  - Its `not-counted` reasons are all `f_absent_from_baseline` (plus `e_signature_seen` for HT10 and HT14, as under A0).
- Row 2 holds, and the pilot still counts under A1 (`pilot-P1-A1.out`: `registered 1 counted 1`).

## Row-by-row detail for the holds

- **Row 2.** `KamaR26CtlAllFalse/invalid-flag-usage.stdout.txt`: `registered 14 counted 12 target 12 met True`, EXIT CODE 0, under counter `f800865d` (A0, the a12850c5 bytes). `controls/A1-rescore/invalid-flag-usage-A1.out`: `registered 14 counted 0 … met False`, exit 0. A1 committed at a23c0e04 (00:32:54) precedes the wave-1 dispatch commit 84ec083b (00:33:21). The counter sha at a23c0e04 and f4066979 is `6501737c…6588` = `preregistration.json:18` = `final/tip-counter-sha.txt`.
- **Routed defect 2.** `corpus/QUALITY.md:205-213` defines "landed tip" as asked. The erratum appended to `round-25.md` is true: `git show a23c0e04:SKILL.md | grep -n M17` prints only lines 883 and 889, and neither says M17 survives. The KQ36 qualification's own test holds for the C1 receipt: `git diff --stat 7e5ff9b5 f4066979` touches only `w1-build/` files and LOG.md, so SKILL, registry, SOURCES and the counter bytes are identical.
- **Routed defect 3.** All five teaches cells start `supersedes S106 —`, `S107`, `S109`, `S112`, `S113`; status `mined`. `git diff 1560e4d8 f4066979 -- corpus/SOURCES.md | grep '^-'` shows no removed line. Fresh fetch on 2026-10-23 from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/` of common/fit.cpp, src/llama-context.cpp, tools/server/server-context.cpp, tools/server/README.md and src/llama-kv-cache.cpp: every curl rc=0 and `cmp` against the lane snapshot exited 0 (sha256 1f83da2a…, 2a25e556…, dd1de0f2…, 714c067b…, d0739eaf…). The quoted lines 264, 219, 1813, 165 and 301 are present.
- **Routed defect 4.** `corpus/knowledge/context-capacity.md` gained an appended "Errata — round 26" section. The original lines 55-56 and 137 are unchanged.
- **Routed defect 6.** The SCORECARD round-26 section appends "Round 26 correction — round-25 trend verdicts" without editing the earlier bytes.

## Residual risk and verification gaps

- I did not re-run the A1 re-score or any C1 count: the counter starts llama-server and this seat has no port block.
- I did not attack E26 rows individually for F1-F3; sibling seats own that.
- [INFERENCE] Prompt `kama-round-26.md:357-358` says "A rule changed after any seat has scored is not the claim's rule". A1 changed the rule after a *control* seat scored. Lines 354-356 order that fix before data, so the lane's reading is defensible, but the two sentences conflict literally.
- `wave-slots` still holds round-23 kama rows (`1792595209 68 kama round23-build`, `1792597546 73 kama round23-falsify`). This is an unreleased reservation from an older round, outside this item.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/ReviewerLessonMistakes.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/ReviewerLessonMistakes/runs-r26.txt` (prereg-time-check at the five round-26 revisions, default and `--strict`)
- `.ufo/waves/round-26/w2-falsify/out/ReviewerLessonMistakes/runs-r25.txt` (round-25 preregistration and amendments 1-4)
- `.ufo/waves/round-26/w2-falsify/out/ReviewerLessonMistakes/ptc-mutants.out` (9 timestamp-spelling mutants)
- `.ufo/waves/round-26/w2-falsify/out/ReviewerLessonMistakes/c2mut.py`, `c2-mutants.out` (count-c2 mutants; N4 there is a no-op, excluded above)
- Scratch: `/fast/scratch/hyaku/kama-r26w2/ReviewerLessonMistakes/` (clone, tip extract, c2m trees, mut repo, fetch)
