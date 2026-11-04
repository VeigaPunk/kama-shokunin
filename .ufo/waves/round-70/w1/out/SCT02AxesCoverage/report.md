# SCT02AxesCoverage — `## Axes` anchor coverage at tip `6035e952`

Seat: SCT02AxesCoverage (round 70, lane kama, axes operability + calibration).
Reconnaissance only: **no lane file was edited, created or deleted.** Every write is under
`.ufo/waves/round-70/w1/out/SCT02AxesCoverage/` and `/fast/scratch/hyaku/kama-r70/SCT02AxesCoverage/`
(the scratch tree is removed before yield). Read-only git only.

Tip under measurement: `6035e952c2521999e192d6f236331f265ac98392` (round-69 verifier spot-check;
lane HEAD at recon was `0e14facd0c619f45a6461821d2bd80ddac9855b1`, which only adds round-70 controls).

---

## 1. Instrument model (what actually parses the six rows)

`tools/round41-scorecard-reconcile.py` (`m41.evaluate`) is the only instrument that reads the
`## Axes` table itself. Population: `m41.axes_table()` = the first Markdown table after the line
that is exactly `## Axes`, header+separator dropped, so at this tip **lines 12-19** (six data rows;
lines 10-11, the intro paragraphs, are *not* in the population). Per data row it parses:

| reader | regex / rule | what it proves |
|---|---|---|
| HASH | `` `PATH`\s+(md5\|sha256)\s+`HEX` `` | blake-of-blob at tip (`git cat-file -p <tip>:PATH`) |
| LINES | `` `PATH`…\s+\((\d+) lines `` | `blob.count(b"\n")` at tip |
| RUN | `` run `CMD` (→\|->) `OUT` `` + optional `(exit N)` | executes `bash -c CMD` with cwd = a `git archive` export of the tip; passes iff **some stdout line, stripped, equals OUT** and exit matches |
| PATH | every other backticked repo-relative token (`.md .py .sh .tsv .json .out .txt .jsonl .csv`, or `.ufo/ corpus/ tools/ registry/ tests/ plans/`; no space, no `< > * $ ~ \| =`) | `git cat-file -e <tip>:PATH` only |
| score | last integer of cell 2 vs the counter's **hardcoded** `EXPECTED` dict | score equals the lane's last-declared vector, not a tree fact |
| hollow | a row with zero HASH and zero RUN facts | flags weak rows |

`mismatches = score_bad + hash_bad + lines_bad + run_bad + dead + hollow + (6 - axes)`.

`tools/round42-selfdesc-reconcile.py` re-uses that r41 evaluation (`c["r41"] = r41c["mismatches"]`)
and adds `banner, planned, retired, saturation, caps, receipts, readme, province, rel, closure_ptr`.
Of these, only `province`, `rel` and `closure_ptr` touch the `## Axes` rows; `saturation` and
`retired` read the vector *from* the table (so they cross-check other sections against the table,
never the table against the tree).

**No standing instrument re-runs either counter.** The per-round census
`tools/round65-host-census.py` runs 22 *selftest* arms (tier A/B); its only r42 arm is
`round42-selfdesc-reconcile selftest`, and that arm is **refused on this host** (NTFS path, the
round-65 L0 question) — see `.ufo/waves/round-69/measured/host-census-final.out` at the tip:
`refused [A] round42-selfdesc-reconcile selftest: fail-closed refusal: the lane holds a tracked path
NTFS cannot check out…`, `HOST_CENSUS pass=20 fail=0 refused=2 total=22`, `EXIT=0`. There is **no
census or snapshot arm that runs the live reconciler**, so the six rows are re-derived only when a
round invokes the counter explicitly.

---

## 2. Observed instrument output at the tip (the base state)

```
$ python3 tools/round41-scorecard-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 6035e952
tip=6035e952c2521999e192d6f236331f265ac98392
axes=6 facts=44 hash_bad=0 lines_bad=0 run_bad=2 dead=0 score_bad=0 hollow=0 mismatches=2 met=False
detail: operability run `python3 tools/gate-registry-check.py --selftest` no stdout line == 'GATE_SELFTEST pass=7 fail=0' (exit 1)
detail: calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` no stdout line == 'NEWEST_CLOSURE … row_current=true' (exit 2)
EXIT=1
```
```
$ python3 tools/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip 6035e952
r41=2 banner=1 planned=1 retired=1 saturation=0 caps=0 receipts=0 readme=0 province=4 rel=0 closure_ptr=0 mismatches=10 maxN=69 met=False
detail: r41 operability run `python3 tools/gate-registry-check.py --selftest` … (exit 1)
detail: r41 calibration run `python3 tools/round69-newest-closure-counter.py --since-round 63` … (exit 2)
detail: banner: head lacks 'Latest measured round: 69'
detail: planned: section does not name '### Planned (round 70)'
detail: retired: does not state '15 capabilities'
detail: province: PROVINCE.md lacks tools/round67-worktree-landing-check.py (capability worktree-landing-check)
detail: province: PROVINCE.md lacks tools/round68-receipt-pointer-audit.py (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks registry/receipt-pointer-resolutions.tsv (capability receipt-pointer-audit)
detail: province: PROVINCE.md lacks tools/round69-newest-closure-counter.py (capability newest-closure-counter)
detail: closure_ptr: calibration row latest outside closure is round-68; newest at tip is round-69
EXIT=1
```
This reproduces the frozen C1 base (`mismatches=10`, exit 1) exactly. Every one of the 44 r41 facts
and all six hashes/line counts were also re-derived by hand below (independent commands, §9).

---

## 3. The table: row | cited identity | re-derived by | observed at tip 6035e952 | gap?

Legend — `OK`: instrument re-derives it and it holds. `STALE`: instrument re-derives it and it is
**false at the tip**. `HARNESS`: cited as an r41 RUN fact but **structurally unreproducible** in
r41's harness. `NONE`: no instrument re-derives it (observed by hand here; may still be true).
`WEAK`: re-derived but degenerate (cannot detect drift). `PROSE`: a limit/history sentence with no
identity to re-derive. `…` inside a quoted identity is my elision unless marked `[literal …]`.

### operability (score 8)

| cited identity (verbatim) | re-derived by | observed at tip | gap? |
|---|---|---|---|
| `` `tools/kama-probe.sh` sha256 `4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4` `` | r41 HASH | equal | OK |
| `(1138 lines)` | r41 LINES | 1138 | OK |
| ``run `bash tools/test-snapshot.sh` → `RESULT pass=30 fail=0` `` | r41 RUN | passes in r41's tip export | OK |
| ``run `python3 tools/pin-watch.py selftest` → `selftest pass=9 fail=0` `` | r41 RUN (+ `rel` needle `pin-watch.py selftest`) | passes | OK |
| ``run `python3 tools/report-landing-audit.py --selftest` → `selftest cases=79 failed=0` `` | r41 RUN | passes | OK |
| ``run `python3 tools/sources-append-only.py --selftest` → `46/46 selftest cases passed` `` | r41 RUN | passes | OK |
| ``run `python3 tools/round67-worktree-landing-check.py --selftest` → `WLC_SELFTEST pass=6 fail=0` `` | r41 RUN | passes | OK |
| ``run `python3 tools/gate-registry-check.py --selftest` → `GATE_SELFTEST pass=7 fail=0` `` | r41 RUN | **export (r41's harness): `GATE_SELFTEST pass=6 fail=1`, exit 1**; real repo: `GATE_SELFTEST pass=7 fail=0`, exit 0 | **HARNESS (F1)** |
| `` `git ls-tree HEAD` `` | nothing (`path_like` rejects the space) | token is a command fragment, not checkable | NONE (harmless) |
| "the worktree-mode population is tree-authoritative since round 69" | only the run fact above (which cannot execute) | repo re-derivation supports it; r41 cannot | HARNESS |
| "Limit: the registered endpoints sample DEAD …" | — | prose limit | PROSE |

### freshness (score 8)

| cited identity | re-derived by | observed | gap? |
|---|---|---|---|
| `` `tools/test-snapshot.sh` sha256 `236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646` `` | r41 HASH | equal | OK |
| `(194 lines)` | r41 LINES | 194 | OK |
| ``run `python3 tools/citation-provenance.py --selftest` → `selftest: ok (24 cases)` `` | r41 RUN (+ census tier-A arm) | passes | OK |
| `` `.ufo/waves/round-41/c2/ls-remote-vllm.txt` sha256 `13388e483163357aa4daea784d0e67cdc8d6b5438d3166d613a2a044590b9282` `` | r41 HASH | equal | OK |
| ``run `python3 -c "recheck=[…]<=477]…"` → `218` `` | r41 RUN | 218 (hand re-derived 218) | OK (but the count is capped at S477 by construction — it can never grow) |
| "rows S001–S477" | embedded in the run command's filter only | consistent with the command | OK |
| `` `registry/release-recheck-b11889.tsv` `` | r41 PATH (existence) | exists | OK (existence only) |
| "the 91 `on-release` registry rows" | **nothing** at tip (r44 audit is frozen to base `9d9cc93e` + needs `--upstream`; not in the census) | ledger has 91 data rows; the *tip's* SOURCES population was not re-derived by any instrument | **NONE (F2)** |
| "§Round-44 measured results: 82 holds, 3 holds-reworded, 6 unchanged-file, 0 drifted, 0 removed" | **nothing** standing (same r44 audit) | re-counting the committed ledger's verdict column gives exactly 82/3/6/0/0 (91 rows) — true, but only because I recounted it by hand | **NONE (F2)** |
| `` `tools/round44-release-recheck-audit.py` `` | r41 PATH | exists | OK (existence only) |
| "§Round-44 measured results" | nothing (r42 `receipts` covers only `.ufo/` tokens in sections whose heading names round 40/41) | heading exists at line 2391 | NONE (section-ref unchecked) |
| "Limit: snapshots are invocation-driven (no clock)…" | — | prose | PROSE |

### depth (score 7)

| cited identity | re-derived by | observed | gap? |
|---|---|---|---|
| `` `SKILL.md` sha256 `86be9083a1ddc4453fc57a0d3980502bd497455902a2b00f653c4239ea0818b8` `` | r41 HASH | equal | OK |
| `(1721 lines)` | r41 LINES | 1721 | OK |
| ``run `grep -c '^## ' SKILL.md` → `48` `` | r41 RUN (+ `rel` needle `SKILL.md`) | 48 (hand re-derived 48) | OK |
| `` `corpus/knowledge/endpoint-identity.md` sha256 `0100ac6d…` `` | r41 HASH | equal | OK |
| `(218 lines)` | r41 LINES | 218 | OK |
| "the round-68 sha had drifted … — lesson Mistake 4" | **nothing**: no backticked path, so r41's PATH reader never sees it; r42 never reads cell 4 or prose | `Mistake 4` exists as item 4 of **three different lessons** (`round-67.md` registry-row placement, `round-68.md` check-polarity, `round-69.md` the depth-row drift — the intended one). Literal string `Mistake 4` occurs only in `round-66-verifier-spotcheck.md:85` and `round-69.md` | **NONE (F3, the r68 depth-row class)** |
| "score round 1; evidence re-anchored round 69" (cell 4) | **nothing** — no counter parses cell 4 | unverifiable by any instrument | **NONE** |

### coverage (score 9)

| cited identity | re-derived by | observed | gap? |
|---|---|---|---|
| `` `PROVINCE.md` sha256 `f0aaae9ccfd0ecb6641ad1646934f4ff5555fcc45d2e397670b2eb5ff083e8a6` `` | r41 HASH | equal | OK |
| `(270 lines; round-67 serving-side fixture surface markers)` | r41 LINES (270) | 270 | OK for the count; the "round-67 markers" parenthetical is PROSE |
| ``run `python3 -c "import glob;print(len([…'engine-sides' not in f and 'processes' not in f]))"` → `39` `` | r41 RUN (+ `rel` needle `corpus/knowledge`) | 39 (hand re-derived 39) | OK |
| `` `corpus/knowledge/ollama-live-lifecycle.md` `` / `` `…ollama-live-amendment-r61.md` `` / `` `…completion-request-plane.md` `` | r41 PATH | exist | OK (existence only; "round 60/61/62 added" is PROSE) |
| "last re-derived at 36 in round 60; the `38` … stale — re-derived `39` in round 66, lesson Mistake 3; re-derived `39` again in round 67" | **nothing** | `grep -rn 'Mistake 3' corpus/lessons/` → **0 hits**; the referent is item 3 of `corpus/lessons/round-66.md` ("number-drift (inherited) · the SCORECARD coverage row's knowledge count said 38…"), while item 3 of `round-68.md` is a different class | **NONE (F3)** |
| `` `corpus/knowledge/endpoint-health-probe-conventions.md` ``, `` `…kv-cache-reclamation-models.md` ``, `` `…serving-alias-contract.md` `` ("held ground includes") | r41 PATH | exist | OK (existence only; the "held ground" claim itself is unchecked) |

### calibration (score 7)

| cited identity | re-derived by | observed | gap? |
|---|---|---|---|
| ``run `python3 tools/capability-repertoire-audit.py --selftest` → `CAP_SELFTEST pass=2 fail=0` `` | r41 RUN (+ census A) | passes | OK |
| ``run `python3 tools/round68-receipt-pointer-audit.py --selftest` → `9/9 selftest arms passed` `` | r41 RUN (+ census A) | passes | OK |
| ``run `python3 tools/round69-newest-closure-counter.py --selftest` → `10/10 selftest arms passed` `` | r41 RUN (+ census A) | passes | OK |
| ``run `python3 tools/round69-newest-closure-counter.py --since-round 63` → `NEWEST_CLOSURE … row_current=true`, exit 0`` | r41 RUN (fails) + r42 `closure_ptr` (fails) | **repo: `NEWEST_CLOSURE … round=69 row_names=…round-68… row_current=false` + `STALE_CALIBRATION`, exit 1; export: `COULD_NOT_EVALUATE`, exit 2.** The row's expected string is not even a line this tool can print (its format is `NEWEST_CLOSURE newest=<file> date=<iso> round=<n> row_names=<file> row_current=<true\|false>`; the row's `[literal …]` is an ellipsis) | **STALE + HARNESS + non-literal expectation (F1, F4)** |
| "verifier-spotcheck population and latest outside closure are derived at the measured tip by `python3 tools/round59-c2-counter.py --repo <repo> --tip <rev> --fleet-ref HEAD`" | r41 PATH (tool exists) only; the tool is **not run** by r41, r42 or the census; r42 re-derives `maxN` itself but not the population count | population at tip = **56** files, newest `round-69` (hand-derived) | **NONE for the population number (F5)** |
| ``run `python3 -c "import glob; n=len(glob.glob('corpus/lessons/*verifier-spotcheck.md')); print(…present…)"` → `verifier-spotcheck population present` (exit 0)`` | r41 RUN | passes, but prints "present" for any n≥1 (56 at tip) — cannot detect drift | **WEAK (F5)** |
| "latest outside closure `corpus/lessons/round-68-verifier-spotcheck.md` (admitted — …), including round 68" | r42 `closure_ptr` (`CLOSURE_RE`/`INCL_RE`/`SPOT_RE`); verdict token checkable only by `tools/round58-c2-counter.py` (needs `--fleet-repo`/`--manifest-rev`, not standing) | newest at tip is `round-69`; pointer names `round-68` → `closure_ptr=0`. I did **not** verify "admitted" (fleet repo is off-limits to me) | **STALE (F4)**; verdict token: NONE standing |
| ``run `python3 tools/instrument-agreement.py --selftest` → `IA_SELFTEST pass=4 fail=0` `` | r41 RUN (+ census A) | passes | OK |
| `` `tools/round41-scorecard-reconcile.py` `` and `` `tools/round42-selfdesc-reconcile.py` `` ("this table's counters") | r41 PATH | exist | OK (existence) |
| `` `registry/verdict-ledger.tsv` (204 rows, self against outside for rounds 10–43: `agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`) `` | r41 PATH only. `tools/round44-verdict-ledger-audit.py` recomputes it (registered) but is frozen to `--fleet`/lane base `9d9cc93e`, needs the fleet repo, and is not in the census | 204 data rows, 102 keys; re-pairing self/outside by `harmed<unchanged<unprovable<unprovable-but-better<improved` gives **agree 69, overclaim 2, underclaim 16, other 0, absent 15** — exactly the cited figures | **NONE standing (F2)** (hand re-derivation matches) |
| `` `registry/claim-outcome-ledger.tsv` (126 rows, the 63 claims of rounds 10–44: `agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`) `` | r41 PATH only. `tools/round45-claim-outcome-audit{,-v2}.py` recompute it (registered) but frozen + fleet repo + not in census | 126 data rows, 63 keys; re-pairing with `not-met<unprovable<partial<unprovable-but-better<met` gives **agree 58, overclaim 1, underclaim 2, other 1, absent 1** | **NONE standing (F2)** (hand re-derivation matches) |
| "§Round-44 calibration ledger" / "§Round-45 claim-outcome ledger" | nothing | headings exist (lines 2355, 2418) | NONE (section-ref) |
| "score round 1; evidence re-anchored round 69" (cell 4) | nothing | — | NONE |

### adjacency (score 7)

| cited identity | re-derived by | observed | gap? |
|---|---|---|---|
| `` `corpus/knowledge/cross-lane-scope.md` sha256 `1801cb7fa45ef6f56ff96cb67c7840256fcffce000a56067cd8133797b9728a9` `` | r41 HASH | equal | OK |
| `(87 lines)` | r41 LINES | 87 | OK |
| ``run `python3 -c "print(sum(1 for l in open('corpus/knowledge/cross-lane-scope.md') if l.startswith(chr(124))))"` → `16` `` | r41 RUN (+ `rel` needle `cross-lane-scope.md`) | 16 (hand re-derived 16) | OK |
| "(lines starting with a table pipe, header and separator lines included)" | — | descriptive | PROSE |
| `` `PROVINCE.md` `` paragraph "Out of province → report, never absorb" | r41 PATH (file exists) only; r42 `province` greps only `tools/`/`registry/` tokens | paragraph present at `PROVINCE.md:53`; the **quoted string** is unchecked | NONE (string unchecked) |

### Table-wide, not in any row

| identity | re-derived by | observed | gap? |
|---|---|---|---|
| six score cells (`8 8 7 9 7 7`) | r41 score check against the hardcoded `EXPECTED` literal in the counter; r42 `saturation`/`retired` read the vector *from the table* | equal | OK, but the authority is a Python literal, not a tree fact |
| header promise "Evidence pointer (re-derivable at the measured commit)" | nothing | **the `## Axes` section names no commit at this tip**; the tip is whatever `--tip` the caller passes | **NONE (F6)** |
| cells 4 ("Last change") of all six rows | nothing (never parsed by r41 or r42) | — | NONE |
| intro paragraphs lines 10-11 (`Reconciled in round 41…`, `Round 43 re-anchors the SKILL.md and PROVINCE.md hashes…`) | nothing (outside the table population; r42 `receipts` does not cover the `## Axes` heading) | — | NONE |

---

## 4. Findings

**F1 (structural blocker for C1) — two r41 `run` facts cannot execute in r41's own harness.**
`m41.run_fact` executes `bash -c CMD` with `cwd` = a `git archive` extraction of the tip. That tree
has **no `.git`**. Reproduced byte-for-byte at `6035e952`:

```
$ git archive --format=tar 6035e952 | tar -x -C <scratch>/export && cd <scratch>/export
$ python3 tools/gate-registry-check.py --selftest
…
FAIL lane-tip: cannot resolve master: fatal: not a git repository (or any parent up to mount point /)
GATE_SELFTEST pass=6 fail=1
EXIT=1
$ python3 tools/round69-newest-closure-counter.py --since-round 63
COULD_NOT_EVALUATE git ls-tree --name-only failed (rc=128): fatal: not a git repository (or any parent up to mount point /)
EXIT=2
```
In a real worktree both tools behave: `GATE_SELFTEST pass=7 fail=0` (exit 0) and
`STALE_CALIBRATION … row_current=false` (exit 1). Consequences: (a) the operability row's cited
`GATE_SELFTEST pass=7 fail=0` is **unreachable** under r41 — this fact alone keeps `run_bad≥1` at
every tip, so `r41.met` can never be true while the row keeps that citation; (b) the calibration
row's live-counter fact is unreachable for the same reason, on top of being stale (F4).
Repair directions (L1's choice, not mine): make r41's export a real clone (`git clone --shared` +
checkout of the tip) instead of `git archive`, or cite these two commands in a form that does not
need `.git`, or stop citing them as `run` facts (which weakens `rel`, see §6).

**F2 (nothing standing re-derives the ledger/release aggregates).** Four numeric blocks in the
freshness and calibration rows are true only because they were true when written:
`91 on-release registry rows`, `82 holds / 3 holds-reworded / 6 unchanged-file / 0 drifted /
0 removed`, `204 rows / agreement=69/87 overclaim=2 underclaim=16 other=0 absent=15`,
`126 rows / agreement=58/61 overclaim=1 underclaim=2 other=1 absent=1`. The instruments that *can*
re-derive them (`tools/round44-release-recheck-audit.py`, `tools/round44-verdict-ledger-audit.py`,
`tools/round45-claim-outcome-audit-v2.py`) are frozen to round-44/45 revisions, need `--fleet` and
(for C1) an upstream llama.cpp clone, and **none is a census arm**. I re-derived all four by hand at
the tip and all four still hold (the release-recheck aggregate is the ledger's own verdict-column
count; the two agreement blocks are self/outside pairings over 102 and 63 keys) — so this is a
*coverage* gap, not a live error.

**F3 (unchecked ordinal cross-references — the r68 depth-row class, twice).** The depth row's
"lesson Mistake 4" and the coverage row's "lesson Mistake 3" are prose ordinals: no backticked path,
so r41's PATH reader never sees them, and neither counter reads cell 4. Worse, the ordinal is
ambiguous: `Mistake 4` is item 4 in `round-67.md`, `round-68.md` and `round-69.md` with three
different meanings, and the literal string `Mistake 3` does not occur anywhere under
`corpus/lessons/` (the intended referent is item 3 of `round-66.md`). These are exactly the anchor
class round 68 mined as "Mistake 4" (a cited identity that drifted because no command re-derived
it): a mechanical sweep cannot resolve them without a naming convention (e.g. cite
`` `corpus/lessons/round-69.md` item 4 ``).

**F4 (stale at the tip, and the counter that would catch it is not standing).** The calibration row
names `round-68` as `latest outside closure` while `round-69-verifier-spotcheck.md` exists and is
dated `2026-11-01` — `closure_ptr=0`, and the r69 counter's live mode prints `STALE_CALIBRATION`.
Separately, the row's cited line `NEWEST_CLOSURE … row_current=true` (a `[literal …]` ellipsis)
**can never equal any output line** of the tool, whose format is
`NEWEST_CLOSURE newest=<file> date=<iso> round=<n> row_names=<file> row_current=<true|false>`.

**F5 (the verifier-spotcheck "population" number has no re-derivation at any tip).** The row
delegates it to `tools/round59-c2-counter.py --fleet-ref HEAD`, which no counter runs and which is
not a census arm; the row also carries a `run` fact that only prints
`verifier-spotcheck population present` (true for n≥1; n=56 at the tip), and explicitly says "exact
count … in the counter receipt". The number is therefore uncited and unchecked — neither a stale
risk nor a checkable claim today.

**F6 (the table's own header promise has no anchor).** Cell 3 is headed "Evidence pointer
(re-derivable at the measured commit)" but `## Axes` names no measured commit at this tip, and both
counters take `--tip` from the caller. A reader cannot tell which revision the rows were reconciled
against; the r41/r42 receipts are the only record.

**F7 (score authority is a literal, not the tree).** All six scores are checked against
`EXPECTED = {"operability": 8, …, "calibration": 7}` inside `tools/round41-scorecard-reconcile.py`.
r42's `saturation`/`retired` legs read the vector *from the table*, so nothing in the tree
independently states the vector; a score change requires editing the counter. This is by design
("last-declared assessment") but it means a score cell is never wrong *relative to the tree*.

---

## 5. The four `province`-detail tokens (EX03 patch checklist)

Rule (`tools/round42-selfdesc-reconcile.py`, in `evaluate`), verbatim:

```python
    pv = show(repo, tip, "PROVINCE.md") or ""
    for r in crows:
        if len(r) >= 3:
            for tok in re.findall(r"`([^`]+)`", r[2]):
                if tok.startswith(("tools/", "registry/")) and tok not in pv:
                    bad("province", f"PROVINCE.md lacks {tok} (capability {r[0].strip('` *')})")
```
`crows` = the rows of the §Capabilities canon table (`canon(sc)`); `r[2]` is the evidence cell.
The test is a **raw substring test against PROVINCE.md bytes** — the token need not be backticked
there. At `6035e952` exactly four fail:

| token | capability | occurrences in PROVINCE.md at tip |
|---|---|---|
| `tools/round67-worktree-landing-check.py` | worktree-landing-check | 0 |
| `tools/round68-receipt-pointer-audit.py` | receipt-pointer-audit | 0 |
| `registry/receipt-pointer-resolutions.tsv` | receipt-pointer-audit | 0 |
| `tools/round69-newest-closure-counter.py` | newest-closure-counter | 0 |

Controls (already present, must stay): `tools/append-only-audit.py` → 1, `tools/kama-probe.sh` → 3.
Patch requirement: add those four tokens (verbatim, with the `tools/`–`registry/` prefix) to
`PROVINCE.md`; touching SCORECARD.md does not satisfy this leg.

## 6. The r42 rule strings EX03's patch must not break

`head` = every line before the first `## ` heading; `maxn` = max N over `^## Round (\d+)` headings
(69 at the tip); `vector` = [(axis, score)] parsed from the `## Axes` rows; `names` = first cell of
each §Capabilities canon row (15 at the tip).

**banner** (exact literals):
```python
if "operability + calibration" not in head: bad("banner", "head lacks 'operability + calibration'")
if "operability and freshness" in head: bad("banner", "head still says 'operability and freshness'")
if "adds **zero** verified completed rounds" in head: bad("banner", "head still says 'adds zero verified completed rounds'")
if not re.search(r"Latest measured round: %d\b" % maxn, head): bad("banner", f"head lacks 'Latest measured round: {maxn}'")
```

**planned** (`sections(sc,"Planned")[:1]`):
```python
if ".ufo/round-5/continuation.md" in pl: bad("planned", "still points at .ufo/round-5/continuation.md")
if "freshness move" in pl: bad("planned", "still plans a 'freshness move'")
ph = f"### Planned (round {maxn + 1})"
if ph not in pl: bad("planned", f"section does not name '{ph}'")
# plus: a line whose .strip() == ph must be followed by a line matching r"\s*1\.\s"
```

**retired** (`sections(sc,"Retired")[:1]`):
```python
if "Both assigned axes" in rt: bad("retired", "still says 'Both assigned axes'")
if "every model endpoint is dead" in rt: bad("retired", "still says 'every model endpoint is dead'")
if f"{len(vector)} axes" not in rt: bad("retired", f"does not state '{len(vector)} axes'")
if f"{len(names)} capabilities" not in rt: bad("retired", f"does not state '{len(names)} capabilities'")
```
At the tip the §Retired text reads "None. 6 axes and 13 capabilities remain active." — the **6 axes**
conjunct passes, `15 capabilities` fails (13 vs 15 canon rows): a real stale count, not wording.

**closure_ptr** (calibration row text):
```python
CLOSURE_RE = re.compile(r"latest outside closure\s+`corpus/lessons/round-(\d+)-verifier-spotcheck\.md`")
INCL_RE    = re.compile(r"including round (\d+)")
SPOT_RE    = re.compile(r"corpus/lessons/round-(\d+)-verifier-spotcheck\.md")
ns   = [int(m.group(1)) for n in git(repo,"ls-tree","--name-only",tip,"corpus/lessons/").split("\n")
        for m in [SPOT_RE.fullmatch(n.strip())] if m]
want = max(ns)
ptrs = [int(x) for x in CLOSURE_RE.findall(cal_row)]
# exactly one pointer; ptrs[0] == want; every INCL_RE value == want
# a false conjunct adds exactly 1 to mismatches (not a per-fact counter)
```

**rel** (must survive any row edit): each axis row must carry a `run` fact whose *command* contains
`NEEDLE[axis]`:
```python
NEEDLE = {"operability": "pin-watch.py selftest", "freshness": "recheck", "depth": "SKILL.md",
          "coverage": "corpus/knowledge", "calibration": "verifier-spotcheck",
          "adjacency": "cross-lane-scope.md"}
```
So EX03 must not delete the `pin-watch.py selftest`, recheck, `grep -c '^## ' SKILL.md`,
`corpus/knowledge` glob, `verifier-spotcheck` and `cross-lane-scope.md` run facts. Scores must stay
`8,8,7,9,7,7` (`EXPECTED`), and the six axis names must be exactly
`operability freshness depth coverage calibration adjacency` (`AXES`).

---

## 7. The three anchors whose re-derivation is hardest to make mechanical

1. **The `round59-c2-counter`-delegated "verifier-spotcheck population" (calibration row).** The
   derivation needs `--fleet-ref` against a *different* repo (the fleet root), i.e. state outside
   the lane tree. No lane-local instrument can re-derive it, which is why the row delegates; making
   it mechanical requires either a lane-committed copy of the fleet verdict/closure index or a
   counter that takes an explicit fleet path and is wired into the census. The lane-local part
   (`maxN`) is already mechanical via `SPOT_RE`; the population number is not.
2. **The b11889 release-recheck block (`91` population and `82/3/6/0/0`).** Truth requires the
   upstream llama.cpp clone at release `d854d98b…` plus a re-read of every cited range; the lane
   only holds the ledger. The cheap mechanical substitute (count the ledger's `verdict` column) is
   self-referential: it proves the aggregate matches the ledger, not that the ledger is right. I ran
   the cheap version (it matches 82/3/6/0/0) and regard the strong version as un-mechanizable
   without the external object store.
3. **The "lesson Mistake N" ordinals (depth and coverage rows).** Resolving them needs a convention
   (which lesson? whose numbering?) and then prose matching against a numbered list; `Mistake 4`
   names three different items in three lessons and `Mistake 3` occurs nowhere literally. Making
   this mechanical means changing the citation form (a path plus an item number), not adding a check
   to any existing instrument.

Runner-up (fixable, so not in the three): the two `.git`-dependent `run` facts of F1 — hard to
re-derive *today* only because r41's harness extracts a tar instead of a clone; a harness change
makes them trivially mechanical.

---

## 8. What I could NOT verify

- I did **not** run `tools/round44-release-recheck-audit.py`, `tools/round44-verdict-ledger-audit.py`,
  `tools/round45-claim-outcome-audit*.py`, `tools/round58-c2-counter.py` or
  `tools/round59-c2-counter.py`: each needs `--fleet` / `--fleet-repo` / `--upstream`, and the fleet
  repo is off-limits to this seat. I read their contracts and re-derived the ledger aggregates from
  committed columns instead; the *validity* legs (does each cited line really carry that verdict at
  that rev) are unverified.
- I did **not** verify that `corpus/lessons/round-68-verifier-spotcheck.md` says "admitted" (the
  calibration row's token) — that needs the fleet `MANIFEST.json`.
- I did **not** run the r42 selftest: it is refused on this host (NTFS path) per the r69 census
  receipt; I did not attempt the fixture myself.
- The 14 r41 `run` facts other than the two failures were observed **through r41's harness only**
  (single instrument); I did not re-run each command independently. All seven sha256 values, all six
  line counts and the four `python3 -c` / `grep -c` counts were re-derived independently (§9).
- I made no judgement on C1's admission, no axis score, and no capability claim.

## 9. Independent re-derivation commands and outputs

```
$ for p in tools/kama-probe.sh tools/test-snapshot.sh .ufo/waves/round-41/c2/ls-remote-vllm.txt SKILL.md corpus/knowledge/endpoint-identity.md PROVINCE.md corpus/knowledge/cross-lane-scope.md; do git cat-file -p 6035e952:$p | sha256sum; git cat-file -p 6035e952:$p | wc -l; done
tools/kama-probe.sh 4393ab819d6a741646237ef0268cc0836988a9711bab6b06c46cbfea382964f4   1138
tools/test-snapshot.sh 236c23c12964cf0b2f0a2f970187e216d3398dcf2b92ffb7e8606e0fdd029646   194
.ufo/waves/round-41/c2/ls-remote-vllm.txt 13388e483163357aa4daea784d0e67cdc8d6b5438d3166d613a2a044590b9282   224
SKILL.md 86be9083a1ddc4453fc57a0d3980502bd497455902a2b00f653c4239ea0818b8   1721
corpus/knowledge/endpoint-identity.md 0100ac6d89876b2f11a58542ae1ab75c3765f61d9d138fdad4d720074ddf13d7   218
PROVINCE.md f0aaae9ccfd0ecb6641ad1646934f4ff5555fcc45d2e397670b2eb5ff083e8a6   270
corpus/knowledge/cross-lane-scope.md 1801cb7fa45ef6f56ff96cb67c7840256fcffce000a56067cd8133797b9728a9   87
$ git cat-file -p 6035e952:SKILL.md | grep -c '^## '                     -> 48
$ … cross-lane-scope.md | python3 -c "…startswith(chr(124))…"            -> 16
$ git ls-tree --name-only 6035e952 corpus/knowledge/ | grep '\.md$' | grep -v engine-sides | grep -v processes | wc -l  -> 39
$ git cat-file -p 6035e952:corpus/SOURCES.md | python3 -c "recheck=[…]<=477…]"  -> 218
$ git ls-tree --name-only 6035e952 corpus/lessons/ | grep -c 'verifier-spotcheck\.md$'  -> 56   (newest round = 69)
$ ledger row counts (NR>1): verdict-ledger 204, claim-outcome-ledger 126, release-recheck-b11889 91
$ release-recheck-b11889 verdict column (field 10): 82 holds, 3 holds-reworded, 6 unchanged-file (0 others)
$ re-paired self/outside: verdict 102 keys -> agree 69, overclaim 2, underclaim 16, other 0, absent 15
$ re-paired self/outside: claim    63 keys -> agree 58, overclaim 1, underclaim 2, other 1, absent 1
$ grep -c -F <token> PROVINCE.md for the four province tokens -> 0 0 0 0; tools/append-only-audit.py -> 1
```
Tooling installs: **none** (no `pacman`, `uv tool`, `pip` or binary install was performed; the
forbidden `pacman -Sy/-Syu/-U/-R` class was not touched).
Scratch `/fast/scratch/hyaku/kama-r70/SCT02AxesCoverage/` is deleted before yield; nothing was
written under `/tmp` and nothing in the lane tree outside this out directory.
