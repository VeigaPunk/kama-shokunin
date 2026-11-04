# SC03Knowledge — round-82 seat report (scribe: pin-recheck knowledge entry, coverage row, KQ134)

Leaf seat; no subagent dispatched. The lane tree was read-only: only this seat directory and the
scratch root were written. No production file, no git mutation, no `pre-report-gate.py` in scored
mode, no tool install. Scratch `/fast/scratch/hyaku/kama-r82/SC03Knowledge/` was deleted after the
receipts below were copied into the seat dir.

Lane read: master `bacae0726d7c53455bd083bc6d478bbcd6e7fffc` (the round-82 wave-dispatch commit);
round-82 base `aaf974dbd3b6adb2ef914dc7293cda92b4e05551`; C1 sealed revision
`1b64f66ddea89c57b71165eacd14b0e1d6f24e11`. `git status` at seat start showed only the dispatched
wave markers (` D .ufo/waves/round-82/w1.ready.partial`, `?? .ufo/waves/round-82/w1.ready.dispatched`);
this seat directory and the report are the only new untracked paths this seat created, while other
seats' untracked directories appeared during the wave.

## Behavior — drafts written

| draft (absolute path) | lines | content |
|---|---|---|
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC03Knowledge/pin-recheck-trigger.md` | 69 (limit ≤70) | `corpus/knowledge/` entry opening with `source: S563`, `verified-at: 2026-11-04`, `recheck:` a runnable command; body cites S564 (the lane's pin b11755) and S565 (SGLang v0.5.23, rejected); register semantics (`relation=behind`, `newer` = releases above the pin, `newest` = tag observed); behind-is-a-trigger; the pinned-document re-open as the only drift test with a `holds/reworded/moved/drifted` verdict table; a verified newest-document difference (lines 850/1588/2167; 2402 → 2620 lines); the SGLang README boundary and the recheck-row fields; the model-quality/served-behavior boundary |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC03Knowledge/readme-row.md` | 11 | `## Coverage map — round 82 addition` + `\| Entry \| Covers \| Round \|` header + one row for `knowledge/pin-recheck-trigger.md` + a short frontier note (3-cell row, appended-round style) |
| `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC03Knowledge/quality-criterion.md` | 11 | `## Criterion added — round 82` + a four-cell KQ134 row (next free after KQ133 at the item's instruction): rule-prose/code same-identifier admission check, rejects (prose substitutes for an arm, rule rewritten to the code, no red-before receipt, arm cannot fail), motivating lesson citing `corpus/lessons/round-82.md` §Mistakes (`register-introduction-conflated`) |

The L1 files these; nothing was written to `corpus/`, `registry/`, `tools/`, `plans/`, `SCORECARD.md`,
`LOG.md` or `SKILL.md`.

## Evidence — commands, exits and receipts

All commands ran from `/home/vgpnk/Projects/shokunin/kama-shokunin`; downloads lived in the scratch
root and the receipts are absolute under the seat dir.

| # | command | exit | receipt |
|---|---|---|---|
| 1 | `curl -sS --max-time 90 -o <scratch>/S563.raw -w '%{http_code} %{size_download}' https://raw.githubusercontent.com/ggml-org/llama.cpp/b12103/tools/server/README.md` | 0, HTTP 200, 136429 B | `.../SC03Knowledge/curl-S563.out` |
| 2 | same for `.../b11755/tools/server/README.md` (S564) | 0, HTTP 200, 119661 B | `.../SC03Knowledge/curl-S564.out` |
| 3 | same for `https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/README.md` (S565) | 0, HTTP 200, 9472 B | `.../SC03Knowledge/curl-S565.out` |
| 4 | `sha256sum S563.raw S564.raw S565.raw` | 0 | `.../SC03Knowledge/sha256-docs.txt`, `anchors.txt` |
| 5 | anchor/diff recomputation (`grep -n`, `diff -u`, `sed -n`) | 0 | `.../SC03Knowledge/anchors.txt`, `diff-S564-to-S563.txt` |
| 6 | `python3 tools/pin-watch.py check --pins registry/engine-pins.tsv --tags-dir .ufo/waves/round-80/measured/after/c2-tags` | 1 (expected: all three pins `behind`) | `.../SC03Knowledge/pin-watch-tagsdir.out` |
| 7 | `timeout 180 python3 tools/pin-watch.py check --pins registry/engine-pins.tsv` (live) | 1 (expected) | `.../SC03Knowledge/pin-watch-live.out` |
| 8 | `curl -sS ... https://raw.githubusercontent.com/ggml-org/llama.cpp/b12110/tools/server/README.md` | 0, HTTP 200, 136429 B | `.../SC03Knowledge/curl-live-b12110.out`; hash appended to `sha256-docs.txt` |
| 9 | tag recount over `.ufo/waves/round-80/measured/after/c2-tags/llama.cpp.txt` | 0 | `.../SC03Knowledge/tag-recount.txt` |
| 10 | production-entry command as filed: `python3 tools/pin-watch.py check --repo .` | 2 (usage error: `--pins` required) | `.../SC03Knowledge/production-entry-recheck-fails.out` |
| 11 | `python3 tools/round80-engine-pin-relations.py --repo . --tags-dir .ufo/waves/round-80/measured/after/c2-tags` | 0 | `.../SC03Knowledge/pin-relations-tagsdir.out` |

Verified values:

- sha256 of the fetched bytes equals the committed SOURCES rows exactly: S563
  `eafc1b53abd787613d13d1fb9a86a1fc9f90b59f1240b3eeb88c85ea08d9a137` (136429 B, 2620 lines);
  S564 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` (119661 B, 2402 lines);
  S565 `a7654a48a8cd08c824e4445cb906405704148a3c55fb84362c7071d27397303c` (9472 B, 120 lines).
- Anchor: `### GET \`/health\`: Returns health check result` at line 479 (b11755) and 480
  (b12103); the sentence `This endpoint is public (no API key check). \`/v1/health\` also works.`
  at line 481 (b11755) and 482 (b12103); `diff` of the two lines is empty (byte-identical).
- Diff b11755 → b12103: 15 hunks; the health section shifts +1 from an options-table insertion
  (`--models-memory-margin`, first hunk at `@@ -230,6 +230,7 @@`); the newest document adds
  `### POST /tts` (line 850), `### WebSocket /v1/realtime` (line 1588) and
  `### Memory-based unloading` (line 2167), absent at b11755; 2402 → 2620 lines.
- Register row (llama.cpp b11755): `behind`, `newer=278`, `newest=b12103`, dated 2026-11-04. The
  committed tag list recounts to 7608 `b<digits>` release tags, 278 above b11755, newest b12103 —
  matching the register. `newer` is release-tag count, not the 348 difference of build numbers.
  The register's own counter re-derives it against the committed receipt:
  `PIN_RELATIONS engines=3 refs=5 unexplained=0`, exit 0.
- Live recheck (2026-11-04, ~13:10Z) prints `newest=b12110`, `newer=280`; the b12110 README has
  the same sha256 as S563 and zero diff hunks against it, so the tag moved and the document bytes
  did not — the entry's dated-observation caveat, observed live.
- S565's README names no health, `/v1/models` or served-identity route (`grep -i` returns nothing);
  line 1 is `# SGLang: Fast inference for LLMs and multimodal models`. It cannot ground the SGLang
  pin's recheck; the flip is a docs page at v0.5.23 naming the anchored route.

## Findings — production state at the tip (bacae072), for the L1

The tip already carries a pre-wave copy of all three artifacts, filed by commit `962bd251`
("record the round-81 corrections, … the pin-recheck entry and its sources, KQ134 …"), which is an
ancestor of the wave-dispatch commit `bacae072`. My drafts are the independent seat copies; the L1
owns the reconciliation. Defects observed in the pre-wave copies:

1. `corpus/knowledge/pin-recheck-trigger.md` (40 lines) has a non-runnable `recheck:` line:
   `python3 tools/pin-watch.py check --repo .`. The tool's usage is
   `pin-watch.py check --pins registry/engine-pins.tsv [--tags-dir DIR]`
   (`tools/pin-watch.py:42-43`); its argparse declares only `--pins` and `--tags-dir`
   (`:242-243`). Running the filed command exits 2 with `error: the following arguments are
   required: --pins` (receipt 10).
2. That entry never cites S565 in the body (`grep -c S565` = 0), though the item requires the
   S564/S565 body citations; my draft adds the rejected-README boundary.
3. That entry says "the release gap of 348 tags": 348 is b12103 − b11755, not a tag count. The
   register's `newer` is 278 release tags; the entry's own `newer` semantics are blurred. My draft
   states 278 and re-derives it from the committed tag list.
4. `corpus/README.md:1781` appends the coverage row as a bare table row with no
   `## Coverage map — round 82 addition` heading and no `| Entry | Covers | Round |` header
   (`grep -c '^## Criterion added — round 82'` on QUALITY is 0 too). My `readme-row.md` carries the
   heading, header and row.
5. `corpus/QUALITY.md:640` KQ134 is malformed: it is appended under the round-80 criterion section
   with no round-82 heading, and its four cells put the evidence pointers in `Reject or limit when`
   while `Motivating lesson` is just `round 82`. My `quality-criterion.md` gives the proper four
   cells (rule / rejects / motivating lesson) under a round-82 heading.
6. Number reconciliation: the item says "next free number after KQ133", so my row is KQ134; the tip
   already has a KQ134 at line 640. The L1 must either replace that row with the draft or renumber
   the draft to KQ135 — filing both rows would duplicate the ID.

## Gate and out of scope

- `pre-report-gate.py` was not run in scored mode (L1-owned); no commit, tag, push or VCS mutation
  was made. `git status` shows the seat dir untracked.
- No edits to `corpus/SOURCES.md` (SC02), `corpus/lessons/round-82.md` (SC01), planned tools or the
  C1/C2 counters; the instruments were attacked only by reading, not modified.
- No sibling/fleet writes (`/home/vgpnk/Projects/shokunin` root, `.ufo/state/`, `MANIFEST.json`,
  templates, scripts, other repos) and no tools installed — none were needed.

## Artifact paths (absolute)

- Drafts: `.../w1/SC03Knowledge/pin-recheck-trigger.md`, `readme-row.md`, `quality-criterion.md`
- Receipts: `.../w1/SC03Knowledge/{curl-S563.out,curl-S564.out,curl-S565.out,curl-live-b12110.out,sha256-docs.txt,anchors.txt,diff-S564-to-S563.txt,pin-watch-tagsdir.out,pin-watch-live.out,pin-relations-tagsdir.out,tag-recount.txt,production-entry-recheck-fails.out,production-state.txt}`
- This report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-82/w1/SC03Knowledge.md`

Scratch `/fast/scratch/hyaku/kama-r82/SC03Knowledge/` was removed after receipt copy; no raw
document bytes remain there.
