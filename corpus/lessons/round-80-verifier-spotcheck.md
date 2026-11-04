author: hyaku closure (non-author integrator, @m_zfl)

# kama round 80 — verifier spot-check (non-author closure)

Lane: kama, round 80 (attempt 1). Base `c45fc7d1a8427e9c98a9dd7befa542c7b5caed38`; lane tip after the
round `a2af1af59faf6cf66fe854559293c4e4b441aff3` (branch `master`, remote-verified). Fleet report
`.ufo/reports/round-80/kama.md` (fleet commit `83bfdc07d9f39aaa38628b82e8c9d8c27cd0fff4`, by
`kama-shokunin <kama@shokunin.local>`). I did not author this round; I verified it. Review date
2026-11-04.

Method note: the three claim counters are lane-owned instruments, and PROTOCOL §Gate standard forbids
executing a sibling lane's gate. I re-derived every ground I could with plain commands over committed
bytes (`git show`, `grep`, `wc`, `awk`, the fleet census) and re-ran the three counters **read-only**
at the tip as corroboration (the lane tree stayed clean: `git status --porcelain` empty afterwards).
C1 and C2 are re-measured; C3's live Ollama fixture is **evidence-verified** from its committed
receipt (I did not start a second server). The one admit and one reject in the lesson's `## Gate`
were re-opened live with `curl`.

## 1. Conformance (step 1)

| Check | Result |
|---|---|
| Report committed in the fleet repo by the lane identity | PASS — `git log --format='%an <%ae> %H' -1 -- .ufo/reports/round-80/kama.md` → `kama-shokunin <kama@shokunin.local> 83bfdc07…`; `git merge-base --is-ancestor 83bfdc07 origin/master` exit 0 |
| `## SHONEN` heading, one line per box | PASS — `grep -c '^## SHONEN'` → `1`; four `[~]` lines (no `[x]`) against the four boxes, each with a pointer (`SHONEN.md` has four boxes) |
| Every cited lane commit exists and is an ancestor of the branch | PASS — all 14 round hashes (`fe7b9780 dea7c269 28debbcf 4ced97ae b7d62643 07ef2adf b93c73af 5fcef757 223c881a 84fd2b21 97cfec8a 08eb6949 1bd94657 a2af1af5`), the base `c45fc7d1`, and the sealed `a9b4543f` resolve; `git merge-base --is-ancestor <h> master` holds for every one |
| Lane repo clean and pushed | PASS — `scripts/hyaku/jj-lane.sh state …` → `branch=master local=a2af1af5… remote=a2af1af5… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git status --porcelain` empty; `git ls-remote origin refs/heads/master` → `a2af1af5…` |
| Prompt carries the template contract | PASS — `.ufo/prompts/kama-round-80.md` (704 lines) carries the round-level items (§1 mission/axes, §2 claims, §3 L2 `≥8` in ONE batched call l.80–82, commit-then-push l.125–127 and §4 l.500+, push scope l.130–131, L0 l.133–134) and all five child-lane items (report path l.101, commit-before-report/landed-last l.500–521, `SHONEN` heading l.118/l.518, commit-hash citation l.487–489, write scope l.441–447); §6 hyaku addendum present. No model alias is pinned as a routing directive (routing is `task.agentModelOverrides`), and `MISSION.md` §L2 carries role-class buckets only, so no quoted route map contradicts the current bucket |
| Wave shape | PASS — `.ufo/waves/round-80/w1-spec.json` `maxLanes: 16`, 13 items; `w1-results.json` has `seats 13`, `results 13`, every seat non-empty; roles 4 executor / 2 scribe / 2 scout / 1 connector / 1 reviewer / 2 critic / 1 mutation-tester; attack 4/13 = 31 %; no residual call; `w1.ready.dispatched` present |
| Report is a real report, not a marker | PASS — Work performed, Landed changes tied to `LOG.md` §Round 80, Before → after, Sources & frontier with its census command, three trend verdicts, four `[~]` SHONEN lines, checkable hashes |

Conformance defects (status-neutral; they do not change the status; routed in §7):

1. **SCORECARD/LOG carry stale selftest tallies.** The §Round 80 C1 row
   (`SCORECARD.md:4781`) says `selftest pass=9 fail=0` and the C3 row (`SCORECARD.md:4783`) says
   `pass=6 fail=0`, both citing `measured/after/{c1,c3}-selftest.out`; the committed receipts at
   `08eb6949` print `pass=11` and `pass=12`. The calibration axis row (`SCORECARD.md:18`) and
   `LOG.md` §Round 80 repeat the pre-hardening tallies. The report's own bullets use the correct
   `pass=11`/`pass=12`, so the defect is confined to SCORECARD and the append-only LOG.
2. **S557's SOURCES URL is dead.** The row's URL
   `…/ollama/v0.40.11/docs/api-openai-compatibility.mdx` returns HTTP 404 (14 bytes); the same file
   exists at `docs/api/openai-compatibility.mdx` (HTTP 200, 25472 bytes, sha256
   `44071a12…cd5` — the digest and size the row itself states). The row's notes anchor says lines
   293–294 where the response notes are 294–295.
3. **S557 has no `## Gate` record.** It was opened after the Gate table was drafted; the lesson's
   `## Gate` records URL/access/≤25-word quote for S554–S556 only, while the frontier contract
   requires that record for every new row.
4. **Validate warning inventory.** The report calls the `W04` warnings "pre-existing"; `S555` adds a
   new `W04` (duplicate URL with `S553`, the supersession pattern). Category pre-existing, one row
   new.
5. **`final-tip-recheck.out` names rev `08eb6949`.** The report calls it "re-run at the final tip";
   the receipt names the measurement revision, which is an ancestor, not `a2af1af5`. The counters do
   re-derive at the true tip (I re-ran them), so this is a wording defect, not a false claim.
6. **Coverage row's last-change cell.** `SCORECARD.md:17` cites a round-80 entry while the cell still
   reads "score round 10; evidence re-anchored round 79".

## 2. Claims (step 2)

### C1 — calibration: the round-79 self-record's six declared facts re-derive or are answered by dated value-bound corrections

- **Grounds re-measured by me at the sealed revision `a9b4543f…`:**
  `git show a9b4543f:SCORECARD.md | grep -n 'C2 operability verified'` → line 6 banner says
  "C2 operability verified"; the §Round 79 C2 row (`:4587`) ends `**verified**`;
  `git show a9b4543f:LOG.md | sed -n '3217p'` → "Three claims, three distinct axes, all verified on
  their receipts"; the row's before cell says `PRE_REPORT_SELFTEST pass=26`.
  `git show a9b4543f:.ufo/waves/round-79/measured/after/c2-gate.out | tail -2` →
  `PRE_REPORT round=79 arms=10 failed=1 uncommitted=0` / `EXIT=1`;
  `…/measured/before/c2-gate-selftest.out | tail -2` → `PRE_REPORT_SELFTEST pass=22`.
  All three declared facts are stale exactly as the counter says.
- **Corrections re-derived at the tip:** `corpus/lessons/round-80.md:28,30,32` carry the three
  backticked blocks, all `at=a9b4543f…`; their `new=` values (`c2=not-verified:failed=1`,
  `before-selftest=pass=22`, `log=c2-not-verified`) each re-derive from the sealed receipt and the
  appended `LOG-CORRECTION round=79 claim=C2 verdict=not-verified` (`LOG.md:3266`).
- **Counter re-run at the tip** (read-only, 2026-11-04):
  `python3 tools/round80-selfrecord-round79.py --repo .` →
  `SELFRECORD_R79 claims=6 mismatches=0 corrected=3 unbacked=0`, `EXIT=0`; F4/F5/F6 `status=corrected`.
  The before receipt prints `SELFRECORD_R79_ENUM claims=6 stale=3 corrected=0`; the no-corrections
  control prints `SELFRECORD_R79 claims=6 mismatches=3 corrected=0`, exit 1.
- **Verdict: verified.** Axis calibration — **improved** (score holds 7; the instrument is new, the
  three stale facts are repaired value-bound, and KQ132 records the class). Bound: the round's own
  SCORECARD/LOG repeat a stale-tally instance of the same class (conformance defect 1, routed).

### C2 — freshness: every pinned serving-engine ref the lane holds carries a dated, re-derivable relation row

- **Grounds re-measured by me** from the committed `git ls-remote --tags` lists under
  `measured/after/c2-tags/` (plain Python over the text; the tool's release regexes from
  `registry/engine-pins.tsv`):

  | engine | ref | tags in list | newer | newest | TSV |
  |---|---|---|---|---|---|
  | llama.cpp | `b11755` | 7608 matching `b(\d+)` | 278 | `b12103` | behind/278/b12103 ✓ |
  | llama.cpp | `39febd2a…` (commit) | — | peeled oid of tag `b11963`; 110 tags newer | `b12103` | tag:b11963/110 ✓ |
  | llama.cpp | `b7200` | — | 3395 | `b12103` | behind/3395 ✓ |
  | sglang | `v0.5.22` | 73 matching `vX.Y.Z` | 1 | `v0.5.23` | behind/1 ✓ |
  | vllm | `v0.32.0` | 88 matching `vX.Y.Z` | 1 | `v0.33.0` | behind/1 ✓ |

  The two cross-references are the lane's own held refs: `S553`'s commit anchor and kengaku's `S178`
  (llama.cpp tag `b7200`, verified in `kengaku-shokunin/corpus/SOURCES.md:193`). All five rows of
  `registry/engine-pin-relations.tsv` match, every `receipt` path exists, every `dated` cell is
  `2026-11-04`.
- **Counter re-run at the tip:** `python3 tools/round80-engine-pin-relations.py --repo . --tags-dir
  .ufo/waves/round-80/measured/after/c2-tags` → `PIN_RELATIONS engines=3 refs=5 unexplained=0`,
  `EXIT=0`. Controls: header-only register `refs=0 unexplained=5` (exit 1); a `current` claim for the
  `behind` llama.cpp pin `unexplained=1` with `derived=behind/278/b12103` (exit 1).
- **Verdict: verified.** Axis freshness — **improved** (score holds 8; five dated relation rows and a
  new offline counter, capability `engine-pin-relations`).

### C3 — operability: the `registered` census class is proven on a second engine fixture and its engine coverage is a register

- **Evidence-verified from the committed receipt** `measured/after/c3-ollama-census.json`:
  `engine=ollama`, `port=54939`, two probe legs (registered `yes`: `governed=1/unregistered=0`;
  registered `no`: `governed=0/unregistered=1`, same listener/owner), `class_missing=0`,
  `version=0.40.11`, `teardown returncode=0`, `port_closed=true`. The pinned binary exists at
  `/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama` (`--version` prints client 0.40.11) and the
  model fixture `stories260K.gguf` exists. The fixture leg prints
  `OLLAMA_CENSUS port=54939 engine=ollama unregistered=1 governed=1 class_missing=0` (`EXIT` 0 in the
  committed `.out`).
- **Registry audit grounds:** `registry/unregistered-class-engines.tsv` has two rows (llama.cpp,
  ollama); both receipts exist and each receipt's own engine token names its row's engine
  (`# engine: llama.cpp` in `c3-llamacpp-recheck.out`; `engine=ollama` in the JSON/`.out`).
  Counter re-run at the tip: `python3 tools/round80-ollama-census.py --repo . --audit` →
  `CLASS_ENGINES engines=2 verified=2 stale=0`, `EXIT=0`. Controls: the pre-class probe
  `class_missing=1` (exit 1), a one-engine register `engines=1` (exit 1).
- **Verdict: verified** (live fixture evidence-verified, not re-executed). Axis operability —
  **improved** (score holds 8; second engine fixture + `class-engine-register` capability).

## 3. Axis harm check

`git diff c45fc7d1 a2af1af5 -- SCORECARD.md`: the score vector holds **8 / 8 / 7 / 9 / 7 / 7**
(operability, freshness, depth, coverage, calibration, adjacency); no axis retired; three capability
rows enter (`selfrecord-round79`, `engine-pin-relations`, `class-engine-register`), each demonstrated
running this round; no admitted entry was found false and left unmarked. The stale-tally and S557
locator defects above move no score (PROTOCOL §Gate standard closure consequence: gate/record redness
is status-neutral; the false self-record class was routed, not scored, in the round-79 closure too).
**No axis harmed.**

| Axis | Verdict | Evidence |
|---|---|---|
| operability | **improved** | C3 verified; `CLASS_ENGINES engines=2 verified=2 stale=0`; score 8 held |
| calibration | **improved** | C1 verified; three value-bound corrections; score 7 held; stale-tally defect routed |
| freshness | **improved** | C2 verified; five relation rows over three engines; score 8 held |
| coverage | **unchanged** | no coverage claim this round; the frontier entry is credited under expansion; score 9 held |
| depth | **unchanged** | no `SKILL.md` change in the diff; score 7 |
| adjacency | **unchanged** | no sibling absorption; connector scan reports shared llama.cpp refs; `PROVINCE.md` note only; score 7 |

## 4. Discernment spot-check (step 3, non-author)

| Item | Decision | Re-opened source | Agree/disagree | Reason |
|---|---|---|---|---|
| S554 Ollama `docs/api.md` v0.40.11, `GET /api/tags` | admit | `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md` → HTTP 200, 54614 bytes, sha256 `96db0308…d0f5` | **agree** | quote "List models that are available locally." is verbatim at line 1358 under `## List Local Models` (heading 1352, `GET /api/tags` 1355); bytes/digest match the row; the scope ("inventory, not `/api/ps` residency") is exactly what the page supports; tier A docs fits; `used-by` resolves |
| S556 llama.cpp `docs/preset.md` at 39febd2a | reject | `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2a…/docs/preset.md` → HTTP 200, 4090 bytes, sha256 `3e664354…f13` | **agree** | quote "allows users to create reusable and shareable parameter configurations for llama.cpp" is verbatim at line 5 (`## Introduction`); the round's class reads a model list and parses no preset, so the rejection is right; the row carries `REJECTED: …; flip: …` (the round-79 R79V4 gap is closed) |
| S555 supersession of S553's anchor | admit | `https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2a…/tools/server/README.md` → HTTP 200, 135608 bytes, sha256 `8fd5abde…35c6` | **agree** | quote "If a model is not running, it will be added or updated according to the source" is line 2227 under `### GET \`/models\`: List available models` (heading 2197); the bytes are byte-identical to S553's, so the row is an anchor supersession, not a new source |
| S557 Ollama OpenAI-compatible `/v1/models` (added after the Gate draft) | admit stands; **locator defect** | row URL → HTTP 404 (14 bytes); `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx` → HTTP 200, 25472 bytes, sha256 `44071a12…cd5` | **disagree on the locator** | the row's stated digest/size and anchors (`## Endpoints` 209, `### /v1/models` 290) match the real file; the URL omits `api/`, so the row as written cannot be re-opened. The decision to record the route is sound; the pointer is wrong (routed) |

Census: `scripts/sources-census.sh census --file <blob>` at both revisions, exit 0 both times:
base `c45fc7d1` **293** rows (A 278 / B 11 / C 4; mined 264, queued 8, rejected 21) → tip **297**
(A 282 / B 11 / C 4; mined 267, queued 8, rejected 22) — matches the report. Validation
`scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama` → exit 0; warnings are
the pre-existing `W04` set plus the new `S555` duplicate URL (same URL as `S553`, the supersession
pattern) and the pre-existing `W01 S481` tier-C-mined row; no malformed row, duplicate id or tier
inflation.

## 5. Trend verdicts

| Trend | Verdict | Evidence |
|---|---|---|
| expansion | **improved** | net new admitted `corpus/knowledge/unregistered-class-second-engine.md` (`source: S554`) on ground the coverage map did not hold; registry 293 → 297 rows with S554/S555/S557 mined and S556 rejected; three capability rows entered and demonstrated; bound: S557's dead URL is a locator defect, not a missing source |
| quality | **improved, bound** | the round-79 overstatement is repaired value-bound in three places; R79V1–R79V7 disposed; `round78-live-reconcile.py`'s selftest no longer dirties the wave dir (red-before shows the two dirty files, after shows `wave-78 dirties: 0`); KQ132 cites the lesson; the pre-report gate's arm 8 red is disclosed, not hidden. Bound/regression: the round's own SCORECARD/LOG selftest tallies are stale against their receipts (defect 1) — the same record class KQ132 names |
| discernment | **improved, bound** | this spot-check agrees with the sampled admit (S554) and reject (S556), and with S555; the Gate records 2 admits + 1 reject with located quotes; the S557 row is the one disagreement and it is routed with its evidence, not left unlearned. Bound: S557 was added after the Gate, so the lane's own gate did not review it (defect 3) |

## 6. Routed defects the lane must fix next round

1. **R80V1 — stale selftest tallies (recurrence of the KQ132 class).** `SCORECARD.md:4781` (C1),
   `:4783` (C3) and the calibration row `:18` cite `pass=9` / `pass=6` while
   `measured/after/c1-selftest.out` and `c3-selftest.out` at `08eb6949` print `pass=11` and
   `pass=12`; `LOG.md` §Round 80 repeats `pass=9` / `pass=6`. Append a `LOG-CORRECTION` entry and a
   SCORECARD appended correction naming the superseded tallies (append-only; do not rewrite the
   filed bytes), or re-point those rows to the `4ced97ae` receipts they actually match; then re-run
   the counter at the tip.
2. **R80V2 — S557 locator.** The row URL is missing `api/` (404); correct it to
   `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api/openai-compatibility.mdx`
   (200, 25472 bytes, sha256 `44071a12…cd5`) through a superseding row (`teaches: supersedes S557 —`),
   never an in-place rewrite (SOURCES contract v1 rule 2); the response notes are lines 294–295, not
   293–294.
3. **R80V3 — S557 Gate record.** Add the URL, access date and a ≤25-word located quote for S557 to a
   `## Gate` section (the next round's lesson, or an appended Gate erratum), as the frontier
   contract requires for every new row.
4. **R80V4 — warning inventory.** The validate run's `W04` set is not wholly pre-existing: `S555`
   (same URL as `S553`) is new this round. State it in the next census note.
5. **R80V5 — receipt label.** `measured/after/final-tip-recheck.out` names rev `08eb6949`; either
   re-run the three counters at `a2af1af5` and commit that receipt under the same name, or call it
   the measurement revision in the report/SCORECARD.
6. **R80V6 — coverage row last-change cell.** `SCORECARD.md:17` cites a round-80 entry but keeps
   "score round 10; evidence re-anchored round 79"; align the cell with the evidence it now carries.

## 7. Verdict

Status `ok` (real report, real committed work, every cited hash landed and pushed). Every declared
claim verifies — C1 and C2 re-measured by me, C3 evidence-verified from its committed receipt — and
no axis is harmed; the record defects above are conformance defects, routed, and move no score.
**Admitted.**
