# Provenance1 — advisory verification (kama round-11 inherited work)

Status: advisory only. Acceptance and score measurement remain the parent's.
Seat: `Provenance1` (leaf). Wave: `kama-round-11-verification`.
Review time: 2026-10-20 (UTC), read-only.
Target: `corpus/knowledge/alias-endpoint-normalization.md` — appended `## Provenance supplement — round 11 (2026-10-19)` at lines 66–72; baseline body lines 1–64.
Standard: `corpus/QUALITY.md:38` (KQ11) plus the current lane row in `../shokunin.conf` — `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)` — not the historical MISSION example.

Advisory verdict: **KQ11-conformant / honest.** The supplement preserves the original byte prefix, dates every historical observation it cites, explicitly separates metadata review from live revalidation, and names a bounded registered recheck plus an explicit unavailable surface for alias-row re-derivation. One low-severity completeness note (F1) on the round-3 commit summary; it falsifies no claim and fails no KQ11 criterion. For this file, the C1 calibration claim holds: its three missing fields are now present, the 7595-byte original prefix is byte-identical, and no runtime freshness is claimed. The other eight legacy files were not audited here.

## Axes

1. **Source honesty** — every in-repo pointer and commit cited by the supplement resolves as described.
2. **Temporal separation** — original observations dated 2026-09-28 / 2026-10-14 / 2026-10-19; review dated 2026-10-20; no observation refreshed.
3. **Byte-prefix integrity** — original 7595 bytes preserved exactly.
4. **Recheck boundedness** — registered read-only gate named but not executed; alias re-derivation explicitly deferred; metadata-only commands enumerated.
5. **KQ11 negative controls** — no field-presence-only evidence, no `source: none`, no revived config-body read presented as current.

## Evidence (read-only; no gate executed)

### 1. Original byte prefix

```text
sha256sum corpus/knowledge/alias-endpoint-normalization.md
  724ce931c1dd921dfda03ef400b8c3646d83745f2cc4c472913b028fda544131  (current, 10729 bytes, 72 lines)
sha256sum .ufo/waves/round-11/frozen/before/corpus/knowledge/alias-endpoint-normalization.md
  a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93  (7595 bytes, 64 lines)
head -c 7595 <current> | sha256sum
  a441829c75fd6c7780c44411cf93f79ee863d7bebdbe8804229b93dabf08ff93
cmp <(head -c 7595 <current>) <frozen-before>  =>  PREFIX_IDENTICAL
git diff --numstat -- <file>  =>  8  0  <file>
```

`legacy-baseline.json` records the same `a441…` / 7595 bytes and `missing: [source, verified-at, recheck]`. The supplement's claim “preserved byte-for-byte by this append” is exactly true: the append is +8/−0 and the pre-append 7595 bytes hash to the recorded baseline. The table still holds 23 alias rows, and `m_flash` is still at line 11 (`charm-hyper/deepseek-v4.1-flash:max`), matching the supplement's A48 anchor.

### 2. Temporal separation

- Heading line 66 says `(2026-10-19)`; line 69 discloses that the actual review date is `2026-10-20T02:14Z` and that the heading retains the steered label date. Both dates are visible; nothing is backdated silently.
- Append mtime is `2026-10-19 23:24:07.663688769 -0300` = `2026-10-20T02:24:07Z`; the claimed review timestamp precedes the append by ~10 minutes, consistent with review-then-append.
- Wave artifacts (`spec.json`, `legacy-baseline.json`) were created `2026-10-19 23:12 -0300` = `2026-10-20T02:12Z`, consistent with “the round-11 wave executed 2026-10-20 UTC”.
- The supplement adds no host observation and says “no live revalidation is claimed and no observation here is refreshed”; the only new measurements it reports are repository-byte metadata (hash/size), which is metadata review, not runtime evidence.
- Original observation dates are listed: 2026-09-28 (round-1 alias census and loopback grep), 2026-10-14 (errata re-measure), 2026-10-19 (round-10 A16–A18). All three are independently supported (below).

### 3. Cited pointers resolved

| Supplement citation | Observed evidence | Result |
|---|---|---|
| `LOG.md:77-80` — round-1 ledger, `KamaDistillerAliases`, no loopback alias, `m_flash` caught stale | `LOG.md:77-78` (`KamaReviewerCitations` … `m_flash` is `charm-hyper/…`); `LOG.md:79-80` (`KamaDistillerAliases` … “no alias resolves to loopback today”). The range covers both statements. The quoted “today” is a 2026-09-28 ledger statement; the supplement does not present it as current. | PASS |
| `corpus/lessons/round-1.md:3-4,70-72` — F11 re-derivation, live line 24 `charm-hyper/…` | Lines 3–4 ground round 1 in a 2026-09-28 command run; lines 70–72 say F11 is stale and live line 24 is `charm-hyper/deepseek-v4.1-flash:max`. | PASS |
| `corpus/lessons/round-1-citations.md:17,28` | Line 17 is the F11 row (live line 24 `charm-hyper/…`); line 28 is the “Incorrect frozen citation” bullet. | PASS |
| `corpus/lessons/round-4-recensus.md:79` — round-10 A48 re-anchor to this file's line 11 | Line 79 is A48, whose `current anchor` is `corpus/knowledge/alias-endpoint-normalization.md:11`; line 11 is the `m_flash` row. | PASS |
| `.ufo/round-10/audit/stale-anchors.tsv:16-18` — A16–A18, 2026-10-19 | Lines 16–18 are exactly A16/A17/A18 for this file, at source lines 46/47/48. Body lines 46–48 (inside the preserved prefix) are exactly the `MISSION.md:37-43`, `/tmp/fleet-override.yml`, and `config/l1-max-context.yml:19-22` statements being corrected. | PASS |
| `c6199a2` round 1, 2026-09-28, table already 23 rows | Commit date `2026-09-28T23:15:05-03:00`; `git show c6199a2:…` has 23 `\| \`m_…` data rows; `m_flash` is line 11 with `charm-hyper/deepseek-v4.1-flash:max`. | PASS |
| `ea72c3e` round 3 errata, 2026-10-14, paths relocated, “today” dropped, errata line added | Commit date `2026-10-14T09:46:23-03:00`; diff +5/−3; grep paths changed `origin-work/ufo-fsd-alpha` → `ufo-fsd-alpha`; “today” removed from the answer sentence; `2026-10-14 errata:` paragraph added. The commit also edits step 4 (see F1). | PASS for stated changes; F1 completeness note |
| `1e41928` round 10, 2026-10-19, appended A16–A18 only | Commit date `2026-10-19T19:34:42-03:00`; diff +8/−0; adds the `## Corrections — round 10` heading and exactly A16–A18, no deletions. | PASS |
| Host surface `~/.omp/agent/config.yml:21-44` “not retained in this repository” | `grep -rln 'modelRoles:'` over the repo returns no file; only the derived 23-row table (lines 5–37) and the F11 excerpt in `round-1-citations.md:17` exist. The live config body is not retained; excerpted derived evidence is what the supplement cites. | PASS |

### 4. Bounded recheck / unavailable surface

- `tools/kama-probe.sh` exists (47,443 bytes); usage and parser expose `check` (lines 18, 92), `--json` (lines 25, 97, 119), and the default registry `registry/endpoint-consumers.tsv` (lines 59, 101).
- `registry/endpoint-consumers.tsv` exists (36 lines); its data rows are declared loopback consumers (`http://127.0.0.1:8080`, `http://127.0.0.1:34113/...`), so “declared loopback consumers only” is accurate.
- The supplement says the check was **not executed** by this seat and defers it to the next authorized correction round; it defers alias-row / loopback-baseURL re-derivation to an operator/kumitate handoff with approved shape-only tooling; its permitted metadata commands are `test -e /tmp/fleet-override.yml`, `stat -c '%s %y' …/l1-max-context.yml` (size/mtime only), and `test -e ../MISSION.md`. These are bounded and read-only; the first expects the known dead surface.
- I did not run `tools/kama-probe.sh check` and did not contact any endpoint or listener.

## Findings

### F1 — low severity: round-3 commit summary is non-exhaustive (not a KQ11 failure)

Path: `corpus/knowledge/alias-endpoint-normalization.md:68` (the `source:` line).

The supplement describes `ea72c3e` as three changes. The commit's second hunk also changes body line 48 (Normalization step 4): `Apply the origin-work project config and mission overlays…` → `Apply the project config and mission overlays…`, and re-prefixes `mission-nightcall.yml:4-5` → `config/mission-nightcall.yml:4-5 … (re-measured 2026-10-14)` and `l1-max-context.yml:19-22` → `config/l1-max-context.yml:19-22`. That hunk is 1 insertion / 1 deletion of the commit's 5 / 3.

Severity: low. The sentence is a summary, every stated change is true, and the omitted edit is the same 2026-10-14 path relocation/errata — no date, source, or freshness claim is falsified. Smallest repair (optional, one clause): append to the parenthetical “and re-prefixed the step-4 overlay paths to `config/…` with a `(re-measured 2026-10-14)` marker”. No other semantic defect found.

### Checked not defects (so the parent does not re-litigate them)

- “no alias resolves to loopback” is quoted from a 2026-09-28 ledger line that contains “today”; the supplement cites it as history and the `verified-at` line bars refreshing it.
- “not retained in this repository” is about the live host surface, not about derived excerpts; the repo has no `modelRoles:` body file.
- The heading's 2026-10-19 label versus the 2026-10-20 review date is disclosed in the same supplement, not concealed.
- The supplement's unfalsifiable self-attestations (“not re-read”, “no surface contacted”) are consistent with every observable artifact; no contradiction was found.
- The recheck names a live read-only gate for the *next* round, not a claim that it ran now; “nothing executed by this seat” is explicit.

## What is already correct

- Original prefix: 7595 bytes, hash `a441829c…f08ff93`, byte-identical to both `legacy-baseline.json` and the frozen copy.
- Provenance trio: `source:` (68), `verified-at:` (69), `recheck:` (70) are present as single fields and are the three fields baseline listed as missing.
- Historical dates: all three observation dates stated and separately evidenced.
- Metadata vs live: explicit sentence “Metadata review only … no live revalidation is claimed and no observation here is refreshed.”
- Negative controls: no field-presence-only evidence; no `source: none`; the old config-body read is explicitly *not* revived as a current recheck.
- Closing note (line 72) and the +8/−0 diff agree: no byte above rewritten, no observation refreshed.
- The baseline hash/size claim matches `legacy-baseline.json` and the frozen copy exactly.

## Risks and blockers

- None blocking this review. Residual by design: live alias rows remain unverified until the authorized handoff or registered check runs; the supplement states this rather than hiding it.
- Parent still owns post-integration measurement; my hash/prefix comparison is evidence for the supplement's own claim, not a score measurement.

## Scope discipline / tooling record

- Only this report was written; no implementation, corpus, registry, or fleet files were modified.
- No builds, lints, tests, formatters, or gate checks were run; `tools/kama-probe.sh check` was not executed; no endpoint, listener, probe, or dispatch surface was contacted; the host routing config was not opened.
- No public URL was assigned to this seat and none was opened; all evidence above is in-repo or command-derived.
- No tool installs or upgrades by this seat.
