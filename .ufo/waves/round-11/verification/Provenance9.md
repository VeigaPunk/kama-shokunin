# Provenance9 — advisory verification: `corpus/knowledge/snapshot-history.md` round-11 supplement

- Seat: `KamaR11.Provenance9` (leaf; no delegation, no subagents)
- Lane / wave: `kama-shokunin`, round 11
- Review date: 2026-10-20 (system date; no `date -u` run by this seat)
- Axis authority: current `shokunin.conf` kama lane row — `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`. No historical MISSION example was used.
- Assigned artifact: `corpus/knowledge/snapshot-history.md` (104 lines; supplement at lines 99–104). Quality bar: `corpus/QUALITY.md` KQ11.
- Baseline: `HEAD:corpus/knowledge/snapshot-history.md`, 98 lines. `.ufo/waves/round-11/legacy-baseline.json` records 6067 bytes, sha256 `93b2c6f2a6db619751d1d65e1d5c9590c610d594525242f08c24725ee27bb4f5`, missing exactly `source`, `verified-at`, `recheck`.
- Method: read-only repository inspection (`read`, `git diff`, `git log`, `grep -n`, `awk NR` numbered reads, `find`, `ls`). No test, build, lint, formatter, probe, endpoint call, or network fetch was executed. No public URL was assigned to this seat; none was opened.

## Verdict

The supplement is **substantially honest and KQ11-compliant**: exactly one column-zero `source:` / `verified-at:` / `recheck:` field is appended at EOF, the original byte prefix is untouched, the historical observations are separated from the metadata review, and the recheck is bounded. Two low-severity textual defects remain, both on the evidence-status wording; neither invalidates the temporal separation or the no-revalidation claim.

## Findings

### P2-1 — wrong ledger line anchor (`DELTA.md:1` points at the title, not the baseline record)

- Location: `corpus/knowledge/snapshot-history.md:103` (`verified-at`), clause: "baseline timestamp and 11-row count corroborated by `registry/history/DELTA.md:1`".
- Observed: `awk NR==1 registry/history/DELTA.md` → `# kama snapshot DELTA.md — endpoint-verdict transition ledger` (title comment). `grep -n 'baseline recorded' registry/history/DELTA.md` → `6`. The corroborating record is `DELTA.md:6`: `- 2026-09-29T04:30:44Z baseline recorded (11 rows); transitions begin with the next snapshot`.
- Why it matters: a reader following the citation lands on the file title, not the corroboration. The content is correct; only the anchor is wrong. This is the same class of error the file's round-10 corrections fixed (KQ7/KQ9 anchor discipline).
- Smallest repair: in line 103, change `registry/history/DELTA.md:1` → `registry/history/DELTA.md:6`. No other text changes.

### P2-2 — present-tense existence claim contradicts the same sentence's "only … remain"

- Location: `corpus/knowledge/snapshot-history.md:102` (`source:`), clause: "NOT retained: the round-2 live snapshot ids `20260929T043044Z`/`20260929T043052Z` and their summary strings **exist as dated JSON only as local run evidence** …; on disk only `20261014T124232Z.json` and `20261014T124525Z.json` remain, and no `.ufo/round-2` evidence directory exists."
- Observed: `find . -name '*20260929*' -not -path './.git/*'` → no output. `ls registry/history` → `20261014T124232Z.json`, `20261014T124525Z.json`, `DELTA.md`, `latest.tsv` only. `ls .ufo/round-2` → `No such file or directory`. The 2026-09-29 dated JSON files do **not** exist on disk. Separately, the ids/summary strings *are* retained as prose in this same file at lines 65–70; what is not retained is the dated JSON underneath them.
- Why it matters: the clause asserts present-tense existence of files that the continuation says are absent, and it conflates the prose record (retained) with the JSON evidence (not retained). A provenance supplement should not leave an existence ambiguity; KQ11 explicitly separates retained evidence from dated observation.
- Smallest repair (replace the one clause, keep the rest): change

  `NOT retained: the round-2 live snapshot ids \`20260929T043044Z\`/\`20260929T043052Z\` and their summary strings exist as dated JSON only as local run evidence`

  to

  `NOT retained: the dated JSON behind the round-2 live snapshot ids \`20260929T043044Z\`/\`20260929T043052Z\` (the summary strings survive only as this file's prose); those files were untracked local run evidence`

  The following `on disk only … remain` clause then reads consistently.

## What is already correct (KQ11 clause-by-clause)

| KQ11 clause | Evidence observed | Status |
|---|---|---|
| Legacy supplement preserves the original byte prefix | `git diff --numstat -- corpus/knowledge/snapshot-history.md` → `6 0`; hunk `@@ -96,3 +96,9 @@` with the three original tail lines as unchanged context; no deletion in any hunk | pass |
| Exactly one provenance trio, appended at EOF | `grep -cE '^(source\|verified-at\|recheck):'` → `3`; fields at lines 102, 103, 104; no mid-file insertion; round-10 correction entries at lines 84–98 untouched | pass |
| Identifies historical observation dates | `verified-at` names 2026-09-29 (round-2 live baseline) and 2026-10-14 (tracked drift/rebaseline), and explicitly says the `model_ok=3 drift=8 exit=2` summary has no retained dated JSON | pass |
| Distinguishes metadata review from live revalidation | `verified-at: metadata review only, 2026-10-20`; `No live probe, snapshot run, or endpoint revalidation was performed in round 11`; `none of this file's endpoint-state claims are refreshed` | pass |
| Names a bounded current recheck or unavailable surface | `recheck:` names (a) hermetic `bash tools/test-snapshot.sh` (fixture server binds `127.0.0.1`, `tools/test-snapshot.sh:41,64,79`), (b) live `bash tools/kama-probe.sh snapshot` with `--history DIR` for an isolated root, and (c) read-only anchor re-derivation | pass |
| Does not offer field presence/correction date as refreshed runtime evidence | No refreshed-verdict claim; source is explicitly retained repo evidence, and the round-2 summary is explicitly not backed by retained dated JSON | pass |
| Does not revive an obsolete config-body read as a current recheck | Recheck uses the repo probe tool and the hermetic harness, not stale config/environment bodies | pass |
| `source: none` alone is not offered | `source:` lists concrete repo artifacts and commits; no `source: none` | pass |

## Evidence log (read-only; exact observations)

1. `git diff --numstat -- corpus/knowledge/snapshot-history.md` → `6	0	corpus/knowledge/snapshot-history.md`. Only additions; prefix preserved.
2. `git log -1 --format='%H %cI %s' 83bee7f` → `83bee7faf5a733ac7a7bc47cde29cba23c6cefb7 2026-09-29T01:34:16-03:00 round-2`; `git show --stat 83bee7f` includes `corpus/knowledge/snapshot-history.md | 84 +` and `corpus/lessons/round-2.md | 72 +`. Source claim "round-2, 2026-09-29" is accurate.
3. `git log -1 --format='%H %cI %s' 1e41928` → `1e41928aba2b81dd65ea75084918a7fadf453720 2026-10-19T19:34:42-03:00 round-10: … KQ6-KQ10`. Source claim accurate.
4. `registry/history/latest.tsv`: line 1 `#@snapshot_id 20261014T124232Z	# columns: id	verdict	reason	served_model	port	file_match`; lines 2–4 = 3 data rows (all `DEAD connection-refused`). Supplement's "3 rows" is accurate as data rows.
5. `registry/history/DELTA.md`: 17 `- ` lines = 1 baseline (@ `2026-09-29T04:30:44Z`, 11 rows) + 16 transitions, all at `2026-10-14T12:42:32Z`; 8 of them are `row-absent` (11 − 8 = 3 rows, consistent with `latest.tsv`). "transitions through 2026-10-14T12:42:32Z" is accurate.
6. `registry/history/.gitignore:1` → `# Dated snapshots are local run evidence; the normalized baseline and ledger are tracked.` Quote in `source:` is exact (substring).
7. `registry/endpoint-consumers.tsv:35-37` — all three declared URLs are `http://127.0.0.1:…`; the recheck phrase "evaluates only the registry's declared loopback consumers" is accurate for the current registry.
8. `tools/test-snapshot.sh` — hermetic: Python fixture binds `127.0.0.1` at line 64; `CLEAN_URL="http://127.0.0.1:$PORT/v1"` at line 79; prints `RESULT pass=%s fail=%s` at line 170. `corpus/lessons/round-2.md:49` records `bash tools/test-snapshot.sh` → `RESULT pass=24 fail=0`; the supplement correctly labels that as a dated round-2 measurement, not a round-11 run.
9. Cited implementation anchors, all re-read with `awk NR` numbering and all accurate:
   - `tools/kama-probe.sh:110-111` — verdict vocabulary + `exit: 0 reconciled | 2 drift | 1 probe error`.
   - `157-159` — `snapshot refuses --port: a matrix probe has no registry baseline to persist`.
   - `608-612` — resolved-URL credential strip (query/fragment + userinfo).
   - `845-848` — `cmd_check` JSON `exit_codes` emission (line 845) and return.
   - `919-943` — `row-added`, per-field transitions, sorted `row-absent`.
   - `959-970` — `served_persist` normalized basenames.
   - `987-1003` — symlink refusals (989, 994), `flock -w 10 9` (1001), `diff_baseline` (1003).
   - `1040-1054` — tmp-file + `mv` atomic `latest.tsv` replacement (1052–1053).
10. `find . -name '*20260929*' -not -path './.git/*'` → empty; `.ufo/round-2` absent. The only retained dated JSONs are the two 2026-10-14 files. This corroborates the "no retained round-2 dated JSON" claim and is the factual basis for P2-2's wording repair.
11. `git ls-files registry/history corpus/lessons/round-2.md tools/test-snapshot.sh tools/kama-probe.sh` → `registry/history/.gitignore`, `registry/history/DELTA.md`, `registry/history/latest.tsv`, `corpus/lessons/round-2.md`, `tools/kama-probe.sh`, `tools/test-snapshot.sh` are all tracked; `git log --oneline -3 -- corpus/knowledge/snapshot-history.md` → `1e41928 round-10`, `83bee7f round-2`; `git show HEAD:… | wc -l` → `98`, working tree `104`. The `source:` line's "tracked" qualifiers are accurate.

## C1 denominator consistency

`legacy-baseline.json` contains exactly **9** knowledge files, each with the same three missing fields; `snapshot-history.md` is one of them (3/3 fields now present). Nine files × 3 fields = **27**, matching `claims.json` C1 ("Nine legacy knowledge entries lack all 27 column-zero … fields"). The supplement's own count is therefore inside the fixed denominator, and the "9, not 18" adjustment is explained in `claims.json` (`planned_row_adjustment`: lessons are not knowledge entries). No score change is asserted by this seat; the claim is a field-count calibration, not a global 0–10 denominator.

## Cross-file note (not my assigned file)

`corpus/knowledge/listener-census.md` shows `6 1` in `git diff --numstat`. The single deletion is the last line's `\ No newline at end of file` marker being replaced by a newline when the supplement was appended (`git diff` shows the original final line re-added with `**` plus the appended heading). The original bytes remain a prefix; this is a final-newline artifact, not a prefix rewrite. Flagging so the parent's measurement does not count it as a C1 prefix violation.

## Limits / risks

- This is an advisory, author-adjacent read. It is **not** the outside non-author admit/reject review the corpus still requires; that review remains separate.
- I did not execute the file's named recheck (`tools/test-snapshot.sh`, `kama-probe.sh snapshot`, or the `nl … | sed` recipe); the parent owns post-integration measurement. I re-read the cited ranges as content, not as a re-derivation run.
- The supplement's "no live probe … in round 11" is a negative claim about the wave. I found no round-11 advice artifact recording a run (`snapshot=2026…` absent; `Legacy9.md:73` states the harness was not executed), but the wave is still in flight, so the parent should treat the negative as scoped to retained artifacts as of this read.
- The body anchors at lines 15, 21, 36, 51, 53, 55 remain historical with their appended round-10 corrections intact; this is the file's documented KQ7 convention, not a defect.

## Tooling / installs

- Tool installs or upgrades: **none**. No `pacman`, `uv`, `cargo`, `npm`, or release-binary install was run; no install record exists for this seat.
- No commits, pushes, deployments, host-config edits, environment reads, or service/network probes. Sole write: this advisory file.
