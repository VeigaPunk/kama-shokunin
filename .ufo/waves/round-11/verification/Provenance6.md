# Provenance6 — `corpus/knowledge/free-tier-provider-limits.md` provenance supplement review

**Scope:** kama round 11, seat Provenance6. Read-only semantic review of the appended
`## Provenance supplement — round 11 (2026-10-19)` block against the original historical
context and QUALITY KQ11. No implementation, corpus, or fleet file was modified; `measure.py`
was not executed and no build/lint/test/formatter ran. All paths below are relative to
`/home/vgpnk/Projects/shokunin/kama-shokunin/`.

**Target:** `corpus/knowledge/free-tier-provider-limits.md` (77 lines, 5,760 B; supplement at
`:71-77`).

## Verdict

The supplement is **honest on all four KQ11 admit conditions** (prefix preservation,
historical dates, metadata-vs-live separation, bounded recheck). Two wording defects remain,
one of them objectively false, neither of which reverses admission for this file.

## Findings

### Low — `:73` makes a false exhaustiveness claim about in-file pointers

`:73` ends: "the A39 correction note appended above is the only other in-file pointer."

False by two instances that point at the exact evidence surfaces the supplement's `source:`
line lists:

- `:5-7` — "Sources: per-round telemetry `.ufo/round-<N>/telemetry.json` and fleet reports
  `.ufo/reports/round-<N>/kama.md` (fleet root); both are resolvable evidence."
- `:65` — "pinned by `.ufo/round-6..9/telemetry.json`."

Under a stricter reading ("only other in-file *correction* pointer") the sentence is merely
misfocused, because `:69` is a correction note, not a pointer to the telemetry/report
evidence; the words "the only other in-file pointer" still describe the file's pointer set
incorrectly. Either way the reader is told the pointer search is exhausted when it is not.

**Smallest repair:** delete the trailing clause `; the A39 correction note appended above is
the only other in-file pointer.` and, if a pointer note is wanted, append: `; the header
(lines 5–7) and Conclusion (line 65) also name these same evidence surfaces.`

**Effect on KQ11:** none of the reject conditions; the substantive `source:` enumeration is
truthful and complete (four telemetry files + four fleet reports). No evidence is fabricated.

### Low — `:74` conflates the telemetry dates with the status board

`:74` claims the seat "confirmed their recorded dates and counts still match the status
board." The board (`:26-35`) has columns Round | Loop | Model | Launched | Completed | Failed |
Failure class | Wall s | Peak conc. | Inferred TPS — **no date column**. The four dates in
`:73` are telemetry `recorded_utc` values, so only the counts and wall times can be compared
to the board; the dates can only be compared to the telemetry records themselves. As written
the sentence attributes to the board a fact it does not contain.

**Smallest repair:** `confirmed the four telemetry `recorded_utc` values in `source:` above
and the four rounds' counts and wall times still match the status board (lines 30–33).`

**Not a defect:** the word "still" here is a retention check over frozen retained files, not a
runtime freshness claim; the same sentence disclaims refresh ("no endpoint, provider,
dispatch catalog or wire id was contacted … not refreshed by this supplement"). The phrase
does not trip `measure.py`'s `_live_claim_re` guard (`:126-141`): the `verified-at:` value
contains zero `live` and zero `revalid` substrings, so no negation-window rescue is needed.

## KQ11 condition check (QUALITY.md:38)

| KQ11 admit condition | Result | Exact evidence |
|---|---|---|
| Original byte prefix preserved | **PASS** | `git show HEAD:` bytes = baseline sha256 `5dd88870…0caf7e`, 3,914 B; first 3,914 B of the working file hash to the same value; frozen copy `.ufo/waves/round-11/frozen/before/corpus/knowledge/free-tier-provider-limits.md` is byte-identical to HEAD (`cmp`); `git diff` = one hunk `@@ -67,3 +67,11 @@`, 8 insertions, 0 deletions; appended region 1,846 B begins with an empty line, so the column-zero heading at `:71` is not glued to `:69` |
| Historical observation dates identified | **PASS** | `source:` names `recorded_utc` 2026-10-18T18:35:08Z / 18:38:06Z / 18:40:17Z / 18:42:06Z (matches round-6/7/8/9 `telemetry.json` exactly); `verified-at:` names the observation window 2026-10-18T18:32–18:42Z; body retains its own 2026-10-18 dates |
| Metadata review distinguished from live revalidation | **PASS** | `:74` "Metadata review only", "no endpoint, provider, dispatch catalog or wire id was contacted"; `:77` "no observation above is refreshed"; the historical 29-alias catalog read is **not** revived as current — live revalidation is explicitly deferred |
| Bounded current recheck or explicit unavailable surface | **PASS** | `:75`: no-network loop over `n in 6 7 8 9`, read-only `json.load` + `test -f`; names live revalidation as needing an operator-authorized single-seat probe of `opencode-go/deepseek-v4.1-flash-free` plus a fresh catalog listing for `opencode-go/glm-5.3-flash-free` |
| KQ11 reject conditions hit? | **No** | No field-presence-as-evidence, no `source: none`, no revived obsolete config-body read, no altered prefix |

New-knowledge-trio clause is not applicable (legacy file); the three fields are present at
column zero, exactly once each, outside triple fences (one column-zero occurrence per field,
zero backtick fences in the appended region).

## Source honesty — values checked against retained evidence

All eight named files exist and are unmodified since 2026-10-18 (mtimes 15:35–15:43 local,
18:35–18:43Z), consistent with a read-only open:

- `.ufo/round-6/telemetry.json` — `recorded_utc` 2026-10-18T18:35:08Z; 64/0/64; wall 41.562 s → board 41.6.
- `.ufo/round-7/telemetry.json` — 18:38:06Z; 64/0/64; 41.546 s → board 41.5.
- `.ufo/round-8/telemetry.json` — 18:40:17Z; 0/0/0; 0.0 s; local catalog rejection pre-spawn.
- `.ufo/round-9/telemetry.json` — 18:42:06Z; 0/0/0; 0.0 s; identical rejection.
- `/home/vgpnk/Projects/shokunin/.ufo/reports/round-{6,7,8,9}/kama.md` — all four present;
  report bodies agree on 64/0/64, 41.6 s, 64/0/64, 41.5 s, 0/0/0, 0/0/0 and on the verbatim
  `400 Upstream request failed: Model is unavailable.` versus `Invalid model` classes.

The KQ11-sensitive reading — that the 2026-10-18 failure classes are historical and are not
asserted to hold now — is stated explicitly and is correct: deepseek-free's outage is dated,
glm-free's catalog gap is dated, and neither is re-probed.

**Temporal separation:** observations 2026-10-18T18:32Z–18:42Z; claim 2026-10-20T02:14Z
(~32 h later). The file's own mtime is 2026-10-19 23:15:59 −0300 = **2026-10-20T02:15:59Z**,
i.e. 1 min 59 s *after* the declared `verified-at:` — the claimed review time precedes the
write, which is the only ordering that is physically possible. The heading's "2026-10-19"
is declared as the steered label; no date is silently rewritten.

## Recheck assessment (`:75`)

- **Resolvable:** all four `d[...]` keys (`round`, `recorded_utc`, `seats_dispatched`,
  `seats_completed`, `seats_failed`) exist in every one of the four JSON files.
- **Correct base:** `.ufo/round-$n/telemetry.json` resolves from the lane root as stated;
  the `test -f` paths use the exact case `Projects/shokunin` (KQ9), and all four exist.
- **Safe/bounded:** four iterations, read-only, no network, no endpoint or catalog contact,
  no write. It prints rather than asserts; a human compares four tuples against `:30-33`.
  That is a limitation, not a KQ11 failure — the line labels itself a "retained-metadata
  check (no network)".

## What is already correct

- Append-only edit: no original byte changed, no mid-file insertion, so the A39 anchor
  `:26-57` still resolves in bounds and no other file's anchors shift.
- The supplement does not restate the historical `0 usable seats` result as a current
  ceiling; the Conclusion's `0 seats` keeps its 2026-10-18T18:42Z date.
- The 29-alias catalog verbatim from rounds 8–9 stays inside the telemetry as history and is
  not offered as today's catalog.
- Wire ids in `recheck:` match `model_dispatched` in the telemetry
  (`opencode-go/deepseek-v4.1-flash-free`, `opencode-go/glm-5.3-flash-free`).

## Baseline comparison performed (not the acceptance measurement)

Logical comparison only, no `measure.py` run: HEAD/frozen/baseline all hash to
`5dd888709c3525965c4b487588c25d426dee06c2b6059b923b8a3bfa210caf7e` at 3,914 B; working-file
prefix at that extent hashes identically; working file 5,760 B. Parent still owns the
`measure.py provenance` run and its fail-before controls.

## Tools / network

No tools were installed or updated; actual install record: **none**. No public URL was
assigned for this file, so none was opened; no network request was made and no provider,
endpoint, dispatch catalog, or wire id was contacted. Retained evidence was opened read-only
in-repo.
