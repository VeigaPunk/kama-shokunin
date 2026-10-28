# L04LessonsSweep — round-62 mistake-evidence sweep (kama, w1)

Axis: operability. Read-only inventory + one local (no live endpoint, no build/lint/test) grade
differential. Lane tip at scan: `65d7cad0fce90e34de37527cde22e97b63b118bf` (`git rev-parse master`);
scan 2026-10-28T09:31:58-03:00, wave still in flight, so counts are a snapshot that only grows.
Fleet root head at scan: `db40fff7788324e45d842c75afdca36ff301951a`.

Commands used: `git status --porcelain`, `git ls-files --others --exclude-standard`,
`git status --porcelain --ignored=matching`, `git diff`, `git show <tip>:<path>`, `git log`,
`sha256sum`, `cmp`, `find`, `awk`, plus one python import of the tip counter and the working-tree
counter to grade four existing receipts. No git/jj mutation, no commit, no live server, no lane
source edit. Nothing installed or upgraded.

Receipts for every claim below are in `.ufo/waves/round-62/w1/out/L04LessonsSweep/`
(`lane-status.txt`, `untracked.txt`, `tracked-diff.patch`, `ignored.txt`, `nested-misroot.txt`,
`path-citation-scan.txt`, `c1-tip-vs-worktree-grade.txt`, `fleet-status.txt`, `fleet-head.txt`,
`tip.txt`, `scan-time.txt`).

## 1. Claim-critical: the C1 instrument at the tip is not the instrument on disk

`git status --porcelain` (lane) is exactly:

```
 M corpus/SOURCES.md
 M tools/round62-c1-counter.py
```

Both modifications are **uncommitted** and both are load-bearing for the frozen claims.

### 1a. `tools/round62-c1-counter.py` — the working-tree fix is the only counter that can reach C1

Working-tree diff (full text in `tracked-diff.patch`): `u = cj.get('usage')` → `(cj or {}).get('usage')`,
`t = cj.get('timings')` → `(cj or {}).get('timings')`, and `if 'hold' in (receipt.get('checks') or {})`
→ `if 'hold_released' in ...`.

I loaded the committed blob (`git show <tip>:tools/round62-c1-counter.py`) and the working-tree file
side by side and called `grade()` on four existing `REQUEST_OK` receipts written by other seats this
wave (E01 `receipts/run1.receipt.json`, E07 `A2-edge-repeat.json`, A02
`c1-hold-tamper-counter-live-receipt.json`, M05 `receipt-pristine.json`). Verbatim
(`c1-tip-vs-worktree-grade.txt`):

```
=== .../E01CompletionRepeat/receipts/run1.receipt.json  verdict=REQUEST_OK checks=17
  tip:  recomputed=17 hold_released_key=False inconsistent=['unexpected-checks']
  work: recomputed=18 hold_released_key=True  inconsistent=[]
  [tamper: captures.completion.body mutated, body_sha256 untouched]
  tip:  RAISED AttributeError: 'NoneType' object has no attribute 'get'
  work: inconsistent=['completion_deterministic', 'completion_envelope', ...]
```

All four receipts behave identically. Consequences the L1 has to name in the report:

- At the committed tip, `grade()` recomputes 17 checks while every receipt stores 17 keys including
  `hold_released`; `set(stored) != required` therefore appends `unexpected-checks` on a *perfect*
  receipt — the tip counter rejects every real receipt. The spec-time line "C1 met=True at tip
  `65d7cad0`" is reproducible only from the working tree, not from the tip bytes.
- At the committed tip the counter also raises `AttributeError` on the tamper family (body mutated,
  `body_sha256` untouched), i.e. the control rejects by crashing, not by grading —
  `measured/c1-before-fix.txt` says the same thing independently.
- Therefore: if the L1 commits, the tip changes and the final C1 measurement must be re-run at the
  new tip and cite the new tip; if the L1 does not commit, the wave's `met=True` is measured against
  bytes nobody can check out. Either way the delta must be stated; it is currently stated only in
  `corpus/lessons/round-62.md` §Mistakes, not in a report.

### 1b. `corpus/SOURCES.md` — one appended row, outside the freeze's literal fix list

`+ S526`, llama.cpp server README @ `704366d76` (`/v1/completions` surface). Row shape is valid:
11 fields, matching the header order of the registry table, same as S525. `corpus/lessons/round-62.md`
§Gate admits S526 and carries the located quote. The freeze's "Fix (only delta vs base)" lines for C1
and C2 do not name `corpus/SOURCES.md`, and every other `registry/` + `SCORECARD.md` change is
already committed at the tip. Name this row in the report (admitted source) or revert it — do not
leave it unattributed in the working tree.

## 2. Untracked inventory (snapshot: 228 files; 5 outside round-62)

`git ls-files --others --exclude-standard` at scan time — full list in `untracked.txt`.
Breakdown: 44 `w1/<Seat>.md` reports, 172 `w1/out/**` receipts, 3 `w1/*.json` inputs
(`w1-spec.json`, `w1-dispatch.json`, `swarm-registry.json`), 2 wave markers, 2 other round-62
entries, 5 outside round-62.

Precedent for what earlier rounds actually committed, measured with `git ls-files`:
round-58 = 507 files (reports and `out/` receipts committed), round-59 = 161, round-60 = 710,
round-61 = 13 (only `controls/`, `measured/`, `live/receipt.json`, `w1/*.json`, `w1.ready`,
`assimilation/quarantine-slice`). So there is no single house rule; the L1 must state the policy it
picks and name the two extremes rather than let `git add -A` decide.

### 2a. Deliverables that read as intended (name in the report, then commit)

- `corpus/lessons/round-62.md` — every round 1…61 has one; this file is the round's lesson and it is
  currently untracked.
- `corpus/knowledge/completion-request-plane.md` — new knowledge doc backing S526 and the C1 claim.
- `.ufo/waves/round-62/w1.ready` — tracked in round-61; precedent to commit.
- `.ufo/waves/round-62/w1/{w1-spec.json,w1-dispatch.json,swarm-registry.json}` — all three tracked
  in round-61.
- `.ufo/waves/round-62/measured/c1-before-fix.txt` — the only receipt of the pre-fix crash the lesson
  cites; keep it (name it as *before-fix*, not as a measurement of the claim).

### 2b. Do not commit

1. **`kama-shokunin/` — nested misroot inside the lane.** `kama-shokunin/.ufo/waves/round-62/w1/`
   exists in the lane working tree and holds exactly one file,
   `A04C1SchemaFuzz.md` (4412 B, mtime 09:26:49). It is a *superseded* revision of the canonical
   report: sha256 `1111b74787af74…` vs canonical `.ufo/waves/round-62/w1/A04C1SchemaFuzz.md`
   sha256 `9589790dd76ede…` (mtime 09:27:14); the diff is wording-only, no result changes
   (`nested-misroot.txt`). Root cause: the A04C1SchemaFuzz seat wrote its Report path
   (`kama-shokunin/.ufo/...`) with the lane as cwd instead of the fleet root. It is untracked,
   it is inside the A04 seat's write scope. A fleet-wide existence probe (`[ -d $d/$d ]` over the
   21 `*-shokunin` directories) finds exactly two such nested self-named directories:
   `kama-shokunin/kama-shokunin` (this one, created 09:26 today) and
   `kotodama-shokunin/kotodama-shokunin` (pre-existing, not inspected, other lane). The L1 should
   delete the kama copy (with the seat, or itself) and say so.
2. **`.ufo/scopes/kama-r57-w1/swarm-registry.json`** — round-57 leftover, 43 members, milestone text
   "64-seat mixed counter repair…". `git log -- .ufo/scopes` is empty: no `.ufo/scopes` path has ever
   been tracked in this lane. Round-60's report already flagged it as inherited and untouched.
   `git add -A` would commit it for the first time.
3. **`.ufo/waves/round-61/w1.ready.dispatched`** — a closed-round marker whose body is an operator
   note (`closed-round stale: r61 closed admitted before dispatch…`). It belongs to round 61; the
   `w1.ready.dispatched` convention has never been tracked (round-62's own is untracked too).
4. **Byte-identical duplicate reports** — four pairs, same sha256, one copy under `w1/`, one inside
   `w1/out/`: `E03SelftestsA.md` + `out/E03SelftestsA/E03SelftestsA.md`,
   `E02ReceiptGrade.md` + `out/E02ReceiptGrade/report.md`,
   `M03C1AttackThe.md` + `out/M03C1AttackThe/findings.md`,
   `M10C2AttackRename.md` + `out/M10C2AttackRename/M10C2AttackRename.md`. Commit one location.
5. **Derived counter copies in `out/`** — `out/E01CompletionRepeat/derived-only-cjguard.py.txt`,
   `tip-counter-at-tip-master.py.txt`, `derived-2line.*`. These are 2-line-guard variants of the
   frozen counter; as evidence they are fine, but if committed they must be introduced as *derived
   probes*, never in a form that reads as the instrument (this is exactly the ambiguity that makes
   §1a hard to audit).
6. **`.ufo/waves/round-62/M18C2ManifestForger.md`** — the only seat report outside `w1/`; every other
   seat wrote `w1/<Seat>.md`. It sits at the wave root. Move or name it, otherwise the report sweep
   glob `w1/*.md` silently misses one seat.

## 3. Stale, empty, and mis-cited paths

- **The C1 live receipt has no home.** `.ufo/waves/round-62/live/` is empty (created 08:01, attempt 1);
  round-61 tracked `.ufo/waves/round-61/live/receipt.json`. Both new corpus docs cite
  `.ufo/waves/round-62/measure/c1b/receipt.json` (`corpus/knowledge/completion-request-plane.md:1`,
  `corpus/lessons/round-62.md:22`) and **that path does not exist** — `.ufo/waves/round-62/measure/`
  is absent entirely. Copy the counter's `<work>/receipt.json` into `.ufo/waves/round-62/live/` and
  fix both citations before report, or the claim's durable evidence is a scratch path that is
  already gone (`path-citation-scan.txt`).
- **No final measurement receipts.** `measured/` holds only `c1-before-fix.txt`; round-61 precedent is
  `c1-tip.txt`, `c1-final.txt`, `c2-tip.txt`, `c2-final.txt`. Round-62 has none of the four.
- **Wrong watchdog path in the lesson.** `corpus/lessons/round-62.md` cites `.ufo/watchdog.log`; no
  such file exists in the lane. The real file is the fleet root's
  `/home/vgpnk/Projects/shokunin/.ufo/watchdog.log`. I verified the quoted line there, verbatim at
  line 1824: `2026-10-28T08:59:38-03:00 lane-dead-no-report kama round=62; retry same round
  (hyaku-inline attempt=1: KamaR62 stopped on a wrap-up notice before freeze: drafts only
  (tools/round62-c1/c2 counters uncommitted), no wave, no report)`. The quote is accurate; only the
  path is lane-relative when it should be fleet-root-relative (or absolute).
- **Empty attempt-1 scaffolds**: `.ufo/waves/round-62/live/` (08:01), `source/` (08:51),
  `hexrun-evidence/` (08:54) contain nothing. Git cannot record empty directories, so they will
  vanish silently at commit — if any of them was meant to hold evidence, the evidence is missing,
  not "in progress".
- **Orphan `out/` dirs with no receipts**: `M02C1AttackThe`, `M06C1AttackThe`, `S01CensusRerun`,
  `S06OllamaDoc` are empty while those seats filed reports at `w1/`. Either the receipts were
  written to scratch and destroyed, or the seats produced report-only claims; the L1 should say
  which before relying on them.
- **Unattributed archived-counter execution**: `.ufo/waves/round-25/__pycache__/count-c2.cpython-314.pyc`
  was created **today 09:10:38**, i.e. some seat *imported* the archived round-25 `count-c2.py`
  during this wave. A `__pycache__` only appears on import, so this is not "the file was read".
  `tools/round62-c2-counter.py` contains no reference to round-25 (grep). Gitignored, so it cannot be
  committed, but it is evidence that an old instrument was loaded in a round whose whole point is
  bound instruments — worth asking the C2 seats.
- Ignored-but-present (13 paths, `ignored.txt`): all `__pycache__` plus
  `round-34/assimilation/validate/registry/history/{.lock,2×json}`, i.e. pre-existing, none is a
  round-62 artifact that needs rescue.

## 4. Fleet-root `git status --porcelain` — attribution

```
 M .ufo/reports/round-58/chousa.md
?? .scratch/closure-mado-r50.json
?? .scratch/source-routing-queue.md
?? o.bin
?? oldrep1.out
?? oldrep2.out
```

- **Pre-existing, already named by prior lane reports** (rounds 40, 41, 58 kama, 60, 76, 77, 78, 79,
  80, 81): the chousa round-58 modification, the two mado/orchestrator `.scratch` files, and `o.bin`
  (5867 B, a Cloudflare "Just a moment…" HTML capture from 2026-10-27 16:58). `git grep` shows these
  five paths are the standing fleet-root residue.
- **New today, and misrooted**: `oldrep1.out` (09:10) and `oldrep2.out` (09:11) are **byte-identical**
  (`cmp` silent, both 15314 B) and their last line is
  `TSUKUROI_CENSUS_SELFTEST: PASS (164 cases, 164 passed, 0 failed)`. The producer is
  `tsukuroi-shokunin/tools/tsukuroi-census.sh`; neither file names kama, round 62, or any kama tool.
  They are untracked and **not** covered by the fleet `.gitignore`, so an L1 running `git add -A` at
  the fleet root would commit another lane's selftest captures into fleet history. They are that
  lane's to remove; kama must not commit or delete them, only name them.
- **No kama artifact is misrooted at the fleet root.** The only kama-shaped path is the lane
  directory itself.

## 5. Citation scan: two alarm-raisers that are false alarms

I resolved every `` `(\.ufo|tools|corpus|registry)/…` `` path cited by the 50 untracked `.md` files
(110 citations, `path-citation-scan.txt`). Five resolve missing; three are real (the `measure/c1b`
receipt ×2 and the watchdog path, §3), and two are correct as written — do not let them cost time:

- `tools/check-receipt.py` (R04HarmAudit) — the report *documents* that the assignment-named tool is
  absent; the "MISS" is the finding, not a broken reference.
- `tools/server/README.md` (S02LlamaCppSpec) — a path *inside* the pinned llama.cpp source tree
  (`raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/README.md`), not a lane path.

## 6. Tally

No verdict on C1 or C2 is offered here; §1a is a reproducibility fact about the tip bytes, and the
claim verdict belongs to the L1 and the non-author verifier.

```
L04 tally: tip=65d7cad0 modified_tracked=2 claim_critical_uncommitted=2 (c1-counter grade fix, SOURCES S526)
untracked=228 [w1_root_md=44 w1_out=172 w1_inputs=3 markers=2 round62_other=2 outside=5]
nested_misroot=1 stale_leftover=2 (scopes/r57, r61 dispatched) dup_report_pairs=4
missing_cited=1 (round-62/measure/c1b/receipt.json) wrong_path_cited=1 (watchdog) missing_measured=4 live_receipt=absent
empty_attempt1_dirs=3 orphan_out_dirs=4 archived_counter_import=1 fleet_misroot=6 [pre_existing=4 new_today=2]
```
