# Provenance3 — KQ11 verification: `corpus/knowledge/cross-lane-scope.md`

**Seat:** KamaR11.Provenance3 (leaf). **Date:** 2026-10-20 UTC.
**Scope:** `corpus/knowledge/cross-lane-scope.md` only — its round-11 provenance supplement (lines 81–87), its historical pointers, and QUALITY KQ11.
**Mode:** advisory, report-only. No implementation/corpus edit, no build/lint/test/formatter/gate execution, no endpoint/listener/consumer/probe/dispatch/network contact, no delegation. No tools installed or upgraded; no install record. Not a source role: no public URL was assigned; no URL was opened.

## Verdict

**PASS (advisory): the supplement is honest, temporally separated, and its recheck is safe and bounded. No semantic defect found.** The one unexecuted condition is the byte-prefix sha256, which belongs to the parent's measurement (not run by this seat). Outside non-author review remains separate.

## 1. Prefix preservation — logical proof (hash deferred to parent)

| Evidence | Value | Source |
|---|---|---|
| Baseline entry | `bytes: 18448`, `sha256: 97c7a8138c792a8df6c9608b0933aa0cd5623a09afbf6a6fceb98f66357e02a0` | `.ufo/waves/round-11/legacy-baseline.json` |
| Frozen before-copy | 18448 B, 79 lines; tail bytes `...45-49`]*\n` | `.ufo/waves/round-11/frozen/before/corpus/knowledge/cross-lane-scope.md` (mtime 2026-10-19 23:14:33 -03) |
| Current file | 22502 B, 87 lines | `corpus/knowledge/cross-lane-scope.md` |
| Append boundary | heading line 81 starts at 0-based byte offset **18449**; line 80 is a bare `\n` | `grep -b`, `od -c` |
| Diff vs HEAD | `@@ -79,0 +80,8 @@` — 8 insertions, **0 deletions** | `git diff -U0 -- corpus/knowledge/cross-lane-scope.md` |
| History | `c6199a2` 2026-09-28 blob 13089 B → `1e41928` 2026-10-19 blob 18448 B | `git log`, `git cat-file -s` |

Therefore current bytes `[0,18448)` are the original extent, byte 18448 is the separator newline, and no original line was rewritten. Exact byte equality is the parent's measurement: `head -c 18448 corpus/knowledge/cross-lane-scope.md | sha256sum` must print `97c7…02a0`. **This seat did not execute that measurement.**

## 2. KQ11 clause assessment

| KQ11 clause | Status | Evidence in the supplement |
|---|---|---|
| Preserve original byte prefix | Pass (logical) | §1; prefix hash pending parent |
| Identify historical observation dates or unknown dates | Pass | 2026-09-28 (round-1/3/4) and 2026-10-19 (A25–A37); “the 8080/34113 endpoint state is historical” (line 84) |
| Distinguish metadata review from live revalidation | Pass | “Metadata review only”; “No endpoint, listener, consumer pin, probe or dispatch surface was contacted”; “no live revalidation is claimed” (line 84) |
| Name a bounded current recheck or explicit unavailable surface | Pass | line 85: bounded `head -c 18448`, bounded `sed` ranges, `wc -l`; live probe explicitly deferred to an operator-authorized probe round |
| No KQ11 anti-pattern | Pass | Not bare field presence; no obsolete config-body read revived; host surfaces explicitly “not re-read in round 11” (line 83) |

## 3. Source honesty — claim by claim

| Supplement claim | Retained evidence | Result |
|---|---|---|
| round-3 kagi endpoint drift; “committed 2026-09-28” | `.ufo/reports/round-3/kagi.md:23-27` (8080 Jitsi/Jetty 404, llama-server 34113); `git -C ../kagi-shokunin show 06ef644` → 2026-09-28 | Verified |
| round-4 kengaku “dated `Date: 2026-09-28`”; drift + eval | `.ufo/reports/round-4/kengaku.md:3` and `:18-25` | Verified |
| round-1 report: 8080 = docker-jitsi JVB; 34113 = llama-server pid 1299 | `.ufo/reports/round-1/kama.md:47` (`docker-jitsi-meet-jvb-1`), `:51` (`llama-server` pid 1299) | Verified |
| `corpus/lessons/round-1.md:3-4` (commands run 2026-09-28) | `:3-4` state all rules grounded in a command run 2026-09-28, ledger `listener-census.md` | Verified; **0 literal `L1-F` tokens** here (see N2) |
| `round-1-critic.md`, `round-1-safety.md`, `probe-mutation-matrix.md` | L1-F occurrences: 3, 5, 6 respectively | Verified |
| `round-1-citations.md:17,28` (F11 re-derivation) | `:17` F11 citation row; `:28` F11 incorrect-frozen-citation correction | Verified (labels are `F11`, not `L1-F11`; supplement says “F11 re-derivation”) |
| `consumer-registry.md` (F1/F2/F11) | `:279` confirms L1-F1/F2; `:327` confirms L1-F11 | Verified |
| “no standalone round-1 bundle is retained in this repo” | `find` shows only `corpus/lessons/round-1*.md`; no bundle artifact | Verified |
| A25–A37 ledger at `.ufo/round-10/audit/stale-anchors.tsv:25-37` | Rows A25–A37 all name `corpus/knowledge/cross-lane-scope.md` | Verified |
| Re-anchor targets `consumer-registry.md:56-76`, `SKILL.md:35-47`, `PROVINCE.md:45-49` | Deleted consumers/ports-dead section; current `check` sample; write-boundary paragraph | Verified |
| Pointer bounds 390 / 344 / 52 / 67 | Frozen consumer-registry 390 lines (39951 B); current SKILL 344, PROVINCE 52, MINT 67 | Verified at review baseline (see N1) |
| `bash tools/kama-probe.sh check` | 47443 B, mode 0755; usage line 88 and `check` line 92 | Verified |

## 4. Temporal separation

- Heading `2026-10-19` is the spec-mandated steered label; `verified-at: 2026-10-20T02:14Z` is stated as the actual review date and reconciles the two (line 84).
- Wave timing corroborates: `dispatch.json` mtime 2026-10-19 23:13:17 -03 = **2026-10-20T02:13Z UTC**; frozen copy 23:14:33 -03; file 23:20 -03; today is 2026-10-20 UTC.
- Original observations are separately dated (2026-09-28 for round-1/3/4; 2026-10-19 for A25–A37) and the endpoint state is explicitly labeled historical. **No runtime freshness claim.**

## 5. Recheck safety and precision

- All local, read-only, no network: `head -c 18448` (18 KB bound), two bounded `sed` ranges, one `wc -l`.
- The `sed` ranges were verified to contain the cited content: `round-3/kagi.md:23-27` is the drift bullet; `round-4/kengaku.md:18-25` is the drift proof/eval item.
- The live portion is named precisely and explicitly deferred to an operator-authorized probe round (`bash tools/kama-probe.sh check` plus re-derivation against `consumer-registry.md`); it is not claimed to have run. No placeholder.

## 6. Parent gate compatibility (read from `measure.py`, not executed)

- `first_line_column_zero` is true: `data[18447:18448] == b"\n"` (frozen tail ends `]*\n`), so the appended region starts cleanly with the blank-line newline.
- Heading matches `^##\s+Provenance supplement\b` exactly once (line 81; grep count 1); no triple-backtick fences in the region (count 0).
- Exactly one column-zero `source:` (83), `verified-at:` (84), `recheck:` (85).
- The live-claim guard requires “live revalidation” immediately followed by `today` or the run date; the line reads “no live revalidation is claimed” with a non-date continuation, so `_live_claim_re` cannot match. Guard passes.
- The only unexecuted gate condition is the prefix sha256.

## 7. Findings

**Semantic defects: none.**

- **N1 (info, no repair required):** the recheck's third leg (`wc -l consumer-registry.md SKILL.md PROVINCE.md`) states no pass predicate, and `consumer-registry.md` has since grown 390 → 395 lines / 41760 B because a concurrent sibling appended its own complete supplement (trio at lines 393–395). The `verified-at` figure 390 was true of the frozen baseline (390 lines / 39951 B at 23:14:33), and the cited anchor range `:56-76` remains in bounds, so honesty is intact. If the parent wants a self-contained pass condition, the smallest wording is “≥76 lines and lines 56–76 still hold the deleted-consumer/ports-dead section.” **I made no edit.**
- **N2 (info):** `corpus/lessons/round-1.md:3-4` carries 0 literal `L1-F` labels; it supplies the command-run date and ledger pointer. The supplement's parenthetical scopes it correctly (“commands run 2026-09-28”), so this is not an overclaim.
- **N3 (expected):** the exact prefix hash was not executed here per assignment; §1 shows the logical chain and names the parent command.

## 8. Already correct

Spec-exact heading, column-zero trio with one occurrence each, all cited pointers resolvable with matching dates/line ranges, history sizes/dates verified, recheck bounded and network-free, live revalidation explicitly deferred and never claimed, original byte prefix logically preserved with a pure-append diff.

## 9. Files, tooling, limits

- **Files changed:** this report only.
- **Installs/upgrades:** none; no install record.
- **Checks executed:** none (no build, lint, tests, formatters, or acceptance gate). Inspection was read-only: `cat`, `stat`, `wc`, `grep`, `sed`, `od`, `git show/diff/cat-file`, `find`; no network or host endpoint probe.
- **Limits:** advisory only; parent owns measurement, integration, and acceptance; outside non-author review remains separate.
