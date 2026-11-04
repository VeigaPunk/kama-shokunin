# SC03Sources — round-81 w1 scribe report (SOURCES rows)

Seat: scribe, leaf (no dispatch, no subagent). Lane read-only: `corpus/SOURCES.md` was not
edited; the four rows are drafted for the L1 to file. Lane tip read (not trusted to any
`@{u}`): `git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse master` →
`f6cb5303171cc73dc570ace06f99125266e5b956`, subject
`round-81: repay the ten inherited post-introduction append-only events with late-acceptance rows`.
No write of any kind outside this seat dir and `/fast/scratch/hyaku/kama-r81/SC03Sources/`.

## Behavior — what was produced

| artifact | content |
|---|---|
| `sources-rows.md` | 4 rows in the 11-column contract-v1 shape: S558, S559, S560 `mined`; S561 `rejected`. One line per row, no `\|` inside any cell. |
| `curl.txt` | per-URL receipt: URL, exact `curl` command, curl exit, HTTP status, byte count, sha256 — for 7 fetches (S558, the S557-locator control, S559, S560, S560's included `diff-options`, the vLLM tag page, the vLLM feed), the two tag pins (`git ls-remote`), byte-exact located quote extracts with line numbers, the vLLM locator resolution and a two-fetch byte-stability probe. |
| `search-log.md` | one bounded-search paragraph (question, where, date, identified/screened/included/excluded, stop rationale). |
| `fetch.sh`, `probe.sh` | the scripts that produced `curl.txt` (`bash fetch.sh` exit 0, `bash probe.sh` exit 0). |

Every anchor line number in the rows comes from my own fetch this round, not from the plan.

## Receipts (absolute path, command, exit code)

- `/fast/scratch/hyaku/kama-r81/SC03Sources/fetch.sh` — `bash fetch.sh` → exit 0 (all 7
  `curl` calls exit 0). Scratch tree deleted after copying; `ls -d` on it now fails as expected.
- `curl -sS -L -o … https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`
  → exit 0, HTTP 200, 25472 bytes, sha256 `44071a1277796b5ad28e51e561afd94ac75f6f76cd75c4b8d9d80b9dff760cd5`.
- `curl … /v0.40.11/docs/api-openai-compatibility.mdx` (the S557 locator as filed) → exit 0,
  HTTP **404**, 14 bytes, sha256 `d5558cd4…512ed` (body `404: Not Found`).
- `curl … raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-merge-base.adoc` → exit 0,
  HTTP 200, 7759 bytes, sha256 `d3cf8078bc9e34dfca1342d1f4d9a5485cc81f0bb624d124ce87725624f60e82`.
- `curl … /git/v2.56.0/Documentation/git-diff-tree.adoc` → exit 0, HTTP 200, 4188 bytes,
  sha256 `b921aec163609773a30af6a1129e84b406b5ce5c7ae5996b0deaa4c23c269d60`.
- `curl … /git/v2.56.0/Documentation/diff-options.adoc` → exit 0, HTTP 200, 34303 bytes,
  sha256 `f12f2f624417476cf050ca067263be9f5122eb6dc800f09796044975d9046303`.
- `curl … github.com/vllm-project/vllm/releases/tag/v0.33.0` → exit 0, HTTP 200, 163537 and
  163538 bytes on two consecutive fetches, digests `325cc421…dac89` / `890a3514…dfc65`.
- `curl … /vllm/releases.atom` → exit 0, HTTP 200, 733598 bytes, sha256 `e968d03c…43f585`.
- `curl … api.github.com/repos/vllm-project/vllm/releases?per_page=6` → exit 0, HTTP 200,
  346965 bytes, sha256 `f06d8ea1…fd0fbf1`.
- `curl … api.github.com/repos/vllm-project/vllm/releases/tags/v0.33.0` → exit 0, HTTP **404**,
  `{"message":"Not Found", …}`.
- `git ls-remote https://github.com/ollama/ollama refs/tags/v0.40.11` → exit 0,
  `675150d6ad2747df1e218ef59de9194bc4a7e538`; `git ls-remote https://github.com/git/git refs/tags/v2.56.0`
  → exit 0, `2478544319491bbd2a42cc57a83e3d2f4730a280`.
- Format assertion (my own draft): `awk -F'|' '/^\| S/{printf "%s cols=%d\n", $2, NF-2}' sources-rows.md`
  → `S558 cols=11`, `S559 cols=11`, `S560 cols=11`, `S561 cols=11`; header `cols=11`.
- Duplicate-URL screen (read-only): `grep -n 'merge-base' corpus/SOURCES.md` → only `S175`
  (line 187); `grep -n 'diff-tree' corpus/SOURCES.md` → no row; `grep -n 'v0\.33|releases/tag'`
  → S020/S038/S480 (vLLM **v0.31.0**)/S482/S484/S486/S488, no vLLM v0.33 row.

## Findings

1. **R80V2 confirmed in full, with the byte identity that makes the correction safe.** The filed
   S557 URL is a 404 (14 bytes). The corrected path returns HTTP 200 with 25472 bytes and sha256
   `44071a12…cd5` — byte-identical to the digest S557 itself recorded, so S557 pinned the right
   bytes to the wrong locator, and only the locator moves. The response notes are lines **294–295**
   (S557 claimed 293–294; 293 is blank, confirmed by `sed -n '288,296p'`), and `### /v1/models` is
   line 290 exactly as S557 says. S558 carries `supersedes S557 —` and states the note-line change.
2. **S559 collides with a held row — L1 decision needed.** `corpus/SOURCES.md:187` S175 already
   holds `git merge-base --is-ancestor` exit-status semantics at
   `https://git-scm.com/docs/git-merge-base` (opened 2026-10-23, used-by five cells including
   `corpus/knowledge/receipt-tip-binding.md`). S559 as assigned is therefore a *release-byte
   re-pin for a new consumer*, not new ground. Round 70 handled the identical case by extending
   the held row's `used-by` instead of appending a duplicate (its note cites rule 4 / the `W04`
   duplicate-URL warning class); S549 was rejected outright for duplicate coverage. I drafted
   S559 to the assignment (distinct pinned raw-adoc URL, so no duplicate *URL* string) and put
   the relationship in its `scope` cell — "release-byte pin for a consumer S175 does not list" —
   so filing it verbatim cannot read as fresh discovery. If the L1 prefers the round-70
   disposition, the row should be dropped and S175's `used-by` extended with
   `corpus/knowledge/late-acceptance-rule.md`.
3. **S560's premise does not match the frozen audit.** The seat text says the audit parses a
   "`--name-status -z --no-renames`" population; `tools/append-only-audit.py` makes no
   `diff-tree` call at all. Its actual record calls are `ls-tree -r -z --name-only` (line 369),
   `log -z --format= --name-only --no-renames` (line 385), `diff --numstat -z --no-renames`
   (line 468), plus `merge-base --is-ancestor` (line 582). The `--name-status`, `-z` and
   `--no-renames` paragraphs do exist, in `Documentation/diff-options.adoc` — the file
   `git-diff-tree.adoc` includes at line 27 — so S560 anchors `git-diff-tree` and names the
   included file's own bytes, line numbers and sha256, and its `scope` cell names the three calls
   the audit really makes and says the audit reads no status letter. Do not let the row's title
   become a claim that the audit calls `diff-tree --name-status`.
4. **S561's reject is stronger than "unused row", and the candidate URL does not carry the notes.**
   Three grounded legs: (a) no round-81 claim reads a vLLM behaviour — C1 re-derives six
   SCORECARD/LOG facts and C2 grades an append-only acceptance population; (b) the repo has **no
   release object tagged `v0.33.0`** (`releases/tags/v0.33.0` → HTTP 404) and the
   `/releases/tag/v0.33.0` page carries no notes body (two fetches, `927 commits` absent from
   both); (c) the notes GitHub *names* "v0.33.0" live on tag **`v0.33.0rc3`** (published
   2026-11-02T10:10:05Z, body 37794 bytes / 244 lines, `# v0.33.0` at line 1, `## Highlights` at
   line 3, `This release features 927 commits from 389 contributors (122 new)!` at line 5). A
   Gate record that quoted the S561 URL as filed would quote a body that does not exist there —
   an R80V2-class trap in a new place. The row's `teaches` carries `REJECTED: …; flip: …` and
   the flip names the condition that would admit the row later (a load-bearing vLLM release fact,
   cited to the tag that carries the notes body).
5. **GitHub HTML is not byte-pinnable; only raw and API JSON are.** Identical URL, identical
   request, two consecutive fetches: 163537 vs 163538 bytes and different digests (134097 bytes
   differ under `cmp -l`). Therefore no row pins an HTML digest; the pin relation used is
   `raw.githubusercontent.com` bytes plus `git ls-remote` tag→commit, and the S561 quote is taken
   from the releases API JSON (sha256 `f06d8ea1…`), not from the page.
6. **`used-by` names a file that does not exist yet.** `corpus/knowledge/late-acceptance-rule.md`
   is absent at my read (2026-11-04, tip `f6cb5303`) — it is the round plan's own admitted
   knowledge entry. Naming it in S559/S560 `used-by` follows the round-50 precedent (rows naming
   `corpus/lessons/round-50.md` before it landed). The L1 should either land the knowledge entry
   in the same commit train as the rows or leave the cells as drafted and record the order.

## Gates / limits observed

- I did **not** run `tools/round81-selfrecord-round80.py`, `tools/round81-append-debt.py`,
  `tools/round81-late-rows.py` or `pre-report-gate.py`: C1/C2 grading and the scored gate are the
  L1's, and nothing in this item needs their output.
- I did **not** edit `corpus/SOURCES.md`, `corpus/knowledge/`, `corpus/QUALITY.md`,
  `corpus/lessons/`, `SCORECARD.md`, `LOG.md`, any `tools/` file or `plans/`.
- No `git` mutation: no commit, add, stash, checkout, switch, reset, pull, no jj command. Only
  `rev-parse`, `log --oneline`, and `ls-remote` (read-only, network) were run.
- No clone or fixture repo was needed, so no `rev-parse --show-toplevel` assertion applied.
- No tool install or upgrade was required this seat (none performed); no pacman call.
- Scratch `$S = /fast/scratch/hyaku/kama-r81/SC03Sources/` was created under `TMPDIR=$S` and
  deleted before this report; the seat dir is the only surviving copy of `curl.txt`.

## Out of scope (not drafted by this seat)

`corpus/knowledge/late-acceptance-rule.md` itself, the `corpus/lessons/round-81.md` §Corrections
and §Mistakes blocks, the `QUALITY.md` criterion, the `## Gate` record, and the SCORECARD/LOG
appended corrections are all L1 or sibling-seat items. The Gate's per-row ≤25-word located quotes
are pre-extracted in `curl.txt` for whoever writes it.
