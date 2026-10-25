# W3 RevLessonGate — round-36 lesson draft vs C1 counter and quarantine table

Scope: `corpus/lessons/round-36.md` working-tree bytes only (read-only; lesson not edited).
Method: token lists extracted from `tools/round36-statement-audit.py` (`score`/`holds`/`rows_of`/
`KEEP_PATHS`/`FORBIDDEN`/`IDS`), then re-checked against the actual draft bytes by a scratch script
(`token-audit.py` in this seat dir) that imports the counter module — measured, not eyeballed.
Canonical runtime check: counter run on a sandbox clone in this seat dir (git-writing confined to
the clone per lane bounds; lane and fleet repos only read). Measured vs inferred labeled below.

## 1. Gate quarantine table (### "Quarantine hand-check" under ## Gate)

Row count: **7** (S200, S202, S206, S210, S211, S224, S230).

| # | id | URL named? | verdict named? | reason named? | flip condition named? |
|---|----|-----------|----------------|---------------|----------------------|
| 1 | S200 | yes — https://arxiv.org/abs/2312.07104 | yes — "absent" | yes — quoted cell "DOI not in Semantic Scholar" does not occur in page text | yes — "a located sentence from that page replaces the cell" |
| 2 | S202 | yes — https://docs.docker.com/reference/compose-file/services/ | yes — "present, not appended" | yes — page carries the span; register cell differs only in quote style; no admitted entry cites it | yes — "an admitted entry cites it" |
| 3 | S206 | yes — https://www.alibabacloud.com/help/zh/pai/deploy-an-llm/ | yes — "present, not appended" | yes — page carries the span; hosted Alibaba Cloud PAI guide is out of the local-serving province | yes — "an in-province entry cites it" |
| 4 | S210 | yes — https://unsloth.ai/docs/jp/ji-chu/inference-and-deployment/sglang-guide | yes — "absent" | yes — quoted cell "Page Not Found" does not occur on the page | yes — "the cell is replaced by a located span from the page" |
| 5 | S211 | yes — https://github.com/AaronYang238/llm/blob/35b83cee12ae26f10b58d4163298352384503907/chapters/06-推理引擎.md | yes — "absent" | yes — token "still-live" occurs nowhere in the page text read | yes — "a located span from that chapter replaces the cell" |
| 6 | S224 | yes — https://docs.vllm.ai/en/v0.17.0/api/vllm/entrypoints/serve/instrumentator/health/ | yes — "quote not located" | yes — compound span "render-only servers always return 200" absent (neither half on page) | yes — "the compound cell is split and each half is re-quoted" |
| 7 | S230 | yes — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py | yes — "present, covered by the lane's own row" | yes — same URL+anchor as S329; a second row would duplicate the URL (W04) | yes — "a later round needs a second, differently-anchored row for that URL" |

Result: **7/7 rows name all four of URL, verdict, reason, flip.** No incomplete row.

## 2. Corrections rows vs exact C1-required tokens

Row discovery: `rows_of` matches any line starting with `<id>:`; the draft has exactly 4 such lines
(no duplicates, none overridden) — measured `rows_found_total: 4`. Per-row requirements below are
the exact strings the counter tests **in the row**; global `FORBIDDEN = "429"` (substring, rejected
if present) applies to every row.

| row | token required by counter (exact string) | in row? (measured) |
|-----|------------------------------------------|--------------------|
| R35-S211 | line starts `R35-S211:` | yes |
| R35-S211 | `ScoutQuarantineS211.md` | yes |
| R35-S211 | `still-live` | yes |
| R35-S211 | `200` | yes (×2: "HEAD 200", "HTTP 200") |
| R35-S211 | NOT `429` | holds (absent) |
| R35-WORDS | line starts `R35-WORDS:` | yes |
| R35-WORDS | `20 words` | yes ("is 20 words, not the 18 words") |
| R35-WORDS | NOT `429` | holds (absent — incl. blob hash 428f1f8a…, no `429` substring) |
| R35-MIRROR | line starts `R35-MIRROR:` | yes |
| R35-MIRROR | `mixed` | yes |
| R35-MIRROR | `11` | yes |
| R35-MIRROR | `84` | yes |
| R35-MIRROR | NOT `429` | holds (absent) |
| R35-KEEP | line starts `R35-KEEP:` | yes |
| R35-KEEP | `seat-log-flush` | yes |
| R35-KEEP | `overwrite-not-committed` | yes |
| R35-KEEP | `mixed-mirror-not-committed` | yes |
| R35-KEEP | `helper-skipped` | yes |
| R35-KEEP | `1066624` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ConnSibling/seat.log` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ExecDisposition/seat.log` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ScoutCoverageAbsence/seat.log` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ExecDisposition.md` | yes |
| R35-KEEP | `.ufo/waves/round-35/assimilation/validate/` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ScribeGate/fetch/docker-dockerfile.html` | yes |
| R35-KEEP | `.ufo/waves/round-35/w1/out/ScribeGate/fetch/dockerfile.html` | yes |
| R35-KEEP | NOT `429` | holds (absent — incl. `1994`, `1066624`) |

Fact-side requirements (checked by the counter against other committed bytes, not required of the
row): scout `fetched successfully`/`still-live`/`absent`; spotcheck `HTTP 200`/`still-live`/
`11 symlinks`/`84 regular files`/`1066624`; old lesson `quote_words()==20`, the exact 503 QUOTE
sentence, `18 words`; fleet report `symlink tree`; r35 lesson blob = 428f1f8a0e8871022f7c1e8ea47e50ba5a8d6412;
fleet report blob = 6d8f317378ba6048d8a3dfb4944adaf24f341eea; ExecDisposition blob = 9307c5d61c1942857a17cb259b4313460b37d0da;
html paths and r35 `assimilation/validate/` untracked at tip.

## 3. Measured runs (canonical runtime)

- Blob pins at lane HEAD 9014843cb7de8fbe87a97954c13832b67d55f046: all three match the counter's
  frozen constants exactly (lesson 428f1f8a…, report 6d8f3173…, disp 9307c5d6…). Measured.
- Sandbox clone (seat dir) + commit of the five draft corpus bytes
  (round-36.md, knowledge entry, SOURCES.md, QUALITY.md, README.md), tip 5b7c909465f9aaaab8c0abef3cddf3341e432ee2:
  `uncorrected 0 false_corrections 0 lesson_unchanged 1 report_unchanged 1 met True`, exit 0. Measured.
- Counter `--selftest` on same tip: `SELFTEST empty_met=False bad_met=False words=20 pass=1`, exit 0. Measured.
- Control, lane repo at current tip (lesson not yet committed): `uncorrected 4 … met False`, exit 1 —
  consistent with the frozen noop control; expected pre-commit state, not a defect. Measured.

## Findings by severity

- **High (commit-mechanics hazard, not a lesson-bytes defect):** lane working tree carries
  tracked-modified r35 evidence (`M .ufo/waves/round-35/w1/out/ExecDisposition.md` and three
  `M …/seat.log`s) plus untracked r35 mirror/html (`.ufo/waves/round-35/assimilation/validate/`,
  two `ScribeGate/fetch/docker-*.html`). The lesson's own R35-KEEP row and the counter require these
  NOT committed (disp blob pin, `html_clear`, `mirror_clear`). A blanket `git add -A` at the real
  commit flips C1 to `met False` on three independent arms. The sandbox `met True` holds only for a
  commit scoped to the five corpus drafts. Evidence: lane `git status --porcelain` (read-only).
- **No missing-token or quarantine-completeness defect found:** 7/7 quarantine rows complete; 4/4
  correction rows carry every required token and none carries `429`.
- **Info:** `FORBIDDEN` is a bare substring, so any incidental `429` (e.g. inside a hash) anywhere in
  a row would false-flag; current bytes contain none (measured per row). Counter property, not a draft defect.

## Residual risk and verification gaps

- Residual: the real commit shape is the L1's choice; the sandbox `met True` is measured only for the
  five-draft commit. Inference, not measured: that the L1 commits exactly those corpus bytes and
  leaves the modified r35 files uncommitted.
- Not verified here: the campaign-register slice claim ("seven kama rows, class payload-absent") —
  register lives outside the lane; the S328/S329 registry rows, KQ45 and README block (other seats'
  scope); live re-fetch of the seven quarantine URLs (rows were taken as drafted text; the r35
  spot-check/scout bytes they cite are pinned and were verified via the counter's fact-side arms).
- C2/coverage untouched per frozen claims; no predicate changed.

Verdict is a recommendation only. No lane, fleet, or sibling-lane bytes were mutated; the only
git-writing was the seat-dir sandbox clone.
