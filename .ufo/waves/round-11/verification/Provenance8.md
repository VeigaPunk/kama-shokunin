# Provenance8 — `served-model-identity.md` provenance supplement review

**Seat:** KamaR11.Provenance8 (advisory executor).
**Target:** `kama-shokunin/corpus/knowledge/served-model-identity.md` — appended supplement at `:39-44`, original fragment at `:1-37`.
**Quality bar:** `corpus/QUALITY.md:38` (KQ11). KQ12/KQ13 are outside this seat.
**Version reviewed:** 44 lines / 2537 bytes, full-file `sha256 dfc3feb98ad0b7d0954926dbef75d416f2dfb492f809c497df91ba572de5c98e`, mtime `2026-10-20 00:49:02 -0300` (`2026-10-20 03:49 UTC`). The working tree changed during this review (an earlier read was 2462 bytes); the 1221-byte original prefix is unchanged. The parent should pin these bytes before integration.

**Verdict:** The current supplement is honest about the retained sample and passes KQ11's four core clauses for this file. No medium or high semantic defect remains. Three citation nits remain. No finding offers the historical metadata as current runtime evidence.

## Read-only evidence

No `measure.py`, selftest, probe, endpoint, test, lint, or formatter was run. The comparisons below are file reads plus `git`, `sha256sum`, `cmp`, `wc`, `stat`, `jq`, and `nl`.

| Check | Command / source | Observed |
|---|---|---|
| Baseline record | `.ufo/waves/round-11/legacy-baseline.json`, key `corpus/knowledge/served-model-identity.md` | `sha256 294e1192181837cfbc31480c07c005cc012cbd7de7852c6ca58bb1d36d4b630b`, `bytes 1221`, `missing ["source","verified-at","recheck"]` |
| Current size | `wc -lc corpus/knowledge/served-model-identity.md` | `44 2537` |
| Prefix hash | `head -c 1221 corpus/knowledge/served-model-identity.md \| sha256sum` | `294e1192181837cfbc31480c07c005cc012cbd7de7852c6ca58bb1d36d4b630b` — exact match |
| Diff shape | `git diff --numstat -- corpus/knowledge/served-model-identity.md` | `7 0` — 7 insertions, 0 deletions |
| HEAD identity | `git diff --quiet c6199a2 HEAD -- corpus/knowledge/served-model-identity.md; echo $?` | `0` |
| Commit ancestry | `git merge-base --is-ancestor c6199a2 HEAD; echo $?` | `0` |
| Commit metadata | `git show -s --format='%ci%n%s' c6199a2` | `2026-09-28 23:15:05 -0300`; subject `round-1: operability axis — runnable endpoint-identity gate for local model serving` |
| File mtime | `stat -c '%y' corpus/knowledge/served-model-identity.md` | `2026-10-20 00:49:02 -0300` = `2026-10-20 03:49 UTC`, consistent with `metadata review 2026-10-20` |

The original fragment starts with two blank lines and `### Exact readiness-field probes` at `:3`; all 1221 original bytes, including those blank lines and the `###` heading, are inside the matched prefix. The supplement starts with a blank line at `:38`, an H2 at `:39`, and the three column-zero fields at `:40-42`.

**Baseline comparison for this path:** the baseline entry records `source`, `verified-at`, and `recheck` missing (3 of the wave's 27). The current file supplies each exactly once at column zero (`:40`, `:41`, `:42`) with no indented duplicates in the appended block, and the 1221-byte prefix hash matches. Logically, this path's field contribution is 3→0 and its prefix violation is 0; this is not a measurement run.

## KQ11 clause review

| KQ11 clause | Evidence in the supplement | Result |
|---|---|---|
| Preserve the original byte prefix | Prefix sha256 equals the baseline exactly; diff is append-only (`7 0`); `c6199a2` is an ancestor and the file at HEAD is byte-identical to that commit | **Pass** |
| Identify historical observation dates or unknown dates | `:40` cites the 2026-09-28 observation and the 2026-09-28 ~22:47–22:52 -0300 census window; `:41` separates `original samples 2026-09-28` from `metadata review 2026-10-20 only` and from the October dead-endpoint observations | **Pass** |
| Distinguish metadata review from live revalidation | `:41` says `No endpoint contacted or live revalidation claimed` and `None of those host states was re-observed in round 11`; the old `/metrics` counters are not replayed as current | **Pass** |
| Name a bounded current recheck or an explicit unavailable surface | `:42` names `bash tools/kama-probe.sh check; echo "CHECK_EXIT=$?"` and warns `do not replay the 34113 samples above as current`; re-probing readiness is restricted to an operator-authorized serving base URL | **Pass** |
| New entries still open with the provenance trio | Not applicable to this legacy file. The new `corpus/knowledge/served-identity-crosswalk.md:1-3` opens with `source`, `verified-at`, `recheck` (as read; its vendor semantics are outside this seat) | **N/A here; trio present** |
| Failure controls absent | No `source: none`; no field-presence-only runtime claim; no obsolete config-body read revived as a current recheck | **Pass** |

The recheck target exists and matches the description: `tools/kama-probe.sh:9-10` says `Read-only toward live services and consumer configs. listeners/consumers/check write only to a removed mktemp dir`; `:18` documents `check reconcile registry entries against live classification (exit gate)`; `:88-93` documents the subcommand; `:845` reports exit codes `0` / `2` / `1`; `SKILL.md:196-202` states the same three codes and warns `Never describe exit 2 as model readiness`. The current `registry/history/latest.tsv` contains three evaluated rows, so the recheck is bounded to the registry, not an all-host census.

The current `verified-at` sentence cites `registry/history/DELTA.md:9-14` and `LOG.md:245-246` for the October dead-endpoint observations and explicitly says the row deletion at `DELTA` line 20 `does not establish permanent server retirement`. `DELTA.md:9-14` does record the two 34113 consumers transitioning `MODEL_OK -> DEAD` with `connection-refused`; `LOG.md:245-246` does record `qwen-coder.service` inactive, its unit deleted, and `ports 34113 and 8080 both refuse connections`. The retirement-transition caution is therefore grounded, not a new overclaim.

## Findings

### N1 — Nit — `round-1.md` is mislabeled a “command ledger”

**Location:** `:40` (`round-1 command ledger \`corpus/lessons/round-1.md:3-4\``).

`corpus/lessons/round-1.md` is a lesson/rules file, not a command ledger. Its own `:3-5` says: `the full command ledger is in \`corpus/knowledge/listener-census.md\` (C1–C19) and \`corpus/knowledge/consumer-registry.md\``. The quoted phrase at `:3-4` is exact; only the label is wrong.

**Smallest repair:** `round-1 lesson \`corpus/lessons/round-1.md:3-4\`` (it points to the ledger). No change to the quote or date.

### N2 — Nit — commit subject quote is truncated without an ellipsis

**Location:** `:40` quotes `"round-1: operability axis"`.

The actual `git show -s --format=%s c6199a2` subject is `round-1: operability axis — runnable endpoint-identity gate for local model serving`. The hash makes the target unambiguous, and the quoted prefix is exact, but it is presented without an abbreviation mark.

**Smallest repair:** append `…` after `operability axis`, or use the full subject.

### N3 — Nit — measurement-date citation is one hop off

**Location:** `:40` attributes `2026-09-28 ~22:47–22:52 -0300` to `listener-census.md §5 C2`.

The date/window is at `corpus/knowledge/listener-census.md:3` (the file measurement header); `§5` starts at `:182`, the C2 block at `:189-193`, and the C2 block itself carries no timestamp. The date is substantively correct.

**Smallest repair:** cite `corpus/knowledge/listener-census.md:3, §5 C2` (or `:3` plus `:189-193`).

## What is already correct

- **Prefix preservation is exact.** The first 1221 bytes hash to the baseline value; the working-tree change is purely 7 appended lines; `c6199a2` is an ancestor and the file at HEAD equals that commit. The two leading blank lines and the `### Exact readiness-field probes` fragment heading are untouched.
- **The original observation date is grounded.** `corpus/lessons/round-1.md:3-4` says `grounded in a command run on 2026-09-28`; `corpus/knowledge/listener-census.md:3` says `Measured: 2026-09-28 ~22:47–22:52 -0300`; the commit is `2026-09-28 23:15:05 -0300`, after that window and on the same local date. The supplement does not claim the sample is current.
- **Temporal separation is explicit.** `verified-at` separates `original samples 2026-09-28`, `metadata review 2026-10-20 only`, and the October dead-endpoint observations; the file mtime (`2026-10-20 00:49:02 -0300`) is `2026-10-20 03:49 UTC`, consistent with the review date. The heading's `2026-10-19` is the round label; the review date is separately stated, so the two dates are not conflated.
- **The retirement caveat is honest.** `:41` explicitly says the deleted registry row at `DELTA` line 20 `does not establish permanent server retirement`, avoiding an unsupported retirement date. It cites direct October dead-endpoint evidence (`DELTA.md:9-14`, `LOG.md:245-246`) rather than treating row absence as a process stop.
- **The recheck is safe and bounded, not a replay.** `kama-probe.sh check` is a documented read-only registry reconciliation with the stated `0/2/1` exit codes; the supplement explicitly forbids replaying the 34113 samples as current and restricts readiness re-probing to an operator-authorized base URL. This avoids KQ11's `obsolete config-body read revived as a current recheck` failure mode.
- **The scope note is accurate.** `:44` says the retained bytes are the readiness/metrics field fragment (`/health`, `/props`, `/slots`, `/metrics`), not the served-id reconciliation procedure. The original fragment indeed contains no `/v1/models`, alias, or path comparison. `corpus/README.md:102-106` independently records the same correction.
- **The sample's field projections are disclosed.** `:5` says the commands `select only the reported fields; their outputs are exact for those commands`; the `/props` projection is explicitly a field selection, not a claim to be the raw object. This is honest about what the retained bytes are.

## Execution / tools record

- No tools were installed or upgraded; **actual install record: none**.
- No public URL was assigned to this seat and none was opened; all evidence is local repository metadata. No endpoint was contacted.
- No `measure.py`, selftest, `kama-probe.sh`, test, lint, or formatter was executed. The parent owns measurement and acceptance.
- Only read-only commands were used: `git status/diff/show/merge-base/log`, `sha256sum`, `cmp`, `wc`, `stat`, `jq`, `nl`, `grep`, and file reads. The sole write was this advisory report.

## Limits

- The negative `No endpoint contacted` is the author's stated method. No repository evidence contradicts it, and the supplement cites only retained files, but the negative itself cannot be independently verified from local files.
- The C2 crosswalk's vendor-documentation semantics (OpenAI, llama.cpp, Ollama rows) are assigned to source seats; this review did not reopen or adjudicate those sources.
- The target changed during review (2462→2537 bytes; same 1221-byte prefix). The report assesses the 2537-byte working-tree version pinned above; a later edit can invalidate the line anchors, so the parent should re-read before integration.
- This report is advisory. It does not run the round-11 measurement, decide acceptance, or modify corpus/implementation files.
