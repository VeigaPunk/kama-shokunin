# Provenance4 — advisory verification of `corpus/knowledge/drift-timeline.md` round-11 supplement

Seat: `KamaR11.Provenance4` (leaf executor, kama round 11 wave). Advisory only; author-side, not an outside non-author verification (QUALITY.md §Review boundary).

**Review access:** 2026-10-20 03:45 UTC (`date -u`). No network, no endpoints, no host configs, no probe execution, no builds/tests/lint/formatters. No installs or tool upgrades. Nothing edited outside this report.

**Scope:** the appended `## Provenance supplement — round 11 (2026-10-19)` block (`corpus/knowledge/drift-timeline.md:30-34`), the original 28-line historical body (lines 1-28), and KQ11. Baseline compared logically and by bytes against `.ufo/waves/round-11/frozen/before/corpus/knowledge/drift-timeline.md`, `.ufo/waves/round-11/legacy-baseline.json`, and `git show HEAD:corpus/knowledge/drift-timeline.md`.

## Verdict

Substantially honest supplement: original bytes are preserved exactly, the metadata review is explicitly separated from the 2026-08-20 → 2026-09-28 observation window, no runtime freshness or served-model claim is made, and the named recheck is a real, bounded, read-only lane command. One MEDIUM source-honesty defect (a false universal about why the table is not rerunnable) and three LOW precision nits; none asserts current endpoint state.

## Retained evidence — what is correct

| Check | Evidence (read-only, this session) | Result |
|---|---|---|
| Original byte prefix preserved | `sha256` of first 7428 bytes of current file = `a161615286428054f834b0d9e9be9261ce0a52a631cd8fe11bde2d277d214df7`; identical to `frozen/before` sha, `legacy-baseline.json` entry, and `git show HEAD:` sha | **exact**, including original trailing LF |
| No mid-file edits / append-only | `wc -c` 9818 = 7428 + 2390 appended; `wc -l` 34; frozen prefix ends `...consumer-registry.md:62-65`]*\n`; append starts at line 29 (blank) then heading line 30; current EOF ends `\n` | **pass** (KQ7 append-only) |
| Baseline pre-state carries the missing fields control | `legacy-baseline.json` records `drift-timeline.md` 7428 bytes, sha above, `missing: [source, verified-at, recheck]` | real before-state, not post-hoc |
| Provenance trio anchored, once each | `^(source|verified-at|recheck): ` at lines 32, 33, 34, column zero, one occurrence each, after the round-10 correction (lines 26-28) | **pass** |
| `source:` pointers resolve | `LOG.md:74` `KamaRevengerTimeline` drift timeline (range 71-74, round 1 heading line 7); `LOG.md:160-161` "34113 still serves the expected llama.cpp model" (range 159-163, round 2); `LOG.md:246` "ports 34113 and 8080 both refuse connections", `:249-250` backups/`qwen-coder*` units gone (range 203-255, round 3); `registry/history/DELTA.md:20` "systemd-qwen-coder row-absent (was verdict=MODEL_OK port=34113)" (range 14-22, all 2026-10-14T12:42:32Z; file tracked per `git ls-files`); `consumer-registry.md:100` epoch/fossil quote and `:120-123` rows 31-34 | all quoted text located verbatim; ranges contain the quote |
| Observation dates identified / unknown dates retained | Body rows lines 7-20 each dated; the three `2026-09-28 (mtime not collected ...)` rows keep their unknown mtime; supplement states the window 2026-08-20 → 2026-09-28, last row 2026-09-28 | **pass** |
| Metadata review vs live revalidation separated | `verified-at` line 33: review 2026-10-20 02:14 UTC vs steered heading date 2026-10-19; "no endpoint, listener, systemd unit, docker container, or backup file was re-read"; no live revalidation claimed; review clock is consistent with my 03:45 UTC read | **pass** (KQ11 temporal separation) |
| Bounded recheck is real and safe | `tools/kama-probe.sh` exists (47 KB, executable); `check` subcommand + `--json` flag accepted (`parse_args`, usage lines 86-106); default registry `registry/endpoint-consumers.tsv` (line 59) holds 3 surviving rows; header lines 9-11: read-only toward live services/configs, writes only to a removed mktemp dir; bounded curl defaults `--max-time 5`, `--connect-timeout 2` | command is valid and bounded, not a placeholder |
| Expected-reading citation | `registry/history/latest.tsv:2-4` = the three rows `DEAD  connection-refused` | **pass** (dated 2026-10-14T12:42:32Z snapshot) |
| No freshness claim | No row restated as current; supplement explicitly disclaims; `source:` says retained historical record only | **pass** (KQ1/KQ4/KQ11) |

## Defects

### D1 — MEDIUM — line 34 overstates the deletion basis with a false universal

`recheck:` says: "every per-row command in lines 7-20 targets a host artifact recorded gone (`LOG.md:245-255`)". Three counterexamples, all from the cited record:

- **line 17** `~/.config/opencode/opencode.json`: `LOG.md:247` records it **exists**, reshaped to 5 lines with no `qwen-local` provider. Its per-row grep still runs; it just no longer reproduces the dated pin. "Gone" is false; "materially changed" is true.
- **line 11** `~/.config/llama/qwen-coder-godspeed.jinja`: no fate recorded anywhere in `LOG.md` (repo-wide grep for `qwen-coder-godspeed.jinja` finds only the timeline row and `lessons/round-1-safety.md:11`); `LOG.md:245-255` does not list it. Present existence is unknown, neither asserted nor denied.
- **line 15** `docker-jitsi-meet-jvb-1`: `LOG.md:246` only records that 8080 refuses connections; no container removal is recorded. `docker inspect` on a stopped container would still run.

The author's own advice concedes this: `.ufo/waves/round-11/advice/Legacy4.md:48` states rows 11 and 15 "are not covered by the `LOG.md:245-255` deletion list" and says "the recheck line no longer names them" — but the final line 34 still makes the universal claim.

Impact: calibration/source honesty, not freshness — it overstates the evidence for "not rerunnable". No current-state claim is introduced.
**Smallest repair (line 34):** replace the universal with a scoped one, e.g. "the per-row commands that target deleted paths — all `opencode.json.*.bak*`, the janitor/agent files, and `qwen-coder*` units (`LOG.md:245-255`) — are never replayed; line 17's file survives reshaped (`LOG.md:247`), so its dated grep is historical, not current; lines 11 and 15 have no recorded present state and stay dated evidence only."

### D2 — LOW — line 32 "the four `opencode.json.*.bak*` observations"

The timeline's lines 7-20 contain **six** opencode backup observations (file lines 7, 8, 9, 10, 12, 16); `consumer-registry.md:120-123` copies four of them. Also `opencode.json.bak-20260921-devin-slots` (row 34) does not match the literal glob `opencode.json.*.bak*` (it has no `.<x>.bak` segment). **Repair:** "four of the six backup observations, matching `consumer-registry.md:120-123`", dropping the glob.

### D3 — LOW — line 34 "expected reading while nothing listens"

The supporting snapshot is `2026-10-14T12:42:32Z`, six days before the review. The conditional "while nothing listens" reads as a present-state premise even though nothing is asserted. **Repair:** "the last recorded run (`latest.tsv:2-4`, 2026-10-14) read DEAD/connection-refused on all three rows; a fresh `check` is compared against that baseline, not treated as continuous monitoring."

### D4 — LOW — "read-only probe" scope

Line 34 names `bash tools/kama-probe.sh check --json` as read-only (true: script header lines 9-11) and then `bash tools/kama-probe.sh snapshot`; snapshot **writes** dated JSON/TSV/DELTA under `registry/history/` (script header lines 40-46, usage line 93). **Repair:** "`snapshot` persists a dated baseline under `registry/history/` for invocation-to-invocation drift."

## KQ11 conformance summary

- Original byte prefix preserved: **yes**, exact SHA-256 and byte count.
- Historical observation dates / unknowns identified: **yes** (lines 7-20 carry dates; unknown mtimes stay marked; supplement states the window).
- Metadata review distinguished from live revalidation: **yes** (explicit, no freshness claim).
- Bounded current recheck or explicit unavailable surface: **yes** — valid command, 3-row registry, bounded timeouts — but its rationale carries D1.
- New-entry trio rule: N/A (legacy file, append-only correction-style placement).
- Missing-field and altered-prefix controls: the baseline artifact supplies both a genuine missing-trio pre-state and a prefix identity the measure can test; the supplement's own "preserved byte-for-byte" claim is verified true.

## Risks / blockers

- D1 is the only repair worth parent attention before acceptance; it is a one-clause edit on line 34 and does not require touching original bytes.
- D2-D4 are wording calibration, optional.
- Anchors `consumer-registry.md:100` and `:120-123` currently resolve; they remain stable only under the contract's append-only rule if that file's own supplement is appended at EOF (out of this seat's scope).
- No blocker; no tool installation or update was needed or performed.
