# SC05Fetch — external source reconnaissance for the round-81 frontier step

Read-only scout seat. Every claim below is a fetch I ran at the instant shown, with the raw
output committed beside this report. Nothing in the lane was written; nothing outside this seat
dir was written; no tool was installed (the named items required none); the scratch tree
`/fast/scratch/hyaku/kama-r81/SC05Fetch` is deleted at exit.

| field | value |
|---|---|
| lane tip at read | `7eeae5bca46883914dd958af140738e1cee37620` (`git -C …kama-shokunin rev-parse master`, 2026-11-04T11:51:16Z; it was `f6cb5303…` at the first read, 11:47Z — siblings were committing) |
| base | `e7d2fd729cf8204c89c32534303bc9f2a97fcee4` (resolves, `rev-parse`) |
| sealed revision C1 grades | `a2af1af59faf6cf66fe854559293c4e4b441aff3` (resolves, `rev-parse`) |
| access instant | 2026-11-04T11:46Z–11:51Z (per-fetch UTC in `evidence/fetch-status.tsv`, `evidence/headers.txt`) |
| tools | curl 8.23.0, python 3.14.8, git 2.56.0 |
| receipts | `$SEAT/receipts.sh`, `$SEAT/aggregate.sh`, `$SEAT/receipts.out`, `$SEAT/evidence/` where `$SEAT=/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC05Fetch` |

## 1. The four candidates, measured

`bash receipts.sh` → exit 0 (full output `receipts.out`; per-URL table `evidence/fetch-status.tsv`).

| # | candidate | URL | HTTP | bytes | sha256 | best ≤25-word quote (physical line) | words | anchor the plan expects |
|---|---|---|---|---|---|---|---|---|
| S558 admit | Ollama OpenAI-compat @ v0.40.11 (**corrected** path) | `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx` | 200 | 25472 | `44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5` | `- \`owned_by\` corresponds to the ollama username, defaulting to \`"library"\`` — line **295** | 9 | `## Endpoints` **line 209** ✓; `### \`/v1/models\`` **line 290** ✓; response notes **294–295** (filed 293–294 ✗, §3) |
| — | same file, **filed** S557 path | `…/docs/api-openai-compatibility.mdx` | **404** | 14 | `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` | body is exactly `404: Not Found` | 4 | n/a — dead (§2) |
| S559 admit | git-merge-base | `https://git-scm.com/docs/git-merge-base` | 200 | 41397 | `46d106b777754f7ec3072813ace57d2c5385d110181b8db1c56b7136cfb49644` | "Check if the first `<commit>` is an ancestor of the second `<commit>`, and exit with status 0 if true, or with status 1 if not." — lines **1703–1704** (option `dt` 1701, error clause 1705) | **25** (at the cap) | `--is-ancestor` ✓, stable id `Documentation/git-merge-base.txt---is-ancestor`; synopsis 1648 |
| S560 admit | git-diff-tree | `https://git-scm.com/docs/git-diff-tree` | 200 | 256938 | `6473d8a3d1bc12fa2e0ce700664253db537f143a53d34d36313bbda0d9ef5000` | "git diff-tree outputs a line with the commit ID when applicable. This flag suppresses the commit ID output." — lines **4567–4568** (`--no-commit-id`, `dt` 4565) | 18 | raw-record rules ✓: `--raw` 3441–3444 ("This is the default."), `-r` 4375, `--root` 4383, `--name-only` 3654, `Raw output format` 5369, "one output line per changed file" 5400 |
| S561 reject | vLLM v0.33.0 release page | `https://github.com/vllm-project/vllm/releases/tag/v0.33.0` | 200 | 163538 (varies by ±1, §5.1) | **not stable** — four fetches gave four digests (`597819dc…`, `46313aef…`, `18980a94…`, `600f7ee9…`) | the release's entire body is `<p>vLLM v0.33.0</p>` — `releases.atom` line **13** | 2 | **no anchor grounds a round-81 claim**: the page carries no body (§4) |

Commands for the table: `bash receipts.sh` (exit 0) → `receipts.out` §`[1]`, §`[1b]`, §`[1c]`;
digest manifest `evidence/digests.tsv`; per-anchor extracts `evidence/ollama-anchors.txt`,
`evidence/merge-base-anchors.txt`, `evidence/diff-tree-anchors.txt`, `evidence/vllm-release.txt`;
word counts `evidence/quote-words.txt` (the merge-base quote is exactly 25 tokens — do not add a
word when filing S559).

### Anchor existence, stated plainly

- **Ollama (S558).** The plan's expected anchors exist, with one correction: `## Endpoints` is
  line 209 and the heading is literally ``### `/v1/models` `` at line 290, but the two response
  notes are lines **294 and 295** (`#### Notes` at 292, blank at 293) — the filed row's
  "response notes lines 293-294" is off by one (§3).
- **git-merge-base (S559).** Exists. The option is `--is-ancestor` (`dt` 1701, body 1703–1705):
  "Check if the first `<commit>` is an ancestor of the second `<commit>`, and exit with status 0
  if true, or with status 1 if not. Errors are signaled by a non-zero status that is not 1."
  This is exactly the primitive the C2 counter calls at `tools/round81-append-debt.py:298`
  (`def is_ancestor`) and that `tools/append-only-audit.py:582` calls — the counter's
  `strict_descendant` (lines 497–503) depends on the 0/1 exit convention, and on errors ≠ 1.
- **git-diff-tree (S560).** Exists, but see §5.4 before filing it as "C2's record parsing":
  no round-81 counter invokes `diff-tree`.
- **vLLM (S561).** The page returns 200 but has nothing citable: static HTML has zero occurrences
  of `markdown-body`, `release-body`, `Highlights`, `Full Changelog`; the atom entry's body is 19
  bytes (§4).

## 2. S557's dead URL — proven, and the corrected URL is the stated document

`evidence/s557-proof.txt` (command `bash receipts.sh`, section `[2]`, exit 0):

```
filed     https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api-openai-compatibility.mdx
          http=404 bytes=14 sha256=d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed
          body="404: Not Found"
corrected https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx
          http=200 bytes=25472 sha256=44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5
          git blob=75218fc8f8044a8d0c0f0adc6c77684fec57711f
```

- The filed path is a **path typo**: `docs/api-openai-compatibility.mdx` (dash) vs
  `docs/api/openai-compatibility.mdx` (slash). Cause: [INFERENCE] transcription, not a moved
  file — the same tag serves the corrected path with the filed digest.
- **Refutation of "S557 is a phantom":** the corrected object's sha256 is S557's own stated
  digest `44071a12…cd5` at S557's own stated 25472 bytes, and its git blob
  `75218fc8f8044a8d0c0f0adc6c77684fec57711f` is the blob **S524** filed for the same tag path.
  Two independently filed digests agree, so the corrected URL is the document S557 describes.
- The filed row is SOURCES.md line 312 at the lane
  (`grep -n '^| S557 ' corpus/SOURCES.md`), quoted in `evidence/s557-proof.txt`.

## 3. Ollama page — real line numbers

`evidence/ollama-anchors.txt`, command `awk 'NR==209 || (NR>=288 && NR<=296)…'`, exit 0:

```
209|## Endpoints
290|### `/v1/models`
292|#### Notes
294|- `created` corresponds to when the model was last modified
295|- `owned_by` corresponds to the ollama username, defaulting to `"library"`
```

- **True `### /v1/models` heading line: 290** (matches the filed row).
- **True response-notes lines: 294–295** (created at 294, owned_by at 295). The filed row's
  `293-294` is wrong: 293 is the blank line between `#### Notes` (292) and the first bullet.
  This agrees with R80V2's routed correction, and the corrected S558 row must say 294–295.
- The sibling block `### /v1/models/{model}` (heading 297) repeats the same two notes at 301–302
  — do not let a line-anchor drift land on the wrong block; the heading line number is the
  discriminator.
- The corrected file's 432 physical lines and sha256 are stable across fetches; the file is also
  committed here at `evidence/ollama-openai-compatibility.mdx` (byte-identical, sha256 above).

## 4. vLLM v0.33.0 — out of scope for round 81, and the flip

**One-line source quote** (`releases.atom` line 13 — the release's whole body, 19 bytes):

```
13|    <content type="html">&lt;p&gt;vLLM v0.33.0&lt;/p&gt;</content>
```

**Why out of scope (one line):** round 81's frozen claims read lane bytes only — C1 re-derives
six facts from `git show` at the sealed revision and the tip, C2 grades the append-only registers
and audit JSON — so no claim reads a vLLM release note, and this release body has no prose to
read anyway (19 bytes, `<p>vLLM v0.33.0</p>`).

**What flip would admit it:** a frozen claim whose witness *is* what v0.33.0 shipped — e.g. a
pin-freshness claim that reads a release-note change list, or a claim that a named surface landed
in v0.33.0. Even then the witness must be a populated body: today the `v0.33.0` release carries
none (API `releases/tags/v0.33.0` → **404**, `evidence/vllm-release.txt`), while the substantive
notes sit on release **`v0.33.0rc3`** (`tag_name='v0.33.0rc3'`, body 37794 bytes via API /
286096 rendered in the atom; `/releases/latest` returns it), whose atom `<title>` was edited to
"v0.33.0" while its id stayed `…/v0.33.0rc3`.

**R80V4 warning inventory (restated, verified for the census note):** the duplicate-URL `W04`
pair is `S553` (SOURCES.md line 308) and `S555` (line 310) — identical URL
`…llama.cpp/39febd2a…/tools/server/README.md` and identical sha256 `8fd5abde…35c6`; S555 is the
new member this round (`evidence/w04-duplicate.txt`).

## 5. Findings that change how S558–S561 must be filed

### 5.1 A GitHub release *HTML* page has no stable sha256 — do not file one

`evidence/volatility.txt` (a three-fetch probe, `cmp` + `diff`): the page returns 200 at 163537 /
163538 / 163539 bytes with three distinct digests (a fourth fetch earlier in the seat gave a
fourth, `597819dc…`); the diffs are the per-request
`request-id`, `html-safe-nonce`, `visitor-payload` and `visitor-hmac` meta tags. Any Gate row
that states a sha256 for `github.com/.../releases/tag/...` is unreproducible and will fail a
re-run. **Cite the atom feed instead:** `https://github.com/vllm-project/vllm/releases.atom`
returned 200 / 733598 bytes / sha256 `e968d03cba2c7b226f10e1cba8ee2d8bcbb49596e4674446ac39d63eaa43f585`
on three fetches, and that digest equals the server `ETag` (`evidence/headers.txt`).

### 5.2 The 200 page is a JS shell, so "HTTP 200" proves nothing about content

The tag page contains zero `markdown-body`/`release-body`/`Highlights` strings
(`evidence/vllm-release.txt`); the body exists only in the atom/API. A row that cites the page
"opened" without naming the quote would be an unbacked Gate record. [INFERENCE] GitHub now
renders release bodies client-side for this repo/route; the atom feed is the server-side copy.

### 5.3 git-scm pages float on "Latest version" — pin them

`evidence/doc-version.txt`, `evidence/pinned-urls.txt`: both requested URLs carry no version
segment; the pages self-describe as `git-merge-base last updated in 2.43.0` (line 1326) and
`git-diff-tree last updated in 2.56.0` (line 1330) under a "Latest version" selector. The
versioned URLs return 200 and reproduce the anchors at the **same physical lines**:

| versioned URL | HTTP | bytes | sha256 | anchor |
|---|---|---|---|---|
| `https://git-scm.com/docs/git-merge-base/2.43.0` | 200 | 41268 | `1875344e25f5233943577c2336c00a72fbd67d8f3daee0fa2a93bd933b1a0f90` | `--is-ancestor` `dt` 1701; body 1703–1705 **byte-identical** to the floating page |
| `https://git-scm.com/docs/git-diff-tree/2.56.0` | 200 | 256809 | `16cca9f736d58907f9200e81e908a2cc5a1457a7312c8c0b2bdfc1417355a972` | `--no-commit-id` id present; "suppresses the commit ID output" at 4568 |

`git --version` here is **2.56.0**, exactly the diff-tree page's last-change release, so the
floating page and the installed git agree today; the pin still belongs in the row, because the
next git release can move the page.

### 5.4 Grounding precision: `git-diff-tree` is not called by either round-81 counter

`evidence/tool-grounding.txt` (grep of the lane at the tip):

- `tools/round81-append-debt.py` calls `git show <rev>:<path>` (292), `merge-base --is-ancestor`
  (298), `log --diff-filter=A --format=%H` (303). **No `diff-tree`.**
- `tools/round81-selfrecord-round80.py` calls `git show` (85) and `rev-parse --verify`
  (491–492). **No `diff-tree`.**
- `diff-tree` call sites are the older record-scanning family: `round72-receipt-tip-binding.py:197`,
  `round76-selfrecord-facts.py:90`, `round77-selfrecord-round76.py:60` — all
  `--root --no-commit-id --name-only -r`.

So S559 can honestly be filed as grounding C2's ancestry test (a real call site), while S560
grounds the **raw-record format rules** those scanners rely on (`--raw` is the default; one
output line per changed file; suppress the commit id; recurse subtrees; show the initial commit
as a creation event). Filing S560 as "the C2 counter's parser" would be unbacked: C2 parses with
`show` + `log --diff-filter=A`, which the diff-tree page does not document. If the L1 wants a
frozen source for the `--diff-filter=A` introduction scan, that is `git-log`, not in this set —
flag it as an open source gap rather than stretching S560.

### 5.5 The Gate rows can be written now

Gate format as used by the lane (`corpus/lessons/round-79.md` §Gate, `round-80.md` §Gate):
`Candidate | Source (URL, HTTP, bytes, sha256) | Accessed | Located quote (≤25 words) | Decision`.
All five rows' material is in this report: S558 (§1/§3), S559/S560 (§1/§5.3), S561 reject (§4),
plus the S557 erratum (§2, R80V3).

## 6. Receipts — absolute path, command, exit code

Seat dir `SEAT = /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-81/w1/SC05Fetch`.

| receipt | command | exit |
|---|---|---|
| `SEAT/receipts.sh` | `bash receipts.sh` (all fetches, headers, anchor extracts, digests) | 0 |
| `SEAT/receipts.out` | the captured stdout of the above (14827 B, 256 lines) | 0 |
| `SEAT/aggregate.sh` | `bash aggregate.sh` (builds `evidence/`) | 0 |
| `SEAT/evidence/fetch-status.tsv` | per-URL http/bytes/sha256/blob/lines/access | 0 |
| `SEAT/evidence/headers.txt` | `curl -sS -I -L <url> \| grep -iE '^HTTP/\|^content-type:\|^content-length:\|^etag:\|^last-modified:'` | 0 |
| `SEAT/evidence/ollama-anchors.txt` | `awk 'NR==209 \|\| (NR>=288 && NR<=296)'` + `grep -n '^#\{2,4\} '` | 0 |
| `SEAT/evidence/merge-base-anchors.txt` | python tag-strip of physical lines 1643–1652, 1701–1706 | 0 |
| `SEAT/evidence/diff-tree-anchors.txt` | python tag-strip of 3441–3445, 3654–3666, 4375–4382, 4383–4387, 4565–4569, 5369–5373, 5400–5406 | 0 |
| `SEAT/evidence/vllm-release.txt` | body probes + atom 8–27 + API cross-check (`api-v0.33.0.json`, `api-v0.32.0.json`, `api-v0.33.0rc3.json`, `api-latest.json`) | 0 |
| `SEAT/evidence/volatility.txt` | 3× page fetch + `cmp`/`diff`; 3× atom fetch + `sha256sum` | 0 |
| `SEAT/evidence/s557-proof.txt` | filed vs corrected status/size/digest + `grep -n '^| S557 '` | 0 |
| `SEAT/evidence/tool-grounding.txt` | `grep -n` of git primitives in both round-81 counters; `grep -rn '"diff-tree"' tools/*.py`; `sed -n '497,505p'` | 0 |
| `SEAT/evidence/doc-version.txt` | `grep -n 'last updated in'`, version-switcher links, `git --version` | 0 |
| `SEAT/evidence/pinned-urls.txt` | versioned-URL fetches + paragraph equality test | 0 |
| `SEAT/evidence/quote-words.txt` | token counts of every quote filed here | 0 |
| `SEAT/evidence/w04-duplicate.txt` | S553/S555 URL+sha cell extraction | 0 |
| `SEAT/evidence/ollama-openai-compatibility.mdx` | the fetched object itself (25472 B, sha256 `44071a12…`) | 0 |

Lane reads used for context (read-only, no mutation):
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master|e7d2fd72|a2af1af5` (exit 0),
`grep -n '^| S557 ' corpus/SOURCES.md` (exit 0),
`grep -n 'merge-base\|--diff-filter=A\|diff-tree\|"show"' tools/round81-append-debt.py` (exit 0).

Scratch: `/fast/scratch/hyaku/kama-r81/SC05Fetch` (git fixtures: none; only http artifacts) is
removed before this seat yields.

## 7. What I could not settle

- **SC03's draft rows** did not exist at read (`.ufo/waves/round-81/w1/SC03Sources/` empty), so I
  verified the *source objects*, not the filed row text. If SC03 writes S558 with notes
  `293–294` or S559/S560 with a page-level digest, this report contradicts those cells.
- **The API 404 for tag `v0.33.0`** is observed (`/releases/tags/v0.33.0` → 404, remaining rate
  limit 56, while `/releases/tags/v0.32.0` and `…/v0.33.0rc3` both 200). Its *cause* is
  [INFERENCE] — a draft or tag-only record; GitHub does not expose drafts unauthenticated, and
  the atom feed gives no `draft` flag.
- **Whether v0.33.0 will gain a populated body later** is unknowable here; it would change the
  flip's *evidence*, not its scope.
