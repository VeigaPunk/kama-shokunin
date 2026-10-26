# S1Rows — round 48 source re-open: S492 and S493

**Verdict: both rows re-verified against the live sources on 2026-10-26 — every quote is present verbatim and ≤ 25 words, S492 is correct in all 11 cells, and S493's `teaches` overreaches in one clause (a full replacement row is drafted and validates clean); the pair's `used-by` also fails the census gate at the tip because `corpus/lessons/round-48.md` is not in the tree at `380bcdff9c8af06997c482f6eb03db926a794a2b`.**

Registry rows under audit (lane working tree, file `corpus/SOURCES.md`):

- line 245 — S492, HF `ggml-org/models-moved` `stories260K.gguf` pinned to revision `499bc8821c6b12b4e53c5bffcb21ec206f212d81`
- line 246 — S493, huggingface_hub guide *Download files from the Hub*

## Method (all read-only against the lane; every write went to `$S` = `/fast/scratch/hyaku/kama-r48/S1Rows`)

| # | command | outcome |
|---|---|---|
| 1 | `curl -sSI -o hf-head.txt -w 'HTTP %{http_code}\n' https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` | `HTTP 302`, `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81`, `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`, `x-linked-size: 1185376`, `location: https://us.aws.cdn.hf.co/xet-bridge-us/...`, server `date: 2026-10-26 22:34:14 GMT` |
| 2 | `curl -sS -o rev-api.json -w 'HTTP %{http_code}\n' https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc8821c6b12b4e53c5bffcb21ec206f212d81` | `HTTP 200`; `"sha":"499bc8821c6b12b4e53c5bffcb21ec206f212d81"`, `"lastModified":"2025-10-28T10:43:38.000Z"`, `private:false`, `gated:false`, `disabled:false`, 29 siblings incl. `tinyllamas/stories260K.gguf` |
| 3 | `curl -sSL -o stories260K.gguf -w 'HTTP %{http_code} size=%{size_download}\n' <same resolve URL>` then `sha256sum stories260K.gguf` | `HTTP 200 size=1185376`; `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` |
| 4 | same resolve URL with the 7-char revision `499bc88` | `HTTP 302`, same `x-repo-commit` (**full** hash), same `x-linked-etag`, same CDN location |
| 5 | `curl -sS -o api-499bc88.json -w '%{http_code}' https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc88` | `HTTP 200`, `"sha":"499bc8821c6b12b4e53c5bffcb21ec206f212d81"` — the 7-char prefix resolves too |
| 6 | `curl -sSL -o hf-doc.html -w 'HTTP %{http_code} size=%{size_download}\n' https://huggingface.co/docs/huggingface_hub/en/guides/download` | `HTTP 200`, 170833 bytes, `2026-10-26T22:34:22Z`; `<title>Download files from the Hub · Hugging Face</title>`, `<h1>Download files from the Hub</h1>`; `<h2>Download a single file</h2>` → `<h3>From specific version</h3>` exist |
| 7 | `git clone -q --shared <lane> $S/lane`; `git -C $S/lane rev-parse 380bcdff…:corpus/SOURCES.md b85783e:corpus/SOURCES.md` | one blob `4c70f9c81e73dc53e7979db543bc7ceb2e1e8098` — the rows are byte-identical at the build and at lane HEAD |
| 8 | `git -C $S/lane ls-tree 380bcdff… corpus/lessons/ \| grep round-48.md` | 0 matches — `corpus/lessons/round-48.md` is **not** in the build tree (it exists only as an untracked working-tree file, lane `git status --porcelain`: `?? corpus/lessons/round-48.md`) |
| 9 | `bash scripts/sources-census.sh validate --file $S/lane/corpus/SOURCES.md --today 2026-10-26` (tip content, lesson absent) | exit **1**: `file E11 S492 missing used-by corpus/lessons/round-48.md`, `file E11 S493 missing used-by corpus/lessons/round-48.md` |
| 10 | same, after copying the lane's untracked lesson into `$S/lane/corpus/lessons/round-48.md` | exit **0**; `census`: `rows 234`, `tier.A 223`, `status.mined 216`; codes: `ok 1`, `W01 1` (S481, pre-existing), `W04 93` (pre-existing) |
| 11 | same, with the proposed S494 appended after line 246 | exit **0**; `rows 235`; codes unchanged — no new E/W code |
| 12 | quote checks (python): `len(q.split())`, `q in hf-head.txt`, `q in` flattened page text | S492 quote 2+2 = 4 words, both header lines byte-identical to my capture; S493 quote 17 words, present verbatim in the served HTML and in the flattening |

`scripts/sources-census.sh` used: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (fleet, read-only invocation).

## S492 — cell by cell

| cell | as filed | what I saw | verdict |
|---|---|---|---|
| id | `S492` | unique (validator emits no E02/E03) | ok |
| source | name + `…/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf` | `HTTP 302` → xet-bridge CDN; `x-repo-commit` = the URL's revision | ok |
| kind | `dataset` | model weights file | ok (E05 enum allows `dataset`) |
| tier | `A` | first-party HF response headers, directly observed; not `community` (E10 clean) | ok |
| scope | identity the v5 receipt pins; artifact identity only; replaces S490's moving `main` locator (S490 stays as filed) | receipts 1–3 carry `provenance.model.url` = this exact URL and `provenance.model.commit` = this revision; S490 (line 243) is the `resolve/main` form | ok |
| anchor | quote `x-repo-commit: …` and `x-linked-etag: "270cba…"` from `curl -sSI` 2026-10-26T22:09:23Z; download sha256; revision API `sha` equals the commit; copy `.ufo/waves/round-48/c2/hf-revision-499bc882.txt` | reproduced at 22:34:14Z with identical bytes; the copy exists at the build commit and contains the header capture **and** the revision-API `jq` line `{"id":…,"sha":"499bc8821c6b12b4e53c5bffcb21ec206f212d81",…}` | ok |
| teaches | a commit-pinned resolve URL serves fixed bytes; digest equals S039's LFS sha256; replay reproduces or refuses | downloaded 1185376 bytes, sha256 `270cba1b…d256d` = `x-linked-etag` = S039 (line 51) LFS sha256 | ok |
| status | `mined` | — | ok |
| opened | `2026-10-26` | today, not future (no E08) | ok |
| recheck | `every round` | accepted symbolic cadence (no E09). Cheap (`curl -sSI`); a pin cannot drift, so the cadence only detects availability or removal — which is real for a repo literally named `models-moved` | ok, over-sampled but defensible |
| used-by | `corpus/lessons/round-48.md`, `corpus/knowledge/llamacpp-loading-lifecycle.md` | lesson: **absent** at the tip (E11, see finding F1). Knowledge file: exists, but `grep -c S492 corpus/knowledge/llamacpp-loading-lifecycle.md` → **0** (it cites S488/S489/S490 at line 434); the v5 paragraph is seat S9Knowledge's pending draft (`w1/out/S9Knowledge/` empty at audit time) | **not yet true** (F3) |

## S493 — cell by cell

| cell | as filed | what I saw | verdict |
|---|---|---|---|
| id | `S493` | unique | ok |
| source | `huggingface_hub guide, Download files from the Hub — https://huggingface.co/docs/huggingface_hub/en/guides/download` | page title and `<h1>` read exactly "Download files from the Hub" | ok |
| kind / tier | `docs` / `A` | first-party library documentation | ok |
| scope | names a revision (branch, tag or commit hash) and the full-length-hash rule; not HTTP headers, caching or the resolve-URL layout | page: "download a file at a particular version (e.g. from a specific branch, a PR, a tag or a commit hash)" and "use the `revision` parameter" | narrow but not wrong: the page lists a PR ref (`refs/pr/3`) as a fourth form; its list is prefixed `e.g.` (observation O1) |
| anchor | `§Download a single file → From specific version` (served 2026-10-26; copy `.ufo/waves/round-48/c2/hf-hub-download-doc.txt`) | both headings exist in that nesting; the copy exists and carries the quote at line 5 | ok |
| teaches | quote verbatim (17 words) **+ "so a pinned provenance URL records the 40-hex commit, as the v5 receipt and the live tool's pin rule do"** | quote verbatim ✓; the inference is **not** what the page says and is contradicted by the service: the Hub's revision API and its resolve path both accept `499bc88` (7 chars) and attribute it to the full commit (steps 4–5). The page's rule binds the `revision=` argument of `hf_hub_download`, not a URL. kama's 40-hex URL pin is kama's convention (`tools/kama-llamacpp-live.py:71` `PINNED_MODEL_URL = re.compile(r'^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+')`, rejected at `:1477`) and the binding evidence a replay rests on is S492's `x-repo-commit` | **overreach — correction proposed (F2)** |
| status / opened / recheck | `mined` / `2026-10-26` / `180d` | valid cadence, due 2027-04-24 | ok |
| used-by | `corpus/lessons/round-48.md` | lesson absent at the tip → E11 | **not yet true** (F1) |

## Quote verification

| row | located quote | words | verbatim |
|---|---|---|---|
| S492 | `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"` | 4 | ✓ both lines byte-identical in `hf-head.txt` |
| S493 | "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." | 17 | ✓ in the served `<p><strong>Note:</strong> …</p>` and in the seat copy |

Both are under the 25-word cap.

## Gate entries (draft — shaped for `corpus/lessons/round-48.md` §Gate)

- **S492** — https://huggingface.co/ggml-org/models-moved/resolve/499bc8821c6b12b4e53c5bffcb21ec206f212d81/tinyllamas/stories260K.gguf and https://huggingface.co/api/models/ggml-org/models-moved/revision/499bc8821c6b12b4e53c5bffcb21ec206f212d81, accessed 2026-10-26T22:09:23Z, re-opened 2026-10-26T22:34:14Z (`curl -sSI`, a download, the revision API; copies `.ufo/waves/round-48/c2/hf-revision-499bc882.txt`, `.ufo/waves/round-48/w1/out/S1Rows/hf-head.txt`). Located quote (response headers, 4 words): `x-repo-commit: 499bc8821c6b12b4e53c5bffcb21ec206f212d81` and `x-linked-etag: "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"`; download 1185376 bytes sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; revision API `"sha"` equals the commit. Admit: the URL names the commit, the bytes match S039's LFS sha256, and the receipt's `provenance.model.commit` is exactly that 40-hex string.
- **S493** — https://huggingface.co/docs/huggingface_hub/en/guides/download, accessed 2026-10-26T22:09:25Z, re-opened 2026-10-26T22:34:22Z (text copy `.ufo/waves/round-48/c2/hf-hub-download-doc.txt`; re-open copy `.ufo/waves/round-48/w1/out/S1Rows/hf-doc-from-specific-version.txt`). Located quote (§Download a single file → From specific version, 17 words): "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." Admit: the library's `revision=` argument must carry the full hash — the ground for the receipt recording a 40-hex commit. **Reject: a 7-character `/resolve/<short>/` pin** — measured 2026-10-26T22:36:44Z, `499bc88` resolves to the same bytes and the same `x-repo-commit` today, so the short form *works*, which is exactly why it must be refused: the page gives no guarantee that a prefix stays unambiguous and the receipt would pin 7 characters, so `PINNED_MODEL_URL` (`tools/kama-llamacpp-live.py:71`) refusing it is kama's rule, not the server's behaviour.

## Correction proposed (append-only; no lane file touched)

Full replacement row, validated inserted after line 246 in my clone (`$S/lane/corpus/SOURCES.md` → `proposed-SOURCES.md`); `sources-census.sh validate --file … --today 2026-10-26` → **exit 0**, `rows 235`, no new E/W code (verbatim copy in `proposed-row-S494.txt`):

```
| S494 | huggingface_hub guide, Download files from the Hub — https://huggingface.co/docs/huggingface_hub/en/guides/download | docs | A | how a Hub download names a revision (branch, tag or commit hash) and that a commit hash must be the full-length hash; not HTTP headers, caching or the resolve-URL layout | §Download a single file → From specific version (page as served 2026-10-26; text copy `.ufo/waves/round-48/c2/hf-hub-download-doc.txt`) | supersedes S493 — "When using the commit hash, it must be the full-length hash instead of a 7-character commit hash." binds the `revision` argument this page documents, not a resolve URL: the Hub's revision API and its resolve path both accept a 7-character prefix and attribute it to `499bc8821c6b12b4e53c5bffcb21ec206f212d81` (measured 2026-10-26T22:36:44Z), so a 40-hex pinned URL is kama's own unambiguous-locator convention, and the commit binding a replay rests on is S492's `x-repo-commit` | mined | 2026-10-26 | 180d | corpus/lessons/round-48.md |
```

The scope cell is byte-identical to S493's, so the row adds no `W04` and `E04` is avoided by the literal `supersedes S493`; the 17-word quote is repeated unelided.

## Observations not proposed as row changes

- **O1** S493's scope parenthetical lists three revision forms where the page shows four (it also shows `revision="refs/pr/3"`); the page's sentence is prefixed `e.g.`, so the narrower scope is conservative, not false. Add the PR form if the scope is ever touched.
- **O2** S492's `recheck: every round` cannot detect drift on an immutable commit; it detects only availability/removal. Cheap (one HEAD) and the repo is named `models-moved`, so the cadence is defensible as filed.
- **O3** the `x-hub-cache: MISS` / `cache-control: no-store` headers on the resolve response are outside both rows' scope and were not used as evidence.
- **O4** (lesson, not registry) `corpus/lessons/round-48.md:20` quotes the etag elided — `x-linked-etag: "270cba1b…d256d"` — so its "Located quote" is not greppable verbatim; and §Gate carries two `Admit:` lines and no `Reject:` (the round's own lesson spec asks for at least one reject). The Gate draft above fixes both: full etag, and the 7-char-pin reject.

## Evidence files (`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S1Rows/`)

`hf-head.txt`, `h-499bc88.txt`, `h-499bc8821c6b12b4e53c5bffcb21ec206f212d81.txt`, `api-499bc88.json`, `api-499bc8821c6b12b4e53c5bffcb21ec206f212d81.json`, `rev-api.json`, `model-sha256.txt`, `hf-doc-from-specific-version.txt`, `validate-tip-noLesson.tsv` (exit 1, E11 ×2), `validate-tip-withLesson.tsv` (exit 0), `validate-proposed-S494.tsv` (exit 0), `proposed-SOURCES.md`, `proposed-row-S494.txt`.
