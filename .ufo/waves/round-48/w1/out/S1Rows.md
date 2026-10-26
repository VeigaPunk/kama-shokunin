# S1Rows — round 48 (kama-r48-w1): re-open S492 and S493

**Verdict: both registry rows hold up on the live sources — every located quote is verbatim and ≤ 25 words, S492 is right in all 11 cells — but two cells are not yet true at the built tip: the rows' `used-by` names `corpus/lessons/round-48.md`, which is absent from the tree at `380bcdff9c8af06997c482f6eb03db926a794a2b` (census `validate` therefore exits 1 with `E11` ×2), and S492's `used-by` also names a knowledge file that does not cite it yet; S493's `teaches` carries one unsupportable clause, for which a validated replacement row is drafted.** Per-cell matrices, quote counts, gate entries and the replacement row are in `w1/out/S1Rows/rows.md`.

## Findings

### F1 (gate, blocking) — the two new rows' `used-by` does not exist at the tip: `sources-census.sh validate` exits 1

- Evidence: `git -C lane ls-tree 380bcdff9c8af06997c482f6eb03db926a794a2b corpus/lessons/ | grep round-48.md` → **0 matches**. The file exists only as an untracked working-tree file (`git -C <lane> status --porcelain` → `?? corpus/lessons/round-48.md`). `corpus/SOURCES.md` is one blob (`4c70f9c81e73dc53e7979db543bc7ceb2e1e8098`) at `380bcdff` and at lane HEAD `b85783e8`, so the rows are as integrated and the gap is the lesson, not the row text.
- Command that shows it:
  `bash scripts/sources-census.sh validate --file $S/lane/corpus/SOURCES.md --today 2026-10-26`
  → exit **1**, lines `file E11 S492 missing used-by corpus/lessons/round-48.md` and `file E11 S493 missing used-by corpus/lessons/round-48.md` (copy `w1/out/S1Rows/validate-tip-noLesson.tsv`). With the lane's untracked lesson copied into the same clone the same command is exit **0** (`rows 234`, `ok 1`, `W01` S481, `W04` ×93 — all pre-existing; copy `validate-tip-withLesson.tsv`).
- Why it is not the known items you listed: it is neither gate-registry (the two round-48 counters), nor the 33-vs-34 spot-check count, nor hexrun `d0012618`. It is the only `E`-code the registry emits.
- Proposed fix (lane side, at closure): land `corpus/lessons/round-48.md` in the same commit as the round's registry rows (the draft already sits in the working tree, 5836 bytes, `author: kama L1 (agent KamaR48)`), then re-run the gate. If the lesson will not land this round, the append-only substitute is a superseding row per source whose `used-by` names files that exist at the tip (e.g. `corpus/knowledge/llamacpp-loading-lifecycle.md`); that is a weaker fix and leaves the round without a lesson.

### F2 (cell accuracy) — S493's `teaches` turns a library rule into a URL rule

`corpus/SOURCES.md:246` teaches: `"When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." — so a pinned provenance URL records the 40-hex commit, as the v5 receipt and the live tool's pin rule do`.

- The quote is exact (17 words, present verbatim in the served page and in `.ufo/waves/round-48/c2/hf-hub-download-doc.txt:5`). The clause after the dash is not something the page says: the documented subject is the `revision=` argument of `hf_hub_download`.
- What I measured: `curl -sSI` on `…/resolve/499bc88/tinyllamas/stories260K.gguf` → `HTTP 302` with `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and the same `x-linked-etag`; `GET /api/models/ggml-org/models-moved/revision/499bc88` → `HTTP 200`, `"sha":"499bc8821c6b12b4e53c5bffcb21ec206f212d81"`. A 7-character revision therefore *works* on both the API and the resolve path today (`2026-10-26T22:36:44Z`); the full-length rule is the client library's, and kama's 40-hex URL pin is kama's own convention (`tools/kama-llamacpp-live.py:71` `PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')`, refusal at `:1477`), with the commit binding actually evidenced by S492's `x-repo-commit`.
- Why it matters for operability: read as filed, the row says a short pin is not served; a later seat could cite S493 to explain a 404 that would not happen, or could treat the 40-hex rule as externally guaranteed when it is a lane choice the tool enforces by its own regex.
- Proposed fix (append-only): replacement row **S494** — full text in `w1/out/S1Rows/proposed-row-S494.txt`, scope cell byte-identical to S493's, `teaches` corrected, quote repeated unelided, literal `supersedes S493`. Validated inserted after line 246 in my clone: `sources-census.sh validate --file … --today 2026-10-26` → exit **0**, `rows 235`, no new `E`/`W` code (`validate-proposed-S494.tsv`).

### F3 (cell not yet true) — S492's `used-by` names a document that does not cite S492

- `corpus/SOURCES.md:245` lists `corpus/knowledge/llamacpp-loading-lifecycle.md`; `grep -c S492` on that file → **0** (it cites S488/S489/S490 at line 434). The v5 paragraph is seat S9Knowledge's pending draft — `w1/out/S9Knowledge/` is empty at audit time.
- `E11` checks existence only, so this passes the validator while the claim is unrealised. Self-resolving when S9Knowledge's paragraph lands (its spec says to cite S492/S493); if it does not land, the cell overstates and needs a superseding row dropping that path.

### F4 (lesson draft, not the registry) — the draft Gate entry paraphrases its quote and has no reject

- `corpus/lessons/round-48.md:20` writes the located quote as `x-linked-etag: "270cba1b…d256d"` — elided inside quotation marks, so it is neither verbatim nor greppable (`grep -c 270cba1b…d256d` finds only this line; the full digest appears later in the same line only as the download sha). `corpus/lessons/round-48.md:16-22` (`## Gate`) carries two `Admit:` lines and **no `Reject:`**, while the round's own lesson spec asks for at least one reject.
- Proposed fix is in `w1/out/S1Rows/rows.md` §Gate: the full etag quoted verbatim, plus a reject that my measurement makes non-trivial — reject a 7-character `/resolve/<short>/` pin *because it works today* (no prefix-uniqueness guarantee, and the receipt would pin 7 characters).

## Observations (not defects, not proposed as changes)

- O1 `corpus/SOURCES.md:246` scope lists branch/tag/commit-hash where the page also demonstrates a PR ref (`revision="refs/pr/3"`), under an `e.g.` — narrower scope than the page, conservative rather than false.
- O2 S492 `recheck: every round` cannot detect drift on an immutable commit; it detects only availability/removal, which is real for a repo named `models-moved`, and costs one HEAD request. Defensible as filed.
- O3 S493's `recheck: 180d` (due 2027-04-24) and S492/S493 `opened: 2026-10-26` pass `E08`/`E09`; `every round` is an accepted symbolic cadence.
- O4 The resolve response's `x-hub-cache: MISS` / `cache-control: no-store` are outside both scopes and were not used as evidence.

## Checks I ran (all read-only against the lane; nothing written into it)

| check | result |
|---|---|
| resolve URL `curl -sSI` (full 40-hex) | 302; `x-repo-commit` = named revision; `x-linked-etag` = `270cba1b…d256d`; `x-linked-size: 1185376` |
| download + `sha256sum` | 1185376 bytes, `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` = etag = S039 line 51 |
| revision API (full and 7-char) | 200, `"sha":"499bc8821c6b12b4e53c5bffcb21ec206f212d81"` both |
| doc page fetch | 200, 170833 bytes; `<h1>` "Download files from the Hub"; `<h2>Download a single file</h2>` → `<h3>From specific version</h3>`; quote present once |
| receipt provenance (`c2/live/receipt-{1,2,3}.json`) | all `kama-llamacpp-live/v5`; `provenance.model.commit` = `499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `model.sha256` = `270cba…d256d`, `verified.at = record` |
| `sources-census.sh validate` (tip content, lesson absent) | exit 1 — E11 ×2 (F1) |
| `sources-census.sh validate` (tip content + untracked lesson) | exit 0 — rows 234, W01 ×1, W04 ×93 |
| `sources-census.sh validate` (+ proposed S494) | exit 0 — rows 235, W01 ×1, W04 ×93 |
| `sources-census.sh` census (tip + lesson) | rows 234, tier.A 223, tier.B 7, tier.C 4, status.mined 216, status.queued 8, status.rejected 11, tier.invalid 0, status.invalid 0 |

## Out of scope / not done

- Did not run C1/C2 (not this item) and did not re-derive the receipts' check results beyond their provenance block.
- Did not audit S039/S490/S488/S489 content beyond the cross-references this item needed (`S039` LFS sha256; `S490` = `resolve/main` form).
- Did not touch `corpus/SOURCES.md`, the lesson, the counters, the preregistration or the controls; the replacement row exists only in my clone and in `w1/out/S1Rows/proposed-SOURCES.md`.
- The known integration items (gate-registry registration of the two round-48 counters, the 33-vs-34 spot-check count, hexrun `d0012618`) were not re-reported.

## Tooling

No tool installed or upgraded (pacman paused host-wide; nothing was needed). Scratch `/fast/scratch/hyaku/kama-r48/S1Rows` removed after collecting evidence.

## Artifacts

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Rows.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Rows/rows.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Rows/{hf-head.txt,h-499bc88.txt,h-499bc8821c6b12b4e53c5bffcb21ec206f212d81.txt,api-499bc88.json,api-499bc8821c6b12b4e53c5bffcb21ec206f212d81.json,rev-api.json,model-sha256.txt,hf-doc-from-specific-version.txt,validate-tip-noLesson.tsv,validate-tip-withLesson.tsv,validate-proposed-S494.tsv,proposed-SOURCES.md,proposed-row-S494.txt}`
