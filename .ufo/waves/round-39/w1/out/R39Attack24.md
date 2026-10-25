# R39Attack24 — read-only source boundary

Executor findings on committed/working evidence only (read-only observations; no edits to source, no spawn). Axes: calibration, coverage. Milestone: r39 claim falsification.

## 1. Source identity and liveness (S472)

- Live fetch of the S472 URL `https://developers.openai.com/api/reference/resources/models/methods/list/index.md` → HTTP 200, `text/markdown; charset=utf-8`, **1,657 bytes**.
- sha256 of the live fetch = `2bbf06bb7a1687dbc9d25ce86c5d249b3f9d1e2c60efc32dbf7af2e4d052793f` — **byte-identical** to the archived `assimilation/openai-list.md` (same sha). Recorded fetch is a faithful, byte-exact source capture.
- Quote resolves at Markdown line 17: `The Unix timestamp (in seconds) when the model was created.` (10 words), and that exact byte string also occurs once inside the raw HTML archive `assimilation/openai-list.html` (609,612 B, `<title>List models | OpenAI</title>`). The 609,612 B count matches the fleet r16 amendment's recheck note.
- No endpoint contacted beyond the read-only GET of the public Markdown source.

## 2. Committed base controls (verified against 6a4afdfe)

- Base `corpus/SOURCES.md`: **203** registry rows, zero S472 matches. Working tree: **204** rows (exactly one new row S472).
- Base lacks `corpus/lessons/round-39.md`, `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`, any README pointer to the amendment, and any "round 39" README text (grep counts 0). Matches the C1/C2 "base lacked pointer, entry and row" claim.
- `c1-noop.out` (`admit=0 reject=0 source_rows=203 met=False exit=1`) and `c2-noop.out` (`coverage_block=0 file_exists=0 cited_new=0 met=False exit=1`) receipts match recorded values; `preregistration-frozen.json` ≡ `preregistration.json` (identical sha256).

## 3. Working evidence (lane scratch, all uncommitted)

- S472 row in working `corpus/SOURCES.md` matches `assimilation/SOURCES-addition.md` exactly (11-column contract, `mined`, 90d, used-by = the amendment path).
- `corpus/README.md` adds exactly one coverage-map table row (`knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` | `created` catalog metadata | round 39) plus a "Frontier disposition — round 39" section.
- Amendment file present (3,994 B): prepended S472 header (lines 1–3), appended "## Round 39 opened-source correction — 2026-10-25" section; base lacks it.
- Validate mirror receipt shows exit 0 (W04 warnings only); `census-start.out` records exit 2 for scratch root lacking fleet config; `census-end.out` validates the fleet root OK.

## 4. Boundary observations (this item's scope)

- **No wave write into the read-only source repo.** Nothing under `/home/vgpnk/Projects/shokuknow/merge` is newer than 2026-10-25 00:00 (merge package files mtime 2026-10-24 23:33, pre-wave). The only post-midnight file in shokuknow is `lanes/tabi/round8/.work/ratelimit-series.tsv`, unrelated and part of the repo's pre-existing dirty state (1,918 modified files pre-date the wave). Source boundary holds.
- **The lane port is not a byte-faithful copy of the fleet package file named as source.** The lesson names package source `.../served-identity-crosswalk-amendment-2026-10-24-r16.md` (3,551 B, sha `9e1e7405…`); diffing that file against the lane's amendment shows **20 added / 34 removed lines** — header, source rows, and body all differ, not just an appended section. The lane body instead matches the fleet's sibling file `served-model-identity-amendment-2026-10-24-r16.md` (3,338 B): same body text, renamed `served-model-identity` → `served-identity-crosswalk` in the title, reflowed wrapping, plus the S472 front matter and round-39 appendix. The lesson's own Mistakes table ("stale-premise") independently admits the staged entry repeated a stale premise from the package narrative, consistent with a carried-over/reworked body rather than a verbatim port.
- Consequence: read *access* is clean (byte-exact web capture, no writes), but *reproduction* is an edited derivation (rename + reflow + extension). This does not falsify C1/C2 as written (they require only S472 newly cited by the amendment and pointer/entry/row added over an absent base — all observed), but it contradicts the "differs exactly by the appended correction section" fidelity claim made in R39Attack01's report.
- **Integration state:** the real project repo `/home/vgpnk/Projects/shokunin/kama-shokunin` still has 203 registry rows, no S472, and no amendment files — all round-39 evidence exists only as working-tree/uncommitted content in the lane scratch; nothing is committed at tip.

## 5. Conclusion

No falsification of the round-39 C1/C2 claims observed from this seat. The source boundary is respected on the read side: the S472 Markdown source is live, and its archived copy is byte-exact (sha match). All base-absence claims verify. The one discrepancy worth flagging is the port fidelity detail: the amendment carries a sibling file's body under a renamed title rather than a verbatim copy of the named package source — a calibration-adjacent nuance (R39Attack01's "exactly by appended section" phrasing is not byte-accurate), not a claim falsifier.
